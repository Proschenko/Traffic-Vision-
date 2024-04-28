from Train.CustomModel import CustomYOLOv8Model


if __name__ == "__main__":
    model = CustomYOLOv8Model(dataset_version=1, project_version=4)
    model.download_dataset()
    model.train_my_model(150)
