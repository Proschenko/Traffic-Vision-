from CustomModel import CustomYOLOv8Model
from Tracking import Tracking
from ultralytics import YOLO


def main():
    # model = CustomYOLOv8Model()
    # model.download_dataset()
    # model.train_my_model(50)

    tracking = Tracking()
    model = YOLO('runs/detect/train2/weights/best.pt')
    model.fuse()
    input_video = r"test.mp4"

    tracking.process_video_with_tracking(model, input_video, show_video=True)


if __name__ == "__main__":
    main()
