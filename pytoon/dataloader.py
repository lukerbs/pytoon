from dataclasses import dataclass
from .util import read_json
from copy import deepcopy


@dataclass
class MouthCoordinates:
    """Data class for mouth image coordinate and transformation data"""

    x: float  # Distance (pxls) from top border of mouth img to top border of pose img.
    y: float  # Distance (pxls) from left border of mouth img to left border of pose img.
    scale_x: float  # Multiple by which the image should be scaled along x-axis (width)
    scale_y: float  # Multiple by which the image should be scaled along y-axis (height)
    flip_x: bool  # Image should be flipped horizontally (about the center y-axis)
    rotation: float  # Counter clockwise degrees that the image should be rotated


@dataclass
class Pose:
    """Data class for storing data for specific character poses."""

    image_files: dict  # Dictionary containing paths to variations of the pose image.
    mouth_coordinates: MouthCoordinates  # Mouth coordinates / transformations.


@dataclass
class Emotions:
    """Data class for storing emotion specific poses"""

    explain: list[Pose]  # List of poses for the explain emotion.
    happy: list[Pose]  # List os poses for the happy emotion.
    rhetorical: list[Pose]  # List of poses for the sad emotion.

#sad: list[Pose]  # List of poses for the sad emotion.
#angry: list[Pose]  # List of poses for the sad emotion.
#confused: list[Pose]  # List of poses for the sad emotion.


def get_assets() -> Emotions:
    """Loads pose data from json file and returns as a dictionary.

    Returns:
        dict: Pose data, including paths to images, emotion specific poses, and mouth coords.
    """
    pose_data = read_json(file="pose_data.json")["emotions"]

    emotions = {}
    for emotion in pose_data.keys():
        if emotion not in ["sad", "angry", "confused"]:
            poses = []
            for i, _ in enumerate(pose_data[emotion]):
                images = deepcopy(pose_data[emotion][i]["image_files"])
                coords = deepcopy(pose_data[emotion][i]["mouth_coordinates"])
                pose = {
                    "image_files": images,
                    "mouth_coordinates": MouthCoordinates(**coords),
                }
                poses.append(Pose(**pose))
            emotions[emotion] = poses
    return Emotions(**emotions)
