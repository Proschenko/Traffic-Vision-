from dataclasses import dataclass
from Doors import Doors
from misc import Distances, Location, dist


@dataclass(frozen=True, slots=True)
class People:
    id_person: int
    model_class: str
    confidence: float
    position: tuple[int, int]

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
        print("X:", self.position[0])
        print("Y:", self.position[1])

    def check_how_close_to_door(self) -> Location:
        """
        Смотрим насколько близко находится к двери
        :return: Возвращаем код, который означает как далеко человек находится от двери 
            0 - далеко; 1 - около дверной рамы; 2 - в пределах дверной рамы.
        :rtype: int
        """
        door_centers = Doors.centers
        # print(door_centers)
        for door_center in door_centers:
            distance_to_door = dist(*self.position, *door_center)
            # print(distance_to_door, door_center, (self.center_x, self.center_y))
            if distance_to_door < Distances.Close:
                # self.print_person()
                return Location.Close
            elif distance_to_door < Distances.Around:
                return Location.Around
        return Location.Far
