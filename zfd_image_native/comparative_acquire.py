"""Reproducible IIIF acquisition for a source selected by an edition page."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from hashlib import sha256
from io import BytesIO
import json
import os
from pathlib import Path
import re
from typing import Any
from urllib.request import Request, urlopen

from PIL import Image

from .io import canonical_json, sha256_file, write_json


USER_AGENT = "ZFD-image-native/0.1"
INFO_URL_PATTERN = re.compile(
    rb"https://digi\.vatlib\.it/iiifimage/[^\"'<>\s]+?/info\.json"
)


@dataclass(frozen=True)
class ComparativeAcquisitionSummary:
    source_id: str
    selected_canvas_count: int
    verified_asset_count: int
    downloaded_asset_count: int
    reused_asset_count: int
    failed_asset_count: int
    manifest_sha256: str
    selection_sha256: str | None
    receipt_sha256: str


def _fetch(uri: str, timeout_seconds: float) -> tuple[bytes, str, str]:
    request = Request(uri, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout_seconds) as response:
        payload = response.read()
        final_uri = response.geturl()
        content_type = response.headers.get_content_type()
    return payload, final_uri, content_type


def _service_id(resource: dict[str, Any]) -> str | None:
    service = resource.get("service")
    if isinstance(service, list):
        service = next((item for item in service if isinstance(item, dict)), None)
    if not isinstance(service, dict):
        return None
    value = service.get("@id") or service.get("id")
    return value.rstrip("/") if isinstance(value, str) and value else None


def _manifest_canvases(payload: Any) -> dict[str, dict[str, str]]:
    if not isinstance(payload, dict):
        raise ValueError("IIIF manifest is not an object")
    found: dict[str, dict[str, str]] = {}
    sequences = payload.get("sequences")
    if not isinstance(sequences, list):
        raise ValueError("IIIF Presentation 2 manifest has no sequences")
    for sequence in sequences:
        if not isinstance(sequence, dict):
            continue
        for canvas in sequence.get("canvases", []):
            if not isinstance(canvas, dict):
                continue
            images = canvas.get("images")
            if not isinstance(images, list) or not images or not isinstance(images[0], dict):
                continue
            resource = images[0].get("resource")
            if not isinstance(resource, dict):
                continue
            service_id = _service_id(resource)
            if service_id is None:
                continue
            if service_id in found:
                raise ValueError(f"IIIF service occurs on more than one canvas: {service_id}")
            canvas_id = canvas.get("@id") or canvas.get("id")
            label = canvas.get("label")
            if not isinstance(canvas_id, str) or not isinstance(label, str):
                raise ValueError(f"IIIF canvas identity is incomplete for {service_id}")
            found[service_id] = {
                "canvas_id": canvas_id,
                "canvas_label": label,
                "image_service_id": service_id,
            }
    return found


def _selected_services(selection_payload: bytes) -> list[str]:
    services: list[str] = []
    seen: set[str] = set()
    for match in INFO_URL_PATTERN.findall(selection_payload):
        service = match.decode("ascii")[: -len("/info.json")].rstrip("/")
        if service not in seen:
            seen.add(service)
            services.append(service)
    if not services:
        raise ValueError("Selection page contains no supported IIIF image services")
    return services


def _local_name(canvas_id: str, service_id: str) -> str:
    canvas_token = canvas_id.rstrip("/").rsplit("/", 1)[-1]
    folio_match = re.search(r"_([0-9]{4}[rv])\.jp2$", service_id)
    folio_token = folio_match.group(1) if folio_match else sha256(service_id.encode()).hexdigest()[:12]
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", canvas_token):
        raise ValueError(f"Unsafe canvas token: {canvas_token}")
    return f"{canvas_token}_{folio_token}.jpg"


def _measure_image(payload: bytes) -> tuple[int, int, str]:
    with Image.open(BytesIO(payload)) as image:
        image.load()
        width, height = image.size
        mime_type = Image.MIME.get(image.format or "", "application/octet-stream")
    if not mime_type.startswith("image/"):
        raise ValueError(f"Downloaded payload is not a supported image: {mime_type}")
    return width, height, mime_type


def _download_image(
    service_id: str,
    target: Path,
    width: int,
    timeout_seconds: float,
) -> tuple[str, str, int, int, str]:
    request_uris = (
        f"{service_id}/full/{width},/0/default.jpg",
        f"{service_id}/full/max/0/default.jpg",
    )
    last_error: Exception | None = None
    for request_uri in request_uris:
        try:
            payload, final_uri, content_type = _fetch(request_uri, timeout_seconds)
            if not content_type.startswith("image/"):
                raise ValueError(f"Unexpected image response type: {content_type}")
            measured_width, measured_height, mime_type = _measure_image(payload)
            part = target.with_suffix(target.suffix + ".part")
            part.write_bytes(payload)
            os.replace(part, target)
            return request_uri, final_uri, measured_width, measured_height, mime_type
        except Exception as error:
            last_error = error
            part = target.with_suffix(target.suffix + ".part")
            if part.exists():
                part.unlink()
    assert last_error is not None
    raise last_error


def acquire_iiif_selection(
    *,
    source_id: str,
    manifest_uri: str,
    selection_uri: str | None,
    output_root: str | Path,
    expected_count: int,
    width: int = 2000,
    timeout_seconds: float = 60.0,
    overwrite: bool = False,
) -> ComparativeAcquisitionSummary:
    if not source_id or expected_count < 1 or width < 1:
        raise ValueError("Source identity, expected count, and width must be positive")
    root = Path(output_root)
    image_root = root / "img"
    metadata_root = root / "meta"
    image_root.mkdir(parents=True, exist_ok=True)
    metadata_root.mkdir(parents=True, exist_ok=True)

    manifest_bytes, manifest_final_uri, manifest_type = _fetch(manifest_uri, timeout_seconds)
    if "json" not in manifest_type:
        raise ValueError(f"Unexpected manifest response type: {manifest_type}")
    manifest_payload = json.loads(manifest_bytes.decode("utf-8"))
    canvases = _manifest_canvases(manifest_payload)
    selection_bytes: bytes | None = None
    selection_final_uri: str | None = None
    if selection_uri is None:
        selection_method = "complete_manifest"
        selected_services = list(canvases)
    else:
        selection_method = "edition_page"
        selection_bytes, selection_final_uri, selection_type = _fetch(
            selection_uri, timeout_seconds
        )
        if "html" not in selection_type:
            raise ValueError(f"Unexpected selection response type: {selection_type}")
        selected_services = _selected_services(selection_bytes)
    if len(selected_services) != expected_count:
        raise ValueError(
            f"Selected IIIF count mismatch: expected {expected_count}, got {len(selected_services)}"
        )
    missing = [service for service in selected_services if service not in canvases]
    if missing:
        raise ValueError(f"Selected IIIF services are absent from the manifest: {missing[:3]}")

    manifest_path = metadata_root / "manifest.json"
    manifest_path.write_bytes(manifest_bytes)
    selection_path: Path | None = None
    if selection_bytes is not None:
        selection_path = metadata_root / "selection.html"
        selection_path.write_bytes(selection_bytes)

    mappings: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    downloaded = 0
    reused = 0
    used_names: set[str] = set()
    for service_id in selected_services:
        canvas = canvases[service_id]
        local_name = _local_name(canvas["canvas_id"], service_id)
        if local_name in used_names:
            raise ValueError(f"Selected canvases produce a duplicate local name: {local_name}")
        used_names.add(local_name)
        target = image_root / local_name
        request_uri = f"{service_id}/full/{width},/0/default.jpg"
        final_uri: str | None = None
        disposition = "reused_verified"
        try:
            if overwrite or not target.is_file():
                request_uri, final_uri, measured_width, measured_height, mime_type = _download_image(
                    service_id, target, width, timeout_seconds
                )
                downloaded += 1
                disposition = "downloaded_verified"
            else:
                payload = target.read_bytes()
                measured_width, measured_height, mime_type = _measure_image(payload)
                reused += 1
            mappings.append(
                {
                    "local_name": local_name,
                    "source_label": canvas["canvas_label"],
                    "request_uri": request_uri,
                    "final_uri": final_uri,
                    "canvas_id": canvas["canvas_id"],
                    "canvas_label": canvas["canvas_label"],
                    "image_service_id": service_id,
                    "sha256": sha256_file(target),
                    "byte_length": target.stat().st_size,
                    "width": measured_width,
                    "height": measured_height,
                    "mime_type": mime_type,
                    "disposition": disposition,
                }
            )
        except Exception as error:
            failures.append(
                {
                    "canvas_id": canvas["canvas_id"],
                    "image_service_id": service_id,
                    "error_type": type(error).__name__,
                    "error": str(error),
                }
            )

    write_json(metadata_root / "canvas_mapping.json", mappings)
    receipt = {
        "schema": "zfd.comparative_acquisition.v1",
        "schema_version": "1.0.0",
        "source_id": source_id,
        "manifest_uri": manifest_uri,
        "manifest_final_uri": manifest_final_uri,
        "manifest_sha256": sha256_file(manifest_path),
        "selection_method": selection_method,
        "selection_uri": selection_uri,
        "selection_final_uri": selection_final_uri,
        "selection_sha256": sha256_file(selection_path) if selection_path else None,
        "expected_count": expected_count,
        "selected_canvas_count": len(selected_services),
        "verified_asset_count": len(mappings),
        "downloaded_asset_count": downloaded,
        "reused_asset_count": reused,
        "failed_asset_count": len(failures),
        "failures": failures,
    }
    receipt_hash = sha256(canonical_json(receipt).encode("utf-8")).hexdigest()
    write_json(metadata_root / "acquisition_receipt.json", {**receipt, "receipt_sha256": receipt_hash})
    return ComparativeAcquisitionSummary(
        source_id=source_id,
        selected_canvas_count=len(selected_services),
        verified_asset_count=len(mappings),
        downloaded_asset_count=downloaded,
        reused_asset_count=reused,
        failed_asset_count=len(failures),
        manifest_sha256=receipt["manifest_sha256"],
        selection_sha256=receipt["selection_sha256"],
        receipt_sha256=receipt_hash,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="zfd-comparative-acquire")
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--manifest-uri", required=True)
    parser.add_argument("--selection-uri")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--expected-count", required=True, type=int)
    parser.add_argument("--width", type=int, default=2000)
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    summary = acquire_iiif_selection(
        source_id=args.source_id,
        manifest_uri=args.manifest_uri,
        selection_uri=args.selection_uri,
        output_root=args.output,
        expected_count=args.expected_count,
        width=args.width,
        overwrite=args.overwrite,
    )
    print(canonical_json(asdict(summary)))
    return 0 if summary.failed_asset_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
