import os
import sys

import magic
from PIL import Image, ImageFile


def is_jpeg(file_path):
    return "image/jpeg" in magic.Magic(mime=True).from_file(file_path)


def generate_output_path(file_path):
    file_name, _file_extension = os.path.splitext(file_path)
    return file_name + ".avif"


def formatted_size(path):
    return f"{os.stat(path).st_size / 1024 / 1024:.1f}MB"


def jpeg_to_avif(input_path, output_path):
    JPGimg = Image.open(input_path)
    JPGimg.save(output_path, "AVIF", quality=70)


def encode_to_avif(input_path, dry_run=True):
    """Encode input to avif.

    Args:
        input_path (_type_): _description_
        dry_run (bool, optional): _description_. Defaults to True.

    Returns:
        boolean: whether picture is encoded to avif
    """
    if not is_jpeg(input_path):
        return False  # not jpeg
    print(f"Input: {input_path} ({formatted_size(input_path)})")
    output_path = generate_output_path(input_path)
    if not dry_run:
        jpeg_to_avif(input_path, output_path)
        print(f"Output: {output_path} ({formatted_size(output_path)})")
    return True


def traverse(path, accumulated_data_size=0) -> int:
    for filename in os.listdir(path):
        input_path = os.path.join(path, filename)
        if os.path.isdir(input_path):
            accumulated_data_size = traverse(input_path, accumulated_data_size)
        if os.path.isfile(input_path):
            if accumulated_data_size > target_data_size:
                return accumulated_data_size
            if encode_to_avif(input_path, dry_run):
                accumulated_data_size += os.stat(input_path).st_size
                print(f"accumulated_data_size: {accumulated_data_size}")
    return accumulated_data_size


path = sys.argv[1]  # required command line argument
target_data_size = 1_000_000_000  # process a cumulated maximum of 1GB of data
dry_run = False  # toggle this for dry run / real run
print(f"{'dry run...' if dry_run else 'real run...'}")

ImageFile.LOAD_TRUNCATED_IMAGES = True
traverse(path)
