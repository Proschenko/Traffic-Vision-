from CustomModel import CustomYOLOv8Model
from Tracking import Tracking
from ultralytics import YOLO

# model = CustomYOLOv8Model()
# model.download_dataset()
# model.train_my_model(50)

tracking = Tracking()
model = YOLO('runs/detect/train2/weights/best.pt')
model.fuse()
input_video = r"D:\я у мамы программист\3 курс 2 семестр IT-проекты\Traffic-Vision-\Test video output\output_2.mp4"
tracking.process_video_with_tracking(model, input_video, show_video=True, save_video=False,
                                     output_video_path="output_video.mp4")
