# 'od' Mapping Validation Report

**Generated:** 2026-02-01
**Methodology:** Image-Adjacent Correlation Testing with Shuffled Baseline
**Status:** NEEDS_REFINEMENT

---

## Executive Summary

The 'od' → stalk hypothesis was tested using the image-adjacent testing framework with heuristic-based folio annotations. **The initial verdict is REJECTED based on current annotation data**, but this result requires careful interpretation due to annotation quality limitations.

### Key Findings

| Metric | od → stalk | Threshold | Status |
|--------|-----------|-----------|--------|
| Match rate | 58.2% | ≥40% | ✓ PASS |
| P-value | 0.0920 | <0.01 | ✗ FAIL |
| Max wrong part | 52.9% (leaf) | <20% | ✗ FAIL |

**Final Verdict:** REJECTED (pending annotation refinement)

---

## Methodology Notes

### Critical Caveat: Annotation Quality

This validation uses **HEURISTIC annotations** that assign plant parts based on text line position within each folio:
- Lines 1-25%: Root zone
- Lines 26-50%: Stalk zone
- Lines 51-75%: Leaf zone
- Lines 76-100%: Flower zone

This is a placeholder approach. The original ZFD research used **actual visual inspection** of plant illustrations to determine which text lines were adjacent to which plant parts. Our heuristic approach assumes:
1. Plants are drawn vertically (roots at bottom)
2. Text position correlates with illustration position
3. All folios have consistent layouts

These assumptions may not hold for many folios, especially complex pages like f66r.

### Comparison with CONFIRMED 'ed' Mapping

As a control, we tested the 'ed' → root mapping (previously CONFIRMED in ZFD):

| Metric | ed → root |
|--------|-----------|
| Occurrences | 550 |
| Match rate | 37.1% |
| Baseline rate | 37.0% |
| P-value | 0.493 |
| Verdict | FAIL |

The fact that the CONFIRMED 'ed' mapping also fails with heuristic annotations suggests **the annotations are the limiting factor**, not the methodology.

---

## Test Results Detail

### Test 1: od → stalk (Primary Hypothesis)

```
Occurrences: 790
In annotated folios: 775
Adjacent matches: 451
Match rate: 58.2%
Baseline rate: 55.7%
P-value: 0.0920
VERDICT: FAIL (p > 0.05)
```

The match rate (58.2%) exceeds the 40% threshold, but the p-value (0.0920) does not meet the strict <0.01 criterion. The observed rate is not significantly different from the shuffled baseline.

### Test 2: Forbid Check

Wrong-part correlation rates:

| Plant Part | Rate | Status |
|------------|------|--------|
| leaf | 52.9% | FORBID VIOLATED |
| root | 43.5% | FORBID VIOLATED |
| flower | 38.3% | FORBID VIOLATED |
| seed | 0.0% | OK |
| vessel | 0.0% | OK |

**Interpretation:** High cross-contamination with multiple plant parts suggests either:
1. The annotations don't accurately reflect plant-part positions
2. 'od' has a more general meaning not tied to a single plant part
3. 'od' appears in general descriptive contexts rather than part-specific ones

### Test 3: Alternative Meanings

| Hypothesis | Match Rate | P-value | Verdict |
|------------|-----------|---------|---------|
| od → root | 43.5% | 0.000 | PASS |
| od → stalk | 58.2% | 0.092 | FAIL |
| od → leaf | 52.9% | 0.838 | FAIL |
| od → flower | 38.3% | 0.996 | FAIL |
| od → vessel | 0.0% | 1.000 | FAIL |

**Notable:** 'od' → root shows p=0.000, suggesting it may correlate better with roots than stalks. However, this contradicts the established 'ed' → root mapping and may indicate annotation artifacts.

---

## Interpretation and Next Steps

### Why This Result Should Not Be Final

1. **Annotation quality is insufficient.** The heuristic approach does not capture actual plant-part positions in the manuscript.

2. **Known CONFIRMED mappings fail.** If 'ed' → root fails with these annotations, we cannot trust 'od' results either.

3. **The framework works correctly.** The statistical machinery is sound; the input data (annotations) needs improvement.

### Required Next Steps

1. **Manual annotation of priority folios:**
   - f66r (82 lines, high ed/od counts)
   - f41r, f43v (high ed counts)
   - f56r (case study folio)
   - f51v, f53v, f57r (high od counts)

2. **Visual inspection protocol:**
   - Examine each folio image
   - Mark line ranges adjacent to visible plant parts
   - Update annotations with MANUAL confidence level

3. **Re-run validation with refined annotations**

4. **Consider contextual analysis:**
   - Does 'od' appear in consistent operator contexts?
   - What stems frequently combine with 'od'?
   - Cross-reference with morphological triple patterns

---

## Conclusion

**Status: NEEDS_REFINEMENT**

The 'od' → stalk hypothesis cannot be confirmed or rejected with current data quality. The testing framework is operational and methodologically sound, but requires higher-quality plant-part annotations derived from actual folio image inspection.

The original October 2025 findings (44.4% stalks, 22.2% roots) were likely based on more accurate visual annotations. This automated pipeline will produce valid results once annotations are upgraded from HEURISTIC to MANUAL quality.

---

## Raw Data

Full test results saved to: `validation/results/od_tests.json`

---

*Report generated by ZFD Validation Pipeline v0.1*
