from datetime import datetime

import numpy as np

from DataBase.Redis import Redis
from Shared.Classes import Action, Gender, People
from Shared.Context import doors

IGNORE = Gender.Cleaner, Gender.Coach

class State:
    def __init__(self, close: bool, gender: Gender):
        self.newborn = True
        self.close = close
        self.gender_count = [0] * len(Gender)
        self.update_gender(gender)

    def update(self, close: bool):
        self.newborn = self.newborn and self.close == close
        self.close = close

    def update_gender(self, current: Gender):
        self.gender_count[current.value] += 1

    @property
    def gender(self) -> Gender:
        return Gender(np.argmax(self.gender_count))

# TODO: put all this into State class
def is_entered(close: bool, state: State) -> bool:
    return state.newborn and state.close > close


def is_exited(close: bool, state: State) -> bool:
    return state.close < close


def is_passed(close: bool, state: State) -> bool:
    return not state.newborn and state.close > close


def check_action(close: bool, state: State) -> Action | None:
    if is_entered(close, state):
        return Action.Enter
    if is_exited(close, state):
        return Action.Exit
    if is_passed(close, state):
        return Action.Pass


class Traker:
    def __init__(self) -> None:
        self.history: dict[int, State] = dict()
        self.count = [0, 0]
        self.redis = Redis()

    def track(self, persons: list[People], time: datetime):
        for person in persons:
            result = self.oleg(person)
            if result is None:
                continue
            self.update_counters(*result, time)

    def oleg(self, person: People) -> tuple[Gender, Action | None] | None:
        if person.id is None:
            return
        close = person.is_close(doors)
        state = self.history.get(person.id, None)
        if state is None:
            self.history[person.id] = State(close, person.gender)
            return
        state.update_gender(person.gender)
        if state.gender in IGNORE:
            return
        action = check_action(close, state)
        state.update(close)
        return state.gender, action

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

