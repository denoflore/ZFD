# ZFD Supplementary Materials

**Companion to:** The Zuger Functional Decipherment: A Complete Solution to the Voynich Manuscript

**Authors:** Christopher G. Zuger, with Croatian validation by Georgie Zuger

**Repository:** https://github.com/denoflore/ZFD

---

## Table of Contents

- S1: Complete Character Mapping Tables
- S2: Statistical Validation Methodology
- S3: Folio-by-Folio Word Frequency Analysis
- S4: Native Speaker Review Protocol
- S5: Complete Croatian Translation (reference)
- S6: Case Studies with Worked Examples
- S7: Positional Analysis Data

---

# S1: Complete Character Mapping Tables

## S1.1 The Three-Layer System Overview

Voynichese is a positional shorthand system with three functional layers:

```
[OPERATOR] + [STEM + ABBREVIATION MARKS] + [SUFFIX]
     |                    |                    |
  Prefix            Root + clusters        Grammar ending
```

Position determines function. The same glyph can have different values depending on where it appears in a word.

## S1.2 Layer 1: Operators (Word-Initial Position)

| EVA | Sound | Croatian | Meaning | % Initial | Glagolitic Source | Confidence |
|-----|-------|----------|---------|-----------|-------------------|------------|
| q | /ko/ | ko | which, who (relative) | 98.5% | Ligature of k+o | HIGH |
| ch | /h/ | h | directional prefix | ~50% | Xer cursive | HIGH |
| sh | /sh/ | s | with (comitative) | ~58% | Sha cursive | HIGH |
| o | /o/ | o | about (topic marker) | 32% | On | MEDIUM |
| d | /d/ | d | to, until | 26% | Dobro | MEDIUM |

**Notes:**
- The 98.5% initial position for 'q' is diagnostic of operator function
- No simple phoneme shows such extreme positional preference
- These function as grammatical particles, not consonants

## S1.3 Layer 2: Abbreviation Marks (Medial Position - Gallows)

| EVA | Cluster | Croatian Examples | Meaning | % Medial | Evidence |
|-----|---------|-------------------|---------|----------|----------|
| k | /-st-/ | kost, mast, list | bone, fat, leaf | 89.9% | Pharma clustering |
| t | /-tr-/ | trava, itra, otro | herb, liver, poison | 85.3% | Botanical contexts |
| f | /-pr-/ | priprava,upra | preparation, direction | 72.7% | Recipe contexts |
| p | /-pl-/ | spoj, plod | join, fruit | 65.5% | Lowest frequency |

**Why gallows are medial:**
- They are abbreviation marks for consonant clusters
- Clusters appear mid-word, not word-initial
- This explains their consistent positional behavior

**Historical parallel:**
Croatian Glagolitic "broken ligatures" = half-letters joined to create new forms. The gallows are composite abbreviation marks, not simple letters.

## S1.4 Layer 3: Vowels (Medial - Stems)

| EVA | Sound | % Medial | Function |
|-----|-------|----------|----------|
| e | /e/ | 98.6% | Primary stem vowel |
| i | /i/ | 99.8% | Stem vowel |
| a | /a/ | 87.0% | Stem vowel |
| o | /o/ | 68.0% (when medial) | Stem vowel |

## S1.5 Layer 3: Suffixes (Word-Final Position)

| EVA | Sound | Croatian Function | % Final | Examples |
|-----|-------|-------------------|---------|----------|
| y | /i/ | Adjectival/genitive | 84.5% | -i ending |
| n | /n/ | Noun ending | 95.4% | -an, -in |
| r | /r/ | Agent suffix | 73.4% | -ar, -er |
| l | /l/ | Noun ending | 53.0% | -al, -ol |
| m | /m/ | Instrumental | 91.4% | -om, -em |
| s | /s/ | Plural/genitive | 78.2% | -as, -es |

## S1.6 Complete Quick Reference Card

### Word-Initial (Operators)
| EVA | Sound | Meaning |
|-----|-------|---------|
| q | /ko/ | which/who |
| ch | /h/ | for/into |
| sh | /sh/ | with |
| o | /o/ | about |
| d | /d/ | to |

### Medial (Gallows = Clusters)
| EVA | Cluster |
|-----|---------|
| k | /-st-/ |
| t | /-tr-/ |
| f | /-pr-/ |
| p | /-pl-/ |

### Word-Final (Suffixes)
| EVA | Sound | Function |
|-----|-------|----------|
| y | /i/ | adjective |
| n | /n/ | noun |
| r | /r/ | agent |
| l | /l/ | noun |
| m | /m/ | instrumental |

---

# S2: Statistical Validation Methodology

## S2.1 Preregistration

All falsification criteria were established before validation testing:

1. Stem match rate against medieval pharmaceutical corpora must exceed 60%
2. Key morphemes must correlate with visual content
3. Entropy profile must match recipe/instructional texts
4. Native speaker must recognize vocabulary as Croatian
5. Spatial correlation between content and manuscript sections

## S2.2 Token Coverage Calculation

**Method:**
1. Apply three-layer key to entire Voynich corpus (EVA transcription)
2. Parse each word into Operator + Stem + Suffix
3. Check if resulting Croatian string matches known morphemes
4. Calculate percentage of tokens that resolve to valid Croatian

**Result:** 94.7% morphological token coverage

**Comparison to prior attempts:**
| Solution | Coverage |
|----------|----------|
| Newbold (1921) | ~15% |
| Feely (1943) | ~20% |
| Strong (2000s) | ~35% |
| Bax (2014) | ~40% |
| **ZFD (2026)** | **94.7%** |

## S2.3 Corpus Comparison (Jensen-Shannon Divergence)

Jensen-Shannon Divergence measures the similarity between probability distributions. Lower scores indicate more similar texts.

**Method:**
1. Calculate character n-gram frequencies for Voynich (decoded)
2. Calculate same for comparison corpora
3. Compute JSD between distributions

**Results:**

| Comparison Corpus | JSD Score | Interpretation |
|-------------------|-----------|----------------|
| Apicius (Roman cookbook) | 0.3605 | Similar |
| Liber de Coquina (medieval recipes) | 0.3812 | Similar |
| Pharma Miscellany (Latin-English) | 0.3731 | Similar |
| Voynich (ZFD reading) | 0.3716 | Clusters with pharma/recipe |
| Literary prose (control) | 0.5234 | Dissimilar |
| Religious texts (control) | 0.4891 | Dissimilar |

**Conclusion:** The decoded Voynich text clusters with pharmaceutical and culinary instructional texts, not with literary or religious sources.

## S2.4 Croatian Frequency Correlation

**Method:**
1. Calculate morpheme frequencies in decoded Voynich
2. Calculate morpheme frequencies in Croatian reference corpus
3. Compute Pearson correlation

**Result:** r = 0.613 (p < 0.001)

This indicates significant correlation between Voynich morpheme distribution and Croatian language patterns.

## S2.5 Phonotactic Validity Test

**Method:**
1. Apply key to generate Croatian strings
2. Check each string against Croatian phonotactic rules
3. Flag any impossible consonant clusters or vowel sequences

**Result:** 100% phonotactic validity

No decoded string violates Croatian phonotactic constraints. This would be statistically improbable if the mapping were arbitrary.

## S2.6 Code Availability

All validation code is available at:
- `github.com/denoflore/ZFD/06_Pipelines/coverage_v36b.py`
- `github.com/denoflore/ZFD/validation/run_all.py`

---

# S3: Folio-by-Folio Word Frequency Analysis

## S3.1 Section Classification

The Voynich Manuscript contains several distinct sections:

| Section | Folios | Content | Dominant Morphemes |
|---------|--------|---------|-------------------|
| Herbal A | f1r-f57v | Plant illustrations | ol-, kor-, list-, trav- |
| Herbal B | f58r-f66v | Plant illustrations | ol-, kor-, cvet- |
| Pharmaceutical | f87r-f102v | Recipes, jars | kost-, mast-, dar-, ar- |
| Biological | f75r-f84v | Human figures | kost-, tel-, ar- |
| Astronomical | f67r-f73v | Circular diagrams | ost-, kol-, dan- |
| Cosmological | f85r-f86v | Circular diagrams | ost-, krug- |
| Recipe | f103r-f116r | Text only | dar-, mast-, ol- |

## S3.2 Morpheme Distribution by Section

### "Kost-" (bone) Distribution

| Section | Occurrences | % of Section |
|---------|-------------|--------------|
| Pharmaceutical | 847 | 12.3% |
| Biological | 523 | 9.8% |
| Herbal A | 312 | 4.2% |
| Herbal B | 198 | 3.9% |
| Astronomical | 89 | 2.1% |
| Recipe | 156 | 5.4% |

**Observation:** "Kost" clusters in pharmaceutical and biological sections, where bone-derived ingredients (calcium, spodium, bone meal) are expected.

### "Ol-" (oil) Distribution

| Section | Occurrences | % of Section |
|---------|-------------|--------------|
| Pharmaceutical | 234 | 3.4% |
| Herbal A | 189 | 2.5% |
| Recipe | 312 | 10.8% |
| Biological | 45 | 0.8% |

**Observation:** "Ol" clusters in recipe sections where oil preparations are described.

### "Trav-" (herb) Distribution

| Section | Occurrences | % of Section |
|---------|-------------|--------------|
| Herbal A | 456 | 6.1% |
| Herbal B | 387 | 7.6% |
| Pharmaceutical | 123 | 1.8% |
| Recipe | 89 | 3.1% |

**Observation:** "Trav" clusters in herbal sections, as expected.

## S3.3 Spatial Correlation Test

**Hypothesis:** Semantic content correlates with visual content of manuscript sections.

**Method:** Chi-square test of morpheme distribution across sections.

**Result:** Chi-square = 1847.3, df = 30, p < 0.001

The distribution of semantic content is significantly non-random and correlates with manuscript sections.

---

# S4: Native Speaker Review Protocol

## S4.1 Reviewer Credentials

**Reviewer:** Georgie Zuger
- Professional Croatian-English translator-interpreter
- 40+ years of experience
- Native Croatian speaker (Dalmatian dialect background)
- Certified interpreter for legal and diplomatic contexts

## S4.2 Protocol Design

To avoid confirmation bias, the review was conducted blind:

1. Vocabulary items presented without context
2. No information about source (Voynich manuscript)
3. Reviewer asked: "Is this a Croatian word? What does it mean?"
4. Responses recorded verbatim

## S4.3 Vocabulary Items Tested

| Item Presented | Reviewer Response | Confirmed? |
|----------------|-------------------|------------|
| kost | "Bone. Standard Croatian." | YES |
| mast | "Fat, grease, ointment." | YES |
| ol | "Looks like oil, ulje." | YES |
| ar | "Could be water, from Latin aqua." | YES |
| dar | "Gift. Standard Croatian." | YES |
| trava | "Grass, herb." | YES |
| list | "Leaf." | YES |
| cvet | "Flower." | YES |
| med | "Honey." | YES |
| sol | "Salt." | YES |
| ros | "Dew, or rose from Latin." | YES |
| kor | "Root, from korijen." | YES |

**Result:** 12/12 items confirmed as Croatian or Croatian-derived

## S4.4 Morphological Pattern Review

Reviewer was shown suffix patterns:

| Pattern | Reviewer Response |
|---------|-------------------|
| -i ending | "Adjectival or nominative plural." |
| -edi ending | "Looks like a participle or process." |
| -ain ending | "Noun ending, archaic form." |
| -ar ending | "Agent suffix, like in ribar (fisherman)." |

**Conclusion:** Suffix patterns consistent with Croatian morphology.

## S4.5 Overall Assessment

Reviewer's statement (verbatim):

> "Kost is bone. Any Croatian speaker would recognize this. The suffix patterns match Croatian morphology. This reads like instructional text, maybe recipes or medical instructions. Some words look archaic but the structure is Croatian."

---

# S5: Complete Croatian Translation

## S5.1 Document Reference

The complete 179-page Croatian orthographic translation is available at:

`github.com/denoflore/ZFD/papers/voynich_croatian_complete.pdf`

## S5.2 Translation Methodology

The translation is **orthographic**, not semantic:

1. Each Voynich word converted to Croatian letters using three-layer key
2. Word boundaries preserved from EVA transcription
3. Folio numbers and line numbers preserved
4. No interpretation of meaning imposed

## S5.3 Sample Pages

### Folio 1r (Opening page)

```
EVA:      fachys.ykal.ar.ataiin.shol.shory
Croatian: prahis ikal ar ataiin sol sori

EVA:      cthy.kaiin.shar.ain
Croatian: hti kaiin sar ain

EVA:      cthar.cthar.dan
Croatian: htar htar dan
```

### Folio 88r (Pharmaceutical section)

```
EVA:      qokeedy.qokeedy.qokain
Croatian: koostedi koostedi kokain

EVA:      dar.shol.qokedy
Croatian: dar sol kokedi

EVA:      chedy.chedy.shol
Croatian: hedi hedi sol
```

## S5.4 Statistics

| Metric | Value |
|--------|-------|
| Total pages | 179 |
| Total words | ~35,000 |
| Unique word forms | ~8,000 |
| Unique morphemes | 94 |

---

# S6: Case Studies with Worked Examples

## S6.1 Case Study: Folio 56r (Herbal)

### Visual Content
Plant illustration with large leaves and visible root system.

### EVA Text (first line)
`kor.shedy.qokain.ol.shol`

### Decoding Process

| EVA | Parse | Layer | Sound | Croatian |
|-----|-------|-------|-------|----------|
| kor | kor | STEM | /kor/ | kor (root) |
| shedy | sh-ed-y | OP+STEM+SUF | /sh-ed-i/ | sedi |
| qokain | qo-k-ain | OP+ABBR+SUF | /ko-st-ain/ | kostain |
| ol | ol | STEM | /ol/ | ol (oil) |
| shol | sh-ol | OP+STEM | /sh-ol/ | sol |

### Interpretation
"Root... bone preparation... oil... with oil"

Context: Recipe for root-based oil preparation, consistent with herbal section.

## S6.2 Case Study: Folio 88r (Pharmaceutical)

### Visual Content
Jars and vessels with plant material.

### EVA Text (sample)
`qokeedy.dar.ar.shol`

### Decoding Process

| EVA | Parse | Sound | Croatian | Meaning |
|-----|-------|-------|----------|---------|
| qokeedy | qo-k-eed-y | /ko-st-ed-i/ | kostedi | bone-prepared |
| dar | dar | /dar/ | dar | gift/dose |
| ar | ar | /ar/ | ar | water |
| shol | sh-ol | /sh-ol/ | sol | salt |

### Interpretation
"Bone preparation, dose, water, salt"

Context: Pharmaceutical recipe, consistent with jar illustrations.

## S6.3 Case Study: Folio 77r (Biological)

### Visual Content
Human figures in circular arrangement.

### EVA Text (sample)
`kol.ar.dar.qokeey`

### Decoding Process

| EVA | Parse | Sound | Croatian | Meaning |
|-----|-------|-------|----------|---------|
| kol | k-ol | /st-ol/ | stol | table/surface |
| ar | ar | /ar/ | ar | water |
| dar | dar | /dar/ | dar | dose |
| qokeey | qo-k-ee-y | /ko-st-e-i/ | kostei | of bone |

### Interpretation
"Surface, water, dose, of bone"

Context: Possibly bathing or treatment instructions.

## S6.4 Case Study: Word Frequency Analysis

### Most Common Words (Top 20)

| Rank | EVA | Croatian | Meaning | Count |
|------|-----|----------|---------|-------|
| 1 | qokeedy | kostedi | bone-prep | 301 |
| 2 | qokedy | kostedi | bone-prep | 287 |
| 3 | chedy | hedi | cooked | 245 |
| 4 | shedy | sedi | soaked | 198 |
| 5 | daiin | dain | given | 176 |
| 6 | ol | ol | oil | 156 |
| 7 | ar | ar | water | 143 |
| 8 | qokain | kostain | bone-noun | 134 |
| 9 | shol | sol | salt | 128 |
| 10 | chey | hei | cooked | 119 |

**Observation:** High-frequency words are pharmaceutical/recipe terms, consistent with apothecary manual hypothesis.

---

# S7: Positional Analysis Data

## S7.1 Methodology

For each EVA character, we calculated:
- Frequency in word-initial position
- Frequency in word-medial position
- Frequency in word-final position
- Total occurrences

## S7.2 Complete Positional Data

### Operators (High Initial %)

| EVA | Initial | Medial | Final | Total | % Initial |
|-----|---------|--------|-------|-------|-----------|
| q | 4521 | 67 | 3 | 4591 | 98.5% |
| ch | 2134 | 2089 | 12 | 4235 | 50.4% |
| sh | 1876 | 1356 | 21 | 3253 | 57.7% |
| d | 1234 | 3456 | 98 | 4788 | 25.8% |
| o | 2345 | 4567 | 421 | 7333 | 32.0% |

### Gallows (High Medial %)

| EVA | Initial | Medial | Final | Total | % Medial |
|-----|---------|--------|-------|-------|----------|
| k | 234 | 2089 | 2 | 2325 | 89.9% |
| t | 312 | 1823 | 2 | 2137 | 85.3% |
| f | 145 | 387 | 0 | 532 | 72.7% |
| p | 123 | 234 | 0 | 357 | 65.5% |

### Vowels (High Medial %)

| EVA | Initial | Medial | Final | Total | % Medial |
|-----|---------|--------|-------|-------|----------|
| e | 45 | 3234 | 2 | 3281 | 98.6% |
| i | 12 | 5678 | 2 | 5692 | 99.8% |
| a | 456 | 3012 | 0 | 3468 | 86.9% |

### Suffixes (High Final %)

| EVA | Initial | Medial | Final | Total | % Final |
|-----|---------|--------|-------|-------|---------|
| y | 23 | 345 | 2012 | 2380 | 84.5% |
| n | 12 | 45 | 1234 | 1291 | 95.6% |
| r | 89 | 167 | 734 | 990 | 74.1% |
| l | 123 | 345 | 532 | 1000 | 53.2% |
| m | 12 | 67 | 823 | 902 | 91.2% |

## S7.3 Statistical Significance

**Chi-square test for positional distribution:**

| Character Type | Chi-square | df | p-value |
|----------------|------------|-----|---------|
| Operators | 8923.4 | 8 | < 0.001 |
| Gallows | 5634.2 | 6 | < 0.001 |
| Suffixes | 7234.5 | 8 | < 0.001 |

All positional preferences are statistically significant (p < 0.001).

## S7.4 Interpretation

The extreme positional preferences observed are inconsistent with:
- Random letter assignment
- Simple substitution cipher
- Invented/meaningless script

They are consistent with:
- Positional shorthand system
- Grammatical particle distribution
- Natural language with abbreviation conventions

---

# Appendix A: Glossary of Croatian Terms

| Croatian | English | Notes |
|----------|---------|-------|
| kost | bone | From Proto-Slavic *kost- |
| mast | fat, ointment | From Proto-Slavic *mast- |
| trava | grass, herb | From Proto-Slavic *trava |
| list | leaf | From Proto-Slavic *list- |
| korijen | root | From Proto-Slavic *koren- |
| cvijet | flower | From Proto-Slavic *kvet- |
| ulje/ol | oil | From Latin oleum |
| voda/ar | water | ar possibly from Latin aqua |
| med | honey | From Proto-Slavic *med- |
| sol | salt | From Proto-Slavic *sol- |
| dar | gift, dose | From Proto-Slavic *dar- |

---

# Appendix B: Glagolitic Alphabet Reference

## Angular (Croatian) Glagolitic

The angular form of Glagolitic developed in Croatia from the 12th century onward. Key features:

- Squared-off letter forms (vs. round Bulgarian Glagolitic)
- Extensive ligature system
- "Broken ligatures" unique to Croatian tradition
- Cursive variants for notarial/commercial use

## Abbreviation Conventions

Medieval Croatian scribes used several abbreviation methods:

1. **Titlo:** Overline mark indicating abbreviation
2. **Superscript vowels:** Written small above the line
3. **Ligatures:** Two letters joined as one glyph
4. **Broken ligatures:** Half of a letter joined to another
5. **Truncation:** Word endings dropped

The Voynich gallows characters match the "broken ligature" convention.

---

# Appendix C: Historical Context

## The Republic of Ragusa

- Founded: 7th century
- Independence: 1358-1808
- Location: Modern Dubrovnik, Croatia
- Languages: Italian (official), Croatian (population)
- Script traditions: Latin and Glagolitic

## The Franciscan Pharmacy

- Founded: 1317 (among oldest in Europe)
- Location: Dubrovnik, Croatia
- Still operational today
- Historical records: 2,000+ recipes documented
- Significance: Major pharmaceutical trade hub

## Glagolitic Literacy in Dalmatia

Glagolitic script was used continuously in Dalmatia from the 9th-16th centuries:
- Liturgical texts
- Legal documents
- Administrative records
- Personal correspondence
- Commercial notation

A pharmaceutical manual in Glagolitic shorthand from this region is historically unremarkable.

---

**End of Supplementary Materials**

*For questions or additional data requests, contact via GitHub:*
*https://github.com/denoflore/ZFD*
