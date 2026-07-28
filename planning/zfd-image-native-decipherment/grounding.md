# GROUND: reality check for zfd-image-native-decipherment

> Phase GROUND. Every interface and count below was read or measured from the
> current branch, local corpus, installed runtime, or live Yale IIIF metadata.

## Real signatures and APIs the build will call

### Repository and Yale image authority

- Working root: `F:\Dropbox\0 ZFD`.
- Branch: `codex/zfd-image-native-decipherment`.
- Base commit: `3193695b69fa8983734af8917cf3c791118033fd`.
- `06_Pipelines/glagolitic_ocr/data/folio_iiif_map.json` is a JSON object with
  210 unique surface labels mapped to 210 unique Yale IIIF Image API base URLs.
- Example: `1r` maps to
  `https://collections.library.yale.edu/iiif/2/1006076`.
- Live `info.json` for `1006076` returned IIIF Image API 2 level 2, width 2,972,
  height 3,766, 512 pixel tiles, colour and gray qualities, and region and size
  operations. Live spine record `11868210` returned 1,030 by 3,833 pixels.
- A deterministic derivative uses
  `{iiif_base}/full/{width},/0/default.jpg` and records the IIIF ID and width.
- Root `folio_iiif_map.json` has 197 simplified folio keys and drops covers,
  edges, composite surfaces, and split identity. It is not corpus authority.

### Current local manuscript assets

- `folios/jpg`: 209 RGB JPEGs, 55,620,083 bytes.
- Width range: 547 to 1,536 pixels. Height range: 646 to 1,536 pixels. There are
  136 distinct dimensions, 191 portrait pages, and 18 landscape pages.
- `folios/jp2`: 209 sequential JP2 files from `0000` through `0208`.
- `00_GM/TheVoynichManuscript/Voynich_Manuscript_jp2`: another 209 sequential
  files. Prior SHA256 audit found all three JP2 copies are exact duplicate sets.
- The 209 named JPEGs do not equal the official 210 surfaces. Tail, fore edge,
  spine, and back cover are absent. Three extra local split derivatives, second
  parts of 70v, 72v, and 102v, lack one to one official surface labels.
- Official composite and foldout labels require plural `folios_covered` fields.
- Resolution: named JPEGs may support local smoke tests. Newly acquired images
  named by IIIF ID are required for authoritative records. No join uses order.

### Existing OCR interfaces

- `ManuscriptImageProcessor.load(image_path)` returns a BGR NumPy array through
  `cv2.imread`.
- `preprocess(image, deskew_enabled=True)` performs grayscale conversion,
  adaptive thresholding, morphology, and optional deskew.
- `segment_lines(binary_image)` returns `(y_start, y_end)` pairs from a horizontal
  projection threshold of 0.1 and a minimum line height.
- `GlyphExtractor.extract(binary_image)` returns dictionaries with `image`,
  `bbox` as `(x, y, w, h)`, and an index.
- `GlagoliticOCR.process_image(image_path, output_dir=None)` chains those calls.
- `classify_glyph` returns `(None, 0.0)` when no external template directory was
  loaded. The repository contains no template set.
- The old builder merges Glagolitic, EVA, and Croatian into one recognition
  object. The new primary package cannot call it because those layers must remain
  independent.

### New package functions grounded in real libraries

```text
load_source_register(path) -> list[SourceRecord]
build_page_manifest(iiif_map, image_root, output) -> ManifestReport
validate_page_manifest(records) -> ValidationReport
process_page(page_record, config) -> PageOCRRecord
process_manifest(manifest, output_dir, config) -> CorpusOCRReport
validate_split(records) -> ValidationReport
evaluate_predictions(gold, predictions) -> EvaluationReport
validate_page_parity(pages, regions, ocr, translations) -> ParityReport
validate_claims(claim_ledger, receipts) -> ValidationReport
```

Stage A can use installed `cv2`, `numpy`, and `PIL`, plus standard library
`hashlib`, `json`, `csv`, `pathlib`, `dataclasses`, `argparse`, and `unicodedata`.
All file operations specify UTF 8 and all CLI failure states return nonzero.

## Real data shapes at every interface

### Source register and local comparative records

```text
source_id, title, institution, shelfmark, stable_locator, manifest_uri,
date_min, date_max, language, script_family, script_style, hand_scope,
rights_text, rights_uri, training_use, redistribution_allowed,
identity_status, evidentiary_role, notes
```

Observed IIIF Presentation API 2 fields include `@id`, `label`, `metadata`,
`sequences[0].canvases`, canvas `@id`, dimensions, resource `@id`, and service
`@id`.

- Petrisov zbornik: manifest `ri=15967`, 703 canvases, shelfmark R 4001, dated
  1468, Glagolitic, rights `Javno dobro`, three cursive hands in the description.
- Istarski razvod: manifest `ri=14616`, 74 canvases, shelfmark R 3677,
  Glagolitic, rights `Javno dobro`. The local folder has 214 JPEGs and needs
  deduplication.
- Vinodolski zakon: manifest `ri=11569`, 40 canvases, shelfmark R 4080,
  beginning of the sixteenth century, Glagolitic, rights `Javno dobro`. It is a
  later control.
- Misal kneza Novaka: 559 canvas manifest, dated 1368, Glagolitic, contractual
  restrictions. Its local folder has 703 files previously found SHA identical to
  Petrisov, so it is quarantined as misidentified.
- Hrvoje's Missal: local manifests expose 538 canvases and one canvas under
  different identities. Its folder has 703 files. Identity and rights remain
  unresolved, so it is quarantined.

### Page, region, and grapheme records

```text
page_id, source_id, source_label, iiif_base, info_uri, image_uri,
requested_width, local_path, sha256, width, height, mime_type,
folios_covered, surface_type, text_expectation, duplicate_group,
derivative_of, identity_status, acquisition_time, acquisition_receipt

region_id, page_id, polygon, region_type, detection_method, review_state
line_id, region_id, polygon, baseline, reading_order, crop_sha256
grapheme_id, line_id, polygon, visual_descriptor, cluster_candidates,
alternatives, unknown_score, confidence, method, model_receipt
```

Coordinates are integer pixels in the exact parent image. Every crop records the
parent checksum and its own checksum. `page_id` derives from source ID plus the
immutable IIIF numeric ID. Folio labels are metadata and may be plural.

### Terminology and translation records

```text
record_id, line_id, diplomatic_candidates, diplomatic_confidence,
normalised_reading, normalisation_confidence, historical_language,
morphology, terminology_links, modern_croatian, literal_english,
fluent_english, alternatives, reviewer_ids, adjudicator_id, review_state,
disposition
```

Terminology separately stores observed form, reconstructed form, lemma, language,
date range, source locator, Latin parallel, modern Croatian, English, alternatives,
confidence, and reviewer state. Character coverage is not semantic confidence.

### Split, metric, and parity records

- Split identity is the transitive closure of source manuscript, shelfmark, hand,
  page lineage, duplicate group, and synthetic parent.
- Metrics record population, split receipt, ground truth receipt, line detection
  counts, CER counts, grapheme confusion, unknown rejection counts, calibration
  bins, grouped results, and confidence intervals.
- A metric with zero adjudicated truth is `not_measured`, never zero.
- Page parity joins page, region, OCR, diplomatic transcription, terminology,
  modern Croatian, literal English, fluent English, citations, and review state
  by explicit IDs and parent hashes.

## Hardware and runtime verified

- Python 3.13.14 at
  `C:\Users\czuger\AppData\Local\Programs\Python\Python313\python.exe`.
- Python launcher also exposes Python 3.14 and Astral CPython 3.11.15.
- pytest 9.1.1; opencv-python 4.13.0.92; NumPy 2.5.0; Pillow 12.2.0;
  jsonschema 4.26.0; scikit-learn 1.9.0; SciPy 1.18.0; torch 2.12.1.
- Kraken and torchvision are absent.
- Standard output is cp1252 while default file encoding is UTF 8. CLI output must
  be ASCII safe or use `python -X utf8`.
- `F:` had 1,968,610,414,592 free bytes during GROUND.
- CPU, RAM, and GPU CIM queries were denied. No acceleration claim is made.

## Current executable receipts

- Default `python -m pytest zfd_decoder/tests -p no:cacheprovider` fails during
  collection because `compound.py` opens UTF 8 JSON through cp1252.
- With `python -X utf8`, all 32 decoder mechanics tests pass.
- Default `python scripts/test_mapper.py` fails while printing Unicode marks.
  Under UTF 8 it prints successful cases, while the Croatian pattern routine
  always returns true and there is no aggregate failure exit.
- `coverage_v36b.py` and `coverage_v40.py` fail on
  `/home/claude/word_freq.csv`.
- Dropbox pytest cache directories can become unreadable. New test commands use
  `-p no:cacheprovider` and an explicit temporary directory.

## Contradictions between HARDEN and reality, resolved

1. The 210 official surfaces and 209 local files do not reconcile by filename.
   Official IIIF IDs define canonical pages; local assets remain verified,
   unverified, or absent until a checksum backed binding exists.
2. Kraken is absent and Python 3.13 is active. Stage A uses installed OpenCV and
   NumPy. Polyscriptor and Rabus use a pinned Python 3.11 or 3.12 optional
   environment after model and data rights are registered.
3. No adjudicated image truth exists. The metric harness is implemented now,
   while real OCR accuracy remains `not_measured` until gold review exists.
4. Automatic line detection confuses illustrations with text. Every page receives
   candidate region records plus review state. Confirmed region coverage waits for
   human review and no page is silently excluded.
5. Generated crops and detailed OCR records go under ignored `build/`.
   Deterministic manifests, schemas, summaries, receipts, and tests are committed.
6. The console is cp1252 and legacy loaders omit encodings. New I/O is UTF 8 and
   ASCII safe. Narrow legacy loaders and mapper exits receive tests and repairs.
