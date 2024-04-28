if __name__ == "__main__":
    import sys
    from os.path import dirname

    sys.path.append(dirname(__file__).rpartition('\\')[0])

from datetime import datetime, timedelta
from enum import Enum
from itertools import product
from time import mktime
from typing import NamedTuple, Sequence

import numpy as np
import pandas as pd
import redis

from Config.Context import Redis as config
from Tracker.misc import Action
from Tracker.People import Gender


class RedisError(Exception):
    """ Exception from redis """


class Filter:
    def __init__(self, action: Action | tuple[Action] = None, gender: Gender | tuple[Gender] = None) -> None:
        self.actions = self.parse(action, (Action.Enter, Action.Exit))
        self.genders = self.parse(gender, (Gender.Kid, Gender.Man, Gender.Woman))

    @staticmethod
    def parse(something, anything: Enum) -> tuple[Enum]:
        if something is None:
            something = tuple(anything)
        if not isinstance(something, Sequence):
            something = (something,)
        return something

    @staticmethod
    def tuple_to_str(s: tuple[Enum]) -> str:
        if len(s) == 1:
            return s[0].name
        return f"({','.join(e.name for e in s)})"

    @property
    def filter(self) -> tuple[str]:
        return (f"action={self.tuple_to_str(self.actions)}",
                f"gender={self.tuple_to_str(self.genders)}")

    def __str__(self) -> str:
        return f"Filter {self.actions}, {self.genders}"


class Key(NamedTuple):
    action: Action
    gender: Gender
    people_key = "ts_people"

    @property
    def label(self) -> dict[str, str]:
        return {"action": self.action.name, "gender": self.gender.name}

    @property
    def key(self) -> str:
        return f"{self.people_key}:{self.action.name}:{self.gender.name}"


unix_timestamp = int


def datetime_to_unix(time: datetime) -> unix_timestamp:
    return int(mktime(time.timetuple()) * 1000)


def unix_to_datetime(time: int) -> datetime:
    return datetime.fromtimestamp(time / 1000)


class Redis:
    def __init__(self) -> None:
        self.redis = redis.Redis(**config.args)
        try:
            self.redis.ping()
        except redis.exceptions.ConnectionError:
            raise RedisError("Can't connect to radis")
        self.timeseries = self.redis.ts()

    def add(self, key: Key, time: datetime, number: int):
        self.timeseries.add(key.key, datetime_to_unix(time), number, labels=key.label)

    def get_count(self, start: datetime, end: datetime,
                  action: Action, step: int) -> dict[str, list[tuple[unix_timestamp, int]]]:
        "deprecated, don't use it"
        start, end = map(datetime_to_unix, (start, end))
        bucket = int(step * 1000)

        data = self.timeseries.mrange(start, end, [f"action={action}"], empty=True,
                                      aggregation_type="last", bucket_size_msec=bucket)
        res = dict()
        for (name, value), *_ in map(dict.items, data):
            _, _, gender = name.rpartition(":")
            res[gender] = value[1]
        return res

    def get_hist(self, date: datetime, n_buckets: int, filter: Filter = None) -> pd.DataFrame:
        """
        Возвращает количество человек в день date с шагом 24/n_buckets часов.

        :param date: Дата
        :type date: datetime
        :param n_buckets: Число строчек таблицы
        :type n_buckets: int
        :param filter: Фильтр действия и пола, defaults to None
        :type filter: Filter, optional
        :return: Таблица где индекс - datetime время, колонки - action, gender
        :rtype: pd.DataFrame
        """
        filter = filter or Filter()
        start = date.date()
        end = start + timedelta(days=1)
        return self.range_aggregation(start, end, n_buckets, filter)

    def get_hour(self, start_date: datetime, end_date: datetime, filter: Filter = None) -> pd.DataFrame:
        """
        Возвращает количество человек за час указаный в date.

        :param date: Дата
        :type date: datetime
        :param filter: Фильтр действия и пола, defaults to None
        :type filter: Filter, optional
        :return: Таблица где индекс - datetime время, колонки - action, gender
        :rtype: pd.DataFrame
        """
        filter = filter or Filter()
        print(f"Вырезаю данные начиная с {start_date} до {end_date}")
        return self.range_aggregation(start_date, end_date, 1, filter)

    def range_aggregation(self, start: datetime, end: datetime, n_buckets: int, filter: Filter):
        bucket = int((end - start).total_seconds() * 1000) // n_buckets
        start_unxi, end_unix = map(datetime_to_unix, (start, end))
        response = self.timeseries.mrange(start_unxi, end_unix - 1, filter.filter, align="-",
                                          aggregation_type="range", bucket_size_msec=bucket)
        index = pd.date_range(start, end, n_buckets + 1, inclusive="left")
        actions = filter.actions
        genders = filter.genders

        columns = pd.MultiIndex.from_product((actions, genders))
        result = pd.DataFrame(0, index=index, columns=columns)

        for part in response:
            (full_name, raw_data), *_ = part.items()
            _, act, gen = full_name.split(":")
            act, gen = Action[act], Gender[gen]
            for time, count in raw_data[1]:
                time = unix_to_datetime(time)
                result.at[time, (act, gen)] = count
        return result

    def last_update(self, key: Key) -> datetime:
        if not self.redis.exists(key.key):
            return datetime.now()
        time, _ = self.timeseries.get(key.key)
        return unix_to_datetime(time)

    def reset_counter(self, key: Key, time: datetime):
        if self.last_update(key).day == time.day:
            return
        print("I am gona reset counter!")
        self.add(key, time.date(), 0)

    def increment(self, key: Key, time: datetime):
        self.reset_counter(key, time)
        time = datetime_to_unix(time)
        self.timeseries.incrby(key.key, 1, time,
                               labels=key.label)

    def decrement(self, key: Key, time: datetime):
        self.reset_counter(key, time)
        time = datetime_to_unix(time)
        self.timeseries.decrby(key.key, 1, time,
                               labels=key.label)

    def entered(self, gender: Gender, time: datetime):
        self.increment(Key(Action.Enter, gender), time)

    def exited(self, gender: Gender, time: datetime):
        self.increment(Key(Action.Exit, gender), time)

    def passed(self, gender: Gender, time: datetime):
        self.decrement(Key(Action.Exit, gender), time)

    def remove_all_data(self, force=False):
        if force or input("Вы уверенны что хотите удалить все данные из базы? [y/n]: ") == 'y':
            for key in self.redis.scan_iter("*"):
                self.redis.delete(key)
            return
        print("Отмена")

    def create_test_data(self):
        if input("Вы уверенны что хотите наполнить базу фальшивыми данными? [y/n]: ") != 'y':
            print("Отмена")
            return
        np.random.seed(1)
        self.remove_all_data(True)
        center = datetime_to_unix(datetime(2024, 3, 15, 12))
        # center = datetime_to_unix(datetime.now())
        spread = 5 * 3600 * 1000

        for action, gender in product((Action.Enter, Action.Exit),
                                      (Gender.Kid, Gender.Man, Gender.Woman)):
            times = np.random.normal(center, spread, size=1000)
            times = np.unique(times)

            for t in times:
                self.increment(Key(action, gender), unix_to_datetime(t))


if __name__ == "__main__":
    from matplotlib import pyplot as plt

    db = Redis()
    db.create_test_data()

    res = db.get_hist(datetime(2024, 3, 15, 12), 24)
    res.plot(kind='bar')
    plt.xticks(rotation=45, ha='right')
    plt.show()

# if __name__ == "__main__":
#     from matplotlib import pyplot as plt
#
# db = Redis()
# db.remove_all_data()
# db.create_test_data()
# print("111")

# res = db.get_hour(datetime(2024, 4, 4, 14))
# print(res)
# print()
# res.plot(kind='bar')
# plt.xticks(rotation=45, ha='right')
# plt.show()
