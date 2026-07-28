"""Executable acceptance contract for the ZFD image native evidence lane."""

from __future__ import annotations

import ast
from io import BytesIO
import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.error import HTTPError

import pytest
from PIL import Image

from zfd_image_native import acquire as acquisition
from zfd_image_native.boundary import scan_primary_lane
from zfd_image_native.claims import validate_claims
from zfd_image_native.io import canonical_json, sha256_file
from zfd_image_native.manifest import (
    build_page_manifest,
    load_page_manifest,
    reconcile_local_assets,
    validate_corpus_coverage,
)
from zfd_image_native.metrics import GoldSequence, PredictedSequence, evaluate_predictions
from zfd_image_native.models import PageRecord, SourceRecord, SplitAsset, TerminologyRecord
from zfd_image_native.ocr import OpenSetConfig, process_page
from zfd_image_native.parity import validate_page_parity
from zfd_image_native.sources import validate_sources
from zfd_image_native.split import validate_split
from zfd_image_native.terminology import validate_terminology


ROOT = Path(__file__).resolve().parents[2]
OFFICIAL_MAP = ROOT / "06_Pipelines" / "glagolitic_ocr" / "data" / "folio_iiif_map.json"
LEGACY_IMAGES = ROOT / "folios" / "jpg"
COMMITTED_MANIFEST = ROOT / "data" / "image_native" / "voynich_pages.jsonl"


def _page_for_image(path: Path, *, digest: str | None = None) -> PageRecord:
    return PageRecord(
        page_id="yale-ms-408:iiif:1006076",
        source_id="yale-ms-408",
        surface_label="1r",
        iiif_id="1006076",
        iiif_base_uri="https://collections.library.yale.edu/iiif/2/1006076",
        image_request_uri="legacy-local-smoke-only",
        image_sha256=digest or sha256_file(path),
        image_path=str(path),
        width=None,
        height=None,
        mime_type="image/jpeg",
        acquisition_status="legacy_unverified",
    )


def _complete_parity_record() -> dict:
    image_hash = "a" * 64
    shared = {"page_id": "yale-ms-408:iiif:1006076", "image_sha256": image_hash}
    return {
        "page": {**shared, "source_id": "yale-ms-408"},
        "region": {**shared, "region_id": "region-1", "geometry": [10, 20, 30, 40]},
        "ocr": {**shared, "region_id": "region-1", "ocr_id": "ocr-1", "status": "frozen"},
        "diplomatic": {**shared, "region_id": "region-1", "ocr_id": "ocr-1", "text": "<?>"},
        "terminology": {
            **shared,
            "region_id": "region-1",
            "ocr_id": "ocr-1",
            "analysis_id": "term-1",
            "status": "unresolved",
        },
        "translation": {
            **shared,
            "region_id": "region-1",
            "ocr_id": "ocr-1",
            "analysis_id": "term-1",
            "modern_croatian": "nepoznato",
            "literal_english": "unknown",
            "fluent_english": "Unknown.",
            "reviewer_id": "reviewer-1",
            "adjudicator_id": "adjudicator-1",
            "review_state": "approved",
        },
    }


def test_primary_lane_has_no_inherited_transcription_dependency() -> None:
    hits = scan_primary_lane(
        ROOT / "zfd_image_native",
        {
            "eva",
            "ivtff",
            "zandbergen",
            "lsi_ivtff",
            "voynich-transcription",
            "zfd_decoder",
            "02_transcriptions",
            "raw_eva",
            "transcriptions",
            "translations",
            "lexicon.csv",
        },
        include={
            "__init__.py",
            "__main__.py",
            "acquire.py",
            "boundary.py",
            "cli.py",
            "corpus.py",
            "io.py",
            "manifest.py",
            "metrics.py",
            "models.py",
            "ocr.py",
            "receipts.py",
            "sources.py",
            "split.py",
        },
    )
    assert hits == []


def test_primary_lane_boundary_rejects_dynamic_import_evasion(tmp_path) -> None:
    module = tmp_path / "ocr.py"
    module.write_text(
        "import importlib\n"
        "__import__('zfd_' + 'decoder')\n"
        "importlib.import_module('legacy_' + 'transcriptions')\n",
        encoding="utf-8",
    )

    hits = scan_primary_lane(
        tmp_path,
        {"zfd_decoder", "transcriptions"},
        include={"ocr.py"},
    )

    assert any(hit.endswith(":DYNAMIC_IMPORT") for hit in hits)


def test_primary_lane_boundary_catches_receipts_import_leakage(tmp_path) -> None:
    module = tmp_path / "receipts.py"
    module.write_text("from zfd_decoder import inherited_receipt\n", encoding="utf-8")

    hits = scan_primary_lane(
        tmp_path,
        {"zfd_decoder"},
        include={"receipts.py"},
    )

    assert hits == ["receipts.py:1:zfd_decoder"]


def test_official_page_identity_has_210_unique_surfaces() -> None:
    pages = build_page_manifest(OFFICIAL_MAP)
    assert len(pages) == 210
    assert len({page.page_id for page in pages}) == 210
    assert len({page.iiif_base_uri for page in pages}) == 210
    assert pages[2].page_id == "yale-ms-408:iiif:1006076"


def test_committed_page_manifest_matches_authority() -> None:
    pages = load_page_manifest(COMMITTED_MANIFEST)
    assert len(pages) == 210
    assert {page.page_id for page in pages} == {
        page.page_id for page in build_page_manifest(OFFICIAL_MAP)
    }


def test_legacy_209_set_reports_identity_debt() -> None:
    report = reconcile_local_assets(build_page_manifest(OFFICIAL_MAP), LEGACY_IMAGES)
    assert report.authoritative_pages == 210
    assert report.local_assets == 209
    assert report.fully_verified is False
    assert report.unverified or report.missing


def test_training_source_requires_rights_identity_and_checksum() -> None:
    source = SourceRecord(
        source_id="unsafe",
        source_label="Unsafe fixture",
        title="Unsafe fixture",
        stable_locator="https://example.invalid/source",
        date_kind="writing",
        date_basis="fixture writing date",
        dating_authority="fixture authority",
        dating_authority_locator="https://example.invalid/authority",
        dating_certainty="exact",
        material_date_start=None,
        material_date_end=None,
        writing_date_start=1450,
        writing_date_end=1450,
        text_date_start=None,
        text_date_end=None,
        copy_date_start=None,
        copy_date_end=None,
        publication_date_start=None,
        publication_date_end=None,
        institution="Fixture archive",
        shelfmark="MS fixture",
        language="Croatian",
        script="Glagolitic",
        hand_style="office_cursive",
        genre="fixture",
        region="fixture region",
        source_type="manuscript",
        evidentiary_role="comparative",
        training_use="train",
        rights_statement="",
        rights_locator="",
        rights_status="unresolved",
        identity_status="unresolved",
        manifest_sha256=None,
        asset_mapping_sha256=None,
        page_mapping_sha256=None,
        lineage_sha256=None,
        control_group="croatian_glagolitic",
    )
    report = validate_sources([source])
    assert report.ok is False
    assert {error.code for error in report.errors} >= {
        "RIGHTS_MISSING",
        "IDENTITY_UNRESOLVED",
        "CHECKSUM_MISSING",
    }


def test_split_rejects_duplicate_lineage_and_hand_crossing() -> None:
    common = {
        "parent_asset_id": "parent-1",
        "lineage_root_id": "root-1",
        "sha256": "b" * 64,
        "perceptual_hash": "p1",
        "manuscript_id": "ms-1",
        "hand_id": "hand-1",
        "style": "office_cursive",
    }
    rows = [
        SplitAsset(asset_id="asset-train", split="train", **common),
        SplitAsset(asset_id="asset-test", split="test", **common),
    ]
    report = validate_split(rows)
    assert report.ok is False
    assert {error.code for error in report.errors} >= {
        "DUPLICATE_LEAKAGE",
        "LINEAGE_LEAKAGE",
        "HAND_LEAKAGE",
    }


def test_real_page_emits_open_set_geometry_and_unknowns() -> None:
    image = LEGACY_IMAGES / "VM_f1r.jpg"
    result = process_page(_page_for_image(image), OpenSetConfig(min_components_per_line=3))
    assert result.page_sha256 == sha256_file(image)
    assert result.regions
    assert result.lines
    assert result.graphemes
    assert all(line.region_id for line in result.lines)
    assert all(glyph.polygon for glyph in result.graphemes)
    assert all(0.0 <= glyph.unknown_score <= 1.0 for glyph in result.graphemes)
    assert all(glyph.diplomatic_label is None for glyph in result.graphemes)
    assert all(glyph.alternatives for glyph in result.graphemes)


def test_same_pixels_and_config_are_deterministic() -> None:
    image = LEGACY_IMAGES / "VM_f1r.jpg"
    page = _page_for_image(image)
    config = OpenSetConfig(min_components_per_line=3)
    assert canonical_json(process_page(page, config)) == canonical_json(process_page(page, config))


def test_changed_source_hash_is_rejected_before_ocr() -> None:
    image = LEGACY_IMAGES / "VM_f1r.jpg"
    with pytest.raises(ValueError, match="checksum"):
        process_page(_page_for_image(image, digest="0" * 64), OpenSetConfig())


def test_metrics_refuse_accuracy_without_adjudicated_gold() -> None:
    metrics = evaluate_predictions([], [])
    assert metrics.status == "not_measured"
    assert metrics.cer is None
    assert metrics.accuracy_claim_allowed is False


def test_metric_arithmetic_unknown_rejection_and_calibration() -> None:
    gold = [
        GoldSequence(
            record_id="line-1",
            labels=("a", None, "c", None),
            manuscript_id="gold-ms",
            hand_id="gold-hand",
            style="office_cursive",
            adjudicated=True,
        )
    ]
    predictions = [
        PredictedSequence(
            record_id="line-1",
            labels=("a", None, "x", "q"),
            confidences=(0.9, 0.8, 0.6, 0.7),
            unknown_scores=(0.1, 0.9, 0.2, 0.4),
        )
    ]
    metrics = evaluate_predictions(gold, predictions, calibration_bins=1, unknown_threshold=0.5)
    assert metrics.status == "measured"
    assert metrics.character_edits == 2
    assert metrics.reference_characters == 4
    assert metrics.cer == pytest.approx(0.5)
    assert metrics.sequence_error == pytest.approx(1.0)
    assert metrics.unknown_true_positive == 1
    assert metrics.unknown_false_negative == 1
    assert metrics.ece == pytest.approx(0.25)
    assert metrics.by_hand["gold-hand"]["cer"] == pytest.approx(0.5)


def test_confirmed_translation_requires_every_layer_and_adjudication() -> None:
    record = _complete_parity_record()
    record["translation"]["fluent_english"] = None
    record["translation"]["adjudicator_id"] = None
    report = validate_page_parity(record)
    assert report.confirmed_translated == 0
    assert report.unresolved == 1
    assert {"FLUENT_ENGLISH_MISSING", "ADJUDICATION_MISSING"} <= set(report.reasons)


def test_filename_similarity_cannot_override_parent_hash() -> None:
    record = _complete_parity_record()
    record["translation"]["image_sha256"] = "f" * 64
    report = validate_page_parity(record)
    assert report.ok is False
    assert "PARENT_IDENTITY_MISMATCH" in report.reasons


def test_corpus_coverage_accounts_for_every_manifest_page() -> None:
    pages = build_page_manifest(OFFICIAL_MAP)
    report = validate_corpus_coverage(pages, [page.page_id for page in pages[:-1]])
    assert report.total_pages == 210
    assert report.missing_pages == 1
    assert report.ok is False


def test_current_completion_claims_are_blocked_without_receipts() -> None:
    ledger = {
        "complete_translation": {"required_receipts": ["page_translation_parity"]},
        "ragusan_provenance": {"required_receipts": ["provenance_comparative_controls"]},
        "ocr_accuracy": {"required_receipts": ["held_out_gold_metrics"]},
    }
    report = validate_claims(ledger, receipts={})
    assert report.claim("complete_translation").allowed is False
    assert report.claim("ragusan_provenance").allowed is False
    assert report.claim("ocr_accuracy").allowed is False


def test_terminology_requires_dated_locator_and_separate_forms() -> None:
    term = TerminologyRecord(
        term_id="term-1",
        ocr_id="ocr-1",
        observed_form="ulje",
        expanded_form=None,
        normalized_historical_form=None,
        reconstructed_form="ulje",
        latin_parallel=None,
        modern_croatian=None,
        literal_english=None,
        fluent_english=None,
        source_id="source-1",
        witness_date_kind=None,
        witness_date_start=None,
        witness_date_end=None,
        witness_language=None,
        witness_script=None,
        witness_domain=None,
        passage_locator=None,
        stable_locator=None,
        source_sha256=None,
        passage_asset_id=None,
        passage_asset_sha256=None,
        passage_image_id=None,
        passage_image_sha256=None,
        diplomatic_passage=None,
        reviewer_id=None,
        adjudicator_id=None,
        review_state="unreviewed",
        alternatives=(),
        confidence=None,
        confidence_basis=None,
        speculation=True,
    )
    report = validate_terminology(term)
    assert report.ok is False
    assert {"WITNESS_DATE_MISSING", "PASSAGE_LOCATOR_MISSING"} <= set(report.codes)


def test_decoder_production_open_calls_declare_utf8() -> None:
    paths = [
        ROOT / "zfd_decoder" / "src" / "compound.py",
        ROOT / "zfd_decoder" / "src" / "operators.py",
        ROOT / "zfd_decoder" / "src" / "gallows.py",
        ROOT / "zfd_decoder" / "src" / "suffixes.py",
        ROOT / "zfd_decoder" / "src" / "stems.py",
        ROOT / "zfd_decoder" / "batch_decode.py",
    ]
    missing: list[str] = []
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "open":
                if not any(keyword.arg == "encoding" for keyword in node.keywords):
                    missing.append(f"{path.relative_to(ROOT)}:{node.lineno}")
    assert missing == []


def test_mapper_failure_is_ascii_safe_and_nonzero() -> None:
    environment = os.environ.copy()
    environment["ZFD_MAPPER_FORCE_PATTERN_FAILURE"] = "1"
    completed = subprocess.run(
        [sys.executable, "scripts/test_mapper.py"],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert completed.returncode != 0
    assert "[FAIL]" in completed.stdout


def test_acquisition_falls_back_to_source_maximum(monkeypatch, tmp_path: Path) -> None:
    payload = BytesIO()
    Image.new("RGB", (7, 11), "white").save(payload, format="JPEG")
    image_bytes = payload.getvalue()
    calls: list[str] = []

    class Headers:
        @staticmethod
        def get_content_type() -> str:
            return "image/jpeg"

    class Response:
        headers = Headers()

        def __init__(self, uri: str) -> None:
            self.uri = uri

        def __enter__(self):
            return self

        def __exit__(self, *_args) -> None:
            return None

        def read(self) -> bytes:
            return image_bytes

        def geturl(self) -> str:
            return self.uri

    def fake_urlopen(request, timeout):
        calls.append(request.full_url)
        if len(calls) == 1:
            raise HTTPError(request.full_url, 403, "upscale rejected", None, None)
        return Response(request.full_url)

    monkeypatch.setattr(acquisition, "urlopen", fake_urlopen)
    page = build_page_manifest(OFFICIAL_MAP)[0]
    result = acquisition.acquire_pages([page], tmp_path, width=2000)
    assert result.failed == 0
    assert calls[0].endswith("/full/2000,/0/default.jpg")
    assert calls[1].endswith("/full/max/0/default.jpg")
    assert result.receipts[0].request_uri == calls[1]
    assert result.pages[0].width == 7
    assert result.pages[0].height == 11


def test_acquisition_records_failure_without_aborting(monkeypatch, tmp_path: Path) -> None:
    def fail(request, timeout):
        raise HTTPError(request.full_url, 500, "source failure", None, None)

    monkeypatch.setattr(acquisition, "urlopen", fail)
    pages = build_page_manifest(OFFICIAL_MAP)[:2]
    result = acquisition.acquire_pages(pages, tmp_path, width=2000)
    assert result.failed == 2
    assert len(result.receipts) == 2
    assert all(item.disposition == "acquisition_failed" for item in result.receipts)
    assert all(page.acquisition_status == "acquisition_failed" for page in result.pages)


def test_public_readme_carries_current_evidence_status() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    first_section = "\n".join(readme.splitlines()[:100]).lower()
    assert "evidence status" in first_section
    assert "ocr accuracy is not measured" in first_section
    assert "translation remains unresolved" in first_section
    assert "the voynich manuscript is a ragusan pharmaceutical recipe book." not in readme.lower()
    assert "translation verified across 201 folios" not in readme.lower()
