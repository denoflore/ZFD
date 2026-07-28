"""Portable, exact receipts for provisional image segmentation outputs."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
import platform
import subprocess
from typing import Any, Iterable

import cv2
import numpy as np
import PIL
from PIL import Image

from . import __version__
from .io import canonical_json, read_json, read_jsonl, sha256_file, write_json, write_jsonl
from .manifest import load_page_manifest
from .models import PageRecord
from .ocr import OpenSetConfig


SCHEMA_VERSION = "2.1.0"
PARITY_SCHEMA_VERSION = "1.0.0"
SEGMENTED_DISPOSITIONS = frozenset(
    {"segmented_unrecognized", "segmented_unrecognized_layout_review"}
)
NO_TEXT_DISPOSITIONS = frozenset(
    {"no_text_detected", "no_text_detected_layout_review"}
)
STAGE_A_DISPOSITIONS = SEGMENTED_DISPOSITIONS | NO_TEXT_DISPOSITIONS
UNRESOLVED_BLOCKERS = (
    "DIPLOMATIC_RECORD_MISSING",
    "TERMINOLOGY_RECORD_MISSING",
    "TRANSLATION_RECORD_MISSING",
    "REVIEW_STATE_MISSING",
    "ADJUDICATION_STATE_MISSING",
    "HELD_OUT_METRICS_MISSING",
)


@dataclass(frozen=True)
class FrozenStageASummary:
    schema_version: str
    total_pages: int
    frozen_pages: int
    total_regions: int
    frozen_regions: int
    total_lines: int
    total_graphemes: int
    unknown_graphemes: int
    total_rejected_components: int
    total_component_candidates: int
    segmentation_complete: bool
    recognition_status: str
    metrics_status: str
    translation_status: str
    confirmed_translated_pages: int
    confirmed_translated_regions: int
    authoritative_manifest_sha256: str
    config_sha256: str | None
    run_id: str
    run_receipt_sha256: str


@dataclass(frozen=True)
class ReceiptValidationReport:
    ok: bool
    archival_integrity_ok: bool
    artifact_integrity_ok: bool
    freshness_ok: bool
    page_count: int
    region_count: int
    confirmed_translated_pages: int
    confirmed_translated_regions: int
    archival_errors: tuple[str, ...]
    artifact_errors: tuple[str, ...]
    freshness_errors: tuple[str, ...]
    errors: tuple[str, ...]


def _value_sha256(value: Any) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _with_receipt_hash(row: dict[str, Any]) -> dict[str, Any]:
    payload = {key: value for key, value in row.items() if key != "receipt_sha256"}
    return {**payload, "receipt_sha256": _value_sha256(payload)}


def _receipt_hash_is_valid(row: dict[str, Any]) -> bool:
    supplied = row.get("receipt_sha256")
    payload = {key: value for key, value in row.items() if key != "receipt_sha256"}
    return isinstance(supplied, str) and supplied == _value_sha256(payload)


def _implementation_sha256() -> str:
    package_root = Path(__file__).resolve().parent
    inventory = [
        {"path": path.relative_to(package_root).as_posix(), "sha256": sha256_file(path)}
        for path in sorted(package_root.rglob("*.py"))
    ]
    return _value_sha256(inventory)


def _config_sha256(config: OpenSetConfig) -> str:
    return _value_sha256(asdict(config))


def _dependency_identity() -> dict[str, str]:
    return {
        "package": f"zfd-image-native=={__version__}",
        "python_implementation": platform.python_implementation(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "opencv_python": cv2.__version__,
        "pillow": PIL.__version__,
    }


def _page_authority_sha256(pages: Iterable[PageRecord | dict[str, Any]]) -> str:
    authority: list[dict[str, Any]] = []
    for page in pages:
        row = page if isinstance(page, dict) else page.__dict__
        authority.append(
            {
                "page_id": row.get("page_id"),
                "source_id": row.get("source_id"),
                "iiif_id": row.get("iiif_id"),
                "iiif_base_uri": row.get("iiif_base_uri"),
            }
        )
    return _value_sha256(authority)


def _current_source_freshness_errors(
    current_pages: Iterable[PageRecord],
    frozen_pages: dict[str, dict[str, Any]],
    repository_root: Path,
) -> list[str]:
    """Recheck each current manifest image against pixels and frozen identity."""

    errors: list[str] = []
    resolved_root = repository_root.resolve()
    for page in current_pages:
        page_id = page.page_id
        frozen = frozen_pages.get(page_id)
        if frozen is None:
            errors.append(f"CURRENT_PAGE_RECORD_MISSING:{page_id}")
            frozen = {}
        for field in ("source_id", "iiif_id", "iiif_base_uri"):
            if getattr(page, field) != frozen.get(field):
                errors.append(f"CURRENT_PAGE_{field.upper()}_MISMATCH:{page_id}")

        if not page.image_path:
            errors.append(f"CURRENT_PAGE_IMAGE_PATH_MISSING:{page_id}")
            continue
        image_path = Path(page.image_path)
        if not image_path.is_absolute():
            image_path = resolved_root / image_path
        image_path = image_path.resolve()
        try:
            portable_path = image_path.relative_to(resolved_root).as_posix()
        except ValueError:
            errors.append(f"CURRENT_PAGE_IMAGE_OUTSIDE_REPOSITORY:{page_id}")
            continue
        if frozen.get("image_path") != portable_path:
            errors.append(f"CURRENT_PAGE_IMAGE_PATH_MISMATCH:{page_id}")
        if not image_path.is_file():
            errors.append(f"CURRENT_PAGE_IMAGE_MISSING:{page_id}")
            continue

        actual_hash = sha256_file(image_path)
        try:
            manifest_hash = _require_hash(page.image_sha256, f"{page_id} image hash")
        except ValueError:
            errors.append(f"CURRENT_PAGE_IMAGE_SHA256_INVALID:{page_id}")
            manifest_hash = None
        try:
            frozen_hash = _require_hash(
                frozen.get("image_sha256"),
                f"{page_id} frozen image hash",
            )
        except ValueError:
            errors.append(f"CURRENT_FROZEN_PAGE_IMAGE_SHA256_INVALID:{page_id}")
            frozen_hash = None
        expected_hashes = {
            digest for digest in (manifest_hash, frozen_hash) if digest is not None
        }
        if expected_hashes and any(actual_hash != digest for digest in expected_hashes):
            errors.append(f"CURRENT_PAGE_PIXELS_SHA256_MISMATCH:{page_id}")
        if (
            manifest_hash is not None
            and frozen_hash is not None
            and frozen_hash != manifest_hash
        ):
            errors.append(f"CURRENT_PAGE_IMAGE_SHA256_MISMATCH:{page_id}")

        try:
            with Image.open(image_path) as image:
                image.load()
                actual_width, actual_height = image.size
                actual_mime = Image.MIME.get(image.format or "", "application/octet-stream")
        except OSError:
            errors.append(f"CURRENT_PAGE_IMAGE_INVALID:{page_id}")
            continue
        for field, actual in (("width", actual_width), ("height", actual_height)):
            manifest_value = getattr(page, field)
            if manifest_value != actual:
                errors.append(f"CURRENT_PAGE_IMAGE_{field.upper()}_MISMATCH:{page_id}")
            if frozen.get(field) != manifest_value:
                errors.append(f"CURRENT_PAGE_{field.upper()}_MISMATCH:{page_id}")
        if page.mime_type is not None and page.mime_type != actual_mime:
            errors.append(f"CURRENT_PAGE_IMAGE_MIME_MISMATCH:{page_id}")
        if frozen.get("mime_type") != page.mime_type:
            errors.append(f"CURRENT_PAGE_MIME_TYPE_MISMATCH:{page_id}")
    return errors


def _git_state(repository_root: Path) -> tuple[str | None, bool | None]:
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repository_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=repository_root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True,
            ).stdout.strip()
        )
        return commit, dirty
    except (OSError, subprocess.CalledProcessError):
        return None, None


def _unique(rows: Iterable[dict[str, Any]], key: str, label: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        value = row.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label} has a blank {key}")
        if value in indexed:
            raise ValueError(f"Duplicate {label} {key}: {value}")
        indexed[value] = row
    return indexed


def _portable(path: str | Path, repository_root: Path) -> str:
    resolved = Path(path).resolve()
    try:
        relative = resolved.relative_to(repository_root.resolve())
    except ValueError as error:
        raise ValueError(f"Receipt path is outside repository root: {resolved}") from error
    return relative.as_posix()


def _require_hash(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{label} must be a SHA256 digest")
    try:
        int(value, 16)
    except ValueError as error:
        raise ValueError(f"{label} must be hexadecimal") from error
    return value.lower()


def _require_box(value: Any, width: int, height: int, label: str) -> list[int]:
    if not isinstance(value, list) or len(value) != 4 or not all(isinstance(item, int) for item in value):
        raise ValueError(f"{label} bbox must contain four integers")
    x, y, box_width, box_height = value
    if x < 0 or y < 0 or box_width <= 0 or box_height <= 0:
        raise ValueError(f"{label} bbox is invalid")
    if x + box_width > width or y + box_height > height:
        raise ValueError(f"{label} bbox is outside page bounds")
    return value


def _require_polygon(value: Any, width: int, height: int, label: str) -> list[list[int]]:
    if not isinstance(value, list) or len(value) < 4:
        raise ValueError(f"{label} polygon must contain at least four points")
    for point in value:
        if (
            not isinstance(point, list)
            or len(point) != 2
            or not all(isinstance(item, int) for item in point)
            or point[0] < 0
            or point[1] < 0
            or point[0] > width
            or point[1] > height
        ):
            raise ValueError(f"{label} polygon is outside page bounds")
    return value


def _validate_page_source(page: PageRecord) -> Path:
    if page.acquisition_status != "verified":
        raise ValueError(f"Page source is not verified: {page.page_id}")
    if not page.image_path or not page.image_sha256 or page.width is None or page.height is None:
        raise ValueError(f"Page source identity is incomplete: {page.page_id}")
    image_path = Path(page.image_path)
    if not image_path.is_file():
        raise ValueError(f"Page pixels are missing: {page.page_id}")
    actual_hash = sha256_file(image_path)
    if actual_hash != _require_hash(page.image_sha256, f"{page.page_id} image hash"):
        raise ValueError(f"Page image checksum mismatch: {page.page_id}")
    return image_path


def _validate_page_ocr(
    page: PageRecord,
    payload: dict[str, Any],
    aggregate_regions: dict[str, dict[str, Any]],
    disposition: dict[str, Any],
) -> tuple[
    list[dict[str, Any]],
    int,
    int,
    int,
    str | None,
    list[dict[str, Any]],
    list[dict[str, str]],
    dict[str, int],
]:
    identity = {
        "page_id": page.page_id,
        "source_id": page.source_id,
        "page_sha256": page.image_sha256,
        "width": page.width,
        "height": page.height,
    }
    for field, expected in identity.items():
        if payload.get(field) != expected:
            raise ValueError(f"OCR {field} mismatch for {page.page_id}")
    config_hash = _require_hash(payload.get("config_sha256"), f"{page.page_id} config hash")
    page_disposition = payload.get("disposition")
    if page_disposition not in STAGE_A_DISPOSITIONS:
        raise ValueError(f"Unsupported Stage A disposition for {page.page_id}")
    if disposition.get("disposition") != page_disposition:
        raise ValueError(f"Page disposition aggregate mismatch for {page.page_id}")
    layout_disposition = payload.get("layout_disposition")
    if layout_disposition not in {None, "cartesian_provisional", "layout_review_required"}:
        raise ValueError(f"Unsupported layout disposition for {page.page_id}")
    if page_disposition.endswith("_layout_review") and layout_disposition != "layout_review_required":
        raise ValueError(f"Layout review disposition is missing review evidence for {page.page_id}")
    if page_disposition in {"segmented_unrecognized", "no_text_detected"} and (
        layout_disposition == "layout_review_required"
    ):
        raise ValueError(f"Layout review evidence is inconsistent for {page.page_id}")

    regions = payload.get("regions")
    lines = payload.get("lines")
    graphemes = payload.get("graphemes")
    if not all(isinstance(items, list) for items in (regions, lines, graphemes)):
        raise ValueError(f"OCR collections are malformed for {page.page_id}")
    region_index = _unique(regions, "region_id", "OCR region")
    line_index = _unique(lines, "line_id", "OCR line")
    grapheme_index = _unique(graphemes, "grapheme_id", "OCR grapheme")
    rejected_components = payload.get("rejected_components", [])
    if not isinstance(rejected_components, list):
        raise ValueError(f"Rejected component collection is malformed for {page.page_id}")
    rejected_index = _unique(rejected_components, "component_id", "rejected component")
    for component_id, component in rejected_index.items():
        _require_box(component.get("bbox"), page.width, page.height, component_id)
        _require_polygon(component.get("polygon"), page.width, page.height, component_id)
        if not isinstance(component.get("reason"), str) or not component["reason"].strip():
            raise ValueError(f"Rejected component reason is missing for {component_id}")

    for region_id, region in region_index.items():
        _require_box(region.get("bbox"), page.width, page.height, region_id)
        _require_polygon(region.get("polygon"), page.width, page.height, region_id)
        expected_lines = region.get("line_ids")
        actual_lines = [line_id for line_id, line in line_index.items() if line.get("region_id") == region_id]
        if expected_lines != actual_lines:
            raise ValueError(f"Region to line join mismatch for {region_id}")
        aggregate = aggregate_regions.get(region_id)
        expected_aggregate = {
            **region,
            "page_id": page.page_id,
            "image_sha256": page.image_sha256,
            "ocr_record": f"pages/{page.iiif_id}.json",
        }
        if aggregate is None or canonical_json(aggregate) != canonical_json(expected_aggregate):
            raise ValueError(f"Region aggregate mismatch for {region_id}")

    line_geometry: list[dict[str, str]] = []
    line_geometry_modes: Counter[str] = Counter()
    for line_id, line in line_index.items():
        region_id = line.get("region_id")
        if region_id not in region_index:
            raise ValueError(f"Line to region join mismatch for {line_id}")
        _require_box(line.get("bbox"), page.width, page.height, line_id)
        _require_polygon(line.get("polygon"), page.width, page.height, line_id)
        expected_graphemes = line.get("grapheme_ids")
        actual_graphemes = [
            grapheme_id
            for grapheme_id, grapheme in grapheme_index.items()
            if grapheme.get("line_id") == line_id
        ]
        if expected_graphemes != actual_graphemes:
            raise ValueError(f"Line to grapheme join mismatch for {line_id}")
        geometry_mode = line.get("geometry_mode")
        if geometry_mode is not None:
            if not isinstance(geometry_mode, str) or not geometry_mode.strip():
                raise ValueError(f"Line geometry mode is invalid for {line_id}")
            line_geometry.append({"line_id": line_id, "geometry_mode": geometry_mode})
            line_geometry_modes[geometry_mode] += 1

    unknown_count = 0
    for grapheme_id, grapheme in grapheme_index.items():
        line_id = grapheme.get("line_id")
        region_id = grapheme.get("region_id")
        if line_id not in line_index or region_id not in region_index:
            raise ValueError(f"Grapheme parent join mismatch for {grapheme_id}")
        if line_index[line_id].get("region_id") != region_id:
            raise ValueError(f"Grapheme region lineage mismatch for {grapheme_id}")
        _require_box(grapheme.get("bbox"), page.width, page.height, grapheme_id)
        _require_polygon(grapheme.get("polygon"), page.width, page.height, grapheme_id)
        if grapheme.get("diplomatic_label") is not None:
            raise ValueError(f"Stage A contains an unadjudicated diplomatic label: {grapheme_id}")
        if grapheme.get("unknown_score") != 1.0 or grapheme.get("recognition_confidence") != 0.0:
            raise ValueError(f"Stage A unknown confidence semantics are invalid: {grapheme_id}")
        alternatives = grapheme.get("alternatives")
        if not isinstance(alternatives, list) or not alternatives:
            raise ValueError(f"Stage A alternatives are missing: {grapheme_id}")
        unknown_count += 1

    if set(region_index) != {key for key, row in aggregate_regions.items() if row.get("page_id") == page.page_id}:
        raise ValueError(f"Page region aggregate set mismatch for {page.page_id}")
    if page_disposition in NO_TEXT_DISPOSITIONS and (regions or lines or graphemes):
        raise ValueError(f"No text disposition contains OCR geometry for {page.page_id}")
    if page_disposition in SEGMENTED_DISPOSITIONS and not lines:
        raise ValueError(f"Segmented disposition has no lines for {page.page_id}")
    if config_hash != payload["config_sha256"]:
        raise ValueError(f"Config hash casing is noncanonical for {page.page_id}")
    return (
        list(region_index.values()),
        len(line_index),
        len(grapheme_index),
        unknown_count,
        layout_disposition,
        list(rejected_index.values()),
        line_geometry,
        dict(sorted(line_geometry_modes.items())),
    )


def _component_evidence(
    graphemes: list[dict[str, Any]], rejected_components: list[dict[str, Any]]
) -> dict[str, Any]:
    grapheme_hash = _value_sha256(graphemes)
    rejected_hash = _value_sha256(rejected_components)
    grapheme_count = len(graphemes)
    rejected_count = len(rejected_components)
    component_count = grapheme_count + rejected_count
    return {
        "grapheme_evidence_sha256": grapheme_hash,
        "rejected_component_evidence_sha256": rejected_hash,
        "component_candidate_count": component_count,
        "component_disposition_set_sha256": _value_sha256(
            {
                "grapheme_count": grapheme_count,
                "grapheme_evidence_sha256": grapheme_hash,
                "rejected_component_count": rejected_count,
                "rejected_component_evidence_sha256": rejected_hash,
                "component_candidate_count": component_count,
            }
        ),
    }


def _ocr_artifact_integrity_errors(
    page_receipts: dict[str, dict[str, Any]],
    *,
    corpus_root: Path | None,
    repository_root: Path | None,
) -> list[str]:
    if corpus_root is None and repository_root is None:
        return ["OCR_ARTIFACT_CONTEXT_MISSING"]

    explicit_corpus_root = corpus_root.resolve() if corpus_root is not None else None
    resolved_repository_root = (
        repository_root.resolve() if repository_root is not None else None
    )
    errors: list[str] = []
    for page_id, receipt in page_receipts.items():
        if explicit_corpus_root is not None:
            relative = receipt.get("ocr_artifact_path")
            if not isinstance(relative, str) or not relative:
                iiif_id = receipt.get("iiif_id")
                relative = f"pages/{iiif_id}.json" if iiif_id else None
            base = explicit_corpus_root
        else:
            relative = receipt.get("ocr_record")
            base = resolved_repository_root
        if not isinstance(relative, str) or not relative or base is None:
            errors.append(f"OCR_ARTIFACT_PATH_MISSING:{page_id}")
            continue
        artifact = (base / relative).resolve()
        try:
            artifact.relative_to(base)
        except ValueError:
            errors.append(f"OCR_ARTIFACT_PATH_OUTSIDE_ROOT:{page_id}")
            continue
        if not artifact.is_file():
            errors.append(f"OCR_ARTIFACT_MISSING:{page_id}")
            continue
        expected_hash = receipt.get("ocr_artifact_sha256", receipt.get("ocr_sha256"))
        if not isinstance(expected_hash, str) or sha256_file(artifact) != expected_hash:
            errors.append(f"OCR_ARTIFACT_SHA256_MISMATCH:{page_id}")
            continue
        if receipt.get("schema_version") != SCHEMA_VERSION:
            continue
        try:
            payload = read_json(artifact)
        except (OSError, ValueError):
            errors.append(f"OCR_ARTIFACT_MALFORMED:{page_id}")
            continue
        if not isinstance(payload, dict):
            errors.append(f"OCR_ARTIFACT_MALFORMED:{page_id}")
            continue
        if (
            payload.get("page_id") != page_id
            or payload.get("source_id") != receipt.get("source_id")
            or payload.get("page_sha256") != receipt.get("image_sha256")
        ):
            errors.append(f"OCR_ARTIFACT_IDENTITY_MISMATCH:{page_id}")
        graphemes = payload.get("graphemes")
        rejected_components = payload.get("rejected_components")
        if not isinstance(graphemes, list) or not isinstance(rejected_components, list):
            errors.append(f"OCR_ARTIFACT_COMPONENT_EVIDENCE_MALFORMED:{page_id}")
            continue
        evidence = _component_evidence(graphemes, rejected_components)
        expected = {
            **evidence,
            "grapheme_count": len(graphemes),
            "rejected_component_count": len(rejected_components),
        }
        if any(receipt.get(field) != item for field, item in expected.items()):
            errors.append(f"OCR_ARTIFACT_COMPONENT_EVIDENCE_MISMATCH:{page_id}")
    return errors


def freeze_stage_a_receipts(
    manifest_path: str | Path,
    corpus_root: str | Path,
    output_root: str | Path,
    *,
    repository_root: str | Path,
    config: OpenSetConfig | None = None,
) -> FrozenStageASummary:
    """Validate every Stage A join, then write compact deterministic receipts."""

    manifest_path = Path(manifest_path)
    corpus_root = Path(corpus_root)
    output_root = Path(output_root)
    repository_root = Path(repository_root)
    config = config or OpenSetConfig()
    pages = load_page_manifest(manifest_path)
    if not pages:
        raise ValueError("Cannot freeze an empty page manifest")
    page_ids = [page.page_id for page in pages]
    if len(page_ids) != len(set(page_ids)):
        raise ValueError("Page manifest contains duplicate page IDs")
    if len({page.iiif_id for page in pages}) != len(pages):
        raise ValueError("Page manifest contains duplicate IIIF IDs")

    aggregate_regions = _unique(read_jsonl(corpus_root / "regions.jsonl"), "region_id", "region aggregate")
    dispositions = _unique(
        read_jsonl(corpus_root / "page_dispositions.jsonl"), "page_id", "page disposition"
    )
    if set(dispositions) != set(page_ids):
        raise ValueError("Page disposition set does not match the manifest")

    portable_pages: list[dict[str, Any]] = []
    validated_pages: list[dict[str, Any]] = []
    config_hashes: set[str] = set()
    total_lines = 0
    total_graphemes = 0
    total_unknown = 0
    total_rejected = 0

    for page in pages:
        image_path = _validate_page_source(page)
        if page.page_id not in dispositions:
            raise ValueError(f"Page disposition is missing: {page.page_id}")
        ocr_path = corpus_root / "pages" / f"{page.iiif_id}.json"
        if not ocr_path.is_file():
            raise ValueError(f"Page OCR record is missing: {page.page_id}")
        payload = read_json(ocr_path)
        if not isinstance(payload, dict):
            raise ValueError(f"Page OCR record is malformed: {page.page_id}")
        (
            regions,
            line_count,
            grapheme_count,
            unknown_count,
            layout_disposition,
            rejected_components,
            line_geometry,
            line_geometry_mode_counts,
        ) = _validate_page_ocr(page, payload, aggregate_regions, dispositions[page.page_id])
        config_sha256 = payload["config_sha256"]
        config_hashes.add(config_sha256)
        ocr_sha256 = sha256_file(ocr_path)
        component_evidence = _component_evidence(payload["graphemes"], rejected_components)
        portable_image_path = _portable(image_path, repository_root)
        portable_ocr_path = _portable(ocr_path, repository_root)
        portable_pages.append(
            {
                **page.__dict__,
                "image_path": portable_image_path,
            }
        )
        validated_pages.append(
            {
                "page": page,
                "regions": regions,
                "line_count": line_count,
                "grapheme_count": grapheme_count,
                "unknown_count": unknown_count,
                "layout_disposition": layout_disposition,
                "rejected_component_count": len(rejected_components),
                **component_evidence,
                "line_geometry": line_geometry,
                "line_geometry_mode_counts": line_geometry_mode_counts,
                "ocr_path": ocr_path,
                "ocr_sha256": ocr_sha256,
                "config_sha256": config_sha256,
                "portable_image_path": portable_image_path,
                "portable_ocr_path": portable_ocr_path,
            }
        )
        total_lines += line_count
        total_graphemes += grapheme_count
        total_unknown += unknown_count
        total_rejected += len(rejected_components)

    validated_source_region_ids = {
        region["region_id"] for item in validated_pages for region in item["regions"]
    }
    if set(aggregate_regions) != validated_source_region_ids:
        raise ValueError("Frozen region set does not match the corpus aggregate")
    config_sha256 = next(iter(config_hashes)) if len(config_hashes) == 1 else None
    current_config_sha256 = _config_sha256(config)
    if config_sha256 != current_config_sha256:
        raise ValueError(
            "Stage A configuration differs from the configuration supplied to the freezer"
        )
    git_commit, git_worktree_dirty = _git_state(repository_root)
    page_authority_sha256 = _page_authority_sha256(pages)
    dependency_identity = _dependency_identity()
    run_core = {
        "schema": "zfd.ocr_run.v3",
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "stage_a_ocr_run",
        "page_authority_sha256": page_authority_sha256,
        "acquired_manifest_sha256": sha256_file(manifest_path),
        "input_page_count": len(pages),
        "input_region_count": len(aggregate_regions),
        "total_line_count": total_lines,
        "total_grapheme_count": total_graphemes,
        "total_unknown_grapheme_count": total_unknown,
        "total_rejected_component_count": total_rejected,
        "total_component_candidate_count": total_graphemes + total_rejected,
        "config_sha256": config_sha256,
        "configuration_set_sha256": _value_sha256(sorted(config_hashes)),
        "segmentation_version": config.segmentation_version,
        "implementation_sha256": _implementation_sha256(),
        "dependency_identity": dependency_identity,
        "dependency_set_sha256": _value_sha256(dependency_identity),
        "git_commit": git_commit,
        "git_worktree_dirty": git_worktree_dirty,
        "package_version": __version__,
        "python_version": platform.python_version(),
        "opencv_version": cv2.__version__,
        "numpy_version": np.__version__,
        "command": [
            "python",
            "-m",
            "zfd_image_native",
            "segment-corpus",
            "--manifest",
            _portable(manifest_path, repository_root),
            "--output",
            _portable(corpus_root, repository_root),
        ],
    }
    run_id = f"sha256:{_value_sha256(run_core)}"
    run_receipt = _with_receipt_hash({**run_core, "run_id": run_id})

    page_receipts: list[dict[str, Any]] = []
    region_receipts: list[dict[str, Any]] = []
    page_parity: list[dict[str, Any]] = []
    region_parity: list[dict[str, Any]] = []
    unresolved_layers = {
        "diplomatic": {"id": None, "sha256": None, "state": "unresolved"},
        "normalised": {"id": None, "sha256": None, "state": "unresolved"},
        "terminology": {"id": None, "sha256": None, "state": "unresolved"},
        "modern_croatian": {"id": None, "sha256": None, "state": "unresolved"},
        "literal_english": {"id": None, "sha256": None, "state": "unresolved"},
        "fluent_english": {"id": None, "sha256": None, "state": "unresolved"},
        "review": {"id": None, "sha256": None, "state": "unreviewed"},
    }

    for item in validated_pages:
        page = item["page"]
        ocr_path = item["ocr_path"]
        payload = read_json(ocr_path)
        if not isinstance(payload, dict):
            raise ValueError(f"Page OCR record changed after validation: {page.page_id}")
        ocr_sha256 = sha256_file(ocr_path)
        if ocr_sha256 != item["ocr_sha256"]:
            raise ValueError(f"Page OCR record changed during freeze: {page.page_id}")
        ocr_id = "sha256:" + _value_sha256(
            {
                "run_id": run_id,
                "page_id": page.page_id,
                "image_sha256": page.image_sha256,
                "config_sha256": item["config_sha256"],
                "segmentation_version": config.segmentation_version,
                "ocr_sha256": ocr_sha256,
            }
        )
        lines_by_region: dict[str, list[dict[str, Any]]] = {}
        graphemes_by_region: dict[str, list[dict[str, Any]]] = {}
        for line in payload["lines"]:
            lines_by_region.setdefault(line["region_id"], []).append(line)
        for grapheme in payload["graphemes"]:
            graphemes_by_region.setdefault(grapheme["region_id"], []).append(grapheme)
        prepared_regions: list[dict[str, Any]] = []
        for region_index, source_region in enumerate(item["regions"], start=1):
            source_region_id = source_region["region_id"]
            source_lines = lines_by_region.get(source_region_id, [])
            region_line_geometry = [
                {"line_id": line["line_id"], "geometry_mode": line["geometry_mode"]}
                for line in source_lines
                if "geometry_mode" in line
            ]
            region_mode_counts = dict(
                sorted(Counter(row["geometry_mode"] for row in region_line_geometry).items())
            )
            region_payload_sha256 = _value_sha256(
                {
                    "region": source_region,
                    "lines": source_lines,
                    "graphemes": graphemes_by_region.get(source_region_id, []),
                }
            )
            region_id = "sha256:" + _value_sha256(
                {
                    "ocr_id": ocr_id,
                    "region_index": region_index,
                    "source_region_id": source_region_id,
                    "bbox": source_region["bbox"],
                    "polygon": source_region["polygon"],
                    "region_payload_sha256": region_payload_sha256,
                }
            )
            prepared_regions.append(
                {
                    "region_id": region_id,
                    "source_region_id": source_region_id,
                    "region_index": region_index,
                    "source": source_region,
                    "line_set_sha256": _value_sha256(sorted(source_region["line_ids"])),
                    "line_geometry": region_line_geometry,
                    "line_geometry_mode_counts": region_mode_counts,
                    "region_payload_sha256": region_payload_sha256,
                }
            )
        region_ids = [region["region_id"] for region in prepared_regions]
        region_set_sha256 = _value_sha256(sorted(region_ids))
        acquisition_receipt_path = Path(page.image_path).parent / "acquisition_receipt.json"
        acquisition_receipt_sha256 = (
            sha256_file(acquisition_receipt_path) if acquisition_receipt_path.is_file() else None
        )
        page_receipt = _with_receipt_hash(
            {
                "schema": "zfd.page_ocr.v3",
                "schema_version": SCHEMA_VERSION,
                "receipt_type": "stage_a_page_ocr",
                "run_id": run_id,
                "run_receipt_sha256": run_receipt["receipt_sha256"],
                "page_id": page.page_id,
                "source_id": page.source_id,
                "iiif_id": page.iiif_id,
                "image_sha256": page.image_sha256,
                "image_path": item["portable_image_path"],
                "image_request_uri": page.image_request_uri,
                "acquisition_receipt_sha256": acquisition_receipt_sha256,
                "ocr_id": ocr_id,
                "ocr_record": item["portable_ocr_path"],
                "ocr_sha256": ocr_sha256,
                "ocr_artifact_path": f"pages/{page.iiif_id}.json",
                "ocr_artifact_sha256": ocr_sha256,
                "config_sha256": item["config_sha256"],
                "segmentation_version": config.segmentation_version,
                "width": page.width,
                "height": page.height,
                "record_state": "frozen",
                "disposition": payload["disposition"],
                "layout_disposition": item["layout_disposition"],
                "rejected_component_count": item["rejected_component_count"],
                "rejected_component_evidence_sha256": item[
                    "rejected_component_evidence_sha256"
                ],
                "grapheme_evidence_sha256": item["grapheme_evidence_sha256"],
                "component_candidate_count": item["component_candidate_count"],
                "component_disposition_set_sha256": item[
                    "component_disposition_set_sha256"
                ],
                "line_geometry": item["line_geometry"],
                "line_geometry_mode_counts": item["line_geometry_mode_counts"],
                "region_count": len(prepared_regions),
                "line_count": item["line_count"],
                "grapheme_count": item["grapheme_count"],
                "unknown_grapheme_count": item["unknown_count"],
                "region_set_sha256": region_set_sha256,
                "segmentation_status": "provisional_complete",
                "recognition_status": "unrecognized",
                "metrics_status": "not_measured",
            }
        )
        page_receipts.append(page_receipt)
        page_reasons = ["REGIONS_UNRESOLVED", *UNRESOLVED_BLOCKERS]
        if not region_ids:
            page_reasons.insert(0, "TEXT_REGION_DISPOSITION_UNREVIEWED")
        page_parity.append(
            _with_receipt_hash(
                {
                    "schema": "zfd.page_parity.v1",
                    "schema_version": PARITY_SCHEMA_VERSION,
                    "parity_type": "page_to_translation",
                    "run_id": run_id,
                    "page_id": page.page_id,
                    "image_sha256": page.image_sha256,
                    "ocr_id": ocr_id,
                    "page_ocr_receipt_sha256": page_receipt["receipt_sha256"],
                    "surface_state": "unreviewed",
                    "region_ids": region_ids,
                    "region_set_sha256": region_set_sha256,
                    "expected_region_count": len(region_ids),
                    "confirmed_regions": 0,
                    "unresolved_regions": len(region_ids),
                    "excluded_regions": 0,
                    "missing_regions": 0,
                    "unexpected_regions": 0,
                    "confirmed_translated": False,
                    "translation_status": "unresolved",
                    "disposition": "accounted_unresolved",
                    "reason_codes": page_reasons,
                }
            )
        )
        for prepared in prepared_regions:
            source_region = prepared["source"]
            region_receipt = _with_receipt_hash(
                {
                    "schema": "zfd.region.v3",
                    "schema_version": SCHEMA_VERSION,
                    "record_type": "voynich_text_region",
                    "run_id": run_id,
                    "region_id": prepared["region_id"],
                    "source_region_id": prepared["source_region_id"],
                    "region_index": prepared["region_index"],
                    "page_id": page.page_id,
                    "source_id": page.source_id,
                    "image_sha256": page.image_sha256,
                    "ocr_id": ocr_id,
                    "page_ocr_receipt_sha256": page_receipt["receipt_sha256"],
                    "ocr_record": item["portable_ocr_path"],
                    "ocr_sha256": ocr_sha256,
                    "config_sha256": item["config_sha256"],
                    "segmentation_version": config.segmentation_version,
                    "coordinate_space": "source_pixels",
                    "bbox": source_region["bbox"],
                    "polygon": source_region["polygon"],
                    "line_count": len(source_region["line_ids"]),
                    "line_set_sha256": prepared["line_set_sha256"],
                    "line_geometry": prepared["line_geometry"],
                    "line_geometry_mode_counts": prepared["line_geometry_mode_counts"],
                    "region_payload_sha256": prepared["region_payload_sha256"],
                    "detection_method": "adaptive_threshold_connected_components",
                    "region_state": "candidate_unreviewed",
                    "review_state": "unreviewed",
                    "exclusion_reason": None,
                    "reviewer_ids": [],
                    "adjudicator_id": None,
                }
            )
            region_receipts.append(region_receipt)
            region_parity.append(
                _with_receipt_hash(
                    {
                        "schema": "zfd.region_parity.v1",
                        "schema_version": PARITY_SCHEMA_VERSION,
                        "parity_type": "region_to_translation",
                        "run_id": run_id,
                        "page_id": page.page_id,
                        "image_sha256": page.image_sha256,
                        "ocr_id": ocr_id,
                        "page_ocr_receipt_sha256": page_receipt["receipt_sha256"],
                        "region_id": prepared["region_id"],
                        "region_receipt_sha256": region_receipt["receipt_sha256"],
                        "geometry": source_region["polygon"],
                        "layers": unresolved_layers,
                        "confirmed_translated": False,
                        "translation_status": "unresolved",
                        "disposition": "unresolved",
                        "reason_codes": list(UNRESOLVED_BLOCKERS),
                    }
                )
            )

    summary = FrozenStageASummary(
        schema_version=SCHEMA_VERSION,
        total_pages=len(pages),
        frozen_pages=len(page_receipts),
        total_regions=len(aggregate_regions),
        frozen_regions=len(region_receipts),
        total_lines=total_lines,
        total_graphemes=total_graphemes,
        unknown_graphemes=total_unknown,
        total_rejected_components=total_rejected,
        total_component_candidates=total_graphemes + total_rejected,
        segmentation_complete=len(page_receipts) == len(pages),
        recognition_status="unrecognized",
        metrics_status="not_measured",
        translation_status="unresolved",
        confirmed_translated_pages=0,
        confirmed_translated_regions=0,
        authoritative_manifest_sha256=sha256_file(manifest_path),
        config_sha256=config_sha256,
        run_id=run_id,
        run_receipt_sha256=run_receipt["receipt_sha256"],
    )

    write_json(output_root / "ocr_run_receipt.json", run_receipt)
    write_jsonl(output_root / "voynich_pages.jsonl", portable_pages)
    write_jsonl(output_root / "ocr_page_receipts.jsonl", page_receipts)
    write_jsonl(output_root / "voynich_regions.jsonl", region_receipts)
    write_jsonl(output_root / "page_parity.jsonl", page_parity)
    write_jsonl(output_root / "region_parity.jsonl", region_parity)
    write_json(output_root / "corpus_stage_a_summary.json", summary)
    report = validate_stage_a_receipts(
        output_root,
        corpus_root=corpus_root,
        repository_root=repository_root,
        manifest_path=manifest_path,
        config=config,
    )
    if not report.ok:
        raise ValueError("Frozen receipt self validation failed: " + "; ".join(report.errors))
    return summary


def validate_stage_a_receipts(
    receipt_root: str | Path,
    *,
    corpus_root: str | Path | None = None,
    repository_root: str | Path | None = None,
    manifest_path: str | Path | None = None,
    config: OpenSetConfig | None = None,
) -> ReceiptValidationReport:
    """Validate frozen integrity and current checkout freshness independently."""

    root = Path(receipt_root)
    archival_errors: list[str] = []
    errors = archival_errors
    try:
        run_receipt = read_json(root / "ocr_run_receipt.json")
        if not isinstance(run_receipt, dict):
            raise ValueError("OCR run receipt is malformed")
        pages = _unique(read_jsonl(root / "voynich_pages.jsonl"), "page_id", "frozen page")
        page_receipts = _unique(
            read_jsonl(root / "ocr_page_receipts.jsonl"), "page_id", "page OCR receipt"
        )
        regions = _unique(read_jsonl(root / "voynich_regions.jsonl"), "region_id", "frozen region")
        page_parity = _unique(read_jsonl(root / "page_parity.jsonl"), "page_id", "page parity")
        region_parity = _unique(
            read_jsonl(root / "region_parity.jsonl"), "region_id", "region parity"
        )
        summary = read_json(root / "corpus_stage_a_summary.json")
    except (OSError, ValueError) as error:
        archive_error = str(error)
        freshness_error = "FRESHNESS_UNAVAILABLE_ARCHIVE_MALFORMED"
        return ReceiptValidationReport(
            ok=False,
            archival_integrity_ok=False,
            artifact_integrity_ok=False,
            freshness_ok=False,
            page_count=0,
            region_count=0,
            confirmed_translated_pages=0,
            confirmed_translated_regions=0,
            archival_errors=(archive_error,),
            artifact_errors=("OCR_ARTIFACT_VALIDATION_UNAVAILABLE",),
            freshness_errors=(freshness_error,),
            errors=(archive_error, "OCR_ARTIFACT_VALIDATION_UNAVAILABLE", freshness_error),
        )

    if not _receipt_hash_is_valid(run_receipt):
        errors.append("RUN_RECEIPT_HASH_MISMATCH")
    run_core = {
        key: value
        for key, value in run_receipt.items()
        if key not in {"run_id", "receipt_sha256"}
    }
    expected_run_id = f"sha256:{_value_sha256(run_core)}"
    if run_receipt.get("run_id") != expected_run_id:
        errors.append("RUN_ID_MISMATCH")
    if run_receipt.get("input_page_count") != len(pages):
        errors.append("RUN_PAGE_COUNT_MISMATCH")
    if run_receipt.get("page_authority_sha256") != _page_authority_sha256(pages.values()):
        errors.append("RUN_FROZEN_PAGE_AUTHORITY_MISMATCH")
    if run_receipt.get("schema_version") == SCHEMA_VERSION:
        if not isinstance(run_receipt.get("segmentation_version"), str):
            errors.append("RUN_SEGMENTATION_VERSION_MISSING")
        dependency_identity = run_receipt.get("dependency_identity")
        if not isinstance(dependency_identity, dict):
            errors.append("RUN_DEPENDENCY_IDENTITY_MISSING")
        elif run_receipt.get("dependency_set_sha256") != _value_sha256(dependency_identity):
            errors.append("RUN_DEPENDENCY_SET_HASH_MISMATCH")
    if set(pages) != set(page_receipts) or set(pages) != set(page_parity):
        errors.append("PAGE_RECORD_SET_MISMATCH")
    if set(regions) != set(region_parity):
        errors.append("REGION_RECORD_SET_MISMATCH")
    for page_id, page in pages.items():
        receipt = page_receipts.get(page_id, {})
        parity = page_parity.get(page_id, {})
        if not _receipt_hash_is_valid(receipt):
            errors.append(f"PAGE_RECEIPT_HASH_MISMATCH:{page_id}")
        if not _receipt_hash_is_valid(parity):
            errors.append(f"PAGE_PARITY_HASH_MISMATCH:{page_id}")
        if receipt.get("run_id") != run_receipt.get("run_id"):
            errors.append(f"PAGE_RUN_MISMATCH:{page_id}")
        if receipt.get("run_receipt_sha256") != run_receipt.get("receipt_sha256"):
            errors.append(f"PAGE_RUN_RECEIPT_MISMATCH:{page_id}")
        for field in ("image_sha256", "source_id"):
            if page.get(field) != receipt.get(field):
                errors.append(f"PAGE_{field.upper()}_MISMATCH:{page_id}")
        if run_receipt.get("schema_version") == SCHEMA_VERSION and receipt.get(
            "schema_version"
        ) != SCHEMA_VERSION:
            errors.append(f"PAGE_SCHEMA_VERSION_MISMATCH:{page_id}")
        if run_receipt.get("schema_version") == SCHEMA_VERSION and receipt.get(
            "segmentation_version"
        ) != run_receipt.get("segmentation_version"):
            errors.append(f"PAGE_SEGMENTATION_VERSION_MISMATCH:{page_id}")
        if receipt.get("schema_version") == SCHEMA_VERSION:
            disposition = receipt.get("disposition")
            layout_disposition = receipt.get("layout_disposition")
            if receipt.get("schema") != "zfd.page_ocr.v3":
                errors.append(f"PAGE_SCHEMA_MISMATCH:{page_id}")
            if disposition not in STAGE_A_DISPOSITIONS:
                errors.append(f"PAGE_DISPOSITION_INVALID:{page_id}")
            if disposition in {
                "segmented_unrecognized_layout_review",
                "no_text_detected_layout_review",
            } and layout_disposition != "layout_review_required":
                errors.append(f"PAGE_LAYOUT_REVIEW_EVIDENCE_MISSING:{page_id}")
            if "rejected_components" in receipt:
                errors.append(f"PAGE_REJECTED_COMPONENTS_EMBEDDED:{page_id}")
            try:
                rejected_count = receipt.get("rejected_component_count")
                grapheme_count = receipt.get("grapheme_count")
                component_count = receipt.get("component_candidate_count")
                if any(
                    not isinstance(count, int) or isinstance(count, bool) or count < 0
                    for count in (rejected_count, grapheme_count, component_count)
                ):
                    raise ValueError("component counts are invalid")
                if component_count != rejected_count + grapheme_count:
                    raise ValueError("component counts do not conserve candidates")
                if receipt.get("unknown_grapheme_count") != grapheme_count:
                    raise ValueError("Stage A graphemes are not all explicit unknowns")
                grapheme_hash = _require_hash(
                    receipt.get("grapheme_evidence_sha256"), "grapheme evidence hash"
                )
                rejected_hash = _require_hash(
                    receipt.get("rejected_component_evidence_sha256"),
                    "rejected component evidence hash",
                )
                disposition_hash = _require_hash(
                    receipt.get("component_disposition_set_sha256"),
                    "component disposition hash",
                )
                expected_disposition_hash = _value_sha256(
                    {
                        "grapheme_count": grapheme_count,
                        "grapheme_evidence_sha256": grapheme_hash,
                        "rejected_component_count": rejected_count,
                        "rejected_component_evidence_sha256": rejected_hash,
                        "component_candidate_count": component_count,
                    }
                )
                if disposition_hash != expected_disposition_hash:
                    raise ValueError("component disposition hash is inconsistent")
                if receipt.get("ocr_artifact_path") != f"pages/{receipt.get('iiif_id')}.json":
                    raise ValueError("OCR artifact path is not canonical")
                if _require_hash(
                    receipt.get("ocr_artifact_sha256"), "OCR artifact hash"
                ) != receipt.get("ocr_sha256"):
                    raise ValueError("OCR artifact hash does not match OCR identity")
            except ValueError as error:
                errors.append(f"PAGE_COMPONENT_EVIDENCE_INVALID:{page_id}:{error}")
            line_geometry = receipt.get("line_geometry")
            stored_mode_counts = receipt.get("line_geometry_mode_counts")
            if not isinstance(line_geometry, list) or not isinstance(stored_mode_counts, dict):
                errors.append(f"PAGE_LINE_GEOMETRY_MALFORMED:{page_id}")
            else:
                seen_line_ids: set[str] = set()
                calculated_mode_counts: Counter[str] = Counter()
                for row in line_geometry:
                    if not isinstance(row, dict):
                        errors.append(f"PAGE_LINE_GEOMETRY_MALFORMED:{page_id}")
                        break
                    line_id = row.get("line_id")
                    geometry_mode = row.get("geometry_mode")
                    if (
                        not isinstance(line_id, str)
                        or not line_id
                        or line_id in seen_line_ids
                        or not isinstance(geometry_mode, str)
                        or not geometry_mode
                    ):
                        errors.append(f"PAGE_LINE_GEOMETRY_INVALID:{page_id}")
                        break
                    seen_line_ids.add(line_id)
                    calculated_mode_counts[geometry_mode] += 1
                if dict(sorted(calculated_mode_counts.items())) != stored_mode_counts:
                    errors.append(f"PAGE_LINE_GEOMETRY_MODE_COUNT_MISMATCH:{page_id}")
                if len(line_geometry) > receipt.get("line_count", -1):
                    errors.append(f"PAGE_LINE_GEOMETRY_COUNT_INVALID:{page_id}")
        if parity.get("image_sha256") != page.get("image_sha256"):
            errors.append(f"PAGE_PARITY_HASH_MISMATCH:{page_id}")
        if parity.get("ocr_id") != receipt.get("ocr_id") or parity.get(
            "page_ocr_receipt_sha256"
        ) != receipt.get("receipt_sha256"):
            errors.append(f"PAGE_PARITY_OCR_MISMATCH:{page_id}")
        if parity.get("confirmed_translated") is not False or parity.get("translation_status") != "unresolved":
            errors.append(f"UNSUPPORTED_PAGE_TRANSLATION_CLAIM:{page_id}")
        page_region_ids = sorted(
            region_id for region_id, region in regions.items() if region.get("page_id") == page_id
        )
        if sorted(parity.get("region_ids", [])) != page_region_ids:
            errors.append(f"PAGE_REGION_SET_MISMATCH:{page_id}")
        if receipt.get("region_set_sha256") != _value_sha256(page_region_ids):
            errors.append(f"PAGE_REGION_SET_HASH_MISMATCH:{page_id}")
        if parity.get("region_set_sha256") != receipt.get("region_set_sha256"):
            errors.append(f"PAGE_PARITY_REGION_SET_HASH_MISMATCH:{page_id}")
        if not parity.get("reason_codes"):
            errors.append(f"PAGE_BLOCKERS_MISSING:{page_id}")
    for region_id, region in regions.items():
        page_id = region.get("page_id")
        parity = region_parity.get(region_id, {})
        receipt = page_receipts.get(page_id, {})
        if not _receipt_hash_is_valid(region):
            errors.append(f"REGION_RECEIPT_HASH_MISMATCH:{region_id}")
        if not _receipt_hash_is_valid(parity):
            errors.append(f"REGION_PARITY_HASH_MISMATCH:{region_id}")
        if run_receipt.get("schema_version") == SCHEMA_VERSION and (
            region.get("schema_version") != SCHEMA_VERSION
            or region.get("schema") != "zfd.region.v3"
        ):
            errors.append(f"REGION_SCHEMA_MISMATCH:{region_id}")
        if run_receipt.get("schema_version") == SCHEMA_VERSION and region.get(
            "segmentation_version"
        ) != run_receipt.get("segmentation_version"):
            errors.append(f"REGION_SEGMENTATION_VERSION_MISMATCH:{region_id}")
        if page_id not in pages:
            errors.append(f"REGION_PAGE_MISSING:{region_id}")
        if region.get("image_sha256") != receipt.get("image_sha256"):
            errors.append(f"REGION_IMAGE_HASH_MISMATCH:{region_id}")
        if region.get("ocr_id") != receipt.get("ocr_id") or region.get(
            "page_ocr_receipt_sha256"
        ) != receipt.get("receipt_sha256"):
            errors.append(f"REGION_OCR_MISMATCH:{region_id}")
        if parity.get("page_id") != page_id or parity.get("image_sha256") != region.get("image_sha256"):
            errors.append(f"REGION_PARITY_IDENTITY_MISMATCH:{region_id}")
        if parity.get("geometry") != region.get("polygon"):
            errors.append(f"REGION_PARITY_GEOMETRY_MISMATCH:{region_id}")
        if parity.get("region_receipt_sha256") != region.get("receipt_sha256"):
            errors.append(f"REGION_PARITY_RECEIPT_MISMATCH:{region_id}")
        if parity.get("confirmed_translated") is not False or parity.get("translation_status") != "unresolved":
            errors.append(f"UNSUPPORTED_REGION_TRANSLATION_CLAIM:{region_id}")
        layers = parity.get("layers")
        if not isinstance(layers, dict) or any(
            not isinstance(layer, dict) or layer.get("state") not in {"unresolved", "unreviewed"}
            for layer in layers.values()
        ):
            errors.append(f"REGION_LAYER_STATE_INVALID:{region_id}")
        if not parity.get("reason_codes"):
            errors.append(f"REGION_BLOCKERS_MISSING:{region_id}")

    confirmed_pages = sum(row.get("confirmed_translated") is True for row in page_parity.values())
    confirmed_regions = sum(row.get("confirmed_translated") is True for row in region_parity.values())
    expected_summary = {
        "total_pages": len(pages),
        "frozen_pages": len(page_receipts),
        "total_regions": len(regions),
        "frozen_regions": len(regions),
        "total_rejected_components": sum(
            row.get("rejected_component_count", 0) for row in page_receipts.values()
        ),
        "total_component_candidates": sum(
            row.get("component_candidate_count", 0) for row in page_receipts.values()
        ),
        "confirmed_translated_pages": confirmed_pages,
        "confirmed_translated_regions": confirmed_regions,
        "recognition_status": "unrecognized",
        "metrics_status": "not_measured",
        "translation_status": "unresolved",
        "run_id": run_receipt.get("run_id"),
        "run_receipt_sha256": run_receipt.get("receipt_sha256"),
    }
    if not isinstance(summary, dict):
        errors.append("SUMMARY_MALFORMED")
    else:
        for field, expected in expected_summary.items():
            if summary.get(field) != expected:
                errors.append(f"SUMMARY_{field.upper()}_MISMATCH")
        if summary.get("authoritative_manifest_sha256") != run_receipt.get(
            "acquired_manifest_sha256"
        ):
            errors.append("SUMMARY_MANIFEST_IDENTITY_MISMATCH")

    artifact_repository_root = (
        Path(repository_root).resolve() if repository_root is not None else None
    )
    artifact_corpus_root: Path | None = None
    if corpus_root is not None:
        artifact_corpus_root = Path(corpus_root)
        if not artifact_corpus_root.is_absolute() and artifact_repository_root is not None:
            artifact_corpus_root = artifact_repository_root / artifact_corpus_root
        artifact_corpus_root = artifact_corpus_root.resolve()
    artifact_errors = _ocr_artifact_integrity_errors(
        page_receipts,
        corpus_root=artifact_corpus_root,
        repository_root=artifact_repository_root,
    )

    freshness_errors: list[str] = []
    if run_receipt.get("schema_version") != SCHEMA_VERSION:
        freshness_errors.append("CURRENT_SCHEMA_VERSION_MISMATCH")
    if run_receipt.get("implementation_sha256") != _implementation_sha256():
        freshness_errors.append("CURRENT_IMPLEMENTATION_MISMATCH")
    current_config = config or OpenSetConfig()
    current_config_sha256 = _config_sha256(current_config)
    if (
        run_receipt.get("config_sha256") != current_config_sha256
        or run_receipt.get("configuration_set_sha256")
        != _value_sha256([current_config_sha256])
    ):
        freshness_errors.append("CURRENT_CONFIG_MISMATCH")
    current_dependencies = _dependency_identity()
    if run_receipt.get("dependency_set_sha256") != _value_sha256(current_dependencies):
        freshness_errors.append("CURRENT_DEPENDENCY_SET_MISMATCH")

    if repository_root is None or manifest_path is None:
        freshness_errors.append("CURRENT_CONTEXT_MISSING")
    else:
        current_repository_root = Path(repository_root).resolve()
        current_manifest_path = Path(manifest_path)
        if not current_manifest_path.is_absolute():
            current_manifest_path = current_repository_root / current_manifest_path
        current_manifest_path = current_manifest_path.resolve()
        if not current_repository_root.is_dir():
            freshness_errors.append("CURRENT_REPOSITORY_ROOT_UNAVAILABLE")
        try:
            current_manifest_path.relative_to(current_repository_root)
        except ValueError:
            freshness_errors.append("CURRENT_MANIFEST_OUTSIDE_REPOSITORY")
        if not current_manifest_path.is_file():
            freshness_errors.append("CURRENT_MANIFEST_UNAVAILABLE")
        else:
            try:
                current_pages = load_page_manifest(current_manifest_path)
            except (OSError, TypeError, ValueError):
                freshness_errors.append("CURRENT_MANIFEST_MALFORMED")
            else:
                if run_receipt.get("acquired_manifest_sha256") != sha256_file(
                    current_manifest_path
                ):
                    freshness_errors.append("CURRENT_MANIFEST_MISMATCH")
                if run_receipt.get("page_authority_sha256") != _page_authority_sha256(
                    current_pages
                ):
                    freshness_errors.append("CURRENT_PAGE_AUTHORITY_MISMATCH")
                if run_receipt.get("input_page_count") != len(current_pages):
                    freshness_errors.append("CURRENT_PAGE_COUNT_MISMATCH")
                freshness_errors.extend(
                    _current_source_freshness_errors(
                        current_pages,
                        pages,
                        current_repository_root,
                    )
                )

    archival_integrity_ok = not archival_errors
    artifact_integrity_ok = not artifact_errors
    freshness_ok = not freshness_errors
    combined_errors = tuple(archival_errors + artifact_errors + freshness_errors)
    return ReceiptValidationReport(
        ok=archival_integrity_ok and artifact_integrity_ok and freshness_ok,
        archival_integrity_ok=archival_integrity_ok,
        artifact_integrity_ok=artifact_integrity_ok,
        freshness_ok=freshness_ok,
        page_count=len(pages),
        region_count=len(regions),
        confirmed_translated_pages=confirmed_pages,
        confirmed_translated_regions=confirmed_regions,
        archival_errors=tuple(archival_errors),
        artifact_errors=tuple(artifact_errors),
        freshness_errors=tuple(freshness_errors),
        errors=combined_errors,
    )
