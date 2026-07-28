"""Pinned model metadata and quarantine validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

from .io import read_json, sha256_file


_SHA256 = re.compile(r"[0-9a-f]{64}")
_MODEL_TYPES = {"segmentation", "recognition"}
_QUARANTINE_STATES = {
    "comparative_only_unvalidated_on_voynich",
    "comparative_only_unvalidated_on_registered_hands",
}


@dataclass(frozen=True)
class ModelRegistryReport:
    ok: bool
    model_count: int
    cached_file_count: int
    errors: tuple[str, ...]


def _text(row: dict[str, Any], field: str, model_id: str, errors: list[str]) -> str | None:
    value = row.get(field)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"MODEL_FIELD_MISSING:{model_id}:{field}")
        return None
    return value


def validate_model_registry(
    register_path: str | Path,
    *,
    repository_root: str | Path | None = None,
    require_cache: bool = False,
) -> ModelRegistryReport:
    """Validate pinned model identity, output boundaries, and optional cached bytes."""

    payload = read_json(register_path)
    errors: list[str] = []
    if not isinstance(payload, dict) or not isinstance(payload.get("models"), list):
        return ModelRegistryReport(False, 0, 0, ("MODEL_REGISTER_MALFORMED",))

    root = Path(repository_root).resolve() if repository_root is not None else None
    model_ids: set[str] = set()
    cached_files = 0
    for row in payload["models"]:
        if not isinstance(row, dict):
            errors.append("MODEL_ROW_MALFORMED")
            continue
        model_id = _text(row, "model_id", "unknown", errors) or "unknown"
        if model_id in model_ids:
            errors.append(f"MODEL_ID_DUPLICATE:{model_id}")
        model_ids.add(model_id)

        for field in (
            "stable_locator",
            "acquisition_uri",
            "pinned_revision",
            "license_spdx",
            "software",
            "output_layer",
        ):
            _text(row, field, model_id, errors)
        if row.get("model_type") not in _MODEL_TYPES:
            errors.append(f"MODEL_TYPE_INVALID:{model_id}")
        if row.get("quarantine_status") not in _QUARANTINE_STATES:
            errors.append(f"MODEL_QUARANTINE_INVALID:{model_id}")
        if row.get("primary_lane_allowed") is not False:
            errors.append(f"MODEL_PRIMARY_LANE_NOT_BLOCKED:{model_id}")
        if row.get("diplomatic_label_allowed") is not False:
            errors.append(f"MODEL_DIPLOMATIC_LABEL_NOT_BLOCKED:{model_id}")

        limitations = row.get("limitations")
        if not isinstance(limitations, list) or not limitations or not all(
            isinstance(item, str) and item.strip() for item in limitations
        ):
            errors.append(f"MODEL_LIMITATIONS_MISSING:{model_id}")
        training_scope = row.get("training_scope")
        if not isinstance(training_scope, dict) or not training_scope.get("sources"):
            errors.append(f"MODEL_TRAINING_SCOPE_MISSING:{model_id}")

        metrics = row.get("reported_metrics")
        if not isinstance(metrics, list):
            errors.append(f"MODEL_REPORTED_METRICS_MALFORMED:{model_id}")
        else:
            for index, metric in enumerate(metrics):
                if not isinstance(metric, dict):
                    errors.append(f"MODEL_REPORTED_METRIC_MALFORMED:{model_id}:{index}")
                    continue
                if metric.get("zfd_held_out") is not False:
                    errors.append(f"MODEL_REPORTED_METRIC_SCOPE_INVALID:{model_id}:{index}")
                if not isinstance(metric.get("source_locator"), str):
                    errors.append(f"MODEL_REPORTED_METRIC_SOURCE_MISSING:{model_id}:{index}")

        files = row.get("files")
        if not isinstance(files, list) or not files:
            errors.append(f"MODEL_FILES_MISSING:{model_id}")
            continue
        seen_paths: set[str] = set()
        for file_row in files:
            if not isinstance(file_row, dict):
                errors.append(f"MODEL_FILE_MALFORMED:{model_id}")
                continue
            relpath = file_row.get("cache_relpath")
            if (
                not isinstance(relpath, str)
                or not relpath
                or Path(relpath).is_absolute()
                or re.match(r"^[A-Za-z]:", relpath)
                or ".." in Path(relpath).parts
            ):
                errors.append(f"MODEL_CACHE_PATH_INVALID:{model_id}")
                continue
            if relpath in seen_paths:
                errors.append(f"MODEL_CACHE_PATH_DUPLICATE:{model_id}:{relpath}")
            seen_paths.add(relpath)
            digest = file_row.get("sha256")
            byte_length = file_row.get("byte_length")
            if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
                errors.append(f"MODEL_FILE_SHA256_INVALID:{model_id}:{relpath}")
            if not isinstance(byte_length, int) or byte_length <= 0:
                errors.append(f"MODEL_FILE_SIZE_INVALID:{model_id}:{relpath}")

            if root is None:
                if require_cache:
                    errors.append(f"MODEL_CACHE_ROOT_MISSING:{model_id}:{relpath}")
                continue
            target = (root / relpath).resolve()
            try:
                target.relative_to(root)
            except ValueError:
                errors.append(f"MODEL_CACHE_PATH_ESCAPES_ROOT:{model_id}:{relpath}")
                continue
            if not target.is_file():
                if require_cache:
                    errors.append(f"MODEL_CACHE_FILE_MISSING:{model_id}:{relpath}")
                continue
            cached_files += 1
            if target.stat().st_size != byte_length:
                errors.append(f"MODEL_CACHE_SIZE_MISMATCH:{model_id}:{relpath}")
            if isinstance(digest, str) and _SHA256.fullmatch(digest):
                if sha256_file(target) != digest:
                    errors.append(f"MODEL_CACHE_SHA256_MISMATCH:{model_id}:{relpath}")

    return ModelRegistryReport(
        ok=not errors,
        model_count=len(model_ids),
        cached_file_count=cached_files,
        errors=tuple(errors),
    )
