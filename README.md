# ZFD - Zuger Functional Decipherment

A systematic approach to deciphering the Voynich Manuscript through functional linguistic analysis.

## Overview

The Zuger Functional Decipherment (ZFD) represents a novel methodology for analyzing the Voynich Manuscript based on:
- **Operator-Stem-Suffix morphology** - identifying functional word components
- **Cross-corpus validation** - comparing VM patterns against medieval Latin, Croatian, and other manuscripts
- **Statistical falsification testing** - preregistered tests with explicit failure criteria

## Core Finding: "ed = root/base"

The ZFD's primary validated finding is that the Voynichese glyph sequence commonly transcribed as "ed" functions as a semantic marker meaning "root" or "base" - consistent with a herbal/botanical manual context.

## Repository Structure

```
├── 02_Transcriptions/
│   ├── LSI_ivtff_0d.txt              # Full IVTFF transcription (1.7MB)
│   ├── ocr_lines.csv                  # OCR extraction
│   └── Baselines/
│       ├── Latin/                     # Apicius, Liber de Coquina, Pharmacological
│       └── Croatian/                  # Vinodolski Zakonik, token comparisons
│
├── 03_Analysis_Data/
│   ├── Deep_State/                    # Character/prefix frequencies, word lengths
│   ├── Experimental/f88r/             # f88r mechanical decoding, coverage analysis
│   ├── Statistical_Outputs/           # Operator aliases, plant chains, baseline comparisons
│   └── Visuals/                       # Charts and manuscript images
│
├── 04_Reports/
│   ├── Part1_Main.docx                # Main methodology report
│   ├── Part2_Statistical_Analysis.docx
│   ├── ZFD_Complete.docx              # Full combined report
│   └── Parts3_Drafts.zip              # Grammatical inversion & paleographic drafts
│
├── 05_Case_Studies/
│   └── f56r/                          # Detailed f56r folio decipherment (4-6MB each)
│
├── 06_Pipelines/
│   ├── vms_replication_export.py      # Main replication pipeline
│   └── f_56_r_decipherment_update.py  # f56r analysis script
│
├── 08_Final_Proofs/
│   ├── Master_Key/                    # Operators, suffixes, stems, lexicons
│   │   ├── MasterKey_v1_1__operators.csv
│   │   ├── MasterKey_v1_1__suffixes.csv
│   │   ├── Herbal_Lexicon_v3_5_full.csv
│   │   └── MasterKey_v1_calibration_grid.csv
│   └── Final_Report/                  # Token frequencies, morphological triples
│
└── 10_Supplementary/                  # Appendices B/C/D
```

## Key Data Files

| File | Description | Size |
|------|-------------|------|
| `LSI_ivtff_0d.txt` | Complete IVTFF transcription | 1.7MB |
| `full_transcription_token_freq.csv` | Token frequency analysis | 193KB |
| `morphological_triples_counts.csv` | Operator-stem-suffix patterns | 223KB |
| `mechanical_decoding.csv` | f88r mechanical decoding attempt | 43KB |
| `plant_refined_evidence_top3.json` | Plant chain evidence | 15KB |

## Methodology

1. **Pattern Extraction** - Statistical analysis of word-initial, word-medial, and word-final patterns
2. **Cross-Validation** - Comparison with CATMuS medieval Latin corpus (160k+ abbreviated lines)
3. **Falsification Protocol** - Preregistered tests with binding decision rules
4. **Coverage Testing** - Template matching against known medieval text patterns

## Baseline Corpora

- **Latin**: Apicius (De Re Coquinaria), Liber de Coquina, Pharmacological Miscellany
- **Croatian**: Vinodolski Zakonik (medieval Croatian legal text)
- **Control**: Statistical baselines for word length, character frequency, prefix distribution

## Replication

```bash
# Clone repository
git clone https://github.com/denoflore/ZFD.git
cd ZFD

# Run replication pipeline
python 06_Pipelines/vms_replication_export.py
```

## Author

**Christopher G. Zuger (CGZ)**  
Email: chris.zuger@gmail.com

## Status

Active research - validation phase with CATMuS medieval Latin corpus achieving 92% template coverage.

## License

Research data provided for academic validation purposes.
