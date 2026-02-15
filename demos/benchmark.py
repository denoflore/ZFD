#!/usr/bin/env python3
"""Benchmark LGN-Eye pipeline stages independently and combined.

Generates timing report showing per-stage latency and throughput.
Uses synthetic frames (no webcam needed).
Tests at multiple resolutions: 320x240, 640x480, 1280x720, 1920x1080.
"""

import time
import sys

import numpy as np
import torch

from lgn_eye.config import LGNConfig
from lgn_eye.temporal import TemporalAttentionLayer
from lgn_eye.roi import ROIExtractor, ROI
from lgn_eye.flow import FlowEstimator
from lgn_eye.pipeline import LGNPipeline


def benchmark_stage(fn, warmup=5, iterations=50):
    """Benchmark a callable, returning median time in ms."""
    for _ in range(warmup):
        fn()
    if torch.cuda.is_available():
        torch.cuda.synchronize()

    times = []
    for _ in range(iterations):
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        t0 = time.perf_counter()
        fn()
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000)

    times.sort()
    return {
        "median_ms": times[len(times) // 2],
        "mean_ms": sum(times) / len(times),
        "min_ms": times[0],
        "max_ms": times[-1],
    }


def print_table(results):
    """Print benchmark results as a formatted table."""
    print()
    print(f"{'Resolution':<14} {'Stage':<14} {'Median(ms)':>10} {'Mean(ms)':>10} {'Min(ms)':>10} {'Max(ms)':>10} {'FPS':>8}")
    print("-" * 82)
    for row in results:
        fps = 1000.0 / row["median_ms"] if row["median_ms"] > 0 else float("inf")
        print(
            f"{row['resolution']:<14} {row['stage']:<14} "
            f"{row['median_ms']:>10.2f} {row['mean_ms']:>10.2f} "
            f"{row['min_ms']:>10.2f} {row['max_ms']:>10.2f} "
            f"{fps:>8.1f}"
        )
    print()


def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    if device == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    print()

    resolutions = [
        (320, 240),
        (640, 480),
        (1280, 720),
        (1920, 1080),
    ]

    all_results = []

    for W, H in resolutions:
        res_str = f"{W}x{H}"
        print(f"Benchmarking {res_str}...")

        config = LGNConfig(width=W, height=H, device=device)

        # Synthetic frames
        frame_tensor = torch.rand(1, 3, H, W, device=device)
        frame_np = np.random.randint(0, 255, (H, W, 3), dtype=np.uint8)
        frame_np2 = np.random.randint(0, 255, (H, W, 3), dtype=np.uint8)

        # --- Temporal attention ---
        temporal = TemporalAttentionLayer(config)
        # Warmup to fill ring buffer
        for _ in range(5):
            temporal(frame_tensor)

        def run_temporal():
            temporal(torch.rand(1, 3, H, W, device=device))

        stats = benchmark_stage(run_temporal)
        all_results.append({"resolution": res_str, "stage": "temporal", **stats})

        # --- ROI extraction ---
        energy = torch.rand(1, 1, H, W) * 0.5
        # Add some above-threshold regions
        energy[:, :, H // 4 : H // 2, W // 4 : W // 2] = 0.8
        roi_ext = ROIExtractor(config)

        def run_roi():
            roi_ext(energy)

        stats = benchmark_stage(run_roi)
        all_results.append({"resolution": res_str, "stage": "roi", **stats})

        # --- Optical flow ---
        rois = [ROI(x=W // 4, y=H // 4, w=W // 4, h=H // 4, area=(W * H) // 16, centroid=(W * 3 / 8, H * 3 / 8))]
        flow_est = FlowEstimator(config)

        def run_flow():
            flow_est(frame_np, frame_np2, rois)

        stats = benchmark_stage(run_flow, warmup=3, iterations=20)
        all_results.append({"resolution": res_str, "stage": "flow", **stats})

        # --- Full pipeline ---
        pipeline = LGNPipeline(config)

        def run_pipeline():
            f = np.random.randint(0, 255, (H, W, 3), dtype=np.uint8)
            pipeline.process_frame(f)

        stats = benchmark_stage(run_pipeline, warmup=5, iterations=20)
        all_results.append({"resolution": res_str, "stage": "full_pipeline", **stats})

    print_table(all_results)


if __name__ == "__main__":
    main()
