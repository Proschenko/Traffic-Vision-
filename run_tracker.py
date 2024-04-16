from ultralytics import YOLO

from Tracker.Tracking import Tracking


def main():
    model = YOLO('runs/detect/train8/weights/best.pt')
    model.fuse()
    tracking = Tracking(model)
    input_video = 'rtsp://rtsp:EL3gS7XV@80.91.19.85:58002/Streaming/Channels/101'
    tracking.process_video_with_tracking(input_video)


if __name__ == "__main__":
    main()
