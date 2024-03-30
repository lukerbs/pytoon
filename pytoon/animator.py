import os
import json
import random

from PIL import Image
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


class animate:
    """Animates a cartoon that is lip synced to provieded audio voiceover."""
    def __init__(self, audio_file: str, transcript: str, fps:int=48):
        self.audio_file = audio_file
        self.sequence = FrameSequence()
        self.assets = get_assets()
        self.fps = fps
        self.final_frames = []

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
        seconds_per_pose = 6
        seconds_per_blink = 3

        frame_count = 0
        blink_count = 0
        emotion = self.random_emotion()
        pose = random.choice(emotion)
        # Add a character pose frame for every frame of a mouth
        while len(self.sequence.pose_files) <= len(self.sequence.mouth_files):
            added_frames = len(self.sequence.pose_files) - frame_count
            if added_frames > seconds_per_pose * self.fps:
                # Change pose if 6 seconds has passed
                emotion = self.random_emotion()
                pose = random.choice(emotion)
                frame_count = len(self.sequence.pose_files)

            # Add 1 second worth of pose files to pose frames sequencs
            pose_files = [pose.image_files["open"] for _ in range(self.fps)]
            mouth_coords = [pose.mouth_coordinates for _ in range(self.fps)]
            self.sequence.pose_files.extend(pose_files)
            self.sequence.mouth_coords.extend(mouth_coords)

            # Character should blink every x seconds
            frames_since_blink = len(self.sequence.pose_files) - blink_count
            if frames_since_blink > seconds_per_blink * self.fps:
                self.blink(pose=pose)
                blink_count = len(self.sequence.pose_files)
                seconds_per_blink = random.randint(1, 3)

            # Shorten list of poses if too many were made
            if len(self.sequence.pose_files) > len(self.sequence.mouth_files):
                self.sequence.pose_files = self.sequence.pose_files[
                    : len(self.sequence.mouth_files)
                ]
                self.sequence.mouth_coords = self.sequence.mouth_coords[
                    : len(self.sequence.mouth_files)
                ]
                break

        # Prepend absolute path to all pose images
        self.sequence.pose_files = [
            f"{os.path.dirname(__file__)}{file}" for file in self.sequence.pose_files
        ]

        # Create mouth PIL image for every frame, with image transformations based on pose
        for i, _ in enumerate(self.sequence.mouth_files):
            transformed_image = mouth_transformation(
                mouth_file=self.sequence.mouth_files[i],
                mouth_coord=self.sequence.mouth_coords[i],
            )
            self.sequence.mouth_images.append(transformed_image)
        return

    def blink(self, pose):
        """Generates an animation sequence for eye blinking in a specific pose

        Args:
            pose (Pose): A Pose object containing pose configuration data

        Returns:
            int: Returns the number of frames that were generated for talling total generated
        """
        frames = []
        blink_duration = 0.4
        subsequence_duration = blink_duration / 5
        num_frames = int(self.fps * subsequence_duration)

        open_frames = [pose.image_files["open"] for _ in range(num_frames)]
        mid_frames = [pose.image_files["middle"] for _ in range(num_frames)]
        shut_frames = [pose.image_files["shut"] for _ in range(num_frames)]
        open_wait = [pose.image_files["open"] for _ in range(int(self.fps * 1.5))]

        frames.extend(open_frames)
        frames.extend(mid_frames)
        frames.extend(shut_frames)
        frames.extend(mid_frames)
        frames.extend(open_frames)

        self.sequence.pose_files.extend(frames)

        mouth_coords = [pose.mouth_coordinates for _ in range(len(frames))]
        self.sequence.mouth_coords.extend(mouth_coords)

        return len(frames)

    def build_mouth_sequence(self):
        """Generates a sequence of mouth images for video"""
        # Add mouth images to mouth image file sequence
        for i, _ in enumerate(self.viseme_sequence):
            if self.viseme_sequence[i].visemes:
                self.sequence.mouth_files.extend(self.viseme_sequence[i].visemes)

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

    def export(self, path:str, background: VideoClip):
        animation_clip = ImageSequenceClip(self.final_frames, fps=self.fps, with_mask=True)
        new_height = int(background.size[1])
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
        final_clip.write_videofile(path, codec="libx264", audio_codec='aac', fps=self.fps)





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

    # # Convert BGR PIL image to RGB (if necessary)
    # if np_image.shape[2] == 3:
    #     np_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
    return np_image
