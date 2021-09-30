import numpy as np
import pytest

print("hello world")
a = np.zeros(50)


def inc(x):
    return x + 1


def test_inc():
    assert inc(3) == 4
