# VIBE: interview and emergent shape for zfd-image-native-decipherment

> Phase VIBE. These questions were answered from Chris's explicit request, the
> ownership clarification, and the repository audit. No decision below expands
> authority beyond the ZFD repository and the public research sources requested.

## Clarifying questions and answers

1. Q: What does complete mean when the manuscript still contains unknown text?
   A: Every surviving text bearing region has an image anchored record and an
   explicit disposition. `unresolved` is a complete disposition when evidence
   cannot decide a reading. Forced readings do not count as completion.

2. Q: What is the primary observation boundary?
   A: Yale manuscript pixels and independently dated comparative manuscript
   pixels. EVA, IVTFF, ZL, and derived ZFD text stay outside the primary OCR lane.

3. Q: What happens to the existing ZFD translations and validation results?
   A: Preserve them as historical hypothesis artefacts with exact lineage. Their
   labels and public claims must describe what they actually measure.

4. Q: What does the OCR emit before script identity is established?
   A: Regions, baselines, grapheme spans, opaque visual cluster identifiers,
   competing Unicode candidates, geometry, confidence, and unknown states. A
   Glagolitic label is an inference layer, never a mandatory classifier output.

5. Q: What is the recognition target for genuine Glagolitic comparanda?
   A: Diplomatic Glagolitic Unicode at line level, preserving abbreviation marks,
   ligatures, damage, and uncertainty. Latin transliteration, abbreviation
   expansion, linguistic normalisation, and translation remain separate fields.

6. Q: How can OCR accuracy be claimed?
   A: Only against a sealed, image aligned, independently reviewed gold set with
   line detection, CER, grapheme confusion, unknown rejection, and calibration
   reported by source manuscript, hand, date, and script style.

7. Q: How is translation separated from decoder self consistency?
   A: Each record stores observation, proposed graphemes, transliteration,
   morphology, lemma, literal gloss, fluent translation, alternatives, reviewer,
   and confidence independently. Character coverage cannot award semantic status.

8. Q: How is the Ragusan claim tested?
   A: Freeze the image reading first. Register competing places, languages, and
   script traditions; acquire direct dated archive controls; define nulls and
   negative evidence; then test rare bundles with multiplicity correction.

9. Q: What external data may enter training?
   A: Only assets with stable identity, checksum, provenance, and explicit rights
   metadata. Model weights may be used under their licence while underlying page
   images and ground truth remain quarantined until their rights are confirmed.

10. Q: What is the smallest safe complete first build?
    A: A canonical corpus and source manifest, an evidence schema, an image only
    boundary gate, deterministic segmentation and opaque clustering, a ten folio
    annotation protocol, claim ledger, source acquisition commands, and tests.

## Emergent shape

The build is an evidence spine with independent layers:

`source asset -> page identity -> region -> line -> visual grapheme lattice -> script candidate -> transliteration -> linguistic analysis -> translation -> provenance claim`

Every arrow creates a new assertion with its own source, author, method,
alternatives, confidence, and review state. Downstream knowledge cannot silently
rewrite an upstream observation.

The first executable lane is deliberately open set. It extracts authentic image
regions, segments candidate lines, produces deterministic visual features, groups
similar shapes, and can reject a forced alphabet. The legacy EVA decoder becomes
a quarantined comparison lane that runs only after the image result is frozen.

The source registry supplies the common identity layer. It binds Yale IIIF
surfaces, local derivatives, comparative manuscripts, duplicates, dates, hands,
styles, rights, checksums, and evidentiary roles. Split generation uses those
identities so a page, crop, duplicate, hand, or manuscript cannot leak across
training and evaluation.

The claim ledger becomes the publication gate. A claim names its type, scope,
status, evidence, counterevidence, falsifier, and allowed wording. Statements such
as complete translation, OCR accuracy, and Ragusan provenance remain blocked
until their named receipts exist.

## Open hand waves carried into HARDEN

- The exact Yale reuse statement must be captured per downloaded derivative.
- The GAMS TEI licence is visible, while Vatican facsimile training and
  republication rights require confirmation.
- The Rabus weight licence is clear. The underlying line image and ground truth
  rights remain unconfirmed.
- HAZU IV d 55 and IV d 56 require direct image access and permission before they
  can become training assets.
- Two independent qualified palaeographers plus adjudication are required for a
  publishable gold set. The repository can define and validate the workflow; it
  cannot impersonate those reviewers.
- A robust line recogniser requires a dedicated Python 3.12 environment if the
  Polyscriptor baseline is adopted. The repository currently runs Python 3.13.
