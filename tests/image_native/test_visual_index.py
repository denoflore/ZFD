"""Stage B indexes registered pixels without claiming grapheme identity."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
import shutil

from PIL import Image, ImageDraw
import pytest

from zfd_image_native.boundary import scan_primary_lane
from zfd_image_native.io import canonical_json, read_json, sha256_file, write_json, write_jsonl
from zfd_image_native.models import PageRecord
from zfd_image_native.ocr import OpenSetConfig
from zfd_image_native.receipts import freeze_stage_a_receipts
from zfd_image_native.receipts import _implementation_sha256 as stage_a_implementation_sha256
from zfd_visual_index.cli import main as visual_index_main
from zfd_visual_index import (
    VisualIndexConfig,
    descriptor_distance,
    index_page_candidates,
    open_frozen_stage_a_run,
    resolve_visual_index_output,
    validate_page_local_visual_index,
    validate_stage_a_geometry_graph,
)


ROOT = Path(__file__).resolve().parents[2]
RECEIPT_FILES = (
    "corpus_stage_a_summary.json",
    "ocr_page_receipts.jsonl",
    "ocr_run_receipt.json",
    "page_parity.jsonl",
    "region_parity.jsonl",
    "voynich_pages.jsonl",
    "voynich_regions.jsonl",
)


@dataclass(frozen=True)
class _Fixture:
    repository_root: Path
    manifest_path: Path
    stage_a_root: Path
    authority_root: Path
    page_id: str

    def open(self):
        return open_frozen_stage_a_run(
            self.stage_a_root,
            authority_root=self.authority_root,
            repository_root=self.repository_root,
            manifest_path=self.manifest_path,
        )


def _polygon(box: tuple[int, int, int, int]) -> list[list[int]]:
    x, y, width, height = box
    return [[x, y], [x + width, y], [x + width, y + height], [x, y + height]]


def _inventory(stage_a_root: Path) -> tuple[int, int, str]:
    rows: list[str] = []
    total = 0
    for subdir in ("corpus", "receipts"):
        for path in sorted((stage_a_root / subdir).rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(stage_a_root).as_posix()
            length = path.stat().st_size
            total += length
            rows.append(f"{relative}|{length}|{sha256_file(path)}")
    digest = sha256(("\n".join(rows) + "\n").encode("utf-8")).hexdigest()
    return len(rows), total, digest


def _rehash_receipt(receipt: dict) -> dict:
    payload = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    receipt["receipt_sha256"] = sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    return receipt


def _stage_a_fixture(tmp_path: Path, *, reverse_graphemes: bool = False) -> _Fixture:
    root = tmp_path / "repo"
    image_path = root / "build" / "image_native" / "sources" / "yale-ms-408" / "fixture.png"
    image_path.parent.mkdir(parents=True)
    image = Image.new("RGB", (160, 60), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((10, 10, 21, 39), fill="black")
    draw.rectangle((50, 10, 61, 39), fill="black")
    draw.rectangle((90, 20, 121, 27), fill="black")
    image.save(image_path)
    page = PageRecord(
        page_id="yale-ms-408:iiif:fixture",
        source_id="yale-ms-408",
        surface_label="fixture",
        iiif_id="fixture",
        iiif_base_uri="https://example.invalid/iiif/2/fixture",
        image_request_uri="https://example.invalid/iiif/2/fixture/full/max/0/default.png",
        image_sha256=sha256_file(image_path),
        image_path=str(image_path),
        width=160,
        height=60,
        mime_type="image/png",
        acquisition_status="verified",
    )
    manifest = root / "data" / "image_native" / "voynich_pages.jsonl"
    write_jsonl(manifest, [page])
    stage_root = root / "evidence" / "stage-a"
    corpus_root = stage_root / "corpus"
    region_id = f"{page.page_id}:region:0001"
    line_id = f"{page.page_id}:line:0001"
    boxes = ((10, 10, 12, 30), (50, 10, 12, 30), (90, 20, 32, 8))
    grapheme_ids = tuple(f"{page.page_id}:grapheme:{index:06d}" for index in range(1, 4))
    region = {
        "region_id": region_id,
        "bbox": [8, 8, 118, 34],
        "polygon": _polygon((8, 8, 118, 34)),
        "line_ids": [line_id],
    }
    graphemes = [
        {
            "grapheme_id": grapheme_id,
            "line_id": line_id,
            "region_id": region_id,
            "bbox": list(box),
            "polygon": _polygon(box),
            "visual_fingerprint": str(index) * 64,
            "alternatives": [
                {
                    "candidate_id": f"visual:fixture:{index}",
                    "score": 0.0,
                    "candidate_type": "visual_cluster",
                }
            ],
            "unknown_score": 1.0,
            "recognition_confidence": 0.0,
            "diplomatic_label": None,
        }
        for index, (grapheme_id, box) in enumerate(zip(grapheme_ids, boxes), start=1)
    ]
    if reverse_graphemes:
        graphemes.reverse()
    config_hash = sha256(canonical_json(asdict(OpenSetConfig())).encode("utf-8")).hexdigest()
    stage = {
        "page_id": page.page_id,
        "source_id": page.source_id,
        "page_sha256": page.image_sha256,
        "width": page.width,
        "height": page.height,
        "config_sha256": config_hash,
        "disposition": "segmented_unrecognized_layout_review",
        "layout_disposition": "layout_review_required",
        "regions": [region],
        "lines": [
            {
                "line_id": line_id,
                "region_id": region_id,
                "bbox": [8, 8, 118, 34],
                "polygon": _polygon((8, 8, 118, 34)),
                "grapheme_ids": [row["grapheme_id"] for row in graphemes],
                "geometry_mode": "cartesian_fragment",
                "maximum_gap_heights": 3.0,
                "ink_density": 0.25,
            }
        ],
        "graphemes": graphemes,
        "rejected_components": [
            {
                "component_id": f"{page.page_id}:component-rejection:000001",
                "bbox": [130, 10, 5, 5],
                "polygon": _polygon((130, 10, 5, 5)),
                "reason": "unassigned_after_cartesian_continuity_and_density_gates",
            }
        ],
    }
    write_json(corpus_root / "pages" / "fixture.json", stage)
    write_jsonl(
        corpus_root / "regions.jsonl",
        [{**region, "page_id": page.page_id, "image_sha256": page.image_sha256, "ocr_record": "pages/fixture.json"}],
    )
    write_jsonl(
        corpus_root / "page_dispositions.jsonl",
        [{"page_id": page.page_id, "disposition": stage["disposition"]}],
    )
    receipts_root = stage_root / "receipts"
    freeze_stage_a_receipts(manifest, corpus_root, receipts_root, repository_root=root)
    file_count, byte_count, inventory_sha256 = _inventory(stage_root)
    run = read_json(receipts_root / "ocr_run_receipt.json")
    preservation = {
        "schema": "zfd.local_preservation.v1",
        "receipt_schema_version": run["schema_version"],
        "inventory_format": "all files below corpus/ and receipts/, relative POSIX path|byte_length|lowercase_sha256, UTF-8, LF, sorted by relative path, terminal LF",
        "file_count": file_count,
        "byte_count": byte_count,
        "inventory_sha256": inventory_sha256,
        "run_id": run["run_id"],
        "run_receipt_sha256": run["receipt_sha256"],
        "manifest_sha256": run["acquired_manifest_sha256"],
        "implementation_sha256": run["implementation_sha256"],
        "structural_integrity_ok": True,
        "artifact_integrity_ok": True,
    }
    write_json(stage_root / "preservation_receipt.json", preservation)
    authority_root = root / "data" / "image_native" / "stage-a-authority"
    authority_root.mkdir(parents=True)
    for name in RECEIPT_FILES:
        shutil.copyfile(receipts_root / name, authority_root / name)
    shutil.copyfile(stage_root / "preservation_receipt.json", authority_root / "preservation_receipt.json")
    return _Fixture(root, manifest, stage_root, authority_root, page.page_id)


def test_registered_pixels_build_page_local_visual_index_without_identity_claim(
    tmp_path: Path,
) -> None:
    fixture = _stage_a_fixture(tmp_path)
    run = fixture.open()

    receipt = index_page_candidates(run.page(fixture.page_id))

    assert receipt.schema == "zfd.page_local_visual_index.v1"
    assert receipt.candidate_count == 3
    assert receipt.page_local_exemplar_count == 2
    first, second, third = receipt.candidates
    assert first.assigned_page_local_exemplar_id == second.assigned_page_local_exemplar_id
    assert first.descriptor_sha256 == second.descriptor_sha256
    assert third.assigned_page_local_exemplar_id != first.assigned_page_local_exemplar_id
    assert {first.page_local_exemplar_relationship, second.page_local_exemplar_relationship} == {
        "self",
        "assigned_exemplar",
    }
    assert all(candidate.diplomatic_label is None for candidate in receipt.candidates)
    assert all(candidate.unknown_score is None for candidate in receipt.candidates)
    assert all(candidate.recognition_confidence is None for candidate in receipt.candidates)
    assert all(
        candidate.decision == "identity_withheld_no_adjudicated_authority"
        for candidate in receipt.candidates
    )
    assert receipt.identity_recognition_status == "not_run_no_adjudicated_registry"
    assert receipt.semantic_class_authority_count == 0
    assert receipt.accuracy_claim_allowed is False
    assert receipt.confirmed_translated is False
    assert receipt.dependency_identity["opencv_python"] == "4.13.0.92"
    assert receipt.dependency_identity["opencv_runtime"] == "4.13.0"
    assert receipt.stage_a_authority["retained_grapheme_count"] == 3
    assert receipt.stage_a_authority["rejected_component_count"] == 1
    assert receipt.stage_a_authority["component_candidate_count"] == 4


def test_visual_neighbours_exclude_self_and_record_distance_components(tmp_path: Path) -> None:
    fixture = _stage_a_fixture(tmp_path)
    receipt = index_page_candidates(fixture.open().page(fixture.page_id))

    for candidate in receipt.candidates:
        assert all(
            neighbour.page_local_exemplar_id != candidate.assigned_page_local_exemplar_id
            for neighbour in candidate.visual_neighbours
        )
        assignment = candidate.assignment_distance
        assert assignment.descriptor_distance == round(
            min(1.0, assignment.bitmap_hamming_fraction + assignment.aspect_ratio_penalty), 8
        )
        assert assignment.descriptor_bit_count == 256


def test_cached_integer_distance_matches_exact_hamming_and_aspect_components() -> None:
    result = descriptor_distance("0f" * 32, 2.0, "f0" * 32, 1.0, descriptor_size=16)

    assert result.bitmap_hamming_count == 256
    assert result.bitmap_hamming_fraction == 1.0
    assert result.aspect_log_ratio_abs > 0.0
    assert result.aspect_ratio_penalty > 0.0
    assert result.descriptor_distance == 1.0


def test_visual_index_config_rejects_an_unregistered_descriptor_bit_count() -> None:
    with pytest.raises(ValueError, match="registered 256 bit metric"):
        VisualIndexConfig(descriptor_size=8)
    with pytest.raises(ValueError, match="registered 256 bit metric"):
        descriptor_distance("00" * 8, 1.0, "ff" * 8, 1.0, descriptor_size=8)
    for invalid_aspect in (float("nan"), float("inf"), 0.0):
        with pytest.raises(ValueError, match="finite and positive"):
            descriptor_distance("00" * 32, invalid_aspect, "ff" * 32, 1.0)


def test_stage_a_authority_rejects_artifact_or_receipt_substitution(tmp_path: Path) -> None:
    fixture = _stage_a_fixture(tmp_path)
    stage_path = fixture.stage_a_root / "corpus" / "pages" / "fixture.json"
    stage = read_json(stage_path)
    stage["graphemes"][0]["bbox"][0] += 1
    write_json(stage_path, stage)

    with pytest.raises(ValueError, match="STAGE_A_INVENTORY_SHA256_MISMATCH"):
        fixture.open()

    fixture = _stage_a_fixture(tmp_path / "second")
    receipt_file = fixture.stage_a_root / "receipts" / "ocr_page_receipts.jsonl"
    receipt_file.write_text(receipt_file.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="STAGE_A_RECEIPT_AUTHORITY_MISMATCH"):
        fixture.open()


def test_geometry_graph_rejects_duplicate_missing_and_reparented_edges(tmp_path: Path) -> None:
    fixture = _stage_a_fixture(tmp_path)
    payload = read_json(fixture.stage_a_root / "corpus" / "pages" / "fixture.json")

    duplicate = {**payload, "graphemes": [*payload["graphemes"], payload["graphemes"][0]]}
    with pytest.raises(ValueError, match="STAGE_A_GRAPHEME_ID_DUPLICATE"):
        validate_stage_a_geometry_graph(duplicate, width=160, height=60)

    missing_edge = read_json(fixture.stage_a_root / "corpus" / "pages" / "fixture.json")
    missing_edge["lines"][0]["grapheme_ids"].pop()
    with pytest.raises(ValueError, match="STAGE_A_LINE_GRAPHEME_SET_MISMATCH"):
        validate_stage_a_geometry_graph(missing_edge, width=160, height=60)

    outside = read_json(fixture.stage_a_root / "corpus" / "pages" / "fixture.json")
    outside["graphemes"][0]["bbox"] = [140, 40, 10, 10]
    outside["graphemes"][0]["polygon"] = _polygon((140, 40, 10, 10))
    with pytest.raises(ValueError, match="STAGE_A_GRAPHEME_OUTSIDE_LINE"):
        validate_stage_a_geometry_graph(outside, width=160, height=60)

    split_geometry = read_json(fixture.stage_a_root / "corpus" / "pages" / "fixture.json")
    split_geometry["graphemes"][0]["polygon"] = _polygon((30, 10, 12, 30))
    with pytest.raises(ValueError, match="STAGE_A_GRAPHEME_POLYGON_BBOX_MISMATCH"):
        validate_stage_a_geometry_graph(split_geometry, width=160, height=60)


def test_canonical_grouping_projection_is_stable_under_stage_row_permutation(
    tmp_path: Path,
) -> None:
    normal = _stage_a_fixture(tmp_path / "normal")
    reverse = _stage_a_fixture(tmp_path / "reverse", reverse_graphemes=True)

    first = index_page_candidates(normal.open().page(normal.page_id))
    second = index_page_candidates(reverse.open().page(reverse.page_id))
    first_projection = sorted(
        (row.descriptor_sha256, row.occurrence_count) for row in first.page_local_visual_exemplars
    )
    second_projection = sorted(
        (row.descriptor_sha256, row.occurrence_count) for row in second.page_local_visual_exemplars
    )

    assert first_projection == second_projection


def test_visual_index_receipt_recomputes_and_rejects_semantic_tampering(tmp_path: Path) -> None:
    fixture = _stage_a_fixture(tmp_path)
    run = fixture.open()
    receipt = index_page_candidates(run.page(fixture.page_id))

    assert validate_page_local_visual_index(asdict(receipt), run) == ()
    tampered = asdict(receipt)
    tampered["candidates"][0]["diplomatic_label"] = "invented"
    errors = validate_page_local_visual_index(tampered, run)
    assert "CANDIDATE_SEMANTIC_AUTHORITY_FORBIDDEN" in errors
    assert "RECEIPT_HASH_MISMATCH" in errors

    provenance_tampered = asdict(receipt)
    provenance_tampered["implementation_git_commit"] = "0" * 40
    provenance_tampered["action_identity"] = ["invented", "action"]
    errors = validate_page_local_visual_index(_rehash_receipt(provenance_tampered), run)
    assert "VISUAL_INDEX_RECOMPUTE_MISMATCH" in errors

    malformed = asdict(receipt)
    malformed["candidates"] = None
    errors = validate_page_local_visual_index(_rehash_receipt(malformed), run)
    assert "CANDIDATE_COLLECTION_MALFORMED" in errors


def test_visual_index_output_cannot_overlap_frozen_stage_a(tmp_path: Path) -> None:
    fixture = _stage_a_fixture(tmp_path)
    run = fixture.open()

    with pytest.raises(ValueError, match="OUTPUT_OVERLAPS_STAGE_A_AUTHORITY"):
        resolve_visual_index_output(run.stage_a_root / "corpus" / "index.json", run)
    for protected in (
        run.stage_a_root / "preservation_receipt.json",
        run.manifest_path,
        run.page(fixture.page_id).image_path,
    ):
        with pytest.raises(ValueError, match="OUTPUT_OVERLAPS_STAGE_A_AUTHORITY"):
            resolve_visual_index_output(protected, run)
    target = fixture.repository_root / "build" / "visual-index" / "fixture.json"
    assert resolve_visual_index_output(target, run) == target.resolve()


def test_validate_page_cli_rejects_a_different_page_argument(tmp_path: Path, capsys) -> None:
    fixture = _stage_a_fixture(tmp_path)
    receipt_path = fixture.repository_root / "build" / "visual-index" / "fixture.json"
    write_json(receipt_path, index_page_candidates(fixture.open().page(fixture.page_id)))

    exit_code = visual_index_main(
        [
            "validate-page",
            "--repository-root",
            str(fixture.repository_root),
            "--manifest",
            str(fixture.manifest_path),
            "--stage-a-root",
            str(fixture.stage_a_root),
            "--authority-root",
            str(fixture.authority_root),
            "--page-id",
            "wrong-page-id",
            "--receipt",
            str(receipt_path),
        ]
    )

    assert exit_code == 1
    assert "PAGE_ID_ARGUMENT_RECEIPT_MISMATCH" in capsys.readouterr().out


def test_stage_b_package_does_not_stale_stage_a_implementation_receipt() -> None:
    run = read_json(ROOT / "data" / "image_native" / "receipts-v2b" / "ocr_run_receipt.json")

    assert stage_a_implementation_sha256() == run["implementation_sha256"]


def test_visual_index_primary_lane_has_no_inherited_text_dependency() -> None:
    hits = scan_primary_lane(
        ROOT / "zfd_visual_index",
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
        include={"__init__.py", "__main__.py", "authority.py", "core.py", "cli.py", "stage_a.py"},
    )
    assert hits == []
