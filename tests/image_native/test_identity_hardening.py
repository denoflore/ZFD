"""Immutable corpus and OCR identity regression tests."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw
import pytest

from zfd_image_native.io import sha256_file, write_jsonl
from zfd_image_native.manifest import load_page_manifest, validate_corpus_coverage
from zfd_image_native.models import PageRecord
from zfd_image_native.ocr import OpenSetConfig, process_page


def _page(image_path: Path) -> PageRecord:
    return PageRecord(
        page_id="yale-ms-408:iiif:fixture",
        source_id="yale-ms-408",
        surface_label="fixture",
        iiif_id="fixture",
        iiif_base_uri="https://example.invalid/iiif/2/fixture",
        image_request_uri="https://example.invalid/iiif/2/fixture/full/max/0/default.jpg",
        image_sha256=sha256_file(image_path),
        image_path=str(image_path),
        width=240,
        height=120,
        mime_type="image/png",
        acquisition_status="verified",
    )


def test_page_manifest_rejects_duplicate_page_or_iiif_identity(tmp_path: Path) -> None:
    image = tmp_path / "fixture.png"
    Image.new("RGB", (240, 120), "white").save(image)
    page = _page(image)
    manifest = tmp_path / "pages.jsonl"
    write_jsonl(manifest, [page, page])

    with pytest.raises(ValueError, match="Duplicate page_id"):
        load_page_manifest(manifest)


def test_corpus_coverage_rejects_duplicate_observations(tmp_path: Path) -> None:
    image = tmp_path / "fixture.png"
    Image.new("RGB", (240, 120), "white").save(image)
    page = _page(image)

    report = validate_corpus_coverage([page], [page.page_id, page.page_id])

    assert report.ok is False
    assert report.duplicate_page_ids == (page.page_id,)


def test_configuration_change_produces_new_ocr_identity_namespace(tmp_path: Path) -> None:
    image_path = tmp_path / "fixture.png"
    image = Image.new("RGB", (240, 120), "white")
    draw = ImageDraw.Draw(image)
    for x in (20, 50, 80, 110, 140, 170):
        draw.rectangle((x, 40, x + 12, 46), fill="black")
    image.save(image_path)
    page = _page(image_path)
    first = process_page(page, OpenSetConfig(adaptive_c=11, min_components_per_line=3))
    second = process_page(page, OpenSetConfig(adaptive_c=9, min_components_per_line=3))

    assert first.config_sha256 != second.config_sha256
    assert first.regions and second.regions
    assert {item.region_id for item in first.regions}.isdisjoint(
        {item.region_id for item in second.regions}
    )
    assert {item.line_id for item in first.lines}.isdisjoint({item.line_id for item in second.lines})
    assert {item.grapheme_id for item in first.graphemes}.isdisjoint(
        {item.grapheme_id for item in second.graphemes}
    )
