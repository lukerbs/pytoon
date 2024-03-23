from forcealign import ForceAlign
from .util import read_json
from dataclasses import dataclass
from datetime import datetime

# ARPAbet phonemes to simplified phonemes mapping
PHONEMES = read_json("phonemes.json")
# Simplified phonemes to viseme-sequence mapping
VISEMES = read_json("visemes.json")


@dataclass
class Viseme:
    viseme: list[str]  # List of mouth shape images for viseme
    phoneme: str  # The phoneme associated with the viseme
    time_start: datetime  # The time the viseme starts (seconds)
    time_end: datetime  # The time the viseme ends (seconds)
    duration: float  # total viseme duration from start to end (seconds)


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


def viseme_sequencer(audio_file: str, txt_file: str) -> list[Viseme]:
    """Converts and audio / txt file to force aligned viseme sequence

    Args:
        audio_file (str): Path to audio file of a person speaking english (.wav or .mp3)
        txt_file (str): Path to txt file trascript of audio recording

    Returns:
        list[Viseme]: A list of force aligned Viseme objects
    """
    # Provide path to audio_file and corresponding txt_file with audio transcript
    aligner = ForceAlign(audio_file=audio_file, txt_file=txt_file)

    # Runs forced alignment algorithm and returns alignment results
    aligner.inference()
    phonemes = aligner.phoneme_alignments

    # Convert phonemes to visime sequence
    viseme_sequence = []
    for phoneme in phonemes:
        viseme = phoneme_to_viseme(phoneme=phoneme.phoneme)
        duration = round((phoneme.time_end - phoneme.time_start), 10)
        viseme_sequence.append(
            Viseme(
                viseme=viseme,
                phoneme=phoneme_no_stress(phoneme.phoneme),
                time_start=phoneme.time_start,
                time_end=phoneme.time_end,
                duration=duration,
            )
        )
    return viseme_sequence
