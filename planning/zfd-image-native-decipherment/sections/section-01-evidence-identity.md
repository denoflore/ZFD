# section-01-evidence-identity: Evidence identity

> Self-contained, context-isolated build unit. An implementer can execute this
> file alone. The section manifest records its dependency position.

## Context

This unit establishes the immutable evidence spine for an image native
decipherment. Yale MS 408 pixels are the only permitted primary recognition
input. Existing ZFD transcriptions and outside Voynich transliterations remain
quarantined until an image native output is frozen and identified by hash.
Every downstream page, region, line, glyph, term, review, and translation record
must join through stable identifiers and parent hashes.

## Inputs

- `06_Pipelines/glagolitic_ocr/data/folio_iiif_map.json`, a JSON object with 210
  Yale surface labels and IIIF Image API base URLs.
- Local pixels named by Yale IIIF numeric identifier and accompanied by an
  acquisition receipt containing request URL, SHA 256, byte count, MIME type,
  width, and height.
- Source metadata fields: source ID, title, stable locator, date range, script,
  hand/style, evidentiary role, rights statement and locator, identity status,
  acquisition checksum, and train/evaluate/control/quarantine disposition.
- Split metadata fields: asset ID, parent asset ID, lineage root ID, SHA 256,
  perceptual identity, manuscript ID, hand ID, style, and split.

## Outputs

- `data/image_native/source_register.json` and a validator that rejects missing
  rights, unresolved identity, missing checksums, and mixed control roles.
- `data/image_native/voynich_pages.jsonl`, exactly 210 unique `PageRecord` rows
  keyed as `yale-ms-408:iiif:<numeric-id>`.
- `zfd_image_native.manifest` builders, loaders, asset reconciliation, and corpus
  coverage reports. Filename similarity is diagnostic only and never proves a join.
- `zfd_image_native.split` leakage validation for byte duplicates, derivatives,
  lineage roots, manuscripts, and hands crossing a held-out boundary.
- `zfd_image_native.boundary` checks proving the primary lane reads pixels and
  registered metadata only.

## Tests

- Exactly 210 unique Yale page IDs and IIIF bases are required.
- The legacy 209 image set must report missing or unverified identity debt.
- Any forbidden inherited transcription dependency in the primary package fails.
- A training source with blank rights or unresolved identity fails.
- A duplicate, crop lineage, manuscript, or hand crossing splits fails.
- A source byte hash that differs from its page record fails before processing.

## Dependencies

None.
