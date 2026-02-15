"""Configuration dataclass for LGN-Eye pipeline."""

from __future__ import annotations

import torch
from dataclasses import dataclass, field


@dataclass
class LGNConfig:
    """Configuration for the LGN temporal attention pipeline.

    All parameters have sensible defaults matching the Gao et al. (2026) paper.
    """

    # Resolution
    width: int = 640
    height: int = 480

    # Temporal attention
    decay_alpha: float = 0.85
    motion_threshold: float = 0.05
    accumulator_threshold: float = 0.3

    # Center-surround (DoG)
    dog_sigma_center: float = 1.0
    dog_sigma_surround: float = 1.6
    dog_scales: int = 3

    # ROI extraction
    roi_min_area: int = 100
    roi_padding: int = 20
    roi_max_count: int = 10

    # Ring buffer
    buffer_size: int = 5

    # Optical flow
    flow_method: str = "farneback"  # "farneback" | "raft" | "none"

    # Accumulator type
    accumulator_type: str = "ema"  # "ema" | "lif"

    # Device
    device: str = "auto"  # "auto" | "cuda" | "cpu"

    def resolve_device(self) -> torch.device:
        """Resolve 'auto' device to actual device."""
        if self.device == "auto":
            return torch.device("cuda" if torch.cuda.is_available() else "cpu")
        return torch.device(self.device)

    def __post_init__(self):
        assert 0.0 <= self.decay_alpha <= 1.0, "decay_alpha must be in [0, 1]"
        assert self.motion_threshold > 0, "motion_threshold must be positive"
        assert self.accumulator_threshold > 0, "accumulator_threshold must be positive"
        assert self.dog_sigma_center > 0, "dog_sigma_center must be positive"
        assert self.dog_sigma_surround > 0, "dog_sigma_surround must be positive"
        assert self.dog_scales >= 1, "dog_scales must be >= 1"
        assert self.roi_min_area >= 1, "roi_min_area must be >= 1"
        assert self.roi_max_count >= 1, "roi_max_count must be >= 1"
        assert self.buffer_size >= 2, "buffer_size must be >= 2"
        assert self.flow_method in ("farneback", "raft", "none"), (
            f"Unknown flow method: {self.flow_method}"
        )
        assert self.accumulator_type in ("ema", "lif"), (
            f"Unknown accumulator type: {self.accumulator_type}"
        )
        assert self.device in ("auto", "cuda", "cpu"), (
            f"Unknown device: {self.device}"
        )
