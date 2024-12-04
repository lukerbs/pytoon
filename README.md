
# PyToon
[![Downloads](https://static.pepy.tech/badge/pytoon)](https://pepy.tech/project/pytoon)

## Overview 
PyToon is a Python-based animation library for animating characters and their mouth movements. This tool uses machine learning-based audio analysis techniques to automatically lip-sync animated character mouth movements to a given audio recording of someone talking.

[Example Output Video](https://youtu.be/fX2loRnr7II)

## Features
- Automatically create cartoon animated lip-sync videos from just an audio file.
- Use a provided transcript or let PyToon automatically generate the transcript from the audio with built-in text-to-speech.
- Programmatically generate animated videos.
- OS Independent! PyToon works on Mac, Windows, and Linux.
- Optimized for both CPU and GPU.
- Fast Processing! A 60-second lip-sync animation clip takes ~39 seconds to generate.

## Getting Started 
1. Install pytoon: `pip3 install pytoon`
2. Install ffmpeg:
    - Mac: `brew install ffmpeg`
    - Linux: `sudo apt install ffmpeg`
    - Windows: Install from [ffmpeg.org](https://ffmpeg.org/download.html)

## Basic Usage

### Example 1: Generating Animation from an MP3 File (with transcript)
If you have a transcript of the audio, you can directly pass it to the `animate` function.

```python
from pytoon.animator import animate
from moviepy.editor import VideoFileClip

# Read audio transcript to a string.
transcript_path = "./.temp/speech.txt"
with open(transcript_path, "r") as file:
    transcript = file.read()

# Create a PyToon animation 
animation = animate(
    audio_file="speech.mp3",  # Input audio
    transcript=transcript,   # Audio transcript
)

# Overlay the animation on top of another video and save as an .mp4 file.
background_video = VideoFileClip("./path/to/background_video.mp4")
animation.export(path='video_with_transcript.mp4', background=background_video, scale=0.7)
```

### Example 2: Example 1: Generating Animation from an MP3 File (without transcript)
If you do not have a transcript, PyToon can automatically generate one using text-to-speech.

```python
from pytoon.animator import animate
from moviepy.editor import VideoFileClip

# Create a PyToon animation without providing a transcript
animation = animate(
    audio_file="speech.mp3"  # Input audio (transcript will be auto-generated)
)

# Overlay the animation on top of another video and save as an .mp4 file.
background_video = VideoFileClip("./path/to/background_video.mp4")
animation.export(path='video_auto_transcript.mp4', background=background_video, scale=0.7)
```

## Acknowledgements
This project uses character images created by [lazykh](https://github.com/carykh/lazykh).
