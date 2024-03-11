from dataclasses import dataclass

from ultralytics.engine.results import Results

from Doors import Doors, Door
from misc import Distances, Location, boxes_center, dist


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
    
    def nearest_door(self) -> Door:
        return min(Doors, key=lambda d: dist(*d.center, *self.position))

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


@dataclass
class State:
    location: Location
    newborn: bool = True

    def update(self, new_location: Location):
        if self.location is new_location:
            return

        self.location = new_location
        self.newborn = False


def parse_results(results: Results) -> list[People]:
    """
    Создаёт список объектов People на основе result

    :param results: Результат обнаружения объектов
    :type results: Results
    :return: Список объектов People
    :rtype: list[People]
    """
    if results.boxes.id is None:
        return list()
    boxes = results.boxes.numpy()
    centers = boxes_center(boxes.xyxy)
    people = list()
    for box, center in zip(boxes, centers.astype(int)):
        people.append(People(int(*box.id), int(*box.cls), *box.conf, tuple(center)))
    return people
