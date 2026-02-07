# ZFD Paleographic Transcription -- Progress Log

**Project:** Direct manuscript-to-Croatian transcription of Voynich Manuscript (Beinecke MS 408)
**Method:** 7-layer constraint stack, behavioral paleography
**Start date:** 2026-02-07

---

## Phase Summary

| Phase | Description | Status | Deliverables |
|-------|-------------|--------|-------------|
| 1 | Hand Sheet -- Profile the Scribe | COMPLETE | hand_sheet/ (7 files + 12 exemplar notes) |
| 2 | Ductus Analysis | COMPLETE | DUCTUS_ANALYSIS.md, stroke_sequences.json |
| 3 | Exemplar Transcription (5 anchors) | COMPLETE | folios/f88r, f1r, f2r, f71r, f102v |
| 4 | Abbreviation Inventory | COMPLETE | ABBREVIATION_INVENTORY.md, abbreviation_rules.json, METHODOLOGY.md |
| 5 | Herbal Section (f1r-f57v) | PENDING | ~114 pages |
| 6 | Pharmaceutical Section (f87r-f116r) | PENDING | ~60 pages + Latin index |
| 7 | Zodiac, Biological, Stars | PENDING | ~50 pages |
| 8 | Assembly & Validation | PENDING | FULL_CORPUS.jsonl, COMPARISON_REPORT.md |

---

## Completed Folios

| Folio | Section | Lines | Labels | Confidence Distribution | Date |
|-------|---------|-------|--------|------------------------|------|
| f88r | Pharmaceutical | 16 | 15 | 2A, 14B, 10C, 1D | 2026-02-07 |
| f1r | Text (opening) | 28 | 4 titles | Mixed B/C | 2026-02-07 |
| f2r | Herbal | 12 | -- | Mixed B/C | 2026-02-07 |
| f71r | Zodiac | 18 | 15 nymph labels | Mixed B/C | 2026-02-07 |
| f102v | Pharmaceutical | 39 | ~16 | Mixed B/C | 2026-02-07 |

**Total folios transcribed:** 5 / 197
**Total lines transcribed:** ~113

---

## Phase 1-2 Deliverables

### Hand Sheet (transcription/hand_sheet/)
- `HAND_DESCRIPTION.md` -- Full scribal hand profile (21KB)
- `glyph_inventory.json` -- 20+ glyphs cataloged with positional data
- `ligature_catalog.json` -- 20 ligatures cataloged
- `abbreviation_inventory.json` -- 34 abbreviation types
- `DUCTUS_ANALYSIS.md` -- Stroke-by-stroke decomposition (20KB)
- `stroke_sequences.json` -- Machine-readable stroke data
- `exemplar_notes/` -- 12 per-folio analysis files

### Key Findings from Hand Sheet
- Single scribe throughout (consistent ductus across all sections)
- Writing speed varies: careful (labels, openings) vs standard (body text) vs rapid (dense recipe sections)
- 5 cases where ductus distinguishes glyphs EVA conflates
- 3 cases where EVA treats differently what is actually the same
- aiin is a zero-pen-lift ligature unit (strongest evidence for shorthand system)
- Gallows distinguished by loop orientation (k=right, t=left, f=double, p=forward)

---

## Phase 3 Anchor Folio Notes

### f88r (Gold Standard)
- Curio-validated labels: "ostol" (bone oil) and "otrorhetri" (treated heated fluid)
- 3-register pharmaceutical apparatus layout
- Highest confidence readings in the corpus
- ~25 k-gallows, ~8 t-gallows instances

### f1r (Opening Page)
- 4 paragraphs with right-justified titles
- Two "weirdo" decorated initials (@252, @253)
- Careful hand, Language A, Hand 1
- Faint Tepenecz signature at top
- Right margin stained key sequences

### f2r (Herbal)
- Cornflower plant illustration (Petersen identification)
- Text interrupted by plant parts
- Standard herbal vocabulary with operator/suffix patterns

### f71r (Zodiac)
- Circular diagram with Aries goat at center
- 15 nymph labels (inner + outer rings)
- Tests generalization of pharmaceutical vocabulary to zodiac context
- High frequency of ot/ok operators in labels

### f102v (Pharmaceutical)
- Pharmaceutical page with ~16 labels and 2 text blocks
- Some partially illegible labels (lines 9, 16, 29)
- Dense pharmaceutical vocabulary comparable to f88r

---

## Phase 4 Deliverables

- `ABBREVIATION_INVENTORY.md` -- 34 abbreviation types, human-readable (13KB)
- `abbreviation_rules.json` -- Machine-readable parsing pipeline (6KB)
- `METHODOLOGY.md` -- Formal methodology document (11KB)

---

## Batch Log

| Batch | Folios | Date | Notes |
|-------|--------|------|-------|
| Anchor set | f88r, f1r, f2r, f71r, f102v | 2026-02-07 | Phase 3 complete |

---

*This log is updated as transcription progresses through Phases 5-8.*
