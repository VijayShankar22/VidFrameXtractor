# VidFrameXtractor

**VidFrameXtractor** is a powerful Python tool for extracting, enhancing, and processing frames from video files. Whether you're working with a single video or an entire directory, this tool offers flexible options for frame extraction, metadata retrieval, and frame enhancement.

## Features
- **Batch Processing**: Process multiple videos at once by specifying a directory path.
- **Video Information Extraction**: Retrieve detailed metadata from your videos, including size, duration, bitrate, codec type, and stream information.
- **Frame Rate Control**: Specify custom frame extraction rates or extract frames between specific time intervals.
- **Frame Enhancement**: Enhance extracted frames with image sharpening or denoising.
- **Multithreading**: Efficiently handle large video files and directories with multithreaded processing.
- **Output Formats**: Save frames in multiple formats (JPG, PNG, BMP) with adjustable quality settings.

## Installation

Clone the repository:

```bash
git clone https://github.com/VijayShankar22/VidFrameXtractor.git
cd VidFrameXtractor
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Ensure `ffmpeg` is installed on your system and added to the PATH.

## Usage

Run the script:

```bash
python VidFrameXtractor.py
```

### Input Parameters:

- **Video/Directory Path**: Provide the path to a single video file or a directory containing multiple videos.
- **Output Folder**: Specify where the extracted frames should be saved.
- **Frame Rate**: Choose to extract frames at the original rate or specify a custom rate.
- **Image Format**: Choose between JPG, PNG, or BMP.
- **Quality**: Set the quality of the output images (0-100 for JPG, 0-9 for PNG).
- **Time Frame**: Extract frames between specific start and end times.
- **Frame Enhancement**: Choose whether to enhance the frames and select the enhancement method (sharpening, denoising).

