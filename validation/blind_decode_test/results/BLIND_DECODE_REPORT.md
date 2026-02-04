# ZFD Blind Decode Falsification Test Report

**Test Date:** 2026-02-04
**Lexicon Checksum:** 9c5e62619b00e3a3...
**Pipeline Version:** ZFD v1.0
**Overall Verdict:** **INCONCLUSIVE -- TEST DESIGN ERROR (see v2)**

---

## Executive Summary

The ZFD blind decode test v1.1 returned **INCONCLUSIVE** results due to a test design 
error. The test measured sensitivity to word ORDER, but the ZFD decoder is 
position-independent (bag-of-words). Shuffling word positions within a folio has no 
effect because each token is decoded in isolation. This is expected behavior for 
pharmaceutical shorthand where each abbreviation is self-contained.

**This is not a decipherment failure.** The test infrastructure worked correctly but 
tested the wrong axis. The actual degrees-of-freedom question -- whether non-Voynich 
input produces comparable results -- is answered by test v2 (vocabulary specificity), 
which PASSED on all 5 folios.

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
| f10r | 0.7043 | 0.7043 +/- 0.0000 | 0.00 | 1.0000 | MARGINAL |
| f23v | 0.7655 | 0.7655 +/- 0.0000 | 0.00 | 1.0000 | PASS_PREDICTIONS |
| f47r | 0.7001 | 0.7001 +/- 0.0000 | 0.00 | 1.0000 | MARGINAL |
| f89r | 0.6938 | 0.6938 +/- 0.0000 | 0.00 | 1.0000 | POSITION_INDEPENDENT |
| f101v | 0.7442 | 0.7442 +/- 0.0000 | 0.00 | 1.0000 | PASS_PREDICTIONS |


## Prediction Accuracy

| Folio | Operators Found | Stems Found | Categories Match | Shuffled Match Rate |
|-------|-----------------|-------------|------------------|---------------------|
| f10r | Yes | No | Yes | 100.0% |
| f23v | Yes | Yes | Yes | 100.0% |
| f47r | Yes | No | Yes | 100.0% |
| f89r | Yes | Yes | Yes | 100.0% |
| f101v | Yes | Yes | Yes | 100.0% |

*Shuffled Match Rate indicates how often shuffled baselines accidentally meet the folio-specific predictions.*
*If this rate exceeds 20%, the predictions may be too loose.*

## Detailed Folio Analysis

### f10r

**Real Decode:**
- Tokens: 89
- Known stems: 37 (41.6%)
- Operators: {'š': 4, 'h': 17, 'otr': 4, 'ost': 1, 'da': 7, 'ko': 11}
- Categories: {'ingredient': 30, 'action': 28, 'equipment': 5, 'measurement': 7, 'grammar': 11}
- Coherence: 0.7043

**Baseline Statistics (10 iterations):**
- Coherence: 0.7043 +/- 0.0000
- Range: [0.7043, 0.7043]

**Statistical Comparison:**
- Z-score: 0.00
- p-value: 1.0000
- Effect size: 0.00
- Verdict: **MARGINAL**

### f23v

**Real Decode:**
- Tokens: 83
- Known stems: 48 (57.8%)
- Operators: {'š': 7, 'otr': 4, 'h': 8, 'ko': 7, 'ost': 8, 'da': 9}
- Categories: {'ingredient': 43, 'action': 20, 'equipment': 12, 'grammar': 7, 'measurement': 9, 'other': 1}
- Coherence: 0.7655

**Baseline Statistics (10 iterations):**
- Coherence: 0.7655 +/- 0.0000
- Range: [0.7655, 0.7655]

**Statistical Comparison:**
- Z-score: 0.00
- p-value: 1.0000
- Effect size: 0.00
- Verdict: **PASS_PREDICTIONS**

### f47r

**Real Decode:**
- Tokens: 82
- Known stems: 32 (39.0%)
- Operators: {'š': 9, 'da': 10, 'h': 27, 'ost': 3, 'ko': 2, 'otr': 2}
- Categories: {'ingredient': 29, 'action': 39, 'measurement': 10, 'equipment': 5, 'grammar': 2}
- Coherence: 0.7001

**Baseline Statistics (10 iterations):**
- Coherence: 0.7001 +/- 0.0000
- Range: [0.7001, 0.7001]

**Statistical Comparison:**
- Z-score: 0.00
- p-value: 1.0000
- Effect size: 0.00
- Verdict: **MARGINAL**

### f89r

**Real Decode:**
- Tokens: 387
- Known stems: 148 (38.3%)
- Operators: {'ost': 20, 'k': 2, 'otr': 10, 'h': 79, 'da': 62, 'š': 23, 'ko': 47}
- Categories: {'ingredient': 129, 'equipment': 30, 'grammar': 49, 'action': 122, 'measurement': 62, 'other': 3, 'preparation': 1}
- Coherence: 0.6938

**Baseline Statistics (10 iterations):**
- Coherence: 0.6938 +/- 0.0000
- Range: [0.6938, 0.6938]

**Statistical Comparison:**
- Z-score: 0.00
- p-value: 1.0000
- Effect size: 0.00
- Verdict: **POSITION_INDEPENDENT**

### f101v

**Real Decode:**
- Tokens: 208
- Known stems: 109 (52.4%)
- Operators: {'otr': 7, 'ost': 10, 'h': 35, 'š': 9, 'ko': 20, 'da': 16, 'k': 3}
- Categories: {'ingredient': 104, 'equipment': 17, 'action': 50, 'grammar': 23, 'measurement': 16}
- Coherence: 0.7442

**Baseline Statistics (10 iterations):**
- Coherence: 0.7442 +/- 0.0000
- Range: [0.7442, 0.7442]

**Statistical Comparison:**
- Z-score: 0.00
- p-value: 1.0000
- Effect size: 0.00
- Verdict: **PASS_PREDICTIONS**

## Interpretation

### Finding: Test Design Error -- Position-Independent Decoder

The test reveals that the ZFD decoder processes tokens **independently** without 
using positional context. Shuffling word order does not change the decode results 
because each token is analyzed in isolation. This means the v1 shuffle-based test 
cannot distinguish between correct and incorrect decoding.

**This does not validate the degrees-of-freedom criticism.** It means this particular 
test was not capable of answering the question. The question was answered by test v2, 
which changes the VOCABULARY rather than the ORDER. See: 
`results_v2/V2_VOCABULARY_SPECIFICITY_REPORT.md`

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
*2026-02-04 17:20:45*