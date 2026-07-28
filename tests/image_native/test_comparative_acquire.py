"""Comparative acquisition binds selected edition images to IIIF canvases."""

from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path

from PIL import Image
import pytest

from zfd_image_native import comparative_acquire
from zfd_image_native.io import read_json


def _image_bytes() -> bytes:
    stream = BytesIO()
    Image.new("RGB", (32, 48), "white").save(stream, format="JPEG")
    return stream.getvalue()


def _remote_payloads() -> tuple[str, str, dict[str, tuple[bytes, str]]]:
    manifest_uri = "https://example.invalid/manifest.json"
    selection_uri = "https://example.invalid/edition"
    services = [
        "https://digi.vatlib.it/iiifimage/MSS_Test/Test_0017_fa_0001r.jp2",
        "https://digi.vatlib.it/iiifimage/MSS_Test/Test_0018_fa_0001v.jp2",
    ]
    canvases = []
    for index, service in enumerate(services, start=17):
        canvases.append(
            {
                "@id": f"https://example.invalid/canvas/p{index:04d}",
                "label": "1r" if index == 17 else "1v",
                "images": [{"resource": {"service": {"@id": service}}}],
            }
        )
    manifest = json.dumps({"sequences": [{"canvases": canvases}]}).encode()
    selection = "\n".join(f'<img data-info="{service}/info.json">' for service in services).encode()
    payloads: dict[str, tuple[bytes, str]] = {
        manifest_uri: (manifest, "application/json"),
        selection_uri: (selection, "text/html"),
    }
    image = _image_bytes()
    for service in services:
        payloads[f"{service}/full/2000,/0/default.jpg"] = (image, "image/jpeg")
    return manifest_uri, selection_uri, payloads


def test_acquire_iiif_selection_maps_and_hashes_assets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest_uri, selection_uri, payloads = _remote_payloads()

    def fake_fetch(uri: str, timeout_seconds: float) -> tuple[bytes, str, str]:
        assert timeout_seconds == 60.0
        payload, content_type = payloads[uri]
        return payload, uri, content_type

    monkeypatch.setattr(comparative_acquire, "_fetch", fake_fetch)
    summary = comparative_acquire.acquire_iiif_selection(
        source_id="dated-source",
        manifest_uri=manifest_uri,
        selection_uri=selection_uri,
        output_root=tmp_path,
        expected_count=2,
    )

    mapping = read_json(tmp_path / "meta" / "canvas_mapping.json")
    receipt = read_json(tmp_path / "meta" / "acquisition_receipt.json")
    assert summary.verified_asset_count == 2
    assert summary.failed_asset_count == 0
    assert summary.downloaded_asset_count == 2
    assert sorted(path.name for path in (tmp_path / "img").glob("*.jpg")) == [
        "p0017_0001r.jpg",
        "p0018_0001v.jpg",
    ]
    assert [row["canvas_id"] for row in mapping] == [
        "https://example.invalid/canvas/p0017",
        "https://example.invalid/canvas/p0018",
    ]
    assert all(len(row["sha256"]) == 64 for row in mapping)
    assert receipt["verified_asset_count"] == 2
    assert receipt["receipt_sha256"] == summary.receipt_sha256
    receipt_payload = {
        key: value for key, value in receipt.items() if key != "receipt_sha256"
    }
    canonical_payload = json.dumps(
        receipt_payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    assert receipt["receipt_sha256"] == sha256(canonical_payload.encode("utf-8")).hexdigest()
    assert str(tmp_path) not in json.dumps(receipt)


def test_acquire_iiif_selection_rejects_selection_count_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest_uri, selection_uri, payloads = _remote_payloads()

    def fake_fetch(uri: str, timeout_seconds: float) -> tuple[bytes, str, str]:
        payload, content_type = payloads[uri]
        return payload, uri, content_type

    monkeypatch.setattr(comparative_acquire, "_fetch", fake_fetch)
    with pytest.raises(ValueError, match="count mismatch"):
        comparative_acquire.acquire_iiif_selection(
            source_id="dated-source",
            manifest_uri=manifest_uri,
            selection_uri=selection_uri,
            output_root=tmp_path,
            expected_count=3,
        )


def test_acquire_complete_iiif_manifest_without_selection_page(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest_uri, _selection_uri, payloads = _remote_payloads()
    payloads.pop(_selection_uri)

    def fake_fetch(uri: str, timeout_seconds: float) -> tuple[bytes, str, str]:
        payload, content_type = payloads[uri]
        return payload, uri, content_type

    monkeypatch.setattr(comparative_acquire, "_fetch", fake_fetch)
    summary = comparative_acquire.acquire_iiif_selection(
        source_id="complete-manifest-source",
        manifest_uri=manifest_uri,
        selection_uri=None,
        output_root=tmp_path,
        expected_count=2,
    )

    receipt = read_json(tmp_path / "meta" / "acquisition_receipt.json")
    mapping = read_json(tmp_path / "meta" / "canvas_mapping.json")
    assert summary.selected_canvas_count == 2
    assert summary.verified_asset_count == 2
    assert receipt["selection_method"] == "complete_manifest"
    assert receipt["selection_uri"] is None
    assert receipt["selection_sha256"] is None
    assert [row["canvas_label"] for row in mapping] == ["1r", "1v"]
