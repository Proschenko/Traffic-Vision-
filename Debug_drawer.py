import cv2
import numpy as np
from cv2.typing import MatLike
from ultralytics.engine.results import Results

from Doors import Door, Doors
from misc import Distances
from People import parse_results


def draw_debug(results: Results,
               draw_boxes=True, draw_doors=True, draw_lines=True) -> MatLike:
    frame = results.orig_img
    if draw_boxes:
        frame = results.plot()
    if draw_lines:
        line_door_person(frame, results)
    if draw_doors:
        for door in Doors:
            draw_door(frame, door)
    return cv2.resize(frame, (0, 0), fx=0.75, fy=0.75)


def draw_door(frame: MatLike, door: Door):
    x, y = door.center
    r = 10
    pt1 = door.corners[:2]
    pt2 = door.corners[2:]
    cv2.rectangle(frame, pt1, pt2, color=(255, 255, 255))
    cv2.circle(frame, (x, y), radius=Distances.Close, color=(0, 0, 255))
    cv2.circle(frame, (x, y), radius=Distances.Around, color=(0, 255, 0))
    cv2.putText(frame, door.name[0], org=(x - r, y - r * 2),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=1, color=(255, 255, 255),
                thickness=2)


def line_door_person(frame: np.ndarray, results: Results, coef: float = 1) -> None:
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
    people_objects = parse_results(results)
    for person in people_objects:
        for door in Doors.centers:
            cv2.line(frame, person.position, door,
                     color=(102, 255, 51), thickness=5)
