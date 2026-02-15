# LGN-Eye Architecture

## System Overview

LGN-Eye replicates the lateral geniculate nucleus (LGN) temporal attention mechanism
in software, using PyTorch + Kornia + OpenCV + snnTorch.

## Pipeline Data Flow

```
Camera / Video Frame (BGR, uint8)
         │
         ▼
┌─────────────────────────────┐
│   RGB Conversion + Tensor   │  frame → (B, 3, H, W) float32 [0,1]
│   Transfer to GPU           │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│   Log-Luminance             │  0.2126*R + 0.7152*G + 0.0722*B
│   log1p(luminance)          │  → (B, 1, H, W)
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│   Multi-Scale DoG Filter    │  Center-surround at N scales
│   (Kornia gaussian_blur2d)  │  → (B, 1, H, W) filtered
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│   Temporal Difference       │  |filtered_t - filtered_{t-1}|
│   Ring Buffer (GPU)         │  → (B, 1, H, W) abs_diff
└─────────────┬───────────────┘
              │
              ├───────────────────────┐
              ▼                       ▼
┌──────────────────────┐  ┌──────────────────────┐
│  Binary Events       │  │  Leaky Accumulation  │
│  (abs_diff > thresh) │  │  EMA or LIF neurons  │
│  → events (B,1,H,W)  │  │  → motion_energy     │
└──────────────────────┘  └──────────┬───────────┘
                                     │
                                     ▼
                          ┌──────────────────────┐
                          │  ROI Extraction       │
                          │  Binarize + Morphology│
                          │  Connected Components │
                          │  → List[ROI]          │
                          └──────────┬───────────┘
                                     │
                          ┌──────────┴───────────┐
                          │                      │
                    Crop prev_frame       Crop curr_frame
                          │                      │
                          └────── Optical ────────┘
                                  Flow
                          (Farneback or RAFT)
                                  │
                                  ▼
                          ┌──────────────────────┐
                          │  Flow Vectors         │
                          │  (within ROIs only)   │
                          │  → (H, W, 2) flow     │
                          └──────────┬───────────┘
                                     │
                                     ▼
                          ┌──────────────────────┐
                          │  Visualization        │
                          │  Quad / Overlay / Dbg │
                          │  + HUD overlay        │
                          └──────────────────────┘
```

## Module Responsibilities

| Module       | File                  | Role                                      |
|--------------|-----------------------|-------------------------------------------|
| Config       | `src/lgn_eye/config.py`    | Dataclass with all pipeline parameters    |
| Temporal     | `src/lgn_eye/temporal.py`  | DoG filtering, differencing, accumulation |
| ROI          | `src/lgn_eye/roi.py`       | Connected components → bounding boxes     |
| Flow         | `src/lgn_eye/flow.py`      | ROI-restricted optical flow               |
| Spiking      | `src/lgn_eye/spiking.py`   | LIF neuron accumulator (snnTorch)         |
| Visualization| `src/lgn_eye/viz.py`       | Multi-mode display rendering              |
| Pipeline     | `src/lgn_eye/pipeline.py`  | Orchestrates all modules                  |

## Device Strategy

- All tensor operations target CUDA when available
- ROI extraction transfers a single 2D mask to CPU for OpenCV connected components
- Optical flow runs on CPU (OpenCV Farneback) or GPU (RAFT)
- Automatic fallback to CPU if CUDA unavailable
