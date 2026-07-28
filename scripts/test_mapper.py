#!/usr/bin/env python3
"""Deterministic process-level checks for the legacy mapper."""

from __future__ import annotations

import os
import sys

from zfd_mapper import convert_folio, map_eva_to_croatian, map_line


EXTENDED_TESTS = [
    ("qokeedy", "kostedi"),
    ("chedy", "hedi"),
    ("shedy", "šedi"),
    ("kol", "stol"),
    ("tor", "tror"),
    ("for", "pror"),
    ("pol", "plol"),
    ("qo", "ko"),
    ("qol", "kol"),
    ("qokal", "kostal"),
    ("cheey", "hei"),
    ("daiin", "dain"),
    ("aiin", "ain"),
    ("ochar", "ohar"),
    ("oshar", "ošar"),
    ("ockhy", "ocsthi"),
    ("octol", "octrol"),
    ("shey", "šei"),
    ("chody", "hodi"),
    ("qockhey", "kocsthei"),
    ("sholfchor", "šolprhor"),
    ("cthol", "ctrhol"),
    ("dar", "dar"),
    ("sal", "sal"),
    ("sam", "sam"),
]


def _status(ok: bool, detail: str) -> bool:
    safe_detail = detail.encode("ascii", "backslashreplace").decode("ascii")
    print(f"[{'PASS' if ok else 'FAIL'}] {safe_detail}")
    return ok


def check_word_mapping() -> bool:
    passed = True
    for source, expected in EXTENDED_TESTS:
        actual = map_eva_to_croatian(source)
        passed &= _status(actual == expected, f"word {source}: {actual!r} expected {expected!r}")
    return passed


def check_line_mapping() -> bool:
    fixtures = [
        ("daiin.chol.dar", "dain hol dar"),
        ("qokeedy.shedy.ol", "kostedi šedi ol"),
        ("sal.sheom.kol", "sal šeom stol"),
    ]
    return all(_status(map_line(source) == expected, f"line {source}") for source, expected in fixtures)


def check_folio_conversion() -> bool:
    result = convert_folio(
        {
            "labels": ["otorchety", "oral", "oldar"],
            "text": ["daiin.chol.dar", "qokeedy.shedy"],
        }
    )
    ok = len(result["labels"]) == 3 and len(result["text"]) == 2 and "dain" in result["text"][0]
    return _status(ok, "folio structure")


def check_croatian_patterns() -> bool:
    words = ["qokeedy", "qokeey", "qokain", "qokedy", "qoky"]
    outcomes = [(word, "kost" in map_eva_to_croatian(word)) for word in words]
    if os.environ.get("ZFD_MAPPER_FORCE_PATTERN_FAILURE") == "1":
        outcomes[0] = (outcomes[0][0], False)
    return all(_status(ok, f"pattern {word} contains kost") for word, ok in outcomes)


def test_word_mapping() -> None:
    assert check_word_mapping()


def test_line_mapping() -> None:
    assert check_line_mapping()


def test_folio_conversion() -> None:
    assert check_folio_conversion()


def test_croatian_patterns() -> None:
    assert check_croatian_patterns()


def main() -> int:
    print("ZFD MAPPER PROCESS TESTS")
    passed = all(
        [
            check_word_mapping(),
            check_line_mapping(),
            check_folio_conversion(),
            check_croatian_patterns(),
        ]
    )
    print("[PASS] all mapper checks" if passed else "[FAIL] mapper checks failed")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
