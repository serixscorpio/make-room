import ffmpy
import magic
import os
import traceback
import subprocess  # nosec B404
import sys


def is_h265(file_path):
    stdout, _ = ffmpy.FFprobe(
        global_options="-v error -select_streams v:0 -show_entries stream=codec_name -of default=nokey=1:noprint_wrappers=1",
        inputs={file_path: None},
    ).run(stdout=subprocess.PIPE)
    video_coding_format = stdout.decode("utf-8").rstrip()
    return (
        "hevc" == video_coding_format
    )  # hevc is h265's official name, see https://en.wikipedia.org/wiki/High_Efficiency_Video_Coding


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
        outputs={output_path: "-vcodec libx265 -crf 28"},
    )
    ff.run(stdout=open("conversion.log", "a"), stderr=open("conversion.log", "a"))
    print(f"Output: {output_path} ({formatted_size(output_path)})")
    # Commented out the following to avoid potential data loss.  Better be safe than sorry
    # os.remove(input_path)
    # print(f"Removed {input_path}")


path = sys.argv[1]  # required command line argument
target_data_size = 2_000_000_000  # process a maximum of N bytes of data
dry_run = True  # toggle this for dry run / real run
print(f"{'dry run...' if dry_run else 'real run...'}")

actual_data_size = 0
for filename in os.listdir(path):
    input_path = os.path.join(path, filename)
    if not os.path.isfile(input_path):
        continue
    try:
        if is_video(input_path) and not is_h265(input_path):
            print(f"Input: {input_path} ({formatted_size(input_path)})")
            if not dry_run:
                output_path = generate_output_path(input_path)
                convert_to_h265(input_path, output_path)
            actual_data_size += os.stat(input_path).st_size
            if actual_data_size > target_data_size:
                break
    except ffmpy.FFRuntimeError:
        traceback.print_exc()
