if __name__ == "__main__":
    import sys
    from os.path import dirname
    sys.path.append(dirname(__file__).rpartition('\\')[0])

import cv2
from tqdm import tqdm
from ultralytics import YOLO

from Tracker.Debug_drawer import draw_debug
from Tracker.misc import crop_image, frame_crop
from Tracker.StreamCatcher import Stream
from Tracker.Tracking import Tracking

model_args = {"iou": 0, "conf": 0.2,
              "imgsz": 640, "verbose": False}
model = YOLO('runs/detect/train5/weights/best.pt')
tracker = Tracking(model)

path = ("D:/я у мамы программист"
        "/3 курс 2 семестр IT-проекты"
        "/Traffic-Vision-"
        "/Test input video"
        "/test.mp4")
stream = Stream(path)
stream.jump_to(39*60)

frame_step = 40
total = (stream.n_frames - stream.frame_number) // frame_step
for frame in tqdm(stream.iter_frames(frame_step), total=total, disable=False):
    frame = crop_image(frame, **frame_crop)
    detected = model.predict(frame, **model_args)[0]
    persons = tracker.parse_results(detected)

    if len(persons) < 2:
        continue
    if len(persons) == 2:
        if persons[0].model_class != persons[1].model_class:
            continue
    directory = "D:/я у мамы программист/3 курс 2 семестр IT-проекты/Traffic-Vision-/self development images/"
    cv2.imwrite(directory+f"frame_{stream.frame_number}.png", frame)

    debug_frame = draw_debug(detected, persons, (1, 1), *[1, 0, 0])
    cv2.imshow("frame", debug_frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break