import enum
import numpy as np
from OperationsWithCordinates import OperationsWithCoordinates


class Doors(enum.Enum):
    women_center_door = (277, 263)
    men_center_door = (372, 227)
    kid_center_door = (846, 140)

    # _old_women_center_door = (277, 263)
    # _old_men_center_door = (372, 227)
    # _old_kid_center_door = (846, 140)


class _Door:
    def __init__(self, _women_coordinates, _men_coordinates, _kid_coordinates) -> None:
        self.women_center_door = np.ravel(OperationsWithCoordinates.boxes_center(women_coordinates))
        self.men_center_door = np.ravel(OperationsWithCoordinates.boxes_center(men_coordinates))
        self.kid_center_door = np.ravel(OperationsWithCoordinates.boxes_center(kid_coordinates))

        print(self.women_center_door)
        print(self.men_center_door)
        print(self.kid_center_door)

        # Новые координаты
        # [0.0796875  0.15234375]
        # [0.1078125  0.14140625]
        # [0.22734375 0.09765625]

        # Старые координаты
        # self.women_center_door = (0.14453125, 0.244140625)
        # self.men_center_door = (0.19375, 0.2109375)
        # self.kid_center_door = (0.440625, 0.13046875000000002)

    @staticmethod
    def _get_normalized_coordinates(center):
        """
        Преобразует нормализованные координаты центра в абсолютные координаты для разрешения изображения.
        """
        if center is None:
            return None

        image_width = 1920
        image_height = 1080
        absolute_x = int(center[0] * image_width)
        absolute_y = int(center[1] * image_height)
        return absolute_x, absolute_y

    def get_women_door_coordinates(self):
        """
        Возвращает абсолютные координаты центра дверей для женщин.
        """
        return self._get_normalized_coordinates(self.women_center_door)

    def get_men_door_coordinates(self):
        """
        Возвращает абсолютные координаты центра дверей для мужчин.
        """
        return self._get_normalized_coordinates(self.men_center_door)

    def get_kid_door_coordinates(self):
        """
        Возвращает абсолютные координаты центра дверей для детей.
        """
        return self._get_normalized_coordinates(self.kid_center_door)


if __name__ == "__main__":
    # Новые координаты
    # women_coordinates = np.array([0.11953125, 0.15625, 0.03984375, 0.1484375])
    # men_coordinates = np.array([0.17421875, 0.1328125, 0.04140625, 0.15])
    # kid_coordinates = np.array([0.4265625, 0.065625, 0.028125, 0.1296875])
    # women_coordinates = [0.11953125, 0.15625, 0.03984375, 0.1484375]
    # men_coordinates = [0.17421875, 0.1328125, 0.04140625, 0.15]
    # kid_coordinates = [0.4265625, 0.065625, 0.028125, 0.1296875]

    # Старые координаты
    women_coordinates = np.array([0.11953125, 0.15625, 0.03984375, 0.1484375])
    men_coordinates = np.array([0.17421875, 0.1328125, 0.04140625, 0.15])
    kid_coordinates = np.array([0.4265625, 0.065625, 0.028125, 0.1296875])

    door = _Door(women_coordinates, men_coordinates, kid_coordinates)

    print("women_center_door =", door.get_women_door_coordinates())
    print("men_center_door =", door.get_men_door_coordinates())
    print("kid_center_door =", door.get_kid_door_coordinates())
