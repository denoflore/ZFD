# Glagolitic Paleographic OCR Pipeline - CC Build Instructions

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

Build a computational paleographic OCR pipeline that takes Voynich manuscript folio scans from Yale Beinecke IIIF, performs glyph-by-glyph identification as Angular Glagolitic cursive letterforms, and produces a proper Glagolitic transcription with Latin transliteration. This replaces the lossy EVA intermediary with a direct Voynich-glyph-to-Glagolitic-letter identification. The output is per-folio transcription files with five layers: scan region, Glagolitic Unicode, Latin transliteration, Croatian shorthand, expanded Croatian.

**End state:** `06_Pipelines/glagolitic_ocr/` directory containing the pipeline scripts, a `transcriptions/` output directory with per-folio JSON and markdown files, and integration into the voynich-edition static site.

---

## REQUIRED READING

Before writing ANY code, read these completely:

1. **`mapping/FINAL_CHARACTER_MAP_v1.md`** - The complete EVA-to-Glagolitic character map with positional analysis (operators, stems, suffixes), Unicode codepoints, and confidence levels. This is the GROUND TRUTH for glyph identification.

2. **`mapping/GLYPH_MAPPING_GLAGOLITIC_VOYNICH.md`** - Tier 1-4 mappings between Voynichese shapes and Angular Glagolitic letterforms. Contains the Unicode lookup table (U+2C00-U+2C5F), structural similarity notes, and abbreviation system hypothesis.

3. **`02_Transcriptions/LSI_ivtff_0d.txt`** - The IVTFF consensus transcription (Stolfi/Landini/Zandbergen). Use the `;H` lines as primary reference. Each line is tagged with folio ID, line number, panel position.

4. **`WHY_GLAGOLITIC.md`** - The behavioral paleographic case for Angular Glagolitic identification. Contains the stroke logic comparison, operator detection results, and ligature analysis.

5. **`voynich-edition/scripts/build_data.py`** - Existing data pipeline. Your pipeline should output data compatible with this system. Check the `folio_metadata.json` schema.

---

## CRITICAL REQUIREMENTS

**IMAGE SOURCE:** Yale Beinecke IIIF API. The manifest is at `https://collections.library.yale.edu/manifests/2002046` (IIIF v3). Image IDs are sequential starting at `1006074` (front cover). The folio-to-IIIF-ID mapping is embedded in the manifest. Pattern: `https://collections.library.yale.edu/iiif/2/{IMAGE_ID}/full/{WIDTH},/0/default.jpg`. Region crops: `https://collections.library.yale.edu/iiif/2/{IMAGE_ID}/{X},{Y},{W},{H}/{OUTPUT_WIDTH},/0/default.jpg`.

**210 folios total** in the manifest. Build the complete folio-label-to-IIIF-ID lookup table from the manifest at startup.

**GLAGOLITIC UNICODE RANGE:** U+2C00 to U+2C5F (Glagolitic block). The pipeline MUST output actual Unicode characters, not transliteration approximations.

**THE KEY INSIGHT:** This is NOT traditional OCR. We are not training a neural network. We are using Claude's vision capability (YOU can see images) combined with the character map to produce glyph-by-glyph Glagolitic identifications. The pipeline is: download scan > crop text regions > for each line, use the IVTFF transcription as positional guide > identify each glyph cluster as its Glagolitic equivalent using the character map > output five-layer interlinear.

**DO NOT:**
- Use any external OCR library (Tesseract, etc.). This is behavioral paleographic identification, not pixel extraction.
- Guess at mappings not in the character map. Mark uncertain glyphs with `[?]`.
- Break the existing voynich-edition build. Your output should EXTEND it, not replace it.
- Use API keys for Claude API calls. Everything runs locally via vision inspection of downloaded images.

---

## Phase 1: IIIF Manifest Parser and Image Downloader

**Goal:** Build the folio-to-image lookup and a reliable downloader that fetches any folio scan at any resolution or region crop.

**Files to create:**
- `06_Pipelines/glagolitic_ocr/iiif_manifest.py` - Parse the Beinecke IIIF v3 manifest, build `{folio_label: iiif_base_url}` dictionary, cache locally as `data/folio_iiif_map.json`
- `06_Pipelines/glagolitic_ocr/image_fetch.py` - Download functions: `fetch_folio(folio_id, width=800)`, `fetch_region(folio_id, x, y, w, h, output_width=800)`, `fetch_full_res(folio_id)`. Save to `06_Pipelines/glagolitic_ocr/scans/`. Respect rate limits (1 req/sec).

**Validation:**
- [ ] `folio_iiif_map.json` contains 210 entries
- [ ] `fetch_folio("13v")` downloads a valid JPEG (>100KB)
- [ ] `fetch_region("13v", 0, 0, 2000, 500, 800)` returns a cropped text region
- [ ] All folio labels match those in `02_Transcriptions/LSI_ivtff_0d.txt`

**After completing Phase 1, read this document again to find Phase 2.**

---

## Phase 2: IVTFF Parser and Line Extractor

**Goal:** Parse the IVTFF transcription file into a structured per-folio, per-line data structure with clean EVA tokens.

**Files to create:**
- `06_Pipelines/glagolitic_ocr/ivtff_parser.py` - Parse `LSI_ivtff_0d.txt`:
  - Extract `;H` transcriber lines (primary)
  - For each folio: list of lines, each line has: `line_number`, `panel`, `eva_tokens` (list of words), `raw_text`, `has_plant_marker` (bool, from `<!plant>` tags), `line_break_type` (from `<->`, `<$>` markers)
  - Handle special markup: `!` (uncertain), `*` (illegible), `<->` (line continues around illustration), `<$>` (paragraph end)
  - Output: `data/ivtff_parsed.json`

**Data structure per folio:**
```json
{
  "f13v": {
    "metadata": {"section": "herbal_a", "quire": 3},
    "lines": [
      {
        "line_num": 1,
        "panel": "P0",
        "eva_raw": "koair.chtoiin.otchy.kchod.otol.otchy.octhos",
        "eva_words": ["koair", "chtoiin", "otchy", "kchod", "otol", "otchy", "octhos"],
        "uncertain_chars": [],
        "has_plant_break": false,
        "paragraph_end": false
      }
    ]
  }
}
```

**Validation:**
- [ ] Parser handles all 210+ folios without errors
- [ ] f13v has exactly 10 lines
- [ ] f1r line 1 contains "fachys" or similar known opening
- [ ] Plant markers (`<!plant>`) correctly flagged
- [ ] Uncertain characters (`!`) tracked per position

**After completing Phase 2, read this document again to find Phase 3.**

---

## Phase 3: Glagolitic Transliterator Engine

**Goal:** Build the core engine that converts EVA token sequences to five-layer interlinear output using the character maps.

**Files to create:**
- `06_Pipelines/glagolitic_ocr/glagolitic_engine.py` - The transliteration engine:

**Layer 1 - EVA (input):** Clean EVA from IVTFF parser.

**Layer 2 - Glagolitic Unicode:** Apply the mapping from `FINAL_CHARACTER_MAP_v1.md`:
  - Handle digraphs FIRST: `ch` -> Ⱈ (U+2C17), `sh` -> Ⱊ (U+2C1A), `cth` -> Ⱌ+Ⱅ, `cph` -> Ⱌ+Ⱂ
  - Then single chars: `a` -> Ⰰ, `d` -> Ⰴ, `e` -> Ⰵ, `i` -> Ⰹ, `k` -> Ⰼ, `l` -> Ⰾ, `m` -> Ⰿ, `n` -> Ⱀ, `o` -> Ⱁ, `p` -> Ⱂ, `q` -> ⰼⱁ (ligature), `r` -> Ⱃ, `s` -> Ⱄ, `t` -> Ⱅ, `y` -> Ⱏ
  - Mark unmapped characters with `[?X]` where X is the EVA char
  - Track confidence per character (HIGH/MEDIUM/LOW from the map)

**Layer 3 - Latin transliteration:** Convert Glagolitic to standard Latin values:
  - Ⰰ -> a, Ⰴ -> d, Ⰵ -> e, Ⰹ -> i, Ⰼ -> k, Ⰾ -> l, Ⰿ -> m/n, Ⱀ -> n, Ⱁ -> o, Ⱂ -> p, Ⱃ -> r, Ⱄ -> s, Ⱅ -> t, Ⱇ -> f, Ⱈ -> h/x, Ⱊ -> š, Ⱏ -> y/ъ

**Layer 4 - Croatian shorthand:** Apply the morpheme system from the character map:
  - Operator detection: word-initial `q`/`ch`/`sh`/`o`/`d` -> prefix markers
  - Stem extraction: medial content
  - Suffix identification: word-final `y`/`n`/`r`/`l`/`m`

**Layer 5 - Expanded Croatian:** Use the 141 validated morphemes from `04_Morphemes/` to expand abbreviations:
  - `ol` -> oil/ulje
  - `kost` -> bone
  - `ed` -> root/base
  - `dain`/`daiin` -> dati (give/dose)
  - `thor` -> boil
  - etc.

**Output per word:**
```json
{
  "eva": "qokol",
  "glagolitic": "ⰼⱁⱁⰼⱁⰾ",
  "latin": "kookol",
  "croatian_short": "kostol",
  "croatian_expanded": "kost-ol (bone-oil)",
  "english": "bone oil",
  "confidence": 0.85,
  "morpheme_breakdown": {"operator": "qo/ko", "stem": "k/kost", "suffix": "ol"}
}
```

**Validation:**
- [ ] `transliterate("qokol")` produces Glagolitic `ⰼⱁⱁⰼⱁⰾ` 
- [ ] `transliterate("daiin")` produces `ⰴⰰⰹⰹⱀ`
- [ ] `transliterate("chtoiin")` produces Ⱈ-initial form
- [ ] Digraphs handled before singles (no double-conversion)
- [ ] Unknown chars marked, not silently dropped
- [ ] All 141 morphemes from morpheme files loaded and applied

**After completing Phase 3, read this document again to find Phase 4.**

---

## Phase 4: Full Corpus Transcription Generator

**Goal:** Run the engine across all 201 recipe folios and produce per-folio output files.

**Files to create:**
- `06_Pipelines/glagolitic_ocr/run_transcription.py` - Orchestrator that:
  1. Loads `ivtff_parsed.json`
  2. For each folio, for each line, for each word: run through glagolitic_engine
  3. Output per-folio files in two formats:

**Format A - JSON** (`transcriptions/json/f{folio}.json`):
```json
{
  "folio": "f13v",
  "iiif_url": "https://collections.library.yale.edu/iiif/2/1006099",
  "section": "herbal_a",
  "lines": [
    {
      "line_num": 1,
      "layers": {
        "eva": "koair chtoiin otchy kchod otol otchy octhos",
        "glagolitic": "...",
        "latin": "...",
        "croatian_short": "...",
        "croatian_expanded": "...",
        "english": "..."
      },
      "words": [/* per-word breakdown */],
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

**Format B - Markdown** (`transcriptions/md/f{folio}.md`):
```markdown
# Folio 13v - Glagolitic Transcription

**Section:** Herbal A | **Quire:** 3 | **IIIF:** [View scan](url)

## Line 1
| Layer | Text |
|-------|------|
| EVA | koair chtoiin otchy kchod otol otchy octhos |
| Glagolitic | ... |
| Latin | ... |
| Croatian | ... |
| English | ... |
```

- `06_Pipelines/glagolitic_ocr/generate_stats.py` - Corpus-wide statistics:
  - Total glyphs processed
  - Confidence distribution
  - Most frequent Glagolitic characters
  - Coverage percentage (mapped vs unmapped)
  - Per-section statistics

**Validation:**
- [ ] 201 JSON files generated (one per recipe folio)
- [ ] 201 markdown files generated
- [ ] No folio has 0 lines
- [ ] Overall confidence average computed
- [ ] f13v output matches the known decode (bone-oil, rose cream)
- [ ] Statistics JSON generated with corpus totals

**After completing Phase 4, read this document again to find Phase 5.**

---

## Phase 5: Voynich Edition Integration

**Goal:** Integrate the Glagolitic transcriptions into the existing voynich-edition static site, adding a Glagolitic layer to each folio page.

**Files to modify:**
- `voynich-edition/scripts/build_data.py` - Add loading of `transcriptions/json/` files into `folio_metadata.json`, adding a `glagolitic_transcription` field per folio
- `voynich-edition/scripts/build_site.py` - Update folio HTML template to include:
  - Toggle button: "Show Glagolitic / Show EVA"
  - Five-layer interlinear display with Glagolitic Unicode rendered in proper font
  - Confidence highlighting (green/yellow/red per word)
  - Per-line statistics

**Files to create:**
- `voynich-edition/css/glagolitic.css` - Styling for Glagolitic text display. Use `font-family: 'Noto Sans Glagolitic', 'Segoe UI Historic', sans-serif;` for Glagolitic Unicode rendering.
- `voynich-edition/js/interlinear-toggle.js` - Toggle between EVA and Glagolitic views

**Also create:**
- `06_Pipelines/glagolitic_ocr/README.md` - Pipeline documentation: what it does, how to run it, dependencies, data flow diagram

**Validation:**
- [ ] `build_data.py` incorporates Glagolitic data without breaking existing build
- [ ] `build_site.py` generates folio pages with Glagolitic layer
- [ ] Toggle switches between EVA and Glagolitic views
- [ ] Glagolitic Unicode characters render correctly in HTML
- [ ] README documents the complete pipeline
- [ ] All 201 folio pages updated

**After completing Phase 5, read this document again to find Phase 6.**

---

## Phase 6: Scholarly Output and Validation Report

**Goal:** Generate publication-ready output documenting the Glagolitic identification.

**Files to create:**
- `06_Pipelines/glagolitic_ocr/validation_report.py` - Generate:
  - `reports/GLAGOLITIC_TRANSCRIPTION_REPORT.md` - Full scholarly report:
    - Methodology (behavioral paleographic OCR, not pixel extraction)
    - Character map with Unicode codepoints and confidence levels
    - Corpus statistics (coverage, confidence distribution)
    - Sample transcriptions (f13v rose cream, f56r, f1r)
    - Comparison: EVA vs Glagolitic for same text
    - Known limitations and uncertain mappings
  - `reports/folio_confidence_matrix.csv` - Per-folio confidence scores for bulk analysis
  - `reports/unmapped_characters.csv` - All instances of unmapped or uncertain glyphs

**Validation:**
- [ ] Report generated with all sections
- [ ] CSV files parseable
- [ ] Sample transcriptions verified against existing recipe files
- [ ] Report includes the 5-layer f13v example

---

## SUCCESS CRITERIA

- [ ] Complete IIIF manifest parsed with 210 folio mappings
- [ ] IVTFF transcription parsed for all folios
- [ ] Glagolitic transliteration engine handles all EVA characters in the map
- [ ] 201 per-folio JSON and markdown transcription files generated
- [ ] Five-layer interlinear output: EVA > Glagolitic Unicode > Latin > Croatian shorthand > Expanded Croatian
- [ ] Voynich-edition static site updated with Glagolitic toggle
- [ ] Scholarly validation report generated
- [ ] Pipeline is re-runnable (idempotent)
- [ ] All output committed to `denoflore/ZFD` repository

---

## REFERENCE: Key IIIF URLs

```
Manifest: https://collections.library.yale.edu/manifests/2002046
f1r:   https://collections.library.yale.edu/iiif/2/1006076
f13v:  https://collections.library.yale.edu/iiif/2/1006099
f56r:  https://collections.library.yale.edu/iiif/2/1006184
f88r:  https://collections.library.yale.edu/iiif/2/1037112
f99r:  https://collections.library.yale.edu/iiif/2/1006246
f103r: https://collections.library.yale.edu/iiif/2/1006254
Image pattern: {base}/full/{width},/0/default.jpg
Region crop: {base}/{x},{y},{w},{h}/{output_width},/0/default.jpg
```

## REFERENCE: Glagolitic Unicode Quick Map

```
EVA -> Glagolitic -> Unicode -> Latin
a   -> Ⰰ -> U+2C00 -> a
d   -> Ⰴ -> U+2C04 -> d
e   -> Ⰵ -> U+2C05 -> e
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
y   -> Ⱏ -> U+2C1F -> y/ъ
f   -> Ⱇ -> U+2C17 -> f
ch  -> Ⱈ -> U+2C18 -> h/x
sh  -> Ⱊ -> U+2C1A -> š
```
