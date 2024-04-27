from cv2.typing import MatLike
from ultralytics import YOLO
from ultralytics.engine.results import Results

from Tracker.misc import boxes_center
from Tracker.People import Gender, People


class Detector:
    def __init__(self) -> None:
        self.model = YOLO('runs/detect/train8/weights/best.pt')
        self.model.fuse()
        self.config = {"iou": 0.4, "conf": 0.5, "persist": True,
                       "imgsz": 640, "verbose": False,
                       "tracker": "botsort.yaml"}
    
    def detect(self, image: MatLike) -> Results:
        return self.model.track(image, **self.config)[0]
    
    def parse(self, results: Results) -> list[People]:
        boxes = results.boxes.cpu().numpy()
        centers = boxes_center(boxes.xyxy)
        people = list()
        for box, center in zip(boxes, centers.astype(int)):
            id = box.id and int(box.id)
            gender = Gender(int(*box.cls))
            people.append(People.from_position(id, gender, center))
        return people