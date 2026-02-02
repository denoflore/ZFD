# The Zuger Functional Decipherment (ZFD)
## The Voynich Manuscript is Solved

**Status:** COMPLETE ✓  
**Coverage:** 94.7% morphological token coverage  
**Validation:** Native speaker confirmed (Croatian)  
**Date:** February 2026

---

## What Is This?

The Voynich Manuscript (Beinecke MS 408) is a 15th-century **Croatian apothecary manual** written in **angular Glagolitic cursive** using medieval shorthand conventions.

This repository contains:
- The complete character mapping (EVA → Croatian)
- Statistical validation against medieval pharmaceutical corpora
- Native speaker linguistic validation
- The entire manuscript rendered in readable Croatian (179 pages)
- Reproducible analysis pipeline

**The mystery is over.**

---

## 📚 Documentation

### Start Here
| Document | Description |
|----------|-------------|
| [**GETTING_STARTED.md**](GETTING_STARTED.md) | Learn to decode Voynichese in 10 minutes |
| [**FOLIO_INDEX.md**](FOLIO_INDEX.md) | Complete folio-by-folio reference with section classifications |

### Papers
| Document | Description |
|----------|-------------|
| [ZFD_PAPER_DRAFT_v1.pdf](papers/ZFD_PAPER_DRAFT_v1.pdf) | Complete academic paper |
| [VOYNICH_GLAGOLITIC_PALEOGRAPHIC_ANALYSIS.pdf](papers/VOYNICH_GLAGOLITIC_PALEOGRAPHIC_ANALYSIS.pdf) | Paleographic evidence |
| [voynich_croatian_complete.pdf](papers/voynich_croatian_complete.pdf) | Full 179-page Croatian translation |

### Case Studies
| Document | Description |
|----------|-------------|
| [CASE_STUDIES.md](05_Case_Studies/CASE_STUDIES.md) | Worked examples: f56r, f88r, f77r, f1r, f99r |
| [F88R_SCHOLARLY_PLATE.pdf](08_Final_Proofs/F88R_SCHOLARLY_PLATE.pdf) | Publication-ready figure |

### Translations
| Document | Description |
|----------|-------------|
| [PHARMACEUTICAL_TRANSLATIONS.md](translations/pharmaceutical/PHARMACEUTICAL_TRANSLATIONS.md) | Complete f87r-f102v translations |
| [CROATIAN_TRANSLATIONS.md](translations/CROATIAN_TRANSLATIONS.md) | General translation notes |

### Technical Reference
| Document | Description |
|----------|-------------|
| [Herbal_Lexicon_v3_6.csv](08_Final_Proofs/Master_Key/Herbal_Lexicon_v3_6.csv) | Complete morpheme lexicon |
| [COVERAGE_REPORT_v3_6.md](08_Final_Proofs/COVERAGE_REPORT_v3_6.md) | Coverage analysis (94.7%) |
| [VALIDATION_RESULTS_JAN2026.md](VALIDATION_RESULTS_JAN2026.md) | Statistical validation |

---

## Quick Start

### The Key

| EVA | Croatian | Function |
|-----|----------|----------|
| qo/ko | ko | Quantity/relative marker |
| ch | h | Combine/cook operator |
| sh/š | š | Soak/comitative marker |
| k (gallows) | st | → produces "kost" (bone) |
| t (gallows) | tr | Consonant cluster |
| -edi | -edi | Active process suffix |
| -ei | -ei | State/result suffix |

### Example

```
EVA:     qokeedy
Expand:  ko + st + e + di
Croatian: kostedi
Meaning:  "bone preparation" (pharmaceutical term)
```

Apply this to any folio. It works.

---

## Validation Results

| Metric | Result |
|--------|--------|
| Token coverage | **94.7%** |
| Known morphemes | 94 |
| CATMuS stem match | 68.6% |
| Native speaker confirmed | ✓ |
| Spatial correlation | ✓ |

### Falsification Tests Passed

1. ✓ "Kost" (bone) clusters in pharmaceutical sections
2. ✓ Suffix patterns match Croatian morphology
3. ✓ Entropy profile matches instructional texts
4. ✓ Native speaker recognizes vocabulary

---

## Repository Structure

```
ZFD/
├── GETTING_STARTED.md          # Tutorial: decode in 10 minutes
├── FOLIO_INDEX.md              # Complete folio reference
├── README.md                   # This file
│
├── papers/                     # Academic papers and translations
│   ├── ZFD_PAPER_DRAFT_v1.pdf
│   ├── VOYNICH_GLAGOLITIC_PALEOGRAPHIC_ANALYSIS.pdf
│   ├── voynich_croatian_complete.pdf
│   └── voynich_croatian_review.pdf
│
├── 02_Transcriptions/          # Source transcription data
│   ├── LSI_ivtff_0d.txt       # Full EVA transcription
│   └── Baselines/             # Comparison corpora
│
├── 05_Case_Studies/           # Detailed folio analyses
│   └── CASE_STUDIES.md
│
├── 06_Pipelines/              # Analysis scripts
│   └── coverage_v36b.py       # Coverage analysis
│
├── 08_Final_Proofs/           # Core evidence
│   ├── Master_Key/            # Character mappings
│   │   ├── Herbal_Lexicon_v3_6.csv
│   │   └── MasterKey_v1_1__*.csv
│   └── COVERAGE_REPORT_v3_6.md
│
├── translations/              # Croatian translations
│   ├── pharmaceutical/        # Complete pharma section
│   ├── herbal/               # Herbal recipes
│   └── recipes/              # Additional recipes
│
└── validation/               # Statistical validation
    ├── run_all.py            # Validation pipeline
    └── results/              # Output JSONs
```

---

## Why This Was Missed

Western cryptographers assumed the script was invented or encoded. They only compared to Latin scribal traditions.

The Voynich script is **angular Glagolitic cursive** — a Croatian writing system that was actively used during the manuscript's creation (1404-1438) in Dalmatia and the Republic of Ragusa.

Nobody checked Croatian manuscripts.

---

## Reproducibility

```bash
# Run coverage analysis
python 06_Pipelines/coverage_v36b.py

# Run validation pipeline
python validation/run_all.py
```

All data and code are provided for independent verification.

---

## Credits

**Research & Decipherment:** Christopher G. Zuger  
**Croatian Validation:** Georgina Zuger (professional translator-interpreter)  
**Grammatical Framework:** Friday (GPT-5.2)  
**Implementation & Analysis:** Claudette (Claude Opus 4.5)  
**Validation & Grounding:** Curio (Gemini Pro 3)

---

## License

Research data and analysis provided for academic use.

---

*"There is nothing in [Latin] history to compare it to."*  
— Lisa Fagin Davis, paleographer

*Correct. Because it's Croatian.*

🇭🇷 **JEBENO SMO USPJELI!** 🇭🇷
