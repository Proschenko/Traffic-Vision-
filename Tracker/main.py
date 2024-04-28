if __name__ == "__main__":
    import sys
    from os.path import dirname

    sys.path.append(dirname(__file__).rpartition('\\')[0])

from timer_cm import Timer

from Shared.Context import Master as config
from Tracker.Detector import Detector
from Tracker.Drawer import Drawer
from Tracker.Framer import Framer
from Tracker.Saver import VideoSaver
from Tracker.Traker import Traker


class Master:
    def __init__(self, urls: tuple[str, str]) -> None:
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
        if not config.save_path:
            return self.mainloop()
        with VideoSaver(self.save_path, 25, (640, 640)) as saver:
            return self.mainloop(saver)
    
    def mainloop(self, saver: VideoSaver=None):
        for frame in self.framer:
            result = self.detector.detect(frame.image)
            persons = self.detector.parse(result)
            self.tracker.track(persons, frame.time)

            debug_frame = self.drawer.debug(result, persons, self.tracker.count)

            if config.show_video:
                if self.drawer.show(debug_frame):
                    break
            
            if saver:
                saver.write(debug_frame)

if __name__ == "__main__":
    from Shared.Context import url
    Master([url, url]).run()
