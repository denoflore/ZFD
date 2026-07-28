"""Immutable, pixel-bound comparative manuscript review queues.

This module deliberately has no dependency on the OCR, decoder, transcription,
or translation packages.  It inventories source pixels for human palaeographic
review while preserving every unresolved hand as an explicit unknown.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
from typing import Any, Iterable

from PIL import Image


QUEUE_SCHEMA = "zfd.comparative_hand_boundary_queue.v1"
QUEUE_ROW_SCHEMA = "zfd.comparative_hand_boundary_queue_row.v1"
PILOT_SCHEMA = "zfd.comparative_hand_boundary_pilot.v1"
PILOT_ROW_SCHEMA = "zfd.comparative_hand_boundary_pilot_row.v1"
SCHEMA_VERSION = "1.0.0"
SELECTION_RULE_ID = "endpoint_inclusive_even_adjacent_pairs.v1"
MAVROV_SOURCE_ID = "nsk-mavrov-r7822"
MAVROV_ASSET_COUNT = 848
MAVROV_PILOT_PAIRS = (
    (0, 1),
    (121, 122),
    (242, 243),
    (363, 364),
    (483, 484),
    (604, 605),
    (725, 726),
    (846, 847),
)
_SHA256 = re.compile(r"[0-9a-f]{64}")
_GIT_OBJECT_ID = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")
_IMPLEMENTATION_PATHS = (
    "zfd_comparative_gold/__init__.py",
    "zfd_comparative_gold/__main__.py",
    "zfd_comparative_gold/cli.py",
    "zfd_comparative_gold/core.py",
)
_ENVIRONMENT_AUTHORITY_SHA256 = {
    "pyproject.toml": "253a0de61caa4bb9cf617fb9554814a28e45bc931fe32b1b2ff62d5005b09522",
    "requirements-image-native.txt": "56599eacb0f2a0465bdea8869d0111e661b8e5ae22c58153f66078ae7056e7aa",
}
_MAVROV_TRUST_ANCHOR = {
    "source_config_record_sha256": "4e11d0e709161f36a426e4ddcb62c1537c2e38d101d836e68d5026b1a7b1c411",
    "source_register_record_sha256": "c5db1d877dcf3bd3ed59fc57d237981a2f88302974b8b48de39182349fb7dcb1",
    "manifest_file_sha256": "789a7a8eb6d584cefc999d2ae3099dbbc8c4366fdc4b840c1eab0f95ed6742df",
    "mapping_file_sha256": "f43b604ad62f133e41c534ca29579e7e17c1e7176fb2a1315aa2cb68df41bca5",
    "acquisition_file_sha256": "e7b105fc676969900e05a158f08e8659d7fa436481184a8c2323f4c3b8a36694",
    "acquisition_receipt_sha256": "54ebce142ec0b1ae23875faa14f4864d509a35ecf57e9ad5db08522de88b6b94",
}
_TRAINING_AUTHORITY_FIELDS = (
    "hand_boundary_sha256",
    "line_annotation_sha256",
    "split_lineage_sha256",
)
_REQUIRED_REGISTER_TEXT_FIELDS = (
    "source_label",
    "title",
    "stable_locator",
    "date_kind",
    "date_basis",
    "dating_authority",
    "dating_authority_locator",
    "dating_certainty",
    "institution",
    "shelfmark",
    "language",
    "script",
    "hand_style",
    "genre",
    "region",
    "source_type",
    "evidentiary_role",
    "rights_statement",
    "rights_locator",
    "control_group",
)


@dataclass(frozen=True)
class ComparativeQueueConfig:
    source_id: str = MAVROV_SOURCE_ID
    expected_asset_count: int = MAVROV_ASSET_COUNT
    pilot_pairs: tuple[tuple[int, int], ...] = MAVROV_PILOT_PAIRS
    selection_rule_id: str = SELECTION_RULE_ID

    def __post_init__(self) -> None:
        if not isinstance(self.source_id, str) or not self.source_id.strip():
            raise ValueError("SOURCE_ID_INVALID")
        if type(self.expected_asset_count) is not int or self.expected_asset_count < 2:
            raise ValueError("EXPECTED_ASSET_COUNT_INVALID")
        if self.selection_rule_id != SELECTION_RULE_ID:
            raise ValueError("PILOT_PAIR_SELECTION_RULE_INVALID")
        if self.source_id == MAVROV_SOURCE_ID:
            if self.expected_asset_count != MAVROV_ASSET_COUNT:
                raise ValueError("MAVROV_EXPECTED_ASSET_COUNT_INVALID")
            if self.pilot_pairs != MAVROV_PILOT_PAIRS:
                raise ValueError("MAVROV_PILOT_PAIR_SET_INVALID")
        seen_pairs: set[tuple[int, int]] = set()
        seen_ordinals: set[int] = set()
        if not self.pilot_pairs:
            raise ValueError("PILOT_PAIR_SET_EMPTY")
        for pair in self.pilot_pairs:
            if (
                not isinstance(pair, tuple)
                or len(pair) != 2
                or any(type(value) is not int for value in pair)
            ):
                raise ValueError("PILOT_PAIR_MALFORMED")
            left, right = pair
            if left < 0 or right >= self.expected_asset_count or right != left + 1:
                raise ValueError("PILOT_PAIR_NOT_ADJACENT_OR_OUT_OF_RANGE")
            if pair in seen_pairs or left in seen_ordinals or right in seen_ordinals:
                raise ValueError("PILOT_PAIR_DUPLICATE_OR_OVERLAPPING")
            seen_pairs.add(pair)
            seen_ordinals.update(pair)


@dataclass
class HandBoundaryQueueBundle:
    rows: list[dict[str, Any]]
    pilot: list[dict[str, Any]]
    summary: dict[str, Any]


@dataclass(frozen=True)
class _Authority:
    source: dict[str, Any]
    register: dict[str, Any]
    summary_source: dict[str, Any]
    mapping: tuple[dict[str, Any], ...]
    assets: tuple[dict[str, Any], ...]
    source_root: Path
    authority_projection: dict[str, Any]


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _canonical_bytes(value: Any) -> bytes:
    return _canonical_json(value).encode("utf-8")


def _value_sha256(value: Any) -> str:
    return sha256(_canonical_bytes(value)).hexdigest()


def _domain_sha256(domain: str, value: Any) -> str:
    return sha256(domain.encode("ascii") + b"\0" + _canonical_bytes(value)).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _jsonl_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    return b"".join(_canonical_bytes(row) + b"\n" for row in rows)


def _receipt(payload: dict[str, Any]) -> dict[str, Any]:
    body = {key: value for key, value in payload.items() if key != "receipt_sha256"}
    return {**body, "receipt_sha256": _value_sha256(body)}


def _receipt_valid(payload: dict[str, Any]) -> bool:
    supplied = payload.get("receipt_sha256")
    body = {key: value for key, value in payload.items() if key != "receipt_sha256"}
    return isinstance(supplied, str) and supplied == _value_sha256(body)


def _valid_git_object_id(value: Any) -> bool:
    return isinstance(value, str) and _GIT_OBJECT_ID.fullmatch(value) is not None


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as stream:
        return json.load(stream)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"SOURCE_LEDGER_ROW_MALFORMED:{line_number}")
            rows.append(value)
    return rows


def _inside(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _safe_relative_path(value: Any, code: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError(code)
    candidate = PurePosixPath(value)
    if candidate.is_absolute() or ".." in candidate.parts or "." in candidate.parts:
        raise ValueError(code)
    return candidate


def _safe_join(root: Path, value: Any, code: str) -> Path:
    relative = _safe_relative_path(value, code)
    target = root.joinpath(*relative.parts).resolve()
    if not _inside(target, root):
        raise ValueError(code)
    return target


def _unique_source(rows: Any, source_id: str, code: str) -> dict[str, Any]:
    if not isinstance(rows, list):
        raise ValueError(code)
    selected = [row for row in rows if isinstance(row, dict) and row.get("source_id") == source_id]
    if len(selected) != 1:
        raise ValueError(code)
    return selected[0]


def _require_no_training_authority(row: dict[str, Any]) -> None:
    if any(row.get(field) is not None for field in _TRAINING_AUTHORITY_FIELDS):
        raise ValueError("SOURCE_TRAINING_AUTHORITY_ALREADY_PRESENT")


def _validate_register_metadata(register: dict[str, Any]) -> None:
    for field in _REQUIRED_REGISTER_TEXT_FIELDS:
        value = register.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"SOURCE_REGISTER_METADATA_INVALID:{field}")
    start = register.get("writing_date_start")
    end = register.get("writing_date_end")
    if type(start) is not int or type(end) is not int or not 1000 <= start <= end <= 2000:
        raise ValueError("SOURCE_REGISTER_METADATA_INVALID:writing_date_range")


def _validate_mavrov_trust_anchor(
    config: ComparativeQueueConfig,
    *,
    source: dict[str, Any],
    register: dict[str, Any],
    authority_projection: dict[str, Any],
) -> None:
    if config.source_id != MAVROV_SOURCE_ID:
        return
    observed = {
        "source_config_record_sha256": _value_sha256(source),
        "source_register_record_sha256": _value_sha256(register),
        **{
            field: authority_projection.get(field)
            for field in (
                "manifest_file_sha256",
                "mapping_file_sha256",
                "acquisition_file_sha256",
                "acquisition_receipt_sha256",
            )
        },
    }
    for field, expected in _MAVROV_TRUST_ANCHOR.items():
        if observed.get(field) != expected:
            raise ValueError(f"MAVROV_TRUST_ANCHOR_MISMATCH:{field}")


def _canvas_sequence(manifest: Any) -> list[dict[str, Any]]:
    if not isinstance(manifest, dict) or not isinstance(manifest.get("sequences"), list):
        raise ValueError("SOURCE_MANIFEST_MALFORMED")
    canvases: list[dict[str, Any]] = []
    for sequence in manifest["sequences"]:
        if not isinstance(sequence, dict) or not isinstance(sequence.get("canvases"), list):
            raise ValueError("SOURCE_MANIFEST_MALFORMED")
        for canvas in sequence["canvases"]:
            if not isinstance(canvas, dict):
                raise ValueError("SOURCE_MANIFEST_CANVAS_MALFORMED")
            canvases.append(canvas)
    return canvases


def _manifest_service_id(canvas: dict[str, Any]) -> Any:
    images = canvas.get("images")
    if not isinstance(images, list) or len(images) != 1 or not isinstance(images[0], dict):
        raise ValueError("SOURCE_MANIFEST_CANVAS_IMAGE_MALFORMED")
    resource = images[0].get("resource")
    if not isinstance(resource, dict):
        raise ValueError("SOURCE_MANIFEST_CANVAS_IMAGE_MALFORMED")
    service = resource.get("service")
    if not isinstance(service, dict):
        raise ValueError("SOURCE_MANIFEST_CANVAS_IMAGE_MALFORMED")
    return service.get("@id")


def _implementation_projection(
    file_bytes: dict[str, bytes], environment_hashes: dict[str, str]
) -> list[dict[str, str]]:
    records = [
        {"path": path, "sha256": sha256(file_bytes[path]).hexdigest()}
        for path in sorted(file_bytes)
    ]
    records.extend(
        {"path": path, "sha256": environment_hashes[path]}
        for path in sorted(environment_hashes)
    )
    return sorted(records, key=lambda record: record["path"])


def _implementation_sha256(
    *,
    package_root: Path | None = None,
    repository_root: Path | None = None,
) -> str:
    package_root = Path(__file__).resolve().parent if package_root is None else package_root.resolve()
    repository_root = package_root.parent if repository_root is None else repository_root.resolve()
    file_bytes: dict[str, bytes] = {}
    for relative in _IMPLEMENTATION_PATHS:
        parts = PurePosixPath(relative).parts
        if not parts or parts[0] != "zfd_comparative_gold":
            raise ValueError(f"IMPLEMENTATION_PATH_INVALID:{relative}")
        path = package_root.joinpath(*parts[1:])
        if not path.is_file():
            raise ValueError(f"IMPLEMENTATION_FILE_MISSING:{relative}")
        file_bytes[relative] = path.read_bytes()
    environment_hashes = dict(_ENVIRONMENT_AUTHORITY_SHA256)
    for relative, expected in environment_hashes.items():
        path = repository_root.joinpath(*PurePosixPath(relative).parts)
        if path.is_file() and _file_sha256(path) != expected:
            raise ValueError(f"ENVIRONMENT_AUTHORITY_MISMATCH:{relative}")
    return _value_sha256(_implementation_projection(file_bytes, environment_hashes))


def _git_state() -> tuple[str | None, bool | None]:
    repository_root = Path(__file__).resolve().parents[1]
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repository_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        status = subprocess.run(
            [
                "git",
                "status",
                "--porcelain",
                "--",
                "zfd_comparative_gold",
                "pyproject.toml",
                "requirements-image-native.txt",
            ],
            cwd=repository_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None, None
    if not _valid_git_object_id(commit):
        return None, None
    return commit, bool(status.strip())


def _git_commit_reachable(repository_root: Path, commit: str) -> bool:
    if not _valid_git_object_id(commit):
        return False
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, "HEAD"],
        cwd=repository_root,
        check=False,
        capture_output=True,
    )
    return result.returncode == 0


def _historical_implementation_sha256(repository_root: Path, commit: str) -> str:
    if not _valid_git_object_id(commit):
        raise ValueError("IMPLEMENTATION_GIT_COMMIT_INVALID")
    if not _git_commit_reachable(repository_root, commit):
        raise ValueError("IMPLEMENTATION_GIT_COMMIT_UNREACHABLE")
    kind = subprocess.run(
        ["git", "cat-file", "-t", commit],
        cwd=repository_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if kind != "commit":
        raise ValueError("IMPLEMENTATION_GIT_OBJECT_NOT_COMMIT")
    file_bytes: dict[str, bytes] = {}
    for relative in _IMPLEMENTATION_PATHS:
        result = subprocess.run(
            ["git", "show", f"{commit}:{relative}"],
            cwd=repository_root,
            check=True,
            capture_output=True,
        )
        file_bytes[relative] = result.stdout
    environment_hashes: dict[str, str] = {}
    for relative in _ENVIRONMENT_AUTHORITY_SHA256:
        result = subprocess.run(
            ["git", "show", f"{commit}:{relative}"],
            cwd=repository_root,
            check=True,
            capture_output=True,
        )
        environment_hashes[relative] = sha256(result.stdout).hexdigest()
    return _value_sha256(_implementation_projection(file_bytes, environment_hashes))


def _validate_full_asset_ledgers(
    all_assets: list[dict[str, Any]],
    duplicate_rows: list[dict[str, Any]],
    summary_payload: dict[str, Any],
) -> None:
    asset_ids: set[str] = set()
    by_content: dict[str, list[dict[str, Any]]] = {}
    source_ids: set[str] = set()
    for ordinal, asset in enumerate(all_assets):
        if not _receipt_valid(asset):
            raise ValueError(f"SOURCE_ASSET_LEDGER_RECEIPT_INVALID:{ordinal}")
        source_id = asset.get("source_id")
        local_relpath = asset.get("local_relpath")
        digest = asset.get("sha256")
        if not isinstance(source_id, str) or not source_id:
            raise ValueError(f"SOURCE_ASSET_LEDGER_SOURCE_ID_INVALID:{ordinal}")
        _safe_relative_path(local_relpath, f"SOURCE_ASSET_LEDGER_PATH_INVALID:{ordinal}")
        if not isinstance(digest, str) or _SHA256.fullmatch(digest) is None:
            raise ValueError(f"SOURCE_ASSET_LEDGER_SHA256_INVALID:{ordinal}")
        expected_asset_id = "sha256:" + _value_sha256(
            {"source_id": source_id, "local_relpath": local_relpath, "sha256": digest}
        )
        if asset.get("asset_id") != expected_asset_id:
            raise ValueError(f"SOURCE_ASSET_ID_MISMATCH:{ordinal}")
        if expected_asset_id in asset_ids:
            raise ValueError(f"SOURCE_ASSET_ID_DUPLICATE:{ordinal}")
        if asset.get("lineage_root_id") != f"sha256:{digest}":
            raise ValueError(f"SOURCE_ASSET_LINEAGE_MISMATCH:{ordinal}")
        asset_ids.add(expected_asset_id)
        source_ids.add(source_id)
        by_content.setdefault(digest, []).append(asset)

    expected_duplicates: list[dict[str, Any]] = []
    duplicate_asset_count = 0
    for digest, content_assets in sorted(by_content.items()):
        expected_group = (
            "sha256:" + _value_sha256({"content_sha256": digest})
            if len(content_assets) > 1
            else None
        )
        for asset in content_assets:
            if asset.get("duplicate_group") != expected_group:
                raise ValueError("SOURCE_DUPLICATE_LEDGER_BACKLINK_MISMATCH")
        if expected_group is None:
            continue
        duplicate_asset_count += len(content_assets)
        group_sources = sorted({asset["source_id"] for asset in content_assets})
        expected_duplicates.append(
            _receipt(
                {
                    "schema": "zfd.comparative_duplicate_group.v1",
                    "schema_version": SCHEMA_VERSION,
                    "duplicate_group": expected_group,
                    "content_sha256": digest,
                    "asset_ids": sorted(asset["asset_id"] for asset in content_assets),
                    "source_ids": group_sources,
                    "asset_count": len(content_assets),
                    "cross_source": len(group_sources) > 1,
                    "training_disposition": "exclude_duplicate_leakage",
                }
            )
        )
    if _jsonl_bytes(duplicate_rows) != _jsonl_bytes(expected_duplicates):
        raise ValueError("SOURCE_DUPLICATE_LEDGER_RECOMPUTE_MISMATCH")

    expected_totals = {
        "schema_version": SCHEMA_VERSION,
        "source_count": len(source_ids),
        "asset_count": len(all_assets),
        "unique_content_count": len(by_content),
        "duplicate_asset_count": duplicate_asset_count,
        "duplicate_groups": len(expected_duplicates),
        "cross_source_duplicate_groups": sum(
            bool(row["cross_source"]) for row in expected_duplicates
        ),
        "mapped_canvas_count": sum(asset.get("canvas_id") is not None for asset in all_assets),
        "training_ready_asset_count": sum(
            asset.get("training_disposition") == "train" for asset in all_assets
        ),
    }
    if any(summary_payload.get(field) != value for field, value in expected_totals.items()):
        raise ValueError("SOURCE_ASSET_SUMMARY_TOTALS_INVALID")
    summary_sources = summary_payload.get("sources")
    if not isinstance(summary_sources, list):
        raise ValueError("SOURCE_ASSET_SUMMARY_SOURCES_INVALID")
    summary_source_ids = [
        row.get("source_id") for row in summary_sources if isinstance(row, dict)
    ]
    if len(summary_source_ids) != len(source_ids) or set(summary_source_ids) != source_ids:
        raise ValueError("SOURCE_ASSET_SUMMARY_SOURCES_INVALID")
    for source_id in source_ids:
        source_assets = [asset for asset in all_assets if asset["source_id"] == source_id]
        source_summary = next(row for row in summary_sources if row.get("source_id") == source_id)
        expected_source_totals = {
            "asset_count": len(source_assets),
            "unique_content_count": len({asset["sha256"] for asset in source_assets}),
            "mapped_canvas_count": sum(asset.get("canvas_id") is not None for asset in source_assets),
        }
        if any(
            source_summary.get(field) != value
            for field, value in expected_source_totals.items()
        ):
            raise ValueError(f"SOURCE_ASSET_SUMMARY_SOURCE_TOTALS_INVALID:{source_id}")


def _load_authority(
    *,
    repository_root: Path,
    source_mount: Path,
    asset_root: Path,
    config_path: Path,
    register_path: Path,
    config: ComparativeQueueConfig,
) -> _Authority:
    repository_root = repository_root.resolve()
    source_mount = source_mount.resolve()
    asset_root = asset_root.resolve()
    config_path = config_path.resolve()
    register_path = register_path.resolve()
    if not repository_root.is_dir():
        raise ValueError("REPOSITORY_ROOT_MISSING")
    if not source_mount.is_dir():
        raise ValueError("SOURCE_MOUNT_MISSING")
    if not asset_root.is_dir() or not _inside(asset_root, repository_root):
        raise ValueError("SOURCE_ASSET_ROOT_OUTSIDE_REPOSITORY")
    if not config_path.is_file() or not _inside(config_path, asset_root):
        raise ValueError("SOURCE_CONFIG_MISSING_OR_OUTSIDE_ASSET_ROOT")
    if not register_path.is_file() or not _inside(register_path, asset_root):
        raise ValueError("SOURCE_REGISTER_MISSING_OR_OUTSIDE_ASSET_ROOT")

    config_payload = _read_json(config_path)
    register_payload = _read_json(register_path)
    if not isinstance(config_payload, dict) or not isinstance(register_payload, dict):
        raise ValueError("SOURCE_AUTHORITY_MALFORMED")
    source = _unique_source(config_payload.get("sources"), config.source_id, "SOURCE_CONFIG_IDENTITY_INVALID")
    register = _unique_source(register_payload.get("sources"), config.source_id, "SOURCE_REGISTER_IDENTITY_INVALID")
    _require_no_training_authority(source)
    _require_no_training_authority(register)
    _validate_register_metadata(register)
    if source.get("expected_asset_count") != config.expected_asset_count:
        raise ValueError("SOURCE_EXPECTED_ASSET_COUNT_MISMATCH")
    if source.get("registered_source_id") != config.source_id:
        raise ValueError("SOURCE_REGISTERED_ID_MISMATCH")
    if source.get("source_identity_status") != "resolved" or register.get("identity_status") != "resolved":
        raise ValueError("SOURCE_IDENTITY_UNRESOLVED")
    if source.get("local_asset_identity_status") != "resolved_canvas_mapping":
        raise ValueError("SOURCE_LOCAL_IDENTITY_UNRESOLVED")
    if source.get("rights_status") != "public_domain" or register.get("rights_status") != "public_domain":
        raise ValueError("SOURCE_RIGHTS_NOT_PUBLIC_DOMAIN")
    if source.get("training_disposition") != "quarantine_pending_hand_boundary_and_lineage":
        raise ValueError("SOURCE_TRAINING_DISPOSITION_UNSAFE")
    if register.get("training_use") != "quarantined":
        raise ValueError("SOURCE_REGISTER_TRAINING_USE_UNSAFE")
    if not isinstance(source.get("manifest_uri"), str) or not source["manifest_uri"].strip():
        raise ValueError("SOURCE_CONFIG_MANIFEST_URI_INVALID")

    source_subpath = _safe_relative_path(source.get("local_subpath"), "SOURCE_LOCAL_SUBPATH_INVALID")
    source_root = source_mount.joinpath(*source_subpath.parts).resolve()
    if not source_root.is_dir() or not _inside(source_root, source_mount):
        raise ValueError("SOURCE_ROOT_MISSING_OR_OUTSIDE_MOUNT")
    manifest_path = _safe_join(source_root, source.get("manifest_relpath"), "SOURCE_MANIFEST_PATH_INVALID")
    mapping_config = source.get("mapping")
    if not isinstance(mapping_config, dict) or mapping_config.get("local_name_field") != "local_name":
        raise ValueError("SOURCE_MAPPING_CONFIG_INVALID")
    mapping_path = _safe_join(source_root, mapping_config.get("direct_relpath"), "SOURCE_MAPPING_PATH_INVALID")
    acquisition_path = _safe_join(source_root, "meta/acquisition_receipt.json", "SOURCE_ACQUISITION_PATH_INVALID")
    for path, code in (
        (manifest_path, "SOURCE_MANIFEST_MISSING"),
        (mapping_path, "SOURCE_MAPPING_MISSING"),
        (acquisition_path, "SOURCE_ACQUISITION_MISSING"),
    ):
        if not path.is_file():
            raise ValueError(code)

    manifest_sha = _file_sha256(manifest_path)
    mapping_sha = _file_sha256(mapping_path)
    acquisition_file_sha = _file_sha256(acquisition_path)
    if source.get("manifest_sha256") != manifest_sha or register.get("manifest_sha256") != manifest_sha:
        raise ValueError("SOURCE_MANIFEST_SHA256_MISMATCH")
    if register.get("asset_mapping_sha256") != mapping_sha or register.get("page_mapping_sha256") != mapping_sha:
        raise ValueError("SOURCE_MAPPING_SHA256_MISMATCH")

    manifest = _read_json(manifest_path)
    mapping_payload = _read_json(mapping_path)
    acquisition = _read_json(acquisition_path)
    if not isinstance(mapping_payload, list) or not all(isinstance(row, dict) for row in mapping_payload):
        raise ValueError("SOURCE_MAPPING_MALFORMED")
    if not isinstance(acquisition, dict) or not _receipt_valid(acquisition):
        raise ValueError("SOURCE_ACQUISITION_RECEIPT_INVALID")
    if register.get("lineage_sha256") != acquisition.get("receipt_sha256"):
        raise ValueError("SOURCE_ACQUISITION_LINEAGE_MISMATCH")
    if (
        acquisition.get("source_id") != config.source_id
        or acquisition.get("manifest_sha256") != manifest_sha
        or acquisition.get("selection_method") != "complete_manifest"
        or acquisition.get("selected_canvas_count") != config.expected_asset_count
        or acquisition.get("expected_count") != config.expected_asset_count
        or acquisition.get("verified_asset_count") != config.expected_asset_count
        or acquisition.get("downloaded_asset_count", 0) + acquisition.get("reused_asset_count", 0)
        != config.expected_asset_count
        or acquisition.get("failed_asset_count") != 0
        or acquisition.get("failures") != []
    ):
        raise ValueError("SOURCE_ACQUISITION_COUNTS_INVALID")

    canvases = _canvas_sequence(manifest)
    if len(canvases) != config.expected_asset_count or len(mapping_payload) != config.expected_asset_count:
        raise ValueError("SOURCE_CANVAS_MAPPING_COUNT_MISMATCH")
    for ordinal, (canvas, mapping_row) in enumerate(zip(canvases, mapping_payload, strict=True)):
        if (
            canvas.get("@id") != mapping_row.get("canvas_id")
            or canvas.get("label") != mapping_row.get("canvas_label")
            or _manifest_service_id(canvas) != mapping_row.get("image_service_id")
        ):
            raise ValueError(f"SOURCE_MANIFEST_MAPPING_ORDER_MISMATCH:{ordinal}")

    assets_path = asset_root / "comparative_assets.jsonl"
    summary_path = asset_root / "comparative_asset_summary.json"
    duplicate_path = asset_root / "comparative_duplicate_groups.jsonl"
    for path, code in (
        (assets_path, "SOURCE_ASSET_LEDGER_MISSING"),
        (summary_path, "SOURCE_ASSET_SUMMARY_MISSING"),
        (duplicate_path, "SOURCE_DUPLICATE_LEDGER_MISSING"),
    ):
        if not path.is_file():
            raise ValueError(code)
    all_assets = _read_jsonl(assets_path)
    duplicate_rows = _read_jsonl(duplicate_path)
    summary_payload = _read_json(summary_path)
    if not isinstance(summary_payload, dict):
        raise ValueError("SOURCE_ASSET_SUMMARY_MALFORMED")
    _validate_full_asset_ledgers(all_assets, duplicate_rows, summary_payload)
    assets = tuple(row for row in all_assets if row.get("source_id") == config.source_id)
    if len(assets) != config.expected_asset_count:
        raise ValueError("SOURCE_ASSET_LEDGER_COUNT_MISMATCH")
    summary_source = _unique_source(
        summary_payload.get("sources"), config.source_id, "SOURCE_ASSET_SUMMARY_IDENTITY_INVALID"
    )
    _require_no_training_authority(summary_source)
    if (
        summary_source.get("asset_count") != config.expected_asset_count
        or summary_source.get("unique_content_count") != config.expected_asset_count
        or summary_source.get("mapped_canvas_count") != config.expected_asset_count
        or summary_source.get("training_disposition") != "quarantine_pending_hand_boundary_and_lineage"
    ):
        raise ValueError("SOURCE_ASSET_SUMMARY_COUNTS_INVALID")

    mapping_local_names: set[str] = set()
    canvas_ids: set[str] = set()
    image_hashes: set[str] = set()
    asset_ids: set[str] = set()
    assets_by_canvas: dict[str, dict[str, Any]] = {}
    for ledger_ordinal, asset in enumerate(assets):
        if not _receipt_valid(asset):
            raise ValueError(f"SOURCE_ASSET_RECEIPT_INVALID:{ledger_ordinal}")
        _require_no_training_authority(asset)
        if (
            asset.get("registered_source_id") != config.source_id
            or asset.get("source_identity_status") != "resolved"
            or asset.get("local_asset_identity_status") != "resolved_canvas_mapping"
            or asset.get("rights_status") != "public_domain"
            or asset.get("training_disposition") != "quarantine_pending_hand_boundary_and_lineage"
            or asset.get("duplicate_group") is not None
            or asset.get("derivative_of") is not None
            or asset.get("manifest_sha256") != manifest_sha
        ):
            raise ValueError(f"SOURCE_ASSET_STATE_INVALID:{ledger_ordinal}")
        canvas_id = asset.get("canvas_id")
        if not isinstance(canvas_id, str) or canvas_id in assets_by_canvas:
            raise ValueError(f"SOURCE_ASSET_CANVAS_ID_DUPLICATE:{ledger_ordinal}")
        assets_by_canvas[canvas_id] = asset

    ordered_assets: list[dict[str, Any]] = []
    configured_glob = source.get("asset_glob")
    if not isinstance(configured_glob, str) or configured_glob != "img/*.jpg":
        raise ValueError("SOURCE_ASSET_GLOB_INVALID")
    expected_image_paths: set[Path] = set()
    for ordinal, mapping_row in enumerate(mapping_payload):
        local_name = mapping_row.get("local_name")
        canvas_id = mapping_row.get("canvas_id")
        digest = mapping_row.get("sha256")
        if not isinstance(local_name, str) or Path(local_name).name != local_name:
            raise ValueError(f"SOURCE_MAPPING_LOCAL_NAME_INVALID:{ordinal}")
        if local_name in mapping_local_names:
            raise ValueError(f"SOURCE_MAPPING_LOCAL_NAME_DUPLICATE:{ordinal}")
        if not isinstance(canvas_id, str) or canvas_id in canvas_ids:
            raise ValueError(f"SOURCE_MAPPING_CANVAS_ID_DUPLICATE:{ordinal}")
        if not isinstance(digest, str) or _SHA256.fullmatch(digest) is None or digest in image_hashes:
            raise ValueError(f"SOURCE_MAPPING_IMAGE_SHA256_INVALID_OR_DUPLICATE:{ordinal}")
        mapping_local_names.add(local_name)
        canvas_ids.add(canvas_id)
        image_hashes.add(digest)
        image_path = _safe_join(source_root, f"img/{local_name}", f"SOURCE_ASSET_PATH_INVALID:{ordinal}")
        expected_image_paths.add(image_path)
        if not image_path.is_file():
            raise ValueError(f"SOURCE_ASSET_MISSING:{ordinal}")
        actual_size = image_path.stat().st_size
        actual_sha = _file_sha256(image_path)
        if actual_size != mapping_row.get("byte_length"):
            raise ValueError(f"SOURCE_ASSET_BYTE_LENGTH_MISMATCH:{ordinal}")
        if actual_sha != digest:
            raise ValueError(f"SOURCE_ASSET_SHA256_MISMATCH:{ordinal}")
        try:
            with Image.open(image_path) as image:
                width, height = image.size
                image.verify()
        except (OSError, ValueError) as error:
            raise ValueError(f"SOURCE_ASSET_IMAGE_INVALID:{ordinal}") from error
        if width != mapping_row.get("width") or height != mapping_row.get("height"):
            raise ValueError(f"SOURCE_ASSET_DIMENSION_MISMATCH:{ordinal}")
        asset = assets_by_canvas.get(canvas_id)
        if asset is None:
            raise ValueError(f"SOURCE_ASSET_LEDGER_JOIN_MISSING:{ordinal}")
        expected_relpath = (source_subpath / "img" / local_name).as_posix()
        if (
            asset.get("local_relpath") != expected_relpath
            or asset.get("sha256") != digest
            or asset.get("byte_length") != actual_size
            or asset.get("canvas_label") != mapping_row.get("canvas_label")
            or asset.get("source_label") != mapping_row.get("source_label")
            or asset.get("image_service_id") != mapping_row.get("image_service_id")
        ):
            raise ValueError(f"SOURCE_ASSET_LEDGER_JOIN_MISMATCH:{ordinal}")
        asset_id = asset.get("asset_id")
        if not isinstance(asset_id, str) or asset_id in asset_ids:
            raise ValueError(f"SOURCE_ASSET_ID_INVALID_OR_DUPLICATE:{ordinal}")
        asset_ids.add(asset_id)
        ordered_assets.append(asset)
    actual_image_paths = {path.resolve() for path in source_root.glob(configured_glob) if path.is_file()}
    if actual_image_paths != expected_image_paths:
        raise ValueError("SOURCE_ASSET_FILE_SET_MISMATCH")

    authority_projection = {
        "schema": QUEUE_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "source_id": config.source_id,
        "expected_asset_count": config.expected_asset_count,
        "source_config_file_sha256": _file_sha256(config_path),
        "source_config_record_sha256": _value_sha256(source),
        "source_register_file_sha256": _file_sha256(register_path),
        "source_register_record_sha256": _value_sha256(register),
        "comparative_assets_file_sha256": _file_sha256(assets_path),
        "comparative_asset_summary_file_sha256": _file_sha256(summary_path),
        "comparative_duplicate_groups_file_sha256": _file_sha256(duplicate_path),
        "manifest_file_sha256": manifest_sha,
        "mapping_file_sha256": mapping_sha,
        "acquisition_file_sha256": acquisition_file_sha,
        "acquisition_receipt_sha256": acquisition["receipt_sha256"],
        "rights_status": register["rights_status"],
        "rights_locator": register.get("rights_locator"),
        "ordering_authority": "saved_iiif_canvas_mapping_sequence.v1",
        "training_authority_state": "absent_quarantined",
    }
    _validate_mavrov_trust_anchor(
        config,
        source=source,
        register=register,
        authority_projection=authority_projection,
    )
    return _Authority(
        source=source,
        register=register,
        summary_source=summary_source,
        mapping=tuple(mapping_payload),
        assets=tuple(ordered_assets),
        source_root=source_root,
        authority_projection=authority_projection,
    )


def _build_bundle(
    authority: _Authority,
    config: ComparativeQueueConfig,
    *,
    provenance_override: dict[str, Any] | None = None,
) -> HandBoundaryQueueBundle:
    queue_id = "sha256:" + _domain_sha256("zfd.comparative_hand_queue.v1", authority.authority_projection)
    item_ids: list[str] = []
    base_items: list[dict[str, Any]] = []
    for ordinal, (mapping_row, asset) in enumerate(zip(authority.mapping, authority.assets, strict=True)):
        item = {
            "queue_id": queue_id,
            "source_id": config.source_id,
            "ordinal": ordinal,
            "asset_id": asset["asset_id"],
            "asset_receipt_sha256": asset["receipt_sha256"],
            "mapping_entry_sha256": _value_sha256(mapping_row),
            "canvas_id": mapping_row["canvas_id"],
            "canvas_label": mapping_row["canvas_label"],
            "image_sha256": mapping_row["sha256"],
            "byte_length": mapping_row["byte_length"],
            "width": mapping_row["width"],
            "height": mapping_row["height"],
            "local_relpath": f"img/{mapping_row['local_name']}",
            "lineage_root_id": asset["lineage_root_id"],
        }
        item_id = "sha256:" + _domain_sha256("zfd.comparative_hand_queue_item.v1", item)
        item_ids.append(item_id)
        base_items.append(item)

    rows: list[dict[str, Any]] = []
    for ordinal, item in enumerate(base_items):
        payload = {
            "schema": QUEUE_ROW_SCHEMA,
            "schema_version": SCHEMA_VERSION,
            **item,
            "queue_item_id": item_ids[ordinal],
            "previous_queue_item_id": item_ids[ordinal - 1] if ordinal else None,
            "next_queue_item_id": item_ids[ordinal + 1] if ordinal + 1 < len(item_ids) else None,
            "boundary_before_state": "manuscript_start" if ordinal == 0 else "unresolved_unreviewed",
            "hand_identity_state": "unknown_unreviewed",
            "hand_id": None,
            "line_annotation_state": "not_started",
            "hand_boundary_sha256": None,
            "line_annotation_sha256": None,
            "split_assignment_state": "blocked_unknown_hand",
            "split_lineage_sha256": None,
            "review_state": "unreviewed",
            "diplomatic_label_count": 0,
            "semantic_authority_count": 0,
            "inherited_text_used": False,
            "training_disposition": "quarantine",
            "training_eligible": False,
            "training_promotion_allowed": False,
        }
        rows.append(_receipt(payload))

    pilot_projection = {
        "queue_id": queue_id,
        "selection_rule_id": config.selection_rule_id,
        "pair_indices": [list(pair) for pair in config.pilot_pairs],
    }
    pilot_id = "sha256:" + _domain_sha256("zfd.comparative_hand_pair_pilot.v1", pilot_projection)
    pilot: list[dict[str, Any]] = []
    for pilot_ordinal, (left, right) in enumerate(config.pilot_pairs):
        task_projection = {
            "pilot_id": pilot_id,
            "pilot_ordinal": pilot_ordinal,
            "left_queue_item_id": item_ids[left],
            "right_queue_item_id": item_ids[right],
        }
        task_id = "sha256:" + _domain_sha256("zfd.comparative_hand_pair_task.v1", task_projection)
        payload = {
            "schema": PILOT_ROW_SCHEMA,
            "schema_version": SCHEMA_VERSION,
            "pilot_id": pilot_id,
            "pair_task_id": task_id,
            "pilot_ordinal": pilot_ordinal,
            "selection_rule_id": config.selection_rule_id,
            "left_ordinal": left,
            "right_ordinal": right,
            "left_queue_item_id": item_ids[left],
            "right_queue_item_id": item_ids[right],
            "left_asset_id": rows[left]["asset_id"],
            "right_asset_id": rows[right]["asset_id"],
            "left_canvas_id": rows[left]["canvas_id"],
            "right_canvas_id": rows[right]["canvas_id"],
            "left_image_sha256": rows[left]["image_sha256"],
            "right_image_sha256": rows[right]["image_sha256"],
            "left_local_relpath": rows[left]["local_relpath"],
            "right_local_relpath": rows[right]["local_relpath"],
            "review_state": "unreviewed",
            "boundary_decision": None,
            "palaeographic_observation_authority": "absent",
            "named_hand_authority": "absent",
            "whole_manuscript_boundary_authority_allowed": False,
            "training_disposition": "quarantine",
            "training_promotion_allowed": False,
            "inherited_text_used": False,
        }
        pilot.append(_receipt(payload))

    if provenance_override is None:
        git_commit, git_dirty = _git_state()
        provenance = {
            "implementation_sha256": _implementation_sha256(),
            "implementation_git_commit": git_commit,
            "implementation_git_worktree_dirty": git_dirty,
        }
    else:
        provenance = {
            "implementation_sha256": provenance_override.get("implementation_sha256"),
            "implementation_git_commit": provenance_override.get("implementation_git_commit"),
            "implementation_git_worktree_dirty": provenance_override.get("implementation_git_worktree_dirty"),
        }
    if (
        provenance["implementation_git_commit"] is not None
        and provenance["implementation_git_worktree_dirty"] is False
    ):
        implementation_provenance_status = "clean_reachable_commit"
    elif (
        provenance["implementation_git_commit"] is None
        and provenance["implementation_git_worktree_dirty"] is None
    ):
        implementation_provenance_status = "unversioned_current_bytes"
    else:
        implementation_provenance_status = "blocked_dirty_or_malformed"
    summary_payload = {
        "schema": QUEUE_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "queue_id": queue_id,
        "pilot_id": pilot_id,
        "source_id": config.source_id,
        "authority": authority.authority_projection,
        **provenance,
        "implementation_provenance_status": implementation_provenance_status,
        "asset_count": len(rows),
        "queue_row_count": len(rows),
        "queue_rows_sha256": sha256(_jsonl_bytes(rows)).hexdigest(),
        "first_queue_item_id": item_ids[0],
        "last_queue_item_id": item_ids[-1],
        "possible_adjacent_boundary_count": len(rows) - 1,
        "unresolved_boundary_count": len(rows) - 1,
        "pilot_pair_count": len(pilot),
        "pilot_pairs": [list(pair) for pair in config.pilot_pairs],
        "pilot_selection_rule_id": config.selection_rule_id,
        "pilot_rows_sha256": sha256(_jsonl_bytes(pilot)).hexdigest(),
        "human_observation_count": 0,
        "adjudicated_boundary_count": 0,
        "unknown_hand_asset_count": len(rows),
        "line_annotated_asset_count": 0,
        "split_assigned_asset_count": 0,
        "training_ready_asset_count": 0,
        "hand_boundary_sha256": None,
        "line_annotation_sha256": None,
        "split_lineage_sha256": None,
        "training_promotion_allowed": False,
        "hand_boundary_authority_complete": False,
        "line_annotation_authority_complete": False,
        "split_lineage_authority_complete": False,
        "ocr_accuracy_claim_allowed": False,
        "translation_claim_allowed": False,
        "provenance_claim_allowed": False,
        "workflow_status": "queue_created_review_not_started",
        "inherited_text_used": False,
    }
    return HandBoundaryQueueBundle(rows=rows, pilot=pilot, summary=_receipt(summary_payload))


def build_hand_boundary_queue(
    *,
    repository_root: str | Path,
    source_mount: str | Path,
    asset_root: str | Path,
    config_path: str | Path,
    register_path: str | Path,
    config: ComparativeQueueConfig = ComparativeQueueConfig(),
) -> HandBoundaryQueueBundle:
    """Build a deterministic, fully quarantined review queue from source pixels."""

    authority = _load_authority(
        repository_root=Path(repository_root),
        source_mount=Path(source_mount),
        asset_root=Path(asset_root),
        config_path=Path(config_path),
        register_path=Path(register_path),
        config=config,
    )
    return _build_bundle(authority, config)


def _validate_implementation_provenance(summary: dict[str, Any], repository_root: Path) -> list[str]:
    errors: list[str] = []
    implementation_sha = summary.get("implementation_sha256")
    if not isinstance(implementation_sha, str) or _SHA256.fullmatch(implementation_sha) is None:
        return ["IMPLEMENTATION_SHA256_INVALID"]
    commit = summary.get("implementation_git_commit")
    dirty = summary.get("implementation_git_worktree_dirty")
    if (commit is None) != (dirty is None):
        return ["IMPLEMENTATION_GIT_PROVENANCE_TUPLE_INVALID"]
    if commit is None:
        if _git_state() != (None, None):
            return ["IMPLEMENTATION_GIT_PROVENANCE_ERASED"]
        try:
            if implementation_sha != _implementation_sha256():
                errors.append("IMPLEMENTATION_HASH_MISMATCH")
        except (OSError, ValueError):
            errors.append("IMPLEMENTATION_HASH_UNREADABLE")
        return errors
    if not isinstance(dirty, bool):
        return ["IMPLEMENTATION_GIT_PROVENANCE_TUPLE_INVALID"]
    if dirty:
        return ["IMPLEMENTATION_WORKTREE_DIRTY"]
    try:
        historical = _historical_implementation_sha256(repository_root.resolve(), commit)
    except (OSError, subprocess.CalledProcessError, ValueError):
        errors.append("IMPLEMENTATION_GIT_PROVENANCE_INVALID")
    else:
        if historical != implementation_sha:
            errors.append("IMPLEMENTATION_HASH_MISMATCH")
    return errors


def validate_hand_boundary_queue(
    bundle: HandBoundaryQueueBundle,
    *,
    repository_root: str | Path,
    source_mount: str | Path,
    asset_root: str | Path,
    config_path: str | Path,
    register_path: str | Path,
    config: ComparativeQueueConfig = ComparativeQueueConfig(),
) -> tuple[str, ...]:
    """Rehash every authority and compare the queue to a fresh pixel-bound build."""

    errors: list[str] = []
    if not isinstance(bundle, HandBoundaryQueueBundle):
        return ("QUEUE_BUNDLE_TYPE_INVALID",)
    for ordinal, row in enumerate(bundle.rows):
        if not isinstance(row, dict) or not _receipt_valid(row):
            errors.append(f"QUEUE_ROW_RECEIPT_HASH_MISMATCH:{ordinal}")
    for ordinal, row in enumerate(bundle.pilot):
        if not isinstance(row, dict) or not _receipt_valid(row):
            errors.append(f"PILOT_ROW_RECEIPT_HASH_MISMATCH:{ordinal}")
    if not isinstance(bundle.summary, dict) or not _receipt_valid(bundle.summary):
        errors.append("QUEUE_SUMMARY_RECEIPT_HASH_MISMATCH")
    else:
        errors.extend(_validate_implementation_provenance(bundle.summary, Path(repository_root)))

    try:
        authority = _load_authority(
            repository_root=Path(repository_root),
            source_mount=Path(source_mount),
            asset_root=Path(asset_root),
            config_path=Path(config_path),
            register_path=Path(register_path),
            config=config,
        )
        expected = _build_bundle(authority, config, provenance_override=bundle.summary)
    except (KeyError, OSError, TypeError, ValueError) as error:
        errors.append(str(error))
        return tuple(dict.fromkeys(errors))
    if (
        _jsonl_bytes(bundle.rows) != _jsonl_bytes(expected.rows)
        or _jsonl_bytes(bundle.pilot) != _jsonl_bytes(expected.pilot)
        or _canonical_bytes(bundle.summary) != _canonical_bytes(expected.summary)
    ):
        errors.append("QUEUE_RECOMPUTE_MISMATCH")
    return tuple(dict.fromkeys(errors))


__all__ = [
    "ComparativeQueueConfig",
    "HandBoundaryQueueBundle",
    "MAVROV_ASSET_COUNT",
    "MAVROV_PILOT_PAIRS",
    "MAVROV_SOURCE_ID",
    "build_hand_boundary_queue",
    "validate_hand_boundary_queue",
]
