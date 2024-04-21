from enum import Enum
from attr import frozen

from Tracker.Doors import Doors
from Tracker.misc import Distances, dist


class Gender(Enum):
    Cleaner = 0
    Coach = 1
    Kid = 2
    Man = 3
    Woman = 4


def _is_close(position: tuple[int, int]) -> bool:
    """
    Проверяет находится ли позиция в какой-либо двери

    :param position: Позиция для проверки
    :type position: tuple[int, int]
    :return: Находится в двери
    :rtype: bool
    """
    for door in Doors:
        if dist(*door.center, *position) < float(Distances.Close):
            return True
    return False

def is_close(position: tuple[int, int]) -> bool:
    """
    Проверяет находится ли позиция в какой-либо двери

    :param position: Позиция для проверки
    :type position: tuple[int, int]
    :return: Находится в двери
    :rtype: bool
    """
    x,y = position
    for door in Doors:
        x_min, y_min, x_max, y_max = door.corners
        if (x_min < x < x_max) and (y_min < y < y_max):
            return True
    return False


@frozen
class People:
    id: int
    gender: Gender
    is_close: bool

    @classmethod
    def from_position(cls, id: int, gender: Gender, position: tuple[int, int]):
        return cls(id, gender, is_close(position))
