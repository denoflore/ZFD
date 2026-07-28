"""Windows-safe command line surface for comparative review queues."""

from __future__ import annotations

from argparse import ArgumentParser
import json
import os
from pathlib import Path, PurePosixPath
import sys
from typing import Any

from .core import (
    ComparativeQueueConfig,
    HandBoundaryQueueBundle,
    MAVROV_ASSET_COUNT,
    MAVROV_PILOT_PAIRS,
    MAVROV_SOURCE_ID,
    build_hand_boundary_queue,
    _git_commit_reachable,
    _git_state,
    validate_hand_boundary_queue,
)
from .review import (
    ComparativeReviewAuthority,
    build_pair_review_task,
    open_comparative_review_authority,
    seal_pair_adjudication,
    seal_pair_observation,
    validate_pair_adjudication,
    validate_pair_observation,
    validate_pair_review_task,
)


_REVIEW_COMMANDS = frozenset(
    (
        "create-review-task",
        "validate-review-task",
        "seal-review-observation",
        "validate-review-observation",
        "seal-review-adjudication",
        "validate-review-adjudication",
    )
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
    if not _inside(target, repository_root):
        raise ValueError("OUTPUT_OUTSIDE_REPOSITORY")
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


def _resolve_review_output(path: Path, repository_root: Path) -> Path:
    target = _resolve_output_root(path, repository_root)
    allowed_roots = (
        (repository_root.resolve() / "build" / "comparative_review").resolve(),
        (repository_root.resolve() / "06_Pipelines" / "comparative_review_runs").resolve(),
    )
    if target in allowed_roots or target.suffix.lower() != ".json":
        raise ValueError("REVIEW_OUTPUT_MUST_BE_STRICT_JSON_DESCENDANT")
    if target.exists() or target.with_name(target.name + ".part").exists():
        raise ValueError("REVIEW_OUTPUT_ALREADY_EXISTS")
    return target


def _write_review_json_new(
    path: Path, value: dict[str, Any], repository_root: Path
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    target = _resolve_review_output(path, repository_root)
    _write_new(target, (_canonical_json(value) + "\n").encode("utf-8"))


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


def _review_common(parser: ArgumentParser) -> None:
    _common(parser)
    parser.add_argument("--queue-root", required=True, type=Path)


def _review_task_input(parser: ArgumentParser) -> None:
    _review_common(parser)
    parser.add_argument("--task", required=True, type=Path)


def _review_observation_inputs(parser: ArgumentParser) -> None:
    _review_task_input(parser)
    parser.add_argument("--primary", required=True, type=Path)
    parser.add_argument("--independent", required=True, type=Path)


def _parser() -> ArgumentParser:
    parser = ArgumentParser(prog="zfd-comparanda")
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build-queue", help="build an immutable quarantined Mavrov review queue")
    _common(build)
    build.add_argument("--output-root", required=True, type=Path)
    validate = commands.add_parser("validate-queue", help="rehash source pixels and validate a queue")
    _common(validate)
    validate.add_argument("--queue-root", required=True, type=Path)

    create_review = commands.add_parser(
        "create-review-task", help="create one pixel bound pilot pair task"
    )
    _review_common(create_review)
    create_review.add_argument("--pair-task-id", required=True)
    create_review.add_argument("--left-region", nargs=4, type=int)
    create_review.add_argument("--right-region", nargs=4, type=int)
    create_review.add_argument("--output", required=True, type=Path)

    validate_review = commands.add_parser(
        "validate-review-task", help="rehash one pilot pair task and both source images"
    )
    _review_task_input(validate_review)

    seal_observation = commands.add_parser(
        "seal-review-observation", help="seal one blinded pair observation"
    )
    _review_task_input(seal_observation)
    seal_observation.add_argument("--draft", required=True, type=Path)
    seal_observation.add_argument("--output", required=True, type=Path)

    validate_observation = commands.add_parser(
        "validate-review-observation", help="validate one blinded pair observation"
    )
    _review_task_input(validate_observation)
    validate_observation.add_argument("--observation", required=True, type=Path)

    seal_adjudication = commands.add_parser(
        "seal-review-adjudication", help="seal a distinct reviewer pair adjudication"
    )
    _review_observation_inputs(seal_adjudication)
    seal_adjudication.add_argument("--draft", required=True, type=Path)
    seal_adjudication.add_argument("--output", required=True, type=Path)

    validate_adjudication = commands.add_parser(
        "validate-review-adjudication", help="validate a pair scoped adjudication"
    )
    _review_observation_inputs(validate_adjudication)
    validate_adjudication.add_argument("--adjudication", required=True, type=Path)
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


def _resolve_review_input(path: Path, repository_root: Path) -> Path:
    target = _resolve_output_root(path, repository_root)
    if not target.is_file():
        raise ValueError("REVIEW_INPUT_MISSING")
    return target


def _read_review_json(path: Path, repository_root: Path) -> dict[str, Any]:
    value = _read_json(_resolve_review_input(path, repository_root))
    if not isinstance(value, dict):
        raise ValueError("REVIEW_INPUT_MALFORMED")
    return value


def _registered_source_root(build_args: dict[str, Any]) -> Path:
    config_payload = _read_json(build_args["config_path"])
    if not isinstance(config_payload, dict) or not isinstance(config_payload.get("sources"), list):
        raise ValueError("SOURCE_CONFIG_MALFORMED")
    source_id = build_args["config"].source_id
    matches = [
        row
        for row in config_payload["sources"]
        if isinstance(row, dict) and row.get("source_id") == source_id
    ]
    if len(matches) != 1:
        raise ValueError("SOURCE_CONFIG_RECORD_INVALID")
    local_subpath = matches[0].get("local_subpath")
    if not isinstance(local_subpath, str) or not local_subpath or "\\" in local_subpath:
        raise ValueError("SOURCE_LOCAL_SUBPATH_INVALID")
    relative = PurePosixPath(local_subpath)
    if relative.is_absolute() or "." in relative.parts or ".." in relative.parts:
        raise ValueError("SOURCE_LOCAL_SUBPATH_INVALID")
    source_mount = build_args["source_mount"].resolve()
    source_root = source_mount.joinpath(*relative.parts).resolve()
    if not _inside(source_root, source_mount) or not source_root.is_dir():
        raise ValueError("SOURCE_ROOT_MISSING_OR_OUTSIDE_MOUNT")
    return source_root


def _require_review_implementation_publishable(repository_root: Path) -> None:
    commit, dirty = _git_state()
    try:
        reachable = commit is not None and _git_commit_reachable(repository_root, commit)
    except OSError:
        reachable = False
    if dirty is not False or not reachable:
        raise ValueError("REVIEW_IMPLEMENTATION_NOT_PUBLISHABLE")


def _open_review_authority(
    args: Any,
) -> tuple[Path, ComparativeReviewAuthority, Path]:
    repository_root = args.repository_root.resolve()
    if not repository_root.is_dir():
        raise ValueError("REPOSITORY_ROOT_MISSING")
    queue_root = _resolve_output_root(args.queue_root, repository_root)
    bundle = _read_bundle(queue_root)
    build_args = _build_args(args)
    _require_valid_bundle(bundle, build_args)
    source_root = _registered_source_root(build_args)
    authority = open_comparative_review_authority(
        bundle,
        repository_root=build_args["repository_root"],
        source_mount=build_args["source_mount"],
        asset_root=build_args["asset_root"],
        config_path=build_args["config_path"],
        register_path=build_args["register_path"],
        config=build_args["config"],
        source_root=source_root,
    )
    return repository_root, authority, source_root


def _open_review_task(
    args: Any,
) -> tuple[Path, ComparativeReviewAuthority, Path, dict[str, Any]]:
    repository_root, bundle, source_root = _open_review_authority(args)
    task = _read_review_json(args.task, repository_root)
    errors = validate_pair_review_task(task, bundle, source_root)
    if errors:
        raise ValueError("PAIR_REVIEW_TASK_INVALID:" + ",".join(errors))
    return repository_root, bundle, source_root, task


def _review_main(args: Any) -> int:
    if args.command == "create-review-task":
        repository_root, bundle, source_root = _open_review_authority(args)
        _require_review_implementation_publishable(repository_root)
        regions = {
            side: value
            for side, value in (
                ("left", args.left_region),
                ("right", args.right_region),
            )
            if value is not None
        }
        task = build_pair_review_task(
            bundle,
            pair_task_id=args.pair_task_id,
            source_root=source_root,
            regions=regions,
        )
        if task.get("review_implementation_provenance_status") != "clean_git_commit":
            raise ValueError("REVIEW_IMPLEMENTATION_NOT_PUBLISHABLE")
        output = _resolve_review_output(args.output, repository_root)
        _write_review_json_new(output, task, repository_root)
        print(
            _stdout_json(
                {
                    "authority_scope": task["authority_scope"],
                    "ok": True,
                    "output_relpath": _repository_relative_locator(output, repository_root),
                    "receipt_sha256": task["receipt_sha256"],
                    "task_id": task["task_id"],
                    "training_promotion_allowed": False,
                }
            )
        )
        return 0

    repository_root, bundle, source_root, task = _open_review_task(args)
    if args.command == "validate-review-task":
        print(
            _stdout_json(
                {
                    "errors": [],
                    "ok": True,
                    "task_id": task["task_id"],
                    "training_promotion_allowed": False,
                }
            )
        )
        return 0
    if args.command == "seal-review-observation":
        _require_review_implementation_publishable(repository_root)
        draft = _read_review_json(args.draft, repository_root)
        observation = seal_pair_observation(
            task, draft, bundle=bundle, source_root=source_root
        )
        output = _resolve_review_output(args.output, repository_root)
        _write_review_json_new(output, observation, repository_root)
        print(
            _stdout_json(
                {
                    "authority_scope": observation["authority_scope"],
                    "boundary_decision": observation["boundary_decision"],
                    "ok": True,
                    "output_relpath": _repository_relative_locator(output, repository_root),
                    "receipt_sha256": observation["receipt_sha256"],
                    "training_promotion_allowed": False,
                }
            )
        )
        return 0
    if args.command == "validate-review-observation":
        observation = _read_review_json(args.observation, repository_root)
        errors = validate_pair_observation(
            observation, task, bundle=bundle, source_root=source_root
        )
        print(_stdout_json({"errors": errors, "ok": not errors}))
        return 0 if not errors else 1

    primary = _read_review_json(args.primary, repository_root)
    independent = _read_review_json(args.independent, repository_root)
    if args.command == "seal-review-adjudication":
        _require_review_implementation_publishable(repository_root)
        draft = _read_review_json(args.draft, repository_root)
        adjudication = seal_pair_adjudication(
            task,
            primary,
            independent,
            draft,
            bundle=bundle,
            source_root=source_root,
        )
        output = _resolve_review_output(args.output, repository_root)
        _write_review_json_new(output, adjudication, repository_root)
        print(
            _stdout_json(
                {
                    "authority_scope": adjudication["authority_scope"],
                    "boundary_decision": adjudication["boundary_decision"],
                    "ok": True,
                    "output_relpath": _repository_relative_locator(output, repository_root),
                    "receipt_sha256": adjudication["receipt_sha256"],
                    "review_state": adjudication["review_state"],
                    "training_promotion_allowed": False,
                }
            )
        )
        return 0
    adjudication = _read_review_json(args.adjudication, repository_root)
    errors = validate_pair_adjudication(
        adjudication,
        task,
        primary,
        independent,
        bundle=bundle,
        source_root=source_root,
    )
    print(_stdout_json({"errors": errors, "ok": not errors}))
    return 0 if not errors else 1


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(list(sys.argv[1:] if argv is None else argv))
    try:
        if args.command in _REVIEW_COMMANDS:
            return _review_main(args)
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


__all__ = [
    "_resolve_output_root",
    "_resolve_review_output",
    "_write_bundle_new",
    "main",
]
