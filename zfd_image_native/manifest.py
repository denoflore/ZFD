"""Canonical page identity and corpus coverage records."""

from __future__ import annotations

from dataclasses import dataclass
from collections import Counter
from pathlib import Path
from typing import Iterable

from .io import read_json, read_jsonl
from .models import PageRecord


SOURCE_ID = "yale-ms-408"


@dataclass(frozen=True)
class ReconciliationReport:
    authoritative_pages: int
    local_assets: int
    verified: tuple[str, ...]
    unverified: tuple[str, ...]
    missing: tuple[str, ...]

    @property
    def fully_verified(self) -> bool:
        return (
            self.authoritative_pages > 0
            and len(self.verified) == self.authoritative_pages
            and not self.unverified
            and not self.missing
        )


@dataclass(frozen=True)
class CorpusCoverageReport:
    total_pages: int
    present_pages: int
    missing_pages: int
    unexpected_pages: int
    duplicate_pages: int
    missing_page_ids: tuple[str, ...]
    unexpected_page_ids: tuple[str, ...]
    duplicate_page_ids: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return self.missing_pages == 0 and self.unexpected_pages == 0 and self.duplicate_pages == 0


def build_page_manifest(map_path: str | Path) -> list[PageRecord]:
    payload = read_json(map_path)
    if not isinstance(payload, dict):
        raise ValueError("Official page map must be a JSON object")
    pages: list[PageRecord] = []
    page_ids: set[str] = set()
    bases: set[str] = set()
    for surface_label, raw_base in payload.items():
        base = str(raw_base).rstrip("/")
        iiif_id = base.rsplit("/", 1)[-1]
        page_id = f"{SOURCE_ID}:iiif:{iiif_id}"
        if page_id in page_ids or base in bases:
            raise ValueError(f"Duplicate page identity: {surface_label}")
        page_ids.add(page_id)
        bases.add(base)
        pages.append(
            PageRecord(
                page_id=page_id,
                source_id=SOURCE_ID,
                surface_label=str(surface_label),
                iiif_id=iiif_id,
                iiif_base_uri=base,
                image_request_uri=f"{base}/full/2000,/0/default.jpg",
            )
        )
    return pages


def load_page_manifest(path: str | Path) -> list[PageRecord]:
    pages = [PageRecord(**row) for row in read_jsonl(path)]
    page_ids: set[str] = set()
    iiif_ids: set[str] = set()
    for page in pages:
        if page.page_id in page_ids:
            raise ValueError(f"Duplicate page_id in manifest: {page.page_id}")
        if page.iiif_id in iiif_ids:
            raise ValueError(f"Duplicate iiif_id in manifest: {page.iiif_id}")
        page_ids.add(page.page_id)
        iiif_ids.add(page.iiif_id)
    return pages


def reconcile_local_assets(
    authority_pages: Iterable[PageRecord], local_image_root: str | Path
) -> ReconciliationReport:
    pages = list(authority_pages)
    root = Path(local_image_root)
    assets = sorted(path for path in root.glob("*.jpg") if path.is_file()) if root.is_dir() else []
    return ReconciliationReport(
        authoritative_pages=len(pages),
        local_assets=len(assets),
        verified=(),
        unverified=tuple(path.name for path in assets),
        missing=tuple(page.page_id for page in pages),
    )


def validate_corpus_coverage(
    authority_pages: Iterable[PageRecord], ocr_page_ids: Iterable[str]
) -> CorpusCoverageReport:
    expected_rows = [page.page_id for page in authority_pages]
    if len(expected_rows) != len(set(expected_rows)):
        raise ValueError("Authority page IDs must be unique")
    observed_rows = list(ocr_page_ids)
    counts = Counter(observed_rows)
    duplicates = tuple(sorted(page_id for page_id, count in counts.items() if count > 1))
    expected = set(expected_rows)
    observed = set(observed_rows)
    missing = tuple(sorted(expected - observed))
    unexpected = tuple(sorted(observed - expected))
    return CorpusCoverageReport(
        total_pages=len(expected),
        present_pages=len(expected & observed),
        missing_pages=len(missing),
        unexpected_pages=len(unexpected),
        duplicate_pages=len(duplicates),
        missing_page_ids=missing,
        unexpected_page_ids=unexpected,
        duplicate_page_ids=duplicates,
    )
