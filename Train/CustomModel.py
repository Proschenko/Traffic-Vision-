import os
import random
import shutil

import numpy as np
import torch
import yaml
from roboflow import Roboflow
from ultralytics import YOLO

torch.manual_seed(42)
random.seed(42)
np.random.seed(42)


class CustomYOLOv8Model:
    def __init__(self, dataset_version):
        self.dataset_version = dataset_version
        self.rf = Roboflow(api_key="rBzIu5I6ccC0pMQqHBlF")
        self.dataset_name = "traffic-control-№3"

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
        """
        Загружает датасет с Roboflow

        :return: путь к датасету
        :rtype: str
        """
        project = self.rf.workspace("traffic-vision-workspace-kb8fc").project("traffic-control-3")
        version = project.version(self.dataset_version)
        dataset = version.download("yolov8")
        return dataset.location

    @staticmethod
    def _delete_exists_folder(folder_path):
        """
        Удаляет папку, если она существует

        :param folder_path: Путь к папке
        :type folder_path: str
        """
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
        train_model = YOLO(name_model)
        train_model.train(data=f"{self.dataset_name}-{self.dataset_version}/data.yaml",
                          epochs=number_epoch, imgsz=image_size)
