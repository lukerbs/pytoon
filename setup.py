from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="pytoon",
    version="1.4.2",
    packages=find_packages(),
    install_requires=[
        "forcealign==1.1.5",
        "moviepy",
        "opencv-python",
        "scipy",
        "numpy",
        "pillow",
    ],
    author="Luke Kerbs",
    description="A Python library for lip-syncing cartoons to voice recordings.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lukerbs/apple",
    keywords=[
        "animation",
        "forced alignment",
        "lip-sync",
        "audio forced alignment",
        "phoneme",
        "generate subtitles",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_data={"pytoon": ["assets/*", "assets/**/*", "assets/**/**/*"]},
    include_package_data=True,
)
