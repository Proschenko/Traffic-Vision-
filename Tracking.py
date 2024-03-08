import cv2
from ultralytics import YOLO

from Debug_drawer import draw_debug
from misc import Location
from People import People, parse_results


class Tracking:
    def __init__(self) -> None:
        self.image_width = 1920
        self.image_height = 1080
        self.id_state = dict()

    def process_video_with_tracking(self, model: YOLO, video_path: str, show_video=True, save_path=None):
        save_video = save_path is not None
        out = None

        model_args = {"iou": 0.4, "conf": 0.5, "persist": True,
                      "imgsz": 640, "verbose": False,
                      "tracker": "botsort.yaml",
                      "vid_stride": 3}

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

            self._tracking(results)

        if save_video:
            out.release()
        cv2.destroyAllWindows()

    def _tracking(self, results):
        people_objects = parse_results(results)

        for person in people_objects:
            if not self.id_state.get(person.get_person_id()):
                self.id_state[person.get_person_id()] = False
            code = person.check_how_close_to_door()  # сохраняем код с функции
            self.door_touch(person, code)  # смотрим если человек вошёл в дверь

    def door_touch(self, person: People, code: Location) -> None:
        """
        Выводит в консоль сообщение о том что человек вошёл в дверь, информацию о человеке
        :param person: Человек и его данные
        :type person: People
        :param code: код, возвращаемый People.check_how_close_to_door
        :type code: int
        :return: Ничего
        :rtype: None
        """
        if code is not Location.Close or self.id_state[person.get_person_id()]:
            return
        self.id_state[person.get_person_id()] = True
        print("Человек вошёл в дверь")
        person.print_person()
        
    def people_leave(self, person: People):
        location_person = person.check_how_close_to_door()
        if location_person is Location.Around:
            print("Человек находится рядом с дверной рамой")
        elif location_person is Location.Close:
            print("Человек находится внутри дверной раме")
        else:
            print("Человек находится далеко от двери")


if __name__ == "__main__":
    pass
