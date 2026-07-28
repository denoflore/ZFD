"""The external comparison environment is exact and separate from primary OCR."""

from __future__ import annotations

from pathlib import Path


LOCK = Path("requirements-kraken-comparison.txt")


def test_kraken_comparison_environment_is_fully_pinned() -> None:
    lines = [
        line.strip()
        for line in LOCK.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    packages = {line.split("==", 1)[0].lower(): line for line in lines}

    assert lines
    assert all(line.count("==") == 1 for line in lines)
    assert len(packages) == len(lines)
    assert "zfd-image-native" not in packages
    assert packages["kraken"] == "kraken==6.0.0"
    assert packages["torch"] == "torch==2.7.1"
    assert packages["numpy"] == "numpy==2.0.2"
    assert packages["shapely"] == "shapely==2.0.7"
    assert packages["pillow"] == "pillow==12.3.0"
