import os

from dotenv import load_dotenv
from ultralytics import YOLO

from CustomModel import CustomYOLOv8Model
from Tracking import Tracking

load_dotenv()


def main():
    # model = CustomYOLOv8Model()
    # model.download_dataset()
    # model.train_my_model(50)

    tracking = Tracking()
    model = YOLO('runs/detect/train2/weights/best.pt')
    model.fuse()
    # input_video = os.getenv("INPUT_VIDEO")
    # input_video = r"C:\Users\ivers\Desktop\Traffic-Vision-iversy\Test video output\output_8.mp4"
    input_video = r"D:\я у мамы программист\3 курс 2 семестр IT-проекты\Traffic-Vision-\Test output video\output_9.mp4"
    # input_video = r"D:\я у мамы программист\3 курс 2 семестр IT-проекты\Traffic-Vision-\Test input video\test.mp4"

    tracking.process_video_with_tracking(model, input_video, show_video=True, save_path="result_video.mp4")


if __name__ == "__main__":
    main()
