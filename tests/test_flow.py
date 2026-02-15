"""Tests for optical flow estimation."""

import numpy as np
import pytest

from lgn_eye.config import LGNConfig
from lgn_eye.flow import FlowEstimator
from lgn_eye.roi import ROI


class TestFlowEstimator:
    """Tests for ROI-restricted optical flow."""

    def _make_estimator(self, **overrides):
        cfg = LGNConfig(device="cpu", **overrides)
        return FlowEstimator(cfg)

    def _make_frames_with_motion(self, H=480, W=640, shift=10):
        """Create two frames where a white square moves horizontally."""
        prev = np.zeros((H, W, 3), dtype=np.uint8)
        curr = np.zeros((H, W, 3), dtype=np.uint8)
        # White square in previous frame
        prev[200:260, 300:360] = 255
        # Same square shifted right in current frame
        curr[200:260, 300 + shift : 360 + shift] = 255
        return prev, curr

    def test_moving_object_nonzero_flow(self):
        """A moving object within an ROI should produce non-zero flow."""
        est = self._make_estimator()
        prev, curr = self._make_frames_with_motion()
        roi = ROI(x=280, y=180, w=100, h=100, area=10000, centroid=(330.0, 230.0))
        result = est(prev, curr, [roi])

        # Flow within the ROI should be non-zero
        flow_in_roi = result["flow"][180:280, 280:380]
        assert np.any(flow_in_roi != 0), "Flow should be non-zero in ROI"

    def test_static_region_zero_flow(self):
        """Regions outside ROIs should have zero flow."""
        est = self._make_estimator()
        prev, curr = self._make_frames_with_motion()
        roi = ROI(x=280, y=180, w=100, h=100, area=10000, centroid=(330.0, 230.0))
        result = est(prev, curr, [roi])

        # Flow outside the ROI region should be zero
        flow_outside = result["flow"][0:100, 0:100]
        assert np.all(flow_outside == 0), "Flow outside ROI should be zero"

    def test_speedup_ratio(self):
        """Speedup ratio should reflect ROI coverage."""
        est = self._make_estimator()
        H, W = 480, 640
        prev, curr = self._make_frames_with_motion(H, W)

        # ROI covers 100x100 = 10000 pixels out of 307200
        roi = ROI(x=280, y=180, w=100, h=100, area=10000, centroid=(330.0, 230.0))
        result = est(prev, curr, [roi])

        expected_speedup = (H * W) / (100 * 100)  # 30.72
        assert result["speedup_ratio"] == pytest.approx(expected_speedup, rel=0.01)

    def test_no_rois_returns_zero(self):
        """No ROIs should produce all-zero flow."""
        est = self._make_estimator()
        prev, curr = self._make_frames_with_motion()
        result = est(prev, curr, [])

        assert np.all(result["flow"] == 0)
        assert result["speedup_ratio"] == float("inf")

    def test_flow_method_none(self):
        """flow_method='none' should return zero flow."""
        est = self._make_estimator(flow_method="none")
        prev, curr = self._make_frames_with_motion()
        roi = ROI(x=280, y=180, w=100, h=100, area=10000, centroid=(330.0, 230.0))
        result = est(prev, curr, [roi])

        assert np.all(result["flow"] == 0)

    def test_flow_magnitude_map(self):
        """Flow magnitude should be non-negative everywhere."""
        est = self._make_estimator()
        prev, curr = self._make_frames_with_motion()
        roi = ROI(x=280, y=180, w=100, h=100, area=10000, centroid=(330.0, 230.0))
        result = est(prev, curr, [roi])

        assert np.all(result["flow_magnitude"] >= 0)

    def test_multiple_rois(self):
        """Multiple ROIs should all have flow computed."""
        est = self._make_estimator()
        H, W = 480, 640
        prev = np.zeros((H, W, 3), dtype=np.uint8)
        curr = np.zeros((H, W, 3), dtype=np.uint8)

        # Two moving objects
        prev[100:140, 100:140] = 255
        curr[100:140, 110:150] = 255  # shifted right
        prev[300:340, 400:440] = 255
        curr[300:340, 410:450] = 255  # shifted right

        rois = [
            ROI(x=80, y=80, w=100, h=80, area=8000, centroid=(130.0, 120.0)),
            ROI(x=380, y=280, w=100, h=80, area=8000, centroid=(420.0, 320.0)),
        ]
        result = est(prev, curr, rois)

        assert len(result["roi_flows"]) == 2
        # Both ROI regions should have some flow
        assert np.any(result["flow"][80:160, 80:180] != 0)
        assert np.any(result["flow"][280:360, 380:480] != 0)

    def test_output_shapes(self):
        """Output arrays should have correct shapes."""
        est = self._make_estimator()
        H, W = 480, 640
        prev, curr = self._make_frames_with_motion(H, W)
        roi = ROI(x=280, y=180, w=100, h=100, area=10000, centroid=(330.0, 230.0))
        result = est(prev, curr, [roi])

        assert result["flow"].shape == (H, W, 2)
        assert result["flow_magnitude"].shape == (H, W)
        assert isinstance(result["roi_flows"], list)
        assert isinstance(result["speedup_ratio"], float)
