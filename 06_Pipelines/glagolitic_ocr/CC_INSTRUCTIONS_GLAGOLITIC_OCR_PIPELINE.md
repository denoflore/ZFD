# Glagolitic OCR Pipeline - Phases 2-6 (Phase 1 COMPLETE)

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

## STATUS

**Phase 1 is COMPLETE.** The following files already exist in `06_Pipelines/glagolitic_ocr/`:
- `glagolitic_ocr.py` (420 lines) - Main pipeline with GlagoliticOCR class, template matching, image processing orchestration
- `character_reference.py` (490 lines) - 33 Glagolitic chars, 21 EVA-mapped, transliteration functions
- `image_processor.py` (331 lines) - ManuscriptImageProcessor: threshold, deskew, line segmentation
- `glyph_extractor.py` (345 lines) - GlyphExtractor: contour-based character extraction
- `data/glagolitic_alphabet.json` - Complete alphabet reference
- `data/folio_iiif_map.json` - 210 Beinecke IIIF folio-to-image-ID mappings

**Your job: Build Phases 2-6 on top of Phase 1.**

---

## REQUIRED READING

Before writing ANY code, read these files completely:

1. **`06_Pipelines/glagolitic_ocr/character_reference.py`** - The existing Glagolitic character data. Your transliteration engine MUST use this as its foundation, not duplicate it.
2. **`mapping/FINAL_CHARACTER_MAP_v1.md`** - The complete EVA-to-Glagolitic character map with positional analysis, Unicode codepoints, and confidence levels.
3. **`02_Transcriptions/LSI_ivtff_0d.txt`** - The IVTFF consensus transcription. Use `;H` lines as primary. Each line tagged with folio ID, line number, panel position.
4. **`06_Pipelines/glagolitic_ocr/data/folio_iiif_map.json`** - Pre-built folio-to-IIIF-URL mapping.
5. **`voynich-edition/scripts/build_data.py`** - Existing data pipeline. Your output must be compatible.

---

## CRITICAL REQUIREMENTS

**GLAGOLITIC UNICODE RANGE:** U+2C00 to U+2C5F. Output MUST be actual Unicode characters.

**FIVE-LAYER OUTPUT:** Every word must produce all five layers:
1. EVA (from IVTFF)
2. Glagolitic Unicode
3. Latin transliteration
4. Croatian shorthand
5. Expanded Croatian / English

**DIGRAPH PRIORITY:** When transliterating EVA to Glagolitic, ALWAYS process digraphs before singles: `ch` before `c`+`h`, `sh` before `s`+`h`, `cth` before `c`+`t`+`h`.

**IIIF IMAGE URLS:**
```
Base pattern: https://collections.library.yale.edu/iiif/2/{IMAGE_ID}/full/{WIDTH},/0/default.jpg
Region crop:  https://collections.library.yale.edu/iiif/2/{IMAGE_ID}/{X},{Y},{W},{H}/{OUTPUT_WIDTH},/0/default.jpg
```
The `folio_iiif_map.json` has the complete mapping. Load it, don't re-derive it.

**DO NOT:**
- Modify Phase 1 files (glagolitic_ocr.py, character_reference.py, image_processor.py, glyph_extractor.py)
- Use external OCR libraries
- Guess at mappings not in the character map. Mark uncertain glyphs with `[?]`
- Break the existing voynich-edition build

---

## Phase 2: IVTFF Parser and Line Extractor

**Goal:** Parse the IVTFF transcription file into a structured per-folio, per-line data structure with clean EVA tokens.

**Files to create:**
- `06_Pipelines/glagolitic_ocr/ivtff_parser.py` - Parse `02_Transcriptions/LSI_ivtff_0d.txt`:
  - Extract `;H` transcriber lines (primary)
  - For each folio: list of lines, each line has: `line_number`, `panel`, `eva_tokens` (list of words), `raw_text`
  - Handle special markup: `!` (uncertain), `*` (illegible), `<->` (line continues), `<$>` (paragraph end)
  - Handle period separators between words (`.` in IVTFF = word boundary)
  - Output: `06_Pipelines/glagolitic_ocr/data/ivtff_parsed.json`

**Data structure per folio:**
```json
{
  "f13v": {
    "lines": [
      {
        "line_num": 1,
        "panel": "P",
        "eva_raw": "koair.chtoiin.otchy.kchod.otol.otchy.octhos",
        "eva_words": ["koair", "chtoiin", "otchy", "kchod", "otol", "otchy", "octhos"],
        "uncertain_positions": [],
        "illegible_positions": []
      }
    ],
    "total_lines": 10,
    "total_words": 42
  }
}
```

**Validation:**
- [ ] Parser handles all folios without errors
- [ ] f13v has exactly 10 lines (verify against IVTFF)
- [ ] f1r line 1 starts with expected content
- [ ] Word count per folio is reasonable (no zero-line folios, no 1000-word folios)
- [ ] Uncertain/illegible markers tracked
- [ ] Print summary: total folios, total lines, total words

**After completing Phase 2, read this document again to find Phase 3.**

---

## Phase 3: Glagolitic Transliteration Engine

**Goal:** Build the core engine that converts EVA token sequences to five-layer interlinear output.

**Files to create:**
- `06_Pipelines/glagolitic_ocr/transliteration_engine.py` - The five-layer converter:

**IMPORT** the existing `character_reference.py` data. Build on it, don't replace it.

**Layer 1 - EVA:** Clean EVA from IVTFF parser (input).

**Layer 2 - Glagolitic Unicode:** Apply mapping, digraphs first:
```python
DIGRAPH_MAP = {
    'ch': 'Ⱈ',    # U+2C18, Xer, /x/
    'sh': 'Ⱊ',    # U+2C1A, Sha, /sh/
    'cth': 'ⰽⱅⱈ', # compound gallows
    'cph': 'ⰽⱂⱈ', # compound gallows
    'ckh': 'ⰽⰼⱈ', # compound gallows
    'cfh': 'ⰽⱇⱈ', # compound gallows
    'ii': 'ⰹⰹ',   # doubled i
}

SINGLE_MAP = {
    'a': 'Ⰰ', 'd': 'Ⰴ', 'e': 'Ⰵ', 'f': 'Ⱇ',
    'g': 'Ⰳ', 'i': 'Ⰹ', 'k': 'Ⰼ', 'l': 'Ⰾ',
    'm': 'Ⰿ', 'n': 'Ⱀ', 'o': 'Ⱁ', 'p': 'Ⱂ',
    'q': 'ⰼⱁ',  # ko ligature
    'r': 'Ⱃ', 's': 'Ⱄ', 't': 'Ⱅ', 'y': 'Ⱏ',
}
```

**Layer 3 - Latin transliteration:** Glagolitic to standard Latin phonetic values.

**Layer 4 - Croatian shorthand:** Identify operator/stem/suffix structure.

**Layer 5 - Expanded Croatian + English:** Use morpheme database. Load morphemes from `04_Morphemes/` if available, otherwise use these core validated morphemes:
```python
MORPHEMES = {
    'ol': ('ulje', 'oil'),
    'kost': ('kost', 'bone'),
    'ed': ('korijen', 'root/base'),
    'dain': ('dati', 'give/dose'),
    'daiin': ('dati', 'give/dose'),
    'thor': ('kuhati', 'boil'),
    'kor': ('korijen', 'root'),
    'kar': ('vatra', 'fire/heat'),
    'sol': ('sol', 'salt'),
    'ros': ('ruza', 'rose'),
}
```

**Public API:**
```python
def transliterate_word(eva_word: str) -> dict:
    """Returns {eva, glagolitic, latin, croatian_short, croatian_expanded, english, confidence}"""

def transliterate_line(eva_line: str) -> list[dict]:
    """Splits on spaces, transliterates each word"""

def transliterate_folio(folio_data: dict) -> dict:
    """Processes all lines in a folio"""
```

**Validation:**
- [ ] `transliterate_word("qokol")` returns Glagolitic containing `ⰼⱁ` (ko ligature for q)
- [ ] `transliterate_word("daiin")` returns Glagolitic `ⰴⰰⰹⰹⱀ`
- [ ] `transliterate_word("chtoiin")` starts with Ⱈ (ch digraph handled before c+h)
- [ ] `transliterate_word("shedy")` starts with Ⱊ (sh digraph)
- [ ] Unknown chars produce `[?X]` markers, not crashes
- [ ] All 5 layers populated for every word
- [ ] Print 3 test words with full 5-layer output

**After completing Phase 3, read this document again to find Phase 4.**

---

## Phase 4: Full Corpus Transcription Run

**Goal:** Run the transliteration engine across all folios and produce per-folio output files.

**Files to create:**
- `06_Pipelines/glagolitic_ocr/run_corpus.py` - Orchestrator:
  1. Load `data/ivtff_parsed.json` (from Phase 2)
  2. For each folio, for each line, for each word: run through transliteration engine
  3. Output two formats per folio:

**JSON output** (`06_Pipelines/glagolitic_ocr/transcriptions/json/f{folio}.json`):
```json
{
  "folio": "f13v",
  "iiif_url": "https://collections.library.yale.edu/iiif/2/1006099",
  "lines": [
    {
      "line_num": 1,
      "layers": {
        "eva": "koair chtoiin otchy kchod otol otchy octhos",
        "glagolitic": "...",
        "latin": "...",
        "croatian_short": "...",
        "croatian_expanded": "..."
      },
      "words": [{"eva": "koair", "glagolitic": "...", "latin": "...", "confidence": 0.8}],
      "confidence_avg": 0.78
    }
  ],
  "statistics": {
    "total_words": 42,
    "high_confidence": 28,
    "medium_confidence": 10,
    "low_confidence": 4,
    "unmapped": 0
  }
}
```

**Markdown output** (`06_Pipelines/glagolitic_ocr/transcriptions/md/f{folio}.md`):
```markdown
# Folio 13v - Glagolitic Transcription

**IIIF:** [View scan](url)

## Line 1
| Layer | Text |
|-------|------|
| EVA | koair chtoiin otchy kchod otol otchy octhos |
| Glagolitic | ... |
| Latin | ... |
| Croatian | ... |
| English | ... |
```

- `06_Pipelines/glagolitic_ocr/corpus_stats.py` - Generate corpus-wide statistics:
  - `transcriptions/CORPUS_STATISTICS.json` - Totals, per-folio confidence, character frequencies
  - `transcriptions/CORPUS_STATISTICS.md` - Human-readable summary

**Validation:**
- [ ] JSON file count matches number of folios with text
- [ ] Markdown file count matches JSON count
- [ ] No folio produces 0 words
- [ ] f13v output matches known decode (bone-oil, rose cream vocabulary)
- [ ] Corpus statistics generated with totals
- [ ] Print summary: X folios processed, Y total words, Z% average confidence

**After completing Phase 4, read this document again to find Phase 5.**

---

## Phase 5: Voynich Edition Integration

**Goal:** Add the Glagolitic layer to the existing voynich-edition static site.

**Files to modify:**
- `voynich-edition/scripts/build_data.py` - Load transcription JSON files, add `glagolitic_transcription` field to `folio_metadata.json`
- `voynich-edition/scripts/build_site.py` - Update folio HTML template:
  - Add toggle button: "Show Glagolitic / Show EVA"
  - Five-layer interlinear display with Glagolitic Unicode
  - Color-coded confidence per word (green > 0.8, yellow > 0.5, red < 0.5)

**Files to create:**
- `voynich-edition/css/glagolitic.css` - Glagolitic text styling. Font stack: `'Noto Sans Glagolitic', 'Segoe UI Historic', sans-serif;`
- `voynich-edition/js/interlinear.js` - Toggle between EVA and Glagolitic views

**Validation:**
- [ ] `build_data.py` runs without errors
- [ ] `build_site.py` generates folio pages with Glagolitic layer
- [ ] HTML pages contain Glagolitic Unicode characters
- [ ] Toggle JS works (inspect the generated HTML for both views)
- [ ] Existing folio pages not broken

**After completing Phase 5, read this document again to find Phase 6.**

---

## Phase 6: Validation Report

**Goal:** Generate a scholarly validation report documenting the pipeline and its output.

**Files to create:**
- `06_Pipelines/glagolitic_ocr/reports/GLAGOLITIC_TRANSCRIPTION_REPORT.md`:
  - Methodology: behavioral paleographic OCR, not pixel extraction
  - Character map table with all 33 Glagolitic chars, EVA mappings, confidence
  - Corpus statistics: coverage, confidence distribution
  - Sample transcriptions: f13v (rose cream), f1r, f56r with full 5-layer output
  - EVA vs Glagolitic comparison for same text
  - Known limitations and uncertain mappings

- `06_Pipelines/glagolitic_ocr/reports/confidence_matrix.csv` - Per-folio: folio_id, total_words, high_conf, med_conf, low_conf, unmapped, avg_confidence

- `06_Pipelines/glagolitic_ocr/reports/unmapped_glyphs.csv` - All unmapped character instances: folio, line, position, eva_char, context

- `06_Pipelines/glagolitic_ocr/README.md` - Pipeline documentation: what it does, how to run, dependencies, data flow

**Validation:**
- [ ] Report contains all sections
- [ ] CSVs are parseable
- [ ] README includes usage examples
- [ ] Sample transcriptions verified correct

---

## SUCCESS CRITERIA

- [ ] IVTFF parsed for all folios (Phase 2)
- [ ] Transliteration engine handles all mapped EVA chars (Phase 3)
- [ ] Per-folio JSON + markdown for all text folios (Phase 4)
- [ ] Five-layer output: EVA > Glagolitic Unicode > Latin > Croatian > English
- [ ] Voynich-edition updated with Glagolitic toggle (Phase 5)
- [ ] Validation report + statistics generated (Phase 6)
- [ ] Pipeline re-runnable (idempotent)
- [ ] All committed to `denoflore/ZFD` main branch

---

## REFERENCE: Glagolitic Unicode Quick Map

```
EVA -> Glagolitic -> Unicode -> Latin
a   -> Ⰰ -> U+2C00 -> a
d   -> Ⰴ -> U+2C04 -> d
e   -> Ⰵ -> U+2C05 -> e
f   -> Ⱇ -> U+2C17 -> f
g   -> Ⰳ -> U+2C03 -> g
i   -> Ⰹ -> U+2C09 -> i
k   -> Ⰼ -> U+2C0C -> k
l   -> Ⰾ -> U+2C0E -> l
m   -> Ⰿ -> U+2C0F -> m
n   -> Ⱀ -> U+2C10 -> n
o   -> Ⱁ -> U+2C11 -> o
p   -> Ⱂ -> U+2C12 -> p
q   -> ⰼⱁ -> ligature -> ko
r   -> Ⱃ -> U+2C13 -> r
s   -> Ⱄ -> U+2C14 -> s
t   -> Ⱅ -> U+2C15 -> t
y   -> Ⱏ -> U+2C1F -> y

DIGRAPHS (process FIRST):
ch  -> Ⱈ -> U+2C18 -> h/x
sh  -> Ⱊ -> U+2C1A -> sh
```
