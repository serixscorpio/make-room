import tempfile
import os
import shutil
from make_room import make_room

import pytest

fixture_path = os.path.join(os.path.dirname(__file__), "fixtures")


def test_my_tempfiles():
    with tempfile.TemporaryDirectory() as tmp_dirname:
        shutil.copy(f"{fixture_path}/original.mp4", tmp_dirname)
        make_room.main(tmp_dirname, dry_run=False)
        print(os.listdir(tmp_dirname))
