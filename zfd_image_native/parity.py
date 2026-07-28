"""Strict pixel to translation record parity."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import math
import re
from typing import Any, Mapping

from .io import canonical_json


@dataclass(frozen=True)
class ParityReport:
    ok: bool
    confirmed_translated: int
    unresolved: int
    reasons: tuple[str, ...]


LAYERS = ("page", "region", "ocr", "diplomatic", "normalised", "terminology", "translation")
EVIDENCE_AUTHORITY_SCHEMA = "zfd.parity_evidence_authority.v1"
AUTHORITY_BUCKETS = (
    "layers",
    "sources",
    "reviewers",
    "unknown_rejection",
    "adjudications",
)
LAYER_SCHEMAS = {
    "page": "zfd.parity_page.v1",
    "region": "zfd.parity_region.v1",
    "ocr": "zfd.parity_ocr.v1",
    "diplomatic": "zfd.parity_diplomatic.v1",
    "normalised": "zfd.parity_normalised.v1",
    "terminology": "zfd.parity_terminology.v1",
    "translation": "zfd.parity_translation.v1",
}
SOURCE_AUTHORITY_SCHEMA = "zfd.parity_source_authority.v1"
REVIEWER_AUTHORITY_SCHEMA = "zfd.parity_reviewer_authority.v1"
REJECTION_AUTHORITY_SCHEMA = "zfd.parity_unknown_rejection.v1"
ADJUDICATION_AUTHORITY_SCHEMA = "zfd.parity_adjudication.v1"


def _valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _receipt_valid(layer: Mapping[str, Any]) -> bool:
    supplied = layer.get("receipt_sha256")
    if not _valid_sha256(supplied):
        return False
    payload = {key: value for key, value in layer.items() if key != "receipt_sha256"}
    expected = sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    return supplied == expected


def _identity_values(
    layers: Mapping[str, Mapping[str, Any]], names: tuple[str, ...], field: str
) -> tuple[Any, ...]:
    return tuple(layers[name].get(field) for name in names if name in layers)


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_identifier_list(value: Any, *, allow_empty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(isinstance(item, str) and bool(item.strip()) for item in value)
        and len(value) == len(set(value))
    )


def _valid_polygon(value: Any) -> bool:
    if not isinstance(value, (list, tuple)) or len(value) < 4:
        return False
    points: list[tuple[float, float]] = []
    for point in value:
        if not isinstance(point, (list, tuple)) or len(point) != 2:
            return False
        x, y = point
        if (
            not isinstance(x, (int, float))
            or isinstance(x, bool)
            or not isinstance(y, (int, float))
            or isinstance(y, bool)
            or not math.isfinite(float(x))
            or not math.isfinite(float(y))
            or x < 0
            or y < 0
        ):
            return False
        points.append((float(x), float(y)))
    area_twice = sum(
        points[index][0] * points[(index + 1) % len(points)][1]
        - points[(index + 1) % len(points)][0] * points[index][1]
        for index in range(len(points))
    )
    return not math.isclose(area_twice, 0.0)


def _authority_receipt(
    authority: Mapping[str, Any], bucket: str, key: str
) -> Mapping[str, Any] | None:
    records = authority.get(bucket)
    if not isinstance(records, Mapping):
        return None
    value = records.get(key)
    return value if isinstance(value, Mapping) else None


def _authority_reasons(
    layers: Mapping[str, Mapping[str, Any]], authority: Mapping[str, Any]
) -> list[str]:
    reasons: list[str] = []
    if authority.get("schema") != EVIDENCE_AUTHORITY_SCHEMA:
        reasons.append("EVIDENCE_AUTHORITY_SCHEMA_INVALID")
    if not _receipt_valid(authority):
        reasons.append("EVIDENCE_AUTHORITY_RECEIPT_INVALID")
    for bucket_name in AUTHORITY_BUCKETS:
        if not isinstance(authority.get(bucket_name), Mapping):
            reasons.append(f"EVIDENCE_AUTHORITY_{bucket_name.upper()}_MISSING")

    layer_authority = authority.get("layers")
    for layer_name, layer in layers.items():
        receipt_hash = layer.get("receipt_sha256")
        registered = None
        if isinstance(layer_authority, Mapping):
            bucket = layer_authority.get(layer_name)
            if isinstance(bucket, Mapping):
                registered = bucket.get(receipt_hash)
        if registered != layer:
            reasons.append(f"{layer_name.upper()}_AUTHORITY_MISMATCH")

    page = layers.get("page")
    terminology = layers.get("terminology")
    translation = layers.get("translation")
    ocr = layers.get("ocr")
    if page is not None:
        source_id = page.get("source_id")
        source = _authority_receipt(authority, "sources", str(source_id))
        if source is None or not _receipt_valid(source):
            reasons.append("PAGE_SOURCE_AUTHORITY_MISSING")
        else:
            if (
                source.get("schema") != SOURCE_AUTHORITY_SCHEMA
                or source.get("source_id") != source_id
                or source.get("source_type") != "target_manuscript"
                or source.get("asset_sha256") != page.get("image_sha256")
                or not _nonempty_text(source.get("stable_locator"))
            ):
                reasons.append("PAGE_SOURCE_AUTHORITY_INVALID")
            if page.get("source_receipt_sha256") != source.get("receipt_sha256"):
                reasons.append("PAGE_SOURCE_AUTHORITY_MISMATCH")

    if terminology is not None:
        source_id = terminology.get("source_id")
        source = _authority_receipt(authority, "sources", str(source_id))
        if source is None or not _receipt_valid(source):
            reasons.append("TERMINOLOGY_SOURCE_AUTHORITY_MISSING")
        else:
            if (
                source.get("schema") != SOURCE_AUTHORITY_SCHEMA
                or source.get("source_id") != source_id
                or not _nonempty_text(source.get("stable_locator"))
            ):
                reasons.append("TERMINOLOGY_SOURCE_AUTHORITY_INVALID")
            if terminology.get("source_receipt_sha256") != source.get("receipt_sha256"):
                reasons.append("TERMINOLOGY_SOURCE_AUTHORITY_MISMATCH")
            if source.get("source_type") not in {
                "primary_manuscript_witness",
                "primary_print_witness",
                "critical_edition_of_primary_witness",
            }:
                reasons.append("TERMINOLOGY_SOURCE_NOT_PRIMARY")
            if not _valid_sha256(source.get("asset_sha256")):
                reasons.append("TERMINOLOGY_SOURCE_ASSET_HASH_MISSING")
            elif terminology.get("passage_asset_sha256") != source.get("asset_sha256"):
                reasons.append("TERMINOLOGY_SOURCE_ASSET_LINK_MISMATCH")
            if terminology.get("stable_locator") != source.get("stable_locator"):
                reasons.append("TERMINOLOGY_SOURCE_LOCATOR_MISMATCH")

    if ocr is not None:
        rejection_id = ocr.get("unknown_rejection_receipt_id")
        rejection = _authority_receipt(authority, "unknown_rejection", str(rejection_id))
        if rejection is None or not _receipt_valid(rejection):
            reasons.append("OCR_UNKNOWN_REJECTION_AUTHORITY_MISSING")
        else:
            if rejection.get("schema") != REJECTION_AUTHORITY_SCHEMA:
                reasons.append("OCR_UNKNOWN_REJECTION_SCHEMA_INVALID")
            expected = {
                "page_id": ocr.get("page_id"),
                "region_id": ocr.get("region_id"),
                "ocr_id": ocr.get("ocr_id"),
            }
            if any(rejection.get(field) != value for field, value in expected.items()):
                reasons.append("OCR_UNKNOWN_REJECTION_LINK_MISMATCH")
            counts: dict[str, int] = {}
            for field in (
                "candidate_count",
                "recognized_count",
                "unknown_count",
                "rejected_count",
            ):
                value = rejection.get(field)
                if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                    reasons.append("OCR_UNKNOWN_REJECTION_COUNTS_INVALID")
                    break
                counts[field] = value
            if counts.get("candidate_count", 0) <= 0:
                reasons.append("OCR_UNKNOWN_REJECTION_CANDIDATES_EMPTY")

            id_fields = (
                "candidate_ids",
                "recognized_grapheme_ids",
                "unknown_grapheme_ids",
                "rejected_candidate_ids",
            )
            id_sets: dict[str, set[str]] = {}
            for field in id_fields:
                identifiers = rejection.get(field)
                if (
                    not isinstance(identifiers, list)
                    or any(not isinstance(item, str) or not item for item in identifiers)
                    or len(set(identifiers)) != len(identifiers)
                ):
                    reasons.append("OCR_UNKNOWN_REJECTION_IDS_INVALID")
                    continue
                id_sets[field] = set(identifiers)

            if len(counts) == 4:
                if (
                    counts["recognized_count"]
                    + counts["unknown_count"]
                    + counts["rejected_count"]
                    != counts["candidate_count"]
                ):
                    reasons.append("OCR_UNKNOWN_REJECTION_CONSERVATION_MISMATCH")
                if counts["recognized_count"] + counts["unknown_count"] != len(
                    ocr.get("grapheme_ids", [])
                ):
                    reasons.append("OCR_GRAPHEME_COUNT_CONSERVATION_MISMATCH")
                if counts["unknown_count"] > 0:
                    reasons.append("OCR_UNRESOLVED_UNKNOWN_GRAPHEMES_PRESENT")
                if counts["rejected_count"] > 0:
                    reasons.append("OCR_UNADJUDICATED_REJECTED_CANDIDATES_PRESENT")

            if len(id_sets) == len(id_fields):
                recognized_ids = id_sets["recognized_grapheme_ids"]
                unknown_ids = id_sets["unknown_grapheme_ids"]
                rejected_ids = id_sets["rejected_candidate_ids"]
                disposition_ids = recognized_ids | unknown_ids | rejected_ids
                if (
                    recognized_ids & unknown_ids
                    or recognized_ids & rejected_ids
                    or unknown_ids & rejected_ids
                    or disposition_ids != id_sets["candidate_ids"]
                ):
                    reasons.append("OCR_UNKNOWN_REJECTION_PARTITION_INVALID")
                expected_counts = {
                    "candidate_count": len(id_sets["candidate_ids"]),
                    "recognized_count": len(recognized_ids),
                    "unknown_count": len(unknown_ids),
                    "rejected_count": len(rejected_ids),
                }
                if any(counts.get(field) != count for field, count in expected_counts.items()):
                    reasons.append("OCR_UNKNOWN_REJECTION_ID_COUNT_MISMATCH")
                ocr_grapheme_ids = ocr.get("grapheme_ids")
                if not isinstance(ocr_grapheme_ids, list) or set(ocr_grapheme_ids) != (
                    recognized_ids | unknown_ids
                ):
                    reasons.append("OCR_GRAPHEME_DISPOSITION_MISMATCH")
                if ocr.get("recognized_grapheme_ids") != rejection.get(
                    "recognized_grapheme_ids"
                ):
                    reasons.append("OCR_RECOGNIZED_DISPOSITION_LINK_MISMATCH")
                if ocr.get("unknown_grapheme_ids") != rejection.get("unknown_grapheme_ids"):
                    reasons.append("OCR_UNKNOWN_DISPOSITION_LINK_MISMATCH")
            threshold = rejection.get("threshold")
            if (
                not isinstance(threshold, (int, float))
                or isinstance(threshold, bool)
                or not 0 <= threshold <= 1
            ):
                reasons.append("OCR_UNKNOWN_REJECTION_THRESHOLD_INVALID")
            if not rejection.get("method"):
                reasons.append("OCR_UNKNOWN_REJECTION_METHOD_MISSING")

    if translation is not None:
        reviewer_id = translation.get("reviewer_id")
        adjudicator_id = translation.get("adjudicator_id")
        if reviewer_id == adjudicator_id:
            reasons.append("REVIEWER_ADJUDICATOR_NOT_DISTINCT")
        required_layers = {"diplomatic", "normalised", "terminology", "translation"}
        for identity, expected_role, code in (
            (reviewer_id, "reviewer", "REVIEWER_AUTHORITY_MISSING"),
            (adjudicator_id, "adjudicator", "ADJUDICATOR_AUTHORITY_MISSING"),
        ):
            reviewer = _authority_receipt(authority, "reviewers", str(identity))
            if reviewer is None or not _receipt_valid(reviewer):
                reasons.append(code)
                continue
            if (
                reviewer.get("schema") != REVIEWER_AUTHORITY_SCHEMA
                or reviewer.get("reviewer_id") != identity
                or reviewer.get("status") != "active"
                or reviewer.get("role") != expected_role
            ):
                reasons.append(code.replace("MISSING", "INVALID"))
            qualifications = reviewer.get("qualified_layers")
            if (
                not _valid_identifier_list(qualifications)
                or not required_layers <= set(qualifications)
            ):
                reasons.append(code.replace("MISSING", "UNQUALIFIED"))

        adjudication_id = translation.get("adjudication_id")
        adjudication = _authority_receipt(authority, "adjudications", str(adjudication_id))
        if adjudication is None or not _receipt_valid(adjudication):
            reasons.append("ADJUDICATION_AUTHORITY_MISSING")
        else:
            if (
                adjudication.get("schema") != ADJUDICATION_AUTHORITY_SCHEMA
                or adjudication.get("adjudication_id") != adjudication_id
            ):
                reasons.append("ADJUDICATION_AUTHORITY_INVALID")
            expected_links = {
                name: layer.get("receipt_sha256") for name, layer in layers.items()
            }
            if adjudication.get("layer_receipts") != expected_links:
                reasons.append("ADJUDICATION_LAYER_LINK_MISMATCH")
            if adjudication.get("reviewer_id") != reviewer_id:
                reasons.append("ADJUDICATION_REVIEWER_LINK_MISMATCH")
            if adjudication.get("adjudicator_id") != adjudicator_id:
                reasons.append("ADJUDICATION_IDENTITY_LINK_MISMATCH")
            if adjudication.get("status") != "approved":
                reasons.append("ADJUDICATION_NOT_APPROVED")
    return reasons


def validate_page_parity(
    record: Mapping[str, Any], authority: Mapping[str, Any] | None = None
) -> ParityReport:
    reasons: list[str] = []
    if not isinstance(record, Mapping):
        return ParityReport(False, 0, 1, ("PARITY_RECORD_INVALID",))
    if not isinstance(authority, Mapping):
        reasons.append("EVIDENCE_AUTHORITY_MISSING")
    layers: dict[str, Mapping[str, Any]] = {}
    for layer_name in LAYERS:
        value = record.get(layer_name)
        if not isinstance(value, Mapping):
            reasons.append(f"{layer_name.upper()}_MISSING")
        else:
            layers[layer_name] = value
            if not _receipt_valid(value):
                reasons.append(f"{layer_name.upper()}_RECEIPT_INVALID")
            if value.get("schema") != LAYER_SCHEMAS[layer_name]:
                reasons.append(f"{layer_name.upper()}_SCHEMA_INVALID")

    page_ids = _identity_values(layers, LAYERS, "page_id")
    image_hashes = _identity_values(layers, LAYERS, "image_sha256")
    if (
        not page_ids
        or any(not isinstance(value, str) or not value for value in page_ids)
        or len(set(page_ids)) != 1
        or not image_hashes
        or any(not _valid_sha256(value) for value in image_hashes)
        or len(set(image_hashes)) != 1
    ):
        reasons.append("PARENT_IDENTITY_MISMATCH")

    page = layers.get("page")
    region = layers.get("region")
    ocr = layers.get("ocr")
    diplomatic = layers.get("diplomatic")
    normalised = layers.get("normalised")
    terminology = layers.get("terminology")
    translation = layers.get("translation")

    if page is not None:
        if not page.get("source_id"):
            reasons.append("SOURCE_ID_MISSING")
        if not page.get("page_id"):
            reasons.append("PAGE_ID_MISSING")

    region_layer_names = tuple(name for name in LAYERS[1:] if name in layers)
    region_ids = _identity_values(layers, region_layer_names, "region_id")
    if (
        not region_ids
        or any(not isinstance(value, str) or not value for value in region_ids)
        or len(set(region_ids)) != 1
    ):
        reasons.append("REGION_IDENTITY_MISMATCH")
    geometry_hash: str | None = None
    if region is not None:
        geometry = region.get("geometry")
        if not _valid_polygon(geometry):
            reasons.append("REGION_GEOMETRY_MISSING")
        else:
            geometry_hash = sha256(canonical_json(geometry).encode("utf-8")).hexdigest()
            if region.get("geometry_sha256") != geometry_hash:
                reasons.append("REGION_GEOMETRY_HASH_MISMATCH")
        if page is not None and region.get("page_receipt_sha256") != page.get("receipt_sha256"):
            reasons.append("REGION_PAGE_LINK_MISMATCH")

    ocr_layer_names = tuple(
        name for name in ("ocr", "diplomatic", "normalised", "terminology", "translation") if name in layers
    )
    ocr_ids = _identity_values(layers, ocr_layer_names, "ocr_id")
    if (
        not ocr_ids
        or any(not isinstance(value, str) or not value for value in ocr_ids)
        or len(set(ocr_ids)) != 1
    ):
        reasons.append("OCR_IDENTITY_MISMATCH")
    for layer_name in ocr_layer_names:
        layer_geometry_hash = layers[layer_name].get("geometry_sha256")
        if geometry_hash is None or layer_geometry_hash != geometry_hash:
            reasons.append(f"{layer_name.upper()}_GEOMETRY_LINK_MISMATCH")

    if ocr is not None:
        if ocr.get("status") != "frozen":
            reasons.append("OCR_NOT_FROZEN")
        if ocr.get("input_kind") != "manuscript_pixels":
            reasons.append("OCR_INPUT_NOT_PIXELS")
        if region is not None and ocr.get("region_receipt_sha256") != region.get("receipt_sha256"):
            reasons.append("OCR_REGION_LINK_MISMATCH")
        if ocr.get("unknown_rejection") is not True:
            reasons.append("OCR_UNKNOWN_REJECTION_MISSING")
        line_ids = ocr.get("line_ids")
        grapheme_ids = ocr.get("grapheme_ids")
        if not _valid_identifier_list(line_ids):
            reasons.append("OCR_LINE_IDS_INVALID")
        if not _valid_identifier_list(grapheme_ids):
            reasons.append("OCR_GRAPHEME_IDS_INVALID")
        if not ocr.get("unknown_rejection_receipt_id"):
            reasons.append("OCR_UNKNOWN_REJECTION_RECEIPT_MISSING")

    if diplomatic is not None:
        if not _nonempty_text(diplomatic.get("text")):
            reasons.append("DIPLOMATIC_TEXT_MISSING")
        if diplomatic.get("state") != "resolved":
            reasons.append("DIPLOMATIC_UNRESOLVED")
        if diplomatic.get("review_state") != "adjudicated":
            reasons.append("DIPLOMATIC_NOT_ADJUDICATED")
        if ocr is not None and diplomatic.get("ocr_receipt_sha256") != ocr.get("receipt_sha256"):
            reasons.append("DIPLOMATIC_OCR_LINK_MISMATCH")
        if ocr is not None:
            if diplomatic.get("line_ids") != ocr.get("line_ids"):
                reasons.append("DIPLOMATIC_LINE_ALIGNMENT_MISMATCH")
            if diplomatic.get("grapheme_ids") != ocr.get("grapheme_ids"):
                reasons.append("DIPLOMATIC_GRAPHEME_ALIGNMENT_MISMATCH")
        alignments = diplomatic.get("grapheme_alignment")
        if not isinstance(alignments, list) or not alignments:
            reasons.append("DIPLOMATIC_GRAPHEME_ALIGNMENT_MISSING")
        else:
            valid_alignments = all(
                isinstance(row, Mapping)
                and isinstance(row.get("grapheme_id"), str)
                and bool(row.get("grapheme_id"))
                and _nonempty_text(row.get("label"))
                and _valid_sha256(row.get("polygon_sha256"))
                for row in alignments
            )
            aligned_ids = [
                row.get("grapheme_id") for row in alignments if isinstance(row, Mapping)
            ]
            if not valid_alignments or aligned_ids != diplomatic.get("grapheme_ids"):
                reasons.append("DIPLOMATIC_GRAPHEME_ALIGNMENT_MISMATCH")
        if not isinstance(diplomatic.get("alternatives"), list):
            reasons.append("DIPLOMATIC_ALTERNATIVES_MISSING")

    if normalised is not None:
        if not _nonempty_text(normalised.get("expanded_text")):
            reasons.append("EXPANDED_TEXT_MISSING")
        if not _nonempty_text(normalised.get("normalised_historical_text")):
            reasons.append("NORMALISED_HISTORICAL_TEXT_MISSING")
        if normalised.get("review_state") != "adjudicated":
            reasons.append("NORMALISED_NOT_ADJUDICATED")
        if diplomatic is not None and normalised.get("line_ids") != diplomatic.get("line_ids"):
            reasons.append("NORMALISED_LINE_ALIGNMENT_MISMATCH")
        if diplomatic is not None and normalised.get("diplomatic_receipt_sha256") != diplomatic.get(
            "receipt_sha256"
        ):
            reasons.append("NORMALISED_DIPLOMATIC_LINK_MISMATCH")

    if terminology is not None:
        if terminology.get("status") != "resolved":
            reasons.append("TERMINOLOGY_UNRESOLVED")
        for field, code in (
            ("observed_form", "TERMINOLOGY_OBSERVED_FORM_MISSING"),
            ("source_id", "TERMINOLOGY_SOURCE_MISSING"),
            ("passage_locator", "TERMINOLOGY_LOCATOR_MISSING"),
            ("stable_locator", "TERMINOLOGY_STABLE_LOCATOR_MISSING"),
        ):
            if not terminology.get(field):
                reasons.append(code)
        for field, code in (
            ("source_receipt_sha256", "TERMINOLOGY_SOURCE_RECEIPT_MISSING"),
            ("passage_asset_sha256", "TERMINOLOGY_PASSAGE_ASSET_HASH_MISSING"),
            ("passage_image_sha256", "TERMINOLOGY_PASSAGE_HASH_MISSING"),
            ("diplomatic_passage", "TERMINOLOGY_DIPLOMATIC_PASSAGE_MISSING"),
            ("witness_language", "TERMINOLOGY_LANGUAGE_MISSING"),
            ("witness_script", "TERMINOLOGY_SCRIPT_MISSING"),
        ):
            if not terminology.get(field):
                reasons.append(code)
        for field, code in (
            ("source_receipt_sha256", "TERMINOLOGY_SOURCE_RECEIPT_INVALID"),
            ("passage_asset_sha256", "TERMINOLOGY_PASSAGE_ASSET_HASH_INVALID"),
            ("passage_image_sha256", "TERMINOLOGY_PASSAGE_HASH_INVALID"),
        ):
            if not _valid_sha256(terminology.get(field)):
                reasons.append(code)
        stable_locator = terminology.get("stable_locator")
        if not isinstance(stable_locator, str) or re.fullmatch(r"https?://\S+", stable_locator) is None:
            reasons.append("TERMINOLOGY_STABLE_LOCATOR_INVALID")
        if not isinstance(terminology.get("alternatives"), list):
            reasons.append("TERMINOLOGY_ALTERNATIVES_MISSING")
        date_start = terminology.get("source_date_start")
        date_end = terminology.get("source_date_end")
        if (
            not isinstance(date_start, int)
            or isinstance(date_start, bool)
            or not isinstance(date_end, int)
            or isinstance(date_end, bool)
            or not 500 <= date_start <= date_end <= 2000
        ):
            reasons.append("TERMINOLOGY_DATE_MISSING")
        if terminology.get("review_state") != "approved":
            reasons.append("TERMINOLOGY_REVIEW_UNAPPROVED")
        if normalised is not None and terminology.get("normalised_receipt_sha256") != normalised.get(
            "receipt_sha256"
        ):
            reasons.append("TERMINOLOGY_NORMALISED_LINK_MISMATCH")

    if terminology is not None and translation is not None:
        if terminology.get("analysis_id") != translation.get("analysis_id"):
            reasons.append("TERMINOLOGY_IDENTITY_MISMATCH")
        if translation.get("terminology_receipt_sha256") != terminology.get("receipt_sha256"):
            reasons.append("TRANSLATION_TERMINOLOGY_LINK_MISMATCH")

    if translation is not None:
        for field, code in (
            ("modern_croatian", "MODERN_CROATIAN_MISSING"),
            ("literal_english", "LITERAL_ENGLISH_MISSING"),
            ("fluent_english", "FLUENT_ENGLISH_MISSING"),
            ("reviewer_id", "REVIEWER_MISSING"),
            ("adjudicator_id", "ADJUDICATION_MISSING"),
        ):
            if not translation.get(field):
                reasons.append(code)
        if translation.get("status") != "resolved":
            reasons.append("TRANSLATION_UNRESOLVED")
        if translation.get("review_state") != "approved":
            reasons.append("REVIEW_NOT_APPROVED")
        alternatives = translation.get("alternatives")
        if not isinstance(alternatives, list):
            reasons.append("TRANSLATION_ALTERNATIVES_MISSING")
        confidence = translation.get("confidence")
        if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= confidence <= 1:
            reasons.append("TRANSLATION_CONFIDENCE_INVALID")
        if translation.get("confidence_basis") != "evidentiary_review":
            reasons.append("TRANSLATION_CONFIDENCE_BASIS_INVALID")
        if not translation.get("adjudication_id"):
            reasons.append("ADJUDICATION_RECEIPT_MISSING")

    if isinstance(authority, Mapping):
        reasons.extend(_authority_reasons(layers, authority))

    unique = tuple(dict.fromkeys(reasons))
    return ParityReport(not unique, int(not unique), int(bool(unique)), unique)
