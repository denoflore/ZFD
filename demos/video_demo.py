#!/usr/bin/env python3
"""LGN-Eye: Process a video file with temporal attention pipeline.

Usage:
    python demos/video_demo.py input.mp4
    python demos/video_demo.py input.mp4 -o output.mp4
    python demos/video_demo.py input.mp4 --no-cuda
"""

import argparse

from lgn_eye import LGNPipeline, LGNConfig


def main():
    parser = argparse.ArgumentParser(description="LGN-Eye Video Demo")
    parser.add_argument("input", help="Path to input video file")
    parser.add_argument("-o", "--output", help="Path to save output video")
    parser.add_argument(
        "--flow", choices=["farneback", "raft", "none"], default="farneback"
    )
    parser.add_argument("--no-cuda", action="store_true")
    args = parser.parse_args()

    config = LGNConfig(
        flow_method=args.flow,
        device="cpu" if args.no_cuda else "auto",
    )
    pipeline = LGNPipeline(config)
    pipeline.run_video(args.input, args.output)


if __name__ == "__main__":
    main()
