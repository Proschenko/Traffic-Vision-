if __name__ == "__main__":
    import sys
    from os.path import dirname
    sys.path.append(dirname(__file__).rpartition('\\')[0])

from itertools import count
from multiprocessing import freeze_support
from time import sleep
from typing import Generator
from time import time

import cv2
from cv2.typing import MatLike
from tqdm import tqdm
from ultralytics import YOLO

from Tracker.Debug_drawer import draw_debug
from Tracker.misc import crop_image
from Tracker.People import People, Gender
from Tracker.StreamCatcher import ParallelStream
from Tracker.Tracking import parse_results


def save() -> Generator[None, tuple[MatLike, list[People]], None]:
    directory = ("D:/я у мамы программист/3 курс 2 семестр IT-проекты/"
                "Traffic-Vision-/self development images/")
    for i in count():
        image, persons = yield
        name = f"frame_{i:08}"
        for oleg in sorted(p.gender.name.lower() for p in persons):
            name += f"_{oleg}"
        # print(f"New frame {name}")
        cv2.imwrite(directory+name+".png", image)


if __name__ == "__main__":
    freeze_support()
    classes = [g.value for g in (Gender.Kid, Gender.Man, Gender.Woman)]
    model_args = {"iou": 0.4, "conf": 0.5, "classes":classes,
                "imgsz": 640, "verbose": False}
    model = YOLO('runs/detect/train8/weights/best.pt')
    url = "rtsp://rtsp:EL3gS7XV@80.91.19.85:58002/Streaming/Channels/101"
    stream = ParallelStream(url)

    step = 15
    prev = None
    last_time = 0
    saver = save()
    saver.send(None)
    with tqdm() as pbar:
        for frame in stream.iter_actual():
            frame = crop_image(frame)
            detected = model.track(frame, **model_args)[0]
            persons = parse_results(detected)

            cv2.imshow("frame", draw_debug(detected, persons, draw_lines=False))
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            if prev and len(persons) < len(prev) > 1 and (time()-last_time >= step):
                pbar.update(1)
                saver.send((frame, prev))
                last_time = time()
            prev = persons
