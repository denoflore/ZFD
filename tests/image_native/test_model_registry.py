"""Comparative OCR models remain pinned, hashed, and quarantined."""

from __future__ import annotations

from pathlib import Path

from zfd_image_native.io import read_json, write_json
from zfd_image_native.model_registry import validate_model_registry


ROOT = Path(__file__).resolve().parents[2]
REGISTER = ROOT / "data" / "image_native" / "model_register.json"


def test_committed_model_register_is_valid_without_ignored_cache() -> None:
    report = validate_model_registry(REGISTER)

    assert report.ok is True
    assert report.model_count == 2
    assert report.cached_file_count == 0


def test_model_register_rejects_primary_or_diplomatic_use(tmp_path: Path) -> None:
    payload = read_json(REGISTER)
    payload["models"][0]["primary_lane_allowed"] = True
    payload["models"][1]["diplomatic_label_allowed"] = True
    target = tmp_path / "models.json"
    write_json(target, payload)

    report = validate_model_registry(target)

    assert report.ok is False
    assert "MODEL_PRIMARY_LANE_NOT_BLOCKED:kraken-blla-zenodo-14602569" in report.errors
    assert "MODEL_DIPLOMATIC_LABEL_NOT_BLOCKED:rabus-crnn-ctc-glagolitic-16549a7f" in report.errors


def test_model_register_rejects_tampered_cached_file(tmp_path: Path) -> None:
    payload = read_json(REGISTER)
    model = payload["models"][0]
    model["files"] = [
        {
            "name": "fixture.mlmodel",
            "cache_relpath": "cache/fixture.mlmodel",
            "byte_length": 4,
            "sha256": "0" * 64,
        }
    ]
    target = tmp_path / "models.json"
    write_json(target, payload)
    cache = tmp_path / "cache"
    cache.mkdir()
    (cache / "fixture.mlmodel").write_bytes(b"safe")

    report = validate_model_registry(target, repository_root=tmp_path, require_cache=True)

    assert report.ok is False
    assert any(error.startswith("MODEL_CACHE_SHA256_MISMATCH:") for error in report.errors)
