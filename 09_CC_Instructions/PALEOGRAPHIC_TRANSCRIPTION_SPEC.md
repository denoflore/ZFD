# ZFD Paleographic Transcription: Direct Manuscript-to-Croatian Pipeline

## EXECUTION PATTERN

**Follow this iterative pattern:**
1. Read a section of this file
2. Build what that section specifies
3. Test/validate what you built
4. Read the file AGAIN to find where you are
5. Continue to next section
6. Repeat until complete

**DO NOT try to transcribe everything at once. Work folio by folio.**

---

## PROJECT OVERVIEW

Replace the EVA-dependent decode pipeline with a proper paleographic transcription going directly from Voynich manuscript images to Croatian orthography. EVA was built on wrong assumptions (each glyph = one letter in an unknown alphabet). The ZFD proved the manuscript uses a positional shorthand system with operators, abbreviation marks, and suffixes. A real paleographer would never have created an intermediate notation layer when the target language is known.

**End state:** 197 folios transcribed into Croatian orthography with per-line confidence scores, a comprehensive hand sheet documenting the scribe's specific letterforms, and a formal abbreviation inventory. All anchored to manuscript images via IIIF, not to EVA transliteration.

**Repository:** https://github.com/denoflore/ZFD  
**Working directory:** `transcription/` (new)

---

## REQUIRED READING

Before doing ANY transcription work, read these completely:

1. **`skills/glagolitic-angular-cursive-ocr/SKILL.md`** in the NSCA repo -- The 7-layer constraint system. This IS the methodology.
2. **`mapping/FINAL_CHARACTER_MAP_v1.md`** -- Current ZFD character map (operators, gallows, stems, suffixes)
3. **`mapping/GLYPH_MAPPING_GLAGOLITIC_VOYNICH.md`** -- Glagolitic-to-Voynich glyph correspondences
4. **`zfd_decoder/data/unified_lexicon_v2.json`** -- 304 verified stems. Your vocabulary anchor.
5. **`zfd_decoder/data/operators.json`** -- Operator inventory
6. **`zfd_decoder/data/gallows.json`** -- Gallows expansion rules
7. **`zfd_decoder/data/suffixes.json`** -- Suffix inventory
8. **`folio_iiif_map.json`** -- IIIF IDs for all 197 folios (Beinecke Digital Library)
9. **`02_Transcriptions/LSI_ivtff_0d.txt`** -- Existing EVA transcription (reference only, NOT source of truth)

---

## CRITICAL REQUIREMENTS

**METHODOLOGY:** This is behavioral paleography, not OCR. Every reading must be justified by the 7-layer constraint stack. A glyph you cannot read in isolation becomes readable when the word demands it, the syntax expects it, and the genre confirms it.

**IMAGE ACCESS:** Folio images are accessed via Yale Beinecke IIIF:
```
https://collections.library.yale.edu/iiif/2/{IIIF_ID}/full/full/0/default.jpg
```
IIIF IDs are in `folio_iiif_map.json`. For higher resolution regions:
```
https://collections.library.yale.edu/iiif/2/{IIIF_ID}/{x},{y},{w},{h}/full/0/default.jpg
```

**SOURCE OF TRUTH:** The manuscript image is always the source of truth. Not EVA. Not the existing decoder output. If the image contradicts EVA, EVA is wrong. If the image contradicts the decoder, the decoder is wrong.

**CONFIDENCE SCORING:** Every line gets a confidence score:
- **A (95%+):** All 7 layers converge. Unambiguous reading. Known vocabulary.
- **B (80-94%):** 5-6 layers converge. Minor ambiguity, most probable reading given.
- **C (60-79%):** 3-4 layers converge. Multiple candidate readings listed.
- **D (<60%):** Damaged, illegible, or genuinely ambiguous. Document what CAN be determined.

**EVA CROSSWALK:** For every line, include the EVA transliteration as a reference column. This enables validation of where EVA agrees/disagrees with the direct paleographic reading. Where they disagree, document why.

**DO NOT:**
- Treat EVA as input to the transcription. Look at the image.
- Force readings. If it's ambiguous, say so.
- Skip illustrations. They are content. Label what you see.
- Ignore line breaks, paragraph marks, or marginal additions.
- Assume the scribe was consistent. Document variations.

---

## Phase 1: Hand Sheet -- Profile the Scribe

**Goal:** Build a complete inventory of the Voynich scribe's specific letterforms, ligatures, abbreviation marks, and writing habits. This is the foundation everything else builds on.

**Method:** Select 15-20 lines from across the manuscript that are:
- Maximally legible (clear ink, minimal damage)
- From different sections (herbal, pharmaceutical, zodiac, biological, recipe)
- Representative of both careful and rapid writing

**Suggested exemplar lines (fetch via IIIF):**

| Section | Folio | Why |
|---------|-------|-----|
| Herbal (clear labels) | f1r lines 1-3 | Opening page, likely careful hand |
| Herbal (body text) | f2r lines 1-5 | Continuous text, standard pace |
| Pharmaceutical | f88r labels | Known spatial correlation (adversarial-validated) |
| Pharmaceutical | f102r labels + text | "orolaly" confirmed Latin pharmaceutical |
| Recipe section | f103r lines 1-5 | Dense recipe text |
| Zodiac | f70r labels | Labels on illustrations |
| Zodiac | f71r labels | Different label context |
| Biological | f75r lines 1-5 | Different genre within manuscript |
| Biological | f78r lines 1-5 | Cross-section comparison |
| Stars | f67r labels | Marginalia/label hand |
| Herbal (rapid) | f15r lines 1-5 | Mid-manuscript, possibly faster hand |
| Herbal (rapid) | f30r lines 1-5 | Later herbal, pace comparison |
| Recipe/pharma | f105r lines 1-3 | Late manuscript recipes |
| Recipe/pharma | f116r lines 1-3 | Near end, fatigue check |

**For each exemplar line, document:**

1. **Glyph inventory:** Every distinct letterform with stroke analysis
2. **Ductus notes:** Pen direction, lift points, speed indicators
3. **Ligature catalog:** Every character combination that merges
4. **Abbreviation marks:** Titlo, superscript, suspension, gallows behavior
5. **Spacing behavior:** Word boundaries, line breaks, indentation
6. **Variation notes:** Same character written differently? When/why?
7. **Speed indicators:** Where is the scribe writing carefully vs quickly?

**Files to create:**
- `transcription/hand_sheet/HAND_DESCRIPTION.md` -- Full scribal hand profile
- `transcription/hand_sheet/glyph_inventory.json` -- Machine-readable glyph catalog
- `transcription/hand_sheet/ligature_catalog.json` -- All observed ligatures
- `transcription/hand_sheet/abbreviation_inventory.json` -- All abbreviation conventions
- `transcription/hand_sheet/exemplar_notes/` -- Per-folio exemplar analysis

**Validation:**
- [ ] 15+ exemplar lines analyzed from 5+ manuscript sections
- [ ] Every Voynich glyph type accounted for in inventory
- [ ] Gallows characters analyzed by ductus (stroke order), not just shape
- [ ] At least 3 speed variants documented (careful/standard/rapid)
- [ ] Ligature catalog covers the 20 most common character pairs
- [ ] Abbreviation inventory distinguishes positional variants

**After completing Phase 1, read this document again to find Phase 2.**

---

## Phase 2: Ductus Analysis -- How the Strokes Were Made

**Goal:** Determine stroke order and pen movement for every glyph type. This is what EVA completely ignores and what distinguishes glyphs that LOOK similar but ARE different.

**Method:** For each glyph in the Phase 1 inventory:

1. **Stroke decomposition:** How many strokes? In what order?
2. **Pen lift analysis:** Where does the pen leave the vellum?
3. **Direction of movement:** Left-to-right? Top-to-bottom? Rotational?
4. **Connection points:** Where does this glyph connect to neighbors?
5. **Speed sensitivity:** Does this glyph change at different writing speeds?

**Key questions to resolve:**

| Question | Why It Matters |
|----------|---------------|
| Do all four gallows have different ductus? | Confirms they are distinct abbreviation marks, not variants |
| Are EVA 'e' and 'ch' distinguished by stroke or only by context? | Determines if EVA conflates distinct characters |
| Is EVA 'o' a single stroke or two? | Single = vowel, two = ligature? |
| Do 'aiin' sequences show continuous pen movement? | If yes, it's a ligature unit, not four separate characters |
| Are word-initial and word-medial forms of the same character different? | Positional variants = shorthand system confirmed |

**Files to create:**
- `transcription/hand_sheet/DUCTUS_ANALYSIS.md` -- Full ductus report
- `transcription/hand_sheet/stroke_sequences.json` -- Per-glyph stroke data
- Update `glyph_inventory.json` with ductus fields

**Validation:**
- [ ] All 4 gallows analyzed for distinct ductus
- [ ] At least 5 cases identified where ductus distinguishes glyphs EVA treats as identical
- [ ] At least 3 cases identified where EVA treats as different what ductus shows is the same
- [ ] 'aiin' and 'daiin' sequences analyzed as potential ligature units
- [ ] Positional variants cataloged (initial vs medial vs final forms)

**After completing Phase 2, read this document again to find Phase 3.**

---

## Phase 3: Exemplar Transcription -- 5 Anchor Folios

**Goal:** Full paleographic transcription of 5 carefully selected folios, going directly from manuscript image to Croatian orthography. These 5 will calibrate the method before scaling.

**Selection criteria:** Choose folios that maximize validation coverage:

| # | Folio | Section | Why This One |
|---|-------|---------|-------------|
| 1 | f88r | Pharmaceutical apparatus | Adversarial-validated spatial correlation. "ostol" and "otrorhetri" confirmed by Curio. Gold standard. |
| 2 | f102r | Pharmaceutical recipe | "orolaly" Latin label confirmed. Recipe structure visible. |
| 3 | f1r | Herbal (opening) | First page of manuscript. Careful hand. Establishes baseline. |
| 4 | f2r | Herbal (body) | Continuous text, standard pace. Tests reading at scale. |
| 5 | f71r | Zodiac | Labels on illustrations. Different genre, same scribe. Tests generalization. |

**For each folio, produce:**

```
transcription/folios/f{NNN}{r|v}/
├── TRANSCRIPTION.md          # Full line-by-line transcription
├── metadata.json             # Folio metadata, section, condition
├── line_data.jsonl           # Machine-readable per-line data
└── notes.md                  # Observations, anomalies, uncertainties
```

**Line data format (JSONL):**
```json
{
  "folio": "f88r",
  "line": 1,
  "type": "text|label|marginalia|illustration_note",
  "image_region": {"x": 0, "y": 0, "w": 0, "h": 0},
  "eva_transliteration": "qokeedy.otedy.qokeey...",
  "zfd_croatian": "koostedi. otredi. koostei...",
  "english_gloss": "bone preparation. treated. bone [substance]...",
  "confidence": "A",
  "confidence_notes": "All 7 layers converge. Known pharmaceutical vocabulary.",
  "eva_divergences": [
    {"position": 3, "eva": "k", "zfd": "st", "reason": "Gallows = cluster abbreviation, not standalone letter"}
  ],
  "illustrations": "Label adjacent to output vessel in apparatus diagram",
  "uncertain_readings": []
}
```

**Transcription format (TRANSCRIPTION.md):**
```markdown
# Folio f88r -- Paleographic Transcription

**Section:** Pharmaceutical apparatus  
**Condition:** Good. Minor ink fading lower right.  
**IIIF:** https://collections.library.yale.edu/iiif/2/{ID}/full/full/0/default.jpg

## Text

| Line | Croatian | English Gloss | Conf | EVA |
|------|----------|---------------|------|-----|
| L1 | koostedi otredi | bone preparation, treated | A | qokeedy.otedy |
| L2 | ... | ... | ... | ... |

## Labels

| Label # | Position | Croatian | English | Conf | EVA |
|---------|----------|----------|---------|------|-----|
| 1 | Output vessel | ostol | bone oil | A | okol |
| 2 | Process tube | otrorhetri | treated heated fluid | B | ... |

## Illustrations

[Description of apparatus/plant/figure with labeled components]

## Notes

[Observations about scribe behavior, ink quality, unusual forms]
```

**Validation per folio:**
- [ ] Every text line transcribed
- [ ] Every label transcribed
- [ ] Illustrations described
- [ ] EVA crosswalk complete (agreement/divergence documented)
- [ ] Confidence scores assigned per line
- [ ] At least one line validated against Georgie's native speaker review
- [ ] Spatial correlation checked (do labels match what they're labeling?)

**After completing Phase 3, read this document again to find Phase 4.**

---

## Phase 4: Abbreviation Inventory -- Formal Catalog

**Goal:** Systematic catalog of every abbreviation convention discovered in Phases 1-3. This becomes the formal reference for all subsequent transcription.

**Building on Phase 1 hand sheet, formalize:**

| Category | Example | Expansion | Frequency | Certainty |
|----------|---------|-----------|-----------|-----------|
| Gallows cluster | EVA 'k' | -st- | 2000+ | High |
| Gallows cluster | EVA 't' | -tr- | 1500+ | High |
| Gallows cluster | EVA 'f' | -pr- | ~800 | High |
| Gallows cluster | EVA 'p' | -pl- | ~600 | Medium |
| Operator prefix | EVA 'q' | ko- | 98.5% initial | High |
| Ligature unit | EVA 'aiin' | -ain | Suffix | High |
| Titlo/overline | [varies] | [varies] | [count] | [assess] |
| Suspension | [varies] | [varies] | [count] | [assess] |

**Files to create:**
- `transcription/ABBREVIATION_INVENTORY.md` -- Human-readable reference
- `transcription/abbreviation_rules.json` -- Machine-readable rules for automated pipeline
- `transcription/METHODOLOGY.md` -- Formal methodology document describing the paleographic approach

**Validation:**
- [ ] Every abbreviation type from Phase 1-3 cataloged
- [ ] Frequency counts from corpus-level data
- [ ] Certainty levels justified by evidence
- [ ] At least 5 abbreviations where this reading DIFFERS from EVA's implied reading
- [ ] Rules formatted for programmatic application

**After completing Phase 4, read this document again to find Phase 5.**

---

## Phase 5: Herbal Section Transcription (f1r-f57v)

**Goal:** Transcribe all herbal section folios. This is the largest section (~114 pages) and the most text-dense.

**Method:**
1. Fetch folio image via IIIF
2. Transcribe each line using 7-layer constraint stack
3. Transcribe all labels
4. Describe illustration (plant depiction)
5. Cross-reference with EVA transliteration
6. Assign confidence scores
7. Save in standard format (Phase 3 structure)

**Batch processing:** Work in batches of 5-10 folios. After each batch:
- Review for consistency with hand sheet
- Update abbreviation inventory if new forms found
- Checkpoint progress in `transcription/PROGRESS.md`

**Files to create:**
- `transcription/folios/f{NNN}{r|v}/` for each folio (standard structure)
- `transcription/PROGRESS.md` -- Running log of completed folios
- Update `transcription/ABBREVIATION_INVENTORY.md` with any new findings

**Validation per batch:**
- [ ] All folios in batch transcribed to standard format
- [ ] Confidence distribution reasonable (not all A's, not all D's)
- [ ] EVA divergences documented where found
- [ ] New glyph forms (if any) added to hand sheet
- [ ] Spatial correlation checked for labeled illustrations

**After completing Phase 5, read this document again to find Phase 6.**

---

## Phase 6: Pharmaceutical Section Transcription (f87r-f116r)

**Goal:** Transcribe all pharmaceutical/recipe section folios. This is the section with the strongest validation evidence (apparatus diagrams, Latin pharmaceutical terms, recipe structure).

**Priority order within section:**
1. Folios with apparatus diagrams (strongest spatial correlation)
2. Folios with confirmed Latin terms (oral, dolor, sal, ana)
3. Dense recipe text
4. Transitional/mixed folios

**Same method as Phase 5, plus:**
- Flag every Latin pharmaceutical term encountered
- Map recipe structure (Recipe/Take, Ingredients, Process, Administration)
- Cross-reference ingredients against unified_lexicon_v2 and V27 commodity list

**Files to create:**
- `transcription/folios/f{NNN}{r|v}/` for each folio
- `transcription/LATIN_PHARMACEUTICAL_INDEX.md` -- Every Latin term with folio location
- `transcription/RECIPE_STRUCTURE_MAP.md` -- Recipe boundaries and structure across section

**After completing Phase 6, read this document again to find Phase 7.**

---

## Phase 7: Zodiac, Biological, and Stars Sections

**Goal:** Complete remaining manuscript sections.

**Zodiac (f70r-f73v):** Label-heavy, illustration-heavy. Focus on label accuracy and figure identification.

**Biological (f75r-f84v):** The "bathing" or "biological" section. Different content domain. Document how the pharmaceutical vocabulary adapts (or doesn't) to body/anatomical content.

**Stars/Cosmological (f67r-f69v, f85r-f86v):** Sparse text, diagram-heavy. Every label matters.

**Rosettes (f85v-f86r):** Large foldout. Map all labels to diagram regions.

**Files to create:**
- `transcription/folios/f{NNN}{r|v}/` for all remaining folios
- `transcription/SECTION_COMPARISON.md` -- How vocabulary/syntax differs across manuscript sections

**After completing Phase 7, read this document again to find Phase 8.**

---

## Phase 8: Assembly, Validation, and Comparison

**Goal:** Assemble all folio transcriptions into a unified corpus. Validate against existing decoded output. Generate comparison report.

**Assembly:**
- Concatenate all `line_data.jsonl` files into `transcription/FULL_CORPUS.jsonl`
- Generate `transcription/FULL_TRANSCRIPTION.md` -- Complete manuscript, folio by folio
- Generate `transcription/STATISTICS.md` -- Coverage, confidence distribution, vocabulary stats

**Comparison with existing EVA-based decode:**
```
transcription/COMPARISON_REPORT.md
```
For every line in the manuscript:
- Does the paleographic reading agree with the EVA-pipeline reading?
- Where they disagree, which has better evidence?
- What vocabulary does the paleographic reading find that EVA missed?
- What EVA tokens are actually misreadings of ligatures or abbreviation marks?

**Corpus-level statistics:**
- Total words transcribed
- Confidence distribution (% A, B, C, D)
- EVA agreement rate (% of lines where readings match)
- New vocabulary discovered (not in unified_lexicon_v2)
- Updated suffix/prefix distributions

**Validation:**
- [ ] All 197 folios transcribed
- [ ] Full corpus assembled in JSONL and markdown
- [ ] Comparison report generated
- [ ] Statistics calculated
- [ ] Hand sheet finalized with all scribe variations
- [ ] Abbreviation inventory complete
- [ ] Methodology document suitable for publication

**After completing Phase 8, read this document again to find Success Criteria.**

---

## REFERENCE: IIIF Image Access

Beinecke Digital Library, Yale University. All Voynich folios accessible via IIIF:

```
Base URL: https://collections.library.yale.edu/iiif/2/{IIIF_ID}

Full image:     /full/full/0/default.jpg
Scaled:         /full/800,/0/default.jpg
Region:         /{x},{y},{w},{h}/full/0/default.jpg
High quality:   /full/full/0/default.png
```

IIIF IDs are in `folio_iiif_map.json` at repo root.

---

## REFERENCE: Existing Decoder Pipeline

The current pipeline in `zfd_decoder/` works as follows:
1. Takes EVA transliteration as input
2. Tokenizes by word boundaries
3. Applies operator detection (word-initial)
4. Applies gallows expansion (medial position)
5. Applies stem matching against unified lexicon
6. Applies suffix resolution (word-final)
7. Outputs Croatian orthography

The paleographic transcription REPLACES steps 1-3 by going directly from image to Croatian. Steps 4-7 become validation checks rather than transformation steps.

---

## REFERENCE: The 7-Layer Constraint Stack

```
Layer 7: CODEX    -- scribal hand, abbreviation habits, spelling norms
Layer 6: TEXT     -- pharmaceutical genre, recipe formulae, ingredient lists  
Layer 5: CLAUSE   -- [Imperative] + [Object] + [Prepositional phrase]
Layer 4: WORD     -- does this match unified_lexicon_v2? Croatian morphology?
Layer 3: MORPHEME -- operator + stem + suffix structure? 
Layer 2: GLYPH    -- which letter given position, ductus, neighbors?
Layer 1: STROKE   -- what does this mark physically look like?
```

When in doubt, go UP the stack. If you cannot read a stroke, the word constrains it. If you cannot read a word, the clause constrains it. If you cannot read a clause, the genre constrains it.

---

## SUCCESS CRITERIA

✅ Phase 1: Hand sheet complete with 15+ exemplars from 5+ sections  
✅ Phase 2: Ductus analysis distinguishing all glyph types  
✅ Phase 3: 5 anchor folios fully transcribed with validation  
✅ Phase 4: Formal abbreviation inventory (machine-readable + human-readable)  
✅ Phase 5: Herbal section complete (~114 pages)  
✅ Phase 6: Pharmaceutical section complete with Latin index  
✅ Phase 7: All remaining sections complete  
✅ Phase 8: Full corpus assembled, comparison report generated  
✅ Methodology document suitable for peer review  
✅ EVA divergence report documenting where EVA got it wrong  
✅ Updated vocabulary inventory (new words not in unified_lexicon_v2)  

---

**Estimated scope:** Phases 1-4 are the foundation (days). Phases 5-7 are the grind (weeks). Phase 8 is assembly (days).

**Human checkpoints required:**
- After Phase 1: Chris/Georgie review hand sheet for scribe behavior insights
- After Phase 3: Georgie validates anchor folio readings as native speaker
- After Phase 5: Georgie spot-checks herbal vocabulary
- After Phase 8: Full review of comparison report and methodology

---

*This transcription replaces EVA as the reference reading of the Voynich Manuscript.*
