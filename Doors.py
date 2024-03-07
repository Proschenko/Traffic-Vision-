from dataclasses import dataclass, field
from typing import Generator

import numpy as np

from OperationsWithCordinates import boxes_center

corners_path = "doors_corners.txt"
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
        doors = list()
        with open(path) as file:
            for row in file.readlines():
                name, *corners = row.split()
                corners = np.fromiter(map(int, corners), int)
                doors.append(Door(name, corners))
        return cls(doors)

    def __iter__(self) -> Generator[Door, None, None]:
        yield from self.doors

    @property
    def centers(self) -> tuple[tuple[int, int]]:
        return tuple(d.center for d in self.doors)


def update_corners(corners: list[list[float]]):
    with open(corners_path, 'w') as file:
        for name, row in zip(door_names, corners):
            print(name, " ".join(map(str, row)), file=file)


def corners_from_norm(corners: list[list[float]],
                      image_shape: tuple[int, int]) -> np.ndarray[int, int]:
    corners = np.array(corners)
    corners[..., (0, 2)] *= image_shape[0]
    corners[..., (1, 3)] *= image_shape[1]
    return corners.astype(int)


def corners_from_width_height(data: list[list[int]]) -> np.ndarray[int, int]:
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
