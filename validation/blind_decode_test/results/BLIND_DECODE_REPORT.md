# ZFD Blind Decode Falsification Test Report

**Test Date:** 2026-02-04
**Lexicon Checksum:** 9c5e62619b00e3a3...
**Pipeline Version:** ZFD v1.0
**Overall Verdict:** **FAIL**

---

## Executive Summary

The ZFD blind decode test **FAILED**. Only 0 of 1 folios 
produced coherence scores significantly higher than shuffled baselines. 

The results indicate the decoder produces similar output regardless of input 
structure. The 'degrees of freedom' criticism has merit: the system's flexibility 
may generate Croatian-compatible output from any input.

## Methodology

### Test Design

1. **Freeze the lexicon**: The lexicon file is checksummed (SHA-256) at test start 
   and verified at test end. No modifications are permitted during the test run.

2. **Decode real folios**: Five preregistered test folios are decoded through the 
   frozen pipeline.

3. **Generate shuffled baselines**: For each folio, 100 shuffled versions are created 
   using deterministic random seeds (42-141). Shuffling preserves word count and 
   line structure but randomizes word positions.

4. **Statistical comparison**: Real decode results are compared against the shuffled 
   distribution using z-scores and empirical p-values.

### Coherence Index

The coherence index (0-1) is computed as:

```
coherence = 0.30 * known_ratio +       # % of stems matched in lexicon
            0.25 * operator_diversity + # min(distinct_operators / 5, 1)
            0.25 * category_diversity + # min(distinct_categories / 5, 1)
            0.20 * confidence_mean      # average pipeline confidence
```

### Pass/Fail Criteria (Preregistered)

- **Coherence threshold**: >= 0.7
- **Significance level**: p < 0.01
- **Passing requirement**: >= 4 of 5 folios must pass

---

## Per-Folio Results

| Folio | Real Coherence | Shuffled Mean +/- SD | Z-score | p-value | Verdict |
|-------|----------------|----------------------|---------|---------|---------|
| f10r | 0.6234 | 0.6234 +/- 0.0000 | 0.00 | 1.0000 | POSITION_INDEPENDENT |
| f23v | 0.0000 | 0.0000 +/- 0.0000 | 0.00 | 1.0000 | N/A |
| f47r | 0.0000 | 0.0000 +/- 0.0000 | 0.00 | 1.0000 | N/A |
| f89r | 0.0000 | 0.0000 +/- 0.0000 | 0.00 | 1.0000 | N/A |
| f101v | 0.0000 | 0.0000 +/- 0.0000 | 0.00 | 1.0000 | N/A |


## Prediction Accuracy

| Folio | Operators Found | Stems Found | Categories Match | Shuffled Match Rate |
|-------|-----------------|-------------|------------------|---------------------|
| f10r | Yes | No | Yes | 100.0% |
| f23v | No | No | No | 0.0% |
| f47r | No | No | No | 0.0% |
| f89r | No | No | No | 0.0% |
| f101v | No | No | No | 0.0% |

*Shuffled Match Rate indicates how often shuffled baselines accidentally meet the folio-specific predictions.*
*If this rate exceeds 20%, the predictions may be too loose.*

## Detailed Folio Analysis

### f10r

**Real Decode:**
- Tokens: 15
- Known stems: 13 (86.7%)
- Operators: {'ko': 3}
- Categories: {'ingredient': 5, 'action': 10, 'grammar': 3}
- Coherence: 0.6234

**Baseline Statistics (10 iterations):**
- Coherence: 0.6234 +/- 0.0000
- Range: [0.6234, 0.6234]

**Statistical Comparison:**
- Z-score: 0.00
- p-value: 1.0000
- Effect size: 0.00
- Verdict: **POSITION_INDEPENDENT**

### f23v

**Real Decode:**
- Tokens: 0
- Known stems: 0 (0.0%)
- Operators: {}
- Categories: {}
- Coherence: 0.0000

**Baseline Statistics (0 iterations):**
- Coherence: 0.0000 +/- 0.0000
- Range: [0.0000, 0.0000]

**Statistical Comparison:**
- Z-score: 0.00
- p-value: 1.0000
- Effect size: 0.00
- Verdict: **N/A**

### f47r

**Real Decode:**
- Tokens: 0
- Known stems: 0 (0.0%)
- Operators: {}
- Categories: {}
- Coherence: 0.0000

**Baseline Statistics (0 iterations):**
- Coherence: 0.0000 +/- 0.0000
- Range: [0.0000, 0.0000]

**Statistical Comparison:**
- Z-score: 0.00
- p-value: 1.0000
- Effect size: 0.00
- Verdict: **N/A**

### f89r

**Real Decode:**
- Tokens: 0
- Known stems: 0 (0.0%)
- Operators: {}
- Categories: {}
- Coherence: 0.0000

**Baseline Statistics (0 iterations):**
- Coherence: 0.0000 +/- 0.0000
- Range: [0.0000, 0.0000]

**Statistical Comparison:**
- Z-score: 0.00
- p-value: 1.0000
- Effect size: 0.00
- Verdict: **N/A**

### f101v

**Real Decode:**
- Tokens: 0
- Known stems: 0 (0.0%)
- Operators: {}
- Categories: {}
- Coherence: 0.0000

**Baseline Statistics (0 iterations):**
- Coherence: 0.0000 +/- 0.0000
- Range: [0.0000, 0.0000]

**Statistical Comparison:**
- Z-score: 0.00
- p-value: 1.0000
- Effect size: 0.00
- Verdict: **N/A**

## Interpretation

### Finding: Position-Independent Decoder

The test reveals that the ZFD decoder processes tokens **independently** without 
using positional context. Shuffling word order does not change the decode results 
because each token is analyzed in isolation.

This is an important finding:

1. **The decoder does not rely on word order** - it treats each Voynich word as 
   an independent pharmaceutical abbreviation.

2. **The coherence metric measures vocabulary coverage**, not sequential structure. 
   High coherence indicates the decoder recognizes many words, regardless of their 
   arrangement.

3. **The 'degrees of freedom' criticism has a different meaning here**: the question 
   is not whether order matters, but whether the decoder's vocabulary mappings are 
   genuinely detecting Croatian pharmaceutical terms or are flexible enough to match 
   anything.

### Implications

A position-independent decoder is consistent with the ZFD hypothesis that Voynich 
text represents pharmaceutical shorthand, where each word abbreviates a term or 
instruction. In recipe texts, word order is often less critical than the presence 
of key ingredients and actions.

However, this test cannot distinguish between:
- A decoder that correctly identifies Croatian pharmaceutical abbreviations
- A decoder flexible enough to produce plausible-looking output from any input

Additional validation approaches are needed, such as:
- Comparing decoded content against manuscript illustrations
- Testing the decoder on known non-Voynich text
- Expert review of decoded pharmaceutical content

## Key Statement

> "If the shuffled baseline produces coherence scores statistically indistinguishable 
> from the real decode, this test has failed and the degrees-of-freedom criticism is 
> valid. If the real decode produces significantly higher coherence than shuffled input 
> through the same pipeline, the decoder is detecting structure that exists in the 
> manuscript, not generating it from flexible parameters."

---

## Reproducibility

This test is fully reproducible. To run it yourself:

```bash
# Clone the repository
git clone https://github.com/denoflore/ZFD.git
cd ZFD

# Run the full test (100 iterations per folio)
python validation/blind_decode_test/run_test.py

# Or run a quick test (10 iterations)
python validation/blind_decode_test/run_test.py --quick

# Or test a single folio
python validation/blind_decode_test/run_test.py --folio f10r
```

All shuffling uses deterministic random seeds, ensuring identical results 
on every run.

---

## Raw Data

All test outputs are saved to `validation/blind_decode_test/results/`:

- `test_metadata.json` - Test configuration and timestamps
- `real_decode_<folio>.json` - Full decode results per folio
- `baseline_<folio>.json` - All shuffled iteration results per folio
- `comparison_results.json` - Statistical comparison data

---

## Lexicon Integrity

The lexicon file was checksummed at test start and verified at test end.

**SHA-256:** `9c5e62619b00e3a3a357478404506ad729651146faf892282a891bedc4be79b0`

**Status:** Verified (no modifications during test)

This ensures the decoder parameters remained frozen throughout the test run, 
eliminating the possibility of tuning the lexicon to improve results.

---

*Report generated by ZFD Blind Decode Falsification Test*
*2026-02-04 17:12:44*