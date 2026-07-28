"""Checksum backed IIIF acquisition for registered manuscript surfaces."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from pathlib import Path
import os
from typing import Iterable
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from PIL import Image

from .io import sha256_file, write_json
from .models import PageRecord


@dataclass(frozen=True)
class AcquisitionReceipt:
    page_id: str
    iiif_id: str
    request_uri: str
    final_uri: str | None
    image_path: str | None
    image_sha256: str | None
    byte_count: int | None
    mime_type: str | None
    width: int | None
    height: int | None
    disposition: str
    error_type: str | None = None
    error: str | None = None


@dataclass(frozen=True)
class AcquisitionResult:
    pages: tuple[PageRecord, ...]
    receipts: tuple[AcquisitionReceipt, ...]

    @property
    def failed(self) -> int:
        return sum(item.disposition == "acquisition_failed" for item in self.receipts)


def _measure(path: Path) -> tuple[int, int, str]:
    with Image.open(path) as image:
        image.load()
        width, height = image.size
        mime_type = Image.MIME.get(image.format or "", "application/octet-stream")
    return width, height, mime_type


def _registered_reuse(
    page: PageRecord,
    target: Path,
    width: int,
) -> tuple[int, int, str, str]:
    """Verify that an existing derivative is the registered page asset."""

    expected_page_id = f"{page.source_id}:iiif:{page.iiif_id}"
    if page.page_id != expected_page_id:
        raise ValueError(f"Registered page identity mismatch: {page.page_id}")
    base_uri = page.iiif_base_uri.rstrip("/")
    if not base_uri or base_uri.rsplit("/", 1)[-1] != page.iiif_id:
        raise ValueError(f"Registered IIIF identity mismatch: {page.page_id}")
    expected_requests = {
        f"{base_uri}/full/{width},/0/default.jpg",
        f"{base_uri}/full/max/0/default.jpg",
    }
    if page.image_request_uri not in expected_requests:
        raise ValueError(f"Registered image request mismatch: {page.page_id}")
    if page.acquisition_status != "verified":
        raise ValueError(f"Existing target lacks verified authority: {page.page_id}")
    if not page.image_path or Path(page.image_path).resolve() != target.resolve():
        raise ValueError(f"Registered image path mismatch: {page.page_id}")
    if not isinstance(page.image_sha256, str) or len(page.image_sha256) != 64:
        raise ValueError(f"Registered image checksum is invalid: {page.page_id}")
    try:
        int(page.image_sha256, 16)
    except ValueError as error:
        raise ValueError(f"Registered image checksum is invalid: {page.page_id}") from error
    if not target.is_file():
        raise ValueError(f"Registered image target is unavailable: {page.page_id}")

    measured_width, measured_height, mime_type = _measure(target)
    digest = sha256_file(target)
    if digest.lower() != page.image_sha256.lower():
        raise ValueError(f"Registered image checksum mismatch: {page.page_id}")
    if page.width != measured_width or page.height != measured_height:
        raise ValueError(f"Registered image dimensions mismatch: {page.page_id}")
    if page.mime_type != mime_type:
        raise ValueError(f"Registered image MIME mismatch: {page.page_id}")
    return measured_width, measured_height, mime_type, digest


def _download(
    page: PageRecord,
    target: Path,
    width: int,
    timeout_seconds: float,
) -> tuple[str, str]:
    request_uris = [
        f"{page.iiif_base_uri}/full/{width},/0/default.jpg",
        f"{page.iiif_base_uri}/full/max/0/default.jpg",
    ]
    part = target.with_suffix(".jpg.part")
    last_error: Exception | None = None
    for index, request_uri in enumerate(request_uris):
        request = Request(request_uri, headers={"User-Agent": "ZFD-image-native/0.1"})
        try:
            with urlopen(request, timeout=timeout_seconds) as response:
                payload = response.read()
                final_uri = response.geturl()
                content_type = response.headers.get_content_type()
            if not content_type.startswith("image/"):
                raise ValueError(f"Unexpected MIME type for {page.page_id}: {content_type}")
            part.write_bytes(payload)
            _measure(part)
            os.replace(part, target)
            return request_uri, final_uri
        except HTTPError as error:
            last_error = error
            if error.code == 403 and index + 1 < len(request_uris):
                continue
            break
        except Exception as error:
            last_error = error
            break
        finally:
            if part.exists():
                part.unlink()
    assert last_error is not None
    raise last_error


def acquire_pages(
    pages: Iterable[PageRecord],
    output_root: str | Path,
    *,
    width: int = 2000,
    timeout_seconds: float = 60.0,
    overwrite: bool = False,
) -> AcquisitionResult:
    root = Path(output_root)
    root.mkdir(parents=True, exist_ok=True)
    updated: list[PageRecord] = []
    receipts: list[AcquisitionReceipt] = []

    for page in pages:
        request_uri = f"{page.iiif_base_uri}/full/{width},/0/default.jpg"
        target = root / f"{page.iiif_id}.jpg"
        disposition = "acquisition_failed"
        final_uri = request_uri
        try:
            if overwrite or not target.exists():
                request_uri, final_uri = _download(page, target, width, timeout_seconds)
                disposition = "downloaded_verified"
                measured_width, measured_height, mime_type = _measure(target)
                digest = sha256_file(target)
            else:
                measured_width, measured_height, mime_type, digest = _registered_reuse(
                    page,
                    target,
                    width,
                )
                request_uri = page.image_request_uri
                final_uri = request_uri
                disposition = "reused_verified"
            receipt = AcquisitionReceipt(
                page_id=page.page_id,
                iiif_id=page.iiif_id,
                request_uri=request_uri,
                final_uri=final_uri,
                image_path=str(target.resolve()),
                image_sha256=digest,
                byte_count=target.stat().st_size,
                mime_type=mime_type,
                width=measured_width,
                height=measured_height,
                disposition=disposition,
            )
            updated.append(
                replace(
                    page,
                    image_request_uri=request_uri,
                    image_sha256=digest,
                    image_path=str(target.resolve()),
                    width=measured_width,
                    height=measured_height,
                    mime_type=mime_type,
                    acquisition_status="verified",
                )
            )
        except Exception as error:
            receipt = AcquisitionReceipt(
                page_id=page.page_id,
                iiif_id=page.iiif_id,
                request_uri=request_uri,
                final_uri=None,
                image_path=None,
                image_sha256=None,
                byte_count=None,
                mime_type=None,
                width=None,
                height=None,
                disposition="acquisition_failed",
                error_type=type(error).__name__,
                error=str(error),
            )
            updated.append(replace(page, acquisition_status="acquisition_failed"))
        receipts.append(receipt)

    result = AcquisitionResult(tuple(updated), tuple(receipts))
    write_json(root / "acquisition_receipt.json", {"pages": [asdict(item) for item in receipts]})
    return result
