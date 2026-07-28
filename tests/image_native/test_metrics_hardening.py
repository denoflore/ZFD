"""Held out metrics stay separate from training lineage and require reviewed geometry."""

from __future__ import annotations

import pytest

from zfd_image_native.metrics import (
    GoldSequence,
    LineageAuthorityRecord,
    PredictedSequence,
    SegmentationObservation,
    evaluate_predictions,
)


SOURCE_HASH = "a" * 64
GOLD_DERIVATIVE_HASH = "b" * 64
SEGMENTATION_DERIVATIVE_HASH = "c" * 64
TRAIN_SOURCE_HASH = "d" * 64
TRAIN_DERIVATIVE_HASH = "e" * 64


def _gold() -> GoldSequence:
    return GoldSequence(
        record_id="line-1",
        labels=("a", None, "c"),
        manuscript_id="ms-1",
        hand_id="hand-1",
        style="angular_cursive",
        adjudicated=True,
        source_sha256=SOURCE_HASH,
        derivative_sha256=GOLD_DERIVATIVE_HASH,
        lineage_root_id="root-held-out",
        split="held_out",
        reviewer_id="reviewer-1",
        adjudicator_id="adjudicator-1",
    )


def _prediction() -> PredictedSequence:
    return PredictedSequence(
        record_id="line-1",
        labels=("a", None, "c"),
        confidences=(0.9, 0.8, 0.9),
        unknown_scores=(0.1, 0.9, 0.1),
        source_sha256=SOURCE_HASH,
        derivative_sha256=GOLD_DERIVATIVE_HASH,
    )


def _segmentation() -> SegmentationObservation:
    return SegmentationObservation(
        record_id="page-1",
        manuscript_id="ms-1",
        hand_id="hand-1",
        style="angular_cursive",
        reference_regions=4,
        predicted_regions=5,
        matched_regions=4,
        mean_iou=0.75,
        adjudicated=True,
        source_sha256=SOURCE_HASH,
        derivative_sha256=SEGMENTATION_DERIVATIVE_HASH,
        lineage_root_id="root-held-out",
        split="held_out",
    )


def _authority(
    *,
    training_manuscript: str = "ms-train",
    training_hand: str = "hand-train",
    training_source_hash: str = TRAIN_SOURCE_HASH,
    training_derivative_hash: str = TRAIN_DERIVATIVE_HASH,
    training_lineage_root: str = "root-train",
) -> tuple[LineageAuthorityRecord, ...]:
    return (
        LineageAuthorityRecord(
            record_id="train-line-1",
            corpus_role="training",
            manuscript_id=training_manuscript,
            hand_id=training_hand,
            style="angular_cursive",
            exact_sha256=training_source_hash,
            derivative_sha256=training_derivative_hash,
            lineage_root_id=training_lineage_root,
            split="train",
        ),
        LineageAuthorityRecord(
            record_id="line-1",
            corpus_role="gold",
            manuscript_id="ms-1",
            hand_id="hand-1",
            style="angular_cursive",
            exact_sha256=SOURCE_HASH,
            derivative_sha256=GOLD_DERIVATIVE_HASH,
            lineage_root_id="root-held-out",
            split="held_out",
        ),
        LineageAuthorityRecord(
            record_id="page-1",
            corpus_role="gold",
            manuscript_id="ms-1",
            hand_id="hand-1",
            style="angular_cursive",
            exact_sha256=SOURCE_HASH,
            derivative_sha256=SEGMENTATION_DERIVATIVE_HASH,
            lineage_root_id="root-held-out",
            split="held_out",
        ),
    )


def test_complete_held_out_evaluation_can_authorize_accuracy_claim() -> None:
    metrics = evaluate_predictions(
        [_gold()],
        [_prediction()],
        segmentation=[_segmentation()],
        lineage_authority=_authority(),
    )

    assert metrics.status == "measured"
    assert metrics.adjudicated_gold_count == 1
    assert metrics.validation_errors == ()
    assert metrics.accuracy_claim_allowed is True
    assert metrics.cer == pytest.approx(0.0)
    assert metrics.unknown_precision == pytest.approx(1.0)
    assert metrics.unknown_recall == pytest.approx(1.0)
    assert metrics.segmentation_mean_iou == pytest.approx(0.75)
    assert metrics.segmentation_precision == pytest.approx(0.8)
    assert metrics.segmentation_recall == pytest.approx(1.0)
    assert metrics.segmentation_by_hand["hand-1"]["mean_iou"] == pytest.approx(0.75)


def test_training_hash_and_lineage_overlap_block_accuracy_claim() -> None:
    metrics = evaluate_predictions(
        [_gold()],
        [_prediction()],
        segmentation=[_segmentation()],
        lineage_authority=_authority(
            training_manuscript="ms-1",
            training_hand="hand-1",
            training_source_hash=SOURCE_HASH,
            training_derivative_hash=GOLD_DERIVATIVE_HASH,
            training_lineage_root="root-held-out",
        ),
    )

    assert metrics.accuracy_claim_allowed is False
    assert f"DUPLICATE_HASH_LEAKAGE:{SOURCE_HASH}" in metrics.validation_errors
    assert f"DERIVATIVE_HASH_LEAKAGE:{GOLD_DERIVATIVE_HASH}" in metrics.validation_errors
    assert "LINEAGE_LEAKAGE:root-held-out" in metrics.validation_errors
    assert "MANUSCRIPT_LEAKAGE:ms-1" in metrics.validation_errors
    assert "HAND_LEAKAGE:hand-1" in metrics.validation_errors


def test_missing_or_empty_lineage_authority_fails_closed() -> None:
    missing = evaluate_predictions([_gold()], [_prediction()], segmentation=[_segmentation()])
    empty = evaluate_predictions(
        [_gold()], [_prediction()], segmentation=[_segmentation()], lineage_authority=[]
    )

    assert missing.accuracy_claim_allowed is False
    assert "LINEAGE_AUTHORITY_MISSING" in missing.validation_errors
    assert empty.accuracy_claim_allowed is False
    assert "LINEAGE_AUTHORITY_EMPTY" in empty.validation_errors


def test_missing_prediction_record_is_scored_and_cannot_authorize_claim() -> None:
    metrics = evaluate_predictions(
        [_gold()],
        [],
        segmentation=[_segmentation()],
        lineage_authority=_authority(),
    )

    assert metrics.character_edits == len(_gold().labels)
    assert metrics.deletions == len(_gold().labels)
    assert metrics.accuracy_claim_allowed is False
    assert "PREDICTION_RECORD_MISSING:line-1" in metrics.validation_errors


def test_authority_requires_exact_derivative_and_split_metadata() -> None:
    broken = list(_authority())
    broken[0] = LineageAuthorityRecord(
        record_id="train-line-1",
        corpus_role="training",
        manuscript_id="",
        hand_id="",
        style="",
        exact_sha256="bad",
        derivative_sha256="",
        lineage_root_id="",
        split="",
    )

    metrics = evaluate_predictions(
        [_gold()],
        [_prediction()],
        segmentation=[_segmentation()],
        lineage_authority=broken,
    )

    assert metrics.accuracy_claim_allowed is False
    assert "AUTHORITY_MANUSCRIPT_MISSING:train-line-1" in metrics.validation_errors
    assert "AUTHORITY_HAND_MISSING:train-line-1" in metrics.validation_errors
    assert "AUTHORITY_EXACT_HASH_INVALID:train-line-1" in metrics.validation_errors
    assert "AUTHORITY_DERIVATIVE_HASH_INVALID:train-line-1" in metrics.validation_errors
    assert "AUTHORITY_SPLIT_INVALID:train-line-1" in metrics.validation_errors


def test_missing_alignment_metadata_and_geometry_gold_are_reported() -> None:
    gold = GoldSequence(
        record_id="line-1",
        labels=("a",),
        manuscript_id="ms-1",
        hand_id="hand-1",
        style="angular_cursive",
        adjudicated=True,
    )
    prediction = PredictedSequence("line-1", ("a",), (), (), source_sha256=None)

    metrics = evaluate_predictions([gold], [prediction])

    assert metrics.status == "measured"
    assert metrics.accuracy_claim_allowed is False
    assert "GOLD_SOURCE_HASH_INVALID:line-1" in metrics.validation_errors
    assert "GOLD_LINEAGE_MISSING:line-1" in metrics.validation_errors
    assert "GOLD_ADJUDICATION_IDENTITY_MISSING:line-1" in metrics.validation_errors
    assert "CONFIDENCE_LENGTH_MISMATCH:line-1" in metrics.validation_errors
    assert "UNKNOWN_SCORE_LENGTH_MISMATCH:line-1" in metrics.validation_errors
    assert "ADJUDICATED_SEGMENTATION_GOLD_EMPTY" in metrics.validation_errors


def test_edit_alignment_preserves_labels_after_middle_insertion() -> None:
    gold = _gold().__class__(
        **{
            **_gold().__dict__,
            "labels": ("a", None, "c"),
        }
    )
    prediction = _prediction().__class__(
        **{
            **_prediction().__dict__,
            "labels": ("a", "x", None, "c"),
            "confidences": (0.9, 0.2, 0.8, 0.9),
            "unknown_scores": (0.1, 0.1, 0.9, 0.1),
        }
    )

    metrics = evaluate_predictions(
        [gold],
        [prediction],
        segmentation=[_segmentation()],
        lineage_authority=_authority(),
    )

    assert metrics.character_edits == 1
    assert metrics.insertions == 1
    assert metrics.deletions == 0
    assert metrics.substitutions == 0
    assert metrics.confusion["<INSERTION>"]["x"] == 1
    assert metrics.confusion["<UNKNOWN>"]["<UNKNOWN>"] == 1
    assert metrics.confusion["c"]["c"] == 1
    assert metrics.unknown_true_positive == 1
    assert metrics.unknown_false_positive == 0
    assert metrics.unknown_false_negative == 0


def test_edit_alignment_reports_middle_deletion_without_shifting_tail() -> None:
    gold = _gold().__class__(
        **{
            **_gold().__dict__,
            "labels": ("a", "b", "c"),
        }
    )
    prediction = _prediction().__class__(
        **{
            **_prediction().__dict__,
            "labels": ("a", "c"),
            "confidences": (0.9, 0.9),
            "unknown_scores": (0.1, 0.1),
        }
    )

    metrics = evaluate_predictions(
        [gold],
        [prediction],
        segmentation=[_segmentation()],
        lineage_authority=_authority(),
    )

    assert metrics.character_edits == 1
    assert metrics.insertions == 0
    assert metrics.deletions == 1
    assert metrics.substitutions == 0
    assert metrics.confusion["b"]["<DELETION>"] == 1
    assert metrics.confusion["c"]["c"] == 1
