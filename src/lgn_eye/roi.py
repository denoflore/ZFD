"""ROI extraction from motion energy maps via connected components.

Converts continuous motion energy tensors into discrete bounding box ROIs
using morphological cleanup and OpenCV connected components analysis.
"""

from __future__ import annotations

from typing import List, NamedTuple

import cv2
import numpy as np
import torch

from lgn_eye.config import LGNConfig


class ROI(NamedTuple):
    """A region of interest extracted from the motion energy map."""

    x: int
    y: int
    w: int
    h: int
    area: int
    centroid: tuple[float, float]


class ROIExtractor:
    """Extract bounding-box ROIs from motion energy maps."""

    def __init__(self, config: LGNConfig):
        self.config = config
        self._morph_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    def __call__(self, motion_energy: torch.Tensor) -> List[ROI]:
        """Extract ROIs from a motion energy tensor.

        Args:
            motion_energy: (B, 1, H, W) float tensor. Only batch element 0
                is processed (single-stream use case).

        Returns:
            List of ROI namedtuples sorted by area descending,
            capped at roi_max_count.
        """
        cfg = self.config

        # 1. Binarize
        mask = (motion_energy[0, 0] > cfg.accumulator_threshold)

        # 2. Transfer to CPU for OpenCV operations
        mask_np = mask.cpu().numpy().astype(np.uint8) * 255

        # 3. Morphological cleanup
        mask_np = cv2.morphologyEx(mask_np, cv2.MORPH_CLOSE, self._morph_kernel)
        dilate_iters = max(1, cfg.roi_padding // 5)
        mask_np = cv2.dilate(mask_np, self._morph_kernel, iterations=dilate_iters)

        # 4. Connected components
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            mask_np, connectivity=8
        )

        # 5. Filter and collect ROIs
        H = motion_energy.shape[2]
        W = motion_energy.shape[3]
        rois: List[ROI] = []

        for i in range(1, num_labels):  # skip background label 0
            area = int(stats[i, cv2.CC_STAT_AREA])
            if area < cfg.roi_min_area:
                continue

            x = int(stats[i, cv2.CC_STAT_LEFT])
            y = int(stats[i, cv2.CC_STAT_TOP])
            w = int(stats[i, cv2.CC_STAT_WIDTH])
            h = int(stats[i, cv2.CC_STAT_HEIGHT])
            cx, cy = float(centroids[i][0]), float(centroids[i][1])

            # Clip to frame bounds
            x = max(0, x)
            y = max(0, y)
            w = min(w, W - x)
            h = min(h, H - y)

            rois.append(ROI(x=x, y=y, w=w, h=h, area=area, centroid=(cx, cy)))

        # 6. Sort by area descending, cap at max count
        rois.sort(key=lambda r: r.area, reverse=True)
        return rois[: cfg.roi_max_count]
