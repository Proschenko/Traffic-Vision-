from collections import defaultdict, deque
from functools import partial

import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.engine.results import Results

from Debug_drawer import draw_debug
from misc import Location
from People import People, State, parse_results


class Tracking:
    def __init__(self) -> None:
        self.image_width = 1920
        self.image_height = 1080
        self.id_state = dict()
        self.id_location: dict[int, State] = dict()
        self.predict_history = np.empty(10, dtype=Results)
        self.in_out = [0, 0]

    def process_video_with_tracking(self, model: YOLO, video_path: str, show_video=True, save_path=None):
        """
        TODO: документация
        :param model:
        :param video_path:
        :param show_video:
        :param save_path:
        :return:
        """
        save_video = save_path is not None
        out = None

        model_args = {"iou": 0.4, "conf": 0.5, "persist": True,
                      "imgsz": 640, "verbose": False,
                      "tracker": "botsort.yaml",
                      "vid_stride": 7}

        for frame_number, results in enumerate(model.track(video_path, stream=True, **model_args)):
            if save_video:
                if out is None:
                    fps = 25
                    shape = results.orig_shape
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    out = cv2.VideoWriter(save_path, fourcc, fps, shape)
                out.write(results.plot())

            if show_video:
                frame = draw_debug(results, draw_lines=False)
                cv2.imshow("frame", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            self.tracking(results)
            print(f"На данный момент Вышло: {self.in_out[1]} Зашло: {self.in_out[0]}")
            # TODO: Замах на будущее
            # self.predict_history[frame_number % 10] = results
            #
            # if frame_number % 100 == 0 and frame_number != 0:
            #     self._tracking()

        if save_video:
            out.release()
        cv2.destroyAllWindows()

    def tracking(self, results: Results):
        """
        TODO: документация
        :param results:
        :return:
        """
        people = parse_results(results)
        for person in people:
            current_location = person.check_how_close_to_door()
            last_state, last_newborn = self.update_location_state(person, current_location)
            if last_state:
                self.handle_entry(person, last_state, last_newborn, current_location)
        
    def handle_entry(self, person: People, last_location: State, last_newborn: bool, current_location: Location):
        nearest_door = person.nearest_door()
        message = ""
        # print(last_state.location, current_location)
        if current_location is Location.Close and last_location is Location.Around:
            self.in_out[1] += 1
            message = "Я вышел!"
        if not last_newborn and current_location is Location.Around and last_location is Location.Close:
            self.in_out[1] -= 1
            message = "Погодите-ка, я просто мимо проходил"
        if message:
            print(message, nearest_door.name)

    def update_location_state(self, person: People, location: Location) -> Location:
        if person.id_person not in self.id_location:
            self.id_location[person.id_person] = State(location)
            self.in_out[0] += 1
            nearest_door = person.nearest_door()
            print("Я родился!", nearest_door.name)
            return None, None
        last_location, last_newborn = self.id_location[person.id_person].location, self.id_location[person.id_person].newborn
        self.id_location[person.id_person].update(location)
        return last_location, last_newborn

    def _tracking(self):
        # TODO: Так будет работать логика будущего, сначала парсинг result, потом парсинг массива каждым методом
        # pass
        frame_objects = np.empty(10, dtype=object)
        for i, frame_result in enumerate(self.predict_history):
            frame_objects[i] = parse_results(frame_result)

        self._door_touch(frame_objects)

        # self.people_coming(person)
        # self._people_leave(frame_objects)

    def _people_coming(self, person: People):
        # TODO: Проверка, человек ушел
        pass

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


if __name__ == "__main__":
    pass
