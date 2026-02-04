# ZFD Validation Suite

This directory contains validation tools and tests for the Zuger Functional Decipherment (ZFD) of the Voynich Manuscript.

## Contents

### Validation Tools

- **annotation_builder.py** - Build and update folio annotations
- **catmus_validator.py** - Validate against CATMuS medieval Croatian corpus
- **image_adjacent.py** - Image-text adjacency analysis
- **zfd_loader.py** - Load and parse ZFD decode outputs

### Validation Phases

- **phase4_geometric.py** - Geometric pattern analysis
- **phase4_upper_canopy.py** - Upper canopy text analysis
- **phase5_pharma.py** - Pharmaceutical vocabulary validation
- **phase6_operators.py** - Operator frequency analysis
- **phase7_parser.py** - Parser validation
- **phase8_recipes.py** - Recipe structure analysis
- **phase9_summary.py** - Summary generation
- **phase9_translator.py** - Translation validation

### Falsification Tests

- **[blind_decode_test/](blind_decode_test/)** - **Blind Decode Falsification Test**
  - Addresses the "degrees of freedom" criticism
  - Compares real decodes vs shuffled baselines
  - Run with: `python blind_decode_test/run_test.py`

### Data Files

- **folio_annotations.json** - Annotated folio data
- **folio_images.json** - Image-text correlations

### Reports

- **catmus_report.md** - CATMuS validation results
- **od_validation_report.md** - Operator detection validation
- **visual_annotation_log.md** - Visual annotation process

### Results

- **results/** - JSON output files from validation runs

## Running Validation

```bash
# Run all validation phases
python run_all.py

# Run specific phase
python phase5_pharma.py

# Run blind decode falsification test
python blind_decode_test/run_test.py
python blind_decode_test/run_test.py --quick  # 10 iterations
```

## Key Validation Results

| Metric | Result |
|--------|--------|
| Token coverage | 96.8% |
| CATMuS stem match | 68.6% |
| Phonotactic validity | 100% |
| Spatial correlation | p < 0.001 |

See [VALIDATION_RESULTS_JAN2026.md](../VALIDATION_RESULTS_JAN2026.md) for complete results.
