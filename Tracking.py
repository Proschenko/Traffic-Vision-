from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum, auto
from itertools import count, takewhile

import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.engine.results import Results

from DataBase import Redis
from Debug_drawer import draw_debug
from misc import Location, boxes_center
from People import People


class Action(Enum):
    Entered = auto()
    Exited = auto()
    Passed = auto()


@dataclass
class State:
    close: bool
    entering: bool

    def update(self, close: bool):
        if self.close == close:
            return
        self.close = close
        self.entering = False


class Tracking:
    def __init__(self, model: YOLO) -> None:
        self.model = model
        self.id_location: dict[int, State] = dict()
        self.predict_history = np.empty(10, dtype=Results)
        self.in_out = [0, 0]
        self.redis = Redis()

    def process_video_with_tracking(self, rtsp_url: str, show_video=True, save_path=None):
        """
        TODO: документация
        :param model:
        :param rtsp_url:
        :param show_video:
        :param save_path:
        :return:
        """
        save_video = save_path is not None
        out = None

        model_args = {"iou": 0.4, "conf": 0.5, "persist": True,
                      "imgsz": 640, "verbose": False,
                      "tracker": "botsort.yaml"}
        frame_step = 4

        cap = cv2.VideoCapture(rtsp_url)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 25*8)
        position_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
        start_time = datetime.now() - timedelta(milliseconds=position_ms)

        if not cap.isOpened():
            raise Exception("Error: Could not open video file.")

        fps = int(cap.get(cv2.CAP_PROP_FPS))

        for frame_number in takewhile(lambda _: cap.isOpened(), count()):
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_number % frame_step != 0:
                continue
            frame = frame[:300, :950]

            # Process the frame with your YOLO model
            results = self.model.track(frame, **model_args)[0]
            
            persons = self.parse_results(results)
            position_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
            frame_time = start_time + timedelta(milliseconds=position_ms)
            self.tracking(persons, frame_time)

            if save_video or show_video:
                debug_frame = draw_debug(results, persons, draw_lines=False)

            if save_video:
                if out is None:
                    height, width, _ = debug_frame.shape
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    out = cv2.VideoWriter(save_path, fourcc, fps//frame_step, (width, height))
                out.write(debug_frame)

            if show_video:
                cv2.imshow("frame", debug_frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        cap.release()
        if save_video:
            out.release()
        cv2.destroyAllWindows()

    @staticmethod
    def is_person_entered(close: bool, history: State | None) -> bool:
        return history is None and close

    @staticmethod
    def is_person_exited(close: bool, history: State | None) -> bool:
        return close and history is not None and not history.close

    @staticmethod
    def is_person_passed(close: bool, history: State | None) -> bool:
        return not close and history is not None and history.close and not history.entering

    def check_action(self, close: bool, history: State | None) -> Action | None:
        if self.is_person_entered(close, history):
            return Action.Entered
        if self.is_person_exited(close, history):
            return Action.Exited
        if self.is_person_passed(close, history):
            return Action.Passed

    def tracking(self, persons: list[People], time: datetime):
        for person in persons:
            close = person.is_close()
            history = self.id_location.get(person.id_person, None)
            action = self.check_action(close, history)
            match action:
                case Action.Entered:
                    # print("Я родилсо")
                    self.in_out[0] += 1
                    self.redis.increment("enter", person.model_class, time)
                case Action.Exited:
                    # print("Я ухожук")
                    self.in_out[1] += 1
                    self.redis.increment("exit", person.model_class, time)
                case Action.Passed:
                    # print("Я передумал")
                    self.in_out[1] -= 1
                    self.redis.decrement("exit", person.model_class, time)
            if action is not None:
                print(f"На данный момент Вышло: {self.in_out[1]} Зашло: {self.in_out[0]}")
            if history is None:
                self.id_location[person.id_person] = State(close, action is Action.Entered)
            else:
                self.id_location[person.id_person].update(close)

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
        for box, center in zip(boxes, centers.astype(int)):
            people.append(People(int(*box.id), self.model.names[int(*box.cls)], *box.conf, center))
        return people

    # region Пусть пока подумает над своим поведением
    def _tracking2(self):
        # TODO: Так будет работать логика будущего(наверное), сначала парсинг result,
        #  потом парсинг массива каждым методом
        # pass
        frame_objects = np.empty(10, dtype=object)
        for i, frame_result in enumerate(self.predict_history):
            frame_objects[i] = self.parse_results(frame_result)

        self._door_touch(frame_objects)

        # self.people_coming(person)
        # self._people_leave(frame_objects)

    @staticmethod
    def _door_touch(peoples_from_frame) -> None:
        # TODO: Не работает, нужно разбираться почему
        person_door_relationship = dict()
        for frame_object in peoples_from_frame:
            for person in frame_object:
                person_id = person.get_person_id()
                location_person = person.check_how_close_to_door()
                if not person_door_relationship.get(person_id):
                    person_door_relationship[person_id] = location_person
                    continue
                last_location = person_door_relationship[person_id]
                if last_location == Location.Far and location_person == Location.Close:
                    print(
                        "Мама что произошло за за 7 фреймов")  # Смотрим случай когда за 7 кадров человек улетел куда-то
                elif last_location == Location.Around and location_person == Location.Close:
                    print("Человек вошёл в дверь")
                    person.print_person()
                elif last_location == Location.Close and location_person == Location.Around:
                    print("Человек вышел из двери")
                    person.print_person()
                elif last_location == Location.Close and location_person == Location.Far:
                    print("Мама что произошло за за 7 фреймов")
                person_door_relationship[person_id] = location_person

    # endregion


if __name__ == "__main__":
    pass
