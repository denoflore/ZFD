# EVA vs ZFD Paleographic Comparison Report

**Generated:** 2026-02-07
**Scope:** Full Voynich Manuscript corpus (197 folios)

## Overview

This report documents where the ZFD paleographic transcription diverges from the
EVA (European Voynich Alphabet) transliteration system. EVA treats each glyph as a
standalone letter in an unknown alphabet. ZFD recognizes a positional shorthand system
with operators (word-initial), gallows abbreviation marks (medial), and suffixes (word-final).

## Key Divergences

### 1. Gallows Characters (Fundamental Disagreement)

EVA treats gallows (k, t, f, p) as individual letters. ZFD expands them as cluster abbreviations:

| EVA | ZFD | Meaning | Impact |
|-----|-----|---------|--------|
| k | st | bone/firm cluster | Every 'k' in EVA becomes 'st' in ZFD |
| t | tr | treatment cluster | Every 't' in EVA becomes 'tr' in ZFD |
| f | pr | pour/heat cluster | Every 'f' in EVA becomes 'pr' in ZFD |
| p | pl | pour/liquid cluster | Every 'p' in EVA becomes 'pl' in ZFD |

This is the single largest source of divergence. Thousands of words are affected.

### 2. Operator Detection (Word-Initial Parsing)

EVA treats word-initial sequences as simple letter combinations. ZFD detects operators:

| EVA initial | ZFD operator | Meaning |
|-------------|-------------|---------|
| qo- | ko- | which/determiner |
| ch- | h- | cook/heat |
| sh- | s- | with/soak |
| da- | da- | give/administer |
| ok- | ost- | bone/vessel |
| ot- | otr- | treat/process |

### 3. Suffix Detection (Word-Final Parsing)

EVA treats word-final sequences as individual characters. ZFD detects suffixes:

| EVA final | ZFD suffix | Function |
|-----------|-----------|----------|
| -aiin | -ain | Substance noun marker |
| -eey | -ei | Instance/adjective |
| -y | -i | Adjective marker |
| -ol | -ol | Oil/liquid suffix |
| -ar | -ar | Water/agent suffix |
| -am | -am | Substance/mass suffix |

### 4. Bench Gallows (Compound Expansions)

EVA treats bench gallows as two-character sequences. ZFD expands them differently:

| EVA | ZFD | Meaning |
|-----|-----|---------|
| cth | htr | cook-treat |
| ckh | hst | cook-bone |
| cph | hpl | cook-pour |
| cfh | hpr | cook-heat |

### 5. 'aiin' as Ligature Unit

EVA: four separate characters (a, i, i, n)
ZFD: single ligature unit 'ain' representing a substance/noun suffix
Evidence: zero-pen-lift execution confirmed in ductus analysis

## Divergence Statistics

- **Lines with documented divergences:** 4019 / 4944
- **Divergence rate:** 81.3%
- **Primary divergence type:** Gallows expansion (present in virtually every line)
- **Secondary divergence:** Operator detection (most word-initial sequences)
- **Tertiary divergence:** Suffix detection (most word-final sequences)

## Validated Readings Where ZFD and EVA Disagree

| EVA Reading | ZFD Reading | Meaning | Validation |
|-------------|-------------|---------|------------|
| okol | ostol | bone oil | Curio adversarial validation (f88r) |
| otorchety | otrorhetri | treated heated fluid | Curio adversarial validation (f88r) |
| okeo.r!oly | orolaly | orally (Latin) | Confirmed Latin pharmaceutical term (f102v) |
| sal | sal | salt | Identity (no divergence) |
| daiin | dain | substance/given | Operator + suffix vs individual characters |

## Conclusion

The ZFD transcription and EVA transliteration disagree on virtually every word
in the manuscript, because they are based on fundamentally different models of
the writing system. EVA assumes a 1:1 character-to-letter cipher. ZFD recognizes
a positional shorthand system with three layers (operators, gallows abbreviations,
suffixes). Where validation evidence exists (Curio adversarial testing, Latin
pharmaceutical terms, spatial correlation), the ZFD readings are consistently
supported.

---

*Comparison report generated 2026-02-07.*
