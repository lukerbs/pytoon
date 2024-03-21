import os
import json


from PIL import Image
import numpy as np
import cv2

from .util import read_json
from .dataloader import poses

"""
class animate:
    def __init__(self, audio_file: str, transcript: str):
        self.emotions = poses()
"""


def animate(images: list[str], mouths: list, fps: int, video_path: str) -> None:
    """Turns a sequence of images into an mp4 video

    Args:
        photos (list[str]): List of paths to image files, in sequential order
        video_path (str): Output .mp4 file path for final video
    """
    images = [f"{os.path.dirname(__file__)}{image}" for image in images]

    # set frame size
    img = cv2.imread(images[0])
    height, width, _ = img.shape

    frame_size = (width, height)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(video_path, fourcc, fps, frame_size)

    for image in images:
        frame = cv2.imread(image)
        out.write(frame)
    out.release()
    return


def load_poses():
    """Loads image file paths to pose images"""
    path = f"{os.path.dirname(__file__)}/assets/poses"
    files = os.listdir(path)
    files.sort(key=lambda x: int(x.split(".")[0]))
    files = [os.path.join(path, file) for file in files]
    return files


def load_mouths():
    """Loads image file paths to mouth images"""
    path = f"{os.path.dirname(__file__)}/assets/mouths"
    files = os.listdir(path)
    files.sort(key=lambda x: int(x.split(".")[0]))
    files = [os.path.join(path, file) for file in files]
    return files


def mouth_coordinates():
    """
    0: Width
    1: Height
    2: Flip Horizontal
    3: Resize
    4: Rotate
    """
    path = f"{os.path.dirname(__file__)}/assets/mouth_coordinates.json"
    with open(path, "r") as file:
        data = json.load(file)
        coordinates = data["coordinates"]

    coordinates = np.array(coordinates)
    # IMPORTANT: will no longer need to do this with new COORDINATES SYSTEM
    coordinates[:, 0:2] *= 3
    return coordinates


def mouth_transformation(mouth_path: str, transformation: np.array) -> Image:
    """Transforms mouth image with scaling, flipping, and rotation.
        This transformation is applied because, the same mouth shape images
        are used for different pose images, but the size, angle, and position
        of a mouth image will depend on which pose image is being used.

    Args:
        mouth_path (str): .png file path pointing to mouth image
        transformation (np.array): image transformation data for mouth

    Returns:
        Image: PIL Image object of mouth image with applied transformations
    """
    mouth = Image.open(mouth_path)
    # Flip mouth horizontally if necessary
    if transformation[2] == -1:
        mouth = mouth.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    # Scale mouth image if necessary
    if transformation[3] != 1:
        og_width, og_height = mouth.size
        new_width = int(abs(og_width * transformation[2]))
        new_height = int(og_height * transformation[3])
        mouth = mouth.resize(new_width, new_height, Image.Resampling.LANCZOS)
    # Apply image rotation if necessary
    if transformation[4] != 0:
        mouth = mouth.rotate(-transformation[4], resample=Image.Resampling.BICUBIC)
    return mouth


def render_frame(pose_img: Image, mouth_img: Image, transformation: np.array):
    mouth_width, mouth_height = mouth_img.size
    print(f"Mouth Shape: {mouth_img.size}")

    # Location in pose image where mouth / viseme image will be added
    paste_coordinates = (
        int(transformation[0] - (mouth_width / 2)),
        int(transformation[1] - (mouth_height / 2)),
    )
    print(f"Mouth Coords: {paste_coordinates}")

    # Paste the mouth image onto the face image at the specified coordinates
    print(f"Pose Size: {pose_img.size}")
    pose_img.paste(im=mouth_img, box=paste_coordinates, mask=mouth_img)
    return pose_img
