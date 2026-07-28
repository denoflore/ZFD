"""Failed acquisition attempts must leave no ambiguous partial files."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from PIL import Image

from zfd_image_native import acquire as acquisition
from zfd_image_native.io import sha256_file
from zfd_image_native.manifest import build_page_manifest


ROOT = Path(__file__).resolve().parents[2]
OFFICIAL_MAP = ROOT / "06_Pipelines" / "glagolitic_ocr" / "data" / "folio_iiif_map.json"


def _registered_page(page, target: Path, *, width: int = 10, height: int = 10):
    return replace(
        page,
        image_path=str(target.resolve()),
        image_sha256=sha256_file(target),
        width=width,
        height=height,
        mime_type="image/jpeg",
        acquisition_status="verified",
    )


def test_arbitrary_existing_iiif_filename_is_never_reused(
    monkeypatch, tmp_path: Path
) -> None:
    page = build_page_manifest(OFFICIAL_MAP)[0]
    target = tmp_path / f"{page.iiif_id}.jpg"
    Image.new("RGB", (10, 10), "red").save(target, format="JPEG")
    original = target.read_bytes()
    monkeypatch.setattr(
        acquisition,
        "urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("network called")),
    )

    result = acquisition.acquire_pages([page], tmp_path)

    assert result.failed == 1
    assert result.receipts[0].disposition == "acquisition_failed"
    assert result.receipts[0].error == f"Existing target lacks verified authority: {page.page_id}"
    assert target.read_bytes() == original


def test_existing_file_with_matching_hash_and_wrong_metadata_fails_closed(
    monkeypatch, tmp_path: Path
) -> None:
    page = build_page_manifest(OFFICIAL_MAP)[0]
    target = tmp_path / f"{page.iiif_id}.jpg"
    Image.new("RGB", (10, 10), "white").save(target, format="JPEG")
    page = _registered_page(page, target, width=11)
    monkeypatch.setattr(
        acquisition,
        "urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("network called")),
    )

    result = acquisition.acquire_pages([page], tmp_path)

    assert result.failed == 1
    assert result.receipts[0].error == f"Registered image dimensions mismatch: {page.page_id}"


def test_existing_registered_target_is_reused_without_network(
    monkeypatch, tmp_path: Path
) -> None:
    page = build_page_manifest(OFFICIAL_MAP)[0]
    target = tmp_path / f"{page.iiif_id}.jpg"
    Image.new("RGB", (10, 10), "white").save(target, format="JPEG")
    page = _registered_page(page, target)
    monkeypatch.setattr(
        acquisition,
        "urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("network called")),
    )

    result = acquisition.acquire_pages([page], tmp_path)

    assert result.failed == 0
    assert result.receipts[0].disposition == "reused_verified"
    assert result.pages[0] == page


def test_failed_overwrite_removes_partial_file_and_preserves_verified_target(
    monkeypatch, tmp_path: Path
) -> None:
    page = build_page_manifest(OFFICIAL_MAP)[0]
    target = tmp_path / f"{page.iiif_id}.jpg"
    Image.new("RGB", (10, 10), "white").save(target, format="JPEG")
    page = _registered_page(page, target)
    original = target.read_bytes()

    class Headers:
        @staticmethod
        def get_content_type() -> str:
            return "image/jpeg"

    class Response:
        headers = Headers()

        def __enter__(self):
            return self

        def __exit__(self, *_args) -> None:
            return None

        @staticmethod
        def read() -> bytes:
            return b"invalid jpeg"

        @staticmethod
        def geturl() -> str:
            return "https://example.invalid/invalid.jpg"

    monkeypatch.setattr(acquisition, "urlopen", lambda request, timeout: Response())

    result = acquisition.acquire_pages([page], tmp_path, overwrite=True)

    assert result.failed == 1
    assert target.read_bytes() == original
    assert not target.with_suffix(".jpg.part").exists()
