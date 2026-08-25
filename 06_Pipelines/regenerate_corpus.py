#!/usr/bin/env python3
"""
ZFD Corpus Regeneration and Determinism Gate
============================================
Regenerates every recipe translation (all 244 loci) from repo-local EVA
sources through the canonical decoder and unified lexicon v3, so the whole
corpus is reproducible from what the repository actually contains. The
original 201 were generated with a container-local lexicon file that never
entered the repo; that made them unverifiable, which the 2026-08-25 audit
treats as incorrect by construction.

Sources:
- voynich_data/raw_eva/<folio>.txt for the 201 standard folios
- 02_Transcriptions/LSI_ivtff_0d.txt for the 43 multi-panel loci

The determinism gate decodes every locus twice and fails on any byte
difference between the two renderings.

Usage:
    python regenerate_corpus.py           # regenerate + determinism gate
    python regenerate_corpus.py --check   # determinism gate only, no writes
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import process_all_folios as paf
from zfd_decoder_v2 import ZFDDecoder
from complete_missing_folios import parse_lsi, eva_text_for, existing_locus_ids

REPO_ROOT = Path(__file__).resolve().parent.parent
RECIPES_DIR = REPO_ROOT / "translations" / "recipes"
SUMMARY_PATH = REPO_ROOT / "translations" / "PIPELINE_SUMMARY_v3.json"


def corpus_sources():
    """Every locus with its EVA text, raw_eva first, LSI for the rest."""
    sources = {}
    for eva_path in sorted((REPO_ROOT / "voynich_data" / "raw_eva").glob("f*.txt")):
        sources[eva_path.stem] = eva_path.read_text(encoding="utf-8",
                                                   errors="replace")
    lsi = parse_lsi()
    for locus, page_lines in lsi.items():
        if locus not in sources:
            text = eva_text_for(locus, page_lines)
            if text.strip():
                sources[locus] = text
    return sources


def render(decoder, iiif_map, locus, eva_text):
    decoder.reset_stats()
    decoded = decoder.decode_folio(eva_text, folio_id=locus)
    return paf.generate_recipe_markdown(locus, decoded, iiif_map), dict(
        decoder.stats)


def main():
    check_only = "--check" in sys.argv
    sources = corpus_sources()
    iiif_map = json.loads((REPO_ROOT / "folio_iiif_map.json").read_text())
    decoder = ZFDDecoder()

    summary = {
        "pipeline_version": "3.0",
        "lexicon_version": f"{paf.LEXICON_VERSION} ({paf.MORPHEME_COUNT} morphemes)",
        "loci": {},
    }
    nondeterministic = []
    changed = 0
    for locus in sorted(sources):
        first, stats = render(decoder, iiif_map, locus, sources[locus])
        second, _ = render(decoder, iiif_map, locus, sources[locus])
        if first != second:
            nondeterministic.append(locus)
            continue
        out_path = RECIPES_DIR / f"{locus}_recipe.md"
        previous = out_path.read_text(encoding="utf-8") if out_path.exists() else None
        if not check_only and previous != first:
            out_path.write_text(first, encoding="utf-8")
            changed += 1
        total = max(1, stats.get("total_words", 0))
        resolved = stats.get("fully_resolved", 0) + stats.get(
            "partially_resolved", 0)
        summary["loci"][locus] = {
            "words": stats.get("total_words", 0),
            "resolved": resolved,
            "resolved_pct": round(100.0 * resolved / total, 1),
        }

    totals = summary["loci"].values()
    summary["totals"] = {
        "loci": len(summary["loci"]),
        "words": sum(entry["words"] for entry in totals),
        "resolved": sum(entry["resolved"] for entry in totals),
    }
    if not check_only:
        SUMMARY_PATH.write_text(json.dumps(summary, indent=2),
                                encoding="utf-8")

    print(f"loci decoded: {len(summary['loci'])}")
    print(f"words: {summary['totals']['words']}  "
          f"resolved: {summary['totals']['resolved']}")
    print(f"rewritten files: {changed}" if not check_only else "check only")
    if nondeterministic:
        print(f"DETERMINISM GATE FAILED: {nondeterministic}")
        return 1
    print("DETERMINISM GATE PASSED: every locus renders byte-identical twice")
    return 0


if __name__ == "__main__":
    sys.exit(main())
