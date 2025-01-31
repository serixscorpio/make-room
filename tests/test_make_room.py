import os
import shutil

import pytest  # noqa: F401
from click.testing import CliRunner

from make_room import make_room

fixture_path = os.path.join(os.path.dirname(__file__), "fixtures")


def test_make_room_on_directory() -> None:
    """compress video files in the current directory, non-recursively"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        shutil.copy(f"{fixture_path}/example-video.mp4", ".")
        runner.invoke(make_room.main, ["."], catch_exceptions=False)
        assert make_room.encoded_with_crf("example-video-c.mp4")
        assert os.stat("example-video.mp4").st_size > os.stat("example-video-c.mp4").st_size


def test_make_room_on_file() -> None:
    """compress a specified video file"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        shutil.copy(f"{fixture_path}/example-video.mp4", ".")
        runner.invoke(make_room.main, ["./example-video.mp4"], catch_exceptions=False)
        assert make_room.encoded_with_crf("example-video-c.mp4")
        assert os.stat("example-video.mp4").st_size > os.stat("example-video-c.mp4").st_size
