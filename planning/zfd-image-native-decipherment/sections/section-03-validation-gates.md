# section-03-validation-gates: Validation gates

> Self-contained, context-isolated build unit. An implementer can execute this
> file alone. The section manifest records its dependency position.

## Context

This unit prevents segmentation output or decoder coverage from becoming an OCR,
translation, or provenance claim. It evaluates only leakage resistant,
image aligned, adjudicated gold and requires exact parent identity through the
pixel to translation chain. Missing evidence remains an explicit unresolved
disposition.

## Inputs

- Section 01 page and source records plus split validation receipts.
- Section 02 region, line, grapheme, alternative, confidence, and unknown records.
- Held-out gold rows containing source page hash, region and line geometry,
  diplomatic labels, annotator IDs, adjudicator state, manuscript, hand, style,
  and lineage root.
- Layer records keyed by immutable parent IDs and hashes: diplomatic reading,
  normalized expansion, terminology analysis, modern Croatian, literal English,
  fluent English, alternatives, confidence, reviewer, and adjudicator.
- A claim ledger listing each publication claim and its required current receipts.

## Outputs

- Segmentation precision, recall, IoU, CER, sequence error, confusion counts,
  unknown rejection, expected calibration error, and breakdowns by manuscript,
  hand, and style. An empty or non-adjudicated gold set returns `not_measured`.
- Strict page and region parity reports. Confirmed translation requires every
  exact join plus the configured review and adjudication state.
- Corpus coverage reports accounting for all 210 authority pages and every
  detected text region, including missing and unresolved records.
- Machine-readable claim decisions with allowed state, blocking reason codes,
  receipt hashes, and evaluation time.

## Tests

- No gold truth means CER and accuracy are null and accuracy claims are blocked.
- Fixed fixtures must reproduce independently checkable edit, rejection, and
  calibration arithmetic.
- Removing fluent English, an adjudicator, or any earlier layer blocks confirmed
  translation.
- Matching filenames with different parent IDs or hashes fail the join.
- One missing OCR page makes whole corpus coverage fail.
- Current complete translation, provenance, and OCR accuracy claims remain blocked
  while their required receipts are absent.

## Dependencies

Sections 01 and 02.
