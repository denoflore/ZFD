# HARDEN: the design for zfd-image-native-decipherment

> Phase HARDEN. The VIBE shape was attacked for circularity, forced readings,
> leakage, rights ambiguity, false joins, semantic confidence inflation, and
> publication overclaiming. The design below is what survived.

## NSL: what is missing or expected but absent

- No canonical join across Yale surface, folio, local image, checksum, text
  region, OCR record, transcription record, terminology record, and translation.
- No committed source register with authority, date, script style, hand, rights,
  stable locator, checksum, identity review, and evidentiary role.
- No image aligned ground truth for Voynich or the local Glagolitic corpus.
- No diplomatic Glagolitic truth. Existing models output Latin transliteration
  and may expand abbreviations.
- No open-set recognition state. The current template matcher either forces a
  supplied class or emits no result.
- No full manuscript page or text region inventory. Current denominators vary
  among 201 EVA files, 199 converted files, 197 transcription directories, 210
  Yale IIIF surfaces, and 225 index units.
- No split lineage that keeps duplicate files, crops, synthetic derivatives,
  folio groups, hands, and manuscripts together.
- No machine gate connecting a completion claim to image identity, geometry,
  recognition, terminology, translation, and human review.
- No model and data receipts binding code revision, input hashes, vocabulary,
  configuration, and result metrics.
- No portable root package, dependency declaration, or default Windows test run.
- No independent fifteenth century terminology ledger linking observed forms,
  historical Croatian, Croatian Church Slavonic, Latin parallels, modern
  Croatian, English, alternatives, dates, and citations.
- No direct pre seventeenth century documentary link between MS 408 and Ragusa.

## ZLF: what would falsify the design or hypothesis

### Build falsifiers

1. Any primary OCR module imports, opens, or derives labels from EVA, IVTFF, ZL,
   legacy transcription, the ZFD character map, lexicons, or translations.
2. A page, region, line, or translation is joined by a guessed filename without
   a source identifier, checksum, and parent identifier.
3. A duplicate image, crop lineage, hand, folio group, or source manuscript
   crosses a train and held out boundary.
4. A training source lacks a recorded permission state or a stable authority.
5. OCR confidence is reused as script, language, terminology, or translation
   confidence.
6. A page is called confirmed translated when any required record or qualified
   review state is missing.
7. Whole manuscript processing silently drops an image or text region.
8. A clean Windows run requires a private absolute path or undocumented package.

### Glagolitic hypothesis falsifiers

1. A recogniser that generalises across held out genuine Glagolitic hands returns
   unstable clusters or calibrated unknowns on sealed Voynich lines.
2. Proposed Voynich grapheme assignments change materially across scribal hands,
   sections, crop margins, resolution, or small preprocessing changes.
3. Independent palaeographers reject the claimed ductus and structural matches.
4. Croatian yield disappears when inherited transcription, dictionaries,
   illustration cues, and abbreviation expansion are removed.
5. Wrong mappings, unrelated medieval lexicons, or competing scripts produce
   comparable registered scores.
6. Correcting the current Unicode mapping removes the apparent lexical results.

### Ragusan hypothesis falsifiers

1. Direct period Ragusan hands favour Latin and Cyrillic while no comparable
   Glagolitic production hand is found.
2. Registered rare ingredient bundles fail to distinguish Dubrovnik from Venice,
   Zadar, Split, Kotor, Vinodol, Istria, or broad European controls.
3. Matches depend on salt, water, wine, oil, wax, metals, or other ubiquitous
   commodities.
4. No production, ownership, trade, or custody link survives independent archival
   review.

## CANON CHECK

- The user requires the whole manuscript to pass through one image native record
  system. The design creates the complete page and region ledger before model
  claims, then retains unresolved as a valid result.
- The user forbids dependence on inherited transliterations. The primary package
  has an enforced dependency boundary, with legacy comparisons in a separate
  adapter and output namespace.
- The user requires period appropriate Croatian and Latin terminology. The schema
  keeps observed forms, historical reconstructions, Latin parallels, modern
  Croatian, literal English, fluent English, and speculation separate.
- The user requires page by page confirmation. The parity gate operates on exact
  identifiers, hashes, coordinates, review states, and parent links.
- Repository audit evidence requires the existing all folio output to remain
  historical and qualified. No artefact is deleted; public wording is corrected.
- Scholarly evidence distinguishes book cursive, office cursive, angular formal,
  Latin, and Cyrillic controls. Dataset labels preserve those categories.

## What survived: the design

### 1. One package and one command surface

Create a root Python package named `zfd_image_native` with a `zfd-ocr` command.
The package owns source validation, corpus manifest generation, image processing,
open-set grapheme lattices, split validation, evaluation metrics, evidence records,
page parity, and completion claim gates.

Core commands:

```text
zfd-ocr sources validate
zfd-ocr manifest build
zfd-ocr manifest validate
zfd-ocr run --manifest ... --output ...
zfd-ocr parity --manifest ... --records ...
zfd-ocr evaluate --gold ... --predictions ...
zfd-ocr claims validate
```

All commands accept explicit paths, use UTF 8, emit deterministic JSON or JSONL,
and return nonzero when their named gate fails.

### 2. Immutable source and corpus identity

`data/source_register.json` records source level authority and rights.
`data/voynich_pages.jsonl` records every official Yale surface and local image
binding. `data/voynich_regions.jsonl` records every known or detected text bearing
region. Each identity uses explicit parent IDs and SHA256.

Local duplicates remain present and are grouped by hash. Misidentified sources
are quarantined through `identity_status`, never silently renamed or trained on.

### 3. Evidence records with separate inference layers

Every record keeps:

```text
page pixels and checksum
region and line geometry
visual grapheme spans and opaque cluster candidates
diplomatic script candidates
expanded or normalised historical reading
historical Croatian and Latin terminology analysis
modern Croatian
literal English
fluent English
alternatives and explicit unknowns
confidence per layer
source citations
annotators, adjudicator, and review state
```

No downstream value overwrites the preceding layer.

### 4. Runnable image-native baseline

The first recogniser is deterministic and open set:

1. verify the source checksum;
2. normalise orientation and contrast without language knowledge;
3. detect candidate text regions and lines from image structure;
4. segment connected grapheme candidates while retaining ligature uncertainty;
5. produce stable visual descriptors and corpus cluster candidates;
6. emit alternatives and calibrated unknown status;
7. store exact geometry and preprocessing provenance.

This baseline does not claim letter identity. Its purpose is to make every pixel
to record transition inspectable and to provide the annotation substrate.

The Apache licensed Rabus CRNN CTC model enters later as a quarantined comparative
baseline. Its Latin transliteration and abbreviation expansion never become
diplomatic truth. A genuine Glagolitic recogniser requires expert corrected line
truth and leave one manuscript out evaluation.

### 5. Full manuscript coverage and parity

The manifest builder starts from the official 210 surface map, reconciles the 209
local image files, folio labels, foldouts, covers, and known missing leaves, and
requires an explicit exclusion reason for every nontext surface.

The first corpus run creates a record for every page and detected candidate text
region. Unreviewed geometry and unknown readings remain visible. The parity gate
reports exact counts for:

- source pages;
- text bearing pages;
- regions and lines;
- OCR records;
- diplomatic transcriptions;
- terminology analyses;
- modern Croatian renderings;
- literal and fluent English renderings;
- reviewer and adjudication states;
- confirmed, unresolved, excluded, and missing dispositions.

`confirmed_translated` requires all joins, nonempty source citations, calibrated
layer confidence, and the configured qualified review state.

### 6. Leakage resistant validation

The split group is the transitive closure of source manuscript, shelfmark, hand,
canvas lineage, derivative lineage, exact hash, perceptual duplicate group, and
synthetic parent. The validator rejects any crossing.

Evaluation reports line detection precision, recall, and F1; CER or sequence error;
grapheme confusion; unknown rejection precision and recall; confidence calibration;
and results by manuscript, hand, century, and script style. Synthetic and legacy
transcription comparisons use separate report sections.

### 7. Terminology and translation ledger

Terminology candidates require dated citations and preserve observed spelling,
expanded form, lemma, language, date range, domain, source passage locator,
modern Croatian equivalent, English gloss, alternatives, and reviewer state.
Decoder character coverage is forbidden as semantic confidence.

Translation records remain line aligned. They may be `unresolved`, `candidate`,
`reviewed`, or `adjudicated`. Only adjudicated records can satisfy the final page
translation gate.

### 8. Claim and provenance control

`data/claim_ledger.json` assigns every public claim a status, evidence, negative
evidence, falsifier, scope, and allowed wording. The validator blocks claims whose
wording exceeds their receipts.

Material date, writing date, script family, language, genre, production place,
trade context, ownership, and custody remain separate provenance variables. Ragusa
is tested alongside registered alternatives after the image reading is frozen.

## Staged implementation and proof

### Stage A: executable evidence foundation

- Package metadata and clean Windows test entry point.
- Source, page, region, OCR, translation, terminology, split, and claim schemas.
- Full Yale page manifest and local checksum reconciliation.
- Deterministic image-only segmentation and open-set lattice output.
- Page parity and claim gates.
- Corrected publication status and legacy test portability defects.
- Whole local manuscript baseline run with unresolved records preserved.

Proof: schema tests, dependency boundary test, source rights test, split leakage
test, real image smoke test, whole corpus count reconciliation, parity report, and
clean tracked diff after validation.

### Stage B: comparative Glagolitic benchmark

- Register and deduplicate Petrisov, Istarski, Vinodolski, GAMS, and permitted
  Rabus assets by manuscript and hand.
- Acquire pinned model metadata and weights with hashes.
- Create PAGE XML annotation queues and an expert adjudication protocol.
- Evaluate the untouched model on source-excluded material.

Proof: source and rights receipts, zero leakage, held out metrics by hand and
style, Unicode inventory check, and model provenance receipt.

### Stage C: Voynich recognition and transcription

- Freeze preprocessing, segmentation, Unicode inventory, clustering, and model
  selection before opening legacy transcriptions.
- Run every page, every detected region, and every proposed line.
- Obtain independent palaeographic labels and adjudication for the gold subset.
- Compare frozen image output to EVA only in the quarantined lane.

Proof: whole corpus image records, sealed gold metrics, cross-hand stability,
unknown rejection, and comparison report with lineage.

### Stage D: terminology and translation

- Acquire dated Croatian Glagolitic, Croatian Church Slavonic, Latin, and regional
  controls with exact locators.
- Resolve terms through cited alternatives and human review.
- Produce modern Croatian, literal English, and fluent English line records.
- Run page parity after every batch.

Proof: every text region has a disposition; confirmed pages satisfy the strict
join and review gate; unresolved pages remain named debt.

### Stage E: provenance falsification and publication

- Acquire direct Ragusan inventories and customs records plus comparison cities.
- Preregister matching rules, nulls, and multiple testing correction.
- Rank hypotheses and correct all public claims to the observed result.
- Commit and push only bounded stages with same turn receipts.

Proof: reproducible provenance report, claim ledger pass, full test matrix, fresh
clone regeneration, and remote commit receipt.
