from dataclasses import dataclass, field
from typing import Generator, Any

import numpy as np
from numpy import ndarray, dtype

from Tracker.misc import boxes_center

corners_path = r"D:\PyCharm Com\Project\Traffic-Vision-\doors_corners.txt"
door_names = ("women", "men", "kid")


@dataclass(slots=True)
class Door:
    name: str
    corners: np.ndarray[int]
    center: tuple[int, int] = field(init=False)

    def __post_init__(self):
        self.center = np.ravel(boxes_center(self.corners)).astype(int)


class DoorList:

    def __init__(self, doors: list[Door]) -> None:
        self.doors = doors

    @classmethod
    def from_file(cls, path: str):
        """
        TODO: документация
        :param path:
        :return:
        """
        doors = list()
        with open(path) as file:
            for row in file.readlines():
                name, *corners_inner = row.split()
                corners_inner = np.fromiter(map(int, corners_inner), int)
                doors.append(Door(name, corners_inner))
        return cls(doors)

    def __iter__(self) -> Generator[Door, None, None]:
        yield from self.doors

    @property
    def centers(self) -> tuple[tuple[int, int], ...]:
        """
        TODO: документация
        :return:
        """
        return tuple(door.center for door in self.doors)


def update_corners(corners_inner: ndarray[Any, dtype[Any]]):
    """
    TODO: документация
    :param corners_inner:
    :return:
    """
    with open(corners_path, 'w') as file:
        for name, row in zip(door_names, corners_inner):
            print(name, " ".join(map(str, row)), file=file)


def corners_from_norm(corners_inner: list[list[float]],
                      image_shape: tuple[int, int]) -> ndarray[Any, dtype[Any]]:
    """
    TODO: документация
    :param corners_inner:
    :param image_shape:
    :return:
    """
    corners_inner = np.array(corners_inner)
    corners_inner[..., (0, 2)] *= image_shape[0]
    corners_inner[..., (1, 3)] *= image_shape[1]
    return corners_inner.astype(int)


def corners_from_width_height(data: list[list[int]]) -> ndarray[Any, dtype[Any]]:
    """
    TODO: документация
    :param data:
    :return:
    """
    data = np.array(data)
    data[..., 2:] += data[..., :2]
    return data


Doors = DoorList.from_file(corners_path)

if __name__ == "__main__":
    image_size = 1920, 1080
    norm = [
        [0.11953125, 0.15625, 0.03984375, 0.1484375],
        [0.17421875, 0.1328125, 0.04140625, 0.15],
        [0.4265625, 0.065625, 0.028125, 0.1296875],
    ]

    corners = corners_from_norm(norm, image_size)
    update_corners(corners)

    width_height = [
        [175, 67, 108, 208],
        [283, 38, 105, 206],
        [785, 0, 63, 149]
    ]

    corners = corners_from_width_height(width_height)
    update_corners(corners)

    for d in Doors:
        print(d)

    print(Doors.centers)
