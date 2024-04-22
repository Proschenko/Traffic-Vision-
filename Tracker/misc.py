from enum import Enum, IntEnum, auto

import numpy as np
from cv2.typing import MatLike

WIDTH = 640
HEIGHT = 300
WIDTH_2_MIN = 900
WIDTH_2_MAX = 1540
HEIGHT2 = 150


class Action(Enum):
    Enter = auto()
    Exit = auto()
    Pass = auto()


class Distances(IntEnum):
    """
    Расстояние до двери:
    Close: близко
    Around: около
    """
    Close = 54
    Around = 100


def crop_image(image: np.ndarray) -> np.ndarray:
    # Создаем черное изображение нужного размера
    final_image = np.zeros((640, 640, 3), dtype=np.uint8)

    # Размещаем первую часть изображения
    first_part = image[:HEIGHT, :WIDTH]
    final_image[:HEIGHT, :WIDTH] = first_part

    # Размещаем вторую часть изображения с отступом в 20 пикселей
    second_part = image[:HEIGHT2, WIDTH_2_MIN:WIDTH_2_MAX]
    final_image[HEIGHT + 20:HEIGHT + 20 + HEIGHT2, :WIDTH] = second_part

    return final_image


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
