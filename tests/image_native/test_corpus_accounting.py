"""Whole corpus execution must conserve the authority manifest identity."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from PIL import Image
import pytest

from zfd_image_native import corpus as corpus_module
from zfd_image_native.corpus import run_corpus
from zfd_image_native.io import sha256_file
from zfd_image_native.manifest import CorpusCoverageReport
from zfd_image_native.models import PageRecord


def _page(tmp_path: Path) -> PageRecord:
    image_path = tmp_path / "page.png"
    Image.new("RGB", (80, 60), "white").save(image_path)
    return PageRecord(
        page_id="yale-ms-408:iiif:fixture",
        source_id="yale-ms-408",
        surface_label="fixture",
        iiif_id="fixture",
        iiif_base_uri="https://example.invalid/iiif/2/fixture",
        image_request_uri="https://example.invalid/iiif/2/fixture/full/max/0/default.jpg",
        image_sha256=sha256_file(image_path),
        image_path=str(image_path),
        width=80,
        height=60,
        mime_type="image/png",
        acquisition_status="verified",
    )


def test_corpus_run_rejects_empty_or_missing_authority_page_ids(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="authority manifest is empty"):
        run_corpus([], tmp_path / "empty-corpus")

    page = replace(_page(tmp_path), page_id="")
    with pytest.raises(ValueError, match="missing page IDs"):
        run_corpus([page], tmp_path / "blank-id-corpus")


def test_corpus_run_rejects_duplicate_authority_page_ids_before_processing(
    monkeypatch, tmp_path: Path
) -> None:
    page = _page(tmp_path)
    called = False

    def unexpected_process(*_args, **_kwargs):
        nonlocal called
        called = True
        raise AssertionError("processing must not start")

    monkeypatch.setattr(corpus_module, "process_page", unexpected_process)

    with pytest.raises(ValueError, match="duplicate page IDs"):
        run_corpus([page, page], tmp_path / "duplicate-corpus")

    assert called is False


def test_corpus_run_enforces_exact_authority_coverage_gate(monkeypatch, tmp_path: Path) -> None:
    page = _page(tmp_path)
    calls: list[tuple[tuple[str, ...], tuple[str, ...]]] = []

    def incomplete_coverage(authority_pages, observed_page_ids):
        authority = tuple(item.page_id for item in authority_pages)
        observed = tuple(observed_page_ids)
        calls.append((authority, observed))
        return CorpusCoverageReport(
            total_pages=1,
            present_pages=0,
            missing_pages=1,
            unexpected_pages=0,
            duplicate_pages=0,
            missing_page_ids=(page.page_id,),
            unexpected_page_ids=(),
            duplicate_page_ids=(),
        )

    monkeypatch.setattr(corpus_module, "validate_corpus_coverage", incomplete_coverage, raising=False)

    with pytest.raises(ValueError, match="Corpus coverage mismatch"):
        run_corpus([page], tmp_path / "coverage-corpus")

    assert calls == [((page.page_id,), (page.page_id,))]
