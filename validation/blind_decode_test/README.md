# ZFD Blind Decode Falsification Test

## Purpose

This test addresses the "degrees of freedom" criticism: that the ZFD system has so many
adjustable parameters (operators, layers, abbreviations, phonetic adjustments) that it
will produce Croatian-compatible output regardless of input.

The response is not argument. It is execution.

## Methodology

1. **Freeze the lexicon**: The lexicon file is checksummed (SHA-256) at test start and
   verified at test end. No modifications are permitted during the test run.

2. **Decode real folios**: Five preregistered test folios are decoded through the
   frozen pipeline:
   - f10r (Herbal A - plant preparation)
   - f23v (Herbal A - plant processing)
   - f47r (Herbal B - herbal recipe)
   - f89r (Pharmaceutical - recipe with vessels)
   - f101v (Recipes/Stars - dosage grid)

3. **Generate shuffled baselines**: For each folio, 100 shuffled versions are created
   using deterministic random seeds (42-141). Shuffling preserves word count and line
   structure but randomizes word positions.

4. **Decode shuffled versions**: Each shuffled version is processed through the SAME
   pipeline with the SAME frozen lexicon.

5. **Statistical comparison**: Real decode results are compared against the shuffled
   distribution using z-scores and empirical p-values.

## Interpretation

- **If real >> shuffled**: The decoder is detecting structure that exists in the
  manuscript. The "degrees of freedom" cannot explain the results.

- **If real == shuffled**: The decoder produces similar output regardless of input
  structure. The criticism is valid.

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

Every run with the same code produces identical results:
- Shuffling uses fixed seeds (42 + iteration_number)
- Pipeline parameters are frozen
- Lexicon is checksummed and verified

Any researcher can clone this repository and run the test to verify results.
