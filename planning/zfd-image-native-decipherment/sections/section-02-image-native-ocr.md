# section-02-image-native-ocr: Image native OCR

> Self-contained, context-isolated build unit. An implementer can execute this
> file alone. The section manifest records its dependency position.

## Context

This unit supplies the first runnable recognition lane from manuscript pixels.
It detects candidate text regions and lines, extracts grapheme candidates, and
emits an open set lattice. In the absence of adjudicated image aligned exemplars,
each grapheme remains unknown. A visual cluster or nearest candidate is an
alternative hypothesis and never a diplomatic character assignment.

## Inputs

- A Section 01 `PageRecord` with page ID, source ID, exact pixel SHA 256, pixel
  dimensions, and local asset path or resolved acquisition record.
- `OpenSetConfig` containing only image processing and rejection parameters:
  threshold window, component limits, line grouping distance, descriptor size,
  candidate count, and calibrated rejection threshold.
- Optional registered image aligned grapheme exemplars whose source, hand, style,
  split, rights, label state, geometry, and checksum passed Section 01 gates.
- OpenCV and NumPy versions pinned in the reproducible Windows environment.

## Outputs

- `process_page(PageRecord, OpenSetConfig) -> PageOCRResult` with the verified
  parent hash, configuration hash, original dimensions, regions, lines,
  graphemes, processing disposition, and deterministic software receipt.
- Every region, line, and grapheme has an immutable ID and original pixel
  coordinates. Each grapheme carries a visual descriptor, ordered alternatives,
  recognition confidence, unknown score, and nullable diplomatic label.
- Deterministic JSON and JSONL writers. Repeated runs over identical bytes and
  configuration produce byte identical scientific records.
- A corpus command that processes page records independently and writes detailed
  records under ignored `build/` while exposing a compact checked summary.

## Tests

- Authentic `VM_f1r` pixels must yield spatially anchored candidate lines and
  graphemes without loading a transcription, language model, map, or lexicon.
- With no registered recognizer, every diplomatic label is null and every glyph
  has an explicit unknown score between zero and one.
- A changed source checksum is rejected before segmentation.
- Two runs on the same bytes and configuration serialize identically.
- Visual confidence cannot populate terminology, semantic, or translation
  confidence fields.

## Dependencies

Section 01, Evidence identity.
