from datetime import datetime
from itertools import product
from time import mktime
from typing import Literal

import numpy as np
import redis

Action = Literal["enter", "exit"]
Gender = Literal["man", "woman", "kid"]

unix_timestamp = int


def datetime_to_unix(time: datetime) -> unix_timestamp:
    return int(mktime(time.timetuple()) * 1000)


def unix_to_datetime(time: int) -> datetime:
    return datetime.fromtimestamp(time / 1000)


class Redis:
    people_key = "ts_people"

    def __init__(self) -> None:
        self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.timeseries = self.redis.ts()
    
    def key(self, action: Action, gender: Gender) -> str:
        return f"{self.people_key}:{action}:{gender}"
    
    def labels(self, action: Action, gender: Gender) -> dict[str, str]:
        return {"action": action, "gender": gender, "oleg": "pepeg"}

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
    
    def last_update(self, action: Action, gender: Gender) -> datetime:
        if not self.redis.exists(self.key(action, gender)):
            return datetime.now()
        time, _ = self.timeseries.get(self.key(action, gender))
        return unix_to_datetime(time)
    
    def reset_counter(self, action: Action, gender: Gender, time: datetime):
        if self.last_update(action, gender).day == time.day:
            return
        print("I am gona reset counter!")
        time = datetime_to_unix(time.date())
        self.timeseries.add(self.key(action, gender), time, 0,
                            labels=self.labels(action, gender))

    def increment(self, action: Action, gender: Gender, time: datetime):
        self.reset_counter(action, gender, time)
        time = datetime_to_unix(time)
        self.timeseries.incrby(self.key(action, gender), 1, time,
                               labels=self.labels(action, gender))

    def decrement(self, action: Action, gender: Gender, time: datetime):
        self.reset_counter(action, gender, time)
        time = datetime_to_unix(time)
        self.timeseries.decrby(self.key(action, gender), 1, time,
                               labels=self.labels(action, gender))

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

    print(db.get_count(datetime.fromtimestamp(0), datetime.now(), "enter", 1*3600*24))
    # print(db.last_update("enter", "man"))
