import os
import json
import random

from PIL import Image
from datetime import datetime
import numpy as np
import cv2
import copy
from moviepy.editor import (
    ImageSequenceClip, 
    CompositeVideoClip, 
    CompositeAudioClip, 
    AudioFileClip,
    VideoClip
) 

from .util import read_json
from .dataloader import get_assets
from .lipsync import viseme_sequencer, upsample


class FrameSequence:
    def __init__(self):
        self.pose_files = []
        self.mouth_files = []
        self.pose_images = []
        self.mouth_images = []
        self.mouth_coords = []
        self.final_frames = []
        self.pose_changes = []


class animate:
    """Animates a cartoon that is lip synced to provieded audio voiceover."""
    def __init__(self, audio_file: str, transcript: str, fps:int=48):
        self.audio_file = audio_file
        self.sequence = FrameSequence()
        self.assets = get_assets()
        self.fps = fps
        self.final_frames = []

        # Initialize blinking rate (blink every 3 seconds)
        self.blink_rate = 3.0

        # Create sequence of mouth images
        self.viseme_sequence = viseme_sequencer(self.audio_file, transcript, self.fps)
        self.build_mouth_sequence()

        self.duration = len(self.sequence.mouth_files) / self.fps
        print(f"Num Created: {len(self.sequence.mouth_files)}")
        print(f"Duration: {self.duration}")

        self.build_pose_sequence()

        self.frame_size = self.get_frame_size()
        # Create the animation
        self.compile_animation()


    def build_pose_sequence(self):
        """Creates the sequence of pose images for the video"""
        emotion = self.random_emotion()
        pose = random.choice(emotion)

        # Add a character pose frame for every frame of a mouth
        for i,_ in enumerate(self.sequence.mouth_files):
            if self.sequence.pose_changes[i]:
                # Change the pose of the character
                emotion = self.random_emotion()
                pose = random.choice(emotion)

            eyes = self.blink_manager(idx=i)
            self.sequence.pose_files.append(pose.image_files[eyes])
            self.sequence.mouth_coords.append(pose.mouth_coordinates)

        # Prepend absolute path to all pose images
        self.sequence.pose_files = [
            f"{os.path.dirname(__file__)}{file}" for file in self.sequence.pose_files
        ]

        # Create mouth PIL image for every frame, with image transformations based on pose
        for i,_ in enumerate(self.sequence.mouth_files):
            transformed_image = mouth_transformation(
                mouth_file=self.sequence.mouth_files[i],
                mouth_coord=self.sequence.mouth_coords[i],
            )
            self.sequence.mouth_images.append(transformed_image)
        return
    
    def blink_manager(self, idx):

        BLINK_DURATION = 0.16
        SUB_BLINKS = ["middle", "shut", "middle"]

        frames_between_blinks = int(self.blink_rate * self.fps)
        frames_per_blink = int(BLINK_DURATION * self.fps)
        frames_per_sub_blink = int(frames_per_blink / len(SUB_BLINKS)) + 1

        full_cycle = frames_between_blinks + (frames_per_sub_blink * len(SUB_BLINKS))

        start_1 = frames_between_blinks
        start_2 = start_1 + frames_per_sub_blink
        start_3 = start_2 + frames_per_sub_blink
        end_3 = start_3 + frames_per_sub_blink

        if start_1 <= (idx % full_cycle) < start_2:
            eyes = "middle"

        elif start_2 <= (idx % full_cycle) < start_3:
            eyes = "shut"

        elif start_3 <= (idx % full_cycle) < end_3:
            eyes = "middle"

        else:
            eyes = "open"

        return eyes

    def build_mouth_sequence(self):
        """Generates a sequence of mouth images for video"""
        # Add mouth images to mouth image file sequence
        for i, _ in enumerate(self.viseme_sequence):
            if self.viseme_sequence[i].visemes:
                self.sequence.mouth_files.extend(self.viseme_sequence[i].visemes)
                pose_changes = [0] * len(self.viseme_sequence[i].visemes)
                if self.viseme_sequence[i].breath:
                    pose_changes[0] = 1
                    self.sequence.pose_changes.extend(pose_changes)
                else:
                    self.sequence.pose_changes.extend(pose_changes)

        # Prepend absolute path to mouth images
        for i, _ in enumerate(self.sequence.mouth_files):
            file = self.sequence.mouth_files[i]
            new_file = f"{os.path.dirname(__file__)}/assets/visemes/positive/{file}"
            self.sequence.mouth_files[i] = new_file

    def random_emotion(self):
        """Generates a random emotion to use in sequence

        Returns:
            list[Pose]: List of poses from a random emotion
        """
        emotions_list = list(self.assets.__dict__.keys())
        emotion = random.choice(emotions_list)
        return getattr(self.assets, emotion)

    def get_frame_size(self):
        pose_image = cv2.imread(self.sequence.pose_files[0])
        height, width, _ = pose_image.shape
        return (width, height)

    def compile_animation(self):
        for i, _ in enumerate(self.sequence.pose_files):
            frame = cv2.imread(self.sequence.pose_files[i], cv2.IMREAD_UNCHANGED)
            if self.sequence.mouth_files[i] is not None:
                final_frame = render_frame(
                    pose_img=frame,
                    mouth_img=self.sequence.mouth_images[i],
                    mouth_coord=self.sequence.mouth_coords[i],
                )
            else:
                final_frame = frame
            self.final_frames.append(final_frame)

    def export(self, path:str, background: VideoClip, scale: float=0.7):
        animation_clip = ImageSequenceClip(self.final_frames, fps=self.fps, with_mask=True)
        new_height = int(background.size[1] * scale)
        new_width = int(animation_clip.w * (new_height / animation_clip.h))
        animation_clip = animation_clip.resize(width=new_width, height=new_height)

        # Overlay the animation on top of thee background clip
        final_clip = CompositeVideoClip(
            clips=[background, animation_clip.set_position(("right", "bottom"))],
            use_bgclip=True
        )

        # Add speech audio to clip with 0.2 second delay
        audio_clip= AudioFileClip(self.audio_file)
        audio_clip = CompositeAudioClip([audio_clip.set_start(0.2)])
        final_clip = final_clip.set_audio(audio_clip)

        # Export video to .mp4 
        final_clip.write_videofile(path, codec="libx264", audio_codec='aac', preset="ultrafast", threads=4, fps=self.fps)
        


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
    mouth = copy.deepcopy(Image.open(mouth_file))
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


def bgra_to_rgba(image):
    # Swap blue and red channels
    b, g, r, a = np.rollaxis(image, axis=-1)
    return np.dstack([r, g, b, a])

def render_frame(pose_img: Image, mouth_img: Image, mouth_coord):
    pose_img = bgra_to_rgba(pose_img) # convert to rgba
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

    return np_image
