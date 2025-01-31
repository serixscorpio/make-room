import os
import re
import traceback

import click
import ffmpy  # type: ignore
from pymediainfo import (  # type:ignore
    MediaInfo,
    Track,
)

THRESHOLD_CONSTANT_RATE_FACTOR = 23


def encoded_with_crf(file_path: str) -> bool:
    print(f"Checking {file_path} to see if it's encoded with CRF...")
    tracks = video_tracks(file_path)
    if not tracks:
        raise ValueError(f"No video tracks found in {file_path}")
    encoding_setting = tracks[0].encoding_settings
    if not encoding_setting:
        return False
    match = re.search(r"crf=(\d+)", encoding_setting)
    if not match:
        return False
    crf = int(match.group(1))
    if crf <= THRESHOLD_CONSTANT_RATE_FACTOR:
        return True
    return False


def video_tracks(file_path: str) -> list[Track]:
    media_info = MediaInfo.parse(file_path)
    if not isinstance(media_info, MediaInfo):
        raise TypeError("media_info must be an instance of MediaInfo")
    return media_info.video_tracks


def generate_output_path(file_path: str, suffix: str = "-c") -> str:
    file_name, file_extension = os.path.splitext(file_path)
    return file_name + suffix + ".mp4"  # convert to mp4 for compatibility with most devices


def formatted_size(path: str) -> str:
    return f"{os.stat(path).st_size / 1024 / 1024:.1f}MB"


def convert_to_h265(input_path: str, output_path: str) -> None:
    try:
        ff = ffmpy.FFmpeg(
            inputs={input_path: None},
            outputs={output_path: f"-vcodec libx265 -crf {THRESHOLD_CONSTANT_RATE_FACTOR} -c:a aac"},
        )
        ff.run(
            stdout=open(os.devnull),  # suppress output to console
            stderr=None,  # display error to console
        )
    except ffmpy.FFRuntimeError:
        traceback.print_exc()
    print(f"Output: {output_path} ({formatted_size(output_path)})")
    # Commented out the following to avoid potential data loss.  For better safety.
    # os.remove(input_path)
    # print(f"Removed {input_path}")


def make_room_at(path: str, dry_run: bool) -> None:
    # Ignore anything that isn't a file.
    if not os.path.isfile(path):
        return
    # Ignore any file that isn't a video.
    if not video_tracks(path):
        return
    # Notice any video that is already encoded with CRF.
    if encoded_with_crf(path):
        print(f"Already encoded with CRF: {path}")
        return
    # Print the input file.
    print(f"Input: {path} ({formatted_size(path)})")
    # If we're not doing a dry run, actually convert the file.
    if not dry_run:
        output_path: str = generate_output_path(path)
        convert_to_h265(path, output_path)


@click.command(context_settings={"show_default": True})
@click.argument("path")
@click.option(
    "--dry-run",
    is_flag=True,
    help="List files to convert, but don't actually convert anything.",
)
def main(path: str, dry_run: bool) -> None:
    """Converts all videos in the specified directory to h265. see https://en.wikipedia.org/wiki/High_Efficiency_Video_Coding"""

    print(f"{'dry run...' if dry_run else 'real run...'}")

    # If the path is a file, process the single file.
    if os.path.isfile(path):
        make_room_at(path, dry_run)
        return

    # Or, process path as a directory. Walk through entries in the directory, 1-level deep (i.e. non-recursively).
    actual_data_size: int = 0
    target_data_size: int = 4_000_000_000  # process a maximum of N bytes of data
    for entry in os.listdir(path):
        input_path: str = os.path.join(path, entry)
        make_room_at(input_path, dry_run)
        # Keep track of the total data size.
        actual_data_size += os.stat(input_path).st_size
        # Stop processing files once we've reached our target data size.
        if actual_data_size > target_data_size:
            break
