"""Adjudicated grapheme authority must be content bound and leakage resistant."""

from __future__ import annotations

from dataclasses import replace

from zfd_visual_index import (
    GraphemeAuthorityMetadataRecord,
    authority_record_receipt_sha256,
    pixel_occurrence_id,
    validate_grapheme_authority_metadata,
)


def _record(**changes) -> GraphemeAuthorityMetadataRecord:
    row = GraphemeAuthorityMetadataRecord(
        pixel_occurrence_id="pending",
        source_id="zrcalo-1445",
        source_asset_id="sha256:" + "1" * 64,
        source_page_id="zrcalo-1445:1r",
        source_image_sha256="2" * 64,
        source_image_width=1000,
        source_image_height=1500,
        bbox=(100, 200, 30, 40),
        crop_bbox=(98, 198, 34, 44),
        crop_sha256="3" * 64,
        descriptor_sha256="4" * 64,
        descriptor_config_sha256="5" * 64,
        descriptor_aspect_ratio=0.75,
        manuscript_id="zrcalo-1445",
        hand_id="hand-1",
        style="angular-glagolitic",
        split="validation",
        lineage_root_id="zrcalo-1445:1r:line-1:glyph-1",
        rights_status="public_domain",
        source_authority_receipt_sha256="6" * 64,
        diplomatic_label="Ⰰ",
        label_kind="diplomatic_grapheme",
        label_ontology_sha256="7" * 64,
        label_source_lane="human_image_aligned",
        reviewer_id="reviewer-a",
        reviewer_authority_receipt_sha256="8" * 64,
        adjudicator_id="adjudicator-b",
        adjudicator_authority_receipt_sha256="9" * 64,
        review_state="adjudicated",
        adjudication_receipt_sha256="a" * 64,
        record_receipt_sha256="pending",
    )
    row = replace(row, **changes)
    row = replace(row, pixel_occurrence_id=pixel_occurrence_id(row))
    return replace(row, record_receipt_sha256=authority_record_receipt_sha256(row))


def test_valid_metadata_remains_ineligible_without_bound_authority_receipts() -> None:
    report = validate_grapheme_authority_metadata((_record(),))

    assert report.metadata_valid is True
    assert report.authority_usable is False
    assert report.labelled_record_count == 1
    assert report.metadata_eligible_count == 1
    assert report.semantic_authority_count == 0
    assert report.errors == ()


def test_pixel_identity_binds_crop_geometry_descriptor_and_configuration() -> None:
    original = _record()

    for field, value in (
        ("bbox", (101, 200, 30, 40)),
        ("crop_bbox", (97, 198, 34, 44)),
        ("crop_sha256", "b" * 64),
        ("descriptor_sha256", "c" * 64),
        ("descriptor_config_sha256", "d" * 64),
        ("descriptor_aspect_ratio", 0.8),
    ):
        changed = replace(original, **{field: value})
        assert pixel_occurrence_id(changed) != original.pixel_occurrence_id


def test_duplicate_pixels_fail_closed_and_zero_the_registry() -> None:
    row = _record()
    report = validate_grapheme_authority_metadata((row, row))

    assert report.metadata_valid is False
    assert report.authority_usable is False
    assert report.semantic_authority_count == 0
    assert any(error.startswith("PIXEL_OCCURRENCE_ID_DUPLICATE:") for error in report.errors)
    assert any(error.startswith("PIXEL_LOCUS_DUPLICATE:") for error in report.errors)
    assert any(error.startswith("CROP_DUPLICATE:") for error in report.errors)


def test_lineage_image_manuscript_and_scoped_hand_cannot_cross_splits() -> None:
    first = _record(split="train")
    second = _record(
        bbox=(200, 300, 30, 40),
        crop_bbox=(198, 298, 34, 44),
        crop_sha256="b" * 64,
        descriptor_sha256="c" * 64,
        split="validation",
    )
    report = validate_grapheme_authority_metadata((first, second))

    assert report.semantic_authority_count == 0
    assert any(error.startswith("SOURCE_IMAGE_SPLIT_LEAKAGE:") for error in report.errors)
    assert any(error.startswith("LINEAGE_ROOT_SPLIT_LEAKAGE:") for error in report.errors)
    assert any(error.startswith("MANUSCRIPT_SPLIT_LEAKAGE:") for error in report.errors)
    assert any(error.startswith("SCOPED_HAND_SPLIT_LEAKAGE:") for error in report.errors)


def test_source_asset_and_stable_source_page_cannot_cross_splits() -> None:
    first = _record(split="train")
    second = _record(
        source_image_sha256="b" * 64,
        bbox=(200, 300, 30, 40),
        crop_bbox=(198, 298, 34, 44),
        crop_sha256="c" * 64,
        descriptor_sha256="d" * 64,
        manuscript_id="alias-manuscript",
        hand_id="alias-hand",
        lineage_root_id="alias-lineage",
        split="validation",
    )
    report = validate_grapheme_authority_metadata((first, second))

    assert any(error.startswith("SOURCE_ASSET_SPLIT_LEAKAGE:") for error in report.errors)
    assert any(error.startswith("SOURCE_PAGE_SPLIT_LEAKAGE:") for error in report.errors)


def test_descriptor_label_conflict_is_not_semantic_authority() -> None:
    first = _record()
    second = _record(
        source_id="petrisov-1468",
        source_asset_id="sha256:" + "b" * 64,
        source_page_id="petrisov-1468:2r",
        source_image_sha256="c" * 64,
        bbox=(20, 30, 30, 40),
        crop_bbox=(18, 28, 34, 44),
        crop_sha256="d" * 64,
        manuscript_id="petrisov-1468",
        hand_id="hand-2",
        lineage_root_id="petrisov-1468:2r:line-1:glyph-1",
        diplomatic_label="Ⰱ",
    )
    report = validate_grapheme_authority_metadata((first, second))

    assert report.semantic_authority_count == 0
    assert any(error.startswith("DESCRIPTOR_LABEL_CONFLICT:") for error in report.errors)


def test_invalid_rights_review_or_placeholder_label_fails_closed() -> None:
    row = _record(
        rights_status="reference_only",
        diplomatic_label="unknown",
        adjudicator_id="REVIEWER-A",
        review_state="unreviewed",
    )
    report = validate_grapheme_authority_metadata((row,))

    assert report.semantic_authority_count == 0
    assert {
        "TRAINING_RIGHTS_INVALID:" + row.pixel_occurrence_id,
        "DIPLOMATIC_LABEL_PLACEHOLDER:" + row.pixel_occurrence_id,
        "REVIEWER_ADJUDICATOR_NOT_DISTINCT:" + row.pixel_occurrence_id,
        "REVIEW_STATE_INVALID:" + row.pixel_occurrence_id,
    } <= set(report.errors)


def test_malformed_metadata_returns_coded_errors_without_raising() -> None:
    original = _record()
    malformed = replace(
        original,
        source_id=None,
        descriptor_aspect_ratio=[],
        split=[],
    )
    duplicate = replace(malformed, record_receipt_sha256="malformed-duplicate")

    report = validate_grapheme_authority_metadata((malformed, duplicate))

    assert report.metadata_valid is False
    assert any(error.startswith("SOURCE_ID_MISSING:") for error in report.errors)
    assert any(error.startswith("DESCRIPTOR_ASPECT_RATIO_INVALID:") for error in report.errors)
    assert any(error.startswith("TRAINING_SPLIT_INVALID:") for error in report.errors)


def test_authority_report_is_input_order_independent() -> None:
    first = _record()
    second = _record(
        source_id="petrisov-1468",
        source_asset_id="sha256:" + "b" * 64,
        source_page_id="petrisov-1468:2r",
        source_image_sha256="c" * 64,
        bbox=(20, 30, 30, 40),
        crop_bbox=(18, 28, 34, 44),
        crop_sha256="d" * 64,
        descriptor_sha256="e" * 64,
        manuscript_id="petrisov-1468",
        hand_id="hand-2",
        lineage_root_id="petrisov-1468:2r:line-1:glyph-1",
    )

    assert validate_grapheme_authority_metadata((first, second)) == validate_grapheme_authority_metadata(
        (second, first)
    )
