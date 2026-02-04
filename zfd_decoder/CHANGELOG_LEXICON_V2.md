# Lexicon v2 Changelog

**Date:** 2025-02-04
**Version:** lexicon_v2.csv

## Summary

The ZFD decoder lexicon has been upgraded from 92 entries (v1) to 185 entries (v2), representing 101% growth in vocabulary coverage.

## New Columns

The v2 schema adds 3 new columns to the existing 6:

| Column | Description | Example |
|--------|-------------|---------|
| `croatian` | Croatian word form | "kost", "ulje", "voda" |
| `category` | Semantic category | "ingredient", "action", "body_part" |
| `source` | Entry provenance | "lexicon_v1", "miscellany_new" |

## Categories

The v2 lexicon organizes entries into 11 semantic categories:

| Category | Count | Description |
|----------|-------|-------------|
| ingredient | 72 | Substances used in recipes |
| action | 32 | Verbs for preparation methods |
| body_part | 22 | Anatomical targets for treatment |
| grammar | 21 | Function words (prepositions, conjunctions) |
| condition | 10 | Medical conditions being treated |
| equipment | 8 | Tools and vessels |
| preparation | 8 | Medicinal forms (powder, ointment) |
| latin_pharma | 5 | Latin pharmaceutical abbreviations |
| measurement | 3 | Dosage units |
| timing | 2 | Time-related terms |
| modifier | 2 | Adjectives and qualifiers |

## Status Confidence Tiers

Each entry has a status that determines its confidence contribution:

| Status | Confidence | Count | Description |
|--------|------------|-------|-------------|
| CONFIRMED | 0.30 | 81 | Validated from multiple sources |
| CANDIDATE | 0.15 | 23 | High probability, pending full validation |
| MISCELLANY | 0.10 | 81 | Newly mined from medieval pharmaceutical texts |

## Source

New entries sourced from medieval pharmaceutical miscellany mining (Pharmacological etc. miscellany 2066895), including:
- Body part terminology for treatment targets
- Action verbs for preparation methods
- Medical conditions vocabulary
- Equipment and measurement terms

## Backward Compatibility

- Old `lexicon.csv` (v1) format still works as fallback
- Pipeline auto-detects format by checking for `croatian` column
- Can force v1 with `--lexicon path/to/lexicon.csv` CLI argument
- All existing tests pass without modification

## API Changes

### StemLexicon

New methods:
- `get_category(stem: str) -> str` - Returns category or "unknown"
- `get_croatian(stem: str) -> str` - Returns Croatian form or ""
- `confidence_for_status(status: str) -> float` - Returns confidence value
- `is_v2` property - True if using v2 format

### ZFDPipeline

- New `lexicon_file` parameter in `__init__` for custom lexicon path
- Default behavior: load `lexicon_v2.csv` if present, fallback to `lexicon.csv`
- Diagnostics now include `category_distribution` and `miscellany_stems`

### Croatian Output Layer

- `_build_croatian()` now uses actual Croatian words from lexicon
- Example: "sar" produces "sol" (salt) in Croatian layer
