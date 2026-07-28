"""Validation for historically layered terminology records."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import re
from typing import Any, Mapping

from .io import canonical_json
from .models import SourceRecord, TerminologyRecord
from .sources import validate_sources


AUTHORITY_SCHEMA = "zfd.terminology_evidence_authority.v1"
_WITNESS_DATE_FIELDS = {
    "writing": ("writing_date_start", "writing_date_end"),
    "copy": ("copy_date_start", "copy_date_end"),
    "text": ("text_date_start", "text_date_end"),
    "publication": ("publication_date_start", "publication_date_end"),
}
_PRIMARY_WITNESS_SOURCE_TYPES = frozenset(
    {"manuscript", "manuscript_fragment", "incunable_print"}
)
_REVIEW_STATES = frozenset({"unreviewed", "in_review", "approved", "rejected"})
CONFIDENCE_BASES = frozenset(
    {
        "adjudicated_primary_witness_reading",
        "independent_image_aligned_review",
        "primary_witness_critical_edition_alignment",
    }
)


def _valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _receipt_valid(row: Mapping[str, Any]) -> bool:
    supplied = row.get("receipt_sha256")
    if not _valid_sha256(supplied):
        return False
    payload = {key: value for key, value in row.items() if key != "receipt_sha256"}
    expected = sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    return supplied == expected


def _authority_record(
    authority: Mapping[str, Any], bucket: str, identity: str | None
) -> Mapping[str, Any] | None:
    records = authority.get(bucket)
    if not isinstance(records, Mapping) or not isinstance(identity, str):
        return None
    row = records.get(identity)
    return row if isinstance(row, Mapping) else None


def _present(value: str | None) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _diplomatic_sha256(value: str | None) -> str | None:
    if not isinstance(value, str):
        return None
    return sha256(value.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class TerminologyValidationReport:
    codes: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.codes


def _validate_identity(
    row: Mapping[str, Any] | None,
    *,
    identity_id: str | None,
    role: str,
    language: str | None,
    missing_code: str,
    codes: list[str],
) -> None:
    if row is None:
        codes.append(missing_code)
        return
    if not _receipt_valid(row):
        codes.append(missing_code.replace("MISSING", "RECEIPT_INVALID"))
        return
    if (
        row.get("identity_id") != identity_id
        or row.get("role") != role
        or row.get("status") != "active"
    ):
        codes.append(missing_code.replace("MISSING", "INVALID"))
    qualified_layers = row.get("qualified_layers")
    qualified_languages = row.get("qualified_languages")
    if (
        not isinstance(qualified_layers, list)
        or "historical_terminology" not in qualified_layers
        or not isinstance(qualified_languages, list)
        or language not in qualified_languages
    ):
        codes.append(missing_code.replace("MISSING", "UNQUALIFIED"))


def validate_terminology(
    record: TerminologyRecord,
    authority: Mapping[str, Any] | None = None,
) -> TerminologyValidationReport:
    """Validate a term against one content-bound evidence authority.

    A caller-supplied source object or plausible checksum is insufficient. Every
    witness, image, diplomatic reading, reviewer, and adjudication must be a
    self-hashing member of the same self-hashing authority.
    """

    codes: list[str] = []
    if not _present(record.ocr_id):
        codes.append("OCR_PARENT_MISSING")
    if not _present(record.observed_form):
        codes.append("OBSERVED_FORM_MISSING")
    if record.witness_date_start is None or record.witness_date_end is None:
        codes.append("WITNESS_DATE_MISSING")
    elif record.witness_date_start > record.witness_date_end:
        codes.append("WITNESS_DATE_RANGE_REVERSED")
    if record.witness_date_kind not in _WITNESS_DATE_FIELDS:
        codes.append("WITNESS_DATE_KIND_INVALID")
    if not _present(record.witness_language):
        codes.append("WITNESS_LANGUAGE_MISSING")
    if not _present(record.witness_script):
        codes.append("WITNESS_SCRIPT_MISSING")
    if not _present(record.witness_domain):
        codes.append("WITNESS_DOMAIN_MISSING")
    if not _present(record.passage_locator):
        codes.append("PASSAGE_LOCATOR_MISSING")
    if not _present(record.stable_locator):
        codes.append("STABLE_LOCATOR_MISSING")
    if not _present(record.source_id):
        codes.append("SOURCE_ID_MISSING")
    if not _valid_sha256(record.source_sha256):
        codes.append(
            "SOURCE_CHECKSUM_MISSING"
            if record.source_sha256 is None
            else "SOURCE_CHECKSUM_INVALID"
        )
    if not _present(record.passage_asset_id):
        codes.append("PASSAGE_ASSET_ID_MISSING")
    if not _valid_sha256(record.passage_asset_sha256):
        codes.append(
            "PASSAGE_ASSET_CHECKSUM_MISSING"
            if record.passage_asset_sha256 is None
            else "PASSAGE_ASSET_CHECKSUM_INVALID"
        )
    if not _present(record.passage_image_id):
        codes.append("PASSAGE_IMAGE_ID_MISSING")
    if not _valid_sha256(record.passage_image_sha256):
        codes.append(
            "PASSAGE_IMAGE_CHECKSUM_MISSING"
            if record.passage_image_sha256 is None
            else "PASSAGE_IMAGE_CHECKSUM_INVALID"
        )
    if not _present(record.diplomatic_passage):
        codes.append("DIPLOMATIC_PASSAGE_MISSING")
    elif (
        _present(record.observed_form)
        and record.observed_form.strip().casefold()
        not in record.diplomatic_passage.casefold()
    ):
        codes.append("OBSERVED_FORM_NOT_IN_DIPLOMATIC_PASSAGE")
    if not _present(record.modern_croatian):
        codes.append("MODERN_CROATIAN_MISSING")
    if not _present(record.reviewer_id):
        codes.append("REVIEWER_MISSING")
    if not _present(record.adjudicator_id):
        codes.append("ADJUDICATOR_MISSING")
    if (
        _present(record.reviewer_id)
        and _present(record.adjudicator_id)
        and record.reviewer_id.strip().casefold()
        == record.adjudicator_id.strip().casefold()
    ):
        codes.append("ADJUDICATOR_NOT_INDEPENDENT")
    if record.review_state not in _REVIEW_STATES:
        codes.append("REVIEW_STATE_INVALID")
    if record.review_state != "approved":
        codes.append("REVIEW_NOT_APPROVED")
    if record.confidence is None:
        codes.append("CONFIDENCE_MISSING")
    elif isinstance(record.confidence, bool) or not 0.0 <= record.confidence <= 1.0:
        codes.append("CONFIDENCE_OUT_OF_RANGE")
    if not _present(record.confidence_basis):
        codes.append("CONFIDENCE_BASIS_MISSING")
    elif record.confidence_basis not in CONFIDENCE_BASES:
        codes.append("CONFIDENCE_BASIS_INVALID")
    if record.speculation and record.reconstructed_form == record.observed_form:
        codes.append("RECONSTRUCTION_NOT_SEPARATED")

    if not isinstance(authority, Mapping):
        codes.append("EVIDENCE_AUTHORITY_MISSING")
        return TerminologyValidationReport(tuple(dict.fromkeys(codes)))
    if (
        authority.get("schema") != AUTHORITY_SCHEMA
        or authority.get("schema_version") != "1.0.0"
    ):
        codes.append("EVIDENCE_AUTHORITY_SCHEMA_INVALID")
    if not _receipt_valid(authority):
        codes.append("EVIDENCE_AUTHORITY_RECEIPT_INVALID")

    source_row = _authority_record(authority, "sources", record.source_id)
    source: SourceRecord | None = None
    if source_row is None:
        codes.append("SOURCE_AUTHORITY_MISSING")
    elif not _receipt_valid(source_row):
        codes.append("SOURCE_AUTHORITY_RECEIPT_INVALID")
    else:
        try:
            source = SourceRecord(
                **{
                    key: value
                    for key, value in source_row.items()
                    if key != "receipt_sha256"
                }
            )
        except TypeError:
            codes.append("SOURCE_AUTHORITY_INVALID")
        else:
            if source.source_id != record.source_id:
                codes.append("SOURCE_AUTHORITY_LINK_MISMATCH")
            if not validate_sources([source]).ok:
                codes.append("REGISTERED_SOURCE_INVALID")
            if source.source_type not in _PRIMARY_WITNESS_SOURCE_TYPES | {
                "critical_edition"
            }:
                codes.append("OBSERVED_FORM_SOURCE_NOT_PRIMARY_OR_CRITICAL")
            if (
                source.source_type == "critical_edition"
                and record.witness_date_kind == "publication"
            ):
                codes.append("CRITICAL_EDITION_WITNESS_DATE_MISSING")
            if record.stable_locator != source.stable_locator:
                codes.append("STABLE_LOCATOR_MISMATCH")
            if not _valid_sha256(source.manifest_sha256):
                codes.append("REGISTERED_SOURCE_CHECKSUM_MISSING")
            elif record.source_sha256 != source.manifest_sha256:
                codes.append("SOURCE_CHECKSUM_MISMATCH")
            if record.witness_language != source.language:
                codes.append("WITNESS_LANGUAGE_MISMATCH")
            if record.witness_script != source.script:
                codes.append("WITNESS_SCRIPT_MISMATCH")
            if record.witness_date_kind in _WITNESS_DATE_FIELDS:
                start_field, end_field = _WITNESS_DATE_FIELDS[
                    record.witness_date_kind
                ]
                registered_start = getattr(source, start_field)
                registered_end = getattr(source, end_field)
                if registered_start is None or registered_end is None:
                    codes.append("REGISTERED_WITNESS_DATE_MISSING")
                elif (
                    record.witness_date_start != registered_start
                    or record.witness_date_end != registered_end
                ):
                    codes.append("WITNESS_DATE_MISMATCH")

    asset = _authority_record(authority, "passage_assets", record.passage_asset_id)
    if asset is None:
        codes.append("PASSAGE_ASSET_AUTHORITY_MISSING")
    elif not _receipt_valid(asset):
        codes.append("PASSAGE_ASSET_AUTHORITY_RECEIPT_INVALID")
    elif any(
        asset.get(field) != expected
        for field, expected in (
            ("passage_asset_id", record.passage_asset_id),
            ("source_id", record.source_id),
            ("source_sha256", record.source_sha256),
            ("sha256", record.passage_asset_sha256),
            ("stable_locator", record.stable_locator),
            ("passage_locator", record.passage_locator),
        )
    ):
        codes.append("PASSAGE_ASSET_AUTHORITY_LINK_MISMATCH")

    image = _authority_record(authority, "passage_images", record.passage_image_id)
    if image is None:
        codes.append("PASSAGE_IMAGE_AUTHORITY_MISSING")
    elif not _receipt_valid(image):
        codes.append("PASSAGE_IMAGE_AUTHORITY_RECEIPT_INVALID")
    elif any(
        image.get(field) != expected
        for field, expected in (
            ("passage_image_id", record.passage_image_id),
            ("source_id", record.source_id),
            ("passage_asset_id", record.passage_asset_id),
            ("passage_asset_sha256", record.passage_asset_sha256),
            ("sha256", record.passage_image_sha256),
        )
    ):
        codes.append("PASSAGE_IMAGE_AUTHORITY_LINK_MISMATCH")

    diplomatic_hash = _diplomatic_sha256(record.diplomatic_passage)
    ocr = _authority_record(authority, "ocr_records", record.ocr_id)
    if ocr is None:
        codes.append("OCR_AUTHORITY_MISSING")
    elif not _receipt_valid(ocr):
        codes.append("OCR_AUTHORITY_RECEIPT_INVALID")
    elif any(
        ocr.get(field) != expected
        for field, expected in (
            ("ocr_id", record.ocr_id),
            ("source_id", record.source_id),
            ("passage_image_id", record.passage_image_id),
            ("passage_image_sha256", record.passage_image_sha256),
            ("diplomatic_passage_sha256", diplomatic_hash),
        )
    ):
        codes.append("OCR_DIPLOMATIC_AUTHORITY_LINK_MISMATCH")

    _validate_identity(
        _authority_record(authority, "reviewers", record.reviewer_id),
        identity_id=record.reviewer_id,
        role="historical_terminology_reviewer",
        language=record.witness_language,
        missing_code="REVIEWER_AUTHORITY_MISSING",
        codes=codes,
    )
    _validate_identity(
        _authority_record(authority, "adjudicators", record.adjudicator_id),
        identity_id=record.adjudicator_id,
        role="historical_terminology_adjudicator",
        language=record.witness_language,
        missing_code="ADJUDICATOR_AUTHORITY_MISSING",
        codes=codes,
    )

    adjudication = _authority_record(authority, "adjudications", record.term_id)
    if adjudication is None:
        codes.append("ADJUDICATION_AUTHORITY_MISSING")
    elif not _receipt_valid(adjudication):
        codes.append("ADJUDICATION_AUTHORITY_RECEIPT_INVALID")
    elif any(
        adjudication.get(field) != expected
        for field, expected in (
            ("term_id", record.term_id),
            ("ocr_id", record.ocr_id),
            ("source_id", record.source_id),
            ("source_sha256", record.source_sha256),
            ("passage_asset_id", record.passage_asset_id),
            ("passage_asset_sha256", record.passage_asset_sha256),
            ("passage_image_id", record.passage_image_id),
            ("passage_image_sha256", record.passage_image_sha256),
            ("diplomatic_passage_sha256", diplomatic_hash),
            ("reviewer_id", record.reviewer_id),
            ("adjudicator_id", record.adjudicator_id),
            ("confidence_basis", record.confidence_basis),
            ("status", "approved"),
        )
    ):
        codes.append("ADJUDICATION_AUTHORITY_LINK_MISMATCH")

    return TerminologyValidationReport(tuple(dict.fromkeys(codes)))
