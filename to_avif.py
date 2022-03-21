import magic
import os
from PIL import Image, ImageFile
import pillow_avif
import sys


def is_jpeg(file_path):
    return "image/jpeg" in magic.Magic(mime=True).from_file(file_path)


def generate_output_path(file_path):
    file_name, _file_extension = os.path.splitext(file_path)
    return file_name + ".avif"


def formatted_size(path):
    return f"{os.stat(path).st_size / 1024 / 1024:.1f}MB"


def convert_to_avif(input_path, output_path):
    JPGimg = Image.open(input_path)
    JPGimg.save(output_path, "AVIF", quality=70)
    print(f"Output: {output_path} ({formatted_size(output_path)})")


path = sys.argv[1]  # required command line argument
target_data_size = 3_000_000_000  # process a maximum of N MB of data, or a single file if greater than N MB
dry_run = False  # toggle this for dry run / real run
print(f"{'dry run...' if dry_run else 'real run...'}")

ImageFile.LOAD_TRUNCATED_IMAGES = True
actual_data_size = 0
for filename in os.listdir(path):
    input_path = os.path.join(path, filename)
    if not os.path.isfile(input_path):
        continue
    if is_jpeg(input_path):
        print(f"Input: {input_path} ({formatted_size(input_path)})")
        if not dry_run:
            output_path = generate_output_path(input_path)
            convert_to_avif(input_path, output_path)
        actual_data_size += os.stat(input_path).st_size
        if actual_data_size > target_data_size:
            break
