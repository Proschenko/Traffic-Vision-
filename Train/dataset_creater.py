from datetime import timedelta

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
    model = YOLO('runs/detect/train8/weights/best.pt')

    stream = ParallelStream(rtsp_url)
    last_save_time = time.time()
    for frame in stream.iter_actual():
        frame = crop_image(frame)

        # Process the frame with your YOLO model
        results = model.track(frame, **model_args)[0]

        persons = parse_results(results)
        frame_time = stream.start_time + timedelta(milliseconds=stream.position)

        if show_video:
            if save_path_images and persons:  # Если указан путь для сохранения и найдены люди на кадре
                current_time = time.time()
                if current_time - last_save_time >= 5:  # Проверяем, прошло ли уже 5 секунд с последнего сохранения
                    if not os.path.exists(save_path_images):
                        os.makedirs(save_path_images)
                    cv2.imwrite(os.path.join(save_path_images, f"{frame_time}.jpg"), frame)
                    last_save_time = current_time  # Обновляем время последнего сохранения

        if show_video:
            cv2.imshow("frame", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    input_video = 'rtsp://rtsp:EL3gS7XV@80.91.19.85:58002/Streaming/Channels/101'
    process_video_with_tracking_and_save_predict_images(input_video)
