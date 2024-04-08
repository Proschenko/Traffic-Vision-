from Train.CustomModel import CustomYOLOv8Model


if __name__ == "__main__":
    model = CustomYOLOv8Model(1)
    # model.download_dataset()
    model.train_my_model(100)
