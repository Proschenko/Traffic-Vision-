if __name__ == "__main__":
    import sys
    from os.path import dirname

    sys.path.append(dirname(__file__).rpartition('\\')[0])

from timer_cm import Timer

from Tracker.Detector import Detector
from Tracker.Drawer import Drawer
from Tracker.Framer import Framer
from Tracker.Saver import VideoSaver
from Tracker.Traker import Traker


class Master:
    def __init__(self, urls: list[str], show_video=True, save_path=None) -> None:
        self.show_video = show_video
        self.save_path = save_path
        with Timer("Loading childs") as timer:
            with timer.child("Framer"):
                self.framer = Framer(*urls)
            with timer.child("Detector"):
                self.detector = Detector()
            with timer.child("Traker"):
                self.tracker = Traker()
            with timer.child("Drawer"):
                self.drawer = Drawer()
    
    def run(self):
        if not self.save_path:
            return self.mainloop()
        with VideoSaver(self.save_path, 25, (640, 640)) as saver:
            return self.mainloop(saver)
    
    def mainloop(self, saver: VideoSaver=None):
        for frame in self.framer:
            result = self.detector.detect(frame.image)
            persons = self.detector.parse(result)
            self.tracker.track(persons, frame.time)

            debug_frame = self.drawer.debug(result, persons, self.tracker.count)

            if self.show_video:
                if self.drawer.show(debug_frame):
                    break
            
            if saver:
                saver.write(debug_frame)

if __name__ == "__main__":
    urls = ['rtsp://rtsp:EL3gS7XV@80.91.19.85:58002/Streaming/Channels/101']*2
    Master(urls).run()
