"""The dated Frašćić Psalter remains a quarantined longhand control."""

from __future__ import annotations

import json
from pathlib import Path

from zfd_image_native.comparative import validate_comparative_assets


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "image_native"
SOURCE_ID = "onb-frascic-psalter-cod-slav-77-1463"


def _json(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def _jsonl(name: str) -> list[dict]:
    return [
        json.loads(line)
        for line in (DATA / name).read_text(encoding="utf-8").splitlines()
        if line
    ]


def test_frascic_source_authority_preserves_catalogue_scope_and_hashes() -> None:
    sources = {row["source_id"]: row for row in _json("source_register.json")["sources"]}
    source = sources[SOURCE_ID]

    assert source["stable_locator"] == "https://data.onb.ac.at/rec/AC14377621"
    assert source["dating_authority_locator"] == (
        "https://api.onb.ac.at/iiif/presentation/v3/manifest/10004B90"
    )
    assert source["rights_locator"] == "https://www.onb.ac.at/en/use/"
    assert "Austrian National Library" in source["rights_statement"]
    assert source["writing_date_start"] == source["writing_date_end"] == 1463
    assert source["language"] == "Croatian Church Slavonic"
    assert source["script"] == "Glagolitic, semi-uncial"
    assert source["hand_style"] == (
        "catalogued_semi_uncial_longhand_angular_unresolved_not_catalogued_as_cursive_"
        "shorthand_unattested"
    )
    assert source["region"] == "Lindar, Istria"
    assert source["training_use"] == "quarantined"
    assert source["manifest_sha256"] == (
        "549340357111904908c4a27fa8288d1c444c76f984c9a4ce46c393c81b7c02f6"
    )
    assert source["asset_mapping_sha256"] == (
        "f33b9a22af00ee0d47a2bd6b546c78e691c3c8a282da0b3277b0f2a41b8e18bb"
    )
    assert source["page_mapping_sha256"] == source["asset_mapping_sha256"]
    assert source["lineage_sha256"] == (
        "d0cf9a35feb7f538e4a96ec74287e319ec4a78bd7aced6f192d23cd8fa407eeb"
    )


def test_frascic_acquisition_config_blocks_unadjudicated_pixels_from_training() -> None:
    sources = {row["source_id"]: row for row in _json("comparative_sources.json")["sources"]}
    source = sources[SOURCE_ID]

    assert source["registered_source_id"] == SOURCE_ID
    assert source["local_subpath"] == "Frascic_Psalter_1463_ONB_Cod_slav_77"
    assert source["expected_asset_count"] == 278
    assert source["manifest_uri"] == (
        "https://api.onb.ac.at/iiif/presentation/v3/manifest/10004B90"
    )
    assert source["mapping"] == {
        "direct_relpath": "meta/canvas_mapping.json",
        "local_name_field": "local_name",
    }
    assert source["angular_status"] == "unresolved_not_catalogued"
    assert source["cursive_status"] == "not_catalogued_as_cursive"
    assert source["shorthand_status"] == "unattested_in_catalogue"
    assert source["longhand_status"] == "catalogued_semi_uncial_control"
    assert source["pixel_labels_present"] is False
    assert source["training_disposition"] == "quarantine_pending_hand_boundary_and_lineage"


def test_frascic_assets_join_exact_canvases_and_leave_ledger_training_closed() -> None:
    assets = _jsonl("comparative_assets.jsonl")
    frascic = [row for row in assets if row["source_id"] == SOURCE_ID]
    summary = _json("comparative_asset_summary.json")

    assert len(frascic) == 278
    assert len({row["sha256"] for row in frascic}) == 278
    assert len({row["canvas_id"] for row in frascic}) == 278
    assert all(row["canvas_id"] is not None for row in frascic)
    assert all(row["duplicate_group"] is None for row in frascic)
    assert all(row["hand_boundary_sha256"] is None for row in frascic)
    assert all(row["line_annotation_sha256"] is None for row in frascic)
    assert all(row["split_lineage_sha256"] is None for row in frascic)
    assert all(row["training_disposition"] != "train" for row in frascic)
    assert summary["source_count"] == 7
    assert summary["asset_count"] == 2948
    assert summary["unique_content_count"] == 2105
    assert summary["mapped_canvas_count"] == 1991
    assert summary["duplicate_asset_count"] == 1616
    assert summary["duplicate_groups"] == 773
    assert summary["cross_source_duplicate_groups"] == 703
    assert summary["training_ready_asset_count"] == 0
    assert validate_comparative_assets(DATA, DATA / "source_register.json").ok is True


def test_comparative_authority_contains_no_machine_absolute_path() -> None:
    for name in (
        "source_register.json",
        "comparative_sources.json",
        "comparative_assets.jsonl",
        "comparative_duplicate_groups.jsonl",
        "comparative_asset_summary.json",
    ):
        text = (DATA / name).read_text(encoding="utf-8")
        assert "F:\\" not in text
        assert "F:/" not in text
