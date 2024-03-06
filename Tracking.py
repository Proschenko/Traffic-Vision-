import cv2
import numpy as np
from cv2.typing import MatLike
from ultralytics import YOLO
from ultralytics.engine.results import Results
from OperationsWithCordinates import boxes_center

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
                frame = self.draw_debug(results, draw_boxes=False)
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
        centers = boxes_center(boxes.xyxy)
        people = list()
        for box, center in zip(boxes, centers):
            people.append(People(int(*box.cls), center, *box.conf))
        return people

    def draw_debug(self, results: Results,
                   draw_boxes=True, draw_doors=True, draw_lines=True) -> MatLike:
        frame = results.orig_img
        if draw_boxes:
            frame = results.plot()
        if draw_lines:
            self.line_door_person(frame, results)
        if draw_doors:
            self.draw_doors(frame)
        return cv2.resize(frame, (0, 0), fx=0.75, fy=0.75)
    
    def draw_doors(self, frame: MatLike):
        for door in Doors:
            x, y = door.center
            r = 10
            cv2.circle(frame, (x, y), radius=r, color=(0, 0, 255), 
                            thickness=-1)
            cv2.putText(frame, door.name[0], org=(x-r, y-r*2), 
                                fontFace=cv2.FONT_HERSHEY_SIMPLEX, 
                                fontScale=1, color=(255, 255, 255),
                                thickness=2)
    
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
        for person in people_objects:
            for door in Doors.centers:
                cv2.line(frame, (int(person.center_x*coef), int(person.center_y*coef)),
                        (int(door[0]*coef), int(door[1]*coef)), (102, 255, 51), 5)




if __name__ == "__main__":
    a = People("kid", (0.44, 0.13), 0.952134)
    a.check_how_close_to_door()
