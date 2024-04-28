from cv2.typing import MatLike
from ultralytics import YOLO
from ultralytics.engine.results import Results

from Config.Context import Detector as config
from Tracker.misc import boxes_center
from Tracker.People import Gender, People


class Detector:
    def __init__(self) -> None:
        self.model = YOLO(config.model_path)
        self.model.fuse()
        self.args = config.args
    
    def detect(self, image: MatLike) -> Results:
        return self.model.track(image, **self.args)[0]
    
    def parse(self, results: Results) -> list[People]:
        boxes = results.boxes.cpu().numpy()
        centers = boxes_center(boxes.xyxy)
        people = list()
        for box, center in zip(boxes, centers.astype(int)):
            id = box.id and int(box.id)
            gender = Gender(int(*box.cls))
            people.append(People.from_position(id, gender, center))
        return people