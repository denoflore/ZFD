"""Public commands and corpus counts must stay bound to checked receipts."""

from __future__ import annotations

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_byte_hash_authorities_have_platform_stable_line_endings() -> None:
    attributes = set(_read(".gitattributes").splitlines())
    assert "*.py text eol=lf" in attributes
    assert "*.jsonl text eol=lf" in attributes


def test_windows_commands_pin_the_interpreter_and_bootstrap() -> None:
    readme = _read("README.md")
    guide = _read("docs/IMAGE_NATIVE_OCR.md")
    for document in (readme, guide):
        assert ".venv\\Scripts\\python -m pip install pip==26.1.2" in document
        assert ".venv\\Scripts\\python -m pytest -q -p no:cacheprovider" in document
        assert re.search(r"(?m)^python -m zfd_image_native", document) is None


def test_freeze_examples_preserve_v1_and_write_explicit_v2_build_receipts() -> None:
    for relative in ("README.md", "docs/IMAGE_NATIVE_OCR.md"):
        document = _read(relative)
        match = re.search(r"freeze-receipts `.*?```", document, flags=re.DOTALL)
        assert match is not None
        block = match.group(0)
        assert "--output build\\image_native\\receipts-v2 `" in block
        assert "--receipts build\\image_native\\receipts-v2 `" in block
        assert "--corpus build\\image_native\\corpus `" in block
        assert "--manifest build\\image_native\\voynich_pages.acquired.jsonl `" in block
        assert "--output data\\image_native `" not in block


def test_model_acquisition_command_precedes_explicit_cache_validation() -> None:
    for relative in ("README.md", "docs/IMAGE_NATIVE_OCR.md"):
        document = _read(relative)
        acquire_index = document.index(
            ".venv\\Scripts\\python -m zfd_image_native acquire-models `"
        )
        validate_index = document.index(
            ".venv\\Scripts\\python -m zfd_image_native validate-models `"
        )
        assert acquire_index < validate_index
        assert "--require-cache" in document[validate_index:]


def test_kraken_comparison_has_a_separate_reproducible_environment() -> None:
    guide = _read("docs/IMAGE_NATIVE_OCR.md")
    assert "uv venv --python 3.11.15 .venv-kraken" in guide
    assert "requirements-kraken-comparison.txt" in guide
    assert ".venv-kraken\\Scripts\\python -m zfd_image_native.kraken_compare" in guide
    assert "primary_lane_allowed" in guide
    assert "not_measured" in guide


def test_comparative_counts_match_the_committed_ledger() -> None:
    readme = _read("README.md")
    status = _read("docs/PROVENANCE_STATUS.md")
    guide = _read("docs/IMAGE_NATIVE_OCR.md")
    summary = json.loads(_read("data/image_native/comparative_asset_summary.json"))
    receipt_counts = (
        f"{summary['asset_count']:,}",
        f"{summary['unique_content_count']:,}",
        f"{summary['mapped_canvas_count']:,}",
    )

    for document in (readme, status, guide):
        assert all(count in document for count in receipt_counts)
        assert "Mavrov" in document
        assert "Zero" in document and "training ready" in document
    assert f"across {summary['source_count']} collections" in readme
    assert summary["training_ready_asset_count"] == 0
    assert "GAMS Zrcalo" in readme
    assert "There is no verified shorthand corpus" in readme
    assert "--source-id nsk-mavrov-r7822" in guide


def test_corpus_parity_command_documents_safe_unresolved_authority() -> None:
    readme = _read("README.md")
    guide = _read("docs/IMAGE_NATIVE_OCR.md")
    parity = _read("docs/CORPUS_PARITY.md")

    for document in (readme, guide, parity):
        assert "zfd-parity" in document
        assert "PARITY_PROMOTION_AUTHORITY_UNPINNED" in document
    assert "build-parity-corpus" in guide
    assert "validate-parity-corpus" in guide
    assert "CURRENT_IMPLEMENTATION_MISMATCH" in guide
    assert "exactly six files" in parity
    assert "completion_claim_allowed=false" in parity
