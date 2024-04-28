import numpy as np
from cv2.typing import MatLike
from ultralytics import YOLO
from ultralytics.engine.results import Results

from Shared.Classes import Gender, People
from Shared.Context import Detector as config


class Detector:
    def __init__(self) -> None:
        self.model = YOLO(config.model_path)
        self.model.fuse()
        self.args = config.args
    
    def detect(self, image: MatLike) -> Results:
        return self.model.track(image, **self.args)[0]
    
    def parse(self, results: Results) -> list[People]:
        boxes = results.boxes.cpu().numpy()
        centers = np.mean(boxes.xyxy.reshape((-1, 2, 2)), 1).astype(int)
        people = list()
        for box, center in zip(boxes, centers):
            id = box.id and int(box.id)
            gender = Gender(int(*box.cls))
            people.append(People.from_position(id, gender, center))
        return people