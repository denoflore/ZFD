"""Shared pytest fixtures for LGN-Eye tests."""

import pytest
import torch
import numpy as np

from lgn_eye.config import LGNConfig


@pytest.fixture
def device():
    """Resolve test device (CUDA if available, else CPU)."""
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


@pytest.fixture
def config(device):
    """Default LGNConfig with resolved device."""
    dev_str = "cuda" if device.type == "cuda" else "cpu"
    return LGNConfig(device=dev_str)


@pytest.fixture
def static_frame():
    """A static gray frame (B, 3, H, W) float32 tensor, value 0.5."""
    return torch.full((1, 3, 480, 640), 0.5, dtype=torch.float32)


@pytest.fixture
def moving_square_frames():
    """Generate a sequence of 10 frames with a white 40x40 square moving right.

    Returns list of (1, 3, H, W) float32 tensors on CPU.
    """
    H, W = 480, 640
    frames = []
    for i in range(10):
        frame = torch.zeros(1, 3, H, W, dtype=torch.float32)
        x_start = 50 + i * 30
        x_end = min(x_start + 40, W)
        y_start = 200
        y_end = 240
        frame[:, :, y_start:y_end, x_start:x_end] = 1.0
        frames.append(frame)
    return frames


@pytest.fixture
def two_objects_frames():
    """Generate frames with two separated moving squares.

    Square A moves right in upper half, Square B moves left in lower half.
    """
    H, W = 480, 640
    frames = []
    for i in range(10):
        frame = torch.zeros(1, 3, H, W, dtype=torch.float32)
        # Object A: upper half, moving right
        ax = 50 + i * 25
        frame[:, :, 100:140, ax:min(ax + 40, W)] = 1.0
        # Object B: lower half, moving left
        bx = 500 - i * 25
        frame[:, :, 340:380, max(bx, 0):bx + 40] = 1.0
        frames.append(frame)
    return frames


@pytest.fixture
def static_frame_np():
    """A static gray frame as numpy BGR uint8 (H, W, 3)."""
    return np.full((480, 640, 3), 128, dtype=np.uint8)


@pytest.fixture
def moving_square_frames_np():
    """Generate numpy BGR frames with a moving white square.

    Returns list of (H, W, 3) uint8 arrays.
    """
    H, W = 480, 640
    frames = []
    for i in range(10):
        frame = np.zeros((H, W, 3), dtype=np.uint8)
        x_start = 50 + i * 30
        x_end = min(x_start + 40, W)
        y_start = 200
        y_end = 240
        frame[y_start:y_end, x_start:x_end] = 255
        frames.append(frame)
    return frames
