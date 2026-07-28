"""Pixel bound line tasks and independent visual form review receipts."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import platform
import re
import unicodedata
from typing import Any, Mapping

import cv2
import numpy as np

from zfd_image_native.io import canonical_json, sha256_file


TASK_SCHEMA = "zfd.line_visual_form_review_task.v1"
OBSERVATION_SCHEMA = "zfd.visual_form_observation.v1"
ADJUDICATION_SCHEMA = "zfd.visual_form_adjudication.v1"
SCHEMA_VERSION = "1.0.0"
_SHA256 = re.compile(r"[0-9a-f]{64}")
_CONTENT_ID = re.compile(r"sha256:[0-9a-f]{64}")
_OPAQUE_CLASS = re.compile(r"opaque:[0-9]{4,}")
_ROLES = frozenset({"primary_annotator", "independent_reviewer"})
_CERTAINTIES = frozenset({"clear", "probable", "uncertain"})
_LABEL_STATES = frozenset({"opaque_form", "unresolved"})
_EXCLUSION_STATES = frozenset({"duplicate_component", "non_text", "unresolved"})
_UNCERTAINTY_CODES = frozenset(
    {
        "boundary_uncertain",
        "crop_edge",
        "ink_damage",
        "low_contrast",
        "overlap_or_ligature",
        "possible_abbreviation_mark",
        "possible_diacritic",
        "visually_ambiguous_form",
        "other_visual_uncertainty",
    }
)
_EXCLUSION_REASON_CODES = frozenset(
    {
        "boundary_uncertain",
        "component_duplicate",
        "non_text_illustration",
        "non_text_noise",
        "non_text_rule",
        "other_visual_exclusion",
    }
)
_EXCLUSION_REASON_BY_STATUS = {
    "duplicate_component": frozenset({"component_duplicate"}),
    "non_text": frozenset({"non_text_illustration", "non_text_noise", "non_text_rule"}),
    "unresolved": frozenset({"boundary_uncertain", "other_visual_exclusion"}),
}
_RATIONALE_CODES = frozenset(
    {
        "independent_observations_agree",
        "merge_selected",
        "non_text_selected",
        "primary_geometry_preferred",
        "reviewer_geometry_preferred",
        "source_observations_disagree",
        "split_selected",
        "unresolved_retained",
        "visual_form_selected",
    }
)
_OBSERVATION_DRAFT_FIELDS = frozenset(
    {
        "schema",
        "task_id",
        "annotator_id",
        "observer_role",
        "independent_viewing_attestation",
        "source_lane",
        "inherited_text_used",
        "glyphs",
        "candidate_exclusions",
    }
)
_GLYPH_DRAFT_FIELDS = frozenset(
    {
        "ordinal",
        "bbox",
        "polygons",
        "stage_a_candidate_ids",
        "label_state",
        "opaque_class_id",
        "alternatives",
        "certainty",
        "uncertainty_codes",
    }
)
_ADJUDICATION_GLYPH_FIELDS = _GLYPH_DRAFT_FIELDS | {
    "source_observation_glyph_ids",
    "rationale_codes",
}
_EXCLUSION_DRAFT_FIELDS = frozenset({"candidate_id", "status", "reason_code"})
_ADJUDICATION_DRAFT_FIELDS = frozenset(
    {
        "schema",
        "task_id",
        "primary_observation_receipt_sha256",
        "review_observation_receipt_sha256",
        "adjudicator_id",
        "source_lane",
        "inherited_text_used",
        "glyphs",
        "candidate_exclusions",
        "source_glyph_dispositions",
    }
)
_SOURCE_GLYPH_DISPOSITION_FIELDS = frozenset(
    {"observer_role", "glyph_observation_id", "disposition", "rationale_code"}
)
_SOURCE_GLYPH_DISPOSITION_RATIONALES = {
    "excluded_duplicate_visual_hypothesis": frozenset({"visual_form_selected"}),
    "excluded_non_text": frozenset({"non_text_selected"}),
    "unresolved_conflict": frozenset(
        {"source_observations_disagree", "unresolved_retained"}
    ),
}


@dataclass(frozen=True)
class VisualReviewTaskConfig:
    crop_padding_x: int = 24
    crop_padding_y: int = 16

    def __post_init__(self) -> None:
        if any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0
            for value in (self.crop_padding_x, self.crop_padding_y)
        ):
            raise ValueError("GOLD_TASK_PADDING_INVALID")


def _value_sha256(value: Any) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _content_id(value: Any) -> str:
    return "sha256:" + _value_sha256(value)


def _exact_fields(row: Mapping[str, Any], allowed: frozenset[str], code: str) -> None:
    unexpected = set(row) - allowed
    if unexpected:
        raise ValueError(code + ":" + ",".join(sorted(repr(value) for value in unexpected)))


def _identity(value: Any, code: str) -> str:
    if not isinstance(value, str):
        raise ValueError(code)
    normalized = unicodedata.normalize("NFKC", value).strip()
    if not normalized:
        raise ValueError(code)
    return normalized


def _receipt(payload: Mapping[str, Any]) -> dict[str, Any]:
    plain = dict(payload)
    return {**plain, "receipt_sha256": _value_sha256(plain)}


def _receipt_valid(row: Mapping[str, Any]) -> bool:
    try:
        supplied = row.get("receipt_sha256")
        payload = {key: value for key, value in row.items() if key != "receipt_sha256"}
        return isinstance(supplied, str) and supplied == _value_sha256(payload)
    except (TypeError, ValueError):
        return False


def _implementation_sha256() -> str:
    package_root = Path(__file__).resolve().parent
    inventory = [
        {"path": path.relative_to(package_root).as_posix(), "sha256": sha256_file(path)}
        for path in sorted(package_root.rglob("*.py"))
    ]
    return _value_sha256(inventory)


def _dependency_identity() -> dict[str, str]:
    try:
        package = version("zfd-image-native")
    except PackageNotFoundError:
        package = "0.1.0+uninstalled"
    return {
        "package": f"zfd-image-native=={package}",
        "python_implementation": platform.python_implementation(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "opencv_python": version("opencv-python"),
        "opencv_runtime": cv2.__version__,
    }


def _box(value: Any, *, code: str) -> tuple[int, int, int, int]:
    if (
        not isinstance(value, (list, tuple))
        or len(value) != 4
        or any(isinstance(item, bool) or not isinstance(item, int) for item in value)
    ):
        raise ValueError(code)
    box = tuple(value)
    if box[0] < 0 or box[1] < 0 or box[2] <= 0 or box[3] <= 0:
        raise ValueError(code)
    return box


def _segments_intersect(
    first_a: tuple[int, int],
    first_b: tuple[int, int],
    second_a: tuple[int, int],
    second_b: tuple[int, int],
) -> bool:
    def orientation(a: tuple[int, int], b: tuple[int, int], c: tuple[int, int]) -> int:
        value = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        return (value > 0) - (value < 0)

    def on_segment(a: tuple[int, int], b: tuple[int, int], c: tuple[int, int]) -> bool:
        return (
            min(a[0], c[0]) <= b[0] <= max(a[0], c[0])
            and min(a[1], c[1]) <= b[1] <= max(a[1], c[1])
        )

    o1 = orientation(first_a, first_b, second_a)
    o2 = orientation(first_a, first_b, second_b)
    o3 = orientation(second_a, second_b, first_a)
    o4 = orientation(second_a, second_b, first_b)
    if o1 * o2 < 0 and o3 * o4 < 0:
        return True
    return (
        (o1 == 0 and on_segment(first_a, second_a, first_b))
        or (o2 == 0 and on_segment(first_a, second_b, first_b))
        or (o3 == 0 and on_segment(second_a, first_a, second_b))
        or (o4 == 0 and on_segment(second_a, first_b, second_b))
    )


def _canonical_polygon(points: list[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    variants: list[tuple[tuple[int, int], ...]] = []
    for ordered in (points, list(reversed(points))):
        variants.extend(
            tuple(ordered[index:] + ordered[:index]) for index in range(len(ordered))
        )
    return min(variants)


def _without_redundant_collinear_vertices(
    points: list[tuple[int, int]],
) -> list[tuple[int, int]]:
    simplified = list(points)
    while len(simplified) > 3:
        removed = False
        for index, current in enumerate(simplified):
            previous = simplified[index - 1]
            following = simplified[(index + 1) % len(simplified)]
            cross = (current[0] - previous[0]) * (following[1] - current[1]) - (
                current[1] - previous[1]
            ) * (following[0] - current[0])
            between = (
                min(previous[0], following[0]) <= current[0] <= max(previous[0], following[0])
                and min(previous[1], following[1])
                <= current[1]
                <= max(previous[1], following[1])
            )
            if cross == 0 and between:
                simplified.pop(index)
                removed = True
                break
        if not removed:
            break
    return simplified


def _point_inside_polygon(
    point: tuple[int, int], polygon: tuple[tuple[int, int], ...]
) -> bool:
    x, y = point
    inside = False
    previous = polygon[-1]
    for current in polygon:
        if (current[1] > y) != (previous[1] > y):
            crossing_x = (previous[0] - current[0]) * (y - current[1]) / (
                previous[1] - current[1]
            ) + current[0]
            if x < crossing_x:
                inside = not inside
        previous = current
    return inside


def _polygons_overlap(
    first: tuple[tuple[int, int], ...], second: tuple[tuple[int, int], ...]
) -> bool:
    for first_index, first_a in enumerate(first):
        first_b = first[(first_index + 1) % len(first)]
        for second_index, second_a in enumerate(second):
            second_b = second[(second_index + 1) % len(second)]
            if _segments_intersect(first_a, first_b, second_a, second_b):
                return True
    return _point_inside_polygon(first[0], second) or _point_inside_polygon(second[0], first)


def _polygon(value: Any, *, code: str) -> tuple[tuple[int, int], ...]:
    if not isinstance(value, (list, tuple)) or len(value) < 3:
        raise ValueError(code)
    points: list[tuple[int, int]] = []
    for point in value:
        if (
            not isinstance(point, (list, tuple))
            or len(point) != 2
            or any(isinstance(axis, bool) or not isinstance(axis, int) for axis in point)
        ):
            raise ValueError(code)
        points.append(tuple(point))
    if len(points) > 3 and points[0] == points[-1]:
        points.pop()
    if len(points) < 3 or len(set(points)) != len(points):
        raise ValueError(code)
    points = _without_redundant_collinear_vertices(points)
    edge_count = len(points)
    for first in range(edge_count):
        first_next = (first + 1) % edge_count
        for second in range(first + 1, edge_count):
            second_next = (second + 1) % edge_count
            if first == second or first_next == second or second_next == first:
                continue
            if _segments_intersect(
                points[first],
                points[first_next],
                points[second],
                points[second_next],
            ):
                raise ValueError(code)
    twice_area = sum(
        first[0] * second[1] - second[0] * first[1]
        for first, second in zip(points, points[1:] + points[:1], strict=True)
    )
    if twice_area == 0:
        raise ValueError(code)
    return _canonical_polygon(points)


def _polygon_bbox(polygons: tuple[tuple[tuple[int, int], ...], ...]) -> tuple[int, int, int, int]:
    xs = [point[0] for polygon in polygons for point in polygon]
    ys = [point[1] for polygon in polygons for point in polygon]
    return min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)


def _polygons_share_interior_pixel(
    first: tuple[tuple[tuple[int, int], ...], ...],
    second: tuple[tuple[tuple[int, int], ...], ...],
) -> bool:
    """Return true only when one image pixel centre lies inside both shapes."""

    for first_polygon in first:
        first_box = _polygon_bbox((first_polygon,))
        first_contour = np.asarray(first_polygon, dtype=np.float32)
        for second_polygon in second:
            second_box = _polygon_bbox((second_polygon,))
            if not _overlaps(first_box, second_box):
                continue
            second_contour = np.asarray(second_polygon, dtype=np.float32)
            left = max(first_box[0], second_box[0])
            top = max(first_box[1], second_box[1])
            right = min(first_box[0] + first_box[2], second_box[0] + second_box[2])
            bottom = min(first_box[1] + first_box[3], second_box[1] + second_box[3])
            for y in range(top, bottom):
                for x in range(left, right):
                    pixel_centre = (x + 0.5, y + 0.5)
                    if (
                        cv2.pointPolygonTest(first_contour, pixel_centre, False) > 0
                        and cv2.pointPolygonTest(second_contour, pixel_centre, False) > 0
                    ):
                        return True
    return False


def _inside(parent: tuple[int, int, int, int], child: tuple[int, int, int, int]) -> bool:
    px, py, pw, ph = parent
    cx, cy, cw, ch = child
    return px <= cx and py <= cy and cx + cw <= px + pw and cy + ch <= py + ph


def _overlaps(first: tuple[int, int, int, int], second: tuple[int, int, int, int]) -> bool:
    ax, ay, aw, ah = first
    bx, by, bw, bh = second
    return max(ax, bx) < min(ax + aw, bx + bw) and max(ay, by) < min(ay + ah, by + bh)


def _pixel_hash(image: np.ndarray, box: tuple[int, int, int, int]) -> str:
    x, y, width, height = box
    if x + width > image.shape[1] or y + height > image.shape[0]:
        raise ValueError("PIXEL_GEOMETRY_OUTSIDE_IMAGE")
    crop = image[y : y + height, x : x + width]
    header = canonical_json({"bbox": list(box), "shape": list(crop.shape)}).encode("utf-8")
    return sha256(header + crop.tobytes()).hexdigest()


def _encoded_png(image: np.ndarray) -> bytes:
    ok, encoded = cv2.imencode(".png", image, [cv2.IMWRITE_PNG_COMPRESSION, 9])
    if not ok:
        raise ValueError("GOLD_TASK_CROP_ENCODING_FAILED")
    return encoded.tobytes()


def _page_identity(page: Any) -> dict[str, Any]:
    record = page.page
    return {
        "page_id": record.page_id,
        "source_id": record.source_id,
        "iiif_id": record.iiif_id,
        "surface_label": record.surface_label,
        "image_sha256": record.image_sha256,
        "width": record.width,
        "height": record.height,
    }


def _stage_a_identity(page: Any) -> dict[str, Any]:
    return {
        "run_id": page.run_receipt.get("run_id"),
        "run_receipt_sha256": page.run_receipt.get("receipt_sha256"),
        "page_receipt_sha256": page.page_receipt.get("receipt_sha256"),
        "ocr_id": page.page_receipt.get("ocr_id"),
        "artifact_sha256": page.artifact_sha256,
        "config_sha256": page.page_receipt.get("config_sha256"),
        "segmentation_version": page.page_receipt.get("segmentation_version"),
    }


def _visual_candidates_for_line(
    visual: Mapping[str, Any], line_id: str
) -> list[dict[str, Any]]:
    rows = visual.get("candidates")
    if not isinstance(rows, (list, tuple)):
        raise ValueError("VISUAL_CANDIDATES_MALFORMED")
    selected: list[dict[str, Any]] = []
    required = (
        "candidate_id",
        "stage_a_grapheme_id",
        "line_id",
        "region_id",
        "bbox",
        "polygon",
        "crop_bbox",
        "crop_sha256",
        "descriptor_sha256",
        "descriptor_aspect_ratio",
        "assigned_page_local_exemplar_id",
    )
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("VISUAL_CANDIDATE_MALFORMED")
        if row.get("line_id") != line_id:
            continue
        if any(key not in row for key in required):
            raise ValueError("VISUAL_CANDIDATE_FIELD_MISSING")
        if any(row.get(key) is not None for key in ("diplomatic_label", "unknown_score", "recognition_confidence")):
            raise ValueError("VISUAL_CANDIDATE_SEMANTIC_VALUE_PRESENT")
        selected.append({key: row[key] for key in required})
    return sorted(selected, key=lambda row: str(row["stage_a_grapheme_id"]))


def build_line_task(
    page: Any,
    visual_index: Mapping[str, Any],
    *,
    visual_index_file_sha256: str,
    line_id: str,
    config: VisualReviewTaskConfig | None = None,
) -> tuple[dict[str, Any], bytes]:
    """Create one unlabelled line task from verified image and geometry records."""

    config = config or VisualReviewTaskConfig()
    if not _SHA256.fullmatch(str(visual_index_file_sha256)):
        raise ValueError("VISUAL_INDEX_FILE_HASH_INVALID")
    identity = _page_identity(page)
    if any(visual_index.get(key) != identity[key] for key in ("page_id", "source_id", "image_sha256")):
        raise ValueError("VISUAL_INDEX_PAGE_IDENTITY_MISMATCH")
    if visual_index.get("inherited_text_used") is not False:
        raise ValueError("VISUAL_INDEX_SOURCE_LANE_TAINTED")
    if visual_index.get("semantic_class_authority_count") != 0:
        raise ValueError("VISUAL_INDEX_AUTHORITY_PRESENT")
    if not _receipt_valid(visual_index):
        raise ValueError("VISUAL_INDEX_RECEIPT_HASH_MISMATCH")

    artifact = page.read_artifact()
    lines = [row for row in artifact.get("lines", []) if isinstance(row, Mapping) and row.get("line_id") == line_id]
    if len(lines) != 1:
        raise ValueError("STAGE_A_LINE_NOT_UNIQUE")
    line = lines[0]
    line_box = _box(line.get("bbox"), code="STAGE_A_LINE_BBOX_INVALID")
    line_polygon = _polygon(line.get("polygon"), code="STAGE_A_LINE_POLYGON_INVALID")
    candidates = _visual_candidates_for_line(visual_index, line_id)
    stage_ids = list(line.get("grapheme_ids", []))
    if [row["stage_a_grapheme_id"] for row in candidates] != stage_ids:
        raise ValueError("STAGE_A_VISUAL_LINE_JOIN_MISMATCH")
    if not candidates:
        raise ValueError("GOLD_TASK_LINE_HAS_NO_CANDIDATES")
    region_ids = {str(row["region_id"]) for row in candidates}
    if region_ids != {str(line.get("region_id"))}:
        raise ValueError("STAGE_A_VISUAL_REGION_JOIN_MISMATCH")

    image = page.read_image()
    if image.shape[1] != identity["width"] or image.shape[0] != identity["height"]:
        raise ValueError("SOURCE_IMAGE_DIMENSIONS_MISMATCH")
    x, y, width, height = line_box
    crop_box = (
        max(0, x - config.crop_padding_x),
        max(0, y - config.crop_padding_y),
        0,
        0,
    )
    left, top = crop_box[:2]
    right = min(image.shape[1], x + width + config.crop_padding_x)
    bottom = min(image.shape[0], y + height + config.crop_padding_y)
    crop_box = (left, top, right - left, bottom - top)
    crop_array = image[top:bottom, left:right]
    crop_png = _encoded_png(crop_array)
    raw_crop_hash = _pixel_hash(image, crop_box)
    candidate_set_sha256 = _value_sha256(candidates)
    visual_identity = {
        "file_sha256": visual_index_file_sha256,
        "receipt_sha256": visual_index.get("receipt_sha256"),
        "implementation_sha256": visual_index.get("implementation_sha256"),
        "dependency_set_sha256": visual_index.get("dependency_set_sha256"),
        "config_sha256": visual_index.get("config_sha256"),
        "candidate_set_sha256": candidate_set_sha256,
    }
    task_identity = {
        "schema": "zfd.line_visual_form_review_task_identity.v1",
        **identity,
        "stage_a_authority": _stage_a_identity(page),
        "visual_index_authority": visual_identity,
        "region_id": line.get("region_id"),
        "line_id": line_id,
        "line_bbox": list(line_box),
        "line_polygon": [list(point) for point in line_polygon],
        "crop_bbox": list(crop_box),
        "raw_pixel_sha256": raw_crop_hash,
        "candidate_set_sha256": candidate_set_sha256,
    }
    dependency_identity = _dependency_identity()
    payload = {
        "schema": TASK_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "task_id": _content_id(task_identity),
        **identity,
        "stage_a_authority": _stage_a_identity(page),
        "visual_index_authority": visual_identity,
        "implementation_sha256": _implementation_sha256(),
        "dependency_identity": dependency_identity,
        "dependency_set_sha256": _value_sha256(dependency_identity),
        "config": asdict(config),
        "region_id": line.get("region_id"),
        "line_id": line_id,
        "line_bbox": list(line_box),
        "line_polygon": [list(point) for point in line_polygon],
        "line_geometry_status": "stage_a_provisional_requires_human_review",
        "crop": {
            "bbox": list(crop_box),
            "raw_pixel_sha256": raw_crop_hash,
            "encoding": "png_lossless",
            "encoded_asset_sha256": sha256(crop_png).hexdigest(),
            "byte_length": len(crop_png),
        },
        "candidate_count": len(candidates),
        "candidate_set_sha256": candidate_set_sha256,
        "candidates": candidates,
        "review_policy": {
            "source_lane": "human_image_aligned",
            "minimum_independent_observations": 2,
            "independent_adjudicator_required": True,
            "prefilled_labels": False,
        },
        "split": {
            "assignment_state": "unassigned",
            "manuscript_id": "yale-ms-408",
            "hand_scope": "yale-ms-408:unattributed",
            "style": "unclassified",
            "lineage_root_id": "yale-ms-408:unattributed",
        },
        "observation_count": 0,
        "adjudication_count": 0,
        "sequence_authority_status": "not_established",
        "semantic_class_authority_count": 0,
        "authority_promotion_eligible": False,
        "accuracy_claim_allowed": False,
        "confirmed_translated": False,
        "inherited_text_used": False,
    }
    return _receipt(payload), crop_png


def validate_line_task(
    task: Mapping[str, Any],
    page: Any,
    visual_index: Mapping[str, Any],
    *,
    visual_index_file_sha256: str,
    crop_png: bytes,
) -> tuple[str, ...]:
    errors: list[str] = []
    if not isinstance(task, Mapping) or not _receipt_valid(task):
        errors.append("GOLD_TASK_RECEIPT_HASH_MISMATCH")
    try:
        config = VisualReviewTaskConfig(**dict(task.get("config", {})))
        expected, expected_crop = build_line_task(
            page,
            visual_index,
            visual_index_file_sha256=visual_index_file_sha256,
            line_id=str(task.get("line_id")),
            config=config,
        )
        if canonical_json(dict(task)) != canonical_json(expected):
            errors.append("GOLD_TASK_RECOMPUTE_MISMATCH")
        if crop_png != expected_crop:
            errors.append("GOLD_TASK_CROP_RECOMPUTE_MISMATCH")
    except Exception as error:
        errors.append(f"GOLD_TASK_RECOMPUTE_FAILED:{type(error).__name__}:{error}")
    return tuple(dict.fromkeys(errors))


def _validate_task_shell(task: Mapping[str, Any]) -> None:
    if not _receipt_valid(task) or task.get("schema") != TASK_SCHEMA:
        raise ValueError("GOLD_TASK_RECEIPT_INVALID")
    if (
        task.get("inherited_text_used") is not False
        or task.get("semantic_class_authority_count") != 0
        or task.get("authority_promotion_eligible") is not False
        or task.get("accuracy_claim_allowed") is not False
        or task.get("confirmed_translated") is not False
        or task.get("sequence_authority_status") != "not_established"
        or not isinstance(task.get("split"), Mapping)
        or task["split"].get("assignment_state") != "unassigned"
    ):
        raise ValueError("GOLD_TASK_AUTHORITY_BOUNDARY_INVALID")


def _validate_task_pixels(task: Mapping[str, Any], image: np.ndarray) -> None:
    if image.ndim not in {2, 3}:
        raise ValueError("SOURCE_IMAGE_ARRAY_INVALID")
    if image.shape[1] != task.get("width") or image.shape[0] != task.get("height"):
        raise ValueError("SOURCE_IMAGE_DIMENSIONS_MISMATCH")
    crop = task.get("crop")
    if not isinstance(crop, Mapping):
        raise ValueError("GOLD_TASK_CROP_MALFORMED")
    crop_box = _box(crop.get("bbox"), code="GOLD_TASK_CROP_BBOX_INVALID")
    if _pixel_hash(image, crop_box) != crop.get("raw_pixel_sha256"):
        raise ValueError("SOURCE_IMAGE_TASK_PIXEL_MISMATCH")


def _normalise_glyphs(
    task: Mapping[str, Any],
    glyph_rows: Any,
    image: np.ndarray,
    *,
    id_schema: str,
    id_field: str,
    identity_context: Mapping[str, Any],
    adjudication: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, list[int]]]:
    if not isinstance(glyph_rows, list):
        raise ValueError("GLYPH_ROWS_MALFORMED")
    candidate_by_id = {row["candidate_id"]: row for row in task["candidates"]}
    candidate_ids = set(candidate_by_id)
    output: list[dict[str, Any]] = []
    pixel_occurrence_ids: set[str] = set()
    references: dict[str, list[int]] = {candidate_id: [] for candidate_id in candidate_ids}
    for expected_ordinal, row in enumerate(glyph_rows):
        if not isinstance(row, Mapping) or row.get("ordinal") != expected_ordinal:
            raise ValueError("GLYPH_ORDINAL_INVALID")
        _exact_fields(
            row,
            _ADJUDICATION_GLYPH_FIELDS if adjudication else _GLYPH_DRAFT_FIELDS,
            "GLYPH_DRAFT_FIELDS_UNEXPECTED",
        )
        box = _box(row.get("bbox"), code="GLYPH_BBOX_INVALID")
        polygons_value = row.get("polygons")
        if not isinstance(polygons_value, list) or not polygons_value:
            raise ValueError("GLYPH_POLYGONS_INVALID")
        polygons = tuple(
            sorted(_polygon(value, code="GLYPH_POLYGONS_INVALID") for value in polygons_value)
        )
        if len(set(polygons)) != len(polygons):
            raise ValueError("GLYPH_POLYGON_DUPLICATE")
        if any(
            _polygons_overlap(first, second)
            for index, first in enumerate(polygons)
            for second in polygons[index + 1 :]
        ):
            raise ValueError("GLYPH_POLYGONS_OVERLAP")
        if _polygon_bbox(polygons) != box:
            raise ValueError("GLYPH_POLYGON_BBOX_MISMATCH")
        if not _inside(tuple(task["crop"]["bbox"]), box):
            raise ValueError("GLYPH_OUTSIDE_TASK_CROP")
        refs = row.get("stage_a_candidate_ids")
        if not isinstance(refs, list) or len(set(refs)) != len(refs):
            raise ValueError("GLYPH_CANDIDATE_REFERENCES_INVALID")
        if any(ref not in candidate_ids for ref in refs):
            raise ValueError("GLYPH_CANDIDATE_REFERENCE_UNKNOWN")
        referenced_boxes = [
            _box(candidate_by_id[ref].get("bbox"), code="TASK_CANDIDATE_BBOX_INVALID")
            for ref in refs
        ]
        if any(not _overlaps(box, candidate_box) for candidate_box in referenced_boxes):
            raise ValueError("GLYPH_CANDIDATE_GEOMETRY_DISJOINT")
        referenced_polygons = [
            (
                _polygon(
                    candidate_by_id[ref].get("polygon"),
                    code="TASK_CANDIDATE_POLYGON_INVALID",
                ),
            )
            for ref in refs
        ]
        if any(
            not _polygons_share_interior_pixel(polygons, candidate_polygons)
            for candidate_polygons in referenced_polygons
        ):
            raise ValueError("GLYPH_CANDIDATE_GEOMETRY_DISJOINT")
        if len(refs) > 1 and any(not _inside(box, candidate_box) for candidate_box in referenced_boxes):
            raise ValueError("MERGE_GEOMETRY_DOES_NOT_CONTAIN_COMPONENTS")
        for ref in refs:
            references[ref].append(expected_ordinal)
        label_state = row.get("label_state")
        opaque = row.get("opaque_class_id")
        if label_state not in _LABEL_STATES:
            raise ValueError("LABEL_STATE_INVALID")
        if label_state == "opaque_form":
            if not isinstance(opaque, str) or not _OPAQUE_CLASS.fullmatch(opaque):
                raise ValueError("OPAQUE_CLASS_ID_INVALID")
        elif opaque is not None:
            raise ValueError("UNRESOLVED_GLYPH_HAS_CLASS")
        alternatives = row.get("alternatives")
        if not isinstance(alternatives, list) or any(
            not isinstance(value, str) or not _OPAQUE_CLASS.fullmatch(value)
            for value in alternatives
        ):
            raise ValueError("OPAQUE_ALTERNATIVES_INVALID")
        certainty = row.get("certainty")
        if certainty not in _CERTAINTIES:
            raise ValueError("VISUAL_CERTAINTY_INVALID")
        uncertainty_codes = row.get("uncertainty_codes")
        if (
            not isinstance(uncertainty_codes, list)
            or len(set(uncertainty_codes)) != len(uncertainty_codes)
            or any(value not in _UNCERTAINTY_CODES for value in uncertainty_codes)
        ):
            raise ValueError("UNCERTAINTY_CODES_INVALID")
        relation = "stage_a_miss" if not refs else "single"
        if len(refs) > 1:
            relation = "merge"
        pixel_hash = _pixel_hash(image, box)
        identity = {
            "schema": id_schema,
            "review_identity_context": dict(identity_context),
            "task_id": task["task_id"],
            "image_sha256": task["image_sha256"],
            "ordinal": expected_ordinal,
            "bbox": list(box),
            "polygons": [[list(point) for point in polygon] for polygon in polygons],
            "raw_pixel_sha256": pixel_hash,
            "stage_a_candidate_ids": refs,
            "label_state": label_state,
            "opaque_class_id": opaque,
        }
        occurrence_id = _content_id(
            {
                "schema": "zfd.review_pixel_occurrence.v1",
                "image_sha256": task["image_sha256"],
                "bbox": list(box),
                "polygons": identity["polygons"],
                "raw_pixel_sha256": pixel_hash,
            }
        )
        if occurrence_id in pixel_occurrence_ids:
            raise ValueError("DUPLICATE_GLYPH_PIXEL_OCCURRENCE")
        pixel_occurrence_ids.add(occurrence_id)
        result = {
            "ordinal": expected_ordinal,
            "bbox": list(box),
            "polygons": [[list(point) for point in polygon] for polygon in polygons],
            "stage_a_candidate_ids": list(refs),
            "segmentation_relation": relation,
            "raw_pixel_sha256": pixel_hash,
            "pixel_occurrence_id": occurrence_id,
            "label_state": label_state,
            "opaque_class_id": opaque,
            "alternatives": list(alternatives),
            "certainty": certainty,
            "uncertainty_codes": list(uncertainty_codes),
            id_field: _content_id(identity),
        }
        for optional in ("source_observation_glyph_ids", "rationale_codes"):
            if optional in row:
                value = row[optional]
                if optional == "source_observation_glyph_ids":
                    if not isinstance(value, Mapping) or set(value) != {
                        "primary",
                        "independent_reviewer",
                    }:
                        raise ValueError("SOURCE_OBSERVATION_GLYPH_IDS_INVALID")
                    groups: dict[str, list[str]] = {}
                    for group_name in ("primary", "independent_reviewer"):
                        group = value[group_name]
                        if (
                            not isinstance(group, list)
                            or not group
                            or len(set(group)) != len(group)
                            or any(not isinstance(item, str) or not item.strip() for item in group)
                        ):
                            raise ValueError("SOURCE_OBSERVATION_GLYPH_IDS_INVALID")
                        groups[group_name] = list(group)
                    result[optional] = groups
                else:
                    if (
                        not isinstance(value, list)
                        or not value
                        or len(set(value)) != len(value)
                        or any(item not in _RATIONALE_CODES for item in value)
                    ):
                        raise ValueError(optional.upper() + "_INVALID")
                    result[optional] = list(value)
        output.append(result)
    for candidate_id, ordinals in references.items():
        if len(ordinals) > 1:
            for ordinal in ordinals:
                if len(output[ordinal]["stage_a_candidate_ids"]) != 1:
                    raise ValueError("CANDIDATE_SPLIT_MERGE_CONFLICT")
                output[ordinal]["segmentation_relation"] = "split"
    return output, references


def _component_dispositions(
    task: Mapping[str, Any],
    glyphs: list[dict[str, Any]],
    references: Mapping[str, list[int]],
    exclusions: Any,
) -> list[dict[str, Any]]:
    if not isinstance(exclusions, list):
        raise ValueError("CANDIDATE_EXCLUSIONS_MALFORMED")
    excluded: dict[str, Mapping[str, Any]] = {}
    candidate_ids = {row["candidate_id"] for row in task["candidates"]}
    for row in exclusions:
        if not isinstance(row, Mapping):
            raise ValueError("CANDIDATE_EXCLUSION_MALFORMED")
        _exact_fields(row, _EXCLUSION_DRAFT_FIELDS, "CANDIDATE_EXCLUSION_FIELDS_UNEXPECTED")
        candidate_id = row.get("candidate_id")
        if candidate_id not in candidate_ids or candidate_id in excluded:
            raise ValueError("CANDIDATE_EXCLUSION_ID_INVALID")
        if references[candidate_id]:
            raise ValueError("CANDIDATE_BOTH_USED_AND_EXCLUDED")
        if row.get("status") not in _EXCLUSION_STATES:
            raise ValueError("CANDIDATE_EXCLUSION_STATUS_INVALID")
        reason = row.get("reason_code")
        status = row.get("status")
        if reason not in _EXCLUSION_REASON_CODES or reason not in _EXCLUSION_REASON_BY_STATUS[status]:
            raise ValueError("CANDIDATE_EXCLUSION_REASON_INVALID")
        excluded[candidate_id] = row
    dispositions: list[dict[str, Any]] = []
    for candidate in task["candidates"]:
        candidate_id = candidate["candidate_id"]
        ordinals = references[candidate_id]
        if not ordinals and candidate_id not in excluded:
            raise ValueError("CANDIDATE_DISPOSITION_MISSING")
        if candidate_id in excluded:
            row = excluded[candidate_id]
            dispositions.append(
                {
                    "candidate_id": candidate_id,
                    "status": row["status"],
                    "glyph_ordinals": [],
                    "reason_code": row["reason_code"],
                }
            )
            continue
        if len(ordinals) > 1:
            status = "split_source"
        elif len(glyphs[ordinals[0]]["stage_a_candidate_ids"]) > 1:
            status = "merge_member"
        else:
            status = "used_single"
        dispositions.append(
            {
                "candidate_id": candidate_id,
                "status": status,
                "glyph_ordinals": list(ordinals),
                "reason_code": None,
            }
        )
    return dispositions


def _source_glyph_dispositions(
    primary_ids: set[str],
    review_ids: set[str],
    referenced_primary: set[str],
    referenced_review: set[str],
    supplied: Any,
) -> list[dict[str, Any]]:
    if not isinstance(supplied, list):
        raise ValueError("SOURCE_GLYPH_DISPOSITIONS_MALFORMED")
    role_ids = {
        "primary_annotator": primary_ids,
        "independent_reviewer": review_ids,
    }
    role_references = {
        "primary_annotator": referenced_primary,
        "independent_reviewer": referenced_review,
    }
    seen: set[tuple[str, str]] = set()
    output: list[dict[str, Any]] = []
    for row in supplied:
        if not isinstance(row, Mapping):
            raise ValueError("SOURCE_GLYPH_DISPOSITION_MALFORMED")
        _exact_fields(
            row,
            _SOURCE_GLYPH_DISPOSITION_FIELDS,
            "SOURCE_GLYPH_DISPOSITION_FIELDS_UNEXPECTED",
        )
        role = row.get("observer_role")
        glyph_id = row.get("glyph_observation_id")
        if role not in role_ids or glyph_id not in role_ids[role]:
            raise ValueError("SOURCE_GLYPH_DISPOSITION_JOIN_INVALID")
        key = (role, glyph_id)
        if key in seen or glyph_id in role_references[role]:
            raise ValueError("SOURCE_GLYPH_DISPOSITION_DUPLICATE_OR_REFERENCED")
        disposition = row.get("disposition")
        rationale = row.get("rationale_code")
        if (
            disposition not in _SOURCE_GLYPH_DISPOSITION_RATIONALES
            or rationale not in _SOURCE_GLYPH_DISPOSITION_RATIONALES[disposition]
        ):
            raise ValueError("SOURCE_GLYPH_DISPOSITION_REASON_INVALID")
        seen.add(key)
        output.append(
            {
                "observer_role": role,
                "glyph_observation_id": glyph_id,
                "disposition": disposition,
                "rationale_code": rationale,
            }
        )
    for role, ids in role_ids.items():
        covered = role_references[role] | {
            glyph_id for disposition_role, glyph_id in seen if disposition_role == role
        }
        if covered != ids:
            raise ValueError("SOURCE_OBSERVATION_GLYPH_DISPOSITION_MISSING")
    return sorted(output, key=lambda row: (row["observer_role"], row["glyph_observation_id"]))


def seal_observation(
    task: Mapping[str, Any], draft: Mapping[str, Any], image: np.ndarray
) -> dict[str, Any]:
    _validate_task_shell(task)
    _validate_task_pixels(task, image)
    if not isinstance(draft, Mapping):
        raise ValueError("OBSERVATION_DRAFT_MALFORMED")
    _exact_fields(draft, _OBSERVATION_DRAFT_FIELDS, "OBSERVATION_DRAFT_FIELDS_UNEXPECTED")
    if draft.get("schema") != "zfd.visual_form_observation_draft.v1":
        raise ValueError("OBSERVATION_DRAFT_SCHEMA_INVALID")
    if draft.get("task_id") != task.get("task_id"):
        raise ValueError("OBSERVATION_TASK_JOIN_MISMATCH")
    annotator = _identity(draft.get("annotator_id"), "OBSERVER_IDENTITY_INVALID")
    role = draft.get("observer_role")
    if role not in _ROLES:
        raise ValueError("OBSERVER_IDENTITY_INVALID")
    if draft.get("independent_viewing_attestation") is not True:
        raise ValueError("INDEPENDENT_VIEWING_ATTESTATION_MISSING")
    if draft.get("source_lane") != "human_image_aligned" or draft.get("inherited_text_used") is not False:
        raise ValueError("SOURCE_LANE_TAINTED")
    glyphs, references = _normalise_glyphs(
        task,
        draft.get("glyphs"),
        image,
        id_schema="zfd.visual_form_observation_identity.v1",
        id_field="glyph_observation_id",
        identity_context={"annotator_id": annotator, "observer_role": role},
    )
    exclusions = draft.get("candidate_exclusions", [])
    dispositions = _component_dispositions(task, glyphs, references, exclusions)
    unresolved = any(row["label_state"] == "unresolved" for row in glyphs) or any(
        row["status"] == "unresolved" for row in dispositions
    )
    payload = {
        "schema": OBSERVATION_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "task_id": task["task_id"],
        "task_receipt_sha256": task["receipt_sha256"],
        "page_id": task["page_id"],
        "line_id": task["line_id"],
        "image_sha256": task["image_sha256"],
        "annotator_id": annotator,
        "observer_role": role,
        "independent_viewing_attestation": True,
        "source_lane": "human_image_aligned",
        "inherited_text_used": False,
        "glyphs": glyphs,
        "candidate_exclusions": list(exclusions),
        "component_dispositions": dispositions,
        "line_state": (
            "visual_form_review_complete_with_unresolved"
            if unresolved
            else "visual_form_review_complete"
        ),
        "semantic_class_authority_count": 0,
        "authority_promotion_eligible": False,
        "accuracy_claim_allowed": False,
    }
    observation_id = _content_id(
        {"schema": "zfd.visual_form_observation_receipt_identity.v1", **payload}
    )
    return _receipt({**payload, "observation_id": observation_id})


def validate_observation(
    observation: Mapping[str, Any], task: Mapping[str, Any], image: np.ndarray
) -> tuple[str, ...]:
    errors: list[str] = []
    if not isinstance(observation, Mapping) or not _receipt_valid(observation):
        errors.append("OBSERVATION_RECEIPT_HASH_MISMATCH")
    try:
        draft = {
            "schema": "zfd.visual_form_observation_draft.v1",
            "task_id": observation.get("task_id"),
            "annotator_id": observation.get("annotator_id"),
            "observer_role": observation.get("observer_role"),
            "independent_viewing_attestation": observation.get("independent_viewing_attestation"),
            "source_lane": observation.get("source_lane"),
            "inherited_text_used": observation.get("inherited_text_used"),
            "glyphs": [
                {
                    key: row.get(key)
                    for key in (
                        "ordinal",
                        "bbox",
                        "polygons",
                        "stage_a_candidate_ids",
                        "label_state",
                        "opaque_class_id",
                        "alternatives",
                        "certainty",
                        "uncertainty_codes",
                    )
                }
                for row in observation.get("glyphs", [])
            ],
            "candidate_exclusions": observation.get("candidate_exclusions", []),
        }
        expected = seal_observation(task, draft, image)
        if canonical_json(dict(observation)) != canonical_json(expected):
            errors.append("OBSERVATION_RECOMPUTE_MISMATCH")
    except Exception as error:
        errors.append(f"OBSERVATION_RECOMPUTE_FAILED:{type(error).__name__}:{error}")
    return tuple(dict.fromkeys(errors))


def seal_adjudication(
    task: Mapping[str, Any],
    primary: Mapping[str, Any],
    reviewer: Mapping[str, Any],
    draft: Mapping[str, Any],
    image: np.ndarray,
) -> dict[str, Any]:
    _validate_task_shell(task)
    _validate_task_pixels(task, image)
    if not isinstance(draft, Mapping):
        raise ValueError("ADJUDICATION_DRAFT_MALFORMED")
    _exact_fields(draft, _ADJUDICATION_DRAFT_FIELDS, "ADJUDICATION_DRAFT_FIELDS_UNEXPECTED")
    if validate_observation(primary, task, image) or validate_observation(reviewer, task, image):
        raise ValueError("SOURCE_OBSERVATION_INVALID")
    if primary.get("observer_role") != "primary_annotator" or reviewer.get("observer_role") != "independent_reviewer":
        raise ValueError("SOURCE_OBSERVATION_ROLES_INVALID")
    if draft.get("schema") != "zfd.visual_form_adjudication_draft.v1" or draft.get("task_id") != task.get("task_id"):
        raise ValueError("ADJUDICATION_DRAFT_JOIN_INVALID")
    if (
        draft.get("primary_observation_receipt_sha256") != primary.get("receipt_sha256")
        or draft.get("review_observation_receipt_sha256") != reviewer.get("receipt_sha256")
    ):
        raise ValueError("ADJUDICATION_OBSERVATION_JOIN_MISMATCH")
    adjudicator = _identity(draft.get("adjudicator_id"), "ADJUDICATOR_IDENTITY_INVALID")
    identities = [
        _identity(primary.get("annotator_id"), "OBSERVER_IDENTITY_INVALID"),
        _identity(reviewer.get("annotator_id"), "OBSERVER_IDENTITY_INVALID"),
        adjudicator,
    ]
    if len({value.casefold() for value in identities}) != 3:
        raise ValueError("REVIEW_IDENTITIES_NOT_DISTINCT")
    if draft.get("source_lane") != "human_image_aligned" or draft.get("inherited_text_used") is not False:
        raise ValueError("SOURCE_LANE_TAINTED")
    glyphs, references = _normalise_glyphs(
        task,
        draft.get("glyphs"),
        image,
        id_schema="zfd.visual_form_adjudication_identity.v1",
        id_field="adjudicated_glyph_id",
        identity_context={
            "adjudicator_id": adjudicator,
            "primary_observation_receipt_sha256": primary.get("receipt_sha256"),
            "review_observation_receipt_sha256": reviewer.get("receipt_sha256"),
        },
        adjudication=True,
    )
    primary_by_id = {row["glyph_observation_id"]: row for row in primary["glyphs"]}
    review_by_id = {row["glyph_observation_id"]: row for row in reviewer["glyphs"]}
    primary_ids = set(primary_by_id)
    review_ids = set(review_by_id)
    referenced_primary: set[str] = set()
    referenced_review: set[str] = set()
    for row in glyphs:
        source_groups = row.get("source_observation_glyph_ids")
        if not isinstance(source_groups, Mapping):
            raise ValueError("ADJUDICATED_GLYPH_SOURCE_JOIN_INVALID")
        primary_source_ids = source_groups.get("primary")
        review_source_ids = source_groups.get("independent_reviewer")
        if (
            not isinstance(primary_source_ids, list)
            or not primary_source_ids
            or not isinstance(review_source_ids, list)
            or not review_source_ids
            or any(value not in primary_ids for value in primary_source_ids)
            or any(value not in review_ids for value in review_source_ids)
        ):
            raise ValueError("ADJUDICATED_GLYPH_SOURCE_JOIN_INVALID")
        source_rows = [
            *(primary_by_id[value] for value in primary_source_ids),
            *(review_by_id[value] for value in review_source_ids),
        ]
        referenced_primary.update(primary_source_ids)
        referenced_review.update(review_source_ids)
        adjudicated_box = tuple(row["bbox"])
        adjudicated_polygons = tuple(
            _polygon(value, code="ADJUDICATED_GLYPH_POLYGONS_INVALID")
            for value in row["polygons"]
        )
        adjudicated_candidates = set(row["stage_a_candidate_ids"])
        for source_row in source_rows:
            if not _overlaps(adjudicated_box, tuple(source_row["bbox"])):
                raise ValueError("ADJUDICATED_GLYPH_SOURCE_GEOMETRY_DISJOINT")
            source_polygons = tuple(
                _polygon(value, code="SOURCE_OBSERVATION_GLYPH_POLYGONS_INVALID")
                for value in source_row["polygons"]
            )
            if not _polygons_share_interior_pixel(adjudicated_polygons, source_polygons):
                raise ValueError("ADJUDICATED_GLYPH_SOURCE_GEOMETRY_DISJOINT")
            source_candidates = set(source_row["stage_a_candidate_ids"])
            if (
                adjudicated_candidates
                and source_candidates
                and adjudicated_candidates.isdisjoint(source_candidates)
            ):
                raise ValueError("ADJUDICATED_GLYPH_SOURCE_CANDIDATE_DISJOINT")
        if not row.get("rationale_codes"):
            raise ValueError("ADJUDICATION_RATIONALE_MISSING")
    source_dispositions = _source_glyph_dispositions(
        primary_ids,
        review_ids,
        referenced_primary,
        referenced_review,
        draft.get("source_glyph_dispositions", []),
    )
    exclusions = draft.get("candidate_exclusions", [])
    dispositions = _component_dispositions(task, glyphs, references, exclusions)
    unresolved = (
        any(row["label_state"] == "unresolved" for row in glyphs)
        or any(row["status"] == "unresolved" for row in dispositions)
        or any(
            row["disposition"] == "unresolved_conflict" for row in source_dispositions
        )
    )
    blocking = ["SPLIT_AUTHORITY_UNASSIGNED", "DIPLOMATIC_LABEL_AUTHORITY_UNBOUND"]
    if unresolved:
        blocking.append("ADJUDICATED_LINE_CONTAINS_UNRESOLVED")
    payload = {
        "schema": ADJUDICATION_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "task_id": task["task_id"],
        "task_receipt_sha256": task["receipt_sha256"],
        "page_id": task["page_id"],
        "line_id": task["line_id"],
        "image_sha256": task["image_sha256"],
        "primary_observation_id": primary["observation_id"],
        "primary_observation_receipt_sha256": primary["receipt_sha256"],
        "review_observation_id": reviewer["observation_id"],
        "review_observation_receipt_sha256": reviewer["receipt_sha256"],
        "adjudicator_id": adjudicator,
        "source_lane": "human_image_aligned",
        "inherited_text_used": False,
        "glyphs": glyphs,
        "candidate_exclusions": list(exclusions),
        "component_dispositions": dispositions,
        "source_glyph_dispositions": source_dispositions,
        "review_state": (
            "visual_form_adjudicated_with_unresolved"
            if unresolved
            else "visual_form_adjudicated"
        ),
        "blocking_reasons": blocking,
        "semantic_class_authority_count": 0,
        "authority_promotion_eligible": False,
        "diplomatic_sequence_authority_eligible": False,
        "accuracy_claim_allowed": False,
        "confirmed_translated": False,
    }
    adjudication_id = _content_id(
        {"schema": "zfd.visual_form_adjudication_receipt_identity.v1", **payload}
    )
    return _receipt({**payload, "adjudication_id": adjudication_id})


def validate_adjudication(
    adjudication: Mapping[str, Any],
    task: Mapping[str, Any],
    primary: Mapping[str, Any],
    reviewer: Mapping[str, Any],
    image: np.ndarray,
) -> tuple[str, ...]:
    errors: list[str] = []
    if not isinstance(adjudication, Mapping) or not _receipt_valid(adjudication):
        errors.append("ADJUDICATION_RECEIPT_HASH_MISMATCH")
    try:
        draft = {
            "schema": "zfd.visual_form_adjudication_draft.v1",
            "task_id": adjudication.get("task_id"),
            "primary_observation_receipt_sha256": adjudication.get(
                "primary_observation_receipt_sha256"
            ),
            "review_observation_receipt_sha256": adjudication.get(
                "review_observation_receipt_sha256"
            ),
            "adjudicator_id": adjudication.get("adjudicator_id"),
            "source_lane": adjudication.get("source_lane"),
            "inherited_text_used": adjudication.get("inherited_text_used"),
            "glyphs": [
                {
                    key: row.get(key)
                    for key in (
                        "ordinal",
                        "bbox",
                        "polygons",
                        "stage_a_candidate_ids",
                        "label_state",
                        "opaque_class_id",
                        "alternatives",
                        "certainty",
                        "uncertainty_codes",
                        "source_observation_glyph_ids",
                        "rationale_codes",
                    )
                }
                for row in adjudication.get("glyphs", [])
            ],
            "candidate_exclusions": adjudication.get("candidate_exclusions", []),
            "source_glyph_dispositions": adjudication.get(
                "source_glyph_dispositions", []
            ),
        }
        expected = seal_adjudication(task, primary, reviewer, draft, image)
        if canonical_json(dict(adjudication)) != canonical_json(expected):
            errors.append("ADJUDICATION_RECOMPUTE_MISMATCH")
    except Exception as error:
        errors.append(f"ADJUDICATION_RECOMPUTE_FAILED:{type(error).__name__}:{error}")
    return tuple(dict.fromkeys(errors))
