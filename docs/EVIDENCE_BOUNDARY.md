# Evidence boundary

## Primary recognition lane

Permitted inputs are image bytes, immutable source metadata, image geometry,
registered image processing configuration, and image aligned training examples
that passed rights and split validation.

The lane is barred from inherited Voynich transliterations, transcriptions,
decoder outputs, word lists, lexicons, language models fitted to the manuscript,
and existing translations. Static tests scan the package for forbidden imports
and resource references. Runtime functions accept a `PageRecord` and pixels.

## Quarantined comparison lane

Legacy text artifacts can be compared only after image native output is frozen.
A comparison record must identify the frozen OCR receipt, comparison asset,
comparison method, operator, and date. It cannot change the primary result.

Claim bearing inherited reports carry a visible warning plus machine readable
status markers. The repository wide gate is:

```powershell
.venv\Scripts\python -m zfd_image_native `
  validate-publication-boundary `
  --repository-root .
```

Any scanned Markdown or JSON file that states completion, translation, or
certainty about provenance, language, script, or genre without the complete
legacy marker set fails this command. Current documentation is scanned as well.
Explicit unresolved, unproven, and blocked statements remain valid current
status language.

## Immutable joins

Each downstream record carries these parent fields:

- Yale source ID and IIIF numeric ID
- page ID and image SHA 256
- region ID and original pixel geometry
- OCR record ID and configuration hash
- diplomatic, terminology, and translation parent IDs
- reviewer and adjudicator state

Filenames are display labels. They never establish record identity.

## Confidence semantics

Visual candidate confidence, unknown probability, diplomatic confidence,
terminology confidence, semantic confidence, and translation confidence are
separate fields. Missing evidence stays null. Decoder character coverage is not
an OCR or semantic confidence measure.
