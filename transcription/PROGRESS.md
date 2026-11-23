# ZFD Paleographic Transcription -- Progress Log

**Project:** Croatian (ZFD) transcription of Voynich Manuscript (Beinecke MS 408): 5 hand-transcribed anchor folios plus automated rule parsing of the Takahashi (H) EVA transliteration for the rest
**Method:** 7-layer constraint stack, behavioral paleography
**Start date:** 2026-02-07
**Initial assembly:** 2026-02-07
**Latest audit:** 2026-11-23

---

## Phase Summary

| Phase | Description | Status | Deliverables |
|-------|-------------|--------|-------------|
| 1 | Hand Sheet -- Profile the Scribe | COMPLETE | hand_sheet/ (7 files + 12 exemplar notes) |
| 2 | Ductus Analysis | COMPLETE | DUCTUS_ANALYSIS.md, stroke_sequences.json |
| 3 | Exemplar Transcription (5 anchors) | COMPLETE | folios/f88r, f1r, f2r, f71r, f102v (hand-transcribed) |
| 4 | Abbreviation Inventory | COMPLETE | ABBREVIATION_INVENTORY.md, abbreviation_rules.json, METHODOLOGY.md |
| 5 | Herbal Section (f1r-f57v) | COMPLETE | 112 folios (110 automated + 2 anchor) |
| 6 | Pharmaceutical Section (f87r-f116r) | COMPLETE | ~60 folios |
| 7 | Zodiac, Biological, Stars | COMPLETE | ~25 folios + retained diagram/text stubs |
| 8 | Assembly & Validation | COMPLETE | FULL_CORPUS.jsonl, STATISTICS.md, COMPARISON_REPORT.md, SECTION_COMPARISON.md |

---

## Coverage Summary

- **Packages:** 203 = 196 automated packages + 5 hand anchors + 2 retained stubs.
- **Source page representation:** all 201 page IDs returned by the H-transcription selector are represented. This is not complete source-text coverage: f102v's retained anchor has 38 rows / 180 EVA tokens, versus 62 selected source lines / 311 tokens.
- **JSONL rows:** 5,194, including an empty f85v diagram placeholder and the fragmentary f116v text stub. The source selector itself returns 5,215 lines; the preserved anchors differ from that selection.
- **EVA and ZFD word tokens:** 37,785 each.
- **Hand anchors:** f88r, f1r, f2r, f71r and f102v. The compiler agrees on 621 / 735 words (84.4898%) across all 129 anchor rows, with zero rows skipped and `sh` normalized to `š`.
- **Automated packages:** 196, regenerated 21 November under abbreviation_rules v1.1.0. The 23 November report correction fixes comma tokenization and parser-order statistics; see [AUDIT_2026-11.md](AUDIT_2026-11.md).
- **Retained stubs:** f85v is an empty diagram placeholder; f116v contains fragmentary legacy text. Neither is a completed transcription.

## Section Breakdown

Pre-audit counts (197-folio corpus). Current per-section folio and line counts are in STATISTICS.md.

| Section | Folios | Status |
|---------|--------|--------|
| Herbal (f1r-f57v) | 112 | Complete |
| Herbal Large (f58r-f66v) | 8 | Complete |
| Cosmological (f67r-f69v) | 6 | Complete |
| Zodiac (f70v-f73v) | 5 | Complete |
| Biological (f75r-f84v) | 20 | Complete |
| Rosettes (f85r-f86v) | 4 | Complete (f85v stub) |
| Pharmaceutical (f87r-f102v) | 18 | Complete |
| Recipe (f103r-f116v) | 24 | Complete (f116v stub) |

## Key Deliverables

### Phase 1-2: Foundation
- `hand_sheet/HAND_DESCRIPTION.md` -- Scribal hand profile
- `hand_sheet/glyph_inventory.json` -- 20+ glyphs cataloged
- `hand_sheet/ligature_catalog.json` -- 20 ligatures
- `hand_sheet/abbreviation_inventory.json` -- 34 abbreviation types
- `hand_sheet/DUCTUS_ANALYSIS.md` -- Stroke decomposition
- `hand_sheet/stroke_sequences.json` -- Machine-readable strokes
- `hand_sheet/exemplar_notes/` -- 12 per-folio analyses

### Phase 3: Anchor Folios (Hand-Transcribed)
- `folios/f88r/` -- Project hand anchor
- `folios/f1r/` -- Opening page
- `folios/f2r/` -- Herbal with validated "ostol" and "sal"
- `folios/f71r/` -- Zodiac (cross-section test)
- `folios/f102v/` -- Pharmaceutical with "orolaly" Latin term

### Phase 4: Reference Documents
- `ABBREVIATION_INVENTORY.md` -- Formal catalog
- `abbreviation_rules.json` -- Machine-readable parsing pipeline
- `METHODOLOGY.md` -- Publication-ready methodology

### Phase 5-7: Full Corpus
- `folios/f{NNN}{r|v}/` -- 203 package directories, with:
  - `metadata.json` -- Folio metadata and IIIF links
  - `TRANSCRIPTION.md` -- Line-by-line transcription
  - `line_data.jsonl` -- Machine-readable per-line data
  - `notes.md` -- Observations and statistics

### Phase 8: Assembly
- `FULL_CORPUS.jsonl` -- Concatenated corpus (5,194 JSONL rows)
- `STATISTICS.md` -- Coverage, confidence, vocabulary stats
- `COMPARISON_REPORT.md` -- EVA vs ZFD divergence analysis
- `SECTION_COMPARISON.md` -- Cross-section vocabulary analysis

### Scripts
- `scripts/batch_transcribe.py` -- Automated ZFD parsing pipeline
- `scripts/generate_reports.py` -- Report generation

## Validated Readings

| Term | Folio | EVA | ZFD | Meaning | Validation Method |
|------|-------|-----|-----|---------|-------------------|
| ostol | f88r, f1r, f2r | okol | ostol | bone oil | Project hand reading |
| otrorhetri | f88r | otorchety | otrorhetri | treated heated fluid | Project hand reading |
| orolaly | f102v | okeo.r!oly | orolaly | orally (Latin) | Latin pharmaceutical |
| sal | f2r, f102v | sal | sal | salt | Standard pharmaceutical |
| dain | throughout | daiin | dain | substance/given | Frequency + consistency |

---

*This project transcription is an interpretation compiled from EVA and retained hand anchors. The source EVA, coverage differences and compiler agreement remain available for comparison.*
