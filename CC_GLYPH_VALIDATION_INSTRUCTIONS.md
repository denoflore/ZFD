# Claude Code Instructions: Voynich-Glagolitic Glyph Validation

**Priority:** HIGH
**Branch:** `claude/voynich-zfd-validation-6FFwL`
**Repository:** `denoflore/ZFD`

---

## Context

We have established a behavioral paleographic link between Voynichese and Angular Glagolitic. The hypothesis: Voynichese is a highly abbreviated cursive Glagolitic derivative used for pharmaceutical notation in medieval Ragusa (Dubrovnik).

Two new documents have been added:
- `papers/VOYNICH_GLAGOLITIC_PALEOGRAPHIC_ANALYSIS.md` - Full paleographic comparison paper
- `mapping/GLYPH_MAPPING_GLAGOLITIC_VOYNICH.md` - Preliminary glyph mapping hypothesis

---

## Your Task: Validate Glyph Mappings

### Phase 1: Frequency Analysis

**Goal:** Compare Voynich glyph frequencies to expected Glagolitic/Croatian letter frequencies.

**Steps:**
1. Load the Voynich transcription corpus (EVA encoding)
2. Calculate frequency for each EVA glyph
3. Calculate positional frequency (initial, medial, final)
4. Compare to known Croatian letter frequency data

**Expected Output:**
```
EVA_glyph | total_freq | initial_freq | medial_freq | final_freq | croatian_match
o         | 15.2%      | 5.1%         | 45.3%       | 12.8%      | /o/ 8.9%
...
```

### Phase 2: Positional Distribution Test

**Goal:** Test if the gallows → consonant hypothesis holds.

**Hypothesis:** If gallows (EVA: k, t, f, p) are consonants, they should:
- Appear primarily at syllable onsets (word-initial, post-vowel)
- Be followed by vowel-like glyphs more often than consonant-like
- Not cluster heavily at word-final position

**Test:**
```python
def test_gallows_consonant_hypothesis(corpus):
    gallows = ['k', 't', 'f', 'p']
    vowels = ['o', 'a', 'e', 'i', 'y']
    
    for g in gallows:
        # Position distribution
        initial_pct = count_initial(g) / total_count(g)
        final_pct = count_final(g) / total_count(g)
        
        # Following character
        followed_by_vowel = count_followed_by(g, vowels) / total_count(g)
        
        print(f"{g}: initial={initial_pct:.1%}, final={final_pct:.1%}, +vowel={followed_by_vowel:.1%}")
```

**Expected if hypothesis valid:**
- initial_pct > 60%
- final_pct < 10%
- followed_by_vowel > 50%

### Phase 3: Vowel Distribution Test

**Goal:** Test if EVA 'o', 'a', 'e', 'i', 'y' behave as vowels.

**Croatian vowel characteristics:**
- Appear in every word
- Alternate with consonants (CVC structure common)
- Word-final position common (Croatian words often end in vowels)
- /a/, /o/, /i/ most common

**Test:**
```python
def test_vowel_hypothesis(corpus):
    proposed_vowels = ['o', 'a', 'e', 'i', 'y']
    
    for v in proposed_vowels:
        # Position
        final_pct = count_final(v) / total_count(v)
        
        # Alternation (preceded AND followed by non-vowel)
        alternation_pct = count_consonant_v_consonant(v) / total_count(v)
        
        print(f"{v}: final={final_pct:.1%}, CVC_pattern={alternation_pct:.1%}")
```

### Phase 4: Morpheme Boundary Validation

**Goal:** Test if the ZFD morpheme boundaries produce valid Croatian words when sound values are applied.

**Morpheme System:**
| ZFD | Sound | Croatian |
|-----|-------|----------|
| qo- | /ko-/ | ko- (who, as relative) |
| ch- | /h-/ | h- (into, for) |
| sh- | /š-/ | š- (with) |
| ed | /-ed/ | -ed/-jet (root/base) |
| od | /-od/ | -od (from) |
| ol | /-ol/ | -ol (oil) |
| -y | /-i/ | -i (adj/gen) |
| -ar | /-ar/ | -ar (agent) |

**Test:** For common Voynich words, apply sound values and check if result is:
1. Phonotactically valid Croatian
2. Semantically plausible for pharmaceutical context

Example:
- `chol` → /hol/ → "hall"? or /xol/ → ? (check)
- `shedy` → /šedi/ → possible verb form?
- `qokedy` → /kokedi/ → ko + ked + i → "which root"? (check against botanical terms)

### Phase 5: Generate Candidate Readings

**Goal:** Produce candidate readings for known plant sections.

**Method:**
1. Select folios with identified plants (e.g., f56r = blue flower)
2. Transcribe using EVA
3. Apply proposed sound values
4. Check if resulting words match Croatian botanical/pharmaceutical terms

**Output Format:**
```
Folio: f56r
Line 1: shedy qokol chedy...
Sound:  /šedi kokol hedi.../
Parsed: še-di ko-kol he-di
Candidate: "with [X] which [Y] for [Z]"
Confidence: LOW/MEDIUM/HIGH
```

---

## Data Requirements

1. **Voynich Corpus:** EVA transcription (available in repo or from voynich.nu)
2. **Croatian Frequency Data:** Letter frequency in Croatian (sources: croatian linguistics papers)
3. **Glagolitic Reference:** Unicode Glagolitic block (U+2C00–U+2C5F)
4. **Croatian Botanical Terms:** Pharmaceutical plant names in Croatian (source needed)

---

## Output Files

Please generate:

1. `analysis/glyph_frequency_analysis.csv` - Raw frequency data
2. `analysis/positional_distribution.csv` - Position-based stats
3. `analysis/hypothesis_test_results.md` - Summary of all hypothesis tests
4. `analysis/candidate_readings.md` - Proposed readings with confidence scores
5. `analysis/validation_summary.md` - Overall assessment of Glagolitic hypothesis

---

## Success Criteria

The Glagolitic hypothesis is SUPPORTED if:
- [ ] Gallows show consonant-like positional distribution (>60% initial)
- [ ] Proposed vowels show vowel-like distribution (>30% word-final)
- [ ] Frequency correlations with Croatian exceed r=0.5
- [ ] At least 3 candidate readings produce recognizable Croatian words
- [ ] No systematic violations of Croatian phonotactics

The hypothesis is FALSIFIED if:
- [ ] Gallows appear >30% at word-final (not consonant behavior)
- [ ] Proposed vowels cluster together (not vowel behavior)
- [ ] Frequency correlations with Croatian below r=0.2
- [ ] All candidate readings produce nonsense
- [ ] Systematic phonotactic violations

---

## Priority Order

1. **Frequency analysis** - Foundation for all other tests
2. **Positional distribution** - Critical for consonant/vowel identification
3. **Morpheme validation** - Tests the complete system
4. **Candidate readings** - The payoff

---

## Notes

- This is validation work, not exploration
- We are testing a specific hypothesis with preregistered success/failure criteria
- Document everything, including negative results
- If the hypothesis fails, that's valuable data

---

*Instructions prepared February 1, 2026*
*Contact: Chris Zuger via repo issues*
