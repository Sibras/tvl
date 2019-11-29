import PIL.Image
import pytest
import torch
from numpy.testing import assert_allclose
import numpy as np


def assert_same_image(actual, expected, atol=50, allow_mismatch=0.0):
    if torch.is_tensor(actual):
        if actual.is_floating_point():
            actual = actual * 255
        actual = actual.to(device='cpu', dtype=torch.uint8)
        actual = PIL.Image.fromarray(actual.permute(1, 2, 0).numpy(), 'RGB')
    if allow_mismatch == 0:
        assert_allclose(actual, expected, rtol=0, atol=atol)
    else:
        close_elements = np.isclose(actual, expected, rtol=0, atol=atol)
        assert np.sum(close_elements) / close_elements.size > (1.0 - allow_mismatch)


def test_duration(backend):
    assert backend.duration == 2.0


def test_frame_rate(backend):
    assert backend.frame_rate == 25


def test_n_frames(backend):
    assert backend.n_frames == 50


def test_width(backend):
    assert backend.width == 1280


def test_height(backend):
    assert backend.height == 720


def test_read_frame(backend, first_frame_image):
    rgb = backend.read_frame()
    assert rgb.size() == (3, 720, 1280)
    assert_same_image(rgb, first_frame_image)


def test_resizing_read_frame(resizing_backend, first_frame_image):
    rgb = resizing_backend.read_frame()
    assert rgb.size() == (3, 90, 160)
    assert_same_image(rgb, first_frame_image.resize((160, 90), PIL.Image.NEAREST), allow_mismatch=0.01)


def test_out_size_attributes(backend, resizing_backend):
    assert backend.out_width == 1280
    assert backend.out_height == 720
    assert resizing_backend.out_width == 160
    assert resizing_backend.out_height == 90

def test_eof(backend):
    backend.seek(2.0)
    with pytest.raises(EOFError):
        backend.read_frame()


def test_read_all_frames(backend):
    n_read = 0
    for i in range(1000):
        try:
            backend.read_frame()
            n_read += 1
        except EOFError:
            break
    assert n_read == 50


def test_seek(backend, mid_frame_image):
    backend.seek(1.0)
    rgb = backend.read_frame()
    assert_same_image(rgb, mid_frame_image)


def test_select_frames(backend, first_frame_image, mid_frame_image):
    frames = list(backend.select_frames([0, 25]))
    assert_same_image(frames[0], first_frame_image)
    assert_same_image(frames[1], mid_frame_image)


def test_select_frames_without_first(backend, mid_frame_image):
    frames = list(backend.select_frames([25, 27, 29]))
    assert_same_image(frames[0], mid_frame_image)
