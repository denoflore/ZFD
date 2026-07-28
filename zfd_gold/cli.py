"""Command line surface for image aligned line review receipts."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
import os
import sys
from typing import Any

from zfd_image_native.io import canonical_json, read_json, sha256_file
from zfd_visual_index import (
    open_frozen_stage_a_run,
    resolve_visual_index_output,
    validate_page_local_visual_index,
)

from .core import (
    build_line_task,
    seal_adjudication,
    seal_observation,
    validate_adjudication,
    validate_line_task,
    validate_observation,
)


def _common(parser: ArgumentParser) -> None:
    parser.add_argument("--repository-root", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--stage-a-root", required=True, type=Path)
    parser.add_argument("--authority-root", required=True, type=Path)
    parser.add_argument("--page-id", required=True)
    parser.add_argument("--visual-index-receipt", required=True, type=Path)


def _task_inputs(parser: ArgumentParser) -> None:
    _common(parser)
    parser.add_argument("--task", required=True, type=Path)
    parser.add_argument("--crop", required=True, type=Path)


def _parser() -> ArgumentParser:
    parser = ArgumentParser(prog="zfd-review")
    commands = parser.add_subparsers(dest="command", required=True)

    create = commands.add_parser("create-task", help="create one unlabelled line review task")
    _common(create)
    create.add_argument("--line-id", required=True)
    create.add_argument("--output", required=True, type=Path)
    create.add_argument("--crop-output", required=True, type=Path)

    validate_task = commands.add_parser("validate-task", help="rehash one line review task")
    _task_inputs(validate_task)

    seal_obs = commands.add_parser("seal-observation", help="seal one image only observation draft")
    _task_inputs(seal_obs)
    seal_obs.add_argument("--draft", required=True, type=Path)
    seal_obs.add_argument("--output", required=True, type=Path)

    validate_obs = commands.add_parser("validate-observation", help="validate one sealed observation")
    _task_inputs(validate_obs)
    validate_obs.add_argument("--observation", required=True, type=Path)

    seal_adj = commands.add_parser("seal-adjudication", help="seal two observations and independent adjudication")
    _task_inputs(seal_adj)
    seal_adj.add_argument("--primary", required=True, type=Path)
    seal_adj.add_argument("--reviewer", required=True, type=Path)
    seal_adj.add_argument("--draft", required=True, type=Path)
    seal_adj.add_argument("--output", required=True, type=Path)

    validate_adj = commands.add_parser("validate-adjudication", help="validate a sealed adjudication")
    _task_inputs(validate_adj)
    validate_adj.add_argument("--primary", required=True, type=Path)
    validate_adj.add_argument("--reviewer", required=True, type=Path)
    validate_adj.add_argument("--adjudication", required=True, type=Path)
    return parser


def _inside(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _resolve_input(path: Path, repository_root: Path) -> Path:
    target = path if path.is_absolute() else repository_root / path
    target = target.resolve()
    if not _inside(target, repository_root) or not target.is_file():
        raise ValueError("GOLD_INPUT_MISSING_OR_OUTSIDE_REPOSITORY")
    return target


def _resolve_output(path: Path, run: Any) -> Path:
    target = resolve_visual_index_output(path, run)
    allowed = (
        (run.stage_a_root / "review").resolve(),
        (run.repository_root / "build" / "review").resolve(),
    )
    if not any(_inside(target, root) for root in allowed):
        raise ValueError("GOLD_OUTPUT_OUTSIDE_ALLOWED_ROOT")
    if target.exists() or target.with_name(target.name + ".part").exists():
        raise ValueError("GOLD_OUTPUT_ALREADY_EXISTS")
    return target


def _write_new(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def _write_json_new(path: Path, value: Any) -> None:
    _write_new(path, (canonical_json(value) + "\n").encode("utf-8"))


def _open_inputs(args: Any):
    run = open_frozen_stage_a_run(
        args.stage_a_root,
        authority_root=args.authority_root,
        repository_root=args.repository_root,
        manifest_path=args.manifest,
    )
    page = run.page(args.page_id)
    visual_path = _resolve_input(args.visual_index_receipt, run.repository_root)
    visual = read_json(visual_path)
    if not isinstance(visual, dict):
        raise ValueError("VISUAL_INDEX_RECEIPT_MALFORMED")
    if visual.get("page_id") != args.page_id:
        raise ValueError("PAGE_ID_ARGUMENT_VISUAL_INDEX_MISMATCH")
    visual_errors = validate_page_local_visual_index(visual, run)
    if visual_errors:
        raise ValueError("VISUAL_INDEX_INVALID:" + ",".join(visual_errors))
    return run, page, visual_path, visual


def _open_task(args: Any):
    run, page, visual_path, visual = _open_inputs(args)
    task_path = _resolve_input(args.task, run.repository_root)
    crop_path = _resolve_input(args.crop, run.repository_root)
    task = read_json(task_path)
    crop = crop_path.read_bytes()
    if not isinstance(task, dict):
        raise ValueError("GOLD_TASK_MALFORMED")
    errors = validate_line_task(
        task,
        page,
        visual,
        visual_index_file_sha256=sha256_file(visual_path),
        crop_png=crop,
    )
    if errors:
        raise ValueError("GOLD_TASK_INVALID:" + ",".join(errors))
    return run, page, task, crop


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(list(sys.argv[1:] if argv is None else argv))
    try:
        if args.command == "create-task":
            run, page, visual_path, visual = _open_inputs(args)
            task, crop = build_line_task(
                page,
                visual,
                visual_index_file_sha256=sha256_file(visual_path),
                line_id=args.line_id,
            )
            output = _resolve_output(args.output, run)
            crop_output = _resolve_output(args.crop_output, run)
            if output == crop_output or output in crop_output.parents or crop_output in output.parents:
                raise ValueError("GOLD_TASK_OUTPUT_COLLISION")
            _write_new(crop_output, crop)
            _write_json_new(output, task)
            print(
                canonical_json(
                    {
                        "candidate_count": task["candidate_count"],
                        "crop_output": str(crop_output),
                        "sequence_authority_status": task["sequence_authority_status"],
                        "line_id": task["line_id"],
                        "output": str(output),
                        "page_id": task["page_id"],
                        "receipt_sha256": task["receipt_sha256"],
                        "semantic_class_authority_count": 0,
                    }
                )
            )
            return 0

        run, page, task, crop = _open_task(args)
        if args.command == "validate-task":
            print(canonical_json({"errors": [], "ok": True, "task_id": task["task_id"]}))
            return 0
        image = page.read_image()
        if args.command == "seal-observation":
            draft = read_json(_resolve_input(args.draft, run.repository_root))
            if not isinstance(draft, dict):
                raise ValueError("OBSERVATION_DRAFT_MALFORMED")
            observation = seal_observation(task, draft, image)
            output = _resolve_output(args.output, run)
            _write_json_new(output, observation)
            print(
                canonical_json(
                    {
                        "authority_promotion_eligible": False,
                        "line_state": observation["line_state"],
                        "output": str(output),
                        "receipt_sha256": observation["receipt_sha256"],
                    }
                )
            )
            return 0
        if args.command == "validate-observation":
            observation = read_json(_resolve_input(args.observation, run.repository_root))
            if not isinstance(observation, dict):
                raise ValueError("OBSERVATION_MALFORMED")
            errors = validate_observation(observation, task, image)
            print(canonical_json({"errors": errors, "ok": not errors}))
            return 0 if not errors else 1

        primary = read_json(_resolve_input(args.primary, run.repository_root))
        reviewer = read_json(_resolve_input(args.reviewer, run.repository_root))
        if not isinstance(primary, dict) or not isinstance(reviewer, dict):
            raise ValueError("SOURCE_OBSERVATION_MALFORMED")
        if args.command == "seal-adjudication":
            draft = read_json(_resolve_input(args.draft, run.repository_root))
            if not isinstance(draft, dict):
                raise ValueError("ADJUDICATION_DRAFT_MALFORMED")
            adjudication = seal_adjudication(task, primary, reviewer, draft, image)
            output = _resolve_output(args.output, run)
            _write_json_new(output, adjudication)
            print(
                canonical_json(
                    {
                        "authority_promotion_eligible": False,
                        "output": str(output),
                        "receipt_sha256": adjudication["receipt_sha256"],
                        "review_state": adjudication["review_state"],
                        "diplomatic_sequence_authority_eligible": False,
                    }
                )
            )
            return 0
        adjudication = read_json(_resolve_input(args.adjudication, run.repository_root))
        if not isinstance(adjudication, dict):
            raise ValueError("ADJUDICATION_MALFORMED")
        errors = validate_adjudication(adjudication, task, primary, reviewer, image)
        print(canonical_json({"errors": errors, "ok": not errors}))
        return 0 if not errors else 1
    except (KeyError, OSError, TypeError, ValueError) as error:
        print(canonical_json({"error": str(error), "ok": False}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
