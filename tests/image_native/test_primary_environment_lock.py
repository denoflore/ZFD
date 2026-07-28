"""The primary Windows environment is a complete exact dependency lock."""

from __future__ import annotations

from pathlib import Path


LOCK = Path("requirements-image-native.txt")


def test_primary_environment_is_fully_pinned() -> None:
    lines = [
        line.strip()
        for line in LOCK.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    packages = {line.split("==", 1)[0].lower(): line for line in lines}

    assert lines
    assert all(line.count("==") == 1 for line in lines)
    assert len(packages) == len(lines)
    assert packages == {
        "colorama": "colorama==0.4.6",
        "iniconfig": "iniconfig==2.3.0",
        "numpy": "numpy==2.5.0",
        "opencv-python": "opencv-python==4.13.0.92",
        "packaging": "packaging==26.2",
        "pillow": "Pillow==12.2.0",
        "pluggy": "pluggy==1.6.0",
        "pygments": "Pygments==2.20.0",
        "pytest": "pytest==9.1.1",
    }
