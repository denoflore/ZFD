# V3 Clean-Input Dual-Configuration Audit

**Run date:** 2026-11-23T11:17:38.694319
**Iterations per baseline:** 30

## Scope and correction

This rerun supersedes the June 2026 headline numbers. The shared EVA
tokenizer now excludes file headings, comments and IVTFF annotations;
drawing interruptions and commas remain word breaks. Null generators
use the same word boundaries and assert equal real/null token counts.

Both configurations use the current audited code. 'Frozen' identifies
the February lexicon and disabled compound decomposition, not a frozen
historical executable. Lexicon hashes are asserted; code, other data
hashes, source hashes and deterministic seeds are recorded in the JSON.

A folio discriminates only if every baseline has z >= 1.645 AND
empirical one-tailed p < 0.05. The empirical estimator is
`p = (count(null_score >= real_score) + 1) / (iterations + 1)`.
These are the existing per-comparison criteria,
without a multiple-comparison correction. Coherence is the pipeline's
scoring function, not a measured translation-accuracy percentage.

## frozen_feb2026

Frozen February 2026 v1 lexicon, no compound decomposition, using the current audited tokenizer and code.

**Discriminating folios:** 5/5
**Ordering hierarchy holds on every folio:** True

| Folio | Tokens | Real coherence | Shuffled mean (z; p) | Synthetic mean (z; p) | Latin mean (z; p) | Verdict |
|---|---:|---:|---|---|---|---|
| f10r | 92 | 0.6891 | 0.4858 (2.75; 0.0323) | 0.3898 (3.71; 0.0323) | 0.3473 (5.88; 0.0323) | DISCRIMINATING |
| f23v | 89 | 0.7608 | 0.5668 (2.55; 0.0323) | 0.3865 (4.47; 0.0323) | 0.3439 (7.39; 0.0323) | DISCRIMINATING |
| f47r | 79 | 0.7041 | 0.4082 (3.34; 0.0323) | 0.3715 (3.98; 0.0323) | 0.3401 (6.58; 0.0323) | DISCRIMINATING |
| f89r | 387 | 0.6906 | 0.5838 (19.93; 0.0323) | 0.5398 (6.00; 0.0323) | 0.4013 (37.97; 0.0323) | DISCRIMINATING |
| f101v | 213 | 0.7370 | 0.5989 (6.03; 0.0323) | 0.5060 (4.89; 0.0323) | 0.3928 (10.83; 0.0323) | DISCRIMINATING |


## current_shipping

Default shipping configuration (auto-selected by ZFDPipeline): lexicon_v2.csv + compound decomposer.

**Discriminating folios:** 4/5
**Ordering hierarchy holds on every folio:** True

| Folio | Tokens | Real coherence | Shuffled mean (z; p) | Synthetic mean (z; p) | Latin mean (z; p) | Verdict |
|---|---:|---:|---|---|---|---|
| f10r | 92 | 0.9020 | 0.7732 (2.00; 0.0323) | 0.7356 (3.17; 0.0323) | 0.5688 (10.86; 0.0323) | DISCRIMINATING |
| f23v | 89 | 0.9006 | 0.8262 (1.53; 0.0323) | 0.7338 (3.01; 0.0323) | 0.5623 (9.09; 0.0323) | WEAK |
| f47r | 79 | 0.9026 | 0.7687 (2.13; 0.0323) | 0.7267 (3.12; 0.0323) | 0.5621 (8.80; 0.0323) | DISCRIMINATING |
| f89r | 387 | 0.9080 | 0.8532 (20.20; 0.0323) | 0.8395 (7.79; 0.0323) | 0.5876 (32.06; 0.0323) | DISCRIMINATING |
| f101v | 213 | 0.9044 | 0.8531 (2.56; 0.0323) | 0.8120 (2.21; 0.0323) | 0.5867 (20.89; 0.0323) | DISCRIMINATING |

- **Threshold not met:** f23v / char_shuffled, z = 1.53, p = 0.0323.

## Interpretation

The hierarchy compares mean scores: real > character-shuffled >
synthetic EVA > random Latin. A preserved hierarchy does not by
itself mean every comparison meets the declared threshold. High
absolute coverage on null inputs also limits what coverage can show.

These results concern the CSV-lexicon ZFDPipeline. They are separate
from recipe-decoder coverage and transcription-anchor agreement.

## Reproduce

```bash
python validation/blind_decode_test/run_test_v3.py
```

The command regenerates this report and
[v3_dual_config_results.json](v3_dual_config_results.json) together.
The optional `--quick` run uses ten iterations and cannot meet p <
0.05 with the empirical estimator; it is a smoke run, not the full test.
