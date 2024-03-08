import os
from CustomModel import CustomYOLOv8Model
from Tracking import Tracking
from ultralytics import YOLO
from dotenv import load_dotenv

load_dotenv()

def main():
    # model = CustomYOLOv8Model()
    # model.download_dataset()
    # model.train_my_model(50)

    tracking = Tracking()
    model = YOLO('runs/detect/train2/weights/best.pt')
    model.fuse()
    input_video = os.getenv("INPUT_VIDEO")
    # input_video = r"C:\Users\Артём\Documents\GitHub\Traffic-Vision-\Test video output\output_8.mp4"

    tracking.process_video_with_tracking(model, input_video, show_video=True)


if __name__ == "__main__":
    main()
