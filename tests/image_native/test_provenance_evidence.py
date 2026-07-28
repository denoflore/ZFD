"""Provenance records keep observation, bearing, and prohibited inference separate."""

from __future__ import annotations

from pathlib import Path

from zfd_image_native.io import read_json


ROOT = Path(__file__).resolve().parents[2]


def test_provenance_evidence_is_explicitly_unresolved_and_source_bound() -> None:
    payload = read_json(ROOT / "data" / "image_native" / "provenance_evidence.json")

    assert payload["programme_status"] == "hypothesis_unresolved"
    records = payload["records"]
    assert records
    assert len({row["evidence_id"] for row in records}) == len(records)
    for row in records:
        assert row["source_id"]
        assert row["passage_locator"]
        assert row["stable_locator"].startswith("https://")
        assert row["observed_claim"]
        assert row["script_evidence"]
        assert row["bearing_on_zfd"]
        assert row["prohibited_inference"]
        assert row["local_artifact_status"]
