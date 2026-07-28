"""Windows safe command surface for canonical corpus parity."""

from __future__ import annotations

from argparse import ArgumentParser
import json
from pathlib import Path
import sys
from typing import Any

from zfd_image_native.io import canonical_json, read_json, read_jsonl

from .core import (
    build_corpus_parity,
    read_corpus_parity,
    validate_corpus_parity_bundle,
    write_corpus_parity_new,
)


def _safe_print(value: Any) -> None:
    text = canonical_json(value)
    print(text.encode("ascii", "backslashreplace").decode("ascii"))


def _inside(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _resolve_input(path: Path, repository_root: Path) -> Path:
    resolved = (repository_root / path if not path.is_absolute() else path).resolve()
    if not _inside(resolved, repository_root):
        raise ValueError("INPUT_OUTSIDE_REPOSITORY")
    return resolved


def _resolve_output(path: Path, repository_root: Path) -> Path:
    resolved = (repository_root / path if not path.is_absolute() else path).resolve()
    if not _inside(resolved, repository_root.resolve()):
        raise ValueError("OUTPUT_OUTSIDE_REPOSITORY")
    bases = (
        (repository_root / "build" / "image_native" / "parity").resolve(),
        (repository_root / "06_Pipelines" / "image_native_runs").resolve(),
    )
    if not any(resolved != base and _inside(resolved, base) for base in bases):
        raise ValueError("OUTPUT_OUTSIDE_PARITY_ROOTS")
    return resolved


def _repository_relative(path: Path, repository_root: Path) -> str:
    return path.relative_to(repository_root).as_posix()


def _parser() -> ArgumentParser:
    parser = ArgumentParser(prog="zfd-parity")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("build-parity-corpus", "validate-parity-corpus"):
        command = commands.add_parser(name)
        command.add_argument("--repository-root", type=Path, default=Path.cwd())
        command.add_argument("--stage-a-receipts", required=True, type=Path)
        command.add_argument("--stage-a-corpus", required=True, type=Path)
        command.add_argument("--manifest", required=True, type=Path)
        if name == "build-parity-corpus":
            command.add_argument("--layer-records", type=Path)
            command.add_argument("--output-root", required=True, type=Path)
        else:
            command.add_argument("--parity-root", required=True, type=Path)
    return parser


def _context(args: Any) -> dict[str, Path]:
    repository = args.repository_root.resolve()
    if not repository.is_dir():
        raise ValueError("REPOSITORY_ROOT_MISSING")
    return {
        "repository_root": repository,
        "stage_a_receipts": _resolve_input(args.stage_a_receipts, repository),
        "corpus_root": _resolve_input(args.stage_a_corpus, repository),
        "manifest_path": _resolve_input(args.manifest, repository),
    }


def _overlay(path: Path | None, repository_root: Path) -> tuple[tuple[dict[str, Any], ...], dict[str, Any] | None]:
    if path is None:
        return (), None
    root = _resolve_input(path, repository_root)
    records = tuple(read_jsonl(root / "records.jsonl"))
    evidence = read_json(root / "evidence_authority.json")
    if not isinstance(evidence, dict):
        raise ValueError("EVIDENCE_OVERLAY_MALFORMED")
    return records, evidence


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(list(sys.argv[1:] if argv is None else argv))
    try:
        context = _context(args)
        repository = context["repository_root"]
        if args.command == "build-parity-corpus":
            proposals, evidence = _overlay(args.layer_records, repository)
            bundle = build_corpus_parity(
                context["stage_a_receipts"],
                proposed_records=proposals,
                evidence_overlay=evidence,
                corpus_root=context["corpus_root"],
                repository_root=repository,
                manifest_path=context["manifest_path"],
            )
            errors = validate_corpus_parity_bundle(
                bundle,
                context["stage_a_receipts"],
                corpus_root=context["corpus_root"],
                repository_root=repository,
                manifest_path=context["manifest_path"],
            )
            if errors:
                raise ValueError("PARITY_BUNDLE_INVALID:" + ",".join(errors))
            output = _resolve_output(args.output_root, repository)
            write_corpus_parity_new(output, bundle)
            _safe_print(
                {
                    "confirmed_translated_pages": bundle.summary[
                        "confirmed_translated_pages"
                    ],
                    "confirmed_translated_regions": bundle.summary[
                        "confirmed_translated_regions"
                    ],
                    "ok": True,
                    "output_root_relpath": _repository_relative(output, repository),
                    "total_pages": bundle.summary["total_pages"],
                    "total_regions": bundle.summary["total_regions"],
                }
            )
            return 0
        root = _resolve_input(args.parity_root, repository)
        bundle = read_corpus_parity(root)
        errors = validate_corpus_parity_bundle(
            bundle,
            context["stage_a_receipts"],
            corpus_root=context["corpus_root"],
            repository_root=repository,
            manifest_path=context["manifest_path"],
        )
        _safe_print(
            {
                "errors": errors,
                "ok": not errors,
                "total_pages": bundle.summary.get("total_pages"),
                "total_regions": bundle.summary.get("total_regions"),
            }
        )
        return 0 if not errors else 1
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        _safe_print({"error": str(error), "ok": False})
        return 1
