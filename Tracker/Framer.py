if __name__ == "__main__":
    import sys
    from os.path import dirname

    sys.path.append(dirname(__file__).rpartition('\\')[0])

from typing import Generator

import cv2
import numpy as np
from cv2.typing import MatLike

from Shared.Classes import Frame
from Shared.Context import Framer as config
from Tracker.Streamer import Stream

SIZE = config.size
HEIGHT1 = config.height1
HEIGHT2 = config.height2
START2 = config.start2
BORDER = config.border


class Framer:
    def __init__(self, url1: str, url2: str) -> None:
        self.left, self.right = Stream(url1), Stream(url2)

    def __iter__(self):
        with self.left, self.right:
            yield from self.get_frames()

    def get_frames(self) -> Generator[Frame, None, None]:
        for (p1, frame1), (p2, frame2) in zip(self.left, self.right):
            yield Frame(p2, self.make_frame(frame1, frame2))

    def make_frame(self, frame1: MatLike, frame2: MatLike) -> MatLike:
        # Создаем черное изображение нужного размера
        image = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)

        # Размещаем первую часть изображения
        image[:HEIGHT1] = frame1[:HEIGHT1, :SIZE]

        # Размещаем вторую часть изображения с отступом
        image[HEIGHT1+BORDER:][:HEIGHT2] = frame2[:, START2:][:HEIGHT2, :SIZE]

        return image

if __name__ == "__main__":
    url = 'rtsp://rtsp:EL3gS7XV@80.91.19.85:58002/Streaming/Channels/101'
    
    for pos, frame in Framer(url, url):
        cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break