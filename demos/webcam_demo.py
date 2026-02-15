#!/usr/bin/env python3
"""LGN-Eye: Real-time neuromorphic temporal attention demo.

Usage:
    python demos/webcam_demo.py                           # Default settings
    python demos/webcam_demo.py --width 1280 --height 720 # HD
    python demos/webcam_demo.py --flow raft               # Use RAFT optical flow
    python demos/webcam_demo.py --no-cuda                 # Force CPU

Controls:
    q     - Quit
    v     - Cycle view mode (quad / overlay / debug)
    t     - Toggle LGN attention (compare with full-frame flow)
    s     - Save screenshot
    +/-   - Adjust motion sensitivity
"""

import argparse

from lgn_eye import LGNPipeline, LGNConfig


def main():
    parser = argparse.ArgumentParser(description="LGN-Eye Webcam Demo")
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=480)
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument(
        "--flow", choices=["farneback", "raft", "none"], default="farneback"
    )
    parser.add_argument("--no-cuda", action="store_true")
    parser.add_argument(
        "--display", choices=["quad", "overlay", "debug"], default="quad"
    )
    args = parser.parse_args()

    config = LGNConfig(
        width=args.width,
        height=args.height,
        flow_method=args.flow,
        device="cpu" if args.no_cuda else "auto",
    )
    pipeline = LGNPipeline(config)
    pipeline.run_webcam(camera_id=args.camera, display_mode=args.display)


if __name__ == "__main__":
    main()
