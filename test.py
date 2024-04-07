from pytoon.animator import animate
from pprint import pprint

from moviepy.editor import VideoFileClip, AudioFileClip, vfx, ImageClip, ImageSequenceClip, concatenate_videoclips, VideoClip, CompositeVideoClip, CompositeAudioClip

FPS = 48
text_path = "./.temp/speech.txt"
audio_path = "./.temp/speech.mp3"
output_video = "./test.mp4"

with open(text_path, "r") as file:
    transcript = file.read()

animation = animate(
    audio_file=audio_path,
    transcript=transcript
)

video_clip = ImageClip("./.temp/image.jpeg")
video_clip.set_fps(FPS)
video_clip.duration = animation.duration

animation.export(path=output_video, background=video_clip)