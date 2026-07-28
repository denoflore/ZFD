"""Leakage checks for manuscripts, hands, duplicates, and derivatives."""

from __future__ import annotations

from collections import defaultdict
from typing import Callable, Iterable

from .models import SplitAsset, ValidationIssue, ValidationReport


def _crossing(
    rows: list[SplitAsset],
    key: Callable[[SplitAsset], str],
    code: str,
    message: str,
) -> list[ValidationIssue]:
    groups: dict[str, list[SplitAsset]] = defaultdict(list)
    for row in rows:
        value = key(row)
        if value:
            groups[value].append(row)
    issues: list[ValidationIssue] = []
    for value, members in groups.items():
        splits = {member.split for member in members}
        if len(splits) > 1:
            issues.append(
                ValidationIssue(
                    code,
                    message,
                    value,
                    {"assets": [member.asset_id for member in members], "splits": sorted(splits)},
                )
            )
    return issues


def validate_split(records: Iterable[SplitAsset]) -> ValidationReport:
    rows = list(records)
    issues: list[ValidationIssue] = []
    issues.extend(_crossing(rows, lambda row: row.sha256, "DUPLICATE_LEAKAGE", "Byte duplicate crosses splits"))
    issues.extend(_crossing(rows, lambda row: row.perceptual_hash, "VISUAL_DUPLICATE_LEAKAGE", "Visual duplicate crosses splits"))
    issues.extend(_crossing(rows, lambda row: row.lineage_root_id, "LINEAGE_LEAKAGE", "Derivative lineage crosses splits"))
    issues.extend(_crossing(rows, lambda row: row.manuscript_id, "MANUSCRIPT_LEAKAGE", "Manuscript crosses splits"))
    issues.extend(_crossing(rows, lambda row: row.hand_id, "HAND_LEAKAGE", "Hand crosses splits"))
    return ValidationReport(tuple(issues))
