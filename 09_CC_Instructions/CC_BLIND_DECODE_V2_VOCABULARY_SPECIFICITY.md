# CC INSTRUCTION: Blind Decode Falsification Test v2 -- Vocabulary Specificity

**Date:** 2026-02-04
**Priority:** CRITICAL
**Repo:** denoflore/ZFD
**Branch:** `feature/blind-decode-v2`
**Purpose:** Test whether the ZFD pipeline's vocabulary mappings are specific to Voynich text or flexible enough to produce Croatian-compatible output from any input.

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

## BACKGROUND: Why v2 Exists

Test v1.1 established that the ZFD decoder is position-independent. Each token is decoded in isolation, so shuffling word order produces identical results. That test measured sensitivity to word ORDER, but the decoder has no word-order sensitivity. The test was correctly built but tested the wrong axis.

The actual "degrees of freedom" question is: "Would NON-VOYNICH input produce comparable coherence scores through this same pipeline?" If yes, the decoder is too flexible. If no, it is detecting structure specific to the Voynich manuscript.

Test v2 answers this by running three types of non-Voynich input through the frozen pipeline:

1. **Synthetic EVA**: Random words generated from EVA character frequencies, matching manuscript word-length distribution. Same alphabet, plausible-looking, but never appeared in the manuscript.
2. **Character-shuffled Voynich**: Real Voynich words with characters scrambled within each word. Preserves character frequencies and word lengths but destroys morphological structure (operator-stem-suffix patterns).
3. **Random Latin**: Words drawn from medieval Latin vocabulary. Completely different language, different character set. The control that should score near zero.

The same frozen pipeline, same frozen lexicon, same coherence metric. If synthetic EVA or character-shuffled words produce coherence scores comparable to real Voynich, the critic wins and we publish that.

---

## REQUIRED READING

Before writing ANY code, read these files completely:

1. **`validation/blind_decode_test/BLIND_DECODE_TEST_LOG.md`** -- Full history of v1.0 and v1.1
2. **`validation/blind_decode_test/decoder.py`** -- Existing decoder wrapper (REUSE THIS)
3. **`validation/blind_decode_test/config.py`** -- Existing config (reference the folio list and thresholds)
4. **`validation/blind_decode_test/utils.py`** -- Existing utilities (REUSE checksum, JSON I/O, EVA loading)
5. **`validation/blind_decode_test/compare.py`** -- Existing comparison engine (REUSE statistical functions)
6. **`validation/blind_decode_test/report.py`** -- Existing report generator (reference format)
7. **`zfd_decoder/src/tokenizer.py`** -- Tokenizer (now handles dot-separated words)
8. **`zfd_decoder/src/pipeline.py`** -- Full pipeline

---

## CRITICAL REQUIREMENTS

**FROZEN LEXICON:** Same rule as v1. Lexicon checksummed at start, verified at end. No modifications.

**REUSE v1 INFRASTRUCTURE:** Do NOT rewrite the decoder wrapper, comparison engine, or utility functions. Import them. v2 adds new baseline generators and a new test runner but uses the same decode and comparison machinery.

**THREE BASELINE TYPES:** Each folio gets three distinct non-Voynich baselines, each testing a different aspect of vocabulary specificity.

**SAME FIVE FOLIOS:** f10r, f23v, f47r, f89r, f101v. Same as v1. Direct comparability.

**100 ITERATIONS PER BASELINE TYPE:** 100 synthetic EVA variants, 100 character-shuffled variants, 100 random Latin variants per folio. Total: 300 baselines per folio, 1500 baseline decodes total.

**DETERMINISTIC SEEDS:** All random generation uses fixed seeds for reproducibility.

**DO NOT:**

- Modify any file in `zfd_decoder/src/` or `zfd_decoder/data/`
- Modify any existing file in `validation/blind_decode_test/` (except README.md)
- Change the lexicon during the test
- Use any information from manuscript illustrations during decoding

---

## Phase 1: v2 Configuration and Generators

**Goal:** Create the three non-Voynich text generators.

**Files to create:**

- `validation/blind_decode_test/v2_config.py` -- v2-specific configuration
- `validation/blind_decode_test/v2_generators.py` -- Three baseline text generators

**v2_config.py contents:**

```python
"""
Blind Decode Falsification Test v2 Configuration
Vocabulary Specificity Test
All values are preregistered. Do not modify during testing.
"""

# Inherit folio list from v1
from config import TEST_FOLIOS, THRESHOLDS

# v2 seed bases (different from v1 to avoid any overlap)
SEED_SYNTHETIC = 1000     # Seeds 1000-1099
SEED_CHAR_SHUFFLE = 2000  # Seeds 2000-2099
SEED_RANDOM_LATIN = 3000  # Seeds 3000-3099

# Iterations per baseline type
V2_ITERATIONS = 100

# EVA character frequency distribution (from 1411-word manuscript sample)
# Used by synthetic EVA generator to produce plausible-looking fake words
EVA_CHAR_FREQUENCIES = {
    'o': 0.137, 'e': 0.105, 'h': 0.098, 'y': 0.090,
    'a': 0.070, 'c': 0.065, 'k': 0.063, 'l': 0.057,
    'd': 0.055, 'i': 0.053, 's': 0.051, 'r': 0.040,
    't': 0.034, 'n': 0.031, 'q': 0.024, 'p': 0.008,
    'm': 0.005, 'f': 0.004,
}

# EVA word length distribution (from 1411-word manuscript sample)
# Used by synthetic EVA generator to match real word length patterns
EVA_LENGTH_DISTRIBUTION = {
    1: 0.052, 2: 0.048, 3: 0.082, 4: 0.184,
    5: 0.272, 6: 0.213, 7: 0.089, 8: 0.028,
    9: 0.021, 10: 0.004, 11: 0.004,
}

# Medieval Latin vocabulary for random Latin baseline
# Common words from pharmaceutical/herbalist texts
# This gives Latin its BEST shot -- we use domain-relevant vocabulary
LATIN_VOCABULARY = [
    "aqua", "oleum", "radix", "herba", "folium", "flos", "semen",
    "cortex", "sal", "mel", "vinum", "lac", "cera", "resina",
    "pulvis", "unguentum", "emplastrum", "decoctum", "infusum",
    "recipe", "misce", "adde", "cola", "fiat", "detur", "solve",
    "contere", "coque", "distilla", "filtra", "digere", "macera",
    "dosis", "drachma", "uncia", "libra", "manipulus", "gutta",
    "ana", "quantum", "satis", "ad", "cum", "in", "per", "pro",
    "bis", "ter", "quotidie", "mane", "vespere", "nocte",
    "calidus", "frigidus", "siccus", "humidus", "dulcis", "amarus",
    "vas", "mortarium", "pistillum", "cucurbita", "alembicum",
    "fornax", "ignis", "balneum", "hora", "dies", "mensis",
    "purgatio", "digestio", "calcinatio", "sublimatio", "fixatio",
    "tinctura", "essentia", "spiritus", "extractum", "syrupus",
    "confectio", "electuarium", "cataplasma", "linimentum",
    "absinthe", "aloe", "camphora", "cassia", "cinnamomum",
    "crocus", "gentiana", "glycyrrhiza", "myrrha", "opium",
    "piper", "rhabarbarum", "rosa", "salvia", "thymum",
]

# v2 pass/fail thresholds
V2_THRESHOLDS = {
    # If real Voynich coherence exceeds ALL three baselines by this z-score,
    # the pipeline is Voynich-specific
    "min_z_score": 2.0,

    # If any baseline type scores within this range of real, pipeline is too flexible
    "flexibility_threshold": 0.10,  # If baseline mean is within 0.10 of real coherence

    # Minimum folios where real must significantly beat all baselines
    "min_discriminating_folios": 4,

    # P-value threshold
    "significance_level": 0.01,
}
```

**v2_generators.py contents:**

```python
"""
Non-Voynich text generators for vocabulary specificity testing.

Three generators that produce text the decoder should NOT be able to decode well:
1. Synthetic EVA: Random character combinations matching manuscript statistics
2. Character-shuffled: Real words with internal characters scrambled
3. Random Latin: Medieval pharmaceutical Latin vocabulary
"""

import random
import re
from typing import List
from v2_config import EVA_CHAR_FREQUENCIES, EVA_LENGTH_DISTRIBUTION, LATIN_VOCABULARY


def generate_synthetic_eva(real_eva_text: str, seed: int) -> str:
    """
    Generate synthetic EVA text matching the manuscript's statistical profile.

    Produces fake words that:
    - Use EVA characters at manuscript-matching frequencies
    - Match the manuscript's word length distribution
    - Preserve the original folio's line structure (words per line)
    - Never appeared in the real manuscript

    This tests whether the decoder's mappings are specific to real Voynich
    morphology or will match any EVA-alphabet string.
    """
    rng = random.Random(seed)

    # Build character sampling weights
    chars = list(EVA_CHAR_FREQUENCIES.keys())
    weights = list(EVA_CHAR_FREQUENCIES.values())

    # Build length sampling weights
    possible_lengths = list(EVA_LENGTH_DISTRIBUTION.keys())
    length_weights = list(EVA_LENGTH_DISTRIBUTION.values())

    # Parse the real text to get line structure
    lines = real_eva_text.strip().split('\n')
    output_lines = []

    for line in lines:
        line = line.strip()
        # Preserve non-text lines (headers, markup, comments)
        if not line or line.startswith('#') or line.startswith('===') or line.startswith('['):
            output_lines.append(line)
            continue

        # Count real words on this line
        cleaned = re.sub(r'<[^>]*>', '', line)
        cleaned = re.sub(r'!', '', cleaned)
        real_words = [w.strip() for w in cleaned.split('.') if w.strip()]
        word_count = len(real_words)

        # Generate that many synthetic words
        synthetic_words = []
        for _ in range(word_count):
            # Pick a length from the distribution
            length = rng.choices(possible_lengths, weights=length_weights, k=1)[0]
            # Generate random characters at that length
            word = ''.join(rng.choices(chars, weights=weights, k=length))
            synthetic_words.append(word)

        output_lines.append('.'.join(synthetic_words))

    return '\n'.join(output_lines)


def generate_char_shuffled(real_eva_text: str, seed: int) -> str:
    """
    Shuffle characters WITHIN each word while preserving word lengths and line structure.

    This destroys morphological structure (operator-stem-suffix patterns) while
    keeping the exact same character distribution per word. If the decoder relies
    on specific character sequences (like 'qo' as operator prefix or 'edy' as
    root stem), character shuffling will break those patterns.

    If the decoder still produces high coherence on character-shuffled words,
    it means the mappings are matching individual characters rather than
    meaningful morphological units.
    """
    rng = random.Random(seed)

    lines = real_eva_text.strip().split('\n')
    output_lines = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('===') or line.startswith('['):
            output_lines.append(line)
            continue

        # Extract words, preserving markup structure
        cleaned = re.sub(r'<[^>]*>', '', line)
        cleaned = re.sub(r'!', '', cleaned)
        real_words = [w.strip() for w in cleaned.split('.') if w.strip()]

        shuffled_words = []
        for word in real_words:
            # Shuffle characters within the word
            char_list = list(word)
            rng.shuffle(char_list)
            shuffled_words.append(''.join(char_list))

        output_lines.append('.'.join(shuffled_words))

    return '\n'.join(output_lines)


def generate_random_latin(real_eva_text: str, seed: int) -> str:
    """
    Replace Voynich words with random medieval Latin pharmaceutical vocabulary.

    Uses domain-relevant Latin vocabulary (herbs, preparations, instructions,
    measurements) to give the Latin baseline its BEST possible shot. If the
    decoder produces high coherence even on Latin pharmaceutical text, the
    mappings are truly language-agnostic.

    Preserves the original folio's line structure (words per line).
    """
    rng = random.Random(seed)

    lines = real_eva_text.strip().split('\n')
    output_lines = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('===') or line.startswith('['):
            output_lines.append(line)
            continue

        cleaned = re.sub(r'<[^>]*>', '', line)
        cleaned = re.sub(r'!', '', cleaned)
        real_words = [w.strip() for w in cleaned.split('.') if w.strip()]
        word_count = len(real_words)

        # Pick random Latin words
        latin_words = [rng.choice(LATIN_VOCABULARY) for _ in range(word_count)]

        output_lines.append('.'.join(latin_words))

    return '\n'.join(output_lines)
```

**Validation:**

- [ ] v2_config.py imports from v1 config correctly
- [ ] All three generators preserve line structure from real EVA text
- [ ] Synthetic EVA produces plausible-looking but fake EVA words
- [ ] Character shuffle changes character order within each word
- [ ] Random Latin uses the predefined vocabulary list
- [ ] All generators accept seed parameter for deterministic output
- [ ] Running same generator with same seed produces identical output

**After completing Phase 1, read this document again to find Phase 2.**

---

## Phase 2: v2 Baseline Runner

**Goal:** Run all three baseline types through the existing decoder wrapper.

**Files to create:**

- `validation/blind_decode_test/v2_baselines.py` -- Runs all baseline types

**v2_baselines.py must:**

1. Import `decode_eva_text` from the existing `decoder.py` (do NOT rewrite the decoder)
2. Import all three generators from `v2_generators.py`
3. Import `load_eva_folio` from existing `utils.py`
4. For each test folio and each baseline type:
   - Load the real EVA text
   - Generate 100 variants using the appropriate generator and seed range
   - Decode each variant through the SAME pipeline
   - Collect coherence scores, known ratios, category distributions
   - Compute distribution statistics (mean, std, min, max, percentiles)
5. Save results per folio per baseline type

**Seed assignment:**

- Synthetic EVA: seeds 1000 through 1099
- Character shuffle: seeds 2000 through 2099
- Random Latin: seeds 3000 through 3099

**Output per folio per baseline type:**

```json
{
    "folio": "f10r",
    "baseline_type": "synthetic_eva",
    "iterations": 100,
    "coherence_scores": [0.23, 0.19, ...],
    "known_ratios": [0.08, 0.11, ...],
    "category_counts_summary": {"ingredient": 42, "action": 31, ...},
    "stats": {
        "coherence_mean": 0.21,
        "coherence_std": 0.04,
        "coherence_p5": 0.15,
        "coherence_p25": 0.18,
        "coherence_p50": 0.21,
        "coherence_p75": 0.24,
        "coherence_p95": 0.28,
        "known_ratio_mean": 0.09,
        "known_ratio_std": 0.03,
    }
}
```

**Print progress during execution.** This will be 1500 decode operations. Print every 50.

**Validation:**

- [ ] Imports decoder.py without modification
- [ ] Generates exactly 100 iterations per baseline type per folio
- [ ] All seeds are deterministic
- [ ] Results saved to JSON with full score arrays (not just summary stats)
- [ ] Progress printed during execution

**After completing Phase 2, read this document again to find Phase 3.**

---

## Phase 3: v2 Comparison Engine

**Goal:** Compare real Voynich decode against all three baseline types.

**Files to create:**

- `validation/blind_decode_test/v2_compare.py` -- v2 statistical comparison

**v2_compare.py must:**

1. Load real decode results from v1.1 (already in `results/real_decode_*.json`)
2. Load all three baseline distributions from Phase 2
3. For each folio, compute against EACH baseline type:
   - Z-score: `(real_coherence - baseline_mean) / baseline_std`
   - Empirical p-value: `count(baseline >= real) / total`
   - Effect size (Cohen's d)
   - Known ratio comparison: `real_known_ratio - baseline_known_ratio_mean`
   - Category overlap: How many of the real decode's categories appear in baseline decodes?
4. Handle edge case: if baseline_std == 0 (all identical scores), report as "DEGENERATE" with explanation
5. Compute per-folio verdict:
   - **DISCRIMINATING**: Real coherence significantly exceeds ALL THREE baselines (p < 0.01 for each)
   - **PARTIAL**: Real exceeds some but not all baselines
   - **NON-DISCRIMINATING**: Real is comparable to one or more baselines
6. Compute overall verdict:
   - **PASS**: >= 4 folios are DISCRIMINATING
   - **PARTIAL**: 2-3 folios are DISCRIMINATING
   - **FAIL**: 0-1 folios are DISCRIMINATING

**Additional analysis: Baseline-vs-baseline comparison**

Also compare the three baseline types against each other:
- Does synthetic EVA score higher than random Latin? (Expected: yes, since it uses EVA characters)
- Does character-shuffled score higher than synthetic? (If yes, partial character patterns survive shuffling)
- Is there a hierarchy: Real > CharShuffle > SyntheticEVA > Latin?

If a clear hierarchy exists with real Voynich at the top, that supports vocabulary specificity even if individual p-values are marginal.

**Output:**

```json
{
    "test_date": "...",
    "test_version": "v2",
    "lexicon_sha256": "...",
    "overall_verdict": "PASS|PARTIAL|FAIL",
    "folios": {
        "f10r": {
            "real_coherence": 0.7043,
            "baselines": {
                "synthetic_eva": {
                    "mean": 0.21,
                    "std": 0.04,
                    "z_score": 12.36,
                    "p_value": 0.00,
                    "effect_size": 12.36
                },
                "char_shuffled": {
                    "mean": 0.45,
                    "std": 0.05,
                    "z_score": 5.09,
                    "p_value": 0.00,
                    "effect_size": 5.09
                },
                "random_latin": {
                    "mean": 0.08,
                    "std": 0.02,
                    "z_score": 31.22,
                    "p_value": 0.00,
                    "effect_size": 31.22
                }
            },
            "verdict": "DISCRIMINATING"
        }
    },
    "baseline_hierarchy": {
        "f10r": {
            "real": 0.7043,
            "char_shuffled": 0.45,
            "synthetic_eva": 0.21,
            "random_latin": 0.08,
            "hierarchy_holds": true
        }
    },
    "summary": {
        "folios_discriminating": 5,
        "folios_required": 4,
        "mean_z_synthetic": 11.5,
        "mean_z_char_shuffled": 4.8,
        "mean_z_latin": 28.3
    }
}
```

**Validation:**

- [ ] Loads real decode results from v1.1 output files
- [ ] Computes statistics against all three baseline types
- [ ] Handles degenerate cases (zero std dev)
- [ ] Baseline hierarchy analysis included
- [ ] Overall verdict logic correct

**After completing Phase 3, read this document again to find Phase 4.**

---

## Phase 4: v2 Report Generator

**Goal:** Generate a comprehensive human-readable report.

**Files to create:**

- `validation/blind_decode_test/v2_report.py` -- v2 Markdown report generator

**The report must include:**

1. **Header**: Test name, version (v2), date, lexicon checksum
2. **Executive Summary**: One paragraph with overall verdict
3. **Context**: Why v2 exists (link to v1.1 findings)
4. **Methodology**: Three baseline types explained clearly
5. **Per-Folio Results Table** (wide format):

| Folio | Real | Synthetic EVA (mean +/- sd) | Z | Char Shuffle (mean +/- sd) | Z | Latin (mean +/- sd) | Z | Verdict |

6. **Baseline Hierarchy Table**:

| Folio | Real | Char Shuffle | Synthetic EVA | Random Latin | Hierarchy Holds? |

7. **Known Ratio Comparison Table**:

| Folio | Real Known% | Synthetic Known% | CharShuffle Known% | Latin Known% |

8. **Interpretation**: What results mean for vocabulary specificity
9. **Comparison to v1.1**: How v2 results relate to v1.1 position-independence finding
10. **Key Statement** (REQUIRED regardless of outcome):

> "Test v2 asks whether the ZFD pipeline is specific to Voynich manuscript text or flexible enough to produce comparable output from any input. Three non-Voynich baselines were tested: synthetic EVA characters matching manuscript statistics, character-shuffled Voynich words destroying morphological patterns, and random medieval Latin pharmaceutical vocabulary. If real Voynich text produces significantly higher coherence than all three baselines through the same frozen pipeline, the decoder's vocabulary mappings are detecting structure specific to the manuscript. If any baseline produces comparable coherence, the degrees-of-freedom criticism is supported for that axis of comparison."

11. **Reproducibility**: Exact commands
12. **Lexicon Integrity**: SHA-256 verification

**Validation:**

- [ ] Report is valid Markdown
- [ ] All tables have correct columns
- [ ] Key statement included
- [ ] Context links to v1.1 findings
- [ ] Baseline hierarchy clearly presented

**After completing Phase 4, read this document again to find Phase 5.**

---

## Phase 5: v2 Test Runner

**Goal:** Wire everything together into a single-command test runner.

**Files to create:**

- `validation/blind_decode_test/run_test_v2.py` -- v2 main entry point

**run_test_v2.py must:**

1. Print banner: "ZFD BLIND DECODE FALSIFICATION TEST v2: VOCABULARY SPECIFICITY"
2. Verify prerequisites:
   - All 5 EVA files exist
   - Lexicon file exists
   - v1.1 real decode results exist in `results/` (reuse, do not re-decode)
   - Pipeline importable
3. Compute and record lexicon SHA-256 (START)
4. Load real decode results from v1.1 (DO NOT re-run real decode)
5. Run synthetic EVA baselines (100 iterations x 5 folios, print progress)
6. Run character-shuffled baselines (100 iterations x 5 folios, print progress)
7. Run random Latin baselines (100 iterations x 5 folios, print progress)
8. Run v2 statistical comparison
9. Verify lexicon SHA-256 (END) matches START
10. Generate v2 report
11. Save all outputs to `validation/blind_decode_test/results_v2/`
12. Print summary to console

**CLI:**

```
# Run full v2 test
python validation/blind_decode_test/run_test_v2.py

# Quick mode (10 iterations instead of 100)
python validation/blind_decode_test/run_test_v2.py --quick

# Single folio
python validation/blind_decode_test/run_test_v2.py --folio f10r

# Single baseline type
python validation/blind_decode_test/run_test_v2.py --baseline synthetic_eva
```

**Output directory structure:**

```
validation/blind_decode_test/results_v2/
    v2_test_metadata.json
    v2_synthetic_eva_f10r.json
    v2_synthetic_eva_f23v.json
    v2_synthetic_eva_f47r.json
    v2_synthetic_eva_f89r.json
    v2_synthetic_eva_f101v.json
    v2_char_shuffled_f10r.json
    v2_char_shuffled_f23v.json
    v2_char_shuffled_f47r.json
    v2_char_shuffled_f89r.json
    v2_char_shuffled_f101v.json
    v2_random_latin_f10r.json
    v2_random_latin_f23v.json
    v2_random_latin_f47r.json
    v2_random_latin_f89r.json
    v2_random_latin_f101v.json
    v2_comparison_results.json
    V2_VOCABULARY_SPECIFICITY_REPORT.md
```

**Validation:**

- [ ] `python run_test_v2.py --quick` completes without error
- [ ] All output files created in results_v2/
- [ ] Lexicon checksums match start and end
- [ ] Report generated and readable
- [ ] Console shows clear verdict
- [ ] v1.1 real decode results reused (not re-decoded)

**After completing Phase 5, read this document again to find Phase 6.**

---

## Phase 6: Integration and Cleanup

**Goal:** Update documentation and ensure clean repo state.

**Files to modify/create:**

- `validation/blind_decode_test/README.md` -- Update with v2 information
- `validation/blind_decode_test/BLIND_DECODE_TEST_LOG.md` -- Append v2 results section
- Main `README.md` -- Update falsification testing section

**README.md updates:**

Add v2 to the "Current Status" line. Add running instructions:

```markdown
### Test v2: Vocabulary Specificity (2026-02-04)

Tests whether non-Voynich input produces comparable results:

```bash
python validation/blind_decode_test/run_test_v2.py
```

Three baselines: synthetic EVA strings, character-shuffled Voynich words, random
medieval Latin. If real Voynich significantly outperforms all three, the pipeline
is detecting manuscript-specific structure.

Results: `validation/blind_decode_test/results_v2/V2_VOCABULARY_SPECIFICITY_REPORT.md`
```

**BLIND_DECODE_TEST_LOG.md updates:**

Append a new section "## Test v2: Vocabulary Specificity" with:
- Date and commit hash
- Results summary table
- Verdict
- What this means for the degrees-of-freedom criticism

**Validation:**

- [ ] README updated with v2 info
- [ ] Test log updated with v2 results
- [ ] No modifications to zfd_decoder/ files
- [ ] All files committed to feature branch
- [ ] PR created against main (do NOT auto-merge)

---

## SUCCESS CRITERIA

The CC task is complete when:

- [ ] All 6 phases implemented
- [ ] `python run_test_v2.py --quick` runs to completion
- [ ] Report generated with clear verdict
- [ ] Lexicon integrity verified
- [ ] All output files in results_v2/
- [ ] v1.1 real decode results reused (not re-decoded)
- [ ] README and test log updated
- [ ] Feature branch pushed, PR created
- [ ] No modifications to any zfd_decoder/ files

---

## WHAT THIS PROVES

**If PASS (real >> all three baselines):**

> "The ZFD pipeline produces significantly higher coherence on real Voynich manuscript text than on synthetic EVA strings, character-shuffled words, or medieval Latin vocabulary. The decoder's mappings are specific to Voynich morphological patterns. The degrees-of-freedom criticism is empirically refuted: the system cannot produce comparable output from arbitrary input."

**If PARTIAL (real >> some baselines but not all):**

> "The ZFD pipeline discriminates between Voynich text and some but not all non-Voynich inputs. [Specify which baseline type was comparable.] This suggests the decoder has [partial/character-level/alphabet-level] specificity but the vocabulary mappings may be [too flexible in specific ways]. Further refinement of the lexicon or coherence metric may be needed."

**If FAIL (real comparable to one or more baselines):**

> "The ZFD pipeline produces comparable coherence scores on real Voynich text and [baseline type]. The degrees-of-freedom criticism is supported: the decoder's flexibility allows it to generate Croatian-compatible output from non-Voynich input."

**Either outcome is published. This is how science works.**
