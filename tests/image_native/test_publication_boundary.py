"""Legacy completion and provenance claims remain visibly quarantined."""

from __future__ import annotations

from pathlib import Path

import pytest

from zfd_image_native.publication import LEGACY_MARKERS, scan_publication_boundary


ROOT = Path(__file__).resolve().parents[2]


def test_scanner_rejects_unbannered_claim_and_accepts_complete_banner(tmp_path: Path) -> None:
    report = tmp_path / "report.md"
    report.write_text("# Old report\n\nComplete translation across all 201 folios.\n", encoding="utf-8")
    issues = scan_publication_boundary(tmp_path)
    assert len(issues) == 1
    assert issues[0].code == "LEGACY_CLAIM_BANNER_MISSING"

    report.write_text("\n".join((*LEGACY_MARKERS, "Complete translation.")), encoding="utf-8")
    assert scan_publication_boundary(tmp_path) == ()


def test_repository_claim_bearing_legacy_documents_are_bannered() -> None:
    assert scan_publication_boundary(ROOT) == ()


@pytest.mark.parametrize(
    "claim",
    (
        "The manuscript is fully translated.",
        "The translation is complete.",
        "The provenance is confirmed.",
        "The language has been confirmed.",
        "The script was confirmed.",
        "This is the confirmed genre.",
        "Language confirmed as Croatian.",
        "The evidence confirms the script.",
        "All pages have been translated.",
        "The corpus is translated.",
    ),
)
def test_scanner_rejects_semantic_completion_and_provenance_claims(
    tmp_path: Path, claim: str
) -> None:
    (tmp_path / "claim.md").write_text(claim, encoding="utf-8")

    issues = scan_publication_boundary(tmp_path)

    assert len(issues) == 1
    assert issues[0].code == "LEGACY_CLAIM_BANNER_MISSING"


def test_scanner_accepts_explicitly_blocked_current_statements(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text(
        "Complete translation remains blocked.\n"
        "No language is confirmed.\n"
        "The specific provenance is unproven.\n",
        encoding="utf-8",
    )

    assert scan_publication_boundary(tmp_path) == ()


def test_complete_legacy_banner_quarantines_broader_claims(tmp_path: Path) -> None:
    (tmp_path / "legacy.md").write_text(
        "\n".join((*LEGACY_MARKERS, "Fully translated. Provenance is confirmed.")),
        encoding="utf-8",
    )

    assert scan_publication_boundary(tmp_path) == ()
