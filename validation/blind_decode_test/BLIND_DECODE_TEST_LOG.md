# Blind Decode Falsification Test: Complete Log

**Project:** ZFD (Zuger Folio Decipherment)
**Test initiated:** 2026-02-04
**Author:** Chris Zuger
**Purpose:** Answer the "degrees of freedom" criticism with automated, reproducible evidence

---

## Context

A critic raised the following challenge:

> "The system has so many degrees of freedom (operators, layers, abbreviations, phonetic adjustments) that it will always produce something Croatian-compatible, regardless of the input."

They argued that metrics like 96.8% token coverage and 100% phonotactic validity demonstrate only that the generator works, not that the decipherment is correct.

This is a valid concern. The response was not argument but execution: build a test, run it, publish whatever comes out.

---

## Test v1.0: Initial Run

**Commit:** 9a8463e (2026-02-04 17:13 UTC)
**Branch:** claude/blind-decode-test-mZ08a
**Verdict:** FAIL (0/5 folios passing)

### What happened

The test infrastructure was built correctly: checksumming, shuffled baseline generation, statistical comparison engine, report generator all functioned as specified. However, the test produced nonsensical results:

- f10r: 15 tokens (expected ~86)
- f23v through f101v: 0 tokens each
- All z-scores: 0.00, all p-values: 1.0000

### Root cause: Tokenizer bug

The EVA transcription files use **dots** as word separators:

```
pchocthy.shor.octhody.chorchy.pchodol.chopchal.ypch.kom
```

The tokenizer in `zfd_decoder/src/tokenizer.py` was splitting on **spaces only**:

```python
words = line.strip().split()
```

Each line in the EVA files is a single dot-separated string with no spaces, so the tokenizer treated entire lines as single tokens. This meant:

- f10r had 12 text lines, producing only 15 "tokens" (some lines with inline markup)
- Four folios produced 0 tokens due to parsing failures on their specific formatting
- Shuffling had no effect because there were no discrete words to shuffle

**This was a pipeline bug, not a test design flaw.** The test correctly reported what the pipeline produced. The pipeline was not processing the input format correctly.

### Lesson

The EVA file format should have been validated before the test was built. The instruction spec said "Read pipeline.py, tokenizer.py" but the disconnect between the tokenizer's space-splitting and the EVA format's dot-separation was not caught during spec design.

---

## Test v1.1: Tokenizer Fix and Re-run

**Commit:** 437a86c (2026-02-04 17:21 UTC)
**Merged to main:** 571dd6c
**Verdict:** FAIL (0/5 folios passing)

### Fix applied

Two files were patched:

1. **`zfd_decoder/src/tokenizer.py`**: Changed `words = line.strip().split()` to normalize dots to spaces first:
   ```python
   normalized = line.strip().replace('.', ' ')
   words = normalized.split()
   ```

2. **`validation/blind_decode_test/utils.py`**: Updated `shuffle_eva_text()` with the same dot-awareness so the shuffle function operates on actual EVA words.

### Results after fix

Token counts are now correct:

| Folio | Tokens | Known Stems | Known Ratio | Coherence |
|-------|--------|-------------|-------------|-----------|
| f10r  | 89     | 37          | 41.6%       | 0.7043    |
| f23v  | 83     | 48          | 57.8%       | 0.7655    |
| f47r  | 82     | 32          | 39.0%       | 0.7001    |
| f89r  | 387    | 148         | 38.3%       | 0.6938    |
| f101v | 208    | 109         | 52.4%       | 0.7442    |

The pipeline is processing real EVA words. Coherence scores range from 0.69 to 0.77. Known stem ratios range from 38% to 58%. All five folios show rich operator distributions (6-7 distinct operators each) and diverse category assignments.

### But: Position-independent decoder

Every shuffled baseline produced **identical** coherence scores to the real decode:

| Folio | Real Coherence | Shuffled Mean | Std Dev | Z-score |
|-------|----------------|---------------|---------|---------|
| f10r  | 0.7043         | 0.7043        | 0.0000  | 0.00    |
| f23v  | 0.7655         | 0.7655        | 0.0000  | 0.00    |
| f47r  | 0.7001         | 0.7001        | 0.0000  | 0.00    |
| f89r  | 0.6938         | 0.6938        | 0.0000  | 0.00    |
| f101v | 0.7442         | 0.7442        | 0.0000  | 0.00    |

### Why this happened

The ZFD pipeline is a **bag-of-words decoder**. Each token is processed independently: EVA word in, operator/stem/suffix analysis out. The pipeline never examines word order, adjacent tokens, or positional context. This is by design, because the hypothesis is that Voynich text represents pharmaceutical shorthand where each word abbreviates a standalone term or instruction.

Shuffling word order within a folio preserves the exact same set of words. Since the decoder processes each word identically regardless of position, shuffled text produces identical results. The test measured sensitivity to **word order**, but the decoder has no word-order sensitivity to measure.

This is not evidence that ZFD is wrong. It is evidence that **v1's null hypothesis tested the wrong axis**.

### What the test DID establish

1. The pipeline processes all five folios with meaningful token counts (82-387 per folio)
2. Known stem ratios of 38-58% are consistent but not trivially high
3. Operator diversity is rich (6-7 distinct operators per folio)
4. Category distribution is diverse (5-7 categories per folio)
5. The lexicon remained frozen throughout (SHA-256 verified)
6. The test infrastructure is sound and reproducible

### What the test did NOT establish

Whether the decoder's vocabulary mappings are specific to Voynich text or flexible enough to produce similar results from any input. The shuffle preserved Voynich vocabulary and only rearranged positions. A position-independent decoder will always score identically on shuffled vs. original when the vocabulary is preserved.

---

## Why Test v2 Is Required

The degrees-of-freedom criticism asks: "Would ANY input produce Croatian-compatible output through this pipeline?" The v1/v1.1 test shuffled word order but kept the same Voynich words. That cannot answer the question.

Test v2 must change the **vocabulary**, not the **order**. Three approaches:

1. **Synthetic EVA strings**: Generate words from random EVA character combinations matching the manuscript's character frequency distribution but producing words that never appear in the real manuscript. If these score comparably, the decoder's mappings are too flexible.

2. **Non-Voynich text**: Run text from a known source (random medieval Latin, synthetic gibberish, or another manuscript's EVA transcription) through the same frozen pipeline. If it produces coherence scores in the same range (0.69-0.77), the mappings match anything.

3. **Intra-word character shuffle**: Shuffle the characters WITHIN each word while preserving word length and line structure. This destroys morphological structure (operator-stem-suffix patterns) while keeping the same character distribution. If the decoder still produces high coherence, its pattern matching is too loose.

The v1 test was honest work that exposed both a real bug and a real design limitation. v2 will test the actual claim.

---

## File inventory

All test v1.1 results are in `validation/blind_decode_test/results/`:

- `test_metadata.json`: Config, timestamps, checksums
- `real_decode_f10r.json` through `real_decode_f101v.json`: Full decode per folio
- `baseline_f10r.json` through `baseline_f89r.json`: 10 shuffled iterations per folio
- `comparison_results.json`: Statistical comparison
- `BLIND_DECODE_REPORT.md`: Human-readable report

Test code is in `validation/blind_decode_test/`:

- `run_test.py`: Main entry point
- `decoder.py`: Pipeline wrapper
- `baseline.py`: Shuffle generator
- `compare.py`: Statistical engine
- `report.py`: Report generator
- `config.py`: Preregistered thresholds
- `utils.py`: Shared utilities

---

*Documenting failures is not weakness. It is how science works.*
