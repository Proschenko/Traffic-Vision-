from ultralytics import YOLO

from Tracker.StreamCatcher import Stream
from Tracker.Tracking import Tracking


def main():
    model = YOLO('runs/detect/train8/weights/best.pt')
    model.fuse()
    tracking = Tracking(model)
    input_video = 'rtsp://rtsp:EL3gS7XV@80.91.19.85:58002/Streaming/Channels/101'
    with Stream(input_video) as video:
        tracking.process_video_with_tracking(video)


if __name__ == "__main__":
    main()
