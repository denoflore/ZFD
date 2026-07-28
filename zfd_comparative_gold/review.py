"""Pixel bound, blinded review of comparative pilot hand boundaries."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any, Mapping, Sequence

from PIL import Image

from .core import (
    ComparativeQueueConfig,
    HandBoundaryQueueBundle,
    _git_state,
    validate_hand_boundary_queue,
)


SCHEMA_VERSION = "1.0.0"
TASK_SCHEMA = "zfd.comparative_hand_pair_review_task.v1"
OBSERVATION_DRAFT_SCHEMA = "zfd.comparative_hand_pair_observation_draft.v1"
OBSERVATION_SCHEMA = "zfd.comparative_hand_pair_observation.v1"
ADJUDICATION_DRAFT_SCHEMA = "zfd.comparative_hand_pair_adjudication_draft.v1"
ADJUDICATION_SCHEMA = "zfd.comparative_hand_pair_adjudication.v1"

BOUNDARY_DECISIONS = frozenset(("same_hand", "different_hand", "uncertain"))
CERTAINTY_LEVELS = frozenset(("high", "moderate", "low"))
REVIEW_ROLES = frozenset(("primary", "independent_reviewer"))
EVIDENCE_CODES = frozenset(
    (
        "ductus_consistent",
        "ductus_shift",
        "stroke_angle_consistent",
        "stroke_angle_shift",
        "pen_width_consistent",
        "pen_width_shift",
        "spacing_consistent",
        "spacing_shift",
        "letterform_construction_consistent",
        "letterform_construction_shift",
        "insufficient_comparable_forms",
        "region_quality_limit",
    )
)
UNCERTAINTY_CODES = frozenset(
    (
        "limited_visible_forms",
        "image_quality_limit",
        "region_quality_limit",
        "mixed_signals",
        "possible_pen_or_posture_change",
        "possible_temporal_variation",
        "reviewer_disagreement",
        "insufficient_evidence",
    )
)
RATIONALE_CODES = frozenset(
    (
        "observations_agree",
        "visible_form_evidence_supports_same",
        "visible_form_evidence_supports_difference",
        "evidence_remains_equivocal",
    )
)
CONFLICT_RESOLUTION_CODES = frozenset(
    (
        "resolved_by_ductus",
        "resolved_by_letterform_construction",
        "resolved_by_stroke_angle",
        "resolved_by_spacing",
        "resolved_by_region_quality",
    )
)
_SHA256_ID = re.compile(r"sha256:[0-9a-f]{64}")
_RAW_SHA256 = re.compile(r"[0-9a-f]{64}")
_IDENTITY_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:@/-]{2,127}")
_SAME_HAND_EVIDENCE = frozenset(
    code for code in EVIDENCE_CODES if code.endswith("_consistent")
)
_DIFFERENT_HAND_EVIDENCE = frozenset(
    code for code in EVIDENCE_CODES if code.endswith("_shift")
)
_RATIONALE_BY_DECISION = {
    "same_hand": frozenset(("observations_agree", "visible_form_evidence_supports_same")),
    "different_hand": frozenset(
        ("observations_agree", "visible_form_evidence_supports_difference")
    ),
    "uncertain": frozenset(("observations_agree", "evidence_remains_equivocal")),
}

_OBSERVATION_DRAFT_FIELDS = frozenset(
    (
        "schema",
        "task_id",
        "reviewer_id",
        "review_role",
        "source_lane",
        "inherited_text_used",
        "other_observation_seen",
        "boundary_decision",
        "certainty",
        "evidence_codes",
        "uncertainty_codes",
    )
)
_ADJUDICATION_DRAFT_FIELDS = frozenset(
    (
        "schema",
        "task_id",
        "primary_observation_receipt_sha256",
        "independent_observation_receipt_sha256",
        "adjudicator_id",
        "source_lane",
        "inherited_text_used",
        "source_observations_reviewed",
        "boundary_decision",
        "certainty",
        "rationale_codes",
        "uncertainty_codes",
        "conflict_resolution_codes",
    )
)


@dataclass(frozen=True)
class ComparativeReviewAuthority:
    """Full registered queue validation context for comparative review."""

    bundle: HandBoundaryQueueBundle
    repository_root: Path
    source_mount: Path
    asset_root: Path
    config_path: Path
    register_path: Path
    config: ComparativeQueueConfig
    source_root: Path

    @property
    def rows(self) -> list[dict[str, Any]]:
        return self.bundle.rows

    @property
    def pilot(self) -> list[dict[str, Any]]:
        return self.bundle.pilot

    @property
    def summary(self) -> dict[str, Any]:
        return self.bundle.summary


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _canonical_bytes(value: Any) -> bytes:
    return _canonical_json(value).encode("utf-8")


def _value_sha256(value: Any) -> str:
    return sha256(_canonical_bytes(value)).hexdigest()


def _domain_id(domain: str, value: Any) -> str:
    digest = sha256(domain.encode("ascii") + b"\0" + _canonical_bytes(value)).hexdigest()
    return "sha256:" + digest


def _receipt(payload: Mapping[str, Any]) -> dict[str, Any]:
    body = {key: value for key, value in payload.items() if key != "receipt_sha256"}
    return {**body, "receipt_sha256": _value_sha256(body)}


def _receipt_valid(payload: Any) -> bool:
    if not isinstance(payload, Mapping):
        return False
    supplied = payload.get("receipt_sha256")
    body = {key: value for key, value in payload.items() if key != "receipt_sha256"}
    return isinstance(supplied, str) and supplied == _value_sha256(body)


def _jsonl_sha256(rows: Sequence[Mapping[str, Any]]) -> str:
    payload = b"".join(_canonical_bytes(dict(row)) + b"\n" for row in rows)
    return sha256(payload).hexdigest()


def _review_implementation_sha256() -> str:
    return "sha256:" + sha256(Path(__file__).resolve().read_bytes()).hexdigest()


def _inside(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _authority_errors(authority: ComparativeReviewAuthority) -> tuple[str, ...]:
    if not isinstance(authority, ComparativeReviewAuthority):
        return ("COMPARATIVE_REVIEW_AUTHORITY_REQUIRED",)
    errors = validate_hand_boundary_queue(
        authority.bundle,
        repository_root=authority.repository_root,
        source_mount=authority.source_mount,
        asset_root=authority.asset_root,
        config_path=authority.config_path,
        register_path=authority.register_path,
        config=authority.config,
    )
    if not authority.source_root.is_dir() or not _inside(
        authority.source_root, authority.source_mount
    ):
        errors = (*errors, "COMPARATIVE_REVIEW_SOURCE_ROOT_INVALID")
    return tuple(dict.fromkeys(errors))


def open_comparative_review_authority(
    bundle: HandBoundaryQueueBundle,
    *,
    repository_root: Path,
    source_mount: Path,
    asset_root: Path,
    config_path: Path,
    register_path: Path,
    config: ComparativeQueueConfig,
    source_root: Path,
) -> ComparativeReviewAuthority:
    authority = ComparativeReviewAuthority(
        bundle=bundle,
        repository_root=Path(repository_root).resolve(),
        source_mount=Path(source_mount).resolve(),
        asset_root=Path(asset_root).resolve(),
        config_path=Path(config_path).resolve(),
        register_path=Path(register_path).resolve(),
        config=config,
        source_root=Path(source_root).resolve(),
    )
    errors = _authority_errors(authority)
    if errors:
        raise ValueError("COMPARATIVE_REVIEW_AUTHORITY_INVALID:" + ",".join(errors))
    return authority


def _validated_authority(
    authority: ComparativeReviewAuthority, source_root: Path
) -> HandBoundaryQueueBundle:
    if not isinstance(authority, ComparativeReviewAuthority):
        raise ValueError("COMPARATIVE_REVIEW_AUTHORITY_REQUIRED")
    if Path(source_root).resolve() != authority.source_root:
        raise ValueError("COMPARATIVE_REVIEW_SOURCE_ROOT_MISMATCH")
    errors = _authority_errors(authority)
    if errors:
        raise ValueError("COMPARATIVE_REVIEW_AUTHORITY_INVALID:" + ",".join(errors))
    return authority.bundle


def _safe_source_path(source_root: Path, locator: Any) -> Path:
    if not isinstance(locator, str) or not locator or "\\" in locator:
        raise ValueError("SOURCE_IMAGE_LOCATOR_INVALID")
    relative = PurePosixPath(locator)
    if relative.is_absolute() or "." in relative.parts or ".." in relative.parts:
        raise ValueError("SOURCE_IMAGE_LOCATOR_INVALID")
    root = source_root.resolve()
    target = root.joinpath(*relative.parts).resolve()
    if not _inside(target, root) or not target.is_file():
        raise ValueError("SOURCE_IMAGE_MISSING_OR_OUTSIDE_ROOT")
    return target


def _queue_errors(bundle: HandBoundaryQueueBundle) -> tuple[str, ...]:
    errors: list[str] = []
    if not isinstance(bundle, HandBoundaryQueueBundle):
        return ("QUEUE_BUNDLE_MALFORMED",)
    if not _receipt_valid(bundle.summary):
        errors.append("QUEUE_SUMMARY_RECEIPT_HASH_MISMATCH")
    for ordinal, row in enumerate(bundle.rows):
        if not _receipt_valid(row):
            errors.append(f"QUEUE_ROW_RECEIPT_HASH_MISMATCH:{ordinal}")
    for ordinal, row in enumerate(bundle.pilot):
        if not _receipt_valid(row):
            errors.append(f"PILOT_ROW_RECEIPT_HASH_MISMATCH:{ordinal}")
    summary = bundle.summary
    queue_id = summary.get("queue_id")
    pilot_id = summary.get("pilot_id")
    if summary.get("queue_row_count") != len(bundle.rows):
        errors.append("QUEUE_ROW_COUNT_MISMATCH")
    if summary.get("pilot_pair_count") != len(bundle.pilot):
        errors.append("PILOT_ROW_COUNT_MISMATCH")
    if summary.get("queue_rows_sha256") != _jsonl_sha256(bundle.rows):
        errors.append("QUEUE_ROWS_HASH_MISMATCH")
    if summary.get("pilot_rows_sha256") != _jsonl_sha256(bundle.pilot):
        errors.append("PILOT_ROWS_HASH_MISMATCH")
    if (
        summary.get("training_ready_asset_count") != 0
        or summary.get("hand_boundary_authority_complete") is not False
        or summary.get("split_lineage_authority_complete") is not False
        or summary.get("ocr_accuracy_claim_allowed") is not False
        or summary.get("inherited_text_used") is not False
    ):
        errors.append("QUEUE_AUTHORITY_STATE_INVALID")

    item_ids: set[Any] = set()
    for row in bundle.rows:
        item_id = row.get("queue_item_id")
        if item_id in item_ids:
            errors.append("QUEUE_ITEM_ID_DUPLICATE")
        item_ids.add(item_id)
        if (
            row.get("queue_id") != queue_id
            or row.get("hand_identity_state") != "unknown_unreviewed"
            or row.get("hand_id") is not None
            or row.get("split_assignment_state") != "blocked_unknown_hand"
            or row.get("training_eligible") is not False
            or row.get("training_promotion_allowed") is not False
            or row.get("inherited_text_used") is not False
        ):
            errors.append(f"QUEUE_ROW_AUTHORITY_STATE_INVALID:{row.get('ordinal')}")

    for pilot_ordinal, pilot in enumerate(bundle.pilot):
        left = pilot.get("left_ordinal")
        right = pilot.get("right_ordinal")
        if (
            type(left) is not int
            or type(right) is not int
            or left < 0
            or right >= len(bundle.rows)
            or right != left + 1
        ):
            errors.append(f"PILOT_ROW_ORDINAL_INVALID:{pilot_ordinal}")
            continue
        left_row = bundle.rows[left]
        right_row = bundle.rows[right]
        expected = {
            "pilot_id": pilot_id,
            "left_queue_item_id": left_row.get("queue_item_id"),
            "right_queue_item_id": right_row.get("queue_item_id"),
            "left_asset_id": left_row.get("asset_id"),
            "right_asset_id": right_row.get("asset_id"),
            "left_canvas_id": left_row.get("canvas_id"),
            "right_canvas_id": right_row.get("canvas_id"),
            "left_image_sha256": left_row.get("image_sha256"),
            "right_image_sha256": right_row.get("image_sha256"),
            "left_local_relpath": left_row.get("local_relpath"),
            "right_local_relpath": right_row.get("local_relpath"),
        }
        if any(pilot.get(field) != value for field, value in expected.items()):
            errors.append(f"PILOT_ROW_QUEUE_JOIN_INVALID:{pilot_ordinal}")
        if (
            pilot.get("review_state") != "unreviewed"
            or pilot.get("boundary_decision") is not None
            or pilot.get("whole_manuscript_boundary_authority_allowed") is not False
            or pilot.get("training_promotion_allowed") is not False
            or pilot.get("inherited_text_used") is not False
        ):
            errors.append(f"PILOT_ROW_AUTHORITY_STATE_INVALID:{pilot_ordinal}")
    return tuple(dict.fromkeys(errors))


def _region_xywh(side: str, supplied: Any, width: int, height: int) -> tuple[str, list[int]]:
    if supplied is None:
        return "full_page", [0, 0, width, height]
    if (
        not isinstance(supplied, Sequence)
        or isinstance(supplied, (str, bytes, bytearray))
        or len(supplied) != 4
        or any(type(value) is not int for value in supplied)
    ):
        raise ValueError(f"REVIEW_REGION_GEOMETRY_INVALID:{side}")
    x, y, region_width, region_height = supplied
    if (
        x < 0
        or y < 0
        or region_width <= 0
        or region_height <= 0
        or x + region_width > width
        or y + region_height > height
    ):
        raise ValueError(f"REVIEW_REGION_GEOMETRY_INVALID:{side}")
    return "explicit_region", [x, y, region_width, region_height]


def _pixel_hash(domain: str, image: Image.Image, context: Mapping[str, Any]) -> str:
    rgb = image.convert("RGB")
    digest = sha256()
    digest.update(domain.encode("ascii"))
    digest.update(b"\0")
    digest.update(_canonical_bytes({**context, "mode": "RGB", "size": list(rgb.size)}))
    digest.update(b"\0")
    digest.update(rgb.tobytes())
    return "sha256:" + digest.hexdigest()


def _side_binding(
    side: str,
    row: Mapping[str, Any],
    source_root: Path,
    supplied_region: Any,
) -> dict[str, Any]:
    width = row.get("width")
    height = row.get("height")
    if type(width) is not int or type(height) is not int or width <= 0 or height <= 0:
        raise ValueError(f"QUEUE_IMAGE_DIMENSIONS_INVALID:{side}")
    geometry_kind, xywh = _region_xywh(side, supplied_region, width, height)
    path = _safe_source_path(source_root, row.get("local_relpath"))
    source_bytes = path.read_bytes()
    if sha256(source_bytes).hexdigest() != row.get("image_sha256"):
        raise ValueError(f"SOURCE_IMAGE_BYTES_MISMATCH:{side}")
    if len(source_bytes) != row.get("byte_length"):
        raise ValueError(f"SOURCE_IMAGE_LENGTH_MISMATCH:{side}")
    try:
        with Image.open(BytesIO(source_bytes)) as opened:
            opened.load()
            image = opened.convert("RGB")
    except (OSError, ValueError) as error:
        raise ValueError(f"SOURCE_IMAGE_DECODE_FAILED:{side}") from error
    if image.size != (width, height):
        raise ValueError(f"SOURCE_IMAGE_DIMENSIONS_MISMATCH:{side}")
    x, y, region_width, region_height = xywh
    crop = image.crop((x, y, x + region_width, y + region_height))
    geometry = {"kind": geometry_kind, "xywh": xywh}
    return {
        "side": side,
        "queue_item_id": row.get("queue_item_id"),
        "queue_row_receipt_sha256": row.get("receipt_sha256"),
        "asset_id": row.get("asset_id"),
        "asset_receipt_sha256": row.get("asset_receipt_sha256"),
        "canvas_id": row.get("canvas_id"),
        "source_local_relpath": row.get("local_relpath"),
        "source_image_sha256": row.get("image_sha256"),
        "source_byte_length": row.get("byte_length"),
        "decoded_mode": "RGB",
        "decoded_width": width,
        "decoded_height": height,
        "decoded_pixel_sha256": _pixel_hash(
            "zfd.comparative_decoded_rgb.v1",
            image,
            {"source_image_sha256": row.get("image_sha256")},
        ),
        "geometry": geometry,
        "region_pixel_sha256": _pixel_hash(
            "zfd.comparative_review_region_rgb.v1",
            crop,
            {
                "source_image_sha256": row.get("image_sha256"),
                "geometry": geometry,
            },
        ),
    }


def _image_bindings(task: Mapping[str, Any]) -> dict[str, Any]:
    sides = task.get("sides")
    if not isinstance(sides, Mapping):
        raise ValueError("PAIR_REVIEW_TASK_SIDES_INVALID")
    result: dict[str, Any] = {}
    for side in ("left", "right"):
        binding = sides.get(side)
        if not isinstance(binding, Mapping):
            raise ValueError(f"PAIR_REVIEW_TASK_SIDE_INVALID:{side}")
        source_hash = binding.get("source_image_sha256")
        derived_hashes = (
            binding.get("decoded_pixel_sha256"),
            binding.get("region_pixel_sha256"),
        )
        if (
            not isinstance(source_hash, str)
            or _RAW_SHA256.fullmatch(source_hash) is None
            or any(
                not isinstance(value, str) or _SHA256_ID.fullmatch(value) is None
                for value in derived_hashes
            )
        ):
            raise ValueError(f"PAIR_REVIEW_TASK_PIXEL_BINDING_INVALID:{side}")
        geometry = binding.get("geometry")
        if not isinstance(geometry, Mapping) or set(geometry) != {"kind", "xywh"}:
            raise ValueError(f"PAIR_REVIEW_TASK_GEOMETRY_INVALID:{side}")
        xywh = geometry.get("xywh")
        if (
            geometry.get("kind") not in {"full_page", "explicit_region"}
            or not isinstance(xywh, list)
            or len(xywh) != 4
            or any(type(value) is not int for value in xywh)
            or xywh[0] < 0
            or xywh[1] < 0
            or xywh[2] <= 0
            or xywh[3] <= 0
        ):
            raise ValueError(f"PAIR_REVIEW_TASK_GEOMETRY_INVALID:{side}")
        result[side] = {
            "source_image_sha256": binding.get("source_image_sha256"),
            "decoded_pixel_sha256": binding.get("decoded_pixel_sha256"),
            "region_pixel_sha256": binding.get("region_pixel_sha256"),
            "geometry": binding.get("geometry"),
        }
    return result


def build_pair_review_task(
    authority: ComparativeReviewAuthority,
    *,
    pair_task_id: str,
    source_root: Path,
    regions: Mapping[str, Sequence[int]] | None = None,
) -> dict[str, Any]:
    bundle = _validated_authority(authority, source_root)
    queue_errors = _queue_errors(bundle)
    if queue_errors:
        raise ValueError("QUEUE_BUNDLE_INVALID:" + ",".join(queue_errors))
    matches = [row for row in bundle.pilot if row.get("pair_task_id") == pair_task_id]
    if len(matches) != 1:
        raise ValueError("PILOT_PAIR_TASK_NOT_FOUND")
    if regions is not None and (
        not isinstance(regions, Mapping) or not set(regions).issubset({"left", "right"})
    ):
        raise ValueError("REVIEW_REGIONS_INVALID")
    pilot = matches[0]
    left_row = bundle.rows[pilot["left_ordinal"]]
    right_row = bundle.rows[pilot["right_ordinal"]]
    supplied = {} if regions is None else regions
    sides = {
        "left": _side_binding("left", left_row, Path(source_root), supplied.get("left")),
        "right": _side_binding("right", right_row, Path(source_root), supplied.get("right")),
    }
    source_binding_sha256 = _domain_id(
        "zfd.comparative_hand_pair_source_binding.v1", sides
    )
    review_git_commit, review_git_dirty = _git_state()
    review_implementation_sha256 = _review_implementation_sha256()
    if review_git_commit is not None and review_git_dirty is False:
        review_provenance_status = "clean_git_commit"
    elif review_git_commit is None and review_git_dirty is None:
        review_provenance_status = "unversioned_current_bytes"
    else:
        review_provenance_status = "dirty_or_malformed"
    identity = {
        "queue_id": bundle.summary["queue_id"],
        "queue_summary_receipt_sha256": bundle.summary["receipt_sha256"],
        "pilot_row_receipt_sha256": pilot["receipt_sha256"],
        "pair_task_id": pair_task_id,
        "source_binding_sha256": source_binding_sha256,
        "review_implementation_sha256": review_implementation_sha256,
        "review_implementation_git_commit": review_git_commit,
        "review_implementation_git_worktree_dirty": review_git_dirty,
        "review_implementation_provenance_status": review_provenance_status,
    }
    task_id = _domain_id("zfd.comparative_hand_pair_review_task.v1", identity)
    payload = {
        "schema": TASK_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "task_id": task_id,
        **identity,
        "source_id": bundle.summary.get("source_id"),
        "pilot_id": pilot.get("pilot_id"),
        "pilot_ordinal": pilot.get("pilot_ordinal"),
        "sides": sides,
        "review_question": "adjacent_page_hand_boundary",
        "allowed_boundary_decisions": sorted(BOUNDARY_DECISIONS),
        "blinding_state": "workflow_requires_independent_observations",
        "blinding_enforced": False,
        "commitment_before_reveal_enforced": False,
        "identity_authority_state": "self_asserted_unverified",
        "authority_scope": "pilot_pair_task_only",
        "inherited_text_used": False,
        "named_hand_authority_allowed": False,
        "whole_manuscript_hand_authority_allowed": False,
        "training_eligible": False,
        "training_promotion_allowed": False,
        "split_assignment_allowed": False,
        "ocr_accuracy_claim_allowed": False,
        "translation_claim_allowed": False,
        "qualified_review_authority_allowed": False,
        "scientific_boundary_authority_allowed": False,
    }
    return _receipt(payload)


def _task_regions(task: Mapping[str, Any]) -> dict[str, Sequence[int]]:
    sides = task.get("sides")
    if not isinstance(sides, Mapping):
        raise ValueError("PAIR_REVIEW_TASK_SIDES_INVALID")
    regions: dict[str, Sequence[int]] = {}
    for side in ("left", "right"):
        binding = sides.get(side)
        geometry = binding.get("geometry") if isinstance(binding, Mapping) else None
        if not isinstance(geometry, Mapping):
            raise ValueError(f"PAIR_REVIEW_TASK_GEOMETRY_INVALID:{side}")
        kind = geometry.get("kind")
        xywh = geometry.get("xywh")
        if kind == "explicit_region":
            regions[side] = xywh
        elif kind != "full_page":
            raise ValueError(f"PAIR_REVIEW_TASK_GEOMETRY_INVALID:{side}")
    return regions


def validate_pair_review_task(
    task: Mapping[str, Any],
    authority: ComparativeReviewAuthority,
    source_root: Path,
) -> tuple[str, ...]:
    errors: list[str] = []
    if not _receipt_valid(task):
        errors.append("PAIR_REVIEW_TASK_RECEIPT_HASH_MISMATCH")
    if not isinstance(task, Mapping):
        errors.append("PAIR_REVIEW_TASK_MALFORMED")
        return tuple(dict.fromkeys(errors))
    try:
        bundle = _validated_authority(authority, source_root)
    except (OSError, TypeError, ValueError) as error:
        errors.append(str(error))
        return tuple(dict.fromkeys(errors))
    errors.extend(_queue_errors(bundle))
    if errors and any(error.startswith(("QUEUE_", "PILOT_ROW_")) for error in errors):
        return tuple(dict.fromkeys(errors))
    try:
        expected = build_pair_review_task(
            authority,
            pair_task_id=task.get("pair_task_id"),
            source_root=source_root,
            regions=_task_regions(task),
        )
        if _canonical_json(dict(task)) != _canonical_json(expected):
            errors.append("PAIR_REVIEW_TASK_RECOMPUTE_MISMATCH")
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as error:
        errors.append(str(error))
    return tuple(dict.fromkeys(errors))


def _identity(value: Any, code: str) -> str:
    if (
        not isinstance(value, str)
        or value != value.strip()
        or not value.isascii()
        or _IDENTITY_ID.fullmatch(value) is None
    ):
        raise ValueError(code)
    return value


def _controlled_list(
    value: Any,
    allowed: frozenset[str],
    code: str,
    *,
    required: bool = False,
) -> list[str]:
    if (
        not isinstance(value, list)
        or any(not isinstance(item, str) or item not in allowed for item in value)
        or len(set(value)) != len(value)
        or (required and not value)
    ):
        raise ValueError(code)
    return list(value)


def _task_ready_for_review(
    task: Mapping[str, Any],
    bundle: ComparativeReviewAuthority,
    source_root: Path,
) -> None:
    errors = validate_pair_review_task(task, bundle, source_root)
    if errors or task.get("schema") != TASK_SCHEMA:
        raise ValueError("PAIR_REVIEW_TASK_INVALID:" + ",".join(errors))
    if (
        task.get("inherited_text_used") is not False
        or task.get("named_hand_authority_allowed") is not False
        or task.get("whole_manuscript_hand_authority_allowed") is not False
        or task.get("training_eligible") is not False
        or task.get("training_promotion_allowed") is not False
        or task.get("split_assignment_allowed") is not False
        or task.get("ocr_accuracy_claim_allowed") is not False
        or task.get("translation_claim_allowed") is not False
        or task.get("qualified_review_authority_allowed") is not False
        or task.get("scientific_boundary_authority_allowed") is not False
    ):
        raise ValueError("PAIR_REVIEW_TASK_AUTHORITY_STATE_INVALID")
    _image_bindings(task)


def seal_pair_observation(
    task: Mapping[str, Any],
    draft: Mapping[str, Any],
    *,
    bundle: ComparativeReviewAuthority,
    source_root: Path,
) -> dict[str, Any]:
    _task_ready_for_review(task, bundle, source_root)
    if not isinstance(draft, Mapping) or set(draft) != _OBSERVATION_DRAFT_FIELDS:
        raise ValueError("OBSERVATION_DRAFT_FIELDS_INVALID")
    if draft.get("schema") != OBSERVATION_DRAFT_SCHEMA or draft.get("task_id") != task.get("task_id"):
        raise ValueError("OBSERVATION_DRAFT_TASK_JOIN_INVALID")
    reviewer_id = _identity(draft.get("reviewer_id"), "REVIEWER_IDENTITY_INVALID")
    role = draft.get("review_role")
    if role not in REVIEW_ROLES:
        raise ValueError("REVIEW_ROLE_INVALID")
    if (
        draft.get("source_lane") != "human_image_only_blinded"
        or draft.get("inherited_text_used") is not False
        or draft.get("other_observation_seen") is not False
    ):
        raise ValueError("OBSERVATION_SOURCE_LANE_TAINTED")
    decision = draft.get("boundary_decision")
    if decision not in BOUNDARY_DECISIONS:
        raise ValueError("BOUNDARY_DECISION_INVALID")
    certainty = draft.get("certainty")
    if certainty not in CERTAINTY_LEVELS:
        raise ValueError("OBSERVATION_CERTAINTY_INVALID")
    evidence_codes = _controlled_list(
        draft.get("evidence_codes"), EVIDENCE_CODES, "OBSERVATION_EVIDENCE_CODES_INVALID", required=True
    )
    uncertainty_codes = _controlled_list(
        draft.get("uncertainty_codes"),
        UNCERTAINTY_CODES,
        "OBSERVATION_UNCERTAINTY_CODES_INVALID",
    )
    if (decision == "uncertain" or certainty != "high") and not uncertainty_codes:
        raise ValueError("OBSERVATION_UNCERTAINTY_REQUIRED")
    if certainty == "high" and uncertainty_codes:
        raise ValueError("OBSERVATION_CERTAINTY_UNCERTAINTY_CONTRADICTION")
    if decision == "same_hand" and (
        not set(evidence_codes).issubset(_SAME_HAND_EVIDENCE) or not evidence_codes
    ):
        raise ValueError("OBSERVATION_EVIDENCE_DECISION_CONTRADICTION")
    if decision == "different_hand" and (
        not set(evidence_codes).issubset(_DIFFERENT_HAND_EVIDENCE) or not evidence_codes
    ):
        raise ValueError("OBSERVATION_EVIDENCE_DECISION_CONTRADICTION")
    image_bindings = _image_bindings(task)
    payload = {
        "schema": OBSERVATION_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "task_id": task["task_id"],
        "task_receipt_sha256": task["receipt_sha256"],
        "queue_id": task["queue_id"],
        "pair_task_id": task["pair_task_id"],
        "source_binding_sha256": task["source_binding_sha256"],
        "review_implementation_sha256": task["review_implementation_sha256"],
        "review_implementation_git_commit": task["review_implementation_git_commit"],
        "review_implementation_git_worktree_dirty": task[
            "review_implementation_git_worktree_dirty"
        ],
        "image_bindings": image_bindings,
        "reviewer_id": reviewer_id,
        "review_role": role,
        "source_lane": "human_image_only_blinded",
        "inherited_text_used": False,
        "other_observation_seen": False,
        "blinding_state": "self_attested_other_observation_not_seen",
        "blinding_verified": False,
        "identity_authority_state": "self_asserted_unverified",
        "boundary_decision": decision,
        "certainty": certainty,
        "evidence_codes": evidence_codes,
        "uncertainty_codes": uncertainty_codes,
        "authority_scope": "pilot_pair_observation_only",
        "named_hand_authority_allowed": False,
        "whole_manuscript_hand_authority_allowed": False,
        "training_eligible": False,
        "training_promotion_allowed": False,
        "split_assignment_allowed": False,
        "ocr_accuracy_claim_allowed": False,
        "translation_claim_allowed": False,
        "qualified_review_authority_allowed": False,
        "scientific_boundary_authority_allowed": False,
    }
    observation_id = _domain_id(
        "zfd.comparative_hand_pair_observation.v1",
        {
            "task_id": task["task_id"],
            "reviewer_id": reviewer_id,
            "review_role": role,
            "boundary_decision": decision,
            "certainty": certainty,
            "evidence_codes": evidence_codes,
            "uncertainty_codes": uncertainty_codes,
        },
    )
    return _receipt({**payload, "observation_id": observation_id})


def _observation_draft(observation: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": OBSERVATION_DRAFT_SCHEMA,
        "task_id": observation.get("task_id"),
        "reviewer_id": observation.get("reviewer_id"),
        "review_role": observation.get("review_role"),
        "source_lane": observation.get("source_lane"),
        "inherited_text_used": observation.get("inherited_text_used"),
        "other_observation_seen": observation.get("other_observation_seen"),
        "boundary_decision": observation.get("boundary_decision"),
        "certainty": observation.get("certainty"),
        "evidence_codes": observation.get("evidence_codes"),
        "uncertainty_codes": observation.get("uncertainty_codes"),
    }


def validate_pair_observation(
    observation: Mapping[str, Any],
    task: Mapping[str, Any],
    *,
    bundle: ComparativeReviewAuthority,
    source_root: Path,
) -> tuple[str, ...]:
    errors: list[str] = []
    if not _receipt_valid(observation):
        errors.append("OBSERVATION_RECEIPT_HASH_MISMATCH")
    if not isinstance(observation, Mapping):
        errors.append("OBSERVATION_MALFORMED")
        return tuple(dict.fromkeys(errors))
    try:
        expected = seal_pair_observation(
            task,
            _observation_draft(observation),
            bundle=bundle,
            source_root=source_root,
        )
        if _canonical_json(dict(observation)) != _canonical_json(expected):
            errors.append("OBSERVATION_RECOMPUTE_MISMATCH")
    except (AttributeError, KeyError, TypeError, ValueError) as error:
        errors.append(f"OBSERVATION_RECOMPUTE_FAILED:{error}")
    return tuple(dict.fromkeys(errors))


def _validated_source_observations(
    task: Mapping[str, Any],
    primary: Mapping[str, Any],
    independent: Mapping[str, Any],
    bundle: ComparativeReviewAuthority,
    source_root: Path,
) -> tuple[str, str]:
    primary_errors = validate_pair_observation(
        primary, task, bundle=bundle, source_root=source_root
    )
    independent_errors = validate_pair_observation(
        independent, task, bundle=bundle, source_root=source_root
    )
    if primary_errors or independent_errors:
        raise ValueError(
            "SOURCE_OBSERVATION_INVALID:"
            + ",".join((*primary_errors, *independent_errors))
        )
    if primary.get("review_role") != "primary" or independent.get("review_role") != "independent_reviewer":
        raise ValueError("SOURCE_OBSERVATION_ROLES_INVALID")
    primary_id = _identity(primary.get("reviewer_id"), "REVIEWER_IDENTITY_INVALID")
    independent_id = _identity(independent.get("reviewer_id"), "REVIEWER_IDENTITY_INVALID")
    if primary_id.casefold() == independent_id.casefold():
        raise ValueError("REVIEW_IDENTITIES_NOT_DISTINCT")
    return primary_id, independent_id


def seal_pair_adjudication(
    task: Mapping[str, Any],
    primary: Mapping[str, Any],
    independent: Mapping[str, Any],
    draft: Mapping[str, Any],
    *,
    bundle: ComparativeReviewAuthority,
    source_root: Path,
) -> dict[str, Any]:
    _task_ready_for_review(task, bundle, source_root)
    primary_id, independent_id = _validated_source_observations(
        task, primary, independent, bundle, source_root
    )
    if not isinstance(draft, Mapping) or set(draft) != _ADJUDICATION_DRAFT_FIELDS:
        raise ValueError("ADJUDICATION_DRAFT_FIELDS_INVALID")
    if draft.get("schema") != ADJUDICATION_DRAFT_SCHEMA or draft.get("task_id") != task.get("task_id"):
        raise ValueError("ADJUDICATION_DRAFT_TASK_JOIN_INVALID")
    if (
        draft.get("primary_observation_receipt_sha256") != primary.get("receipt_sha256")
        or draft.get("independent_observation_receipt_sha256") != independent.get("receipt_sha256")
    ):
        raise ValueError("ADJUDICATION_OBSERVATION_JOIN_MISMATCH")
    adjudicator_id = _identity(draft.get("adjudicator_id"), "ADJUDICATOR_IDENTITY_INVALID")
    if len({primary_id.casefold(), independent_id.casefold(), adjudicator_id.casefold()}) != 3:
        raise ValueError("REVIEW_IDENTITIES_NOT_DISTINCT")
    if (
        draft.get("source_lane") != "human_image_only_adjudication"
        or draft.get("inherited_text_used") is not False
        or draft.get("source_observations_reviewed") is not True
    ):
        raise ValueError("ADJUDICATION_SOURCE_LANE_TAINTED")
    decision = draft.get("boundary_decision")
    if decision not in BOUNDARY_DECISIONS:
        raise ValueError("BOUNDARY_DECISION_INVALID")
    certainty = draft.get("certainty")
    if certainty not in CERTAINTY_LEVELS:
        raise ValueError("ADJUDICATION_CERTAINTY_INVALID")
    rationale_codes = _controlled_list(
        draft.get("rationale_codes"), RATIONALE_CODES, "ADJUDICATION_RATIONALE_CODES_INVALID", required=True
    )
    uncertainty_codes = _controlled_list(
        draft.get("uncertainty_codes"),
        UNCERTAINTY_CODES,
        "ADJUDICATION_UNCERTAINTY_CODES_INVALID",
    )
    conflict_codes = _controlled_list(
        draft.get("conflict_resolution_codes"),
        CONFLICT_RESOLUTION_CODES,
        "ADJUDICATION_CONFLICT_CODES_INVALID",
    )
    if (decision == "uncertain" or certainty != "high") and not uncertainty_codes:
        raise ValueError("ADJUDICATION_UNCERTAINTY_REQUIRED")
    if certainty == "high" and uncertainty_codes:
        raise ValueError("ADJUDICATION_CERTAINTY_UNCERTAINTY_CONTRADICTION")
    if not set(rationale_codes).issubset(_RATIONALE_BY_DECISION[decision]):
        raise ValueError("ADJUDICATION_RATIONALE_DECISION_CONTRADICTION")
    source_decisions = {
        primary.get("boundary_decision"),
        independent.get("boundary_decision"),
    }
    conflict_exists = len(source_decisions) != 1 or decision not in source_decisions
    if "observations_agree" in rationale_codes and not (
        len(source_decisions) == 1 and decision in source_decisions
    ):
        raise ValueError("ADJUDICATION_OBSERVATIONS_AGREE_FALSE")
    aligned_visible_rationale = {
        "same_hand": "visible_form_evidence_supports_same",
        "different_hand": "visible_form_evidence_supports_difference",
        "uncertain": "evidence_remains_equivocal",
    }[decision]
    if conflict_exists and aligned_visible_rationale not in rationale_codes:
        raise ValueError("ADJUDICATION_CONFLICT_RATIONALE_REQUIRED")
    if conflict_exists and decision != "uncertain" and not conflict_codes:
        raise ValueError("ADJUDICATION_CONFLICT_RESOLUTION_REQUIRED")
    if not conflict_exists and conflict_codes:
        raise ValueError("ADJUDICATION_CONFLICT_CODES_WITHOUT_CONFLICT")
    image_bindings = _image_bindings(task)
    payload = {
        "schema": ADJUDICATION_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "task_id": task["task_id"],
        "task_receipt_sha256": task["receipt_sha256"],
        "queue_id": task["queue_id"],
        "pair_task_id": task["pair_task_id"],
        "source_binding_sha256": task["source_binding_sha256"],
        "review_implementation_sha256": task["review_implementation_sha256"],
        "review_implementation_git_commit": task["review_implementation_git_commit"],
        "review_implementation_git_worktree_dirty": task[
            "review_implementation_git_worktree_dirty"
        ],
        "image_bindings": image_bindings,
        "primary_observation_id": primary["observation_id"],
        "primary_observation_receipt_sha256": primary["receipt_sha256"],
        "independent_observation_id": independent["observation_id"],
        "independent_observation_receipt_sha256": independent["receipt_sha256"],
        "adjudicator_id": adjudicator_id,
        "source_lane": "human_image_only_adjudication",
        "inherited_text_used": False,
        "source_observations_reviewed": True,
        "blinding_state": "source_observations_self_attested_blinded",
        "blinding_verified": False,
        "identity_authority_state": "self_asserted_unverified",
        "boundary_decision": decision,
        "certainty": certainty,
        "rationale_codes": rationale_codes,
        "uncertainty_codes": uncertainty_codes,
        "conflict_resolution_codes": conflict_codes,
        "review_state": "adjudicated_unresolved" if decision == "uncertain" else "adjudicated_pair_decision",
        "authority_scope": "pilot_pair_boundary_only",
        "named_hand_authority_allowed": False,
        "whole_manuscript_hand_authority_allowed": False,
        "training_eligible": False,
        "training_promotion_allowed": False,
        "split_assignment_allowed": False,
        "ocr_accuracy_claim_allowed": False,
        "translation_claim_allowed": False,
        "qualified_review_authority_allowed": False,
        "scientific_boundary_authority_allowed": False,
    }
    adjudication_id = _domain_id(
        "zfd.comparative_hand_pair_adjudication.v1",
        {
            "task_id": task["task_id"],
            "primary_observation_receipt_sha256": primary["receipt_sha256"],
            "independent_observation_receipt_sha256": independent["receipt_sha256"],
            "adjudicator_id": adjudicator_id,
            "boundary_decision": decision,
            "certainty": certainty,
            "rationale_codes": rationale_codes,
            "uncertainty_codes": uncertainty_codes,
            "conflict_resolution_codes": conflict_codes,
        },
    )
    return _receipt({**payload, "adjudication_id": adjudication_id})


def _adjudication_draft(adjudication: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": ADJUDICATION_DRAFT_SCHEMA,
        "task_id": adjudication.get("task_id"),
        "primary_observation_receipt_sha256": adjudication.get(
            "primary_observation_receipt_sha256"
        ),
        "independent_observation_receipt_sha256": adjudication.get(
            "independent_observation_receipt_sha256"
        ),
        "adjudicator_id": adjudication.get("adjudicator_id"),
        "source_lane": adjudication.get("source_lane"),
        "inherited_text_used": adjudication.get("inherited_text_used"),
        "source_observations_reviewed": adjudication.get("source_observations_reviewed"),
        "boundary_decision": adjudication.get("boundary_decision"),
        "certainty": adjudication.get("certainty"),
        "rationale_codes": adjudication.get("rationale_codes"),
        "uncertainty_codes": adjudication.get("uncertainty_codes"),
        "conflict_resolution_codes": adjudication.get("conflict_resolution_codes"),
    }


def validate_pair_adjudication(
    adjudication: Mapping[str, Any],
    task: Mapping[str, Any],
    primary: Mapping[str, Any],
    independent: Mapping[str, Any],
    *,
    bundle: ComparativeReviewAuthority,
    source_root: Path,
) -> tuple[str, ...]:
    errors: list[str] = []
    if not _receipt_valid(adjudication):
        errors.append("ADJUDICATION_RECEIPT_HASH_MISMATCH")
    if not isinstance(adjudication, Mapping):
        errors.append("ADJUDICATION_MALFORMED")
        return tuple(dict.fromkeys(errors))
    try:
        expected = seal_pair_adjudication(
            task,
            primary,
            independent,
            _adjudication_draft(adjudication),
            bundle=bundle,
            source_root=source_root,
        )
        if _canonical_json(dict(adjudication)) != _canonical_json(expected):
            errors.append("ADJUDICATION_RECOMPUTE_MISMATCH")
    except (AttributeError, KeyError, TypeError, ValueError) as error:
        errors.append(f"ADJUDICATION_RECOMPUTE_FAILED:{error}")
    return tuple(dict.fromkeys(errors))


__all__ = [
    "ADJUDICATION_DRAFT_SCHEMA",
    "ADJUDICATION_SCHEMA",
    "BOUNDARY_DECISIONS",
    "ComparativeReviewAuthority",
    "OBSERVATION_DRAFT_SCHEMA",
    "OBSERVATION_SCHEMA",
    "TASK_SCHEMA",
    "build_pair_review_task",
    "open_comparative_review_authority",
    "seal_pair_adjudication",
    "seal_pair_observation",
    "validate_pair_adjudication",
    "validate_pair_observation",
    "validate_pair_review_task",
]
