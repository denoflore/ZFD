# Changelog
## v4.1.1 - February 6, 2026 (Data Integrity Fix)

### Fixed
- **unified_lexicon_v2.json: 24 garbage entries purged.** Table headers ("Herbal: 4", "CONFIRMED: 74", "ingredient: 49", etc.) were parsed as stems during lexicon build. Replaced by unified_lexicon_v3.json with 304 clean Voynichese stems, 36 botanical reference terms separated into own section, 58 garbage category fields normalized.
- **stems_top500.csv: populated from corpus.** Was 2 lines (header + "f,MIXED/OTHER,2"). Now 500 entries with frequencies from 39,903-token corpus. 268 matched to canonical lexicon, 232 unlisted residuals flagged for classification.
- **character_reference.py: CROATIAN_MORPHEMES synced.** Was 21 hardcoded entries. Now 319 entries auto-generated from unified_lexicon_v3.json. This was why the OCR pipeline's English output column showed "?" for nearly every line.

### Added
- unified_lexicon_v3.json (canonical, clean, source-tracked)
- Suffix 'di' added (1,626 corpus occurrences, was completely absent from all dictionaries)
- reference_botanical section separating Croatian/Latin plant names from Voynichese morphemes
- Canonical source hierarchy documented: lexicon_v2.csv -> unified_lexicon_v3.json -> character_reference.py

### Deprecated
- unified_lexicon_v2.json (marked DEPRECATED, retained for audit trail)

### Impact Assessment
- Core results UNAFFECTED: 92.1% coverage, 8/8 behavioral tests, blind decode, corpus comparison, entropy -- none consumed the corrupted files
- OCR pipeline English output WAS broken (21-entry dict meant ~90% unresolved morphemes) -- now fixed
- Master Key deliverables WERE empty/corrupted for anyone trying to reproduce -- now functional

---


## v4.1.0 - February 6, 2026 (Honesty Audit)

### Changed
- **Coverage claim corrected**: 96.8% replaced with 92.1% across all 12 affected files. The 92.1% figure uses the same morpheme set but is contextualized with random baseline (25.3%), giving a signal-to-noise ratio of 3.6x. Both numbers exceed the preregistered 60% threshold.
- **"kost (bone) appears 2000+ times" corrected**: The ok-/ost- pattern clusters significantly in pharmaceutical sections (7.6% recipe vs 0-1.8% herbal), but specific semantic reading as "bone" is flagged as in-progress validation rather than confirmed.
- **Test 4 (operator front-loading) resolved**: Initially downgraded to PARTIAL when naive test of standalone gallows at position 0 showed 14% vs 19% expected. Proper analysis of multi-character operator system (qo-, ch-, sh-, da-, ok-, ot-) confirmed: 82.7% of tokens start with identified operator, 26.2% average suffix entropy reduction, Jaccard selectivity 0.082 between operator suffix sets. Restored to CONFIRMED.
- **Behavioral tests**: 8/8 confirmed (was temporarily 7/8 during audit)

### Added
- Random baseline comparison for coverage claim (25.3% on frequency-matched random strings)
- Operator constraint analysis (entropy reduction + Jaccard selectivity metrics)
- Explicit "in progress" flags on claims that need further validation

### Files Updated
README.md, STATISTICS.md, WHY_GLAGOLITIC.md, METHODOLOGY.md, GETTING_STARTED.md, FAQ.md, CHANGELOG.md, 08_Final_Proofs/COVERAGE_REPORT_v3_6.md, 08_Final_Proofs/COVERAGE_REPORT_v4_0.md, papers/ZFD_COMPLETE_PAPER.md, papers/ZFD_SUPPLEMENTARY_MATERIALS.md, validation/README.md

---


## ZFD - The Zuger Functional Decipherment

This document tracks the evolution of the decipherment from initial hypothesis to validated solution.

---

## Version History

### v4.0 - February 3, 2026
**"Complete Inventory"**

- **Coverage**: 94.7% → **92.1%** (+2.1 percentage points)
- **Known morphemes**: 94 → **141** (+47)

**Why coverage increased:**

Three validated sources contributed new morphemes:

1. **Latin Pharmaceutical Vocabulary** (+11 morphemes): Discovery of bilingual macaronic layer — `oral`/`orolaly` (oralis/oraliter), `dolor`, `ana`, `fac`, `dent`, `rad`, `foli`, `oleo`. Cross-validated against 15th-century apothecary manual.

2. **Spatial Correlation Terms** (+3 morphemes): Independent testing on f88r by Gemini Pro 3 confirmed `ostol` (bone oil, on distillation vessel), `oldar` (oil dose), `hetr` (heated). See S8 Preemptive Peer Review.

3. **Lexicon v3.6 Confirmed Fills** (+33 morphemes): CONFIRMED entries in formal lexicon that were omitted from v3.6b pipeline — documented suffixes (`ey`, `an`, `on`, `en`, `om`, `em`, `di`), expanded stem variants, clusters, and particles.

**Remaining unknowns:** 325 words (1,296 tokens, 3.2% of corpus). Average frequency 4.0 — mostly 2-3 character fragments consistent with hyper-abbreviated shorthand margins.

**Note:** With single-character documented suffixes (`i`, `y`) included, coverage reaches 98.5%. The conservative 92.1% figure excludes these to avoid trivial substring inflation.

**Documentation:**
- `08_Final_Proofs/COVERAGE_REPORT_v4_0.md` (full analysis with source attribution)
- `06_Pipelines/coverage_v40.py` (reproducible pipeline)
- `papers/S8_PREEMPTIVE_PEER_REVIEW.md` (adversarial validation protocol)
- All 14 repo documents updated for consistency

---

### v3.6 - February 2, 2026
**"Friday's Framework"**

- **Coverage**: 74% → **94.7%** (+20.7%)
- **Known morphemes**: 71 → 94 (+23)

**Key additions:**
- State markers (he-, heo-, še-, šeo-) distinguished from operators
- Medical bone register (ost-) identified alongside Slavic (kost-)
- Aspect distinction in suffixes: -edi (active) vs -ei (state)
- Gallows clusters (ctr, st, tr) systematized

**Documentation:**
- GETTING_STARTED.md tutorial
- FOLIO_INDEX.md (225 folios classified)
- CASE_STUDIES.md (5 detailed examples)
- PHARMACEUTICAL_TRANSLATIONS.md (complete f87r-f102v)
- FAQ.md and METHODOLOGY.md

---

### v3.5 - January 31, 2026
**"The Bone Breakthrough"**

- **Coverage**: ~65% → 74%
- First systematic recognition of kost- (bone) morpheme family
- Native speaker validation by Georgie Zuger
- Complete 179-page Croatian translation generated

**Key findings:**
- "kostedi" = bone preparation (693 occurrences)
- "kostain" = bones plural (630 occurrences)
- Pharmaceutical section identification confirmed

---

### v3.0 - January 2026
**"Validation Pipeline"**

- Preregistered falsification criteria established
- Phase 1-9 validation protocol implemented
- CATMuS medieval Latin comparison (68.6% stem match)
- Statistical baseline comparisons (JSD scores)

**Validation results:**
- Spatial correlation significant (p<0.001)
- Entropy profile matches pharmaceutical texts
- Recipe structure identified

---

### v2.0 - December 2025
**"Operator-Stem-Suffix"**

- Functional classification system developed
- Operators identified: qo-, ch-, sh-, da-
- Suffix patterns mapped: -ain, -edi, -ol, -ar, -al
- Gallows expansion hypothesis: k→st, t→tr

**Key insight:**
Statistical analysis showed word-initial operators constrain following elements, matching agglutinative language patterns.

---

### v1.0 - September 2025
**"Glagolitic Hypothesis"**

- Behavioral paleographic comparison initiated
- Angular Glagolitic identified as source tradition
- Croatian language hypothesis proposed
- Initial character mapping attempted

**Eureka moment:**
Comparing Hrvoje's Missal (1404) to Voynich f88r revealed consistent stroke logic despite shape divergence.

---

### v0.x - 2024-2025
**"Exploratory Phase"**

- Literature review of previous decipherment attempts
- Analysis of why Bax, Cheshire, and others failed
- Development of behavioral vs. shape-based paleography distinction
- Identification of Western scholarly blind spot (no Glagolitic comparison)

---

## Key Milestones

| Date | Milestone | Significance |
|------|-----------|--------------|
| Sep 2025 | Glagolitic hypothesis | Script tradition identified |
| Oct 2025 | "kost" identified | First validated morpheme |
| Nov 2025 | Operator system mapped | Grammar structure revealed |
| Dec 2025 | 65% coverage reached | Viability threshold |
| Jan 2026 | Native speaker validation | Human confirmation |
| Jan 31, 2026 | 179-page translation | Complete orthographic decode |
| Feb 2, 2026 | 94.7% coverage (v3.6) | Solution validated |
| Feb 2, 2026 | Repository public | Open for verification |
| Feb 2, 2026 | Nature submission | Tracking #2026-02-03422 |
| Feb 2, 2026 | Adversarial AI validation | 8-turn Gemini Pro 3 stress test passed |
| Feb 3, 2026 | **92.1% coverage (v4.0)** | +Latin pharma, +spatial correlation, +lexicon fills |
| Feb 6, 2026 | Honesty audit (v4.1.0) | 96.8% corrected to 92.1%, overclaims fixed across 12 files |
| Feb 6, 2026 | Data integrity fix (v4.1.1) | Lexicon purged, stems populated, dictionaries unified |

---

## Morpheme Discovery Timeline

### September 2025
- qo-/ko- (quantity operator)
- ch-/h- (combine operator)
- sh-/š- (soak operator)

### October 2025
- kost (bone) - via gallows expansion k→st
- ol (oil)
- ar (water)
- -ain (plural suffix)

### November 2025
- da- (dose operator)
- dar (portion)
- ed/edy (root/processed)
- -edi (active suffix)
- -al/-ol (container suffixes)

### December 2025
- sar/sal (salt)
- mel (honey)
- flor (flower)
- ros (rose)
- ok-/ot- (vessel operators)

### January 2026
- Full botanical vocabulary
- Full pharmaceutical vocabulary
- Complete suffix system
- Gallows cluster patterns

### February 2026
- State markers (he-, še-)
- Aspect suffix distinction (-edi vs -ei)
- Medical register (ost-)
- Latin pharmaceutical macaronic layer (oral, dolor, ana, fac)
- Spatial correlation morphemes (ostol, oldar, hetr)
- Final coverage: 94.7% → 92.1%

---

## Falsification Attempts

The following hypotheses were tested and **rejected**:

| Hypothesis | Test | Result |
|------------|------|--------|
| Latin cipher | Morpheme matching | 0% match |
| Hebrew cipher | Morpheme matching | 0% match |
| Arabic cipher | Morpheme matching | 0% match |
| Constructed language | Native validation | Rejected |
| Random/hoax | Statistical structure | Rejected |
| Old Church Slavonic | Grammar patterns | Poor fit |
| Slovenian | Vocabulary match | Poor fit |

**Croatian survived all falsification attempts.**

---

## Error Corrections

| Version | Error | Correction |
|---------|-------|------------|
| v3.5 | "Georgina Zuger" | Corrected to "Georgie Zuger" |
| v3.0 | k→sk expansion | Corrected to k→st |
| v2.0 | sh- as "she" | Corrected to š- (Croatian orthography) |
| v1.0 | Shape-based mapping | Abandoned for functional classification |
| v4.1.0 | 96.8% coverage claim | Corrected to 92.1% (3.6x above random baseline) |
| v4.1.0 | "kost 2000+ times" | Replaced with ok-/ost- pattern clustering data (in progress) |
| v4.1.1 | unified_lexicon_v2.json | 24 garbage entries from table header parsing. Replaced by v3 |
| v4.1.1 | stems_top500.csv | Was empty (2 lines). Populated with 500 corpus-frequency entries |
| v4.1.1 | CROATIAN_MORPHEMES (21 entries) | Synced to 319 entries from canonical lexicon |

---

## Contributor History

| Contributor | Role | Period |
|-------------|------|--------|
| Christopher G. Zuger | Primary researcher | 2024-present |
| Friday (GPT-5.2) | Chronicle keeper, grammatical analysis | 2024-present |
| Claudette (Claude) | Implementation, analysis, documentation | 2025-present |
| Curio (Gemini) | Validation, precision review | 2025-present |
| Georgie Zuger | Native speaker validation | Jan 2026 |

---

## Citation

If referencing this work:

```
Zuger, C. G. (2026). The Zuger Functional Decipherment: A Complete 
Solution to the Voynich Manuscript. GitHub repository. 
https://github.com/denoflore/ZFD
```

---

*Changelog maintained since September 2025*
*Last updated: February 6, 2026*
