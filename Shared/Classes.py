from datetime import datetime
from enum import Enum, auto
from itertools import repeat
from typing import NamedTuple

from attr import frozen
from cv2.typing import MatLike


class Gender(Enum):
    Cleaner = 0
    Coach = 1
    Kid = 2
    Man = 3
    Woman = 4


class Action(Enum):
    Enter = auto()
    Exit = auto()
    Pass = auto()


class Frame(NamedTuple):
    time: datetime
    image: MatLike

@frozen
class Door:
    name: str
    corners: tuple[int, int, int, int]

    def center(self) -> tuple[int, int]:
        return sum(self.corners[::2])//2, sum(self.corners[1::2])//2
    
    def is_close(self, position: tuple[int, int]) -> bool:
        x, y = position
        x_min, y_min, x_max, y_max = self.corners
        return (x_min < x < x_max) and (y_min < y < y_max)
    
@frozen
class People:
    id: int
    gender: Gender
    position: tuple[int, int]

    @classmethod
    def from_position(cls, id: int, gender: Gender, position: tuple[int, int]):
        return cls(id, gender, tuple(map(int, position)))
    
    def is_close(self, doors: list[Door]) -> bool:
        return any(map(Door.is_close, doors, repeat(self.position)))


