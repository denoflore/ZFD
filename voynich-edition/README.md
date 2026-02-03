# Voynich Digital Edition

An open-source annotated digital edition of the Voynich Manuscript, based on the Zuger Functional Decipherment (ZFD).

## What This Is

This edition presents the Voynich Manuscript (Beinecke MS 408) as what the ZFD reveals it to be: a **Ragusan pharmaceutical SOP manual** from the 14th-15th century. Each folio is treated as a page in that manual, with:

- **Manuscript scans** from Internet Archive IIIF
- **Interlinear translations** (Voynichese > Croatian > Expanded > English)
- **Ingredient analysis** with Latin pharmaceutical terms
- **SOP chain visualization** showing procedural relationships between folios

## Quick Start

### View Locally

Simply open `index.html` in a web browser:

```bash
cd voynich-edition
open index.html  # macOS
# or
xdg-open index.html  # Linux
# or
start index.html  # Windows
```

### Regenerate the Site

If you modify the source data, regenerate the HTML:

```bash
# Generate JSON data from recipe files
python3 scripts/build_data.py

# Build static HTML pages
python3 scripts/build_site.py
```

## Directory Structure

```
voynich-edition/
├── index.html              # Landing page with section navigation
├── folios/                 # 201 individual folio pages
│   ├── f1r.html
│   ├── f1v.html
│   └── ...
├── data/                   # JSON data files
│   ├── folio_metadata.json      # Parsed recipe data per folio
│   ├── section_data.json        # Manuscript section structure
│   ├── ingredient_index.json    # Searchable ingredient catalog
│   ├── sop_graph.json           # Cross-reference dependency graph
│   └── folio_page_mapping.json  # Folio-to-IIIF page mapping
├── css/
│   └── edition.css         # Scholarly-themed stylesheet
├── scripts/
│   ├── build_data.py       # Data pipeline script
│   └── build_site.py       # Static site generator
└── docs/                   # Documentation (TBD)
```

## Data Sources

- **Recipe translations**: `../translations/recipes/` (201 folio files)
- **Folio index**: `../FOLIO_INDEX.md`
- **Recipe index**: `../translations/RECIPE_INDEX.md`
- **Croatian readings**: `../translations/croatian_readings.json`
- **Manuscript images**: Internet Archive IIIF (https://archive.org/details/voynich)

## Features

### Per-Folio Pages

Each folio page includes:

1. **Manuscript scan** - High-resolution image from Internet Archive
2. **Interlinear decode** - 4-layer format:
   - EVA (Voynichese transcription)
   - CRO (Croatian reading)
   - EXP (Expanded form)
   - ENG (English translation)
3. **Ingredients table** - Identified ingredients with Latin terms
4. **Preparation methods** - Cooking/processing techniques
5. **Latin terms** - Pharmaceutical vocabulary (oral, dolor, etc.)
6. **SOP chain** - Related folios by shared ingredients
7. **Codicological notes** - Section, confidence, word count

### Landing Page

- Section-based navigation (Herbal A/B, Pharmaceutical, Recipes, etc.)
- Full-text search across all folios
- Top ingredients summary
- Complete folio table with confidence levels

## Technology

- **Static HTML/CSS/JS** - No build tools or frameworks required
- **Internet Archive IIIF** - Dynamic image serving
- **Python 3** - Data pipeline scripts (no dependencies)
- **GitHub Pages ready** - Deploy directly from repository

## License

- **Content**: CC BY-SA 4.0
- **Code**: MIT License
- **Manuscript Images**: Public domain (Yale Beinecke Library via Internet Archive)

## Contributing

Contributions welcome. Areas of interest:

- Scholarly notes per folio (Stolfi, Currier, quire structure)
- Ljekarna Male Brace recipe mappings
- Improved interlinear translations
- UI/UX enhancements

See the main [ZFD repository](https://github.com/denoflore/ZFD) for the complete decipherment.

---

*"No one fabricates 179 pages of bone poultice instructions for a prank."*
