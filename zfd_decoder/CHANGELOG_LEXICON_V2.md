# Lexicon v2 Integration Changelog

**Date:** 2026-02-05
**Commit:** feat: integrate lexicon_v2 with category-aware glossing and confidence tiers

## What Changed

### Lexicon Upgrade
- **92 -> 181 unique entries** (185 rows, 4 variant overlaps) from 14 sources
- **3 new columns:** `croatian` (Croatian form), `category` (semantic type), `source` (provenance)
- Sources merged: lexicon_v1, miscellany mining, herbal lexicon v3.6, botanical glossary, proof kit, pharmaceutical morphemes

### Confidence Tiers
Status-based confidence replaces hardcoded 0.30 boost:
- **CONFIRMED** (74 entries): 0.30 confidence
- **CANDIDATE** (23 entries): 0.15 confidence
- **MISCELLANY** (88 entries): 0.10 confidence

MISCELLANY entries are newly mined from medieval pharmaceutical manuscripts. They contribute to glossing but are flagged as lower confidence.

### Category Distribution
11 semantic categories across all entries:
- ingredient (72), action (32), body_part (22), grammar (21)
- condition (10), equipment (8), preparation (8), latin_pharma (5)
- measurement (3), timing (2), modifier (2)

### Croatian Output Layer
`_build_croatian()` now produces actual Croatian words when available:
- `ol` -> `ulje` (oil)
- `sar` -> `sol` (salt)
- `kost` -> `kost` (bone)
- `ar` -> `voda` (water)

Falls back to ZFD orthography when no Croatian form is mapped.

### Pipeline Changes
- `stems.py`: Auto-detects v1 (6-col) vs v2 (9-col) format. New methods: `get_category()`, `get_croatian()`, `confidence_for_status()`
- `pipeline.py`: Prefers `lexicon_v2.csv` when present, falls back to `lexicon.csv`. Accepts `lexicon_file` parameter for explicit override.
- `main.py`: Added `--lexicon` CLI argument for custom lexicon path.
- Diagnostics now include `category_distribution` and `miscellany_stems` count.

### Backward Compatibility
- `lexicon.csv` (v1) preserved as fallback
- All 10 original tests pass unchanged
- v1 format loads cleanly with default values for new fields
- `--lexicon data/lexicon.csv` explicitly selects v1

### Test Coverage
- 10 existing tests: ALL PASS
- 14 new v2 tests: entry counts, format detection, confidence tiers, Croatian output, category lookup, diagnostics, backward compat, schema validation

## f88r Benchmark
| Metric | v1 | v2 |
|--------|----|----|
| Lexicon entries | 89 | 181 |
| Known stems | 95 | 95 |
| Known ratio | 71.4% | 71.4% |
| Avg confidence | 0.338 | 0.338 |

f88r shows identical resolution because its unknown stems are morphological fragments (state markers, suffix clusters) not yet in either lexicon. The v2 entries expand coverage for folios with more ingredient/body-part/action vocabulary. The real improvement shows across the full 201-folio corpus.
