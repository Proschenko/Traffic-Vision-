from datetime import timedelta

from Tracker.Debug_drawer import draw_debug

if __name__ == "__main__":
    import sys
    from os.path import dirname

    sys.path.append(dirname(__file__).rpartition('\\')[0])

import os
import cv2
import time
from ultralytics import YOLO
from Tracker.misc import crop_image
from Tracker.StreamCatcher import ParallelStream
from Tracker.Tracking import Tracking, parse_results


def process_video_with_tracking_and_save_predict_images(rtsp_url: str, show_video=True, save_path_images=None):
    """
    TODO: документация
    :param rtsp_url:
    :param show_video:
    :param save_path_images:
    :return:
    """

    # TODO: конфиг должен читаться из отдельного файла
    model_args = {"iou": 0.4, "conf": 0.5, "persist": True,
                  "imgsz": 640, "verbose": False,
                  "tracker": "botsort.yaml"}
    model = YOLO(r'D:\PyCharm Com\Project\Traffic-Vision-\runs/detect/train9/weights/best.pt')

    miss_frame = 30  # Берем каждый N кадр
    border_max_frame = 1000  # Ограничение по кадрам в папке
    count_frame_in_save_folder = 0
    stream = ParallelStream(rtsp_url)
    for number_frame, frame in enumerate(stream.iter_actual()):
        frame = crop_image(frame)

        # Process the frame with your YOLO model
        results = model.track(frame, **model_args)[0]

        persons = parse_results(results)
        frame_time = stream.start_time + timedelta(milliseconds=stream.position)
        formatted_frame_time = frame_time.strftime("%Y_%m_%d_%H_%M_%S")

        if show_video and number_frame % miss_frame == 0 and count_frame_in_save_folder <= border_max_frame:
            if save_path_images and persons:  # Если указан путь для сохранения и найдены люди на кадре
                if not os.path.exists(save_path_images):
                    os.makedirs(save_path_images)
                name_image = f"frame_{count_frame_in_save_folder}_{formatted_frame_time}.png"
                cv2.imwrite(os.path.join(save_path_images, name_image), frame)
                print(f"Записал изображение {name_image}")
                count_frame_in_save_folder += 1

        if show_video:
            debug_frame = draw_debug(results, persons, draw_lines=False)
            cv2.imshow("frame", debug_frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    input_video = 'rtsp://rtsp:EL3gS7XV@80.91.19.85:58002/Streaming/Channels/101'
    save_directory = r"D:\PyCharm Com\Project\Traffic-Vision-\self development images"
    process_video_with_tracking_and_save_predict_images(input_video, True, save_directory)
