from cv2.typing import MatLike
from enum import Enum, IntEnum

import numpy as np

frame_crop = {
    "width": 950,
    "height": 950
}


class Location(Enum):
    """
    Положениние человека относительно двери:
    Far = 0     : Далеко
    Around = 1  : Около
    Close = 2   : Внутри

    >>> p = Location.Far
    >>> p is Location.Far
    True
    """
    Far = 0
    Around = 1
    Close = 2


class Distances(IntEnum):
    """
    Расстояние до двери:
    Close   : близко
    Around  : около
    """
    Close = 54
    Around = 100

def crop_image(image: MatLike,
               left=None, width=None, 
               top=None, height=None) -> MatLike:
    return image[top or 0: height or -1,
                 left or 0: width or -1]

def fill_black(frame):
    height, width, _ = frame.shape

    if height > 350:
        frame[300:, :, :] = 0  # Закрашиваем часть изображения, превышающую 300 пикселей по высоте, в черный цвет

    return frame

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
