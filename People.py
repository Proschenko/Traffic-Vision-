import numpy

from Doors import Doors


class People:
    def __init__(self, id_person, class_person, coordinates, conf) -> None:
        self.id_person: int = id_person
        self.model_class: str = class_person  # Eсли циферками класс задается то можно в случае чего преобразовывать
        # в строку
        self.confidence: float = conf

        self.center_x: int = coordinates[0]
        self.center_y: int = coordinates[1]

    def print_person(self):
        """
        Выводит всю информацию о человеке
        :return:
        """
        print("ID:", self.id_person)
        print("Class:", self.model_class)
        print("Confidence:", self.confidence)
        print("X:", self.center_x)
        print("Y:", self.center_y)

    def check_how_close_to_door(self):
        """
        Смотрим насколько близко находится к двери
        :return:
        """
        door_centers = Doors.centers

        for door_center in door_centers:
            distance_to_door = numpy.sqrt((self.center_x - door_center[0]) ** 2 + (self.center_y - door_center[1]) ** 2)
            if distance_to_door < 20:
                # self.print_person()
                return 2  # Человек находится в пределах дверной рамы
            if distance_to_door < 100:
                return 1  # Человек находится около дверной рамы
            else:
                return 0  # Человек находится далеко от дверной рамы
