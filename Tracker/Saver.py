import os
from datetime import datetime

import cv2
from cv2.typing import MatLike


class VideoSaver:
    def __init__(self, path: str, fps: int, resolution: tuple[int, int]) -> None:
        name = "Record_" + datetime.now().strftime("%d-%m-%y %H-%M-%S")
        full_path = os.path.join(path, name+".mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.file = cv2.VideoWriter(full_path, fourcc, fps, resolution)

    def write(self, frame: MatLike):
        self.file.write(frame)
    
    def __enter__(self):
        return self
    
    def __exit__(self, *_):
        self.file.release()