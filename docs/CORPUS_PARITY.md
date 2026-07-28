# Canonical corpus parity

`zfd-parity` materialises one exact page and region ledger from a fully
validated Stage A image run. It starts with manuscript pixels and the frozen
Stage A geometry. It does not read EVA, IVTFF, ZL, inherited transcription,
decoder output, or legacy translation files.

## Current boundary

The current command accounts for the canonical 210 Yale MS 408 surfaces and
every candidate region in the supplied current Stage A run. Every region is
emitted unresolved. Translation promotion is deliberately disabled because
the repository does not yet have pinned external authority roots for OCR runs,
models, pixel aligned line and grapheme records, calibration, reviewers,
adjudications, and terminology passage assets.

Any nonempty `--layer-records` input returns
`PARITY_PROMOTION_AUTHORITY_UNPINNED`. Self hashed records cannot mint their own
scientific authority. The summary records
`promotion_authority_pinned=false`, `region_authority_pinned=false`, and
`completion_claim_allowed=false`.

## Build and validate

Run from the repository root after freezing a Stage A receipt set against the
same clean checkout. The paths below name the next intended v2c run. The command
must remain blocked while that receipt set is absent or stale.

```powershell
$stageARun = "06_Pipelines\image_native_runs\20260728-v2c"
$parityRun = "06_Pipelines\image_native_runs\20260728-parity-v1"

.venv\Scripts\zfd-parity build-parity-corpus `
  --repository-root . `
  --stage-a-receipts "$stageARun\receipts" `
  --stage-a-corpus "$stageARun\corpus" `
  --manifest "$stageARun\receipts\voynich_pages.jsonl" `
  --output-root $parityRun

.venv\Scripts\zfd-parity validate-parity-corpus `
  --repository-root . `
  --stage-a-receipts "$stageARun\receipts" `
  --stage-a-corpus "$stageARun\corpus" `
  --manifest "$stageARun\receipts\voynich_pages.jsonl" `
  --parity-root $parityRun
```

Both commands require inputs inside the repository. Outputs are confined to a
strict child of `build/image_native/parity` or
`06_Pipelines/image_native_runs`. Resolved Windows junctions cannot escape the
repository. Publication uses a sibling staging directory and one final rename,
so a failed write leaves no partial target.

## Exact authority files

Each run contains exactly six files:

1. `page_authority.jsonl` binds page ID, Yale IIIF identity, source identity,
   image SHA 256, and the frozen Stage A page receipt.
2. `region_authority.jsonl` binds each region to its page, image, polygon hash,
   and frozen Stage A region receipt.
3. `records.jsonl` contains one unresolved parity record for every canonical
   region. Only the declared page and region layers are present while promotion
   authority is unpinned.
4. `page_dispositions.jsonl` recomputes every page from its exact region set.
5. `evidence_authority.json` contains the generated page, region, and source
   receipts. Extra or orphan evidence is rejected.
6. `summary.json` recomputes counts, collection hashes, Stage A integrity and
   freshness, the code pinned 210 page identity, authority pin states, and the
   completion claim gate.

Every record and collection is content bound. The validator reloads the Stage A
pixels and artifacts, reconstructs the canonical authority, rejects missing,
duplicate, unexpected, cross-page, cross-region, extra-layer, and orphan rows,
then recomputes all dispositions and summary fields.

## Promotion prerequisites

Promotion can be implemented only after all of these authorities are registered
and digest bound:

- the exact region authority for the current reviewed segmentation
- OCR run, model, artifact, calibration, line geometry, grapheme geometry,
  confidence, alternatives, and open set disposition receipts
- pixel linked adjudication for rejected nontext candidates
- reviewer identity and qualification registry with distinct adjudicator state
- terminology source records joined to dated passage pixels and stable locators
- diplomatic, expanded, normalised, modern Croatian, literal English, and
  fluent English records joined through the same page, image, region, and OCR
  identities

Until then, zero translated pages and zero translated regions is the only valid
result.
