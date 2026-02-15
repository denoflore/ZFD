"""Tests for the TemporalAttentionLayer."""

import torch
import pytest

from lgn_eye.config import LGNConfig
from lgn_eye.temporal import TemporalAttentionLayer


class TestTemporalAttentionLayer:
    """Tests for temporal change detection."""

    def _make_layer(self, device, **overrides):
        dev_str = "cuda" if device.type == "cuda" else "cpu"
        cfg = LGNConfig(device=dev_str, **overrides)
        return TemporalAttentionLayer(cfg)

    def test_output_shapes(self, device):
        """All outputs must have correct shapes."""
        layer = self._make_layer(device)
        frame = torch.rand(1, 3, 480, 640, device=device)
        out = layer(frame)

        assert out["events"].shape == (1, 1, 480, 640)
        assert out["motion_energy"].shape == (1, 1, 480, 640)
        assert out["temporal_diff"].shape == (1, 1, 480, 640)
        assert out["dog_filtered"].shape == (1, 1, 480, 640)

    def test_static_scene_zero_events(self, device, static_frame):
        """A static scene should produce zero events after warmup."""
        layer = self._make_layer(device)
        frame = static_frame.to(device)

        # Feed same frame multiple times
        for _ in range(5):
            out = layer(frame)

        # After warmup with identical frames, events and diff should be zero
        assert out["events"].sum().item() == 0.0
        assert out["temporal_diff"].max().item() < 1e-6

    def test_static_scene_decaying_accumulator(self, device, static_frame):
        """Accumulator should decay toward zero for static scenes."""
        layer = self._make_layer(device)
        frame = static_frame.to(device)

        # First frame: no history, so diff=0, accumulator=0
        out1 = layer(frame)
        energy1 = out1["motion_energy"].max().item()

        # Second frame: still static, diff=0, accumulator decays
        out2 = layer(frame)
        energy2 = out2["motion_energy"].max().item()

        # Accumulator should stay at zero or decrease
        assert energy2 <= energy1 + 1e-6

    def test_moving_square_produces_events(self, device, moving_square_frames):
        """A moving white square should produce events at its edges."""
        layer = self._make_layer(device, motion_threshold=0.01)

        # Feed first frame as warmup
        layer(moving_square_frames[0].to(device))

        # Feed second frame - the square has moved, should generate events
        out = layer(moving_square_frames[1].to(device))

        assert out["events"].sum().item() > 0, "Moving square should produce events"

    def test_accumulator_proportional_to_speed(self, device):
        """Faster motion should produce higher accumulator values."""
        H, W = 240, 320

        # Slow motion: square moves 5px per frame
        layer_slow = self._make_layer(device, width=W, height=H)
        for i in range(5):
            frame = torch.zeros(1, 3, H, W, device=device)
            x = 50 + i * 5
            frame[:, :, 100:130, x:x + 30] = 1.0
            out_slow = layer_slow(frame)

        # Fast motion: square moves 30px per frame
        layer_fast = self._make_layer(device, width=W, height=H)
        for i in range(5):
            frame = torch.zeros(1, 3, H, W, device=device)
            x = 50 + i * 30
            x = min(x, W - 30)
            frame[:, :, 100:130, x:x + 30] = 1.0
            out_fast = layer_fast(frame)

        slow_energy = out_slow["motion_energy"].max().item()
        fast_energy = out_fast["motion_energy"].max().item()
        assert fast_energy > slow_energy, (
            f"Fast motion ({fast_energy:.4f}) should produce more energy "
            f"than slow motion ({slow_energy:.4f})"
        )

    def test_batch_independence(self, device):
        """Multiple batch elements should be processed independently."""
        layer = self._make_layer(device, width=320, height=240)
        H, W = 240, 320

        # Batch of 2: first is static, second has a moving square
        for i in range(3):
            frame = torch.zeros(2, 3, H, W, device=device)
            frame[0] = 0.5  # static gray
            x = 50 + i * 20
            frame[1, :, 100:130, x:min(x + 30, W)] = 1.0  # moving square
            out = layer(frame)

        # Batch element 0 (static) should have much less energy than element 1
        energy_0 = out["motion_energy"][0].max().item()
        energy_1 = out["motion_energy"][1].max().item()
        assert energy_1 > energy_0, (
            f"Moving element energy ({energy_1:.4f}) should exceed "
            f"static element energy ({energy_0:.4f})"
        )

    def test_cpu_gpu_consistency(self):
        """CPU and GPU should produce identical results within tolerance."""
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")

        cfg_cpu = LGNConfig(device="cpu", width=160, height=120)
        cfg_gpu = LGNConfig(device="cuda", width=160, height=120)
        layer_cpu = TemporalAttentionLayer(cfg_cpu)
        layer_gpu = TemporalAttentionLayer(cfg_gpu)

        torch.manual_seed(42)
        frames = [torch.rand(1, 3, 120, 160) for _ in range(3)]

        for f in frames:
            out_cpu = layer_cpu(f)
            out_gpu = layer_gpu(f.cuda())

        for key in out_cpu:
            cpu_val = out_cpu[key]
            gpu_val = out_gpu[key].cpu()
            torch.testing.assert_close(cpu_val, gpu_val, atol=1e-5, rtol=1e-5)

    def test_memory_stability(self, device):
        """Memory usage should not grow over many iterations."""
        layer = self._make_layer(device, width=160, height=120)

        # Run 100 iterations and check ring buffer stays bounded
        for i in range(100):
            frame = torch.rand(1, 3, 120, 160, device=device)
            layer(frame)

        assert len(layer.ring_buffer) == layer.config.buffer_size

    def test_reset(self, device):
        """Reset should clear all internal state."""
        layer = self._make_layer(device, width=160, height=120)

        # Feed some frames
        for _ in range(5):
            layer(torch.rand(1, 3, 120, 160, device=device))

        assert len(layer.ring_buffer) > 0
        assert layer.accumulator is not None

        layer.reset()

        assert len(layer.ring_buffer) == 0
        assert layer.accumulator is None

    def test_different_resolutions(self, device):
        """Should work at various resolutions."""
        for h, w in [(120, 160), (240, 320), (480, 640)]:
            layer = self._make_layer(device, width=w, height=h)
            frame = torch.rand(1, 3, h, w, device=device)
            out = layer(frame)
            assert out["events"].shape == (1, 1, h, w)
