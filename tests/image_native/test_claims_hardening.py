"""Publication claims require complete, self hashing receipts."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from zfd_image_native.claims import (
    CANONICAL_VOYNICH_PAGE_IDENTITY_SHA256,
    validate_claims,
)
from zfd_image_native.io import canonical_json, read_json, read_jsonl


ROOT = Path(__file__).resolve().parents[2]


def _receipt(**fields: object) -> dict[str, object]:
    payload = dict(fields)
    return {
        **payload,
        "receipt_sha256": sha256(canonical_json(payload).encode("utf-8")).hexdigest(),
    }


def test_minimal_self_hashed_rows_cannot_authorize_complete_translation() -> None:
    ledger = {
        "complete_translation": {
            "status": "supported",
            "required_receipts": ["page_translation_parity"],
        }
    }
    rows = [
        _receipt(
            page_id=f"page-{page}",
            region_id=f"region-{page}",
            confirmed_translated=True,
            review_state="approved",
        )
        for page in range(1, 211)
    ]
    receipt = _receipt(
        schema="zfd.claim_receipt.v1",
        receipt_type="page_translation_parity",
        issuer="zfd_image_native",
        records_sha256=sha256(canonical_json(rows).encode("utf-8")).hexdigest(),
        status="complete",
        confirmed_translated_pages=210,
        total_pages=210,
        confirmed_translated_regions=210,
        total_regions=210,
        unresolved_pages=0,
        unresolved_regions=0,
        review_state="approved",
    )

    decision = validate_claims(
        ledger,
        {"page_translation_parity": receipt},
        {"page_translation_parity": {"records": rows}},
    ).claim("complete_translation")

    assert decision.allowed is False
    assert (
        "RECEIPT_page_translation_parity:AUTHORITY_SCHEMA_INVALID"
        in decision.blocking_reasons
    )
    assert (
        "RECEIPT_page_translation_parity:TRUSTED_AUTHORITY_HASH_MISSING"
        in decision.blocking_reasons
    )
    assert (
        "RECEIPT_page_translation_parity:PAGE_MANIFEST_MISSING"
        in decision.blocking_reasons
    )


def test_claim_validator_traverses_full_parity_chain_and_canonical_scope() -> None:
    page_id = "yale-ms-408:iiif:1006076"
    page = _receipt(
        schema="zfd.canonical_page_authority.v1",
        page_id=page_id,
        source_id="yale-ms-408",
        iiif_id="1006076",
        iiif_base_uri="https://collections.library.yale.edu/iiif/2/1006076",
        image_sha256="a" * 64,
        page_layer_receipt_sha256="b" * 64,
    )
    region = _receipt(
        schema="zfd.canonical_region_authority.v1",
        page_id=page_id,
        region_id="region-1",
        image_sha256="a" * 64,
        geometry_sha256="c" * 64,
        page_manifest_receipt_sha256=page["receipt_sha256"],
        region_layer_receipt_sha256="d" * 64,
    )
    parity_record = _receipt(
        schema="zfd.translation_parity_record.v1",
        page_id=page_id,
        region_id="region-1",
        page_manifest_receipt_sha256=page["receipt_sha256"],
        region_manifest_receipt_sha256=region["receipt_sha256"],
        layers={},
        confirmed_translated=True,
        reason_codes=[],
        review_state="approved",
    )
    disposition = _receipt(
        schema="zfd.page_translation_disposition.v1",
        page_id=page_id,
        page_manifest_receipt_sha256=page["receipt_sha256"],
        region_ids=["region-1"],
        confirmed_translated=True,
        disposition="translated",
        review_state="approved",
        exclusion_reason=None,
    )
    evidence_authority = _receipt(
        schema="zfd.parity_evidence_authority.v1",
        layers={},
        sources={},
        reviewers={},
        unknown_rejection={},
        adjudications={},
    )
    page_manifest = [page]
    region_manifest = [region]
    records = [parity_record]
    page_dispositions = [disposition]
    authority = _receipt(
        schema="zfd.claim_parity_authority.v1",
        page_manifest=page_manifest,
        page_manifest_sha256=sha256(canonical_json(page_manifest).encode("utf-8")).hexdigest(),
        region_manifest=region_manifest,
        region_manifest_sha256=sha256(canonical_json(region_manifest).encode("utf-8")).hexdigest(),
        records=records,
        records_sha256=sha256(canonical_json(records).encode("utf-8")).hexdigest(),
        page_dispositions=page_dispositions,
        page_dispositions_sha256=sha256(
            canonical_json(page_dispositions).encode("utf-8")
        ).hexdigest(),
        evidence_authority=evidence_authority,
        evidence_authority_receipt_sha256=evidence_authority["receipt_sha256"],
    )
    ledger = {
        "complete_translation": {
            "status": "supported",
            "required_receipts": ["page_translation_parity"],
            "authority_receipt_sha256": authority["receipt_sha256"],
            "canonical_page_manifest_sha256": authority["page_manifest_sha256"],
            "canonical_region_manifest_sha256": authority["region_manifest_sha256"],
            "expected_total_pages": 1,
            "expected_total_regions": 1,
        }
    }
    receipt = _receipt(
        schema="zfd.claim_receipt.v1",
        receipt_type="page_translation_parity",
        issuer="zfd_image_native",
        authority_receipt_sha256=authority["receipt_sha256"],
        page_manifest_sha256=authority["page_manifest_sha256"],
        region_manifest_sha256=authority["region_manifest_sha256"],
        page_dispositions_sha256=authority["page_dispositions_sha256"],
        records_sha256=authority["records_sha256"],
        evidence_authority_receipt_sha256=evidence_authority["receipt_sha256"],
        status="complete",
        confirmed_translated_pages=1,
        total_pages=1,
        confirmed_translated_regions=1,
        total_regions=1,
        unresolved_pages=0,
        unresolved_regions=0,
        review_state="approved",
    )

    decision = validate_claims(
        ledger,
        {"page_translation_parity": receipt},
        {"page_translation_parity": authority},
    ).claim("complete_translation")

    assert decision.allowed is False
    assert (
        "RECEIPT_page_translation_parity:CANONICAL_PAGE_SCOPE_NOT_210"
        in decision.blocking_reasons
    )
    assert (
        "RECEIPT_page_translation_parity:CANONICAL_RECORD_PARITY_RESULT_MISMATCH"
        in decision.blocking_reasons
    )
    assert (
        "RECEIPT_page_translation_parity:CANONICAL_RECORD_PARITY_REASONS_MISMATCH"
        in decision.blocking_reasons
    )


def test_self_hashed_parity_counter_without_canonical_rows_is_blocked() -> None:
    ledger = {
        "complete_translation": {
            "status": "supported",
            "required_receipts": ["page_translation_parity"],
        }
    }
    receipt = _receipt(
        schema="zfd.claim_receipt.v1",
        receipt_type="page_translation_parity",
        issuer="zfd_image_native",
        records_sha256="a" * 64,
        status="complete",
        confirmed_translated_pages=210,
        total_pages=210,
        confirmed_translated_regions=337,
        total_regions=337,
        unresolved_pages=0,
        unresolved_regions=0,
        review_state="approved",
    )

    decision = validate_claims(ledger, {"page_translation_parity": receipt}).claim(
        "complete_translation"
    )

    assert decision.allowed is False
    assert "RECEIPT_page_translation_parity:AUTHORITY_MISSING" in decision.blocking_reasons


def test_boolean_or_tampered_receipt_cannot_authorize_claim() -> None:
    ledger = {
        "claim": {"status": "supported", "required_receipts": ["evidence"]}
    }
    decision = validate_claims(ledger, {"evidence": True}).claim("claim")
    assert decision.allowed is False
    assert "RECEIPT_evidence:UNSTRUCTURED" in decision.blocking_reasons

    tampered = _receipt(status="approved", ok=True)
    tampered["stale"] = True
    decision = validate_claims(ledger, {"evidence": tampered}).claim("claim")
    assert decision.allowed is False
    assert "RECEIPT_evidence:SELF_HASH_INVALID" in decision.blocking_reasons
    assert "RECEIPT_evidence:STALE" in decision.blocking_reasons


def test_metric_receipt_needs_measured_nonempty_adjudicated_gold() -> None:
    ledger = {
        "ocr_accuracy": {
            "status": "supported",
            "required_receipts": ["held_out_gold_metrics"],
        }
    }
    empty = _receipt(
        status="not_measured",
        reference_characters=0,
        adjudicated_gold_count=0,
        accuracy_claim_allowed=False,
    )

    decision = validate_claims(ledger, {"held_out_gold_metrics": empty}).claim(
        "ocr_accuracy"
    )

    assert decision.allowed is False
    assert "RECEIPT_held_out_gold_metrics:METRICS_NOT_MEASURED" in decision.blocking_reasons
    assert "RECEIPT_held_out_gold_metrics:ADJUDICATED_GOLD_EMPTY" in decision.blocking_reasons


def test_candidate_status_and_empty_receipt_scope_fail_closed() -> None:
    ledger = {"claim": {"required_receipts": []}}
    decision = validate_claims(ledger, {}).claim("claim")
    assert decision.allowed is False
    assert "CLAIM_REQUIRED_RECEIPTS_MALFORMED" in decision.blocking_reasons


def test_none_required_receipts_fails_closed_without_type_error() -> None:
    decision = validate_claims(
        {"claim": {"status": "supported", "required_receipts": None}},
        {},
    ).claim("claim")

    assert decision.allowed is False
    assert decision.blocking_reasons == ("CLAIM_REQUIRED_RECEIPTS_MALFORMED",)


def test_parity_shaped_receipt_cannot_alias_expert_adjudication() -> None:
    receipt = _receipt(
        schema="zfd.claim_receipt.v1",
        receipt_type="expert_adjudication",
        issuer="zfd_image_native",
        status="complete",
        confirmed_translated_pages=210,
        excluded_nontext_pages=0,
        total_pages=210,
        confirmed_translated_regions=1,
        total_regions=1,
        unresolved_pages=0,
        unresolved_regions=0,
        review_state="approved",
    )
    decision = validate_claims(
        {
            "complete_translation": {
                "status": "supported",
                "required_receipts": ["expert_adjudication"],
            }
        },
        {"expert_adjudication": receipt},
        {"expert_adjudication": {}},
    ).claim("complete_translation")

    assert decision.allowed is False
    assert (
        "RECEIPT_expert_adjudication:AUTHORITY_VALIDATOR_UNSUPPORTED"
        in decision.blocking_reasons
    )


def test_code_pinned_yale_page_identity_matches_the_retained_210_surface_manifest() -> None:
    rows = read_jsonl(ROOT / "data" / "image_native" / "voynich_pages.jsonl")
    identity = sorted(
        (
            {
                "page_id": row["page_id"],
                "source_id": row["source_id"],
                "iiif_id": row["iiif_id"],
                "iiif_base_uri": row["iiif_base_uri"],
            }
            for row in rows
        ),
        key=lambda row: row["page_id"],
    )

    assert len(identity) == 210
    assert sha256(canonical_json(identity).encode("utf-8")).hexdigest() == (
        CANONICAL_VOYNICH_PAGE_IDENTITY_SHA256
    )


def test_209_self_declared_nontext_pages_cannot_complete_the_manuscript() -> None:
    source_rows = read_jsonl(ROOT / "data" / "image_native" / "voynich_pages.jsonl")
    pages = [
        _receipt(
            schema="zfd.canonical_page_authority.v1",
            page_id=row["page_id"],
            source_id=row["source_id"],
            iiif_id=row["iiif_id"],
            iiif_base_uri=row["iiif_base_uri"],
            image_sha256=row["image_sha256"],
            page_layer_receipt_sha256=sha256(row["page_id"].encode("utf-8")).hexdigest(),
        )
        for row in source_rows
    ]
    first = pages[0]
    region = _receipt(
        schema="zfd.canonical_region_authority.v1",
        page_id=first["page_id"],
        region_id="region-1",
        image_sha256=first["image_sha256"],
        geometry_sha256="c" * 64,
        page_manifest_receipt_sha256=first["receipt_sha256"],
        region_layer_receipt_sha256="d" * 64,
    )
    records = [
        _receipt(
            schema="zfd.translation_parity_record.v1",
            page_id=first["page_id"],
            region_id="region-1",
            page_manifest_receipt_sha256=first["receipt_sha256"],
            region_manifest_receipt_sha256=region["receipt_sha256"],
            layers={},
            confirmed_translated=True,
            reason_codes=[],
            review_state="approved",
        )
    ]
    dispositions = [
        _receipt(
            schema="zfd.page_translation_disposition.v1",
            page_id=page["page_id"],
            page_manifest_receipt_sha256=page["receipt_sha256"],
            region_ids=["region-1"] if index == 0 else [],
            confirmed_translated=True,
            excluded_nontext=False,
            disposition="translated" if index == 0 else "excluded_nontext",
            review_state="adjudicated",
            exclusion_reason=None if index == 0 else "self asserted blank",
        )
        for index, page in enumerate(pages)
    ]
    evidence_authority = _receipt(
        schema="zfd.parity_evidence_authority.v1",
        layers={},
        sources={},
        reviewers={},
        unknown_rejection={},
        adjudications={},
    )
    page_hash = sha256(canonical_json(pages).encode("utf-8")).hexdigest()
    region_hash = sha256(canonical_json([region]).encode("utf-8")).hexdigest()
    records_hash = sha256(canonical_json(records).encode("utf-8")).hexdigest()
    dispositions_hash = sha256(canonical_json(dispositions).encode("utf-8")).hexdigest()
    authority = _receipt(
        schema="zfd.claim_parity_authority.v1",
        page_manifest=pages,
        page_manifest_sha256=page_hash,
        region_manifest=[region],
        region_manifest_sha256=region_hash,
        records=records,
        records_sha256=records_hash,
        page_dispositions=dispositions,
        page_dispositions_sha256=dispositions_hash,
        evidence_authority=evidence_authority,
        evidence_authority_receipt_sha256=evidence_authority["receipt_sha256"],
    )
    receipt = _receipt(
        schema="zfd.claim_receipt.v1",
        receipt_type="page_translation_parity",
        issuer="zfd_image_native",
        authority_receipt_sha256=authority["receipt_sha256"],
        page_manifest_sha256=page_hash,
        region_manifest_sha256=region_hash,
        page_dispositions_sha256=dispositions_hash,
        records_sha256=records_hash,
        evidence_authority_receipt_sha256=evidence_authority["receipt_sha256"],
        status="complete",
        confirmed_translated_pages=210,
        excluded_nontext_pages=0,
        total_pages=210,
        confirmed_translated_regions=1,
        total_regions=1,
        unresolved_pages=0,
        unresolved_regions=0,
        review_state="approved",
    )
    ledger = {
        "complete_translation": {
            "status": "supported",
            "required_receipts": ["page_translation_parity"],
            "authority_receipt_sha256": authority["receipt_sha256"],
            "canonical_page_manifest_sha256": page_hash,
            "canonical_region_manifest_sha256": region_hash,
            "expected_total_pages": 210,
            "expected_total_regions": 1,
        }
    }

    decision = validate_claims(
        ledger,
        {"page_translation_parity": receipt},
        {"page_translation_parity": authority},
    ).claim("complete_translation")

    assert decision.allowed is False
    assert (
        "RECEIPT_page_translation_parity:CANONICAL_PAGE_LAYER_AUTHORITY_MISMATCH"
        in decision.blocking_reasons
    )
    assert (
        "RECEIPT_page_translation_parity:NON_TEXT_PAGE_DISPOSITION_INVALID"
        in decision.blocking_reasons
    )
    assert (
        "RECEIPT_page_translation_parity:NON_TEXT_PAGE_REVIEW_AUTHORITY_INVALID"
        in decision.blocking_reasons
    )


def test_claim_ledger_covers_every_publication_inference_layer() -> None:
    ledger = read_json(ROOT / "data" / "image_native" / "claim_ledger.json")
    expected = {
        "image_native_segmentation",
        "ocr_accuracy",
        "script_identification",
        "historical_language_identification",
        "genre_identification",
        "manuscript_date",
        "palaeographic_match",
        "historical_terminology_resolution",
        "complete_translation",
        "corpus_pixel_translation_parity",
        "geographic_provenance",
        "institutional_provenance",
        "ragusan_provenance",
    }
    assert expected <= (set(ledger) - {"schema_version"})
    assert all(ledger[name]["status"] == "blocked" for name in expected)
