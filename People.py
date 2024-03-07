import numpy

from Doors import Doors


class People:
    def __init__(self, id_person, class_person, coordinates, conf) -> None:
        self.id_person: int = id_person
        self.model_class: str = class_person  # Eсли циферками класс задается то можно в случае чего преобразовывать
        # в строку
        self.confidence: float = conf

        self.center_x: int = None
        self.center_y: int = None

        self._set_coordinates(coordinates)

    def _set_coordinates(self, coordinates):
        """
        Ставим новые нормализованные координаты
        """
        self.center_x = coordinates[0]
        self.center_y = coordinates[1]

    def check_how_close_to_door(self):
        """
        Смотрим насколько близко находится к двери
        :return:
        """
        # door_centers = [Doors.kid_center_door.value, Doors.women_center_door.value, Doors.men_center_door.value]
        door_centers = Doors.centers

        for door_center in door_centers:
            # print("People", self.center_x, self.center_y, "Doors", door_center[0], door_center[1])
            distance_to_door = numpy.sqrt((self.center_x - door_center[0]) ** 2 + (self.center_y - door_center[1]) ** 2)
            if distance_to_door < 20:
                print(distance_to_door)
                self.print_person()
                return
        # print("Not close enough")

    # Обновление структуры, новые координаты, новая уверенность в себе(в точности предсказания), сразу проверяем
    # насколько близко к двери
    def update(self, coordinates, conf):
        self.confidence = conf
        self._set_coordinates(coordinates)
        self.check_how_close_to_door()

    # Выводит всю инфу
    def print_person(self):
        print("ID:", self.id_person)
        print("Class:", self.model_class)
        print("Confidence:", self.confidence)
        print("X:", self.center_x)
        print("Y:", self.center_y)
