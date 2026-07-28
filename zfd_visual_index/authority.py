"""Fail closed metadata gate for future image aligned grapheme authority."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from hashlib import sha256
from math import isfinite
import re
import unicodedata
from typing import Any, Iterable

from zfd_image_native.io import canonical_json
from zfd_image_native.sources import TRAINING_RIGHTS_STATUSES


_SHA256 = re.compile(r"[0-9a-f]{64}")
_CONTENT_ID = re.compile(r"sha256:[0-9a-f]{64}")
_PLACEHOLDER_LABELS = frozenset({"unknown", "<unknown>", "?", "unresolved", "none", "null"})


@dataclass(frozen=True)
class GraphemeAuthorityMetadataRecord:
    pixel_occurrence_id: str
    source_id: str
    source_asset_id: str
    source_page_id: str
    source_image_sha256: str
    source_image_width: int
    source_image_height: int
    bbox: tuple[int, int, int, int]
    crop_bbox: tuple[int, int, int, int]
    crop_sha256: str
    descriptor_sha256: str
    descriptor_config_sha256: str
    descriptor_aspect_ratio: float
    manuscript_id: str
    hand_id: str
    style: str
    split: str
    lineage_root_id: str
    rights_status: str
    source_authority_receipt_sha256: str
    diplomatic_label: str | None
    label_kind: str
    label_ontology_sha256: str
    label_source_lane: str
    reviewer_id: str | None
    reviewer_authority_receipt_sha256: str | None
    adjudicator_id: str | None
    adjudicator_authority_receipt_sha256: str | None
    review_state: str
    adjudication_receipt_sha256: str | None
    record_receipt_sha256: str


@dataclass(frozen=True)
class AuthorityMetadataReport:
    metadata_valid: bool
    authority_usable: bool
    record_count: int
    labelled_record_count: int
    metadata_eligible_count: int
    semantic_authority_count: int
    independent_cross_witness_descriptor_groups: int
    errors: tuple[str, ...]


def _value_sha256(value: Any) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None


def _text(value: Any) -> str | None:
    return value if isinstance(value, str) and bool(value.strip()) else None


def _stable_key(value: Any) -> Any:
    if isinstance(value, dict):
        return tuple(sorted((str(key), _stable_key(item)) for key, item in value.items()))
    if isinstance(value, (list, tuple, set, frozenset)):
        return tuple(_stable_key(item) for item in value)
    if isinstance(value, float) and not isfinite(value):
        return repr(value)
    try:
        hash(value)
    except TypeError:
        return repr(value)
    return value


def _key_digest(value: Any) -> str:
    return sha256(repr(_stable_key(value)).encode("utf-8")).hexdigest()


def _box_valid(
    box: tuple[int, int, int, int], width: int, height: int
) -> bool:
    if (
        not isinstance(box, tuple)
        or len(box) != 4
        or any(isinstance(item, bool) or not isinstance(item, int) for item in box)
        or isinstance(width, bool)
        or isinstance(height, bool)
        or not isinstance(width, int)
        or not isinstance(height, int)
        or width <= 0
        or height <= 0
    ):
        return False
    x, y, box_width, box_height = box
    return (
        x >= 0
        and y >= 0
        and box_width > 0
        and box_height > 0
        and x + box_width <= width
        and y + box_height <= height
    )


def _contains(parent: tuple[int, int, int, int], child: tuple[int, int, int, int]) -> bool:
    px, py, pw, ph = parent
    cx, cy, cw, ch = child
    return px <= cx and py <= cy and cx + cw <= px + pw and cy + ch <= py + ph


def pixel_occurrence_id(record: GraphemeAuthorityMetadataRecord) -> str:
    """Content address one padded, described occurrence without semantic metadata."""

    payload = {
        "schema": "zfd.glyph_pixel_occurrence_identity.v1",
        "source_image_sha256": record.source_image_sha256,
        "bbox": list(record.bbox),
        "crop_bbox": list(record.crop_bbox),
        "crop_sha256": record.crop_sha256,
        "descriptor_sha256": record.descriptor_sha256,
        "descriptor_config_sha256": record.descriptor_config_sha256,
        "descriptor_aspect_ratio": record.descriptor_aspect_ratio,
    }
    return "sha256:" + _value_sha256(payload)


def authority_record_receipt_sha256(record: GraphemeAuthorityMetadataRecord) -> str:
    """Bind occurrence identity to all provenance, label, split, and review metadata."""

    payload = asdict(record)
    payload.pop("record_receipt_sha256", None)
    return _value_sha256(payload)


def _group(rows: Iterable[GraphemeAuthorityMetadataRecord], key):
    grouped: dict[Any, list[GraphemeAuthorityMetadataRecord]] = defaultdict(list)
    for row in rows:
        grouped[_stable_key(key(row))].append(row)
    return grouped


def _split_leakage(
    errors: list[str],
    rows: list[GraphemeAuthorityMetadataRecord],
    *,
    key,
    code: str,
) -> None:
    for value, group in _group(rows, key).items():
        splits = {_stable_key(row.split) for row in group}
        if len(splits) > 1:
            errors.append(f"{code}:{_key_digest(value)}")


def validate_grapheme_authority_metadata(
    records: Iterable[GraphemeAuthorityMetadataRecord],
) -> AuthorityMetadataReport:
    """Validate metadata and leakage while withholding semantic authority activation.

    This gate cannot activate a registry by itself. Source, reviewer, and adjudication
    receipt contents still require a separate byte level authority join.
    """

    supplied_rows = list(records)
    rows = sorted(
        [row for row in supplied_rows if isinstance(row, GraphemeAuthorityMetadataRecord)],
        key=lambda row: (
            repr(row.pixel_occurrence_id),
            repr(row.source_image_sha256),
            repr(row.bbox),
            repr(row.crop_sha256),
        ),
    )
    if not supplied_rows:
        return AuthorityMetadataReport(
            metadata_valid=False,
            authority_usable=False,
            record_count=0,
            labelled_record_count=0,
            metadata_eligible_count=0,
            semantic_authority_count=0,
            independent_cross_witness_descriptor_groups=0,
            errors=("GRAPHEME_AUTHORITY_METADATA_EMPTY",),
        )
    errors: list[str] = [
        f"AUTHORITY_RECORD_TYPE_INVALID:{index}"
        for index, row in enumerate(supplied_rows)
        if not isinstance(row, GraphemeAuthorityMetadataRecord)
    ]
    for row in rows:
        suffix = f":{row.pixel_occurrence_id}"
        try:
            expected_occurrence_id = pixel_occurrence_id(row)
        except (TypeError, ValueError):
            expected_occurrence_id = None
        if (
            not isinstance(row.pixel_occurrence_id, str)
            or not _CONTENT_ID.fullmatch(row.pixel_occurrence_id)
            or expected_occurrence_id != row.pixel_occurrence_id
        ):
            errors.append("PIXEL_OCCURRENCE_ID_CONTENT_MISMATCH" + suffix)
        if _text(row.source_id) is None:
            errors.append("SOURCE_ID_MISSING" + suffix)
        if not isinstance(row.source_asset_id, str) or not _CONTENT_ID.fullmatch(row.source_asset_id):
            errors.append("SOURCE_ASSET_ID_INVALID" + suffix)
        if _text(row.source_page_id) is None:
            errors.append("SOURCE_PAGE_ID_MISSING" + suffix)
        for field, value in (
            ("SOURCE_IMAGE_HASH", row.source_image_sha256),
            ("CROP_HASH", row.crop_sha256),
            ("DESCRIPTOR_HASH", row.descriptor_sha256),
            ("DESCRIPTOR_CONFIG_HASH", row.descriptor_config_sha256),
            ("SOURCE_AUTHORITY_RECEIPT", row.source_authority_receipt_sha256),
            ("LABEL_ONTOLOGY", row.label_ontology_sha256),
            ("REVIEWER_AUTHORITY_RECEIPT", row.reviewer_authority_receipt_sha256),
            ("ADJUDICATOR_AUTHORITY_RECEIPT", row.adjudicator_authority_receipt_sha256),
            ("ADJUDICATION_RECEIPT", row.adjudication_receipt_sha256),
        ):
            if not _valid_sha256(value):
                errors.append(field + "_INVALID" + suffix)
        if (
            isinstance(row.descriptor_aspect_ratio, bool)
            or not isinstance(row.descriptor_aspect_ratio, (int, float))
            or not isfinite(row.descriptor_aspect_ratio)
            or row.descriptor_aspect_ratio <= 0.0
        ):
            errors.append("DESCRIPTOR_ASPECT_RATIO_INVALID" + suffix)
        if not _box_valid(row.bbox, row.source_image_width, row.source_image_height):
            errors.append("GEOMETRY_INVALID" + suffix)
        if not _box_valid(row.crop_bbox, row.source_image_width, row.source_image_height):
            errors.append("CROP_GEOMETRY_INVALID" + suffix)
        elif _box_valid(row.bbox, row.source_image_width, row.source_image_height) and not _contains(
            row.crop_bbox, row.bbox
        ):
            errors.append("CROP_DOES_NOT_CONTAIN_GLYPH" + suffix)
        if _text(row.manuscript_id) is None:
            errors.append("MANUSCRIPT_ID_MISSING" + suffix)
        if _text(row.hand_id) is None:
            errors.append("HAND_ID_MISSING" + suffix)
        if _text(row.style) is None:
            errors.append("STYLE_MISSING" + suffix)
        if not isinstance(row.split, str) or row.split not in {"train", "validation", "test"}:
            errors.append("TRAINING_SPLIT_INVALID" + suffix)
        if _text(row.lineage_root_id) is None:
            errors.append("LINEAGE_ROOT_MISSING" + suffix)
        if not isinstance(row.rights_status, str) or row.rights_status not in TRAINING_RIGHTS_STATUSES:
            errors.append("TRAINING_RIGHTS_INVALID" + suffix)
        label = row.diplomatic_label
        if not isinstance(label, str) or not label.strip():
            errors.append("DIPLOMATIC_LABEL_MISSING" + suffix)
        else:
            if unicodedata.normalize("NFC", label) != label:
                errors.append("DIPLOMATIC_LABEL_NOT_NFC" + suffix)
            if label.strip().casefold() in _PLACEHOLDER_LABELS:
                errors.append("DIPLOMATIC_LABEL_PLACEHOLDER" + suffix)
        if row.label_kind != "diplomatic_grapheme":
            errors.append("LABEL_KIND_INVALID" + suffix)
        if row.label_source_lane != "human_image_aligned":
            errors.append("LABEL_SOURCE_LANE_INVALID" + suffix)
        if not isinstance(row.reviewer_id, str) or not row.reviewer_id.strip() or row.reviewer_id != row.reviewer_id.strip():
            errors.append("REVIEWER_INVALID" + suffix)
        if not isinstance(row.adjudicator_id, str) or not row.adjudicator_id.strip() or row.adjudicator_id != row.adjudicator_id.strip():
            errors.append("ADJUDICATOR_INVALID" + suffix)
        if (
            isinstance(row.reviewer_id, str)
            and isinstance(row.adjudicator_id, str)
            and row.reviewer_id.strip().casefold() == row.adjudicator_id.strip().casefold()
        ):
            errors.append("REVIEWER_ADJUDICATOR_NOT_DISTINCT" + suffix)
        if row.review_state != "adjudicated":
            errors.append("REVIEW_STATE_INVALID" + suffix)
        try:
            expected_record_receipt = authority_record_receipt_sha256(row)
        except (TypeError, ValueError):
            expected_record_receipt = None
        if row.record_receipt_sha256 != expected_record_receipt:
            errors.append("AUTHORITY_RECORD_RECEIPT_MISMATCH" + suffix)

    for occurrence_id, group in _group(rows, lambda row: row.pixel_occurrence_id).items():
        if len(group) > 1:
            errors.append(f"PIXEL_OCCURRENCE_ID_DUPLICATE:{occurrence_id}")
    for locus, group in _group(rows, lambda row: (row.source_image_sha256, row.bbox)).items():
        if len(group) > 1:
            key = _key_digest(locus)
            errors.append(f"PIXEL_LOCUS_DUPLICATE:{key}")
            identities = {
                _stable_key(
                    (
                        row.crop_sha256,
                        row.descriptor_sha256,
                        row.descriptor_config_sha256,
                        row.descriptor_aspect_ratio,
                    )
                )
                for row in group
            }
            if len(identities) > 1:
                errors.append(f"PIXEL_LOCUS_CONTENT_CONFLICT:{key}")
    for crop_hash, group in _group(rows, lambda row: row.crop_sha256).items():
        if len(group) > 1:
            errors.append(f"CROP_DUPLICATE:{crop_hash}")
            if len({_stable_key(row.diplomatic_label) for row in group}) > 1:
                errors.append(f"CROP_LABEL_CONFLICT:{crop_hash}")
    for descriptor, group in _group(
        rows,
        lambda row: (
            row.descriptor_config_sha256,
            row.descriptor_sha256,
            row.descriptor_aspect_ratio,
        ),
    ).items():
        if len({_stable_key(row.diplomatic_label) for row in group}) > 1:
            errors.append(f"DESCRIPTOR_LABEL_CONFLICT:{_key_digest(descriptor)}")

    _split_leakage(errors, rows, key=lambda row: row.source_asset_id, code="SOURCE_ASSET_SPLIT_LEAKAGE")
    _split_leakage(
        errors,
        rows,
        key=lambda row: (row.source_id, row.source_page_id),
        code="SOURCE_PAGE_SPLIT_LEAKAGE",
    )
    _split_leakage(errors, rows, key=lambda row: row.source_image_sha256, code="SOURCE_IMAGE_SPLIT_LEAKAGE")
    _split_leakage(errors, rows, key=lambda row: (row.source_image_sha256, row.bbox), code="PIXEL_LOCUS_SPLIT_LEAKAGE")
    _split_leakage(errors, rows, key=lambda row: row.crop_sha256, code="CROP_SPLIT_LEAKAGE")
    _split_leakage(
        errors,
        rows,
        key=lambda row: (
            row.descriptor_config_sha256,
            row.descriptor_sha256,
            row.descriptor_aspect_ratio,
        ),
        code="DESCRIPTOR_SPLIT_LEAKAGE",
    )
    _split_leakage(errors, rows, key=lambda row: row.lineage_root_id, code="LINEAGE_ROOT_SPLIT_LEAKAGE")
    _split_leakage(errors, rows, key=lambda row: row.manuscript_id, code="MANUSCRIPT_SPLIT_LEAKAGE")
    _split_leakage(
        errors,
        rows,
        key=lambda row: (row.manuscript_id, row.hand_id),
        code="SCOPED_HAND_SPLIT_LEAKAGE",
    )

    independent_groups = 0
    for group in _group(
        rows,
        lambda row: (
            row.descriptor_config_sha256,
            row.descriptor_sha256,
            row.descriptor_aspect_ratio,
            row.diplomatic_label,
        ),
    ).values():
        if (
            len({_stable_key(row.manuscript_id) for row in group}) > 1
            and len({_stable_key(row.source_image_sha256) for row in group}) == len(group)
            and len({_stable_key(row.crop_sha256) for row in group}) == len(group)
            and len({_stable_key(row.lineage_root_id) for row in group}) == len(group)
            and len({_stable_key(row.split) for row in group}) == 1
        ):
            independent_groups += 1
    unique_errors = tuple(sorted(set(errors)))
    labelled_count = sum(isinstance(row.diplomatic_label, str) and bool(row.diplomatic_label.strip()) for row in rows)
    return AuthorityMetadataReport(
        metadata_valid=not unique_errors,
        authority_usable=False,
        record_count=len(supplied_rows),
        labelled_record_count=labelled_count,
        metadata_eligible_count=len(supplied_rows) if not unique_errors else 0,
        semantic_authority_count=0,
        independent_cross_witness_descriptor_groups=independent_groups if not unique_errors else 0,
        errors=unique_errors,
    )
