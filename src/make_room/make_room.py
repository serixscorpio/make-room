import os
import re
import traceback

import click
import ffmpy
import magic
import pillow_avif  # type: ignore # noqa: F401
from PIL import Image, ImageFile
from pymediainfo import MediaInfo, Track

THRESHOLD_CONSTANT_RATE_FACTOR = 23


def is_jpeg(file_path: str) -> bool:
    try:
        return "image/jpeg" in magic.Magic(mime=True).from_file(file_path)
    except Exception:
        return False


def video_tracks(file_path: str) -> list[Track]:
    try:
        media_info = MediaInfo.parse(file_path)
        if not isinstance(media_info, MediaInfo):
            raise TypeError("media_info must be an instance of MediaInfo")
        return media_info.video_tracks
    except Exception:
        return []


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


def generate_output_path(file_path: str, suffix: str = "-c", extension: str = ".mp4") -> str:
    file_name, _ = os.path.splitext(file_path)
    return file_name + suffix + extension


def formatted_size(path: str) -> str:
    return f"{os.stat(path).st_size / 1024 / 1024:.1f}MB"


def convert_to_h265(input_path: str, output_path: str) -> None:
    try:
        ff = ffmpy.FFmpeg(
            inputs={input_path: None},
            outputs={
                output_path: f"-vcodec libx265 -crf {THRESHOLD_CONSTANT_RATE_FACTOR} -c:a aac"
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


def jpeg_to_avif(input_path: str, output_path: str) -> None:
    JPGimg = Image.open(input_path)
    JPGimg.save(output_path, "AVIF", quality=70)


def make_room_at(path: str, dry_run: bool) -> bool:
    # Ignore anything that isn't a file.
    if not os.path.isfile(path):
        return False

    # Process videos
    if video_tracks(path):
        # Notice any video that is already encoded with CRF.
        if encoded_with_crf(path):
            print(f"Already encoded with CRF: {path}")
            return False
        # Print the input file.
        print(f"Input: {path} ({formatted_size(path)})")
        # If we're not doing a dry run, actually convert the file.
        if not dry_run:
            output_path: str = generate_output_path(path)
            convert_to_h265(path, output_path)
        return True

    # Process images
    if is_jpeg(path):
        print(f"Input: {path} ({formatted_size(path)})")
        if not dry_run:
            output_path = generate_output_path(path, suffix="", extension=".avif")
            jpeg_to_avif(path, output_path)
            print(f"Output: {output_path} ({formatted_size(output_path)})")
        return True


@click.command(context_settings={"show_default": True})
@click.argument("path")
@click.option(
    "--dry-run",
    is_flag=True,
    help="List files to convert, but don't actually convert anything.",
)
@click.option(
    "--recursive/--no-recursive",
    default=True,
    help="Recursively process files in subdirectories.",
)
@click.option(
    "--target-data-size",
    default=3_000_000_000,
    help="The maximum total size of files to process, in bytes.",
)
def main(path: str, dry_run: bool, recursive: bool, target_data_size: int) -> None:
    """Converts all videos in the specified directory to h265 and all images to AVIF."""

    print(f"{'dry run...' if dry_run else 'real run...'}")
    ImageFile.LOAD_TRUNCATED_IMAGES = True

    # If the path is a file, process the single file.
    if os.path.isfile(path):
        make_room_at(path, dry_run)
        return

    # Or, process path as a directory.
    actual_data_size: int = 0
    files_to_process = []
    if recursive:
        for dirpath, _, filenames in os.walk(path):
            for filename in filenames:
                files_to_process.append(os.path.join(dirpath, filename))
    else:
        # get a list of files in a directory
        all_entries = os.listdir(path)
        for entry in all_entries:
            full_path = os.path.join(path, entry)
            if os.path.isfile(full_path):
                files_to_process.append(full_path)

    for input_path in files_to_process:
        if actual_data_size >= target_data_size:
            print(
                f"Processed {actual_data_size} bytes, which is over the target of {target_data_size} bytes. Stopping."
            )
            break
        try:
            if make_room_at(input_path, dry_run):
                actual_data_size += os.stat(input_path).st_size
        except FileNotFoundError:
            # The file might have been moved or removed after conversion.
            pass
