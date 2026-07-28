"""Quarantined Kraken geometry comparison bound to frozen primary receipts."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
from importlib.metadata import version
from pathlib import Path
from typing import Any, Iterable

from PIL import Image

from .io import canonical_json, read_json, read_jsonl, sha256_file, write_json
from .manifest import load_page_manifest
from .model_registry import validate_model_registry
from .models import PageRecord


SCHEMA_VERSION = "1.0.0"


@dataclass(frozen=True)
class ExternalSegmentationResult:
    segmentation: Any
    disposition: str
    warnings: tuple[str, ...]


def _value_sha256(value: Any) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _points(value: Any, *, width: int, height: int, record: str) -> list[list[int]]:
    if not isinstance(value, (list, tuple)) or len(value) < 2:
        raise ValueError(f"Geometry has fewer than two points: {record}")
    points: list[list[int]] = []
    for point in value:
        if not isinstance(point, (list, tuple)) or len(point) != 2:
            raise ValueError(f"Geometry point is malformed: {record}")
        x, y = point
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            raise ValueError(f"Geometry coordinate is not numeric: {record}")
        px, py = int(round(x)), int(round(y))
        if not 0 <= px < width or not 0 <= py < height:
            raise ValueError(f"Geometry leaves image bounds: {record}")
        points.append([px, py])
    return points


def _bbox(*geometries: Iterable[Iterable[int]]) -> list[int]:
    points = [point for geometry in geometries for point in geometry]
    left = min(point[0] for point in points)
    top = min(point[1] for point in points)
    right = max(point[0] for point in points)
    bottom = max(point[1] for point in points)
    return [left, top, right - left + 1, bottom - top + 1]


def _frozen_page_receipt(receipts_root: Path, page: PageRecord) -> dict[str, Any]:
    run = read_json(receipts_root / "ocr_run_receipt.json")
    rows = read_jsonl(receipts_root / "ocr_page_receipts.jsonl")
    matches = [row for row in rows if row.get("page_id") == page.page_id]
    if len(matches) != 1:
        raise ValueError(f"Frozen primary page receipt is not unique: {page.page_id}")
    row = matches[0]
    if row.get("record_state") != "frozen":
        raise ValueError(f"Primary page receipt is not frozen: {page.page_id}")
    if row.get("image_sha256") != page.image_sha256:
        raise ValueError(f"Primary page receipt image hash differs: {page.page_id}")
    if row.get("run_id") != run.get("run_id"):
        raise ValueError(f"Primary page receipt run differs: {page.page_id}")
    if row.get("run_receipt_sha256") != run.get("receipt_sha256"):
        raise ValueError(f"Primary page receipt run hash differs: {page.page_id}")
    return row


def _verify_frozen_page_receipt(
    run: dict[str, Any], row: dict[str, Any], page: PageRecord
) -> None:
    if row.get("record_state") != "frozen":
        raise ValueError(f"Primary page receipt is not frozen: {page.page_id}")
    if row.get("image_sha256") != page.image_sha256:
        raise ValueError(f"Primary page receipt image hash differs: {page.page_id}")
    if row.get("run_id") != run.get("run_id"):
        raise ValueError(f"Primary page receipt run differs: {page.page_id}")
    if row.get("run_receipt_sha256") != run.get("receipt_sha256"):
        raise ValueError(f"Primary page receipt run hash differs: {page.page_id}")


def _model_record(register_path: Path, model_id: str) -> dict[str, Any]:
    payload = read_json(register_path)
    matches = [row for row in payload.get("models", []) if row.get("model_id") == model_id]
    if len(matches) != 1:
        raise ValueError(f"Segmentation model record is not unique: {model_id}")
    row = matches[0]
    if row.get("model_type") != "segmentation":
        raise ValueError(f"Model is not registered for segmentation: {model_id}")
    if row.get("primary_lane_allowed") is not False:
        raise ValueError(f"Comparative model is not quarantined: {model_id}")
    if len(row.get("files", [])) != 1:
        raise ValueError(f"Segmentation model must identify exactly one model file: {model_id}")
    return row


def freeze_geometry_comparison(
    *,
    page: PageRecord,
    frozen_page_receipt: dict[str, Any],
    model: dict[str, Any],
    segmentation: Any,
    software_version: str,
    external_segmentation_disposition: str = "strict",
    external_warnings: Iterable[str] = (),
) -> dict[str, Any]:
    """Convert a model result to stable, content addressed, label-free geometry."""

    if not page.image_sha256 or not page.width or not page.height:
        raise ValueError(f"Page identity is incomplete: {page.page_id}")
    width, height = page.width, page.height
    model_file = model["files"][0]

    raw_regions: list[tuple[str, dict[str, Any]]] = []
    for region_type, regions in sorted(segmentation.regions.items()):
        for region in regions:
            boundary = _points(
                region.boundary,
                width=width,
                height=height,
                record=f"region:{region.id}",
            )
            content = {
                "region_type": str(region_type),
                "boundary": boundary,
                "bbox": _bbox(boundary),
            }
            raw_regions.append((str(region.id), content))
    raw_regions.sort(key=lambda item: canonical_json(item[1]))
    source_to_stable: dict[str, str] = {}
    region_rows: list[dict[str, Any]] = []
    for source_id, content in raw_regions:
        stable_id = "sha256:" + _value_sha256(
            {
                "page_id": page.page_id,
                "model_sha256": model_file["sha256"],
                **content,
            }
        )
        if stable_id in {row["region_id"] for row in region_rows}:
            raise ValueError(f"Duplicate comparative region geometry: {stable_id}")
        source_to_stable[source_id] = stable_id
        region_rows.append({"region_id": stable_id, **content, "line_ids": []})

    line_rows: list[dict[str, Any]] = []
    for line in segmentation.lines:
        baseline = _points(
            line.baseline,
            width=width,
            height=height,
            record=f"line-baseline:{line.id}",
        )
        boundary = _points(
            line.boundary,
            width=width,
            height=height,
            record=f"line-boundary:{line.id}",
        )
        region_ids = sorted(
            source_to_stable[source_id]
            for source_id in (getattr(line, "regions", None) or [])
            if source_id in source_to_stable
        )
        content = {
            "baseline": baseline,
            "boundary": boundary,
            "bbox": _bbox(baseline, boundary),
            "region_ids": region_ids,
        }
        line_id = "sha256:" + _value_sha256(
            {
                "page_id": page.page_id,
                "model_sha256": model_file["sha256"],
                **content,
            }
        )
        line_rows.append(
            {
                "line_id": line_id,
                **content,
                "diplomatic_label": None,
                "recognition_confidence": None,
            }
        )
    line_rows.sort(key=lambda row: (row["bbox"][1], row["bbox"][0], row["line_id"]))
    if len({row["line_id"] for row in line_rows}) != len(line_rows):
        raise ValueError("Duplicate comparative line geometry")
    region_by_id = {row["region_id"]: row for row in region_rows}
    for line in line_rows:
        for region_id in line["region_ids"]:
            region_by_id[region_id]["line_ids"].append(line["line_id"])

    warnings = tuple(str(warning) for warning in external_warnings)
    allowed_dispositions = {
        "strict",
        "tolerant_after_strict_topology_failure",
    }
    if external_segmentation_disposition not in allowed_dispositions:
        raise ValueError("External segmentation disposition is invalid")
    if external_segmentation_disposition == "strict" and warnings:
        raise ValueError("Strict external segmentation cannot carry fallback warnings")
    if external_segmentation_disposition != "strict" and not warnings:
        raise ValueError("Tolerant external segmentation must preserve the strict failure")

    payload = {
        "schema": "zfd.segmentation_comparison.v1",
        "schema_version": SCHEMA_VERSION,
        "page_id": page.page_id,
        "source_id": page.source_id,
        "image_sha256": page.image_sha256,
        "width": width,
        "height": height,
        "primary_run_id": frozen_page_receipt["run_id"],
        "primary_page_receipt_sha256": frozen_page_receipt["receipt_sha256"],
        "model_id": model["model_id"],
        "model_sha256": model_file["sha256"],
        "model_pinned_revision": model["pinned_revision"],
        "software": model["software"],
        "software_runtime_version": software_version,
        "primary_lane_allowed": False,
        "review_state": "unreviewed",
        "disposition": "comparative_geometry_unreviewed",
        "regions": region_rows,
        "lines": line_rows,
        "recognition_output": None,
    }
    if external_segmentation_disposition != "strict":
        payload["external_segmentation_disposition"] = external_segmentation_disposition
        payload["external_warnings"] = list(warnings)
    comparison_id = "sha256:" + _value_sha256(payload)
    receipt = {**payload, "comparison_id": comparison_id}
    return {**receipt, "receipt_sha256": _value_sha256(receipt)}


def validate_geometry_comparison(path: str | Path) -> tuple[str, ...]:
    """Return machine-readable errors for a saved comparative geometry receipt."""

    payload = read_json(path)
    if not isinstance(payload, dict):
        return ("COMPARISON_MALFORMED",)
    errors: list[str] = []
    supplied_receipt_hash = payload.get("receipt_sha256")
    receipt_payload = {key: value for key, value in payload.items() if key != "receipt_sha256"}
    if supplied_receipt_hash != _value_sha256(receipt_payload):
        errors.append("COMPARISON_RECEIPT_HASH_MISMATCH")
    supplied_id = payload.get("comparison_id")
    comparison_payload = {
        key: value
        for key, value in receipt_payload.items()
        if key != "comparison_id"
    }
    if supplied_id != "sha256:" + _value_sha256(comparison_payload):
        errors.append("COMPARISON_ID_MISMATCH")
    if payload.get("primary_lane_allowed") is not False:
        errors.append("COMPARISON_PRIMARY_LANE_NOT_BLOCKED")
    if payload.get("review_state") != "unreviewed":
        errors.append("COMPARISON_REVIEW_STATE_INVALID")
    if payload.get("disposition") != "comparative_geometry_unreviewed":
        errors.append("COMPARISON_DISPOSITION_INVALID")
    if payload.get("recognition_output") is not None:
        errors.append("COMPARISON_RECOGNITION_OUTPUT_PRESENT")
    external_disposition = payload.get("external_segmentation_disposition", "strict")
    external_warnings = payload.get("external_warnings", [])
    if external_disposition not in {
        "strict",
        "tolerant_after_strict_topology_failure",
    }:
        errors.append("COMPARISON_EXTERNAL_DISPOSITION_INVALID")
    if not isinstance(external_warnings, list) or any(
        not isinstance(warning, str) or not warning for warning in external_warnings
    ):
        errors.append("COMPARISON_EXTERNAL_WARNINGS_INVALID")
    elif external_disposition == "strict" and external_warnings:
        errors.append("COMPARISON_STRICT_EXTERNAL_WARNINGS_PRESENT")
    elif external_disposition != "strict" and not external_warnings:
        errors.append("COMPARISON_TOLERANT_WARNING_MISSING")
    width, height = payload.get("width"), payload.get("height")
    if not isinstance(width, int) or width <= 0 or not isinstance(height, int) or height <= 0:
        errors.append("COMPARISON_DIMENSIONS_INVALID")
        return tuple(errors)

    regions = payload.get("regions")
    lines = payload.get("lines")
    if not isinstance(regions, list) or not isinstance(lines, list):
        errors.append("COMPARISON_GEOMETRY_MALFORMED")
        return tuple(errors)
    region_ids = [row.get("region_id") for row in regions if isinstance(row, dict)]
    line_ids = [row.get("line_id") for row in lines if isinstance(row, dict)]
    if len(region_ids) != len(regions) or len(set(region_ids)) != len(region_ids):
        errors.append("COMPARISON_REGION_IDS_INVALID")
    if len(line_ids) != len(lines) or len(set(line_ids)) != len(line_ids):
        errors.append("COMPARISON_LINE_IDS_INVALID")
    region_set = set(region_ids)
    line_set = set(line_ids)
    for region in regions:
        if not isinstance(region, dict):
            continue
        if any(line_id not in line_set for line_id in region.get("line_ids", [])):
            errors.append(f"COMPARISON_REGION_LINE_JOIN_INVALID:{region.get('region_id')}")
    for line in lines:
        if not isinstance(line, dict):
            continue
        line_id = line.get("line_id")
        if line.get("diplomatic_label") is not None or line.get("recognition_confidence") is not None:
            errors.append(f"COMPARISON_LABEL_PRESENT:{line_id}")
        if any(region_id not in region_set for region_id in line.get("region_ids", [])):
            errors.append(f"COMPARISON_LINE_REGION_JOIN_INVALID:{line_id}")
        try:
            _points(line.get("baseline"), width=width, height=height, record=str(line_id))
            _points(line.get("boundary"), width=width, height=height, record=str(line_id))
        except ValueError:
            errors.append(f"COMPARISON_LINE_GEOMETRY_INVALID:{line_id}")
    return tuple(errors)


def validate_corpus_geometry_comparison(
    summary_path: str | Path,
    manifest_path: str | Path | None = None,
) -> tuple[str, ...]:
    """Validate a whole-corpus comparison summary and every joined page receipt."""

    path = Path(summary_path)
    try:
        payload = read_json(path)
    except (OSError, ValueError):
        return ("CORPUS_COMPARISON_MALFORMED",)
    if not isinstance(payload, dict):
        return ("CORPUS_COMPARISON_MALFORMED",)

    errors: list[str] = []
    supplied_receipt_hash = payload.get("receipt_sha256")
    receipt_payload = {
        key: value for key, value in payload.items() if key != "receipt_sha256"
    }
    if supplied_receipt_hash != _value_sha256(receipt_payload):
        errors.append("CORPUS_RECEIPT_HASH_MISMATCH")
    supplied_id = payload.get("summary_id")
    summary_payload = {
        key: value for key, value in receipt_payload.items() if key != "summary_id"
    }
    if supplied_id != "sha256:" + _value_sha256(summary_payload):
        errors.append("CORPUS_SUMMARY_ID_MISMATCH")
    if payload.get("schema") != "zfd.segmentation_comparison_corpus.v1":
        errors.append("CORPUS_SCHEMA_INVALID")
    if payload.get("primary_lane_allowed") is not False:
        errors.append("CORPUS_PRIMARY_LANE_NOT_BLOCKED")
    if payload.get("metrics_status") != "not_measured":
        errors.append("CORPUS_METRICS_STATUS_INVALID")
    if payload.get("review_state") != "unreviewed":
        errors.append("CORPUS_REVIEW_STATE_INVALID")

    pages = payload.get("pages")
    failures = payload.get("failures")
    if not isinstance(pages, list) or not isinstance(failures, list):
        errors.append("CORPUS_PAGE_LISTS_MALFORMED")
        return tuple(errors)
    processed_count = payload.get("processed_page_count")
    failed_count = payload.get("failed_page_count")
    input_count = payload.get("input_page_count")
    if processed_count != len(pages):
        errors.append("CORPUS_PROCESSED_COUNT_MISMATCH")
    if failed_count != len(failures):
        errors.append("CORPUS_FAILED_COUNT_MISMATCH")
    if not all(isinstance(value, int) and value >= 0 for value in (processed_count, failed_count, input_count)):
        errors.append("CORPUS_COUNTS_INVALID")
    elif processed_count + failed_count != input_count:
        errors.append("CORPUS_INPUT_COUNT_MISMATCH")
    if isinstance(failed_count, int) and failed_count:
        errors.append(f"CORPUS_COMPARISON_INCOMPLETE:{failed_count}")

    page_ids = [row.get("page_id") for row in pages if isinstance(row, dict)]
    failure_ids = [row.get("page_id") for row in failures if isinstance(row, dict)]
    if len(page_ids) != len(pages) or len(set(page_ids)) != len(page_ids):
        errors.append("CORPUS_PAGE_IDS_INVALID")
    if len(failure_ids) != len(failures) or len(set(failure_ids)) != len(failure_ids):
        errors.append("CORPUS_FAILURE_IDS_INVALID")
    if set(page_ids) & set(failure_ids):
        errors.append("CORPUS_SUCCESS_FAILURE_OVERLAP")

    summary_root = path.parent.resolve()
    expected_records: set[str] = set()
    primary_lines = 0
    comparative_lines = 0
    comparative_regions = 0
    for row in pages:
        if not isinstance(row, dict):
            continue
        page_id = str(row.get("page_id"))
        record_name = row.get("comparison_record")
        if not isinstance(record_name, str) or not record_name:
            errors.append(f"CORPUS_PAGE_RECORD_MISSING:{page_id}")
            continue
        record_path = (summary_root / record_name).resolve()
        if record_path.parent != summary_root:
            errors.append(f"CORPUS_PAGE_RECORD_OUTSIDE:{page_id}")
            continue
        expected_records.add(record_path.name)
        if not record_path.is_file():
            errors.append(f"CORPUS_PAGE_RECORD_MISSING:{page_id}")
            continue
        record_errors = validate_geometry_comparison(record_path)
        errors.extend(
            f"CORPUS_PAGE_INVALID:{page_id}:{error}" for error in record_errors
        )
        record = read_json(record_path)
        expected = {
            "page_id": row.get("page_id"),
            "image_sha256": row.get("image_sha256"),
            "comparison_id": row.get("comparison_id"),
            "receipt_sha256": row.get("comparison_receipt_sha256"),
        }
        if any(record.get(field) != value for field, value in expected.items()):
            errors.append(f"CORPUS_PAGE_RECEIPT_MISMATCH:{page_id}")
        if len(record.get("lines", [])) != row.get("comparative_line_count"):
            errors.append(f"CORPUS_PAGE_LINE_COUNT_MISMATCH:{page_id}")
        if len(record.get("regions", [])) != row.get("comparative_region_count"):
            errors.append(f"CORPUS_PAGE_REGION_COUNT_MISMATCH:{page_id}")
        if isinstance(row.get("primary_line_count"), int):
            primary_lines += row["primary_line_count"]
        comparative_lines += len(record.get("lines", []))
        comparative_regions += len(record.get("regions", []))

    actual_records = {item.name for item in summary_root.glob("*.kraken.json")}
    if actual_records != expected_records:
        errors.append("CORPUS_COMPARISON_FILE_SET_MISMATCH")
    if payload.get("primary_total_lines") != primary_lines:
        errors.append("CORPUS_PRIMARY_TOTAL_LINES_MISMATCH")
    if payload.get("comparative_total_lines") != comparative_lines:
        errors.append("CORPUS_COMPARATIVE_TOTAL_LINES_MISMATCH")
    if payload.get("comparative_total_regions") != comparative_regions:
        errors.append("CORPUS_COMPARATIVE_TOTAL_REGIONS_MISMATCH")

    if manifest_path is not None:
        try:
            manifest_ids = {page.page_id for page in load_page_manifest(manifest_path)}
        except (OSError, ValueError):
            errors.append("CORPUS_MANIFEST_MALFORMED")
        else:
            if set(page_ids) | set(failure_ids) != manifest_ids:
                errors.append("CORPUS_MANIFEST_COVERAGE_MISMATCH")
            if input_count != len(manifest_ids):
                errors.append("CORPUS_MANIFEST_COUNT_MISMATCH")
    return tuple(errors)


def _reusable_comparison(
    path: Path,
    *,
    page: PageRecord,
    frozen: dict[str, Any],
    model: dict[str, Any],
) -> dict[str, Any] | None:
    if not path.is_file() or validate_geometry_comparison(path):
        return None
    payload = read_json(path)
    expected = {
        "page_id": page.page_id,
        "image_sha256": page.image_sha256,
        "primary_run_id": frozen.get("run_id"),
        "primary_page_receipt_sha256": frozen.get("receipt_sha256"),
        "model_id": model.get("model_id"),
        "model_sha256": model["files"][0].get("sha256"),
    }
    if any(payload.get(field) != value for field, value in expected.items()):
        return None
    return payload


def _external_segment(
    blla: Any, source: Image.Image, network: Any
) -> ExternalSegmentationResult:
    """Run the external model while preserving its exception as page evidence."""

    try:
        segmentation = blla.segment(
            source.convert("RGB"),
            model=network,
            device="cpu",
            raise_on_error=True,
        )
    except Exception as error:
        error_type = f"{type(error).__module__}.{type(error).__name__}"
        strict_failure = f"{error_type}:{error}"
        if error_type != "shapely.errors.GEOSException":
            raise RuntimeError(f"external_segment_failure:{strict_failure}") from error
        try:
            segmentation = blla.segment(
                source.convert("RGB"),
                model=network,
                device="cpu",
                raise_on_error=False,
            )
        except Exception as tolerant_error:
            tolerant_type = (
                f"{type(tolerant_error).__module__}.{type(tolerant_error).__name__}"
            )
            raise RuntimeError(
                "external_segment_failure:"
                f"strict={strict_failure};tolerant={tolerant_type}:{tolerant_error}"
            ) from tolerant_error
        return ExternalSegmentationResult(
            segmentation=segmentation,
            disposition="tolerant_after_strict_topology_failure",
            warnings=(strict_failure,),
        )
    return ExternalSegmentationResult(
        segmentation=segmentation,
        disposition="strict",
        warnings=(),
    )


def run_comparison(
    *,
    manifest_path: Path,
    page_id: str,
    receipts_root: Path,
    register_path: Path,
    model_id: str,
    repository_root: Path,
) -> dict[str, Any]:
    report = validate_model_registry(
        register_path,
        repository_root=repository_root,
        require_cache=True,
    )
    if not report.ok:
        raise ValueError("Model register failed validation: " + ",".join(report.errors))
    pages = {page.page_id: page for page in load_page_manifest(manifest_path)}
    if page_id not in pages:
        raise ValueError(f"Unknown page ID: {page_id}")
    page = pages[page_id]
    if not page.image_path or not page.image_sha256:
        raise ValueError(f"Page pixels are not registered: {page_id}")
    image_path = repository_root / page.image_path
    if not image_path.is_file() or sha256_file(image_path) != page.image_sha256:
        raise ValueError(f"Page pixel checksum mismatch: {page_id}")
    frozen = _frozen_page_receipt(receipts_root, page)
    model = _model_record(register_path, model_id)
    model_path = repository_root / model["files"][0]["cache_relpath"]

    from kraken import blla
    from kraken.lib import vgsl

    network = vgsl.TorchVGSLModel.load_model(model_path)
    with Image.open(image_path) as source:
        external = _external_segment(blla, source, network)
    return freeze_geometry_comparison(
        page=page,
        frozen_page_receipt=frozen,
        model=model,
        segmentation=external.segmentation,
        software_version=version("kraken"),
        external_segmentation_disposition=external.disposition,
        external_warnings=external.warnings,
    )


def run_corpus_comparison(
    *,
    manifest_path: Path,
    receipts_root: Path,
    register_path: Path,
    model_id: str,
    repository_root: Path,
    output_dir: Path,
) -> dict[str, Any]:
    """Run one quarantined segmentation model over every frozen page."""

    report = validate_model_registry(
        register_path,
        repository_root=repository_root,
        require_cache=True,
    )
    if not report.ok:
        raise ValueError("Model register failed validation: " + ",".join(report.errors))
    model = _model_record(register_path, model_id)
    model_file = model["files"][0]
    model_path = repository_root / model_file["cache_relpath"]
    pages = load_page_manifest(manifest_path)
    if len({page.page_id for page in pages}) != len(pages):
        raise ValueError("Page manifest contains duplicate IDs")
    run = read_json(receipts_root / "ocr_run_receipt.json")
    frozen_rows = read_jsonl(receipts_root / "ocr_page_receipts.jsonl")
    frozen_by_page = {row.get("page_id"): row for row in frozen_rows}
    if len(frozen_by_page) != len(frozen_rows):
        raise ValueError("Frozen primary page receipts contain duplicate IDs")
    if set(frozen_by_page) != {page.page_id for page in pages}:
        raise ValueError("Frozen primary page coverage differs from the manifest")

    from kraken import blla
    from kraken.lib import vgsl

    network = vgsl.TorchVGSLModel.load_model(model_path)
    runtime_version = version("kraken")
    output_dir.mkdir(parents=True, exist_ok=True)
    page_results: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for index, page in enumerate(pages, start=1):
        try:
            frozen = frozen_by_page[page.page_id]
            _verify_frozen_page_receipt(run, frozen, page)
            if not page.image_path or not page.image_sha256:
                raise ValueError(f"Page pixels are not registered: {page.page_id}")
            image_path = repository_root / page.image_path
            if not image_path.is_file() or sha256_file(image_path) != page.image_sha256:
                raise ValueError(f"Page pixel checksum mismatch: {page.page_id}")
            filename = f"{page.iiif_id}.kraken.json"
            target = output_dir / filename
            comparison = _reusable_comparison(
                target,
                page=page,
                frozen=frozen,
                model=model,
            )
            if comparison is None:
                if network is None:
                    network = vgsl.TorchVGSLModel.load_model(model_path)
                with Image.open(image_path) as source:
                    external = _external_segment(blla, source, network)
                comparison = freeze_geometry_comparison(
                    page=page,
                    frozen_page_receipt=frozen,
                    model=model,
                    segmentation=external.segmentation,
                    software_version=runtime_version,
                    external_segmentation_disposition=external.disposition,
                    external_warnings=external.warnings,
                )
                write_json(target, comparison)
            page_results.append(
                {
                    "page_id": page.page_id,
                    "iiif_id": page.iiif_id,
                    "image_sha256": page.image_sha256,
                    "comparison_id": comparison["comparison_id"],
                    "comparison_receipt_sha256": comparison["receipt_sha256"],
                    "comparison_record": filename,
                    "primary_line_count": frozen.get("line_count"),
                    "comparative_line_count": len(comparison["lines"]),
                    "comparative_region_count": len(comparison["regions"]),
                    "review_state": "unreviewed",
                    "disposition": "comparative_geometry_unreviewed",
                }
            )
        except (OSError, RuntimeError, ValueError) as error:
            failures.append(
                {
                    "page_id": page.page_id,
                    "error_type": f"{type(error).__module__}.{type(error).__name__}",
                    "error": str(error),
                }
            )
        if index == 1 or index % 10 == 0 or index == len(pages):
            print(
                canonical_json(
                    {
                        "progress": index,
                        "total": len(pages),
                        "processed": len(page_results),
                        "failed": len(failures),
                    }
                ),
                flush=True,
            )

    summary_payload = {
        "schema": "zfd.segmentation_comparison_corpus.v1",
        "schema_version": SCHEMA_VERSION,
        "model_id": model["model_id"],
        "model_sha256": model_file["sha256"],
        "model_pinned_revision": model["pinned_revision"],
        "software": model["software"],
        "software_runtime_version": runtime_version,
        "primary_run_id": run.get("run_id"),
        "primary_run_receipt_sha256": run.get("receipt_sha256"),
        "input_page_count": len(pages),
        "processed_page_count": len(page_results),
        "failed_page_count": len(failures),
        "primary_total_lines": sum(
            row["primary_line_count"] for row in page_results if isinstance(row["primary_line_count"], int)
        ),
        "comparative_total_lines": sum(row["comparative_line_count"] for row in page_results),
        "comparative_total_regions": sum(row["comparative_region_count"] for row in page_results),
        "primary_lane_allowed": False,
        "metrics_status": "not_measured",
        "review_state": "unreviewed",
        "pages": page_results,
        "failures": failures,
    }
    summary_id = "sha256:" + _value_sha256(summary_payload)
    summary_receipt = {**summary_payload, "summary_id": summary_id}
    summary = {**summary_receipt, "receipt_sha256": _value_sha256(summary_receipt)}
    write_json(output_dir / "summary.json", summary)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m zfd_image_native.kraken_compare")
    parser.add_argument("--manifest", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--page-id")
    mode.add_argument("--all", action="store_true")
    parser.add_argument("--receipts", required=True, type=Path)
    parser.add_argument("--model-register", required=True, type=Path)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.all:
            result = run_corpus_comparison(
                manifest_path=args.manifest,
                receipts_root=args.receipts,
                register_path=args.model_register,
                model_id=args.model_id,
                repository_root=args.repository_root.resolve(),
                output_dir=args.output,
            )
            print(
                canonical_json(
                    {
                        "summary_id": result["summary_id"],
                        "processed_pages": result["processed_page_count"],
                        "failed_pages": result["failed_page_count"],
                        "lines": result["comparative_total_lines"],
                        "review_state": result["review_state"],
                        "output": str(args.output / "summary.json"),
                    }
                )
            )
            return 0 if result["failed_page_count"] == 0 else 1
        result = run_comparison(
            manifest_path=args.manifest,
            page_id=args.page_id,
            receipts_root=args.receipts,
            register_path=args.model_register,
            model_id=args.model_id,
            repository_root=args.repository_root.resolve(),
        )
        write_json(args.output, result)
        print(
            canonical_json(
                {
                    "comparison_id": result["comparison_id"],
                    "page_id": result["page_id"],
                    "regions": len(result["regions"]),
                    "lines": len(result["lines"]),
                    "review_state": result["review_state"],
                    "output": str(args.output),
                }
            )
        )
        return 0
    except (OSError, RuntimeError, ValueError) as error:
        print(f"ERROR: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
