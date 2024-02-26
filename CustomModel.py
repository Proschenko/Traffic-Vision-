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
        self.dataset_version = 2
        self.rf = Roboflow(api_key="AmQ0vHqaiNHr6SeXUAWb")
        self.dataset_name = "traffic_vision--"

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

    def download_dataset(self):
        """
        Загружает датасет с Roboflow и организует его структуру.

        Качает датасет с использованием API-ключа Roboflow. Перемещает файлы из исходной папки в целевую,
        а затем обновляет файл данных YAML с новыми путями.

        :return: Нет возвращаемого значения.
        """

        dataset_path = self.dataset_name + str(self.dataset_version)

        # Если папка существует, удалить ее
        if os.path.exists(dataset_path):
            shutil.rmtree(dataset_path)
            print(f'Папка {dataset_path} успешно удалена.')

        target_folder_tmp = os.path.join("yolov5", "datasets", self.dataset_name + str(self.dataset_version))

        # Если папка существует, удалить ее
        if os.path.exists(target_folder_tmp):
            shutil.rmtree(target_folder_tmp)
            print(f'Папка {target_folder_tmp} успешно удалена.')

        # качаем датасет с Roboflow
        project = self.rf.workspace("detected").project("traffic_vision")
        dataset = project.version(self.dataset_version).download("yolov8")

        data_yaml_path = f"{dataset_path}/data.yaml"
        self._update_data_yaml(data_yaml_path)

        # Путь к исходной папке
        source_folder = dataset.location
        dataset_name = f"{dataset.name}-{dataset.version}"
        # Путь к целевой папке
        target_folder = os.path.join("yolov5", "datasets", dataset_path)
        target_folder_tmp = os.path.join("yolov5", "datasets", dataset_path)

        # Если папка не существует, создайте ее
        if not os.path.exists(target_folder_tmp):
            os.makedirs(target_folder_tmp)

        # Переместите файлы в целевую папку
        for file_name in os.listdir(source_folder):
            source_file_path = os.path.join(source_folder, file_name)
            target_file_path = os.path.join(target_folder, file_name)
            print(f"Move file {file_name}")
            shutil.move(source_file_path, target_file_path)

        # Удаляем папку, если она пуста
        try:
            os.rmdir(dataset_path)
            print(f'Папка {dataset_path} успешно удалена.')
        except OSError as e:
            print(f'Не удалось удалить папку {dataset_path}: {e}')

        project = self.rf.workspace("detected").project("traffic_vision")
        dataset = project.version(self.dataset_version).download("yolov8")

        self._update_data_yaml(data_yaml_path)

    # endregion

    @staticmethod
    def text_recognition(file_path):
        reader = Reader(["en", "ru"])
        result = reader.readtext(file_path, detail=0)
        return result

    def train_my_model(self, number_epoch):
        """
        Обучает модель YOLOv8 на предоставленных данных.

        Инициализирует и обучает модель YOLOv8 на указанных данных.
        В данном случае, обучение происходит на протяжении 60 эпох с размером изображения 640x640.

        :return: Нет возвращаемого значения.
        """

        name_model = "yolov8n.pt"
        model = YOLO(name_model)
        model.train(data=f"{self.dataset_name}{self.dataset_version}/data.yaml", epochs=number_epoch, imgsz=640)


    # region варианты предсказания
    def predict_my_model(self, img_path, show_predict=False):
        """
        Предсказывает объекты на изображении с использованием обученной модели YOLOv8.

        :param img_path: Путь к изображению для предсказания объектов.
        :type img_path: str
        :param show_predict: Флаг для отображения графического представления предсказанных объектов.
        :type show_predict: bool, optional
        :return: Строка JSON с информацией о распознанных объектах.
        :rtype: str
        """

        name_model = "runs/detect/train12/weights/best.pt"
        model = YOLO(name_model)  # Загрузка
        rez_predict = model.predict(img_path)
        rez_json_file, coordinates, categories = self._infer_objects(rez_predict)
        if show_predict and img_path.find(".jpg"):
            self._plot_results(coordinates, categories, img_path)
        return rez_json_file

    @staticmethod
    def process_video_with_tracking(model, input_video_path, show_video=True, save_video=False,
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


