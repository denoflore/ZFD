"""Quarantined geometry comparison receives stable IDs and no labels."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from zfd_image_native.io import write_json, write_jsonl
from zfd_image_native.kraken_compare import (
    _external_segment,
    _value_sha256,
    freeze_geometry_comparison,
    validate_corpus_geometry_comparison,
    validate_geometry_comparison,
)
from zfd_image_native.models import PageRecord


@dataclass
class _Region:
    id: str
    boundary: list[list[int]]


@dataclass
class _Line:
    id: str
    baseline: list[list[int]]
    boundary: list[list[int]]
    regions: list[str]


@dataclass
class _Segmentation:
    regions: dict[str, list[_Region]]
    lines: list[_Line]


def _page() -> PageRecord:
    return PageRecord(
        page_id="source:iiif:1",
        source_id="source",
        surface_label="1r",
        iiif_id="1",
        iiif_base_uri="https://example.invalid/iiif/1",
        image_request_uri="https://example.invalid/iiif/1/full/max/0/default.jpg",
        image_sha256="a" * 64,
        image_path="build/source/1.jpg",
        width=100,
        height=80,
        mime_type="image/jpeg",
        acquisition_status="verified",
    )


def _model() -> dict:
    return {
        "model_id": "segmenter",
        "pinned_revision": "revision",
        "software": "kraken==6.0.0",
        "files": [{"sha256": "b" * 64}],
    }


def _frozen() -> dict:
    return {"run_id": "sha256:" + "c" * 64, "receipt_sha256": "d" * 64}


def _segmentation(region_id: str, line_id: str) -> _Segmentation:
    return _Segmentation(
        regions={"text": [_Region(region_id, [[5, 5], [90, 5], [90, 50], [5, 50]])]},
        lines=[
            _Line(
                line_id,
                [[10, 30], [80, 30]],
                [[10, 15], [80, 15], [80, 35], [10, 35]],
                [region_id],
            )
        ],
    )


def test_geometry_comparison_is_stable_across_upstream_random_ids() -> None:
    first = freeze_geometry_comparison(
        page=_page(),
        frozen_page_receipt=_frozen(),
        model=_model(),
        segmentation=_segmentation("random-region-a", "random-line-a"),
        software_version="6.0.0",
    )
    second = freeze_geometry_comparison(
        page=_page(),
        frozen_page_receipt=_frozen(),
        model=_model(),
        segmentation=_segmentation("random-region-b", "random-line-b"),
        software_version="6.0.0",
    )

    assert first == second
    assert first["primary_lane_allowed"] is False
    assert first["review_state"] == "unreviewed"
    assert first["recognition_output"] is None
    assert first["lines"][0]["diplomatic_label"] is None
    assert first["lines"][0]["region_ids"] == [first["regions"][0]["region_id"]]


def test_geometry_comparison_rejects_coordinates_outside_source_pixels() -> None:
    segmentation = _segmentation("region", "line")
    segmentation.lines[0].baseline[1][0] = 100

    try:
        freeze_geometry_comparison(
            page=_page(),
            frozen_page_receipt=_frozen(),
            model=_model(),
            segmentation=segmentation,
            software_version="6.0.0",
        )
    except ValueError as error:
        assert "image bounds" in str(error)
    else:
        raise AssertionError("Out of bounds comparative geometry was accepted")


def test_tolerant_geometry_receipt_preserves_strict_failure(tmp_path) -> None:
    result = freeze_geometry_comparison(
        page=_page(),
        frozen_page_receipt=_frozen(),
        model=_model(),
        segmentation=_segmentation("region", "line"),
        software_version="6.0.0",
        external_segmentation_disposition="tolerant_after_strict_topology_failure",
        external_warnings=(
            "shapely.errors.GEOSException:TopologyException: invalid polygon",
        ),
    )
    target = tmp_path / "comparison.json"
    write_json(target, result)

    assert result["external_segmentation_disposition"] == (
        "tolerant_after_strict_topology_failure"
    )
    assert result["external_warnings"] == [
        "shapely.errors.GEOSException:TopologyException: invalid polygon"
    ]
    assert validate_geometry_comparison(target) == ()


def test_saved_geometry_comparison_tampering_is_detected(tmp_path) -> None:
    result = freeze_geometry_comparison(
        page=_page(),
        frozen_page_receipt=_frozen(),
        model=_model(),
        segmentation=_segmentation("region", "line"),
        software_version="6.0.0",
    )
    result["primary_lane_allowed"] = True
    result["lines"][0]["diplomatic_label"] = "x"
    target = tmp_path / "comparison.json"
    write_json(target, result)

    errors = validate_geometry_comparison(target)

    assert "COMPARISON_RECEIPT_HASH_MISMATCH" in errors
    assert "COMPARISON_ID_MISMATCH" in errors
    assert "COMPARISON_PRIMARY_LANE_NOT_BLOCKED" in errors
    assert any(error.startswith("COMPARISON_LABEL_PRESENT:") for error in errors)


def test_corpus_geometry_comparison_joins_manifest_and_page_receipts(tmp_path) -> None:
    comparison = freeze_geometry_comparison(
        page=_page(),
        frozen_page_receipt=_frozen(),
        model=_model(),
        segmentation=_segmentation("region", "line"),
        software_version="6.0.0",
    )
    comparison_name = "1.kraken.json"
    write_json(tmp_path / comparison_name, comparison)
    manifest = tmp_path / "manifest.jsonl"
    write_jsonl(manifest, [asdict(_page())])
    summary_payload = {
        "schema": "zfd.segmentation_comparison_corpus.v1",
        "schema_version": "1.0.0",
        "model_id": "segmenter",
        "model_sha256": "b" * 64,
        "model_pinned_revision": "revision",
        "software": "kraken==6.0.0",
        "software_runtime_version": "6.0.0",
        "primary_run_id": _frozen()["run_id"],
        "primary_run_receipt_sha256": "e" * 64,
        "input_page_count": 1,
        "processed_page_count": 1,
        "failed_page_count": 0,
        "primary_total_lines": 1,
        "comparative_total_lines": 1,
        "comparative_total_regions": 1,
        "primary_lane_allowed": False,
        "metrics_status": "not_measured",
        "review_state": "unreviewed",
        "pages": [
            {
                "page_id": _page().page_id,
                "iiif_id": _page().iiif_id,
                "image_sha256": _page().image_sha256,
                "comparison_id": comparison["comparison_id"],
                "comparison_receipt_sha256": comparison["receipt_sha256"],
                "comparison_record": comparison_name,
                "primary_line_count": 1,
                "comparative_line_count": 1,
                "comparative_region_count": 1,
                "review_state": "unreviewed",
                "disposition": "comparative_geometry_unreviewed",
            }
        ],
        "failures": [],
    }
    summary_id = "sha256:" + _value_sha256(summary_payload)
    summary_receipt = {**summary_payload, "summary_id": summary_id}
    summary = {
        **summary_receipt,
        "receipt_sha256": _value_sha256(summary_receipt),
    }
    summary_path = tmp_path / "summary.json"
    write_json(summary_path, summary)

    assert validate_corpus_geometry_comparison(summary_path, manifest) == ()

    summary["pages"][0]["comparison_receipt_sha256"] = "0" * 64
    changed_payload = {
        key: value
        for key, value in summary.items()
        if key not in {"summary_id", "receipt_sha256"}
    }
    summary["summary_id"] = "sha256:" + _value_sha256(changed_payload)
    summary["receipt_sha256"] = _value_sha256(
        {key: value for key, value in summary.items() if key != "receipt_sha256"}
    )
    write_json(summary_path, summary)

    errors = validate_corpus_geometry_comparison(summary_path, manifest)
    assert any(error.startswith("CORPUS_PAGE_RECEIPT_MISMATCH:") for error in errors)


def test_external_segment_failure_keeps_exception_type() -> None:
    class Source:
        def convert(self, _mode):
            return self

    class ModelAPI:
        @staticmethod
        def segment(*args, **kwargs):
            raise ArithmeticError("invalid polygon")

    try:
        _external_segment(ModelAPI, Source(), object())
    except RuntimeError as error:
        assert "builtins.ArithmeticError" in str(error)
        assert "invalid polygon" in str(error)
    else:
        raise AssertionError("External segment failure was hidden")


def test_external_segment_retries_topology_failure_with_explicit_warning() -> None:
    topology_error = type("GEOSException", (Exception,), {"__module__": "shapely.errors"})

    class Source:
        def convert(self, _mode):
            return self

    class ModelAPI:
        calls: list[bool] = []

        @classmethod
        def segment(cls, *args, **kwargs):
            strict = kwargs["raise_on_error"]
            cls.calls.append(strict)
            if strict:
                raise topology_error("TopologyException: invalid polygon")
            return _segmentation("region", "line")

    result = _external_segment(ModelAPI, Source(), object())

    assert ModelAPI.calls == [True, False]
    assert result.disposition == "tolerant_after_strict_topology_failure"
    assert result.segmentation.lines
    assert result.warnings == (
        "shapely.errors.GEOSException:TopologyException: invalid polygon",
    )
