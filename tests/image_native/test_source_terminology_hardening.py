"""Adversarial source dating and historical terminology evidence tests."""

from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from zfd_image_native.models import SourceRecord, TerminologyRecord
from zfd_image_native.io import canonical_json
from zfd_image_native.sources import validate_sources
from zfd_image_native.terminology import AUTHORITY_SCHEMA, validate_terminology


MANIFEST_HASH = "a" * 64
ASSET_HASH = "b" * 64
IMAGE_HASH = "c" * 64


def _source(**overrides: object) -> SourceRecord:
    values: dict[str, object] = {
        "source_id": "primary-witness",
        "source_label": "Primary witness",
        "title": "Primary witness title",
        "stable_locator": "https://example.invalid/primary-witness",
        "date_kind": "writing",
        "date_basis": "dated scribal colophon",
        "dating_authority": "Example manuscript catalogue",
        "dating_authority_locator": "https://example.invalid/catalogue",
        "dating_certainty": "exact",
        "material_date_start": None,
        "material_date_end": None,
        "writing_date_start": 1450,
        "writing_date_end": 1450,
        "text_date_start": None,
        "text_date_end": None,
        "copy_date_start": None,
        "copy_date_end": None,
        "publication_date_start": None,
        "publication_date_end": None,
        "institution": "Example archive",
        "shelfmark": "MS 1",
        "language": "Croatian",
        "script": "Croatian Glagolitic",
        "hand_style": "angular_cursive",
        "genre": "medical recipe",
        "region": "northern Adriatic",
        "source_type": "manuscript",
        "evidentiary_role": "primary_terminology_witness",
        "training_use": "reference_only",
        "rights_statement": "Research consultation permitted.",
        "rights_locator": "https://example.invalid/rights",
        "rights_status": "research_use_user_responsible",
        "identity_status": "resolved",
        "manifest_sha256": MANIFEST_HASH,
        "asset_mapping_sha256": None,
        "page_mapping_sha256": None,
        "lineage_sha256": None,
        "control_group": "croatian_glagolitic_medical",
    }
    values.update(overrides)
    return SourceRecord(**values)


def _term(**overrides: object) -> TerminologyRecord:
    values: dict[str, object] = {
        "term_id": "term-1",
        "ocr_id": "ocr-1",
        "observed_form": "ulie",
        "expanded_form": "ulie",
        "normalized_historical_form": "ulje",
        "reconstructed_form": None,
        "latin_parallel": "oleum",
        "modern_croatian": "ulje",
        "literal_english": "oil",
        "fluent_english": "oil",
        "source_id": "primary-witness",
        "witness_date_kind": "writing",
        "witness_date_start": 1450,
        "witness_date_end": 1450,
        "witness_language": "Croatian",
        "witness_script": "Croatian Glagolitic",
        "witness_domain": "medicine",
        "passage_locator": "folio 1r, line 3",
        "stable_locator": "https://example.invalid/primary-witness",
        "source_sha256": MANIFEST_HASH,
        "passage_asset_id": "primary-witness:folio-1r",
        "passage_asset_sha256": ASSET_HASH,
        "passage_image_id": "primary-witness:folio-1r:image",
        "passage_image_sha256": IMAGE_HASH,
        "diplomatic_passage": "... ulie ...",
        "reviewer_id": "reviewer-1",
        "adjudicator_id": "adjudicator-1",
        "review_state": "approved",
        "alternatives": (),
        "confidence": 0.85,
        "confidence_basis": "independent_image_aligned_review",
        "speculation": False,
    }
    values.update(overrides)
    return TerminologyRecord(**values)


def _receipt(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        **payload,
        "receipt_sha256": sha256(canonical_json(payload).encode("utf-8")).hexdigest(),
    }


def _authority(
    source: SourceRecord | None = None, term: TerminologyRecord | None = None
) -> dict[str, Any]:
    source = source or _source()
    term = term or _term()
    diplomatic_hash = sha256((term.diplomatic_passage or "").encode("utf-8")).hexdigest()
    source_row = _receipt(asdict(source))
    asset = _receipt(
        {
            "passage_asset_id": term.passage_asset_id,
            "source_id": term.source_id,
            "source_sha256": term.source_sha256,
            "sha256": term.passage_asset_sha256,
            "stable_locator": term.stable_locator,
            "passage_locator": term.passage_locator,
        }
    )
    image = _receipt(
        {
            "passage_image_id": term.passage_image_id,
            "source_id": term.source_id,
            "passage_asset_id": term.passage_asset_id,
            "passage_asset_sha256": term.passage_asset_sha256,
            "sha256": term.passage_image_sha256,
        }
    )
    ocr = _receipt(
        {
            "ocr_id": term.ocr_id,
            "source_id": term.source_id,
            "passage_image_id": term.passage_image_id,
            "passage_image_sha256": term.passage_image_sha256,
            "diplomatic_passage_sha256": diplomatic_hash,
        }
    )
    reviewer = _receipt(
        {
            "identity_id": term.reviewer_id,
            "role": "historical_terminology_reviewer",
            "status": "active",
            "qualified_layers": ["historical_terminology"],
            "qualified_languages": [term.witness_language],
        }
    )
    adjudicator = _receipt(
        {
            "identity_id": term.adjudicator_id,
            "role": "historical_terminology_adjudicator",
            "status": "active",
            "qualified_layers": ["historical_terminology"],
            "qualified_languages": [term.witness_language],
        }
    )
    adjudication = _receipt(
        {
            "term_id": term.term_id,
            "ocr_id": term.ocr_id,
            "source_id": term.source_id,
            "source_sha256": term.source_sha256,
            "passage_asset_id": term.passage_asset_id,
            "passage_asset_sha256": term.passage_asset_sha256,
            "passage_image_id": term.passage_image_id,
            "passage_image_sha256": term.passage_image_sha256,
            "diplomatic_passage_sha256": diplomatic_hash,
            "reviewer_id": term.reviewer_id,
            "adjudicator_id": term.adjudicator_id,
            "confidence_basis": term.confidence_basis,
            "status": "approved",
        }
    )
    return _receipt(
        {
            "schema": AUTHORITY_SCHEMA,
            "schema_version": "1.0.0",
            "sources": {source.source_id: source_row},
            "passage_assets": {str(term.passage_asset_id): asset},
            "passage_images": {str(term.passage_image_id): image},
            "ocr_records": {term.ocr_id: ocr},
            "reviewers": {str(term.reviewer_id): reviewer},
            "adjudicators": {str(term.adjudicator_id): adjudicator},
            "adjudications": {term.term_id: adjudication},
        }
    )


def test_material_date_cannot_satisfy_dated_manuscript_hand_role() -> None:
    source = _source(
        date_kind="material",
        date_basis="radiocarbon analysis of parchment",
        dating_certainty="scientific_range",
        material_date_start=1404,
        material_date_end=1438,
        writing_date_start=None,
        writing_date_end=None,
        evidentiary_role="dated_script_control",
    )

    report = validate_sources([source])

    assert report.ok is False
    assert "ROLE_WRITING_OR_COPY_DATE_REQUIRED" in {issue.code for issue in report.errors}


def test_radiocarbon_basis_cannot_be_labelled_as_writing_date() -> None:
    source = _source(
        date_kind="writing",
        date_basis="radiocarbon analysis of parchment",
        material_date_start=1404,
        material_date_end=1438,
        writing_date_start=None,
        writing_date_end=None,
    )

    report = validate_sources([source])
    codes = {issue.code for issue in report.errors}

    assert {"DATE_KIND_RANGE_MISSING", "MATERIAL_DATE_MISCLASSIFIED"} <= codes


def test_source_date_ranges_must_be_complete_and_ordered() -> None:
    source = _source(copy_date_start=1470, copy_date_end=1450)

    report = validate_sources([source])

    assert "COPY_DATE_RANGE_REVERSED" in {issue.code for issue in report.errors}


def test_unknown_training_disposition_including_candidate_fails() -> None:
    report = validate_sources([_source(training_use="train_candidate")])

    assert "TRAINING_DISPOSITION_INVALID" in {issue.code for issue in report.errors}


def test_training_capable_source_requires_all_identity_lineage_checksums() -> None:
    source = _source(
        training_use="train",
        rights_status="public_domain",
        asset_mapping_sha256=None,
        page_mapping_sha256=None,
        lineage_sha256=None,
    )

    report = validate_sources([source])
    codes = {issue.code for issue in report.errors}

    assert {
        "ASSET_MAPPING_CHECKSUM_MISSING",
        "PAGE_MAPPING_CHECKSUM_MISSING",
        "LINEAGE_CHECKSUM_MISSING",
        "HAND_BOUNDARY_CHECKSUM_MISSING",
        "LINE_ANNOTATION_CHECKSUM_MISSING",
        "SPLIT_LINEAGE_CHECKSUM_MISSING",
    } <= codes


def test_fully_authorised_training_source_with_complete_lineage_can_pass() -> None:
    source = _source(
        training_use="train",
        rights_status="public_domain",
        asset_mapping_sha256="d" * 64,
        page_mapping_sha256="e" * 64,
        lineage_sha256="f" * 64,
        hand_boundary_sha256="1" * 64,
        line_annotation_sha256="2" * 64,
        split_lineage_sha256="3" * 64,
    )

    assert validate_sources([source]).ok is True


def test_registered_primary_witness_can_support_observed_historical_form() -> None:
    source = _source()

    term = _term()
    report = validate_terminology(term, _authority(source, term))

    assert report.ok is True


def test_registered_critical_edition_can_join_its_underlying_witness_date() -> None:
    source = _source(
        source_type="critical_edition",
        evidentiary_role="critical_edition_terminology_witness",
        date_kind="publication",
        date_basis="critical edition publication with identified manuscript witness",
        writing_date_start=None,
        writing_date_end=None,
        copy_date_start=1450,
        copy_date_end=1450,
        publication_date_start=2020,
        publication_date_end=2020,
    )
    term = _term(witness_date_kind="copy")

    assert validate_sources([source]).ok is True
    assert validate_terminology(term, _authority(source, term)).ok is True


def test_modern_secondary_source_cannot_be_only_observed_form_witness() -> None:
    source = _source(
        source_type="scholarly_article",
        evidentiary_role="secondary_terminology_control",
        date_kind="publication",
        date_basis="journal publication record",
        writing_date_start=None,
        writing_date_end=None,
        publication_date_start=2024,
        publication_date_end=2024,
        language="modern Croatian",
        script="Latin",
    )
    term = _term(
        witness_date_kind="publication",
        witness_date_start=2024,
        witness_date_end=2024,
        witness_language="modern Croatian",
        witness_script="Latin",
    )

    report = validate_terminology(term, _authority(source, term))

    assert "OBSERVED_FORM_SOURCE_NOT_PRIMARY_OR_CRITICAL" in report.codes


def test_observed_form_requires_exact_asset_image_review_and_confidence_evidence() -> None:
    source = _source()
    term = _term(
        source_sha256="not-a-hash",
        passage_asset_id=None,
        passage_asset_sha256=None,
        passage_image_id=None,
        passage_image_sha256=None,
        diplomatic_passage=None,
        reviewer_id=None,
        adjudicator_id=None,
        review_state="unreviewed",
        confidence_basis=None,
    )

    report = validate_terminology(term, _authority(source, _term()))

    assert {
        "SOURCE_CHECKSUM_INVALID",
        "PASSAGE_ASSET_ID_MISSING",
        "PASSAGE_ASSET_CHECKSUM_MISSING",
        "PASSAGE_IMAGE_ID_MISSING",
        "PASSAGE_IMAGE_CHECKSUM_MISSING",
        "DIPLOMATIC_PASSAGE_MISSING",
        "REVIEWER_MISSING",
        "ADJUDICATOR_MISSING",
        "REVIEW_NOT_APPROVED",
        "CONFIDENCE_BASIS_MISSING",
    } <= set(report.codes)


def test_adjudicator_must_be_independent_and_registered_hash_must_match() -> None:
    source = _source()
    term = _term(source_sha256="d" * 64, adjudicator_id="reviewer-1")

    report = validate_terminology(term, _authority(source, _term()))

    assert {"SOURCE_CHECKSUM_MISMATCH", "ADJUDICATOR_NOT_INDEPENDENT"} <= set(
        report.codes
    )


def test_adjudicator_identity_comparison_is_case_and_whitespace_insensitive() -> None:
    report = validate_terminology(
        _term(reviewer_id=" Reviewer-1 ", adjudicator_id="reviewer-1"),
        _authority(),
    )

    assert "ADJUDICATOR_NOT_INDEPENDENT" in report.codes


def test_source_mapping_key_cannot_hide_mismatched_record_identity() -> None:
    authority = _authority()
    authority["sources"]["different-source"] = authority["sources"].pop(
        "primary-witness"
    )
    authority = _receipt(
        {key: value for key, value in authority.items() if key != "receipt_sha256"}
    )
    report = validate_terminology(_term(), authority)

    assert "SOURCE_AUTHORITY_MISSING" in report.codes


def test_source_authority_key_cannot_hide_mismatched_record_identity() -> None:
    authority = _authority()
    row = authority["sources"]["primary-witness"]
    payload = {key: value for key, value in row.items() if key != "receipt_sha256"}
    payload["source_id"] = "different-source"
    authority["sources"]["primary-witness"] = _receipt(payload)
    authority = _receipt(
        {key: value for key, value in authority.items() if key != "receipt_sha256"}
    )

    report = validate_terminology(_term(), authority)

    assert "SOURCE_AUTHORITY_LINK_MISMATCH" in report.codes


def test_invalid_registered_source_cannot_support_historical_observation() -> None:
    source = _source(training_use="train_candidate")
    report = validate_terminology(_term(), _authority(source, _term()))

    assert "REGISTERED_SOURCE_INVALID" in report.codes


def test_terminology_fails_without_self_hashing_evidence_authority() -> None:
    assert "EVIDENCE_AUTHORITY_MISSING" in validate_terminology(_term()).codes

    authority = _authority()
    authority["schema_version"] = "tampered"
    assert "EVIDENCE_AUTHORITY_RECEIPT_INVALID" in validate_terminology(
        _term(), authority
    ).codes


def test_diplomatic_passage_must_join_the_registered_ocr_hash() -> None:
    term = _term(diplomatic_passage="... ulie ... altered")

    report = validate_terminology(term, _authority())

    assert "OCR_DIPLOMATIC_AUTHORITY_LINK_MISMATCH" in report.codes


def test_confidence_basis_is_a_closed_evidentiary_enum() -> None:
    term = _term(confidence_basis="sounds convincing")

    report = validate_terminology(term, _authority())

    assert "CONFIDENCE_BASIS_INVALID" in report.codes


def test_boolean_is_not_a_historical_confidence_score() -> None:
    report = validate_terminology(_term(confidence=True), _authority())

    assert "CONFIDENCE_OUT_OF_RANGE" in report.codes


def test_real_mavrov_source_cannot_authorise_invented_passage_evidence() -> None:
    payload = json.loads(
        Path("data/image_native/source_register.json").read_text(encoding="utf-8")
    )
    source = SourceRecord(
        **next(row for row in payload["sources"] if row["source_id"] == "nsk-mavrov-r7822")
    )
    term = _term(
        source_id=source.source_id,
        stable_locator=source.stable_locator,
        source_sha256=source.manifest_sha256,
        witness_date_kind="writing",
        witness_date_start=source.writing_date_start,
        witness_date_end=source.writing_date_end,
        witness_language=source.language,
        witness_script=source.script,
        passage_asset_id="invented:mavrov:folio",
        passage_asset_sha256="d" * 64,
        passage_image_id="invented:mavrov:image",
        passage_image_sha256="e" * 64,
    )
    authority = _receipt(
        {
            "schema": AUTHORITY_SCHEMA,
            "schema_version": "1.0.0",
            "sources": {source.source_id: _receipt(asdict(source))},
            "passage_assets": {},
            "passage_images": {},
            "ocr_records": {},
            "reviewers": {},
            "adjudicators": {},
            "adjudications": {},
        }
    )

    report = validate_terminology(term, authority)

    assert report.ok is False
    assert {
        "PASSAGE_ASSET_AUTHORITY_MISSING",
        "PASSAGE_IMAGE_AUTHORITY_MISSING",
        "OCR_AUTHORITY_MISSING",
        "REVIEWER_AUTHORITY_MISSING",
        "ADJUDICATOR_AUTHORITY_MISSING",
        "ADJUDICATION_AUTHORITY_MISSING",
    } <= set(report.codes)
