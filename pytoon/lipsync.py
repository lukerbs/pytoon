from forcealign import ForceAlign
from .util import read_json
from dataclasses import dataclass
from datetime import datetime
from typing import Union
import random
import re

# Viseme image for silence (i.e. closed mouth, not speaking)
SILENT_VISEME = "9.png"
SILENT_PHONEME = "PAUSE"
# ARPAbet phonemes to simplified phonemes mapping
PHONEMES = read_json("phonemes.json")
# Simplified phonemes to viseme-sequence mapping
VISEMES = read_json("visemes.json")


@dataclass
class WordViseme:
    word: Union[str, None]  # Word associated with viseme
    visemes: list[str]  # List of mouth shape images for viseme
    phonemes: list[str]  # The phoneme associated with the viseme
    time_start: datetime  # The time the word starts (seconds)
    time_end: datetime  # The time the word ends (seconds)
    duration: float  # total word duration from start to end (seconds)
    total_frames: int  # total number of frames in video for word
    breath: bool


def viseme_sequencer(audio_file: str, transcript: str, fps:int=48) -> list[WordViseme]:
    """Converts and audio / txt file to force aligned viseme sequence

    Args:
        audio_file (str): Path to audio file of a person speaking english (.wav or .mp3)
        transcript (str): Trascript string of audio recording

    Returns:
        list[WordViseme]: A list of force aligned WordViseme objects
    """
    ENDING_SILENCE_SECONDS = 2.5
    # Provide path to audio_file and corresponding txt_file with audio transcript
    aligner = ForceAlign(audio_file=audio_file, transcript=transcript)

    # Runs forced alignment algorithm and returns alignment results
    words = aligner.inference()

    first_word = words[0]
    print(f"Time Start: {first_word.time_start}")
    last_word = words[-1]
    total_duration = last_word.time_end
    target_frames = int(total_duration * fps) 
    print(f"Target Duration: {total_duration + ENDING_SILENCE_SECONDS}")
    print(f"Target Frames: {target_frames + int(ENDING_SILENCE_SECONDS *fps)}")

    viseme_sequence = []
    for word in words:
        phonemes = [phoneme_no_stress(phoneme) for phoneme in word.phonemes]
        images = [phoneme_to_viseme(phoneme=phoneme) for phoneme in phonemes]
        duration = word.time_end - word.time_start
        total_frames = int((duration / total_duration) * target_frames)

        remainder = ((duration / total_duration) * target_frames) % 1
        if random.choices([True, False], [remainder, (1-remainder)])[0]:
            total_frames += 1

        # If viseme is more than one frame long
        visemes = generate_viseme_frames(sequence=images, total_frames=total_frames)
        total_frames = len(visemes)

        viseme_sequence.append(
            WordViseme(
                word=word.word,
                visemes=visemes,
                phonemes=phonemes,
                time_start=word.time_start,
                time_end=word.time_end,
                duration=duration,
                total_frames=total_frames,
                breath=word.breath
            )
        )

    # Add silence viseme (closed mouth) between speaking visemes
    finished_sequence = []
    for i, _ in enumerate(viseme_sequence):
        finished_sequence.append(viseme_sequence[i])
        if i == len(viseme_sequence) - 1:
            break

        silent_viseme = get_silent_viseme(
            viseme_sequence[i], viseme_sequence[i + 1], total_duration, target_frames
        )
        if silent_viseme:
            finished_sequence.append(silent_viseme)
    
    finshed_sequence = upsample(finished_sequence, length=target_frames)
    silence = ending_silence(duration=ENDING_SILENCE_SECONDS, fps=fps, start_t=total_duration+0.001)
    finished_sequence.append(silence)
    return finished_sequence


def generate_viseme_frames(sequence: list, total_frames: int) -> list:
    """Generates the complete viseme frame sequence for word viseme

    Args:
        sequence (list): List of visemes in word
        total_frames (int): Total frames allocated to full word

    Returns:
        list: Completed viseme video sequence of images for word
    """
    frames_per_subviseme = total_frames // len(sequence)
    remainder_end = total_frames % len(sequence)
    if frames_per_subviseme == 0:
        if random.choice([True, False]):
            frames_per_subviseme = 1
        else:
            return []

    viseme_frames = []
    for i, _ in enumerate(sequence):
        if len(sequence[i]) > frames_per_subviseme:
            viseme_frames.extend(sequence[i][:frames_per_subviseme])
        elif len(sequence[i]) < frames_per_subviseme:
            seq = upsample(sequence[i], frames_per_subviseme)
            viseme_frames.extend(seq)
        else:
            viseme_frames.extend(sequence[i])

    # Upsample the frames to target length
    if len(viseme_frames) < total_frames:
        viseme_frames = upsample(viseme_frames, total_frames)
    
    return viseme_frames


def upsample(sequence, length):
    repetitions = length // len(sequence)
    remainder = length % len(sequence)
    upsampled = [elem for elem in sequence for _ in range(repetitions)]

    final_upsampled = []
    for i, _ in enumerate(upsampled):
        if i > (len(upsampled) - remainder - 1):
            final_upsampled.extend([upsampled[i], upsampled[i]])
        else:
            final_upsampled.append(upsampled[i])

    return final_upsampled


def phoneme_no_stress(phoneme: str) -> str:
    """Removes stress symbol from an ARPAbet phoneme

    Args:
        phoneme (str): An ARPAbet phoneme

    Returns:
        str: ARPAbet phoneme without stress symbol
    """
    if phoneme[-1].isdigit():
        return phoneme[:-1]
    else:
        return phoneme


def phoneme_to_viseme(phoneme: str) -> list[str]:
    """Converts a phoneme to a viseme image sequence

    Args:
        phoneme (str): An ARPAbet phoneme

    Returns:
        str: A list of images files for the viseme
    """
    phoneme = phoneme_no_stress(phoneme=phoneme)
    simplified_phone = PHONEMES[phoneme]
    viseme = VISEMES[simplified_phone]
    return viseme


def get_silent_viseme(current_viseme, next_viseme, total_duration, target_frames):
    # The time the silent viseme should start after previous viseme (i.e. the next frame)
    delta = 0.00000000000000000001

    # Get start time, end time, and total duration of silence
    silence_start = current_viseme.time_end + delta
    silence_end = next_viseme.time_start - delta
    duration = silence_end - silence_start

    # Get number of frames for silence segment (24 frames per second of silence)
    total_frames = int((duration / total_duration) * target_frames)
    remainder = ((duration / total_duration) * target_frames) % 1
    if random.choices([True, False], [remainder, (1-remainder)])[0]:
        total_frames += 1

    # Create frames for silence
    silent_visemes = [SILENT_VISEME for _ in range(total_frames)]
    phonemes = [SILENT_PHONEME for _ in range(total_frames)]
    return WordViseme(
        word=None,
        visemes=silent_visemes,
        phonemes=phonemes,
        time_start=silence_start,
        time_end=silence_end,
        duration=duration,
        total_frames=total_frames,
        breath=False
    )

def ending_silence(duration:float, fps:int, start_t:int):
    total_frames = int(duration * fps)

    # Create frames for silence
    silent_visemes = [SILENT_VISEME for _ in range(total_frames)]
    phonemes = [SILENT_PHONEME for _ in range(total_frames)]
    return WordViseme(
        word=None,
        visemes=silent_visemes,
        phonemes=phonemes,
        time_start=start_t,
        time_end=start_t+duration,
        duration=duration,
        total_frames=total_frames,
        breath=False
    )