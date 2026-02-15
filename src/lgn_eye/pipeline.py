"""LGN-Eye pipeline orchestrator.

Wires together temporal attention, ROI extraction, optical flow, and
visualization into a single processing pipeline.
"""

from __future__ import annotations

import time
from typing import Dict, Optional

import cv2
import numpy as np
import torch

from lgn_eye.config import LGNConfig
from lgn_eye.temporal import TemporalAttentionLayer
from lgn_eye.roi import ROIExtractor
from lgn_eye.flow import FlowEstimator
from lgn_eye.viz import Visualizer


class LGNPipeline:
    """Full LGN temporal attention pipeline."""

    def __init__(self, config: LGNConfig | None = None):
        self.config = config or LGNConfig()
        self.device = self.config.resolve_device()
        self.temporal = TemporalAttentionLayer(self.config)
        self.roi_extractor = ROIExtractor(self.config)
        self.flow_estimator = FlowEstimator(self.config)
        self.visualizer = Visualizer(self.config)
        self.prev_frame_np: Optional[np.ndarray] = None
        self.timings: Dict[str, float] = {}

    def process_frame(self, frame: np.ndarray) -> dict:
        """Process a single BGR frame through the full pipeline.

        Args:
            frame: BGR uint8 image (H, W, 3).

        Returns:
            Dict with all outputs and rendered visualization.
        """
        H, W = frame.shape[:2]

        # 1. Convert to tensor
        t0 = time.perf_counter()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        tensor = (
            torch.from_numpy(frame_rgb)
            .permute(2, 0, 1)
            .unsqueeze(0)
            .float()
            .div(255.0)
            .to(self.device)
        )

        # 2. Temporal attention
        t1 = time.perf_counter()
        temporal_out = self.temporal(tensor)
        t2 = time.perf_counter()

        # 3. ROI extraction
        rois = self.roi_extractor(temporal_out["motion_energy"])
        t3 = time.perf_counter()

        # 4. Optical flow (need previous frame)
        if self.prev_frame_np is not None:
            flow_out = self.flow_estimator(self.prev_frame_np, frame, rois)
        else:
            flow_out = {
                "flow": np.zeros((H, W, 2), dtype=np.float32),
                "flow_magnitude": np.zeros((H, W), dtype=np.float32),
                "roi_flows": [],
                "speedup_ratio": float("inf"),
            }
        t4 = time.perf_counter()

        self.prev_frame_np = frame.copy()

        self.timings = {
            "temporal": (t2 - t1) * 1000,
            "roi": (t3 - t2) * 1000,
            "flow": (t4 - t3) * 1000,
        }
        total_ms = (t4 - t0) * 1000
        fps = 1000.0 / total_ms if total_ms > 0 else 0.0

        # Extract numpy arrays from tensor outputs
        events_np = temporal_out["events"][0, 0].cpu().numpy()
        energy_np = temporal_out["motion_energy"][0, 0].cpu().numpy()

        return {
            "events": events_np,
            "motion_energy": energy_np,
            "temporal_diff": temporal_out["temporal_diff"][0, 0].cpu().numpy(),
            "dog_filtered": temporal_out["dog_filtered"][0, 0].cpu().numpy(),
            "rois": rois,
            "flow": flow_out["flow"],
            "flow_magnitude": flow_out["flow_magnitude"],
            "roi_flows": flow_out["roi_flows"],
            "speedup_ratio": flow_out["speedup_ratio"],
            "timings": self.timings,
            "fps": fps,
        }

    def render(self, frame: np.ndarray, result: dict, mode: str = "quad") -> np.ndarray:
        """Render visualization from pipeline results.

        Args:
            frame: Original BGR frame.
            result: Output from process_frame().
            mode: 'quad', 'overlay', or 'debug'.

        Returns:
            Rendered BGR visualization.
        """
        return self.visualizer.render(
            frame=frame,
            events=result["events"],
            motion_energy=result["motion_energy"],
            rois=result["rois"],
            flow=result["flow"],
            flow_magnitude=result["flow_magnitude"],
            timings=result["timings"],
            fps=result["fps"],
            speedup_ratio=result["speedup_ratio"],
            mode=mode,
        )

    def run_webcam(self, camera_id: int = 0, display_mode: str = "quad"):
        """Live webcam loop with keyboard controls.

        Controls:
            q - Quit
            v - Cycle display mode (quad / overlay / debug)
            t - Toggle temporal attention on/off
            s - Save screenshot
            +/= - Increase motion threshold
            -   - Decrease motion threshold
        """
        cap = cv2.VideoCapture(camera_id)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)

        if not cap.isOpened():
            raise RuntimeError(f"Cannot open camera {camera_id}")

        modes = ["quad", "overlay", "debug"]
        mode_idx = modes.index(display_mode) if display_mode in modes else 0
        attention_enabled = True
        screenshot_counter = 0

        print("LGN-Eye Webcam Demo")
        print("Controls: q=quit, v=cycle view, t=toggle attention, s=screenshot, +/-=threshold")

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if attention_enabled:
                    result = self.process_frame(frame)
                    vis = self.render(frame, result, mode=modes[mode_idx])
                else:
                    # Full-frame flow without attention (for comparison)
                    H, W = frame.shape[:2]
                    result = {
                        "events": np.zeros((H, W), dtype=np.float32),
                        "motion_energy": np.zeros((H, W), dtype=np.float32),
                        "rois": [],
                        "flow": np.zeros((H, W, 2), dtype=np.float32),
                        "flow_magnitude": np.zeros((H, W), dtype=np.float32),
                        "timings": {},
                        "fps": 0.0,
                        "speedup_ratio": 1.0,
                    }
                    vis = frame.copy()
                    cv2.putText(
                        vis, "ATTENTION OFF", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2,
                    )

                cv2.imshow("LGN-Eye", vis)

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                elif key == ord("v"):
                    mode_idx = (mode_idx + 1) % len(modes)
                    print(f"Display mode: {modes[mode_idx]}")
                elif key == ord("t"):
                    attention_enabled = not attention_enabled
                    if not attention_enabled:
                        self.temporal.reset()
                        self.prev_frame_np = None
                    print(f"Attention: {'ON' if attention_enabled else 'OFF'}")
                elif key == ord("s"):
                    fname = f"lgn_eye_screenshot_{screenshot_counter:04d}.png"
                    cv2.imwrite(fname, vis)
                    print(f"Saved: {fname}")
                    screenshot_counter += 1
                elif key in (ord("+"), ord("=")):
                    self.config.motion_threshold = min(
                        1.0, self.config.motion_threshold + 0.01
                    )
                    self.temporal.config.motion_threshold = self.config.motion_threshold
                    print(f"Threshold: {self.config.motion_threshold:.3f}")
                elif key == ord("-"):
                    self.config.motion_threshold = max(
                        0.001, self.config.motion_threshold - 0.01
                    )
                    self.temporal.config.motion_threshold = self.config.motion_threshold
                    print(f"Threshold: {self.config.motion_threshold:.3f}")
        finally:
            cap.release()
            cv2.destroyAllWindows()

    def run_video(self, input_path: str, output_path: str | None = None):
        """Process a video file, optionally saving output.

        Args:
            input_path: Path to input video.
            output_path: Optional path to save rendered output video.
        """
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open video: {input_path}")

        fps_in = cap.get(cv2.CAP_PROP_FPS) or 30.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(output_path, fourcc, fps_in, (width, height))

        frame_idx = 0
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                result = self.process_frame(frame)
                vis = self.render(frame, result, mode="quad")

                if writer:
                    writer.write(vis)

                frame_idx += 1
                if frame_idx % 30 == 0:
                    pct = 100.0 * frame_idx / total_frames if total_frames > 0 else 0
                    print(
                        f"Frame {frame_idx}/{total_frames} ({pct:.1f}%) "
                        f"- FPS: {result['fps']:.1f}"
                    )
        finally:
            cap.release()
            if writer:
                writer.release()

        print(f"Processed {frame_idx} frames.")
