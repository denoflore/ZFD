"""Deterministic pixel segmentation with open set unknown rejection."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
from statistics import median

import cv2
import numpy as np

from .io import canonical_json, sha256_file
from .models import PageRecord


@dataclass(frozen=True)
class OpenSetConfig:
    adaptive_block_size: int = 35
    adaptive_c: int = 11
    minimum_component_area: int = 4
    minimum_component_height_fraction: float = 0.003
    maximum_component_height_fraction: float = 0.08
    maximum_component_width_fraction: float = 0.20
    maximum_component_area_fraction: float = 0.02
    line_centre_tolerance: float = 0.75
    minimum_line_span_fraction: float = 0.03
    min_components_per_line: int = 4
    region_gap_multiplier: float = 3.0
    descriptor_size: int = 32
    maximum_intercomponent_gap_heights: float = 8.0
    minimum_line_ink_density: float = 0.08
    maximum_core_line_height_multiplier: float = 3.5
    layout_review_rejection_fraction: float = 0.5
    maximum_cartesian_lines_per_vertical_pixel: float = 0.06
    segmentation_version: str = "2.0.0"

    def __post_init__(self) -> None:
        if self.adaptive_block_size < 3:
            raise ValueError("adaptive_block_size must be at least 3")
        if self.min_components_per_line < 1:
            raise ValueError("min_components_per_line must be positive")
        if self.descriptor_size < 8:
            raise ValueError("descriptor_size must be at least 8")
        if self.maximum_intercomponent_gap_heights <= 0:
            raise ValueError("maximum_intercomponent_gap_heights must be positive")
        if not 0.0 <= self.minimum_line_ink_density <= 1.0:
            raise ValueError("minimum_line_ink_density must be between zero and one")
        if self.maximum_core_line_height_multiplier <= 0:
            raise ValueError("maximum_core_line_height_multiplier must be positive")
        if not 0.0 <= self.layout_review_rejection_fraction <= 1.0:
            raise ValueError("layout_review_rejection_fraction must be between zero and one")
        if self.maximum_cartesian_lines_per_vertical_pixel <= 0:
            raise ValueError("maximum_cartesian_lines_per_vertical_pixel must be positive")


@dataclass(frozen=True)
class Alternative:
    candidate_id: str
    score: float
    candidate_type: str = "visual_cluster"


@dataclass(frozen=True)
class RegionResult:
    region_id: str
    bbox: tuple[int, int, int, int]
    polygon: tuple[tuple[int, int], ...]
    line_ids: tuple[str, ...]


@dataclass(frozen=True)
class LineResult:
    line_id: str
    region_id: str
    bbox: tuple[int, int, int, int]
    polygon: tuple[tuple[int, int], ...]
    grapheme_ids: tuple[str, ...]
    geometry_mode: str = "cartesian_fragment"
    maximum_gap_heights: float = 0.0
    ink_density: float = 0.0


@dataclass(frozen=True)
class GraphemeResult:
    grapheme_id: str
    line_id: str
    region_id: str
    bbox: tuple[int, int, int, int]
    polygon: tuple[tuple[int, int], ...]
    visual_fingerprint: str
    alternatives: tuple[Alternative, ...]
    unknown_score: float
    recognition_confidence: float
    diplomatic_label: str | None


@dataclass(frozen=True)
class RejectedComponent:
    component_id: str
    bbox: tuple[int, int, int, int]
    polygon: tuple[tuple[int, int], ...]
    reason: str


@dataclass(frozen=True)
class PageOCRResult:
    page_id: str
    source_id: str
    page_sha256: str
    width: int
    height: int
    config_sha256: str
    disposition: str
    regions: tuple[RegionResult, ...]
    lines: tuple[LineResult, ...]
    graphemes: tuple[GraphemeResult, ...]
    rejected_components: tuple[RejectedComponent, ...] = ()
    layout_disposition: str = "cartesian_provisional"


@dataclass(frozen=True)
class _Component:
    x: int
    y: int
    width: int
    height: int
    area: int
    label: int = 0

    @property
    def centre_y(self) -> float:
        return self.y + self.height / 2.0


@dataclass(frozen=True)
class _ComponentRejection:
    component: _Component
    reason: str


def _component_sort_key(component: _Component) -> tuple[float, int, int, int, int, int]:
    return (
        component.centre_y,
        component.x,
        component.y,
        component.width,
        component.height,
        component.label,
    )


def _polygon(box: tuple[int, int, int, int]) -> tuple[tuple[int, int], ...]:
    x, y, width, height = box
    return ((x, y), (x + width, y), (x + width, y + height), (x, y + height))


def _union_box(components: list[_Component]) -> tuple[int, int, int, int]:
    left = min(item.x for item in components)
    top = min(item.y for item in components)
    right = max(item.x + item.width for item in components)
    bottom = max(item.y + item.height for item in components)
    return left, top, right - left, bottom - top


def _decode(path: Path) -> np.ndarray:
    payload = np.frombuffer(path.read_bytes(), dtype=np.uint8)
    image = cv2.imdecode(payload, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Cannot decode image: {path}")
    return image


def _binary_mask(gray: np.ndarray, config: OpenSetConfig) -> np.ndarray:
    smallest = min(gray.shape[:2])
    block = min(config.adaptive_block_size, smallest if smallest % 2 else smallest - 1)
    block = max(3, block if block % 2 else block - 1)
    mask = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        block,
        config.adaptive_c,
    )
    return cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((2, 2), dtype=np.uint8))


def _components(
    mask: np.ndarray, config: OpenSetConfig
) -> tuple[list[_Component], list[_ComponentRejection]]:
    height, width = mask.shape
    count, _, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    minimum_height = max(3, round(height * config.minimum_component_height_fraction))
    maximum_height = max(minimum_height, round(height * config.maximum_component_height_fraction))
    maximum_width = max(3, round(width * config.maximum_component_width_fraction))
    maximum_area = max(config.minimum_component_area, round(width * height * config.maximum_component_area_fraction))
    found: list[_Component] = []
    rejected: list[_ComponentRejection] = []
    for label in range(1, count):
        x, y, component_width, component_height, area = (int(value) for value in stats[label])
        component = _Component(x, y, component_width, component_height, area, label)
        reasons: list[str] = []
        if area < config.minimum_component_area:
            reasons.append("area_below_minimum_pixels")
        if area > maximum_area:
            reasons.append("area_above_maximum_page_fraction")
        if component_height < minimum_height:
            reasons.append("height_below_minimum_page_fraction")
        if component_height > maximum_height:
            reasons.append("height_above_maximum_page_fraction")
        if component_width < 1:
            reasons.append("width_below_one_pixel")
        if component_width > maximum_width:
            reasons.append("width_above_maximum_page_fraction")
        aspect = component_width / component_height
        if aspect < 0.03:
            reasons.append("aspect_ratio_below_minimum")
        if aspect > 12.0:
            reasons.append("aspect_ratio_above_maximum")
        if reasons:
            rejected.append(
                _ComponentRejection(
                    component=component,
                    reason="threshold_rejected:" + ",".join(reasons),
                )
            )
            continue
        found.append(component)
    return (
        sorted(found, key=_component_sort_key),
        sorted(rejected, key=lambda item: _component_sort_key(item.component)),
    )


def _line_groups(
    components: list[_Component],
    page_width: int,
    page_height: int,
    config: OpenSetConfig,
) -> list[list[_Component]]:
    groups: list[list[_Component]] = []
    for component in components:
        best_index: int | None = None
        best_distance: float | None = None
        for index, group in enumerate(groups):
            centre = median(item.centre_y for item in group)
            typical_height = median(item.height for item in group)
            capped_component_height = min(component.height, typical_height * 2.0)
            tolerance = max(
                3.0,
                config.line_centre_tolerance
                * max(typical_height, capped_component_height),
            )
            distance = abs(component.centre_y - centre)
            if distance <= tolerance and (best_distance is None or distance < best_distance):
                best_index = index
                best_distance = distance
        if best_index is None:
            groups.append([component])
        else:
            groups[best_index].append(component)

    candidates: list[list[_Component]] = []
    for group in groups:
        ordered = sorted(group, key=lambda item: (item.x, item.y))
        typical_height = median(item.height for item in ordered)
        maximum_gap = typical_height * config.maximum_intercomponent_gap_heights
        current: list[_Component] = []
        current_right: int | None = None
        for component in ordered:
            gap = component.x - current_right if current_right is not None else 0
            if current and gap > maximum_gap:
                candidates.append(current)
                current = []
                current_right = None
            current.append(component)
            current_right = max(
                current_right if current_right is not None else component.x,
                component.x + component.width,
            )
        if current:
            candidates.append(current)

    accepted: list[list[_Component]] = []
    minimum_span = page_width * config.minimum_line_span_fraction
    for group in candidates:
        ordered = sorted(group, key=lambda item: (item.x, item.y))
        box = _union_box(ordered)
        typical_height = median(item.height for item in ordered)
        height_limit = float(np.percentile([item.height for item in ordered], 80))
        core = [item for item in ordered if item.height <= height_limit]
        core_box = _union_box(core or ordered)
        clipped_ink_width = sum(
            min(item.width, typical_height * 4.0) for item in ordered
        )
        ink_density = clipped_ink_width / max(1.0, box[2])
        if len(ordered) < config.min_components_per_line:
            continue
        if box[2] < minimum_span:
            continue
        if core_box[3] > typical_height * config.maximum_core_line_height_multiplier:
            continue
        if ink_density < config.minimum_line_ink_density:
            continue
        accepted.append(ordered)
    return sorted(accepted, key=lambda group: (_union_box(group)[1], _union_box(group)[0]))


def _line_quality(components: list[_Component]) -> tuple[float, float]:
    ordered = sorted(components, key=lambda item: (item.x, item.y))
    typical_height = max(1.0, float(median(item.height for item in ordered)))
    gaps: list[int] = []
    running_right = ordered[0].x + ordered[0].width
    for component in ordered[1:]:
        gaps.append(max(0, component.x - running_right))
        running_right = max(running_right, component.x + component.width)
    maximum_gap_heights = max(gaps, default=0) / typical_height
    box = _union_box(ordered)
    ink_density = sum(min(item.width, typical_height * 4.0) for item in ordered) / max(
        1.0, box[2]
    )
    return maximum_gap_heights, ink_density


def _region_groups(lines: list[list[_Component]], config: OpenSetConfig) -> list[list[list[_Component]]]:
    if not lines:
        return []
    regions: list[list[list[_Component]]] = [[lines[0]]]
    for line in lines[1:]:
        previous = regions[-1][-1]
        previous_box = _union_box(previous)
        current_box = _union_box(line)
        typical_height = median([item.height for item in previous + line])
        gap = current_box[1] - (previous_box[1] + previous_box[3])
        if gap <= max(6.0, typical_height * config.region_gap_multiplier):
            regions[-1].append(line)
        else:
            regions.append([line])
    return regions


def _fingerprint(mask: np.ndarray, component: _Component, size: int) -> str:
    crop = mask[
        component.y : component.y + component.height,
        component.x : component.x + component.width,
    ]
    side = max(crop.shape)
    canvas = np.zeros((side, side), dtype=np.uint8)
    y_offset = (side - crop.shape[0]) // 2
    x_offset = (side - crop.shape[1]) // 2
    canvas[y_offset : y_offset + crop.shape[0], x_offset : x_offset + crop.shape[1]] = crop
    normalized = cv2.resize(canvas, (size, size), interpolation=cv2.INTER_AREA)
    return sha256(normalized.tobytes()).hexdigest()


def process_page(page: PageRecord, config: OpenSetConfig | None = None) -> PageOCRResult:
    config = config or OpenSetConfig()
    config_sha256 = sha256(canonical_json(asdict(config)).encode("utf-8")).hexdigest()
    identity_namespace = f"{page.page_id}:ocr:{config_sha256[:16]}"
    if not page.image_path:
        raise ValueError(f"Page has no image path: {page.page_id}")
    path = Path(page.image_path)
    if not path.is_file():
        raise FileNotFoundError(path)
    actual_sha256 = sha256_file(path)
    if not page.image_sha256 or actual_sha256.lower() != page.image_sha256.lower():
        raise ValueError(f"Image checksum mismatch for {page.page_id}")

    image = _decode(path)
    height, width = image.shape[:2]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mask = _binary_mask(gray, config)
    components, threshold_rejections = _components(mask, config)
    line_groups = _line_groups(components, width, height, config)
    region_groups = _region_groups(line_groups, config)

    region_results: list[RegionResult] = []
    line_results: list[LineResult] = []
    grapheme_results: list[GraphemeResult] = []
    assigned_components: set[_Component] = set()
    line_number = 0
    grapheme_number = 0

    for region_number, region_lines in enumerate(region_groups, start=1):
        region_id = f"{identity_namespace}:region:{region_number:04d}"
        region_components = [item for line in region_lines for item in line]
        region_box = _union_box(region_components)
        region_line_ids: list[str] = []
        for line_components in region_lines:
            assigned_components.update(line_components)
            line_number += 1
            line_id = f"{identity_namespace}:line:{line_number:04d}"
            region_line_ids.append(line_id)
            line_box = _union_box(line_components)
            grapheme_ids: list[str] = []
            for component in line_components:
                grapheme_number += 1
                grapheme_id = f"{identity_namespace}:grapheme:{grapheme_number:06d}"
                grapheme_ids.append(grapheme_id)
                box = (component.x, component.y, component.width, component.height)
                fingerprint = _fingerprint(mask, component, config.descriptor_size)
                grapheme_results.append(
                    GraphemeResult(
                        grapheme_id=grapheme_id,
                        line_id=line_id,
                        region_id=region_id,
                        bbox=box,
                        polygon=_polygon(box),
                        visual_fingerprint=fingerprint,
                        alternatives=(Alternative(f"visual:{fingerprint[:16]}", 0.0),),
                        unknown_score=1.0,
                        recognition_confidence=0.0,
                        diplomatic_label=None,
                    )
                )
            maximum_gap_heights, ink_density = _line_quality(line_components)
            line_results.append(
                LineResult(
                    line_id=line_id,
                    region_id=region_id,
                    bbox=line_box,
                    polygon=_polygon(line_box),
                    grapheme_ids=tuple(grapheme_ids),
                    geometry_mode="cartesian_fragment",
                    maximum_gap_heights=maximum_gap_heights,
                    ink_density=ink_density,
                )
            )
        region_results.append(
            RegionResult(
                region_id=region_id,
                bbox=region_box,
                polygon=_polygon(region_box),
                line_ids=tuple(region_line_ids),
            )
        )

    unassigned_components = [
        component for component in components if component not in assigned_components
    ]
    rejection_candidates = [
        *threshold_rejections,
        *(
            _ComponentRejection(
                component=component,
                reason="unassigned_after_cartesian_continuity_and_density_gates",
            )
            for component in unassigned_components
        ),
    ]
    rejection_candidates.sort(key=lambda item: _component_sort_key(item.component))
    rejected_components = tuple(
        RejectedComponent(
            component_id=f"{identity_namespace}:component-rejection:{index:06d}",
            bbox=(
                candidate.component.x,
                candidate.component.y,
                candidate.component.width,
                candidate.component.height,
            ),
            polygon=_polygon(
                (
                    candidate.component.x,
                    candidate.component.y,
                    candidate.component.width,
                    candidate.component.height,
                )
            ),
            reason=candidate.reason,
        )
        for index, candidate in enumerate(rejection_candidates, start=1)
    )
    rejected_fraction = len(unassigned_components) / len(components) if components else 1.0
    layout_disposition = (
        "layout_review_required"
        if rejected_fraction > config.layout_review_rejection_fraction
        or len(line_results) / max(1, height)
        > config.maximum_cartesian_lines_per_vertical_pixel
        else "cartesian_provisional"
    )
    if line_results:
        disposition = (
            "segmented_unrecognized_layout_review"
            if layout_disposition == "layout_review_required"
            else "segmented_unrecognized"
        )
    else:
        disposition = "no_text_detected_layout_review"
    return PageOCRResult(
        page_id=page.page_id,
        source_id=page.source_id,
        page_sha256=actual_sha256,
        width=width,
        height=height,
        config_sha256=config_sha256,
        disposition=disposition,
        regions=tuple(region_results),
        lines=tuple(line_results),
        graphemes=tuple(grapheme_results),
        rejected_components=rejected_components,
        layout_disposition=layout_disposition,
    )
