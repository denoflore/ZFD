# LGN-Eye

**Software replication of LGN temporal attention for real-time motion detection**

A PyTorch implementation of the lateral geniculate nucleus temporal attention mechanism
from Gao et al. (2026) "Ultrafast visual perception beyond human capabilities enabled
by motion analysis using synaptic transistors" (Nature Communications).

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Run webcam demo
python demos/webcam_demo.py

# Run benchmark (no webcam needed)
python demos/benchmark.py

# Run tests
pytest tests/ -v
```

## Architecture

```
Camera Frame ──┐
               ├── Log-Luminance ── DoG Filter ── Temporal Diff ── |ΔI|
Previous Frame ┘                                                     │
                                                          ┌──────────┴──────────┐
                                                          ▼                     ▼
                                                    Binary Events     Leaky Accumulator
                                                                      (EMA or LIF)
                                                                            │
                                                                            ▼
                                                                    ROI Extraction
                                                                    (Connected Components)
                                                                            │
                                                               ┌────────────┴────────────┐
                                                               ▼                         ▼
                                                         Crop Frame(t)           Crop Frame(t-1)
                                                               │                         │
                                                               └──── Optical Flow ───────┘
                                                                     (ROIs only)
                                                                          │
                                                                          ▼
                                                                  Visualization
```

## Configuration

```python
from lgn_eye import LGNConfig, LGNPipeline

config = LGNConfig(
    width=640, height=480,
    decay_alpha=0.85,          # Accumulator decay
    motion_threshold=0.05,     # Brightness change threshold
    accumulator_threshold=0.3, # ROI detection threshold
    dog_scales=3,              # Multi-scale DoG levels
    flow_method="farneback",   # "farneback" | "raft" | "none"
    accumulator_type="ema",    # "ema" | "lif" (spiking neurons)
    device="auto",             # "auto" | "cuda" | "cpu"
)

pipeline = LGNPipeline(config)
```

## Display Modes

- **Quad view** (default): 2x2 grid - original+ROIs, energy heatmap, events, flow HSV
- **Overlay mode**: Original frame with semi-transparent energy overlay + flow arrows
- **Debug mode**: All intermediate tensors tiled

## Webcam Controls

| Key | Action                              |
|-----|-------------------------------------|
| q   | Quit                                |
| v   | Cycle display mode                  |
| t   | Toggle temporal attention on/off    |
| s   | Save screenshot                     |
| +/- | Adjust motion sensitivity           |

## Modules

| Module                    | Description                                    |
|---------------------------|------------------------------------------------|
| `lgn_eye.temporal`        | Temporal attention: DoG, differencing, accumulation |
| `lgn_eye.roi`             | Connected component ROI extraction              |
| `lgn_eye.flow`            | ROI-restricted optical flow (Farneback/RAFT)    |
| `lgn_eye.spiking`         | LIF neuron accumulator (snnTorch)               |
| `lgn_eye.viz`             | Multi-mode visualization rendering              |
| `lgn_eye.pipeline`        | Full pipeline orchestrator                      |

## Performance

Target: 30+ fps at 640x480 on NVIDIA RTX 4070/4080 GPU.
CPU fallback works at reduced frame rate.

Key metric: **Speedup ratio** - processing only ROI regions yields 3-10x speedup
over full-frame optical flow.

## Citation

```bibtex
@article{gao2026ultrafast,
  title={Ultrafast visual perception beyond human capabilities enabled by motion
         analysis using synaptic transistors},
  author={Gao, et al.},
  journal={Nature Communications},
  year={2026},
  doi={10.1038/s41467-026-68659-y}
}
```

## Acknowledgments

- Gao et al. for the LGN temporal attention algorithm
- [Kornia](https://kornia.github.io/) for differentiable image processing
- [snnTorch](https://snntorch.readthedocs.io/) for spiking neural network dynamics
- [OpenCV](https://opencv.org/) for optical flow and connected components

## License

MIT
