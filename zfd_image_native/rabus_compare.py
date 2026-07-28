"""Quarantined Rabus CRNN CTC comparison for one registered image line."""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path
import re
from typing import Any

import numpy as np
from PIL import Image, ImageDraw

from .io import canonical_json, read_json, sha256_file, write_json
from .kraken_compare import validate_geometry_comparison
from .manifest import load_page_manifest
from .model_registry import validate_model_registry


SCHEMA_VERSION = "1.0.0"
OUTPUT_CLASS_COUNT = 77
BLANK_CLASS_ID = 0
TARGET_HEIGHT = 128
MIN_WIDTH = 32
MAX_WIDTH = 10000
DEFAULT_MODEL_ID = "rabus-crnn-ctc-glagolitic-16549a7f"
REJECTION_REASONS = (
    "model_output_is_expanded_latin_comparative_text_not_diplomatic_glyphs",
    "model_has_no_source_excluded_validation_on_the_selected_unknown_hand",
    "model_posterior_is_not_calibrated_as_recognition_confidence",
    "model_has_no_calibrated_open_set_unknown_rejection",
    "upstream_line_geometry_is_unreviewed",
)

_SHA256 = re.compile(r"[0-9a-f]{64}")
_SHA256_ID = re.compile(r"sha256:[0-9a-f]{64}")


def _value_sha256(value: Any) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _image_sha256(image: Image.Image) -> str:
    digest = sha256()
    digest.update(
        canonical_json(
            {"mode": image.mode, "width": image.width, "height": image.height}
        ).encode("utf-8")
    )
    digest.update(b"\0")
    digest.update(image.tobytes())
    return digest.hexdigest()


def _tensor_sha256(tensor: np.ndarray) -> str:
    stable = np.ascontiguousarray(tensor, dtype="<f4")
    digest = sha256()
    digest.update(
        canonical_json(
            {"dtype": "float32-le", "shape": [int(value) for value in stable.shape]}
        ).encode("utf-8")
    )
    digest.update(b"\0")
    digest.update(stable.tobytes(order="C"))
    return digest.hexdigest()


def load_ordered_symbols(path: str | Path) -> tuple[str, ...]:
    """Load one symbol per line without constructing a symbol keyed mapping."""

    text = Path(path).read_text(encoding="utf-8")
    symbols = tuple(text.splitlines())
    if not symbols or any(symbol == "" for symbol in symbols):
        raise ValueError("Symbol inventory contains an empty class line")
    return symbols


def _class_symbol(ordered_symbols: Sequence[str], class_id: int) -> str | None:
    if class_id == BLANK_CLASS_ID:
        return None
    if not 1 <= class_id <= len(ordered_symbols):
        raise ValueError(f"Class ID leaves the ordered symbol inventory: {class_id}")
    return ordered_symbols[class_id - 1]


def _candidate_symbol(symbol: str) -> str:
    return " " if symbol in {"<space>", "<SPACE>"} else symbol


def _points(
    value: Any,
    *,
    width: int,
    height: int,
    minimum_points: int = 3,
) -> list[list[int]]:
    if not isinstance(value, list) or len(value) < minimum_points:
        raise ValueError(f"Geometry has fewer than {minimum_points} points")
    points: list[list[int]] = []
    for point in value:
        if not isinstance(point, list) or len(point) != 2:
            raise ValueError("Line boundary point is malformed")
        x, y = point
        if not isinstance(x, int) or not isinstance(y, int):
            raise ValueError("Line boundary coordinate is not an integer")
        if not 0 <= x < width or not 0 <= y < height:
            raise ValueError("Line boundary leaves registered source pixels")
        points.append([x, y])
    if len({tuple(point) for point in points}) < minimum_points:
        raise ValueError(f"Geometry has fewer than {minimum_points} distinct points")
    return points


def _geometry_bbox(*geometries: Sequence[Sequence[int]]) -> list[int]:
    points = [point for geometry in geometries for point in geometry]
    left = min(point[0] for point in points)
    top = min(point[1] for point in points)
    right = max(point[0] for point in points)
    bottom = max(point[1] for point in points)
    return [left, top, right - left + 1, bottom - top + 1]


def polygon_mask_crop(
    source: Image.Image,
    boundary: Sequence[Sequence[int]],
) -> tuple[Image.Image, list[int]]:
    """Crop one polygon and replace every pixel outside it with white."""

    points = _points(
        [list(point) for point in boundary],
        width=source.width,
        height=source.height,
    )
    bbox = _geometry_bbox(points)
    left, top, crop_width, crop_height = bbox
    grayscale = source.convert("L")
    source_crop = grayscale.crop((left, top, left + crop_width, top + crop_height))
    local_points = [(x - left, y - top) for x, y in points]
    mask = Image.new("L", source_crop.size, 0)
    ImageDraw.Draw(mask).polygon(local_points, fill=255)
    white = Image.new("L", source_crop.size, 255)
    return Image.composite(source_crop, white, mask), bbox


def preprocess_crop(crop: Image.Image) -> tuple[np.ndarray, dict[str, Any]]:
    """Apply the registered Rabus grayscale and resize transform."""

    if crop.width <= 0 or crop.height <= 0:
        raise ValueError("Line crop has invalid dimensions")
    grayscale = crop.convert("L")
    unclamped_width = max(1, int(TARGET_HEIGHT * grayscale.width / grayscale.height))
    target_width = min(MAX_WIDTH, max(MIN_WIDTH, unclamped_width))
    resized = grayscale.resize(
        (target_width, TARGET_HEIGHT),
        resample=Image.Resampling.LANCZOS,
    )
    array = np.asarray(resized, dtype=np.float32).copy()
    array /= np.float32(255.0)
    array = (array - np.float32(0.5)) / np.float32(0.5)
    tensor = np.ascontiguousarray(array[np.newaxis, np.newaxis, :, :], dtype=np.float32)
    metadata = {
        "source_mode": crop.mode,
        "source_width": crop.width,
        "source_height": crop.height,
        "grayscale_mode": "L",
        "target_height": TARGET_HEIGHT,
        "unclamped_width": unclamped_width,
        "target_width": target_width,
        "width_clamp": [MIN_WIDTH, MAX_WIDTH],
        "aspect_ratio_preserved_before_width_clamp": True,
        "resampling": "PIL.Image.Resampling.LANCZOS",
        "normalisation": "(x/255-0.5)/0.5",
        "tensor_dtype": "float32",
        "tensor_layout": "NCHW",
    }
    return tensor, metadata


def _ctc_lattice_from_probabilities(
    probabilities: np.ndarray,
    ordered_symbols: Sequence[str],
    *,
    alternative_count: int = 5,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    """Keep every greedy timestep, then collapse classes under the CTC rule."""

    values = np.asarray(probabilities, dtype=np.float64)
    expected_classes = len(ordered_symbols) + 1
    if values.ndim != 2 or values.shape[1] != expected_classes:
        raise ValueError(
            f"Probability lattice shape is invalid: {values.shape}; expected (*,{expected_classes})"
        )
    if not 1 <= alternative_count <= expected_classes:
        raise ValueError("Alternative count leaves the class inventory")
    if not np.all(np.isfinite(values)) or np.any(values < 0.0) or np.any(values > 1.0):
        raise ValueError("Probability lattice contains invalid posterior values")
    if not np.allclose(values.sum(axis=1), 1.0, atol=1e-5, rtol=1e-5):
        raise ValueError("Probability lattice rows do not sum to one")

    lattice: list[dict[str, Any]] = []
    top_classes: list[int] = []
    for timestep, row in enumerate(values):
        ranked = sorted(range(expected_classes), key=lambda class_id: (-row[class_id], class_id))
        top_class = ranked[0]
        top_classes.append(top_class)
        alternatives = [
            {
                "class_id": class_id,
                "symbol": _class_symbol(ordered_symbols, class_id),
                "posterior": float(row[class_id]),
            }
            for class_id in ranked[:alternative_count]
        ]
        lattice.append(
            {
                "timestep": timestep,
                "top_class_id": top_class,
                "top_symbol": _class_symbol(ordered_symbols, top_class),
                "top_posterior": float(row[top_class]),
                "blank_posterior": float(row[BLANK_CLASS_ID]),
                "alternatives": alternatives,
            }
        )

    events: list[dict[str, Any]] = []
    previous_class: int | None = None
    for timestep, class_id in enumerate(top_classes):
        if class_id != BLANK_CLASS_ID and class_id != previous_class:
            symbol = _class_symbol(ordered_symbols, class_id)
            if symbol is None:
                raise ValueError("Nonblank CTC event has no ordered symbol")
            events.append(
                {
                    "event_index": len(events),
                    "timestep": timestep,
                    "class_id": class_id,
                    "symbol": symbol,
                    "posterior": lattice[timestep]["top_posterior"],
                    "alternatives": lattice[timestep]["alternatives"],
                }
            )
        previous_class = class_id
    candidate = "".join(_candidate_symbol(event["symbol"]) for event in events)
    return lattice, events, candidate


def _load_checkpoint_state(torch_module: Any, checkpoint_path: Path) -> Mapping[str, Any]:
    checkpoint = torch_module.load(
        checkpoint_path,
        map_location="cpu",
        weights_only=True,
    )
    if not isinstance(checkpoint, Mapping):
        raise ValueError("Rabus checkpoint is not a mapping")
    state = checkpoint.get("model_state_dict", checkpoint.get("state_dict", checkpoint))
    if not isinstance(state, Mapping) or "fc.weight" not in state:
        raise ValueError("Rabus checkpoint has no recognised model state")
    return state


def _architecture_config(config: Mapping[str, Any]) -> dict[str, Any]:
    expected = {
        "img_height": TARGET_HEIGHT,
        "cnn_filters": [12, 24, 48, 48],
        "cnn_poolsize": [2, 2, 0, 2],
        "rnn_hidden": 256,
        "rnn_layers": 3,
        "dropout": 0.5,
    }
    for field, value in expected.items():
        if config.get(field) != value:
            raise ValueError(f"Registered Rabus architecture differs at {field}")
    return expected


def _build_crnn(torch_module: Any, config: Mapping[str, Any]) -> Any:
    nn = torch_module.nn
    architecture = _architecture_config(config)

    class CRNN(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            cnn_layers: list[Any] = []
            in_channels = 1
            for index, out_channels in enumerate(architecture["cnn_filters"]):
                cnn_layers.extend(
                    [
                        nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1, dilation=1),
                        nn.BatchNorm2d(out_channels),
                        nn.LeakyReLU(0.2, inplace=True),
                    ]
                )
                if architecture["cnn_poolsize"][index] > 0:
                    cnn_layers.append(nn.MaxPool2d(kernel_size=2, stride=2))
                in_channels = out_channels
            self.cnn = nn.Sequential(*cnn_layers)
            pool_count = sum(value > 0 for value in architecture["cnn_poolsize"])
            output_height = architecture["img_height"] // (2**pool_count)
            rnn_input = architecture["cnn_filters"][-1] * output_height
            self.rnn = nn.LSTM(
                input_size=rnn_input,
                hidden_size=architecture["rnn_hidden"],
                num_layers=architecture["rnn_layers"],
                dropout=architecture["dropout"],
                bidirectional=True,
                batch_first=False,
            )
            self.lin_dropout = nn.Dropout(architecture["dropout"])
            self.fc = nn.Linear(architecture["rnn_hidden"] * 2, OUTPUT_CLASS_COUNT)

        def forward(self, tensor: Any) -> Any:
            convolution = self.cnn(tensor)
            batch, channels, height, width = convolution.size()
            sequence = convolution.permute(3, 0, 1, 2)
            sequence = sequence.reshape(width, batch, channels * height)
            recurrent, _ = self.rnn(sequence)
            output = self.fc(self.lin_dropout(recurrent))
            return torch_module.nn.functional.log_softmax(output, dim=2)

    return CRNN()


def _load_model(
    torch_module: Any,
    checkpoint_path: Path,
    config: Mapping[str, Any],
) -> Any:
    state = _load_checkpoint_state(torch_module, checkpoint_path)
    fc_weight = state["fc.weight"]
    shape = tuple(int(value) for value in getattr(fc_weight, "shape", ()))
    if shape != (OUTPUT_CLASS_COUNT, 512):
        raise ValueError(f"Rabus checkpoint output architecture is invalid: {shape}")
    model = _build_crnn(torch_module, config)
    model.load_state_dict(state, strict=True)
    model = model.to(torch_module.device("cpu"))
    model.eval()
    return model


def _registered_model(payload: Any, model_id: str) -> dict[str, Any]:
    if not isinstance(payload, dict) or not isinstance(payload.get("models"), list):
        raise ValueError("Model register is malformed")
    matches = [row for row in payload["models"] if row.get("model_id") == model_id]
    if len(matches) != 1:
        raise ValueError(f"Recognition model record is not unique: {model_id}")
    model = matches[0]
    if model.get("model_type") != "recognition":
        raise ValueError(f"Model is not registered for recognition: {model_id}")
    if model.get("primary_lane_allowed") is not False:
        raise ValueError(f"Recognition model is not quarantined: {model_id}")
    if model.get("diplomatic_label_allowed") is not False:
        raise ValueError(f"Recognition model permits diplomatic labels: {model_id}")
    required_files = {"best_model.pt", "model_config.json", "symbols.txt"}
    files = model.get("files")
    if not isinstance(files, list):
        raise ValueError(f"Recognition model files are malformed: {model_id}")
    names = [row.get("name") for row in files if isinstance(row, dict)]
    if not required_files <= set(names) or len(names) != len(set(names)):
        raise ValueError(f"Recognition model file identities are incomplete: {model_id}")
    return model


def _registered_geometry_model(payload: Any, geometry: Mapping[str, Any]) -> dict[str, Any]:
    model_id = geometry.get("model_id")
    matches = [row for row in payload.get("models", []) if row.get("model_id") == model_id]
    if len(matches) != 1 or matches[0].get("model_type") != "segmentation":
        raise ValueError("Geometry model record is not unique")
    model = matches[0]
    files = model.get("files")
    if not isinstance(files, list) or len(files) != 1:
        raise ValueError("Geometry model file identity is malformed")
    if files[0].get("sha256") != geometry.get("model_sha256"):
        raise ValueError("Geometry model checksum differs from its registered record")
    return model


def _model_files(model: Mapping[str, Any], repository_root: Path) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for row in model["files"]:
        path = (repository_root / row["cache_relpath"]).resolve()
        try:
            path.relative_to(repository_root)
        except ValueError as error:
            raise ValueError(f"Registered model path leaves repository: {row['name']}") from error
        if not path.is_file():
            raise ValueError(f"Registered model file is absent: {row['name']}")
        if sha256_file(path) != row["sha256"]:
            raise ValueError(f"Registered model checksum differs: {row['name']}")
        result[row["name"]] = path
    return result


def freeze_rabus_comparison(
    *,
    page_id: str,
    source_id: str,
    image_sha256: str,
    page_record_sha256: str,
    manifest_sha256: str,
    geometry_comparison_id: str,
    geometry_receipt_sha256: str,
    geometry_file_sha256: str,
    geometry_model_id: str,
    geometry_model_sha256: str,
    line_id: str,
    line_geometry_sha256: str,
    boundary: list[list[int]],
    crop_bbox: list[int],
    crop_sha256: str,
    tensor_sha256: str,
    tensor_shape: list[int],
    preprocessing: dict[str, Any],
    preprocessing_sha256: str,
    model_id: str,
    model_sha256: str,
    model_record_sha256: str,
    model_register_sha256: str,
    model_revision: str,
    model_config_sha256: str,
    model_config_record_sha256: str,
    symbols_sha256: str,
    ordered_symbols_sha256: str,
    ordered_symbols: Sequence[str],
    software_runtime_version: str,
    output_shape: list[int],
    lattice: list[dict[str, Any]],
    greedy_events: list[dict[str, Any]],
    comparative_candidate_latin: str,
    comparative_candidate_score: float | None,
) -> dict[str, Any]:
    """Freeze a content addressed comparison that is rejected from evidence layers."""

    symbol_inventory = [{"class_id": BLANK_CLASS_ID, "symbol": None}] + [
        {"class_id": class_id, "symbol": symbol}
        for class_id, symbol in enumerate(ordered_symbols, start=1)
    ]
    payload = {
        "schema": "zfd.rabus_recognition_comparison.v1",
        "schema_version": SCHEMA_VERSION,
        "page_id": page_id,
        "source_id": source_id,
        "image_sha256": image_sha256,
        "page_record_sha256": page_record_sha256,
        "manifest_sha256": manifest_sha256,
        "geometry_comparison_id": geometry_comparison_id,
        "geometry_receipt_sha256": geometry_receipt_sha256,
        "geometry_file_sha256": geometry_file_sha256,
        "geometry_model_id": geometry_model_id,
        "geometry_model_sha256": geometry_model_sha256,
        "line_id": line_id,
        "line_geometry_sha256": line_geometry_sha256,
        "line_boundary": boundary,
        "crop_bbox": crop_bbox,
        "crop_sha256": crop_sha256,
        "tensor_sha256": tensor_sha256,
        "tensor_shape": tensor_shape,
        "preprocessing": preprocessing,
        "preprocessing_sha256": preprocessing_sha256,
        "model_id": model_id,
        "model_sha256": model_sha256,
        "model_record_sha256": model_record_sha256,
        "model_register_sha256": model_register_sha256,
        "model_pinned_revision": model_revision,
        "model_config_sha256": model_config_sha256,
        "model_config_record_sha256": model_config_record_sha256,
        "symbols_sha256": symbols_sha256,
        "ordered_symbols_sha256": ordered_symbols_sha256,
        "blank_class_id": BLANK_CLASS_ID,
        "output_class_count": OUTPUT_CLASS_COUNT,
        "ordered_symbol_count": len(ordered_symbols),
        "ordered_symbol_inventory": symbol_inventory,
        "software": "custom-pytorch-crnn-ctc",
        "software_runtime_version": software_runtime_version,
        "output_shape": output_shape,
        "ctc_lattice": lattice,
        "greedy_class_events": greedy_events,
        "comparative_candidate_latin": comparative_candidate_latin,
        "comparative_candidate_score": comparative_candidate_score,
        "candidate_score_semantics": (
            "mean_emitted_top_class_posterior_comparative_score_only"
        ),
        "diplomatic_label": None,
        "recognition_confidence": None,
        "unknown_probability": None,
        "acceptance_state": "rejected",
        "rejection_reasons": list(REJECTION_REASONS),
        "primary_lane_allowed": False,
        "metrics_status": "not_measured",
        "review_state": "unreviewed",
        "disposition": "comparative_candidate_latin_rejected",
    }
    comparison_id = "sha256:" + _value_sha256(payload)
    receipt = {**payload, "comparison_id": comparison_id}
    return {**receipt, "receipt_sha256": _value_sha256(receipt)}


def _valid_hash(value: Any) -> bool:
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None


def _valid_hash_id(value: Any) -> bool:
    return isinstance(value, str) and _SHA256_ID.fullmatch(value) is not None


def validate_rabus_comparison(path: str | Path) -> tuple[str, ...]:
    """Validate a frozen Rabus comparison and its permanent quarantine fields."""

    try:
        payload = read_json(path)
    except (OSError, ValueError):
        return ("RABUS_COMPARISON_MALFORMED",)
    if not isinstance(payload, dict):
        return ("RABUS_COMPARISON_MALFORMED",)
    errors: list[str] = []
    receipt_payload = {
        key: value for key, value in payload.items() if key != "receipt_sha256"
    }
    if payload.get("receipt_sha256") != _value_sha256(receipt_payload):
        errors.append("RABUS_RECEIPT_HASH_MISMATCH")
    comparison_payload = {
        key: value for key, value in receipt_payload.items() if key != "comparison_id"
    }
    if payload.get("comparison_id") != "sha256:" + _value_sha256(comparison_payload):
        errors.append("RABUS_COMPARISON_ID_MISMATCH")
    if payload.get("schema") != "zfd.rabus_recognition_comparison.v1":
        errors.append("RABUS_SCHEMA_INVALID")
    if payload.get("schema_version") != SCHEMA_VERSION:
        errors.append("RABUS_SCHEMA_VERSION_INVALID")

    if payload.get("primary_lane_allowed") is not False:
        errors.append("RABUS_PRIMARY_LANE_NOT_BLOCKED")
    if payload.get("acceptance_state") != "rejected":
        errors.append("RABUS_ACCEPTANCE_STATE_INVALID")
    if payload.get("diplomatic_label") is not None:
        errors.append("RABUS_DIPLOMATIC_LABEL_PRESENT")
    if payload.get("recognition_confidence") is not None:
        errors.append("RABUS_RECOGNITION_CONFIDENCE_PRESENT")
    if payload.get("unknown_probability") is not None:
        errors.append("RABUS_UNKNOWN_PROBABILITY_PRESENT")
    if payload.get("metrics_status") != "not_measured":
        errors.append("RABUS_METRICS_STATUS_INVALID")
    if payload.get("review_state") != "unreviewed":
        errors.append("RABUS_REVIEW_STATE_INVALID")
    if payload.get("disposition") != "comparative_candidate_latin_rejected":
        errors.append("RABUS_DISPOSITION_INVALID")
    if payload.get("rejection_reasons") != list(REJECTION_REASONS):
        errors.append("RABUS_REJECTION_REASONS_INVALID")
    if payload.get("candidate_score_semantics") != (
        "mean_emitted_top_class_posterior_comparative_score_only"
    ):
        errors.append("RABUS_SCORE_SEMANTICS_INVALID")

    plain_hash_fields = (
        "image_sha256",
        "page_record_sha256",
        "manifest_sha256",
        "geometry_receipt_sha256",
        "geometry_file_sha256",
        "geometry_model_sha256",
        "line_geometry_sha256",
        "crop_sha256",
        "tensor_sha256",
        "preprocessing_sha256",
        "model_sha256",
        "model_record_sha256",
        "model_register_sha256",
        "model_config_sha256",
        "model_config_record_sha256",
        "symbols_sha256",
        "ordered_symbols_sha256",
        "receipt_sha256",
    )
    for field in plain_hash_fields:
        if not _valid_hash(payload.get(field)):
            errors.append(f"RABUS_HASH_INVALID:{field}")
    for field in ("geometry_comparison_id", "line_id", "comparison_id"):
        if not _valid_hash_id(payload.get(field)):
            errors.append(f"RABUS_HASH_ID_INVALID:{field}")

    inventory = payload.get("ordered_symbol_inventory")
    if not isinstance(inventory, list) or len(inventory) != OUTPUT_CLASS_COUNT:
        errors.append("RABUS_SYMBOL_INVENTORY_INVALID")
        inventory = []
    else:
        for class_id, row in enumerate(inventory):
            if not isinstance(row, dict) or row.get("class_id") != class_id:
                errors.append("RABUS_SYMBOL_CLASS_ORDER_INVALID")
                break
            symbol = row.get("symbol")
            if class_id == BLANK_CLASS_ID:
                if symbol is not None:
                    errors.append("RABUS_BLANK_SYMBOL_INVALID")
            elif not isinstance(symbol, str) or symbol == "":
                errors.append(f"RABUS_SYMBOL_INVALID:{class_id}")
        if (
            inventory[2].get("symbol") != "2"
            or inventory[13].get("symbol") != "2"
        ):
            errors.append("RABUS_DUPLICATE_SYMBOL_CLASS_IDS_INVALID")
        if payload.get("ordered_symbols_sha256") != _value_sha256(inventory):
            errors.append("RABUS_ORDERED_SYMBOL_HASH_MISMATCH")
    if payload.get("blank_class_id") != BLANK_CLASS_ID:
        errors.append("RABUS_BLANK_CLASS_INVALID")
    if payload.get("output_class_count") != OUTPUT_CLASS_COUNT:
        errors.append("RABUS_OUTPUT_CLASS_COUNT_INVALID")
    if payload.get("ordered_symbol_count") != OUTPUT_CLASS_COUNT - 1:
        errors.append("RABUS_ORDERED_SYMBOL_COUNT_INVALID")

    tensor_shape = payload.get("tensor_shape")
    output_shape = payload.get("output_shape")
    if (
        not isinstance(tensor_shape, list)
        or len(tensor_shape) != 4
        or tensor_shape[:3] != [1, 1, TARGET_HEIGHT]
        or not isinstance(tensor_shape[3], int)
        or not MIN_WIDTH <= tensor_shape[3] <= MAX_WIDTH
    ):
        errors.append("RABUS_TENSOR_SHAPE_INVALID")
    expected_timesteps = tensor_shape[3] // 8 if isinstance(tensor_shape, list) and len(tensor_shape) == 4 and isinstance(tensor_shape[3], int) else None
    if output_shape != [expected_timesteps, 1, OUTPUT_CLASS_COUNT]:
        errors.append("RABUS_OUTPUT_SHAPE_INVALID")
    preprocessing = payload.get("preprocessing")
    if not isinstance(preprocessing, dict) or payload.get("preprocessing_sha256") != _value_sha256(preprocessing):
        errors.append("RABUS_PREPROCESSING_HASH_MISMATCH")

    lattice = payload.get("ctc_lattice")
    events = payload.get("greedy_class_events")
    if not isinstance(lattice, list) or len(lattice) != expected_timesteps:
        errors.append("RABUS_LATTICE_LENGTH_INVALID")
        lattice = []
    if not isinstance(events, list):
        errors.append("RABUS_GREEDY_EVENTS_INVALID")
        events = []
    symbols_by_id = {
        row.get("class_id"): row.get("symbol")
        for row in inventory
        if isinstance(row, dict)
    }
    expected_events: list[dict[str, Any]] = []
    previous_class: int | None = None
    for timestep, row in enumerate(lattice):
        if not isinstance(row, dict) or row.get("timestep") != timestep:
            errors.append(f"RABUS_LATTICE_TIMESTEP_INVALID:{timestep}")
            continue
        class_id = row.get("top_class_id")
        if not isinstance(class_id, int) or not 0 <= class_id < OUTPUT_CLASS_COUNT:
            errors.append(f"RABUS_LATTICE_CLASS_INVALID:{timestep}")
            continue
        if row.get("top_symbol") != symbols_by_id.get(class_id):
            errors.append(f"RABUS_LATTICE_SYMBOL_JOIN_INVALID:{timestep}")
        for field in ("top_posterior", "blank_posterior"):
            value = row.get(field)
            if not isinstance(value, (int, float)) or not 0.0 <= value <= 1.0:
                errors.append(f"RABUS_LATTICE_POSTERIOR_INVALID:{timestep}:{field}")
        alternatives = row.get("alternatives")
        if not isinstance(alternatives, list) or not alternatives:
            errors.append(f"RABUS_LATTICE_ALTERNATIVES_INVALID:{timestep}")
        else:
            for rank, alternative in enumerate(alternatives):
                if not isinstance(alternative, dict):
                    errors.append(
                        f"RABUS_LATTICE_ALTERNATIVE_MALFORMED:{timestep}:{rank}"
                    )
                    continue
                alternative_class = alternative.get("class_id")
                posterior = alternative.get("posterior")
                if (
                    not isinstance(alternative_class, int)
                    or not 0 <= alternative_class < OUTPUT_CLASS_COUNT
                    or alternative.get("symbol") != symbols_by_id.get(alternative_class)
                    or not isinstance(posterior, (int, float))
                    or not 0.0 <= posterior <= 1.0
                ):
                    errors.append(
                        f"RABUS_LATTICE_ALTERNATIVE_INVALID:{timestep}:{rank}"
                    )
            first = alternatives[0]
            if isinstance(first, dict) and (
                first.get("class_id") != class_id
                or first.get("posterior") != row.get("top_posterior")
            ):
                errors.append(f"RABUS_LATTICE_TOP_ALTERNATIVE_INVALID:{timestep}")
        if class_id != BLANK_CLASS_ID and class_id != previous_class:
            expected_events.append(
                {
                    "event_index": len(expected_events),
                    "timestep": timestep,
                    "class_id": class_id,
                    "symbol": symbols_by_id.get(class_id),
                    "posterior": row.get("top_posterior"),
                    "alternatives": alternatives,
                }
            )
        previous_class = class_id

    if events != expected_events:
        errors.append("RABUS_GREEDY_COLLAPSE_INVALID")

    candidate_parts: list[str] = []
    event_posteriors: list[float] = []
    for event_index, event in enumerate(events):
        if not isinstance(event, dict) or event.get("event_index") != event_index:
            errors.append(f"RABUS_EVENT_INDEX_INVALID:{event_index}")
            continue
        class_id = event.get("class_id")
        symbol = symbols_by_id.get(class_id)
        if not isinstance(class_id, int) or class_id == BLANK_CLASS_ID or event.get("symbol") != symbol:
            errors.append(f"RABUS_EVENT_CLASS_JOIN_INVALID:{event_index}")
            continue
        candidate_parts.append(_candidate_symbol(symbol))
        posterior = event.get("posterior")
        if not isinstance(posterior, (int, float)) or not 0.0 <= posterior <= 1.0:
            errors.append(f"RABUS_EVENT_POSTERIOR_INVALID:{event_index}")
        else:
            event_posteriors.append(float(posterior))
    if payload.get("comparative_candidate_latin") != "".join(candidate_parts):
        errors.append("RABUS_CANDIDATE_EVENT_JOIN_INVALID")
    expected_score = sum(event_posteriors) / len(event_posteriors) if event_posteriors else None
    score = payload.get("comparative_candidate_score")
    if expected_score is None:
        if score is not None:
            errors.append("RABUS_CANDIDATE_SCORE_INVALID")
    elif not isinstance(score, (int, float)) or abs(float(score) - expected_score) > 1e-12:
        errors.append("RABUS_CANDIDATE_SCORE_INVALID")
    return tuple(errors)


def run_rabus_comparison(
    *,
    manifest_path: Path,
    page_id: str,
    geometry_path: Path,
    line_id: str,
    register_path: Path,
    model_id: str,
    repository_root: Path,
    alternative_count: int = 5,
) -> dict[str, Any]:
    """Run the registered CRNN over one exact registered page polygon."""

    repository_root = repository_root.resolve()
    report = validate_model_registry(
        register_path,
        repository_root=repository_root,
        require_cache=True,
    )
    if not report.ok:
        raise ValueError("Model register failed validation: " + ",".join(report.errors))
    register = read_json(register_path)
    model = _registered_model(register, model_id)
    files = _model_files(model, repository_root)

    pages = load_page_manifest(manifest_path)
    page_matches = [page for page in pages if page.page_id == page_id]
    if len(page_matches) != 1:
        raise ValueError(f"Registered page is not unique: {page_id}")
    page = page_matches[0]
    if not page.image_path or not page.image_sha256 or not page.width or not page.height:
        raise ValueError(f"Registered page pixel identity is incomplete: {page_id}")
    image_path = (repository_root / page.image_path).resolve()
    try:
        image_path.relative_to(repository_root)
    except ValueError as error:
        raise ValueError(f"Registered page path leaves repository: {page_id}") from error
    if not image_path.is_file() or sha256_file(image_path) != page.image_sha256:
        raise ValueError(f"Registered page pixel checksum differs: {page_id}")

    geometry_errors = validate_geometry_comparison(geometry_path)
    if geometry_errors:
        raise ValueError("Kraken geometry receipt failed validation: " + ",".join(geometry_errors))
    geometry = read_json(geometry_path)
    if geometry.get("schema") != "zfd.segmentation_comparison.v1":
        raise ValueError("Kraken geometry schema is invalid")
    expected_geometry = {
        "page_id": page.page_id,
        "source_id": page.source_id,
        "image_sha256": page.image_sha256,
        "width": page.width,
        "height": page.height,
        "primary_lane_allowed": False,
        "review_state": "unreviewed",
    }
    for field, expected in expected_geometry.items():
        if geometry.get(field) != expected:
            raise ValueError(f"Kraken geometry differs from registered page at {field}")
    _registered_geometry_model(register, geometry)
    line_matches = [row for row in geometry["lines"] if row.get("line_id") == line_id]
    if len(line_matches) != 1:
        raise ValueError(f"Kraken line geometry is not unique: {line_id}")
    line = line_matches[0]
    boundary = _points(line.get("boundary"), width=page.width, height=page.height)
    baseline = line.get("baseline")
    if not isinstance(baseline, list) or len(baseline) < 2:
        raise ValueError("Kraken line baseline is malformed")
    baseline_points = _points(
        baseline,
        width=page.width,
        height=page.height,
        minimum_points=2,
    )
    if line.get("bbox") != _geometry_bbox(baseline_points, boundary):
        raise ValueError("Kraken line bounding box differs from geometry")
    line_content = {
        "baseline": baseline,
        "boundary": boundary,
        "bbox": line["bbox"],
        "region_ids": line.get("region_ids", []),
    }
    expected_line_id = "sha256:" + _value_sha256(
        {
            "page_id": page.page_id,
            "model_sha256": geometry["model_sha256"],
            **line_content,
        }
    )
    if line_id != expected_line_id:
        raise ValueError("Kraken line ID differs from its exact geometry")

    with Image.open(image_path) as source:
        if source.size != (page.width, page.height):
            raise ValueError(f"Registered page dimensions differ: {page_id}")
        crop, crop_bbox = polygon_mask_crop(source, boundary)
    tensor, preprocessing = preprocess_crop(crop)

    config = read_json(files["model_config.json"])
    if not isinstance(config, dict):
        raise ValueError("Registered Rabus model configuration is malformed")
    _architecture_config(config)
    symbols = load_ordered_symbols(files["symbols.txt"])
    if len(symbols) != OUTPUT_CLASS_COUNT - 1:
        raise ValueError("Registered Rabus symbol count does not match 77 output classes")
    if symbols[1] != "2" or symbols[12] != "2":
        raise ValueError("Registered duplicate symbol class IDs 2 and 13 were not preserved")
    inventory = [{"class_id": 0, "symbol": None}] + [
        {"class_id": class_id, "symbol": symbol}
        for class_id, symbol in enumerate(symbols, start=1)
    ]

    import torch

    model_instance = _load_model(torch, files["best_model.pt"], config)
    input_tensor = torch.from_numpy(tensor).to(device="cpu", dtype=torch.float32)
    with torch.no_grad():
        log_probabilities = model_instance(input_tensor)
    output_shape = [int(value) for value in log_probabilities.shape]
    expected_output = [tensor.shape[3] // 8, 1, OUTPUT_CLASS_COUNT]
    if output_shape != expected_output:
        raise ValueError(
            f"Rabus model output shape differs: {output_shape}; expected {expected_output}"
        )
    probabilities = torch.exp(log_probabilities).detach().cpu().numpy()
    lattice, events, candidate = _ctc_lattice_from_probabilities(
        probabilities[:, 0, :],
        symbols,
        alternative_count=alternative_count,
    )
    candidate_score = (
        sum(float(event["posterior"]) for event in events) / len(events)
        if events
        else None
    )
    return freeze_rabus_comparison(
        page_id=page.page_id,
        source_id=page.source_id,
        image_sha256=page.image_sha256,
        page_record_sha256=_value_sha256(asdict(page)),
        manifest_sha256=sha256_file(manifest_path),
        geometry_comparison_id=geometry["comparison_id"],
        geometry_receipt_sha256=geometry["receipt_sha256"],
        geometry_file_sha256=sha256_file(geometry_path),
        geometry_model_id=geometry["model_id"],
        geometry_model_sha256=geometry["model_sha256"],
        line_id=line_id,
        line_geometry_sha256=_value_sha256(line_content),
        boundary=boundary,
        crop_bbox=crop_bbox,
        crop_sha256=_image_sha256(crop),
        tensor_sha256=_tensor_sha256(tensor),
        tensor_shape=[int(value) for value in tensor.shape],
        preprocessing=preprocessing,
        preprocessing_sha256=_value_sha256(preprocessing),
        model_id=model["model_id"],
        model_sha256=next(
            row["sha256"] for row in model["files"] if row["name"] == "best_model.pt"
        ),
        model_record_sha256=_value_sha256(model),
        model_register_sha256=sha256_file(register_path),
        model_revision=model["pinned_revision"],
        model_config_sha256=sha256_file(files["model_config.json"]),
        model_config_record_sha256=_value_sha256(config),
        symbols_sha256=sha256_file(files["symbols.txt"]),
        ordered_symbols_sha256=_value_sha256(inventory),
        ordered_symbols=symbols,
        software_runtime_version=str(torch.__version__),
        output_shape=output_shape,
        lattice=lattice,
        greedy_events=events,
        comparative_candidate_latin=candidate,
        comparative_candidate_score=candidate_score,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m zfd_image_native.rabus_compare")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--page-id", required=True)
    parser.add_argument("--geometry", required=True, type=Path)
    parser.add_argument("--line-id", required=True)
    parser.add_argument("--model-register", required=True, type=Path)
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    parser.add_argument("--alternatives", type=int, default=5)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = run_rabus_comparison(
            manifest_path=args.manifest,
            page_id=args.page_id,
            geometry_path=args.geometry,
            line_id=args.line_id,
            register_path=args.model_register,
            model_id=args.model_id,
            repository_root=args.repository_root,
            alternative_count=args.alternatives,
        )
        write_json(args.output, result)
        errors = validate_rabus_comparison(args.output)
        if errors:
            raise ValueError("Saved Rabus comparison failed validation: " + ",".join(errors))
        print(
            canonical_json(
                {
                    "comparison_id": result["comparison_id"],
                    "page_id": result["page_id"],
                    "line_id": result["line_id"],
                    "timesteps": len(result["ctc_lattice"]),
                    "events": len(result["greedy_class_events"]),
                    "acceptance_state": result["acceptance_state"],
                    "primary_lane_allowed": result["primary_lane_allowed"],
                    "metrics_status": result["metrics_status"],
                    "output": str(args.output),
                }
            )
        )
        return 0
    except (OSError, RuntimeError, ValueError) as error:
        print(f"ERROR: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
