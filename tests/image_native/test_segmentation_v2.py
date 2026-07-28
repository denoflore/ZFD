"""Segmentation v2 rejects page wide joins and exposes unresolved layout ink."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image
import pytest

from zfd_image_native import ocr as ocr_module
from zfd_image_native.io import sha256_file
from zfd_image_native.manifest import load_page_manifest
from zfd_image_native.models import PageRecord
from zfd_image_native.ocr import (
    OpenSetConfig,
    _Component,
    _line_groups,
    process_page,
)


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data" / "image_native" / "voynich_pages.jsonl"


def _acquired_page(iiif_id: str) -> PageRecord:
    page = next(
        page for page in load_page_manifest(MANIFEST) if page.iiif_id == iiif_id
    )
    image_path = ROOT / page.image_path if page.image_path else None
    if image_path is None or not image_path.is_file():
        pytest.skip(f"requires acquired Yale image {iiif_id}")
    return PageRecord(**{**page.__dict__, "image_path": str(image_path)})


def _run(start_x: int) -> list[_Component]:
    return [
        _Component(x=start_x + index * 15, y=100, width=10, height=10, area=80)
        for index in range(5)
    ]


def test_disconnected_same_y_components_do_not_form_one_line() -> None:
    config = OpenSetConfig(maximum_intercomponent_gap_heights=8.0)
    groups = _line_groups(_run(100) + _run(600), 1000, 1200, config)

    assert len(groups) == 2
    assert max(item.x + item.width for item in groups[0]) < min(item.x for item in groups[1])


def test_real_cartesian_fragments_obey_continuity_and_expose_rejections() -> None:
    page = _acquired_page("1006076")
    config = OpenSetConfig()
    result = process_page(page, config)

    assert result.lines
    assert result.rejected_components
    assert all(line.geometry_mode == "cartesian_fragment" for line in result.lines)
    assert all(line.ink_density >= config.minimum_line_ink_density for line in result.lines)
    assert all(item.reason for item in result.rejected_components)
    assigned = {glyph.bbox for glyph in result.graphemes}
    rejected = {item.bbox for item in result.rejected_components}
    assert assigned.isdisjoint(rejected)


def test_radial_page_is_flagged_for_layout_review_without_external_model() -> None:
    page = _acquired_page("1006187")
    result = process_page(page, OpenSetConfig())

    assert result.layout_disposition == "layout_review_required"
    assert result.disposition == "segmented_unrecognized_layout_review"
    assert all(glyph.diplomatic_label is None for glyph in result.graphemes)


def test_every_connected_component_is_emitted_with_threshold_rejection_reason(
    monkeypatch, tmp_path: Path
) -> None:
    image_path = tmp_path / "component-accounting.png"
    Image.new("RGB", (240, 100), "white").save(image_path)
    page = PageRecord(
        page_id="yale-ms-408:iiif:component-accounting",
        source_id="yale-ms-408",
        surface_label="fixture",
        iiif_id="component-accounting",
        iiif_base_uri="https://example.invalid/iiif/2/component-accounting",
        image_request_uri="https://example.invalid/iiif/2/component-accounting/full/max/0/default.jpg",
        image_sha256=sha256_file(image_path),
        image_path=str(image_path),
        width=240,
        height=100,
        mime_type="image/png",
        acquisition_status="verified",
    )
    mask = np.zeros((100, 240), dtype=np.uint8)
    for x in (20, 40, 60, 80):
        mask[40:50, x : x + 8] = 255
    mask[5:7, 5:7] = 255
    mask[5:30, 115:119] = 255
    mask[65:75, 135:150] = 255
    mask[80:88, 170:230] = 255
    raw_component_count = cv2.connectedComponentsWithStats(mask, connectivity=8)[0] - 1
    monkeypatch.setattr(ocr_module, "_binary_mask", lambda _gray, _config: mask.copy())

    result = process_page(
        page,
        OpenSetConfig(
            minimum_component_area=5,
            minimum_component_height_fraction=0.03,
            maximum_component_height_fraction=0.20,
            maximum_component_width_fraction=0.20,
            maximum_component_area_fraction=0.005,
            min_components_per_line=4,
        ),
    )

    assert len(result.graphemes) + len(result.rejected_components) == raw_component_count
    assert all(item.bbox and item.polygon for item in result.rejected_components)
    reasons = "\n".join(item.reason for item in result.rejected_components)
    assert "area_below_minimum_pixels" in reasons
    assert "area_above_maximum_page_fraction" in reasons
    assert "height_above_maximum_page_fraction" in reasons
    assert "width_above_maximum_page_fraction" in reasons
