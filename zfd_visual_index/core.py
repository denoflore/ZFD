"""Deterministic page local indexing of Stage A connected component hypotheses."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import heapq
from importlib.metadata import PackageNotFoundError, version
from math import isfinite, log
from pathlib import Path
import platform
import re
import subprocess
from typing import Any, Mapping

import cv2
import numpy as np
import PIL

from zfd_image_native.io import canonical_json, sha256_file

from .stage_a import FrozenStageAPage, FrozenStageARun, validate_stage_a_geometry_graph


RECEIPT_SCHEMA = "zfd.page_local_visual_index.v1"
RECEIPT_SCHEMA_VERSION = "1.0.0"
DISTANCE_METRIC_ID = "bitmap256_hamming_plus_capped_log_aspect.v1"
GROUPING_ALGORITHM = "canonical_greedy_first_exemplar.v1"
_SHA256 = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True)
class VisualIndexConfig:
    descriptor_size: int = 16
    crop_padding: int = 2
    page_local_grouping_cutoff: float = 0.08
    maximum_visual_neighbours: int = 3
    index_version: str = "1.0.0"

    def __post_init__(self) -> None:
        if self.descriptor_size != 16:
            raise ValueError("descriptor_size must be 16 for the registered 256 bit metric")
        if self.crop_padding < 0:
            raise ValueError("crop_padding cannot be negative")
        if not 0.0 <= self.page_local_grouping_cutoff <= 1.0:
            raise ValueError("page_local_grouping_cutoff must be between zero and one")
        if self.maximum_visual_neighbours < 0:
            raise ValueError("maximum_visual_neighbours cannot be negative")


@dataclass(frozen=True)
class PixelDescriptor:
    bitmap_hex: str
    descriptor_sha256: str
    crop_sha256: str
    crop_bbox: tuple[int, int, int, int]
    aspect_ratio: float
    ink_fraction: float


@dataclass(frozen=True)
class DescriptorDistance:
    bitmap_hamming_count: int
    descriptor_bit_count: int
    bitmap_hamming_fraction: float
    aspect_log_ratio_abs: float
    aspect_ratio_penalty: float
    descriptor_distance: float
    descriptor_similarity_unscaled: float
    distance_metric_id: str = DISTANCE_METRIC_ID


@dataclass(frozen=True)
class VisualNeighbour:
    page_local_exemplar_id: str
    exemplar_candidate_id: str
    relationship: str
    candidate_descriptor_aspect_ratio: float
    exemplar_descriptor_aspect_ratio: float
    bitmap_hamming_count: int
    descriptor_bit_count: int
    bitmap_hamming_fraction: float
    aspect_log_ratio_abs: float
    aspect_ratio_penalty: float
    descriptor_distance: float
    descriptor_similarity_unscaled: float
    distance_metric_id: str = DISTANCE_METRIC_ID


@dataclass(frozen=True)
class PageLocalVisualExemplar:
    page_local_exemplar_id: str
    descriptor_bitmap_hex: str
    descriptor_sha256: str
    descriptor_aspect_ratio: float
    exemplar_candidate_id: str
    member_candidate_ids: tuple[str, ...]
    occurrence_count: int
    review_state: str = "unreviewed_visual_only"
    diplomatic_label: str | None = None


@dataclass(frozen=True)
class VisualIndexCandidate:
    candidate_id: str
    stage_a_grapheme_id: str
    line_id: str
    region_id: str
    bbox: tuple[int, int, int, int]
    polygon: tuple[tuple[int, int], ...]
    crop_bbox: tuple[int, int, int, int]
    descriptor_bitmap_hex: str
    descriptor_sha256: str
    crop_sha256: str
    descriptor_aspect_ratio: float
    descriptor_ink_fraction: float
    assigned_page_local_exemplar_id: str
    page_local_exemplar_relationship: str
    assignment_distance: DescriptorDistance
    visual_neighbours: tuple[VisualNeighbour, ...]
    segmentation_unit: str
    decision: str
    decision_basis: str
    unknown_rejection_status: str
    unknown_score: float | None
    recognition_confidence: float | None
    confidence_basis: str
    diplomatic_label: str | None


@dataclass(frozen=True)
class PageLocalVisualIndexReceipt:
    schema: str
    schema_version: str
    page_id: str
    source_id: str
    image_sha256: str
    stage_a_authority: dict[str, Any]
    implementation_sha256: str
    dependency_identity: dict[str, str]
    dependency_set_sha256: str
    implementation_git_commit: str | None
    implementation_git_worktree_dirty: bool | None
    action_identity: tuple[str, ...]
    config: dict[str, Any]
    config_sha256: str
    page_local_exemplar_set_sha256: str
    calibration_receipt_sha256: str | None
    line_count: int
    candidate_count: int
    page_local_exemplar_count: int
    rejected_component_count: int
    component_candidate_count: int
    page_local_visual_exemplars: tuple[PageLocalVisualExemplar, ...]
    candidates: tuple[VisualIndexCandidate, ...]
    processing_stage: str
    page_local_exemplar_scope: str
    grouping_algorithm: str
    grouping_cutoff_calibration_status: str
    descriptor_metric: str
    visual_neighbour_status: str
    identity_recognition_status: str
    script_identity_status: str
    semantic_class_authority_count: int
    unknown_rejection_status: str
    diplomatic_sequence_status: str
    metrics_status: str
    accuracy_claim_allowed: bool
    confirmed_translated: bool
    inherited_text_used: bool
    receipt_sha256: str


@dataclass(frozen=True)
class _CandidateDraft:
    candidate_id: str
    stage_a_grapheme_id: str
    line_id: str
    region_id: str
    bbox: tuple[int, int, int, int]
    polygon: tuple[tuple[int, int], ...]
    descriptor: PixelDescriptor
    bitmap_int: int
    log_aspect: float


@dataclass
class _WorkingExemplar:
    page_local_exemplar_id: str
    exemplar: _CandidateDraft
    members: list[str]


def _value_sha256(value: Any) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _implementation_sha256() -> str:
    package_root = Path(__file__).resolve().parent
    inventory = [
        {"path": path.relative_to(package_root).as_posix(), "sha256": sha256_file(path)}
        for path in sorted(package_root.rglob("*.py"))
    ]
    return _value_sha256(inventory)


def _distribution_version() -> str:
    try:
        return version("zfd-image-native")
    except PackageNotFoundError:
        return "0.1.0+uninstalled"


def _dependency_identity() -> dict[str, str]:
    return {
        "package": f"zfd-image-native=={_distribution_version()}",
        "python_implementation": platform.python_implementation(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "opencv_python": version("opencv-python"),
        "opencv_runtime": cv2.__version__,
        "pillow": version("Pillow"),
        "pillow_runtime": PIL.__version__,
    }


def _git_state() -> tuple[str | None, bool | None]:
    root = Path(__file__).resolve().parents[1]
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True,
            ).stdout.strip()
        )
        return commit, dirty
    except (OSError, subprocess.CalledProcessError):
        return None, None


def _implementation_sha256_at_git_commit(commit: str) -> str | None:
    root = Path(__file__).resolve().parents[1]
    try:
        object_type = subprocess.run(
            ["git", "cat-file", "-t", commit],
            cwd=root,
            capture_output=True,
            check=True,
        ).stdout.strip()
        if object_type != b"commit":
            return None
        listed = subprocess.run(
            ["git", "ls-tree", "-r", "-z", "--name-only", commit, "--", "zfd_visual_index"],
            cwd=root,
            capture_output=True,
            check=True,
        ).stdout
        paths = sorted(
            path
            for path in listed.decode("utf-8").split("\0")
            if path.startswith("zfd_visual_index/") and path.endswith(".py")
        )
        if not paths:
            return None
        inventory = []
        for path in paths:
            blob = subprocess.run(
                ["git", "show", f"{commit}:{path}"],
                cwd=root,
                capture_output=True,
                check=True,
            ).stdout
            inventory.append(
                {
                    "path": path.removeprefix("zfd_visual_index/"),
                    "sha256": sha256(blob).hexdigest(),
                }
            )
        return _value_sha256(inventory)
    except (OSError, UnicodeDecodeError, subprocess.CalledProcessError):
        return None


def _bitmap_int(bitmap_hex: str, descriptor_size: int) -> int:
    expected_length = (descriptor_size * descriptor_size + 3) // 4
    if (
        not isinstance(bitmap_hex, str)
        or len(bitmap_hex) != expected_length
        or bitmap_hex.lower() != bitmap_hex
        or any(character not in "0123456789abcdef" for character in bitmap_hex)
    ):
        raise ValueError("Descriptor bitmap is not canonical hexadecimal")
    return int(bitmap_hex, 16)


def _distance_from_prepared(
    bitmap_a: int,
    log_aspect_a: float,
    bitmap_b: int,
    log_aspect_b: float,
    descriptor_size: int,
) -> DescriptorDistance:
    bit_count = descriptor_size * descriptor_size
    hamming_count = (bitmap_a ^ bitmap_b).bit_count()
    hamming_fraction = round(hamming_count / bit_count, 8)
    aspect_delta = round(abs(log_aspect_a - log_aspect_b), 8)
    aspect_penalty = round(min(0.20, aspect_delta * 0.05), 8)
    distance = round(min(1.0, hamming_fraction + aspect_penalty), 8)
    return DescriptorDistance(
        bitmap_hamming_count=hamming_count,
        descriptor_bit_count=bit_count,
        bitmap_hamming_fraction=hamming_fraction,
        aspect_log_ratio_abs=aspect_delta,
        aspect_ratio_penalty=aspect_penalty,
        descriptor_distance=distance,
        descriptor_similarity_unscaled=round(1.0 - distance, 8),
    )


def descriptor_distance(
    bitmap_a: str,
    aspect_a: float,
    bitmap_b: str,
    aspect_b: float,
    *,
    descriptor_size: int = 16,
) -> DescriptorDistance:
    """Return auditable uncalibrated descriptor distance components."""

    if descriptor_size != 16:
        raise ValueError("descriptor_size must be 16 for the registered 256 bit metric")
    if (
        isinstance(aspect_a, bool)
        or isinstance(aspect_b, bool)
        or not isinstance(aspect_a, (int, float))
        or not isinstance(aspect_b, (int, float))
        or not isfinite(aspect_a)
        or not isfinite(aspect_b)
        or aspect_a <= 0.0
        or aspect_b <= 0.0
    ):
        raise ValueError("Descriptor aspect ratios must be finite and positive")
    return _distance_from_prepared(
        _bitmap_int(bitmap_a, descriptor_size),
        log(max(aspect_a, 1e-6)),
        _bitmap_int(bitmap_b, descriptor_size),
        log(max(aspect_b, 1e-6)),
        descriptor_size,
    )


def extract_pixel_descriptor(
    image: np.ndarray,
    bbox: tuple[int, int, int, int],
    config: VisualIndexConfig | None = None,
) -> PixelDescriptor:
    """Derive a coarse binary shape descriptor directly from registered pixels."""

    config = config or VisualIndexConfig()
    if image.ndim not in {2, 3}:
        raise ValueError("Image must be grayscale or colour")
    height, width = image.shape[:2]
    if (
        len(bbox) != 4
        or any(isinstance(item, bool) or not isinstance(item, int) for item in bbox)
    ):
        raise ValueError("Candidate bbox must contain four integers")
    x, y, box_width, box_height = bbox
    if x < 0 or y < 0 or box_width <= 0 or box_height <= 0 or x + box_width > width or y + box_height > height:
        raise ValueError("Candidate bbox exceeds image dimensions")
    left = max(0, x - config.crop_padding)
    top = max(0, y - config.crop_padding)
    right = min(width, x + box_width + config.crop_padding)
    bottom = min(height, y + box_height + config.crop_padding)
    crop = image[top:bottom, left:right]
    crop_header = canonical_json(
        {"bbox": [left, top, right - left, bottom - top], "shape": list(crop.shape)}
    ).encode("utf-8")
    crop_sha256 = sha256(crop_header + crop.tobytes()).hexdigest()
    gray = crop if crop.ndim == 2 else cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    points = cv2.findNonZero(mask)
    if points is None:
        trimmed = np.zeros((1, 1), dtype=np.uint8)
        aspect_ratio = box_width / box_height
    else:
        ink_x, ink_y, ink_width, ink_height = cv2.boundingRect(points)
        trimmed = mask[ink_y : ink_y + ink_height, ink_x : ink_x + ink_width]
        aspect_ratio = ink_width / max(1, ink_height)
    side = max(trimmed.shape)
    canvas = np.zeros((side, side), dtype=np.uint8)
    y_offset = (side - trimmed.shape[0]) // 2
    x_offset = (side - trimmed.shape[1]) // 2
    canvas[y_offset : y_offset + trimmed.shape[0], x_offset : x_offset + trimmed.shape[1]] = trimmed
    resized = cv2.resize(
        canvas,
        (config.descriptor_size, config.descriptor_size),
        interpolation=cv2.INTER_AREA,
    )
    binary = (resized >= 96).astype(np.uint8)
    packed = np.packbits(binary.reshape(-1)).tobytes()
    return PixelDescriptor(
        bitmap_hex=packed.hex(),
        descriptor_sha256=sha256(packed).hexdigest(),
        crop_sha256=crop_sha256,
        crop_bbox=(left, top, right - left, bottom - top),
        aspect_ratio=round(float(aspect_ratio), 8),
        ink_fraction=round(float(binary.mean()), 8),
    )


def _page_local_exemplar_id(
    page: FrozenStageAPage,
    draft: _CandidateDraft,
    config_sha256: str,
) -> str:
    return "sha256:" + _value_sha256(
        {
            "schema": "zfd.page_local_visual_exemplar_identity.v1",
            "page_id": page.page_id,
            "stage_a_artifact_sha256": page.artifact_sha256,
            "exemplar_candidate_id": draft.candidate_id,
            "descriptor_sha256": draft.descriptor.descriptor_sha256,
            "descriptor_aspect_ratio": draft.descriptor.aspect_ratio,
            "distance_metric_id": DISTANCE_METRIC_ID,
            "config_sha256": config_sha256,
        }
    )


def _build_page_local_exemplars(
    page: FrozenStageAPage,
    drafts: list[_CandidateDraft],
    config: VisualIndexConfig,
    config_sha256: str,
) -> tuple[tuple[PageLocalVisualExemplar, ...], dict[str, tuple[str, DescriptorDistance]]]:
    working: list[_WorkingExemplar] = []
    assignments: dict[str, tuple[str, DescriptorDistance]] = {}
    ordered = sorted(
        drafts,
        key=lambda row: (
            row.descriptor.bitmap_hex,
            row.descriptor.aspect_ratio,
            row.descriptor.crop_sha256,
            row.candidate_id,
        ),
    )
    for draft in ordered:
        ranked: list[tuple[float, int, float, str, _WorkingExemplar, DescriptorDistance]] = []
        for exemplar in working:
            distance = _distance_from_prepared(
                draft.bitmap_int,
                draft.log_aspect,
                exemplar.exemplar.bitmap_int,
                exemplar.exemplar.log_aspect,
                config.descriptor_size,
            )
            ranked.append(
                (
                    distance.descriptor_distance,
                    distance.bitmap_hamming_count,
                    distance.aspect_ratio_penalty,
                    exemplar.page_local_exemplar_id,
                    exemplar,
                    distance,
                )
            )
        ranked.sort(key=lambda item: item[:4])
        if ranked and ranked[0][0] <= config.page_local_grouping_cutoff:
            chosen = ranked[0][4]
            distance = ranked[0][5]
            chosen.members.append(draft.candidate_id)
        else:
            chosen = _WorkingExemplar(
                page_local_exemplar_id=_page_local_exemplar_id(page, draft, config_sha256),
                exemplar=draft,
                members=[draft.candidate_id],
            )
            working.append(chosen)
            distance = _distance_from_prepared(
                draft.bitmap_int,
                draft.log_aspect,
                draft.bitmap_int,
                draft.log_aspect,
                config.descriptor_size,
            )
        assignments[draft.candidate_id] = (chosen.page_local_exemplar_id, distance)
    exemplars = tuple(
        PageLocalVisualExemplar(
            page_local_exemplar_id=row.page_local_exemplar_id,
            descriptor_bitmap_hex=row.exemplar.descriptor.bitmap_hex,
            descriptor_sha256=row.exemplar.descriptor.descriptor_sha256,
            descriptor_aspect_ratio=row.exemplar.descriptor.aspect_ratio,
            exemplar_candidate_id=row.exemplar.candidate_id,
            member_candidate_ids=tuple(sorted(row.members)),
            occurrence_count=len(row.members),
        )
        for row in sorted(working, key=lambda item: item.page_local_exemplar_id)
    )
    return exemplars, assignments


def _visual_neighbours(
    draft: _CandidateDraft,
    assigned_id: str,
    exemplars: tuple[PageLocalVisualExemplar, ...],
    draft_by_candidate: Mapping[str, _CandidateDraft],
    config: VisualIndexConfig,
) -> tuple[VisualNeighbour, ...]:
    if config.maximum_visual_neighbours == 0:
        return ()
    ranked: list[tuple[float, int, float, str, PageLocalVisualExemplar, DescriptorDistance]] = []
    for exemplar in exemplars:
        if exemplar.page_local_exemplar_id == assigned_id:
            continue
        exemplar_draft = draft_by_candidate[exemplar.exemplar_candidate_id]
        distance = _distance_from_prepared(
            draft.bitmap_int,
            draft.log_aspect,
            exemplar_draft.bitmap_int,
            exemplar_draft.log_aspect,
            config.descriptor_size,
        )
        ranked.append(
            (
                distance.descriptor_distance,
                distance.bitmap_hamming_count,
                distance.aspect_ratio_penalty,
                exemplar.page_local_exemplar_id,
                exemplar,
                distance,
            )
        )
    selected = heapq.nsmallest(config.maximum_visual_neighbours, ranked, key=lambda item: item[:4])
    return tuple(
        VisualNeighbour(
            page_local_exemplar_id=exemplar.page_local_exemplar_id,
            exemplar_candidate_id=exemplar.exemplar_candidate_id,
            relationship="neighbour",
            candidate_descriptor_aspect_ratio=draft.descriptor.aspect_ratio,
            exemplar_descriptor_aspect_ratio=exemplar.descriptor_aspect_ratio,
            bitmap_hamming_count=distance.bitmap_hamming_count,
            descriptor_bit_count=distance.descriptor_bit_count,
            bitmap_hamming_fraction=distance.bitmap_hamming_fraction,
            aspect_log_ratio_abs=distance.aspect_log_ratio_abs,
            aspect_ratio_penalty=distance.aspect_ratio_penalty,
            descriptor_distance=distance.descriptor_distance,
            descriptor_similarity_unscaled=distance.descriptor_similarity_unscaled,
        )
        for _, _, _, _, exemplar, distance in selected
    )


def _stage_a_authority(page: FrozenStageAPage, artifact: Mapping[str, Any]) -> dict[str, Any]:
    receipt = page.page_receipt
    graphemes = artifact.get("graphemes")
    rejected = artifact.get("rejected_components")
    if not isinstance(graphemes, list) or not isinstance(rejected, list):
        raise ValueError("STAGE_A_COMPONENT_EVIDENCE_MALFORMED")
    grapheme_hash = _value_sha256(graphemes)
    rejected_hash = _value_sha256(rejected)
    component_count = len(graphemes) + len(rejected)
    disposition_hash = _value_sha256(
        {
            "grapheme_count": len(graphemes),
            "grapheme_evidence_sha256": grapheme_hash,
            "rejected_component_count": len(rejected),
            "rejected_component_evidence_sha256": rejected_hash,
            "component_candidate_count": component_count,
        }
    )
    expected = {
        "grapheme_count": len(graphemes),
        "grapheme_evidence_sha256": grapheme_hash,
        "rejected_component_count": len(rejected),
        "rejected_component_evidence_sha256": rejected_hash,
        "component_candidate_count": component_count,
        "component_disposition_set_sha256": disposition_hash,
    }
    if any(receipt.get(field) != value for field, value in expected.items()):
        raise ValueError("STAGE_A_COMPONENT_DISPOSITION_MISMATCH")
    return {
        "preservation_receipt_file_sha256": page.preservation_receipt_file_sha256,
        "preservation_inventory_sha256": page.preservation_receipt.get("inventory_sha256"),
        "receipt_authority_sha256": page.receipt_authority_sha256,
        "run_id": page.run_receipt.get("run_id"),
        "run_receipt_sha256": page.run_receipt.get("receipt_sha256"),
        "run_receipt_file_sha256": sha256_file(page.stage_a_root / "receipts" / "ocr_run_receipt.json"),
        "manifest_sha256": page.run_receipt.get("acquired_manifest_sha256"),
        "stage_a_implementation_sha256": page.run_receipt.get("implementation_sha256"),
        "stage_a_dependency_set_sha256": page.run_receipt.get("dependency_set_sha256"),
        "page_receipt_sha256": page.page_receipt.get("receipt_sha256"),
        "ocr_id": page.page_receipt.get("ocr_id"),
        "artifact_path": page.page_receipt.get("ocr_artifact_path"),
        "artifact_sha256": page.artifact_sha256,
        "config_sha256": page.page_receipt.get("config_sha256"),
        "segmentation_version": page.page_receipt.get("segmentation_version"),
        "retained_grapheme_count": len(graphemes),
        "retained_grapheme_evidence_sha256": grapheme_hash,
        "rejected_component_count": len(rejected),
        "rejected_component_evidence_sha256": rejected_hash,
        "component_candidate_count": component_count,
        "component_disposition_set_sha256": disposition_hash,
        "disposition": page.page_receipt.get("disposition"),
        "layout_disposition": page.page_receipt.get("layout_disposition"),
    }


def index_page_candidates(
    page: FrozenStageAPage,
    *,
    config: VisualIndexConfig | None = None,
) -> PageLocalVisualIndexReceipt:
    """Index retained Stage A components while withholding every semantic identity."""

    config = config or VisualIndexConfig()
    artifact = page.read_artifact()
    identity = {
        "page_id": page.page_id,
        "source_id": page.page.source_id,
        "page_sha256": page.page.image_sha256,
        "width": page.page.width,
        "height": page.page.height,
        "config_sha256": page.page_receipt.get("config_sha256"),
    }
    if any(artifact.get(field) != value for field, value in identity.items()):
        raise ValueError("STAGE_A_ARTIFACT_IDENTITY_MISMATCH")
    if page.page.width is None or page.page.height is None:
        raise ValueError("STAGE_A_PAGE_DIMENSIONS_MISSING")
    validate_stage_a_geometry_graph(artifact, width=page.page.width, height=page.page.height)
    stage_authority = _stage_a_authority(page, artifact)
    image = page.read_image()
    if image.shape[1] != page.page.width or image.shape[0] != page.page.height:
        raise ValueError("STAGE_A_PAGE_IMAGE_DIMENSIONS_MISMATCH")
    config_payload = asdict(config)
    config_sha256 = _value_sha256(config_payload)
    drafts: list[_CandidateDraft] = []
    for row in artifact.get("graphemes", []):
        stage_id = str(row["grapheme_id"])
        line_id = str(row["line_id"])
        region_id = str(row["region_id"])
        bbox = tuple(int(item) for item in row["bbox"])
        polygon = tuple(tuple(int(axis) for axis in point) for point in row["polygon"])
        descriptor = extract_pixel_descriptor(image, bbox, config)
        candidate_id = "sha256:" + _value_sha256(
            {
                "schema": "zfd.visual_index_candidate_identity.v1",
                "page_id": page.page_id,
                "source_id": page.page.source_id,
                "image_sha256": page.page.image_sha256,
                "stage_a_run_id": page.run_receipt.get("run_id"),
                "stage_a_page_receipt_sha256": page.page_receipt.get("receipt_sha256"),
                "stage_a_artifact_sha256": page.artifact_sha256,
                "stage_a_grapheme_id": stage_id,
                "region_id": region_id,
                "line_id": line_id,
                "bbox": list(bbox),
                "polygon": [list(point) for point in polygon],
                "crop_bbox": list(descriptor.crop_bbox),
                "crop_sha256": descriptor.crop_sha256,
                "descriptor_sha256": descriptor.descriptor_sha256,
                "config_sha256": config_sha256,
            }
        )
        drafts.append(
            _CandidateDraft(
                candidate_id=candidate_id,
                stage_a_grapheme_id=stage_id,
                line_id=line_id,
                region_id=region_id,
                bbox=bbox,
                polygon=polygon,
                descriptor=descriptor,
                bitmap_int=_bitmap_int(descriptor.bitmap_hex, config.descriptor_size),
                log_aspect=log(max(descriptor.aspect_ratio, 1e-6)),
            )
        )
    if len({draft.candidate_id for draft in drafts}) != len(drafts):
        raise ValueError("VISUAL_INDEX_CANDIDATE_ID_DUPLICATE")
    exemplars, assignments = _build_page_local_exemplars(page, drafts, config, config_sha256)
    exemplar_by_id = {row.page_local_exemplar_id: row for row in exemplars}
    draft_by_candidate = {row.candidate_id: row for row in drafts}
    candidates: list[VisualIndexCandidate] = []
    for draft in sorted(drafts, key=lambda row: row.stage_a_grapheme_id):
        exemplar_id, assignment = assignments[draft.candidate_id]
        exemplar = exemplar_by_id[exemplar_id]
        relationship = "self" if exemplar.exemplar_candidate_id == draft.candidate_id else "assigned_exemplar"
        candidates.append(
            VisualIndexCandidate(
                candidate_id=draft.candidate_id,
                stage_a_grapheme_id=draft.stage_a_grapheme_id,
                line_id=draft.line_id,
                region_id=draft.region_id,
                bbox=draft.bbox,
                polygon=draft.polygon,
                crop_bbox=draft.descriptor.crop_bbox,
                descriptor_bitmap_hex=draft.descriptor.bitmap_hex,
                descriptor_sha256=draft.descriptor.descriptor_sha256,
                crop_sha256=draft.descriptor.crop_sha256,
                descriptor_aspect_ratio=draft.descriptor.aspect_ratio,
                descriptor_ink_fraction=draft.descriptor.ink_fraction,
                assigned_page_local_exemplar_id=exemplar_id,
                page_local_exemplar_relationship=relationship,
                assignment_distance=assignment,
                visual_neighbours=_visual_neighbours(
                    draft,
                    exemplar_id,
                    exemplars,
                    draft_by_candidate,
                    config,
                ),
                segmentation_unit="stage_a_connected_component_hypothesis",
                decision="identity_withheld_no_adjudicated_authority",
                decision_basis="no_adjudicated_authority_or_calibration",
                unknown_rejection_status="not_scored_no_calibration",
                unknown_score=None,
                recognition_confidence=None,
                confidence_basis="not_available_no_adjudicated_calibration",
                diplomatic_label=None,
            )
        )
    dependency_identity = _dependency_identity()
    git_commit, git_dirty = _git_state()
    action_identity = (
        "zfd-visual-index",
        "index-page",
        "--page-id",
        page.page_id,
    )
    exemplar_payload = [asdict(row) for row in exemplars]
    payload = {
        "schema": RECEIPT_SCHEMA,
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "page_id": page.page_id,
        "source_id": page.page.source_id,
        "image_sha256": page.page.image_sha256,
        "stage_a_authority": stage_authority,
        "implementation_sha256": _implementation_sha256(),
        "dependency_identity": dependency_identity,
        "dependency_set_sha256": _value_sha256(dependency_identity),
        "implementation_git_commit": git_commit,
        "implementation_git_worktree_dirty": git_dirty,
        "action_identity": action_identity,
        "config": config_payload,
        "config_sha256": config_sha256,
        "page_local_exemplar_set_sha256": _value_sha256(exemplar_payload),
        "calibration_receipt_sha256": None,
        "line_count": len(artifact.get("lines", [])),
        "candidate_count": len(candidates),
        "page_local_exemplar_count": len(exemplars),
        "rejected_component_count": len(artifact.get("rejected_components", [])),
        "component_candidate_count": len(candidates) + len(artifact.get("rejected_components", [])),
        "page_local_visual_exemplars": exemplars,
        "candidates": tuple(candidates),
        "processing_stage": "component_descriptor_and_page_local_grouping",
        "page_local_exemplar_scope": "single_page_unadjudicated_visual_grouping",
        "grouping_algorithm": GROUPING_ALGORITHM,
        "grouping_cutoff_calibration_status": "heuristic_unvalidated",
        "descriptor_metric": DISTANCE_METRIC_ID,
        "visual_neighbour_status": "page_local_descriptor_neighbours_uncalibrated",
        "identity_recognition_status": "not_run_no_adjudicated_registry",
        "script_identity_status": "unassessed",
        "semantic_class_authority_count": 0,
        "unknown_rejection_status": "not_scored_no_calibration",
        "diplomatic_sequence_status": "unresolved",
        "metrics_status": "not_measured_no_image_aligned_gold",
        "accuracy_claim_allowed": False,
        "confirmed_translated": False,
        "inherited_text_used": False,
    }
    receipt_sha256 = _value_sha256(payload)
    return PageLocalVisualIndexReceipt(**payload, receipt_sha256=receipt_sha256)


def validate_page_local_visual_index(
    receipt: Mapping[str, Any], run: FrozenStageARun
) -> tuple[str, ...]:
    """Rehash pixels and geometry, then recompute the entire page local index."""

    errors: list[str] = []
    supplied_hash = receipt.get("receipt_sha256")
    payload = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    if supplied_hash != _value_sha256(payload):
        errors.append("RECEIPT_HASH_MISMATCH")
    if receipt.get("schema") != RECEIPT_SCHEMA or receipt.get("schema_version") != RECEIPT_SCHEMA_VERSION:
        errors.append("RECEIPT_SCHEMA_INVALID")
    if receipt.get("semantic_class_authority_count") != 0 or receipt.get("accuracy_claim_allowed") is not False:
        errors.append("UNSUPPORTED_AUTHORITY_OR_ACCURACY_CLAIM")
    if receipt.get("confirmed_translated") is not False or receipt.get("inherited_text_used") is not False:
        errors.append("UNSUPPORTED_TRANSLATION_OR_INHERITED_TEXT_CLAIM")
    candidate_rows = receipt.get("candidates")
    if not isinstance(candidate_rows, (list, tuple)):
        errors.append("CANDIDATE_COLLECTION_MALFORMED")
    else:
        for candidate in candidate_rows:
            if not isinstance(candidate, Mapping):
                errors.append("CANDIDATE_MALFORMED")
                continue
            if (
                candidate.get("diplomatic_label") is not None
                or candidate.get("unknown_score") is not None
                or candidate.get("recognition_confidence") is not None
            ):
                errors.append("CANDIDATE_SEMANTIC_AUTHORITY_FORBIDDEN")
            if (
                candidate.get("decision") != "identity_withheld_no_adjudicated_authority"
                or candidate.get("unknown_rejection_status") != "not_scored_no_calibration"
            ):
                errors.append("CANDIDATE_WITHHELD_IDENTITY_SEMANTICS_INVALID")
    try:
        page = run.page(str(receipt.get("page_id")))
        config_payload = receipt.get("config")
        if not isinstance(config_payload, Mapping):
            raise ValueError("Visual index config is missing")
        config = VisualIndexConfig(**dict(config_payload))
        action_identity = receipt.get("action_identity")
        if not isinstance(action_identity, (list, tuple)) or any(
            not isinstance(item, str) for item in action_identity
        ):
            raise ValueError("Visual index action identity is malformed")
        git_commit = receipt.get("implementation_git_commit")
        git_dirty = receipt.get("implementation_git_worktree_dirty")
        if (git_commit is None) != (git_dirty is None):
            raise ValueError("Visual index git state pair is malformed")
        if git_commit is not None and (
            not isinstance(git_commit, str)
            or not re.fullmatch(r"[0-9a-f]{40}", git_commit)
        ):
            raise ValueError("Visual index git commit is malformed")
        if git_dirty is not None and not isinstance(git_dirty, bool):
            raise ValueError("Visual index git state is malformed")
        receipt_implementation = receipt.get("implementation_sha256")
        current_implementation = _implementation_sha256()
        if git_commit is not None:
            committed_implementation = _implementation_sha256_at_git_commit(git_commit)
            if committed_implementation is None:
                errors.append("VISUAL_INDEX_GIT_PROVENANCE_UNAVAILABLE")
            elif receipt_implementation != committed_implementation:
                errors.append("IMPLEMENTATION_HASH_MISMATCH")
        elif receipt_implementation != current_implementation:
            errors.append("IMPLEMENTATION_HASH_MISMATCH")
        expected = index_page_candidates(
            page,
            config=config,
        )
        expected_payload = asdict(expected)
        for historical_field in (
            "implementation_sha256",
            "implementation_git_commit",
            "implementation_git_worktree_dirty",
        ):
            expected_payload[historical_field] = receipt.get(historical_field)
        expected_payload["receipt_sha256"] = _value_sha256(
            {
                key: value
                for key, value in expected_payload.items()
                if key != "receipt_sha256"
            }
        )
        if canonical_json(expected_payload) != canonical_json(dict(receipt)):
            errors.append("VISUAL_INDEX_RECOMPUTE_MISMATCH")
    except Exception as error:
        errors.append(f"VISUAL_INDEX_RECOMPUTE_FAILED:{type(error).__name__}")
    return tuple(dict.fromkeys(errors))


def _inside(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def resolve_visual_index_output(path: str | Path, run: FrozenStageARun) -> Path:
    """Resolve a writable output without permitting overlap with frozen authority."""

    raw = Path(path)
    target = (
        run.repository_root / raw if not raw.is_absolute() else raw
    ).resolve()
    if not _inside(target, run.repository_root):
        raise ValueError("OUTPUT_OUTSIDE_REPOSITORY")
    blocked = (
        (run.stage_a_root / "corpus").resolve(),
        (run.stage_a_root / "receipts").resolve(),
        run.authority_root.resolve(),
    )
    if any(_inside(target, root) for root in blocked):
        raise ValueError("OUTPUT_OVERLAPS_STAGE_A_AUTHORITY")
    protected_files = {
        (run.stage_a_root / "preservation_receipt.json").resolve(),
        run.manifest_path.resolve(),
        *(path.resolve() for path in run.image_paths),
        *(path.parent.joinpath("acquisition_receipt.json").resolve() for path in run.image_paths),
    }
    if target in protected_files:
        raise ValueError("OUTPUT_OVERLAPS_STAGE_A_AUTHORITY")
    return target
