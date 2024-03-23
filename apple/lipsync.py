from forcealign import ForceAlign
from .util import read_json
from dataclasses import dataclass
from datetime import datetime
from typing import Union

FPS = 24
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


def generate_viseme_frames(sequence: list, total_frames: int) -> list:
    """Generates the complete viseme frame sequence for word viseme

    Args:
        sequence (list): List of visemes in word
        total_frames (int): Total frames allocated to full word

    Returns:
        list: Completed viseme video sequence of images for word
    """
    if total_frames <= 0:
        raise Exception("total_frames must be an integer greater than 0.")

    frames_per_subviseme = total_frames // len(sequence)
    remainder_end = total_frames % len(sequence)
    if frames_per_subviseme == 0:
        frames_per_subviseme = 1

    viseme_frames = []
    for i, _ in enumerate(sequence):
        sub_sequence = sequence[i]
        if len(sub_sequence) > frames_per_subviseme:
            viseme_frames.extend(sub_sequence[:frames_per_subviseme])
        elif len(sub_sequence) < frames_per_subviseme:
            multiple = frames_per_subviseme // len(sequence)
            remainder = frames_per_subviseme % len(sequence)
            for _ in range(multiple):
                viseme_frames.extend(sub_sequence)
            last_frame = sub_sequence[-1]
            for _ in range(remainder):
                viseme_frames.append(last_frame)
        else:
            viseme_frames.extend(sub_sequence)

    if remainder_end:
        last_frame = viseme_frames[-1]
        for _ in range(remainder_end):
            viseme_frames.append(last_frame)
    if len(viseme_frames) > total_frames:
        remove_n = len(viseme_frames) // total_frames
        viseme_frames = [
            viseme_frames[i]
            for i in range(len(viseme_frames))
            if (i + 1) % remove_n != 0
        ]
        viseme_frames = viseme_frames[:total_frames]

    return viseme_frames


def viseme_sequencer(audio_file: str, txt_file: str) -> list[WordViseme]:
    """Converts and audio / txt file to force aligned viseme sequence

    Args:
        audio_file (str): Path to audio file of a person speaking english (.wav or .mp3)
        txt_file (str): Path to txt file trascript of audio recording

    Returns:
        list[WordViseme]: A list of force aligned WordViseme objects
    """
    # Provide path to audio_file and corresponding txt_file with audio transcript
    aligner = ForceAlign(audio_file=audio_file, txt_file=txt_file)

    # Runs forced alignment algorithm and returns alignment results
    words = aligner.inference()

    viseme_sequence = []
    for word in words:
        phonemes = [phoneme_no_stress(phoneme) for phoneme in word.phonemes]
        images = [phoneme_to_viseme(phoneme=phoneme) for phoneme in phonemes]
        duration = word.time_end - word.time_start
        total_frames = int(duration * FPS)
        if total_frames:
            visemes = generate_viseme_frames(sequence=images, total_frames=total_frames)
            total_frames = len(visemes)
        else:
            visemes = None
            total_frames = None

        viseme_sequence.append(
            WordViseme(
                word=word.word,
                visemes=visemes,
                phonemes=phonemes,
                time_start=word.time_start,
                time_end=word.time_end,
                duration=duration,
                total_frames=total_frames,
            )
        )

    # Add silence viseme (closed mouth) between speaking visemes
    finished_sequence = []
    for i, _ in enumerate(viseme_sequence):
        finished_sequence.append(viseme_sequence[i])
        if i == len(viseme_sequence) - 1:
            break

        silent_viseme = get_silent_viseme(viseme_sequence[i], viseme_sequence[i + 1])
        if silent_viseme:
            finished_sequence.append(silent_viseme)

    return finished_sequence


def get_silent_viseme(current_viseme, next_viseme, fps=FPS):
    # The time the silent viseme should start after previous viseme (i.e. the next frame)
    delta = 1 / fps

    # Get start time, end time, and total duration of silence
    silence_start = current_viseme.time_end + delta
    silence_end = next_viseme.time_start - delta
    duration = silence_end - silence_start

    # Get number of frames for silence segment (24 frames per second of silence)
    total_frames = int(fps * duration)
    if total_frames <= 0:
        return None

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
    )
