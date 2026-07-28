# section-06-corpus-execution: Corpus execution

> Self-contained, context-isolated build unit. An implementer can execute this
> file alone. The section manifest records its dependency position.

## Context

This unit executes the registered pipeline across Yale MS 408 and closes the
accounting loop. It acquires each authority surface by IIIF ID, verifies every
byte, processes each page independently, records every detected text region, and
keeps unresolved readings explicit. Detailed pixels and OCR artifacts remain
local under ignored build storage; compact manifests and receipts are committed.

## Inputs

- Section 01 source register and 210 row Yale authority map.
- A pinned IIIF request profile, expected MIME type, retry limit, timeout, and
  local acquisition root. Redirect targets and response bytes are recorded.
- Section 02 deterministic OCR configuration and package version receipt.
- Section 03 gold, parity, coverage, and claim validators.
- Section 04 terminology and translation records when they exist.
- Section 05 Windows commands and ignored `build/` storage policy.

## Outputs

- An acquisition receipt for all 210 requested surfaces with IIIF ID, final URL,
  byte hash, byte count, MIME type, width, height, and disposition.
- One OCR receipt per acquired page, one record per detected region and line,
  and explicit `no_text_detected`, `processing_failed`, or `unresolved`
  dispositions where applicable.
- Canonical page and region manifests whose totals join exactly to the authority
  map. Every translation record references a region ID and parent hashes.
- Whole corpus summaries for page counts, region and line counts, grapheme and
  unknown counts, failures, missing joins, metrics status, and claim decisions.
- A rerun command that produces the same scientific JSON for identical inputs,
  configuration, and package revision.

## Tests

- Any authority page missing from acquisition or OCR is counted and blocks whole
  corpus completion.
- An asset whose content hash changed is rejected before OCR.
- A detected text region without geometry, page ID, parent hash, and OCR record
  fails coverage.
- A translation row without the same region identity and review state fails.
- A no gold corpus run reports metrics as `not_measured`.
- Generated scientific records from two identical runs must compare byte for byte.

## Dependencies

Sections 01, 02, 03, 04, and 05.
