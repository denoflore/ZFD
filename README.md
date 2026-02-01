# ZFD - Zuger Functional Decipherment

A systematic approach to deciphering the Voynich Manuscript through functional linguistic analysis.

## Overview

The Zuger Functional Decipherment (ZFD) represents a novel methodology for analyzing the Voynich Manuscript based on:
- **Operator-Stem-Suffix morphology** - identifying functional word components
- **Cross-corpus validation** - comparing VM patterns against medieval Latin, Croatian, and other manuscripts
- **Statistical falsification testing** - preregistered tests with explicit failure criteria

## Repository Structure

```
├── 02_Transcriptions/     # Source transcription data (LSI, OCR)
├── 03_Analysis_Data/      # Processed analysis outputs
├── 06_Pipelines/          # Python replication scripts
├── 08_Final_Proofs/
│   ├── Master_Key/        # Lexicon, operators, suffixes, stems
│   └── Final_Report/      # Validation data, corpus comparisons
└── 10_Supplementary/      # Appendices, phase tracking
```

## Key Files

### Master Key (Decipherment Tables)
- `MasterKey_v1_1__operators.csv` - Identified operators (prefixes/infixes)
- `MasterKey_v1_1__suffixes.csv` - Identified suffix patterns
- `Herbal_Lexicon_v3_5_full.csv` - Herbal section lexicon
- `MasterKey_v1_calibration_grid.csv` - Validation calibration data

### Data Files
- `LSI_ivtff_0d.txt` - Full IVTFF transcription (1.7MB)
- `full_transcription_token_freq.csv` - Token frequency analysis
- `morphological_triples_counts.csv` - Operator-stem-suffix patterns

### Scripts
- `vms_replication_export.py` - Main replication pipeline
- `f_56_r_decipherment_update.py` - Folio f56r analysis

## Key Finding: "ed = root/base"

The ZFD's core validated finding is that the Voynichese glyph sequence commonly transcribed as "ed" functions as a semantic marker meaning "root" or "base" - consistent with a herbal/botanical manual context.

## Methodology

1. **Pattern Extraction** - Statistical analysis of word-initial, word-medial, and word-final patterns
2. **Cross-Validation** - Comparison with CATMuS medieval Latin corpus (160k+ abbreviated lines)
3. **Falsification Protocol** - Preregistered tests with binding decision rules

## Author

Christopher G. Zuger (CGZ)
Email: chris.zuger@gmail.com

## License

Research data provided for academic validation purposes.
