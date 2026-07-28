"""Comparative hand review stays pixel bound, blinded, and pair scoped."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import importlib
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

from PIL import Image
import pytest

from zfd_comparative_gold.core import ComparativeQueueConfig, HandBoundaryQueueBundle


def _canonical_json(value) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _value_sha256(value) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _receipt(value: dict) -> dict:
    body = {key: item for key, item in value.items() if key != "receipt_sha256"}
    return {**body, "receipt_sha256": _value_sha256(body)}


def _jsonl_sha256(rows: list[dict]) -> str:
    payload = "".join(_canonical_json(row) + "\n" for row in rows).encode("utf-8")
    return sha256(payload).hexdigest()


def _api():
    return importlib.import_module("zfd_comparative_gold.review")


@pytest.fixture(autouse=True)
def _fixture_queue_validator(monkeypatch: pytest.MonkeyPatch) -> None:
    api = _api()
    monkeypatch.setattr(api, "validate_hand_boundary_queue", lambda *_args, **_kwargs: ())


def _queue_fixture(tmp_path: Path):
    source_root = tmp_path / "Mavrov"
    image_root = source_root / "img"
    image_root.mkdir(parents=True)
    images = (
        ("left.png", (24, 30), (241, 232, 218)),
        ("right.png", (26, 30), (232, 225, 211)),
    )
    queue_id = "sha256:" + "1" * 64
    rows: list[dict] = []
    for ordinal, (name, size, colour) in enumerate(images):
        path = image_root / name
        Image.new("RGB", size, colour).save(path)
        image_sha256 = sha256(path.read_bytes()).hexdigest()
        body = {
            "schema": "zfd.comparative_hand_boundary_queue_row.v1",
            "schema_version": "1.0.0",
            "queue_id": queue_id,
            "source_id": "fixture-mavrov-r7822",
            "ordinal": ordinal,
            "asset_id": "sha256:" + str(ordinal + 2) * 64,
            "asset_receipt_sha256": str(ordinal + 4) * 64,
            "mapping_entry_sha256": str(ordinal + 6) * 64,
            "canvas_id": f"https://example.invalid/canvas/{ordinal}",
            "canvas_label": f"R7822_{ordinal + 1:03d}",
            "image_sha256": image_sha256,
            "byte_length": path.stat().st_size,
            "width": size[0],
            "height": size[1],
            "local_relpath": f"img/{name}",
            "lineage_root_id": "sha256:" + image_sha256,
            "queue_item_id": "sha256:" + str(ordinal + 8) * 64,
            "previous_queue_item_id": None if ordinal == 0 else "sha256:" + "8" * 64,
            "next_queue_item_id": "sha256:" + "9" * 64 if ordinal == 0 else None,
            "boundary_before_state": "manuscript_start" if ordinal == 0 else "unresolved_unreviewed",
            "hand_identity_state": "unknown_unreviewed",
            "hand_id": None,
            "line_annotation_state": "not_started",
            "hand_boundary_sha256": None,
            "line_annotation_sha256": None,
            "split_assignment_state": "blocked_unknown_hand",
            "split_lineage_sha256": None,
            "review_state": "unreviewed",
            "diplomatic_label_count": 0,
            "semantic_authority_count": 0,
            "inherited_text_used": False,
            "training_disposition": "quarantine",
            "training_eligible": False,
            "training_promotion_allowed": False,
        }
        rows.append(_receipt(body))

    pilot_id = "sha256:" + "a" * 64
    pair_task_id = "sha256:" + "b" * 64
    pilot = [
        _receipt(
            {
                "schema": "zfd.comparative_hand_boundary_pilot_row.v1",
                "schema_version": "1.0.0",
                "pilot_id": pilot_id,
                "pair_task_id": pair_task_id,
                "pilot_ordinal": 0,
                "selection_rule_id": "endpoint_inclusive_even_adjacent_pairs.v1",
                "left_ordinal": 0,
                "right_ordinal": 1,
                "left_queue_item_id": rows[0]["queue_item_id"],
                "right_queue_item_id": rows[1]["queue_item_id"],
                "left_asset_id": rows[0]["asset_id"],
                "right_asset_id": rows[1]["asset_id"],
                "left_canvas_id": rows[0]["canvas_id"],
                "right_canvas_id": rows[1]["canvas_id"],
                "left_image_sha256": rows[0]["image_sha256"],
                "right_image_sha256": rows[1]["image_sha256"],
                "left_local_relpath": rows[0]["local_relpath"],
                "right_local_relpath": rows[1]["local_relpath"],
                "review_state": "unreviewed",
                "boundary_decision": None,
                "palaeographic_observation_authority": "absent",
                "named_hand_authority": "absent",
                "whole_manuscript_boundary_authority_allowed": False,
                "training_disposition": "quarantine",
                "training_promotion_allowed": False,
                "inherited_text_used": False,
            }
        )
    ]
    summary = _receipt(
        {
            "schema": "zfd.comparative_hand_boundary_queue.v1",
            "schema_version": "1.0.0",
            "queue_id": queue_id,
            "pilot_id": pilot_id,
            "source_id": "fixture-mavrov-r7822",
            "queue_row_count": 2,
            "queue_rows_sha256": _jsonl_sha256(rows),
            "pilot_pair_count": 1,
            "pilot_rows_sha256": _jsonl_sha256(pilot),
            "training_ready_asset_count": 0,
            "hand_boundary_authority_complete": False,
            "split_lineage_authority_complete": False,
            "ocr_accuracy_claim_allowed": False,
            "inherited_text_used": False,
        }
    )
    raw_bundle = HandBoundaryQueueBundle(rows=rows, pilot=pilot, summary=summary)
    repository_root = tmp_path / "authority-repo"
    repository_root.mkdir()
    authority = _api().open_comparative_review_authority(
        raw_bundle,
        repository_root=repository_root,
        source_mount=tmp_path,
        asset_root=repository_root / "data" / "image_native",
        config_path=repository_root / "data" / "image_native" / "comparative_sources.json",
        register_path=repository_root / "data" / "image_native" / "source_register.json",
        config=ComparativeQueueConfig(
            source_id="fixture-mavrov-r7822",
            expected_asset_count=2,
            pilot_pairs=((0, 1),),
        ),
        source_root=source_root,
    )
    return authority, source_root


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_canonical_json(value) + "\n", encoding="utf-8", newline="\n")


def _write_bundle(root: Path, bundle: HandBoundaryQueueBundle) -> None:
    root.mkdir(parents=True)
    (root / "hand_boundary_queue.jsonl").write_text(
        "".join(_canonical_json(row) + "\n" for row in bundle.rows),
        encoding="utf-8",
        newline="\n",
    )
    (root / "hand_boundary_pilot.jsonl").write_text(
        "".join(_canonical_json(row) + "\n" for row in bundle.pilot),
        encoding="utf-8",
        newline="\n",
    )
    _write_json(root / "hand_boundary_summary.json", bundle.summary)


def _observation_draft(
    task: dict,
    *,
    reviewer_id: str,
    role: str,
    decision: str = "different_hand",
    certainty: str = "moderate",
) -> dict:
    evidence_codes = {
        "same_hand": ["ductus_consistent", "letterform_construction_consistent"],
        "different_hand": ["ductus_shift", "letterform_construction_shift"],
        "uncertain": ["insufficient_comparable_forms"],
    }.get(decision, ["insufficient_comparable_forms"])
    return {
        "schema": "zfd.comparative_hand_pair_observation_draft.v1",
        "task_id": task["task_id"],
        "reviewer_id": reviewer_id,
        "review_role": role,
        "source_lane": "human_image_only_blinded",
        "inherited_text_used": False,
        "other_observation_seen": False,
        "boundary_decision": decision,
        "certainty": certainty,
        "evidence_codes": evidence_codes,
        "uncertainty_codes": [] if certainty == "high" else ["limited_visible_forms"],
    }


def _adjudication_draft(task: dict, primary: dict, independent: dict) -> dict:
    return {
        "schema": "zfd.comparative_hand_pair_adjudication_draft.v1",
        "task_id": task["task_id"],
        "primary_observation_receipt_sha256": primary["receipt_sha256"],
        "independent_observation_receipt_sha256": independent["receipt_sha256"],
        "adjudicator_id": "reviewer-c",
        "source_lane": "human_image_only_adjudication",
        "inherited_text_used": False,
        "source_observations_reviewed": True,
        "boundary_decision": "different_hand",
        "certainty": "moderate",
        "rationale_codes": ["visible_form_evidence_supports_difference"],
        "uncertainty_codes": ["limited_visible_forms"],
        "conflict_resolution_codes": [],
    }


def test_pair_task_binds_queue_rows_source_bytes_decoded_pixels_and_regions(
    tmp_path: Path,
) -> None:
    api = _api()
    bundle, source_root = _queue_fixture(tmp_path)

    task = api.build_pair_review_task(
        bundle,
        pair_task_id=bundle.pilot[0]["pair_task_id"],
        source_root=source_root,
        regions={"left": [2, 3, 10, 12]},
    )

    assert task["queue_id"] == bundle.summary["queue_id"]
    assert task["queue_summary_receipt_sha256"] == bundle.summary["receipt_sha256"]
    assert task["pilot_row_receipt_sha256"] == bundle.pilot[0]["receipt_sha256"]
    assert task["source_binding_sha256"].startswith("sha256:")
    assert task["sides"]["left"]["queue_row_receipt_sha256"] == bundle.rows[0]["receipt_sha256"]
    assert task["sides"]["left"]["source_image_sha256"] == bundle.rows[0]["image_sha256"]
    assert task["sides"]["left"]["decoded_pixel_sha256"].startswith("sha256:")
    assert task["sides"]["left"]["region_pixel_sha256"].startswith("sha256:")
    assert task["sides"]["left"]["geometry"] == {
        "kind": "explicit_region",
        "xywh": [2, 3, 10, 12],
    }
    assert task["sides"]["right"]["geometry"] == {
        "kind": "full_page",
        "xywh": [0, 0, 26, 30],
    }
    assert task["blinding_state"] == "workflow_requires_independent_observations"
    assert task["blinding_enforced"] is False
    assert task["whole_manuscript_hand_authority_allowed"] is False
    assert task["training_promotion_allowed"] is False
    assert api.validate_pair_review_task(task, bundle, source_root) == ()


def test_pair_task_rejects_queue_source_and_geometry_tampering(tmp_path: Path) -> None:
    api = _api()
    bundle, source_root = _queue_fixture(tmp_path)
    task = api.build_pair_review_task(
        bundle,
        pair_task_id=bundle.pilot[0]["pair_task_id"],
        source_root=source_root,
    )

    (source_root / "img" / "left.png").write_bytes(b"replaced")
    assert "SOURCE_IMAGE_BYTES_MISMATCH:left" in api.validate_pair_review_task(
        task, bundle, source_root
    )

    forged_bundle = deepcopy(bundle)
    forged_bundle.rows[0]["canvas_id"] = "https://example.invalid/forged"
    errors = api.validate_pair_review_task(task, forged_bundle, source_root)
    assert "QUEUE_ROW_RECEIPT_HASH_MISMATCH:0" in errors

    with pytest.raises(ValueError, match="REVIEW_REGION_GEOMETRY_INVALID:left"):
        api.build_pair_review_task(
            bundle,
            pair_task_id=bundle.pilot[0]["pair_task_id"],
            source_root=source_root,
            regions={"left": [20, 0, 10, 10]},
        )


def test_pair_task_accepts_only_an_exact_pilot_pair(tmp_path: Path) -> None:
    api = _api()
    bundle, source_root = _queue_fixture(tmp_path)

    with pytest.raises(ValueError, match="PILOT_PAIR_TASK_NOT_FOUND"):
        api.build_pair_review_task(
            bundle,
            pair_task_id="sha256:" + "f" * 64,
            source_root=source_root,
        )


def test_pair_task_decodes_the_same_immutable_bytes_that_it_hashes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    api = _api()
    bundle, source_root = _queue_fixture(tmp_path)
    original_open = api.Image.open

    def require_byte_snapshot(source, *args, **kwargs):
        assert hasattr(source, "read")
        return original_open(source, *args, **kwargs)

    monkeypatch.setattr(api.Image, "open", require_byte_snapshot)

    task = api.build_pair_review_task(
        bundle, pair_task_id=bundle.pilot[0]["pair_task_id"], source_root=source_root
    )
    assert task["sides"]["left"]["source_image_sha256"] == bundle.rows[0][
        "image_sha256"
    ]


def test_observations_are_blinded_controlled_and_explicitly_uncertain(tmp_path: Path) -> None:
    api = _api()
    bundle, source_root = _queue_fixture(tmp_path)
    task = api.build_pair_review_task(
        bundle, pair_task_id=bundle.pilot[0]["pair_task_id"], source_root=source_root
    )

    observation = api.seal_pair_observation(
        task,
        _observation_draft(task, reviewer_id="reviewer-a", role="primary"),
        bundle=bundle,
        source_root=source_root,
    )

    assert observation["task_receipt_sha256"] == task["receipt_sha256"]
    assert observation["source_binding_sha256"] == task["source_binding_sha256"]
    assert observation["blinding_state"] == "self_attested_other_observation_not_seen"
    assert observation["blinding_verified"] is False
    assert observation["boundary_decision"] == "different_hand"
    assert observation["uncertainty_codes"] == ["limited_visible_forms"]
    assert observation["authority_scope"] == "pilot_pair_observation_only"
    assert observation["training_eligible"] is False
    assert api.validate_pair_observation(
        observation, task, bundle=bundle, source_root=source_root
    ) == ()

    uncertain = _observation_draft(
        task,
        reviewer_id="reviewer-b",
        role="independent_reviewer",
        decision="uncertain",
        certainty="low",
    )
    uncertain["uncertainty_codes"] = []
    with pytest.raises(ValueError, match="OBSERVATION_UNCERTAINTY_REQUIRED"):
        api.seal_pair_observation(
            task, uncertain, bundle=bundle, source_root=source_root
        )


@pytest.mark.parametrize(
    "forbidden_field",
    (
        "transcription",
        "transliteration",
        "translation",
        "diplomatic_label",
        "semantic_label",
        "ocr_output",
        "hand_name",
        "notes",
    ),
)
def test_observation_rejects_reading_and_free_text_fields(
    tmp_path: Path, forbidden_field: str
) -> None:
    api = _api()
    bundle, source_root = _queue_fixture(tmp_path)
    task = api.build_pair_review_task(
        bundle, pair_task_id=bundle.pilot[0]["pair_task_id"], source_root=source_root
    )
    draft = _observation_draft(task, reviewer_id="reviewer-a", role="primary")
    draft[forbidden_field] = "counterfeit authority"

    with pytest.raises(ValueError, match="OBSERVATION_DRAFT_FIELDS_INVALID"):
        api.seal_pair_observation(
            task, draft, bundle=bundle, source_root=source_root
        )


def test_observation_rejects_tainted_lane_and_uncontrolled_values(tmp_path: Path) -> None:
    api = _api()
    bundle, source_root = _queue_fixture(tmp_path)
    task = api.build_pair_review_task(
        bundle, pair_task_id=bundle.pilot[0]["pair_task_id"], source_root=source_root
    )
    inherited = _observation_draft(task, reviewer_id="reviewer-a", role="primary")
    inherited["inherited_text_used"] = True
    with pytest.raises(ValueError, match="OBSERVATION_SOURCE_LANE_TAINTED"):
        api.seal_pair_observation(
            task, inherited, bundle=bundle, source_root=source_root
        )

    uncontrolled = _observation_draft(task, reviewer_id="reviewer-a", role="primary")
    uncontrolled["boundary_decision"] = "probably_scribe_b"
    with pytest.raises(ValueError, match="BOUNDARY_DECISION_INVALID"):
        api.seal_pair_observation(
            task, uncontrolled, bundle=bundle, source_root=source_root
        )


def test_adjudication_requires_exact_observations_and_three_distinct_identities(
    tmp_path: Path,
) -> None:
    api = _api()
    bundle, source_root = _queue_fixture(tmp_path)
    task = api.build_pair_review_task(
        bundle, pair_task_id=bundle.pilot[0]["pair_task_id"], source_root=source_root
    )
    primary = api.seal_pair_observation(
        task,
        _observation_draft(task, reviewer_id="reviewer-a", role="primary"),
        bundle=bundle,
        source_root=source_root,
    )
    independent = api.seal_pair_observation(
        task,
        _observation_draft(
            task, reviewer_id="reviewer-b", role="independent_reviewer"
        ),
        bundle=bundle,
        source_root=source_root,
    )
    draft = _adjudication_draft(task, primary, independent)

    adjudication = api.seal_pair_adjudication(
        task,
        primary,
        independent,
        draft,
        bundle=bundle,
        source_root=source_root,
    )

    assert adjudication["primary_observation_receipt_sha256"] == primary["receipt_sha256"]
    assert adjudication["independent_observation_receipt_sha256"] == independent["receipt_sha256"]
    assert adjudication["source_binding_sha256"] == task["source_binding_sha256"]
    assert api.validate_pair_adjudication(
        adjudication,
        task,
        primary,
        independent,
        bundle=bundle,
        source_root=source_root,
    ) == ()

    same_person = deepcopy(draft)
    same_person["adjudicator_id"] = "Reviewer-A"
    with pytest.raises(ValueError, match="REVIEW_IDENTITIES_NOT_DISTINCT"):
        api.seal_pair_adjudication(
            task,
            primary,
            independent,
            same_person,
            bundle=bundle,
            source_root=source_root,
        )

    repeated_reviewer = _observation_draft(
        task, reviewer_id="REVIEWER-A", role="independent_reviewer"
    )
    repeated = api.seal_pair_observation(
        task,
        repeated_reviewer,
        bundle=bundle,
        source_root=source_root,
    )
    with pytest.raises(ValueError, match="REVIEW_IDENTITIES_NOT_DISTINCT"):
        api.seal_pair_adjudication(
            task,
            primary,
            repeated,
            _adjudication_draft(task, primary, repeated),
            bundle=bundle,
            source_root=source_root,
        )


def test_adjudication_stays_pair_scoped_and_blocks_claim_promotion(tmp_path: Path) -> None:
    api = _api()
    bundle, source_root = _queue_fixture(tmp_path)
    task = api.build_pair_review_task(
        bundle, pair_task_id=bundle.pilot[0]["pair_task_id"], source_root=source_root
    )
    primary = api.seal_pair_observation(
        task,
        _observation_draft(task, reviewer_id="reviewer-a", role="primary"),
        bundle=bundle,
        source_root=source_root,
    )
    independent = api.seal_pair_observation(
        task,
        _observation_draft(
            task, reviewer_id="reviewer-b", role="independent_reviewer"
        ),
        bundle=bundle,
        source_root=source_root,
    )
    adjudication = api.seal_pair_adjudication(
        task,
        primary,
        independent,
        _adjudication_draft(task, primary, independent),
        bundle=bundle,
        source_root=source_root,
    )

    assert adjudication["authority_scope"] == "pilot_pair_boundary_only"
    assert adjudication["named_hand_authority_allowed"] is False
    assert adjudication["whole_manuscript_hand_authority_allowed"] is False
    assert adjudication["training_eligible"] is False
    assert adjudication["training_promotion_allowed"] is False
    assert adjudication["split_assignment_allowed"] is False
    assert adjudication["ocr_accuracy_claim_allowed"] is False
    assert adjudication["translation_claim_allowed"] is False
    assert adjudication["identity_authority_state"] == "self_asserted_unverified"
    assert adjudication["qualified_review_authority_allowed"] is False
    assert adjudication["scientific_boundary_authority_allowed"] is False


def test_adjudication_requires_conflict_resolution_or_preserves_uncertainty(
    tmp_path: Path,
) -> None:
    api = _api()
    bundle, source_root = _queue_fixture(tmp_path)
    task = api.build_pair_review_task(
        bundle, pair_task_id=bundle.pilot[0]["pair_task_id"], source_root=source_root
    )
    primary = api.seal_pair_observation(
        task,
        _observation_draft(
            task,
            reviewer_id="reviewer-a",
            role="primary",
            decision="same_hand",
            certainty="high",
        ),
        bundle=bundle,
        source_root=source_root,
    )
    independent = api.seal_pair_observation(
        task,
        _observation_draft(
            task,
            reviewer_id="reviewer-b",
            role="independent_reviewer",
            decision="different_hand",
            certainty="moderate",
        ),
        bundle=bundle,
        source_root=source_root,
    )
    draft = _adjudication_draft(task, primary, independent)

    with pytest.raises(ValueError, match="ADJUDICATION_CONFLICT_RESOLUTION_REQUIRED"):
        api.seal_pair_adjudication(
            task,
            primary,
            independent,
            draft,
            bundle=bundle,
            source_root=source_root,
        )

    draft["boundary_decision"] = "uncertain"
    draft["rationale_codes"] = ["evidence_remains_equivocal"]
    adjudication = api.seal_pair_adjudication(
        task,
        primary,
        independent,
        draft,
        bundle=bundle,
        source_root=source_root,
    )
    assert adjudication["review_state"] == "adjudicated_unresolved"


def test_validators_recompute_canonical_receipts(tmp_path: Path) -> None:
    api = _api()
    bundle, source_root = _queue_fixture(tmp_path)
    task = api.build_pair_review_task(
        bundle, pair_task_id=bundle.pilot[0]["pair_task_id"], source_root=source_root
    )
    primary = api.seal_pair_observation(
        task,
        _observation_draft(task, reviewer_id="reviewer-a", role="primary"),
        bundle=bundle,
        source_root=source_root,
    )
    independent = api.seal_pair_observation(
        task,
        _observation_draft(
            task, reviewer_id="reviewer-b", role="independent_reviewer"
        ),
        bundle=bundle,
        source_root=source_root,
    )
    adjudication = api.seal_pair_adjudication(
        task,
        primary,
        independent,
        _adjudication_draft(task, primary, independent),
        bundle=bundle,
        source_root=source_root,
    )

    changed_observation = deepcopy(primary)
    changed_observation["boundary_decision"] = "same_hand"
    assert "OBSERVATION_RECEIPT_HASH_MISMATCH" in api.validate_pair_observation(
        changed_observation, task, bundle=bundle, source_root=source_root
    )

    changed_adjudication = deepcopy(adjudication)
    changed_adjudication["whole_manuscript_hand_authority_allowed"] = True
    assert "ADJUDICATION_RECEIPT_HASH_MISMATCH" in api.validate_pair_adjudication(
        changed_adjudication,
        task,
        primary,
        independent,
        bundle=bundle,
        source_root=source_root,
    )


def test_sealing_requires_revalidated_queue_and_source_authority(tmp_path: Path) -> None:
    api = _api()
    bundle, source_root = _queue_fixture(tmp_path)
    with pytest.raises(ValueError, match="COMPARATIVE_REVIEW_AUTHORITY_REQUIRED"):
        api.build_pair_review_task(
            bundle.bundle,
            pair_task_id=bundle.pilot[0]["pair_task_id"],
            source_root=source_root,
        )
    task = api.build_pair_review_task(
        bundle, pair_task_id=bundle.pilot[0]["pair_task_id"], source_root=source_root
    )
    forged = deepcopy(task)
    forged["sides"]["left"]["decoded_pixel_sha256"] = None
    forged["sides"]["left"]["region_pixel_sha256"] = None
    forged["training_eligible"] = True
    forged["translation_claim_allowed"] = True
    forged = _receipt(forged)
    draft = _observation_draft(forged, reviewer_id="reviewer-a", role="primary")

    with pytest.raises(ValueError, match="PAIR_REVIEW_TASK_INVALID"):
        api.seal_pair_observation(
            forged,
            draft,
            bundle=bundle,
            source_root=source_root,
        )


def test_review_identity_distinctness_rejects_unicode_aliases(tmp_path: Path) -> None:
    api = _api()
    bundle, source_root = _queue_fixture(tmp_path)
    task = api.build_pair_review_task(
        bundle, pair_task_id=bundle.pilot[0]["pair_task_id"], source_root=source_root
    )
    primary_draft = _observation_draft(
        task, reviewer_id="reviewer-é", role="primary"
    )
    independent_draft = _observation_draft(
        task, reviewer_id="reviewer-e\u0301", role="independent_reviewer"
    )

    with pytest.raises(ValueError, match="REVIEWER_IDENTITY_INVALID|REVIEW_IDENTITIES_NOT_DISTINCT"):
        primary = api.seal_pair_observation(
            task, primary_draft, bundle=bundle, source_root=source_root
        )
        independent = api.seal_pair_observation(
            task, independent_draft, bundle=bundle, source_root=source_root
        )
        api.seal_pair_adjudication(
            task,
            primary,
            independent,
            _adjudication_draft(task, primary, independent),
            bundle=bundle,
            source_root=source_root,
        )


def test_controlled_decisions_reject_contradictory_evidence(tmp_path: Path) -> None:
    api = _api()
    bundle, source_root = _queue_fixture(tmp_path)
    task = api.build_pair_review_task(
        bundle, pair_task_id=bundle.pilot[0]["pair_task_id"], source_root=source_root
    )
    contradictory = _observation_draft(
        task,
        reviewer_id="reviewer-a",
        role="primary",
        decision="same_hand",
        certainty="high",
    )
    contradictory["evidence_codes"] = ["ductus_shift"]
    with pytest.raises(ValueError, match="OBSERVATION_EVIDENCE_DECISION_CONTRADICTION"):
        api.seal_pair_observation(
            task, contradictory, bundle=bundle, source_root=source_root
        )

    primary = api.seal_pair_observation(
        task,
        _observation_draft(
            task,
            reviewer_id="reviewer-a",
            role="primary",
            decision="same_hand",
            certainty="high",
        ),
        bundle=bundle,
        source_root=source_root,
    )
    independent = api.seal_pair_observation(
        task,
        _observation_draft(
            task,
            reviewer_id="reviewer-b",
            role="independent_reviewer",
            decision="same_hand",
            certainty="high",
        ),
        bundle=bundle,
        source_root=source_root,
    )
    adjudication_draft = _adjudication_draft(task, primary, independent)
    adjudication_draft["boundary_decision"] = "same_hand"
    adjudication_draft["certainty"] = "high"
    adjudication_draft["uncertainty_codes"] = []
    adjudication_draft["rationale_codes"] = [
        "visible_form_evidence_supports_difference"
    ]
    with pytest.raises(ValueError, match="ADJUDICATION_RATIONALE_DECISION_CONTRADICTION"):
        api.seal_pair_adjudication(
            task,
            primary,
            independent,
            adjudication_draft,
            bundle=bundle,
            source_root=source_root,
        )


def test_adjudication_cannot_claim_observations_agree_during_conflict(
    tmp_path: Path,
) -> None:
    api = _api()
    bundle, source_root = _queue_fixture(tmp_path)
    task = api.build_pair_review_task(
        bundle, pair_task_id=bundle.pilot[0]["pair_task_id"], source_root=source_root
    )
    primary = api.seal_pair_observation(
        task,
        _observation_draft(
            task,
            reviewer_id="reviewer-a",
            role="primary",
            decision="same_hand",
            certainty="high",
        ),
        bundle=bundle,
        source_root=source_root,
    )
    independent = api.seal_pair_observation(
        task,
        _observation_draft(
            task,
            reviewer_id="reviewer-b",
            role="independent_reviewer",
            decision="different_hand",
            certainty="high",
        ),
        bundle=bundle,
        source_root=source_root,
    )
    draft = _adjudication_draft(task, primary, independent)
    draft["boundary_decision"] = "same_hand"
    draft["certainty"] = "high"
    draft["uncertainty_codes"] = []
    draft["rationale_codes"] = ["observations_agree"]
    draft["conflict_resolution_codes"] = ["resolved_by_ductus"]

    with pytest.raises(ValueError, match="ADJUDICATION_OBSERVATIONS_AGREE_FALSE"):
        api.seal_pair_adjudication(
            task,
            primary,
            independent,
            draft,
            bundle=bundle,
            source_root=source_root,
        )


def test_validators_return_errors_for_non_object_receipts(tmp_path: Path) -> None:
    api = _api()
    bundle, source_root = _queue_fixture(tmp_path)
    task = api.build_pair_review_task(
        bundle, pair_task_id=bundle.pilot[0]["pair_task_id"], source_root=source_root
    )
    primary = api.seal_pair_observation(
        task,
        _observation_draft(task, reviewer_id="reviewer-a", role="primary"),
        bundle=bundle,
        source_root=source_root,
    )
    independent = api.seal_pair_observation(
        task,
        _observation_draft(
            task, reviewer_id="reviewer-b", role="independent_reviewer"
        ),
        bundle=bundle,
        source_root=source_root,
    )

    assert "PAIR_REVIEW_TASK_RECEIPT_HASH_MISMATCH" in api.validate_pair_review_task(
        [], bundle, source_root
    )
    assert "OBSERVATION_RECEIPT_HASH_MISMATCH" in api.validate_pair_observation(
        [], task, bundle=bundle, source_root=source_root
    )
    assert "ADJUDICATION_RECEIPT_HASH_MISMATCH" in api.validate_pair_adjudication(
        [],
        task,
        primary,
        independent,
        bundle=bundle,
        source_root=source_root,
    )


def test_task_binds_review_implementation_and_cli_refuses_dirty_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    api = _api()
    cli = importlib.import_module("zfd_comparative_gold.cli")
    bundle, source_root = _queue_fixture(tmp_path)
    task = api.build_pair_review_task(
        bundle, pair_task_id=bundle.pilot[0]["pair_task_id"], source_root=source_root
    )

    assert task["review_implementation_sha256"].startswith("sha256:")
    assert "review_implementation_git_commit" in task
    assert "review_implementation_git_worktree_dirty" in task
    monkeypatch.setattr(cli, "_git_state", lambda: ("a" * 40, True), raising=False)
    with pytest.raises(ValueError, match="REVIEW_IMPLEMENTATION_NOT_PUBLISHABLE"):
        cli._require_review_implementation_publishable(tmp_path)


def test_review_outputs_are_confined_and_exclusive(tmp_path: Path) -> None:
    cli = importlib.import_module("zfd_comparative_gold.cli")
    repository_root = tmp_path / "repo"
    repository_root.mkdir()
    allowed = repository_root / "build" / "comparative_review" / "pilot" / "task.json"

    assert cli._resolve_review_output(allowed, repository_root) == allowed.resolve()
    allowed.parent.mkdir(parents=True)
    allowed.write_text("occupied", encoding="utf-8")
    with pytest.raises(ValueError, match="REVIEW_OUTPUT_ALREADY_EXISTS"):
        cli._resolve_review_output(allowed, repository_root)
    with pytest.raises(ValueError, match="OUTPUT_OUTSIDE_ALLOWED_ROOT"):
        cli._resolve_review_output(tmp_path / "escape.json", repository_root)
    with pytest.raises(ValueError, match="REVIEW_OUTPUT_MUST_BE_STRICT_JSON_DESCENDANT"):
        cli._resolve_review_output(
            repository_root / "build" / "comparative_review", repository_root
        )
    with pytest.raises(ValueError, match="REVIEW_OUTPUT_MUST_BE_STRICT_JSON_DESCENDANT"):
        cli._resolve_review_output(
            repository_root / "build" / "comparative_review" / "task.txt",
            repository_root,
        )


def test_review_output_rejects_windows_junction_escape(tmp_path: Path) -> None:
    if sys.platform != "win32":
        pytest.skip("Windows junction boundary test")
    cli = importlib.import_module("zfd_comparative_gold.cli")
    repository_root = tmp_path / "repository"
    outside = tmp_path / "outside"
    parent = repository_root / "build"
    parent.mkdir(parents=True)
    outside.mkdir()
    junction = parent / "comparative_review"
    created = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(junction), str(outside)],
        check=False,
        capture_output=True,
        text=True,
    )
    if created.returncode:
        pytest.skip(f"junction unavailable: {created.stderr.strip()}")

    with pytest.raises(ValueError, match="OUTPUT_OUTSIDE_REPOSITORY"):
        cli._resolve_review_output(
            Path("build/comparative_review/pilot/task.json"),
            repository_root.resolve(),
        )


def test_comparanda_cli_exposes_review_commands() -> None:
    cli = importlib.import_module("zfd_comparative_gold.cli")
    help_text = cli._parser().format_help()

    for command in (
        "create-review-task",
        "validate-review-task",
        "seal-review-observation",
        "validate-review-observation",
        "seal-review-adjudication",
        "validate-review-adjudication",
    ):
        assert command in help_text


def test_queue_and_review_commands_keep_the_registered_source_authority() -> None:
    cli = importlib.import_module("zfd_comparative_gold.cli")
    parser = cli._parser()
    commands = (
        [
            "build-queue",
            "--repository-root",
            ".",
            "--source-mount",
            "comparanda",
            "--output-root",
            "build/comparative_review/queue",
        ],
        [
            "create-review-task",
            "--repository-root",
            ".",
            "--source-mount",
            "comparanda",
            "--queue-root",
            "build/comparative_review/queue",
            "--pair-task-id",
            "sha256:" + "1" * 64,
            "--output",
            "build/comparative_review/task.json",
        ],
    )

    for argv in commands:
        args = parser.parse_args(argv)
        assert args.register_path == Path("data/image_native/source_register.json")


def test_review_cli_requires_full_registered_queue_validation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cli = importlib.import_module("zfd_comparative_gold.cli")
    bundle, source_root = _queue_fixture(tmp_path)
    repository_root = tmp_path / "repo"
    queue_root = repository_root / "build" / "comparative_review" / "queue"
    _write_bundle(queue_root, bundle)
    args = SimpleNamespace(
        repository_root=repository_root,
        queue_root=queue_root,
        source_mount=tmp_path / "comparanda",
    )
    monkeypatch.setattr(cli, "_build_args", lambda _args: {"source_mount": tmp_path})
    monkeypatch.setattr(cli, "_registered_source_root", lambda _args: source_root, raising=False)

    def reject(_bundle, _build_args):
        raise ValueError("QUEUE_INVALID:SOURCE_TRUST_ANCHOR_MISMATCH")

    monkeypatch.setattr(cli, "_require_valid_bundle", reject)

    with pytest.raises(ValueError, match="SOURCE_TRUST_ANCHOR_MISMATCH"):
        cli._open_review_authority(args)


def test_comparanda_cli_runs_task_observation_and_adjudication_cycle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    api = _api()
    cli = importlib.import_module("zfd_comparative_gold.cli")
    bundle, source_root = _queue_fixture(tmp_path)
    repository_root = tmp_path / "repo"
    queue_root = repository_root / "build" / "comparative_review" / "queue"
    run_root = repository_root / "build" / "comparative_review" / "run"
    _write_bundle(queue_root, bundle)
    pair_task_id = bundle.pilot[0]["pair_task_id"]

    monkeypatch.setattr(
        cli,
        "_open_review_authority",
        lambda _args: (repository_root, bundle, source_root),
    )
    monkeypatch.setattr(
        cli, "_require_review_implementation_publishable", lambda _root: None
    )
    monkeypatch.setattr(api, "_git_state", lambda: ("a" * 40, False))

    common = [
        "--repository-root",
        str(repository_root),
        "--queue-root",
        str(queue_root),
        "--source-mount",
        str(tmp_path / "comparanda"),
    ]
    task_path = run_root / "task.json"
    assert (
        cli.main(
            [
                "create-review-task",
                *common,
                "--pair-task-id",
                pair_task_id,
                "--left-region",
                "2",
                "3",
                "10",
                "12",
                "--output",
                str(task_path),
            ]
        )
        == 0
    )
    assert (
        cli.main(["validate-review-task", *common, "--task", str(task_path)])
        == 0
    )
    task = json.loads(task_path.read_text(encoding="utf-8"))
    assert task["review_implementation_provenance_status"] == "clean_git_commit"

    observation_paths: list[Path] = []
    for reviewer_id, role, stem in (
        ("reviewer-a", "primary", "primary"),
        ("reviewer-b", "independent_reviewer", "independent"),
    ):
        draft_path = run_root / f"{stem}.draft.json"
        output_path = run_root / f"{stem}.json"
        _write_json(
            draft_path,
            _observation_draft(
                task, reviewer_id=reviewer_id, role=role, certainty="moderate"
            ),
        )
        assert (
            cli.main(
                [
                    "seal-review-observation",
                    *common,
                    "--task",
                    str(task_path),
                    "--draft",
                    str(draft_path),
                    "--output",
                    str(output_path),
                ]
            )
            == 0
        )
        assert (
            cli.main(
                [
                    "validate-review-observation",
                    *common,
                    "--task",
                    str(task_path),
                    "--observation",
                    str(output_path),
                ]
            )
            == 0
        )
        observation_paths.append(output_path)

    primary = json.loads(observation_paths[0].read_text(encoding="utf-8"))
    independent = json.loads(observation_paths[1].read_text(encoding="utf-8"))
    adjudication_draft_path = run_root / "adjudication.draft.json"
    adjudication_path = run_root / "adjudication.json"
    _write_json(
        adjudication_draft_path,
        _adjudication_draft(task, primary, independent),
    )
    assert (
        cli.main(
            [
                "seal-review-adjudication",
                *common,
                "--task",
                str(task_path),
                "--primary",
                str(observation_paths[0]),
                "--independent",
                str(observation_paths[1]),
                "--draft",
                str(adjudication_draft_path),
                "--output",
                str(adjudication_path),
            ]
        )
        == 0
    )
    assert (
        cli.main(
            [
                "validate-review-adjudication",
                *common,
                "--task",
                str(task_path),
                "--primary",
                str(observation_paths[0]),
                "--independent",
                str(observation_paths[1]),
                "--adjudication",
                str(adjudication_path),
            ]
        )
        == 0
    )
    adjudication = json.loads(adjudication_path.read_text(encoding="utf-8"))
    assert adjudication["authority_scope"] == "pilot_pair_boundary_only"
    assert adjudication["training_promotion_allowed"] is False
