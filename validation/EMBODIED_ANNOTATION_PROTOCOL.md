# Embodied Visual Annotation Protocol for Voynich Herbal Folios

**Version:** 2.0
**Date:** February 2026
**Methodology:** Adapted from Curio Paleography Protocol (October 2025)

---

## 1. The Illustrator Persona

When annotating any Voynich herbal folio, **embody a 15th century herbal manuscript illustrator**.

### Pre-Annotation Mental Preparation

Before marking any plant parts, ask yourself:

1. **"What is this plant?"** - Overall gestalt impression (herbaceous, woody, aquatic, etc.)
2. **"What remedy is this for?"** - If preparing a medicine, which part matters most?
3. **"Where have I (the illustrator) placed emphasis?"** - What's drawn larger, more detailed, or colored?
4. **"What text is adjacent and what does it predict?"** - Do CONFIRMED stems suggest what should be shown?

### The Empathy Check

For every annotation decision:
> *"What was the illustrator TRYING to show here?"*

Not "what do I see?" but "what were they **intending** to communicate?"

---

## 2. Plant Part Identification Criteria

### 2.1 ROOT Identification

**Visual Markers:**
- Underground or below-soil-line depiction
- Bulbous, tuberous, or taproot shapes
- Branching structures below main stem
- Often shown with dirt/texture marks, stippling
- May show cut/cross-section (important for preparation)
- Typically at bottom of plant illustration

**Text Correlation:**
- Check for **"ed"** stems (CONFIRMED = root/base)
- Check for "rady" variants

**Confidence Modifiers:**
- HIGH: Clear underground bulb/root system with branching
- MEDIUM: Tapered bottom portion, could be root or stem base
- LOW: Position suggests root but no distinct root morphology

### 2.2 STALK/STEM Identification

**Visual Markers:**
- Central vertical structure
- Connects root zone to leaves/flowers
- May show nodes, joints, or segments
- Often drawn as single or multiple parallel lines
- Thickness may vary (thick herbaceous vs thin wiry)

**Text Correlation:**
- Check for **"od"** stems (CANDIDATE = stalk)
- Context: connecting/structural descriptions

**Confidence Modifiers:**
- HIGH: Clear vertical structure with visible nodes/segments
- MEDIUM: Central line but minimal detail
- LOW: Inferred from leaf attachment points

### 2.3 LEAF Identification

**Visual Markers:**
- Lateral extensions from stalk
- Distinctive shapes (lobed, serrated, palmate, pinnate)
- Often colored green (when color present)
- May show venation patterns
- Arranged alternately or oppositely on stem

**Text Correlation:**
- Leaf-related vocabulary (if identified)
- Descriptions of shape, arrangement

**Confidence Modifiers:**
- HIGH: Clear leaf shapes with venation or distinctive outline
- MEDIUM: Green coloring, lateral position, but stylized
- LOW: Position suggests leaf but highly abstract

### 2.4 FLOWER Identification

**Visual Markers:**
- Terminal or axial blooms
- Petal structures (radial symmetry common)
- Often colored (red, blue, yellow, pink)
- May show reproductive parts (stamens, pistils)
- Sometimes with buds at various stages

**Text Correlation:**
- "flor" stems (CONFIRMED = flower)
- Color descriptions, bloom timing

**Confidence Modifiers:**
- HIGH: Clear petal arrangement, color, reproductive structures
- MEDIUM: Colored terminal structure, but stylized
- LOW: Position at top, could be flower or fruit

### 2.5 SEED/FRUIT Identification

**Visual Markers:**
- Pod or capsule structures
- Berry, drupe, or pome shapes
- Often near or after flowers
- May show internal seeds (cross-section)
- Distinctive surface texture (smooth, hairy, spiny)

**Text Correlation:**
- Seed/grain vocabulary
- "dar/dain/daiin" in dose contexts (PROMOTED = add/portion/seed)

**Confidence Modifiers:**
- HIGH: Clear pod/fruit with visible seeds
- MEDIUM: Rounded structure near flower, likely fruit
- LOW: Could be bud, fruit, or gall

### 2.6 VESSEL/PREPARATION Context (Non-Plant)

**Visual Markers:**
- Container shapes (pots, jars, phials)
- Liquid surfaces or dripping
- Fire/flame indicators
- Mortar and pestle shapes

**Text Correlation:**
- **"kal"** (PROMOTED = cauldron)
- **"kair/kar/fair"** (PROMOTED = fire/heat)
- **"ok-/ot-"** operators (vessel context)

---

## 3. Line-to-Part Mapping Procedure

### 3.1 Initial Folio Survey (MACRO)

1. **Open the folio image** at full resolution
2. **Identify the overall layout:**
   - Single plant or multiple?
   - Plant orientation (vertical, horizontal, diagonal)?
   - Where is the illustration relative to text?
   - Does text wrap around illustration?
3. **Note the illustration style:**
   - Realistic vs stylized?
   - Color present or monochrome?
   - Level of detail?

### 3.2 Plant Part Region Mapping (MESO)

1. **Divide the illustration into zones:**
   - Mark approximate boundaries for each plant part
   - Example: "Root: bottom 20% | Stalk: 20-50% | Leaves: 30-70% | Flower: top 20%"
2. **Note overlaps:**
   - Leaves may span much of the image
   - Some parts may not be depicted

### 3.3 Text Line Assignment (MICRO)

For each numbered text line:

1. **Identify spatial adjacency:**
   - Which illustration region is this line closest to?
   - Is it to the left, right, above, below the plant part?
2. **Assign the adjacent plant part**
3. **Record confidence level:**
   - VISUAL_HIGH: Line clearly adjacent to unambiguous plant part
   - VISUAL_MEDIUM: Line near plant part, but some ambiguity
   - VISUAL_LOW: Inference required, illustration unclear

### 3.4 Bidirectional Validation (THE KEY STEP)

After initial assignment, **cross-validate using CONFIRMED stems:**

```
For each line containing "ed" (CONFIRMED root):
  → PREDICT: This line should be adjacent to root illustration
  → CHECK: Is it?
  → If YES: Annotation VALIDATED ✓
  → If NO: Either (a) annotation wrong, or (b) "ed" usage is broader than root

For each line containing "kair/kar/fair/char" (PROMOTED fire/heat):
  → PREDICT: Should be in cooking/preparation context (vessel, flame)
  → CHECK: Is there vessel/fire imagery nearby?
  → If YES: Annotation VALIDATED ✓
  → If NO: May be metaphorical use or different folio type

For each line containing "kal" (PROMOTED cauldron):
  → PREDICT: Should be near vessel illustration
  → CHECK: Is there container/pot imagery?
  → If YES: Annotation VALIDATED ✓
  → If NO: Flag for review
```

---

## 4. Documentation Requirements

### 4.1 Per-Folio Annotation Record

```json
{
  "folio_id": "fXXr/v",
  "annotation_method": "VISUAL",
  "annotator": "claude_code_phase2",
  "timestamp": "ISO8601",

  "illustration_analysis": {
    "plant_type": "description of overall plant",
    "layout": "centered | left-margin | full-page | etc.",
    "color_present": true/false,
    "root_region": {"description": "...", "image_pct": "0-20%", "confidence": "HIGH|MEDIUM|LOW"},
    "stalk_region": {"description": "...", "image_pct": "20-50%", "confidence": "HIGH|MEDIUM|LOW"},
    "leaf_region": {"description": "...", "image_pct": "30-70%", "confidence": "HIGH|MEDIUM|LOW"},
    "flower_region": {"description": "...", "image_pct": "top 15%", "confidence": "HIGH|MEDIUM|LOW"},
    "seed_region": {"description": "...", "confidence": "HIGH|MEDIUM|LOW"},
    "vessel_present": true/false,
    "fire_present": true/false
  },

  "line_annotations": {
    "1": {"adjacent_part": "flower|leaf|stalk|root|seed|vessel", "confidence": "VISUAL_HIGH|VISUAL_MEDIUM|VISUAL_LOW"},
    "2": {...},
    ...
  },

  "bidirectional_validation": {
    "ed_lines": [list of line numbers containing "ed"],
    "ed_prediction": "root",
    "ed_observed_parts": {"root": X, "stalk": Y, "leaf": Z, ...},
    "ed_match_rate": 0.XX,

    "kair_lines": [list],
    "kair_prediction": "fire/vessel",
    "kair_observed": "...",
    "kair_match": true/false,

    "kal_lines": [list],
    "kal_prediction": "vessel",
    "kal_observed": "...",
    "kal_match": true/false
  },

  "notes": "Free-form observations, anomalies, uncertainties"
}
```

### 4.2 Annotation Log

Maintain `visual_annotation_log.md` with reasoning for each folio:

```markdown
## Folio fXXr

**Annotation Date:** YYYY-MM-DD

### Illustrator Intent Analysis
[What was the illustrator trying to show? What's emphasized?]

### Plant Part Identification
- **Root:** [description, confidence, reasoning]
- **Stalk:** [description, confidence, reasoning]
- **Leaf:** [description, confidence, reasoning]
- **Flower:** [description, confidence, reasoning]

### Text-Image Alignment
[How does text wrap around illustration? Which lines are adjacent to which parts?]

### Bidirectional Validation Results
- "ed" lines: X found, Y adjacent to roots = Z% match
- "kair" lines: X found, context check = PASS/FAIL
- "kal" lines: X found, vessel check = PASS/FAIL

### Confidence Assessment
[Overall confidence in this folio's annotation]

### Anomalies/Notes
[Anything unusual about this folio]
```

---

## 5. Quality Assurance Checklist

Before finalizing any folio annotation:

- [ ] Illustration fully analyzed (all visible parts identified)
- [ ] Every text line assigned to a plant part
- [ ] Confidence levels recorded for each assignment
- [ ] Bidirectional validation completed for CONFIRMED stems
- [ ] Notes documented for any ambiguities
- [ ] Annotation method marked as "VISUAL" (not "HEURISTIC")

---

## 6. Handling Special Cases

### 6.1 Multiple Plants on One Folio

- Annotate each plant separately
- Map text lines to the nearest/most relevant plant
- Note which plant each line relates to

### 6.2 Abstract or Heavily Stylized Illustrations

- Use position-based inference as secondary evidence
- Assign VISUAL_LOW confidence
- Document the stylization challenge

### 6.3 Missing or Damaged Illustration Regions

- Mark as "UNCLEAR" rather than guessing
- Use surrounding context if available
- Note the damage in annotation record

### 6.4 Text-Only Regions

- If a line is far from any illustration: assign based on nearest plant part
- Confidence: VISUAL_LOW
- Note: "Text distant from illustration"

---

## 7. Revision Protocol

If a bidirectional validation check fails:

1. **Re-examine the illustration region** - Did you misidentify the plant part?
2. **Re-examine the text line position** - Is it actually adjacent to a different part?
3. **Consider alternative interpretations** - Could the stem have broader meaning?
4. **Document the discrepancy** - Flag for potential semantic refinement

The goal is NOT to force agreement, but to identify where text and image align AND where they don't. Disagreements are valuable data.

---

*Protocol adapted from Curio Paleography Methodology (October 2025)*
*"Become the illustrator. See what they saw. Know what they knew."*
