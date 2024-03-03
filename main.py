from CustomModel import CustomYOLOv8Model
from ultralytics import YOLO

model = CustomYOLOv8Model()
model.download_dataset()
model.train_my_model(50)

# model_tmp = CustomYOLOv8Model()
# model = YOLO('runs/detect/train5/weights/best.pt')
# model.fuse()
# model_tmp.process_video_with_tracking(model, "test.mp4", show_video=True, save_video=True,
#                                       output_video_path="output_video.mp4")
