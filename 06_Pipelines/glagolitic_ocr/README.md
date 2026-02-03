# Glagolitic OCR Pipeline

Automated transliteration of Voynich Manuscript EVA transcription into Angular Glagolitic Unicode, supporting the ZFD hypothesis.

## Overview

This pipeline transforms the IVTFF consensus transcription (Takahashi) through a five-layer interlinear format:

1. **EVA** - Extended Voynich Alphabet (input)
2. **Glagolitic** - Angular Glagolitic Unicode (U+2C00-2C5F)
3. **Latin** - Standard Latin phonetic transliteration
4. **Croatian** - Abbreviated/shorthand Croatian
5. **English** - Expanded meaning with morpheme analysis

## Quick Start

```bash
# Parse IVTFF transcription
python3 ivtff_parser.py

# Run transliteration on full corpus
python3 run_corpus.py --validate

# Transliterate single word
python3 transliteration_engine.py --word "daiin"
```

## Directory Structure

```
glagolitic_ocr/
├── ivtff_parser.py           # Phase 2: IVTFF parser
├── transliteration_engine.py # Phase 3: 5-layer transliteration
├── run_corpus.py             # Phase 4: Full corpus processing
├── character_reference.py    # Glagolitic alphabet data
├── image_processor.py        # Image preprocessing (requires OpenCV)
├── glyph_extractor.py        # Character segmentation (requires OpenCV)
├── glagolitic_ocr.py         # Main OCR pipeline (requires OpenCV)
├── data/
│   ├── ivtff_parsed.json     # Parsed IVTFF transcription
│   ├── glagolitic_alphabet.json
│   └── folio_iiif_map.json   # Folio-to-IIIF URL mapping
├── transcriptions/
│   ├── json/                 # Per-folio JSON transcriptions
│   ├── md/                   # Per-folio Markdown transcriptions
│   ├── CORPUS_STATISTICS.json
│   └── CORPUS_STATISTICS.md
└── reports/
    ├── GLAGOLITIC_TRANSCRIPTION_REPORT.md
    ├── confidence_matrix.csv
    └── unmapped_glyphs.csv
```

## Pipeline Phases

### Phase 1: Character Reference (Complete)
- 33 Glagolitic character mappings
- EVA-to-Glagolitic lookup tables
- Template matching infrastructure

### Phase 2: IVTFF Parser
```bash
python3 ivtff_parser.py --validate --sample f13v
```
- Parses IVTFF consensus transcription
- Extracts `;H` (Takahashi) lines as primary
- Outputs: `data/ivtff_parsed.json`

### Phase 3: Transliteration Engine
```bash
python3 transliteration_engine.py --validate
```
- Digraph-priority processing (ch, sh before c+h, s+h)
- Five-layer output for every word
- Morpheme recognition for pharmaceutical terms

### Phase 4: Corpus Run
```bash
python3 run_corpus.py --validate
```
- Processes all 225 folios
- Generates JSON + Markdown per folio
- Produces corpus statistics

### Phase 5: Voynich Edition Integration
The transcriptions integrate with `voynich-edition/` static site:
- Glagolitic CSS for Unicode display
- Toggle between EVA/Glagolitic views
- Confidence-coded word highlighting

### Phase 6: Validation Report
- `reports/GLAGOLITIC_TRANSCRIPTION_REPORT.md` - Scholarly documentation
- `reports/confidence_matrix.csv` - Per-folio metrics
- `reports/unmapped_glyphs.csv` - Unmapped character instances

## Usage Examples

### Transliterate a single word
```bash
$ python3 transliteration_engine.py --word "qokol"

EVA:        qokol
Glagolitic: ⰼⱁⰼⱁⰾ
Latin:      kokol
Croatian:   qokol
English:    which/that [k] -ol (oil/liquid)
Confidence: 1.00
```

### Process a single folio
```bash
python3 run_corpus.py --sample f13v
```

### View corpus statistics
```bash
cat transcriptions/CORPUS_STATISTICS.md
```

## Dependencies

**Core (no external deps):**
- Python 3.8+
- Standard library only

**Image Processing (optional):**
- OpenCV (`pip install opencv-python`)
- NumPy (`pip install numpy`)

Image processing is only needed for the OCR components (`glagolitic_ocr.py`, `image_processor.py`, `glyph_extractor.py`). The transliteration pipeline works without them.

## Output Formats

### JSON (per folio)
```json
{
  "folio": "f13v",
  "iiif_url": "https://...",
  "lines": [
    {
      "line_num": 1,
      "layers": {
        "eva": "koair chtoiin otchy kchod",
        "glagolitic": "ⰼⱁⰰⰹⱃ Ⱈⱅⱁⰹⰹⱀ ...",
        "latin": "koair htoiin ...",
        "croatian_short": "...",
        "croatian_expanded": "..."
      },
      "confidence_avg": 0.98
    }
  ],
  "statistics": {...}
}
```

### Markdown (per folio)
```markdown
# Folio F13V - Glagolitic Transcription

## Line 1
| Layer | Text |
|-------|------|
| EVA | koair chtoiin otchy kchod |
| Glagolitic | ⰼⱁⰰⰹⱃ Ⱈⱅⱁⰹⰹⱀ ... |
...
```

## Validation

Run validation on all phases:
```bash
python3 ivtff_parser.py --validate
python3 transliteration_engine.py --validate
python3 run_corpus.py --validate
```

Expected output:
- All checks should show `[PASS]`
- f13v should have exactly 10 lines
- f1r line 1 should start with "fachys"
- No zero-word folios

## Known Limitations

1. **Source Dependency**: Output accuracy depends on IVTFF transcription accuracy
2. **Morpheme Coverage**: ~20 validated pharmaceutical terms; unknown morphemes marked with `[?]`
3. **Font Requirements**: Requires Glagolitic Unicode font for proper display

## Integration with Voynich Edition

The transcriptions are automatically loaded into the digital edition:
```bash
cd voynich-edition/scripts
python3 build_data.py  # Loads Glagolitic transcriptions
python3 build_site.py  # Generates HTML with 5-layer display
```

## License

CC BY-SA 4.0 - Part of the ZFD Project

## References

- [IVTFF Transcription](http://www.voynich.nu/)
- [EVA Encoding](http://www.voynich.nu/extra/eva.html)
- [Glagolitic Unicode](https://www.unicode.org/charts/PDF/U2C00.pdf)
