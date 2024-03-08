from Doors import Doors
from misc import Position, dist


class People:
    def __init__(self, id_person, class_person, coordinates, conf) -> None:
        self.id_person: int = id_person
        self.model_class: str = class_person  # Eсли циферками класс задается то можно в случае чего преобразовывать
        # в строку
        self.confidence: float = conf

        self.center_x: int = coordinates[0]
        self.center_y: int = coordinates[1]

    def get_person_id(self):
        return self.id_person

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

    def check_how_close_to_door(self) -> Position:
        """
        Смотрим насколько близко находится к двери
        :return: Возвращаем код, который означает как далеко человек находится от двери 
            0 - далеко; 1 - около дверной рамы; 2 - в пределах дверной рамы.
        :rtype: int
        """
        door_centers = Doors.centers
        # print(door_centers)
        for door_center in door_centers:
            distance_to_door = dist(self.center_x, self.center_y, *door_center)
            # print(distance_to_door, door_center, (self.center_x, self.center_y))
            if distance_to_door < 20:
                # self.print_person()
                return Position.Close
            elif distance_to_door < 100:
                return Position.Around
        return Position.Far
