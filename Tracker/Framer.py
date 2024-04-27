if __name__ == "__main__":
    import sys
    from os.path import dirname

    sys.path.append(dirname(__file__).rpartition('\\')[0])

from itertools import count
from time import sleep
import cv2
from cv2.typing import MatLike
import numpy as np

from Tracker.StreamCatcher import Stream

WIDTH = 640
HEIGHT1 = 300
HEIGHT2 = 150
START1 = 0
START2 = 900


# HEIGHT = 300
# WIDTH_2_MIN = 900
# WIDTH_2_MAX = 1540
# HEIGHT2 = 150


def make_frame(left: Stream, right: Stream):
    for (p1, frame1), (p2, frame2) in zip(left, right):
        # Создаем черное изображение нужного размера
        image = np.zeros((WIDTH, WIDTH, 3), dtype=np.uint8)

        # Размещаем первую часть изображения
        image[:HEIGHT1] = frame1[START1:][:HEIGHT1, :WIDTH]

        # Размещаем вторую часть изображения с отступом в 20 пикселей
        image[HEIGHT1+20:][:HEIGHT2] = frame2[:, START2:][:HEIGHT2, :WIDTH]

        yield (p1, p2), image

if __name__ == "__main__":
    url = 'rtsp://rtsp:EL3gS7XV@80.91.19.85:58002/Streaming/Channels/101'

    with Stream(url) as left, Stream(url) as right:
        for pos, frame in make_frame(left, right):
            cv2.imshow("frame", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break