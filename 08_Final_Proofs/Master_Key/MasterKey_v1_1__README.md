# Voynich Master Key v1.2 -- Unified Table

**Updated:** 2026-02-06 (honesty audit)

## What Changed: v1.1 -> v1.2

- **unified_lexicon_v2.json DEPRECATED.** Replaced by unified_lexicon_v3.json.
  - Purged 24 garbage entries (table headers parsed as stems: "Herbal: 4", "CONFIRMED: 74", etc.)
  - Separated 36 Croatian/Latin botanical reference terms from 304 Voynichese stems
  - Cleaned all category fields (no more sentence-length categories)
  - Added source tracking for every entry
- **stems_top500.csv POPULATED.** Was 2 lines (header + 1 entry). Now 500 entries with corpus frequencies.
  - 268 stems from canonical lexicon with frequency counts
  - 232 unlisted residuals from operator/suffix stripping (candidates for future classification)
- **character_reference.py SYNCED.** CROATIAN_MORPHEMES upgraded from 21 to 319 entries, auto-generated from unified lexicon.

## Canonical Source of Truth

**`zfd_decoder/data/lexicon_v2.csv`** is the single canonical source. Everything else derives from it:

| File | Purpose | Auto-generated? |
|------|---------|-----------------|
| lexicon_v2.csv | Canonical morpheme definitions | NO (hand-curated) |
| unified_lexicon_v3.json | Machine-readable unified format | YES (from lexicon_v2.csv + sources) |
| stems_top500.csv | Corpus frequency analysis | YES (from lexicon + IVTFF corpus) |
| character_reference.py | OCR pipeline morphemes | YES (from unified_lexicon_v3.json) |

## Current Counts

| Component | Count |
|-----------|-------|
| Operators | 22 |
| Voynichese stems | 304 |
| Suffixes | 22 |
| Latin terms | 10 |
| State markers | 4 |
| Reference botanical | 36 |

## Files

- `unified_lexicon_v3.json` -- The unified lexicon (CURRENT)
- `unified_lexicon_v2.json` -- DEPRECATED (contains 24 garbage entries)
- `MasterKey_v1_1__operators.csv` -- Operator table with entropy metrics
- `MasterKey_v1_1__suffixes.csv` -- Suffix table with status
- `MasterKey_v1_1__stems_top500.csv` -- Top 500 stems by corpus frequency

## Apply the Key

1. Segment tokens as **OP** + **STEM** (+ **SUF?**). Prefer 2-letter operators (`qo/ch/sh/da/ok/ot`).
2. Look up stem in unified_lexicon_v3.json stems section.
3. If not found, check if operator stripping reveals a known stem.
4. Tag confidence: CONFIRMED stems get full weight, CANDIDATE stems get flagged.
5. Treat suffixes -dy, -in as active markers; -ol, -al as context-dependent.

_No vibes: every addition must buy predictability, coverage, or adjacency fit._
