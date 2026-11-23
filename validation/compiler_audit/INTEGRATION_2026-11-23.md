# ZFD integration audit, 23 November 2026

## Scope

This integration starts from the November compiler audit commit
`e1ec81081b9f41ccaa04001f646f7543e74ebb01` in [PR #8](https://github.com/denoflore/ZFD/pull/8),
whose parent is `3f030a9293b8db15dc2c7b0d0e7c703e71711f62`.
It combines those transcription fixes with the recipe-output gate, pharmacy
concordance, report-denominator corrections and shared-tokenizer correction.
The repository changes were inspected directly. No unavailable Claude-chat
transcript is treated as an additional verified source.

## Three processing paths

| Path | Inputs and measurement | Current result |
|---|---|---|
| `transcription/scripts/batch_transcribe.py` | H-transcription EVA compiled to ZFD orthography; compared with five retained project hand anchors | 621/735 words agree after `sh` to `š` normalization: **84.4897959%** |
| `06_Pipelines/zfd_decoder_v2.py::ZFDDecoder` | Canonical raw-EVA/LSI union; unified lexicon v3; rounded score ≥0.30 | 46,578/48,379: **96.2773104%** combined full/partial parser coverage |
| Same recipe decoder, preferred-LSI extraction | Existing selector chooses one preferred transcriber for each line | 35,568/36,959: **96.2363700%**, across 226 identifiers |
| `zfd_decoder/src/pipeline.py::ZFDPipeline` | CSV lexicons with explicitly controlled compound decomposition; five-folio blind-decode comparison | Frozen lexicon **5/5** and shipping configuration **4/5** folios discriminate against all three tested baselines |

These measurements are not interchangeable and none is a calibrated
translation-accuracy percentage. The hand anchors also informed the
transcription rules, so their agreement is not an independent held-out test.

## Transcription corrections and coverage

The 21 November fixes cover bench-gallows expansion, filler handling,
ligature/suffix precedence, medial units, non-final `y`, word breaks,
metadata and corpus regeneration. The integration fixes two remaining
reporting bugs:

- Commas were omitted from anchor tokenization, excluding 13 rows. All **129
  anchor rows / 735 tokens** now align, with **621 agreements and 114
  disagreements**, and zero skipped rows. The earlier 83.8% figure used an
  incomplete 617-token denominator.
- Operator/suffix counts now follow the compiler's ligature-first parsing
  order: **20,894 operator detections** and **34,204 suffix detections** in
  **37,785 EVA tokens**.

The corpus has **203 packages: 196 automated, five hand anchors and two
retained stubs**. There are **5,194 JSONL rows**, including the empty f85v
placeholder and fragmentary f116v row, and **37,785 tokens** in each EVA/ZFD
representation. All 201 source page IDs are represented, but the retained
anchors do not establish complete source-text coverage. The f102v anchor has
**38 rows / 180 EVA tokens**, against **62 selected source lines / 311 tokens**.
The source selector supplies 5,215 lines overall.

Every automated package reproduces in its four generated files after
normalizing the generation date. The report corrections leave all folio
packages and `FULL_CORPUS.jsonl` unchanged. The latter's SHA-256 is
`bad16667165237add812481525d3e0c130692a26d15035aef534bb1062e009bc`.
The three reports are generated from the corrected reporting code.

[Transcription audit](../../transcription/AUDIT_2026-11.md)
| [Statistics and anchor coverage](../../transcription/STATISTICS.md)

## Clean-input validation rerun

The shared CSV-pipeline tokenizer now excludes file headings, comments and
inline IVTFF annotations. Drawing interruptions and commas separate words;
`!` filler contributes no glyph. The null generators consume the same
normalized words, and every null sample must have the real input's token
count. Original source-line positions remain in token IDs.

The full v3 run uses **30 iterations per baseline**, two configurations,
five folios and three baselines. The input counts are **92, 89, 79, 387 and
213** tokens. Both configurations retain the ordering real > character-shuffled
> synthetic EVA > random Latin. In the shipping configuration, f23v versus
character-shuffling has **z = 1.53**, empirical **p = 0.0323**. The declared
rule requires both z ≥1.645 and p <0.05, so f23v is **WEAK** and the shipping
result is **4/5**, superseding the earlier 5/5 headline.

The current report is generated from the same run as the JSON receipt, which
records code/data/source hashes and seed schedule. 'Frozen' refers to the
February lexicon with compound decomposition disabled; both configurations
use the current audited code.

The noise-robustness rerun reproduces **NON-DISCRIMINATING** because the simple
null decoder also has flat coverage and declining stem identity. The layer
perturbation rerun gives an operator diagonal ratio of **3.03 on real text
versus 12.92 on shuffled glyphs**. None of the three layers supplies manuscript
evidence under the script's control comparison. Earlier positive statements
are explicitly superseded in README and CHANGELOG.

[Blind-decode report](../blind_decode_test/results_v3/V3_DUAL_CONFIG_REPORT.md)
| [Robustness receipt](../transcription_robustness/robustness_results.json)
| [Layer receipt](../transcription_robustness/layer_stratified_results.json)

## Recipe gate and pharmacy concordance

The recipe decoder and its lexicon remain unchanged. All **244 committed
recipe files and their summary** reproduce. The strengthened `--check` gate
now detects stale/missing outputs, unexpected recipe files and changed
summaries, in addition to deterministic regeneration. The recipe source union
retains overlapping whole-page/panel versions and some parallel readings;
the audit separately reports the preferred-LSI comparison.

The README's pharmacy register lists the **18 named preparations or product
categories in the cited sources**, with source dates and disclosed ingredients.
This is not a verified live stock list or 18 proven manuscript recipe matches.
Current rose/rosewater stem candidates occur on **f9v, f105v and f115v**.
The old f13v rose-cream assignment is not emitted by the current recipe decoder.
The sources support changes to recipes over time but do not establish dates
or causes for specific ingredient substitutions. The unsupported bone-oil to
beeswax and post-1667 storax claims were removed.

[Recipe audit and source accounting](COMPILER_AUDIT_2026-11-23.md)
| [Recipe measurement receipt](RESULTS_2026-11-23.json)
| [Pharmacy register](../../README.md#the-ingredient-match)
| [Comment continuation](CONTINUATION.md)

## Verification

The full pytest run passes **78 tests**. The test and committed-output gate receipts are stored as
[TEST_RECEIPT.txt](TEST_RECEIPT.txt) and [GATE_RECEIPT.txt](GATE_RECEIPT.txt).
The suite includes regressions for comma alignment, compiler-order counts,
raw metadata/tag removal, real/null word counts and stale recipe outputs.
The structural lexicon audit reports zero failures and 21 warnings; these
are lexicon-structure checks, not independent validation of the meanings.

```bash
python -m pytest -q
python 06_Pipelines/lexicon_audit.py
python 06_Pipelines/regenerate_corpus.py --check
python validation/compiler_audit/audit_current_corpus.py --output /tmp/zfd-audit.json
python transcription/scripts/generate_reports.py
python validation/blind_decode_test/run_test_v3.py
python validation/transcription_robustness/run_robustness.py
python validation/transcription_robustness/run_layer_stratified.py
```

## Branch review

Before pruning, branch ancestry and unique file changes were checked against
main and PR #8. The blind-decode-test and complete-manuscript-coverage branches
were already ancestors of main. The compiler-audit branch is prunable only
after its final head is incorporated. Five branches contain unique work and
must be retained: LGN eye, edition architecture, paleographic transcription,
folio images/Croatian, and image-native decipherment.
