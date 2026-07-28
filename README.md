# ZFD image native Voynich research

ZFD is rebuilding its Voynich Manuscript work from registered manuscript
pixels. The primary lane inventories source images, candidate text regions,
lines, grapheme components, unknown states, comparative manuscripts, and exact
evidence joins. Inherited Voynich transliterations, transcriptions, decoder
outputs, and translations stay outside that lane.

## Current evidence status

As of 28 July 2026:

- OCR accuracy is not measured. No leakage resistant, image aligned,
  adjudicated gold set exists yet.
- Translation remains unresolved. Zero pages and zero candidate regions meet
  the confirmed translation parity gate.
- Ragusan provenance is unproven. Croatian Glagolitic remains a hypothesis to
  test against dated positive and negative controls.
- The image pipeline has processed all 210 registered Yale MS 408 surfaces.
  Its current native detector groups Cartesian fragments through continuity and
  ink density gates, records rejected components, and exposes layouts needing
  review. A curved or radial text lane is still absent. The pipeline does not
  yet recognize Glagolitic or Voynich graphemes.
- The Stage B visual index derives coarse binary shape descriptors from the
  registered pixels and groups them into deterministic page local exemplars.
  It assigns no letter, script, word, language, or semantic identity. Its
  uncalibrated descriptor distances are visual indexing evidence only.
- The legacy decoder reports character coverage over inherited text records.
  That number is not OCR accuracy, semantic confidence, or translation proof.

The machine authority for publication language is
[`data/image_native/claim_ledger.json`](data/image_native/claim_ledger.json).
The detailed status is in
[`docs/PROVENANCE_STATUS.md`](docs/PROVENANCE_STATUS.md).

## Current executable receipts

The retained Stage A v1 archive records:

| Record | Count or state |
|---|---:|
| Yale MS 408 surfaces | 210 |
| Frozen page OCR receipts | 210 |
| Candidate text regions | 337 |
| Provisional line groups | 22,516 |
| Grapheme components | 490,595 |
| Explicit unknown graphemes | 490,595 |
| Held out OCR metrics | `not_measured` |
| Confirmed translated pages | 0 |
| Confirmed translated regions | 0 |

These are execution and evidence inventory receipts. They do not establish
recognition accuracy or semantic readings. The current detector oversegments
some pages. A held out segmentation gold set is required before its geometry
can be called accurate.

The v1 receipt predates the current Cartesian fragment detector and remains
preserved as historical evidence. A separate current v2b run completed all 210
surfaces with 670 candidate regions, 30,141 provisional line groups, and
356,739 explicit unknown graphemes. Its independent validator has
`archival_integrity_ok=true`, `artifact_integrity_ok=true`,
`freshness_ok=true`, and `ok=true`; scientific review and held out metrics
remain absent, so recognition, script, language, translation, and provenance
claims stay blocked. The 1,415,607,859 byte local evidence set is preserved
under `F:\Dropbox\0 ZFD\06_Pipelines\image_native_runs\20260728-v2b` with
inventory SHA 256
`fb292f1449467b135b1272be1e9d7d212314bb43a0c067210de5e6ac538049d9`.
It is excluded from Git and can be regenerated with the commands below.

`validate-receipts` distinguishes receipt structure, referenced OCR artifact
integrity, and current checkout reproducibility. The frozen 210 page v1 receipt
is structurally intact and stale against the current schema, implementation,
configuration, and dependency lock. Its overall verdict is false and the
command exits nonzero.

The current quarantined Kraken geometry comparison is bound to the v2b run and
all 210 v2b page receipts. It covers 2,088 unreviewed regions and 7,554
unreviewed lines with zero failed pages. Seven pages required a recorded
tolerant retry after a strict Shapely topology failure. Summary ID
`sha256:3f80eddbc3844b38c96f19e077c1a2f86f30d4d080791e460ff5e528b7efcf6b`
validates with zero errors. Its `primary_lane_allowed` field is false,
recognition labels are null, and metrics remain `not_measured`.

The current compact v2b receipt set consists of:

- [`data/image_native/receipts-v2b/ocr_run_receipt.json`](data/image_native/receipts-v2b/ocr_run_receipt.json)
- [`data/image_native/receipts-v2b/ocr_page_receipts.jsonl`](data/image_native/receipts-v2b/ocr_page_receipts.jsonl)
- [`data/image_native/receipts-v2b/voynich_regions.jsonl`](data/image_native/receipts-v2b/voynich_regions.jsonl)
- [`data/image_native/receipts-v2b/page_parity.jsonl`](data/image_native/receipts-v2b/page_parity.jsonl)
- [`data/image_native/receipts-v2b/region_parity.jsonl`](data/image_native/receipts-v2b/region_parity.jsonl)
- [`data/image_native/receipts-v2b/corpus_stage_a_summary.json`](data/image_native/receipts-v2b/corpus_stage_a_summary.json)
- [`data/image_native/receipts-v2b/preservation_receipt.json`](data/image_native/receipts-v2b/preservation_receipt.json)

Every frozen row binds source identity, image SHA 256, OCR output SHA 256,
configuration, geometry, run identity, and its own receipt hash. Any missing
diplomatic, terminology, translation, review, or adjudication layer keeps the
record unresolved.

## Comparative Glagolitic evidence

The local comparative inventory contains 2,670 registered asset records and
1,827 unique pixel payloads across 6 collections. Exactly 1,713 assets have saved
canvas mappings. Zero assets are training ready.

| Local set | Assets | Unique pixels | Current disposition |
|---|---:|---:|---|
| Petrisov zbornik, 1468 | 703 | 703 | Croatian book cursive in three unattributed hands; quarantined pending hand boundaries |
| GAMS Zrcalo, 1445, Borg. L. VII. 9 | 162 | 162 | Angular book hand; mixed Old Croatian witness of unresolved origin; study only |
| Folder labelled Misal kneza Novaka | 703 | 703 | Excluded because every image is byte identical to Petrisov |
| Istarski razvod, 1546 | 214 | 74 | Office cursive control; quarantined pending canvas mapping and exact duplicate collapse |
| Vinodolski zakon | 40 | 40 | Later control with unresolved hand; quarantined pending canvas mapping |
| Mavrov brevijar, 1460 to 1471 | 848 | 848 | Formal and calendar layers remain unmapped; quarantined pending hand boundaries and line level lineage |

The source authority register now contains 17 target, manuscript, terminology,
Latin, and negative control records. It includes exact dated NLR Glagolitic
cursive wills from 1460 and 1472, the 1403 to 1404 Hrvoje formal hand, and the
Bodleian fifteenth century Glagolitic book control. All four are reference only.
The two NLR exhibition images and their rights-aware receipt are preserved under
`F:\Dropbox\0 ZFD\00_GM\NLR_Bercic_cursive_wills_1460_1472_20260728`.
The receipt SHA 256 is
`14b26222ab01e09fdba6b65108389e6796809e63e9b55560e275e3d8a8cf22e2`.

There is no verified shorthand corpus and no balanced fifteenth century set of
angular, cursive, shorthand, and longhand hands yet. That is a direct blocker
for a defensible recognizer.

Comparative receipts are in:

- [`data/image_native/comparative_sources.json`](data/image_native/comparative_sources.json)
- [`data/image_native/comparative_assets.jsonl`](data/image_native/comparative_assets.jsonl)
- [`data/image_native/comparative_duplicate_groups.jsonl`](data/image_native/comparative_duplicate_groups.jsonl)
- [`data/image_native/comparative_asset_summary.json`](data/image_native/comparative_asset_summary.json)

## Clean Windows setup

Run from the repository root in PowerShell:

```powershell
py -3.13 -m venv .venv
.venv\Scripts\python -m pip install pip==26.1.2
.venv\Scripts\python -m pip install -r requirements-image-native.txt
.venv\Scripts\python -m pip install -e .
.venv\Scripts\python -m pytest -q -p no:cacheprovider
```

Dependencies are pinned in
[`requirements-image-native.txt`](requirements-image-native.txt).

Provision the two quarantined comparative models and verify all five registered
files:

```powershell
.venv\Scripts\python -m zfd_image_native acquire-models `
  --register data\image_native\model_register.json `
  --repository-root . `
  --receipt build\image_native\model_acquisition_receipt.json

.venv\Scripts\python -m zfd_image_native validate-models `
  --register data\image_native\model_register.json `
  --repository-root . `
  --require-cache
```

## Reproduce the image native lane

Build the Yale page authority manifest:

```powershell
.venv\Scripts\python -m zfd_image_native build-manifest `
  --map 06_Pipelines\glagolitic_ocr\data\folio_iiif_map.json `
  --output data\image_native\voynich_pages.jsonl
```

Acquire and checksum the Yale image derivatives:

```powershell
.venv\Scripts\python -m zfd_image_native acquire `
  --manifest data\image_native\voynich_pages.jsonl `
  --output build\image_native\sources\yale-ms-408 `
  --updated-manifest build\image_native\voynich_pages.acquired.jsonl
```

Run provisional segmentation over every registered surface:

```powershell
.venv\Scripts\python -m zfd_image_native segment-corpus `
  --manifest build\image_native\voynich_pages.acquired.jsonl `
  --output build\image_native\corpus
```

Freeze compact source and parity receipts:

```powershell
.venv\Scripts\python -m zfd_image_native freeze-receipts `
  --manifest build\image_native\voynich_pages.acquired.jsonl `
  --corpus build\image_native\corpus `
  --output build\image_native\receipts-v2 `
  --repository-root .

.venv\Scripts\python -m zfd_image_native validate-receipts `
  --receipts build\image_native\receipts-v2 `
  --corpus build\image_native\corpus `
  --manifest build\image_native\voynich_pages.acquired.jsonl `
  --repository-root .
```

Page receipts store component counts and exact hashes. The full retained and
rejected component rows stay in the hash-bound page OCR artifacts under the
corpus root. This preserves exact validation without embedding millions of rows
in one receipt ledger.

The retained Stage A v1 receipt under `data\image_native` is preserved and is
expected to fail the freshness half of this gate. The compact current authority
is versioned under `data\image_native\receipts-v2b`; its large OCR artifacts live
under ignored `build` storage and the dated F evidence bundle.
Scientific acceptance separately requires reviewed geometry, leakage resistant
gold data, measured metrics, and qualified adjudication.

Validate the preserved v2b authority once, then build a page local visual index
for f1r:

```powershell
.venv\Scripts\zfd-visual-index validate-stage-a `
  --repository-root . `
  --manifest data\image_native\voynich_pages.jsonl `
  --stage-a-root 06_Pipelines\image_native_runs\20260728-v2b `
  --authority-root data\image_native\receipts-v2b

.venv\Scripts\zfd-visual-index index-page `
  --repository-root . `
  --manifest data\image_native\voynich_pages.jsonl `
  --stage-a-root 06_Pipelines\image_native_runs\20260728-v2b `
  --authority-root data\image_native\receipts-v2b `
  --page-id yale-ms-408:iiif:1006076 `
  --output 06_Pipelines\image_native_runs\20260728-v2b\visual_index\20260728-v1\1006076.json
```

The command rehashes the complete preservation inventory, byte compares the
seven local receipt files with the committed authority, validates Stage A, and
derives the page artifact path from its frozen receipt. Output cannot overlap
the frozen `corpus` or `receipts` directories. Every candidate keeps
`diplomatic_label`, `unknown_score`, and `recognition_confidence` null.
`semantic_class_authority_count` remains zero and
`accuracy_claim_allowed` remains false.

Register the local comparative assets without copying their pixels:

```powershell
.venv\Scripts\python -m zfd_image_native register-comparanda `
  --config data\image_native\comparative_sources.json `
  --source-mount "F:\Dropbox\0 ZFD\00_GM" `
  --output data\image_native

.venv\Scripts\python -m zfd_image_native validate-comparanda `
  --receipts data\image_native `
  --source-register data\image_native\source_register.json
```

Check every claim bearing legacy report for its visible quarantine banner:

```powershell
.venv\Scripts\python -m zfd_image_native `
  validate-publication-boundary `
  --repository-root .
```

See [`docs/IMAGE_NATIVE_OCR.md`](docs/IMAGE_NATIVE_OCR.md) for the pipeline
contract and [`docs/EVIDENCE_BOUNDARY.md`](docs/EVIDENCE_BOUNDARY.md) for the
quarantine rules.

## Evidence layers

The repository keeps these layers separate:

1. Source pixels, checksum, and coordinates
2. Provisional region, line, and grapheme geometry
3. Diplomatic glyph transcription
4. Expanded and normalised historical reading
5. Dated Croatian and Latin terminology analysis
6. Modern Croatian
7. Literal English
8. Fluent English
9. Alternatives, confidence, reviewer state, and adjudication

A page can become confirmed translated only when every candidate region has an
adjudicated text or nontext disposition and every required record joins through
the exact parent IDs and hashes.

## Legacy ZFD material

The original decoder, reports, generated translations, and historical README
remain in the repository for audit and blinded comparison after image native
outputs are frozen. They are quarantined evidence and are not inputs to primary
recognition.

The preserved historical narrative is
[`docs/legacy/README_PRE_IMAGE_NATIVE.md`](docs/legacy/README_PRE_IMAGE_NATIVE.md).

## Licence

See [`LICENSE`](LICENSE). Source images and comparative materials retain their
own institutional rights and reuse terms recorded in the source register.
