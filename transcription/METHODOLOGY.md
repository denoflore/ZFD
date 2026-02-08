# Voynich Manuscript Paleographic Transcription -- Methodology

**Date:** 2026-02-07
**Version:** 1.0.0
**Project:** ZFD (Zagreb-Franciscan-Dubrovnik) Voynich Hypothesis
**Scope:** Direct manuscript-to-Croatian transcription replacing EVA-dependent decode pipeline

---

## 1. Problem Statement

The European Voynich Alphabet (EVA) was designed under the assumption that each Voynich glyph represents one letter in an unknown alphabet. This assumption is wrong.

The ZFD hypothesis, supported by adversarial validation and positional distribution analysis, demonstrates that the Voynich Manuscript employs a **positional shorthand system** where:

- Glyphs in word-initial position function as grammatical operators
- Tall glyphs (gallows) in medial position abbreviate consonant clusters
- Glyphs in word-final position mark morphological suffixes
- Multiple-glyph sequences (ligatures) function as single units

A real paleographer, knowing the target language is Croatian with Latin pharmaceutical admixture, would never create an intermediate notation layer (EVA). This methodology describes the direct manuscript-to-Croatian pipeline that replaces EVA.

---

## 2. Theoretical Foundation

### 2.1 The Three-Layer Positional System

Every Voynich word decomposes as:

```
[OPERATOR] + [STEM (with optional GALLOWS abbreviation)] + [SUFFIX]
```

Not every word has all three layers, but this is the structural template. The layers are:

**Layer 1 -- Operators (word-initial):** Grammatical function markers (relative, comitative, dative, directional, topic). These are phonologically reduced forms of Croatian/Latin function words.

**Layer 2 -- Stems + Gallows (word-medial):** The lexical core. Gallows characters within the stem are abbreviation marks that expand into consonant clusters, following Croatian Angular Glagolitic cursive convention.

**Layer 3 -- Suffixes (word-final):** Morphological markers (adjective, noun, instrumental, substance, process). These mark Croatian grammatical categories.

### 2.2 The 7-Layer Constraint Stack

Transcription decisions are validated against seven hierarchical constraint layers:

```
Layer 7: CODEX    -- scribal hand, abbreviation habits, spelling norms
Layer 6: TEXT     -- pharmaceutical genre, recipe formulae, ingredient lists
Layer 5: CLAUSE   -- [Imperative] + [Object] + [Prepositional phrase]
Layer 4: WORD     -- does this match unified_lexicon_v2? Croatian morphology?
Layer 3: MORPHEME -- operator + stem + suffix structure?
Layer 2: GLYPH    -- which letter given position, ductus, neighbors?
Layer 1: STROKE   -- what does this mark physically look like?
```

**Resolution principle:** When lower layers are ambiguous, go UP the stack. If you cannot read a stroke (Layer 1), the word constrains it (Layer 4). If you cannot read a word, the clause constrains it (Layer 5). If you cannot read a clause, the genre constrains it (Layer 6).

### 2.3 Historical Context

The manuscript connects to the Franciscan Pharmacy of Dubrovnik (Ragusa), founded 1317, directly contemporary with the Voynich Manuscript's radiocarbon-dated vellum (1404-1438). Ragusa was a multilingual trade hub where:

- Croatian Glagolitic literacy was standard for religious and administrative use
- Latin was the language of pharmacy and medicine
- Italian was the language of trade and governance

A pharmaceutical shorthand using Glagolitic-derived cursive conventions, with Latin technical vocabulary embedded in Croatian grammatical structure, is exactly what this environment would produce.

---

## 3. Source Material

### 3.1 Primary Source

The **manuscript image** is always the source of truth. Not EVA. Not the existing decoder output.

Images accessed via Yale Beinecke IIIF:
```
https://collections.library.yale.edu/iiif/2/{IIIF_ID}/full/full/0/default.jpg
```

IIIF IDs for all 197 folios are in `folio_iiif_map.json`.

Local image copies are available in `images/` (JPG) and `folios/jp2/` (JP2 originals).

### 3.2 Reference Materials

| File | Purpose | Status |
|------|---------|--------|
| `mapping/FINAL_CHARACTER_MAP_v1.md` | Character map (operators, gallows, stems, suffixes) | Production candidate |
| `mapping/GLYPH_MAPPING_GLAGOLITIC_VOYNICH.md` | Glagolitic-to-Voynich correspondences | Preliminary |
| `zfd_decoder/data/unified_lexicon_v2.json` | 304 verified stems | v1.0.0 |
| `zfd_decoder/data/operators.json` | 7 operators with detection order | Active |
| `zfd_decoder/data/gallows.json` | 4 gallows expansion rules | Active |
| `zfd_decoder/data/suffixes.json` | 15 suffixes with detection order | Active |
| `02_Transcriptions/LSI_ivtff_0d.txt` | EVA transcription (reference only) | Historical |

### 3.3 EVA as Cross-Reference Only

The EVA transliteration is used **only** for:
1. Identifying word boundaries (the '.' delimiter)
2. Cross-checking glyph identification against multiple transcribers
3. Documenting where the paleographic reading diverges from EVA

EVA is **never** used as input to the Croatian reading.

---

## 4. Transcription Process

### 4.1 Per-Folio Workflow

For each folio:

1. **Fetch image** via IIIF or local copy
2. **Assess layout:** Identify text blocks, labels, illustrations, marginal additions
3. **Profile writing speed:** Careful, standard, or rapid register
4. **Transcribe each line:**
   a. Read glyphs from the image (Layer 1-2)
   b. Parse into operator + stem + suffix (Layer 3)
   c. Check against lexicon (Layer 4)
   d. Validate against clause structure (Layer 5)
   e. Confirm genre plausibility (Layer 6)
   f. Cross-reference with hand sheet for glyph identification (Layer 7)
5. **Transcribe labels** with spatial correlation to illustrations
6. **Describe illustrations**
7. **Cross-reference with EVA** (document agreement/divergence)
8. **Assign confidence scores** (A/B/C/D)

### 4.2 Confidence Scoring

| Grade | Threshold | Criteria |
|-------|-----------|---------|
| **A** | 95%+ | All 7 layers converge. Unambiguous reading. Known vocabulary. Validated examples. |
| **B** | 80-94% | 5-6 layers converge. Minor ambiguity. Most probable reading given. |
| **C** | 60-79% | 3-4 layers converge. Multiple candidate readings listed. |
| **D** | <60% | Damaged, illegible, or genuinely ambiguous. Document what CAN be determined. |

### 4.3 Word Parsing Algorithm

```
Input: EVA word (e.g., "qokol")

Step 1: OPERATOR DETECTION (initial, longest match)
  "qo" matches → operator = "ko" (which/quantity)
  Remaining: "kol"

Step 2: SUFFIX DETECTION (final, longest match)
  "l" matches → suffix = "l" (noun ending)
  Remaining stem: "ko"

Step 3: GALLOWS EXPANSION (medial)
  "k" is gallows → expand to "st"
  Remaining: "o"

Step 4: DIRECT MAPPING
  "o" → "o"

Step 5: ASSEMBLY
  operator + expanded_stem + suffix = "ko" + "ost" + "o" + "l" = "koostol"

Step 6: VALIDATION
  "koostol" = "ko" (which) + "ostol" (bone oil)
  "ostol" is in lexicon (ost=bone + ol=oil) ✓
  Pharmaceutical context ✓
  Croatian morphology valid ✓

Output: "koostol" (which-bone-oil), Confidence A
```

---

## 5. Output Format

### 5.1 Per-Folio Directory Structure

```
transcription/folios/f{NNN}{r|v}/
├── TRANSCRIPTION.md          # Full line-by-line transcription
├── metadata.json             # Folio metadata
├── line_data.jsonl           # Machine-readable per-line data
└── notes.md                  # Observations and anomalies
```

### 5.2 Line Data Schema (JSONL)

Each line produces one JSON object with:
- `folio`: Folio identifier
- `line`: Line number
- `type`: text | label | marginalia | illustration_note
- `eva_transliteration`: EVA reading for cross-reference
- `zfd_croatian`: Croatian orthography (direct paleographic reading)
- `english_gloss`: English translation/gloss
- `confidence`: A | B | C | D
- `confidence_notes`: Justification for confidence grade
- `eva_divergences`: Array of positions where ZFD differs from EVA, with reasons
- `illustrations`: Description of adjacent illustrations
- `uncertain_readings`: Array of alternative readings for ambiguous passages

---

## 6. Validation Framework

### 6.1 Internal Validation

- **Positional distribution:** Operators must appear >50% word-initial; gallows must appear >65% medial; suffixes must appear >50% word-final
- **Lexicon matching:** At least 60% of parsed stems should match unified_lexicon_v2
- **Morphological validity:** Results must satisfy Croatian phonotactic constraints
- **Genre consistency:** Pharmaceutical folios should produce pharmaceutical vocabulary

### 6.2 External Validation

- **Curio adversarial validation:** Labels "ostol" and "otrorhetri" confirmed
- **Spatial correlation:** Pharmaceutical labels must match their illustration positions
- **Latin pharmaceutical terms:** Known terms (oral, dolor, sal, ana) must appear in pharmaceutical sections
- **Native speaker review:** Georgie validates readings as Croatian

### 6.3 Cross-Validation with EVA Pipeline

For every line, the transcription records:
- Whether the paleographic reading agrees with the EVA-pipeline reading
- Where they disagree, which has better evidence
- What vocabulary the paleographic reading finds that EVA missed

---

## 7. Limitations and Caveats

1. **Glyph ambiguity:** Some characters (i/n, e/c-of-ch, o/a at speed) are visually identical. Position and context resolve most cases, but genuine ambiguity remains.

2. **Gallows expansion is conditional:** Not every gallows instance expands the same way. Context (known stems, phonological constraints) guides expansion.

3. **Operator detection is probabilistic:** Not every word-initial "o" is an operator (32% are). Not every initial "d" is a dative marker (26% are). Genre and syntax constrain the decision.

4. **Damaged/faded text:** Some folios have damage, ink fading, or repairs that obscure glyphs. These are marked as confidence D.

5. **Unknown vocabulary:** The unified_lexicon_v2 contains 304 stems. Stems not in the lexicon require contextual inference and receive lower confidence grades.

6. **Single-scribe assumption:** The analysis assumes a single scribal hand throughout. If future evidence identifies multiple scribes, abbreviation conventions may vary between them.

---

## 8. Relationship to Existing ZFD Decoder

The existing pipeline in `zfd_decoder/` works as:
```
EVA input → Tokenize → Detect operators → Expand gallows → Match stems → Resolve suffixes → Croatian output
```

The paleographic transcription **replaces steps 1-3** by going directly from image to Croatian. The decoder's stem matching and suffix resolution (steps 4-6) become **validation checks** rather than transformation steps.

The transcription pipeline is:
```
Manuscript image → Paleographic reading → Croatian orthography → Validate against lexicon
```

---

*This methodology document describes the formal approach for the ZFD paleographic transcription of the Voynich Manuscript. It is intended to be suitable for peer review and publication.*
