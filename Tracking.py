import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.engine.results import Results
from OperationsWithCordinates import OperationsWithCoordinates

from People import People
from Doors import Doors


class Tracking:
    def __init__(self) -> None:
        self.image_width = 1920
        self.image_height = 1080

    def process_video_with_tracking(self, model: YOLO, video_path: str, show_video=True, save_path=None):
        save_video = save_path is not None
        out = None

        model_args = {"iou": 0.4, "conf": 0.5, "persist": True,
                      "imgsz": 640, "verbose": False,
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
                self.line_door_person(frame, results, coef=0.75)
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

    @staticmethod
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
        centers = OperationsWithCoordinates.boxes_center(boxes.xyxy)
        people = list()
        for box, center in zip(boxes, centers):
            people.append(People(int(*box.cls), center, *box.conf))
        return people

    def line_door_person(self, frame: np.ndarray , results: Results, coef: float = 1) -> None:
        """
        Рисует линии от человека к 3м дверям, обращаясь к координатам из enum Doors

        :param frame: Кадр из записи для обработки
        :type frame: np.ndarray
        :param results: Результат обнаружения объектов
        :type results: Results
        :param coef: Коэффициент масштабирования изображения
        :type coef: float
        :return: Ничего
        :rtype: None
        """
        people_objects = self.parse_results(results)
        doors = (Doors.men_center_door.value, Doors.women_center_door.value, Doors.kid_center_door.value)
        for person in people_objects:
            for door in doors:
                cv2.line(frame, (int(person.center_x*coef), int(person.center_y*coef)),
                        (int(door[0]*coef), int(door[1]*coef)), (102, 255, 51), 5)




if __name__ == "__main__":
    a = People("kid", (0.44, 0.13), 0.952134)
    a.check_how_close_to_door()
