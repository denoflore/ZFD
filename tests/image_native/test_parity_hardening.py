"""Pixel to translation parity is an immutable, reviewed record chain."""

from __future__ import annotations

from hashlib import sha256

from zfd_image_native.io import canonical_json
from zfd_image_native.parity import validate_page_parity


def _seal(payload: dict[str, object]) -> dict[str, object]:
    return {
        **payload,
        "receipt_sha256": sha256(canonical_json(payload).encode("utf-8")).hexdigest(),
    }


def _complete_fixture() -> tuple[dict[str, dict[str, object]], dict[str, object]]:
    page_id = "yale-ms-408:iiif:1006076"
    image_hash = "a" * 64
    region_id = "region-1"
    ocr_id = "ocr-1"
    geometry = [[10, 20], [30, 20], [30, 40], [10, 40]]
    geometry_hash = sha256(canonical_json(geometry).encode("utf-8")).hexdigest()
    shared = {"page_id": page_id, "image_sha256": image_hash}

    page_source = _seal(
        {
            "schema": "zfd.parity_source_authority.v1",
            "source_id": "yale-ms-408",
            "source_type": "target_manuscript",
            "asset_sha256": image_hash,
            "stable_locator": "https://collections.library.yale.edu/catalog/2002046",
        }
    )
    term_source = _seal(
        {
            "schema": "zfd.parity_source_authority.v1",
            "source_id": "gams-zrcalo-1445",
            "source_type": "primary_manuscript_witness",
            "asset_sha256": "b" * 64,
            "stable_locator": "https://gams.uni-graz.at/o:speculum.01",
        }
    )
    reviewer = _seal(
        {
            "schema": "zfd.parity_reviewer_authority.v1",
            "reviewer_id": "reviewer-1",
            "role": "reviewer",
            "status": "active",
            "qualified_layers": ["diplomatic", "normalised", "terminology", "translation"],
        }
    )
    adjudicator = _seal(
        {
            "schema": "zfd.parity_reviewer_authority.v1",
            "reviewer_id": "adjudicator-1",
            "role": "adjudicator",
            "status": "active",
            "qualified_layers": ["diplomatic", "normalised", "terminology", "translation"],
        }
    )
    page = _seal(
        {
            "schema": "zfd.parity_page.v1",
            **shared,
            "source_id": "yale-ms-408",
            "source_receipt_sha256": page_source["receipt_sha256"],
        }
    )
    region = _seal(
        {
            "schema": "zfd.parity_region.v1",
            **shared,
            "region_id": region_id,
            "geometry": geometry,
            "geometry_sha256": geometry_hash,
            "page_receipt_sha256": page["receipt_sha256"],
        }
    )
    rejection = _seal(
        {
            "schema": "zfd.parity_unknown_rejection.v1",
            **shared,
            "region_id": region_id,
            "ocr_id": ocr_id,
            "candidate_count": 1,
            "recognized_count": 1,
            "unknown_count": 0,
            "rejected_count": 0,
            "candidate_ids": ["grapheme-1"],
            "recognized_grapheme_ids": ["grapheme-1"],
            "unknown_grapheme_ids": [],
            "rejected_candidate_ids": [],
            "threshold": 0.8,
            "method": "open_set_threshold",
        }
    )
    ocr = _seal(
        {
            "schema": "zfd.parity_ocr.v1",
            **shared,
            "region_id": region_id,
            "ocr_id": ocr_id,
            "geometry_sha256": geometry_hash,
            "region_receipt_sha256": region["receipt_sha256"],
            "status": "frozen",
            "input_kind": "manuscript_pixels",
            "unknown_rejection": True,
            "unknown_rejection_receipt_id": "unknown-rejection-1",
            "line_ids": ["line-1"],
            "grapheme_ids": ["grapheme-1"],
            "recognized_grapheme_ids": ["grapheme-1"],
            "unknown_grapheme_ids": [],
        }
    )
    diplomatic = _seal(
        {
            "schema": "zfd.parity_diplomatic.v1",
            **shared,
            "region_id": region_id,
            "ocr_id": ocr_id,
            "geometry_sha256": geometry_hash,
            "ocr_receipt_sha256": ocr["receipt_sha256"],
            "text": "observed glyph sequence",
            "line_ids": ["line-1"],
            "grapheme_ids": ["grapheme-1"],
            "grapheme_alignment": [
                {
                    "grapheme_id": "grapheme-1",
                    "label": "observed-glyph-1",
                    "polygon_sha256": "c" * 64,
                }
            ],
            "alternatives": [],
            "state": "resolved",
            "review_state": "adjudicated",
        }
    )
    normalised = _seal(
        {
            "schema": "zfd.parity_normalised.v1",
            **shared,
            "region_id": region_id,
            "ocr_id": ocr_id,
            "geometry_sha256": geometry_hash,
            "diplomatic_receipt_sha256": diplomatic["receipt_sha256"],
            "expanded_text": "expanded reading",
            "normalised_historical_text": "historical form",
            "line_ids": ["line-1"],
            "review_state": "adjudicated",
        }
    )
    terminology = _seal(
        {
            "schema": "zfd.parity_terminology.v1",
            **shared,
            "region_id": region_id,
            "ocr_id": ocr_id,
            "geometry_sha256": geometry_hash,
            "normalised_receipt_sha256": normalised["receipt_sha256"],
            "analysis_id": "analysis-1",
            "status": "resolved",
            "observed_form": "historical form",
            "source_id": "gams-zrcalo-1445",
            "source_receipt_sha256": term_source["receipt_sha256"],
            "source_date_start": 1445,
            "source_date_end": 1445,
            "passage_locator": "folio 1r",
            "stable_locator": "https://gams.uni-graz.at/o:speculum.01",
            "passage_asset_sha256": "b" * 64,
            "passage_image_sha256": "d" * 64,
            "diplomatic_passage": "historical form",
            "witness_language": "Croatian Church Slavonic",
            "witness_script": "Croatian angular Glagolitic",
            "alternatives": [],
            "review_state": "approved",
        }
    )
    translation = _seal(
        {
            "schema": "zfd.parity_translation.v1",
            **shared,
            "region_id": region_id,
            "ocr_id": ocr_id,
            "geometry_sha256": geometry_hash,
            "analysis_id": "analysis-1",
            "terminology_receipt_sha256": terminology["receipt_sha256"],
            "modern_croatian": "suvremeni hrvatski",
            "literal_english": "literal English",
            "fluent_english": "Fluent English.",
            "alternatives": [],
            "confidence": 0.8,
            "confidence_basis": "evidentiary_review",
            "reviewer_id": "reviewer-1",
            "adjudicator_id": "adjudicator-1",
            "adjudication_id": "adjudication-1",
            "status": "resolved",
            "review_state": "approved",
        }
    )
    record = {
        "page": page,
        "region": region,
        "ocr": ocr,
        "diplomatic": diplomatic,
        "normalised": normalised,
        "terminology": terminology,
        "translation": translation,
    }
    adjudication = _seal(
        {
            "schema": "zfd.parity_adjudication.v1",
            "adjudication_id": "adjudication-1",
            "reviewer_id": "reviewer-1",
            "adjudicator_id": "adjudicator-1",
            "status": "approved",
            "layer_receipts": {
                name: layer["receipt_sha256"] for name, layer in record.items()
            },
        }
    )
    authority = _seal(
        {
            "schema": "zfd.parity_evidence_authority.v1",
            "layers": {
                name: {layer["receipt_sha256"]: layer} for name, layer in record.items()
            },
            "sources": {
                "yale-ms-408": page_source,
                "gams-zrcalo-1445": term_source,
            },
            "reviewers": {
                "reviewer-1": reviewer,
                "adjudicator-1": adjudicator,
            },
            "unknown_rejection": {"unknown-rejection-1": rejection},
            "adjudications": {"adjudication-1": adjudication},
        }
    )
    return record, authority


def test_complete_immutable_record_chain_can_be_confirmed() -> None:
    record, authority = _complete_fixture()
    report = validate_page_parity(record, authority)

    assert report.ok is True
    assert report.confirmed_translated == 1
    assert report.unresolved == 0
    assert report.reasons == ()


def test_geometry_tamper_breaks_receipt_and_all_downstream_links() -> None:
    record, authority = _complete_fixture()
    record["region"]["geometry"] = [[0, 0], [1, 0], [1, 1], [0, 1]]

    report = validate_page_parity(record, authority)

    assert report.ok is False
    assert "REGION_RECEIPT_INVALID" in report.reasons
    assert "REGION_GEOMETRY_HASH_MISMATCH" in report.reasons
    assert "OCR_GEOMETRY_LINK_MISMATCH" in report.reasons


def test_absent_normalised_layer_blocks_confirmation() -> None:
    record, authority = _complete_fixture()
    del record["normalised"]

    report = validate_page_parity(record, authority)

    assert report.confirmed_translated == 0
    assert "NORMALISED_MISSING" in report.reasons


def test_self_hashed_chain_without_registered_authority_is_unconfirmed() -> None:
    record, _authority = _complete_fixture()

    report = validate_page_parity(record)

    assert report.confirmed_translated == 0
    assert "EVIDENCE_AUTHORITY_MISSING" in report.reasons


def test_unknown_rejection_must_conserve_every_candidate() -> None:
    record, authority = _complete_fixture()
    rejection = dict(authority["unknown_rejection"]["unknown-rejection-1"])
    rejection.pop("receipt_sha256")
    rejection["rejected_count"] = 1
    authority["unknown_rejection"]["unknown-rejection-1"] = _seal(rejection)
    authority_payload = dict(authority)
    authority_payload.pop("receipt_sha256")
    authority = _seal(authority_payload)

    report = validate_page_parity(record, authority)

    assert report.ok is False
    assert "OCR_UNKNOWN_REJECTION_CONSERVATION_MISMATCH" in report.reasons
    assert "OCR_UNKNOWN_REJECTION_ID_COUNT_MISMATCH" in report.reasons


def test_unsealed_ad_hoc_authority_is_unconfirmed() -> None:
    record, authority = _complete_fixture()
    authority.pop("receipt_sha256")

    report = validate_page_parity(record, authority)

    assert report.ok is False
    assert "EVIDENCE_AUTHORITY_RECEIPT_INVALID" in report.reasons


def test_unknown_only_ocr_cannot_confirm_translation() -> None:
    record, authority = _complete_fixture()
    rejection = dict(authority["unknown_rejection"]["unknown-rejection-1"])
    rejection.pop("receipt_sha256")
    rejection.update(
        {
            "recognized_count": 0,
            "unknown_count": 1,
            "recognized_grapheme_ids": [],
            "unknown_grapheme_ids": ["grapheme-1"],
        }
    )
    authority["unknown_rejection"]["unknown-rejection-1"] = _seal(rejection)
    authority_payload = dict(authority)
    authority_payload.pop("receipt_sha256")
    authority = _seal(authority_payload)

    report = validate_page_parity(record, authority)

    assert report.ok is False
    assert "OCR_UNRESOLVED_UNKNOWN_GRAPHEMES_PRESENT" in report.reasons


def test_malformed_geometry_and_historical_evidence_fail_closed() -> None:
    record, authority = _complete_fixture()
    record["region"]["geometry"] = ["this is not a polygon"]
    record["terminology"].update(
        {
            "source_date_start": "yesterday",
            "source_date_end": {"invented": True},
            "stable_locator": "banana",
            "passage_asset_sha256": "not-a-sha256",
            "passage_image_sha256": "also-not-a-sha256",
        }
    )

    report = validate_page_parity(record, authority)

    assert report.ok is False
    assert {
        "REGION_GEOMETRY_MISSING",
        "TERMINOLOGY_DATE_MISSING",
        "TERMINOLOGY_STABLE_LOCATOR_INVALID",
        "TERMINOLOGY_PASSAGE_ASSET_HASH_INVALID",
        "TERMINOLOGY_PASSAGE_HASH_INVALID",
    } <= set(report.reasons)


def test_json_type_confusion_returns_reasons_without_crashing() -> None:
    record, authority = _complete_fixture()
    record["ocr"]["line_ids"] = [{}]
    reviewer = dict(authority["reviewers"]["reviewer-1"])
    reviewer.pop("receipt_sha256")
    reviewer["qualified_layers"] = [{}]
    authority["reviewers"]["reviewer-1"] = _seal(reviewer)
    authority_payload = dict(authority)
    authority_payload.pop("receipt_sha256")
    authority = _seal(authority_payload)

    report = validate_page_parity(record, authority)
    invalid_record = validate_page_parity([], {})

    assert report.ok is False
    assert "OCR_LINE_IDS_INVALID" in report.reasons
    assert "REVIEWER_AUTHORITY_UNQUALIFIED" in report.reasons
    assert invalid_record.reasons == ("PARITY_RECORD_INVALID",)
