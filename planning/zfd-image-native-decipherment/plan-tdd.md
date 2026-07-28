# FORGE: TDD plan for zfd-image-native-decipherment

> Phase FORGE. These tests precede implementation. Each test names the
> counter-condition and the predicate that can kill the build.

## TESTS FIRST

### TEST: primary OCR cannot depend on inherited transcription

```python
def test_image_native_source_has_no_forbidden_dependency():
    # arrange: scan every Python source in zfd_image_native
    forbidden = {"eva", "ivtff", "zandbergen", "lsi_ivtff", "transcription/"}
    # act: collect imports, string paths, and resource opens in the primary lane
    hits = scan_primary_lane(forbidden)
    # assert: one hit kills image-native status
    assert hits == []
```

### TEST: official page identity is complete and unique

```python
def test_yale_manifest_has_all_210_unique_surfaces():
    # arrange: the checked-in 210-entry Yale IIIF map
    # act: build immutable page IDs from source ID plus IIIF numeric ID
    pages = build_page_manifest(OFFICIAL_MAP, local_image_root=None)
    # assert: no label, IIIF ID, or page ID silently collides or disappears
    assert len(pages) == 210
    assert len({p.page_id for p in pages}) == 210
    assert len({p.iiif_base for p in pages}) == 210
```

### TEST: legacy 209 images cannot masquerade as reconciled pages

```python
def test_legacy_209_set_reports_identity_debt():
    # arrange: 210 authority rows plus the 209 named legacy JPEGs
    # act: attempt exact binding without a checksum-backed acquisition receipt
    report = reconcile_local_assets(OFFICIAL_MAP, LEGACY_JPG_ROOT)
    # assert: ambiguous split derivatives and missing surfaces remain explicit
    assert report.authoritative_pages == 210
    assert report.fully_verified is False
    assert report.unverified or report.missing
```

### TEST: source rights gate blocks unsafe training

```python
def test_training_source_requires_rights_and_identity():
    # arrange: a source with blank rights and unresolved identity
    source = source_fixture(training_use="train", rights_text="",
                            identity_status="unresolved")
    # act
    report = validate_sources([source])
    # assert
    assert report.ok is False
    assert {e.code for e in report.errors} >= {"RIGHTS_MISSING", "IDENTITY_UNRESOLVED"}
```

### TEST: duplicate and lineage leakage is rejected

```python
def test_split_rejects_duplicate_crossing():
    # arrange: an original in train and a crop or exact duplicate in test
    rows = split_fixture(parent_split="train", derivative_split="test")
    # act
    report = validate_split(rows)
    # assert
    assert report.ok is False
    assert "LINEAGE_LEAKAGE" in {e.code for e in report.errors}
```

### TEST: image OCR emits geometry, alternatives, and unknown rejection

```python
def test_real_page_emits_open_set_lattice():
    # arrange: authentic VM_f1r pixels with a verified checksum record
    # act: process with no templates, language model, map, or lexicon
    result = process_page(page_record, OpenSetConfig())
    # assert: the output is spatially anchored and never forces a letter
    assert result.page_sha256 == page_record.sha256
    assert all(line.region_id for line in result.lines)
    assert all(g.polygon and 0.0 <= g.unknown_score <= 1.0 for g in result.graphemes)
    assert all(g.diplomatic_label is None for g in result.graphemes)
```

### TEST: OCR output is deterministic

```python
def test_same_pixels_and_config_produce_same_receipt():
    # arrange: identical source checksum and canonical configuration
    # act
    first = process_page(page_record, config)
    second = process_page(page_record, config)
    # assert
    assert canonical_json(first) == canonical_json(second)
```

### TEST: confidence layers cannot be conflated

```python
def test_ocr_confidence_cannot_populate_semantic_confidence():
    # arrange: high visual cluster confidence with no linguistic evidence
    record = evidence_fixture(ocr_confidence=0.99, terminology_links=[])
    # act
    report = validate_evidence_record(record)
    # assert
    assert record.semantic_confidence is None
    assert report.ok is True
```

### TEST: page translation parity requires every exact join

```python
def test_confirmed_translation_fails_when_one_layer_is_missing():
    # arrange: matching page, region, OCR, transcription, and terminology IDs,
    # with fluent English or adjudicator deliberately absent
    records = complete_parity_fixture()
    records.translation.fluent_english = None
    records.translation.adjudicator_id = None
    # act
    report = validate_page_parity(*records)
    # assert
    assert report.confirmed_translated == 0
    assert report.unresolved == 1
    assert {"FLUENT_ENGLISH_MISSING", "ADJUDICATION_MISSING"} <= set(report.reasons)
```

### TEST: filename guesses cannot join records

```python
def test_join_requires_parent_id_and_hash():
    # arrange: matching filenames with different parent checksum or blank parent ID
    # act
    report = validate_page_parity(*filename_collision_fixture())
    # assert
    assert report.ok is False
    assert "PARENT_IDENTITY_MISMATCH" in report.reasons
```

### TEST: zero gold truth reports not measured

```python
def test_metrics_refuse_accuracy_without_gold():
    # arrange: predictions and an empty adjudicated gold set
    # act
    metrics = evaluate_predictions(gold=[], predictions=predictions)
    # assert
    assert metrics.status == "not_measured"
    assert metrics.cer is None
    assert metrics.accuracy_claim_allowed is False
```

### TEST: metric arithmetic is independently checkable

```python
def test_cer_unknown_rejection_and_calibration_on_fixture():
    # arrange: fixed small gold and prediction fixtures with known edit counts
    # act
    metrics = evaluate_predictions(GOLD_FIXTURE, PREDICTION_FIXTURE)
    # assert
    assert metrics.character_edits == EXPECTED_EDITS
    assert metrics.reference_characters == EXPECTED_REFERENCE_CHARS
    assert metrics.unknown_true_positive == EXPECTED_UNKNOWN_TP
    assert metrics.ece == EXPECTED_ECE
```

### TEST: completion claims are blocked by receipts

```python
def test_complete_translation_claim_is_blocked():
    # arrange: the current corpus has unresolved pages and no adjudicated gold OCR
    # act
    report = validate_claims(CURRENT_LEDGER, CURRENT_RECEIPTS)
    # assert
    assert report.claim("complete_translation").allowed is False
    assert report.claim("ragusan_provenance").allowed is False
    assert report.claim("ocr_accuracy").allowed is False
```

### TEST: terminology keeps historical and modern layers separate

```python
def test_terminology_record_requires_dated_locator_and_separate_forms():
    # arrange: a proposed term whose observed and reconstructed forms are merged
    term = term_fixture(source_date=None, passage_locator=None,
                        observed_form="ulje", reconstructed_form="ulje")
    # act
    report = validate_terminology(term)
    # assert
    assert report.ok is False
    assert {"SOURCE_DATE_MISSING", "PASSAGE_LOCATOR_MISSING"} <= set(report.codes)
```

### TEST: whole corpus run cannot silently omit pages

```python
def test_corpus_summary_accounts_for_every_manifest_page():
    # arrange: 210 page manifest with one OCR record deliberately missing
    # act
    report = validate_corpus_coverage(manifest, ocr_records[:-1])
    # assert
    assert report.total_pages == 210
    assert report.missing_pages == 1
    assert report.ok is False
```

### TEST: legacy JSON and CSV loaders are UTF 8 on Windows

```python
def test_decoder_loaders_work_under_cp1252_console():
    # arrange: UTF 8 fixtures containing Croatian and Glagolitic characters
    # act: instantiate every legacy decoder loader without PYTHONUTF8
    # assert: no UnicodeDecodeError and decoded values preserve code points
    assert load_all_utf8_fixtures() == EXPECTED_VALUES
```

### TEST: legacy mapper failures return nonzero

```python
def test_mapper_pattern_failure_changes_process_exit():
    # arrange: inject a mapping that removes required pattern output
    # act
    completed = run_mapper_with_failure_fixture()
    # assert
    assert completed.returncode != 0
    assert "[FAIL]" in completed.stdout
```

## Build order after the red receipt

1. Add root package metadata, schemas, dataclasses, deterministic JSON helpers,
   and ASCII safe CLI errors.
2. Implement source validation and the 210 row Yale page manifest.
3. Implement the primary lane dependency scanner and runtime resource boundary.
4. Implement duplicate lineage closure and split validation.
5. Implement deterministic page preprocessing, candidate regions and lines,
   visual descriptors, open-set cluster alternatives, and unknown rejection.
6. Implement metrics, parity, corpus coverage, and claim gates.
7. Add source register, terminology schema, claim ledger, and annotation protocol.
8. Repair the narrow UTF 8 loaders and mapper exit semantics.
9. Run the complete local manuscript through Stage A and commit deterministic
   summaries while detailed generated records remain under ignored `build/`.
10. Correct public documentation to the claim ledger result.

## Falsifier to section map

- Primary OCR boundary, page identity, rights, and split tests ->
  `section-01-evidence-identity`.
- Image processing, open-set lattice, determinism, and unknown tests ->
  `section-02-image-native-ocr`.
- Metrics, coverage, parity, and claim tests ->
  `section-03-validation-gates`.
- Terminology and translation separation tests ->
  `section-04-terminology-translation`.
- UTF 8, mapper exit, packaging, and documentation tests ->
  `section-05-portability-claims`.
- Whole manuscript run and acquisition receipts ->
  `section-06-corpus-execution`.
