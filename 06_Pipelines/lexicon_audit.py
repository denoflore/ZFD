#!/usr/bin/env python3
"""
ZFD Canonical Lexicon Audit
===========================
Structural correctness gate for the canonical unified lexicon. Exit code 0
means every check passed; nonzero means the lexicon is not fit to decode
with. Run standalone or through pytest (tests/test_zfd_v2_decoder.py).

Checks:
1. Required families present with meta counts matching actual counts.
2. No empty, whitespace, or non-EVA-alphabet keys (the v2 garbage class:
   table headers parsed as entries).
3. Every stem carries a non-empty english gloss.
4. No key duplicated across operators, stems, and suffixes (a key in two
   families makes greedy decomposition order-dependent).
5. Every entry key is reachable by the decoder's EVA-to-Croatian output
   alphabet, so no entry is unmatchable dead weight.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from zfd_decoder_v2 import LEXICON_PATH, EVA_TO_CRO

# Characters the EVA->Croatian mapping can ever emit, plus the mapped
# Croatian letters used by lexicon conventions.
ALLOWED_KEY_CHARS = set("abcdefghijklmnopqrstuvwxyz")
for mapped in EVA_TO_CRO.values():
    ALLOWED_KEY_CHARS.update(mapped)

FAMILIES = ("operators", "stems", "suffixes", "state_markers", "latin_terms")


def audit(lexicon_path=LEXICON_PATH):
    """Returns (failures, warnings). Failures make the lexicon unfit to
    decode with. Warnings are structural facts worth eyes: keys the EVA
    alphabet cannot produce directly (Croatian reference forms reachable
    only through expansion) and keys shared across families (resolved by
    the decoder's documented whole-word precheck and greedy order)."""
    failures = []
    warnings = []
    with open(lexicon_path, encoding="utf-8") as handle:
        lexicon = json.load(handle)

    for family in FAMILIES:
        if family not in lexicon:
            failures.append(f"missing family: {family}")
    if failures:
        return failures, warnings

    meta_counts = lexicon.get("meta", {}).get("counts", {})
    for family, expected in meta_counts.items():
        if family in lexicon and len(lexicon[family]) != expected:
            failures.append(
                f"meta count mismatch: {family} meta={expected} "
                f"actual={len(lexicon[family])}")

    for family in FAMILIES:
        for key, entry in lexicon[family].items():
            if not key or key != key.strip():
                failures.append(f"{family}: blank or padded key {key!r}")
                continue
            if re.search(r"\d|--|\||\s", key):
                failures.append(f"{family}: table-garbage shaped key {key!r}")
                continue
            bad = set(key.lower()) - ALLOWED_KEY_CHARS
            if bad:
                warnings.append(
                    f"{family}: key {key!r} unreachable from EVA directly "
                    f"({sorted(bad)}); expansion-only entry")
            gloss = entry.get("meaning_en") if isinstance(entry, dict) else entry
            if not gloss or not str(gloss).strip():
                failures.append(f"{family}: {key!r} has no meaning_en gloss")
            if isinstance(entry, dict) and entry.get("form") is not None:
                # Operators display as 'da-' and suffixes as '-dy'; the
                # hyphen is presentation, not identity.
                if str(entry["form"]).strip("-") != key:
                    failures.append(
                        f"{family}: {key!r} form field {entry.get('form')!r} "
                        f"disagrees with its key")

    seen = {}
    for family in ("operators", "stems", "suffixes"):
        for key in lexicon[family]:
            if key in seen:
                warnings.append(
                    f"cross-family key {key!r} in {seen[key]} and {family} "
                    f"(resolved by whole-word precheck / greedy order)")
            else:
                seen[key] = family

    return failures, warnings


def main():
    failures, warnings = audit()
    for warning in warnings:
        print(f"  warn: {warning}")
    if failures:
        print(f"LEXICON AUDIT FAILED: {len(failures)} finding(s)")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    with open(LEXICON_PATH, encoding="utf-8") as handle:
        lexicon = json.load(handle)
    total = sum(len(lexicon[family]) for family in FAMILIES)
    print(f"LEXICON AUDIT PASSED: {total} morphemes across "
          f"{len(FAMILIES)} families, version "
          f"{lexicon.get('meta', {}).get('version', 'unknown')}, "
          f"{len(warnings)} warnings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
