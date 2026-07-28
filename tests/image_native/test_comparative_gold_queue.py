"""Mavrov review queues preserve pixels, order, and unresolved hand authority."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from PIL import Image
import pytest

from zfd_comparative_gold import (
    ComparativeQueueConfig,
    build_hand_boundary_queue,
    validate_hand_boundary_queue,
)
from zfd_comparative_gold.cli import _resolve_output_root, _write_bundle_new
from zfd_image_native.boundary import scan_primary_lane
from zfd_image_native.io import canonical_json, sha256_file


FIXTURE_SOURCE_ID = "fixture-mavrov-r7822"


def _value_sha256(value) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _receipt(value: dict) -> dict:
    payload = {key: item for key, item in value.items() if key != "receipt_sha256"}
    return {**payload, "receipt_sha256": _value_sha256(payload)}


def _write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(value) + "\n", encoding="utf-8", newline="\n")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(canonical_json(row) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


def _fixture(tmp_path: Path):
    repository_root = tmp_path / "repo"
    source_mount = tmp_path / "comparanda"
    source_root = source_mount / "Mavrov"
    image_root = source_root / "img"
    meta_root = source_root / "meta"
    asset_root = repository_root / "data" / "image_native"
    image_root.mkdir(parents=True)
    meta_root.mkdir()
    asset_root.mkdir(parents=True)

    names = ("z-page.jpg", "a-page.jpg", "y-page.jpg", "b-page.jpg")
    mapping = []
    assets = []
    canvases = []
    for index, name in enumerate(names):
        image_path = image_root / name
        image = Image.new("RGB", (40 + index, 60), (240 - index, 235, 220))
        image.save(image_path, quality=92)
        digest = sha256_file(image_path)
        canvas_id = f"https://example.invalid/canvas/{100 + index}"
        label = f"R7822_{index + 1:03d}"
        service_id = f"https://example.invalid/service/{100 + index}"
        mapping.append(
            {
                "byte_length": image_path.stat().st_size,
                "canvas_id": canvas_id,
                "canvas_label": label,
                "disposition": "downloaded_verified",
                "final_uri": service_id + "/full/2000,/0/default.jpg",
                "height": 60,
                "image_service_id": service_id,
                "local_name": name,
                "mime_type": "image/jpeg",
                "request_uri": service_id + "/full/2000,/0/default.jpg",
                "sha256": digest,
                "source_label": label,
                "width": 40 + index,
            }
        )
        canvases.append(
            {
                "@id": canvas_id,
                "label": label,
                "images": [
                    {
                        "resource": {
                            "@id": service_id + "/full/2000,/0/default.jpg",
                            "service": {"@id": service_id},
                        }
                    }
                ],
            }
        )
        asset_payload = {
            "schema": "zfd.comparative_asset.v1",
            "schema_version": "1.0.0",
            "source_id": FIXTURE_SOURCE_ID,
            "registered_source_id": FIXTURE_SOURCE_ID,
            "source_identity_status": "resolved",
            "local_asset_identity_status": "resolved_canvas_mapping",
            "source_label": label,
            "local_relpath": f"Mavrov/img/{name}",
            "sha256": digest,
            "byte_length": image_path.stat().st_size,
            "asset_id": "sha256:"
            + _value_sha256(
                {
                    "source_id": FIXTURE_SOURCE_ID,
                    "local_relpath": f"Mavrov/img/{name}",
                    "sha256": digest,
                }
            ),
            "lineage_root_id": "sha256:" + digest,
            "derivative_of": None,
            "duplicate_group": None,
            "manifest_uri": "https://example.invalid/manifest",
            "manifest_sha256": None,
            "canvas_id": canvas_id,
            "canvas_label": label,
            "image_service_id": service_id,
            "image_request_uri": service_id + "/full/2000,/0/default.jpg",
            "rights_status": "public_domain",
            "training_disposition": "quarantine_pending_hand_boundary_and_lineage",
            "hand_boundary_sha256": None,
            "line_annotation_sha256": None,
            "split_lineage_sha256": None,
            "acquisition_receipt": {
                "mapping_state": "canvas_mapped",
                "method": "saved_mapping",
            },
        }
        assets.append(asset_payload)

    manifest = {"sequences": [{"canvases": canvases}]}
    manifest_path = meta_root / "manifest.json"
    mapping_path = meta_root / "canvas_mapping.json"
    _write_json(manifest_path, manifest)
    _write_json(mapping_path, mapping)
    manifest_sha = sha256_file(manifest_path)
    mapping_sha = sha256_file(mapping_path)
    acquisition = _receipt(
        {
            "schema": "zfd.comparative_acquisition.v1",
            "schema_version": "1.0.0",
            "source_id": FIXTURE_SOURCE_ID,
            "manifest_uri": "https://example.invalid/manifest",
            "manifest_final_uri": "https://example.invalid/manifest",
            "manifest_sha256": manifest_sha,
            "selection_uri": None,
            "selection_final_uri": None,
            "selection_method": "complete_manifest",
            "selection_sha256": None,
            "selected_canvas_count": 4,
            "expected_count": 4,
            "downloaded_asset_count": 4,
            "reused_asset_count": 0,
            "verified_asset_count": 4,
            "failed_asset_count": 0,
            "failures": [],
        }
    )
    acquisition_path = meta_root / "acquisition_receipt.json"
    _write_json(acquisition_path, acquisition)

    for row in assets:
        row["manifest_sha256"] = manifest_sha
    asset_rows = [_receipt(row) for row in assets]
    asset_path = asset_root / "comparative_assets.jsonl"
    _write_jsonl(asset_path, asset_rows)
    duplicate_path = asset_root / "comparative_duplicate_groups.jsonl"
    _write_jsonl(duplicate_path, [])
    summary = {
        "schema_version": "1.0.0",
        "source_count": 1,
        "asset_count": 4,
        "unique_content_count": 4,
        "duplicate_asset_count": 0,
        "duplicate_groups": 0,
        "cross_source_duplicate_groups": 0,
        "mapped_canvas_count": 4,
        "training_ready_asset_count": 0,
        "sources": [
            {
                "source_id": FIXTURE_SOURCE_ID,
                "registered_source_id": FIXTURE_SOURCE_ID,
                "manifest_sha256": manifest_sha,
                "asset_count": 4,
                "unique_content_count": 4,
                "mapped_canvas_count": 4,
                "source_identity_status": "resolved",
                "local_asset_identity_status": "resolved_canvas_mapping",
                "rights_status": "public_domain",
                "training_disposition": "quarantine_pending_hand_boundary_and_lineage",
                "hand_boundary_sha256": None,
                "line_annotation_sha256": None,
                "split_lineage_sha256": None,
            }
        ],
    }
    summary_path = asset_root / "comparative_asset_summary.json"
    _write_json(summary_path, summary)

    source_config = {
        "schema_version": "1.0.0",
        "sources": [
            {
                "source_id": FIXTURE_SOURCE_ID,
                "registered_source_id": FIXTURE_SOURCE_ID,
                "local_subpath": "Mavrov",
                "asset_glob": "img/*.jpg",
                "expected_asset_count": 4,
                "manifest_relpath": "meta/manifest.json",
                "manifest_sha256": manifest_sha,
                "manifest_uri": "https://example.invalid/manifest",
                "rights_status": "public_domain",
                "source_identity_status": "resolved",
                "local_asset_identity_status": "resolved_canvas_mapping",
                "training_disposition": "quarantine_pending_hand_boundary_and_lineage",
                "mapping": {
                    "direct_relpath": "meta/canvas_mapping.json",
                    "local_name_field": "local_name",
                },
            }
        ],
    }
    config_path = asset_root / "comparative_sources.json"
    _write_json(config_path, source_config)
    source_register = {
        "schema_version": "2.0.0",
        "sources": [
            {
                "source_id": FIXTURE_SOURCE_ID,
                "source_label": "Mavrov brevijar, R 7822",
                "title": "Mavrov brevijar",
                "stable_locator": "https://example.invalid/manifest",
                "date_kind": "writing",
                "date_basis": "catalogued formal layer 1460 and calendar addition 1471",
                "dating_authority": "fixture authority",
                "dating_authority_locator": "https://example.invalid/manifest",
                "dating_certainty": "catalogued_range",
                "material_date_start": None,
                "material_date_end": None,
                "writing_date_start": 1460,
                "writing_date_end": 1471,
                "text_date_start": None,
                "text_date_end": None,
                "copy_date_start": None,
                "copy_date_end": None,
                "publication_date_start": None,
                "publication_date_end": None,
                "institution": "fixture library",
                "shelfmark": "R 7822",
                "language": "Croatian",
                "script": "Croatian Glagolitic",
                "hand_style": "formal_ustavna_1460_and_calendar_hand_1471_boundaries_unmapped",
                "genre": "breviary",
                "region": "Croatia; precise production place unresolved",
                "source_type": "manuscript",
                "evidentiary_role": "dated_formal_and_calendar_script_control_unmapped_layers",
                "training_use": "quarantined",
                "rights_statement": "public domain fixture",
                "rights_locator": "https://example.invalid/rights",
                "rights_status": "public_domain",
                "identity_status": "resolved",
                "manifest_sha256": manifest_sha,
                "asset_mapping_sha256": mapping_sha,
                "page_mapping_sha256": mapping_sha,
                "lineage_sha256": acquisition["receipt_sha256"],
                "control_group": "formal_glagolitic_fifteenth_century",
                "hand_boundary_sha256": None,
                "line_annotation_sha256": None,
                "split_lineage_sha256": None,
            }
        ],
    }
    register_path = asset_root / "source_register.json"
    _write_json(register_path, source_register)
    return {
        "repository_root": repository_root,
        "source_mount": source_mount,
        "asset_root": asset_root,
        "config_path": config_path,
        "register_path": register_path,
        "source_root": source_root,
        "image_root": image_root,
        "names": names,
    }


@pytest.fixture(autouse=True)
def _uninstalled_git_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    import zfd_comparative_gold.core as queue_core

    monkeypatch.setattr(queue_core, "_git_state", lambda: (None, None))


def _config() -> ComparativeQueueConfig:
    return ComparativeQueueConfig(
        source_id=FIXTURE_SOURCE_ID,
        expected_asset_count=4,
        pilot_pairs=((0, 1), (2, 3)),
    )


def _build_kwargs(fixture: dict) -> dict:
    return {
        "repository_root": fixture["repository_root"],
        "source_mount": fixture["source_mount"],
        "asset_root": fixture["asset_root"],
        "config_path": fixture["config_path"],
        "register_path": fixture["register_path"],
    }


def test_queue_follows_manifest_order_and_blocks_all_authority(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    build_kwargs = _build_kwargs(fixture)
    bundle = build_hand_boundary_queue(**build_kwargs, config=_config())

    assert len(bundle.rows) == 4
    assert [Path(row["local_relpath"]).name for row in bundle.rows] == list(
        fixture["names"]
    )
    assert bundle.rows[0]["boundary_before_state"] == "manuscript_start"
    assert {row["hand_identity_state"] for row in bundle.rows} == {
        "unknown_unreviewed"
    }
    assert {row["line_annotation_state"] for row in bundle.rows} == {"not_started"}
    assert {row["split_assignment_state"] for row in bundle.rows} == {
        "blocked_unknown_hand"
    }
    assert all(row["training_eligible"] is False for row in bundle.rows)
    assert len(bundle.pilot) == 2
    assert bundle.summary["unresolved_boundary_count"] == 3
    assert bundle.summary["training_ready_asset_count"] == 0
    assert bundle.summary["hand_boundary_sha256"] is None
    assert bundle.summary["line_annotation_sha256"] is None
    assert bundle.summary["split_lineage_sha256"] is None
    assert validate_hand_boundary_queue(bundle, **build_kwargs, config=_config()) == ()


def test_queue_rejects_pixel_mapping_and_manifest_tampering(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    build_kwargs = _build_kwargs(fixture)
    bundle = build_hand_boundary_queue(**build_kwargs, config=_config())
    image_path = fixture["image_root"] / fixture["names"][1]
    image_path.write_bytes(image_path.read_bytes() + b"tamper")

    errors = validate_hand_boundary_queue(bundle, **build_kwargs, config=_config())

    assert any("SOURCE_ASSET" in error for error in errors)


def test_queue_rejects_promoted_source_or_existing_training_hashes(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    assets = [
        json.loads(line)
        for line in (fixture["asset_root"] / "comparative_assets.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assets[0]["hand_boundary_sha256"] = "a" * 64
    assets[0] = _receipt(assets[0])
    _write_jsonl(fixture["asset_root"] / "comparative_assets.jsonl", assets)

    with pytest.raises(ValueError, match="SOURCE_TRAINING_AUTHORITY_ALREADY_PRESENT"):
        build_hand_boundary_queue(**_build_kwargs(fixture), config=_config())


@pytest.mark.parametrize(
    ("field", "replacement", "error"),
    (
        ("asset_id", "sha256:" + "f" * 64, "SOURCE_ASSET_ID_MISMATCH"),
        ("lineage_root_id", "sha256:" + "e" * 64, "SOURCE_ASSET_LINEAGE_MISMATCH"),
    ),
)
def test_queue_recomputes_upstream_asset_identities(
    tmp_path: Path, field: str, replacement: str, error: str
) -> None:
    fixture = _fixture(tmp_path)
    asset_path = fixture["asset_root"] / "comparative_assets.jsonl"
    assets = [json.loads(line) for line in asset_path.read_text(encoding="utf-8").splitlines()]
    assets[0][field] = replacement
    assets[0] = _receipt(assets[0])
    _write_jsonl(asset_path, assets)

    with pytest.raises(ValueError, match=error):
        build_hand_boundary_queue(**_build_kwargs(fixture), config=_config())


def test_queue_rejects_missing_dated_script_metadata(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    register_path = fixture["register_path"]
    register = json.loads(register_path.read_text(encoding="utf-8"))
    del register["sources"][0]["script"]
    _write_json(register_path, register)

    with pytest.raises(ValueError, match="SOURCE_REGISTER_METADATA_INVALID:script"):
        build_hand_boundary_queue(**_build_kwargs(fixture), config=_config())


def test_queue_rejects_contradictory_top_level_summary(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    summary_path = fixture["asset_root"] / "comparative_asset_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["training_ready_asset_count"] = 4
    _write_json(summary_path, summary)

    with pytest.raises(ValueError, match="SOURCE_ASSET_SUMMARY_TOTALS_INVALID"):
        build_hand_boundary_queue(**_build_kwargs(fixture), config=_config())


def test_queue_rejects_inconsistent_duplicate_ledger(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    duplicate_path = fixture["asset_root"] / "comparative_duplicate_groups.jsonl"
    _write_jsonl(duplicate_path, [_receipt({"schema": "counterfeit"})])

    with pytest.raises(ValueError, match="SOURCE_DUPLICATE_LEDGER"):
        build_hand_boundary_queue(**_build_kwargs(fixture), config=_config())


def test_queue_validation_rejects_reordered_or_promoted_rows(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    build_kwargs = _build_kwargs(fixture)
    bundle = build_hand_boundary_queue(**build_kwargs, config=_config())
    promoted = deepcopy(bundle)
    promoted.rows[1]["training_eligible"] = True

    errors = validate_hand_boundary_queue(promoted, **build_kwargs, config=_config())

    assert "QUEUE_ROW_RECEIPT_HASH_MISMATCH:1" in errors
    assert "QUEUE_RECOMPUTE_MISMATCH" in errors


def test_queue_pilot_requires_unique_adjacent_in_range_pairs() -> None:
    for pairs in (((0, 2),), ((0, 1), (0, 1)), ((3, 4),)):
        with pytest.raises(ValueError, match="PILOT_PAIR"):
            ComparativeQueueConfig(
                source_id=FIXTURE_SOURCE_ID,
                expected_asset_count=4,
                pilot_pairs=pairs,
            )


def test_canonical_mavrov_requires_exact_count_and_pilot() -> None:
    for count, pairs in ((848, ((10, 11),)), (4, ((0, 1), (2, 3)))):
        with pytest.raises(ValueError, match="MAVROV|PILOT_PAIR"):
            ComparativeQueueConfig(
                source_id="nsk-mavrov-r7822",
                expected_asset_count=count,
                pilot_pairs=pairs,
            )


def test_canonical_mavrov_rejects_counterfeit_trust_anchor() -> None:
    import zfd_comparative_gold.core as queue_core

    with pytest.raises(ValueError, match="MAVROV_TRUST_ANCHOR"):
        queue_core._validate_mavrov_trust_anchor(
            ComparativeQueueConfig(),
            source={"manifest_uri": "https://example.invalid/manifest"},
            register={"stable_locator": "https://example.invalid/manifest"},
            authority_projection={
                "manifest_file_sha256": "0" * 64,
                "mapping_file_sha256": "1" * 64,
                "acquisition_file_sha256": "2" * 64,
                "acquisition_receipt_sha256": "3" * 64,
            },
        )


def test_git_object_ids_accept_sha1_and_sha256_only() -> None:
    import zfd_comparative_gold.core as queue_core

    assert queue_core._valid_git_object_id("a" * 40) is True
    assert queue_core._valid_git_object_id("b" * 64) is True
    assert queue_core._valid_git_object_id("c" * 39) is False
    assert queue_core._valid_git_object_id("d" * 65) is False
    assert queue_core._valid_git_object_id("G" * 40) is False


def test_implementation_authority_includes_package_and_environment_files() -> None:
    import zfd_comparative_gold.core as queue_core

    assert set(queue_core._ENVIRONMENT_AUTHORITY_SHA256) == {
        "pyproject.toml",
        "requirements-image-native.txt",
    }
    assert all(
        len(digest) == 64
        for digest in queue_core._ENVIRONMENT_AUTHORITY_SHA256.values()
    )


def test_implementation_hash_is_equal_without_repository_root(tmp_path: Path) -> None:
    import zfd_comparative_gold.core as queue_core

    source_hash = queue_core._implementation_sha256()
    installed_hash = queue_core._implementation_sha256(
        package_root=Path(queue_core.__file__).resolve().parent,
        repository_root=tmp_path / "site-packages",
    )

    assert installed_hash == source_hash


def test_git_commit_reachability_rejects_dangling_commit(tmp_path: Path) -> None:
    import zfd_comparative_gold.core as queue_core

    repository = tmp_path / "git-repository"
    repository.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=repository, check=True)
    subprocess.run(["git", "config", "user.name", "ZFD test"], cwd=repository, check=True)
    _write_json(repository / "authority.json", {"state": "tracked"})
    subprocess.run(["git", "add", "authority.json"], cwd=repository, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "authority"], cwd=repository, check=True)
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repository, check=True, capture_output=True, text=True
    ).stdout.strip()
    tree = subprocess.run(
        ["git", "rev-parse", "HEAD^{tree}"], cwd=repository, check=True, capture_output=True, text=True
    ).stdout.strip()
    dangling = subprocess.run(
        ["git", "commit-tree", tree, "-m", "dangling"],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    assert queue_core._git_commit_reachable(repository, head) is True
    assert queue_core._git_commit_reachable(repository, dangling) is False


def test_queue_rejects_null_commit_with_nonnull_dirty_state(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    build_kwargs = _build_kwargs(fixture)
    bundle = build_hand_boundary_queue(**build_kwargs, config=_config())
    forged = deepcopy(bundle)
    forged.summary["implementation_git_commit"] = None
    forged.summary["implementation_git_worktree_dirty"] = "forged"
    forged.summary = _receipt(forged.summary)

    errors = validate_hand_boundary_queue(forged, **build_kwargs, config=_config())

    assert "IMPLEMENTATION_GIT_PROVENANCE_TUPLE_INVALID" in errors


def test_queue_rejects_dirty_implementation_receipts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import zfd_comparative_gold.core as queue_core

    fixture = _fixture(tmp_path)
    build_kwargs = _build_kwargs(fixture)
    monkeypatch.setattr(queue_core, "_git_state", lambda: ("a" * 40, True))
    bundle = build_hand_boundary_queue(**build_kwargs, config=_config())

    errors = validate_hand_boundary_queue(bundle, **build_kwargs, config=_config())

    assert "IMPLEMENTATION_WORKTREE_DIRTY" in errors


def test_queue_rejects_coordinated_git_provenance_erasure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import zfd_comparative_gold.core as queue_core

    fixture = _fixture(tmp_path)
    build_kwargs = _build_kwargs(fixture)
    monkeypatch.setattr(queue_core, "_git_state", lambda: ("a" * 40, True))
    bundle = build_hand_boundary_queue(**build_kwargs, config=_config())
    forged = deepcopy(bundle)
    forged.summary["implementation_git_commit"] = None
    forged.summary["implementation_git_worktree_dirty"] = None
    forged.summary["implementation_provenance_status"] = "unversioned_current_bytes"
    forged.summary = _receipt(forged.summary)

    errors = validate_hand_boundary_queue(forged, **build_kwargs, config=_config())

    assert "IMPLEMENTATION_GIT_PROVENANCE_ERASED" in errors


def test_cli_refuses_dirty_bundle_before_writing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import zfd_comparative_gold.cli as queue_cli
    import zfd_comparative_gold.core as queue_core

    fixture = _fixture(tmp_path)
    build_kwargs = _build_kwargs(fixture)
    monkeypatch.setattr(queue_core, "_git_state", lambda: ("a" * 40, True))
    bundle = build_hand_boundary_queue(**build_kwargs, config=_config())

    with pytest.raises(ValueError, match="IMPLEMENTATION_WORKTREE_DIRTY"):
        queue_cli._require_valid_bundle(bundle, {**build_kwargs, "config": _config()})


def test_cli_refuses_unversioned_bundle_before_writing(tmp_path: Path) -> None:
    import zfd_comparative_gold.cli as queue_cli

    fixture = _fixture(tmp_path)
    build_kwargs = _build_kwargs(fixture)
    bundle = build_hand_boundary_queue(**build_kwargs, config=_config())

    with pytest.raises(ValueError, match="IMPLEMENTATION_PROVENANCE_NOT_PUBLISHABLE"):
        queue_cli._require_valid_bundle(bundle, {**build_kwargs, "config": _config()})


def test_cli_stdout_receipts_survive_legacy_windows_encoding() -> None:
    import zfd_comparative_gold.cli as queue_cli

    payload = queue_cli._stdout_json({"output_root": "C:/dokumenti/čakavski"})

    assert "\\u010d" in payload
    payload.encode("cp1252", errors="strict")


def test_cli_output_receipt_uses_repository_relative_locator(tmp_path: Path) -> None:
    import zfd_comparative_gold.cli as queue_cli

    repository_root = tmp_path / "répo"
    target = repository_root / "build" / "comparative_review" / "run-001"

    assert queue_cli._repository_relative_locator(target, repository_root) == (
        "build/comparative_review/run-001"
    )


def test_queue_output_is_confined_new_and_byte_deterministic(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    bundle = build_hand_boundary_queue(**_build_kwargs(fixture), config=_config())
    first = _resolve_output_root(
        Path("build/comparative_review/first"), fixture["repository_root"]
    )
    second = _resolve_output_root(
        Path("build/comparative_review/second"), fixture["repository_root"]
    )
    _write_bundle_new(first, bundle)
    _write_bundle_new(second, bundle)

    for name in (
        "hand_boundary_queue.jsonl",
        "hand_boundary_pilot.jsonl",
        "hand_boundary_summary.json",
    ):
        assert (first / name).read_bytes() == (second / name).read_bytes()
    with pytest.raises(ValueError, match="OUTPUT_ROOT_ALREADY_EXISTS"):
        _write_bundle_new(first, bundle)
    with pytest.raises(ValueError, match="OUTPUT_OUTSIDE_ALLOWED_ROOT"):
        _resolve_output_root(Path("data/image_native/escape"), fixture["repository_root"])


def test_comparative_queue_has_no_inherited_text_dependency() -> None:
    hits = scan_primary_lane(
        Path(__file__).resolve().parents[2] / "zfd_comparative_gold",
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
    )
    assert hits == []
