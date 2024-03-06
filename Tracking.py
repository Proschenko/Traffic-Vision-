import enum

import cv2
import numpy
import numpy as np
from tqdm import tqdm
from ultralytics import YOLO
from ultralytics.engine.results import Results


def boxes_center(corners: np.ndarray[float, float]) -> np.ndarray[float, float]:
    """
    Находит центры прямоугольников, которые заданны двумя углами.

    :param corners: Массив координат размера (n, 4) формата xyxy
    :type corners: np.ndarray[float, float]
    :return: Массив координат размера (n, 2) формата xy
    :rtype: np.ndarray[float, float]
    """
    return np.mean(corners.reshape((-1, 2, 2)), 1)

class People:
    def __init__(self, class_person, coordinates, conf) -> None:

        self.model_class: str = class_person  # если циферками класс задается то можно в случае чего преобразовывать в строку
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

    # Смотрим насколько близко находится к двери
    def check_how_close_to_door(self):
        # door_centers = [Doors.kid_center_door.value, Doors.women_center_door.value, Doors.men_center_door.value]
        door_centers = [Doors.women_center_door.value]

        for door_center in door_centers:
            print("People", self.center_x, self.center_y, "Doors", door_center[0], door_center[1])
            distance_to_door = numpy.sqrt((self.center_x - door_center[0]) ** 2 + (self.center_y - door_center[1]) ** 2)
            print(distance_to_door)
            if distance_to_door < 50:
                self.print_person()
                return
        # print("Not close enough")

    # Обновление структуры, новые координаты, новая уверенность в себе(в точности предсказания), сразу проверяем насколько близко к двери
    def update(self, coordinates, conf):
        self.confidence = conf
        self._set_coordinates(coordinates)
        self.check_how_close_to_door()

    # Выводит всю инфу
    def print_person(self):
        print("Class:", self.model_class)
        print("Confidence:", self.confidence)
        print("X:", self.center_x)
        print("Y:", self.center_y)


class Doors(enum.Enum):
    women_center_door = (185, 175)
    men_center_door = (248, 151)
    kid_center_door = (564, 93)


# class Door:
#     def __init__(self) -> None:
#         self.women_center_door = (0.14453125, 0.244140625)
#         self.men_center_door = (0.19375, 0.2109375)
#         self.kid_center_door = (0.440625, 0.13046875000000002)


#     def get_women_door_coordinates(self):
#         """
#         Возвращает абсолютные координаты центра дверей для женщин.
#         """
#         return Tracking.get_normalized_coordinates(self.women_center_door)

#     def get_men_door_coordinates(self):
#         """
#         Возвращает абсолютные координаты центра дверей для мужчин.
#         """
#         return Tracking.get_normalized_coordinates(self.men_center_door)

#     def get_kid_door_coordinates(self):
#         """
#         Возвращает абсолютные координаты центра дверей для детей.
#         """
#         return Tracking.get_normalized_coordinates(self.kid_center_door)


class Tracking:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_normalized_coordinates(center):
        """
        Преобразует нормализованные координаты центра в абсолютные координаты для разрешения изображения.
        """
        image_width = 1920
        image_height = 1080
        absolute_x = int(center[0] * image_width)
        absolute_y = int(center[1] * image_height)
        return absolute_x, absolute_y

    def process_video_with_tracking(self, model: YOLO, video_path: str, show_video=True, save_path=None):
        save_video = save_path is not None
        out = None
        
        model_args = {"iou": 0.4, "conf": 0.5, "persist": True, 
                      "imgsz": 608, "verbose": False,
                      "tracker": "botsort.yaml",
                      "vid_stride": 3}

        for results in model.track(video_path, stream=True, **model_args):
            if save_video:
                if out is None:
                    fps = 25
                    shape = results.orig_shape
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    out = cv2.VideoWriter(save_path, fourcc, fps, shape)

                out.write(results.plot())

            if show_video:
                frame = cv2.resize(results.plot(), (0, 0), fx=0.75, fy=0.75)
                cv2.imshow("frame", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            self._tracking(results)

        if save_video:
            out.release()
        cv2.destroyAllWindows()

    def _tracking(self, results):
        people_objects = self.parse_results(results)

        for person in people_objects:
            person.check_how_close_to_door()

    def parse_results(self, results: Results) -> list[People]:
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
        for box, center in zip(boxes, centers):
            people.append(People(int(*box.cls), center, *box.conf))
        return people


    @staticmethod
    def _process_tracking_results(tracking_results):
        """
        Process tracking results to compute the class, confidence score, and center of each bounding box.

        Parameters:
        - tracking_results: List of tracking results, where each result contains information about tracked objects.

        Returns:
        - List of People objects, where each object represents a person with their class, confidence score, and center coordinates.
        """
        result_objects = []

        for result in tracking_results:
            if result.boxes.id is not None:  # Check if there is a valid ID
                box = result.boxes.xyxy.cpu().numpy().astype(int)[0]
                center_x = (box[2] + box[0]) // 2
                center_y = (box[1] + box[3]) // 2
                confs = result[0].boxes.conf.tolist()
                class_object = result[0].boxes.cls.tolist()
                # print(int(class_object[0]), (center_x, center_y), confs[0])
                # Create a People object and append it to the list
                person = People(int(class_object[0]), (center_x, center_y), confs[0])
                result_objects.append(person)

        return result_objects


if __name__ == "__main__":
    a = People("kid", (0.44, 0.13), 0.952134)
    a.check_how_close_to_door()
