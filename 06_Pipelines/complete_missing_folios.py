#!/usr/bin/env python3
"""
ZFD Missing Loci Completion
===========================
Completes manuscript translation coverage for the 43 loci the folio pipeline
skipped: multi-panel foldouts (f67-f72 astronomical, f85-f86 rosettes,
f89/f90/f95/f102 pharmaceutical foldouts) and f116v (the final page).

Sources EVA locally from 02_Transcriptions/LSI_ivtff_0d.txt (no network,
no OCR). Decodes through the same frozen ZFD v2 decoder and unified lexicon
v3 as the existing 201 folios, and emits the same recipe markdown format
into translations/recipes/.

Usage:
    python complete_missing_folios.py           # decode all missing loci
    python complete_missing_folios.py --list    # list missing loci only
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import zfd_decoder_v2
import process_all_folios as paf
from zfd_decoder_v2 import ZFDDecoder

REPO_ROOT = Path(__file__).parent.parent
LSI_PATH = REPO_ROOT / "02_Transcriptions" / "LSI_ivtff_0d.txt"
LEXICON_PATH = REPO_ROOT / "08_Final_Proofs" / "Master_Key" / "unified_lexicon_v3.json"
IIIF_MAP_PATH = REPO_ROOT / "folio_iiif_map.json"
RECIPES_DIR = REPO_ROOT / "translations" / "recipes"
SUMMARY_PATH = REPO_ROOT / "translations" / "MISSING_LOCI_COMPLETION.json"

# Transcriber preference: Takahashi first, then the LSI consensus order.
TRANSCRIBER_PREFERENCE = ["H", "C", "F", "U", "D", "G", "J", "L", "M", "V", "X", "Z"]

LOCUS_LINE = re.compile(r"^<(f\d+[rv]\d*)\.([^;>]+);(\w)>\s*(.*)$")
PAGE_LINE = re.compile(r"^<(f\d+[rv]\d*)>")
INLINE_TAG = re.compile(r"<[^>]*>")


def existing_locus_ids():
    return {p.name[: -len("_recipe.md")] for p in RECIPES_DIR.glob("f*_recipe.md")}


def parse_lsi():
    """Parse the LSI IVTFF file into {locus: {line_id: {transcriber: text}}}."""
    pages = defaultdict(lambda: defaultdict(dict))
    with open(LSI_PATH, encoding="utf-8", errors="replace") as handle:
        for raw in handle:
            match = LOCUS_LINE.match(raw.strip())
            if not match:
                continue
            locus, line_id, transcriber, text = match.groups()
            pages[locus][line_id][transcriber] = text.strip()
    return pages


def clean_eva(text):
    """IVTFF cleanup: drop inline tags and fillers, normalize separators."""
    text = INLINE_TAG.sub("", text)
    text = text.replace("!", "").replace("%", "")
    # Uncertain space and hard space both become word separators.
    text = text.replace(",", ".")
    text = re.sub(r"\.+", ".", text)
    return text.strip(". ")


def eva_text_for(locus, page_lines):
    """One EVA line per manuscript line, preferred transcriber per line."""
    lines = []
    for line_id in page_lines:
        by_transcriber = page_lines[line_id]
        chosen = None
        for transcriber in TRANSCRIBER_PREFERENCE:
            if transcriber in by_transcriber:
                chosen = by_transcriber[transcriber]
                break
        if chosen is None:
            chosen = next(iter(by_transcriber.values()))
        cleaned = clean_eva(chosen)
        if cleaned:
            lines.append(cleaned)
    return "\n".join(lines)


def main():
    pages = parse_lsi()
    done = existing_locus_ids()
    missing = sorted(
        (locus for locus in pages if locus not in done),
        key=lambda f: (int(re.match(r"f(\d+)", f).group(1)), f),
    )
    print(f"LSI loci: {len(pages)}  existing recipes: {len(done)}  missing: {len(missing)}")
    if "--list" in sys.argv:
        for locus in missing:
            print(locus)
        return

    iiif_map = json.loads(IIIF_MAP_PATH.read_text()) if IIIF_MAP_PATH.exists() else {}
    decoder = ZFDDecoder(lexicon_path=str(LEXICON_PATH))

    summary = {"completed": {}, "skipped": []}
    for locus in missing:
        eva_text = eva_text_for(locus, pages[locus])
        if not eva_text.strip():
            summary["skipped"].append({"locus": locus, "reason": "no transcribable text"})
            print(f"  {locus}: SKIPPED (no text)")
            continue
        decoder.reset_stats()
        decoded = decoder.decode_folio(eva_text, folio_id=locus)
        recipe_md = paf.generate_recipe_markdown(locus, decoded, iiif_map)
        out_path = RECIPES_DIR / f"{locus}_recipe.md"
        out_path.write_text(recipe_md, encoding="utf-8")
        stats = dict(decoder.stats)
        total = max(1, stats.get("total_words", 0))
        resolved = stats.get("fully_resolved", 0) + stats.get("partially_resolved", 0)
        summary["completed"][locus] = {
            "words": stats.get("total_words", 0),
            "resolved": resolved,
            "resolved_pct": round(100.0 * resolved / total, 1),
            "section": paf.get_folio_section(locus)[1],
        }
        print(f"  {locus}: {stats.get('total_words', 0)} words, {resolved} resolved -> {out_path.name}")

    SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nCompleted {len(summary['completed'])} loci, skipped {len(summary['skipped'])}.")
    print(f"Summary: {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
