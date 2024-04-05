# PyToon
## Overview 
PyToon is a Python based animation library for animating characters and their mouth movements. This tools uses machine learning based audio analysis techiques to automatically lip-sync animated character mouth mouth movements to a given audio recording of someone talking.

[Example Output Video](https://youtu.be/fX2loRnr7II)

## Features
- Automatically create cartoon animated lip-sync videos from just an audio file.
- Programmatically generate videos.
- OS Independent! PyToon works on Mac, Windows, and Linux 
- Optimized for both CPU and GPU
- Fast Processing! A 60 second audio clip takes ~52 seconds to generate a lip-synced video.

## Getting Started 
1. Install pytoon: `pip3 install pytoon`
2. Install ffmpeg
    - Mac: `brew install ffmpeg`
    - Linux: `sudo apt install ffmpeg`
    - Windows: Install from [ffmpeg.org](https://ffmpeg.org/download.html)

## Basic Usage
### Generating a Lip-Sync animation and saving to .mp4 file.
```
from pytoon.animator import animate
from moviepy.editor import VideoFileClip

# Read audio transcript to a string.
transcript_path = "./.temp/speech.txt"
with open(transcript_path, "r") as file:
    transcript = file.read()

# Create a Pytoon animation 
animation = animate(
    audio_file="speech.mp3", # input audio
    transcript=transcript, # audio transcript
)

# Overlay the animation on top of another video and save as an .mp4 file.
background_video = VideoFileClip("./path/to/background_video.mp4")
animation.export(path='video.mp4', background=background_video, scale=0.7)
```

## Acknowledgements
This project uses character images created by [lazykh](https://github.com/carykh/lazykh).