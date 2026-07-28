"""Image aligned visual review preserves pixels, uncertainty, and separation."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from zfd_image_native.boundary import scan_primary_lane
from zfd_image_native.io import canonical_json
from zfd_gold import (
    VisualReviewTaskConfig,
    build_line_task,
    seal_adjudication,
    seal_observation,
    validate_adjudication,
    validate_line_task,
    validate_observation,
)
from zfd_gold.cli import _resolve_output, _write_new


def _hash(value) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _polygon(box: tuple[int, int, int, int]) -> list[list[int]]:
    x, y, width, height = box
    return [[x, y], [x + width, y], [x + width, y + height], [x, y + height]]


class _Page:
    def __init__(self) -> None:
        self.image = np.full((50, 100, 3), 255, dtype=np.uint8)
        self.image[10:20, 10:15] = 0
        self.image[10:20, 16:20] = 0
        self.image[10:20, 30:36] = 0
        self.page = SimpleNamespace(
            page_id="yale-ms-408:iiif:fixture",
            source_id="yale-ms-408",
            iiif_id="fixture",
            surface_label="1r",
            image_sha256="1" * 64,
            width=100,
            height=50,
        )
        self.page_receipt = {
            "receipt_sha256": "2" * 64,
            "ocr_id": "sha256:" + "3" * 64,
            "config_sha256": "4" * 64,
            "segmentation_version": "2.0.0",
        }
        self.run_receipt = {
            "run_id": "sha256:" + "5" * 64,
            "receipt_sha256": "6" * 64,
        }
        self.artifact_sha256 = "7" * 64
        self.region_id = f"{self.page.page_id}:region:0001"
        self.line_id = f"{self.page.page_id}:line:0001"
        self.boxes = ((10, 10, 5, 10), (16, 10, 4, 10), (30, 10, 6, 10))
        self.candidate_ids = tuple("sha256:" + str(index) * 64 for index in range(8, 11))
        self.grapheme_ids = tuple(
            f"{self.page.page_id}:grapheme:{index:06d}" for index in range(1, 4)
        )
        self.artifact = {
            "regions": [
                {
                    "region_id": self.region_id,
                    "bbox": [5, 5, 80, 30],
                    "polygon": _polygon((5, 5, 80, 30)),
                    "line_ids": [self.line_id],
                }
            ],
            "lines": [
                {
                    "line_id": self.line_id,
                    "region_id": self.region_id,
                    "bbox": [5, 5, 80, 30],
                    "polygon": _polygon((5, 5, 80, 30)),
                    "grapheme_ids": list(self.grapheme_ids),
                    "geometry_mode": "cartesian_fragment",
                }
            ],
            "graphemes": [
                {
                    "grapheme_id": grapheme_id,
                    "line_id": self.line_id,
                    "region_id": self.region_id,
                    "bbox": list(box),
                    "polygon": _polygon(box),
                }
                for grapheme_id, box in zip(self.grapheme_ids, self.boxes, strict=True)
            ],
        }

    def read_artifact(self):
        return deepcopy(self.artifact)

    def read_image(self):
        return self.image.copy()


def _visual(page: _Page) -> dict:
    rows = []
    for index, (candidate_id, grapheme_id, box) in enumerate(
        zip(page.candidate_ids, page.grapheme_ids, page.boxes, strict=True), start=1
    ):
        rows.append(
            {
                "candidate_id": candidate_id,
                "stage_a_grapheme_id": grapheme_id,
                "line_id": page.line_id,
                "region_id": page.region_id,
                "bbox": list(box),
                "polygon": _polygon(box),
                "crop_bbox": [max(0, box[0] - 2), max(0, box[1] - 2), box[2] + 4, box[3] + 4],
                "crop_sha256": format(index, "x") * 64,
                "descriptor_sha256": format(index + 3, "x") * 64,
                "descriptor_aspect_ratio": box[2] / box[3],
                "assigned_page_local_exemplar_id": "sha256:" + format(index + 10, "x") * 64,
                "diplomatic_label": None,
                "unknown_score": None,
                "recognition_confidence": None,
            }
        )
    payload = {
        "schema": "zfd.page_local_visual_index.v1",
        "schema_version": "1.0.0",
        "page_id": page.page.page_id,
        "source_id": page.page.source_id,
        "image_sha256": page.page.image_sha256,
        "stage_a_authority": {
            "run_id": page.run_receipt["run_id"],
            "run_receipt_sha256": page.run_receipt["receipt_sha256"],
            "page_receipt_sha256": page.page_receipt["receipt_sha256"],
            "ocr_id": page.page_receipt["ocr_id"],
            "artifact_sha256": page.artifact_sha256,
            "config_sha256": page.page_receipt["config_sha256"],
            "segmentation_version": page.page_receipt["segmentation_version"],
        },
        "implementation_sha256": "b" * 64,
        "dependency_set_sha256": "c" * 64,
        "config_sha256": "d" * 64,
        "candidates": rows,
        "semantic_class_authority_count": 0,
        "accuracy_claim_allowed": False,
        "confirmed_translated": False,
        "inherited_text_used": False,
    }
    return {**payload, "receipt_sha256": _hash(payload)}


def _task_fixture():
    page = _Page()
    task, crop = build_line_task(
        page,
        _visual(page),
        visual_index_file_sha256="e" * 64,
        line_id=page.line_id,
        config=VisualReviewTaskConfig(crop_padding_x=2, crop_padding_y=2),
    )
    return page, task, crop


def _observation_draft(page: _Page, *, annotator: str, role: str) -> dict:
    return {
        "schema": "zfd.visual_form_observation_draft.v1",
        "task_id": None,
        "annotator_id": annotator,
        "observer_role": role,
        "independent_viewing_attestation": True,
        "source_lane": "human_image_aligned",
        "inherited_text_used": False,
        "glyphs": [
            {
                "ordinal": 0,
                "bbox": [10, 10, 10, 10],
                "polygons": [_polygon((10, 10, 5, 10)), _polygon((16, 10, 4, 10))],
                "stage_a_candidate_ids": list(page.candidate_ids[:2]),
                "label_state": "opaque_form",
                "opaque_class_id": "opaque:0001",
                "alternatives": [],
                "certainty": "clear",
                "uncertainty_codes": [],
            },
            {
                "ordinal": 1,
                "bbox": [30, 10, 6, 10],
                "polygons": [_polygon((30, 10, 6, 10))],
                "stage_a_candidate_ids": [page.candidate_ids[2]],
                "label_state": "opaque_form",
                "opaque_class_id": "opaque:0002",
                "alternatives": ["opaque:0003"],
                "certainty": "probable",
                "uncertainty_codes": ["visually_ambiguous_form"],
            },
        ],
        "candidate_exclusions": [],
    }


def test_line_task_binds_pixels_stage_a_visual_index_and_all_candidates() -> None:
    page, task, crop = _task_fixture()

    assert task["schema"] == "zfd.line_visual_form_review_task.v1"
    assert task["page_id"] == page.page.page_id
    assert task["line_id"] == page.line_id
    assert task["candidate_count"] == 3
    assert task["crop"]["encoded_asset_sha256"] == sha256(crop).hexdigest()
    assert task["split"]["assignment_state"] == "unassigned"
    assert task["semantic_class_authority_count"] == 0
    assert task["sequence_authority_status"] == "not_established"
    assert task["accuracy_claim_allowed"] is False
    assert task["confirmed_translated"] is False
    assert task["inherited_text_used"] is False
    assert validate_line_task(
        task,
        page,
        _visual(page),
        visual_index_file_sha256="e" * 64,
        crop_png=crop,
    ) == ()


def test_line_task_rejects_candidate_crop_and_source_identity_tampering() -> None:
    page, task, crop = _task_fixture()

    for mutation in ("candidate", "crop", "page"):
        changed = deepcopy(task)
        if mutation == "candidate":
            changed["candidates"][0]["bbox"][0] += 1
        elif mutation == "crop":
            changed["crop"]["raw_pixel_sha256"] = "0" * 64
        else:
            changed["image_sha256"] = "0" * 64
        errors = validate_line_task(
            changed,
            page,
            _visual(page),
            visual_index_file_sha256="e" * 64,
            crop_png=crop,
        )
        assert "GOLD_TASK_RECOMPUTE_MISMATCH" in errors


def test_observation_seals_merge_and_single_glyphs_from_exact_pixels() -> None:
    page, task, _ = _task_fixture()
    draft = _observation_draft(page, annotator="annotator-a", role="primary_annotator")
    draft["task_id"] = task["task_id"]

    observation = seal_observation(task, draft, page.read_image())

    assert observation["line_state"] == "visual_form_review_complete"
    assert [row["segmentation_relation"] for row in observation["glyphs"]] == [
        "merge",
        "single",
    ]
    assert {row["status"] for row in observation["component_dispositions"]} == {
        "merge_member",
        "used_single",
    }
    assert all(len(row["pixel_occurrence_id"]) == 71 for row in observation["glyphs"])
    assert observation["authority_promotion_eligible"] is False
    assert observation["semantic_class_authority_count"] == 0
    assert validate_observation(observation, task, page.read_image()) == ()


def test_observation_preserves_unresolved_component_and_rejects_silent_gap() -> None:
    page, task, _ = _task_fixture()
    draft = _observation_draft(page, annotator="annotator-a", role="primary_annotator")
    draft["task_id"] = task["task_id"]
    draft["glyphs"].pop()

    with pytest.raises(ValueError, match="CANDIDATE_DISPOSITION_MISSING"):
        seal_observation(task, draft, page.read_image())

    draft["candidate_exclusions"] = [
        {
            "candidate_id": page.candidate_ids[2],
            "status": "unresolved",
            "reason_code": "boundary_uncertain",
        }
    ]
    observation = seal_observation(task, draft, page.read_image())

    assert observation["line_state"] == "visual_form_review_complete_with_unresolved"
    assert observation["component_dispositions"][-1]["status"] == "unresolved"
    assert observation["authority_promotion_eligible"] is False
    assert validate_observation(observation, task, page.read_image()) == ()


def test_observation_rejects_semantic_label_and_unblinded_lane() -> None:
    page, task, _ = _task_fixture()
    draft = _observation_draft(page, annotator="annotator-a", role="primary_annotator")
    draft["task_id"] = task["task_id"]
    draft["glyphs"][0]["opaque_class_id"] = "Ⰰ"
    draft["inherited_text_used"] = True

    with pytest.raises(ValueError) as error:
        seal_observation(task, draft, page.read_image())
    assert "OPAQUE_CLASS_ID_INVALID" in str(error.value) or "SOURCE_LANE_TAINTED" in str(error.value)

    hidden_field = _observation_draft(
        page, annotator="annotator-a", role="primary_annotator"
    )
    hidden_field["task_id"] = task["task_id"]
    hidden_field["glyphs"][0]["diplomatic_label"] = "forbidden"
    with pytest.raises(ValueError, match="GLYPH_DRAFT_FIELDS_UNEXPECTED"):
        seal_observation(task, hidden_field, page.read_image())


def test_observation_rejects_pixels_that_do_not_match_the_task_crop() -> None:
    page, task, _ = _task_fixture()
    draft = _observation_draft(page, annotator="annotator-a", role="primary_annotator")
    draft["task_id"] = task["task_id"]
    changed = page.read_image()
    changed[10, 10] = 255

    with pytest.raises(ValueError, match="SOURCE_IMAGE_TASK_PIXEL_MISMATCH"):
        seal_observation(task, draft, changed)


def test_observation_rejects_candidate_reference_with_disjoint_geometry() -> None:
    page, task, _ = _task_fixture()
    draft = _observation_draft(page, annotator="annotator-a", role="primary_annotator")
    draft["task_id"] = task["task_id"]
    draft["glyphs"][0]["stage_a_candidate_ids"] = [page.candidate_ids[2]]
    draft["glyphs"][1]["stage_a_candidate_ids"] = []

    with pytest.raises(ValueError, match="GLYPH_CANDIDATE_GEOMETRY_DISJOINT"):
        seal_observation(task, draft, page.read_image())


def test_observation_rejects_candidate_inside_empty_polygon_gap() -> None:
    page, task, _ = _task_fixture()
    draft = _observation_draft(page, annotator="annotator-a", role="primary_annotator")
    draft["task_id"] = task["task_id"]
    draft["glyphs"][0]["bbox"] = [10, 3, 10, 24]
    draft["glyphs"][0]["polygons"] = [
        _polygon((10, 3, 10, 6)),
        _polygon((10, 21, 10, 6)),
    ]

    with pytest.raises(ValueError, match="GLYPH_CANDIDATE_GEOMETRY_DISJOINT"):
        seal_observation(task, draft, page.read_image())


def test_observation_rejects_degenerate_duplicate_and_semantic_code_channels() -> None:
    page, task, _ = _task_fixture()
    base = _observation_draft(page, annotator="annotator-a", role="primary_annotator")
    base["task_id"] = task["task_id"]

    degenerate = deepcopy(base)
    degenerate["glyphs"][0]["polygons"] = [[[10, 10], [15, 10], [20, 10]]]
    with pytest.raises(ValueError, match="GLYPH_POLYGONS_INVALID"):
        seal_observation(task, degenerate, page.read_image())

    duplicate = deepcopy(base)
    duplicate["glyphs"].append(deepcopy(duplicate["glyphs"][0]))
    duplicate["glyphs"][-1]["ordinal"] = 2
    with pytest.raises(ValueError, match="DUPLICATE_GLYPH_PIXEL_OCCURRENCE"):
        seal_observation(task, duplicate, page.read_image())

    semantic_code = deepcopy(base)
    semantic_code["glyphs"][0]["uncertainty_codes"] = ["translation:herb"]
    with pytest.raises(ValueError, match="UNCERTAINTY_CODES_INVALID"):
        seal_observation(task, semantic_code, page.read_image())


def _adjudication_draft(task: dict, primary: dict, reviewer: dict) -> dict:
    return {
        "schema": "zfd.visual_form_adjudication_draft.v1",
        "task_id": task["task_id"],
        "primary_observation_receipt_sha256": primary["receipt_sha256"],
        "review_observation_receipt_sha256": reviewer["receipt_sha256"],
        "adjudicator_id": "adjudicator-c",
        "source_lane": "human_image_aligned",
        "inherited_text_used": False,
        "glyphs": [
            {
                "ordinal": row["ordinal"],
                "bbox": row["bbox"],
                "polygons": row["polygons"],
                "stage_a_candidate_ids": row["stage_a_candidate_ids"],
                "label_state": row["label_state"],
                "opaque_class_id": row["opaque_class_id"],
                "alternatives": row["alternatives"],
                "certainty": row["certainty"],
                "uncertainty_codes": row["uncertainty_codes"],
                "source_observation_glyph_ids": {
                    "primary": [row["glyph_observation_id"]],
                    "independent_reviewer": [
                        reviewer["glyphs"][row["ordinal"]]["glyph_observation_id"]
                    ],
                },
                "rationale_codes": ["independent_observations_agree"],
            }
            for row in primary["glyphs"]
        ],
        "candidate_exclusions": [],
        "source_glyph_dispositions": [],
    }


def test_adjudication_requires_independent_roles_and_keeps_authority_zero() -> None:
    page, task, _ = _task_fixture()
    primary_draft = _observation_draft(page, annotator="annotator-a", role="primary_annotator")
    review_draft = _observation_draft(page, annotator="reviewer-b", role="independent_reviewer")
    primary_draft["task_id"] = task["task_id"]
    review_draft["task_id"] = task["task_id"]
    primary = seal_observation(task, primary_draft, page.read_image())
    reviewer = seal_observation(task, review_draft, page.read_image())

    assert primary["glyphs"][0]["glyph_observation_id"] != reviewer["glyphs"][0][
        "glyph_observation_id"
    ]
    assert primary["glyphs"][0]["pixel_occurrence_id"] == reviewer["glyphs"][0][
        "pixel_occurrence_id"
    ]

    adjudication = seal_adjudication(
        task,
        primary,
        reviewer,
        _adjudication_draft(task, primary, reviewer),
        page.read_image(),
    )

    assert adjudication["review_state"] == "visual_form_adjudicated"
    assert adjudication["semantic_class_authority_count"] == 0
    assert adjudication["authority_promotion_eligible"] is False
    assert adjudication["diplomatic_sequence_authority_eligible"] is False
    assert "SPLIT_AUTHORITY_UNASSIGNED" in adjudication["blocking_reasons"]
    assert validate_adjudication(
        adjudication, task, primary, reviewer, page.read_image()
    ) == ()

    swapped = _adjudication_draft(task, primary, reviewer)
    swapped["glyphs"][0]["source_observation_glyph_ids"]["independent_reviewer"] = [
        reviewer["glyphs"][1]["glyph_observation_id"]
    ]
    with pytest.raises(ValueError, match="ADJUDICATED_GLYPH_SOURCE_GEOMETRY_DISJOINT"):
        seal_adjudication(task, primary, reviewer, swapped, page.read_image())

    same_person = _adjudication_draft(task, primary, reviewer)
    same_person["adjudicator_id"] = "REVIEWER-B"
    with pytest.raises(ValueError, match="REVIEW_IDENTITIES_NOT_DISTINCT"):
        seal_adjudication(task, primary, reviewer, same_person, page.read_image())


def test_adjudication_can_retain_merge_split_disagreement_from_both_observers() -> None:
    page, task, _ = _task_fixture()
    primary_draft = _observation_draft(page, annotator="annotator-a", role="primary_annotator")
    primary_draft["task_id"] = task["task_id"]
    primary = seal_observation(task, primary_draft, page.read_image())

    reviewer_draft = _observation_draft(
        page, annotator="reviewer-b", role="independent_reviewer"
    )
    reviewer_draft["task_id"] = task["task_id"]
    reviewer_draft["glyphs"] = [
        {
            "ordinal": index,
            "bbox": list(box),
            "polygons": [_polygon(box)],
            "stage_a_candidate_ids": [candidate_id],
            "label_state": "opaque_form",
            "opaque_class_id": f"opaque:{index + 1:04d}",
            "alternatives": [],
            "certainty": "clear",
            "uncertainty_codes": [],
        }
        for index, (box, candidate_id) in enumerate(
            zip(page.boxes, page.candidate_ids, strict=True)
        )
    ]
    reviewer = seal_observation(task, reviewer_draft, page.read_image())
    draft = _adjudication_draft(task, primary, reviewer)
    draft["glyphs"][0]["source_observation_glyph_ids"]["independent_reviewer"] = [
        reviewer["glyphs"][0]["glyph_observation_id"],
        reviewer["glyphs"][1]["glyph_observation_id"],
    ]
    draft["glyphs"][1]["source_observation_glyph_ids"]["independent_reviewer"] = [
        reviewer["glyphs"][2]["glyph_observation_id"]
    ]

    adjudication = seal_adjudication(task, primary, reviewer, draft, page.read_image())

    assert validate_adjudication(
        adjudication, task, primary, reviewer, page.read_image()
    ) == ()
    assert len(
        adjudication["glyphs"][0]["source_observation_glyph_ids"][
            "independent_reviewer"
        ]
    ) == 2


def test_adjudication_rejects_bbox_overlap_without_source_polygon_overlap() -> None:
    page, task, _ = _task_fixture()
    primary_draft = _observation_draft(
        page, annotator="annotator-a", role="primary_annotator"
    )
    reviewer_draft = _observation_draft(
        page, annotator="reviewer-b", role="independent_reviewer"
    )
    for source_draft in (primary_draft, reviewer_draft):
        source_draft["task_id"] = task["task_id"]
        source_draft["glyphs"][0]["polygons"] = [
            _polygon((10, 10, 3, 10)),
            _polygon((17, 10, 3, 10)),
        ]
    primary = seal_observation(task, primary_draft, page.read_image())
    reviewer = seal_observation(task, reviewer_draft, page.read_image())
    for empty_box in ((14, 10, 2, 10), (13, 10, 4, 10)):
        draft = _adjudication_draft(task, primary, reviewer)
        draft["glyphs"][0]["bbox"] = list(empty_box)
        draft["glyphs"][0]["polygons"] = [_polygon(empty_box)]
        draft["glyphs"][0]["stage_a_candidate_ids"] = []

        with pytest.raises(
            ValueError, match="ADJUDICATED_GLYPH_SOURCE_GEOMETRY_DISJOINT"
        ):
            seal_adjudication(task, primary, reviewer, draft, page.read_image())


def test_adjudication_requires_every_source_glyph_or_explicit_disposition() -> None:
    page, task, _ = _task_fixture()
    primary_draft = _observation_draft(page, annotator="annotator-a", role="primary_annotator")
    reviewer_draft = _observation_draft(
        page, annotator="reviewer-b", role="independent_reviewer"
    )
    primary_draft["task_id"] = task["task_id"]
    reviewer_draft["task_id"] = task["task_id"]
    reviewer_draft["glyphs"].append(
        {
            "ordinal": 2,
            "bbox": [40, 10, 3, 5],
            "polygons": [_polygon((40, 10, 3, 5))],
            "stage_a_candidate_ids": [],
            "label_state": "opaque_form",
            "opaque_class_id": "opaque:0004",
            "alternatives": [],
            "certainty": "uncertain",
            "uncertainty_codes": ["other_visual_uncertainty"],
        }
    )
    primary = seal_observation(task, primary_draft, page.read_image())
    reviewer = seal_observation(task, reviewer_draft, page.read_image())
    draft = _adjudication_draft(task, primary, reviewer)

    with pytest.raises(
        ValueError, match="SOURCE_OBSERVATION_GLYPH_DISPOSITION_MISSING"
    ):
        seal_adjudication(task, primary, reviewer, draft, page.read_image())

    draft["source_glyph_dispositions"] = [
        {
            "observer_role": "independent_reviewer",
            "glyph_observation_id": reviewer["glyphs"][2]["glyph_observation_id"],
            "disposition": "excluded_non_text",
            "rationale_code": "non_text_selected",
        }
    ]
    adjudication = seal_adjudication(task, primary, reviewer, draft, page.read_image())
    assert validate_adjudication(
        adjudication, task, primary, reviewer, page.read_image()
    ) == ()

    unresolved_draft = deepcopy(draft)
    unresolved_draft["source_glyph_dispositions"][0][
        "disposition"
    ] = "unresolved_conflict"
    unresolved_draft["source_glyph_dispositions"][0][
        "rationale_code"
    ] = "unresolved_retained"
    unresolved = seal_adjudication(
        task, primary, reviewer, unresolved_draft, page.read_image()
    )
    assert unresolved["review_state"] == "visual_form_adjudicated_with_unresolved"
    assert "ADJUDICATED_LINE_CONTAINS_UNRESOLVED" in unresolved["blocking_reasons"]


def test_polygon_canonicalization_and_status_reason_pairs_fail_closed() -> None:
    page, task, _ = _task_fixture()
    base = _observation_draft(page, annotator="annotator-a", role="primary_annotator")
    base["task_id"] = task["task_id"]

    reversed_duplicate = deepcopy(base)
    duplicate = deepcopy(reversed_duplicate["glyphs"][0])
    duplicate["ordinal"] = 2
    duplicate["polygons"] = [
        list(reversed(polygon)) for polygon in reversed(duplicate["polygons"])
    ]
    reversed_duplicate["glyphs"].append(duplicate)
    with pytest.raises(ValueError, match="DUPLICATE_GLYPH_PIXEL_OCCURRENCE"):
        seal_observation(task, reversed_duplicate, page.read_image())

    collinear_duplicate = deepcopy(base)
    collinear = deepcopy(collinear_duplicate["glyphs"][0])
    collinear["ordinal"] = 2
    collinear["polygons"][0].insert(1, [12, 10])
    collinear_duplicate["glyphs"].append(collinear)
    with pytest.raises(ValueError, match="DUPLICATE_GLYPH_PIXEL_OCCURRENCE"):
        seal_observation(task, collinear_duplicate, page.read_image())

    nested = deepcopy(base)
    nested["glyphs"][0]["polygons"].append(_polygon((11, 12, 2, 3)))
    with pytest.raises(ValueError, match="GLYPH_POLYGONS_OVERLAP"):
        seal_observation(task, nested, page.read_image())

    self_intersecting = deepcopy(base)
    self_intersecting["glyphs"][0]["bbox"] = [10, 10, 10, 10]
    self_intersecting["glyphs"][0]["polygons"] = [
        [[10, 10], [20, 10], [10, 20], [16, 16]]
    ]
    with pytest.raises(ValueError, match="GLYPH_POLYGONS_INVALID"):
        seal_observation(task, self_intersecting, page.read_image())

    mismatched_reason = deepcopy(base)
    mismatched_reason["glyphs"].pop()
    mismatched_reason["candidate_exclusions"] = [
        {
            "candidate_id": page.candidate_ids[2],
            "status": "non_text",
            "reason_code": "boundary_uncertain",
        }
    ]
    with pytest.raises(ValueError, match="CANDIDATE_EXCLUSION_REASON_INVALID"):
        seal_observation(task, mismatched_reason, page.read_image())


def test_gold_package_has_no_primary_lane_text_dependency() -> None:
    hits = scan_primary_lane(
        __file__.replace("tests\\image_native\\test_gold_task.py", "zfd_gold"),
        {
            "eva",
            "ivtff",
            "zandbergen",
            "lsi_ivtff",
            "voynich-transcription",
            "zfd_decoder",
            "02_transcriptions",
            "raw_eva",
            "transcriptions",
            "translations",
            "lexicon.csv",
        },
    )
    assert hits == []


def test_gold_outputs_are_new_and_confined_to_dedicated_roots(tmp_path) -> None:
    stage = tmp_path / "evidence" / "stage-a"
    authority = tmp_path / "authority"
    stage.mkdir(parents=True)
    authority.mkdir()
    run = SimpleNamespace(
        repository_root=tmp_path,
        stage_a_root=stage,
        authority_root=authority,
        manifest_path=tmp_path / "manifest.jsonl",
        image_paths=(),
    )

    target = _resolve_output(Path("evidence/stage-a/review/task.json"), run)
    assert target == (stage / "review" / "task.json").resolve()

    with pytest.raises(ValueError, match="GOLD_OUTPUT_OUTSIDE_ALLOWED_ROOT"):
        _resolve_output(Path("docs/task.json"), run)

    target.parent.mkdir(parents=True)
    target.write_text("occupied", encoding="utf-8")
    with pytest.raises(ValueError, match="GOLD_OUTPUT_ALREADY_EXISTS"):
        _resolve_output(target, run)


def test_exclusive_writer_does_not_overwrite_target_created_after_resolution(
    tmp_path,
) -> None:
    target = tmp_path / "review.json"
    target.write_text("concurrent-owner", encoding="utf-8")

    with pytest.raises(FileExistsError):
        _write_new(target, b"review-writer")

    assert target.read_text(encoding="utf-8") == "concurrent-owner"
