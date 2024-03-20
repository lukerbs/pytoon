import json
import os


def read_json(file: str) -> dict:
    """Reads a json file to dictionary

    Args:
        path (str): Path to the json file.

    Returns:
        dict: Python dictionary with json data.
    """
    path = f"{os.path.dirname(__file__)}/assets/{file}"
    with open(path, "r") as file:
        data = json.load(file)
    return data


def write_json(data: dict, file: str) -> None:
    """Writes a Python dictionary to a json file.

    Args:
        data (dict): Python dictionary with data.
        path (str): The path to the output json file.
    """
    path = f"{os.path.dirname(__file__)}/assets/{file}"
    with open(path, "w") as file:
        json.dump(data, file, indent=4)
