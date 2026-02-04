# CC INSTRUCTION: Lexicon v2 Integration into ZFD Pipeline

**Date:** 2025-02-04
**Priority:** HIGH
**Repo:** denoflore/ZFD
**Branch:** `feature/lexicon-v2-integration`

---

## EXECUTION PATTERN

**Follow this iterative pattern:**
1. Read a section of this file
2. Build what that section specifies
3. Test/validate what you built
4. Read the file AGAIN to find where you are
5. Continue to next section
6. Repeat until complete

**DO NOT try to build everything at once.**

---

## PROJECT OVERVIEW

The ZFD decoder pipeline (`zfd_decoder/`) currently uses `data/lexicon.csv` with 92 entries and 6 columns. We have a new `lexicon_v2.csv` with 185 entries and 9 columns (adds `croatian`, `category`, `source`). The task is to integrate lexicon_v2 into the pipeline, update `stems.py` to use the new columns, improve the English output layer in `pipeline.py` to leverage category-aware glossing, and add tests that validate the enriched output. The existing pipeline must not break. All existing tests must continue to pass.

---

## REQUIRED READING

Before writing ANY code, read these files completely:

1. **`zfd_decoder/src/stems.py`** -- Current lexicon loader. Uses `csv.DictReader`, expects columns: name, variant, context, gloss, latin, status
2. **`zfd_decoder/src/pipeline.py`** -- Full pipeline. Pay attention to `_build_english()`, `_build_croatian()`, and how `stem_data` is consumed
3. **`zfd_decoder/tests/test_pipeline.py`** -- Existing tests. These MUST all still pass
4. **`zfd_decoder/data/lexicon.csv`** -- Current 92-entry lexicon (6 columns)
5. **`data/lexicon_v2.csv`** -- New 185-entry lexicon (will be placed in data/ during Phase 1)

---

## CRITICAL REQUIREMENTS

**BACKWARD COMPATIBILITY:** All existing tests must pass without modification. The old `lexicon.csv` format must still work if someone passes it in.

**SCHEMA:** lexicon_v2.csv adds 3 columns to the existing 6:
- `croatian` -- Croatian word (e.g., "kost", "ulje", "voda")
- `category` -- Semantic category: ingredient, action, body_part, grammar, condition, equipment, preparation, latin_pharma, measurement, timing, modifier
- `source` -- Provenance: lexicon_v1, miscellany_new, miscellany+voynich

**STATUS VALUES:** CONFIRMED (74), CANDIDATE (23), MISCELLANY (88). MISCELLANY entries are newly mined from medieval pharmaceutical manuscripts. They should be used for glossing but flagged as lower confidence than CONFIRMED.

**DO NOT:**
- Delete or rename `lexicon.csv` (keep as fallback)
- Change the Token dataclass fields in `tokenizer.py` (use existing fields)
- Modify `operators.json`, `suffixes.json`, `gallows.json`, or `mid_word.json`
- Restructure the pipeline stages (1-9 order stays the same)

---

## Phase 1: Data File Placement + Schema Validation

**Goal:** Get `lexicon_v2.csv` into the repo data directory and validate it parses cleanly.

**Files to create/modify:**
- `zfd_decoder/data/lexicon_v2.csv` -- Copy the new lexicon file here
- `zfd_decoder/tests/test_lexicon_v2.py` -- Schema validation tests

**Steps:**
1. Copy `lexicon_v2.csv` to `zfd_decoder/data/lexicon_v2.csv`
2. Create `test_lexicon_v2.py` that validates:
   - File has exactly 9 columns: name, variant, context, gloss, latin, croatian, category, status, source
   - All 185 entries parse without error
   - No duplicate variant values (within same name context)
   - All status values are one of: CONFIRMED, CANDIDATE, MISCELLANY
   - All category values are one of the 11 defined categories
   - Every entry has a non-empty `variant` and `gloss`

**Validation:**
- [ ] `lexicon_v2.csv` is in `zfd_decoder/data/`
- [ ] `python -m pytest zfd_decoder/tests/test_lexicon_v2.py` passes
- [ ] Original `lexicon.csv` still exists untouched

**After completing Phase 1, read this document again to find Phase 2.**

---

## Phase 2: Update StemLexicon to Handle Both Formats

**Goal:** Make `stems.py` load either lexicon format gracefully, exposing new fields when available.

**Files to modify:**
- `zfd_decoder/src/stems.py`

**Changes:**
1. Update `__init__` to detect column count. If `croatian` column exists, store the extra fields. If not, default them to empty string.
2. The `stems` dict value should now include: `name`, `gloss`, `latin`, `status`, `context`, `croatian` (default ""), `category` (default "ingredient"), `source` (default "lexicon_v1")
3. Add a `get_category(self, stem: str) -> str` method that returns the category for a stem, or "unknown" if not found
4. Add a `get_croatian(self, stem: str) -> str` method that returns the Croatian form, or "" if not found
5. Add a `confidence_for_status(self, status: str) -> float` method:
   - CONFIRMED -> 0.30
   - CANDIDATE -> 0.15
   - MISCELLANY -> 0.10

**Key constraint:** `lookup()` and `find_in_text()` signatures do not change. The returned dict just has more keys now.

**Validation:**
- [ ] Load old `lexicon.csv` -- works, no errors, extra fields default gracefully
- [ ] Load new `lexicon_v2.csv` -- works, all 185 entries, new fields populated
- [ ] `get_category("kost")` returns "ingredient"
- [ ] `get_category("nonexistent")` returns "unknown"
- [ ] `confidence_for_status("MISCELLANY")` returns 0.10
- [ ] All existing tests still pass: `python -m pytest zfd_decoder/tests/test_pipeline.py`

**After completing Phase 2, read this document again to find Phase 3.**

---

## Phase 3: Update Pipeline for Category-Aware English Output

**Goal:** Improve `_build_english()` and `_build_croatian()` in `pipeline.py` to produce better output using categories and Croatian forms.

**Files to modify:**
- `zfd_decoder/src/pipeline.py`

**Changes to `process_token()` (Stage 4/5 area):**
1. When `stem_data` is found, use `self.lexicon.confidence_for_status(stem_data['status'])` instead of hardcoded `0.30` for the confidence boost. This means MISCELLANY stems get less confidence than CONFIRMED ones.

**Changes to `_build_croatian()`:**
Currently just returns `token.zfd`. Update to:
```python
def _build_croatian(self, token: Token) -> str:
    parts = []
    if token.operator:
        parts.append(token.operator)
    # Use Croatian form if available, otherwise stem
    if token.stem_known:
        stem_data = self.lexicon.lookup(token.stem)
        croatian = stem_data.get('croatian', '') if stem_data else ''
        parts.append(croatian if croatian else token.stem)
    else:
        parts.append(token.stem)
    if token.suffix:
        parts.append(token.suffix)
    return "".join(parts)
```

**Changes to `_build_english()`:**
Add category-aware glossing after the stem gloss. The category helps disambiguate:

```python
# After the existing stem gloss logic, add category hints for action stems:
if stem_data and stem_data.get('category') == 'action' and not token.operator:
    # Action stems without operators are imperative verbs
    # e.g., "grind" not "grind-noun"
    pass  # gloss is already the verb form
elif stem_data and stem_data.get('category') == 'body_part':
    # Body parts in pharmaceutical context = target/application site
    pass  # gloss is already correct
elif stem_data and stem_data.get('category') == 'condition':
    # Conditions = what's being treated
    pass  # gloss works
```

The main improvement is that `stem_data['gloss']` in v2 is already richer (many entries now have real English glosses where v1 had empty or placeholder text). The category field is for future downstream consumers and diagnostics, not for rewriting the gloss logic.

**Changes to `_generate_diagnostics()`:**
Add a `category_distribution` dict to diagnostics output:
```python
"category_distribution": {category: count for category, count in category_counts.items()}
```
Also add `"miscellany_stems"` count to track how many matches come from the newly mined entries.

**Validation:**
- [ ] `python -m pytest zfd_decoder/tests/test_pipeline.py` -- ALL existing tests pass
- [ ] Token for "sar" still produces english="salt" 
- [ ] Token for "kost" now has `croatian` field = "kost"
- [ ] Diagnostics output includes `category_distribution`
- [ ] MISCELLANY stems get confidence 0.10 instead of 0.30

**After completing Phase 3, read this document again to find Phase 4.**

---

## Phase 4: Update Pipeline Default to Use lexicon_v2

**Goal:** Make lexicon_v2.csv the default, keep lexicon.csv as fallback.

**Files to modify:**
- `zfd_decoder/src/pipeline.py` -- Update `__init__` 
- `zfd_decoder/main.py` -- Add `--lexicon` CLI argument

**Changes to pipeline.py `__init__`:**
```python
def __init__(self, data_dir: str = "data", lexicon_file: str = None):
    data_path = Path(data_dir)
    
    # Prefer lexicon_v2, fall back to lexicon
    if lexicon_file:
        lex_path = Path(lexicon_file)
    elif (data_path / "lexicon_v2.csv").exists():
        lex_path = data_path / "lexicon_v2.csv"
    else:
        lex_path = data_path / "lexicon.csv"
    
    self.operators = OperatorDetector(str(data_path / "operators.json"))
    self.lexicon = StemLexicon(str(lex_path))
    # ... rest unchanged
```

**Changes to main.py:**
Add `--lexicon` argument that passes through to `ZFDPipeline(lexicon_file=args.lexicon)`. Default behavior uses v2 auto-detection.

**Validation:**
- [ ] Pipeline loads lexicon_v2.csv by default when both exist
- [ ] Pipeline falls back to lexicon.csv when v2 is missing
- [ ] `--lexicon path/to/custom.csv` works
- [ ] All existing tests still pass

**After completing Phase 4, read this document again to find Phase 5.**

---

## Phase 5: New Tests for v2 Features

**Goal:** Add tests that exercise the new 96 entries and category-aware features.

**Files to create:**
- `zfd_decoder/tests/test_lexicon_v2_pipeline.py`

**Tests to write:**

```python
def test_v2_entry_count():
    """Lexicon v2 has 185 entries."""
    assert len(pipeline.lexicon.stems) >= 185

def test_miscellany_confidence():
    """MISCELLANY entries get lower confidence than CONFIRMED."""
    # Find a MISCELLANY entry and a CONFIRMED entry
    # Process both through pipeline
    # Assert MISCELLANY token confidence < CONFIRMED token confidence

def test_croatian_output():
    """Croatian layer produces actual Croatian words."""
    token = Token(id="test.v2.1", eva="sar")
    result = pipeline.process_token(token)
    # croatian field should contain "sol" (salt in Croatian)

def test_new_body_part_entries():
    """Body part entries from miscellany mining are accessible."""
    # Test that "glav" (head) or similar new entries resolve

def test_new_action_entries():
    """Action verb entries from miscellany mining are accessible."""
    # Test that action category entries resolve with correct gloss

def test_category_in_diagnostics():
    """Diagnostics include category distribution."""
    result = pipeline.process_folio("qokeedy.chol.sar", "test")
    assert "category_distribution" in result["diagnostics"]

def test_backward_compat_v1():
    """Pipeline works with old lexicon.csv format."""
    old_pipeline = ZFDPipeline(
        data_dir=str(DATA_DIR),
        lexicon_file=str(DATA_DIR / "lexicon.csv")
    )
    token = Token(id="test.v1.1", eva="sar")
    result = old_pipeline.process_token(token)
    assert result.stem_known
    assert "salt" in result.stem_gloss.lower()
```

**Validation:**
- [ ] `python -m pytest zfd_decoder/tests/` -- ALL tests pass (old and new)
- [ ] At least 7 new test functions
- [ ] Tests cover: entry count, confidence tiers, Croatian output, new categories, diagnostics, backward compat

**After completing Phase 5, read this document again to find Phase 6.**

---

## Phase 6: Documentation + Commit

**Goal:** Update docs, clean up, commit with proper message.

**Files to create/modify:**
- `zfd_decoder/CHANGELOG_LEXICON_V2.md` -- Document what changed and why
- `README.md` -- If needed, note the lexicon update

**CHANGELOG content should include:**
- Date: 2025-02-04
- What: lexicon.csv upgraded from 92 to 185 entries (101% growth)
- New columns: croatian, category, source
- New categories: action (32), body_part (22), grammar (21), condition (10), equipment (8), preparation (8), latin_pharma (5), measurement (3), timing (2), modifier (2)
- Source: Medieval pharmaceutical miscellany mining (Pharmacological etc. miscellany 2066895)
- Backward compatible: old lexicon.csv still works as fallback
- Confidence tiers: CONFIRMED (0.30), CANDIDATE (0.15), MISCELLANY (0.10)

**Git commit message:**
```
feat: integrate lexicon_v2 with 185 entries and category-aware glossing

- Upgrade lexicon from 92 to 185 entries (101% growth)
- Add croatian, category, source columns
- Category-aware confidence: CONFIRMED > CANDIDATE > MISCELLANY
- Croatian output layer now produces actual Croatian words
- Diagnostics include category distribution
- Backward compatible with lexicon v1 format
- All existing tests pass, 7+ new tests added
```

**Validation:**
- [ ] CHANGELOG exists and is accurate
- [ ] Git commit is clean (no untracked junk)
- [ ] `python -m pytest zfd_decoder/tests/` -- ALL tests pass one final time

---

## SUCCESS CRITERIA

- [ ] lexicon_v2.csv (185 entries, 9 columns) is in `zfd_decoder/data/`
- [ ] `stems.py` handles both lexicon formats gracefully
- [ ] Pipeline uses lexicon_v2 by default, falls back to v1
- [ ] Confidence tiers: CONFIRMED=0.30, CANDIDATE=0.15, MISCELLANY=0.10
- [ ] Croatian output layer produces real Croatian words
- [ ] Diagnostics include category_distribution
- [ ] All original tests pass unchanged
- [ ] 7+ new tests validate v2 features
- [ ] Clean git commit on `feature/lexicon-v2-integration` branch
- [ ] No changes to operators.json, suffixes.json, gallows.json, mid_word.json, tokenizer.py

---

## DATA FILE REFERENCE

**lexicon_v2.csv schema:**
```
name,variant,context,gloss,latin,croatian,category,status,source
bone,kost,pharmaceutical,bone,os,kost,ingredient,CONFIRMED,lexicon_v1
oil,ol,free or vessels,oil,oleum,ulje,ingredient,CONFIRMED,lexicon_v1
head,glav,body target,head,caput,glava,body_part,MISCELLANY,miscellany_new
grind,sat,preparation,grind/crush,terere,satrti,action,MISCELLANY,miscellany_new
```

**Category counts:**
- ingredient: 72
- action: 32
- body_part: 22
- grammar: 21
- condition: 10
- equipment: 8
- preparation: 8
- latin_pharma: 5
- measurement: 3
- timing: 2
- modifier: 2
