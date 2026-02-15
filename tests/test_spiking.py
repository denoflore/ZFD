"""Tests for the spiking neural network accumulator."""

import torch
import pytest

from lgn_eye.config import LGNConfig
from lgn_eye.spiking import SpikingAccumulator
from lgn_eye.temporal import TemporalAttentionLayer


class TestSpikingAccumulator:
    """Tests for LIF-based accumulator."""

    def _make_accumulator(self, **overrides):
        cfg = LGNConfig(device="cpu", accumulator_type="lif", **overrides)
        return SpikingAccumulator(cfg)

    def test_output_shapes(self):
        """Outputs should match input spatial dimensions."""
        acc = self._make_accumulator()
        inp = torch.rand(1, 1, 120, 160)
        spikes, mem = acc(inp)
        assert spikes.shape == (1, 1, 120, 160)
        assert mem.shape == (1, 1, 120, 160)

    def test_spikes_are_binary(self):
        """Spike outputs should be 0 or 1."""
        acc = self._make_accumulator()
        inp = torch.rand(1, 1, 120, 160)
        for _ in range(10):
            spikes, mem = acc(inp)
        unique_vals = torch.unique(spikes)
        for v in unique_vals:
            assert v.item() in (0.0, 1.0), f"Unexpected spike value: {v}"

    def test_membrane_bounded(self):
        """Membrane potential should stay bounded (not diverge)."""
        acc = self._make_accumulator()
        for _ in range(20):
            inp = torch.rand(1, 1, 60, 80) * 0.1
            _, mem = acc(inp)
        # With subtract reset, membrane can go slightly negative after spike,
        # but should stay bounded. Check it doesn't diverge.
        assert mem.max().item() < 10.0, "Membrane should not diverge"
        assert mem.min().item() > -1.0, "Membrane should not diverge negatively"

    def test_strong_input_fires(self):
        """Sustained strong input should eventually cause spikes."""
        acc = self._make_accumulator(accumulator_threshold=0.3)
        any_spike = False
        for _ in range(50):
            inp = torch.ones(1, 1, 60, 80) * 0.5
            spikes, _ = acc(inp)
            if spikes.sum().item() > 0:
                any_spike = True
                break
        assert any_spike, "Strong sustained input should cause spikes"

    def test_zero_input_no_spikes(self):
        """Zero input should not produce spikes after transient."""
        acc = self._make_accumulator()
        # Feed some initial signal
        for _ in range(5):
            acc(torch.ones(1, 1, 60, 80) * 0.1)
        # Now feed zeros - after a few steps, spikes should stop
        for _ in range(20):
            spikes, _ = acc(torch.zeros(1, 1, 60, 80))
        assert spikes.sum().item() == 0, "Zero input should eventually produce no spikes"

    def test_reset(self):
        """Reset should clear membrane state."""
        acc = self._make_accumulator()
        for _ in range(5):
            acc(torch.rand(1, 1, 60, 80))
        assert acc.mem is not None
        acc.reset()
        assert acc.mem is None

    def test_integration_with_temporal_layer(self):
        """Spiking accumulator should integrate with TemporalAttentionLayer."""
        cfg = LGNConfig(
            device="cpu", width=160, height=120, accumulator_type="lif",
        )
        layer = TemporalAttentionLayer(cfg)

        # Feed a sequence of frames with motion
        for i in range(10):
            frame = torch.zeros(1, 3, 120, 160)
            x = 20 + i * 10
            frame[:, :, 40:70, x : min(x + 30, 160)] = 1.0
            out = layer(frame)

        assert out["events"].shape == (1, 1, 120, 160)
        assert out["motion_energy"].shape == (1, 1, 120, 160)

    def test_lif_produces_similar_rois_to_ema(self):
        """Spiking mode should detect motion in similar regions as EMA mode."""
        H, W = 120, 160

        # Run EMA version
        cfg_ema = LGNConfig(device="cpu", width=W, height=H, accumulator_type="ema")
        layer_ema = TemporalAttentionLayer(cfg_ema)

        # Run LIF version
        cfg_lif = LGNConfig(device="cpu", width=W, height=H, accumulator_type="lif")
        layer_lif = TemporalAttentionLayer(cfg_lif)

        frames = []
        for i in range(15):
            frame = torch.zeros(1, 3, H, W)
            x = 20 + i * 8
            frame[:, :, 40:70, x : min(x + 30, W)] = 1.0
            frames.append(frame)

        for f in frames:
            out_ema = layer_ema(f)
            out_lif = layer_lif(f)

        # Both should have non-zero motion energy in the motion region
        ema_motion_region = out_ema["motion_energy"][:, :, 30:80, 10:150].max().item()
        lif_motion_region = out_lif["motion_energy"][:, :, 30:80, 10:150].max().item()

        assert ema_motion_region > 0, "EMA should detect motion"
        assert lif_motion_region > 0, "LIF should detect motion"
