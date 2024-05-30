from datetime import datetime

import numpy as np

from DataBase.Redis import Redis
from Shared.Classes import Action, Gender, People
from Shared.Context import Tracker as config
from Shared.Context import doors


class State:
    def __init__(self, close, gender):
        self.newborn = True
        self.close = close
        self.gender_count = [0] * len(Gender)
        self.update_gender(gender)
        
    def is_entered(self, close: bool) -> bool:
        return self.newborn and self.close > close

    def is_exited(self, close: bool) -> bool:
        return self.close < close

    def is_passed(self, close: bool) -> bool:
        return not self.newborn and self.close > close

    def check_action(self, close: bool) -> Action | None:
        if self.is_entered(close):
            return Action.Enter
        if self.is_exited(close):
            return Action.Exit
        if self.is_passed(close):
            return Action.Pass

    def update(self, close: bool, gender: Gender):
        action = self.check_action(close)
        self.newborn = self.newborn and self.close == close
        self.close = close
        self.update_gender(gender)
        return action

    def update_gender(self, current):
        self.gender_count[current.value] += 1

    @property
    def gender(self) -> Gender:
        return Gender(np.argmax(self.gender_count))


class Counter:
    def __init__(self) -> None:
        self.history: dict[int, State] = dict()
        self.count = [0, 0]
        self.redis = Redis()

    def track(self, persons: list[People], time: datetime):
        for person in persons:
            if person.id is None:
                continue
            close = person.is_close(doors)
            if person.id not in self.history:
                self.history[person.id] = State(close, person.gender)
                continue
            state = self.history[person.id]
            action = state.update(close, person.gender)
            if action is None:
                continue
            if state.gender in config.ignore:
                continue
            self.update_counters(state.gender, action, time)

    def update_counters(self, gender: Gender, action: Action, time: datetime):
        match action:
            case Action.Enter:
                self.count[0] += 1
                self.redis.entered(gender, time)
            case Action.Exit:
                self.count[1] += 1
                self.redis.exited(gender, time)
            case Action.Pass:
                self.count[1] -= 1
                self.redis.passed(gender, time)
            case _:
                return
        print(f"На данный момент Зашло: {self.count[0]} Вышло: {self.count[1]}")

