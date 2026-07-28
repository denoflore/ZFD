"""Machine decisions for publication claims."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Mapping

from .io import canonical_json
from .parity import validate_page_parity


@dataclass(frozen=True)
class ClaimDecision:
    name: str
    allowed: bool
    status: str
    missing_receipts: tuple[str, ...]
    blocking_reasons: tuple[str, ...]


@dataclass(frozen=True)
class ClaimReport:
    decisions: tuple[ClaimDecision, ...]

    def claim(self, name: str) -> ClaimDecision:
        for decision in self.decisions:
            if decision.name == name:
                return decision
        raise KeyError(name)


PASS_STATES = frozenset({"pass", "passed", "measured", "approved", "complete"})
SUPPORTED_CLAIM_STATES = frozenset({"supported", "approved"})
CANONICAL_VOYNICH_PAGE_COUNT = 210
CANONICAL_VOYNICH_PAGE_IDENTITY_SHA256 = (
    "f11d848fd0f07ee3aaeace2278369efc718f5406a7b98239d596594cc78b8ae7"
)
PARITY_AUTHORITY_SCHEMA = "zfd.claim_parity_authority.v1"
PARITY_RECORD_SCHEMA = "zfd.translation_parity_record.v1"
PAGE_MANIFEST_SCHEMA = "zfd.canonical_page_authority.v1"
REGION_MANIFEST_SCHEMA = "zfd.canonical_region_authority.v1"
PAGE_DISPOSITION_SCHEMA = "zfd.page_translation_disposition.v1"
NON_TEXT_REVIEW_SCHEMA = "zfd.nontext_page_review.v1"
PARITY_RECEIPT_TYPES = frozenset(
    {
        "page_translation_parity",
        "page_translation_parity_210",
        "region_translation_parity_all",
        "canonical_record_recomputation",
        "corpus_pixel_translation_parity",
    }
)


def _self_hash_valid(value: Mapping[str, Any]) -> bool:
    supplied = value.get("receipt_sha256")
    if not isinstance(supplied, str) or len(supplied) != 64:
        return False
    payload = {key: item for key, item in value.items() if key != "receipt_sha256"}
    expected = sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    return supplied == expected


def _positive_count(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _nonnegative_count(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _valid_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _value_sha256(value: Any) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _parity_authority_failures(
    name: str,
    value: Mapping[str, Any],
    authority: Any,
    specification: Mapping[str, Any],
) -> tuple[str, ...]:
    if not isinstance(authority, Mapping):
        return ("AUTHORITY_MISSING",)
    failures: list[str] = []

    if value.get("schema") != "zfd.claim_receipt.v1":
        failures.append("SCHEMA_INVALID")
    if value.get("receipt_type") != name:
        failures.append("RECEIPT_TYPE_MISMATCH")
    if value.get("issuer") != "zfd_image_native":
        failures.append("ISSUER_INVALID")

    if authority.get("schema") != PARITY_AUTHORITY_SCHEMA:
        failures.append("AUTHORITY_SCHEMA_INVALID")
    if not _self_hash_valid(authority):
        failures.append("AUTHORITY_SELF_HASH_INVALID")
    authority_hash = authority.get("receipt_sha256")
    trusted_authority_hash = specification.get("authority_receipt_sha256")
    if not _valid_sha256(trusted_authority_hash):
        failures.append("TRUSTED_AUTHORITY_HASH_MISSING")
    elif trusted_authority_hash != authority_hash:
        failures.append("TRUSTED_AUTHORITY_HASH_MISMATCH")
    if value.get("authority_receipt_sha256") != authority_hash:
        failures.append("RECEIPT_AUTHORITY_HASH_MISMATCH")

    page_manifest = authority.get("page_manifest")
    region_manifest = authority.get("region_manifest")
    page_dispositions = authority.get("page_dispositions")
    records = authority.get("records")
    evidence_authority = authority.get("evidence_authority")
    collections = {
        "page_manifest": page_manifest,
        "region_manifest": region_manifest,
        "page_dispositions": page_dispositions,
        "records": records,
    }
    for field, rows in collections.items():
        if not isinstance(rows, list) or (field != "region_manifest" and not rows):
            failures.append(f"{field.upper()}_MISSING")
            collections[field] = []
            continue
        digest_field = f"{field}_sha256"
        expected_digest = _value_sha256(rows)
        if authority.get(digest_field) != expected_digest:
            failures.append(f"AUTHORITY_{digest_field.upper()}_MISMATCH")
        if value.get(digest_field) != expected_digest:
            failures.append(f"RECEIPT_{digest_field.upper()}_MISMATCH")

    page_manifest = collections["page_manifest"]
    region_manifest = collections["region_manifest"]
    page_dispositions = collections["page_dispositions"]
    records = collections["records"]

    expected_page_manifest_hash = specification.get("canonical_page_manifest_sha256")
    expected_region_manifest_hash = specification.get("canonical_region_manifest_sha256")
    if not _valid_sha256(expected_page_manifest_hash):
        failures.append("TRUSTED_PAGE_MANIFEST_HASH_MISSING")
    elif expected_page_manifest_hash != _value_sha256(page_manifest):
        failures.append("TRUSTED_PAGE_MANIFEST_HASH_MISMATCH")
    if not _valid_sha256(expected_region_manifest_hash):
        failures.append("TRUSTED_REGION_MANIFEST_HASH_MISSING")
    elif expected_region_manifest_hash != _value_sha256(region_manifest):
        failures.append("TRUSTED_REGION_MANIFEST_HASH_MISMATCH")

    expected_total_pages = specification.get("expected_total_pages")
    expected_total_regions = specification.get("expected_total_regions")
    if expected_total_pages != CANONICAL_VOYNICH_PAGE_COUNT:
        failures.append("CANONICAL_PAGE_SCOPE_NOT_210")
    if expected_total_pages != len(page_manifest):
        failures.append("CANONICAL_PAGE_COUNT_MISMATCH")
    if not _positive_count(expected_total_regions) or expected_total_regions != len(
        region_manifest
    ):
        failures.append("CANONICAL_REGION_COUNT_MISMATCH")

    page_by_id: dict[str, Mapping[str, Any]] = {}
    for row in page_manifest:
        if (
            not isinstance(row, Mapping)
            or row.get("schema") != PAGE_MANIFEST_SCHEMA
            or not _self_hash_valid(row)
        ):
            failures.append("CANONICAL_PAGE_RECORD_INVALID")
            continue
        page_id = row.get("page_id")
        if (
            not isinstance(page_id, str)
            or not page_id
            or row.get("source_id") != "yale-ms-408"
            or not isinstance(row.get("source_id"), str)
            or not row.get("source_id")
            or not isinstance(row.get("iiif_id"), str)
            or not row.get("iiif_id")
            or page_id != f"yale-ms-408:iiif:{row.get('iiif_id')}"
            or row.get("iiif_base_uri")
            != f"https://collections.library.yale.edu/iiif/2/{row.get('iiif_id')}"
            or not _valid_sha256(row.get("image_sha256"))
            or not _valid_sha256(row.get("page_layer_receipt_sha256"))
        ):
            failures.append("CANONICAL_PAGE_IDENTITY_INVALID")
            continue
        if page_id in page_by_id:
            failures.append("CANONICAL_PAGE_DUPLICATE")
            continue
        page_by_id[page_id] = row

    canonical_identity_rows = sorted(
        (
            {
                "page_id": row.get("page_id"),
                "source_id": row.get("source_id"),
                "iiif_id": row.get("iiif_id"),
                "iiif_base_uri": row.get("iiif_base_uri"),
            }
            for row in page_by_id.values()
        ),
        key=lambda row: str(row["page_id"]),
    )
    if _value_sha256(canonical_identity_rows) != CANONICAL_VOYNICH_PAGE_IDENTITY_SHA256:
        failures.append("CANONICAL_PAGE_IDENTITY_AUTHORITY_MISMATCH")

    region_by_identity: dict[tuple[str, str], Mapping[str, Any]] = {}
    regions_by_page: dict[str, list[str]] = {page_id: [] for page_id in page_by_id}
    for row in region_manifest:
        if (
            not isinstance(row, Mapping)
            or row.get("schema") != REGION_MANIFEST_SCHEMA
            or not _self_hash_valid(row)
        ):
            failures.append("CANONICAL_REGION_RECORD_INVALID")
            continue
        page_id = row.get("page_id")
        region_id = row.get("region_id")
        identity = (str(page_id), str(region_id))
        page_row = page_by_id.get(str(page_id))
        if (
            page_row is None
            or not isinstance(region_id, str)
            or not region_id
            or row.get("image_sha256") != page_row.get("image_sha256")
            or not _valid_sha256(row.get("geometry_sha256"))
            or not _valid_sha256(row.get("region_layer_receipt_sha256"))
            or row.get("page_manifest_receipt_sha256") != page_row.get("receipt_sha256")
        ):
            failures.append("CANONICAL_REGION_IDENTITY_INVALID")
            continue
        if identity in region_by_identity:
            failures.append("CANONICAL_REGION_DUPLICATE")
            continue
        region_by_identity[identity] = row
        regions_by_page[str(page_id)].append(str(region_id))

    if not isinstance(evidence_authority, Mapping):
        failures.append("EVIDENCE_AUTHORITY_MISSING")
        evidence_authority = {}
    evidence_authority_hash = evidence_authority.get("receipt_sha256")
    if not _self_hash_valid(evidence_authority):
        failures.append("EVIDENCE_AUTHORITY_SELF_HASH_INVALID")
    if authority.get("evidence_authority_receipt_sha256") != evidence_authority_hash:
        failures.append("EVIDENCE_AUTHORITY_LINK_MISMATCH")
    if value.get("evidence_authority_receipt_sha256") != evidence_authority_hash:
        failures.append("RECEIPT_EVIDENCE_AUTHORITY_LINK_MISMATCH")

    evidence_layers = evidence_authority.get("layers")
    evidence_page_layers = (
        evidence_layers.get("page") if isinstance(evidence_layers, Mapping) else None
    )
    evidence_sources = evidence_authority.get("sources")
    for page_id, page_row in page_by_id.items():
        page_layer_hash = page_row.get("page_layer_receipt_sha256")
        page_layer = (
            evidence_page_layers.get(page_layer_hash)
            if isinstance(evidence_page_layers, Mapping)
            else None
        )
        if (
            not isinstance(page_layer, Mapping)
            or not _self_hash_valid(page_layer)
            or page_layer.get("schema") != "zfd.parity_page.v1"
            or page_layer.get("page_id") != page_id
            or page_layer.get("source_id") != page_row.get("source_id")
            or page_layer.get("image_sha256") != page_row.get("image_sha256")
        ):
            failures.append("CANONICAL_PAGE_LAYER_AUTHORITY_MISMATCH")
            continue
        source = (
            evidence_sources.get(page_layer.get("source_id"))
            if isinstance(evidence_sources, Mapping)
            else None
        )
        if (
            not isinstance(source, Mapping)
            or not _self_hash_valid(source)
            or source.get("schema") != "zfd.parity_source_authority.v1"
            or source.get("source_id") != page_layer.get("source_id")
            or source.get("source_type") != "target_manuscript"
            or source.get("asset_sha256") != page_row.get("image_sha256")
            or page_layer.get("source_receipt_sha256") != source.get("receipt_sha256")
        ):
            failures.append("CANONICAL_PAGE_SOURCE_AUTHORITY_MISMATCH")

    record_by_identity: dict[tuple[str, str], Mapping[str, Any]] = {}
    record_results: dict[tuple[str, str], bool] = {}
    for row in records:
        if (
            not isinstance(row, Mapping)
            or row.get("schema") != PARITY_RECORD_SCHEMA
            or not _self_hash_valid(row)
        ):
            failures.append("CANONICAL_RECORD_INVALID")
            continue
        page_id = row.get("page_id")
        region_id = row.get("region_id")
        identity = (str(page_id), str(region_id))
        page_row = page_by_id.get(str(page_id))
        region_row = region_by_identity.get(identity)
        layers = row.get("layers")
        if page_row is None or region_row is None or not isinstance(layers, Mapping):
            failures.append("CANONICAL_RECORD_IDENTITY_INVALID")
            continue
        if identity in record_by_identity:
            failures.append("CANONICAL_RECORD_DUPLICATE")
            continue
        if (
            row.get("page_manifest_receipt_sha256") != page_row.get("receipt_sha256")
            or row.get("region_manifest_receipt_sha256") != region_row.get("receipt_sha256")
        ):
            failures.append("CANONICAL_RECORD_MANIFEST_LINK_MISMATCH")
        page_layer = layers.get("page")
        region_layer = layers.get("region")
        if (
            not isinstance(page_layer, Mapping)
            or page_layer.get("receipt_sha256") != page_row.get("page_layer_receipt_sha256")
            or page_layer.get("page_id") != page_id
            or page_layer.get("image_sha256") != page_row.get("image_sha256")
        ):
            failures.append("CANONICAL_RECORD_PAGE_LAYER_MISMATCH")
        if (
            not isinstance(region_layer, Mapping)
            or region_layer.get("receipt_sha256")
            != region_row.get("region_layer_receipt_sha256")
            or region_layer.get("region_id") != region_id
            or region_layer.get("geometry_sha256") != region_row.get("geometry_sha256")
        ):
            failures.append("CANONICAL_RECORD_REGION_LAYER_MISMATCH")

        parity_report = validate_page_parity(layers, evidence_authority)
        confirmed = row.get("confirmed_translated")
        if not isinstance(confirmed, bool) or confirmed != parity_report.ok:
            failures.append("CANONICAL_RECORD_PARITY_RESULT_MISMATCH")
        reason_codes = row.get("reason_codes")
        if not isinstance(reason_codes, list) or tuple(reason_codes) != parity_report.reasons:
            failures.append("CANONICAL_RECORD_PARITY_REASONS_MISMATCH")
        if parity_report.ok and row.get("review_state") not in {"approved", "adjudicated"}:
            failures.append("CANONICAL_RECORD_REVIEW_UNAPPROVED")
        record_by_identity[identity] = row
        record_results[identity] = parity_report.ok

    if set(record_by_identity) != set(region_by_identity):
        failures.append("CANONICAL_REGION_RECORD_COVERAGE_MISMATCH")

    nontext_reviews = evidence_authority.get("nontext_reviews")
    reviewer_authority = evidence_authority.get("reviewers")
    disposition_by_page: dict[str, Mapping[str, Any]] = {}
    for row in page_dispositions:
        if (
            not isinstance(row, Mapping)
            or row.get("schema") != PAGE_DISPOSITION_SCHEMA
            or not _self_hash_valid(row)
        ):
            failures.append("PAGE_DISPOSITION_RECORD_INVALID")
            continue
        page_id = row.get("page_id")
        page_row = page_by_id.get(str(page_id))
        if page_row is None or page_id in disposition_by_page:
            failures.append("PAGE_DISPOSITION_IDENTITY_INVALID")
            continue
        expected_region_ids = sorted(regions_by_page.get(str(page_id), []))
        if row.get("region_ids") != expected_region_ids:
            failures.append("PAGE_DISPOSITION_REGION_SCOPE_MISMATCH")
        if row.get("page_manifest_receipt_sha256") != page_row.get("receipt_sha256"):
            failures.append("PAGE_DISPOSITION_MANIFEST_LINK_MISMATCH")
        confirmed = row.get("confirmed_translated")
        if expected_region_ids:
            expected_confirmed = all(
                record_results.get((str(page_id), region_id), False)
                for region_id in expected_region_ids
            )
            expected_disposition = "translated" if expected_confirmed else "unresolved"
            if (
                confirmed is not expected_confirmed
                or row.get("excluded_nontext") is not False
                or row.get("disposition") != expected_disposition
            ):
                failures.append("PAGE_DISPOSITION_PARITY_MISMATCH")
        else:
            review_hash = row.get("nontext_review_receipt_sha256")
            nontext_review = (
                nontext_reviews.get(review_hash)
                if isinstance(nontext_reviews, Mapping)
                else None
            )
            if (
                confirmed is not False
                or row.get("excluded_nontext") is not True
                or row.get("disposition") != "excluded_nontext"
                or row.get("review_state") != "adjudicated"
                or not isinstance(row.get("exclusion_reason"), str)
                or not row.get("exclusion_reason", "").strip()
            ):
                failures.append("NON_TEXT_PAGE_DISPOSITION_INVALID")
            if (
                not isinstance(nontext_review, Mapping)
                or not _self_hash_valid(nontext_review)
                or nontext_review.get("schema") != NON_TEXT_REVIEW_SCHEMA
                or nontext_review.get("page_id") != page_id
                or nontext_review.get("image_sha256") != page_row.get("image_sha256")
                or nontext_review.get("page_layer_receipt_sha256")
                != page_row.get("page_layer_receipt_sha256")
                or nontext_review.get("status") != "adjudicated"
                or nontext_review.get("basis") != "full_page_pixel_review"
                or nontext_review.get("exclusion_reason") != row.get("exclusion_reason")
            ):
                failures.append("NON_TEXT_PAGE_REVIEW_AUTHORITY_INVALID")
            else:
                reviewer_id = nontext_review.get("reviewer_id")
                adjudicator_id = nontext_review.get("adjudicator_id")
                if reviewer_id == adjudicator_id:
                    failures.append("NON_TEXT_PAGE_REVIEW_IDENTITIES_NOT_DISTINCT")
                for identity, role in (
                    (reviewer_id, "reviewer"),
                    (adjudicator_id, "adjudicator"),
                ):
                    reviewer = (
                        reviewer_authority.get(identity)
                        if isinstance(reviewer_authority, Mapping)
                        else None
                    )
                    if (
                        not isinstance(reviewer, Mapping)
                        or not _self_hash_valid(reviewer)
                        or reviewer.get("schema") != "zfd.parity_reviewer_authority.v1"
                        or reviewer.get("reviewer_id") != identity
                        or reviewer.get("role") != role
                        or reviewer.get("status") != "active"
                    ):
                        failures.append("NON_TEXT_PAGE_REVIEWER_AUTHORITY_INVALID")
        if confirmed is True and row.get("review_state") not in {"approved", "adjudicated"}:
            failures.append("PAGE_DISPOSITION_REVIEW_UNAPPROVED")
        disposition_by_page[str(page_id)] = row

    if set(disposition_by_page) != set(page_by_id):
        failures.append("CANONICAL_PAGE_DISPOSITION_COVERAGE_MISMATCH")

    confirmed_regions = sum(record_results.values())
    confirmed_pages = sum(
        row.get("confirmed_translated") is True for row in disposition_by_page.values()
    )
    excluded_nontext_pages = sum(
        row.get("excluded_nontext") is True for row in disposition_by_page.values()
    )
    expected_counts = {
        "total_pages": len(page_by_id),
        "total_regions": len(region_by_identity),
        "confirmed_translated_pages": confirmed_pages,
        "excluded_nontext_pages": excluded_nontext_pages,
        "confirmed_translated_regions": confirmed_regions,
        "unresolved_pages": len(page_by_id) - confirmed_pages - excluded_nontext_pages,
        "unresolved_regions": len(region_by_identity) - confirmed_regions,
    }
    for field, expected_value in expected_counts.items():
        if value.get(field) != expected_value:
            failures.append(f"{field.upper()}_RECOMPUTE_MISMATCH")
    return tuple(dict.fromkeys(failures))


def _receipt_failures(
    name: str,
    value: Any,
    authority: Any = None,
    specification: Mapping[str, Any] | None = None,
) -> tuple[str, ...]:
    if not isinstance(value, Mapping):
        return ("UNSTRUCTURED",) if value is not None else ("MISSING",)
    failures: list[str] = []
    if not _self_hash_valid(value):
        failures.append("SELF_HASH_INVALID")
    if value.get("ok") is not True and value.get("status") not in PASS_STATES:
        failures.append("STATE_NOT_PASSING")
    if value.get("stale") is True:
        failures.append("STALE")
    if value.get("errors"):
        failures.append("ERRORS_PRESENT")
    for field in (
        "failed_pages",
        "failed_regions",
        "missing_pages",
        "missing_regions",
        "unresolved_pages",
        "unresolved_regions",
        "split_leakage_count",
    ):
        if _positive_count(value.get(field)):
            failures.append(f"{field.upper()}_PRESENT")

    metric_receipt = any(
        token in name
        for token in ("metric", "calibration", "evaluation", "classification")
    )
    if metric_receipt:
        if value.get("schema") != "zfd.metric_claim_receipt.v1":
            failures.append("METRIC_RECEIPT_SCHEMA_INVALID")
        if value.get("receipt_type") != name:
            failures.append("RECEIPT_TYPE_MISMATCH")
        if value.get("issuer") != "zfd_image_native":
            failures.append("ISSUER_INVALID")
        if value.get("status") != "measured":
            failures.append("METRICS_NOT_MEASURED")
        reference_count = value.get("reference_characters")
        gold_count = value.get("adjudicated_gold_count")
        if not (_positive_count(reference_count) and _positive_count(gold_count)):
            failures.append("ADJUDICATED_GOLD_EMPTY")
        if value.get("accuracy_claim_allowed") is not True:
            failures.append("ACCURACY_CLAIM_BLOCKED")

    parity_receipt = name in PARITY_RECEIPT_TYPES
    if parity_receipt:
        failures.extend(
            _parity_authority_failures(name, value, authority, specification or {})
        )
        total_pages = value.get("total_pages")
        confirmed_pages = value.get("confirmed_translated_pages")
        excluded_pages = value.get("excluded_nontext_pages")
        if (
            not _positive_count(total_pages)
            or not _nonnegative_count(confirmed_pages)
            or not _nonnegative_count(excluded_pages)
            or confirmed_pages + excluded_pages != total_pages
        ):
            failures.append("CONFIRMED_TRANSLATED_PAGES_INCOMPLETE")
        total_regions = value.get("total_regions")
        confirmed_regions = value.get("confirmed_translated_regions")
        if (
            not _positive_count(total_regions)
            or not _nonnegative_count(confirmed_regions)
            or confirmed_regions != total_regions
        ):
            failures.append("CONFIRMED_TRANSLATED_REGIONS_INCOMPLETE")
        if value.get("review_state") not in {"approved", "adjudicated"}:
            failures.append("PARITY_REVIEW_UNAPPROVED")
    elif not metric_receipt:
        failures.append("AUTHORITY_VALIDATOR_UNSUPPORTED")
    return tuple(dict.fromkeys(failures))


def validate_claims(
    ledger: Mapping[str, Mapping[str, Any]],
    receipts: Mapping[str, Any],
    receipt_authority: Mapping[str, Any] | None = None,
) -> ClaimReport:
    if not isinstance(ledger, Mapping):
        return ClaimReport(
            (
                ClaimDecision(
                    "__ledger__",
                    False,
                    "blocked",
                    (),
                    ("CLAIM_LEDGER_MALFORMED",),
                ),
            )
        )
    receipt_values = receipts if isinstance(receipts, Mapping) else {}
    decisions: list[ClaimDecision] = []
    for name, specification in ledger.items():
        if not isinstance(specification, Mapping):
            decisions.append(
                ClaimDecision(name, False, "blocked", (), ("CLAIM_SPECIFICATION_MALFORMED",))
            )
            continue
        raw_required = specification.get("required_receipts")
        if (
            not isinstance(raw_required, (list, tuple))
            or not raw_required
            or any(not isinstance(item, str) or not item for item in raw_required)
            or len(set(raw_required)) != len(raw_required)
        ):
            decisions.append(
                ClaimDecision(
                    name,
                    False,
                    "blocked",
                    (),
                    ("CLAIM_REQUIRED_RECEIPTS_MALFORMED",),
                )
            )
            continue
        required = tuple(raw_required)
        receipt_failures = {
            receipt: _receipt_failures(
                receipt,
                receipt_values.get(receipt),
                receipt_authority.get(receipt) if isinstance(receipt_authority, Mapping) else None,
                specification,
            )
            for receipt in required
        }
        missing = tuple(receipt for receipt, failures in receipt_failures.items() if failures)
        declared_status = str(specification.get("status", "candidate"))
        raw_blockers = specification.get("blocking_reasons", ())
        declared_blockers = (
            tuple(raw_blockers)
            if isinstance(raw_blockers, (list, tuple))
            and all(isinstance(item, str) and item for item in raw_blockers)
            else ("CLAIM_BLOCKING_REASONS_MALFORMED",)
        )
        generated_blockers = tuple(
            f"RECEIPT_{receipt}:{failure}"
            for receipt, failures in receipt_failures.items()
            for failure in failures
        )
        status_blocker = (
            ()
            if declared_status in SUPPORTED_CLAIM_STATES
            else (f"CLAIM_STATUS_{declared_status.upper()}_NOT_SUPPORTED",)
        )
        all_blockers = tuple(dict.fromkeys((*declared_blockers, *status_blocker, *generated_blockers)))
        blocked = bool(all_blockers) or not required
        allowed = not missing and not blocked
        decisions.append(
            ClaimDecision(
                name=name,
                allowed=allowed,
                status="allowed" if allowed else "blocked",
                missing_receipts=missing,
                blocking_reasons=all_blockers,
            )
        )
    return ClaimReport(tuple(decisions))
