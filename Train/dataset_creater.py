if __name__ == "__main__":
    import sys
    from os.path import dirname

    sys.path.append(dirname(__file__).rpartition('\\')[0])


from datetime import datetime, timedelta
from itertools import count
from os import makedirs, path

import cv2

from Tracker.Detector import Detector
from Tracker.Drawer import Drawer
from Tracker.Framer import Framer
from Shared.Classes import Gender

IGNORE = Gender.Man, Gender.Woman

def is_good(persons) -> bool:
    return persons and (len(persons) > 1 or persons[0].gender not in IGNORE)

def main(step: timedelta, save_path: str, show_video=True):
    url = 'rtsp://rtsp:EL3gS7XV@80.91.19.85:58002/Streaming/Channels/101'

    detecter = Detector()
    framer = Framer(url, url)
    drawer = Drawer()

    # make unique folder name
    for i in count(1):
        folder = path.join(save_path, f"pack_{i}")
        if path.exists(folder):
            continue
        makedirs(folder)
        break

    last_save = datetime.fromtimestamp(0)
    index = 0
    for time, frame in framer:
        result = detecter.detect(frame)
        persons = detecter.parse(result)
        if show_video:
            debug_frame = drawer.debug(result, persons)
            if drawer.show(debug_frame):
                break

        if time - last_save > step and is_good(persons):
            name = path.join(folder, f"frame_{index:0>10}.jpg")
            index += 1
            cv2.imwrite(name, result.orig_img)
            last_save = time


if __name__ == "__main__":
    main(timedelta(seconds=3), ".")