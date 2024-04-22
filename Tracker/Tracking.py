from datetime import datetime, timedelta
from typing import Tuple

import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.engine.results import Results

from DataBase.Redis import Redis
from Tracker.Debug_drawer import draw_debug
from Tracker.misc import Action, boxes_center, crop_image
from Tracker.People import Gender, People
from Tracker.StreamCatcher import ParallelStream

IGNORE = Gender.Cleaner, Gender.Coach


class State:
    def __init__(self, close: bool, gender: Gender):
        self.newborn = True
        self.close = close
        self.gender_count = [0] * len(Gender)
        self.update_gender(gender)

    def update(self, close: bool):
        self.newborn = self.newborn and self.close == close
        self.close = close

    def update_gender(self, current: Gender):
        self.gender_count[current.value] += 1

    @property
    def gender(self) -> Gender:
        return Gender(np.argmax(self.gender_count))


def is_entered(close: bool, state: State) -> bool:
    return state.newborn and state.close > close


def is_exited(close: bool, state: State) -> bool:
    return state.close < close


def is_passed(close: bool, state: State) -> bool:
    return not state.newborn and state.close > close


def check_action(close: bool, state: State) -> Action | None:
    if is_entered(close, state):
        return Action.Enter
    if is_exited(close, state):
        return Action.Exit
    if is_passed(close, state):
        return Action.Pass


def parse_results(results: Results) -> list[People]:
    """
    Создаёт список объектов People на основе result

    :param results: Результат обнаружения объектов
    :type results: Results
    :return: Список объектов People
    :rtype: list[People]
    """
    boxes = results.boxes.cpu().numpy()
    centers = boxes_center(boxes.xyxy)
    people = list()
    for box, center in zip(boxes, centers.astype(int)):
        id = box.id and int(box.id)
        gender = Gender(int(*box.cls))
        people.append(People.from_position(id, gender, center))
    return people


class Tracking:
    def __init__(self, model: YOLO) -> None:
        self.model = model
        self.history: dict[int, State] = dict()
        self.in_out = [0, 0]
        self.redis = Redis()

    def process_video_with_tracking(self, rtsp_url: str, show_video=True, save_path=None):
        """
        TODO: документация
        :param rtsp_url:
        :param show_video:
        :param save_path:
        :return:
        """
        save_video = save_path is not None
        out = None

        # TODO: конфиг должен читаться из отдельного файла
        model_args = {"iou": 0.4, "conf": 0.5, "persist": True,
                      "imgsz": 640, "verbose": False,
                      "tracker": "botsort.yaml"}

        frame_step = 4
        stream = ParallelStream(rtsp_url)
        for frame in stream.iter_actual():
            frame = crop_image(frame)

            # Process the frame with your YOLO model
            results = self.model.track(frame, **model_args)[0]

            persons = parse_results(results)
            frame_time = stream.start_time + timedelta(milliseconds=stream.position)
            self.tracking(persons, frame_time)

            if save_video or show_video:
                debug_frame = draw_debug(results, persons, draw_lines=False, 
                                         in_out_count=self.in_out)

            if save_video:
                if out is None:
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    fps = 25
                    frameSize = debug_frame.shape[-2::-1]
                    out = cv2.VideoWriter(save_path, fourcc, fps, frameSize)
                out.write(debug_frame)

            if show_video:
                cv2.imshow("frame", debug_frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        if save_video:
            out.release()
        cv2.destroyAllWindows()

    def tracking(self, persons: list[People], time: datetime):
        for person in persons:
            result = self.track(person)
            if result is None:
                continue
            self.update_counters(*result, time)

    def track(self, person: People) -> tuple[Gender, Action | None] | None:
        if person.id is None:
            return
        state = self.history.get(person.id, None)
        if state is None:
            self.history[person.id] = State(person.is_close, person.gender)
            return
        state.update_gender(person.gender)
        if state.gender in IGNORE:
            return
        action = check_action(person.is_close, state)
        state.update(person.is_close)
        return state.gender, action

    def update_counters(self, gender: Gender, action: Action, time: datetime):
        match action:
            case Action.Enter:
                self.in_out[0] += 1
                self.redis.entered(gender, time)
            case Action.Exit:
                self.in_out[1] += 1
                self.redis.exited(gender, time)
            case Action.Pass:
                self.in_out[1] -= 1
                self.redis.passed(gender, time)
            case _:
                return
        print(f"На данный момент Зашло: {self.in_out[0]} Вышло: {self.in_out[1]}")


if __name__ == "__main__":
    pass
