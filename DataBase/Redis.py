from datetime import datetime, timedelta
from itertools import product
from random import random
from time import mktime
from typing import Literal

import numpy as np
import redis

Action = Literal["enter", "exit"]
Class_ = Literal["man", "woman", "kid"]

unix_timestamp = int


def datetime_to_unix(time: datetime) -> unix_timestamp:
    return int(mktime(time.timetuple()) * 1000)


def unix_to_datetime(time: int) -> datetime:
    return datetime.fromtimestamp(time / 1000)


class Redis:
    people_key = "ts_people"
    action = ["enter", "exit"]
    class_ = ["man", "woman", "kid"]

    def __init__(self) -> None:
        self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.timeseries = self.redis.ts()

    def add_data(self, action: str, class_: str, time: datetime, count: int):
        time = datetime_to_unix(time)
        self.timeseries.add(f"{self.people_key}:{action}:{class_}", time, count,
                            labels={"action": action, "class_": class_})

    def get_data(self, action: str, class_: str, start: datetime, end: datetime) -> list[tuple[unix_timestamp, int]]:
        start, end = map(datetime_to_unix, (start, end))
        return self.timeseries.range(f"{self.people_key}:{action}:{class_}", start, end)

    def get_count(self, start: datetime, end: datetime,
                  action: Action, step: int) -> dict[str, list[tuple[unix_timestamp, int]]]:
        start, end = map(datetime_to_unix, (start, end))
        bucket = int(step * 1000)

        data = self.timeseries.mrange(start, end, [f"action={action}"], empty=True,
                                      aggregation_type="last", bucket_size_msec=bucket)
        res = dict()
        for (name, value), *_ in map(dict.items, data):
            _, _, class_ = name.rpartition(":")
            res[class_] = value[1]
        return res
    
    def last_update(self, action: Action, class_: Class_) -> datetime:
        if not self.redis.exists(f"{self.people_key}:{action}:{class_}"):
            return datetime.now()
        time, _ = self.timeseries.get(f"{self.people_key}:{action}:{class_}")
        return unix_to_datetime(time)
    
    def reset_counter(self, action: Action, class_: Class_, time: datetime):
        if self.last_update(action, class_).day == time.day:
            return
        print("I am gona reset counter!")
        time = datetime_to_unix(time.date())
        self.timeseries.add(f"{self.people_key}:{action}:{class_}", time, 1)

    def increment(self, action: Action, class_: Class_, time: datetime):
        self.reset_counter(action, class_, time)
        time = datetime_to_unix(time)
        self.timeseries.incrby(f"{self.people_key}:{action}:{class_}", 1, time,
                               labels={"action": action, "class_": class_})

    def decrement(self, action: Action, class_: Class_, time: datetime):
        self.reset_counter(action, class_, time)
        time = datetime_to_unix(time)
        self.timeseries.decrby(f"{self.people_key}:{action}:{class_}", 1, time,
                               labels={"action": action, "class_": class_})

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
        spread = 5*3600*1000

        for action, gender in product(("enter", "exit"), ("man", "woman", "kid")):
            times = np.random.normal(center, spread, size=1000)
            times = np.unique(times)

            for t in times:
                self.increment(action, gender, unix_to_datetime(t))


if __name__ == "__main__":
    db = Redis()
    db.create_test_data()

    # pprint(db.get_count(datetime.fromtimestamp(0), datetime.now(), "enter", 1*3600*24))
    # print(db.last_update("enter", "man"))
