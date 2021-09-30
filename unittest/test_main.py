import sys

import pytest

sys.path.append("..")
from src import main


def inc_is_nice():
    assert main.inc(3) == 4
