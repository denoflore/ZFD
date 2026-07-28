"""Command line interface for frozen Stage A page local visual indexing."""

from __future__ import annotations

from argparse import ArgumentParser
from dataclasses import asdict
from pathlib import Path
import sys

from zfd_image_native.io import canonical_json, read_json, write_json

from .core import (
    index_page_candidates,
    resolve_visual_index_output,
    validate_page_local_visual_index,
)
from .stage_a import open_frozen_stage_a_run


def _common(parser: ArgumentParser, *, page: bool = True) -> None:
    parser.add_argument("--repository-root", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--stage-a-root", required=True, type=Path)
    parser.add_argument("--authority-root", required=True, type=Path)
    if page:
        parser.add_argument("--page-id", required=True)


def _parser() -> ArgumentParser:
    parser = ArgumentParser(prog="zfd-visual-index")
    commands = parser.add_subparsers(dest="command", required=True)
    index = commands.add_parser(
        "index-page",
        help="index retained pixel components on one frozen Stage A page",
    )
    _common(index)
    index.add_argument("--output", required=True, type=Path)
    validate = commands.add_parser(
        "validate-page",
        help="rehash pixels, geometry, authority, and one visual index receipt",
    )
    _common(validate)
    validate.add_argument("--receipt", required=True, type=Path)
    stage = commands.add_parser(
        "validate-stage-a",
        help="validate a complete frozen Stage A authority bundle",
    )
    _common(stage, page=False)
    return parser


def main(argv: list[str] | None = None) -> int:
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    args = _parser().parse_args(raw_argv)
    try:
        run = open_frozen_stage_a_run(
            args.stage_a_root,
            authority_root=args.authority_root,
            repository_root=args.repository_root,
            manifest_path=args.manifest,
        )
        if args.command == "validate-stage-a":
            print(
                canonical_json(
                    {
                        "inventory_sha256": run.preservation_receipt.get("inventory_sha256"),
                        "ok": True,
                        "page_count": len(run.page_ids),
                        "run_id": run.run_receipt.get("run_id"),
                    }
                )
            )
            return 0
        if args.command == "index-page":
            page = run.page(args.page_id)
            receipt = index_page_candidates(page)
            target = resolve_visual_index_output(args.output, run)
            write_json(target, receipt)
            print(
                canonical_json(
                    {
                        "accuracy_claim_allowed": receipt.accuracy_claim_allowed,
                        "candidate_count": receipt.candidate_count,
                        "identity_recognition_status": receipt.identity_recognition_status,
                        "output": str(target),
                        "page_id": receipt.page_id,
                        "page_local_exemplar_count": receipt.page_local_exemplar_count,
                        "receipt_sha256": receipt.receipt_sha256,
                        "semantic_class_authority_count": receipt.semantic_class_authority_count,
                    }
                )
            )
            return 0
        receipt = read_json(args.receipt)
        if not isinstance(receipt, dict):
            raise ValueError("VISUAL_INDEX_RECEIPT_MALFORMED")
        if receipt.get("page_id") != args.page_id:
            raise ValueError("PAGE_ID_ARGUMENT_RECEIPT_MISMATCH")
        errors = validate_page_local_visual_index(receipt, run)
        print(canonical_json({"errors": errors, "ok": not errors}))
        return 0 if not errors else 1
    except (OSError, TypeError, ValueError) as error:
        print(canonical_json({"error": str(error), "ok": False}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
