#!/usr/bin/env python3
"""
Generate Phase 8 assembly reports:
- STATISTICS.md -- Coverage, grade, vocabulary stats
- COMPARISON_REPORT.md -- EVA vs ZFD divergence analysis
- SECTION_COMPARISON.md -- Vocabulary differences across sections
- FULL_CORPUS.jsonl -- all folio line_data in manuscript order

2026-11 audit fixes (see transcription/AUDIT_2026-11.md):
  - grade labels no longer claim accuracy bands (A "95%+", B "80-94%", ...)
    that nothing in the pipeline ever measured
  - "Key Observations", divergence claims and the conclusion were fixed
    prose written regardless of the data; they are now computed, and two of
    the old ones were contradicted by the tables printed above them
  - the validated-readings table now shows what the compiler actually emits
    next to the hand reading, plus measured compiler-vs-gold agreement
  - corrupt JSONL lines are counted and reported instead of silently dropped
  - folios load in manuscript order (f1r, f1v, ... not f100r, f100v, ...)
  - repo-relative paths, UTF-8 I/O

Usage:
    python transcription/scripts/generate_reports.py
    python transcription/scripts/generate_reports.py --folios DIR --out DIR
"""

import argparse
import datetime
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import batch_transcribe as bt  # noqa: E402  (same rules the corpus was compiled with)

REPO_ROOT = HERE.parents[1]
FOLIOS_DIR = str(REPO_ROOT / "transcription" / "folios")
OUTPUT_DIR = str(REPO_ROOT / "transcription")
TODAY = datetime.date.today().isoformat()
BAD_JSON = Counter()


def zfd_words(text):
    return [w for w in re.split(r'[.\s|]+', text or "") if w and w != "|"]


def eva_words(text):
    return [w for seg in bt.eva_segments(text or "")
            for w in (bt.clean_eva_word(x) for x in seg) if w]


def load_all_data(folios_dir=None):
    """Load all line_data.jsonl files, in manuscript order."""
    folios_dir = folios_dir or FOLIOS_DIR
    all_lines = []
    for folio_dir in sorted(os.listdir(folios_dir), key=bt.folio_sort_key):
        jsonl_path = os.path.join(folios_dir, folio_dir, "line_data.jsonl")
        if not os.path.exists(jsonl_path):
            continue
        with open(jsonl_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    BAD_JSON[folio_dir] += 1
                    continue
                data["_dir"] = folio_dir
                all_lines.append(data)
    if BAD_JSON:
        print(f"WARNING: unparseable JSONL lines skipped: {dict(BAD_JSON)}")
    return all_lines


def load_metadata(folios_dir=None):
    """Load all metadata.json files."""
    folios_dir = folios_dir or FOLIOS_DIR
    metadata = {}
    for folio_dir in sorted(os.listdir(folios_dir), key=bt.folio_sort_key):
        meta_path = os.path.join(folios_dir, folio_dir, "metadata.json")
        if os.path.exists(meta_path):
            with open(meta_path, encoding="utf-8") as f:
                try:
                    metadata[folio_dir] = json.load(f)
                except json.JSONDecodeError:
                    BAD_JSON[folio_dir + "/metadata.json"] += 1
    return metadata


def grade_desc(grade):
    # What the grades actually encode (batch_transcribe.assess_confidence).
    # Not accuracy percentages: no grade has been scored against gold.
    descs = {"A": "validated term", "B": "operator/suffix parsed or short word",
             "C": "no operator or suffix parsed", "D": "unreadable glyph in source"}
    return descs.get(grade, "")


def normalize_gold(word):
    # The hand anchors spell Croatian š as the ASCII digraph "sh" (63 of 64
    # initial sh). Same sound, different spelling, so compare on š.
    return word.replace("sh", "š")


def anchor_agreement(all_lines):
    """Word-level agreement between the batch compiler and the hand anchors."""
    total = agree = skipped = 0
    for entry in all_lines:
        if entry.get("_dir") not in bt.ANCHORS:
            continue
        ew = [w for w in re.split(r'[.\s]+', re.sub(r'<[^>]*>', '', entry.get("eva_transliteration", ""))) if w]
        gw = zfd_words(entry.get("zfd_croatian", ""))
        if len(ew) != len(gw):
            skipped += 1
            continue
        for e, g in zip(ew, gw):
            total += 1
            agree += bt.parse_word(e)[0] == normalize_gold(g)
    return total, agree, skipped


def generate_statistics(all_lines, metadata):
    """Generate STATISTICS.md."""
    lines = []
    lines.append("# ZFD Transcription -- Statistics\n")
    lines.append(f"**Generated:** {TODAY}")
    lines.append(f"**Total folios:** {len(metadata)}")
    lines.append(f"**Total text lines:** {len(all_lines)}\n")

    section_counts = Counter()
    section_lines = Counter(l.get("_dir") for l in all_lines)
    per_section_lines = defaultdict(int)
    for folio_id, meta in metadata.items():
        section = meta.get("section", "unknown")
        section_counts[section] += 1
        per_section_lines[section] += section_lines.get(folio_id, 0)

    lines.append("## Section Distribution\n")
    lines.append("| Section | Folios | Lines |")
    lines.append("|---------|--------|-------|")
    for section, count in section_counts.most_common():
        lines.append(f"| {section} | {count} | {per_section_lines[section]} |")
    lines.append(f"| **Total** | **{len(metadata)}** | **{len(all_lines)}** |")
    lines.append("")

    conf_counts = Counter(entry.get("confidence", "?") for entry in all_lines)
    lines.append("## Grade Distribution\n")
    lines.append("Grades are parse-structure grades, not measured accuracy.\n")
    lines.append("| Grade | Meaning | Lines | Percentage |")
    lines.append("|-------|---------|-------|------------|")
    total = len(all_lines)
    for grade in ["A", "B", "C", "D"]:
        count = conf_counts.get(grade, 0)
        pct = count / total * 100 if total else 0
        lines.append(f"| {grade} | {grade_desc(grade)} | {count} | {pct:.1f}% |")
    other = sum(v for k, v in conf_counts.items() if k not in ("A", "B", "C", "D"))
    if other:
        lines.append(f"| Other | | {other} | {other / total * 100:.1f}% |")
    lines.append("")

    t, a, s = anchor_agreement(all_lines)
    lines.append("## Measured Agreement With Hand Anchors\n")
    if t:
        lines.append(f"Batch compiler output vs hand-transcribed anchor folios "
                     f"({', '.join(sorted(bt.ANCHORS))}): **{a}/{t} words = {a / t:.1%}** identical "
                     f"({s} anchor lines skipped where word counts differ; gold \"sh\" read as š).\n")
    else:
        lines.append("No anchor folios found.\n")

    all_zfd, all_eva = [], []
    for entry in all_lines:
        all_zfd += zfd_words(entry.get("zfd_croatian", ""))
        all_eva += eva_words(entry.get("eva_transliteration", ""))

    lines.append("## Vocabulary Statistics\n")
    lines.append(f"- **Total ZFD words:** {len(all_zfd)}")
    lines.append(f"- **Unique ZFD words:** {len(set(all_zfd))}")
    lines.append(f"- **Total EVA words:** {len(all_eva)}")
    lines.append(f"- **Unique EVA words:** {len(set(all_eva))}")
    lines.append("")

    word_freq = Counter(all_zfd)
    lines.append("## 30 Most Frequent ZFD Words\n")
    lines.append("| Rank | Word | Count | Likely Meaning |")
    lines.append("|------|------|-------|----------------|")
    validated = {
        "dain": "substance/given", "hol": "cook-oil", "hor": "cook-agent",
        "dar": "give-agent", "šol": "with-oil", "sal": "salt",
        "hi": "cook-adj", "hei": "cook-adj", "or": "oil",
        "ol": "oil", "š": "with", "dor": "give-oil",
        "ostol": "bone oil", "stor": "bone-agent", "stol": "bone-oil",
        "dai": "give-substance", "šei": "with-adj",
    }
    for rank, (word, count) in enumerate(word_freq.most_common(30), 1):
        lines.append(f"| {rank} | {word} | {count} | {validated.get(word, '')} |")
    lines.append("")

    gallows_counts = Counter()
    for w in all_eva:
        for g, exp in bt.GALLOWS.items():
            gallows_counts[f"{g}→{exp}"] += w.count(g)

    lines.append("## Gallows Occurrence Statistics\n")
    lines.append("Raw glyph counts. Includes gallows inside operators (ok, ot) and bench "
                 "gallows (cth, ckh, cph, cfh), which expand differently.\n")
    lines.append("| Gallows | EVA | ZFD | Total Occurrences |")
    lines.append("|---------|-----|-----|-------------------|")
    for g, count in gallows_counts.most_common():
        eva_g, zfd_g = g.split("→")
        lines.append(f"| {g} | {eva_g} | {zfd_g} | {count} |")
    lines.append("")

    lines.append("---\n")
    lines.append(f"*Statistics generated {TODAY} from {len(metadata)}-folio corpus.*\n")
    return "\n".join(lines)


def generate_comparison_report(all_lines):
    """Generate COMPARISON_REPORT.md -- EVA vs ZFD analysis."""
    n_folios = len({l.get("_dir") for l in all_lines})
    lines = []
    lines.append("# EVA vs ZFD Comparison Report\n")
    lines.append(f"**Generated:** {TODAY}")
    lines.append(f"**Scope:** {n_folios} folios, {len(all_lines)} lines\n")

    lines.append("## Overview\n")
    lines.append("This report documents where the ZFD transcription diverges from the")
    lines.append("EVA (European Voynich Alphabet) transliteration system. EVA treats each glyph as a")
    lines.append("standalone letter in an unknown alphabet. ZFD models a positional shorthand system")
    lines.append("with operators (word-initial), gallows abbreviation marks (medial), and suffixes (word-final).\n")

    lines.append("## Key Divergences\n")
    lines.append("### 1. Gallows Characters\n")
    lines.append("EVA treats gallows (k, t, f, p) as individual letters. ZFD expands them as cluster abbreviations:\n")
    lines.append("| EVA | ZFD |")
    lines.append("|-----|-----|")
    for g, exp in bt.GALLOWS.items():
        lines.append(f"| {g} | {exp} |")
    lines.append("")

    lines.append("### 2. Operator Detection (Word-Initial Parsing)\n")
    lines.append("| EVA initial | ZFD operator |")
    lines.append("|-------------|-------------|")
    for eva, zfd in bt.OPERATORS:
        lines.append(f"| {eva}- | {zfd}- |")
    lines.append("")

    lines.append("### 3. Suffix Detection (Word-Final Parsing)\n")
    lines.append("| EVA final | ZFD suffix |")
    lines.append("|-----------|-----------|")
    for eva, zfd in bt.SUFFIXES:
        lines.append(f"| -{eva} | -{zfd} |")
    lines.append("")

    lines.append("### 4. Bench Gallows and Ligatures\n")
    lines.append("| EVA | ZFD |")
    lines.append("|-----|-----|")
    for eva, zfd in bt.BENCH_GALLOWS.items():
        lines.append(f"| {eva} | {zfd} |")
    for eva, zfd in bt.MEDIAL_UNITS:
        lines.append(f"| {eva} (any position) | {zfd} |")
    for eva, zfd in bt.GLYPH_VALUES.items():
        lines.append(f"| {eva} (outside the suffix slot) | {zfd} |")
    for eva, zfd in bt.LIGATURE_SUFFIXES:
        lines.append(f"| -{eva} (ligature, claimed before operators) | -{zfd} |")
    lines.append("")

    div_lines = sum(1 for e in all_lines if e.get("eva_divergences"))
    total = len(all_lines) or 1
    op_words = suf_words = n_words = 0
    for e in all_lines:
        for w in eva_words(e.get("eva_transliteration", "")):
            n_words += 1
            op_words += bt.detect_operator(w)[0] is not None
            suf_words += bt.detect_suffix(w)[0] is not None
    lines.append("## Divergence Statistics (computed)\n")
    lines.append(f"- **Lines with a recorded gallows divergence:** {div_lines} / {len(all_lines)} "
                 f"({div_lines / total * 100:.1f}%)")
    if n_words:
        lines.append(f"- **EVA words with a detected operator:** {op_words} / {n_words} ({op_words / n_words:.1%})")
        lines.append(f"- **EVA words with a detected suffix:** {suf_words} / {n_words} ({suf_words / n_words:.1%})")
    lines.append("")

    lines.append("## Hand Readings vs Compiler Output\n")
    lines.append("| EVA | Hand reading | Compiler output | Match | Source of hand reading |")
    lines.append("|-----|--------------|-----------------|-------|------------------------|")
    hand = [
        ("okol", "ostol", "Curio adversarial validation (f88r)"),
        ("otorchety", "otrorhetri", "Curio adversarial validation (f88r)"),
        ("okeo.r!oly", "orolaly", "Latin term reading (f102v)"),
        ("sal", "sal", "identity"),
        ("shol", "šol", "FINAL_CHARACTER_MAP_v1 §3.2"),
        ("daiin", "dain", "operator + ligature suffix"),
    ]
    for eva, reading, src in hand:
        compiled = bt.parse_line(eva)[0]
        lines.append(f"| {eva} | {reading} | {compiled} | {'yes' if compiled == reading else 'NO'} | {src} |")
    lines.append("")

    t, a, s = anchor_agreement(all_lines)
    lines.append("## Conclusion\n")
    lines.append("ZFD and EVA differ on most words because they model the writing system")
    lines.append("differently (1:1 glyph-to-letter vs positional shorthand).")
    if t:
        lines.append("Measured against the hand-transcribed anchor folios, the batch compiler")
        lines.append(f"reproduces {a}/{t} words ({a / t:.1%}). That number, not the structural")
        lines.append("grades, is the current accuracy evidence for the automated folios.\n")
    lines.append("---\n")
    lines.append(f"*Comparison report generated {TODAY}.*\n")
    return "\n".join(lines)


def section_observations(section_vocab):
    """Observations computed from the data (replaces hardcoded prose)."""
    obs = []
    secs = sorted(section_vocab)
    if len(secs) < 2:
        return obs
    biggest = max(secs, key=lambda s: len(section_vocab[s]))
    obs.append(f"**{biggest}** has the largest vocabulary ({len(section_vocab[biggest])} unique words).")

    def overlap(a, b):
        return len(section_vocab[a] & section_vocab[b]) / len(section_vocab[a]) if section_vocab[a] else 0

    mean_out = {a: sum(overlap(a, b) for b in secs if b != a) / (len(secs) - 1) for a in secs}
    lo = min(secs, key=mean_out.get)
    hi = max(secs, key=mean_out.get)
    obs.append(f"**{lo}** has the most distinctive vocabulary (mean overlap {mean_out[lo]:.0%} with other sections); "
               f"**{hi}** the least ({mean_out[hi]:.0%}).")
    pair = max(((a, b) for a in secs for b in secs if a != b), key=lambda p: overlap(*p))
    obs.append(f"Highest directional overlap: {pair[0]} → {pair[1]} ({overlap(*pair):.0%}).")
    if "recipe" in section_vocab and "pharmaceutical" in section_vocab:
        obs.append(f"recipe → pharmaceutical overlap: {overlap('recipe', 'pharmaceutical'):.0%}.")
    core = ["dain", "hol", "hor", "dar", "sal"]
    everywhere = [w for w in core if all(w in section_vocab[s] for s in secs)]
    missing = {w: [s for s in secs if w not in section_vocab[s]] for w in core if w not in everywhere}
    text = "Core terms present in every section: " + (", ".join(everywhere) or "none")
    if missing:
        text += "; missing: " + ", ".join(
            "{} (not in {})".format(w, ", ".join(m)) for w, m in missing.items())
    obs.append(text + ".")
    return obs


def generate_section_comparison(all_lines, metadata):
    """Generate SECTION_COMPARISON.md."""
    lines = []
    lines.append("# Section Comparison -- Vocabulary Across Manuscript Sections\n")
    lines.append(f"**Generated:** {TODAY}\n")

    section_words = defaultdict(list)
    for entry in all_lines:
        section = metadata.get(entry.get("_dir", ""), {}).get("section", "unknown")
        section_words[section] += [w for w in zfd_words(entry.get("zfd_croatian", "")) if len(w) > 1]

    lines.append("## Section Word Counts\n")
    lines.append("Words of length 1 are excluded here (they are included in STATISTICS.md).\n")
    lines.append("| Section | Total Words | Unique Words |")
    lines.append("|---------|-------------|-------------|")
    for section in sorted(section_words):
        words = section_words[section]
        lines.append(f"| {section} | {len(words)} | {len(set(words))} |")
    lines.append("")

    lines.append("## Top 10 Words by Section\n")
    for section in sorted(section_words):
        freq = Counter(section_words[section])
        lines.append(f"### {section.replace('_', ' ').title()}\n")
        lines.append("| Rank | Word | Count |")
        lines.append("|------|------|-------|")
        for rank, (word, count) in enumerate(freq.most_common(10), 1):
            lines.append(f"| {rank} | {word} | {count} |")
        lines.append("")

    section_vocab = {s: set(w) for s, w in section_words.items()}
    sections = sorted(section_vocab)
    lines.append("## Cross-Section Vocabulary Overlap\n")
    lines.append("Percentage of the row section's vocabulary that also appears in the column section:\n")
    lines.append("| Section | " + " | ".join(sections) + " |")
    lines.append("|" + "|".join(["---"] * (len(sections) + 1)) + "|")
    for sa in sections:
        row = f"| {sa} |"
        for sb in sections:
            if sa == sb:
                row += " -- |"
            else:
                pct = len(section_vocab[sa] & section_vocab[sb]) / len(section_vocab[sa]) * 100 if section_vocab[sa] else 0
                row += f" {pct:.0f}% |"
        lines.append(row)
    lines.append("")

    lines.append("## Key Observations (computed)\n")
    for i, o in enumerate(section_observations(section_vocab), 1):
        lines.append(f"{i}. {o}")
    lines.append("")
    lines.append("---\n")
    lines.append(f"*Section comparison generated {TODAY}.*\n")
    return "\n".join(lines)


def write_full_corpus(all_lines, path):
    """FULL_CORPUS.jsonl: every line_data.jsonl row, in manuscript order.
    (The committed file had no generator and was in string order, f100r first.)"""
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for entry in all_lines:
            row = {k: v for k, v in entry.items() if k != "_dir"}
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Generate Phase 8 transcription reports")
    ap.add_argument("--folios", default=FOLIOS_DIR)
    ap.add_argument("--out", default=OUTPUT_DIR)
    args = ap.parse_args(argv)

    print("Loading data...")
    all_lines = load_all_data(args.folios)
    metadata = load_metadata(args.folios)
    print(f"Loaded {len(all_lines)} lines from {len(metadata)} folios")

    for name, text in [
        ("STATISTICS.md", generate_statistics(all_lines, metadata)),
        ("COMPARISON_REPORT.md", generate_comparison_report(all_lines)),
        ("SECTION_COMPARISON.md", generate_section_comparison(all_lines, metadata)),
    ]:
        print(f"Generating {name}...")
        with open(os.path.join(args.out, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)

    write_full_corpus(all_lines, os.path.join(args.out, "FULL_CORPUS.jsonl"))
    print("Wrote FULL_CORPUS.jsonl")
    print(f"Done! Reports written to {args.out}")


if __name__ == "__main__":
    main()
