"""Comparative manuscript assets require checksums, lineage, and exclusions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from zfd_image_native.comparative import register_comparative_assets, validate_comparative_assets
from zfd_image_native.io import read_json, read_jsonl, sha256_file, write_json, write_jsonl


ROOT = Path(__file__).resolve().parents[2]


def _source_row(
    source_id: str,
    manifest_hash: str,
    *,
    rights_status: str = "public_domain",
    training_use: str = "quarantined",
    hand_boundary_sha256: str | None = None,
    line_annotation_sha256: str | None = None,
    split_lineage_sha256: str | None = None,
) -> dict[str, Any]:
    training_capable = training_use == "train"
    return {
        "source_id": source_id,
        "source_label": source_id,
        "title": source_id,
        "stable_locator": f"https://example.invalid/{source_id}",
        "date_kind": "writing",
        "date_basis": "dated scribal colophon",
        "dating_authority": "Example archive catalogue",
        "dating_authority_locator": f"https://example.invalid/{source_id}/catalogue",
        "dating_certainty": "exact",
        "material_date_start": None,
        "material_date_end": None,
        "writing_date_start": 1450,
        "writing_date_end": 1450,
        "text_date_start": None,
        "text_date_end": None,
        "copy_date_start": None,
        "copy_date_end": None,
        "publication_date_start": None,
        "publication_date_end": None,
        "institution": "Example archive",
        "shelfmark": source_id,
        "language": "Croatian",
        "script": "Croatian Glagolitic",
        "hand_style": "book_cursive",
        "genre": "miscellany",
        "region": "Croatia",
        "source_type": "manuscript",
        "evidentiary_role": "dated_comparative",
        "training_use": training_use,
        "rights_statement": "Registered fixture rights.",
        "rights_locator": f"https://example.invalid/{source_id}/rights",
        "rights_status": rights_status,
        "identity_status": "resolved",
        "manifest_sha256": manifest_hash,
        "asset_mapping_sha256": "a" * 64 if training_capable else None,
        "page_mapping_sha256": "b" * 64 if training_capable else None,
        "lineage_sha256": "c" * 64 if training_capable else None,
        "control_group": "fixture",
        "hand_boundary_sha256": hand_boundary_sha256,
        "line_annotation_sha256": line_annotation_sha256,
        "split_lineage_sha256": split_lineage_sha256,
    }


def _write_source_register(tmp_path: Path, sources: list[dict[str, Any]]) -> Path:
    register = tmp_path / "source_register.json"
    write_json(register, {"schema_version": "2.0.0", "sources": sources})
    return register


def _config(tmp_path: Path, manifest_hash: str) -> Path:
    config = tmp_path / "comparative.json"
    write_json(
        config,
        {
            "schema_version": "1.0.0",
            "sources": [
                {
                    "source_id": "source-a",
                    "local_subpath": "a",
                    "asset_glob": "img/*.jpg",
                    "expected_asset_count": 1,
                    "manifest_relpath": "meta/manifest.json",
                    "manifest_sha256": manifest_hash,
                    "manifest_uri": "https://example.invalid/a/manifest",
                    "rights_status": "public_domain",
                    "source_identity_status": "resolved",
                    "local_asset_identity_status": "unresolved_canvas_mapping",
                    "training_disposition": "quarantine_pending_canvas_mapping",
                },
                {
                    "source_id": "source-b",
                    "local_subpath": "b",
                    "asset_glob": "img/*.jpg",
                    "expected_asset_count": 1,
                    "manifest_relpath": "meta/manifest.json",
                    "manifest_sha256": manifest_hash,
                    "manifest_uri": "https://example.invalid/b/manifest",
                    "rights_status": "contract_restricted",
                    "source_identity_status": "resolved",
                    "local_asset_identity_status": "misidentified_source_a",
                    "training_disposition": "excluded_misidentified",
                },
            ],
        },
    )
    return config


def _fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    manifest_payload = {"sequences": [{"canvases": []}]}
    for name in ("a", "b"):
        root = tmp_path / name
        (root / "img").mkdir(parents=True)
        (root / "meta").mkdir()
        (root / "img" / f"{name}.jpg").write_bytes(b"same-image-bytes")
        write_json(root / "meta" / "manifest.json", manifest_payload)
    manifest_hash = sha256_file(tmp_path / "a" / "meta" / "manifest.json")
    register = _write_source_register(
        tmp_path,
        [
            _source_row("source-a", manifest_hash),
            _source_row(
                "source-b",
                manifest_hash,
                rights_status="contract_restricted",
                training_use="excluded",
            ),
        ],
    )
    return _config(tmp_path, manifest_hash), tmp_path, register


def test_comparative_register_tracks_cross_source_duplicates_and_quarantine(tmp_path: Path) -> None:
    config, source_root, register = _fixture(tmp_path)
    output = tmp_path / "out"

    summary = register_comparative_assets(config, source_root, output)

    assets = read_jsonl(output / "comparative_assets.jsonl")
    duplicate_groups = read_jsonl(output / "comparative_duplicate_groups.jsonl")
    saved_summary = read_json(output / "comparative_asset_summary.json")
    assert summary.asset_count == 2
    assert len(assets) == 2
    assert assets[0]["sha256"] == assets[1]["sha256"]
    assert assets[0]["duplicate_group"] == assets[1]["duplicate_group"]
    assert all(row["canvas_id"] is None for row in assets)
    assert all("quarantine" in row["training_disposition"] or "excluded" in row["training_disposition"] for row in assets)
    assert duplicate_groups[0]["cross_source"] is True
    assert duplicate_groups[0]["source_ids"] == ["source-a", "source-b"]
    assert saved_summary["cross_source_duplicate_groups"] == 1
    assert str(tmp_path) not in (output / "comparative_assets.jsonl").read_text(encoding="utf-8")
    assert validate_comparative_assets(output, register).ok is True


def test_comparative_register_rejects_manifest_checksum_mismatch(tmp_path: Path) -> None:
    config, source_root, _register = _fixture(tmp_path)
    payload = read_json(config)
    payload["sources"][0]["manifest_sha256"] = "0" * 64
    write_json(config, payload)

    with pytest.raises(ValueError, match="manifest checksum"):
        register_comparative_assets(config, source_root, tmp_path / "out")


def test_comparative_register_tampering_fails_validation(tmp_path: Path) -> None:
    config, source_root, register = _fixture(tmp_path)
    output = tmp_path / "out"
    register_comparative_assets(config, source_root, output)
    assets = read_jsonl(output / "comparative_assets.jsonl")
    assets[0]["training_disposition"] = "train"
    write_jsonl(output / "comparative_assets.jsonl", assets)

    report = validate_comparative_assets(output, register)

    assert report.ok is False
    assert any("ASSET_RECEIPT_HASH_MISMATCH" in error for error in report.errors)


def test_comparative_register_accepts_explicit_canvas_mapping(tmp_path: Path) -> None:
    root = tmp_path / "source"
    (root / "img").mkdir(parents=True)
    (root / "meta").mkdir()
    (root / "img" / "p0017_0001r.jpg").write_bytes(b"mapped-image")
    write_json(root / "meta" / "manifest.json", {"sequences": [{"canvases": []}]})
    write_json(
        root / "meta" / "canvas_mapping.json",
        [
            {
                "local_name": "p0017_0001r.jpg",
                "source_label": "1r",
                "request_uri": "https://example.invalid/image/full/2000,/0/default.jpg",
                "canvas_id": "https://example.invalid/canvas/p0017",
                "canvas_label": "1r",
                "image_service_id": "https://example.invalid/image",
            }
        ],
    )
    manifest_hash = sha256_file(root / "meta" / "manifest.json")
    config = tmp_path / "comparative.json"
    write_json(
        config,
        {
            "schema_version": "1.0.0",
            "sources": [
                {
                    "source_id": "mapped-source",
                    "local_subpath": "source",
                    "asset_glob": "img/*.jpg",
                    "expected_asset_count": 1,
                    "manifest_relpath": "meta/manifest.json",
                    "manifest_sha256": manifest_hash,
                    "manifest_uri": "https://example.invalid/manifest",
                    "rights_status": "study_only",
                    "source_identity_status": "resolved",
                    "local_asset_identity_status": "resolved_canvas_mapping",
                    "training_disposition": "quarantine_study_only",
                    "mapping": {
                        "direct_relpath": "meta/canvas_mapping.json",
                        "local_name_field": "local_name",
                    },
                }
            ],
        },
    )

    output = tmp_path / "out"
    summary = register_comparative_assets(config, tmp_path, output)
    assets = read_jsonl(output / "comparative_assets.jsonl")

    assert summary.mapped_canvas_count == 1
    assert assets[0]["canvas_id"] == "https://example.invalid/canvas/p0017"
    assert assets[0]["source_label"] == "1r"
    assert assets[0]["training_disposition"] == "quarantine_study_only"
    register = _write_source_register(
        tmp_path,
        [
            _source_row(
                "mapped-source", manifest_hash, rights_status="study_only"
            )
        ],
    )
    assert validate_comparative_assets(output, register).ok is True


def test_mavrov_formal_control_config_remains_strictly_quarantined() -> None:
    config = read_json(ROOT / "data" / "image_native" / "comparative_sources.json")
    source = next(
        row for row in config["sources"] if row["source_id"] == "nsk-mavrov-r7822"
    )

    assert source["expected_asset_count"] == 848
    assert source["manifest_sha256"] == (
        "789a7a8eb6d584cefc999d2ae3099dbbc8c4366fdc4b840c1eab0f95ed6742df"
    )
    assert source["rights_status"] == "public_domain"
    assert source["local_asset_identity_status"] == "resolved_canvas_mapping"
    assert source["training_disposition"] == (
        "quarantine_pending_hand_boundary_and_lineage"
    )
    assert source["mapping"] == {
        "direct_relpath": "meta/canvas_mapping.json",
        "local_name_field": "local_name",
    }


def test_comparative_training_disposition_is_a_closed_enum(tmp_path: Path) -> None:
    config, source_root, _register = _fixture(tmp_path)
    payload = read_json(config)
    payload["sources"][0]["training_disposition"] = "train_candidate"
    write_json(config, payload)

    with pytest.raises(ValueError, match="unknown training disposition"):
        register_comparative_assets(config, source_root, tmp_path / "out")


def test_training_requires_registered_source_disposition_and_lineage_hashes(
    tmp_path: Path,
) -> None:
    root = tmp_path / "training-source"
    (root / "img").mkdir(parents=True)
    (root / "meta").mkdir()
    (root / "img" / "folio.jpg").write_bytes(b"unique-training-image")
    write_json(root / "meta" / "manifest.json", {"sequences": [{"canvases": []}]})
    write_json(
        root / "meta" / "canvas_mapping.json",
        [
            {
                "local_name": "folio.jpg",
                "canvas_id": "https://example.invalid/canvas/folio",
                "canvas_label": "1r",
                "image_service_id": "https://example.invalid/image/folio",
                "request_uri": "https://example.invalid/image/folio/full/max/0/default.jpg",
            }
        ],
    )
    manifest_hash = sha256_file(root / "meta" / "manifest.json")
    hashes = {
        "hand_boundary_sha256": "d" * 64,
        "line_annotation_sha256": "e" * 64,
        "split_lineage_sha256": "f" * 64,
    }
    config = tmp_path / "training.json"
    write_json(
        config,
        {
            "schema_version": "1.0.0",
            "sources": [
                {
                    "source_id": "training-source",
                    "local_subpath": "training-source",
                    "asset_glob": "img/*.jpg",
                    "expected_asset_count": 1,
                    "manifest_relpath": "meta/manifest.json",
                    "manifest_sha256": manifest_hash,
                    "manifest_uri": "https://example.invalid/manifest",
                    "rights_status": "public_domain",
                    "source_identity_status": "resolved",
                    "local_asset_identity_status": "resolved_canvas_mapping",
                    "training_disposition": "train",
                    **hashes,
                    "mapping": {
                        "direct_relpath": "meta/canvas_mapping.json",
                        "local_name_field": "local_name",
                    },
                }
            ],
        },
    )
    output = tmp_path / "out"
    register_comparative_assets(config, tmp_path, output)
    quarantined_register = _write_source_register(
        tmp_path,
        [_source_row("training-source", manifest_hash, **hashes)],
    )

    blocked = validate_comparative_assets(output, quarantined_register)

    assert blocked.ok is False
    assert blocked.training_ready_asset_count == 0
    assert any("SOURCE_DISPOSITION" in error for error in blocked.errors)

    training_register = _write_source_register(
        tmp_path,
        [
            _source_row(
                "training-source", manifest_hash, training_use="train", **hashes
            )
        ],
    )
    accepted = validate_comparative_assets(output, training_register)

    assert accepted.ok is True
    assert accepted.training_ready_asset_count == 1


def test_comparative_source_register_join_is_mandatory(tmp_path: Path) -> None:
    config, source_root, _register = _fixture(tmp_path)
    output = tmp_path / "out"
    register_comparative_assets(config, source_root, output)
    empty_register = _write_source_register(tmp_path, [])

    report = validate_comparative_assets(output, empty_register)

    assert report.ok is False
    assert any("SOURCE_REGISTER_JOIN_MISSING" in error for error in report.errors)


def test_comparative_source_register_schema_is_mandatory(tmp_path: Path) -> None:
    config, source_root, register = _fixture(tmp_path)
    output = tmp_path / "out"
    register_comparative_assets(config, source_root, output)
    payload = read_json(register)
    payload["schema_version"] = "unregistered"
    write_json(register, payload)

    report = validate_comparative_assets(output, register)

    assert report.ok is False
    assert "SOURCE_REGISTER_SCHEMA_INVALID" in report.errors
