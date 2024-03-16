from itertools import product
from pprint import pprint
from random import randrange
import redis

# class Action(Enum):
#     Entered = "entered"
#     Exited = "exited"

# class Class_(Enum):
#     Man = "man"
#     Woman = "woman"
#     Kid = "kid"


class Redis:
    people_key = "ts_people"
    action = ["enter", "exit"]
    class_ = ["man", "woman", "kid"]
    def __init__(self) -> None:
        self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.timeseries = self.redis.ts()
    
    def init_database(self):
        for action, class_ in product(self.action, self.class_):
            self.timeseries.create(f"{self.people_key}:{action}:{class_}",
                                   labels={"action": action, "class_": class_})
    
    def add_data(self, action: str, class_: str, time: int, count: int) -> bool:
        self.timeseries.add(f"{self.people_key}:{action}:{class_}", time, count,
                            labels={"action": action, "class_": class_})
    
    def get_data(self, action: str, class_: str, start: int, end: int) -> list[tuple[int]]:
        return self.timeseries.range(f"{self.people_key}:{action}:{class_}", start, end)
    
    def get_count(self, start: int, end: int, action: str):
        data = self.timeseries.mrange(start, end, [f"action={action}"], empty=True,
                                     aggregation_type="last", bucket_size_msec=60000)
        res = dict()
        for (name, value), *_ in map(dict.items, data):
            _, _, class_ = name.rpartition(":")
            res[class_] = value[1]
        
        return res
    
    def increments(self, action: str, class_: str, time: int):
        self.timeseries.incrby(f"{self.people_key}:{action}:{class_}", 1, time)
        
    def decrement(self, action: str, class_: str, time: int):
        self.timeseries.decrby(f"{self.people_key}:{action}:{class_}", 1, time)

if __name__ == "__main__":
    db = Redis()
    for key in db.redis.scan_iter("*"):
        db.redis.delete(key)
    for i in range(10):
        time_ = randrange(10**5, 10**5*2)
        count = randrange(1, 10)
        db.add_data("enter", "woman", time_, count)
        db.add_data("enter", "man", time_, count)
        db.add_data("enter", "kid", time_, count)

    pprint(db.get_count("-", "+", "enter"))