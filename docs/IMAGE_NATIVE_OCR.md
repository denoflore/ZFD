# ZFD image native OCR

This package starts from registered manuscript pixels. It records page identity,
candidate text regions, lines, grapheme geometry, visual alternatives, explicit
unknown rejection, and deterministic receipts. It does not inherit a Voynich
transcription or assign Glagolitic letters without image aligned adjudicated
evidence.

## Current scientific status

- Page and grapheme segmentation is executable. The current native detector
  groups Cartesian fragments, applies continuity and ink density gates, records
  every rejected component, and marks suspect layouts for review.
- A curved or radial text lane has not been implemented. Circular and strongly
  curved layouts remain a segmentation blocker.
- Diplomatic labels remain null when no registered recognizer is available.
- OCR accuracy is `not_measured` until a leakage resistant held-out gold set is
  adjudicated.
- Existing decoder and translation artifacts are quarantined comparison material.
- A page is not confirmed translated until the strict parity gate joins its exact
  image hash, region geometry, OCR, diplomatic record, terminology, translation,
  reviewer, and adjudicator.

## Clean Windows environment

Run from the repository root in PowerShell:

```powershell
py -3.13 -m venv .venv
.venv\Scripts\python -m pip install pip==26.1.2
.venv\Scripts\python -m pip install -r requirements-image-native.txt
.venv\Scripts\python -m pip install -e .
.venv\Scripts\python -m pytest -q -p no:cacheprovider
```

The verified development environment used Python 3.13.14. Dependency versions
are pinned in `requirements-image-native.txt`.

## Commands

Build the 210 surface authority manifest:

```powershell
.venv\Scripts\python -m zfd_image_native build-manifest `
  --map 06_Pipelines\glagolitic_ocr\data\folio_iiif_map.json `
  --output data\image_native\voynich_pages.jsonl
```

Acquire Yale IIIF derivatives and write content checksums:

```powershell
.venv\Scripts\python -m zfd_image_native acquire `
  --manifest data\image_native\voynich_pages.jsonl `
  --output build\image_native\sources\yale-ms-408 `
  --updated-manifest build\image_native\voynich_pages.acquired.jsonl
```

Provisionally segment one page:

```powershell
.venv\Scripts\python -m zfd_image_native segment-page `
  --manifest build\image_native\voynich_pages.acquired.jsonl `
  --page-id yale-ms-408:iiif:1006076 `
  --output build\image_native\smoke\1006076.json
```

Provisionally segment all registered surfaces:

```powershell
.venv\Scripts\python -m zfd_image_native segment-corpus `
  --manifest build\image_native\voynich_pages.acquired.jsonl `
  --output build\image_native\corpus
```

Detailed pixels and OCR records live under ignored `build/`. Compact authority,
source, claim, and review receipts are staged separately for bounded publication.

Freeze and validate content bound receipts after segmentation:

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

Each page receipt stores the page OCR artifact hash, retained and rejected
component hashes, exact counts, and one combined disposition hash. The large
component rows remain under `--corpus`. Artifact integrity, receipt structure,
and current-code freshness are reported separately.

Freshness validation rehashes every image named by the supplied manifest. Each
resolved image path must remain inside `--repository-root`. Populate the clone
with `acquire`, a byte-for-byte copy, or same-volume hardlinks at the registered
paths. A directory junction that resolves to pixels outside the clone is
rejected as `CURRENT_PAGE_IMAGE_OUTSIDE_REPOSITORY`.

The preserved Stage A v1 records under `data\image_native` currently return
`archival_integrity_ok=true`, `freshness_ok=false`, and `ok=false`. Freshness is
blocked by the current schema, implementation, configuration, and dependency
lock, plus the current authoritative manifest. The validator reports
`CURRENT_SCHEMA_VERSION_MISMATCH`, `CURRENT_IMPLEMENTATION_MISMATCH`,
`CURRENT_CONFIG_MISMATCH`, `CURRENT_DEPENDENCY_SET_MISMATCH`, and
`CURRENT_MANIFEST_MISMATCH`. Receipt freshness is a reproducibility check.
Geometry review, held out
metrics, recognition, and translation remain separate scientific gates.

The current local v2b run freezes 210 pages, 670 regions, 30,141 provisional line
groups, 356,739 unknown graphemes, and 4,953,273 rejected components. Its
independent validator returns `archival_integrity_ok=true`,
`artifact_integrity_ok=true`, `freshness_ok=true`, and `ok=true`, with zero
confirmed translated pages or regions. The compact page ledger is 3,671,402
bytes, down from 1,170,540,526 bytes, while the artifact hashes still cover all
5,310,012 component dispositions. The 1,415,607,859 byte evidence set is
preserved at
`F:\Dropbox\0 ZFD\06_Pipelines\image_native_runs\20260728-v2b`; its 220 file
inventory SHA 256 is
`fb292f1449467b135b1272be1e9d7d212314bb43a0c067210de5e6ac538049d9`.
The directory is local evidence and is excluded from Git.

Register and validate local comparative manuscript lineage:

```powershell
.venv\Scripts\python -m zfd_image_native register-comparanda `
  --config data\image_native\comparative_sources.json `
  --source-mount "F:\Dropbox\0 ZFD\00_GM" `
  --output data\image_native

.venv\Scripts\python -m zfd_image_native validate-comparanda `
  --receipts data\image_native `
  --source-register data\image_native\source_register.json
```

The frozen Stage A receipt accounts for 210 surfaces, 337 candidate regions,
22,516 provisional line groups, and 490,595 grapheme components. Every grapheme
remains an explicit unknown. This receipt predates the Cartesian fragment
detector and stays frozen until the revised native geometry and curved text lane
are reviewed.

## Reproduce comparative acquisitions

The dated 1445 GAMS Zrcalo selection is acquired from its edition page and
bound to the Vatican IIIF canvases:

```powershell
.venv\Scripts\python -m zfd_image_native.comparative_acquire `
  --source-id gams-zrcalo-1445 `
  --manifest-uri https://digi.vatlib.it/iiif/MSS_Borg.ill.9/manifest.json `
  --selection-uri https://gams.uni-graz.at/o:speculum.01 `
  --output "F:\Dropbox\0 ZFD\00_GM\GAMS_Zrcalo_1445" `
  --expected-count 162 `
  --width 2000
```

The complete official Mavrov breviary manifest is acquired without an edition
page selection. NSK dates the formal ustavna layer to 1460 and the calendar
addition to 1471. Their canvas boundaries have not been adjudicated, so the
whole 1460 to 1471 source remains quarantined:

```powershell
.venv\Scripts\python -m zfd_image_native.comparative_acquire `
  --source-id nsk-mavrov-r7822 `
  --manifest-uri "https://digitalna.nsk.hr/admin/api.php?storage=iiif.m&ri=16161" `
  --output "F:\Dropbox\0 ZFD\00_GM\Mavrov_brevijar_1460" `
  --expected-count 848 `
  --width 2000
```

The resulting local comparative ledger contains 2,670 assets, 1,827 unique
pixel payloads, and 1,713 mapped canvases. Zero assets are training ready. No
separately verified shorthand corpus has been registered.

## Quarantined Kraken geometry environment

Kraken 6.0.0 runs in a separate Python 3.11.15 environment because the primary
package is pinned for Python 3.13 and NumPy 2.5. The comparison lock mirrors the
verified working environment exactly:

```powershell
uv venv --python 3.11.15 .venv-kraken
uv pip install --python .venv-kraken\Scripts\python.exe `
  -r requirements-kraken-comparison.txt
```

Validate the registered model file before running it:

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

`acquire-models` downloads through temporary files, enforces registered cache
paths, verifies byte length and SHA 256 before atomic replacement, and writes a
self hashing receipt. The current registry contains two quarantined models and
five files totalling 47,723,567 bytes. Model acquisition never permits primary
lane use.

Run the model over the registered corpus from the repository root. The Python
3.11 environment imports the local source tree directly and does not install the
Python 3.13 package metadata:

```powershell
.venv-kraken\Scripts\python -m zfd_image_native.kraken_compare `
  --manifest data\image_native\voynich_pages.jsonl `
  --all `
  --receipts data\image_native\receipts-v2b `
  --model-register data\image_native\model_register.json `
  --model-id kraken-blla-zenodo-14602569 `
  --repository-root . `
  --output build\image_native\comparisons-corpus-v2b

.venv\Scripts\python -m zfd_image_native `
  validate-geometry-comparison-corpus `
  --summary build\image_native\comparisons-corpus-v2b\summary.json `
  --manifest data\image_native\voynich_pages.jsonl
```

The current v2b comparison receipt covers all 210 pages with 2,088 regions and
7,554 lines. Seven pages record a tolerant retry following a strict topology
failure. Summary ID
`sha256:3f80eddbc3844b38c96f19e077c1a2f86f30d4d080791e460ff5e528b7efcf6b`
and receipt SHA 256
`8eae5483afbac648ee46a2a6b7e4edfd1895f6f56bed6c60e4de1d60df1d95a4`
bind it to v2b run ID
`sha256:85fb4df911344e879fa4a9c81a978cc44f0247523b0ac0f19e44192cd3daaf61`.
Every result is unreviewed, its `primary_lane_allowed` field is false,
recognition labels are null, and `metrics_status` is `not_measured`. These
records measure corpus execution and geometry accountability. They do not
measure segmentation accuracy, OCR accuracy, language, translation, or
provenance.

Run the registered Rabus CRNN CTC model on one exact Kraken line as a
quarantined recognition comparison:

```powershell
.venv-kraken\Scripts\python -m zfd_image_native.rabus_compare `
  --manifest data\image_native\voynich_pages.jsonl `
  --page-id yale-ms-408:iiif:1006272 `
  --geometry build\image_native\comparisons-corpus-v2b\1006272.kraken.json `
  --line-id sha256:36dfa51f5741972be24fe355b0d345426c1567e44bd46c512dbff81ca68f5213 `
  --model-register data\image_native\model_register.json `
  --model-id rabus-crnn-ctc-glagolitic-16549a7f `
  --repository-root . `
  --output build\image_native\rabus-comparison\1006272-36dfa51f-v2b.json
```

The frozen probe emits 420 time steps and 24 greedy class events. Its
`acceptance_state` is `rejected`, `recognition_confidence` and
`unknown_probability` are null, and `metrics_status` is `not_measured`. The
model emits expanded Latin comparative text and has no source excluded,
open-set evaluation on the selected hand. It supplies no diplomatic labels or
OCR accuracy evidence.
