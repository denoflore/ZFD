"""Issue immutable page handles from a fully verified frozen Stage A run."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

import cv2
import numpy as np

from zfd_image_native.io import canonical_json, read_json, read_jsonl, sha256_file
from zfd_image_native.manifest import load_page_manifest
from zfd_image_native.models import PageRecord
from zfd_image_native.receipts import validate_stage_a_receipts


AUTHORITY_FILES = (
    "corpus_stage_a_summary.json",
    "ocr_page_receipts.jsonl",
    "ocr_run_receipt.json",
    "page_parity.jsonl",
    "region_parity.jsonl",
    "voynich_pages.jsonl",
    "voynich_regions.jsonl",
)
PRESERVATION_SCHEMA = "zfd.local_preservation.v1"


def _value_sha256(value: Any) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _fail(code: str, detail: str | None = None) -> None:
    raise ValueError(code if detail is None else f"{code}:{detail}")


def _inside(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _resolve_inside(path: str | Path, root: Path, code: str) -> Path:
    raw = Path(path)
    resolved = (root / raw if not raw.is_absolute() else raw).resolve()
    if not _inside(resolved, root):
        _fail(code, str(resolved))
    return resolved


def _receipt_hash_is_valid(row: Mapping[str, Any]) -> bool:
    supplied = row.get("receipt_sha256")
    payload = {key: value for key, value in row.items() if key != "receipt_sha256"}
    return isinstance(supplied, str) and supplied == _value_sha256(payload)


def _inventory(stage_a_root: Path) -> tuple[int, int, str]:
    rows: list[str] = []
    byte_count = 0
    for subdir in ("corpus", "receipts"):
        base = stage_a_root / subdir
        if not base.is_dir():
            _fail("STAGE_A_BUNDLE_DIRECTORY_MISSING", subdir)
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(stage_a_root).as_posix()
            length = path.stat().st_size
            byte_count += length
            rows.append(f"{relative}|{length}|{sha256_file(path)}")
    inventory = "\n".join(rows) + "\n"
    return len(rows), byte_count, sha256(inventory.encode("utf-8")).hexdigest()


def _decode_image(path: Path) -> np.ndarray:
    payload = np.frombuffer(path.read_bytes(), dtype=np.uint8)
    image = cv2.imdecode(payload, cv2.IMREAD_COLOR)
    if image is None:
        _fail("STAGE_A_PAGE_IMAGE_DECODE_FAILED", str(path))
    return image


@dataclass(frozen=True)
class FrozenStageAPage:
    """A page whose pixels, geometry, run, and receipt lineage are already verified."""

    page: PageRecord
    image_path: Path
    artifact_path: Path
    artifact_sha256: str
    page_receipt: Mapping[str, Any]
    run_receipt: Mapping[str, Any]
    stage_a_root: Path
    preservation_receipt: Mapping[str, Any]
    preservation_receipt_file_sha256: str
    receipt_authority_sha256: str

    @property
    def page_id(self) -> str:
        return self.page.page_id

    def read_artifact(self) -> Mapping[str, Any]:
        if not self.artifact_path.is_file() or sha256_file(self.artifact_path) != self.artifact_sha256:
            _fail("STAGE_A_ARTIFACT_SHA256_MISMATCH", self.page_id)
        payload = read_json(self.artifact_path)
        if not isinstance(payload, dict):
            _fail("STAGE_A_ARTIFACT_MALFORMED", self.page_id)
        return payload

    def read_image(self) -> np.ndarray:
        if not self.image_path.is_file() or sha256_file(self.image_path) != self.page.image_sha256:
            _fail("STAGE_A_PAGE_IMAGE_SHA256_MISMATCH", self.page_id)
        return _decode_image(self.image_path)


@dataclass(frozen=True)
class FrozenStageARun:
    """Verified Stage A authority opened once and reused across page indexing."""

    stage_a_root: Path
    authority_root: Path
    repository_root: Path
    manifest_path: Path
    run_receipt: Mapping[str, Any]
    preservation_receipt: Mapping[str, Any]
    preservation_receipt_file_sha256: str
    receipt_authority_sha256: str
    _pages: Mapping[str, FrozenStageAPage]

    @property
    def page_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._pages))

    @property
    def image_paths(self) -> tuple[Path, ...]:
        return tuple(sorted(page.image_path for page in self._pages.values()))

    def page(self, page_id: str) -> FrozenStageAPage:
        try:
            return self._pages[page_id]
        except KeyError as error:
            raise ValueError(f"STAGE_A_PAGE_NOT_FOUND:{page_id}") from error


def open_frozen_stage_a_run(
    stage_a_root: str | Path,
    *,
    authority_root: str | Path,
    repository_root: str | Path,
    manifest_path: str | Path,
) -> FrozenStageARun:
    """Validate the complete frozen run, then issue content-bound page handles."""

    repository = Path(repository_root).resolve()
    if not repository.is_dir():
        _fail("REPOSITORY_ROOT_MISSING", str(repository))
    stage_root = _resolve_inside(stage_a_root, repository, "STAGE_A_ROOT_OUTSIDE_REPOSITORY")
    authority = _resolve_inside(authority_root, repository, "STAGE_A_AUTHORITY_OUTSIDE_REPOSITORY")
    manifest = _resolve_inside(manifest_path, repository, "STAGE_A_MANIFEST_OUTSIDE_REPOSITORY")
    receipts_root = (stage_root / "receipts").resolve()
    corpus_root = (stage_root / "corpus").resolve()
    if not _inside(receipts_root, stage_root) or not _inside(corpus_root, stage_root):
        _fail("STAGE_A_LAYOUT_OUTSIDE_ROOT")

    for name in AUTHORITY_FILES:
        local = receipts_root / name
        trusted = authority / name
        if not local.is_file() or not trusted.is_file() or sha256_file(local) != sha256_file(trusted):
            _fail("STAGE_A_RECEIPT_AUTHORITY_MISMATCH", name)
    local_preservation = stage_root / "preservation_receipt.json"
    trusted_preservation = authority / "preservation_receipt.json"
    if (
        not local_preservation.is_file()
        or not trusted_preservation.is_file()
        or sha256_file(local_preservation) != sha256_file(trusted_preservation)
    ):
        _fail("STAGE_A_PRESERVATION_AUTHORITY_MISMATCH")

    preservation = read_json(local_preservation)
    if not isinstance(preservation, dict) or preservation.get("schema") != PRESERVATION_SCHEMA:
        _fail("STAGE_A_PRESERVATION_RECEIPT_INVALID")
    if preservation.get("structural_integrity_ok") is not True or preservation.get(
        "artifact_integrity_ok"
    ) is not True:
        _fail("STAGE_A_PRESERVATION_INTEGRITY_UNCONFIRMED")
    file_count, byte_count, inventory_sha256 = _inventory(stage_root)
    if (
        preservation.get("file_count") != file_count
        or preservation.get("byte_count") != byte_count
        or preservation.get("inventory_sha256") != inventory_sha256
    ):
        _fail("STAGE_A_INVENTORY_SHA256_MISMATCH")

    report = validate_stage_a_receipts(
        receipts_root,
        corpus_root=corpus_root,
        repository_root=repository,
        manifest_path=manifest,
    )
    if not report.ok:
        _fail("STAGE_A_VALIDATION_FAILED", ",".join(report.errors))

    run = read_json(receipts_root / "ocr_run_receipt.json")
    if not isinstance(run, dict) or not _receipt_hash_is_valid(run):
        _fail("STAGE_A_RUN_RECEIPT_HASH_MISMATCH")
    if (
        preservation.get("run_id") != run.get("run_id")
        or preservation.get("run_receipt_sha256") != run.get("receipt_sha256")
        or preservation.get("manifest_sha256") != run.get("acquired_manifest_sha256")
        or preservation.get("implementation_sha256") != run.get("implementation_sha256")
    ):
        _fail("STAGE_A_RUN_AUTHORITY_MISMATCH")

    pages = load_page_manifest(manifest)
    current_by_id = {page.page_id: page for page in pages}
    if len(current_by_id) != len(pages):
        _fail("STAGE_A_CURRENT_MANIFEST_PAGE_ID_DUPLICATE")
    frozen_pages = read_jsonl(receipts_root / "voynich_pages.jsonl")
    frozen_by_id = {row.get("page_id"): row for row in frozen_pages}
    page_receipts = read_jsonl(receipts_root / "ocr_page_receipts.jsonl")
    receipt_by_id = {row.get("page_id"): row for row in page_receipts}
    if len(frozen_by_id) != len(frozen_pages) or len(receipt_by_id) != len(page_receipts):
        _fail("STAGE_A_PAGE_RECEIPT_ID_DUPLICATE")
    if set(current_by_id) != set(frozen_by_id) or set(current_by_id) != set(receipt_by_id):
        _fail("STAGE_A_PAGE_AUTHORITY_SET_MISMATCH")

    receipt_authority_sha256 = sha256_file(authority / "ocr_page_receipts.jsonl")
    preservation_file_sha256 = sha256_file(local_preservation)
    handles: dict[str, FrozenStageAPage] = {}
    pages_root = (corpus_root / "pages").resolve()
    for page_id in sorted(current_by_id):
        page = current_by_id[page_id]
        frozen = frozen_by_id[page_id]
        receipt = receipt_by_id[page_id]
        if not _receipt_hash_is_valid(receipt):
            _fail("STAGE_A_PAGE_RECEIPT_HASH_MISMATCH", page_id)
        expected_identity = {
            "source_id": page.source_id,
            "iiif_id": page.iiif_id,
            "image_sha256": page.image_sha256,
            "width": page.width,
            "height": page.height,
        }
        if any(receipt.get(field) != value for field, value in expected_identity.items()):
            _fail("STAGE_A_PAGE_IDENTITY_MISMATCH", page_id)
        if any(frozen.get(field) != getattr(page, field) for field in ("source_id", "iiif_id", "image_sha256", "width", "height")):
            _fail("STAGE_A_FROZEN_MANIFEST_IDENTITY_MISMATCH", page_id)
        if receipt.get("run_id") != run.get("run_id") or receipt.get(
            "run_receipt_sha256"
        ) != run.get("receipt_sha256"):
            _fail("STAGE_A_PAGE_RUN_MISMATCH", page_id)
        if receipt.get("config_sha256") != run.get("config_sha256") or receipt.get(
            "segmentation_version"
        ) != run.get("segmentation_version"):
            _fail("STAGE_A_PAGE_CONFIGURATION_MISMATCH", page_id)
        relative = receipt.get("ocr_artifact_path")
        canonical_relative = f"pages/{page.iiif_id}.json"
        if relative != canonical_relative or Path(str(relative)).is_absolute():
            _fail("STAGE_A_ARTIFACT_PATH_NONCANONICAL", page_id)
        artifact = (corpus_root / str(relative)).resolve()
        if not _inside(artifact, pages_root):
            _fail("STAGE_A_ARTIFACT_PATH_OUTSIDE_CORPUS", page_id)
        expected_artifact_sha = receipt.get("ocr_artifact_sha256")
        if (
            not isinstance(expected_artifact_sha, str)
            or receipt.get("ocr_sha256") != expected_artifact_sha
            or not artifact.is_file()
            or sha256_file(artifact) != expected_artifact_sha
        ):
            _fail("STAGE_A_ARTIFACT_SHA256_MISMATCH", page_id)
        expected_ocr_id = "sha256:" + _value_sha256(
            {
                "run_id": run.get("run_id"),
                "page_id": page_id,
                "image_sha256": page.image_sha256,
                "config_sha256": receipt.get("config_sha256"),
                "segmentation_version": receipt.get("segmentation_version"),
                "ocr_sha256": expected_artifact_sha,
            }
        )
        if receipt.get("ocr_id") != expected_ocr_id:
            _fail("STAGE_A_OCR_ID_MISMATCH", page_id)
        if not page.image_path:
            _fail("STAGE_A_PAGE_IMAGE_PATH_MISSING", page_id)
        image_path = _resolve_inside(page.image_path, repository, "STAGE_A_PAGE_IMAGE_OUTSIDE_REPOSITORY")
        if not image_path.is_file() or sha256_file(image_path) != page.image_sha256:
            _fail("STAGE_A_PAGE_IMAGE_SHA256_MISMATCH", page_id)
        handles[page_id] = FrozenStageAPage(
            page=page,
            image_path=image_path,
            artifact_path=artifact,
            artifact_sha256=expected_artifact_sha,
            page_receipt=MappingProxyType(dict(receipt)),
            run_receipt=MappingProxyType(dict(run)),
            stage_a_root=stage_root,
            preservation_receipt=MappingProxyType(dict(preservation)),
            preservation_receipt_file_sha256=preservation_file_sha256,
            receipt_authority_sha256=receipt_authority_sha256,
        )
    return FrozenStageARun(
        stage_a_root=stage_root,
        authority_root=authority,
        repository_root=repository,
        manifest_path=manifest,
        run_receipt=MappingProxyType(dict(run)),
        preservation_receipt=MappingProxyType(dict(preservation)),
        preservation_receipt_file_sha256=preservation_file_sha256,
        receipt_authority_sha256=receipt_authority_sha256,
        _pages=MappingProxyType(handles),
    )


def _coerce_bbox(value: Any, width: int, height: int, label: str) -> tuple[int, int, int, int]:
    if (
        not isinstance(value, (list, tuple))
        or len(value) != 4
        or any(isinstance(item, bool) or not isinstance(item, int) for item in value)
    ):
        _fail(f"STAGE_A_{label}_BBOX_INVALID")
    x, y, box_width, box_height = (int(item) for item in value)
    if x < 0 or y < 0 or box_width <= 0 or box_height <= 0 or x + box_width > width or y + box_height > height:
        _fail(f"STAGE_A_{label}_BBOX_INVALID")
    return x, y, box_width, box_height


def _coerce_polygon(value: Any, width: int, height: int, label: str) -> tuple[tuple[int, int], ...]:
    if not isinstance(value, (list, tuple)) or len(value) < 4:
        _fail(f"STAGE_A_{label}_POLYGON_INVALID")
    points: list[tuple[int, int]] = []
    for point in value:
        if (
            not isinstance(point, (list, tuple))
            or len(point) != 2
            or any(isinstance(axis, bool) or not isinstance(axis, int) for axis in point)
        ):
            _fail(f"STAGE_A_{label}_POLYGON_INVALID")
        x, y = int(point[0]), int(point[1])
        if x < 0 or y < 0 or x > width or y > height:
            _fail(f"STAGE_A_{label}_POLYGON_INVALID")
        points.append((x, y))
    return tuple(points)


def _box_contains(parent: tuple[int, int, int, int], child: tuple[int, int, int, int]) -> bool:
    px, py, pw, ph = parent
    cx, cy, cw, ch = child
    return px <= cx and py <= cy and cx + cw <= px + pw and cy + ch <= py + ph


def _polygon_matches_box(
    box: tuple[int, int, int, int], polygon: tuple[tuple[int, int], ...]
) -> bool:
    x, y, width, height = box
    xs = [point[0] for point in polygon]
    ys = [point[1] for point in polygon]
    return min(xs) == x and min(ys) == y and max(xs) == x + width and max(ys) == y + height


def _polygon_contains(parent: tuple[tuple[int, int], ...], child: tuple[tuple[int, int], ...]) -> bool:
    contour = np.asarray(parent, dtype=np.float32)
    return all(cv2.pointPolygonTest(contour, point, False) >= 0 for point in child)


def validate_stage_a_geometry_graph(
    payload: Mapping[str, Any], *, width: int, height: int
) -> None:
    """Prove unique reciprocal region, line, and retained component membership."""

    collections: dict[str, list[Mapping[str, Any]]] = {}
    for name in ("regions", "lines", "graphemes"):
        rows = payload.get(name)
        if not isinstance(rows, list) or any(not isinstance(row, Mapping) for row in rows):
            _fail(f"STAGE_A_{name.upper()}_MALFORMED")
        collections[name] = rows
    indexes: dict[str, dict[str, Mapping[str, Any]]] = {}
    for name, id_field in (("regions", "region_id"), ("lines", "line_id"), ("graphemes", "grapheme_id")):
        index: dict[str, Mapping[str, Any]] = {}
        for row in collections[name]:
            value = row.get(id_field)
            if not isinstance(value, str) or not value:
                _fail(f"STAGE_A_{name[:-1].upper()}_ID_MISSING")
            if value in index:
                _fail(f"STAGE_A_{name[:-1].upper()}_ID_DUPLICATE", value)
            index[value] = row
        indexes[name] = index

    region_geometry: dict[str, tuple[tuple[int, int, int, int], tuple[tuple[int, int], ...]]] = {}
    for region_id, region in indexes["regions"].items():
        box = _coerce_bbox(region.get("bbox"), width, height, "REGION")
        polygon = _coerce_polygon(region.get("polygon"), width, height, "REGION")
        if not _polygon_matches_box(box, polygon):
            _fail("STAGE_A_REGION_POLYGON_BBOX_MISMATCH", region_id)
        region_geometry[region_id] = (box, polygon)
    line_geometry: dict[str, tuple[tuple[int, int, int, int], tuple[tuple[int, int], ...]]] = {}
    lines_by_region: dict[str, set[str]] = {region_id: set() for region_id in indexes["regions"]}
    for line_id, line in indexes["lines"].items():
        region_id = line.get("region_id")
        if region_id not in indexes["regions"]:
            _fail("STAGE_A_LINE_REGION_MISSING", line_id)
        box = _coerce_bbox(line.get("bbox"), width, height, "LINE")
        polygon = _coerce_polygon(line.get("polygon"), width, height, "LINE")
        if not _polygon_matches_box(box, polygon):
            _fail("STAGE_A_LINE_POLYGON_BBOX_MISMATCH", line_id)
        parent_box, parent_polygon = region_geometry[str(region_id)]
        if not _box_contains(parent_box, box) or not _polygon_contains(parent_polygon, polygon):
            _fail("STAGE_A_LINE_OUTSIDE_REGION", line_id)
        line_geometry[line_id] = (box, polygon)
        lines_by_region[str(region_id)].add(line_id)
    for region_id, region in indexes["regions"].items():
        declared = region.get("line_ids")
        if not isinstance(declared, list) or len(declared) != len(set(declared)) or set(declared) != lines_by_region[region_id]:
            _fail("STAGE_A_REGION_LINE_SET_MISMATCH", region_id)

    graphemes_by_line: dict[str, set[str]] = {line_id: set() for line_id in indexes["lines"]}
    for grapheme_id, grapheme in indexes["graphemes"].items():
        line_id = grapheme.get("line_id")
        region_id = grapheme.get("region_id")
        if line_id not in indexes["lines"] or region_id not in indexes["regions"]:
            _fail("STAGE_A_GRAPHEME_PARENT_MISSING", grapheme_id)
        if indexes["lines"][str(line_id)].get("region_id") != region_id:
            _fail("STAGE_A_GRAPHEME_REGION_LINEAGE_MISMATCH", grapheme_id)
        box = _coerce_bbox(grapheme.get("bbox"), width, height, "GRAPHEME")
        polygon = _coerce_polygon(grapheme.get("polygon"), width, height, "GRAPHEME")
        if not _polygon_matches_box(box, polygon):
            _fail("STAGE_A_GRAPHEME_POLYGON_BBOX_MISMATCH", grapheme_id)
        line_box, line_polygon = line_geometry[str(line_id)]
        region_box, region_polygon = region_geometry[str(region_id)]
        if (
            not _box_contains(line_box, box)
            or not _polygon_contains(line_polygon, polygon)
            or not _box_contains(region_box, box)
            or not _polygon_contains(region_polygon, polygon)
        ):
            _fail("STAGE_A_GRAPHEME_OUTSIDE_LINE", grapheme_id)
        if grapheme.get("diplomatic_label") is not None:
            _fail("STAGE_A_UNADJUDICATED_LABEL_PRESENT", grapheme_id)
        graphemes_by_line[str(line_id)].add(grapheme_id)
    for line_id, line in indexes["lines"].items():
        declared = line.get("grapheme_ids")
        if not isinstance(declared, list) or len(declared) != len(set(declared)) or set(declared) != graphemes_by_line[line_id]:
            _fail("STAGE_A_LINE_GRAPHEME_SET_MISMATCH", line_id)
