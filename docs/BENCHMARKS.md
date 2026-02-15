# LGN-Eye Benchmarks

## How to Run

```bash
python demos/benchmark.py
```

## Expected Results (CPU, reference)

| Resolution | Stage         | Median (ms) | FPS   |
|------------|---------------|-------------|-------|
| 320x240    | temporal      | ~14         | ~71   |
| 320x240    | roi           | ~1.4        | ~735  |
| 320x240    | flow          | ~1.2        | ~816  |
| 320x240    | full_pipeline | ~27         | ~37   |
| 640x480    | temporal      | ~28         | ~36   |
| 640x480    | roi           | ~3.5        | ~288  |
| 640x480    | flow          | ~5.8        | ~171  |
| 640x480    | full_pipeline | ~44         | ~23   |

## Expected Results (GPU, target: RTX 4070/4080)

GPU acceleration primarily benefits the temporal attention stage (Kornia gaussian
blur operations). Expected 5-10x speedup on temporal stage, achieving 30+ fps
at 640x480 for full pipeline.

## Speedup Ratio

The key metric from the paper: how much faster is ROI-restricted flow vs
full-frame flow. Typical values:

- 20% frame activity: ~5x speedup
- 10% frame activity: ~10x speedup
- 50% frame activity: ~2x speedup
