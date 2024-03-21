import os
import json
import random

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


def animate(images: list[str], mouth_coords: list, fps: int, video_path: str) -> None:
    """Turns a sequence of images into an mp4 video

    Args:
        photos (list[str]): List of paths to image files, in sequential order
        video_path (str): Output .mp4 file path for final video
    """
    images = [f"{os.path.dirname(__file__)}{image}" for image in images]
    all_mouths = load_mouths()
    mouth_shapes = []
    done = False
    while True:
        if done:
            break
        mouth = random.choice(all_mouths)
        for _ in range(int(fps * 0.1)):
            if len(mouth_shapes) >= len(images):
                done = True
                break
            else:
                mouth_shapes.append(mouth)

    mouth_frames = []
    for i, _ in enumerate(mouth_shapes):

        im = mouth_transformation(
            mouth_file=mouth_shapes[i], mouth_coord=mouth_coords[i]
        )
        mouth_frames.append(im)

    # set frame size
    img = cv2.imread(images[0])
    height, width, _ = img.shape

    frame_size = (width, height)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(video_path, fourcc, fps, frame_size)

    for i, _ in enumerate(images):
        frame = cv2.imread(images[i])
        final_frame = render_frame(
            pose_img=frame, mouth_img=mouth_frames[i], mouth_coord=mouth_coords[i]
        )

        out.write(final_frame)
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


def mouth_transformation(mouth_file, mouth_coord) -> Image:
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
    mouth = Image.open(mouth_file)
    # Flip mouth horizontally if necessary
    if mouth_coord.flip_x is True:
        mouth = mouth.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    # Scale mouth image if necessary
    if mouth_coord.scale_y != 1:
        og_width, og_height = mouth.size
        new_width = int(abs(og_width * mouth_coord.scale_x))
        new_height = int(og_height * mouth_coord.scale_y)
        try:
            mouth = mouth.resize(new_width, new_height, Image.Resampling.LANCZOS)
        except:
            pass
    # Apply image rotation if necessary
    if mouth_coord.rotation != 0:
        mouth = mouth.rotate(-mouth_coord.rotation, resample=Image.Resampling.BICUBIC)
    return mouth


def render_frame(pose_img: Image, mouth_img: Image, mouth_coord):
    pose_img = Image.fromarray(pose_img)
    mouth_width, mouth_height = mouth_img.size

    # Location in pose image where mouth / viseme image will be added
    paste_coordinates = (
        int(mouth_coord.x - (mouth_width / 2)),
        int(mouth_coord.y - (mouth_height / 2)),
    )

    # Paste the mouth image onto the face image at the specified coordinates
    pose_img.paste(im=mouth_img, box=paste_coordinates, mask=mouth_img)
    np_image = np.array(pose_img)

    # Convert BGR PIL image to RGB (if necessary)
    if np_image.shape[2] == 3:
        np_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
    return np_image
