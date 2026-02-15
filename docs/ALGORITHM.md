# LGN-Eye Algorithm

## Reference

Gao et al. (2026) "Ultrafast visual perception beyond human capabilities enabled by
motion analysis using synaptic transistors" (Nature Communications,
DOI: 10.1038/s41467-026-68659-y)

## Biological Basis

The lateral geniculate nucleus (LGN) acts as a relay and preprocessing center
between the retina and visual cortex. Key properties replicated:

1. **Center-surround receptive fields**: Difference-of-Gaussians (DoG) filtering
   enhances edges and contrast boundaries, similar to retinal ganglion cells.

2. **Temporal change detection**: The synapse array in the paper detects brightness
   changes over time with ~100 μs response time. We replicate this with frame
   differencing after DoG filtering.

3. **Leaky integration**: Biological neurons accumulate evidence with exponential
   decay. We implement this as either:
   - Exponential moving average (EMA): `acc = α * acc_prev + (1-α) * input`
   - Leaky integrate-and-fire (LIF) neurons via snnTorch

## Algorithm Steps

### Step 1: Log-Luminance Conversion

Convert RGB to luminance using ITU-R BT.709 coefficients, then apply log
transform for perceptual uniformity and numerical stability:

```
lum = 0.2126*R + 0.7152*G + 0.0722*B
log_lum = log(1 + lum)
```

### Step 2: Multi-Scale Center-Surround (DoG)

For each scale s in [0, N):
```
σ_center = σ_base * 2^s
σ_surround = σ_center * ratio    (ratio ≈ 1.6 per biology)
DoG_s = G(σ_center) * log_lum - G(σ_surround) * log_lum
```

Final filtered output is the mean across scales.

### Step 3: Temporal Difference

```
diff = filtered_t - filtered_{t-1}
abs_diff = |diff|
```

Previous frames stored in a GPU ring buffer (deque with maxlen).

### Step 4: Binary Event Detection

```
events = (abs_diff > motion_threshold)
```

### Step 5: Leaky Accumulation

**EMA mode:**
```
accumulator = α * accumulator + (1-α) * abs_diff
```

**LIF mode (snnTorch):**
```
membrane += input_current
if membrane > threshold:
    spike = 1
    membrane -= threshold
membrane *= β   (decay)
```

### Step 6: ROI Extraction

1. Binarize accumulator: `mask = (energy > threshold)`
2. Morphological close + dilate
3. Connected components (OpenCV)
4. Filter by minimum area
5. Extract bounding boxes with padding

### Step 7: ROI-Restricted Optical Flow

For each ROI bounding box:
1. Crop previous and current frames
2. Run Farneback or RAFT optical flow on crops
3. Place flow vectors back into full-frame map

**Key speedup**: Only process ROI pixels, skip static background.
Typical speedup: 3-10x depending on scene activity.

## Parameters

| Parameter              | Default | Description                          |
|------------------------|---------|--------------------------------------|
| decay_alpha            | 0.85    | EMA/LIF membrane decay rate          |
| motion_threshold       | 0.05    | Temporal difference threshold         |
| accumulator_threshold  | 0.3     | ROI binarization threshold            |
| dog_sigma_center       | 1.0     | DoG center Gaussian sigma             |
| dog_sigma_surround     | 1.6     | DoG surround Gaussian sigma           |
| dog_scales             | 3       | Number of DoG scale levels            |
| roi_min_area           | 100     | Minimum connected component area      |
| roi_padding            | 20      | Dilation padding around ROIs          |
| roi_max_count          | 10      | Maximum simultaneous ROIs             |
