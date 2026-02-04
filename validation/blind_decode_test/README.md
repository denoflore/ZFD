# ZFD Blind Decode Falsification Test

## Current Status: v1.1 Complete, v2 In Progress

Test v1.1 established that the ZFD decoder is position-independent (bag-of-words). Shuffling word order within folios produces identical results because each token is decoded in isolation. This is consistent with the pharmaceutical shorthand hypothesis but means the word-order shuffle cannot distinguish a correct decoder from a flexible one.

Test v2 will test whether non-Voynich input produces comparable results through the same frozen pipeline. See [BLIND_DECODE_TEST_LOG.md](BLIND_DECODE_TEST_LOG.md) for the complete history.

---

## Purpose

This test addresses the "degrees of freedom" criticism: that the ZFD system has so many adjustable parameters (operators, layers, abbreviations, phonetic adjustments) that it will produce Croatian-compatible output regardless of input.

The response is not argument. It is execution.

## Test v1.1 Results (2026-02-04)

| Folio | Tokens | Known Ratio | Coherence | vs. Shuffled |
|-------|--------|-------------|-----------|--------------|
| f10r  | 89     | 41.6%       | 0.7043    | Identical    |
| f23v  | 83     | 57.8%       | 0.7655    | Identical    |
| f47r  | 82     | 39.0%       | 0.7001    | Identical    |
| f89r  | 387    | 38.3%       | 0.6938    | Identical    |
| f101v | 208    | 52.4%       | 0.7442    | Identical    |

**Verdict:** FAIL on position-sensitivity (expected for bag-of-words decoder).
**Finding:** Test measured the wrong axis. Word order is irrelevant to a token-independent decoder.

## Test History

1. **v1.0** (2026-02-04 17:12 UTC): Tokenizer bug. EVA files use dots as word separators, tokenizer split on spaces only. 4/5 folios produced 0 tokens. Results meaningless.
2. **v1.1** (2026-02-04 17:20 UTC): Tokenizer fixed. All 5 folios produce correct token counts. Shuffled baselines identical to real decode due to position-independent processing.
3. **v2** (pending): Will test vocabulary specificity, not word order. Synthetic EVA, non-Voynich text, and intra-word character shuffling.

Full details: [BLIND_DECODE_TEST_LOG.md](BLIND_DECODE_TEST_LOG.md)

## Running the Test

```bash
# Full test (100 shuffle iterations per folio)
python run_test.py

# Quick test (10 shuffle iterations, for validation)
python run_test.py --quick

# Single folio test
python run_test.py --folio f10r
```

## Output Files

Results are saved to `results/`:

- `test_metadata.json` - Test configuration, timestamps, checksums
- `real_decode_<folio>.json` - Full decode output for each folio
- `baseline_<folio>.json` - All shuffled baseline results per folio
- `comparison_results.json` - Statistical comparison and verdicts
- `BLIND_DECODE_REPORT.md` - Human-readable final report
- `BLIND_DECODE_TEST_LOG.md` - Complete test history and rationale

## Pass/Fail Criteria (Preregistered)

- **PASS**: >= 4 folios have coherence >= 0.70 AND p < 0.01 vs shuffled baseline
- **PARTIAL**: 2-3 folios pass
- **FAIL**: 0-1 folios pass

## Key Statement

> "If the shuffled baseline produces coherence scores statistically indistinguishable
> from the real decode, this test has failed and the degrees-of-freedom criticism is
> valid. If the real decode produces significantly higher coherence than shuffled input
> through the same pipeline, the decoder is detecting structure that exists in the
> manuscript, not generating it from flexible parameters."

## Reproducibility

Every run with the same code produces identical results. Shuffling uses fixed seeds (42 + iteration_number). Pipeline parameters are frozen. Lexicon is checksummed and verified.
