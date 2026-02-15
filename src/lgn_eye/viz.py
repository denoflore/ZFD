"""Visualization utilities for the LGN-Eye pipeline.

Renders multi-panel views, HUD overlays, and flow visualizations.
"""

from __future__ import annotations

from collections import deque
from typing import Dict, List, Optional

import cv2
import numpy as np

from lgn_eye.config import LGNConfig
from lgn_eye.roi import ROI


class Visualizer:
    """Renders pipeline outputs into display frames."""

    def __init__(self, config: LGNConfig):
        self.config = config
        self._fps_history: deque[float] = deque(maxlen=30)
        self._font = cv2.FONT_HERSHEY_SIMPLEX

    def render(
        self,
        frame: np.ndarray,
        events: np.ndarray,
        motion_energy: np.ndarray,
        rois: List[ROI],
        flow: np.ndarray,
        flow_magnitude: np.ndarray,
        timings: Dict[str, float],
        fps: float,
        speedup_ratio: float,
        mode: str = "quad",
    ) -> np.ndarray:
        """Render visualization based on display mode.

        Args:
            frame: Original BGR frame (H, W, 3) uint8.
            events: Binary event map (H, W) float32 in [0, 1].
            motion_energy: Continuous energy map (H, W) float32 in [0, 1].
            rois: List of detected ROIs.
            flow: Optical flow map (H, W, 2) float32.
            flow_magnitude: Flow magnitude (H, W) float32.
            timings: Dict of stage name -> milliseconds.
            fps: Current FPS.
            speedup_ratio: Speedup vs full-frame flow.
            mode: 'quad', 'overlay', or 'debug'.

        Returns:
            Rendered visualization frame (BGR uint8).
        """
        self._fps_history.append(fps)

        if mode == "quad":
            return self._render_quad(
                frame, events, motion_energy, rois, flow, flow_magnitude,
                timings, speedup_ratio,
            )
        elif mode == "overlay":
            return self._render_overlay(
                frame, motion_energy, rois, flow, timings, speedup_ratio,
            )
        elif mode == "debug":
            return self._render_debug(
                frame, events, motion_energy, rois, flow, flow_magnitude,
                timings, speedup_ratio,
            )
        else:
            return self._render_quad(
                frame, events, motion_energy, rois, flow, flow_magnitude,
                timings, speedup_ratio,
            )

    def _smoothed_fps(self) -> float:
        if len(self._fps_history) == 0:
            return 0.0
        return sum(self._fps_history) / len(self._fps_history)

    def _draw_rois(self, img: np.ndarray, rois: List[ROI]) -> np.ndarray:
        """Draw green ROI bounding boxes."""
        for roi in rois:
            cv2.rectangle(
                img,
                (roi.x, roi.y),
                (roi.x + roi.w, roi.y + roi.h),
                (0, 255, 0),
                2,
            )
        return img

    def _draw_hud(
        self,
        img: np.ndarray,
        rois: List[ROI],
        timings: Dict[str, float],
        speedup_ratio: float,
    ) -> np.ndarray:
        """Draw HUD overlay with performance stats."""
        H, W = img.shape[:2]
        fps = self._smoothed_fps()
        roi_area = sum(r.w * r.h for r in rois)
        roi_pct = 100.0 * roi_area / (H * W) if H * W > 0 else 0.0
        device_str = self.config.device.upper()
        if device_str == "AUTO":
            import torch
            device_str = "CUDA" if torch.cuda.is_available() else "CPU"

        lines = [
            f"FPS: {fps:.1f}",
            f"ROIs: {len(rois)} ({roi_pct:.1f}%)",
            f"Speedup: {speedup_ratio:.1f}x",
        ]
        for name, ms in timings.items():
            lines.append(f"{name}: {ms:.1f}ms")
        lines.append(f"Device: {device_str}")

        y_offset = 20
        for line in lines:
            # Black shadow
            cv2.putText(
                img, line, (11, y_offset + 1),
                self._font, 0.45, (0, 0, 0), 2, cv2.LINE_AA,
            )
            # White text
            cv2.putText(
                img, line, (10, y_offset),
                self._font, 0.45, (255, 255, 255), 1, cv2.LINE_AA,
            )
            y_offset += 18

        return img

    def _energy_to_heatmap(self, energy: np.ndarray) -> np.ndarray:
        """Convert motion energy to HOT colormap visualization."""
        normed = np.clip(energy * 255, 0, 255).astype(np.uint8)
        return cv2.applyColorMap(normed, cv2.COLORMAP_HOT)

    def _events_to_bgr(self, events: np.ndarray) -> np.ndarray:
        """Convert binary events to white-on-black BGR image."""
        vis = (np.clip(events, 0, 1) * 255).astype(np.uint8)
        return cv2.cvtColor(vis, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def flow_to_hsv(flow: np.ndarray) -> np.ndarray:
        """Convert optical flow (H, W, 2) to HSV color encoding.

        Hue = direction (0-360), Value = magnitude (normalized).
        """
        mag = np.sqrt(flow[:, :, 0] ** 2 + flow[:, :, 1] ** 2)
        ang = np.arctan2(flow[:, :, 1], flow[:, :, 0])
        ang_deg = np.degrees(ang) % 360

        hsv = np.zeros((*flow.shape[:2], 3), dtype=np.uint8)
        hsv[:, :, 0] = (ang_deg / 2).astype(np.uint8)  # OpenCV hue is 0-180
        hsv[:, :, 1] = 255
        max_mag = mag.max()
        if max_mag > 0:
            hsv[:, :, 2] = np.clip(mag / max_mag * 255, 0, 255).astype(np.uint8)
        else:
            hsv[:, :, 2] = 0

        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    def _render_quad(
        self,
        frame: np.ndarray,
        events: np.ndarray,
        motion_energy: np.ndarray,
        rois: List[ROI],
        flow: np.ndarray,
        flow_magnitude: np.ndarray,
        timings: Dict[str, float],
        speedup_ratio: float,
    ) -> np.ndarray:
        """2x2 quad view: original+ROIs, energy heatmap, events, flow HSV."""
        H, W = frame.shape[:2]
        half_h, half_w = H // 2, W // 2

        # Top-left: original with ROI boxes
        tl = frame.copy()
        tl = self._draw_rois(tl, rois)
        tl = cv2.resize(tl, (half_w, half_h))

        # Top-right: motion energy heatmap
        tr = self._energy_to_heatmap(motion_energy)
        tr = cv2.resize(tr, (half_w, half_h))

        # Bottom-left: binary event map
        bl = self._events_to_bgr(events)
        bl = cv2.resize(bl, (half_w, half_h))

        # Bottom-right: flow HSV
        br = self.flow_to_hsv(flow)
        br = cv2.resize(br, (half_w, half_h))

        # Assemble quad
        top = np.hstack([tl, tr])
        bottom = np.hstack([bl, br])
        quad = np.vstack([top, bottom])

        # HUD
        quad = self._draw_hud(quad, rois, timings, speedup_ratio)

        return quad

    def _render_overlay(
        self,
        frame: np.ndarray,
        motion_energy: np.ndarray,
        rois: List[ROI],
        flow: np.ndarray,
        timings: Dict[str, float],
        speedup_ratio: float,
    ) -> np.ndarray:
        """Original frame with semi-transparent energy overlay + ROIs + flow arrows."""
        vis = frame.copy()

        # Semi-transparent energy overlay
        heatmap = self._energy_to_heatmap(motion_energy)
        vis = cv2.addWeighted(vis, 0.6, heatmap, 0.4, 0)

        # ROI boxes
        vis = self._draw_rois(vis, rois)

        # Flow arrows within ROIs
        step = 16
        H, W = frame.shape[:2]
        for y in range(0, H, step):
            for x in range(0, W, step):
                fx, fy = flow[y, x]
                mag = np.sqrt(fx * fx + fy * fy)
                if mag > 1.0:
                    end_x = int(x + fx)
                    end_y = int(y + fy)
                    cv2.arrowedLine(
                        vis, (x, y), (end_x, end_y),
                        (0, 255, 255), 1, tipLength=0.3,
                    )

        vis = self._draw_hud(vis, rois, timings, speedup_ratio)
        return vis

    def _render_debug(
        self,
        frame: np.ndarray,
        events: np.ndarray,
        motion_energy: np.ndarray,
        rois: List[ROI],
        flow: np.ndarray,
        flow_magnitude: np.ndarray,
        timings: Dict[str, float],
        speedup_ratio: float,
    ) -> np.ndarray:
        """Tiled view of all intermediate tensors."""
        H, W = frame.shape[:2]
        tile_h, tile_w = H // 3, W // 3

        def resize(img):
            return cv2.resize(img, (tile_w, tile_h))

        # Row 1: original, original+ROIs, energy heatmap
        orig = resize(frame)
        orig_rois = resize(self._draw_rois(frame.copy(), rois))
        energy_heat = resize(self._energy_to_heatmap(motion_energy))

        # Row 2: events, flow HSV, flow magnitude
        events_vis = resize(self._events_to_bgr(events))
        flow_hsv = resize(self.flow_to_hsv(flow))
        mag_normed = flow_magnitude / (flow_magnitude.max() + 1e-8)
        mag_vis = resize(self._energy_to_heatmap(mag_normed))

        # Row 3: overlay, blank placeholders
        overlay_small = resize(
            cv2.addWeighted(frame, 0.6, self._energy_to_heatmap(motion_energy), 0.4, 0)
        )
        blank = np.zeros((tile_h, tile_w, 3), dtype=np.uint8)

        row1 = np.hstack([orig, orig_rois, energy_heat])
        row2 = np.hstack([events_vis, flow_hsv, mag_vis])
        row3 = np.hstack([overlay_small, blank, blank])

        debug = np.vstack([row1, row2, row3])
        debug = self._draw_hud(debug, rois, timings, speedup_ratio)
        return debug
