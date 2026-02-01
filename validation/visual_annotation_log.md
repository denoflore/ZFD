# Visual Annotation Log

**Methodology:** Embodied Visual Analysis (Phase 2)
**Annotator:** Claude Code
**Date Started:** 2026-02-01

---

## Folio f1r

**Annotation Date:** 2026-02-01
**Image Source:** 03_Analysis_Data/Visuals/voynich_f1r.jpg (local)
**Overall Confidence:** VISUAL_MEDIUM

### Illustrator Intent Analysis

As a 15th century herbal illustrator, I am depicting a **simple herbaceous plant with prominent lobed leaves**. The visual emphasis is entirely on the LEAF structure - multiple green, rounded/lobed leaves spreading from central brown stems.

**What I'm NOT showing:**
- No root system visible (the plant starts at mid-stem level)
- No flowers (top of plant shows more leaves, not blooms)
- No seeds or fruits

**Pedagogical intent:** This appears to be a leaf-focused remedy. The reader needs to identify the LEAF shape and arrangement, not roots or flowers.

### Layout Analysis

The page has **four paragraphs** of text with the plant illustration **centered** in the page:

```
┌─────────────────────────────────┐
│  Paragraph 1 (lines 1-4)        │  ← Above plant
│  [header/introduction]          │
├─────────────────────────────────┤
│  Para 2      ████████████       │  ← Decorative initial + text
│  (lines 5-7) ████PLANT████      │  ← Adjacent to upper leaves
│              ████████████       │
│  Para 3      ████████████       │  ← Decorative initial + main text
│  (lines 8-20)████ILLUST████     │  ← Wraps around left side
│              ████████████       │
│              ██████             │  ← Lower stems
├─────────────────────────────────┤
│  Paragraph 4 (lines 23-27)      │  ← Below plant (no root shown)
│  [continuation/closing]         │
└─────────────────────────────────┘
```

### Plant Part Identification

| Part | Present? | Visual Description | Image Location | Confidence |
|------|----------|-------------------|----------------|------------|
| **Root** | NO | Not depicted - plant starts at stem level | N/A | N/A |
| **Stalk** | YES | Brown/gray central stems connecting leaves | Center, 30-60% height | MEDIUM |
| **Leaf** | YES | Multiple green lobed/rounded leaves, prominent | Center, 40-80% height | HIGH |
| **Flower** | NO | Not depicted | N/A | N/A |
| **Seed** | NO | Not depicted | N/A | N/A |

### Line-to-Part Mapping

Based on visual adjacency:

| Line Range | Adjacent To | Part Assigned | Confidence | Notes |
|------------|-------------|---------------|------------|-------|
| 1-4 | Above plant | GENERAL (not plant-specific) | VISUAL_LOW | Header paragraph, above illustration |
| 5-7 | Upper left of plant | LEAF | VISUAL_MEDIUM | Adjacent to upper leaf cluster |
| 8-12 | Middle-left of plant | LEAF/STALK | VISUAL_MEDIUM | Adjacent to leaf-stem junction |
| 13-16 | Lower-middle left | STALK | VISUAL_MEDIUM | Adjacent to central stems |
| 17-20 | Lower left of plant | STALK | VISUAL_MEDIUM | Adjacent to stem base area |
| 23-27 | Below plant | STALK/BASE | VISUAL_LOW | Below illustration (no root shown) |

### Bidirectional Validation

**"ed" (CONFIRMED = root) lines:** NONE in f1r
- Cannot validate - no "ed" tokens present
- **Observation:** Consistent with no root depicted!

**"od" (CANDIDATE = stalk) lines:** 15 occurrences
- Line 3: shod (above plant - GENERAL)
- Line 4: odsoiin (above plant - GENERAL)
- Line 8: chody (leaf/stalk junction - MATCH if od=stalk)
- Line 9: shody (leaf/stalk junction - MATCH if od=stalk)
- Line 12: shodain (leaf/stalk junction - MATCH if od=stalk)
- Line 13: kodaiin, cphodaiils (stalk area - MATCH if od=stalk)
- Line 14: odaiin, chodain, kod (stalk area - MATCH if od=stalk)
- Line 16: odan (stalk area - MATCH if od=stalk)
- Line 26: shody (below plant)

**Prediction:** If "od" = stalk, most occurrences should be in stalk-adjacent lines.
**Observation:** Lines 8-16 (where most "od" tokens appear) ARE in the stalk/stem zone of the illustration.
**Match rate:** ~60% of "od" tokens are in stalk-adjacent areas (lines 8-16).
**Verdict:** SUPPORTIVE of od=stalk hypothesis in this folio.

**"kair/kar/fair/char" (PROMOTED = fire/heat) lines:** 1 occurrence
- Line 19: dchar (lower stalk area)
- **Observation:** No fire/cooking vessel imagery in this folio - this is a plant illustration only.
- **Verdict:** Cannot validate fire/heat meaning in this plant folio.

**"kal" (PROMOTED = cauldron) lines:** 1 occurrence
- Line 1: ykal (header paragraph)
- **Observation:** No vessel imagery visible.
- **Verdict:** Cannot validate cauldron meaning in this plant folio.

### Key Findings

1. **No root = No "ed"**: The absence of both root illustration AND "ed" tokens is mutually consistent.
2. **Stalk emphasis correlates with "od" clustering**: The "od" tokens concentrate in lines 8-16, which are adjacent to the stem/stalk area of the illustration.
3. **This is a leaf-focused folio**: The illustration emphasizes leaves, and the majority of text wraps around the leaf/stem structure.

### Anomalies/Notes

- Previous Phase 1 annotation marked f1r as "text-only" with "no plant illustration" - this was **WRONG**. There IS a clear plant illustration.
- The plant identification (which species?) remains unknown, but the structure is clear.
- The decorative initials (red/brown) mark paragraph beginnings, not plant parts.

---

## Folio Annotation Summary (In Progress)

| Folio | Method | Status | Root | Stalk | Leaf | Flower | Notes |
|-------|--------|--------|------|-------|------|--------|-------|
| f1r | VISUAL | COMPLETE | NO | YES | YES | NO | Leaf-focused plant |
| f2r | - | PENDING | - | - | - | - | Needs image |
| ... | - | - | - | - | - | - | - |

---

*Log continues as folios are annotated...*
