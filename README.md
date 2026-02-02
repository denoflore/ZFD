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

## Key Documents

### Papers
- [`ZFD_PAPER_DRAFT_v1.pdf`](papers/ZFD_PAPER_DRAFT_v1.pdf) - Complete academic paper
- [`VOYNICH_GLAGOLITIC_PALEOGRAPHIC_ANALYSIS.pdf`](papers/VOYNICH_GLAGOLITIC_PALEOGRAPHIC_ANALYSIS.pdf) - Paleographic evidence
- [`voynich_croatian_complete.pdf`](papers/voynich_croatian_complete.pdf) - Full 179-page Croatian translation

### Data
- [`08_Final_Proofs/Master_Key/`](08_Final_Proofs/Master_Key/) - Character mappings and lexicon
- [`08_Final_Proofs/COVERAGE_REPORT_v3_6.md`](08_Final_Proofs/COVERAGE_REPORT_v3_6.md) - Coverage analysis
- [`validation/`](validation/) - Statistical validation pipeline

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

## Why This Was Missed

Western cryptographers assumed the script was invented or encoded. They only compared to Latin scribal traditions.

The Voynich script is **angular Glagolitic cursive** — a Croatian writing system that was actively used during the manuscript's creation (1404-1438) in Dalmatia and the Republic of Ragusa.

Nobody checked Croatian manuscripts.

---

## The Croatian Heritage

The Republic of Ragusa (modern Dubrovnik) was a major Mediterranean trading power. Ragusan innovations include:
- First quarantine system (1377)
- Advanced pharmaceutical trade networks
- Preservation of Glagolitic literacy alongside Latin

A Ragusan apothecary manual in Glagolitic shorthand is historically unremarkable.

---

## Credits

**Research & Decipherment:** Christopher G. Zuger  
**Croatian Validation:** Georgina Zuger (professional translator-interpreter)  
**Grammatical Framework:** Friday (GPT-5.2)  
**Implementation & Analysis:** Claudette (Claude Opus 4.5)  
**Validation & Grounding:** Curio (Gemini Pro 3)

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

## Contact

- **Repository:** github.com/denoflore/ZFD
- **Author:** Christopher G. Zuger

---

## License

Research data and analysis provided for academic use.

---

*"There is nothing in [Latin] history to compare it to."*  
— Lisa Fagin Davis, paleographer

*Correct. Because it's Croatian.*

🇭🇷 **JEBENO SMO USPJELI!** 🇭🇷
