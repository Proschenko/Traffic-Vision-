if __name__ == "__main__":
    import sys
    from os.path import dirname

    sys.path.append(dirname(__file__).rpartition('\\')[0])


from datetime import datetime, timedelta
from itertools import count
from os import makedirs, path

import cv2
from ultralytics import YOLO

from Tracker.Debug_drawer import draw_debug
from Tracker.People import Gender
from Tracker.StreamCatcher import Stream
from Tracker.Tracking import detect, parse_results

IGNORE = Gender.Man, Gender.Woman

def is_good(persons) -> bool:
    return persons and (len(persons) > 1 or persons[0].gender not in IGNORE)

def main(step: timedelta, save_path: str, show_video=True):
    url = 'rtsp://rtsp:EL3gS7XV@80.91.19.85:58002/Streaming/Channels/101'

    model = YOLO('runs/detect/train8/weights/best.pt')
    model.fuse()

    for i in count(1):
        folder = path.join(save_path, f"pack_{i}")
        if path.exists(folder):
            continue
        makedirs(folder)
        break

    last_save = datetime.fromtimestamp(0)
    index = 0
    with Stream(url) as stream:
        for time, result in detect(model, stream):
            persons = parse_results(result)
            if show_video:
                debug_frame = draw_debug(result, persons, draw_lines=False)
                cv2.imshow("frame", debug_frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            if time - last_save > step:
                if is_good(persons):
                    name = path.join(folder, f"{index:0>10}.jpg")
                    index += 1
                    cv2.imwrite(name, result.orig_img)
                    last_save = time


if __name__ == "__main__":
    main(timedelta(seconds=3), ".")