from dotenv import load_dotenv
from ultralytics import YOLO

from CustomModel import CustomYOLOv8Model
from Tracking import Tracking

load_dotenv()


def main():
    model = CustomYOLOv8Model()
    # model.download_dataset()
    model.train_my_model(100)

    # model = YOLO('runs/detect/train2/weights/best.pt')
    # model.fuse()
    # tracking = Tracking(model)

    # input_video = r"D:\я у мамы программист\3 курс 2 семестр IT-проекты\Traffic-Vision-\Test output_8put video\output_9.mp4"
    # input_video = r"D:\я у мамы программист\3 курс 2 семестр IT-проекты\Traffic-Vision-\Test input video\test.mp4"

    # input_video = 'rtsp://admin:ytn z yt uhb,@192.168.1.64:554/Streaming/Channels/101'

    # input_video = 'rtsp://rtsp:EL3gS7XV@80.91.19.85:58002/Streaming/Channels/101'
    #
    # tracking.process_video_with_tracking(input_video, save_path="result_video.mp4")


if __name__ == "__main__":
    main()
