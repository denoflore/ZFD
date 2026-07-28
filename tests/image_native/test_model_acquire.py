"""Registered comparative models are provisioned as verified quarantined bytes."""

from __future__ import annotations

from hashlib import sha256
from io import BytesIO
from pathlib import Path

import pytest

from zfd_image_native.cli import main
from zfd_image_native.io import canonical_json, read_json, write_json
from zfd_image_native import model_acquire


def _file(name: str, relpath: str, payload: bytes) -> dict[str, object]:
    return {
        "name": name,
        "cache_relpath": relpath,
        "byte_length": len(payload),
        "sha256": sha256(payload).hexdigest(),
    }


def _model(
    model_id: str,
    *,
    acquisition_uri: str,
    revision: str,
    model_type: str,
    files: list[dict[str, object]],
) -> dict[str, object]:
    quarantine = (
        "comparative_only_unvalidated_on_voynich"
        if model_type == "segmentation"
        else "comparative_only_unvalidated_on_registered_hands"
    )
    return {
        "model_id": model_id,
        "model_type": model_type,
        "stable_locator": acquisition_uri,
        "acquisition_uri": acquisition_uri,
        "pinned_revision": revision,
        "license_spdx": "Apache-2.0",
        "software": "fixture",
        "output_layer": "comparative_fixture_only",
        "primary_lane_allowed": False,
        "diplomatic_label_allowed": False,
        "quarantine_status": quarantine,
        "training_scope": {"sources": ["fixture"]},
        "reported_metrics": [],
        "limitations": ["fixture"],
        "files": files,
    }


def _register(root: Path) -> tuple[Path, dict[str, bytes]]:
    layout = b"layout-model"
    weights = b"recognition-weights"
    symbols = b"A\nB\n"
    revision = "a" * 40
    direct_uri = "https://example.invalid/models/layout.bin"
    tree_uri = f"https://huggingface.co/example/glagolitic/tree/{revision}"
    payload = {
        "schema_version": "1.0.0",
        "models": [
            _model(
                "layout-model",
                acquisition_uri=direct_uri,
                revision="b" * 40,
                model_type="segmentation",
                files=[_file("layout.bin", "build/vendor/layout.bin", layout)],
            ),
            _model(
                "recognition-model",
                acquisition_uri=tree_uri,
                revision=revision,
                model_type="recognition",
                files=[
                    _file("weights.pt", "build/models/glagolitic/weights.pt", weights),
                    _file("symbols.txt", "build/models/glagolitic/symbols.txt", symbols),
                ],
            ),
        ],
    }
    register = root / "data" / "image_native" / "model_register.json"
    write_json(register, payload)
    remote = {
        direct_uri: layout,
        f"https://huggingface.co/example/glagolitic/resolve/{revision}/weights.pt?download=true": weights,
        f"https://huggingface.co/example/glagolitic/resolve/{revision}/symbols.txt?download=true": symbols,
    }
    return register, remote


class _Response:
    def __init__(self, payload: bytes, uri: str) -> None:
        self._stream = BytesIO(payload)
        self._uri = uri

    def __enter__(self) -> "_Response":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self, size: int = -1) -> bytes:
        return self._stream.read(size)

    def geturl(self) -> str:
        return self._uri


def _mock_network(
    monkeypatch: pytest.MonkeyPatch,
    payloads: dict[str, bytes],
) -> list[str]:
    calls: list[str] = []

    def fake_open(uri: str, timeout_seconds: float) -> _Response:
        assert timeout_seconds == 60.0
        calls.append(uri)
        return _Response(payloads[uri], uri)

    monkeypatch.setattr(model_acquire, "_open_url", fake_open)
    return calls


def _assert_self_hash(receipt: dict[str, object]) -> None:
    supplied = receipt["receipt_sha256"]
    unsigned = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    assert supplied == sha256(canonical_json(unsigned).encode("utf-8")).hexdigest()


def test_acquire_registered_models_verifies_every_file_and_self_hashes_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    register, remote = _register(tmp_path)
    calls = _mock_network(monkeypatch, remote)
    receipt_path = tmp_path / "build" / "image_native" / "model_acquisition.json"

    summary = model_acquire.acquire_registered_models(
        register,
        repository_root=tmp_path,
        receipt_path=receipt_path,
    )

    assert summary.model_count == 2
    assert summary.file_count == 3
    assert summary.verified_file_count == 3
    assert summary.failed_file_count == 0
    assert calls == list(remote)
    receipt = read_json(receipt_path)
    _assert_self_hash(receipt)
    assert receipt["primary_lane_allowed"] is False
    assert receipt["diplomatic_label_allowed"] is False
    assert receipt["lane"] == "quarantined_comparative_model_acquisition"
    assert {row["quarantine_status"] for row in receipt["models"]} == {
        "comparative_only_unvalidated_on_voynich",
        "comparative_only_unvalidated_on_registered_hands",
    }
    assert {
        file_row["disposition"]
        for model_row in receipt["models"]
        for file_row in model_row["files"]
    } == {"downloaded_verified"}
    assert (tmp_path / "build" / "vendor" / "layout.bin").read_bytes() == remote[calls[0]]
    assert not list(tmp_path.rglob("*.part"))


def test_acquire_registered_models_reuses_only_exact_cached_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    register, remote = _register(tmp_path)
    _mock_network(monkeypatch, remote)
    model_acquire.acquire_registered_models(register, repository_root=tmp_path)

    def fail_network(_uri: str, _timeout_seconds: float) -> _Response:
        raise AssertionError("verified cache must not reach the network")

    monkeypatch.setattr(model_acquire, "_open_url", fail_network)
    summary = model_acquire.acquire_registered_models(register, repository_root=tmp_path)
    receipt = read_json(summary.receipt_path)

    assert summary.verified_file_count == 3
    assert {
        file_row["disposition"]
        for model_row in receipt["models"]
        for file_row in model_row["files"]
    } == {"reused_verified"}


def test_acquisition_receipt_does_not_persist_temporary_redirect_uri(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    register, remote = _register(tmp_path)
    direct_uri = "https://example.invalid/models/layout.bin"

    def fake_open(uri: str, timeout_seconds: float) -> _Response:
        assert timeout_seconds == 60.0
        final_uri = (
            "https://signed-cdn.invalid/model?temporary-secret=must-not-persist"
            if uri == direct_uri
            else uri
        )
        return _Response(remote[uri], final_uri)

    monkeypatch.setattr(model_acquire, "_open_url", fake_open)
    summary = model_acquire.acquire_registered_models(register, repository_root=tmp_path)
    receipt_text = Path(summary.receipt_path).read_text(encoding="utf-8")

    assert "temporary-secret" not in receipt_text
    assert "signed-cdn.invalid" not in receipt_text
    assert read_json(summary.receipt_path)["models"][0]["files"][0]["request_uri"] == direct_uri


def test_acquire_registered_models_replaces_tampered_cache_atomically(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    register, remote = _register(tmp_path)
    target = tmp_path / "build" / "vendor" / "layout.bin"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"tampered")
    calls = _mock_network(monkeypatch, remote)

    summary = model_acquire.acquire_registered_models(register, repository_root=tmp_path)

    assert summary.failed_file_count == 0
    assert target.read_bytes() == b"layout-model"
    assert calls[0] == "https://example.invalid/models/layout.bin"
    assert not list(tmp_path.rglob("*.part"))


def test_failed_verification_preserves_existing_target_and_removes_part(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    register, remote = _register(tmp_path)
    target = tmp_path / "build" / "vendor" / "layout.bin"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"existing-tamper")
    remote["https://example.invalid/models/layout.bin"] = b"wrong-download"
    _mock_network(monkeypatch, remote)

    summary = model_acquire.acquire_registered_models(register, repository_root=tmp_path)
    receipt = read_json(summary.receipt_path)
    layout_receipt = receipt["models"][0]["files"][0]

    assert summary.failed_file_count == 1
    assert target.read_bytes() == b"existing-tamper"
    assert layout_receipt["disposition"] == "acquisition_failed"
    assert layout_receipt["verified_sha256"] is None
    assert not list(tmp_path.rglob("*.part"))


def test_acquire_registered_models_refuses_cache_path_escape_before_network(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    register, _remote = _register(tmp_path)
    payload = read_json(register)
    payload["models"][0]["files"][0]["cache_relpath"] = "../escape.bin"
    write_json(register, payload)
    monkeypatch.setattr(
        model_acquire,
        "_open_url",
        lambda *_args: pytest.fail("invalid register must not reach the network"),
    )

    with pytest.raises(ValueError, match="MODEL_CACHE_PATH_INVALID"):
        model_acquire.acquire_registered_models(register, repository_root=tmp_path)

    assert not (tmp_path.parent / "escape.bin").exists()


def test_acquire_registered_models_refuses_primary_lane_model_before_network(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    register, _remote = _register(tmp_path)
    payload = read_json(register)
    payload["models"][0]["primary_lane_allowed"] = True
    write_json(register, payload)
    monkeypatch.setattr(
        model_acquire,
        "_open_url",
        lambda *_args: pytest.fail("unquarantined register must not reach the network"),
    )

    with pytest.raises(ValueError, match="MODEL_PRIMARY_LANE_NOT_BLOCKED"):
        model_acquire.acquire_registered_models(register, repository_root=tmp_path)


def test_global_duplicate_cache_path_is_refused_before_any_network_call(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    register, _remote = _register(tmp_path)
    payload = read_json(register)
    payload["models"][1]["files"][0]["cache_relpath"] = "build/vendor/layout.bin"
    write_json(register, payload)
    network_calls: list[str] = []

    def unexpected_network(uri: str, _timeout_seconds: float) -> _Response:
        network_calls.append(uri)
        raise AssertionError("all registered targets must pass preflight first")

    monkeypatch.setattr(model_acquire, "_open_url", unexpected_network)

    with pytest.raises(ValueError, match="MODEL_CACHE_PATH_DUPLICATE_GLOBAL"):
        model_acquire.acquire_registered_models(register, repository_root=tmp_path)

    assert network_calls == []
    assert not (tmp_path / "build" / "vendor" / "layout.bin").exists()


def test_acquire_models_cli_writes_verified_receipt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    register, remote = _register(tmp_path)
    _mock_network(monkeypatch, remote)
    receipt = tmp_path / "receipt.json"

    exit_code = main(
        [
            "acquire-models",
            "--register",
            str(register),
            "--repository-root",
            str(tmp_path),
            "--receipt",
            str(receipt),
        ]
    )

    assert exit_code == 0
    assert read_json(receipt)["verified_file_count"] == 3
    assert '"failed_file_count":0' in capsys.readouterr().out
