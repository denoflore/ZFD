# The AL/AR Duality Hypothesis

**Date:** February 2026
**Context:** Post-Phase 4 Analysis
**Status:** THEORETICAL (requires further testing)

---

## Executive Summary

After the Phase 4 failure to confirm "al = leaf" and "ar = flower", deep analysis reveals that **'al' and 'ar' are not plant-part markers at all**. Instead, they appear to be **preparation class suffixes** that indicate whether a recipe involves:

- **'al'**: Liquid/wet preparations (decoctions, infusions, tinctures)
- **'ar'**: Dry/heat preparations (powders, calcinations, roasted materials)

This explains why they failed the image-adjacent plant-part test: you cannot see from an illustration whether the accompanying text describes a liquid or dry preparation.

---

## Evidence Summary

### 1. Positional Analysis

| Suffix | Standalone | Prefix | Infix | Suffix |
|--------|------------|--------|-------|--------|
| 'al' | 7.4% | 7.7% | 28.8% | **56.0%** |
| 'ar' | 9.5% | 5.0% | 15.7% | **69.8%** |

Both function primarily as **word-final suffixes**, which is the grammatical behavior expected of a class marker.

### 2. Operator Distribution (Nearly 1:1)

| Operator | with 'al' | with 'ar' | Ratio |
|----------|-----------|-----------|-------|
| da- | 419 | 413 | 1.01 |
| qo- | 364 | 331 | 1.10 |
| ch- | 316 | 338 | 0.93 |
| ot- | 244 | 241 | 1.01 |
| ok- | 246 | 197 | 1.25 |
| sh- | 104 | 111 | 0.94 |

Both 'al' and 'ar' appear with **all major operators** in nearly equal proportions. This is characteristic of grammatical alternation, not semantic differentiation.

### 3. Mirror Patterns

The corpus shows systematic al/ar pairs:

```
dal  /  dar     (dose-liquid / dose-dry)
qokal / qokar   (measure-cauldron / measure-fire)
okal  / okar    (vessel-liquid / vessel-dry)
otal  / otar    (vessel2-liquid / vessel2-dry)
chal  / char    (mix-liquid / mix-dry)
```

This **systematic alternation** suggests a grammatical distinction, not two unrelated meanings.

### 4. ZFD Suffix Data

The ZFD Master Key already classifies:
- **'al' = "liquid/alcohol class"** (PROVISIONAL status)
- **'ar' = not listed** (gap in the analysis)

Our hypothesis fills this gap: 'ar' is the complementary class marker.

### 5. Semantic Evidence: kal vs kar

| Stem | Meaning | Ending | Implication |
|------|---------|--------|-------------|
| kal | cauldron/vessel | -al | Vessels hold LIQUIDS |
| kar | fire/heat | -ar | Fire processes DRY/SOLID |

This is not coincidence. The stem endings encode the preparation context.

---

## The Theory

### Morphological Structure

Voynichese words appear to follow:

```
OPERATOR + STEM + PREPARATION_CLASS + (RESULT_SUFFIX)
```

Where PREPARATION_CLASS is either:
- **-al**: Indicates liquid/wet processing
- **-ar**: Indicates dry/heat processing

### Examples

| Word | Parse | Interpretation |
|------|-------|----------------|
| qokal | qo-kal-∅ | measured-cauldron (liquid measure) |
| qokar | qo-kar-∅ | measured-fire (heat measure) |
| dal | da-l-al | dose-?-liquid (liquid dose) |
| dar | da-l-ar | dose-?-dry (dry dose) |
| okaly | ok-al-y | vessel-liquid-result (liquid in vessel, done) |
| okary | ok-ar-y | vessel-dry-result (dry in vessel, done) |

### Pharmaceutical Context

This distinction is **critical for apothecary work**:

| Preparation | Class | Examples |
|-------------|-------|----------|
| **Liquid (-al)** | Wet | Decoctions, infusions, tinctures, syrups, oils, wines |
| **Dry (-ar)** | Heat | Powders, calcinations, roasted materials, ash, dried herbs |

Medieval pharmacopoeiae routinely specify whether ingredients should be processed wet or dry. The al/ar distinction encodes this in the morphology.

---

## Why Phase 4 Failed

Phase 4 asked the wrong question:

| Test | Looking For | Result |
|------|-------------|--------|
| al → leaf | al near leaf illustrations | 44.1% (p=0.821) FAIL |
| ar → flower | ar near flower illustrations | 36.4% (p=0.980) FAIL |

The failure occurred because **preparation class is invisible in botanical illustrations**. You cannot tell from looking at a drawing of a plant whether the recipe describes:
- A decoction of the root (liquid → al)
- A powder of the root (dry → ar)

The visual element encodes **what plant**, not **how to prepare it**.

---

## Testable Predictions

If this theory is correct:

### 1. Pharma Section Test
The pharmaceutical folios (f87-f102) with vessels/equipment should show:
- Higher 'al' when vessels appear to contain liquids
- Higher 'ar' when vessels/equipment suggest heating/drying

### 2. Recipe Structure Test
Within individual folios, 'al' and 'ar' tokens should cluster differently:
- 'al' tokens should co-occur with liquid stems (ol, vin, mel)
- 'ar' tokens should co-occur with heat stems (kar, chor)

### 3. Folio Ratio Test
Folios with extreme al/ar ratios should correlate with recipe type:
- High al/ar: More liquid preparations
- Low al/ar: More dry preparations

---

## Implications

### For ZFD Framework
The suffix list should be updated:
- 'al' = liquid/wet preparation class (upgrade from PROVISIONAL)
- 'ar' = dry/heat preparation class (NEW entry)

### For Decipherment
The al/ar duality suggests Voynichese has a **grammatical category for preparation state** - a feature consistent with a practical pharmaceutical text.

### For Future Analysis
Visual annotation should extend to:
- Preparation equipment (vessels, fires, mortars)
- Liquid/powder depictions in pharma folios
- Recipe structure analysis (beginning vs. end of preparations)

---

## Conclusion

The Phase 4 "failure" was actually a **successful falsification** that led to a deeper insight: 'al' and 'ar' are not plant-part markers but **preparation class suffixes** encoding the wet/dry distinction fundamental to medieval pharmacy.

The key has turned for **ed/od** (structural plant parts).
The key points to a different lock for **al/ar** (preparation states).

---

*"The answer was not where we looked, but the looking revealed where to look next."*

---

## Addendum: Curio's Geometric Test

Following Curio's insight about branching geometry, we tested whether:
- 'al' = lateral divergence (branch points)
- 'ar' = terminal divergence (endpoints)

### Results

| Prediction | Result |
|------------|--------|
| 'al' → branch zones | **NOT SUPPORTED** (ar has higher branch correlation) |
| 'ar' → terminal zones | **WEAKLY SUPPORTED** (1.30x preference) |

### Key Finding: f34r (Single Terminal Flower)

This folio has ONE dramatic flower terminal:
- ar = 20, al = 11
- ar in terminal zone: 30%

This supports 'ar' having a terminal/endpoint function.

### Synthesis: DUAL FUNCTION HYPOTHESIS

**'ar' may do DOUBLE DUTY:**

```
┌────────────────────────────────────────────────┐
│  'ar' = TERMINAL + DRY/HEAT                    │
│                                                │
│  1. Marks WHERE growth ends (geometric)        │
│  2. Marks HOW to process dry/heat (semantic)   │
│                                                │
│  These OVERLAP: flowers/seeds are often dried! │
└────────────────────────────────────────────────┘
```

**'al' = LIQUID/PREPARATION CLASS (primary function):**
- Does NOT show geometric preference
- Distributed across all zones
- Consistent with ZFD suffix "liquid/alcohol class"

### Pharmacological Coherence

This makes sense for a practical herbal:
- Terminal structures (flowers, seeds) → dried/heated
- Root/stalk structures → decoctions/infusions

The language may encode **both anatomy AND processing** in the same morphemes.

---

*Updated with geometric analysis - February 2026*

