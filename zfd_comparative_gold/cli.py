"""Windows-safe command line surface for comparative review queues."""

from __future__ import annotations

from argparse import ArgumentParser
import json
import os
from pathlib import Path
import sys
from typing import Any

from .core import (
    ComparativeQueueConfig,
    HandBoundaryQueueBundle,
    MAVROV_ASSET_COUNT,
    MAVROV_PILOT_PAIRS,
    MAVROV_SOURCE_ID,
    build_hand_boundary_queue,
    validate_hand_boundary_queue,
)


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _stdout_json(value: Any) -> str:
    """Emit ASCII-only JSON so Windows legacy consoles cannot corrupt receipts."""

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def _inside(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _resolve_output_root(path: Path, repository_root: Path) -> Path:
    repository_root = repository_root.resolve()
    target = path if path.is_absolute() else repository_root / path
    target = target.resolve()
    allowed_roots = (
        (repository_root / "build" / "comparative_review").resolve(),
        (repository_root / "06_Pipelines" / "comparative_review_runs").resolve(),
    )
    if not any(_inside(target, root) for root in allowed_roots):
        raise ValueError("OUTPUT_OUTSIDE_ALLOWED_ROOT")
    return target


def _repository_relative_locator(path: Path, repository_root: Path) -> str:
    return path.resolve().relative_to(repository_root.resolve()).as_posix()


def _write_new(path: Path, data: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def _jsonl_bytes(rows: list[dict[str, Any]]) -> bytes:
    return b"".join((_canonical_json(row) + "\n").encode("utf-8") for row in rows)


def _write_bundle_new(output_root: Path, bundle: HandBoundaryQueueBundle) -> None:
    if output_root.exists():
        raise ValueError("OUTPUT_ROOT_ALREADY_EXISTS")
    output_root.parent.mkdir(parents=True, exist_ok=True)
    output_root.mkdir()
    _write_new(output_root / "hand_boundary_queue.jsonl", _jsonl_bytes(bundle.rows))
    _write_new(output_root / "hand_boundary_pilot.jsonl", _jsonl_bytes(bundle.pilot))
    _write_new(
        output_root / "hand_boundary_summary.json",
        (_canonical_json(bundle.summary) + "\n").encode("utf-8"),
    )


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as stream:
        return json.load(stream)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as stream:
        for line in stream:
            if line.strip():
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ValueError("QUEUE_FILE_ROW_MALFORMED")
                rows.append(value)
    return rows


def _read_bundle(root: Path) -> HandBoundaryQueueBundle:
    if not root.is_dir():
        raise ValueError("QUEUE_ROOT_MISSING")
    rows = _read_jsonl(root / "hand_boundary_queue.jsonl")
    pilot = _read_jsonl(root / "hand_boundary_pilot.jsonl")
    summary = _read_json(root / "hand_boundary_summary.json")
    if not isinstance(summary, dict):
        raise ValueError("QUEUE_SUMMARY_MALFORMED")
    return HandBoundaryQueueBundle(rows=rows, pilot=pilot, summary=summary)


def _common(parser: ArgumentParser) -> None:
    parser.add_argument("--repository-root", required=True, type=Path)
    parser.add_argument("--source-mount", required=True, type=Path)
    parser.add_argument("--asset-root", type=Path, default=Path("data/image_native"))
    parser.add_argument(
        "--config", dest="config_path", type=Path, default=Path("data/image_native/comparative_sources.json")
    )
    parser.add_argument(
        "--register", dest="register_path", type=Path, default=Path("data/image_native/source_register.json")
    )


def _parser() -> ArgumentParser:
    parser = ArgumentParser(prog="zfd-comparanda")
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build-queue", help="build an immutable quarantined Mavrov review queue")
    _common(build)
    build.add_argument("--output-root", required=True, type=Path)
    validate = commands.add_parser("validate-queue", help="rehash source pixels and validate a queue")
    _common(validate)
    validate.add_argument("--queue-root", required=True, type=Path)
    return parser


def _resolve_input(path: Path, repository_root: Path) -> Path:
    return path.resolve() if path.is_absolute() else (repository_root / path).resolve()


def _build_args(args: Any) -> dict[str, Any]:
    repository_root = args.repository_root.resolve()
    return {
        "repository_root": repository_root,
        "source_mount": args.source_mount.resolve(),
        "asset_root": _resolve_input(args.asset_root, repository_root),
        "config_path": _resolve_input(args.config_path, repository_root),
        "register_path": _resolve_input(args.register_path, repository_root),
        "config": ComparativeQueueConfig(
            source_id=MAVROV_SOURCE_ID,
            expected_asset_count=MAVROV_ASSET_COUNT,
            pilot_pairs=MAVROV_PILOT_PAIRS,
        ),
    }


def _require_valid_bundle(
    bundle: HandBoundaryQueueBundle, build_args: dict[str, Any]
) -> None:
    errors = validate_hand_boundary_queue(bundle, **build_args)
    if errors:
        raise ValueError("QUEUE_INVALID:" + ",".join(errors))
    if bundle.summary.get("implementation_provenance_status") != "clean_reachable_commit":
        raise ValueError("IMPLEMENTATION_PROVENANCE_NOT_PUBLISHABLE")


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(list(sys.argv[1:] if argv is None else argv))
    try:
        build_args = _build_args(args)
        if args.command == "build-queue":
            bundle = build_hand_boundary_queue(**build_args)
            _require_valid_bundle(bundle, build_args)
            output_root = _resolve_output_root(args.output_root, build_args["repository_root"])
            _write_bundle_new(output_root, bundle)
            print(
                _stdout_json(
                    {
                        "asset_count": bundle.summary["asset_count"],
                        "errors": [],
                        "ok": True,
                        "output_root_relpath": _repository_relative_locator(
                            output_root, build_args["repository_root"]
                        ),
                        "pilot_pair_count": bundle.summary["pilot_pair_count"],
                        "queue_id": bundle.summary["queue_id"],
                        "training_ready_asset_count": 0,
                    }
                )
            )
            return 0
        queue_root = _resolve_output_root(args.queue_root, build_args["repository_root"])
        bundle = _read_bundle(queue_root)
        errors = validate_hand_boundary_queue(bundle, **build_args)
        print(
            _stdout_json(
                {
                    "asset_count": len(bundle.rows),
                    "errors": errors,
                    "ok": not errors,
                    "queue_id": bundle.summary.get("queue_id"),
                    "training_ready_asset_count": bundle.summary.get("training_ready_asset_count"),
                }
            )
        )
        return 0 if not errors else 1
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(_stdout_json({"error": str(error), "ok": False}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["_resolve_output_root", "_write_bundle_new", "main"]
