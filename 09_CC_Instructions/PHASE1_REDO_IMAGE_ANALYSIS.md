# ZFD Phase 1 REDO: Actual Paleographic Hand Sheet from Manuscript Images

## EXECUTION PATTERN

**Follow this iterative pattern:**
1. Read a section of this file
2. Do EXACTLY what that section specifies
3. Test/validate what you did
4. Read the file AGAIN to find where you are
5. Continue to next section
6. Repeat until complete

**DO NOT try to do everything at once. Work one exemplar at a time.**

---

## WHY THIS EXISTS

The previous Phase 1 attempt FAILED. It produced a hand sheet that repackaged the existing EVA character map and ZFD decoder output in paleographic language. That is not paleography. That is redescription.

**What went wrong:** The previous attempt started from EVA categories and worked backward to describe what the glyphs "should" look like. A real paleographer starts from INK ON VELLUM and works forward to figure out what the glyphs ARE.

**What must happen this time:** You will look at manuscript images FIRST. You will describe what you physically see BEFORE consulting any EVA transcription, character map, or decoder output. You will discover the scribe's system from the physical evidence, not from the existing decode.

---

## CRITICAL RULES

### Rule 1: IMAGE FIRST, ALWAYS
For every glyph analysis, you MUST:
1. Download the IIIF image region
2. Describe what you physically see (strokes, curves, dots, lifts)
3. ONLY THEN compare to EVA or ZFD readings

If you describe a glyph's appearance using EVA terminology before looking at the image, you have failed.

### Rule 2: NO COPY-PASTING FROM DECODER OUTPUT
The files in `zfd_decoder/data/` and `mapping/` are REFERENCE ONLY for validation AFTER your independent analysis. Do not use them as source material. If your hand sheet looks like a reformatted version of `FINAL_CHARACTER_MAP_v1.md`, you have failed.

### Rule 3: DESCRIBE WHAT YOU SEE, NOT WHAT YOU EXPECT
If you look at a glyph and it does NOT match what EVA or ZFD says it should be, DOCUMENT THAT. The point of this exercise is to find things the existing systems missed. If you find zero disagreements, you probably aren't really looking.

### Rule 4: SPECIFIC PIXEL EVIDENCE
Every glyph description must reference a specific image region with IIIF coordinates. "The glyph appears to be a circle" is not enough. "At IIIF region {x},{y},{w},{h} on folio f88r, the glyph is a clockwise circle approximately 3mm diameter with ink pooling at the 11-o'clock start point and a slight gap at closure" is what we need.

### Rule 5: UNCERTAINTY IS INFORMATION
If you cannot determine stroke order from the image, SAY SO. If two glyphs look identical to you at this resolution, SAY SO. If you need higher resolution to distinguish features, SAY SO. Confident descriptions of things you cannot actually see in the image are worse than honest uncertainty.

---

## REQUIRED READING

Before starting, read ONLY these:
1. **`folio_iiif_map.json`** -- So you can fetch images
2. **The 7-layer constraint skill** at the top of this document (pasted below)

DO NOT read the character map, decoder data, or EVA transcription until AFTER you have completed your independent glyph analysis for each exemplar.

---

## IIIF IMAGE ACCESS

```
Full folio (800px wide):
https://collections.library.yale.edu/iiif/2/{IIIF_ID}/full/800,/0/default.jpg

Full resolution:
https://collections.library.yale.edu/iiif/2/{IIIF_ID}/full/full/0/default.jpg

Region crop (full resolution):
https://collections.library.yale.edu/iiif/2/{IIIF_ID}/{x},{y},{w},{h}/full/0/default.jpg
```

**Image dimensions:** Full resolution is approximately 2714 x 3735 pixels.

**Useful region sizes for glyph analysis:**
- Single label: ~400x100 pixels at full res
- Text line: ~2000x100 pixels at full res  
- Paragraph block: ~2000x500 pixels at full res

**IIIF IDs for key folios:**
- f1r: 1006084
- f2r: 1006086
- f3r: 1006088
- f13v: 1006107
- f33v: 1006151
- f56r: 1006194
- f67r: 1006216
- f71r: 1006222
- f77r: 1006234
- f88r: 1037112
- f99r: 1006246
- f102v: 1006253
- f103r: 1006254
- f105r: 1006258
- f116r: 1006280

---

## STEP 1: Orientation Survey (30 minutes max)

**Goal:** Get a feel for the manuscript hand before analyzing anything.

Download the 800px version of these 5 folios:
1. f1r (1006084) -- opening page
2. f33v (1006151) -- mid-herbal
3. f88r (1037112) -- pharmaceutical
4. f77r (1006234) -- biological
5. f116r (1006280) -- near end

For each folio, write 3-5 sentences describing your FIRST IMPRESSION of the hand. Not glyph-by-glyph analysis. Just: What strikes you? Does it look fast or slow? Consistent or variable? What are the most visually distinctive features? How does the label hand compare to the body text hand?

**Output file:** `transcription/hand_sheet/00_FIRST_IMPRESSIONS.md`

**Validation:**
- [ ] 5 folios viewed at 800px
- [ ] First impressions written BEFORE any detailed analysis
- [ ] No EVA terminology used (no references to specific EVA characters)

**After completing Step 1, read this document again to find Step 2.**

---

## STEP 2: Gallows Character Study (THE CRITICAL TEST)

This is the most important step. The entire ZFD framework rests on gallows being cluster abbreviations, not standalone letters. If this is true, gallows should show PHYSICAL EVIDENCE of being compound marks (multi-stroke construction, abbreviation indicators, structural differences from simple letters).

**Method:** For each of the 4 gallows types, find 10 clear examples across different folios and examine them at full resolution.

### Step 2a: The "k" gallows (EVA k)

Download full-resolution crops of 10 instances of this character from different folios. Choose instances that are:
- In labels (careful hand): at least 3
- In body text (standard hand): at least 4
- In dense text (rapid hand): at least 3

For EACH instance:
1. Download the IIIF region containing the glyph (crop tight, maybe 100x80 pixels at full res)
2. Describe: How many strokes? What direction? Where does the pen start and end?
3. Describe: Is there an abbreviation mark (overline, dot, flourish) associated with it?
4. Describe: How does this glyph connect to its neighbors?
5. Describe: How tall is it compared to baseline characters?
6. Note: Does it look like a SINGLE character or a COMPOUND construction?
7. Compare: Do all 10 instances look the same, or are there variants?

**Output format per instance:**
```markdown
### k-gallows instance 3: f33v, IIIF region {x,y,w,h}
**Context:** [word it appears in, position in word]
**Strokes observed:** [description of what you physically see]
**Height:** [relative to neighboring characters]
**Connection:** [how it joins left and right neighbors]
**Abbreviation marks:** [any diacritical marks, overlines, dots]
**Assessment:** [single character / compound mark / uncertain]
**Notes:** [anything unusual]
```

Repeat for ALL FOUR gallows types:
- EVA k (10 instances)
- EVA t (10 instances)
- EVA f (10 instances)
- EVA p (10 instances)

**THEN AND ONLY THEN:** Compare your observations to the ZFD claim:
- k = st cluster abbreviation
- t = tr cluster abbreviation
- f = pr cluster abbreviation
- p = pl cluster abbreviation

Does the physical evidence support, contradict, or leave ambiguous the cluster abbreviation hypothesis? Be honest. If the evidence is ambiguous, say so. If you found something unexpected, document it.

**Output file:** `transcription/hand_sheet/01_GALLOWS_STUDY.md`

**Validation:**
- [ ] 40 total gallows instances examined (10 per type)
- [ ] Every instance has IIIF coordinates
- [ ] Physical descriptions written BEFORE comparison to ZFD claims
- [ ] Honest assessment of whether evidence supports cluster abbreviation
- [ ] At least one observation that is NOT in the existing character map

**After completing Step 2, read this document again to find Step 3.**

---

## STEP 3: The 'aiin' Question

EVA treats 'aiin' as four separate characters: a + i + i + n. ZFD treats it as a ligature unit (suffix '-ain'). This is testable from physical evidence.

**Method:** Find 15 instances of 'aiin' sequences in the manuscript.

For each:
1. Download full-res crop
2. Does the pen lift between 'a' and the first 'i'? Between 'i' and 'i'? Between 'i' and 'n'?
3. Is the 'aiin' sequence written faster/more fluidly than surrounding text?
4. Do the internal strokes ('ii') look like individual characters or like a single wavy line?
5. Is the final 'n' distinguishable from a third 'i', or does position alone determine the reading?

**Key question:** Is there physical evidence that 'aiin' is executed as a UNIT (single pen movement, no lifts) or as FOUR SEPARATE characters (distinct strokes with lifts between them)?

**Also find 5 instances where 'a', 'i', 'i', and 'n'-like strokes appear NOT in the 'aiin' pattern.** How do those individual characters compare to the same characters within 'aiin'?

**Output file:** `transcription/hand_sheet/02_AIIN_STUDY.md`

**Validation:**
- [ ] 15 'aiin' instances examined with IIIF coordinates
- [ ] 5 non-aiin instances of component characters examined
- [ ] Pen-lift analysis for each instance
- [ ] Clear conclusion: ligature unit / four characters / ambiguous with reasoning

**After completing Step 3, read this document again to find Step 4.**

---

## STEP 4: Baseline Character Inventory

Now do the full glyph inventory for non-gallows characters. For each character type, find 5 clear instances and describe the physical form.

**Characters to catalog:**
1. The circle glyph (EVA 'o')
2. The circle-with-tail glyph (EVA 'a')
3. The crescent glyph (EVA 'e')
4. The short vertical stroke (EVA 'i')
5. The stroke-with-descender (EVA 'y')
6. The 'ch' compound (EVA 'ch')
7. The 'sh' compound (EVA 'sh')
8. The 'q' character (EVA 'q')
9. The 'd' character (EVA 'd')
10. The hook stroke (EVA 'r')
11. The tall-ish stroke (EVA 'l')
12. The 'n'-like final stroke (EVA 'n')
13. The 'm'-like stroke (EVA 'm')
14. The 's' stroke (EVA 's')

For each: 5 instances, IIIF coordinates, physical description, positional behavior (where in words does it appear?), speed variants if visible.

**Critical questions:**
- Can you reliably distinguish 'i' from 'n' from 'r' from 'l' at this resolution? If not, document what CAN be distinguished and what requires context.
- Does 'ch' look like two separate characters written together or a single compound glyph?
- Is 'q' visually distinct from all other characters, or could it be confused with anything?
- Does word position change how characters look? (Same stroke in initial vs medial vs final position)

**Output file:** `transcription/hand_sheet/03_BASELINE_CHARACTERS.md`

**Validation:**
- [ ] All 14 character types cataloged
- [ ] 5 instances each with IIIF coordinates
- [ ] Honest about what CANNOT be distinguished at available resolution
- [ ] Positional variants documented where observed
- [ ] At least 2 cases where characters are genuinely ambiguous

**After completing Step 4, read this document again to find Step 5.**

---

## STEP 5: Speed and Section Comparison

**Goal:** Determine if the scribe writes differently in different sections or at different speeds.

Select one text block (~5 lines) from each of these sections:
1. f1r opening (text-only section, probably careful)
2. f13v herbal (labels + body text)
3. f88r pharmaceutical (labels + body text)
4. f77r biological
5. f116r late manuscript

For each block:
1. Download at full resolution
2. Measure (roughly) the x-height, ascender height, line spacing
3. Characterize: letter spacing (tight/loose), word spacing (clear/ambiguous), overall regularity
4. Note: any characters that look different from the same characters in other sections

**Key questions:**
- Is this one scribe or multiple scribes?
- If one scribe, are there speed registers (careful/standard/rapid)?
- Do labels and body text use the same hand?

**Output file:** `transcription/hand_sheet/04_SPEED_COMPARISON.md`

**Validation:**
- [ ] 5 text blocks examined from different sections
- [ ] Measurements (approximate) provided
- [ ] Single-scribe vs multi-scribe assessment with evidence
- [ ] Speed register assessment with evidence

**After completing Step 5, read this document again to find Step 6.**

---

## STEP 6: Synthesis -- Build the Hand Sheet

NOW you may consult the existing character map (`mapping/FINAL_CHARACTER_MAP_v1.md`) and the EVA transcription.

Compare your independent observations (Steps 1-5) against the existing decode:

1. **Agreements:** Where your physical observations confirm the existing character identifications
2. **Disagreements:** Where you saw something the existing maps don't account for
3. **New observations:** Things you noticed that aren't in any existing documentation
4. **Limitations:** What you could NOT determine from the available image resolution

Produce the final hand sheet as a synthesis of your independent analysis plus validation against existing work.

**Output files:**
- `transcription/hand_sheet/HAND_SHEET_v2.md` -- The formal hand description
- `transcription/hand_sheet/DISAGREEMENTS.md` -- Every case where your observations diverge from existing maps
- `transcription/hand_sheet/RESOLUTION_LIMITS.md` -- What requires higher resolution or different methodology

**Validation:**
- [ ] Hand sheet built from physical evidence (Steps 1-5) first
- [ ] Comparison to existing maps is explicit and documented
- [ ] Disagreements (if any) are honest and specific
- [ ] Limitations are honest
- [ ] At least ONE genuine observation not present in any existing documentation

**After completing Step 6, read this document again to find Success Criteria.**

---

## SUCCESS CRITERIA

This Phase 1 REDO succeeds if and only if:

✅ Every glyph description traces back to specific IIIF image coordinates  
✅ The gallows study provides physical evidence for or against cluster abbreviation  
✅ The 'aiin' study determines ligature vs separate characters from pen-lift evidence  
✅ The hand sheet contains at least ONE genuine new observation  
✅ Honest limitations are documented (not everything claimed with confidence A)  
✅ The work could NOT have been produced without looking at images  

This Phase 1 REDO FAILS if:

❌ The hand sheet reads like a reformatted version of the existing character map  
❌ Glyph descriptions match EVA terminology without independent evidence  
❌ All findings perfectly confirm existing work with zero surprises  
❌ No IIIF coordinates are provided for specific observations  
❌ Resolution limitations are not acknowledged  

---

## REPOSITORY LOCATION

All output goes in: `transcription/hand_sheet/`

New files from this spec:
```
transcription/hand_sheet/
├── 00_FIRST_IMPRESSIONS.md
├── 01_GALLOWS_STUDY.md
├── 02_AIIN_STUDY.md
├── 03_BASELINE_CHARACTERS.md
├── 04_SPEED_COMPARISON.md
├── HAND_SHEET_v2.md
├── DISAGREEMENTS.md
└── RESOLUTION_LIMITS.md
```

The existing files from the previous (failed) attempt should NOT be overwritten. The v2 files supersede them.

---

*A paleographer who produces a hand sheet identical to the existing character map hasn't done paleography. They've done transcription. We already have transcription. We need paleography.*
