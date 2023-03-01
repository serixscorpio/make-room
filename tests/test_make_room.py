import pytest
import os


def test_my_fakefs(fs):
    # "fs" is the reference to the fake file system
    fs.create_file("/var/data/xx1.txt")
    assert os.path.exists("/var/data/xx1.txt")
