# CC INSTRUCTION: Blind Decode Falsification Test

**Date:** 2026-02-04
**Priority:** CRITICAL
**Repo:** denoflore/ZFD
**Branch:** `feature/blind-decode-test`
**Purpose:** Answer the "degrees of freedom" criticism with an automated, reproducible, frozen-lexicon blind decode test that anyone can run.

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

A critic has challenged the ZFD with the claim that the system has "so many degrees of freedom (operators, layers, abbreviations, phonetic adjustments) that it will always produce something Croatian-compatible, regardless of the input." They argue that metrics like 96.8% coverage and 100% phonotactic validity demonstrate only that the generator works, not that the decipherment is correct.

The response is not argument. It is execution. We build an automated blind decode test that:

1. Freezes the lexicon (no tuning during test)
2. Decodes five specific folios using the frozen pipeline
3. Compares decoded semantic content against manuscript illustrations
4. Runs the same pipeline on SHUFFLED input as a null baseline
5. Reports whether real input produces statistically better results than noise
6. Packages everything so any skeptic can run it with one command

If ZFD is real, the frozen decoder on real folios will produce coherent pharmaceutical content that correlates with the illustrations. The shuffled baseline will produce garbage. The difference will be measurable.

If ZFD is not real, both will produce equally "Croatian-compatible" output and the test fails. The critic wins.

This is the test that settles the "degrees of freedom" objection permanently.

---

## REQUIRED READING

Before writing ANY code, read these files completely:

1. **`zfd_decoder/src/pipeline.py`** -- The full decode pipeline. Understand every stage.
2. **`zfd_decoder/src/stems.py`** -- Lexicon loader. Now supports v1 and v2 formats.
3. **`zfd_decoder/src/tokenizer.py`** -- EVA tokenization. This is where words get split.
4. **`zfd_decoder/src/operators.py`** -- Operator prefix detection.
5. **`zfd_decoder/src/suffixes.py`** -- Suffix class detection.
6. **`zfd_decoder/data/lexicon_v2.csv`** -- The 185-entry lexicon (9 columns: name, variant, context, gloss, latin, croatian, category, status, source)
7. **`zfd_decoder/data/operators.json`** -- Operator definitions
8. **`zfd_decoder/data/suffixes.json`** -- Suffix definitions
9. **`zfd_decoder/main.py`** -- Current CLI entry point
10. **`voynich_data/raw_eva/`** -- All 201 EVA transcription files, one per folio

---

## CRITICAL REQUIREMENTS

**FROZEN LEXICON:** The test MUST use the lexicon as-is at test start. No modifications during the run. The lexicon file is checksummed (SHA-256) at test start and verified at test end.

**SHUFFLED BASELINE:** For each test folio, the pipeline is also run on a shuffled version of the EVA text. Shuffling preserves word boundaries but randomly reassigns words to different positions. This creates text with identical vocabulary distribution but no spatial/sequential meaning.

**REPRODUCIBILITY:** The shuffling uses a fixed random seed (42) so results are deterministic. Anyone running the test gets identical results.

**NO IMAGE DATA:** The decoder never sees manuscript images. It operates on EVA text only. Image correlation is scored AFTER decoding, using a preregistered annotation file.

**OUTPUT EVERYTHING:** Every intermediate result, every score, every comparison must be saved. No cherry-picking.

**DO NOT:**
- Modify any file in `zfd_decoder/src/` or `zfd_decoder/data/`
- Change the lexicon during the test
- Use any information from manuscript illustrations during decoding
- Suppress or filter results
- Modify operators.json, suffixes.json, gallows.json, or mid_word.json

---

## BACKGROUND: The Five Test Folios

These five folios were selected from Protocol v1 (preregistered September 2025) to span different manuscript sections:

| Folio | Section | Expected Content | Key Visual Elements |
|-------|---------|-----------------|-------------------|
| f10r | Herbal A | Plant preparation recipe | Plant with prominent root system |
| f23v | Herbal A | Plant processing | Plant with leaves, possible distillation |
| f47r | Herbal B | Herbal recipe | Plant illustration with roots and flowers |
| f89r | Pharmaceutical | Pharmaceutical recipe | Jars, vessels, processing equipment |
| f101v | Recipes/Stars | Recipe grid or dosage table | Grid-like layout, possible astronomical |

---

## Phase 1: Test Infrastructure Setup

**Goal:** Create the test harness directory structure and core utilities.

**Files to create:**
- `validation/blind_decode_test/README.md` -- Test documentation
- `validation/blind_decode_test/run_test.py` -- Main test runner (entry point)
- `validation/blind_decode_test/config.py` -- Test configuration (folios, seeds, thresholds)
- `validation/blind_decode_test/utils.py` -- Shared utilities (checksum, file I/O)

**config.py contents:**

```python
"""
Blind Decode Falsification Test Configuration
All values are preregistered. Do not modify during testing.
"""

# Test folios (from Protocol v1, preregistered September 2025)
TEST_FOLIOS = ["f10r", "f23v", "f47r", "f89r", "f101v"]

# Random seed for shuffled baseline (deterministic reproducibility)
SHUFFLE_SEED = 42

# Number of shuffle iterations for statistical significance
SHUFFLE_ITERATIONS = 100

# Pass/fail thresholds (preregistered)
THRESHOLDS = {
    # Minimum coherence index (0-1) for a folio to "pass"
    "min_coherence": 0.70,
    
    # Minimum folios that must pass (out of 5)
    "min_passing_folios": 4,
    
    # Minimum p-value threshold for real vs shuffled comparison
    "significance_level": 0.01,
    
    # Minimum semantic category diversity (unique categories per folio)
    "min_category_diversity": 3,
    
    # Minimum known stem ratio per folio
    "min_known_ratio": 0.30,
}

# Folio-specific predictions (from preregistered Protocol v1)
FOLIO_PREDICTIONS = {
    "f10r": {
        "expected_process_class": "wash_strain",
        "required_operators": ["qo", "ol", "ch"],
        "required_stems_any": ["edy", "edi", "rady"],  # root terms
        "forbidden_dominant_category": None,
    },
    "f23v": {
        "expected_process_class": "heat_treatment",
        "required_operators": ["ok", "qo"],
        "required_stems_any": ["ol", "or"],  # oil terms
        "forbidden_dominant_category": None,
    },
    "f47r": {
        "expected_process_class": "herbal_preparation",
        "required_operators": ["qo", "ch", "sh"],
        "required_stems_any": ["edy", "edi", "flor", "list"],
        "forbidden_dominant_category": None,
    },
    "f89r": {
        "expected_process_class": "pharmaceutical_recipe",
        "required_operators": ["qo", "da", "ok"],
        "required_stems_any": ["kost", "ost", "ol", "or", "mel"],
        "forbidden_dominant_category": None,
    },
    "f101v": {
        "expected_process_class": "dosage_grid",
        "required_operators": ["qo", "da"],
        "required_stems_any": ["da", "dar"],  # dose terms
        "forbidden_dominant_category": None,
    },
}

# Image-adjacency annotations (preregistered before test run)
# Maps folio regions to expected semantic categories based on illustrations
# These annotations are made by a human looking at the images BEFORE decoding
IMAGE_ANNOTATIONS = {
    "f10r": {
        "description": "Plant with prominent root system, leaves, possible flowers",
        "expected_categories": ["ingredient", "preparation", "action"],
        "key_plant_parts": ["root", "leaf"],
        "has_vessels": False,
        "has_text_blocks": True,
    },
    "f23v": {
        "description": "Plant illustration with distinct parts, possible distillation context",
        "expected_categories": ["ingredient", "action", "equipment"],
        "key_plant_parts": ["leaf", "flower", "oil"],
        "has_vessels": False,
        "has_text_blocks": True,
    },
    "f47r": {
        "description": "Herbal illustration with roots and upper parts visible",
        "expected_categories": ["ingredient", "preparation", "action"],
        "key_plant_parts": ["root", "flower", "leaf"],
        "has_vessels": False,
        "has_text_blocks": True,
    },
    "f89r": {
        "description": "Pharmaceutical section with jars, vessels, processing equipment",
        "expected_categories": ["ingredient", "equipment", "action", "preparation"],
        "key_plant_parts": [],
        "has_vessels": True,
        "has_text_blocks": True,
    },
    "f101v": {
        "description": "Grid-like layout, recipe organization, possible dosage tables",
        "expected_categories": ["measurement", "ingredient", "timing", "action"],
        "key_plant_parts": [],
        "has_vessels": False,
        "has_text_blocks": True,
    },
}
```

**utils.py contents:**

```python
"""Shared utilities for blind decode test."""

import hashlib
import json
import random
from pathlib import Path
from typing import List, Dict


def sha256_file(filepath: str) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def load_eva_folio(folio_id: str, data_dir: str) -> str:
    """Load EVA transcription for a folio."""
    filepath = Path(data_dir) / "voynich_data" / "raw_eva" / f"{folio_id}.txt"
    if not filepath.exists():
        raise FileNotFoundError(f"EVA file not found: {filepath}")
    with open(filepath, encoding='utf-8') as f:
        return f.read()


def shuffle_eva_text(eva_text: str, seed: int) -> str:
    """
    Shuffle EVA text while preserving word boundaries and line structure.
    
    This creates a null baseline: same vocabulary, same word count per line,
    but words randomly reassigned to different positions.
    """
    rng = random.Random(seed)
    
    lines = eva_text.strip().split('\n')
    # Collect all words
    all_words = []
    line_lengths = []
    for line in lines:
        words = line.strip().split()
        # Skip comment lines (starting with #) and empty lines
        if not words or words[0].startswith('#') or words[0].startswith('<'):
            line_lengths.append(0)
            continue
        all_words.extend(words)
        line_lengths.append(len(words))
    
    # Shuffle all words
    rng.shuffle(all_words)
    
    # Reconstruct with original line lengths
    shuffled_lines = []
    word_idx = 0
    for i, length in enumerate(line_lengths):
        if length == 0:
            shuffled_lines.append(lines[i])  # preserve comments/headers
        else:
            line_words = all_words[word_idx:word_idx + length]
            shuffled_lines.append(' '.join(line_words))
            word_idx += length
    
    return '\n'.join(shuffled_lines)


def save_json(data: dict, filepath: str):
    """Save data as formatted JSON."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(filepath: str) -> dict:
    """Load JSON data."""
    with open(filepath, encoding='utf-8') as f:
        return json.load(f)
```

**Validation:**
- [ ] Directory `validation/blind_decode_test/` exists
- [ ] All four files created
- [ ] `config.py` has all 5 folios, all thresholds, all folio predictions, all image annotations
- [ ] `utils.py` has checksum, EVA loading, shuffling, JSON I/O functions
- [ ] Shuffling function preserves line structure and comment lines

**After completing Phase 1, read this document again to find Phase 2.**

---

## Phase 2: Decode Engine Wrapper

**Goal:** Create a wrapper that runs the existing ZFD pipeline on any EVA text and captures structured results.

**Files to create:**
- `validation/blind_decode_test/decoder.py` -- Wraps ZFDPipeline for test use

**decoder.py must:**

1. Initialize ZFDPipeline from `zfd_decoder/data/` directory
2. Accept EVA text and folio ID as inputs
3. Run the full pipeline (no modifications)
4. Extract and return structured results:
   - Total tokens
   - Known stems count and ratio
   - Unknown stems count and list
   - Operator distribution (dict of operator -> count)
   - Category distribution (dict of category -> count)
   - Average confidence score
   - Full token list with all fields
   - Validation checks (kost_present, ol_present, operators_found)

5. Compute a **coherence index** (0-1) for each folio:
   ```
   coherence = weighted_average(
       0.30 * known_ratio,           # What % of stems are known
       0.25 * operator_diversity,     # Normalized count of distinct operators (0-1)
       0.25 * category_diversity,     # Normalized count of distinct categories (0-1)
       0.20 * confidence_mean,        # Average pipeline confidence
   )
   ```
   Where:
   - `operator_diversity` = min(distinct_operators / 5, 1.0)
   - `category_diversity` = min(distinct_categories / 5, 1.0)

6. Return results as a Python dict (JSON-serializable)

**Key constraint:** decoder.py MUST NOT import or modify anything in `zfd_decoder/src/`. It uses the pipeline as a black box. Add the `zfd_decoder` parent directory to sys.path and import normally.

**Validation:**
- [ ] decoder.py can process a single folio EVA file
- [ ] Returns structured dict with all required fields
- [ ] Coherence index is computed correctly
- [ ] Works with both lexicon v1 and v2

**After completing Phase 2, read this document again to find Phase 3.**

---

## Phase 3: Shuffled Baseline Generator

**Goal:** Create the null hypothesis engine that processes shuffled versions of each folio.

**Files to create:**
- `validation/blind_decode_test/baseline.py` -- Generates and decodes shuffled baselines

**baseline.py must:**

1. For each test folio, generate `SHUFFLE_ITERATIONS` (100) shuffled versions
2. Decode each shuffled version through the SAME pipeline
3. Collect coherence scores, known ratios, category distributions for all shuffled versions
4. Compute distribution statistics: mean, std, min, max, percentiles (5th, 25th, 50th, 75th, 95th)
5. Save all individual results (not just summary stats)

**Shuffle method (critical):**
- Each shuffle uses seed = `SHUFFLE_SEED + iteration_number` (42, 43, 44, ... 141)
- This means every run produces identical shuffled baselines
- The shuffling preserves: number of lines, number of words per line, total vocabulary
- The shuffling destroys: word order, positional semantics, sequential meaning

**Output per folio:**
```json
{
    "folio": "f10r",
    "iterations": 100,
    "coherence_scores": [0.23, 0.19, 0.31, ...],  // all 100 scores
    "known_ratios": [0.15, 0.12, 0.18, ...],
    "stats": {
        "coherence_mean": 0.22,
        "coherence_std": 0.06,
        "coherence_p5": 0.14,
        "coherence_p95": 0.33,
        "known_ratio_mean": 0.14,
        "known_ratio_std": 0.04,
    }
}
```

**Validation:**
- [ ] Generates exactly 100 shuffled versions per folio
- [ ] Each shuffle is deterministic (same seed = same result)
- [ ] Shuffled text has same word count and line count as original
- [ ] All 100 decode results are saved
- [ ] Statistics computed correctly

**After completing Phase 3, read this document again to find Phase 4.**

---

## Phase 4: Comparison Engine and Statistical Tests

**Goal:** Compare real decode results against shuffled baselines with proper statistical testing.

**Files to create:**
- `validation/blind_decode_test/compare.py` -- Statistical comparison engine

**compare.py must:**

1. Load real decode results (from Phase 2)
2. Load shuffled baseline results (from Phase 3)
3. For each folio, compute:

   a. **Z-score**: How many standard deviations is the real coherence above the shuffled mean?
      ```
      z = (real_coherence - shuffled_mean) / shuffled_std
      ```
   
   b. **Empirical p-value**: What fraction of shuffled runs scored >= real coherence?
      ```
      p = count(shuffled >= real) / total_shuffled
      ```
   
   c. **Effect size** (Cohen's d): Practical significance
      ```
      d = (real_coherence - shuffled_mean) / shuffled_std
      ```
   
   d. **Prediction accuracy**: For each folio prediction in config.py:
      - Were required operators found? (yes/no)
      - Were any required stems found? (yes/no)
      - Does category distribution match expected categories? (overlap score)

4. Compute overall test verdict:
   - PASS: >= 4 folios have coherence >= 0.70 AND p < 0.01 vs shuffled baseline
   - PARTIAL: 2-3 folios pass
   - FAIL: 0-1 folios pass

5. For the prediction accuracy check, also score the SHUFFLED baselines:
   - What % of shuffled runs accidentally meet the folio-specific predictions?
   - If shuffled runs also meet predictions at >20% rate, the predictions are too loose

**Output:**
```json
{
    "test_date": "2026-02-04T...",
    "lexicon_sha256": "abc123...",
    "overall_verdict": "PASS|PARTIAL|FAIL",
    "folios": {
        "f10r": {
            "real_coherence": 0.78,
            "shuffled_mean": 0.22,
            "shuffled_std": 0.06,
            "z_score": 9.33,
            "p_value": 0.00,
            "effect_size": 9.33,
            "predictions_met": {"operators": true, "stems": true, "categories": true},
            "shuffled_prediction_rate": 0.03,
            "verdict": "PASS"
        },
        // ... other folios
    },
    "summary": {
        "folios_passing": 5,
        "folios_required": 4,
        "overall_p": 0.00,
        "overall_effect_size": 8.12,
    }
}
```

**Validation:**
- [ ] Z-scores computed correctly
- [ ] P-values are empirical (not parametric)
- [ ] Prediction accuracy scored for both real and shuffled
- [ ] Overall verdict logic matches threshold rules
- [ ] All results saved to JSON

**After completing Phase 4, read this document again to find Phase 5.**

---

## Phase 5: Report Generator

**Goal:** Create a human-readable Markdown report from the test results.

**Files to create:**
- `validation/blind_decode_test/report.py` -- Generates Markdown report

**report.py must generate a report with these sections:**

1. **Header**: Test name, date, lexicon checksum, pipeline version
2. **Executive Summary**: Overall verdict (PASS/PARTIAL/FAIL) in one paragraph
3. **Methodology**: What was tested, how shuffling works, what the null hypothesis is
4. **Per-Folio Results Table**:
   | Folio | Real Coherence | Shuffled Mean +/- SD | Z-score | p-value | Verdict |
5. **Prediction Accuracy Table**:
   | Folio | Operators Found | Stems Found | Categories Match | Shuffled Match Rate |
6. **Interpretation**: What the results mean for the "degrees of freedom" criticism
7. **Reproducibility**: How to run the test yourself (exact commands)
8. **Raw Data**: Links to all JSON output files
9. **Lexicon Integrity**: SHA-256 at start and end, confirmation they match

**The report MUST include this statement regardless of outcome:**
> "If the shuffled baseline produces coherence scores statistically indistinguishable from the real decode, this test has failed and the degrees-of-freedom criticism is valid. If the real decode produces significantly higher coherence than shuffled input through the same pipeline, the decoder is detecting structure that exists in the manuscript, not generating it from flexible parameters."

**Validation:**
- [ ] Report is valid Markdown
- [ ] All tables render correctly
- [ ] Executive summary states verdict clearly
- [ ] Reproducibility section has exact commands
- [ ] Lexicon integrity section confirms checksums match

**After completing Phase 5, read this document again to find Phase 6.**

---

## Phase 6: Main Test Runner + CLI

**Goal:** Wire everything together into a single-command test runner.

**Files to modify:**
- `validation/blind_decode_test/run_test.py` -- Main entry point

**run_test.py must:**

1. Print banner: "ZFD BLIND DECODE FALSIFICATION TEST"
2. Verify all prerequisites:
   - EVA files exist for all 5 test folios
   - Lexicon file exists and is readable
   - Pipeline can be imported
3. Compute and record lexicon SHA-256 (START)
4. Run real decode on all 5 folios (Phase 2)
5. Run shuffled baselines on all 5 folios (Phase 3) -- this is the slow part, print progress
6. Run statistical comparison (Phase 4)
7. Verify lexicon SHA-256 (END) matches START -- if not, ABORT and report tampering
8. Generate report (Phase 5)
9. Save all outputs to `validation/blind_decode_test/results/`
10. Print summary to console

**CLI:**
```
# Run full test
python validation/blind_decode_test/run_test.py

# Run with fewer shuffle iterations (for quick testing)
python validation/blind_decode_test/run_test.py --quick  # uses 10 iterations instead of 100

# Run single folio only
python validation/blind_decode_test/run_test.py --folio f10r
```

**Output directory structure:**
```
validation/blind_decode_test/results/
    test_metadata.json          # Test config, checksums, timestamps
    real_decode_f10r.json       # Full decode output for each folio
    real_decode_f23v.json
    real_decode_f47r.json
    real_decode_f89r.json
    real_decode_f101v.json
    baseline_f10r.json          # All 100 shuffled results per folio
    baseline_f23v.json
    baseline_f47r.json
    baseline_f89r.json
    baseline_f101v.json
    comparison_results.json     # Statistical comparison
    BLIND_DECODE_REPORT.md      # Human-readable report
```

**Validation:**
- [ ] `python run_test.py --quick` completes without error
- [ ] All output files created in results/
- [ ] Lexicon checksums match at start and end
- [ ] Report file is readable and complete
- [ ] Console output shows clear PASS/PARTIAL/FAIL verdict

**After completing Phase 6, read this document again to find Phase 7.**

---

## Phase 7: Integration and Cleanup

**Goal:** Ensure the test integrates cleanly with the repo and is discoverable.

**Files to modify/create:**
- `validation/blind_decode_test/requirements.txt` -- Any extra dependencies (should be minimal, stdlib only ideally)
- `validation/README.md` -- Update to reference the blind decode test
- `README.md` -- Add a "Falsification Testing" section that links to the test

**README.md addition** (add under the existing Validation section or create new section):

```markdown
### Blind Decode Falsification Test

To test whether the ZFD pipeline is detecting real structure or merely generating 
Croatian-compatible output from any input:

```bash
cd validation/blind_decode_test
python run_test.py
```

This test:
1. Freezes the lexicon (checksummed, no modifications allowed during test)
2. Decodes 5 preregistered folios using the frozen pipeline
3. Decodes 100 shuffled versions of each folio through the SAME pipeline
4. Compares real vs shuffled results with z-scores and empirical p-values
5. Reports PASS/FAIL with full statistical evidence

If the decoder produces significantly better results on real manuscript text than 
on shuffled text, the "degrees of freedom" criticism is empirically refuted.

Results: `validation/blind_decode_test/results/BLIND_DECODE_REPORT.md`
```

**Validation:**
- [ ] No external dependencies needed (stdlib + existing pipeline only)
- [ ] README.md updated with falsification test section
- [ ] validation/README.md references the test
- [ ] All files committed to feature branch
- [ ] PR created against main (do NOT auto-merge)

---

## SUCCESS CRITERIA

The CC task is complete when:

- [ ] All 7 phases implemented
- [ ] `python run_test.py --quick` runs to completion
- [ ] Report generated with clear verdict
- [ ] Lexicon integrity verified (start checksum == end checksum)
- [ ] All output files created in results/
- [ ] README.md updated
- [ ] Feature branch pushed, PR created
- [ ] No modifications to any existing zfd_decoder/ files

## WHAT THIS PROVES

If the test PASSES (real >> shuffled):
> "The ZFD pipeline detects semantic structure that exists in the manuscript. Shuffled input through the same 'degrees of freedom' produces statistically worse results. The system is not a generator. It is a decoder."

If the test FAILS (real == shuffled):
> "The ZFD pipeline produces similar output regardless of input structure. The degrees-of-freedom criticism is valid. The coverage metrics reflect system flexibility, not decipherment accuracy."

Either outcome is published. This is how science works.
