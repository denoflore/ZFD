# SPARK - spec for zfd-image-native-decipherment

> Phase SPARK. Capture the spark verbatim. Do not optimize, do not narrow to the
> part that fits your mental model. Every detail is a constraint.

## The ask (verbatim or near-verbatim)

Pull Chris's complete `denoflore/ZFD` GitHub repository into
`F:\Dropbox\0 ZFD` without losing the much larger local corpus already stored
there. Finish the ZFD research programme across the full Voynich manuscript.
Repair and complete the translations, testing packages, provenance argument,
and documentation. Find further primary records and period manuscripts for
Croatian angular Glagolitic cursive and related shorthand from Dalmatia,
Dubrovnik or Ragusa, Zagreb, and the wider region. Build an image native OCR
pipeline for the proposed angular Glagolitic cursive shorthand so that primary
recognition and translation no longer depend on EVA or inherited community
transcriptions. Bring every claim to the strongest defensible state supported
by the surviving evidence, with a direct account of uncertainty.

## Constraints already implied

- Chris owns `denoflore/ZFD`; repository repair, commit, and publication are in scope.
- Preserve all local only files. No mirror copy, destructive reset, or silent overwrite.
- Manuscript pixels and independently dated exemplars are the primary evidence.
- EVA, IVTFF, ZL, and other inherited transcriptions may be used only for blinded comparison after an image native result is frozen.
- Keep recognition, grapheme segmentation, script attribution, transliteration, linguistic parsing, semantic translation, and geographic provenance as separate inference layers.
- Record image coordinates, source identifiers, checksums, dates, rights, and acquisition URLs for every training or evaluation asset.
- Prevent train and test leakage across duplicate crops, folio sides, quires, scribes, source manuscripts, and synthetic variants.
- Keep every unknown visible. A complete corpus means every text region is inventoried and adjudicated, including regions whose reading remains unresolved.
- Calibrate confidence at glyph, token, line, folio, translation, and historical claim levels.
- Test the Ragusan Croatian angular Glagolitic hypothesis against serious alternatives using preregistered held out evidence.
- No completion claim without fresh repository, package, model, corpus coverage, and claim ledger receipts.

## What success looks like

1. The merged workspace is a valid checkout whose tracked tree matches live GitHub while every local only research asset remains present.
2. A machine readable source register covers the Voynich images and each comparative manuscript, including stable locator, date range, institution, rights, checksum, page mapping, and evidentiary role.
3. The OCR entry point accepts image regions and emits a grapheme lattice, alternatives, bounding geometry, and calibrated confidence without consuming EVA or any other Voynich transcription.
4. A leakage resistant gold set and held out evaluation report measure segmentation, glyph recognition, sequence recognition, and calibration. Synthetic data is reported separately from manuscript evidence.
5. Every surviving text bearing folio and line has an image anchored adjudication record. Each record contains the observed glyph sequence, competing readings, morphological analysis, Croatian reconstruction where supported, English translation where supported, and an explicit unresolved status where evidence does not determine a reading.
6. The translation package has no silent gaps, invented prose, or circular dictionary matches. Coverage measures distinguish inventory completion from decipherment confidence and semantic translation confidence.
7. A claim ledger traces every palaeographic, linguistic, pharmaceutical, chronological, and provenance claim to primary evidence, a reproducible computation, or a clearly labelled inference. Contradictions and failed tests remain preserved.
8. The complete test suite installs from declared dependencies and reproduces all published metrics from clean inputs. Tests fail when EVA enters the image native lane, when duplicate material crosses a split, when a source lacks rights metadata, or when a completion claim exceeds its receipts.
9. The final provenance report ranks the ZFD hypothesis against alternatives, states what was falsified, and limits its conclusion to the strength of the evidence actually obtained.
