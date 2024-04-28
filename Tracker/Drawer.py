from itertools import product

import cv2
from cv2.typing import MatLike
from ultralytics.engine.results import Results

from Config.Context import Drawer as config
from Tracker.Doors import Door, Doors
from Tracker.People import People


class Drawer:
    def show(self, image: MatLike) -> bool:
        cv2.imshow("frame", image)
        return cv2.waitKey(1) & 0xFF == ord("q")

    def debug(self, results: Results, persons: list[People], 
              count: tuple[int, int]=None):
        frame = results.orig_img
        if config.boxes:
            frame = results.plot()
        if config.lines:
            self.draw_lines(frame, persons)
        if config.doors:
            self.draw_doors(frame)
        if config.points:
            self.draw_points(frame, persons)
        if count != None:
            self.draw_count(frame, count)
        if config.resize:
            frame = cv2.resize(frame, (0, 0), None, *config.resize)
        return frame
    
    def draw_lines(self, frame: MatLike, people: list[People]):
        for person, door in product(people, Doors.centers):
            cv2.line(frame, person.position, door,
                    color=(102, 255, 51), thickness=5)
    
    def draw_doors(self, frame: MatLike):
        for door in Doors:
            x, y = door.center
            r = 10
            pt1 = door.corners[:2]
            pt2 = door.corners[2:]
            cv2.rectangle(frame, pt1, pt2, color=(255, 255, 255))
            cv2.putText(frame, door.name[0], org=(x - r, y - r * 2),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=1, color=(255, 255, 255),
                        thickness=2)

    def draw_points(self, frame: MatLike, people: list[People]):
        for person in people:
            cv2.circle(frame, person.position, radius=10, 
                       color=(255, 0, 0), thickness=-1)

    def draw_count(self, frame: MatLike, in_out_count: tuple[int, int]):
        text = "/".join(map(str, in_out_count))
        cv2.putText(frame, text, (8, frame.shape[0]-16),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=1, color=(255, 255, 255),
                    thickness=2)