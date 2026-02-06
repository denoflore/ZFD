# What the Coverage Numbers Actually Mean

## Coverage Analysis: Honest Assessment

The ZFD morpheme system identifies recurring structural patterns in the Voynich text. Here's what the numbers are, what they mean, and where they need work.

### Headline Number

**92.1% of tokens contain at least one of the 23 core two-letter morpheme patterns.**

This was previously reported as 96.8%. The higher number included longer pharmaceutical terms (Latin plant names, mineral terms) that boosted coverage marginally. The 92.1% reflects the structural backbone alone.

### Is That Meaningful?

Yes. Random strings generated from the same character frequency distribution match only **25.3%** of those patterns. The actual text matches at **3.6x the random baseline**.

| Test | Match Rate |
|------|-----------|
| Voynich actual text | 92.1% |
| Random strings (same char freq) | 25.3% |
| Signal above chance | 66.9 percentage points |
| Enrichment ratio | 3.6x |

This means the text is structured around these specific character combinations far more than chance allows. The morpheme patterns are capturing real linguistic structure, not noise.

### What This Does NOT Mean

The 92.1% does not mean "92% of words are translated." It means 92% of tokens contain recognizable structural elements. The difference matters:

- **Structural recognition**: "This token contains the pattern `ch` + vowel + `ed` + suffix" = YES, consistently
- **Semantic translation**: "This token means 'combine root preparation'" = PARTIAL, many tokens still ambiguous

### Coverage Method

Coverage is calculated by substring matching against a morpheme dictionary. The dictionary includes:

- **23 two-letter patterns** (ch, sh, qo, da, ed, ol, ar, al, or, in, etc.) -- these carry most of the weight
- **24 three-letter patterns** (ain, ost, dar, sal, kal, etc.)
- **37 four-letter patterns** (kost, chor, chol, flor, etc.)
- **10 five-letter patterns** (plant, coral, piper, etc.)

The two-letter patterns are short enough to raise legitimate questions about false positives. The random baseline test addresses this: 25.3% false positive rate means ~67% of the 92.1% coverage is genuine signal.

**Conservative estimate: ~67% definite structural signal, ~25% possible noise, ~8% unmatched.**

---

## Comparison Baselines

| Corpus | Char Entropy | Word Entropy | JSD vs Voynich |
|--------|-------------|-------------|----------------|
| Voynich (decoded) | 3.925 | 10.830 | -- |
| Apicius (Latin recipes) | 4.199 | 10.310 | 0.361 |
| Liber de Coquina (Latin recipes) | 3.965 | 8.895 | 0.381 |
| Pharma Miscellany (Latin pharma) | 4.032 | 7.410 | 0.373 |

The Voynich entropy profile sits squarely in the natural language range (3.5-4.5 bits/char, 9-12 bits/word) and closest to instructional/recipe texts.

---

## Latin Pharmaceutical Terms Found

These terms were identified through the morpheme system and cross-validated against medieval pharmaceutical vocabulary:

| Term | Latin | Meaning | Occurrences | Confidence |
|------|-------|---------|-------------|------------|
| ol | oleum | oil | High frequency | HIGH |
| sal | sal | salt | 62 | MEDIUM |
| ar | -arius/-are | agent/instrument | High frequency | MEDIUM |
| al | alumen/album | alum/white | Common | LOW |
| or | -or/-oris | substance | Common | LOW |

Previously reported terms "oral" (12 occurrences) and "dolor" (2) are included but at LOW confidence -- they may be coincidental substring matches rather than intentional Latin terms.

---

## What Still Needs Work

### In Progress
- **Individual word translations**: The morpheme system identifies structural patterns but specific Croatian vocabulary mapping remains partial. Three questions for native Chakavian speaker validation are pending.
- **Gallows-initial position claim**: Original claim that gallows appear "disproportionately word-initial" showed 14% actual vs 19% random expectation in retest. This needs reworking -- the medial gallows count is complicated by digraph patterns (ck, ct) that may represent different glyphs than standalone gallows. Analysis in progress.
- **"kost (bone) appears 2000+ times" claim**: This depends on the k->st gallows expansion assumption. The expansion produces valid Croatian phonotactics (confirmed at 100%), but whether every instance of expanded `st` means `kost` specifically is overclaimed. More accurate: the `ok-` prefix pattern appears at 7.6% of tokens (significantly more than in herbal section at 0-1.8%), suggesting the recipe section does use different vocabulary, but "bone" as the specific meaning needs more validation.

### Validated
- CATMuS stem match rate: 68.6% of identified stems found in medieval Latin pharmaceutical baselines
- 3 of 12 V1.5 semantic candidates promoted to confirmed status (fire/heat, dose/seed, cauldron)
- Native speaker validation of core vocabulary confirmed
- Adversarial AI test (Gemini Pro 3) -- hypothesis survived 8-turn falsification attempt

---

*Statistics document v2.0 | February 6, 2026*
*Corrected from v1.0 based on independent re-verification of all claims*
*Christopher G. Zuger | github.com/denoflore/ZFD*
