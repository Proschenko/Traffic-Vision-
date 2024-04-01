import imageio
from moviepy.video.io.VideoFileClip import VideoFileClip
import os
import cv2
from tqdm import tqdm


def crop_video(input_video_inner, output_video_inner, start_time_min_inner, end_time_min_inner):
    # Открытие видеофайла
    video_capture = cv2.VideoCapture(input_video_inner)

    # Получение информации о видео
    fps = video_capture.get(cv2.CAP_PROP_FPS)

    # Расчет кадров начала и конца для обрезки
    start_frame = int(start_time_min_inner * 60 * fps)
    end_frame = int(end_time_min_inner * 60 * fps)

    # Установка позиции видео в начальный кадр
    video_capture.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    # Создание объекта для записи видео
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Формат видео, например, mp4
    video_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    output_video_writer = cv2.VideoWriter(output_video_inner, fourcc, fps, (video_width, video_height))

    # Обрезка видео и запись обрезанного видео
    for _ in tqdm(range(start_frame, end_frame + 1), desc="Cropping video", unit="frame"):
        ret, frame = video_capture.read()
        if not ret:
            break
        output_video_writer.write(frame)

    # Освобождение ресурсов
    video_capture.release()
    output_video_writer.release()


def extract_frames(input_video_inner, output_folder_inner, frames_per_second_inner, end, start):
    clean_output_folder(r"D:\я у мамы программист\3 курс 2 семестр IT-проекты\Traffic-Vision-\self development images")
    # Открытие видеофайла
    video_capture = imageio.get_reader(input_video_inner)
    # Получение общего количества кадров
    total_frames = (end - start) * 60 * 25
    # Вычисление количества итераций
    iterations = total_frames // frames_per_second_inner

    # Создание папки для сохранения кадров, если она не существует
    if not os.path.exists(output_folder_inner):
        os.makedirs(output_folder_inner)

    # Извлечение кадров из видео и их сохранение
    with tqdm(total=iterations, desc="Extracting frames") as pbar:
        for frame_count, frame in enumerate(video_capture):
            if frame_count % frames_per_second_inner == 0:
                frame_path = os.path.join(output_folder_inner, f"frame_{frame_count}.png")  # Путь к кадру
                imageio.imwrite(frame_path, frame)
                pbar.update(1)

    # Освобождение ресурсов
    video_capture.close()


def clean_output_folder(folder_path=r"D:\я у мамы программист\3 курс 2 семестр IT-проекты\Traffic-Vision-"
                                    r"\Test output video"):

    # Iterate over all files in the directory
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Check if the current path is a file (not a directory) and delete it
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
        else:
            print(f"{file_path} is not a file")
    print("---Done---")


def cut_video(input_file, output_file_prefix, number_video=2, duration=30):
    clip = VideoFileClip(input_file)

    for i in range(number_video):
        start_time = i * duration
        end_time = (i + 1) * duration
        subclip = clip.subclip(start_time, end_time)
        output_file = f"{output_file_prefix}_{i + 1}.mp4"
        subclip.write_videofile(output_file, codec="libx264", audio_codec="aac")

    clip.close()


if __name__ == "__main__":
    # Пример использования функций
    input_video = (r'D:\я у мамы программист\3 курс 2 семестр IT-проекты\Traffic-Vision-'
                   r'\Test input video\D10_20240228093908.mp4')
    output_video = (r'D:\я у мамы программист\3 курс 2 семестр IT-проекты\Traffic-Vision-'
                    r'\Test output video\cut_output_video.mp4')
    output_folder = r'D:\я у мамы программист\3 курс 2 семестр IT-проекты\Traffic-Vision-\self development images'

    # Указание времени начала и конца для обрезки (в минутах)
    start_time_min = 12
    end_time_min = 20

    # Количество кадров на обрезку видео покадрово
    frames_per_second = 25

    # Обрезка видео
    # crop_video(input_video, output_video, start_time_min, end_time_min)

    # Извлечение кадров из обрезанного видео и сохранение в папку
    extract_frames(output_video, output_folder, frames_per_second, end_time_min, start_time_min)

    # input_video = r"D:\я у мамы программист\3 курс 2 семестр IT-проекты\Traffic-Vision-\Test input video\test.mp4"
    # output_prefix = r"D:\я у мамы программист\3 курс 2 семестр IT-проекты\Traffic-Vision-\Test output video\output"
    # clean_output_folder()
    # cut_video(input_video, output_prefix, number_video=16)
