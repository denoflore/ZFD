"""Repository wide publication boundary for inherited hypothesis artefacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


LEGACY_MARKERS = (
    "evidence_status: legacy_eva_derived_hypothesis",
    "primary_input: inherited_transcription",
    "image_native_confirmed: false",
    "translation_confirmed: false",
    "provenance_confirmed: false",
)
CLAIM_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bcomplete translation\b",
        r"\btranslation verified\b",
        r"\ball 201 folios\b",
        r"\bprovenance lock\b",
        r"\bragusan provenance\b",
        r"\bdefinitive translation\b",
        r"\b(?:fully|completely) translated\b",
        r"\btranslation (?:complete|completed)\b",
        r"\btranslation (?:is|was|has been) (?:fully )?(?:complete|confirmed|verified)\b",
        r"\b(?:the )?provenance (?:is|was|has been) (?:confirmed|established|proven|locked)\b",
        r"\b(?:the )?(?:language|script|genre) (?:is|was|has been) (?:confirmed|established|identified)\b",
        r"\b(?:language|script|genre|provenance) (?:confirmed|established|proven)\b",
        r"\b(?:confirmed|established|proven) (?:language|script|genre|provenance)\b",
        r"\b(?:we|the (?:evidence|results|analysis)) confirm(?:s|ed)? (?:the )?(?:language|script|genre|provenance)\b",
        r"\b(?:all pages|the entire manuscript|the whole manuscript) (?:have|has) been translated\b",
        r"\b(?:the (?:manuscript|corpus)|all (?:folios|pages)) (?:is|are|was|were|has been|have been) (?:fully )?translated\b",
    )
)
NEGATING_CONTEXT = re.compile(
    r"\b(?:no|not|never|cannot|can't|unproven|unconfirmed|unresolved|blocked|false|"
    r"without|pending|quarantined|hypothesis|rejected|disproven)\b",
    re.IGNORECASE,
)
SKIP_PARTS = frozenset({".git", ".pytest_cache", "build", "planning", "data"})


@dataclass(frozen=True)
class PublicationIssue:
    path: str
    code: str
    matched_claims: tuple[str, ...]
    missing_markers: tuple[str, ...]


def _statement_containing(text: str, start: int, end: int) -> str:
    left_candidates = [text.rfind(boundary, 0, start) for boundary in ("\n", ".", "!", "?")]
    left = max(left_candidates) + 1
    right_candidates = [
        position
        for boundary in ("\n", ".", "!", "?")
        if (position := text.find(boundary, end)) >= 0
    ]
    right = min(right_candidates) if right_candidates else len(text)
    return text[left:right]


def _affirmative_claim_patterns(text: str) -> tuple[str, ...]:
    matched: list[str] = []
    for pattern in CLAIM_PATTERNS:
        for claim in pattern.finditer(text):
            statement = _statement_containing(text, claim.start(), claim.end())
            if NEGATING_CONTEXT.search(statement):
                continue
            matched.append(pattern.pattern)
            break
    return tuple(matched)


def scan_publication_boundary(repository_root: str | Path) -> tuple[PublicationIssue, ...]:
    root = Path(repository_root).resolve()
    issues: list[PublicationIssue] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".md", ".json"}:
            continue
        relative = path.relative_to(root).as_posix()
        if any(part in SKIP_PARTS for part in path.relative_to(root).parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            issues.append(PublicationIssue(relative, "PUBLICATION_FILE_UNREADABLE", (), ()))
            continue
        matched = _affirmative_claim_patterns(text)
        if not matched:
            continue
        missing = tuple(marker for marker in LEGACY_MARKERS if marker not in text)
        if missing:
            issues.append(
                PublicationIssue(
                    path=relative,
                    code="LEGACY_CLAIM_BANNER_MISSING",
                    matched_claims=matched,
                    missing_markers=missing,
                )
            )
    return tuple(issues)
