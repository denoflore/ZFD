# ZFD Blind Decode Falsification Test v2: Vocabulary Specificity

**Test Date:** 2026-02-04
**Test Version:** v2 (Vocabulary Specificity)
**Lexicon Checksum:** 9c5e62619b00e3a3...
**Overall Verdict:** **PASS**

---

## Executive Summary

The v2 vocabulary specificity test **PASSED**. 5 of 5 folios 
produced significantly higher coherence scores on real Voynich text compared to all 
three non-Voynich baselines.

**Mean z-scores:** Synthetic EVA: 4.6, Character-shuffled: 6.5, Random Latin: 17.5

This result demonstrates that the ZFD pipeline's vocabulary mappings are **specific to 
Voynich manuscript morphology**. The decoder does not produce comparable output from 
arbitrary input matching manuscript statistics.

## Context: Why v2

Test v1.1 established that the ZFD decoder is **position-independent**. Each token is 
decoded in isolation, so shuffling word order produces identical results. That test 
measured sensitivity to word ORDER, but the decoder has no word-order sensitivity.

The actual degrees-of-freedom question is: **"Would NON-VOYNICH input produce comparable 
coherence scores through this same pipeline?"**

Test v2 answers this by running three types of non-Voynich input through the frozen pipeline:

1. **Synthetic EVA**: Random characters matching manuscript frequency distribution
2. **Character-shuffled**: Real words with letters scrambled (destroys morphology)
3. **Random Latin**: Medieval pharmaceutical vocabulary (different language entirely)

---

## Methodology

### Baseline Types

| Type | Description | What It Tests |
|------|-------------|---------------|
| Synthetic EVA | Random EVA characters, manuscript frequency distribution | Alphabet specificity |
| Character-shuffled | Real words, internal letters randomized | Morphological structure |
| Random Latin | Medieval pharmaceutical vocabulary | Language specificity |

### Test Parameters

- **Iterations per baseline type:** 100
- **Total baseline decodes:** 1500 (3 types x 5 folios x 100)
- **Significance level:** p < 0.01
- **Minimum discriminating folios:** 4 of 5

### Verdict Criteria

- **DISCRIMINATING**: Real coherence significantly exceeds ALL THREE baselines (p < 0.01 each)
- **PARTIAL**: Real exceeds some but not all baselines
- **NON-DISCRIMINATING**: Real is comparable to one or more baselines

---

## Per-Folio Results

| Folio | Real | Synth (mean±sd) | Z | CharShuf (mean±sd) | Z | Latin (mean±sd) | Z | Verdict |
|-------|------|-----------------|---|--------------------|----|-----------------|---|---------|
| f10r | 0.704 | 0.43±0.10 | 2.8 | 0.53±0.06 | 2.8 | 0.35±0.03 | 11.1 | DISCRIMINATING |
| f23v | 0.765 | 0.41±0.10 | 3.6 | 0.55±0.09 | 2.5 | 0.34±0.05 | 9.2 | DISCRIMINATING |
| f47r | 0.700 | 0.42±0.10 | 2.9 | 0.45±0.08 | 3.3 | 0.33±0.05 | 7.3 | DISCRIMINATING |
| f89r | 0.694 | 0.55±0.01 | 10.4 | 0.58±0.01 | 20.9 | 0.40±0.01 | 48.2 | DISCRIMINATING |
| f101v | 0.744 | 0.50±0.08 | 3.2 | 0.58±0.05 | 3.1 | 0.39±0.03 | 11.7 | DISCRIMINATING |


## Baseline Hierarchy

Expected hierarchy (if decoder is Voynich-specific): **Real > CharShuffle > SyntheticEVA > Latin**

| Folio | Real | CharShuffle | SyntheticEVA | Latin | Hierarchy Holds? |
|-------|------|-------------|--------------|-------|------------------|
| f10r | 0.704 | 0.534 | 0.430 | 0.351 | Yes |
| f23v | 0.765 | 0.548 | 0.415 | 0.339 | Yes |
| f47r | 0.700 | 0.447 | 0.416 | 0.330 | Yes |
| f89r | 0.694 | 0.585 | 0.549 | 0.405 | Yes |
| f101v | 0.744 | 0.577 | 0.500 | 0.390 | Yes |

*Hierarchy check: Real > CharShuffle > SyntheticEVA, and SyntheticEVA >= 0.9 * Latin*

## Known Stem Ratio Comparison

| Folio | Real Known% | Synthetic Known% | CharShuffle Known% | Latin Known% |
|-------|-------------|------------------|--------------------|--------------| 
| f10r | 41.6% | 10.8% | 17.9% | 25.2% |
| f23v | 57.8% | 10.9% | 29.9% | 24.7% |
| f47r | 39.0% | 11.0% | 17.1% | 24.9% |
| f89r | 38.3% | 10.5% | 18.3% | 24.7% |
| f101v | 52.4% | 10.9% | 24.0% | 23.6% |


## Interpretation

### Vocabulary Specificity Confirmed

The real Voynich manuscript text produces significantly higher coherence scores than:

1. **Synthetic EVA strings** - Random characters with manuscript-matching statistics
2. **Character-shuffled words** - Real words with morphological structure destroyed
3. **Medieval Latin** - Domain-relevant vocabulary from a different language

This demonstrates that the ZFD decoder's vocabulary mappings are detecting 
**specific morphological patterns** in the Voynich manuscript, not just matching 
any text that uses similar characters or word lengths.

The hierarchy (Real > CharShuffle > Synthetic > Latin) shows that partial 
character preservation (char-shuffle) retains some structure, but the full 
morphological sequences in real Voynich text are required for maximum coherence.

## Relationship to v1.1 Findings

**v1.1 finding:** Decoder is position-independent (shuffling word order has no effect)

**v2 finding:** Decoder is vocabulary-specific (changing the actual words has significant effect)

These findings are **complementary, not contradictory**:

- The decoder processes each word independently (v1.1 confirmed)
- But the decoder's mappings are specific to Voynich morphological patterns (v2 tested)
- Position-independence is expected for pharmaceutical shorthand where each abbreviation 
  decodes to its meaning regardless of location
- Vocabulary-specificity demonstrates the decoder isn't just matching any EVA-like text

---

## Key Statement

> "Test v2 asks whether the ZFD pipeline is specific to Voynich manuscript text or 
> flexible enough to produce comparable output from any input. Three non-Voynich 
> baselines were tested: synthetic EVA strings matching manuscript statistics, 
> character-shuffled Voynich words destroying morphological patterns, and random 
> medieval Latin pharmaceutical vocabulary. If real Voynich text produces significantly 
> higher coherence than all three baselines through the same frozen pipeline, the 
> decoder's vocabulary mappings are detecting structure specific to the manuscript. 
> If any baseline produces comparable coherence, the degrees-of-freedom criticism is 
> supported for that axis of comparison."

---

## Reproducibility

```bash
# Clone the repository
git clone https://github.com/denoflore/ZFD.git
cd ZFD

# Run full v2 test (1500 baseline decodes)
python validation/blind_decode_test/run_test_v2.py

# Quick mode (150 baseline decodes)
python validation/blind_decode_test/run_test_v2.py --quick

# Single folio
python validation/blind_decode_test/run_test_v2.py --folio f10r
```

All random generation uses fixed seeds for deterministic reproducibility.

---

## Lexicon Integrity

The lexicon file was checksummed at test start and verified at test end.

**SHA-256:** `9c5e62619b00e3a3a357478404506ad729651146faf892282a891bedc4be79b0`

**Status:** Verified (no modifications during test)

---

*Report generated by ZFD Blind Decode Falsification Test v2*
*2026-02-04 17:37:50*