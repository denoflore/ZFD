"""Receipts for the image native corpus must stay portable and claim safe."""

from __future__ import annotations

from dataclasses import asdict, replace
from hashlib import sha256
from pathlib import Path

from PIL import Image
import pytest

from zfd_image_native import receipts as receipts_module
from zfd_image_native.corpus import run_corpus
from zfd_image_native.io import canonical_json, read_json, read_jsonl, sha256_file, write_json, write_jsonl
from zfd_image_native.manifest import load_page_manifest
from zfd_image_native.models import PageRecord
from zfd_image_native.ocr import OpenSetConfig
from zfd_image_native.receipts import freeze_stage_a_receipts, validate_stage_a_receipts


def _page(tmp_path: Path) -> PageRecord:
    image_path = tmp_path / "build" / "image_native" / "sources" / "yale-ms-408" / "1.jpg"
    image_path.parent.mkdir(parents=True)
    Image.new("RGB", (80, 60), "white").save(image_path, format="JPEG")
    return PageRecord(
        page_id="yale-ms-408:iiif:1",
        source_id="yale-ms-408",
        surface_label="fixture",
        iiif_id="1",
        iiif_base_uri="https://example.invalid/iiif/2/1",
        image_request_uri="https://example.invalid/iiif/2/1/full/max/0/default.jpg",
        image_sha256=sha256_file(image_path),
        image_path=str(image_path),
        width=80,
        height=60,
        mime_type="image/jpeg",
        acquisition_status="verified",
    )


def _write_stage_a_fixture(tmp_path: Path) -> tuple[Path, Path]:
    page = _page(tmp_path)
    manifest = tmp_path / "build" / "image_native" / "voynich_pages.acquired.jsonl"
    write_jsonl(manifest, [page])
    corpus_root = tmp_path / "build" / "image_native" / "corpus"
    page_path = corpus_root / "pages" / "1.json"
    region_id = f"{page.page_id}:region:0001"
    line_id = f"{page.page_id}:line:0001"
    grapheme_id = f"{page.page_id}:grapheme:000001"
    region = {
        "region_id": region_id,
        "bbox": [10, 10, 30, 20],
        "polygon": [[10, 10], [40, 10], [40, 30], [10, 30]],
        "line_ids": [line_id],
    }
    result = {
        "page_id": page.page_id,
        "source_id": page.source_id,
        "page_sha256": page.image_sha256,
        "width": page.width,
        "height": page.height,
        "config_sha256": sha256(
            canonical_json(asdict(OpenSetConfig())).encode("utf-8")
        ).hexdigest(),
        "disposition": "segmented_unrecognized_layout_review",
        "regions": [region],
        "lines": [
            {
                "line_id": line_id,
                "region_id": region_id,
                "bbox": [10, 10, 30, 20],
                "polygon": [[10, 10], [40, 10], [40, 30], [10, 30]],
                "grapheme_ids": [grapheme_id],
                "geometry_mode": "cartesian_fragment",
                "maximum_gap_heights": 0.5,
                "ink_density": 0.25,
            }
        ],
        "rejected_components": [
            {
                "component_id": f"{page.page_id}:component-rejection:000001",
                "bbox": [50, 10, 5, 5],
                "polygon": [[50, 10], [55, 10], [55, 15], [50, 15]],
                "reason": "unassigned_after_cartesian_continuity_and_density_gates",
            }
        ],
        "layout_disposition": "layout_review_required",
        "graphemes": [
            {
                "grapheme_id": grapheme_id,
                "line_id": line_id,
                "region_id": region_id,
                "bbox": [10, 10, 5, 10],
                "polygon": [[10, 10], [15, 10], [15, 20], [10, 20]],
                "visual_fingerprint": "f" * 64,
                "alternatives": [
                    {"candidate_id": "visual:fixture", "score": 0.0, "candidate_type": "visual_cluster"}
                ],
                "unknown_score": 1.0,
                "recognition_confidence": 0.0,
                "diplomatic_label": None,
            }
        ],
    }
    write_json(page_path, result)
    write_jsonl(
        corpus_root / "regions.jsonl",
        [
            {
                **region,
                "page_id": page.page_id,
                "image_sha256": page.image_sha256,
                "ocr_record": "pages/1.json",
            }
        ],
    )
    write_jsonl(
        corpus_root / "page_dispositions.jsonl",
        [
            {
                "page_id": page.page_id,
                "disposition": "segmented_unrecognized_layout_review",
            }
        ],
    )
    return manifest, corpus_root


def _assert_self_hashing_receipt(row: dict) -> None:
    payload = {key: value for key, value in row.items() if key != "receipt_sha256"}
    expected = sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    assert row["receipt_sha256"] == expected


def test_corpus_summary_names_only_the_completed_stage(tmp_path: Path) -> None:
    page = _page(tmp_path)
    summary = run_corpus([page], tmp_path / "corpus")
    payload = asdict(summary)
    assert "complete" not in payload
    assert payload["segmentation_complete"] is True
    assert payload["recognition_status"] == "unrecognized"
    assert payload["translation_status"] == "unresolved"


def test_freeze_stage_a_writes_portable_exact_unresolved_joins(tmp_path: Path) -> None:
    manifest, corpus_root = _write_stage_a_fixture(tmp_path)
    output = tmp_path / "data" / "image_native"

    summary = freeze_stage_a_receipts(manifest, corpus_root, output, repository_root=tmp_path)

    assert summary.total_pages == 1
    assert summary.frozen_pages == 1
    assert summary.total_regions == 1
    assert summary.segmentation_complete is True
    assert summary.recognition_status == "unrecognized"
    assert summary.translation_status == "unresolved"
    assert summary.confirmed_translated_pages == 0
    assert summary.confirmed_translated_regions == 0
    assert summary.total_rejected_components == 1
    assert summary.total_component_candidates == 2

    page = read_jsonl(output / "voynich_pages.jsonl")[0]
    run_receipt = read_json(output / "ocr_run_receipt.json")
    receipt = read_jsonl(output / "ocr_page_receipts.jsonl")[0]
    region = read_jsonl(output / "voynich_regions.jsonl")[0]
    page_parity = read_jsonl(output / "page_parity.jsonl")[0]
    region_parity = read_jsonl(output / "region_parity.jsonl")[0]
    frozen_summary = read_json(output / "corpus_stage_a_summary.json")

    _assert_self_hashing_receipt(run_receipt)
    _assert_self_hashing_receipt(receipt)
    _assert_self_hashing_receipt(region)
    _assert_self_hashing_receipt(page_parity)
    _assert_self_hashing_receipt(region_parity)
    assert run_receipt["run_id"].startswith("sha256:")
    assert receipt["run_id"] == run_receipt["run_id"]
    assert receipt["run_receipt_sha256"] == run_receipt["receipt_sha256"]
    assert receipt["record_state"] == "frozen"
    assert receipt["disposition"] == "segmented_unrecognized_layout_review"
    assert receipt["layout_disposition"] == "layout_review_required"
    assert receipt["rejected_component_count"] == 1
    assert "rejected_components" not in receipt
    source_ocr = read_json(corpus_root / "pages" / "1.json")
    assert receipt["rejected_component_evidence_sha256"] == sha256(
        canonical_json(source_ocr["rejected_components"]).encode("utf-8")
    ).hexdigest()
    assert receipt["grapheme_evidence_sha256"] == sha256(
        canonical_json(source_ocr["graphemes"]).encode("utf-8")
    ).hexdigest()
    assert receipt["component_candidate_count"] == 2
    assert receipt["ocr_artifact_path"] == "pages/1.json"
    assert receipt["ocr_artifact_sha256"] == receipt["ocr_sha256"]
    assert receipt["line_geometry_mode_counts"] == {"cartesian_fragment": 1}
    assert receipt["segmentation_version"] == OpenSetConfig().segmentation_version
    assert run_receipt["segmentation_version"] == receipt["segmentation_version"]
    assert receipt["region_set_sha256"]
    assert page["image_path"] == "build/image_native/sources/yale-ms-408/1.jpg"
    assert receipt["ocr_record"] == "build/image_native/corpus/pages/1.json"
    assert receipt["ocr_sha256"] == region["ocr_sha256"]
    assert receipt["image_sha256"] == region["image_sha256"] == page["image_sha256"]
    assert region["region_id"].startswith("sha256:")
    assert region["source_region_id"] == "yale-ms-408:iiif:1:region:0001"
    assert region["page_ocr_receipt_sha256"] == receipt["receipt_sha256"]
    assert region["region_state"] == "candidate_unreviewed"
    assert region["review_state"] == "unreviewed"
    assert region["segmentation_version"] == receipt["segmentation_version"]
    assert region["detection_method"] == "adaptive_threshold_connected_components"
    assert region["line_geometry"] == [
        {
            "line_id": "yale-ms-408:iiif:1:line:0001",
            "geometry_mode": "cartesian_fragment",
        }
    ]
    assert page_parity["confirmed_translated"] is False
    assert page_parity["unresolved_regions"] == 1
    assert region_parity["confirmed_translated"] is False
    assert region_parity["layers"]["diplomatic"]["state"] == "unresolved"
    assert "DIPLOMATIC_RECORD_MISSING" in region_parity["reason_codes"]
    assert frozen_summary["metrics_status"] == "not_measured"
    assert frozen_summary["run_id"] == run_receipt["run_id"]
    assert str(tmp_path) not in (output / "voynich_pages.jsonl").read_text(encoding="utf-8")


def test_freeze_stage_a_rejects_region_aggregate_identity_mismatch(tmp_path: Path) -> None:
    manifest, corpus_root = _write_stage_a_fixture(tmp_path)
    rows = read_jsonl(corpus_root / "regions.jsonl")
    rows[0]["image_sha256"] = "0" * 64
    write_jsonl(corpus_root / "regions.jsonl", rows)

    with pytest.raises(ValueError, match="Region aggregate"):
        freeze_stage_a_receipts(
            manifest,
            corpus_root,
            tmp_path / "data" / "image_native",
            repository_root=tmp_path,
        )


def test_frozen_receipt_tampering_is_detected(tmp_path: Path) -> None:
    manifest, corpus_root = _write_stage_a_fixture(tmp_path)
    output = tmp_path / "data" / "image_native"
    freeze_stage_a_receipts(manifest, corpus_root, output, repository_root=tmp_path)
    rows = read_jsonl(output / "voynich_regions.jsonl")
    rows[0]["review_state"] = "adjudicated"
    write_jsonl(output / "voynich_regions.jsonl", rows)

    report = validate_stage_a_receipts(output)

    assert report.ok is False
    assert any("REGION_RECEIPT_HASH_MISMATCH" in error for error in report.errors)


def test_validation_separates_archival_integrity_from_current_freshness(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest, corpus_root = _write_stage_a_fixture(tmp_path)
    output = tmp_path / "data" / "image_native"
    freeze_stage_a_receipts(manifest, corpus_root, output, repository_root=tmp_path)

    fresh = validate_stage_a_receipts(
        output,
        repository_root=tmp_path,
        manifest_path=manifest,
        config=OpenSetConfig(),
    )
    assert fresh.ok is True
    assert fresh.archival_integrity_ok is True
    assert fresh.artifact_integrity_ok is True
    assert fresh.freshness_ok is True
    assert fresh.archival_errors == ()
    assert fresh.artifact_errors == ()
    assert fresh.freshness_errors == ()

    monkeypatch.setattr(receipts_module, "_implementation_sha256", lambda: "0" * 64)
    stale = validate_stage_a_receipts(
        output,
        repository_root=tmp_path,
        manifest_path=manifest,
        config=OpenSetConfig(),
    )
    assert stale.ok is False
    assert stale.archival_integrity_ok is True
    assert stale.artifact_integrity_ok is True
    assert stale.freshness_ok is False
    assert "CURRENT_IMPLEMENTATION_MISMATCH" in stale.freshness_errors


def test_each_current_identity_axis_fails_freshness_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest, corpus_root = _write_stage_a_fixture(tmp_path)
    output = tmp_path / "data" / "image_native"
    freeze_stage_a_receipts(manifest, corpus_root, output, repository_root=tmp_path)

    config_stale = validate_stage_a_receipts(
        output,
        repository_root=tmp_path,
        manifest_path=manifest,
        config=OpenSetConfig(adaptive_c=9),
    )
    assert config_stale.archival_integrity_ok is True
    assert config_stale.freshness_ok is False
    assert "CURRENT_CONFIG_MISMATCH" in config_stale.freshness_errors

    original_dependency_identity = receipts_module._dependency_identity
    current_dependencies = original_dependency_identity()
    monkeypatch.setattr(
        receipts_module,
        "_dependency_identity",
        lambda: {**current_dependencies, "numpy": "0.0.0-test"},
    )
    dependency_stale = validate_stage_a_receipts(
        output,
        repository_root=tmp_path,
        manifest_path=manifest,
        config=OpenSetConfig(),
    )
    assert dependency_stale.archival_integrity_ok is True
    assert dependency_stale.freshness_ok is False
    assert "CURRENT_DEPENDENCY_SET_MISMATCH" in dependency_stale.freshness_errors
    monkeypatch.setattr(receipts_module, "_dependency_identity", original_dependency_identity)

    manifest_rows = read_jsonl(manifest)
    manifest_rows[0]["surface_label"] = "changed current authority"
    write_jsonl(manifest, manifest_rows)
    authority_stale = validate_stage_a_receipts(
        output,
        repository_root=tmp_path,
        manifest_path=manifest,
        config=OpenSetConfig(),
    )
    assert authority_stale.archival_integrity_ok is True
    assert authority_stale.freshness_ok is False
    assert "CURRENT_MANIFEST_MISMATCH" in authority_stale.freshness_errors


def test_validation_without_current_context_fails_freshness_closed(tmp_path: Path) -> None:
    manifest, corpus_root = _write_stage_a_fixture(tmp_path)
    output = tmp_path / "data" / "image_native"
    freeze_stage_a_receipts(manifest, corpus_root, output, repository_root=tmp_path)

    report = validate_stage_a_receipts(output)

    assert report.ok is False
    assert report.archival_integrity_ok is True
    assert report.artifact_integrity_ok is False
    assert "OCR_ARTIFACT_CONTEXT_MISSING" in report.artifact_errors
    assert report.freshness_ok is False
    assert "CURRENT_CONTEXT_MISSING" in report.freshness_errors


def test_explicit_corpus_root_validates_portable_ocr_artifacts_without_current_checkout(
    tmp_path: Path,
) -> None:
    manifest, corpus_root = _write_stage_a_fixture(tmp_path)
    output = tmp_path / "data" / "image_native"
    freeze_stage_a_receipts(manifest, corpus_root, output, repository_root=tmp_path)

    report = validate_stage_a_receipts(output, corpus_root=corpus_root)

    assert report.archival_integrity_ok is True
    assert report.artifact_integrity_ok is True
    assert report.artifact_errors == ()
    assert report.freshness_ok is False
    assert report.ok is False


def test_tampered_page_ocr_artifact_breaks_artifact_integrity_only(tmp_path: Path) -> None:
    manifest, corpus_root = _write_stage_a_fixture(tmp_path)
    output = tmp_path / "data" / "image_native"
    freeze_stage_a_receipts(manifest, corpus_root, output, repository_root=tmp_path)
    ocr_path = corpus_root / "pages" / "1.json"
    payload = read_json(ocr_path)
    payload["rejected_components"][0]["reason"] = "tampered"
    write_json(ocr_path, payload)

    report = validate_stage_a_receipts(
        output,
        corpus_root=corpus_root,
        repository_root=tmp_path,
        manifest_path=manifest,
        config=OpenSetConfig(),
    )

    assert report.archival_integrity_ok is True
    assert report.artifact_integrity_ok is False
    assert "OCR_ARTIFACT_SHA256_MISMATCH:yale-ms-408:iiif:1" in report.artifact_errors
    assert report.freshness_ok is True
    assert report.ok is False


def test_freshness_rehashes_current_pixels_and_checks_registered_dimensions(
    tmp_path: Path,
) -> None:
    manifest, corpus_root = _write_stage_a_fixture(tmp_path)
    output = tmp_path / "data" / "image_native"
    freeze_stage_a_receipts(manifest, corpus_root, output, repository_root=tmp_path)
    page = load_page_manifest(manifest)[0]
    assert page.image_path is not None
    Image.new("RGB", (40, 30), "black").save(page.image_path, format="JPEG")

    report = validate_stage_a_receipts(
        output,
        repository_root=tmp_path,
        manifest_path=manifest,
        config=OpenSetConfig(),
    )

    assert report.archival_integrity_ok is True
    assert report.freshness_ok is False
    assert f"CURRENT_PAGE_PIXELS_SHA256_MISMATCH:{page.page_id}" in report.freshness_errors
    assert f"CURRENT_PAGE_IMAGE_WIDTH_MISMATCH:{page.page_id}" in report.freshness_errors
    assert f"CURRENT_PAGE_IMAGE_HEIGHT_MISMATCH:{page.page_id}" in report.freshness_errors


def test_current_source_freshness_rehashes_every_manifest_image(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = _page(tmp_path)
    second_path = tmp_path / "build" / "image_native" / "sources" / "yale-ms-408" / "2.jpg"
    Image.new("RGB", (80, 60), "white").save(second_path, format="JPEG")
    second = replace(
        first,
        page_id="yale-ms-408:iiif:2",
        iiif_id="2",
        iiif_base_uri="https://example.invalid/iiif/2/2",
        image_request_uri="https://example.invalid/iiif/2/2/full/max/0/default.jpg",
        image_sha256=sha256_file(second_path),
        image_path=str(second_path),
    )
    pages = [first, second]
    frozen = {
        page.page_id: {
            **asdict(page),
            "image_path": Path(page.image_path).resolve().relative_to(tmp_path).as_posix(),
        }
        for page in pages
    }
    frozen[first.page_id]["image_sha256"] = first.image_sha256.upper()
    original_sha256_file = receipts_module.sha256_file
    hashed_paths: list[Path] = []

    def recording_sha256_file(path: str | Path) -> str:
        hashed_paths.append(Path(path).resolve())
        return original_sha256_file(path)

    monkeypatch.setattr(receipts_module, "sha256_file", recording_sha256_file)

    errors = receipts_module._current_source_freshness_errors(pages, frozen, tmp_path)

    assert errors == []
    assert {Path(page.image_path).resolve() for page in pages} <= set(hashed_paths)


def test_freeze_preserves_no_text_layout_review_evidence(tmp_path: Path) -> None:
    manifest, corpus_root = _write_stage_a_fixture(tmp_path)
    page_path = corpus_root / "pages" / "1.json"
    page = read_json(page_path)
    page["disposition"] = "no_text_detected_layout_review"
    page["regions"] = []
    page["lines"] = []
    page["graphemes"] = []
    write_json(page_path, page)
    write_jsonl(corpus_root / "regions.jsonl", [])
    write_jsonl(
        corpus_root / "page_dispositions.jsonl",
        [
            {
                "page_id": page["page_id"],
                "disposition": "no_text_detected_layout_review",
            }
        ],
    )
    output = tmp_path / "data" / "image_native"

    freeze_stage_a_receipts(manifest, corpus_root, output, repository_root=tmp_path)

    receipt = read_jsonl(output / "ocr_page_receipts.jsonl")[0]
    assert receipt["disposition"] == "no_text_detected_layout_review"
    assert receipt["layout_disposition"] == "layout_review_required"
    assert receipt["rejected_component_count"] == 1
    assert "rejected_components" not in receipt
    assert receipt["line_geometry_mode_counts"] == {}
