import os
import shutil

import pytest  # noqa: F401
from click.testing import CliRunner
from make_room import make_room

fixture_path = os.path.join(os.path.dirname(__file__), "fixtures")


def test_make_room():
    runner = CliRunner()
    with runner.isolated_filesystem():
        shutil.copy(f"{fixture_path}/original.mp4", ".")
        runner.invoke(make_room.main, ["."], catch_exceptions=False)
        assert make_room.encoded_with_crf("original-c.mp4")
        assert os.stat("original.mp4").st_size > os.stat("original-c.mp4").st_size
