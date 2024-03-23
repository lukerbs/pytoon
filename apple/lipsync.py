from forcealign import ForceAlign
from .util import read_json
from dataclasses import dataclass
from datetime import datetime

# ARPAbet phonemes to simplified phonemes mapping
PHONEMES = read_json("phonemes.json")
# Simplified phonemes to viseme-sequence mapping
VISEMES = read_json("visemes.json")


@dataclass
class WordViseme:
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

    print(f"Wanted: {total_frames}; Created: {len(viseme_frames)}")
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
    FPS = 24
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
                visemes=visemes,
                phonemes=phonemes,
                time_start=word.time_start,
                time_end=word.time_end,
                duration=duration,
                total_frames=total_frames,
            )
        )
    return viseme_sequence
