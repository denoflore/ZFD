"""Real corpus parity materialisation must preserve every unresolved join."""

from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
from pathlib import Path
import subprocess
import sys

import pytest

from zfd_image_native.boundary import scan_primary_lane
from zfd_image_native.io import canonical_json
from zfd_parity_corpus.cli import _resolve_output
from zfd_parity_corpus.core import (
    CorpusParityBundle,
    PARITY_FILES,
    build_corpus_parity,
    read_corpus_parity,
    validate_corpus_parity_bundle,
    write_corpus_parity_new,
)


ROOT = Path(__file__).resolve().parents[2]
V2B = ROOT / "data" / "image_native" / "receipts-v2b"


def _seal(**fields: object) -> dict[str, object]:
    return {
        **fields,
        "receipt_sha256": sha256(canonical_json(fields).encode("utf-8")).hexdigest(),
    }


def _reseal(record: dict[str, object]) -> dict[str, object]:
    payload = {key: value for key, value in record.items() if key != "receipt_sha256"}
    return _seal(**payload)


def _complete_proposal(bundle) -> tuple[dict[str, object], dict[str, object]]:
    unresolved = bundle.records[0]
    page = unresolved["layers"]["page"]
    region = unresolved["layers"]["region"]
    shared = {"page_id": page["page_id"], "image_sha256": page["image_sha256"]}
    region_id = region["region_id"]
    geometry_hash = region["geometry_sha256"]
    ocr_id = "ocr:test-complete-region"
    term_source = _seal(
        schema="zfd.parity_source_authority.v1",
        source_id="gams-zrcalo-1445",
        source_type="primary_manuscript_witness",
        asset_sha256="b" * 64,
        stable_locator="https://gams.uni-graz.at/o:speculum.01",
    )
    reviewer = _seal(
        schema="zfd.parity_reviewer_authority.v1",
        reviewer_id="reviewer-1",
        role="reviewer",
        status="active",
        qualified_layers=["diplomatic", "normalised", "terminology", "translation"],
    )
    adjudicator = _seal(
        schema="zfd.parity_reviewer_authority.v1",
        reviewer_id="adjudicator-1",
        role="adjudicator",
        status="active",
        qualified_layers=["diplomatic", "normalised", "terminology", "translation"],
    )
    rejection = _seal(
        schema="zfd.parity_unknown_rejection.v1",
        **shared,
        region_id=region_id,
        ocr_id=ocr_id,
        candidate_count=1,
        recognized_count=1,
        unknown_count=0,
        rejected_count=0,
        candidate_ids=["grapheme-1"],
        recognized_grapheme_ids=["grapheme-1"],
        unknown_grapheme_ids=[],
        rejected_candidate_ids=[],
        threshold=0.8,
        method="open_set_threshold",
    )
    ocr = _seal(
        schema="zfd.parity_ocr.v1",
        **shared,
        region_id=region_id,
        ocr_id=ocr_id,
        geometry_sha256=geometry_hash,
        region_receipt_sha256=region["receipt_sha256"],
        status="frozen",
        input_kind="manuscript_pixels",
        unknown_rejection=True,
        unknown_rejection_receipt_id="unknown-rejection-1",
        line_ids=["line-1"],
        grapheme_ids=["grapheme-1"],
        recognized_grapheme_ids=["grapheme-1"],
        unknown_grapheme_ids=[],
    )
    diplomatic = _seal(
        schema="zfd.parity_diplomatic.v1",
        **shared,
        region_id=region_id,
        ocr_id=ocr_id,
        geometry_sha256=geometry_hash,
        ocr_receipt_sha256=ocr["receipt_sha256"],
        text="observed glyph sequence",
        line_ids=["line-1"],
        grapheme_ids=["grapheme-1"],
        grapheme_alignment=[
            {
                "grapheme_id": "grapheme-1",
                "label": "observed-glyph-1",
                "polygon_sha256": "c" * 64,
            }
        ],
        alternatives=[],
        state="resolved",
        review_state="adjudicated",
    )
    normalised = _seal(
        schema="zfd.parity_normalised.v1",
        **shared,
        region_id=region_id,
        ocr_id=ocr_id,
        geometry_sha256=geometry_hash,
        diplomatic_receipt_sha256=diplomatic["receipt_sha256"],
        expanded_text="expanded reading",
        normalised_historical_text="historical form",
        line_ids=["line-1"],
        review_state="adjudicated",
    )
    terminology = _seal(
        schema="zfd.parity_terminology.v1",
        **shared,
        region_id=region_id,
        ocr_id=ocr_id,
        geometry_sha256=geometry_hash,
        normalised_receipt_sha256=normalised["receipt_sha256"],
        analysis_id="analysis-1",
        status="resolved",
        observed_form="historical form",
        source_id="gams-zrcalo-1445",
        source_receipt_sha256=term_source["receipt_sha256"],
        source_date_start=1445,
        source_date_end=1445,
        passage_locator="folio 1r",
        stable_locator="https://gams.uni-graz.at/o:speculum.01",
        passage_asset_sha256="b" * 64,
        passage_image_sha256="d" * 64,
        diplomatic_passage="historical form",
        witness_language="Croatian Church Slavonic",
        witness_script="Croatian angular Glagolitic",
        alternatives=[],
        review_state="approved",
    )
    translation = _seal(
        schema="zfd.parity_translation.v1",
        **shared,
        region_id=region_id,
        ocr_id=ocr_id,
        geometry_sha256=geometry_hash,
        analysis_id="analysis-1",
        terminology_receipt_sha256=terminology["receipt_sha256"],
        modern_croatian="suvremeni hrvatski",
        literal_english="literal English",
        fluent_english="Fluent English.",
        alternatives=[],
        confidence=0.8,
        confidence_basis="evidentiary_review",
        reviewer_id="reviewer-1",
        adjudicator_id="adjudicator-1",
        adjudication_id="adjudication-1",
        status="resolved",
        review_state="approved",
    )
    layers = {
        "page": page,
        "region": region,
        "ocr": ocr,
        "diplomatic": diplomatic,
        "normalised": normalised,
        "terminology": terminology,
        "translation": translation,
    }
    adjudication = _seal(
        schema="zfd.parity_adjudication.v1",
        adjudication_id="adjudication-1",
        reviewer_id="reviewer-1",
        adjudicator_id="adjudicator-1",
        status="approved",
        layer_receipts={name: layer["receipt_sha256"] for name, layer in layers.items()},
    )
    overlay_fields = {
        "schema": "zfd.parity_evidence_authority.v1",
        "layers": {
            name: {layer["receipt_sha256"]: layer}
            for name, layer in layers.items()
            if name not in {"page", "region"}
        },
        "sources": {term_source["receipt_sha256"]: term_source},
        "reviewers": {"reviewer-1": reviewer, "adjudicator-1": adjudicator},
        "unknown_rejection": {"unknown-rejection-1": rejection},
        "adjudications": {"adjudication-1": adjudication},
        "nontext_reviews": {},
    }
    overlay = _seal(**overlay_fields)
    proposal = {
        "schema": "zfd.translation_parity_record.v1",
        "page_id": page["page_id"],
        "region_id": region_id,
        "layers": layers,
        "review_state": "approved",
    }
    return proposal, overlay


@pytest.fixture(scope="module")
def v2b_bundle() -> CorpusParityBundle:
    return build_corpus_parity(V2B)


def test_v2b_materialiser_accounts_for_exact_210_pages_and_670_regions_as_unresolved(
    v2b_bundle: CorpusParityBundle,
) -> None:
    bundle = v2b_bundle

    assert len(bundle.page_authority) == 210
    assert len(bundle.region_authority) == 670
    assert len(bundle.records) == 670
    assert len(bundle.page_dispositions) == 210
    assert bundle.summary["confirmed_translated_pages"] == 0
    assert bundle.summary["confirmed_translated_regions"] == 0
    assert bundle.summary["unresolved_pages"] == 210
    assert bundle.summary["unresolved_regions"] == 670
    assert bundle.summary["stage_a_archival_integrity_ok"] is True
    assert bundle.summary["canonical_page_scope_ok"] is True
    assert bundle.summary["promotion_authority_pinned"] is False
    assert bundle.summary["region_authority_pinned"] is False
    assert bundle.summary["completion_claim_allowed"] is False
    assert all(row["confirmed_translated"] is False for row in bundle.records)
    assert all(row["disposition"] == "unresolved" for row in bundle.page_dispositions)
    assert validate_corpus_parity_bundle(bundle, V2B) == ()


def test_each_page_layer_resolves_its_exact_pixel_source_receipt(
    v2b_bundle: CorpusParityBundle,
) -> None:
    bundle = v2b_bundle

    assert len(bundle.evidence_authority["sources"]) == 210
    for record in bundle.records:
        assert not {
            "PAGE_SOURCE_AUTHORITY_MISSING",
            "PAGE_SOURCE_AUTHORITY_INVALID",
            "PAGE_SOURCE_AUTHORITY_MISMATCH",
        } & set(record["reason_codes"])


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "unexpected"])
def test_validator_rejects_missing_duplicate_or_unexpected_region_record(
    mutation: str, v2b_bundle: CorpusParityBundle
) -> None:
    bundle = v2b_bundle
    regions = list(bundle.region_authority)
    if mutation == "missing":
        regions.pop()
    elif mutation == "duplicate":
        regions.append(regions[0])
    else:
        forged = dict(regions[0])
        forged["region_id"] = "sha256:" + "f" * 64
        regions.append(forged)

    errors = validate_corpus_parity_bundle(
        replace(bundle, region_authority=tuple(regions)),
        V2B,
    )

    assert any(
        code in errors
        for code in {
            "REGION_AUTHORITY_COVERAGE_MISMATCH",
            "REGION_AUTHORITY_ID_DUPLICATE",
            "REGION_AUTHORITY_RECEIPT_INVALID",
        }
    )


def test_filename_match_cannot_override_page_image_region_or_geometry_join(
    v2b_bundle: CorpusParityBundle,
) -> None:
    bundle = v2b_bundle
    first = bundle.records[0]
    sibling = next(
        row for row in bundle.records if row["page_id"] != first["page_id"]
    )
    forged = dict(first)
    forged["layers"] = dict(first["layers"])
    forged["layers"]["page"] = sibling["layers"]["page"]
    records = (forged, *bundle.records[1:])

    errors = validate_corpus_parity_bundle(
        replace(bundle, records=records),
        V2B,
    )

    assert {
        "PARITY_RECORD_RECEIPT_INVALID",
        "PARITY_RECORD_PAGE_LAYER_MISMATCH",
    } & set(errors)


def test_proposal_intake_rejects_existing_region_bound_to_a_different_page(
    v2b_bundle: CorpusParityBundle,
) -> None:
    first = v2b_bundle.records[0]
    sibling = next(
        row for row in v2b_bundle.records if row["page_id"] != first["page_id"]
    )
    proposal = {
        "schema": "zfd.translation_parity_record.v1",
        "page_id": first["page_id"],
        "region_id": sibling["region_id"],
        "layers": first["layers"],
        "review_state": "approved",
    }

    with pytest.raises(ValueError, match="LAYER_RECORD_PAGE_REGION_MISMATCH"):
        build_corpus_parity(V2B, proposed_records=(proposal,))


def test_unadjudicated_visual_task_cannot_promote_a_diplomatic_layer() -> None:
    visual_task = {
        "schema": "zfd.visual_gold_task.v1",
        "page_id": "yale-ms-408:iiif:1006076",
        "region_id": "sha256:" + "a" * 64,
        "review_state": "unreviewed",
    }

    with pytest.raises(ValueError, match="LAYER_RECORD_SCHEMA_INVALID"):
        build_corpus_parity(V2B, proposed_records=(visual_task,))


def test_self_minted_complete_region_chain_is_blocked_until_authorities_are_pinned(
    v2b_bundle: CorpusParityBundle,
) -> None:
    proposal, overlay = _complete_proposal(v2b_bundle)

    with pytest.raises(ValueError, match="PARITY_PROMOTION_AUTHORITY_UNPINNED"):
        build_corpus_parity(
            V2B,
            proposed_records=(proposal,),
            evidence_overlay=overlay,
        )


def test_build_rejects_inherited_or_undeclared_layer_keys(
    v2b_bundle: CorpusParityBundle,
) -> None:
    proposal, overlay = _complete_proposal(v2b_bundle)
    proposal["layers"]["eva_transcription"] = {
        "source": "inherited",
        "text": "forbidden lane",
    }

    with pytest.raises(ValueError, match="LAYER_RECORD_KEYS_INVALID"):
        build_corpus_parity(
            V2B,
            proposed_records=(proposal,),
            evidence_overlay=overlay,
        )


def test_validator_rejects_persisted_undeclared_layer_keys(
    v2b_bundle: CorpusParityBundle,
) -> None:
    target = v2b_bundle.records[0]
    forged = dict(target)
    forged["layers"] = {
        **target["layers"],
        "eva_transcription": {"source": "inherited", "text": "forbidden lane"},
    }
    forged = _reseal(forged)
    records = tuple(
        forged if row["region_id"] == target["region_id"] else row
        for row in v2b_bundle.records
    )
    summary = dict(v2b_bundle.summary)
    summary["records_sha256"] = sha256(canonical_json(records).encode("utf-8")).hexdigest()
    summary = _reseal(summary)

    errors = validate_corpus_parity_bundle(
        replace(v2b_bundle, records=records, summary=summary),
        V2B,
    )

    assert "PARITY_RECORD_LAYER_KEYS_INVALID" in errors


def test_validator_rejects_self_hashed_orphan_evidence(
    v2b_bundle: CorpusParityBundle,
) -> None:
    orphan = _seal(
        schema="zfd.parity_ocr.v1",
        page_id="orphan-page",
        region_id="orphan-region",
        ocr_id="orphan-ocr",
    )
    authority = dict(v2b_bundle.evidence_authority)
    layers = {
        name: dict(records)
        for name, records in v2b_bundle.evidence_authority["layers"].items()
    }
    layers["ocr"] = {orphan["receipt_sha256"]: orphan}
    authority["layers"] = layers
    authority = _reseal(authority)
    summary = dict(v2b_bundle.summary)
    summary["evidence_authority_receipt_sha256"] = authority["receipt_sha256"]
    summary = _reseal(summary)

    errors = validate_corpus_parity_bundle(
        replace(v2b_bundle, evidence_authority=authority, summary=summary),
        V2B,
    )

    assert "EVIDENCE_AUTHORITY_UNPINNED" in errors


def test_validator_recomputes_summary_and_rejects_counter_tampering(
    v2b_bundle: CorpusParityBundle,
) -> None:
    bundle = v2b_bundle
    summary = dict(bundle.summary)
    summary["confirmed_translated_regions"] = 670

    errors = validate_corpus_parity_bundle(replace(bundle, summary=summary), V2B)

    assert "SUMMARY_RECOMPUTE_MISMATCH" in errors


def test_validator_rejects_forged_record_schema_and_review_state(
    v2b_bundle: CorpusParityBundle,
) -> None:
    target = v2b_bundle.records[0]
    forged = dict(target)
    forged["schema"] = "zfd.forged_record.v999"
    forged["review_state"] = "approved"
    forged = _reseal(forged)
    records = tuple(
        forged if row["region_id"] == target["region_id"] else row
        for row in v2b_bundle.records
    )
    summary = dict(v2b_bundle.summary)
    summary["records_sha256"] = sha256(canonical_json(records).encode("utf-8")).hexdigest()
    summary = _reseal(summary)

    errors = validate_corpus_parity_bundle(
        replace(v2b_bundle, records=records, summary=summary),
        V2B,
    )

    assert "PARITY_RECORD_SCHEMA_INVALID" in errors
    assert "PARITY_RECORD_REVIEW_STATE_MISMATCH" in errors


def test_validator_rejects_forged_page_disposition_semantics(
    v2b_bundle: CorpusParityBundle,
) -> None:
    target = v2b_bundle.page_dispositions[0]
    forged = dict(target)
    forged.update(
        schema="zfd.forged_disposition.v999",
        review_state="approved",
        exclusion_reason="invented",
        nontext_review_receipt_sha256="f" * 64,
    )
    forged = _reseal(forged)
    dispositions = tuple(
        forged if row["page_id"] == target["page_id"] else row
        for row in v2b_bundle.page_dispositions
    )
    summary = dict(v2b_bundle.summary)
    summary["page_dispositions_sha256"] = sha256(
        canonical_json(dispositions).encode("utf-8")
    ).hexdigest()
    summary = _reseal(summary)

    errors = validate_corpus_parity_bundle(
        replace(v2b_bundle, page_dispositions=dispositions, summary=summary),
        V2B,
    )

    assert "PAGE_DISPOSITION_SCHEMA_INVALID" in errors
    assert "PAGE_DISPOSITION_RECOMPUTE_MISMATCH" in errors


def test_bundle_writer_is_exact_new_only_and_byte_deterministic(
    tmp_path: Path, v2b_bundle: CorpusParityBundle
) -> None:
    bundle = v2b_bundle
    first = tmp_path / "first"
    second = tmp_path / "second"

    write_corpus_parity_new(first, bundle)
    write_corpus_parity_new(second, bundle)

    assert {path.name for path in first.iterdir()} == set(PARITY_FILES)
    assert read_corpus_parity(first) == bundle
    assert {
        name: (first / name).read_bytes() for name in PARITY_FILES
    } == {name: (second / name).read_bytes() for name in PARITY_FILES}
    assert all(b"\r\n" not in (first / name).read_bytes() for name in PARITY_FILES)
    with pytest.raises(FileExistsError):
        write_corpus_parity_new(first, bundle)


def test_bundle_writer_failure_leaves_no_partial_target_and_allows_retry(
    tmp_path: Path,
    v2b_bundle: CorpusParityBundle,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "parity-run"
    original_open = Path.open

    def fail_on_records(path: Path, *args: object, **kwargs: object):
        if path.name == "records.jsonl":
            raise OSError("injected write failure")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fail_on_records)
    with pytest.raises(OSError, match="injected write failure"):
        write_corpus_parity_new(target, v2b_bundle)
    assert not target.exists()

    monkeypatch.setattr(Path, "open", original_open)
    write_corpus_parity_new(target, v2b_bundle)
    assert {path.name for path in target.iterdir()} == set(PARITY_FILES)


def test_cli_confines_new_outputs_to_parity_evidence_roots(tmp_path: Path) -> None:
    repository = tmp_path.resolve()
    allowed = _resolve_output(
        Path("build/image_native/parity/run-1"),
        repository,
    )

    assert allowed == repository / "build" / "image_native" / "parity" / "run-1"
    with pytest.raises(ValueError, match="OUTPUT_OUTSIDE_PARITY_ROOTS"):
        _resolve_output(Path("translations/guessed.json"), repository)


def test_cli_rejects_windows_junction_escape_from_allowed_output_root(
    tmp_path: Path,
) -> None:
    if sys.platform != "win32":
        pytest.skip("Windows junction boundary test")
    repository = tmp_path / "repository"
    outside = tmp_path / "outside"
    parent = repository / "build" / "image_native"
    parent.mkdir(parents=True)
    outside.mkdir()
    junction = parent / "parity"
    created = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(junction), str(outside)],
        check=False,
        capture_output=True,
        text=True,
    )
    if created.returncode:
        pytest.skip(f"junction unavailable: {created.stderr.strip()}")

    with pytest.raises(ValueError, match="OUTPUT_OUTSIDE_REPOSITORY"):
        _resolve_output(Path("build/image_native/parity/escaped-run"), repository.resolve())


def test_parity_materialiser_primary_lane_has_no_inherited_text_dependency() -> None:
    hits = scan_primary_lane(
        ROOT / "zfd_parity_corpus",
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
        include={"__init__.py", "__main__.py", "cli.py", "core.py"},
    )

    assert hits == []
