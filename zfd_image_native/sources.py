"""Source identity, rights, and evidentiary role validation."""

from __future__ import annotations

from collections import Counter
from typing import Iterable

from .models import SourceRecord, ValidationIssue, ValidationReport


DATE_KINDS = frozenset({"material", "writing", "text", "copy", "publication"})
DATE_CERTAINTIES = frozenset(
    {
        "exact",
        "catalogued_exact",
        "catalogued_range",
        "approximate_range",
        "scientific_range",
        "century",
        "unresolved",
    }
)
SOURCE_TYPES = frozenset(
    {
        "target_manuscript",
        "manuscript",
        "manuscript_fragment",
        "incunable_print",
        "critical_edition",
        "scholarly_article",
    }
)
TRAINING_DISPOSITIONS = frozenset(
    {
        "target_only",
        "reference_only",
        "control_only",
        "quarantined",
        "excluded",
        "train",
        "evaluate",
    }
)
TRAINING_CAPABLE_DISPOSITIONS = frozenset({"train", "evaluate"})
TRAINING_RIGHTS_STATUSES = frozenset(
    {"public_domain", "licensed_training", "open_license"}
)

_DATE_FIELDS = {
    "material": ("material_date_start", "material_date_end"),
    "writing": ("writing_date_start", "writing_date_end"),
    "text": ("text_date_start", "text_date_end"),
    "copy": ("copy_date_start", "copy_date_end"),
    "publication": ("publication_date_start", "publication_date_end"),
}


def _valid_sha256(value: str | None) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    return all(character in "0123456789abcdefABCDEF" for character in value)


def _missing(value: str | None) -> bool:
    return not isinstance(value, str) or not value.strip()


def _complete_date_ranges(
    source: SourceRecord, issues: list[ValidationIssue]
) -> set[str]:
    complete: set[str] = set()
    for date_kind, (start_field, end_field) in _DATE_FIELDS.items():
        start = getattr(source, start_field)
        end = getattr(source, end_field)
        code_prefix = date_kind.upper()
        if (start is None) != (end is None):
            issues.append(
                ValidationIssue(
                    f"{code_prefix}_DATE_RANGE_INCOMPLETE",
                    f"{date_kind.title()} date range needs both bounds",
                    source.source_id,
                )
            )
            continue
        if start is None:
            continue
        if isinstance(start, bool) or isinstance(end, bool) or not isinstance(start, int) or not isinstance(end, int):
            issues.append(
                ValidationIssue(
                    f"{code_prefix}_DATE_RANGE_INVALID",
                    f"{date_kind.title()} date bounds must be integer years",
                    source.source_id,
                )
            )
            continue
        complete.add(date_kind)
        if start > end:
            issues.append(
                ValidationIssue(
                    f"{code_prefix}_DATE_RANGE_REVERSED",
                    f"{date_kind.title()} date starts after it ends",
                    source.source_id,
                )
            )
    return complete


def _require_checksum(
    source: SourceRecord,
    field: str,
    missing_code: str,
    invalid_code: str,
    issues: list[ValidationIssue],
) -> None:
    value = getattr(source, field)
    if value is None:
        issues.append(
            ValidationIssue(missing_code, f"Training source needs {field}", source.source_id)
        )
    elif not _valid_sha256(value):
        issues.append(
            ValidationIssue(invalid_code, f"{field} is not a SHA 256", source.source_id)
        )


def validate_sources(records: Iterable[SourceRecord]) -> ValidationReport:
    sources = list(records)
    issues: list[ValidationIssue] = []
    counts = Counter(source.source_id for source in sources)
    for source_id, count in counts.items():
        if count > 1:
            issues.append(ValidationIssue("SOURCE_ID_DUPLICATE", "Source ID is not unique", source_id))

    for source in sources:
        if _missing(source.source_id):
            issues.append(ValidationIssue("SOURCE_ID_MISSING", "Source ID is required"))
        if _missing(source.stable_locator):
            issues.append(ValidationIssue("LOCATOR_MISSING", "Stable locator is required", source.source_id))
        for field, code, label in (
            ("source_label", "SOURCE_LABEL_MISSING", "Source label"),
            ("title", "TITLE_MISSING", "Title"),
            ("date_basis", "DATE_BASIS_MISSING", "Date basis"),
            ("dating_authority", "DATING_AUTHORITY_MISSING", "Dating authority"),
            (
                "dating_authority_locator",
                "DATING_AUTHORITY_LOCATOR_MISSING",
                "Dating authority locator",
            ),
            ("institution", "INSTITUTION_MISSING", "Institution"),
            ("shelfmark", "SHELFMARK_MISSING", "Shelfmark or publication identifier"),
            ("language", "LANGUAGE_MISSING", "Language"),
            ("script", "SCRIPT_MISSING", "Script"),
            ("hand_style", "HAND_STYLE_MISSING", "Hand or style"),
            ("genre", "GENRE_MISSING", "Genre"),
            ("region", "REGION_MISSING", "Region"),
            ("evidentiary_role", "EVIDENTIARY_ROLE_MISSING", "Evidentiary role"),
        ):
            if _missing(getattr(source, field)):
                issues.append(ValidationIssue(code, f"{label} is required", source.source_id))

        complete_ranges = _complete_date_ranges(source, issues)
        if not complete_ranges:
            issues.append(
                ValidationIssue("SOURCE_DATE_MISSING", "At least one typed date range is required", source.source_id)
            )
        if source.date_kind not in DATE_KINDS:
            issues.append(
                ValidationIssue("DATE_KIND_INVALID", "Date kind is not registered", source.source_id)
            )
        elif source.date_kind not in complete_ranges:
            issues.append(
                ValidationIssue(
                    "DATE_KIND_RANGE_MISSING",
                    "The primary date kind has no complete matching range",
                    source.source_id,
                )
            )
        if source.dating_certainty not in DATE_CERTAINTIES:
            issues.append(
                ValidationIssue(
                    "DATING_CERTAINTY_INVALID",
                    "Dating certainty is not registered",
                    source.source_id,
                )
            )

        basis = (source.date_basis or "").casefold()
        if ("radiocarbon" in basis or "carbon dating" in basis) and source.date_kind != "material":
            issues.append(
                ValidationIssue(
                    "MATERIAL_DATE_MISCLASSIFIED",
                    "Radiocarbon dates describe material and cannot be labelled writing, copy, or text dates",
                    source.source_id,
                )
            )

        if source.source_type not in SOURCE_TYPES:
            issues.append(
                ValidationIssue("SOURCE_TYPE_INVALID", "Source type is not registered", source.source_id)
            )
        elif source.source_type in {"manuscript", "manuscript_fragment"}:
            if not ({"writing", "copy"} & complete_ranges):
                issues.append(
                    ValidationIssue(
                        "ROLE_WRITING_OR_COPY_DATE_REQUIRED",
                        "Manuscript evidence needs a writing or copy date; material and text dates do not date the hand",
                        source.source_id,
                    )
                )
            if source.date_kind not in {"writing", "copy"}:
                issues.append(
                    ValidationIssue(
                        "ROLE_DATE_KIND_INCOMPATIBLE",
                        "A manuscript evidence record must foreground its writing or copy date",
                        source.source_id,
                    )
                )
        elif source.source_type == "target_manuscript":
            if source.evidentiary_role != "target":
                issues.append(
                    ValidationIssue(
                        "ROLE_SOURCE_TYPE_INCOMPATIBLE",
                        "A target manuscript source type must carry the target role",
                        source.source_id,
                    )
                )
        elif source.source_type == "incunable_print":
            if source.date_kind != "publication" or "publication" not in complete_ranges:
                issues.append(
                    ValidationIssue(
                        "ROLE_PUBLICATION_DATE_REQUIRED",
                        "An incunable control needs its publication date",
                        source.source_id,
                    )
                )
        elif source.source_type == "scholarly_article":
            if source.date_kind != "publication" or "publication" not in complete_ranges:
                issues.append(
                    ValidationIssue(
                        "ROLE_PUBLICATION_DATE_REQUIRED",
                        "A scholarly source needs its publication date",
                        source.source_id,
                    )
                )
            if "secondary" not in source.evidentiary_role:
                issues.append(
                    ValidationIssue(
                        "ROLE_SOURCE_TYPE_INCOMPATIBLE",
                        "A scholarly article must be marked as secondary evidence",
                        source.source_id,
                    )
                )
        elif source.source_type == "critical_edition":
            if "publication" not in complete_ranges or not ({"writing", "copy", "text"} & complete_ranges):
                issues.append(
                    ValidationIssue(
                        "CRITICAL_EDITION_WITNESS_DATE_REQUIRED",
                        "A critical edition needs publication and underlying witness dates",
                        source.source_id,
                    )
                )

        if _missing(source.control_group):
            issues.append(ValidationIssue("CONTROL_GROUP_MISSING", "Control group is required", source.source_id))
        if _missing(source.rights_statement) or _missing(source.rights_locator):
            issues.append(ValidationIssue("RIGHTS_MISSING", "Rights statement and locator are required", source.source_id))
        if source.identity_status != "resolved":
            issues.append(ValidationIssue("IDENTITY_UNRESOLVED", "Source identity is unresolved", source.source_id))

        if source.training_use not in TRAINING_DISPOSITIONS:
            issues.append(
                ValidationIssue(
                    "TRAINING_DISPOSITION_INVALID",
                    "Training disposition is not registered",
                    source.source_id,
                )
            )
        elif source.training_use in TRAINING_CAPABLE_DISPOSITIONS:
            if source.rights_status not in TRAINING_RIGHTS_STATUSES:
                issues.append(ValidationIssue("TRAINING_RIGHTS_BLOCKED", "Rights do not authorize training", source.source_id))
            if not _valid_sha256(source.manifest_sha256):
                issues.append(ValidationIssue("CHECKSUM_MISSING", "Training source needs a manifest checksum", source.source_id))
            _require_checksum(
                source,
                "asset_mapping_sha256",
                "ASSET_MAPPING_CHECKSUM_MISSING",
                "ASSET_MAPPING_CHECKSUM_INVALID",
                issues,
            )
            _require_checksum(
                source,
                "page_mapping_sha256",
                "PAGE_MAPPING_CHECKSUM_MISSING",
                "PAGE_MAPPING_CHECKSUM_INVALID",
                issues,
            )
            _require_checksum(
                source,
                "lineage_sha256",
                "LINEAGE_CHECKSUM_MISSING",
                "LINEAGE_CHECKSUM_INVALID",
                issues,
            )
            _require_checksum(
                source,
                "hand_boundary_sha256",
                "HAND_BOUNDARY_CHECKSUM_MISSING",
                "HAND_BOUNDARY_CHECKSUM_INVALID",
                issues,
            )
            _require_checksum(
                source,
                "line_annotation_sha256",
                "LINE_ANNOTATION_CHECKSUM_MISSING",
                "LINE_ANNOTATION_CHECKSUM_INVALID",
                issues,
            )
            _require_checksum(
                source,
                "split_lineage_sha256",
                "SPLIT_LINEAGE_CHECKSUM_MISSING",
                "SPLIT_LINEAGE_CHECKSUM_INVALID",
                issues,
            )

        if source.manifest_sha256 is not None and not _valid_sha256(source.manifest_sha256):
            issues.append(ValidationIssue("CHECKSUM_INVALID", "Manifest checksum is invalid", source.source_id))
        for field, code in (
            ("asset_mapping_sha256", "ASSET_MAPPING_CHECKSUM_INVALID"),
            ("page_mapping_sha256", "PAGE_MAPPING_CHECKSUM_INVALID"),
            ("lineage_sha256", "LINEAGE_CHECKSUM_INVALID"),
            ("hand_boundary_sha256", "HAND_BOUNDARY_CHECKSUM_INVALID"),
            ("line_annotation_sha256", "LINE_ANNOTATION_CHECKSUM_INVALID"),
            ("split_lineage_sha256", "SPLIT_LINEAGE_CHECKSUM_INVALID"),
        ):
            value = getattr(source, field)
            if value is not None and not _valid_sha256(value):
                issues.append(ValidationIssue(code, f"{field} is invalid", source.source_id))

    return ValidationReport(tuple(issues))
