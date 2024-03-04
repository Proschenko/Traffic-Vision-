from moviepy.video.io.VideoFileClip import VideoFileClip


def cut_video(input_file, output_file_prefix, duration=120):
    clip = VideoFileClip(input_file)

    for i in range(2):
        start_time = i * duration
        end_time = (i + 1) * duration
        subclip = clip.subclip(start_time, end_time)
        output_file = f"{output_file_prefix}_{i + 1}.mp4"
        subclip.write_videofile(output_file, codec="libx264", audio_codec="aac")

    clip.close()


if __name__ == "__main__":
    input_video = r"D:\я у мамы программист\3 курс 2 семестр IT-проекты\Traffic-Vision-\Test input video\test.mp4"
    output_prefix = r"D:\я у мамы программист\3 курс 2 семестр IT-проекты\Traffic-Vision-\Test video output\output"

    cut_video(input_video, output_prefix)
