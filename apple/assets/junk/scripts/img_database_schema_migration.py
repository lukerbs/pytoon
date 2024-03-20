import time
import json

from pprint import pprint
from PIL import Image
import copy

from apple.animator import (
    load_poses,
    load_mouths,
    mouth_coordinates,
    mouth_transformation,
)
from apple.util import read_json, write_json


data_templates = read_json(file="poses.json")
pprint(data_templates)
print("\n\n")
emotions_template = data_templates["emotions"]
pose_template = data_templates["pose"]

pose_files = load_poses()
mouth_files = load_mouths()
transformations = mouth_coordinates()
# print(transformations)

emotions = []
for i in range(0, len(pose_files), 15):
    files = [file.rsplit("/", 2)[-1] for file in pose_files[i : i + 15]]
    emotions.append(files)

emotion_labels = ["explain", "happy", "sad", "angry", "confused", "rhetorical"]
emotion_count = 0
pose_count = 0
pose_variation_count = 0

data = emotions_template
# pprint(emotions_template)
for emotion in emotions:
    emotion_label = emotion_labels[emotion_count]
    print(f"Emotion {emotion_count}: {emotion_label}")
    for i in range(0, len(emotion), 3):
        pose_variation = emotion[i : i + 3]
        pose_data = copy.deepcopy(pose_template)
        print(f"Pose {pose_count}: {pose_variation}")
        pose_data["image_files"]["open"] = f"/assets/poses/{pose_variation[0]}"
        pose_data["image_files"]["middle"] = f"/assets/poses/{pose_variation[1]}"
        pose_data["image_files"]["shut"] = f"/assets/poses/{pose_variation[2]}"
        # print(pose_data["image_files"])

        transformation = transformations[pose_count]
        if transformation[2] < 0:
            print("FLIP!")
            flip = True
            scale_x = abs(transformation[2])
        else:
            flip = False
            scale_x = abs(transformation[2])

        pose_data["mouth_coordinates"]["x"] = round(transformation[0], 1)
        pose_data["mouth_coordinates"]["y"] = round(transformation[1], 1)
        pose_data["mouth_coordinates"]["scale_x"] = scale_x
        pose_data["mouth_coordinates"]["scale_y"] = abs(transformation[3])
        pose_data["mouth_coordinates"]["flip_x"] = flip
        pose_data["mouth_coordinates"]["rotation"] = transformation[4]
        # pprint(pose_data)

        data[emotion_label].append(pose_data)
        print(pose_count)
        pose_count += 1

    emotion_count += 1

pprint(data, sort_dicts=False)
final_outut = {"emotions": data}
write_json(data=final_outut, file="out.json")
