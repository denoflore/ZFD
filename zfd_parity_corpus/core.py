"""Materialise immutable corpus parity without promoting absent evidence."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable, Mapping
from uuid import uuid4

from zfd_image_native.claims import (
    CANONICAL_VOYNICH_PAGE_COUNT,
    CANONICAL_VOYNICH_PAGE_IDENTITY_SHA256,
)
from zfd_image_native.io import canonical_json, read_json, read_jsonl
from zfd_image_native.parity import EVIDENCE_AUTHORITY_SCHEMA, LAYERS, validate_page_parity
from zfd_image_native.receipts import validate_stage_a_receipts


PAGE_AUTHORITY_SCHEMA = "zfd.canonical_page_authority.v1"
REGION_AUTHORITY_SCHEMA = "zfd.canonical_region_authority.v1"
PARITY_RECORD_SCHEMA = "zfd.translation_parity_record.v1"
PAGE_DISPOSITION_SCHEMA = "zfd.page_translation_disposition.v1"
SUMMARY_SCHEMA = "zfd.parity_corpus_summary.v1"
PAGE_LAYER_SCHEMA = "zfd.parity_page.v1"
REGION_LAYER_SCHEMA = "zfd.parity_region.v1"
SOURCE_AUTHORITY_SCHEMA = "zfd.parity_source_authority.v1"
_EVIDENCE_BUCKETS = (
    "layers",
    "sources",
    "reviewers",
    "unknown_rejection",
    "adjudications",
    "nontext_reviews",
)
PARITY_FILES = (
    "page_authority.jsonl",
    "region_authority.jsonl",
    "records.jsonl",
    "page_dispositions.jsonl",
    "evidence_authority.json",
    "summary.json",
)
PROMOTION_AUTHORITY_PINNED = False
REGION_AUTHORITY_PINNED = False


@dataclass(frozen=True)
class CorpusParityBundle:
    page_authority: tuple[dict[str, Any], ...]
    region_authority: tuple[dict[str, Any], ...]
    records: tuple[dict[str, Any], ...]
    page_dispositions: tuple[dict[str, Any], ...]
    evidence_authority: dict[str, Any]
    summary: dict[str, Any]


@dataclass(frozen=True)
class _StageA:
    root: Path
    pages: tuple[dict[str, Any], ...]
    page_receipts: tuple[dict[str, Any], ...]
    regions: tuple[dict[str, Any], ...]
    page_parity: tuple[dict[str, Any], ...]
    region_parity: tuple[dict[str, Any], ...]
    run_receipt: dict[str, Any]
    summary: dict[str, Any]
    archival_integrity_ok: bool
    artifact_integrity_ok: bool
    freshness_ok: bool


def _value_sha256(value: Any) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _receipt(**fields: Any) -> dict[str, Any]:
    payload = {key: value for key, value in fields.items() if key != "receipt_sha256"}
    return {**payload, "receipt_sha256": _value_sha256(payload)}


def _receipt_valid(value: Any) -> bool:
    if not isinstance(value, Mapping):
        return False
    supplied = value.get("receipt_sha256")
    payload = {key: item for key, item in value.items() if key != "receipt_sha256"}
    return isinstance(supplied, str) and supplied == _value_sha256(payload)


def _unique(
    rows: Iterable[Mapping[str, Any]], key: str, code: str
) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        value = row.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(f"{code}_ID_INVALID")
        if value in result:
            raise ValueError(f"{code}_ID_DUPLICATE:{value}")
        result[value] = row
    return result


def _load_stage_a(
    receipt_root: str | Path,
    *,
    corpus_root: str | Path | None = None,
    repository_root: str | Path | None = None,
    manifest_path: str | Path | None = None,
) -> _StageA:
    root = Path(receipt_root).resolve()
    supplied_context = (corpus_root, repository_root, manifest_path)
    if any(value is not None for value in supplied_context) and any(
        value is None for value in supplied_context
    ):
        raise ValueError("STAGE_A_VALIDATION_CONTEXT_INCOMPLETE")
    report = validate_stage_a_receipts(
        root,
        corpus_root=corpus_root,
        repository_root=repository_root,
        manifest_path=manifest_path,
    )
    if not report.archival_integrity_ok:
        raise ValueError("STAGE_A_ARCHIVAL_INTEGRITY_INVALID:" + ",".join(report.archival_errors))
    if all(value is not None for value in supplied_context) and not report.ok:
        raise ValueError("STAGE_A_CURRENT_VALIDATION_INVALID:" + ",".join(report.errors))
    pages = tuple(read_jsonl(root / "voynich_pages.jsonl"))
    page_receipts = tuple(read_jsonl(root / "ocr_page_receipts.jsonl"))
    regions = tuple(read_jsonl(root / "voynich_regions.jsonl"))
    page_parity = tuple(read_jsonl(root / "page_parity.jsonl"))
    region_parity = tuple(read_jsonl(root / "region_parity.jsonl"))
    run_receipt = read_json(root / "ocr_run_receipt.json")
    summary = read_json(root / "corpus_stage_a_summary.json")
    if not isinstance(run_receipt, dict) or not isinstance(summary, dict):
        raise ValueError("STAGE_A_SUMMARY_MALFORMED")

    page_identity = sorted(
        (
            {
                "page_id": row.get("page_id"),
                "source_id": row.get("source_id"),
                "iiif_id": row.get("iiif_id"),
                "iiif_base_uri": row.get("iiif_base_uri"),
            }
            for row in pages
        ),
        key=lambda row: str(row["page_id"]),
    )
    if len(page_identity) != CANONICAL_VOYNICH_PAGE_COUNT:
        raise ValueError("STAGE_A_CANONICAL_PAGE_COUNT_MISMATCH")
    if _value_sha256(page_identity) != CANONICAL_VOYNICH_PAGE_IDENTITY_SHA256:
        raise ValueError("STAGE_A_CANONICAL_PAGE_IDENTITY_MISMATCH")

    page_by_id = _unique(pages, "page_id", "STAGE_A_PAGE")
    page_receipt_by_id = _unique(page_receipts, "page_id", "STAGE_A_PAGE_RECEIPT")
    page_parity_by_id = _unique(page_parity, "page_id", "STAGE_A_PAGE_PARITY")
    region_by_id = _unique(regions, "region_id", "STAGE_A_REGION")
    region_parity_by_id = _unique(region_parity, "region_id", "STAGE_A_REGION_PARITY")
    if set(page_by_id) != set(page_receipt_by_id) or set(page_by_id) != set(page_parity_by_id):
        raise ValueError("STAGE_A_PAGE_COVERAGE_MISMATCH")
    if set(region_by_id) != set(region_parity_by_id):
        raise ValueError("STAGE_A_REGION_COVERAGE_MISMATCH")
    for page_id, page in page_by_id.items():
        receipt = page_receipt_by_id[page_id]
        parity = page_parity_by_id[page_id]
        if not _receipt_valid(receipt) or not _receipt_valid(parity):
            raise ValueError(f"STAGE_A_PAGE_RECEIPT_INVALID:{page_id}")
        if any(
            receipt.get(field) != page.get(field)
            for field in ("page_id", "source_id", "iiif_id", "image_sha256")
        ):
            raise ValueError(f"STAGE_A_PAGE_IDENTITY_MISMATCH:{page_id}")
    regions_by_page: dict[str, list[str]] = {page_id: [] for page_id in page_by_id}
    for region_id, region in region_by_id.items():
        parity = region_parity_by_id[region_id]
        page = page_by_id.get(str(region.get("page_id")))
        page_receipt = page_receipt_by_id.get(str(region.get("page_id")))
        if page is None or page_receipt is None:
            raise ValueError(f"STAGE_A_REGION_PAGE_MISSING:{region_id}")
        if not _receipt_valid(region) or not _receipt_valid(parity):
            raise ValueError(f"STAGE_A_REGION_RECEIPT_INVALID:{region_id}")
        if (
            region.get("image_sha256") != page.get("image_sha256")
            or region.get("page_ocr_receipt_sha256") != page_receipt.get("receipt_sha256")
            or parity.get("region_receipt_sha256") != region.get("receipt_sha256")
            or parity.get("image_sha256") != page.get("image_sha256")
        ):
            raise ValueError(f"STAGE_A_REGION_IDENTITY_MISMATCH:{region_id}")
        regions_by_page[str(region.get("page_id"))].append(region_id)
    for page_id, parity in page_parity_by_id.items():
        if sorted(parity.get("region_ids", [])) != sorted(regions_by_page[page_id]):
            raise ValueError(f"STAGE_A_PAGE_REGION_SET_MISMATCH:{page_id}")
    if summary.get("total_pages") != len(pages) or summary.get("total_regions") != len(regions):
        raise ValueError("STAGE_A_SUMMARY_COUNT_MISMATCH")
    return _StageA(
        root=root,
        pages=tuple(sorted((dict(row) for row in pages), key=lambda row: row["page_id"])),
        page_receipts=tuple(
            sorted((dict(row) for row in page_receipts), key=lambda row: row["page_id"])
        ),
        regions=tuple(
            sorted(
                (dict(row) for row in regions),
                key=lambda row: (row["page_id"], row["region_id"]),
            )
        ),
        page_parity=tuple(
            sorted((dict(row) for row in page_parity), key=lambda row: row["page_id"])
        ),
        region_parity=tuple(
            sorted(
                (dict(row) for row in region_parity),
                key=lambda row: (row["page_id"], row["region_id"]),
            )
        ),
        run_receipt=dict(run_receipt),
        summary=dict(summary),
        archival_integrity_ok=report.archival_integrity_ok,
        artifact_integrity_ok=report.artifact_integrity_ok,
        freshness_ok=report.freshness_ok,
    )


def _merge_evidence(
    generated: dict[str, Any], overlay: Mapping[str, Any] | None
) -> dict[str, Any]:
    if overlay is None:
        return _receipt(**generated)
    if overlay.get("schema") != EVIDENCE_AUTHORITY_SCHEMA or not _receipt_valid(overlay):
        raise ValueError("EVIDENCE_OVERLAY_INVALID")
    merged: dict[str, Any] = {"schema": EVIDENCE_AUTHORITY_SCHEMA}
    for bucket in _EVIDENCE_BUCKETS:
        base = generated.get(bucket, {})
        supplied = overlay.get(bucket, {})
        if not isinstance(base, Mapping) or not isinstance(supplied, Mapping):
            raise ValueError(f"EVIDENCE_OVERLAY_BUCKET_INVALID:{bucket}")
        values = dict(base)
        for key, value in supplied.items():
            if key in values and values[key] != value:
                raise ValueError(f"EVIDENCE_OVERLAY_CONFLICT:{bucket}:{key}")
            values[str(key)] = value
        merged[bucket] = values
    return _receipt(**merged)


def _canonical_base(stage: _StageA) -> tuple[
    tuple[dict[str, Any], ...],
    tuple[dict[str, Any], ...],
    dict[str, dict[str, dict[str, Any]]],
]:
    page_receipt_by_id = {row["page_id"]: row for row in stage.page_receipts}
    page_layers: dict[str, dict[str, Any]] = {}
    region_layers: dict[str, dict[str, Any]] = {}
    sources: dict[str, dict[str, Any]] = {}
    page_authority: list[dict[str, Any]] = []
    page_manifest_by_id: dict[str, dict[str, Any]] = {}
    for page in stage.pages:
        source = _receipt(
            schema=SOURCE_AUTHORITY_SCHEMA,
            source_id=page["source_id"],
            source_type="target_manuscript",
            asset_sha256=page["image_sha256"],
            asset_id=page["page_id"],
            stable_locator=page["iiif_base_uri"],
            stage_a_page_receipt_sha256=page_receipt_by_id[page["page_id"]][
                "receipt_sha256"
            ],
        )
        sources[source["receipt_sha256"]] = source
        page_layer = _receipt(
            schema=PAGE_LAYER_SCHEMA,
            page_id=page["page_id"],
            source_id=page["source_id"],
            image_sha256=page["image_sha256"],
            source_receipt_sha256=source["receipt_sha256"],
        )
        page_layers[page_layer["receipt_sha256"]] = page_layer
        authority = _receipt(
            schema=PAGE_AUTHORITY_SCHEMA,
            page_id=page["page_id"],
            source_id=page["source_id"],
            iiif_id=page["iiif_id"],
            iiif_base_uri=page["iiif_base_uri"],
            image_sha256=page["image_sha256"],
            page_layer_receipt_sha256=page_layer["receipt_sha256"],
            stage_a_page_receipt_sha256=page_receipt_by_id[page["page_id"]][
                "receipt_sha256"
            ],
        )
        page_authority.append(authority)
        page_manifest_by_id[page["page_id"]] = authority

    region_authority: list[dict[str, Any]] = []
    for region in stage.regions:
        page_manifest = page_manifest_by_id[region["page_id"]]
        page_layer = page_layers[page_manifest["page_layer_receipt_sha256"]]
        geometry = region["polygon"]
        geometry_sha256 = _value_sha256(geometry)
        region_layer = _receipt(
            schema=REGION_LAYER_SCHEMA,
            page_id=region["page_id"],
            image_sha256=region["image_sha256"],
            region_id=region["region_id"],
            geometry=geometry,
            geometry_sha256=geometry_sha256,
            page_receipt_sha256=page_layer["receipt_sha256"],
        )
        region_layers[region_layer["receipt_sha256"]] = region_layer
        region_authority.append(
            _receipt(
                schema=REGION_AUTHORITY_SCHEMA,
                page_id=region["page_id"],
                region_id=region["region_id"],
                image_sha256=region["image_sha256"],
                geometry_sha256=geometry_sha256,
                page_manifest_receipt_sha256=page_manifest["receipt_sha256"],
                region_layer_receipt_sha256=region_layer["receipt_sha256"],
                stage_a_region_receipt_sha256=region["receipt_sha256"],
            )
        )
    evidence = {
        "layers": {"page": page_layers, "region": region_layers},
        "sources": sources,
        "reviewers": {},
        "unknown_rejection": {},
        "adjudications": {},
        "nontext_reviews": {},
    }
    return tuple(page_authority), tuple(region_authority), evidence


def _record(
    page_manifest: Mapping[str, Any],
    region_manifest: Mapping[str, Any],
    layers: Mapping[str, Mapping[str, Any]],
    evidence_authority: Mapping[str, Any],
    *,
    review_state: str,
) -> dict[str, Any]:
    report = validate_page_parity(layers, evidence_authority)
    return _receipt(
        schema=PARITY_RECORD_SCHEMA,
        page_id=page_manifest["page_id"],
        region_id=region_manifest["region_id"],
        page_manifest_receipt_sha256=page_manifest["receipt_sha256"],
        region_manifest_receipt_sha256=region_manifest["receipt_sha256"],
        layers=dict(layers),
        confirmed_translated=report.ok,
        reason_codes=list(report.reasons),
        review_state="approved" if report.ok else "unreviewed",
    )


def _summary(
    stage: _StageA,
    page_authority: tuple[dict[str, Any], ...],
    region_authority: tuple[dict[str, Any], ...],
    records: tuple[dict[str, Any], ...],
    dispositions: tuple[dict[str, Any], ...],
    evidence: Mapping[str, Any],
) -> dict[str, Any]:
    confirmed_regions = sum(row["confirmed_translated"] is True for row in records)
    confirmed_pages = sum(row["confirmed_translated"] is True for row in dispositions)
    return _receipt(
        schema=SUMMARY_SCHEMA,
        stage_a_run_id=stage.run_receipt.get("run_id"),
        stage_a_run_receipt_sha256=stage.run_receipt.get("receipt_sha256"),
        stage_a_archival_integrity_ok=stage.archival_integrity_ok,
        stage_a_artifact_integrity_ok=stage.artifact_integrity_ok,
        stage_a_freshness_ok=stage.freshness_ok,
        total_pages=len(page_authority),
        total_regions=len(region_authority),
        confirmed_translated_pages=confirmed_pages,
        confirmed_translated_regions=confirmed_regions,
        unresolved_pages=len(page_authority) - confirmed_pages,
        unresolved_regions=len(region_authority) - confirmed_regions,
        page_authority_sha256=_value_sha256(page_authority),
        region_authority_sha256=_value_sha256(region_authority),
        records_sha256=_value_sha256(records),
        page_dispositions_sha256=_value_sha256(dispositions),
        evidence_authority_receipt_sha256=evidence.get("receipt_sha256"),
        canonical_page_count=CANONICAL_VOYNICH_PAGE_COUNT,
        canonical_page_identity_sha256=CANONICAL_VOYNICH_PAGE_IDENTITY_SHA256,
        canonical_page_scope_ok=len(page_authority) == CANONICAL_VOYNICH_PAGE_COUNT,
        promotion_authority_pinned=PROMOTION_AUTHORITY_PINNED,
        region_authority_pinned=REGION_AUTHORITY_PINNED,
        completion_claim_allowed=PROMOTION_AUTHORITY_PINNED
        and REGION_AUTHORITY_PINNED
        and stage.archival_integrity_ok
        and stage.artifact_integrity_ok
        and stage.freshness_ok
        and confirmed_pages == len(page_authority)
        and confirmed_regions == len(region_authority),
    )


def build_corpus_parity(
    stage_a_receipts: str | Path,
    *,
    proposed_records: Iterable[Mapping[str, Any]] = (),
    evidence_overlay: Mapping[str, Any] | None = None,
    corpus_root: str | Path | None = None,
    repository_root: str | Path | None = None,
    manifest_path: str | Path | None = None,
) -> CorpusParityBundle:
    """Build canonical unresolved records, promoting only complete exact layer chains."""

    stage = _load_stage_a(
        stage_a_receipts,
        corpus_root=corpus_root,
        repository_root=repository_root,
        manifest_path=manifest_path,
    )
    page_authority, region_authority, generated_evidence = _canonical_base(stage)
    evidence = _merge_evidence(
        {"schema": EVIDENCE_AUTHORITY_SCHEMA, **generated_evidence}, evidence_overlay
    )
    page_by_id = {row["page_id"]: row for row in page_authority}
    region_by_id = {row["region_id"]: row for row in region_authority}
    proposals: dict[tuple[str, str], Mapping[str, Any]] = {}
    for proposal in proposed_records:
        if proposal.get("schema") != PARITY_RECORD_SCHEMA:
            raise ValueError("LAYER_RECORD_SCHEMA_INVALID")
        layers = proposal.get("layers")
        if not isinstance(layers, Mapping):
            raise ValueError("LAYER_RECORD_LAYERS_INVALID")
        if not set(layers).issubset(LAYERS):
            raise ValueError("LAYER_RECORD_KEYS_INVALID")
        identity = (str(proposal.get("page_id")), str(proposal.get("region_id")))
        if identity in proposals:
            raise ValueError("LAYER_RECORD_ID_DUPLICATE")
        if identity[0] not in page_by_id or identity[1] not in region_by_id:
            raise ValueError("LAYER_RECORD_ID_UNEXPECTED")
        if region_by_id[identity[1]].get("page_id") != identity[0]:
            raise ValueError("LAYER_RECORD_PAGE_REGION_MISMATCH")
        proposals[identity] = proposal
    if proposals or evidence_overlay is not None:
        raise ValueError("PARITY_PROMOTION_AUTHORITY_UNPINNED")

    records: list[dict[str, Any]] = []
    for region_manifest in region_authority:
        page_manifest = page_by_id[region_manifest["page_id"]]
        identity = (page_manifest["page_id"], region_manifest["region_id"])
        proposal = proposals.get(identity)
        if proposal is None:
            layers = {
                "page": evidence["layers"]["page"][
                    page_manifest["page_layer_receipt_sha256"]
                ],
                "region": evidence["layers"]["region"][
                    region_manifest["region_layer_receipt_sha256"]
                ],
            }
            review_state = "unreviewed"
        else:
            layers = proposal.get("layers")
            if not isinstance(layers, Mapping):
                raise ValueError("LAYER_RECORD_LAYERS_INVALID")
            if not set(layers).issubset(LAYERS):
                raise ValueError("LAYER_RECORD_KEYS_INVALID")
            expected_page = evidence["layers"]["page"][
                page_manifest["page_layer_receipt_sha256"]
            ]
            expected_region = evidence["layers"]["region"][
                region_manifest["region_layer_receipt_sha256"]
            ]
            if layers.get("page") != expected_page:
                raise ValueError("LAYER_RECORD_PAGE_LINK_MISMATCH")
            if layers.get("region") != expected_region:
                raise ValueError("LAYER_RECORD_REGION_LINK_MISMATCH")
            review_state = str(proposal.get("review_state", "unreviewed"))
        records.append(
            _record(
                page_manifest,
                region_manifest,
                layers,
                evidence,
                review_state=review_state,
            )
        )

    records_by_page: dict[str, list[dict[str, Any]]] = {
        row["page_id"]: [] for row in page_authority
    }
    for record in records:
        records_by_page[record["page_id"]].append(record)
    dispositions: list[dict[str, Any]] = []
    for page in page_authority:
        page_records = records_by_page[page["page_id"]]
        confirmed = bool(page_records) and all(
            row["confirmed_translated"] is True for row in page_records
        )
        dispositions.append(
            _receipt(
                schema=PAGE_DISPOSITION_SCHEMA,
                page_id=page["page_id"],
                page_manifest_receipt_sha256=page["receipt_sha256"],
                region_ids=sorted(row["region_id"] for row in page_records),
                confirmed_translated=confirmed,
                excluded_nontext=False,
                disposition="translated" if confirmed else "unresolved",
                review_state="adjudicated" if confirmed else "unreviewed",
                exclusion_reason=None,
                nontext_review_receipt_sha256=None,
            )
        )
    record_tuple = tuple(records)
    disposition_tuple = tuple(dispositions)
    summary = _summary(
        stage,
        page_authority,
        region_authority,
        record_tuple,
        disposition_tuple,
        evidence,
    )
    return CorpusParityBundle(
        page_authority=page_authority,
        region_authority=region_authority,
        records=record_tuple,
        page_dispositions=disposition_tuple,
        evidence_authority=evidence,
        summary=summary,
    )


def validate_corpus_parity_bundle(
    bundle: CorpusParityBundle,
    stage_a_receipts: str | Path,
    *,
    corpus_root: str | Path | None = None,
    repository_root: str | Path | None = None,
    manifest_path: str | Path | None = None,
) -> tuple[str, ...]:
    """Recompute the full unresolved or promoted corpus parity authority."""

    errors: list[str] = []
    try:
        stage = _load_stage_a(
            stage_a_receipts,
            corpus_root=corpus_root,
            repository_root=repository_root,
            manifest_path=manifest_path,
        )
        expected_pages, expected_regions, generated_evidence = _canonical_base(stage)
        expected_evidence = _merge_evidence(
            {"schema": EVIDENCE_AUTHORITY_SCHEMA, **generated_evidence}, None
        )
    except (OSError, TypeError, ValueError) as error:
        return (f"STAGE_A_INVALID:{error}",)

    def index(
        rows: Iterable[Mapping[str, Any]], key: str, label: str
    ) -> dict[str, Mapping[str, Any]]:
        result: dict[str, Mapping[str, Any]] = {}
        for row in rows:
            value = row.get(key)
            if not isinstance(value, str) or not value:
                errors.append(f"{label}_ID_INVALID")
                continue
            if value in result:
                errors.append(f"{label}_ID_DUPLICATE")
                continue
            result[value] = row
            if not _receipt_valid(row):
                errors.append(f"{label}_RECEIPT_INVALID")
        return result

    pages = index(bundle.page_authority, "page_id", "PAGE_AUTHORITY")
    regions = index(bundle.region_authority, "region_id", "REGION_AUTHORITY")
    expected_page_by_id = {row["page_id"]: row for row in expected_pages}
    expected_region_by_id = {row["region_id"]: row for row in expected_regions}
    if pages != expected_page_by_id:
        errors.append("PAGE_AUTHORITY_COVERAGE_MISMATCH")
    if regions != expected_region_by_id:
        errors.append("REGION_AUTHORITY_COVERAGE_MISMATCH")
    if not _receipt_valid(bundle.evidence_authority):
        errors.append("EVIDENCE_AUTHORITY_RECEIPT_INVALID")
    if bundle.evidence_authority.get("schema") != EVIDENCE_AUTHORITY_SCHEMA:
        errors.append("EVIDENCE_AUTHORITY_SCHEMA_INVALID")
    if bundle.evidence_authority != expected_evidence:
        errors.append("EVIDENCE_AUTHORITY_UNPINNED")
    for bucket in _EVIDENCE_BUCKETS:
        if not isinstance(bundle.evidence_authority.get(bucket), Mapping):
            errors.append(f"EVIDENCE_AUTHORITY_{bucket.upper()}_INVALID")

    records = index(bundle.records, "region_id", "PARITY_RECORD")
    if set(records) != set(expected_region_by_id):
        errors.append("PARITY_RECORD_COVERAGE_MISMATCH")
    for region_id, record in records.items():
        if record.get("schema") != PARITY_RECORD_SCHEMA:
            errors.append("PARITY_RECORD_SCHEMA_INVALID")
        region = regions.get(region_id)
        page = pages.get(str(record.get("page_id")))
        if region is None or page is None:
            errors.append("PARITY_RECORD_IDENTITY_INVALID")
            continue
        if (
            record.get("page_manifest_receipt_sha256") != page.get("receipt_sha256")
            or record.get("region_manifest_receipt_sha256")
            != region.get("receipt_sha256")
        ):
            errors.append("PARITY_RECORD_MANIFEST_LINK_MISMATCH")
        layers = record.get("layers")
        if not isinstance(layers, Mapping):
            errors.append("PARITY_RECORD_LAYERS_INVALID")
            continue
        if not set(layers).issubset(LAYERS):
            errors.append("PARITY_RECORD_LAYER_KEYS_INVALID")
        if set(layers) != {"page", "region"}:
            errors.append("PARITY_RECORD_PROMOTION_AUTHORITY_UNPINNED")
        page_layer = layers.get("page")
        region_layer = layers.get("region")
        if (
            not isinstance(page_layer, Mapping)
            or page_layer.get("receipt_sha256") != page.get("page_layer_receipt_sha256")
            or page_layer.get("page_id") != page.get("page_id")
            or page_layer.get("image_sha256") != page.get("image_sha256")
        ):
            errors.append("PARITY_RECORD_PAGE_LAYER_MISMATCH")
        if (
            not isinstance(region_layer, Mapping)
            or region_layer.get("receipt_sha256")
            != region.get("region_layer_receipt_sha256")
            or region_layer.get("page_id") != page.get("page_id")
            or region_layer.get("region_id") != region_id
            or region_layer.get("geometry_sha256") != region.get("geometry_sha256")
        ):
            errors.append("PARITY_RECORD_REGION_LAYER_MISMATCH")
        report = validate_page_parity(layers, bundle.evidence_authority)
        if record.get("confirmed_translated") is not report.ok:
            errors.append("PARITY_RECORD_RESULT_MISMATCH")
        if record.get("confirmed_translated") is True:
            errors.append("PARITY_RECORD_PROMOTION_AUTHORITY_UNPINNED")
        if record.get("reason_codes") != list(report.reasons):
            errors.append("PARITY_RECORD_REASONS_MISMATCH")
        expected_review_state = "approved" if report.ok else "unreviewed"
        if record.get("review_state") != expected_review_state:
            errors.append("PARITY_RECORD_REVIEW_STATE_MISMATCH")

    dispositions = index(bundle.page_dispositions, "page_id", "PAGE_DISPOSITION")
    if set(dispositions) != set(expected_page_by_id):
        errors.append("PAGE_DISPOSITION_COVERAGE_MISMATCH")
    records_by_page: dict[str, list[Mapping[str, Any]]] = {
        page_id: [] for page_id in expected_page_by_id
    }
    for record in records.values():
        if str(record.get("page_id")) in records_by_page:
            records_by_page[str(record.get("page_id"))].append(record)
    for page_id, disposition in dispositions.items():
        if disposition.get("schema") != PAGE_DISPOSITION_SCHEMA:
            errors.append("PAGE_DISPOSITION_SCHEMA_INVALID")
        expected_ids = sorted(row["region_id"] for row in records_by_page[page_id])
        confirmed = bool(expected_ids) and all(
            row.get("confirmed_translated") is True for row in records_by_page[page_id]
        )
        expected_review_state = "adjudicated" if confirmed else "unreviewed"
        if (
            disposition.get("page_manifest_receipt_sha256")
            != expected_page_by_id[page_id]["receipt_sha256"]
            or disposition.get("region_ids") != expected_ids
            or disposition.get("confirmed_translated") is not confirmed
            or disposition.get("excluded_nontext") is not False
            or disposition.get("disposition")
            != ("translated" if confirmed else "unresolved")
            or disposition.get("review_state") != expected_review_state
            or disposition.get("exclusion_reason") is not None
            or disposition.get("nontext_review_receipt_sha256") is not None
        ):
            errors.append("PAGE_DISPOSITION_RECOMPUTE_MISMATCH")

    expected_summary = _summary(
        stage,
        tuple(bundle.page_authority),
        tuple(bundle.region_authority),
        tuple(bundle.records),
        tuple(bundle.page_dispositions),
        bundle.evidence_authority,
    )
    if bundle.summary != expected_summary or not _receipt_valid(bundle.summary):
        errors.append("SUMMARY_RECOMPUTE_MISMATCH")
    return tuple(dict.fromkeys(errors))


def _jsonl_bytes(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return "".join(canonical_json(row) + "\n" for row in rows).encode("utf-8")


def _json_bytes(value: Mapping[str, Any]) -> bytes:
    return (canonical_json(value) + "\n").encode("utf-8")


def write_corpus_parity_new(output_root: str | Path, bundle: CorpusParityBundle) -> None:
    """Create one immutable bundle without overwriting any existing path."""

    root = Path(output_root)
    root.parent.mkdir(parents=True, exist_ok=True)
    if root.exists():
        raise FileExistsError(root)
    staging = root.with_name(f".{root.name}.staging-{uuid4().hex}")
    staging.mkdir(exist_ok=False)
    payloads = (
        ("page_authority.jsonl", _jsonl_bytes(bundle.page_authority)),
        ("region_authority.jsonl", _jsonl_bytes(bundle.region_authority)),
        ("records.jsonl", _jsonl_bytes(bundle.records)),
        ("page_dispositions.jsonl", _jsonl_bytes(bundle.page_dispositions)),
        ("evidence_authority.json", _json_bytes(bundle.evidence_authority)),
        ("summary.json", _json_bytes(bundle.summary)),
    )
    try:
        for name, payload in payloads:
            with (staging / name).open("xb") as stream:
                stream.write(payload)
        if root.exists():
            raise FileExistsError(root)
        staging.rename(root)
    except BaseException:
        if staging.exists():
            for child in staging.iterdir():
                if child.is_file():
                    child.unlink()
            staging.rmdir()
        raise


def read_corpus_parity(root: str | Path) -> CorpusParityBundle:
    """Read the exact six file authority surface."""

    base = Path(root)
    actual = {path.name for path in base.iterdir() if path.is_file()}
    if actual != set(PARITY_FILES):
        raise ValueError("PARITY_FILE_SET_INVALID")
    evidence = read_json(base / "evidence_authority.json")
    summary = read_json(base / "summary.json")
    if not isinstance(evidence, dict) or not isinstance(summary, dict):
        raise ValueError("PARITY_JSON_MALFORMED")
    return CorpusParityBundle(
        page_authority=tuple(read_jsonl(base / "page_authority.jsonl")),
        region_authority=tuple(read_jsonl(base / "region_authority.jsonl")),
        records=tuple(read_jsonl(base / "records.jsonl")),
        page_dispositions=tuple(read_jsonl(base / "page_dispositions.jsonl")),
        evidence_authority=evidence,
        summary=summary,
    )
