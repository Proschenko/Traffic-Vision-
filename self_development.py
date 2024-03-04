import cv2
import os
from ultralytics import YOLO


def delete_files_in_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            try:
                os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting file: {file_path} -- {e}")


my_best_model = "runs/detect/train/weights/best.pt"
model = YOLO(my_best_model)
directory = r"D:\я у мамы программист\3 курс 2 семестр IT-проекты\self development images"  # Отсюда берем кадры
train_images_path = 'self development dataset/train/images'  # Сюда складываем
img_list = os.listdir(directory)
print(f"В папке имеется {len(img_list)} изображений")

delete_files_in_folder('self development dataset/train/images')
delete_files_in_folder('self development dataset/train/labels')

for img_name in img_list:
    img_filepath = directory + "\\" + img_name
    print(img_filepath)
    img = cv2.imread(img_filepath)
    img_copy = img

    # получаем ширину и высоту картинки
    h, w, _ = img.shape

    # получаем предсказания по картинке
    results = model.predict(source=img, conf=0.50)

    # расшифровываем объект results
    bboxes_ = results[0].boxes.xyxy.tolist()
    bboxes = list(map(lambda x: list(map(lambda y: int(y), x)), bboxes_))
    confs_ = results[0].boxes.conf.tolist()
    confs = list(map(lambda x: int(x * 100), confs_))
    classes_ = results[0].boxes.cls.tolist()
    classes = list(map(lambda x: int(x), classes_))
    cls_dict = results[0].names
    class_names = list(map(lambda x: cls_dict[x], classes))

    # приводим дешифрированные данные в удобный вид
    annot_lines = []
    for index, val in enumerate(class_names):
        xmin, ymin, xmax, ymax = int(bboxes[index][0]), int(bboxes[index][1]), int(bboxes[index][2]), int(
            bboxes[index][3])
        width = xmax - xmin
        height = ymax - ymin
        center_x = xmin + (width / 2)
        center_y = ymin + (height / 2)
        annotation = f"{classes[index]} {center_x / w} {center_y / h} {width / w} {height / h}"
        annot_lines.append(annotation)

    # копируем картинку в папку базы изображений для импорта
    cv2.imwrite(os.path.join(train_images_path, img_name), img_copy)

    # записываем файл аннотации в папку базы изображений для импорта
    txt_name = img_name.replace(".png", ".txt")
    with open(f'self development dataset/train2/labels/{txt_name}', 'w') as f:
        for line in annot_lines:
            f.write(line)
            f.write('\n')
