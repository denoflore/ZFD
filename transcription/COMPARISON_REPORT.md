# EVA vs ZFD Comparison Report

**Generated:** 2026-11-21
**Scope:** 203 folios, 5194 lines

## Overview

This report documents where the ZFD transcription diverges from the
EVA (European Voynich Alphabet) transliteration system. EVA treats each glyph as a
standalone letter in an unknown alphabet. ZFD models a positional shorthand system
with operators (word-initial), gallows abbreviation marks (medial), and suffixes (word-final).

## Key Divergences

### 1. Gallows Characters

EVA treats gallows (k, t, f, p) as individual letters. ZFD expands them as cluster abbreviations:

| EVA | ZFD |
|-----|-----|
| k | st |
| t | tr |
| f | pr |
| p | pl |

### 2. Operator Detection (Word-Initial Parsing)

| EVA initial | ZFD operator |
|-------------|-------------|
| qo- | ko- |
| ch- | h- |
| sh- | š- |
| da- | da- |
| ok- | ost- |
| ot- | otr- |
| q- | k- |

### 3. Suffix Detection (Word-Final Parsing)

| EVA final | ZFD suffix |
|-----------|-----------|
| -aiiin | -ain |
| -aiin | -ain |
| -edy | -edi |
| -eey | -ei |
| -y | -i |
| -ol | -ol |
| -ar | -ar |
| -or | -or |
| -al | -al |
| -od | -od |
| -am | -am |
| -om | -om |
| -m | -m |
| -n | -n |
| -l | -l |
| -r | -r |

### 4. Bench Gallows and Ligatures

| EVA | ZFD |
|-----|-----|
| cth | htr |
| ckh | hst |
| cph | hpl |
| cfh | hpr |
| ch (any position) | h |
| sh (any position) | š |
| y (outside the suffix slot) | i |
| -aiiin (ligature, claimed before operators) | -ain |
| -aiin (ligature, claimed before operators) | -ain |

## Divergence Statistics (computed)

- **Lines with a recorded gallows divergence:** 4759 / 5194 (91.6%)
- **EVA words with a detected operator:** 21771 / 37785 (57.6%)
- **EVA words with a detected suffix:** 34212 / 37785 (90.5%)

## Hand Readings vs Compiler Output

| EVA | Hand reading | Compiler output | Match | Source of hand reading |
|-----|--------------|-----------------|-------|------------------------|
| okol | ostol | ostol | yes | Curio adversarial validation (f88r) |
| otorchety | otrorhetri | otrorhetri | yes | Curio adversarial validation (f88r) |
| okeo.r!oly | orolaly | osteo. roli | NO | Latin term reading (f102v) |
| sal | sal | sal | yes | identity |
| shol | šol | šol | yes | FINAL_CHARACTER_MAP_v1 §3.2 |
| daiin | dain | dain | yes | operator + ligature suffix |

## Conclusion

ZFD and EVA differ on most words because they model the writing system
differently (1:1 glyph-to-letter vs positional shorthand).
Measured against the hand-transcribed anchor folios, the batch compiler
reproduces 517/617 words (83.8%). That number, not the structural
grades, is the current accuracy evidence for the automated folios.

---

*Comparison report generated 2026-11-21.*
