# Comparative manuscript review queue

The `zfd-comparanda` command builds a review queue bound to pixels for the Mavrov
breviary, NSK R 7822. The queue preserves the official IIIF canvas order and
keeps every hand identity unresolved. It creates workflow evidence for future
qualified palaeographic review. It supplies no diplomatic glyph labels, hand
attribution, OCR accuracy, translation, or provenance conclusion.

## Pinned source authority

The canonical lane accepts exactly 848 canvases for `nsk-mavrov-r7822`. It
rehashes the local JPEGs and verifies these registered authorities:

| Authority | SHA 256 |
|---|---|
| NSK IIIF manifest | `789a7a8eb6d584cefc999d2ae3099dbbc8c4366fdc4b840c1eab0f95ed6742df` |
| Saved canvas mapping | `f43b604ad62f133e41c534ca29579e7e17c1e7176fb2a1315aa2cb68df41bca5` |
| Acquisition receipt file | `e7b105fc676969900e05a158f08e8659d7fa436481184a8c2323f4c3b8a36694` |
| Acquisition receipt payload | `54ebce142ec0b1ae23875faa14f4864d509a35ecf57e9ad5db08522de88b6b94` |

The source and register records are also fixed in the implementation authority.
They identify the formal ustavna layer written by Blaž Baromić in 1460 and the
calendar addition made by Jure of Baška in 1471. Those are catalogue statements.
Their canvas, region, line, and hand boundaries remain
unadjudicated. The source record preserves NSK's `Javno dobro` and `Slobodan
pristup` rights statements and locator.

The validator recomputes every comparative asset ID, content lineage ID,
receipt, duplicate group, duplicate backlink, source summary, and corpus total.
An internally consistent replacement corpus, opaque identifier, contradictory
summary, or altered source metadata fails before a queue is issued.

## Build and validate on Windows

Run from a clean committed checkout after the package has been installed:

```powershell
.venv\Scripts\python -m pip install -e .

.venv\Scripts\zfd-comparanda build-queue `
  --repository-root . `
  --source-mount "F:\Dropbox\0 ZFD\00_GM" `
  --output-root 06_Pipelines\comparative_review_runs\mavrov-20260728-v1

.venv\Scripts\zfd-comparanda validate-queue `
  --repository-root . `
  --source-mount "F:\Dropbox\0 ZFD\00_GM" `
  --queue-root 06_Pipelines\comparative_review_runs\mavrov-20260728-v1
```

The default repository authorities are:

- `data/image_native/comparative_sources.json`
- `data/image_native/source_register.json`
- `data/image_native/comparative_assets.jsonl`
- `data/image_native/comparative_asset_summary.json`
- `data/image_native/comparative_duplicate_groups.jsonl`

Outputs are confined after path resolution to either
`build/comparative_review` or `06_Pipelines/comparative_review_runs`. Traversal,
absolute paths outside those roots, and junction escapes fail. The output
directory must be new. Files use exclusive creation and canonical UTF 8 JSON
with LF line endings. CLI receipts expose a repository relative locator and
ASCII escaped stdout, which remains safe on legacy Windows console encodings.

The CLI refuses to write when implementation provenance is dirty, unversioned,
malformed, unreachable from the current Git history, or inconsistent with the
historical package and environment files. A wheel can reproduce the same
implementation hash. An installed wheel outside Git remains unversioned and is
ineligible to publish a queue.

## Output contract

One run contains exactly three files:

- `hand_boundary_queue.jsonl`, one immutable row per canvas
- `hand_boundary_pilot.jsonl`, eight immutable adjacent page workflow seeds
- `hand_boundary_summary.json`, source, implementation, count, and file hashes

Every one of the 848 queue rows starts with:

```text
hand_identity_state = unknown_unreviewed
line_annotation_state = not_started
split_assignment_state = blocked_unknown_hand
training_eligible = false
training_promotion_allowed = false
```

The fixed endpoint inclusive pilot is:

```text
(0,1)
(121,122)
(242,243)
(363,364)
(483,484)
(604,605)
(725,726)
(846,847)
```

These pairs test queue construction, endpoint handling, and review mechanics.
They do not establish the calendar transition or manuscript wide hand
boundaries. Qualified review requires sealed image crops, primary and blinded
independent observations, a distinct adjudicator, explicit uncertainty, and
coverage of all 847 adjacencies plus any internal page regions with mixed hands.

## Training and scientific status

Queue creation leaves all three promotion authorities null:

```text
hand_boundary_sha256 = null
line_annotation_sha256 = null
split_lineage_sha256 = null
```

The queue reports zero training ready assets. Mavrov remains one unresolved
manuscript lineage and one blocked split. Its internal pages cannot be divided
across training and held out partitions. Page pairs cannot emit a complete hand
boundary authority hash.

The package imports no inherited Voynich transcription, EVA, IVTFF, ZL,
decoder, lexicon, or translation resource. Future labels must be derived from
registered source pixels and sealed qualified review. Until those records
exist, OCR accuracy remains `not_measured`, recognition remains unavailable,
and no Voynich translation or provenance claim follows from this queue.
