
# PyToon
[![Downloads](https://static.pepy.tech/badge/pytoon)](https://pepy.tech/project/pytoon)

## Overview 
PyToon is a Python-based animation library for automatically animating characters and their mouth movements from just an audio file (.mp3 or .wav) of a person speaking English. This tool uses machine learning-based audio analysis techniques to automatically lip-sync animated character mouth movements to a given audio recording of someone talking. It is designed to easily overlay the generated animation over custom background videos in a "presentation" style video format. You can see an example of a PyToon generated animation in the YouTube link below:

[Example Output Video](https://www.youtube.com/watch?v=Sg2OBBNwF-k&ab_channel=LKerbs)

**Installation:** `pip install pytoon`

## Features
- Automatically create cartoon animated lip-sync videos from just an audio file.
- Use a provided transcript or let PyToon automatically generate the transcript from the audio with built-in text-to-speech.
- Programmatically generate animated videos.
- Overlay animations over custom background videos or images.
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
from moviepy.editor import VideoFileClip # Note: this example uses MoviePy v1.0.3

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

### Example 2: Generating Animation from an MP3 File (without transcript)
If you do not have a transcript for the audio, PyToon can automatically generate one using text-to-speech.

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

## Contributing
We welcome contributions to PyToon! To contribute, follow these simple steps:
1. **Fork the Repository**: Click the "Fork" button on the GitHub repository to create a copy under your account.
2. **Clone Your Fork**: Clone your forked repository to your local machine.
   ```bash
   git clone https://github.com/your-username/pytoon.git
   ```
3. **Create a Branch**: Create a new branch for your feature or bug fix.
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make Changes**: Implement your feature or fix the bug in your branch.
6. **Sync with main branch**: Pull the main branch locally and merge any new updates into your feature branch.
    - Fix any merge conflicts if necessary.
7. **Test Your Changes**: Ensure that the `demo.py` script works correctly with your changes.
8. **Commit and Push**: Commit your changes to your branch and push them to your forked repository.
   ```bash
   git add .
   git commit -m "Add your descriptive commit message here"
   git push origin feature/your-feature-name
   ```
9. **Submit a Pull Request**: Open a pull request from your branch to the main repository and describe your changes.
    - Be detailed about what changes your made and the value that it adds.

Thank you for contributing!

## Coming Soon
Bookly is an active project and will be updated whenever I have time to work on it. Somethings to look forward to are:
1. Use create and use custom cartoon characters.
2. Create and use custom emotional expressions and and gestures.
3. Automatic text-to-emotion detection for gestures and facial expressions.

## Acknowledgements
This project uses character images open sourced by: [GitHub: lazykh](https://github.com/carykh/lazykh)
You can check out his YouTube channel here: [YouTube: carykh](https://youtube.com/@carykh)
