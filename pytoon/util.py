import json
import os
from scipy.io import wavfile
from scipy.signal import resample
import numpy as np


def read_json(file: str) -> dict:
    """Reads a json file to dictionary

    Args:
        path (str): Path to the json file.

    Returns:
        dict: Python dictionary with json data.
    """
    path = f"{os.path.dirname(__file__)}/assets/{file}"
    with open(path, "r") as file:
        data = json.load(file)
    return data


def write_json(data: dict, file: str) -> None:
    """Writes a Python dictionary to a json file.

    Args:
        data (dict): Python dictionary with data.
        path (str): The path to the output json file.
    """
    path = f"{os.path.dirname(__file__)}/assets/{file}"
    with open(path, "w") as file:
        json.dump(data, file, indent=4)


def resample_audio(
    audio_file: str,
    output_file: str = None,
    target_sr: int = 48000,
    padding: bool = True,
):
    """Resamples audio to a target sample rate

    Args:
        audio_file (str): Path to audio file to be resampled
        output_file (str, optional): Path to save new file. Defaults to None.
        target_sr (int, optional): Target sample rate. Defaults to 48000.
        padding (bool, optional): Extends duration of audio to nearest integer number of seconds.

    Returns:
        tuple: Returns numpy array of resampled audio and the new audio sample rate
    """
    original_sample_rate, audio_data = wavfile.read(audio_file)
    resample_ratio = target_sr / original_sample_rate
    total_samples = int(len(audio_data) * resample_ratio)

    # Resamples the audio to have only 'total_samples' number of samples
    resampled_audio = resample(x=audio_data, num=total_samples)
    resampled_audio = resampled_audio.astype(np.int16)

    # Adds silence to end of audio so num samples is divisible by sample rate
    zero_pad = target_sr - (len(resampled_audio) % target_sr)
    if padding and int(zero_pad) not in [0, target_sr]:
        silence = np.zeros(zero_pad, dtype=np.int16)
        resampled_audio = np.concatenate((resampled_audio, silence))

    if output_file:
        wavfile.write(output_file, target_sr, resampled_audio)

    padding_secs = round((padding / target_sr), 2)
    return resampled_audio, target_sr


def add_outline(image_path, outline_color=(255, 255, 255), outline_width=5):
    """
    Adds a white outline around a .png image that has a transparent background
    """
    # Open the image
    img = Image.open(image_path)

    # Convert image to RGBA if not already
    img = img.convert("RGBA")

    # Create a new image with the same size as the original image
    outline_img = Image.new("RGBA", img.size, (255, 255, 255, 0))

    # Get pixel data
    pixels = img.load()
    outline_pixels = outline_img.load()

    # Add white outline
    for x in range(img.width):
        for y in range(img.height):
            r, g, b, a = pixels[x, y]
            if a > 0:  # Check if pixel is not transparent
                for dx in range(-outline_width, outline_width + 1):
                    for dy in range(-outline_width, outline_width + 1):
                        # Avoid out-of-bounds access
                        if 0 <= x + dx < img.width and 0 <= y + dy < img.height:
                            outline_pixels[x + dx, y + dy] = outline_color

    # Overlay the original image on top of the outline image
    outline_img.paste(img, (0, 0), mask=img)
    outline_img.save(image_path)
