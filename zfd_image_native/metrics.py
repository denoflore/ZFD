"""Held-out sequence metrics with explicit not measured state."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterable


@dataclass(frozen=True)
class GoldSequence:
    record_id: str
    labels: tuple[str | None, ...]
    manuscript_id: str
    hand_id: str
    style: str
    adjudicated: bool
    source_sha256: str | None = None
    derivative_sha256: str | None = None
    lineage_root_id: str | None = None
    split: str = "test"
    reviewer_id: str | None = None
    adjudicator_id: str | None = None


@dataclass(frozen=True)
class PredictedSequence:
    record_id: str
    labels: tuple[str | None, ...]
    confidences: tuple[float, ...]
    unknown_scores: tuple[float, ...]
    source_sha256: str | None = None
    derivative_sha256: str | None = None


@dataclass(frozen=True)
class SegmentationObservation:
    record_id: str
    manuscript_id: str
    hand_id: str
    style: str
    reference_regions: int
    predicted_regions: int
    matched_regions: int
    mean_iou: float
    adjudicated: bool
    source_sha256: str | None = None
    derivative_sha256: str | None = None
    lineage_root_id: str | None = None
    split: str = "test"


@dataclass(frozen=True)
class LineageAuthorityRecord:
    """One immutable training or held out asset in the evaluation split authority."""

    record_id: str
    corpus_role: str
    manuscript_id: str
    hand_id: str
    style: str
    exact_sha256: str
    derivative_sha256: str
    lineage_root_id: str
    split: str


@dataclass(frozen=True)
class EvaluationMetrics:
    status: str
    adjudicated_gold_count: int
    character_edits: int | None
    substitutions: int | None
    insertions: int | None
    deletions: int | None
    reference_characters: int | None
    cer: float | None
    sequence_error: float | None
    confusion: dict[str, dict[str, int]]
    unknown_true_positive: int | None
    unknown_false_positive: int | None
    unknown_false_negative: int | None
    unknown_precision: float | None
    unknown_recall: float | None
    ece: float | None
    segmentation_mean_iou: float | None
    segmentation_precision: float | None
    segmentation_recall: float | None
    by_manuscript: dict[str, dict[str, float | int]]
    by_hand: dict[str, dict[str, float | int]]
    by_style: dict[str, dict[str, float | int]]
    segmentation_by_manuscript: dict[str, dict[str, float | int]]
    segmentation_by_hand: dict[str, dict[str, float | int]]
    segmentation_by_style: dict[str, dict[str, float | int]]
    validation_errors: tuple[str, ...]
    accuracy_claim_allowed: bool


@dataclass(frozen=True)
class _EditOperation:
    kind: str
    reference_index: int | None
    prediction_index: int | None


def _edit_alignment(
    reference: tuple[Any, ...], hypothesis: tuple[Any, ...]
) -> tuple[_EditOperation, ...]:
    """Return a stable minimum edit path that maximizes retained exact matches."""

    # Scores compare edit cost first and exact matches second. Remaining fields
    # make otherwise equivalent paths stable across Python versions.
    score: list[list[tuple[int, int, int, int, int]]] = [
        [(0, 0, 0, 0, 0) for _ in range(len(hypothesis) + 1)]
        for _ in range(len(reference) + 1)
    ]
    previous: list[list[tuple[int, int, str] | None]] = [
        [None for _ in range(len(hypothesis) + 1)]
        for _ in range(len(reference) + 1)
    ]
    for ref_index in range(1, len(reference) + 1):
        score[ref_index][0] = (ref_index, 0, 0, ref_index, 0)
        previous[ref_index][0] = (ref_index - 1, 0, "delete")
    for prediction_index in range(1, len(hypothesis) + 1):
        score[0][prediction_index] = (prediction_index, 0, 0, 0, prediction_index)
        previous[0][prediction_index] = (0, prediction_index - 1, "insert")

    def add(
        value: tuple[int, int, int, int, int],
        delta: tuple[int, int, int, int, int],
    ) -> tuple[int, int, int, int, int]:
        return tuple(left + right for left, right in zip(value, delta, strict=True))  # type: ignore[return-value]

    for ref_index, reference_label in enumerate(reference, start=1):
        for prediction_index, predicted_label in enumerate(hypothesis, start=1):
            candidates: list[
                tuple[tuple[int, int, int, int, int], int, int, str]
            ] = []
            if reference_label == predicted_label:
                candidates.append(
                    (
                        add(score[ref_index - 1][prediction_index - 1], (0, -1, 0, 0, 0)),
                        ref_index - 1,
                        prediction_index - 1,
                        "match",
                    )
                )
            else:
                candidates.append(
                    (
                        add(score[ref_index - 1][prediction_index - 1], (1, 0, 1, 0, 0)),
                        ref_index - 1,
                        prediction_index - 1,
                        "substitute",
                    )
                )
            candidates.extend(
                (
                    (
                        add(score[ref_index - 1][prediction_index], (1, 0, 0, 1, 0)),
                        ref_index - 1,
                        prediction_index,
                        "delete",
                    ),
                    (
                        add(score[ref_index][prediction_index - 1], (1, 0, 0, 0, 1)),
                        ref_index,
                        prediction_index - 1,
                        "insert",
                    ),
                )
            )
            best = min(candidates, key=lambda item: item[0])
            score[ref_index][prediction_index] = best[0]
            previous[ref_index][prediction_index] = (best[1], best[2], best[3])

    operations: list[_EditOperation] = []
    ref_index = len(reference)
    prediction_index = len(hypothesis)
    while ref_index or prediction_index:
        step = previous[ref_index][prediction_index]
        if step is None:
            raise RuntimeError("edit alignment backtrace is incomplete")
        next_ref, next_prediction, kind = step
        operations.append(
            _EditOperation(
                kind=kind,
                reference_index=ref_index - 1 if kind != "insert" else None,
                prediction_index=prediction_index - 1 if kind != "delete" else None,
            )
        )
        ref_index, prediction_index = next_ref, next_prediction
    operations.reverse()
    return tuple(operations)


def _ece(correct: list[bool], confidence: list[float], bins: int) -> float:
    if not correct:
        return 0.0
    bins = max(1, bins)
    total = len(correct)
    result = 0.0
    for index in range(bins):
        lower = index / bins
        upper = (index + 1) / bins
        members = [
            item
            for item, value in enumerate(confidence)
            if (lower <= value <= upper if index == bins - 1 else lower <= value < upper)
        ]
        if not members:
            continue
        accuracy = sum(correct[item] for item in members) / len(members)
        mean_confidence = sum(confidence[item] for item in members) / len(members)
        result += len(members) / total * abs(accuracy - mean_confidence)
    return result


def _breakdown(rows: list[tuple[str, int, int]]) -> dict[str, dict[str, float | int]]:
    totals: dict[str, list[int]] = {}
    for key, edits, references in rows:
        current = totals.setdefault(key, [0, 0])
        current[0] += edits
        current[1] += references
    return {
        key: {
            "character_edits": values[0],
            "reference_characters": values[1],
            "cer": values[0] / values[1] if values[1] else 0.0,
        }
        for key, values in sorted(totals.items())
    }


def _segmentation_breakdown(
    rows: list[tuple[str, int, int, int, float]],
) -> dict[str, dict[str, float | int]]:
    totals: dict[str, list[float]] = {}
    for key, reference_count, prediction_count, matched_count, mean_iou in rows:
        current = totals.setdefault(key, [0.0, 0.0, 0.0, 0.0, 0.0])
        current[0] += reference_count
        current[1] += prediction_count
        current[2] += matched_count
        current[3] += mean_iou
        current[4] += 1
    return {
        key: {
            "reference_regions": int(values[0]),
            "predicted_regions": int(values[1]),
            "matched_regions": int(values[2]),
            "mean_iou": values[3] / values[4] if values[4] else 0.0,
            "precision": values[2] / values[1] if values[1] else 0.0,
            "recall": values[2] / values[0] if values[0] else 0.0,
        }
        for key, values in sorted(totals.items())
    }


def _valid_sha256(value: str | None) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _duplicates(values: Iterable[str]) -> set[str]:
    seen: set[str] = set()
    repeated: set[str] = set()
    for value in values:
        if value in seen:
            repeated.add(value)
        seen.add(value)
    return repeated


def _lineage_authority_errors(
    authority: Iterable[LineageAuthorityRecord] | None,
    gold_rows: list[GoldSequence],
    segmentation_rows: list[SegmentationObservation],
) -> tuple[list[LineageAuthorityRecord], list[str]]:
    if authority is None:
        return [], ["LINEAGE_AUTHORITY_MISSING"]
    rows = list(authority)
    if not rows:
        return [], ["LINEAGE_AUTHORITY_EMPTY"]

    errors: list[str] = []
    if _duplicates(row.record_id for row in rows):
        errors.append("AUTHORITY_RECORD_ID_DUPLICATE")
    for row in rows:
        if not row.record_id:
            errors.append("AUTHORITY_RECORD_ID_MISSING")
        if row.corpus_role not in {"training", "gold"}:
            errors.append(f"AUTHORITY_ROLE_INVALID:{row.record_id}")
        if not row.manuscript_id:
            errors.append(f"AUTHORITY_MANUSCRIPT_MISSING:{row.record_id}")
        if not row.hand_id:
            errors.append(f"AUTHORITY_HAND_MISSING:{row.record_id}")
        if not row.style:
            errors.append(f"AUTHORITY_STYLE_MISSING:{row.record_id}")
        if not _valid_sha256(row.exact_sha256):
            errors.append(f"AUTHORITY_EXACT_HASH_INVALID:{row.record_id}")
        if not _valid_sha256(row.derivative_sha256):
            errors.append(f"AUTHORITY_DERIVATIVE_HASH_INVALID:{row.record_id}")
        if not row.lineage_root_id:
            errors.append(f"AUTHORITY_LINEAGE_MISSING:{row.record_id}")
        if row.split not in {"train", "validation", "test", "held_out"}:
            errors.append(f"AUTHORITY_SPLIT_INVALID:{row.record_id}")
        elif row.corpus_role == "training" and row.split not in {"train", "validation"}:
            errors.append(f"AUTHORITY_TRAINING_SPLIT_INVALID:{row.record_id}")
        elif row.corpus_role == "gold" and row.split not in {"test", "held_out"}:
            errors.append(f"AUTHORITY_GOLD_SPLIT_INVALID:{row.record_id}")

    training_rows = [row for row in rows if row.corpus_role == "training"]
    held_out_rows = [row for row in rows if row.corpus_role == "gold"]
    if not training_rows:
        errors.append("TRAINING_LINEAGE_AUTHORITY_EMPTY")
    if not held_out_rows:
        errors.append("GOLD_LINEAGE_AUTHORITY_EMPTY")

    def report_crossing(field: str, code: str) -> None:
        grouped: dict[str, list[LineageAuthorityRecord]] = {}
        for row in rows:
            value = getattr(row, field)
            if value:
                grouped.setdefault(value, []).append(row)
        for value, members in sorted(grouped.items()):
            splits = {member.split for member in members}
            if len(splits) > 1:
                errors.append(f"{code}:{value}")

    report_crossing("exact_sha256", "DUPLICATE_HASH_LEAKAGE")
    report_crossing("derivative_sha256", "DERIVATIVE_HASH_LEAKAGE")
    report_crossing("lineage_root_id", "LINEAGE_LEAKAGE")
    report_crossing("manuscript_id", "MANUSCRIPT_LEAKAGE")
    report_crossing("hand_id", "HAND_LEAKAGE")

    authority_by_id = {row.record_id: row for row in rows}
    evaluated_ids = {row.record_id for row in gold_rows} | {
        row.record_id for row in segmentation_rows
    }
    for row in held_out_rows:
        if row.record_id not in evaluated_ids:
            errors.append(f"GOLD_AUTHORITY_OUTSIDE_EVALUATION:{row.record_id}")

    def align(
        record_id: str,
        manuscript_id: str,
        hand_id: str,
        style: str,
        source_sha256: str | None,
        derivative_sha256: str | None,
        lineage_root_id: str | None,
        split: str,
        prefix: str,
    ) -> None:
        authority_row = authority_by_id.get(record_id)
        if authority_row is None:
            errors.append(f"{prefix}_AUTHORITY_RECORD_MISSING:{record_id}")
            return
        if authority_row.corpus_role != "gold":
            errors.append(f"{prefix}_AUTHORITY_ROLE_MISMATCH:{record_id}")
        comparisons = (
            ("MANUSCRIPT", authority_row.manuscript_id, manuscript_id),
            ("HAND", authority_row.hand_id, hand_id),
            ("STYLE", authority_row.style, style),
            ("EXACT_HASH", authority_row.exact_sha256, source_sha256),
            ("DERIVATIVE_HASH", authority_row.derivative_sha256, derivative_sha256),
            ("LINEAGE", authority_row.lineage_root_id, lineage_root_id),
            ("SPLIT", authority_row.split, split),
        )
        for field, expected, observed in comparisons:
            if expected != observed:
                errors.append(f"{prefix}_AUTHORITY_{field}_MISMATCH:{record_id}")

    for row in gold_rows:
        align(
            row.record_id,
            row.manuscript_id,
            row.hand_id,
            row.style,
            row.source_sha256,
            row.derivative_sha256,
            row.lineage_root_id,
            row.split,
            "GOLD",
        )
    for row in segmentation_rows:
        align(
            row.record_id,
            row.manuscript_id,
            row.hand_id,
            row.style,
            row.source_sha256,
            row.derivative_sha256,
            row.lineage_root_id,
            row.split,
            "SEGMENTATION",
        )
    return rows, errors


def evaluate_predictions(
    gold: Iterable[GoldSequence],
    predictions: Iterable[PredictedSequence],
    *,
    segmentation: Iterable[SegmentationObservation] = (),
    lineage_authority: Iterable[LineageAuthorityRecord] | None = None,
    training_source_hashes: Iterable[str] | None = None,
    training_lineage_roots: Iterable[str] | None = None,
    calibration_bins: int = 10,
    unknown_threshold: float = 0.5,
) -> EvaluationMetrics:
    gold_rows = [row for row in gold if row.adjudicated]
    segmentation_rows = [row for row in segmentation if row.adjudicated]
    _, authority_errors = _lineage_authority_errors(
        lineage_authority, gold_rows, segmentation_rows
    )
    if not gold_rows:
        return EvaluationMetrics(
            status="not_measured",
            adjudicated_gold_count=0,
            character_edits=None,
            substitutions=None,
            insertions=None,
            deletions=None,
            reference_characters=None,
            cer=None,
            sequence_error=None,
            confusion={},
            unknown_true_positive=None,
            unknown_false_positive=None,
            unknown_false_negative=None,
            unknown_precision=None,
            unknown_recall=None,
            ece=None,
            segmentation_mean_iou=None,
            segmentation_precision=None,
            segmentation_recall=None,
            by_manuscript={},
            by_hand={},
            by_style={},
            segmentation_by_manuscript={},
            segmentation_by_hand={},
            segmentation_by_style={},
            validation_errors=tuple(
                dict.fromkeys(("ADJUDICATED_GOLD_EMPTY", *authority_errors))
            ),
            accuracy_claim_allowed=False,
        )

    prediction_rows = list(predictions)
    predicted_by_id = {row.record_id: row for row in prediction_rows}
    validation_errors: list[str] = list(authority_errors)
    if _duplicates(row.record_id for row in gold_rows):
        validation_errors.append("GOLD_RECORD_ID_DUPLICATE")
    if _duplicates(row.record_id for row in prediction_rows):
        validation_errors.append("PREDICTION_RECORD_ID_DUPLICATE")
    gold_ids = {row.record_id for row in gold_rows}
    extra_prediction_ids = sorted(set(predicted_by_id) - gold_ids)
    if extra_prediction_ids:
        validation_errors.append("PREDICTION_OUTSIDE_GOLD")
    training_hashes = set(training_source_hashes or ())
    training_roots = set(training_lineage_roots or ())
    for row in gold_rows:
        if row.split not in {"test", "held_out"}:
            validation_errors.append(f"GOLD_SPLIT_NOT_HELD_OUT:{row.record_id}")
        if not _valid_sha256(row.source_sha256):
            validation_errors.append(f"GOLD_SOURCE_HASH_INVALID:{row.record_id}")
        if not _valid_sha256(row.derivative_sha256):
            validation_errors.append(f"GOLD_DERIVATIVE_HASH_INVALID:{row.record_id}")
        if not row.lineage_root_id:
            validation_errors.append(f"GOLD_LINEAGE_MISSING:{row.record_id}")
        if not row.reviewer_id or not row.adjudicator_id:
            validation_errors.append(f"GOLD_ADJUDICATION_IDENTITY_MISSING:{row.record_id}")
        if row.source_sha256 in training_hashes:
            validation_errors.append(f"SOURCE_HASH_LEAKAGE:{row.record_id}")
        if row.lineage_root_id in training_roots:
            validation_errors.append(f"LINEAGE_LEAKAGE:{row.record_id}")
    total_edits = 0
    total_substitutions = 0
    total_insertions = 0
    total_deletions = 0
    total_reference = 0
    sequence_errors = 0
    confusion: dict[str, dict[str, int]] = {}
    unknown_tp = unknown_fp = unknown_fn = 0
    correctness: list[bool] = []
    confidences: list[float] = []
    manuscript_rows: list[tuple[str, int, int]] = []
    hand_rows: list[tuple[str, int, int]] = []
    style_rows: list[tuple[str, int, int]] = []

    for reference in gold_rows:
        prediction = predicted_by_id.get(reference.record_id)
        if prediction is None:
            validation_errors.append(f"PREDICTION_RECORD_MISSING:{reference.record_id}")
            prediction = PredictedSequence(reference.record_id, (), (), ())
        if not reference.labels:
            validation_errors.append(f"GOLD_SEQUENCE_EMPTY:{reference.record_id}")
        if not _valid_sha256(prediction.source_sha256):
            validation_errors.append(f"PREDICTION_SOURCE_HASH_INVALID:{reference.record_id}")
        elif prediction.source_sha256 != reference.source_sha256:
            validation_errors.append(f"SOURCE_HASH_ALIGNMENT_MISMATCH:{reference.record_id}")
        if not _valid_sha256(prediction.derivative_sha256):
            validation_errors.append(
                f"PREDICTION_DERIVATIVE_HASH_INVALID:{reference.record_id}"
            )
        elif prediction.derivative_sha256 != reference.derivative_sha256:
            validation_errors.append(
                f"DERIVATIVE_HASH_ALIGNMENT_MISMATCH:{reference.record_id}"
            )
        if len(prediction.confidences) != len(prediction.labels):
            validation_errors.append(f"CONFIDENCE_LENGTH_MISMATCH:{reference.record_id}")
        if len(prediction.unknown_scores) != len(prediction.labels):
            validation_errors.append(f"UNKNOWN_SCORE_LENGTH_MISMATCH:{reference.record_id}")
        alignment = _edit_alignment(reference.labels, prediction.labels)
        substitutions = sum(item.kind == "substitute" for item in alignment)
        insertions = sum(item.kind == "insert" for item in alignment)
        deletions = sum(item.kind == "delete" for item in alignment)
        edits = substitutions + insertions + deletions
        references = len(reference.labels)
        total_edits += edits
        total_substitutions += substitutions
        total_insertions += insertions
        total_deletions += deletions
        total_reference += references
        sequence_errors += int(edits > 0)
        manuscript_rows.append((reference.manuscript_id, edits, references))
        hand_rows.append((reference.hand_id, edits, references))
        style_rows.append((reference.style, edits, references))

        for operation in alignment:
            gold_label = (
                reference.labels[operation.reference_index]
                if operation.reference_index is not None
                else None
            )
            predicted_label = (
                prediction.labels[operation.prediction_index]
                if operation.prediction_index is not None
                else None
            )
            gold_key = (
                "<INSERTION>"
                if operation.kind == "insert"
                else "<UNKNOWN>"
                if gold_label is None
                else str(gold_label)
            )
            predicted_key = (
                "<DELETION>"
                if operation.kind == "delete"
                else "<UNKNOWN>"
                if predicted_label is None
                else str(predicted_label)
            )
            confusion.setdefault(gold_key, {})[predicted_key] = (
                confusion.setdefault(gold_key, {}).get(predicted_key, 0) + 1
            )

            if operation.reference_index is not None:
                gold_unknown = gold_label is None
                if operation.prediction_index is None:
                    unknown_fn += int(gold_unknown)
                else:
                    prediction_index = operation.prediction_index
                    score = (
                        prediction.unknown_scores[prediction_index]
                        if prediction_index < len(prediction.unknown_scores)
                        else 0.0
                    )
                    predicted_unknown = score >= unknown_threshold or predicted_label is None
                    unknown_tp += int(gold_unknown and predicted_unknown)
                    unknown_fp += int(not gold_unknown and predicted_unknown)
                    unknown_fn += int(gold_unknown and not predicted_unknown)

            if operation.prediction_index is not None:
                prediction_index = operation.prediction_index
                confidence = (
                    prediction.confidences[prediction_index]
                    if prediction_index < len(prediction.confidences)
                    else 0.0
                )
                correctness.append(operation.kind == "match")
                confidences.append(min(1.0, max(0.0, confidence)))

    manuscript_segments: list[tuple[str, int, int, int, float]] = []
    hand_segments: list[tuple[str, int, int, int, float]] = []
    style_segments: list[tuple[str, int, int, int, float]] = []
    if not segmentation_rows:
        validation_errors.append("ADJUDICATED_SEGMENTATION_GOLD_EMPTY")
    if _duplicates(row.record_id for row in segmentation_rows):
        validation_errors.append("SEGMENTATION_RECORD_ID_DUPLICATE")
    for row in segmentation_rows:
        if row.split not in {"test", "held_out"}:
            validation_errors.append(f"SEGMENTATION_SPLIT_NOT_HELD_OUT:{row.record_id}")
        if not _valid_sha256(row.source_sha256):
            validation_errors.append(f"SEGMENTATION_SOURCE_HASH_INVALID:{row.record_id}")
        if not _valid_sha256(row.derivative_sha256):
            validation_errors.append(
                f"SEGMENTATION_DERIVATIVE_HASH_INVALID:{row.record_id}"
            )
        if not row.lineage_root_id:
            validation_errors.append(f"SEGMENTATION_LINEAGE_MISSING:{row.record_id}")
        if row.source_sha256 in training_hashes:
            validation_errors.append(f"SEGMENTATION_SOURCE_HASH_LEAKAGE:{row.record_id}")
        if row.lineage_root_id in training_roots:
            validation_errors.append(f"SEGMENTATION_LINEAGE_LEAKAGE:{row.record_id}")
        if (
            row.reference_regions < 1
            or row.predicted_regions < 0
            or row.matched_regions < 0
            or row.matched_regions > row.reference_regions
            or row.matched_regions > row.predicted_regions
            or not 0.0 <= row.mean_iou <= 1.0
        ):
            validation_errors.append(f"SEGMENTATION_COUNTS_INVALID:{row.record_id}")
            continue
        values = (
            row.reference_regions,
            row.predicted_regions,
            row.matched_regions,
            row.mean_iou,
        )
        manuscript_segments.append((row.manuscript_id, *values))
        hand_segments.append((row.hand_id, *values))
        style_segments.append((row.style, *values))

    segment_reference = sum(row[1] for row in manuscript_segments)
    segment_prediction = sum(row[2] for row in manuscript_segments)
    segment_matched = sum(row[3] for row in manuscript_segments)
    segment_mean_iou = (
        sum(row[4] for row in manuscript_segments) / len(manuscript_segments)
        if manuscript_segments
        else None
    )
    unknown_precision = (
        unknown_tp / (unknown_tp + unknown_fp) if unknown_tp + unknown_fp else 0.0
    )
    unknown_recall = (
        unknown_tp / (unknown_tp + unknown_fn) if unknown_tp + unknown_fn else 0.0
    )
    unique_errors = tuple(dict.fromkeys(validation_errors))

    return EvaluationMetrics(
        status="measured",
        adjudicated_gold_count=len(gold_rows),
        character_edits=total_edits,
        substitutions=total_substitutions,
        insertions=total_insertions,
        deletions=total_deletions,
        reference_characters=total_reference,
        cer=total_edits / total_reference if total_reference else 0.0,
        sequence_error=sequence_errors / len(gold_rows),
        confusion=confusion,
        unknown_true_positive=unknown_tp,
        unknown_false_positive=unknown_fp,
        unknown_false_negative=unknown_fn,
        unknown_precision=unknown_precision,
        unknown_recall=unknown_recall,
        ece=_ece(correctness, confidences, calibration_bins),
        segmentation_mean_iou=segment_mean_iou,
        segmentation_precision=(
            segment_matched / segment_prediction if segment_prediction else 0.0
        )
        if manuscript_segments
        else None,
        segmentation_recall=(segment_matched / segment_reference if segment_reference else 0.0)
        if manuscript_segments
        else None,
        by_manuscript=_breakdown(manuscript_rows),
        by_hand=_breakdown(hand_rows),
        by_style=_breakdown(style_rows),
        segmentation_by_manuscript=_segmentation_breakdown(manuscript_segments),
        segmentation_by_hand=_segmentation_breakdown(hand_segments),
        segmentation_by_style=_segmentation_breakdown(style_segments),
        validation_errors=unique_errors,
        accuracy_claim_allowed=not unique_errors and total_reference > 0,
    )
