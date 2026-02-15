"""Optical flow estimation restricted to ROI regions.

The key insight from Gao et al. (2026): by running optical flow only within
motion-detected ROIs, we achieve significant speedup over full-frame processing
while maintaining tracking accuracy.
"""

from __future__ import annotations

from typing import Dict, List

import cv2
import numpy as np

from lgn_eye.config import LGNConfig
from lgn_eye.roi import ROI


class FlowEstimator:
    """Compute optical flow only within extracted ROIs."""

    def __init__(self, config: LGNConfig):
        self.config = config
        self._raft_model = None

    def __call__(
        self,
        frame_prev: np.ndarray,
        frame_curr: np.ndarray,
        rois: List[ROI],
    ) -> Dict[str, object]:
        """Estimate optical flow within ROI regions.

        Args:
            frame_prev: Previous frame (H, W, 3) BGR uint8.
            frame_curr: Current frame (H, W, 3) BGR uint8.
            rois: List of ROI regions to compute flow within.

        Returns:
            Dict with:
                'flow': Full-frame flow map (H, W, 2) float32, zeros outside ROIs.
                'flow_magnitude': Magnitude map (H, W) float32.
                'roi_flows': List of per-ROI flow crops.
                'speedup_ratio': total_pixels / roi_pixels.
        """
        H, W = frame_prev.shape[:2]
        total_pixels = H * W

        flow_full = np.zeros((H, W, 2), dtype=np.float32)
        roi_flows = []
        roi_pixels = 0

        if self.config.flow_method == "none" or len(rois) == 0:
            return {
                "flow": flow_full,
                "flow_magnitude": np.zeros((H, W), dtype=np.float32),
                "roi_flows": [],
                "speedup_ratio": float("inf") if len(rois) == 0 else 1.0,
            }

        prev_gray = cv2.cvtColor(frame_prev, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(frame_curr, cv2.COLOR_BGR2GRAY)

        for roi in rois:
            x, y, w, h = roi.x, roi.y, roi.w, roi.h

            # Ensure valid crop dimensions
            if w < 2 or h < 2:
                continue

            prev_crop = prev_gray[y : y + h, x : x + w]
            curr_crop = curr_gray[y : y + h, x : x + w]

            if self.config.flow_method == "farneback":
                roi_flow = cv2.calcOpticalFlowFarneback(
                    prev_crop,
                    curr_crop,
                    None,
                    pyr_scale=0.5,
                    levels=3,
                    winsize=15,
                    iterations=3,
                    poly_n=5,
                    poly_sigma=1.2,
                    flags=0,
                )
            elif self.config.flow_method == "raft":
                roi_flow = self._compute_raft(prev_crop, curr_crop)
            else:
                continue

            # Place flow back into full-frame map
            flow_full[y : y + h, x : x + w] = roi_flow
            roi_flows.append(roi_flow)
            roi_pixels += w * h

        magnitude = np.sqrt(flow_full[:, :, 0] ** 2 + flow_full[:, :, 1] ** 2)

        speedup = total_pixels / roi_pixels if roi_pixels > 0 else float("inf")

        return {
            "flow": flow_full,
            "flow_magnitude": magnitude,
            "roi_flows": roi_flows,
            "speedup_ratio": speedup,
        }

    def _compute_raft(self, prev_gray: np.ndarray, curr_gray: np.ndarray) -> np.ndarray:
        """Compute flow using RAFT model (fallback to Farneback if unavailable)."""
        try:
            import torch
            import torchvision.models.optical_flow as of

            if self._raft_model is None:
                self._raft_model = of.raft_small(weights=of.Raft_Small_Weights.DEFAULT)
                self._raft_model.eval()
                device = self.config.resolve_device()
                self._raft_model.to(device)

            device = next(self._raft_model.parameters()).device

            # RAFT expects (B, 3, H, W) float tensors
            prev_t = torch.from_numpy(prev_gray).float().unsqueeze(0).unsqueeze(0)
            prev_t = prev_t.expand(-1, 3, -1, -1) / 255.0
            curr_t = torch.from_numpy(curr_gray).float().unsqueeze(0).unsqueeze(0)
            curr_t = curr_t.expand(-1, 3, -1, -1) / 255.0

            prev_t = prev_t.to(device)
            curr_t = curr_t.to(device)

            with torch.no_grad():
                flow_predictions = self._raft_model(prev_t, curr_t)
                flow = flow_predictions[-1]  # last refinement

            return flow[0].permute(1, 2, 0).cpu().numpy()
        except (ImportError, Exception):
            # Fallback to Farneback
            return cv2.calcOpticalFlowFarneback(
                prev_gray, curr_gray, None,
                pyr_scale=0.5, levels=3, winsize=15,
                iterations=3, poly_n=5, poly_sigma=1.2, flags=0,
            )
