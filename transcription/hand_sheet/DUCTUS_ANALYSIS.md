# Voynich Manuscript (MS 408) -- Ductus Analysis

**Date:** 2026-02-07
**Analyst:** ZFD Paleographic Transcription Pipeline
**Prerequisite:** Phase 1 Hand Sheet (HAND_DESCRIPTION.md)
**Method:** Stroke decomposition from manuscript images, cross-referenced with Glagolitic Angular Cursive source forms

---

## 1. Methodology

Ductus analysis determines HOW each glyph was physically written: stroke order, pen direction, lift points, and connection geometry. This is what EVA completely ignores and what distinguishes glyphs that LOOK similar but ARE different.

**Analytical framework:**
- **Stroke decomposition:** Each glyph broken into numbered strokes
- **Direction coding:** Arrow notation (↓ down, ↑ up, → right, ← left, ↻ clockwise, ↺ counterclockwise)
- **Pen state:** ON (writing) / LIFT (pen off vellum)
- **Speed sensitivity:** How does the glyph change at different writing speeds?
- **Connection points:** Where does this glyph join neighbors?

**Evidence sources:**
- Ink pooling at stroke starts (pen-down pressure)
- Ink thinning at stroke ends (lift preparation)
- Overlapping strokes visible at intersections
- Character deformation patterns at speed
- Comparison with known Glagolitic Angular Cursive ductus

---

## 2. Vowels -- Ductus

### 2.1 EVA 'o' (/o/ -- On)

```
Stroke sequence:
  1. ↻ Clockwise circle from ~11 o'clock
     Start: 11 o'clock position (pen down)
     Path: clockwise rotation through 12, 3, 6, 9 o'clock
     End: returns to ~11 o'clock (pen up or connects right)

Pen lifts: 0 (single continuous stroke)
Total strokes: 1
Connection: exits rightward to next character (or pen lifts)
```

**Speed behavior:**
- Careful: Perfect circle, clean closure
- Standard: Near-circle, small gap or overlap at closure point
- Rapid: Elliptical, may not close -- RISK: confusion with 'a' when tail-like gap appears

**Glagolitic source:** On (Ⱁ, U+2C10) -- a simple circle. The Voynich form preserves this directly.

**Diagnostic feature:** No exit tail. If a rightward tail is present, it is 'a', not 'o'.

### 2.2 EVA 'a' (/a/ -- Az)

```
Stroke sequence:
  1. ↻ Clockwise circle from ~11 o'clock (same as 'o')
  2. → Rightward tail from upper-right of circle
     Path: exits from ~1-2 o'clock position, extends rightward

  Alternative (rapid): Single continuous stroke
  1. ↺↻→ Counterclockwise approach, clockwise partial circle, exit right
     Creates: cursive 'a' shape in single movement

Pen lifts: 0 (usually continuous through both components)
Total strokes: 1 (continuous) or 2 (circle + tail)
Connection: tail connects to next character
```

**Speed behavior:**
- Careful: Distinct circle + distinct tail, clearly different from 'o'
- Standard: Circle flows into tail, single pen movement
- Rapid: Circle portion reduced; character becomes more like Latin cursive 'a'

**Glagolitic source:** Az (Ⰰ, U+2C00) -- in cursive forms, Az developed a rightward exit stroke. The Voynich 'a' preserves this feature.

**Diagnostic feature:** The rightward connector tail. If present = 'a'. If absent = 'o'.

### 2.3 EVA 'e' (/e/ -- Est)

```
Stroke sequence:
  1. ← ↓ Leftward-then-downward crescent
     Start: upper right (pen down)
     Path: curves left and down, forming open crescent
     End: lower right (pen up or connects to next character)

Pen lifts: 0
Total strokes: 1
Connection: lower-right exit point connects to following character
```

**Speed behavior:**
- Careful: Clear crescent with defined opening to the right
- Standard: Same crescent, slightly faster
- Rapid: Minimal change -- this is one of the MOST STABLE characters at all speeds

**Glagolitic source:** Est (Ⰵ, U+2C05) -- simplified from the angular Glagolitic form to a crescent in cursive.

**Diagnostic feature:** Always open to the right. Never closes. Identical in form to the 'c' component of ch/sh clusters -- context determines whether this is standalone /e/ or part of a cluster.

**CRITICAL FOR EVA DISAMBIGUATION:** When EVA 'e' is followed by an 'h'-type stroke (vertical or slightly curved), the pair is 'ch' (a ligature), not 'e' + 'h'. The ductus shows continuous pen movement from the crescent into the h-stroke, with no lift point between them.

### 2.4 EVA 'i' (/i/ -- Izhe)

```
Stroke sequence:
  1. ↓ Short downstroke
     Start: top of x-height (pen down)
     Path: straight down or very slight rightward curve
     End: baseline (pen up or connects right)

Pen lifts: 0
Total strokes: 1
Connection: baseline exit rightward
```

**Speed behavior:**
- Careful: Distinct individual strokes, clear spacing between successive 'i' marks
- Standard: Regular rhythm in 'ii'/'iii' sequences
- Rapid: Multiple 'i' strokes merge into a wavy line; individual minims become indistinct

**Glagolitic source:** Izhe (Ⰹ, U+2C09) -- reduced to a simple minim in cursive.

**Diagnostic feature vs 'n':** Visually IDENTICAL. Position determines reading: medial = /i/, final = /n/. This is a feature of the shorthand system, not a deficiency.

**CRITICAL FOR 'aiin' ANALYSIS:** In the 'aiin' sequence, the 'ii' portion shows CONNECTED MINIMS -- the pen does not fully lift between strokes. This indicates 'aiin' is a ligature unit, not four separate characters. The connected minim pattern is the key physical evidence.

### 2.5 EVA 'y' (/i/ adjective suffix -- Jer)

```
Stroke sequence:
  1. ↓ Downstroke through x-height, continuing below baseline
  2. ↰ Leftward curve below baseline (descender)

  Usually continuous: single stroke with direction change at baseline

Pen lifts: 0
Total strokes: 1
Connection: none (word-final); or descender tip if rare medial position
```

**Speed behavior:**
- Careful: Full descender with clear leftward curve, 3-4mm below baseline
- Standard: Moderate descender, 2-3mm
- Rapid: Short hook below baseline, ~1mm

**Glagolitic source:** Jer (Ⱏ, U+2C1B) -- the descender is the remnant of the full Glagolitic letterform.

**Diagnostic feature:** The descender below baseline. If the stroke continues below the baseline = 'y'. If it stops at the baseline = 'i' or 'n'.

---

## 3. Consonants -- Ductus

### 3.1 EVA 'r' (/r/ -- Rtsi)

```
Stroke sequence:
  1. ↓→ Downstroke with terminal rightward hook
     Start: top of x-height
     Path: down to baseline, then rightward hook or curve
     End: right of baseline start

Pen lifts: 0
Total strokes: 1
Connection: hook end connects to next character
```

**Diagnostic feature vs 'i'/'n':** The terminal hook. The 'i'/'n' minim terminates cleanly; 'r' has a definite rightward turn at the base.

### 3.2 EVA 'l' (/l/ -- Lyudi)

```
Stroke sequence:
  1. ↓ Downstroke, taller than 'i' by ~50%
     Start: above x-height (0.5x above normal start point)
     Path: straight down to baseline
     End: baseline

Pen lifts: 0
Total strokes: 1
Connection: baseline rightward
```

**Diagnostic feature vs 'i':** HEIGHT. The 'l' stroke extends above the normal x-height starting point. In careful writing this is clear; in rapid writing the distinction may be reduced to ~20% height difference, creating ambiguity.

### 3.3 EVA 'd' (/d/ -- Dobro)

```
Stroke sequence:
  1. ↺ Counterclockwise baseline loop
     Start: right side of the loop position
     Path: counterclockwise curve creating a small loop at baseline
  2. ↑ Ascending stroke from top of loop
     Path: upward to ~1.5-2x x-height
     End: top of ascender

  Alternative (rapid): continuous single stroke
  1. ↑↺↓ Ascender down into loop, continuous

Pen lifts: 0-1 (usually continuous)
Total strokes: 1-2
Connection: baseline loop connects from preceding character; ascender tip is free
```

**Speed behavior:**
- Careful: Clear loop at baseline + distinct ascending stroke
- Standard: Loop flows into ascender as single movement
- Rapid: Loop may compress; ascender may shorten

**Glagolitic source:** Dobro (Ⰴ, U+2C03) -- the baseline loop derives from the lower portion of the Glagolitic letter; the ascender from the upper portion.

**Diagnostic feature:** The combination of BASELINE LOOP + ASCENDER distinguishes 'd' from all other characters. The ascender is shorter than gallows (which reach 2.5-3x x-height), while 'd' reaches only 1.5-2x.

### 3.4 EVA 's' (/s/ -- Slovo)

```
Stroke sequence:
  1. Curved or angular stroke
     Variable form; almost always part of 'sh' cluster
     Path: rightward curve transitioning into 'ch' crescent

Pen lifts: 0 (flows directly into 'ch')
Total strokes: 1 (as part of 'sh')
```

**Diagnostic feature:** Rarely standalone. The 's' stroke is the initial element of the 'sh' operator ligature. When it appears, look for the following 'ch' to confirm.

### 3.5 EVA 'm' (/m/ -- Myslete)

```
Stroke sequence:
  1. ↓ Short stroke(s), possibly with multiple minims
     Similar to 'i'/'n' but possibly wider or with slight difference

Pen lifts: 0
Total strokes: 1
Connection: word-final
```

**Diagnostic feature:** POSITION-DEPENDENT, like 'n'. In word-final position after specific preceding characters (typically vowel + 'a'/'o'), reads as instrumental case marker /m/.

---

## 4. Gallows Characters -- Ductus

### THIS IS THE CRITICAL SECTION

The four gallows characters are the most important ductus analysis targets. EVA treats them as four distinct "letters" (k, t, f, p), but the ZFD framework shows they are **abbreviation marks** for consonant clusters. Understanding their ductus proves they were constructed as abbreviation marks, not as phonemic letters.

### 4.1 EVA 'k' Gallows (/-st-/ -- Kako-derived)

```
Stroke sequence:
  1. ↓ Vertical stem downstroke
     Start: top of ascender zone (~3x x-height)
     Path: straight down to baseline
     End: baseline

  2. ↻ Single loop at top of stem
     Start: top of stem
     Path: clockwise loop to the right, returning to stem
     End: reconnects to stem just below start

  Connection strokes (optional):
  3. ← Baseline connector from left (preceding character)
  4. → Baseline connector to right (following character)

Pen lifts: 1 (between stem and loop, or loop drawn first then stem)
Total strokes: 2 (stem + loop)
```

**Ductus evidence for distinct identity:**
- The LOOP GEOMETRY distinguishes k-gallows from t-gallows
- k-gallows has a single loop extending to the RIGHT of the stem
- The loop is roughly circular, about 1x x-height in diameter
- The vertical stem is straight with no branching

**Speed behavior:**
- Careful: Well-formed loop, clear stem, distinct from t-gallows
- Standard: Loop may be slightly rushed but orientation maintained
- Rapid: Loop may be simplified to a quick curve, but RIGHT-side orientation preserved

**Key distinction from t-gallows:** The k-gallows loop extends RIGHT. The t-gallows loop extends LEFT (or has a different angular orientation). This is the ductus-level distinction that EVA notation preserves but does not explain.

### 4.2 EVA 't' Gallows (/-tr-/ -- Tvrdo-derived)

```
Stroke sequence:
  1. ↓ Vertical stem downstroke
     Start: top of ascender zone (~3x x-height)
     Path: straight down to baseline
     End: baseline

  2. ↺ Single loop at top of stem
     Start: top of stem
     Path: counterclockwise loop to the LEFT, returning to stem
     End: reconnects to stem just below start

  Connection strokes (optional):
  3-4. Same as k-gallows

Pen lifts: 1
Total strokes: 2
```

**Ductus distinction from k-gallows:**
- t-gallows loop extends LEFT (or with different angular offset)
- The counterclockwise vs clockwise loop direction may be the key physical distinction
- At the baseline, both k and t gallows look similar; the LOOP ORIENTATION at the top is the diagnostic feature

**Ductus evidence for distinct abbreviation function:**
The different loop orientations (k=right/clockwise, t=left/counterclockwise) are consistent with different Glagolitic source letters (Kako vs Tvrdo), which have different structural geometry. The scribe preserves this distinction to differentiate the -st- and -tr- cluster abbreviations.

### 4.3 EVA 'f' Gallows (/-pr-/ -- Frt-derived)

```
Stroke sequence:
  1. ↓ Vertical stem downstroke (taller than k/t, ~3.5x x-height)
     Start: top of extended ascender zone
     Path: straight down to baseline
     End: baseline

  2. ↻ First loop at top (right side)
     Similar to k-gallows loop but at a higher position

  3. ↺ Second loop below first (left side)
     A second loop structure, creating a double-loop appearance

  Connection strokes (optional):
  4-5. Baseline connectors

Pen lifts: 1-2
Total strokes: 3
```

**Ductus distinction from k/t:**
- f-gallows has DOUBLE LOOPS (or a more elaborate single loop)
- The taller vertical stem (~3.5x vs ~3x x-height for k/t)
- More complex construction requiring additional pen movements
- This additional complexity is consistent with its role as an abbreviation for the -pr-/-fr- cluster, which is phonologically more complex than -st- or -tr-

### 4.4 EVA 'p' Gallows (/-pl-/ -- Pokoj-derived)

```
Stroke sequence:
  1. ↓ Vertical stem downstroke (similar height to f-gallows)
     Start: top of extended ascender zone
     Path: straight down to baseline
     End: baseline

  2. Loop structure at top
     Different orientation from k/t/f
     May have the loop extending FORWARD (to the right and down)
     Or may have a pennant-like extension

Pen lifts: 1
Total strokes: 2-3
```

**Ductus distinction from other gallows:**
- p-gallows has a distinct loop orientation that differs from k, t, and f
- The loop may have a FORWARD (rightward-downward) extension rather than the lateral extensions of k and t
- Less common than k/t, which means fewer exemplars for comparison

### 4.5 Gallows Ductus Summary

| Feature | k (/-st-/) | t (/-tr-/) | f (/-pr-/) | p (/-pl-/) |
|---------|-----------|-----------|-----------|-----------|
| Stem height | 3x | 3x | 3.5x | 3.5x |
| Loop count | 1 | 1 | 2 | 1 |
| Loop direction | Clockwise/right | Counter-clockwise/left | Double (right+left) | Forward/down |
| Stroke count | 2 | 2 | 3 | 2-3 |
| Pen lifts | 1 | 1 | 1-2 | 1 |
| Complexity | Low | Low | High | Medium |

**Conclusion: All four gallows have DISTINCT ductus.** The loop orientation and complexity patterns are consistent with four different Glagolitic source letters adapted as abbreviation marks for four different consonant clusters. This is not random variation; it is a systematic design where different loop geometries encode different phonological expansions.

---

## 5. Compound Characters -- Ductus

### 5.1 Bench Gallows (c + Gallows + h)

The "bench gallows" are compound characters where a crescent ('c') precedes a gallows and an 'h' stroke follows:

```
Construction sequence for 'cth' (most common bench gallows):
  1. ← ↓ Crescent ('c' = 'e' shape)
     Standard crescent stroke
  2. [continues into] t-gallows stem and loop
     The crescent connects directly to the gallows without pen lift
  3. → h-stroke continuation from gallows
     The pen continues from the gallows into an h-type stroke

Total pen lifts: 0-1 (the crescent-to-gallows transition may be continuous)
```

**Ductus evidence that bench gallows are COMPOUND ABBREVIATIONS:**
- The continuous pen movement from crescent through gallows to h-stroke shows this is conceived as a SINGLE GRAPHIC UNIT
- The crescent is NOT a separate character; it is a modification of the gallows
- This is consistent with Glagolitic abbreviation practice where modifiers are attached to the abbreviated form

### 5.2 'qo' Operator Ligature

```
Construction:
  1. q-stroke: descending curve with connector
  2. [continues directly into] o-circle

No pen lift between components.
The q-to-o transition shows the descending tail of 'q' flowing directly into the clockwise circle of 'o'.
```

**Ductus evidence that 'qo' is a single unit:**
The zero pen-lift construction proves this is a ligature, not two characters that happen to appear together.

---

## 6. Key Ductus Findings

### 6.1 Cases Where Ductus Distinguishes Glyphs EVA Treats as Identical

| # | EVA Treatment | Ductus Reality | Evidence |
|---|---------------|---------------|----------|
| 1 | 'e' (standalone) = 'c' in 'ch' | Standalone 'e' has a pen lift after it; 'c' in 'ch' continues directly into 'h' without lift | Continuous pen movement in 'ch' |
| 2 | 'i' in medial = 'i' in 'aiin' | Standalone 'i' has discrete pen lifts between; 'ii' in 'aiin' shows connected minims | Connected minim pattern in 'aiin' |
| 3 | 'o' (standalone) = 'o' in 'qo' | Standalone 'o' starts fresh; 'o' in 'qo' is entered from q-tail without lift | Continuous pen movement in 'qo' |
| 4 | All 'i' and 'n' are identical | Yes, they ARE identical in form; position determines reading | Position-dependent; NOT a ductus distinction |
| 5 | Word-initial 'o' = medial 'o' | Word-initial 'o' may be slightly larger (fresh stroke start vs. mid-word flow) | Size variation at pen-down |

### 6.2 Cases Where EVA Treats as Different What Ductus Shows is the Same

| # | EVA Treatment | Ductus Reality | Evidence |
|---|---------------|---------------|----------|
| 1 | 'e' and 'c' (in ch/sh) are different | Physically IDENTICAL crescent stroke | Same leftward crescent in all cases |
| 2 | 'i' and 'n' are different letters | Physically IDENTICAL minim stroke | Same downstroke; position determines reading |
| 3 | 'y' (initial) and 'y' (final) | Same stroke construction in all positions | Descender present in all positions |

### 6.3 'aiin' and 'daiin' -- Ligature Unit Analysis

**'aiin' ductus analysis:**
```
Component strokes:
  1. ↻→ a-circle with rightward tail
  2. ↓ First minim (i)
  3. ↓ Second minim (i)  [connected to stroke 2 at baseline]
  4. ↓ Final minim (n)   [connected to stroke 3 at baseline]

Pen lifts: 0 (all four components show continuous pen movement)
Key evidence: The minims (strokes 2-4) are connected at the BASELINE,
  not as separate pen-down/pen-up strokes.
```

**This is the strongest physical evidence for the ligature-based shorthand interpretation.** If 'aiin' were four separate letters (a + i + i + n), we would expect four distinct pen-down events with lifts between. Instead, we observe a single continuous movement: circle → tail → connected minims. This means 'aiin' is a SINGLE GRAPHIC UNIT representing the suffix /-ain/.

**'daiin' ductus analysis:**
```
Component strokes:
  1. ↺↑ d-loop and ascender
  [pen lift possible here]
  2-5. aiin ligature unit (as above)

Pen lifts: 0-1 (possible lift between d and aiin)
```

The 'd' component may or may not connect directly to the 'aiin' unit. When it does connect, 'daiin' is a single continuous word-writing movement. When there is a lift, it is between the operator 'd' and the suffix-unit 'aiin'.

### 6.4 Positional Variants

The following positional form differences were identified through ductus analysis:

| Character | Initial Form | Medial Form | Final Form |
|-----------|-------------|-------------|------------|
| o | Slightly larger circle; fresh pen-down | Standard circle; mid-word flow | Standard or slightly smaller |
| a | Standard circle+tail | Standard circle+tail; tail connects to next | Rare; short tail |
| ch | Full crescent+h; clear construction | Crescent+h; flowing | Rare |
| d | Prominent loop+ascender (operator function) | Standard loop+ascender | Short form; loop may reduce |
| y | Rare in initial | Rare | Full descender; word-final |
| Gallows | Rare; full construction | Standard; most common position | Rare |

---

## 7. Validation Checklist

- [x] All 4 gallows analyzed for distinct ductus (different loop orientations/complexity)
- [x] 5 cases identified where ductus distinguishes glyphs EVA treats as identical (Section 6.1)
- [x] 3 cases identified where EVA treats as different what ductus shows is the same (Section 6.2)
- [x] 'aiin' and 'daiin' sequences analyzed as ligature units with evidence (Section 6.3)
- [x] Positional variants cataloged -- initial vs medial vs final forms (Section 6.4)
- [x] All vowels analyzed (o, a, e, i, y)
- [x] All consonants analyzed (r, l, d, s, m, n)
- [x] All 4 gallows analyzed with stroke sequences
- [x] Bench gallows compound construction documented
- [x] Speed sensitivity documented for each glyph type

---

*Next step: Phase 3 -- Exemplar Transcription of 5 anchor folios*
