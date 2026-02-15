"""Tests for visualization utilities."""

import numpy as np
import pytest

from lgn_eye.config import LGNConfig
from lgn_eye.viz import Visualizer
from lgn_eye.roi import ROI


class TestVisualizer:
    """Tests for display rendering."""

    def _make_viz(self, **overrides):
        cfg = LGNConfig(device="cpu", **overrides)
        return Visualizer(cfg)

    def _make_inputs(self, H=480, W=640):
        """Create synthetic pipeline outputs for testing."""
        frame = np.random.randint(0, 255, (H, W, 3), dtype=np.uint8)
        events = np.zeros((H, W), dtype=np.float32)
        events[200:250, 300:350] = 1.0
        energy = np.zeros((H, W), dtype=np.float32)
        energy[190:260, 290:360] = 0.7
        flow = np.zeros((H, W, 2), dtype=np.float32)
        flow[200:250, 300:350, 0] = 5.0  # rightward flow
        flow_mag = np.sqrt(flow[:, :, 0] ** 2 + flow[:, :, 1] ** 2)
        rois = [ROI(x=290, y=190, w=70, h=70, area=4900, centroid=(325.0, 225.0))]
        timings = {"temporal": 1.5, "roi": 0.3, "flow": 3.2}
        return frame, events, energy, rois, flow, flow_mag, timings

    def test_quad_view_dimensions(self):
        """Quad view output should be same H x W as input."""
        viz = self._make_viz()
        frame, events, energy, rois, flow, flow_mag, timings = self._make_inputs()
        H, W = frame.shape[:2]
        result = viz.render(
            frame, events, energy, rois, flow, flow_mag,
            timings, fps=30.0, speedup_ratio=5.0, mode="quad",
        )
        assert result.shape == (H, W, 3)
        assert result.dtype == np.uint8

    def test_overlay_view_dimensions(self):
        """Overlay view should have same dimensions as input frame."""
        viz = self._make_viz()
        frame, events, energy, rois, flow, flow_mag, timings = self._make_inputs()
        H, W = frame.shape[:2]
        result = viz.render(
            frame, events, energy, rois, flow, flow_mag,
            timings, fps=30.0, speedup_ratio=5.0, mode="overlay",
        )
        assert result.shape == (H, W, 3)

    def test_debug_view_renders(self):
        """Debug view should render without errors."""
        viz = self._make_viz()
        frame, events, energy, rois, flow, flow_mag, timings = self._make_inputs()
        result = viz.render(
            frame, events, energy, rois, flow, flow_mag,
            timings, fps=30.0, speedup_ratio=5.0, mode="debug",
        )
        assert result.ndim == 3
        assert result.shape[2] == 3

    def test_hud_renders_without_error(self):
        """HUD overlay should render without exceptions."""
        viz = self._make_viz()
        frame, events, energy, rois, flow, flow_mag, timings = self._make_inputs()
        # Feed some FPS history
        for _ in range(5):
            viz.render(
                frame, events, energy, rois, flow, flow_mag,
                timings, fps=30.0, speedup_ratio=5.0, mode="quad",
            )
        # Should not raise

    def test_flow_hsv_encoding(self):
        """Flow HSV encoding should map directions correctly."""
        H, W = 100, 100

        # Rightward flow (angle = 0)
        flow_right = np.zeros((H, W, 2), dtype=np.float32)
        flow_right[:, :, 0] = 5.0
        hsv_right = Visualizer.flow_to_hsv(flow_right)
        assert hsv_right.shape == (H, W, 3)
        assert hsv_right.dtype == np.uint8

        # Upward flow (angle = -90 = 270 degrees)
        flow_up = np.zeros((H, W, 2), dtype=np.float32)
        flow_up[:, :, 1] = -5.0
        hsv_up = Visualizer.flow_to_hsv(flow_up)

        # Different directions should produce different hue values
        # (they should look different)
        assert not np.array_equal(hsv_right, hsv_up)

    def test_empty_rois(self):
        """Rendering with no ROIs should work fine."""
        viz = self._make_viz()
        frame, events, energy, _, flow, flow_mag, timings = self._make_inputs()
        result = viz.render(
            frame, events, energy, [], flow, flow_mag,
            timings, fps=30.0, speedup_ratio=float("inf"), mode="quad",
        )
        assert result.shape[2] == 3

    def test_energy_heatmap(self):
        """Energy heatmap should produce a valid BGR image."""
        viz = self._make_viz()
        energy = np.random.rand(480, 640).astype(np.float32)
        heatmap = viz._energy_to_heatmap(energy)
        assert heatmap.shape == (480, 640, 3)
        assert heatmap.dtype == np.uint8
