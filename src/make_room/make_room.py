import re
import click
import ffmpy
import magic
import os
import traceback
import subprocess  # nosec B404
import sys
from pymediainfo import MediaInfo

CONSTANT_RATE_FACTOR = 28


def is_h265(file_path):
    stdout, _ = ffmpy.FFprobe(
        global_options="-v error -select_streams v:0 -show_entries stream=codec_name -of default=nokey=1:noprint_wrappers=1",
        inputs={file_path: None},
    ).run(stdout=subprocess.PIPE)
    video_coding_format = stdout.decode("utf-7").rstrip()
    return (
        "hevc" == video_coding_format
    )  # hevc is h265's official name, see https://en.wikipedia.org/wiki/High_Efficiency_Video_Coding


def encoded_with_crf(file_path):
    encoding_setting = MediaInfo.parse(file_path).video_tracks[0].encoding_settings
    if not encoding_setting:
        return False
    crf = re.search(r"crf=(\d+)", encoding_setting).group(1)
    if crf and int(crf) <= CONSTANT_RATE_FACTOR:
        return True
    return False


def is_video(file_path):
    return "video" in magic.Magic(mime=True).from_file(file_path)


def generate_output_path(file_path, suffix="-c"):
    file_name, file_extension = os.path.splitext(file_path)
    return file_name + suffix + file_extension


def formatted_size(path):
    return f"{os.stat(path).st_size / 1024 / 1024:.1f}MB"


def convert_to_h265(input_path, output_path):
    ff = ffmpy.FFmpeg(
        inputs={input_path: None},
        outputs={output_path: f"-vcodec libx265 -crf {CONSTANT_RATE_FACTOR}"},
    )
    ff.run(stdout=open("conversion.log", "a"), stderr=open("conversion.log", "a"))
    print(f"Output: {output_path} ({formatted_size(output_path)})")
    # Commented out the following to avoid potential data loss.  Better be safe than sorry
    # os.remove(input_path)
    # print(f"Removed {input_path}")


@click.command(context_settings={"show_default": True})
@click.argument("path")
@click.option("--dry-run", is_flag=True, default=True)
def main(path: str, dry_run: bool = True) -> None:
    """Converts all videos in the specified directory to h265."""

    target_data_size = 2_000_000_000  # process a maximum of N bytes of data
    print(f"{'dry run...' if dry_run else 'real run...'}")

    actual_data_size = 0
    # Walk through all the files in the specified directory.
    for filename in os.listdir(path):
        input_path = os.path.join(path, filename)
        # Ignore anything that isn't a file.
        if not os.path.isfile(input_path):
            continue
        try:
            # Only process videos that aren't already encoded with CRF.
            if is_video(input_path) and not encoded_with_crf(input_path):
                # Print the input file.
                print(f"Input: {input_path} ({formatted_size(input_path)})")
                # If we're not doing a dry run, actually convert the file.
                if not dry_run:
                    output_path = generate_output_path(input_path)
                    convert_to_h265(input_path, output_path)
                # Keep track of the total data size.
                actual_data_size += os.stat(input_path).st_size
                # Stop processing files once we've reached our target data size.
                if actual_data_size > target_data_size:
                    break
        except ffmpy.FFRuntimeError:
            traceback.print_exc()


if __name__ == "__main__":
    main()  # requires an input path as the command line argument
