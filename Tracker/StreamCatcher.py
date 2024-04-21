import multiprocessing as mp
from datetime import datetime, timedelta
from functools import cached_property
from itertools import count
from multiprocessing import Queue
from queue import Empty
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

class ParallelStream:
    def __init__(self, rtsp_url: str) -> None:
        self.rtsp_url = rtsp_url
        self.data = Queue(maxsize=1)
        self.position = 0
    
    def iter_actual(self) -> Generator[tuple[MatLike, int], None, None]:
        self.start_time = datetime.now()
        while True:
            self.process = mp.Process(target=self.catch_frames, 
                                  args=[self.rtsp_url, self.data])
            self.process.start()
            try: 
                while True:
                    pos, frame = self.data.get(timeout=10)
                    self.position = pos
                    yield frame
            except Empty:
                print(StreamException("Connection time out"))
            finally:
                self.process.terminate()

    @staticmethod
    def catch_frames(rtsp_url: str, output: Queue):
        cap = cv2.VideoCapture(rtsp_url)
        if not cap.isOpened():
            StreamException(f"Cant open file {rtsp_url = }")
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            position = int(cap.get(cv2.CAP_PROP_POS_MSEC))
            try:
                output.get_nowait()
            except Empty:
                pass
            output.put((position, frame), timeout=1)
        cap.release()