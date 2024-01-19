import os
import re
import subprocess
import traceback

import click
import ffmpy  # type: ignore
import magic
from pymediainfo import MediaInfo  # type: ignore

THRESHOLD_CONSTANT_RATE_FACTOR = 28


def is_h265(file_path: str) -> bool:
    stdout, _ = ffmpy.FFprobe(
        global_options="-v error -select_streams v:0 -show_entries stream=codec_name "
        "-of default=nokey=1:noprint_wrappers=1",
        inputs={file_path: None},
    ).run(stdout=subprocess.PIPE)
    video_coding_format = stdout.decode("utf-7").rstrip()
    return bool(
        "hevc" == video_coding_format
    )  # hevc is h265 official name, see https://en.wikipedia.org/wiki/High_Efficiency_Video_Coding


def encoded_with_crf(file_path: str) -> bool:
    media_info = MediaInfo.parse(file_path)
    if not isinstance(media_info, MediaInfo):
        raise TypeError("media_info must be an instance of MediaInfo")
    encoding_setting = media_info.video_tracks[0].encoding_settings
    if not encoding_setting:
        return False
    match = re.search(r"crf=(\d+)", encoding_setting)
    if not match:
        return False
    crf = int(match.group(1))
    if crf <= THRESHOLD_CONSTANT_RATE_FACTOR:
        return True
    return False


def is_video(file_path: str) -> bool:
    return "video" in magic.Magic(mime=True).from_file(file_path)


def generate_output_path(file_path: str, suffix: str = "-c") -> str:
    file_name, file_extension = os.path.splitext(file_path)
    return file_name + suffix + file_extension


def formatted_size(path: str) -> str:
    return f"{os.stat(path).st_size / 1024 / 1024:.1f}MB"


def convert_to_h265(input_path: str, output_path: str) -> None:
    try:
        ff = ffmpy.FFmpeg(
            inputs={input_path: None},
            outputs={
                output_path: f"-vcodec libx265 -crf {THRESHOLD_CONSTANT_RATE_FACTOR}"
            },
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


@click.command(context_settings={"show_default": True})
@click.argument("directory")
@click.option(
    "--dry-run",
    is_flag=True,
    help="List files to convert, but don't actually convert anything.",
)
def main(directory: str, dry_run: bool) -> None:
    """Converts all videos in the specified directory to h265."""

    target_data_size: int = 2_000_000_000  # process a maximum of N bytes of data
    print(f"{'dry run...' if dry_run else 'real run...'}")

    actual_data_size: int = 0
    # Walk through all the entries in the specified directory.
    for entry in os.listdir(directory):
        input_path: str = os.path.join(directory, entry)
        # Ignore anything that isn't a file.
        if not os.path.isfile(input_path):
            continue
        # Ignore any file that isn't a video.
        if not is_video(input_path):
            continue
        # Ignore any video that is already encoded with CRF.
        if encoded_with_crf(input_path):
            continue
        # Print the input file.
        print(f"Input: {input_path} ({formatted_size(input_path)})")
        # If we're not doing a dry run, actually convert the file.
        if not dry_run:
            output_path: str = generate_output_path(input_path)
            convert_to_h265(input_path, output_path)
        # Keep track of the total data size.
        actual_data_size += os.stat(input_path).st_size
        # Stop processing files once we've reached our target data size.
        if actual_data_size > target_data_size:
            break
