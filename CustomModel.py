import json
import os
import random
import shutil

# import matplotlib.patches as patches
# import matplotlib.pyplot as plt
import cv2
import random
import numpy as np
import torch
import yaml
from easyocr import Reader
from roboflow import Roboflow
from ultralytics import YOLO

torch.manual_seed(42)
random.seed(42)
np.random.seed(42)


class CustomYOLOv8Model:
    def __init__(self):
        self.dataset_version = 3
        self.rf = Roboflow(api_key="rBzIu5I6ccC0pMQqHBlF")
        self.dataset_name = "traffic-control-project"
        self.women_center_door = (0.14453125, 0.244140625)
        self.men_center_door = (0.19375, 0.2109375)
        self.kid_center_door = (0.440625, 0.13046875000000002)

    # region чтение датасета
    @staticmethod
    def _update_data_yaml(data_yaml_path):
        """
        Обновляет файл данных YAML для указания путей к изображениям обучения и валидации.

        :param data_yaml_path: Путь к файлу данных YAML.
        :type data_yaml_path: str
        :return: Нет возвращаемого значения.
        """
        train_path = "../train/images"
        val_path = "../valid/images"

        with open(data_yaml_path, 'r') as file:
            data = yaml.safe_load(file)

        data['train'] = train_path
        data['val'] = val_path

        with open(data_yaml_path, 'w') as file:
            yaml.dump(data, file)

    def _download_datasets_from_roboflow(self):
        project = self.rf.workspace("traffic-vision-workspace-kb8fc").project("traffic-control-project")
        version = project.version(self.dataset_version)
        dataset = version.download("yolov8")
        return dataset.location

    @staticmethod
    def _delete_exists_folder(folder_path):
        # Если папка существует, удалить ее
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print(f'Папка {folder_path} успешно удалена.')

    def download_dataset(self):
        """
        Загружает датасет с Roboflow и организует его структуру.

        Качает датасет с использованием API-ключа Roboflow. Перемещает файлы из исходной папки в целевую,
        а затем обновляет файл данных YAML с новыми путями.

        :return: Нет возвращаемого значения.
        """

        dataset_path = self.dataset_name + "-" + str(self.dataset_version)
        self._delete_exists_folder(dataset_path)
        target_folder = os.path.join("yolov5", "datasets", dataset_path)
        self._delete_exists_folder(target_folder)

        source_folder = self._download_datasets_from_roboflow()
        data_yaml_path = f"{dataset_path}/data.yaml"
        self._update_data_yaml(data_yaml_path)

        # Если папка не существует, создайте ее
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        # Переместите файлы в целевую папку
        for file_name in os.listdir(source_folder):
            source_file_path = os.path.join(source_folder, file_name)
            target_file_path = os.path.join(target_folder, file_name)
            print(f"Перенос файла {file_name}")
            shutil.move(source_file_path, target_file_path)

        # Удаляем папку, если она пуста
        try:
            os.rmdir(dataset_path)
            print(f'Папка {dataset_path} успешно удалена.')
        except OSError as e:
            print(f'Не удалось удалить папку {dataset_path}: {e}')

        self._download_datasets_from_roboflow()
        self._update_data_yaml(data_yaml_path)

    # endregion

    def train_my_model(self, number_epoch=50, image_size=640):
        """
        Обучает модель YOLOv8 на предоставленных данных.

        Инициализирует и обучает модель YOLOv8 на указанных данных.
        В данном случае, обучение происходит на протяжении 60 эпох с размером изображения 640x640.

        :return: Нет возвращаемого значения.
        """

        name_model = "yolov8m.pt"
        model = YOLO(name_model)
        model.train(data=f"{self.dataset_name}-{self.dataset_version}/data.yaml", epochs=number_epoch, imgsz=image_size)

    @staticmethod
    def text_recognition(file_path):
        reader = Reader(["en", "ru"])
        result = reader.readtext(file_path, detail=0)
        return result

    @staticmethod
    def _process_tracking_results(tracking_results):
        """
        Process tracking results to compute the center of each bounding box.

        Parameters:
        - tracking_results: List of tracking results, where each result contains information about tracked objects.

        Returns:
        - List of tuples, where each tuple represents the (x, y) coordinates of the center of a bounding box.
        """
        centers = []

        for result in tracking_results:
            if result.boxes.id is not None:  # Check if there is a valid ID
                box = result.boxes.xyxy.cpu().numpy().astype(int)
                center_x = (box[0] + box[2]) // 2
                center_y = (box[1] + box[3]) // 2
                centers.append((center_x, center_y))
                print(center_x, center_y)
        return centers

    def process_video_with_tracking(self, model, input_video_path, show_video=True, save_video=False,
                                    output_video_path="output_video.mp4"):
        # Open the input video file
        cap = cv2.VideoCapture(input_video_path)

        if not cap.isOpened():
            raise Exception("Error: Could not open video file.")

        # Get inaput video frame rate and dimensions
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Define the output video writer
        if save_video:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            results = model.track(frame, iou=0.4, conf=0.5, persist=True, imgsz=608, verbose=False,
                                  tracker="botsort.yaml")

            centers = self._process_tracking_results(results)

            if results[0].boxes.id != None:  # this will ensure that id is not None -> exist tracks
                boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
                ids = results[0].boxes.id.cpu().numpy().astype(int)

                for box, id in zip(boxes, ids):
                    # Generate a random color for each object based on its ID
                    random.seed(int(id))
                    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

                    cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3],), color, 2)
                    cv2.putText(
                        frame,
                        f"Id {id}",
                        (box[0], box[1]),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 255),
                        2,
                    )

            if save_video:
                out.write(frame)

            if show_video:
                frame = cv2.resize(frame, (0, 0), fx=0.75, fy=0.75)
                cv2.imshow("frame", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        # Release the input video capture and output video writer
        cap.release()
        if save_video:
            out.release()

        # Close all OpenCV windows
        cv2.destroyAllWindows()
