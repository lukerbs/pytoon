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
1. Clone the repo to your computer
2. Create a virtual environment: `python3 -m venv venv`
3. Activate your virtual environment: `source venv/bin/activate`
4. Install requirements: `pip3 install -r requirements.txt`

## Usage
- For usage example see `test.py` in the root directory of the repository. 
- Basic Usage:

```
from pytoon.animator import animate

transcript_path = "./.temp/speech.txt"
with open(transcript_path, "r") as file:
    transcript = file.read()

animate(
    audio_file="speech.mp3", # input audio
    transcript=transcript, # audio transcript
    video_path="final.mp4", # output video path
)
```

## Acknowledgements
This project uses character images created by [lazykh](https://github.com/carykh/lazykh).