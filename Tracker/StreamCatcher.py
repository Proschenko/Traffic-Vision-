from datetime import datetime, timedelta
from multiprocessing import Process, Queue
from queue import Empty
from typing import Generator

import cv2

from Tracker.misc import Frame


class StreamException(Exception):
    """Exception from Stream"""

class VideoCapture(cv2.VideoCapture):
    def __enter__(self):
        return self
    
    def __exit__(self, *_):
        self.release()

class Stream(Process):
    def __init__(self, url: str, parallel: bool=True):
        self.url = url
        self.parallel = parallel
        self.frame = Queue(maxsize=1)
        super().__init__(target=self.catch_frames)
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, *_):
        self.terminate()
    
    def __iter__(self) -> Generator[Frame, None, None]:
        while self.is_alive():
            try:
                yield self.frame.get(timeout=0.1)
            except Empty:
                pass
    
    def catch_frames(self):
        start_time = datetime.now()
        with VideoCapture(self.url) as cap:
            if not cap.isOpened():
                raise StreamException(f"Cant open file {self.url = }")

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    raise StreamException(f"Cant read frame")
                position = int(cap.get(cv2.CAP_PROP_POS_MSEC))
                time = start_time + timedelta(milliseconds=position)
                if self.parallel:
                    try:
                        self.frame.get_nowait()
                    except Empty:
                        pass
                self.frame.put(Frame(time, frame))
            cap.release()
            raise StreamException(f"Stream ended succsesfully")

if __name__ == '__main__':
    url = 'rtsp://rtsp:EL3gS7XV@80.91.19.85:58002/Streaming/Channels/101'

    with Stream(url) as stream:
        for pos, frame in stream:
            cv2.imshow("frame", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break