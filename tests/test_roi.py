"""Tests for ROI extraction."""

import torch
import pytest

from lgn_eye.config import LGNConfig
from lgn_eye.roi import ROIExtractor, ROI


class TestROIExtractor:
    """Tests for connected-component ROI extraction."""

    def _make_extractor(self, **overrides):
        cfg = LGNConfig(device="cpu", **overrides)
        return ROIExtractor(cfg)

    def _energy_with_blob(self, H, W, y1, y2, x1, x2, value=0.8):
        """Create a motion energy tensor with a bright blob."""
        energy = torch.zeros(1, 1, H, W)
        energy[:, :, y1:y2, x1:x2] = value
        return energy

    def test_single_object_single_roi(self):
        """A single bright blob should produce exactly one ROI."""
        ext = self._make_extractor(roi_min_area=10)
        energy = self._energy_with_blob(480, 640, 200, 250, 300, 370)
        rois = ext(energy)
        assert len(rois) == 1
        roi = rois[0]
        # ROI should roughly contain the blob (with morphological expansion)
        assert roi.x <= 300
        assert roi.y <= 200
        assert roi.x + roi.w >= 370
        assert roi.y + roi.h >= 250

    def test_two_objects_two_rois(self):
        """Two separated blobs should produce two ROIs."""
        ext = self._make_extractor(roi_min_area=10)
        energy = torch.zeros(1, 1, 480, 640)
        # Blob A: upper left
        energy[:, :, 50:100, 50:120] = 0.8
        # Blob B: lower right
        energy[:, :, 350:400, 450:530] = 0.8
        rois = ext(energy)
        assert len(rois) == 2

    def test_small_noise_filtered(self):
        """Tiny blobs below roi_min_area should be filtered out."""
        ext = self._make_extractor(roi_min_area=500)
        energy = torch.zeros(1, 1, 480, 640)
        # Tiny blob: 3x3 = 9 pixels. Even after morphological dilation
        # this stays well below 500 pixels.
        energy[:, :, 240:243, 320:323] = 0.8
        rois = ext(energy)
        assert len(rois) == 0

    def test_rois_clipped_to_bounds(self):
        """ROIs near frame edges should be clipped."""
        ext = self._make_extractor(roi_min_area=10, roi_padding=30)
        # Blob touching top-left corner
        energy = self._energy_with_blob(480, 640, 0, 40, 0, 40)
        rois = ext(energy)
        if len(rois) > 0:
            roi = rois[0]
            assert roi.x >= 0
            assert roi.y >= 0
            assert roi.x + roi.w <= 640
            assert roi.y + roi.h <= 480

    def test_empty_energy_no_rois(self):
        """All-zero motion energy should produce no ROIs."""
        ext = self._make_extractor()
        energy = torch.zeros(1, 1, 480, 640)
        rois = ext(energy)
        assert len(rois) == 0

    def test_max_count_respected(self):
        """ROI count should not exceed roi_max_count."""
        ext = self._make_extractor(roi_min_area=10, roi_max_count=2)
        energy = torch.zeros(1, 1, 480, 640)
        # Create 4 separated blobs
        for i, (y, x) in enumerate([(50, 50), (50, 400), (350, 50), (350, 400)]):
            energy[:, :, y:y + 40, x:x + 60] = 0.8
        rois = ext(energy)
        assert len(rois) <= 2

    def test_sorted_by_area(self):
        """ROIs should be sorted by area descending."""
        ext = self._make_extractor(roi_min_area=10)
        energy = torch.zeros(1, 1, 480, 640)
        # Small blob
        energy[:, :, 50:80, 50:80] = 0.8
        # Large blob
        energy[:, :, 300:400, 300:500] = 0.8
        rois = ext(energy)
        assert len(rois) >= 2
        assert rois[0].area >= rois[1].area

    def test_roi_has_correct_fields(self):
        """ROI namedtuple should have all expected fields."""
        ext = self._make_extractor(roi_min_area=10)
        energy = self._energy_with_blob(480, 640, 200, 260, 300, 380)
        rois = ext(energy)
        assert len(rois) >= 1
        roi = rois[0]
        assert isinstance(roi.x, int)
        assert isinstance(roi.y, int)
        assert isinstance(roi.w, int)
        assert isinstance(roi.h, int)
        assert isinstance(roi.area, int)
        assert isinstance(roi.centroid, tuple)
        assert len(roi.centroid) == 2

    def test_below_threshold_not_detected(self):
        """Blobs below accumulator_threshold should not be detected."""
        ext = self._make_extractor(accumulator_threshold=0.5)
        # Blob value is below threshold
        energy = self._energy_with_blob(480, 640, 200, 260, 300, 380, value=0.3)
        rois = ext(energy)
        assert len(rois) == 0
