"""Checksum verified acquisition for quarantined comparative model files."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import os
from pathlib import Path
import tempfile
from typing import Any, ContextManager
from urllib.parse import quote, unquote, urlparse, urlunparse
from urllib.request import Request, urlopen

from .io import canonical_json, read_json, sha256_file
from .model_registry import validate_model_registry


_BUFFER_SIZE = 1024 * 1024
_LANE = "quarantined_comparative_model_acquisition"


@dataclass(frozen=True)
class ModelAcquisitionSummary:
    model_count: int
    file_count: int
    verified_file_count: int
    failed_file_count: int
    receipt_path: Path
    receipt_sha256: str


@dataclass(frozen=True)
class _PreparedFile:
    register_row: dict[str, Any]
    cache_relpath: str
    target: Path
    request_uri: str


class ModelFileVerificationError(ValueError):
    """Downloaded bytes did not match the immutable register identity."""


def _value_sha256(value: dict[str, Any]) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _open_url(uri: str, timeout_seconds: float) -> ContextManager[Any]:
    request = Request(uri, headers={"User-Agent": "ZFD-image-native/0.1"})
    return urlopen(request, timeout=timeout_seconds)


def _registered_file_uri(model: dict[str, Any], file_row: dict[str, Any]) -> str:
    acquisition_uri = str(model["acquisition_uri"])
    revision = str(model["pinned_revision"])
    name = file_row.get("name")
    if (
        not isinstance(name, str)
        or not name
        or name in {".", ".."}
        or Path(name).name != name
        or "/" in name
        or "\\" in name
    ):
        raise ValueError(f"MODEL_FILE_NAME_INVALID:{model['model_id']}:{name}")

    parsed = urlparse(acquisition_uri)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"MODEL_ACQUISITION_URI_NOT_HTTPS:{model['model_id']}")
    if unquote(Path(parsed.path).name) == name:
        return acquisition_uri

    parts = [part for part in parsed.path.split("/") if part]
    if parsed.netloc.lower() == "huggingface.co" and "tree" in parts:
        tree_index = parts.index("tree")
        if tree_index < 2 or tree_index + 1 >= len(parts):
            raise ValueError(f"MODEL_ACQUISITION_URI_UNSUPPORTED:{model['model_id']}:{name}")
        if parts[tree_index + 1] != revision:
            raise ValueError(f"MODEL_ACQUISITION_REVISION_MISMATCH:{model['model_id']}:{name}")
        resolved_parts = (
            parts[:tree_index]
            + ["resolve", revision]
            + parts[tree_index + 2 :]
            + [quote(name, safe="")]
        )
        return urlunparse(("https", parsed.netloc, "/" + "/".join(resolved_parts), "", "download=true", ""))

    raise ValueError(f"MODEL_ACQUISITION_URI_UNSUPPORTED:{model['model_id']}:{name}")


def _safe_target(repository_root: Path, relpath: str) -> Path:
    candidate = repository_root / relpath
    if candidate.is_symlink():
        raise ValueError(f"MODEL_CACHE_PATH_SYMLINK:{relpath}")
    target = candidate.resolve()
    try:
        target.relative_to(repository_root)
    except ValueError as error:
        raise ValueError(f"MODEL_CACHE_PATH_ESCAPES_ROOT:{relpath}") from error
    return target


def _cached_exact(target: Path, expected_size: int, expected_sha256: str) -> bool:
    if target.is_symlink() or not target.is_file():
        return False
    return target.stat().st_size == expected_size and sha256_file(target) == expected_sha256


def _download_verified(
    uri: str,
    target: Path,
    *,
    expected_size: int,
    expected_sha256: str,
    timeout_seconds: float,
) -> tuple[int, str]:
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, part_name = tempfile.mkstemp(
        dir=target.parent,
        prefix=f".{target.name}.",
        suffix=".part",
    )
    part = Path(part_name)
    observed_size = 0
    digest = sha256()
    final_uri = uri
    try:
        with os.fdopen(descriptor, "wb") as stream:
            with _open_url(uri, timeout_seconds) as response:
                response_uri = response.geturl()
                if isinstance(response_uri, str):
                    final_uri = response_uri
                if urlparse(final_uri).scheme != "https":
                    raise ValueError(f"MODEL_DOWNLOAD_REDIRECT_NOT_HTTPS:{final_uri}")
                while True:
                    block = response.read(_BUFFER_SIZE)
                    if not block:
                        break
                    observed_size += len(block)
                    if observed_size > expected_size:
                        raise ModelFileVerificationError(
                            f"byte length mismatch: expected {expected_size}, observed more than {expected_size}"
                        )
                    digest.update(block)
                    stream.write(block)
            stream.flush()
            os.fsync(stream.fileno())

        observed_sha256 = digest.hexdigest()
        if observed_size != expected_size:
            raise ModelFileVerificationError(
                f"byte length mismatch: expected {expected_size}, observed {observed_size}"
            )
        if observed_sha256 != expected_sha256:
            raise ModelFileVerificationError(
                f"SHA256 mismatch: expected {expected_sha256}, observed {observed_sha256}"
            )
        os.replace(part, target)
        if not _cached_exact(target, expected_size, expected_sha256):
            raise ModelFileVerificationError("atomic replacement did not preserve verified identity")
        return observed_size, observed_sha256
    finally:
        if part.exists():
            part.unlink()


def _portable_register_path(register_path: Path, repository_root: Path) -> str:
    try:
        return register_path.resolve().relative_to(repository_root).as_posix()
    except ValueError:
        return str(register_path.resolve())


def _write_receipt_atomic(path: Path, receipt: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, part_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".part",
    )
    part = Path(part_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(canonical_json(receipt) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(part, path)
    finally:
        if part.exists():
            part.unlink()


def acquire_registered_models(
    register_path: str | Path,
    *,
    repository_root: str | Path,
    receipt_path: str | Path | None = None,
    timeout_seconds: float = 60.0,
) -> ModelAcquisitionSummary:
    """Provision every registered model file without admitting it to the primary lane."""

    register = Path(register_path)
    root = Path(repository_root).resolve()
    if not root.is_dir():
        raise ValueError(f"MODEL_REPOSITORY_ROOT_INVALID:{root}")
    if timeout_seconds <= 0:
        raise ValueError("MODEL_DOWNLOAD_TIMEOUT_INVALID")

    report = validate_model_registry(register)
    if not report.ok:
        raise ValueError(";".join(report.errors))
    payload = read_json(register)

    seen_targets: set[str] = set()
    prepared_models: list[tuple[dict[str, Any], tuple[_PreparedFile, ...]]] = []
    for model in payload["models"]:
        prepared_files: list[_PreparedFile] = []
        for file_row in model["files"]:
            relpath = str(file_row["cache_relpath"])
            target = _safe_target(root, relpath)
            target_key = os.path.normcase(str(target))
            if target_key in seen_targets:
                raise ValueError(f"MODEL_CACHE_PATH_DUPLICATE_GLOBAL:{relpath}")
            seen_targets.add(target_key)
            prepared_files.append(
                _PreparedFile(
                    register_row=file_row,
                    cache_relpath=relpath,
                    target=target,
                    request_uri=_registered_file_uri(model, file_row),
                )
            )
        prepared_models.append((model, tuple(prepared_files)))

    model_receipts: list[dict[str, Any]] = []
    verified_count = 0
    failed_count = 0
    file_count = sum(len(files) for _model, files in prepared_models)

    for model, prepared_files in prepared_models:
        file_receipts: list[dict[str, Any]] = []
        for prepared in prepared_files:
            file_row = prepared.register_row
            relpath = prepared.cache_relpath
            target = prepared.target
            expected_size = int(file_row["byte_length"])
            expected_sha256 = str(file_row["sha256"])
            request_uri = prepared.request_uri
            disposition = "reused_verified"
            verified_size: int | None = expected_size
            verified_sha256: str | None = expected_sha256
            error_type: str | None = None
            error_text: str | None = None
            try:
                if not _cached_exact(target, expected_size, expected_sha256):
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target = _safe_target(root, relpath)
                    verified_size, verified_sha256 = _download_verified(
                        request_uri,
                        target,
                        expected_size=expected_size,
                        expected_sha256=expected_sha256,
                        timeout_seconds=timeout_seconds,
                    )
                    disposition = "downloaded_verified"
                verified_count += 1
            except Exception as error:
                disposition = "acquisition_failed"
                verified_size = None
                verified_sha256 = None
                error_type = type(error).__name__
                error_text = str(error)
                failed_count += 1

            file_receipts.append(
                {
                    "name": file_row["name"],
                    "cache_relpath": relpath.replace("\\", "/"),
                    "request_uri": request_uri,
                    "expected_byte_length": expected_size,
                    "expected_sha256": expected_sha256,
                    "verified_byte_length": verified_size,
                    "verified_sha256": verified_sha256,
                    "disposition": disposition,
                    "error_type": error_type,
                    "error": error_text,
                }
            )

        model_receipts.append(
            {
                "model_id": model["model_id"],
                "model_type": model["model_type"],
                "pinned_revision": model["pinned_revision"],
                "quarantine_status": model["quarantine_status"],
                "primary_lane_allowed": False,
                "diplomatic_label_allowed": False,
                "files": file_receipts,
            }
        )

    output = (
        Path(receipt_path)
        if receipt_path is not None
        else root / "build" / "image_native" / "model_acquisition_receipt.json"
    )
    unsigned_receipt = {
        "schema": "zfd.model_acquisition.v1",
        "schema_version": "1.0.0",
        "lane": _LANE,
        "primary_lane_allowed": False,
        "diplomatic_label_allowed": False,
        "register_path": _portable_register_path(register, root),
        "register_sha256": sha256_file(register),
        "model_count": len(model_receipts),
        "file_count": file_count,
        "verified_file_count": verified_count,
        "failed_file_count": failed_count,
        "models": model_receipts,
    }
    receipt_hash = _value_sha256(unsigned_receipt)
    _write_receipt_atomic(output, {**unsigned_receipt, "receipt_sha256": receipt_hash})
    return ModelAcquisitionSummary(
        model_count=len(model_receipts),
        file_count=file_count,
        verified_file_count=verified_count,
        failed_file_count=failed_count,
        receipt_path=output,
        receipt_sha256=receipt_hash,
    )
