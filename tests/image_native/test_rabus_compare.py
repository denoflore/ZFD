"""The Rabus recognizer remains an explicitly rejected comparison lane."""

from __future__ import annotations

import ast
from pathlib import Path

import numpy as np
from PIL import Image

from zfd_image_native.boundary import scan_primary_lane
from zfd_image_native.io import write_json
from zfd_image_native.rabus_compare import (
    _ctc_lattice_from_probabilities,
    _load_checkpoint_state,
    _value_sha256,
    freeze_rabus_comparison,
    load_ordered_symbols,
    polygon_mask_crop,
    preprocess_crop,
    validate_rabus_comparison,
)


ROOT = Path(__file__).resolve().parents[2]


def test_ordered_symbols_preserve_duplicate_class_ids(tmp_path: Path) -> None:
    expected = [f"s{class_id}" for class_id in range(1, 77)]
    expected[1] = "2"
    expected[12] = "2"
    symbol_path = tmp_path / "symbols.txt"
    symbol_path.write_text("\n".join(expected) + "\n", encoding="utf-8")

    symbols = load_ordered_symbols(symbol_path)

    assert len(symbols) == 76
    assert symbols[1] == "2"  # class ID 2
    assert symbols[12] == "2"  # class ID 13
    assert symbols.count("2") == 2


def test_polygon_crop_whitens_pixels_outside_line_boundary() -> None:
    source = Image.new("L", (10, 10), 0)
    crop, bbox = polygon_mask_crop(source, [[2, 2], [7, 2], [2, 7]])

    assert bbox == [2, 2, 6, 6]
    assert crop.mode == "L"
    assert crop.size == (6, 6)
    assert crop.getpixel((0, 0)) == 0
    assert crop.getpixel((5, 5)) == 255


def test_preprocess_is_height_128_aspect_preserved_and_normalised() -> None:
    crop = Image.new("L", (60, 30), 255)
    tensor, metadata = preprocess_crop(crop)

    assert tensor.shape == (1, 1, 128, 256)
    assert tensor.dtype == np.float32
    assert np.all(tensor == np.float32(1.0))
    assert metadata["target_height"] == 128
    assert metadata["unclamped_width"] == 256
    assert metadata["target_width"] == 256
    assert metadata["width_clamp"] == [32, 10000]
    assert metadata["normalisation"] == "(x/255-0.5)/0.5"


def test_preprocess_applies_declared_training_width_clamp() -> None:
    narrow, narrow_metadata = preprocess_crop(Image.new("L", (1, 100), 0))
    wide, wide_metadata = preprocess_crop(Image.new("L", (200, 1), 0))

    assert narrow.shape == (1, 1, 128, 32)
    assert narrow_metadata["unclamped_width"] == 1
    assert wide.shape == (1, 1, 128, 10000)
    assert wide_metadata["unclamped_width"] == 25600


def test_lattice_retains_blank_and_duplicate_symbol_class_identity() -> None:
    symbols = tuple(["x"] * 76)
    symbols = symbols[:1] + ("2",) + symbols[2:12] + ("2",) + symbols[13:]
    probabilities = np.full((5, 77), 1e-6, dtype=np.float64)
    tops = [(0, 0.80), (2, 0.70), (2, 0.60), (0, 0.90), (13, 0.75)]
    for timestep, (class_id, posterior) in enumerate(tops):
        probabilities[timestep, class_id] = posterior
        probabilities[timestep, 1] = 1.0 - posterior - (75e-6)

    lattice, events, candidate = _ctc_lattice_from_probabilities(
        probabilities,
        symbols,
        alternative_count=3,
    )

    assert len(lattice) == 5
    assert lattice[0]["top_class_id"] == 0
    assert lattice[0]["top_symbol"] is None
    assert lattice[0]["blank_posterior"] == 0.80
    assert [event["class_id"] for event in events] == [2, 13]
    assert [event["symbol"] for event in events] == ["2", "2"]
    assert candidate == "22"
    assert all(row["alternatives"] for row in lattice)


def test_checkpoint_loader_requires_safe_weights_only_mode(tmp_path) -> None:
    checkpoint_path = tmp_path / "model.pt"
    checkpoint_path.write_bytes(b"fixture")

    class FakeTorch:
        call = None

        @classmethod
        def load(cls, path, *, map_location, weights_only):
            cls.call = (path, map_location, weights_only)
            return {"model_state_dict": {"fc.weight": object()}}

    state = _load_checkpoint_state(FakeTorch, checkpoint_path)

    assert "fc.weight" in state
    assert FakeTorch.call == (checkpoint_path, "cpu", True)


def _receipt_fixture() -> dict:
    ordered_symbols = tuple(f"s{class_id}" for class_id in range(1, 77))
    ordered_symbols = (
        ordered_symbols[:1]
        + ("2",)
        + ordered_symbols[2:12]
        + ("2",)
        + ordered_symbols[13:]
    )
    lattice = [
        {
            "timestep": timestep,
            "top_class_id": 0,
            "top_symbol": None,
            "top_posterior": 0.8,
            "blank_posterior": 0.8,
            "alternatives": [
                {"class_id": 0, "symbol": None, "posterior": 0.8},
                {"class_id": 2, "symbol": "2", "posterior": 0.2},
            ],
        }
        for timestep in range(4)
    ]
    preprocessing = {"target_height": 128, "target_width": 32}
    inventory = [{"class_id": 0, "symbol": None}] + [
        {"class_id": class_id, "symbol": symbol}
        for class_id, symbol in enumerate(ordered_symbols, start=1)
    ]
    return freeze_rabus_comparison(
        page_id="yale-ms-408:iiif:1006272",
        source_id="yale-ms-408",
        image_sha256="a" * 64,
        page_record_sha256="b" * 64,
        manifest_sha256="c" * 64,
        geometry_comparison_id="sha256:" + "d" * 64,
        geometry_receipt_sha256="e" * 64,
        geometry_file_sha256="f" * 64,
        geometry_model_id="segmenter",
        geometry_model_sha256="1" * 64,
        line_id="sha256:" + "2" * 64,
        line_geometry_sha256="3" * 64,
        boundary=[[2, 2], [7, 2], [2, 7]],
        crop_bbox=[2, 2, 6, 6],
        crop_sha256="4" * 64,
        tensor_sha256="5" * 64,
        tensor_shape=[1, 1, 128, 32],
        preprocessing=preprocessing,
        preprocessing_sha256=_value_sha256(preprocessing),
        model_id="rabus",
        model_sha256="7" * 64,
        model_record_sha256="8" * 64,
        model_register_sha256="9" * 64,
        model_revision="revision",
        model_config_sha256="0" * 64,
        model_config_record_sha256="a" * 64,
        symbols_sha256="b" * 64,
        ordered_symbols_sha256=_value_sha256(inventory),
        ordered_symbols=ordered_symbols,
        software_runtime_version="2.7.1+cpu",
        output_shape=[4, 1, 77],
        lattice=lattice,
        greedy_events=[],
        comparative_candidate_latin="",
        comparative_candidate_score=None,
    )


def test_frozen_receipt_blocks_diplomatic_and_semantic_claims(tmp_path) -> None:
    receipt = _receipt_fixture()
    target = tmp_path / "rabus.json"
    write_json(target, receipt)

    assert receipt["primary_lane_allowed"] is False
    assert receipt["acceptance_state"] == "rejected"
    assert receipt["diplomatic_label"] is None
    assert receipt["recognition_confidence"] is None
    assert receipt["unknown_probability"] is None
    assert receipt["metrics_status"] == "not_measured"
    assert receipt["review_state"] == "unreviewed"
    assert len(receipt["rejection_reasons"]) >= 4
    assert validate_rabus_comparison(target) == ()


def test_validator_detects_quarantine_and_hash_tampering(tmp_path) -> None:
    receipt = _receipt_fixture()
    receipt["primary_lane_allowed"] = True
    receipt["diplomatic_label"] = "forbidden"
    receipt["unknown_probability"] = 0.2
    target = tmp_path / "rabus.json"
    write_json(target, receipt)

    errors = validate_rabus_comparison(target)

    assert "RABUS_RECEIPT_HASH_MISMATCH" in errors
    assert "RABUS_COMPARISON_ID_MISMATCH" in errors
    assert "RABUS_PRIMARY_LANE_NOT_BLOCKED" in errors
    assert "RABUS_DIPLOMATIC_LABEL_PRESENT" in errors
    assert "RABUS_UNKNOWN_PROBABILITY_PRESENT" in errors


def test_validator_rejects_resealed_events_that_do_not_follow_lattice(tmp_path) -> None:
    receipt = _receipt_fixture()
    receipt["greedy_class_events"] = [
        {
            "event_index": 0,
            "timestep": 0,
            "class_id": 2,
            "symbol": "2",
            "posterior": 0.8,
            "alternatives": receipt["ctc_lattice"][0]["alternatives"],
        }
    ]
    receipt["comparative_candidate_latin"] = "2"
    receipt["comparative_candidate_score"] = 0.8
    comparison_payload = {
        key: value
        for key, value in receipt.items()
        if key not in {"comparison_id", "receipt_sha256"}
    }
    receipt["comparison_id"] = "sha256:" + _value_sha256(comparison_payload)
    receipt["receipt_sha256"] = _value_sha256(
        {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    )
    target = tmp_path / "rabus.json"
    write_json(target, receipt)

    errors = validate_rabus_comparison(target)

    assert "RABUS_RECEIPT_HASH_MISMATCH" not in errors
    assert "RABUS_COMPARISON_ID_MISMATCH" not in errors
    assert "RABUS_GREEDY_COLLAPSE_INVALID" in errors


def test_module_is_lazy_torch_and_has_no_inherited_text_dependency() -> None:
    module = ROOT / "zfd_image_native" / "rabus_compare.py"
    tree = ast.parse(module.read_text(encoding="utf-8"), filename=str(module))
    top_level_imports = {
        alias.name
        for node in tree.body
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module
        for node in tree.body
        if isinstance(node, ast.ImportFrom) and node.module
    }

    assert "torch" not in top_level_imports
    assert scan_primary_lane(
        ROOT / "zfd_image_native",
        {
            "eva",
            "ivtff",
            "zandbergen",
            "zfd_decoder",
            "02_transcriptions",
            "raw_eva",
            "lexicon.csv",
        },
        include={"rabus_compare.py"},
    ) == []
