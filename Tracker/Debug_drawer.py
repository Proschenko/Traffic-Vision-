import cv2
from cv2.typing import MatLike
from ultralytics.engine.results import Results

from Tracker.Doors import Door, Doors
from Tracker.misc import Distances
from Tracker.People import People


def draw_debug(results: Results, people: list[People],
               resize: tuple[float, float] = (0.75, 0.75),
               draw_boxes=True, draw_doors=True, draw_lines=True) -> MatLike:
    """
    Рисует дебаг информицию

    :param results: Результат обнаружения модели
    :type results: Results
    :param people: Список человеков
    :type people: list[People]
    :param draw_boxes: Надо ли рисовать коробки людей, defaults to True
    :type draw_boxes: bool, optional
    :param draw_doors: Надо ли рисовать коробки дверей, defaults to True
    :type draw_doors: bool, optional
    :param draw_lines: Надо ли рисовать линии от людей до дверей, defaults to True
    :type draw_lines: bool, optional
    :return: Кадр с нарисованной дебаг информацией
    :rtype: MatLike
    """
    frame = results.orig_img
    if draw_boxes:
        frame = results.plot()
    if draw_lines:
        line_door_person(frame, people)
    if draw_doors:
        for door in Doors:
            draw_door(frame, door)
    return cv2.resize(frame, (0, 0), None, *resize)


def draw_door(frame: MatLike, door: Door):
    """
    Рисует прямоугольник вокруг двери и окружности дистанций

    :param frame: Кадр из записи для обработки
    :type frame: MatLike
    :param door: Дверь для отрисовки
    :type door: Door
    """
    x, y = door.center
    r = 10
    pt1 = door.corners[:2]
    pt2 = door.corners[2:]
    cv2.rectangle(frame, pt1, pt2, color=(255, 255, 255))
    cv2.circle(frame, (x, y), radius=Distances.Close, color=(0, 0, 255))
    cv2.putText(frame, door.name[0], org=(x - r, y - r * 2),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=1, color=(255, 255, 255),
                thickness=2)


def line_door_person(frame: MatLike, people: list[People], ) -> None:
    """
    Рисует линии от человека к 3м дверям, обращаясь к координатам из enum Doors

    :param frame: Кадр из записи для обработки
    :type frame: np.ndarray
    :param people: Список человеков
    :type people: list[People]
    """
    for person in people:
        for door in Doors.centers:
            cv2.line(frame, person.position, door,
                     color=(102, 255, 51), thickness=5)
