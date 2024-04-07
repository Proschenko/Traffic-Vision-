from Train.CustomModel import CustomYOLOv8Model


if __name__ == "__main__":
    model = CustomYOLOv8Model()
    model.train_my_model(100)
