"""Whole corpus execution with explicit missing and failure dispositions."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from .io import write_json, write_jsonl
from .manifest import validate_corpus_coverage
from .models import PageRecord
from .ocr import OpenSetConfig, process_page


@dataclass(frozen=True)
class CorpusRunSummary:
    total_pages: int
    processed_pages: int
    missing_pages: int
    failed_pages: int
    region_count: int
    line_count: int
    grapheme_count: int
    unknown_graphemes: int
    metrics_status: str
    segmentation_complete: bool
    recognition_status: str
    translation_status: str


def run_corpus(
    pages: Iterable[PageRecord],
    output_root: str | Path,
    config: OpenSetConfig | None = None,
) -> CorpusRunSummary:
    page_rows = list(pages)
    if not page_rows:
        raise ValueError("Corpus authority manifest is empty")
    page_ids = [page.page_id for page in page_rows]
    missing_page_id_rows = tuple(
        index
        for index, page_id in enumerate(page_ids, start=1)
        if not isinstance(page_id, str) or not page_id.strip()
    )
    if missing_page_id_rows:
        raise ValueError(
            f"Corpus input contains missing page IDs at rows {missing_page_id_rows}"
        )
    if len(page_ids) != len(set(page_ids)):
        raise ValueError("Corpus input contains duplicate page IDs")
    iiif_ids = [page.iiif_id for page in page_rows]
    if len(iiif_ids) != len(set(iiif_ids)):
        raise ValueError("Corpus input contains duplicate IIIF IDs")
    root = Path(output_root)
    page_root = root / "pages"
    page_root.mkdir(parents=True, exist_ok=True)
    config = config or OpenSetConfig()

    processed = 0
    missing = 0
    failed = 0
    regions = 0
    lines = 0
    graphemes = 0
    unknowns = 0
    dispositions: list[dict] = []
    region_rows: list[dict] = []

    for page in page_rows:
        if not page.image_path or not Path(page.image_path).is_file():
            missing += 1
            dispositions.append({"page_id": page.page_id, "disposition": "missing_pixels"})
            continue
        try:
            result = process_page(page, config)
            write_json(page_root / f"{page.iiif_id}.json", result)
            processed += 1
            regions += len(result.regions)
            lines += len(result.lines)
            graphemes += len(result.graphemes)
            unknowns += sum(glyph.diplomatic_label is None for glyph in result.graphemes)
            dispositions.append({"page_id": page.page_id, "disposition": result.disposition})
            for region in result.regions:
                region_rows.append(
                    {
                        **asdict(region),
                        "page_id": page.page_id,
                        "image_sha256": result.page_sha256,
                        "ocr_record": f"pages/{page.iiif_id}.json",
                    }
                )
        except Exception as error:
            failed += 1
            dispositions.append(
                {
                    "page_id": page.page_id,
                    "disposition": "processing_failed",
                    "error_type": type(error).__name__,
                    "error": str(error),
                }
            )

    coverage = validate_corpus_coverage(
        page_rows,
        [row["page_id"] for row in dispositions],
    )
    if not coverage.ok:
        raise ValueError(
            "Corpus coverage mismatch: "
            f"missing_page_ids={coverage.missing_page_ids}; "
            f"unexpected_page_ids={coverage.unexpected_page_ids}; "
            f"duplicate_page_ids={coverage.duplicate_page_ids}"
        )

    summary = CorpusRunSummary(
        total_pages=len(page_rows),
        processed_pages=processed,
        missing_pages=missing,
        failed_pages=failed,
        region_count=regions,
        line_count=lines,
        grapheme_count=graphemes,
        unknown_graphemes=unknowns,
        metrics_status="not_measured",
        segmentation_complete=(
            bool(page_rows) and processed == len(page_rows) and missing == 0 and failed == 0
        ),
        recognition_status="unrecognized",
        translation_status="unresolved",
    )
    write_json(root / "corpus_summary.json", summary)
    write_jsonl(root / "page_dispositions.jsonl", dispositions)
    write_jsonl(root / "regions.jsonl", region_rows)
    return summary
