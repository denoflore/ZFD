"""Historically useful controls remain rights-aware and outside training."""

from __future__ import annotations

import json
from pathlib import Path

from zfd_image_native.models import SourceRecord
from zfd_image_native.sources import validate_sources


REGISTER = Path("data/image_native/source_register.json")


def _sources() -> dict[str, dict]:
    payload = json.loads(REGISTER.read_text(encoding="utf-8"))
    return {row["source_id"]: row for row in payload["sources"]}


def test_complete_register_conforms_to_typed_source_contract() -> None:
    payload = json.loads(REGISTER.read_text(encoding="utf-8"))
    records = [SourceRecord(**row) for row in payload["sources"]]

    assert payload["schema_version"] == "2.0.0"
    assert validate_sources(records).ok is True


def test_medical_and_latin_controls_are_registered_without_training_leakage() -> None:
    sources = _sources()
    required = {
        "hazu-iv-d-56",
        "hazu-iv-d-55",
        "durrigl-fatovic-ferencic-2024",
        "loc-antidotarium-nicolai-1471",
        "hazu-iv-a-48",
        "nsk-mavrov-r7822",
        "nlr-bercic-6-1460",
        "nlr-bercic-7-1472",
        "nsk-hrvoje-missal-19404",
        "bodleian-canon-liturg-414",
    }

    assert required <= sources.keys()
    assert sources["hazu-iv-d-56"]["date_kind"] == "writing"
    assert sources["hazu-iv-d-56"]["writing_date_end"] == 1400
    assert sources["hazu-iv-d-56"]["hand_style"] == (
        "old_or_transitional_semi_uncial"
    )
    assert sources["hazu-iv-d-56"]["language"] == (
        "Croatian Chakavian with limited Church Slavonic elements"
    )
    assert sources["hazu-iv-d-55"]["writing_date_start"] == 1401
    assert sources["hazu-iv-d-55"]["writing_date_end"] == 1500
    assert sources["hazu-iv-d-55"]["hand_style"] == (
        "formal_and_cursive_glagolitic_with_latin_entry"
    )
    assert sources["hazu-iv-d-55"]["script"] == (
        "Croatian Glagolitic with Latin script"
    )
    assert sources["hazu-iv-d-56"]["manifest_sha256"] is None
    assert sources["hazu-iv-d-55"]["manifest_sha256"] is None
    assert sources["hazu-iv-d-56"]["rights_status"] == (
        "archive_access_and_reproduction_unresolved"
    )
    assert sources["hazu-iv-d-55"]["rights_status"] == (
        "archive_access_and_reproduction_unresolved"
    )
    assert sources["durrigl-fatovic-ferencic-2024"]["rights_status"] == (
        "cc_by_nc_4_0"
    )
    assert sources["loc-antidotarium-nicolai-1471"]["control_group"] == (
        "latin_pharmaceutical_print_control"
    )
    assert sources["hazu-iv-a-48"]["training_use"] == "reference_only"
    assert sources["hazu-iv-a-48"]["manifest_sha256"] is None
    assert sources["hazu-iv-a-48"]["writing_date_start"] == 1475
    assert sources["hazu-iv-a-48"]["writing_date_end"] == 1500
    assert sources["nsk-mavrov-r7822"]["training_use"] == "quarantined"
    assert sources["nsk-mavrov-r7822"]["writing_date_start"] == 1460
    assert sources["nsk-mavrov-r7822"]["writing_date_end"] == 1471
    assert sources["nsk-mavrov-r7822"]["hand_style"] == (
        "formal_ustavna_1460_and_calendar_hand_1471_boundaries_unmapped"
    )
    assert sources["nsk-mavrov-r7822"]["evidentiary_role"] == (
        "dated_formal_and_calendar_script_control_unmapped_layers"
    )
    assert sources["nsk-mavrov-r7822"]["asset_mapping_sha256"] == (
        "f43b604ad62f133e41c534ca29579e7e17c1e7176fb2a1315aa2cb68df41bca5"
    )
    assert sources["nsk-mavrov-r7822"]["page_mapping_sha256"] == (
        "f43b604ad62f133e41c534ca29579e7e17c1e7176fb2a1315aa2cb68df41bca5"
    )
    assert sources["nsk-mavrov-r7822"]["lineage_sha256"] == (
        "54ebce142ec0b1ae23875faa14f4864d509a35ecf57e9ad5db08522de88b6b94"
    )
    assert all(sources[source_id]["training_use"] != "train" for source_id in required)


def test_new_period_controls_preserve_exact_dates_rights_and_hand_uncertainty() -> None:
    sources = _sources()
    will_1460 = sources["nlr-bercic-6-1460"]
    will_1472 = sources["nlr-bercic-7-1472"]
    hrvoje = sources["nsk-hrvoje-missal-19404"]
    oxford = sources["bodleian-canon-liturg-414"]

    assert will_1460["writing_date_start"] == 1460
    assert will_1472["writing_date_start"] == 1472
    assert will_1460["hand_style"] == "glagolitic_cursive_catalogued"
    assert will_1472["hand_style"] == "glagolitic_cursive_catalogued"
    assert will_1460["manifest_sha256"] is None
    assert will_1472["manifest_sha256"] is None
    assert will_1460["training_use"] == "reference_only"
    assert will_1472["training_use"] == "reference_only"
    assert hrvoje["writing_date_start"] == 1403
    assert hrvoje["writing_date_end"] == 1404
    assert hrvoje["hand_style"] == "formal_ustavna_by_scribe_butko"
    assert hrvoje["rights_status"] == "contract_restricted"
    assert oxford["writing_date_start"] == 1401
    assert oxford["writing_date_end"] == 1500
    assert oxford["hand_style"] == "hand_and_palaeographic_subtype_unresolved"
    assert oxford["training_use"] == "reference_only"


def test_registered_historical_labels_preserve_hand_and_language_boundaries() -> None:
    sources = _sources()
    gams = sources["gams-zrcalo-1445"]
    petrisov = sources["nsk-petrisov-r4001"]

    assert gams["shelfmark"] == "Borg. L. VII. 9; IIIF identifier Borg.ill.9"
    assert gams["region"].startswith("origin unresolved")
    assert gams["language"] == (
        "mostly Old Croatian with Croatian Church Slavonic and Old Czech elements"
    )
    assert "Vatican Slavic 73" not in json.dumps(gams)
    assert petrisov["hand_style"] == "three_unattributed_cursive_hands"
    assert petrisov["language"] == (
        "Croatian with Chakavian, Kajkavian, and Old Slavonic elements"
    )
    assert sources["nsk-istarski-r3677"]["hand_style"] == "office_cursive"
    assert sources["nsk-vinodolski-r4080"]["hand_style"] == "hand_unresolved"


def test_iv_a_48_does_not_assert_an_unsupported_hand_count() -> None:
    source = _sources()["hazu-iv-a-48"]
    status = Path("docs/PROVENANCE_STATUS.md").read_text(encoding="utf-8")

    assert source["hand_style"] == "book_cursive"
    assert "two reported hands" not in status.casefold()


def test_target_radiocarbon_range_is_explicitly_material_only() -> None:
    target = _sources()["yale-ms-408"]

    assert target["date_kind"] == "material"
    assert target["material_date_start"] == 1404
    assert target["material_date_end"] == 1438
    assert target["writing_date_start"] is None
    assert target["writing_date_end"] is None
