# Claude Code Instructions: Glagolitic OCR Pipeline

**Priority:** MEDIUM
**Branch:** `claude/voynich-edition-architecture-Wu0dr`
**Repository:** `denoflore/ZFD`
**Date:** 2026-02-03

---

## Context

The ZFD establishes that Voynichese is abbreviated Angular Glagolitic. To further validate this and enable comparative analysis, we need a pipeline that can:

1. Process images of known Glagolitic manuscripts
2. Extract and recognize Glagolitic characters
3. Map recognized characters to the ZFD character mapping
4. Enable direct comparison between Voynich glyphs and historical Glagolitic

This pipeline supports the paleographic validation work by providing automated character recognition for Glagolitic manuscript images.

---

## Pipeline Architecture

```
06_Pipelines/glagolitic_ocr/
├── CC_INSTRUCTIONS_GLAGOLITIC_OCR_PIPELINE.md  # This file
├── glagolitic_ocr.py                           # Main pipeline script
├── character_reference.py                       # Glagolitic character data
├── image_processor.py                          # Image preprocessing
├── glyph_extractor.py                          # Character segmentation
├── data/
│   ├── glagolitic_alphabet.json               # Reference alphabet data
│   ├── angular_glagolitic_samples/            # Sample character images
│   └── manuscript_samples/                     # Test manuscript images
├── output/
│   ├── extracted_glyphs/                       # Segmented characters
│   └── recognition_results/                    # OCR output
└── models/
    └── glagolitic_classifier.pkl              # Trained classifier (optional)
```

---

## Your Task: Build the OCR Pipeline

### Phase 1: Glagolitic Character Reference

**Goal:** Create a comprehensive reference dataset for Angular Glagolitic characters.

**Glagolitic Alphabet (Angular/Croatian variant):**

| Letter | Unicode | Sound | Name | EVA Equivalent |
|--------|---------|-------|------|----------------|
| Ⰰ | U+2C00 | /a/ | Az | a |
| Ⰱ | U+2C01 | /b/ | Buky | - |
| Ⰲ | U+2C02 | /v/ | Vede | - |
| Ⰳ | U+2C03 | /g/ | Glagoli | g |
| Ⰴ | U+2C04 | /d/ | Dobro | d |
| Ⰵ | U+2C05 | /e/ | Est | e |
| Ⰶ | U+2C06 | /ʒ/ | Zhivete | - |
| Ⰷ | U+2C07 | /dz/ | Dzelo | - |
| Ⰸ | U+2C08 | /z/ | Zemlja | - |
| Ⰹ | U+2C09 | /i/ | Izhe | i |
| Ⰺ | U+2C0A | /i/ | I | i |
| Ⰻ | U+2C0B | /dʒ/ | Djerv | - |
| Ⰼ | U+2C0C | /k/ | Kako | k |
| Ⰽ | U+2C0D | /l/ | Ljudie | l |
| Ⰾ | U+2C0E | /m/ | Myslete | m |
| Ⰿ | U+2C0F | /n/ | Nash | n |
| Ⱀ | U+2C10 | /o/ | On | o |
| Ⱁ | U+2C11 | /p/ | Pokoj | p |
| Ⱂ | U+2C12 | /r/ | Rtsi | r |
| Ⱃ | U+2C13 | /s/ | Slovo | s |
| Ⱄ | U+2C14 | /t/ | Tvrdo | t |
| Ⱅ | U+2C15 | /u/ | Uk | - |
| Ⱆ | U+2C16 | /f/ | Frt | f |
| Ⱇ | U+2C17 | /x/ | Xer | ch |
| Ⱈ | U+2C18 | /ts/ | Tsi | c |
| Ⱉ | U+2C19 | /tʃ/ | Chrv | - |
| Ⱊ | U+2C1A | /ʃ/ | Sha | sh |
| Ⱋ | U+2C1B | /ʃt/ | Shta | - |
| Ⱌ | U+2C1C | /ɛr/ | Er | - |
| Ⱍ | U+2C1D | /ɨ/ | Yer | y |
| Ⱎ | U+2C1E | /ɛri/ | Yeri | - |
| Ⱏ | U+2C1F | /ʲa/ | Yat | - |
| Ⱐ | U+2C20 | /jo/ | Yo | - |
| Ⱑ | U+2C21 | /ju/ | Yu | - |

**Output:** `data/glagolitic_alphabet.json`

### Phase 2: Image Preprocessing

**Goal:** Prepare manuscript images for character extraction.

**Steps:**
1. Load image (JPEG, PNG, TIFF)
2. Convert to grayscale
3. Apply adaptive thresholding (Otsu's method)
4. Remove noise (morphological operations)
5. Deskew if needed
6. Normalize size and contrast

**Code Template:**
```python
import cv2
import numpy as np
from PIL import Image

def preprocess_image(image_path):
    """Preprocess manuscript image for OCR."""
    # Load image
    img = cv2.imread(image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Adaptive thresholding
    binary = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )

    # Morphological cleanup
    kernel = np.ones((2, 2), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    return cleaned
```

### Phase 3: Glyph Extraction

**Goal:** Segment individual characters from manuscript images.

**Method:**
1. Find contours in preprocessed image
2. Filter contours by size (remove noise, large blobs)
3. Sort contours left-to-right, top-to-bottom
4. Extract bounding boxes
5. Save individual glyph images

**Constraints:**
- Minimum glyph height: 10px
- Maximum glyph height: 200px
- Aspect ratio: 0.2 - 3.0 (width/height)

### Phase 4: Character Recognition

**Goal:** Match extracted glyphs to known Glagolitic characters.

**Methods (choose one or combine):**

**A. Template Matching:**
- Compare extracted glyphs to reference templates
- Use normalized cross-correlation
- Works well for consistent scripts

**B. Feature Extraction + Classification:**
- Extract HOG (Histogram of Oriented Gradients) features
- Train SVM or Random Forest classifier
- More robust to variation

**C. Neural Network (if sufficient training data):**
- CNN for character classification
- Requires labeled training data

**Initial Implementation:** Start with template matching, upgrade if needed.

### Phase 5: ZFD Integration

**Goal:** Map recognized Glagolitic characters to EVA equivalents.

**Mapping (from FINAL_CHARACTER_MAP_v1.md):**

| Glagolitic | Sound | EVA | ZFD Croatian |
|------------|-------|-----|--------------|
| Ⰰ | /a/ | a | a |
| Ⰵ | /e/ | e | e |
| Ⱁ | /o/ | o | o |
| Ⰹ | /i/ | i | i |
| Ⱍ | /ɨ/ | y | i/y |
| Ⰼ | /k/ | k | k |
| Ⱄ | /t/ | t | t |
| Ⱆ | /f/ | f | f |
| Ⱁ | /p/ | p | p |
| Ⱇ | /x/ | ch | h |
| Ⱊ | /ʃ/ | sh | š |

**Output Format:**
```json
{
  "image": "manuscript_001.jpg",
  "extracted_text": [
    {
      "line": 1,
      "glyphs": [
        {"glagolitic": "Ⱊ", "eva": "sh", "confidence": 0.92},
        {"glagolitic": "Ⰵ", "eva": "e", "confidence": 0.88},
        {"glagolitic": "Ⰴ", "eva": "d", "confidence": 0.85}
      ],
      "reconstructed": "šed",
      "croatian": "šedi"
    }
  ]
}
```

---

## Implementation Steps

### Step 1: Create Character Reference Data

```python
# character_reference.py

GLAGOLITIC_ALPHABET = {
    'Ⰰ': {'unicode': 'U+2C00', 'sound': '/a/', 'name': 'Az', 'eva': 'a'},
    'Ⰱ': {'unicode': 'U+2C01', 'sound': '/b/', 'name': 'Buky', 'eva': None},
    # ... complete alphabet
}

# Angular Glagolitic specific variants
ANGULAR_VARIANTS = {
    # Croatian angular forms differ from round Bulgarian forms
}

# Abbreviation marks (important for Voynich)
ABBREVIATION_MARKS = {
    'titlo': 'overline indicating abbreviation',
    'superscript': 'letters written above baseline',
}
```

### Step 2: Build Image Processor

```python
# image_processor.py

class ManuscriptImageProcessor:
    def __init__(self, config=None):
        self.config = config or {}

    def load(self, image_path):
        """Load image from path."""
        pass

    def preprocess(self, image):
        """Apply preprocessing pipeline."""
        pass

    def segment_lines(self, image):
        """Detect and segment text lines."""
        pass

    def segment_characters(self, line_image):
        """Segment characters from a text line."""
        pass
```

### Step 3: Build Glyph Extractor

```python
# glyph_extractor.py

class GlyphExtractor:
    def __init__(self, min_height=10, max_height=200):
        self.min_height = min_height
        self.max_height = max_height

    def extract(self, preprocessed_image):
        """Extract glyph bounding boxes."""
        pass

    def filter_glyphs(self, contours):
        """Filter by size and aspect ratio."""
        pass

    def save_glyphs(self, image, bboxes, output_dir):
        """Save extracted glyphs as images."""
        pass
```

### Step 4: Build Main Pipeline

```python
# glagolitic_ocr.py

class GlagoliticOCR:
    def __init__(self):
        self.processor = ManuscriptImageProcessor()
        self.extractor = GlyphExtractor()
        self.classifier = None  # Template matcher or ML model

    def process_image(self, image_path):
        """Full OCR pipeline for a manuscript image."""
        # Preprocess
        preprocessed = self.processor.preprocess(
            self.processor.load(image_path)
        )

        # Extract glyphs
        glyphs = self.extractor.extract(preprocessed)

        # Classify
        results = []
        for glyph in glyphs:
            char, confidence = self.classify(glyph)
            results.append({
                'glyph': glyph,
                'character': char,
                'confidence': confidence
            })

        return results

    def classify(self, glyph_image):
        """Classify a single glyph."""
        pass
```

---

## Data Requirements

1. **Glagolitic Reference Images:**
   - Sample characters from Angular Glagolitic manuscripts
   - At least 5 samples per character
   - Sources: Croatian manuscripts, printed Glagolitic texts

2. **Test Manuscripts:**
   - Croatian Glagolitic manuscripts (public domain)
   - Breviaries, missals, or charters
   - Various hands/periods for robustness testing

3. **Voynich Samples:**
   - Selected Voynich folio images for comparison
   - Use to test if pipeline can identify Glagolitic-like features

---

## Output Files

The pipeline should generate:

1. `output/extracted_glyphs/` - Individual glyph images
2. `output/recognition_results/*.json` - OCR results per image
3. `output/comparison_report.md` - Voynich vs Glagolitic comparison
4. `data/glagolitic_alphabet.json` - Reference alphabet data

---

## Success Criteria

The pipeline is successful if:

- [ ] Can load and preprocess manuscript images
- [ ] Extracts >80% of visible glyphs from clean images
- [ ] Correctly classifies >70% of clear Glagolitic characters
- [ ] Produces EVA mappings for recognized characters
- [ ] Generates usable comparison data for Voynich analysis

---

## Dependencies

```
opencv-python>=4.5.0
numpy>=1.20.0
Pillow>=8.0.0
scikit-learn>=0.24.0  # For ML classification (optional)
```

---

## Notes

- Start simple: template matching before ML
- Focus on Angular Glagolitic (Croatian variant)
- Prioritize characters with EVA equivalents
- Document failure cases for paleographic analysis
- This is research infrastructure, not production software

---

*Instructions prepared February 3, 2026*
*For ZFD Project - Voynich Manuscript Research*
