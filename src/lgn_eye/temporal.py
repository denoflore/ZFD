"""Temporal attention layer replicating LGN synapse array dynamics.

Implements the core temporal change detection from Gao et al. (2026):
frame differencing, multi-scale center-surround (DoG) filtering,
thresholded event detection, and leaky accumulation.
"""

from __future__ import annotations

import math
from collections import deque
from typing import Dict

import torch
import torch.nn as nn
import kornia.filters

from lgn_eye.config import LGNConfig


class TemporalAttentionLayer(nn.Module):
    """Core LGN temporal attention module.

    Converts raw RGB frames into motion energy maps via biologically-inspired
    temporal differencing and leaky integration.
    """

    def __init__(self, config: LGNConfig):
        super().__init__()
        self.config = config
        self.device = config.resolve_device()

        # Ring buffer for previous filtered frames
        self.ring_buffer: deque[torch.Tensor] = deque(maxlen=config.buffer_size)

        # Persistent accumulator (initialized on first forward, used for EMA mode)
        self.accumulator: torch.Tensor | None = None

        # Spiking accumulator (lazy-loaded for LIF mode)
        self._spiking_accumulator = None
        if config.accumulator_type == "lif":
            from lgn_eye.spiking import SpikingAccumulator
            self._spiking_accumulator = SpikingAccumulator(config)

        # Precompute DoG kernel sizes (must be odd)
        self._kernel_sizes = []
        for s in range(config.dog_scales):
            sigma_s = config.dog_sigma_surround * (2 ** s)
            ksize = max(3, int(math.ceil(sigma_s * 6)) | 1)  # ensure odd
            self._kernel_sizes.append(ksize)

        # Luminance weights (ITU-R BT.709)
        self.register_buffer(
            "lum_weights",
            torch.tensor([0.2126, 0.7152, 0.0722], dtype=torch.float32).view(1, 3, 1, 1),
        )

    def reset(self):
        """Reset all internal state (ring buffer, accumulator)."""
        self.ring_buffer.clear()
        self.accumulator = None
        if self._spiking_accumulator is not None:
            self._spiking_accumulator.reset()

    def _to_log_luminance(self, frame: torch.Tensor) -> torch.Tensor:
        """Convert (B, 3, H, W) RGB to (B, 1, H, W) log-luminance."""
        lum = (frame * self.lum_weights).sum(dim=1, keepdim=True)
        return torch.log1p(lum)

    def _dog_filter(self, log_lum: torch.Tensor) -> torch.Tensor:
        """Multi-scale center-surround (Difference of Gaussians) filtering."""
        cfg = self.config
        responses = []
        for s in range(cfg.dog_scales):
            sigma_c = cfg.dog_sigma_center * (2 ** s)
            sigma_s = cfg.dog_sigma_surround * (2 ** s)
            ksize = self._kernel_sizes[s]
            kernel_size = (ksize, ksize)
            center = kornia.filters.gaussian_blur2d(
                log_lum, kernel_size, (sigma_c, sigma_c)
            )
            surround = kornia.filters.gaussian_blur2d(
                log_lum, kernel_size, (sigma_s, sigma_s)
            )
            responses.append(center - surround)

        # Average across scales
        return torch.stack(responses, dim=0).mean(dim=0)

    def forward(self, frame: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Process a single frame through the temporal attention pipeline.

        Args:
            frame: (B, 3, H, W) float32 RGB tensor in [0, 1], on any device.

        Returns:
            Dict with keys:
                'events': binary event tensor (B, 1, H, W)
                'motion_energy': continuous accumulator (B, 1, H, W)
                'temporal_diff': raw absolute difference (B, 1, H, W)
                'dog_filtered': center-surround output (B, 1, H, W)
        """
        frame = frame.to(self.device)

        # 1. Log-luminance
        log_lum = self._to_log_luminance(frame)

        # 2. Multi-scale DoG
        filtered = self._dog_filter(log_lum)

        # 3. Temporal difference against ring buffer
        if len(self.ring_buffer) == 0:
            prev_filtered = torch.zeros_like(filtered)
        else:
            prev_filtered = self.ring_buffer[-1]

        diff = filtered - prev_filtered
        abs_diff = torch.abs(diff)

        # 4. Binary events (threshold-based)
        events = (abs_diff > self.config.motion_threshold).float()

        # 5. Accumulation (EMA or spiking LIF)
        if self._spiking_accumulator is not None:
            spikes, membrane = self._spiking_accumulator(abs_diff)
            # Use membrane potential as motion energy (continuous signal)
            motion_energy = membrane
            # Override binary events with spike events from LIF
            events = spikes
        else:
            alpha = self.config.decay_alpha
            if self.accumulator is None:
                self.accumulator = torch.zeros_like(abs_diff)
            self.accumulator = alpha * self.accumulator + (1.0 - alpha) * abs_diff
            motion_energy = self.accumulator.clone()

        # 6. Update ring buffer
        self.ring_buffer.append(filtered.detach())

        return {
            "events": events,
            "motion_energy": motion_energy,
            "temporal_diff": abs_diff,
            "dog_filtered": filtered,
        }
