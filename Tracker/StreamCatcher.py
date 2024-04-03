from datetime import datetime, timedelta
from functools import cached_property
from itertools import count
from typing import Generator

import cv2
from cv2.typing import MatLike


class StreamException(Exception):
    """Exception from Stream"""


class Stream:
    def __init__(self, rtsp_url: str) -> None:
        self.cap = cv2.VideoCapture(rtsp_url)
        if not self.cap.isOpened():
            StreamException(f"Cant open file {rtsp_url = }")

        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 25 * 8)
        self.start_time = datetime.now() - timedelta(milliseconds=self.position)

    @property
    def position(self) -> int:
        return int(self.cap.get(cv2.CAP_PROP_POS_MSEC))

    @property
    def frame_number(self) -> int:
        return int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))

    @cached_property
    def fps(self) -> int:
        return int(self.cap.get(cv2.CAP_PROP_FPS))

    @cached_property
    def n_frames(self) -> int:
        return int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def jump_to(self, second: int):
        frame = self.fps * second
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame)

    def iter_frames(self, step: int) -> Generator[MatLike, None, None]:
        for frame_number in count():
            if not self.cap.isOpened():
                break

            ret, frame = self.cap.read()
            if not ret:
                break

            if frame_number % step == 0:
                yield frame

    def release(self):
        self.cap.release()
