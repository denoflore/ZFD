"""Checksum and lineage registration for comparative manuscript pixels."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any

from .io import canonical_json, read_json, read_jsonl, sha256_file, write_json, write_jsonl
from .models import SourceRecord
from .sources import TRAINING_RIGHTS_STATUSES, validate_sources


SCHEMA_VERSION = "1.0.0"
TRAINING_READY_DISPOSITION = "train"
COMPARATIVE_TRAINING_DISPOSITIONS = frozenset(
    {
        "train",
        "quarantine_pending_canvas_mapping",
        "quarantine_pending_canvas_mapping_and_deduplication",
        "quarantine_pending_three_hand_attribution",
        "quarantine_pending_hand_boundary_and_lineage",
        "quarantine_study_only",
        "quarantine_study_only_no_training_authorization",
        "quarantine_control_only_pending_canvas_mapping",
        "excluded_misidentified",
        "excluded_misidentified_and_contract_restricted",
    }
)


@dataclass(frozen=True)
class ComparativeAssetSummary:
    schema_version: str
    source_count: int
    asset_count: int
    unique_content_count: int
    duplicate_asset_count: int
    duplicate_groups: int
    cross_source_duplicate_groups: int
    mapped_canvas_count: int
    training_ready_asset_count: int
    sources: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class ComparativeValidationReport:
    ok: bool
    asset_count: int
    duplicate_group_count: int
    cross_source_duplicate_groups: int
    training_ready_asset_count: int
    errors: tuple[str, ...]


def _value_sha256(value: Any) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _receipt(row: dict[str, Any]) -> dict[str, Any]:
    payload = {key: value for key, value in row.items() if key != "receipt_sha256"}
    return {**payload, "receipt_sha256": _value_sha256(payload)}


def _receipt_valid(row: dict[str, Any]) -> bool:
    supplied = row.get("receipt_sha256")
    payload = {key: value for key, value in row.items() if key != "receipt_sha256"}
    return isinstance(supplied, str) and supplied == _value_sha256(payload)


def _valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _require_text(source: dict[str, Any], field: str) -> str:
    value = source.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Comparative source {source.get('source_id')} has blank {field}")
    return value


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return [dict(row) for row in csv.DictReader(stream)]


def _iiif_manifest_by_pi(payload: Any) -> dict[str, dict[str, str | None]]:
    found: dict[str, dict[str, str | None]] = {}
    if not isinstance(payload, dict):
        return found
    for sequence in payload.get("sequences", []):
        if not isinstance(sequence, dict):
            continue
        for canvas in sequence.get("canvases", []):
            if not isinstance(canvas, dict):
                continue
            images = canvas.get("images", [])
            if not images or not isinstance(images[0], dict):
                continue
            resource = images[0].get("resource", {})
            if not isinstance(resource, dict):
                continue
            service = resource.get("service", {})
            if not isinstance(service, dict):
                service = {}
            candidates = [str(resource.get("@id", "")), str(service.get("@id", ""))]
            pi = next(
                (
                    match.group(1)
                    for candidate in candidates
                    if (match := re.search(r"[?&]pi=(\d+)", candidate))
                ),
                None,
            )
            if pi:
                found[pi] = {
                    "canvas_id": canvas.get("@id"),
                    "canvas_label": canvas.get("label"),
                    "image_service_id": service.get("@id"),
                }
    return found


def _saved_mapping(
    source: dict[str, Any], source_root: Path, manifest_payload: Any
) -> dict[str, dict[str, Any]]:
    mapping = source.get("mapping")
    if not isinstance(mapping, dict):
        return {}
    direct_relpath = mapping.get("direct_relpath")
    if isinstance(direct_relpath, str) and direct_relpath.strip():
        direct_path = source_root / direct_relpath
        direct_payload = json.loads(direct_path.read_text(encoding="utf-8-sig"))
        if not isinstance(direct_payload, list):
            raise ValueError(f"Comparative direct mapping is malformed: {direct_path}")
        local_name_field = _require_text(mapping, "local_name_field")
        field_names = {
            "source_label": str(mapping.get("source_label_field", "source_label")),
            "request_uri": str(mapping.get("request_uri_field", "request_uri")),
            "canvas_id": str(mapping.get("canvas_id_field", "canvas_id")),
            "canvas_label": str(mapping.get("canvas_label_field", "canvas_label")),
            "image_service_id": str(
                mapping.get("image_service_id_field", "image_service_id")
            ),
            "expected_sha256": str(mapping.get("sha256_field", "sha256")),
            "expected_byte_length": str(mapping.get("byte_length_field", "byte_length")),
        }
        saved: dict[str, dict[str, Any]] = {}
        for row in direct_payload:
            if not isinstance(row, dict):
                raise ValueError(f"Comparative direct mapping row is malformed: {direct_path}")
            local_name = row.get(local_name_field)
            if not isinstance(local_name, str) or not local_name:
                raise ValueError(f"Comparative direct mapping has a blank local name: {direct_path}")
            if local_name in saved:
                raise ValueError(f"Comparative direct mapping repeats {local_name}: {direct_path}")
            saved[local_name] = {
                output_name: row.get(input_name)
                for output_name, input_name in field_names.items()
            }
        return saved
    index_path = source_root / _require_text(mapping, "index_relpath")
    url_path = source_root / _require_text(mapping, "url_csv_relpath")
    index_payload = json.loads(index_path.read_text(encoding="utf-8-sig"))
    if not isinstance(index_payload, list):
        raise ValueError(f"Comparative rename index is malformed: {index_path}")
    local_name_field = _require_text(mapping, "local_name_field")
    source_name_field = _require_text(mapping, "source_name_field")
    label_field = str(mapping.get("url_label_field", "Label"))
    uri_field = str(mapping.get("url_uri_field", "Url"))
    local_to_source: dict[str, str] = {}
    for row in index_payload:
        if not isinstance(row, dict):
            continue
        local_name = row.get(local_name_field)
        source_name = row.get(source_name_field)
        if isinstance(local_name, str) and isinstance(source_name, str):
            local_to_source[local_name] = Path(source_name).stem
    label_to_uri = {
        row[label_field]: row[uri_field]
        for row in _read_csv(url_path)
        if row.get(label_field) and row.get(uri_field)
    }
    manifest_by_pi = _iiif_manifest_by_pi(manifest_payload)
    allow_manifest_mapping = bool(mapping.get("allow_manifest_mapping", True))
    saved: dict[str, dict[str, str | None]] = {}
    for local_name, label in local_to_source.items():
        request_uri = label_to_uri.get(label)
        pi_match = re.search(r"[?&]pi=(\d+)", request_uri or "")
        manifest_item = manifest_by_pi.get(pi_match.group(1), {}) if pi_match and allow_manifest_mapping else {}
        saved[local_name] = {
            "source_label": label,
            "request_uri": request_uri,
            "canvas_id": manifest_item.get("canvas_id"),
            "canvas_label": manifest_item.get("canvas_label"),
            "image_service_id": manifest_item.get("image_service_id"),
        }
    return saved


def register_comparative_assets(
    config_path: str | Path,
    source_mount: str | Path,
    output_root: str | Path,
) -> ComparativeAssetSummary:
    """Register local comparative pixels without embedding machine paths."""

    config = read_json(config_path)
    if not isinstance(config, dict) or not isinstance(config.get("sources"), list):
        raise ValueError("Comparative source configuration is malformed")
    source_mount = Path(source_mount)
    output_root = Path(output_root)
    source_ids: set[str] = set()
    raw_assets: list[dict[str, Any]] = []
    per_source: list[dict[str, Any]] = []

    for source in config["sources"]:
        if not isinstance(source, dict):
            raise ValueError("Comparative source row is malformed")
        source_id = _require_text(source, "source_id")
        if source_id in source_ids:
            raise ValueError(f"Duplicate comparative source_id: {source_id}")
        source_ids.add(source_id)
        local_subpath = _require_text(source, "local_subpath")
        root = source_mount / local_subpath
        if not root.is_dir():
            raise ValueError(f"Comparative source root is missing: {local_subpath}")
        asset_glob = _require_text(source, "asset_glob")
        assets = sorted(path for path in root.glob(asset_glob) if path.is_file())
        expected_asset_count = source.get("expected_asset_count")
        if not isinstance(expected_asset_count, int) or expected_asset_count < 0:
            raise ValueError(f"Comparative source {source_id} has invalid expected_asset_count")
        if len(assets) != expected_asset_count:
            raise ValueError(
                f"Comparative asset count mismatch for {source_id}: expected {expected_asset_count}, got {len(assets)}"
            )
        manifest_path = root / _require_text(source, "manifest_relpath")
        if not manifest_path.is_file():
            raise ValueError(f"Comparative manifest is missing for {source_id}")
        actual_manifest_hash = sha256_file(manifest_path)
        expected_manifest_hash = _require_text(source, "manifest_sha256").lower()
        if actual_manifest_hash != expected_manifest_hash:
            raise ValueError(f"Comparative manifest checksum mismatch for {source_id}")
        manifest_payload = read_json(manifest_path)
        saved_mapping = _saved_mapping(source, root, manifest_payload)
        rights_status = _require_text(source, "rights_status")
        source_identity_status = _require_text(source, "source_identity_status")
        local_identity_status = _require_text(source, "local_asset_identity_status")
        training_disposition = _require_text(source, "training_disposition")
        if training_disposition not in COMPARATIVE_TRAINING_DISPOSITIONS:
            raise ValueError(
                f"Comparative source {source_id} has unknown training disposition: "
                f"{training_disposition}"
            )
        registered_source_id = source.get("registered_source_id", source_id)
        if not isinstance(registered_source_id, str) or not registered_source_id.strip():
            raise ValueError(
                f"Comparative source {source_id} has blank registered_source_id"
            )
        training_hashes = {
            field: source.get(field)
            for field in (
                "hand_boundary_sha256",
                "line_annotation_sha256",
                "split_lineage_sha256",
            )
        }
        if local_identity_status == "resolved_canvas_mapping" and set(saved_mapping) != {
            asset.name for asset in assets
        }:
            raise ValueError(f"Comparative resolved mapping coverage mismatch for {source_id}")
        if training_disposition == TRAINING_READY_DISPOSITION:
            if (
                rights_status not in TRAINING_RIGHTS_STATUSES
                or source_identity_status != "resolved"
                or local_identity_status != "resolved_canvas_mapping"
                or any(not _valid_sha256(value) for value in training_hashes.values())
            ):
                raise ValueError(
                    f"Unsafe training disposition for comparative source {source_id}"
                )
        source_rows: list[dict[str, Any]] = []
        for asset in assets:
            digest = sha256_file(asset)
            mapping = saved_mapping.get(asset.name, {})
            expected_asset_hash = mapping.get("expected_sha256")
            if expected_asset_hash is not None and expected_asset_hash != digest:
                raise ValueError(f"Comparative mapped asset checksum mismatch for {source_id}")
            expected_byte_length = mapping.get("expected_byte_length")
            if expected_byte_length is not None and expected_byte_length != asset.stat().st_size:
                raise ValueError(f"Comparative mapped asset byte length mismatch for {source_id}")
            if local_identity_status == "resolved_canvas_mapping" and not mapping.get("canvas_id"):
                raise ValueError(f"Comparative mapped canvas identity is missing for {source_id}")
            local_relpath = (Path(local_subpath) / asset.relative_to(root)).as_posix()
            row = {
                "schema": "zfd.comparative_asset.v1",
                "schema_version": SCHEMA_VERSION,
                "source_id": source_id,
                "registered_source_id": registered_source_id,
                "asset_id": "sha256:"
                + _value_sha256(
                    {"source_id": source_id, "local_relpath": local_relpath, "sha256": digest}
                ),
                "manifest_uri": _require_text(source, "manifest_uri"),
                "manifest_sha256": actual_manifest_hash,
                "canvas_id": mapping.get("canvas_id"),
                "canvas_label": mapping.get("canvas_label"),
                "image_service_id": mapping.get("image_service_id"),
                "image_request_uri": mapping.get("request_uri"),
                "source_label": mapping.get("source_label"),
                "local_relpath": local_relpath,
                "byte_length": asset.stat().st_size,
                "sha256": digest,
                "lineage_root_id": f"sha256:{digest}",
                "duplicate_group": None,
                "derivative_of": None,
                "source_identity_status": source_identity_status,
                "local_asset_identity_status": local_identity_status,
                "rights_status": rights_status,
                "training_disposition": training_disposition,
                **training_hashes,
                "acquisition_receipt": {
                    "method": "saved_mapping" if mapping else "local_inventory_only",
                    "mapping_state": "canvas_mapped" if mapping.get("canvas_id") else "canvas_unresolved",
                },
            }
            source_rows.append(row)
            raw_assets.append(row)
        per_source.append(
            {
                "source_id": source_id,
                "registered_source_id": registered_source_id,
                "manifest_sha256": actual_manifest_hash,
                "asset_count": len(source_rows),
                "unique_content_count": len({row["sha256"] for row in source_rows}),
                "mapped_canvas_count": sum(row["canvas_id"] is not None for row in source_rows),
                "source_identity_status": source_identity_status,
                "local_asset_identity_status": local_identity_status,
                "rights_status": rights_status,
                "training_disposition": training_disposition,
                **training_hashes,
            }
        )

    by_content: dict[str, list[dict[str, Any]]] = {}
    for row in raw_assets:
        by_content.setdefault(row["sha256"], []).append(row)
    duplicate_rows: list[dict[str, Any]] = []
    for digest, rows in sorted(by_content.items()):
        if len(rows) < 2:
            continue
        duplicate_group = f"sha256:{_value_sha256({'content_sha256': digest})}"
        for row in rows:
            row["duplicate_group"] = duplicate_group
        source_set = sorted({row["source_id"] for row in rows})
        duplicate_rows.append(
            _receipt(
                {
                    "schema": "zfd.comparative_duplicate_group.v1",
                    "schema_version": SCHEMA_VERSION,
                    "duplicate_group": duplicate_group,
                    "content_sha256": digest,
                    "asset_ids": sorted(row["asset_id"] for row in rows),
                    "source_ids": source_set,
                    "asset_count": len(rows),
                    "cross_source": len(source_set) > 1,
                    "training_disposition": "exclude_duplicate_leakage",
                }
            )
        )
    asset_rows = [_receipt(row) for row in raw_assets]
    summary = ComparativeAssetSummary(
        schema_version=SCHEMA_VERSION,
        source_count=len(source_ids),
        asset_count=len(asset_rows),
        unique_content_count=len(by_content),
        duplicate_asset_count=sum(len(rows) for rows in by_content.values() if len(rows) > 1),
        duplicate_groups=len(duplicate_rows),
        cross_source_duplicate_groups=sum(row["cross_source"] for row in duplicate_rows),
        mapped_canvas_count=sum(row["canvas_id"] is not None for row in raw_assets),
        training_ready_asset_count=sum(
            row["training_disposition"] == TRAINING_READY_DISPOSITION
            for row in raw_assets
        ),
        sources=tuple(per_source),
    )
    write_jsonl(output_root / "comparative_assets.jsonl", asset_rows)
    write_jsonl(output_root / "comparative_duplicate_groups.jsonl", duplicate_rows)
    write_json(output_root / "comparative_asset_summary.json", summary)
    return summary


def validate_comparative_assets(
    output_root: str | Path, source_register: str | Path
) -> ComparativeValidationReport:
    """Validate compact comparative assets, duplicates, and training exclusions."""

    root = Path(output_root)
    errors: list[str] = []
    try:
        assets = read_jsonl(root / "comparative_assets.jsonl")
        groups = read_jsonl(root / "comparative_duplicate_groups.jsonl")
        summary = read_json(root / "comparative_asset_summary.json")
        register_payload = read_json(source_register)
    except (OSError, ValueError) as error:
        return ComparativeValidationReport(False, 0, 0, 0, 0, (str(error),))
    source_by_id: dict[str, SourceRecord] = {}
    source_register_valid = True
    if not isinstance(register_payload, dict) or not isinstance(
        register_payload.get("sources"), list
    ):
        errors.append("SOURCE_REGISTER_MALFORMED")
        source_register_valid = False
    else:
        if register_payload.get("schema_version") != "2.0.0":
            errors.append("SOURCE_REGISTER_SCHEMA_INVALID")
            source_register_valid = False
        try:
            source_records = [
                SourceRecord(**row) for row in register_payload["sources"]
            ]
        except (TypeError, ValueError):
            errors.append("SOURCE_REGISTER_MALFORMED")
            source_register_valid = False
        else:
            source_report = validate_sources(source_records)
            if not source_report.ok:
                source_register_valid = False
                errors.extend(
                    f"SOURCE_REGISTER_INVALID:{issue.code}:{issue.record_id or ''}"
                    for issue in source_report.errors
                )
            source_by_id = {source.source_id: source for source in source_records}
            if len(source_by_id) != len(source_records):
                errors.append("SOURCE_REGISTER_ID_DUPLICATE")
                source_register_valid = False
    asset_by_id: dict[str, dict[str, Any]] = {}
    content_groups: dict[str, list[dict[str, Any]]] = {}
    training_ready_ids: set[str] = set()
    for row in assets:
        asset_id = row.get("asset_id")
        if not isinstance(asset_id, str) or not asset_id:
            errors.append("ASSET_ID_MISSING")
            continue
        if asset_id in asset_by_id:
            errors.append(f"ASSET_ID_DUPLICATE:{asset_id}")
        asset_by_id[asset_id] = row
        if not _receipt_valid(row):
            errors.append(f"ASSET_RECEIPT_HASH_MISMATCH:{asset_id}")
        local_relpath = row.get("local_relpath")
        if (
            not isinstance(local_relpath, str)
            or not local_relpath
            or Path(local_relpath).is_absolute()
            or re.match(r"^[A-Za-z]:", local_relpath)
        ):
            errors.append(f"ASSET_PATH_NOT_PORTABLE:{asset_id}")
        digest = row.get("sha256")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            errors.append(f"ASSET_SHA256_INVALID:{asset_id}")
        else:
            content_groups.setdefault(digest, []).append(row)
        disposition = row.get("training_disposition")
        if disposition not in COMPARATIVE_TRAINING_DISPOSITIONS:
            errors.append(f"TRAINING_DISPOSITION_INVALID:{asset_id}")
        registered_source_id = row.get("registered_source_id")
        source = source_by_id.get(registered_source_id)
        if source is None:
            errors.append(f"SOURCE_REGISTER_JOIN_MISSING:{asset_id}")
        else:
            if source.manifest_sha256 != row.get("manifest_sha256"):
                errors.append(f"SOURCE_REGISTER_MANIFEST_MISMATCH:{asset_id}")
            if source.rights_status != row.get("rights_status"):
                errors.append(f"SOURCE_REGISTER_RIGHTS_MISMATCH:{asset_id}")

        if disposition == TRAINING_READY_DISPOSITION:
            training_errors: list[str] = []
            if not source_register_valid:
                training_errors.append("SOURCE_REGISTER_INVALID")
            if (
                row.get("rights_status") not in TRAINING_RIGHTS_STATUSES
                or row.get("source_identity_status") != "resolved"
                or row.get("local_asset_identity_status")
                != "resolved_canvas_mapping"
                or row.get("canvas_id") is None
            ):
                training_errors.append("ASSET_BOUNDARY")
            if row.get("duplicate_group") is not None:
                training_errors.append("DUPLICATE_LEAKAGE")
            if source is None or source.training_use != "train":
                training_errors.append("SOURCE_DISPOSITION")
            elif source.rights_status not in TRAINING_RIGHTS_STATUSES:
                training_errors.append("SOURCE_RIGHTS")
            for field in (
                "hand_boundary_sha256",
                "line_annotation_sha256",
                "split_lineage_sha256",
            ):
                value = row.get(field)
                if not _valid_sha256(value):
                    training_errors.append(field.upper())
                elif source is None or getattr(source, field) != value:
                    training_errors.append(field.upper() + "_SOURCE_MISMATCH")
            if training_errors:
                errors.append(
                    f"UNSAFE_TRAINING_ASSET:{asset_id}:"
                    + ",".join(training_errors)
                )
            else:
                training_ready_ids.add(asset_id)

    group_by_id: dict[str, dict[str, Any]] = {}
    for row in groups:
        group_id = row.get("duplicate_group")
        if not isinstance(group_id, str) or not group_id:
            errors.append("DUPLICATE_GROUP_ID_MISSING")
            continue
        if group_id in group_by_id:
            errors.append(f"DUPLICATE_GROUP_ID_DUPLICATE:{group_id}")
        group_by_id[group_id] = row
        if not _receipt_valid(row):
            errors.append(f"DUPLICATE_GROUP_RECEIPT_HASH_MISMATCH:{group_id}")
        members = [asset_by_id.get(asset_id) for asset_id in row.get("asset_ids", [])]
        if not members or any(member is None for member in members):
            errors.append(f"DUPLICATE_GROUP_ASSET_MISSING:{group_id}")
            continue
        member_rows = [member for member in members if member is not None]
        if len({member.get("sha256") for member in member_rows}) != 1:
            errors.append(f"DUPLICATE_GROUP_CONTENT_MISMATCH:{group_id}")
        if any(member.get("duplicate_group") != group_id for member in member_rows):
            errors.append(f"DUPLICATE_GROUP_BACKLINK_MISMATCH:{group_id}")
        if sorted({member.get("source_id") for member in member_rows}) != row.get("source_ids"):
            errors.append(f"DUPLICATE_GROUP_SOURCE_MISMATCH:{group_id}")
    for digest, rows in content_groups.items():
        expected_group = len(rows) > 1
        assigned_groups = {row.get("duplicate_group") for row in rows}
        if expected_group and (None in assigned_groups or len(assigned_groups) != 1):
            errors.append(f"DUPLICATE_CONTENT_UNGROUPED:{digest}")
        if not expected_group and assigned_groups != {None}:
            errors.append(f"UNIQUE_CONTENT_GROUPED:{digest}")

    cross_source = sum(row.get("cross_source") is True for row in groups)
    training_ready = len(training_ready_ids)
    expected_summary = {
        "asset_count": len(assets),
        "unique_content_count": len(content_groups),
        "duplicate_asset_count": sum(len(rows) for rows in content_groups.values() if len(rows) > 1),
        "duplicate_groups": len(groups),
        "cross_source_duplicate_groups": cross_source,
        "mapped_canvas_count": sum(row.get("canvas_id") is not None for row in assets),
        "training_ready_asset_count": training_ready,
    }
    if not isinstance(summary, dict):
        errors.append("COMPARATIVE_SUMMARY_MALFORMED")
    else:
        for field, expected in expected_summary.items():
            if summary.get(field) != expected:
                errors.append(f"COMPARATIVE_SUMMARY_{field.upper()}_MISMATCH")
    return ComparativeValidationReport(
        ok=not errors,
        asset_count=len(assets),
        duplicate_group_count=len(groups),
        cross_source_duplicate_groups=cross_source,
        training_ready_asset_count=training_ready,
        errors=tuple(errors),
    )
