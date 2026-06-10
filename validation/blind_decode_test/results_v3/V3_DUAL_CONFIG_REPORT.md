# V3 Dual-Configuration Audit Report

**Date:** June 9, 2026
**Status:** PASSED under both configurations (5/5 folios discriminating in each)

## What happened

A fresh-clone audit of the v2 vocabulary specificity test could not reproduce
the published numbers (README table: real ≈ 0.70 coherence). Direct decodes of
the same folios returned ≈ 0.90. Root-causing the discrepancy surfaced a
configuration-drift failure:

1. **The published v2 test (Feb 4, 2026) ran against the frozen `lexicon.csv`**
   (SHA-256 `9c5e62…`, which is the hash pinned in the v2 results) **with no
   compound decomposition.**
2. **Two post-publication changes silently altered the default config:**
   `ZFDPipeline` auto-prefers `lexicon_v2.csv` whenever it exists, and the
   `CompoundDecomposer` auto-enables whenever `unified_lexicon_v2.json` exists.
   Both files were added after the freeze.
3. Result: no fresh clone could run the configuration the published numbers
   came from, and the discrimination property had never been re-verified under
   the shipping configuration.

Verification was bidirectional: forcing `lexicon.csv` + disabling the compound
decomposer reproduces the published f10r numbers within 1%
(known_ratio 0.427 vs published 0.4157; coherence 0.7011 vs published 0.7043).

## The fix

`run_test_v3.py` makes this class of failure structurally impossible:

- Every configuration is **explicit** (lexicon file + compound flag).
- The lexicon **SHA-256 is asserted at load time**. A mismatch refuses to run.
- The **full configuration is stamped** into every results record.
- **Both configurations run side by side** against identical baseline
  generators with z-scores and empirical p-values (30 iterations/baseline).

## Results (June 9, 2026)

### Frozen configuration (reproduces Feb 2026)

| Folio | Real coh | Shuffled (z) | Synthetic (z) | Latin (z) | Verdict |
|-------|----------|--------------|---------------|-----------|---------|
| f10r  | 0.701 | 0.511 (2.9) | 0.388 (3.8) | 0.345 (6.4) | DISCRIMINATING |
| f23v  | 0.778 | 0.542 (2.7) | 0.375 (4.8) | 0.343 (7.9) | DISCRIMINATING |
| f47r  | 0.707 | 0.411 (3.4) | 0.375 (4.0) | 0.342 (6.6) | DISCRIMINATING |
| f89r  | 0.696 | 0.587 (16.9) | 0.540 (6.2) | 0.401 (37.3) | DISCRIMINATING |
| f101v | 0.758 | 0.601 (6.2) | 0.501 (5.0) | 0.390 (10.5) | DISCRIMINATING |

### Current shipping configuration (lexicon_v2 + compound decomposer)

| Folio | Real coh | Shuffled (z) | Synthetic (z) | Latin (z) | Verdict |
|-------|----------|--------------|---------------|-----------|---------|
| f10r  | 0.906 | 0.784 (2.3) | 0.730 (3.2) | 0.562 (9.3) | DISCRIMINATING |
| f23v  | 0.906 | 0.787 (1.9) | 0.724 (3.2) | 0.562 (9.0) | DISCRIMINATING |
| f47r  | 0.904 | 0.765 (2.2) | 0.724 (3.2) | 0.562 (8.9) | DISCRIMINATING |
| f89r  | 0.906 | 0.850 (15.5) | 0.838 (7.6) | 0.587 (33.3) | DISCRIMINATING |
| f101v | 0.901 | 0.851 (3.0) | 0.804 (2.4) | 0.583 (17.3) | DISCRIMINATING |

Hierarchy (real > char-shuffled > synthetic EVA > random Latin) holds on all
five folios under both configurations.

## Honest interpretation

- **Absolute coverage is not evidence.** Under the current configuration,
  character-shuffled gibberish reaches ~94% coverage and synthetic EVA ~91%.
  The headline 92.1% morphological coverage figure must therefore be read
  against these nulls: the evidential weight lives in the real-vs-null
  **deltas**, their significance, and the preserved ordering hierarchy, plus
  the external provenance locks (V27 / Ljekarna) that no lexicon flexibility
  can fit.
- **Discrimination survived the permissive configuration**, with smaller
  effect sizes than the frozen configuration. The weakest cell is f23v vs
  char-shuffled (z = 1.9, still significant at one-tailed 0.05).
- **Recommendation carried forward:** lexicon growth must be accompanied by
  null-baseline tracking. Any future lexicon revision re-runs v3 and reports
  both configurations. A specificity budget (maximum allowed null coverage)
  should gate compound-decomposer scoring changes.

## Reproduce

```
python validation/blind_decode_test/run_test_v3.py          # full, 30 iters
python validation/blind_decode_test/run_test_v3.py --quick  # 10 iters
```

Raw output: `results_v3/v3_dual_config_results.json` (config-stamped).
