import os
import shutil

import pytest  # noqa: F401
from click.testing import CliRunner
from make_room import make_room

fixture_path = os.path.join(os.path.dirname(__file__), "fixtures")


def test_make_room() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        shutil.copy(f"{fixture_path}/example-video.mp4", ".")
        runner.invoke(make_room.main, ["."], catch_exceptions=False)
        assert make_room.encoded_with_crf("example-video-c.mp4")
        assert (
            os.stat("example-video.mp4").st_size
            > os.stat("example-video-c.mp4").st_size
        )
