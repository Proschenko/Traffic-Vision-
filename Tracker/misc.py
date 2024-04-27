from datetime import datetime
from enum import Enum, auto
from typing import NamedTuple

import numpy as np
from cv2.typing import MatLike


class Frame(NamedTuple):
    time: datetime
    image: MatLike


class Action(Enum):
    Enter = auto()
    Exit = auto()
    Pass = auto()


def dist(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Вычисляет Евклидово расстояние
    """
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def boxes_center(corners: np.ndarray[float, float]) -> np.ndarray[float, float]:
    """
    Находит центры прямоугольников, которые заданны двумя углами.

    :param corners: Массив координат размера (n, 4) формата xyxy
    :type corners: np.ndarray[float, float]
    :return: Массив координат размера (n, 2) формата xy
    :rtype: np.ndarray[float, float]
    """
    return np.mean(corners.reshape((-1, 2, 2)), 1)
