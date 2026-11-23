#!/usr/bin/env python3
"""Audit the committed recipe decoder without changing its lexicon or outputs.

Reports two explicitly separate input sets: the published recipe input union,
and one preferred transcriber per LSI locus/line using the existing selector.
The second is a source-selection comparison, not a new translation edition.
"""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "06_Pipelines"))
import regenerate_corpus as rc
import process_all_folios as paf
from complete_missing_folios import parse_lsi, eva_text_for, TRANSCRIBER_PREFERENCE
from zfd_decoder_v2 import ZFDDecoder, LEXICON_PATH

FAMILIES = ("operators", "stems", "suffixes", "state_markers", "latin_terms")
TERMS = ("ros", "rosar", "rosol", "stor", "streod", "stroy", "cer", "cera",
         "aloe", "aloin", "sal", "sar", "sain", "mel", "pip", "piper",
         "vin", "arg", "fer", "aq",
         "ol", "or", "ar", "al", "ost", "kost")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit_sources(sources, compare_committed=False):
    decoder = ZFDDecoder()
    totals = Counter()
    stems = defaultdict(Counter)
    latin = defaultdict(Counter)
    selected_tokens = []
    locus_stats = {}
    repeat_mismatches = []
    committed_mismatches = []
    no_residue = 0
    high_score_with_residue = 0
    iiif_map = json.loads((ROOT / "folio_iiif_map.json").read_text())
    for locus, text in sorted(sources.items()):
        decoded = decoder.decode_folio(text, folio_id=locus)
        stats = decoded["stats"]
        totals.update(stats)
        locus_stats[locus] = dict(stats)
        for line_number, line in enumerate(decoded["lines"], 1):
            # Preserve parser word positions; do not retokenize the rendered
            # EVA line, which replaces its original separators with spaces.
            for word_index, word in enumerate(line["words"], 1):
                if word is None:
                    continue
                no_residue += not word["residue"]
                high_score_with_residue += bool(word["residue"]) and word["confidence"] >= .7
                if word["stem"]:
                    form = word["stem"]["form"]
                    stems[form][locus] += 1
                    if form in {"ros", "rosar", "rosol", "cer", "cera"}:
                        selected_tokens.append({
                            "locus": locus, "decoded_line_number": line_number,
                            "word_index": word_index, "decomposition": word,
                            "eva_line": line["eva"],
                        })
                if word["latin_match"]:
                    latin[word["latin_match"]["form"]][locus] += 1
        if compare_committed:
            rendered = paf.generate_recipe_markdown(locus, decoded, iiif_map)
            second = paf.generate_recipe_markdown(
                locus, decoder.decode_folio(text, folio_id=locus), iiif_map)
            if rendered != second:
                repeat_mismatches.append(locus)
            target = ROOT / "translations" / "recipes" / f"{locus}_recipe.md"
            if not target.exists() or target.read_text(encoding="utf-8") != rendered:
                committed_mismatches.append(locus)

    denominator = totals["total_words"]
    resolved = totals["fully_resolved"] + totals["partially_resolved"]

    def count_table(counter, keys):
        return {
            key: {"tokens": sum(counter[key].values()), "loci": len(counter[key]),
                  "by_locus": dict(sorted(counter[key].items()))}
            for key in keys
        }

    result = {
        "loci": len(sources), "stats": dict(totals), "resolved": resolved,
        "resolved_pct": 100 * resolved / denominator,
        "fully_resolved_pct": 100 * totals["fully_resolved"] / denominator,
        "partially_resolved_pct": 100 * totals["partially_resolved"] / denominator,
        "unknown_pct": 100 * totals["unknown"] / denominator,
        "empty_residue_tokens": no_residue,
        "empty_residue_pct": 100 * no_residue / denominator,
        "fully_resolved_with_nonempty_residue": high_score_with_residue,
        "stem_counts": count_table(stems, TERMS),
        "latin_match_counts": count_table(latin, sorted(latin)),
        "selected_token_records": selected_tokens,
        "locus_stats": locus_stats,
    }
    if compare_committed:
        result["verification"] = {
            "decoded_twice": len(sources), "repeat_mismatches": repeat_mismatches,
            "compared_with_committed": len(sources),
            "committed_mismatches": committed_mismatches,
        }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    sources = rc.corpus_sources()
    lsi = parse_lsi()
    preferred = {locus: eva_text_for(locus, lines) for locus, lines in lsi.items()}
    alias_panels = {
        locus: sorted(other for other in preferred
                      if re.fullmatch(re.escape(locus) + r"\d+", other))
        for locus in sources if locus not in preferred
    }
    alias_panels = {locus: panels for locus, panels in alias_panels.items() if panels}
    canonical = audit_sources(sources, compare_committed=True)
    comparison = audit_sources(preferred)
    lexicon = json.loads(LEXICON_PATH.read_text(encoding="utf-8"))
    raw_paths = sorted((ROOT / "voynich_data" / "raw_eva").glob("f*.txt"))
    input_paths = [LEXICON_PATH, ROOT / "02_Transcriptions" / "LSI_ivtff_0d.txt",
                   ROOT / "06_Pipelines" / "zfd_decoder_v2.py",
                   ROOT / "06_Pipelines" / "regenerate_corpus.py",
                   ROOT / "06_Pipelines" / "complete_missing_folios.py",
                   ROOT / "06_Pipelines" / "process_all_folios.py",
                   ROOT / "folio_iiif_map.json", Path(__file__).resolve()] + raw_paths
    result = {
        "base_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "worktree_differs_from_base": bool(subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()),
        "definitions": {
            "canonical": "Existing corpus_sources(): 201 raw_eva files plus 43 additional LSI IDs.",
            "lsi_preferred": "Existing LSI selector: one preferred transcriber for each locus/line ID; no raw_eva whole-page aliases. A comparison dataset, not the committed recipe edition.",
            "fully_resolved": "Decoder label for rounded match score >= 0.70; permits unmatched residue.",
            "partially_resolved": "Decoder label for rounded match score >= 0.30 and < 0.70.",
            "resolved": "Sum of the two score classes; does not measure independently established translation accuracy.",
            "stem_counts": "Counts of emitted decomposition.stem.form only, not substring searches, reference-list entries, Latin-prefix matches, or recipe identifications.",
            "empty_residue": "No unmatched characters under the decoder's parse; no semantic-accuracy claim.",
        },
        "transcriber_preference": TRANSCRIBER_PREFERENCE,
        "lexicon": {
            "version": lexicon["meta"]["version"],
            "family_counts": {family: len(lexicon[family]) for family in FAMILIES},
            "family_entries": sum(len(lexicon[family]) for family in FAMILIES),
            "distinct_key_strings": len(set().union(*(set(lexicon[f]) for f in FAMILIES))),
            "reference_botanical_entries_excluded_from_decoder": len(lexicon.get("reference_botanical", {})),
        },
        "whole_page_aliases": alias_panels,
        "alias_tokens": sum(canonical["locus_stats"][locus]["total_words"] for locus in alias_panels),
        "canonical": canonical, "lsi_preferred": comparison,
        "input_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in input_paths},
    }
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
        for name in ("canonical", "lsi_preferred"):
            row = result[name]
            print(f"{name}: {row['loci']} IDs; {row['resolved']}/{row['stats']['total_words']} = {row['resolved_pct']:.6f}% score-class coverage")
        print(f"All-page verification: {canonical['verification']}")
    else:
        print(serialized, end="")
    failed = canonical["verification"]["repeat_mismatches"] or canonical["verification"]["committed_mismatches"]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
