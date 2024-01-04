import os
import sys

import magic
import pillow_avif  # noqa: F401
from PIL import Image, ImageFile


def is_jpeg(file_path: str) -> bool:
    return "image/jpeg" in magic.Magic(mime=True).from_file(file_path)


def generate_output_path(file_path: str) -> str:
    file_name, _ = os.path.splitext(file_path)
    return file_name + ".avif"


def formatted_size(path: str) -> str:
    return f"{os.stat(path).st_size / 1024 / 1024:.1f}MB"


def jpeg_to_avif(input_path: str, output_path: str) -> None:
    JPGimg = Image.open(input_path)
    JPGimg.save(output_path, "AVIF", quality=70)


def encode_to_avif(input_path: str, dry_run: bool = True) -> bool:
    """Encode input to avif.

    Args:
        input_path (str): path to the input file
        dry_run (bool, optional): whether to perform a dry run. Defaults to True.

    Returns:
        bool: whether the picture is encoded to avif
    """
    if not is_jpeg(input_path):
        return False  # not jpeg
    print(f"Input: {input_path} ({formatted_size(input_path)})")
    output_path = generate_output_path(input_path)
    if not dry_run:
        jpeg_to_avif(input_path, output_path)
        print(f"Output: {output_path} ({formatted_size(output_path)})")
    return True


def traverse(
    path: str, max_data_to_process: int = 2**32, accumulated_data_size: int = 0
) -> int:
    """traverse through a directory structure recurisvely to find jpeg files to convert to avif

    Args:
        path (str): starting path to search and convert jpeg files to avif
        max_data_to_process (int, optional): maximum cumulative input file size to convert. Defaults to 4GB.
        accumulated_data_size (int, optional): cumulative input file size converted so far. Defaults to 0 byte.

    Returns:
        int: _description_
    """
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
