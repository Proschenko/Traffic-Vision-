if __name__ == "__main__":
    import sys
    from os.path import dirname
    sys.path.append(dirname(__file__).rpartition('\\')[0])

from itertools import count
from multiprocessing import freeze_support
from time import sleep
from typing import Generator

import cv2
from cv2.typing import MatLike
from tqdm import tqdm
from ultralytics import YOLO

from Tracker.Debug_drawer import draw_debug
from Tracker.misc import crop_image
from Tracker.People import People
from Tracker.StreamCatcher import ParallelStream
from Tracker.Tracking import Tracking


def save() -> Generator[None, tuple[MatLike, list[People]], None]:
    directory = ("D:/я у мамы программист/3 курс 2 семестр IT-проекты/"
                 "Traffic-Vision-/self development images/")
    for i in count():
        image, persons = yield
        name = f"frame_{i:08}"
        for oleg in sorted(p.model_class for p in persons):
            name += f"_{oleg}"
        cv2.imwrite(directory+name+".png", image)


if __name__ == "__main__":
    freeze_support()
    model_args = {"iou": 0, "conf": 0.6, "classes":(1, 2, 3),
                  "imgsz": 640, "verbose": False}
    model = YOLO('runs/detect/train8/weights/best.pt')
    Oleg = "Pepeg"
    # tracker = Tracking(model)

    # path = ("D:/я у мамы программист/3 курс 2 семестр IT-проекты"
    #         "/Traffic-Vision-/Test input video/test.mp4")
    url = "rtsp://rtsp:EL3gS7XV@80.91.19.85:58002/Streaming/Channels/101"
    stream = ParallelStream(url)
    # stream.jump_to(39*60)

    # frame_step = 40
    # total = (stream.n_frames - stream.frame_number) // frame_step
    prev = None
    saver = save()
    saver.send(None)
    for frame in tqdm(stream.iter_actual(), disable=False):
        frame = crop_image(frame)
        detected = model.track(frame, **model_args)[0]
        persons = Tracking.parse_results(Oleg, detected)

        cv2.imshow("frame", draw_debug(detected, persons, draw_lines=False))
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        if len(persons) > 1:
            # saver.send((frame, persons))
            sleep(1)
        prev = persons
