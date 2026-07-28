"""Command line entry point for image native ZFD evidence processing."""

from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path
import sys

from . import __version__
from .acquire import acquire_pages
from .claims import validate_claims
from .comparative import register_comparative_assets, validate_comparative_assets
from .corpus import run_corpus
from .io import canonical_json, read_json, read_jsonl, write_json, write_jsonl
from .kraken_compare import (
    validate_corpus_geometry_comparison,
    validate_geometry_comparison,
)
from .manifest import build_page_manifest, load_page_manifest
from .model_acquire import acquire_registered_models
from .model_registry import validate_model_registry
from .models import PageRecord, SourceRecord
from .ocr import OpenSetConfig, process_page
from .publication import scan_publication_boundary
from .receipts import freeze_stage_a_receipts, validate_stage_a_receipts
from .sources import validate_sources


def _safe_print(value: object) -> None:
    text = value if isinstance(value, str) else canonical_json(value)
    print(str(text).encode("ascii", "backslashreplace").decode("ascii"))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="zfd-native")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)

    build = commands.add_parser("build-manifest", help="build the Yale page authority manifest")
    build.add_argument("--map", required=True, type=Path)
    build.add_argument("--output", required=True, type=Path)

    acquire = commands.add_parser("acquire", help="acquire registered IIIF pixels")
    acquire.add_argument("--manifest", required=True, type=Path)
    acquire.add_argument("--output", required=True, type=Path)
    acquire.add_argument("--updated-manifest", required=True, type=Path)
    acquire.add_argument("--width", type=int, default=2000)
    acquire.add_argument("--overwrite", action="store_true")

    for name, help_text in (
        ("segment-page", "provisionally segment one registered page"),
        ("ocr-page", "compatibility alias for segment-page"),
    ):
        page = commands.add_parser(name, help=help_text)
        page.add_argument("--manifest", required=True, type=Path)
        page.add_argument("--page-id", required=True)
        page.add_argument("--output", required=True, type=Path)

    for name, help_text in (
        ("segment-corpus", "provisionally segment every manifest page"),
        ("ocr-corpus", "compatibility alias for segment-corpus"),
    ):
        corpus = commands.add_parser(name, help=help_text)
        corpus.add_argument("--manifest", required=True, type=Path)
        corpus.add_argument("--output", required=True, type=Path)

    freeze = commands.add_parser("freeze-receipts", help="freeze validated Stage A evidence receipts")
    freeze.add_argument("--manifest", required=True, type=Path)
    freeze.add_argument("--corpus", required=True, type=Path)
    freeze.add_argument("--output", required=True, type=Path)
    freeze.add_argument("--repository-root", type=Path, default=Path.cwd())

    receipt_check = commands.add_parser(
        "validate-receipts", help="validate frozen Stage A evidence receipts"
    )
    receipt_check.add_argument("--receipts", required=True, type=Path)
    receipt_check.add_argument(
        "--corpus",
        type=Path,
        help="explicit corpus artifact root for portable receipt validation",
    )
    receipt_check.add_argument("--manifest", type=Path)
    receipt_check.add_argument("--repository-root", type=Path, default=Path.cwd())

    comparanda = commands.add_parser(
        "register-comparanda", help="register comparative manuscript assets and duplicate lineage"
    )
    comparanda.add_argument("--config", required=True, type=Path)
    comparanda.add_argument("--source-mount", required=True, type=Path)
    comparanda.add_argument("--output", required=True, type=Path)

    comparanda_check = commands.add_parser(
        "validate-comparanda", help="validate comparative asset receipts and duplicate lineage"
    )
    comparanda_check.add_argument("--receipts", required=True, type=Path)
    comparanda_check.add_argument("--source-register", required=True, type=Path)

    models = commands.add_parser(
        "validate-models", help="validate pinned comparative model identity and quarantine"
    )
    models.add_argument("--register", required=True, type=Path)
    models.add_argument("--repository-root", type=Path, default=Path.cwd())
    models.add_argument("--require-cache", action="store_true")

    acquire_models = commands.add_parser(
        "acquire-models", help="acquire checksum verified quarantined comparative models"
    )
    acquire_models.add_argument("--register", required=True, type=Path)
    acquire_models.add_argument("--repository-root", type=Path, default=Path.cwd())
    acquire_models.add_argument("--receipt", type=Path)
    acquire_models.add_argument("--timeout-seconds", type=float, default=60.0)

    comparison = commands.add_parser(
        "validate-geometry-comparison", help="validate a quarantined geometry receipt"
    )
    comparison.add_argument("--comparison", required=True, type=Path)

    corpus_comparison = commands.add_parser(
        "validate-geometry-comparison-corpus",
        help="validate a whole quarantined geometry comparison corpus",
    )
    corpus_comparison.add_argument("--summary", required=True, type=Path)
    corpus_comparison.add_argument("--manifest", required=True, type=Path)

    sources = commands.add_parser("validate-sources", help="validate source and rights metadata")
    sources.add_argument("--register", required=True, type=Path)

    claims = commands.add_parser("validate-claims", help="evaluate publication claims")
    claims.add_argument("--ledger", required=True, type=Path)
    claims.add_argument("--receipts", type=Path)
    claims.add_argument("--authority", type=Path)

    publication = commands.add_parser(
        "validate-publication-boundary",
        help="reject unbannered legacy completion and provenance claims",
    )
    publication.add_argument("--repository-root", type=Path, default=Path.cwd())

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    if args.command == "build-manifest":
        pages = build_page_manifest(args.map)
        write_jsonl(args.output, pages)
        _safe_print({"output": str(args.output), "pages": len(pages)})
        return 0

    if args.command == "acquire":
        pages = load_page_manifest(args.manifest)
        result = acquire_pages(pages, args.output, width=args.width, overwrite=args.overwrite)
        write_jsonl(args.updated_manifest, result.pages)
        _safe_print(
            {
                "verified": len(result.receipts) - result.failed,
                "failed": result.failed,
                "manifest": str(args.updated_manifest),
            }
        )
        return 0 if result.failed == 0 else 1

    if args.command in {"segment-page", "ocr-page"}:
        pages = {page.page_id: page for page in load_page_manifest(args.manifest)}
        if args.page_id not in pages:
            _safe_print(f"ERROR: unknown page id {args.page_id}")
            return 2
        result = process_page(pages[args.page_id], OpenSetConfig())
        write_json(args.output, result)
        _safe_print(
            {
                "page_id": result.page_id,
                "regions": len(result.regions),
                "lines": len(result.lines),
                "graphemes": len(result.graphemes),
                "unknown": sum(item.diplomatic_label is None for item in result.graphemes),
            }
        )
        return 0

    if args.command in {"segment-corpus", "ocr-corpus"}:
        summary = run_corpus(load_page_manifest(args.manifest), args.output)
        _safe_print(asdict(summary))
        return 0 if summary.failed_pages == 0 and summary.missing_pages == 0 else 1

    if args.command == "freeze-receipts":
        summary = freeze_stage_a_receipts(
            args.manifest,
            args.corpus,
            args.output,
            repository_root=args.repository_root,
        )
        _safe_print(asdict(summary))
        return 0

    if args.command == "validate-receipts":
        report = validate_stage_a_receipts(
            args.receipts,
            corpus_root=args.corpus,
            repository_root=args.repository_root,
            manifest_path=args.manifest,
        )
        _safe_print(asdict(report))
        return 0 if report.ok else 1

    if args.command == "register-comparanda":
        summary = register_comparative_assets(args.config, args.source_mount, args.output)
        _safe_print(asdict(summary))
        return 0

    if args.command == "validate-comparanda":
        report = validate_comparative_assets(args.receipts, args.source_register)
        _safe_print(asdict(report))
        return 0 if report.ok else 1

    if args.command == "validate-models":
        report = validate_model_registry(
            args.register,
            repository_root=args.repository_root,
            require_cache=args.require_cache,
        )
        _safe_print(asdict(report))
        return 0 if report.ok else 1

    if args.command == "acquire-models":
        summary = acquire_registered_models(
            args.register,
            repository_root=args.repository_root,
            receipt_path=args.receipt,
            timeout_seconds=args.timeout_seconds,
        )
        _safe_print(asdict(summary))
        return 0 if summary.failed_file_count == 0 else 1

    if args.command == "validate-geometry-comparison":
        errors = validate_geometry_comparison(args.comparison)
        _safe_print({"ok": not errors, "errors": errors})
        return 0 if not errors else 1

    if args.command == "validate-geometry-comparison-corpus":
        errors = validate_corpus_geometry_comparison(args.summary, args.manifest)
        _safe_print({"ok": not errors, "errors": errors})
        return 0 if not errors else 1

    if args.command == "validate-sources":
        payload = read_json(args.register)
        records = [SourceRecord(**row) for row in payload.get("sources", [])]
        report = validate_sources(records)
        _safe_print({"ok": report.ok, "errors": [asdict(item) for item in report.errors]})
        return 0 if report.ok else 1

    if args.command == "validate-claims":
        payload = read_json(args.ledger)
        ledger = {key: value for key, value in payload.items() if key != "schema_version"}
        receipts = read_json(args.receipts) if args.receipts else {}
        authority_payload = read_json(args.authority) if args.authority else {}
        receipt_authority = authority_payload.get("receipts", authority_payload)
        report = validate_claims(ledger, receipts, receipt_authority)
        decisions = {name: asdict(report.claim(name)) for name in ledger}
        _safe_print(decisions)
        return 0 if all(item["allowed"] for item in decisions.values()) else 1

    if args.command == "validate-publication-boundary":
        issues = scan_publication_boundary(args.repository_root)
        _safe_print({"ok": not issues, "issues": [asdict(issue) for issue in issues]})
        return 0 if not issues else 1

    raise AssertionError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
