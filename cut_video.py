from moviepy.video.io.VideoFileClip import VideoFileClip
import os


def clean_output_folder():
    folder_path = r"D:\я у мамы программист\3 курс 2 семестр IT-проекты\Traffic-Vision-\Test output video"

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
    input_video = r"D:\я у мамы программист\3 курс 2 семестр IT-проекты\Traffic-Vision-\Test input video\test.mp4"
    output_prefix = r"D:\я у мамы программист\3 курс 2 семестр IT-проекты\Traffic-Vision-\Test output video\output"
    clean_output_folder()
    cut_video(input_video, output_prefix, number_video=16)
