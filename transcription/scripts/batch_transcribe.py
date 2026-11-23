#!/usr/bin/env python3
"""
Batch transcription compiler for the ZFD project.

Applies the ZFD parsing rules (transcription/abbreviation_rules.json) to the
Takahashi (H) EVA transliteration in LSI_ivtff_0d.txt and writes the standard
package (metadata.json, TRANSCRIPTION.md, line_data.jsonl, notes.md) per folio.

This is automated rule parsing of an existing EVA transliteration. It is not a
direct reading of the manuscript image.

Usage:
    python transcription/scripts/batch_transcribe.py              # all pages
    python transcription/scripts/batch_transcribe.py f10r f23v    # some pages
    python transcription/scripts/batch_transcribe.py --skip-existing

2026-11 audit fixes (see transcription/AUDIT_2026-11.md):
  - bench gallows were expanded twice (cth -> htr -> htrr)
  - IVTFF "!" filler (= no glyph) was read as an unknown glyph "?"
  - non-plant "<->" breaks were deleted, merging the words on either side
  - "da" operator split the aiin ligature, so daiin was never compiled
  - aiiin suffix and medial ch ligature from the rules spec were missing
  - sh compiled as ASCII "s" and y left as raw EVA; canon is š and i
  - plant marker "|" broke the TRANSCRIPTION.md tables
  - gallows divergence count skipped "t"
  - Currier language/hand and quire were hardcoded instead of read from
    the IVTFF page headers
  - six multi-panel pages with text were never compiled
  - hardcoded /home/user paths and locale-dependent file encoding
"""

import argparse
import datetime
import json
import os
import re
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EVA = REPO_ROOT / "02_Transcriptions" / "LSI_ivtff_0d.txt"
DEFAULT_IIIF = REPO_ROOT / "folio_iiif_map.json"
DEFAULT_OUT = REPO_ROOT / "transcription" / "folios"

# Hand-transcribed gold folios. The batch compiler never overwrites these.
ANCHORS = {"f88r", "f1r", "f2r", "f71r", "f102v"}

# ZFD Parsing Rules
OPERATORS = [
    ("qo", "ko"),
    ("ch", "h"),
    ("sh", "š"),  # canon: lexicon v3, operators.json, character_reference.py
    ("da", "da"),
    ("ok", "ost"),
    ("ot", "otr"),
    ("q", "k"),
]

SUFFIXES = [
    ("aiiin", "ain"),
    ("aiin", "ain"),
    ("edy", "edi"),
    ("eey", "ei"),
    ("y", "i"),
    ("ol", "ol"),
    ("ar", "ar"),
    ("or", "or"),
    ("al", "al"),
    ("od", "od"),
    ("am", "am"),
    ("om", "om"),
    ("m", "m"),
    ("n", "n"),
    ("l", "l"),
    ("r", "r"),
]

GALLOWS = {
    "k": "st",
    "t": "tr",
    "f": "pr",
    "p": "pl",
}

BENCH_GALLOWS = {
    "cth": "htr",
    "ckh": "hst",
    "cph": "hpl",
    "cfh": "hpr",
}

# Ligature suffixes are single units (abbreviation_rules.json "ligature_units").
# They are claimed before operator detection so an operator ending in "a"
# ("da") cannot split them: daiin -> d + aiin -> dain, not da + iin -> daiin.
LIGATURE_SUFFIXES = [("aiiin", "ain"), ("aiin", "ain")]

# ch and sh are single glyph units with one value in every position.
# Canon (2026-11, see transcription/AUDIT_2026-11.md section D):
#   ch -> h   zfd_decoder/data/mid_word.json, abbreviation_rules ligature_units,
#             gold f88r (otorchety -> otrorhetri)
#   sh -> š   Croatian š (/ʃ/, Glagolitic Sha). lexicon_v2.csv (šor, šei, še,
#             šeo, šeom), unified_lexicon_v3 (š, še, šeo), operators.json,
#             mid_word.json, character_reference.py, FINAL_CHARACTER_MAP_v1.
#             The old "s" / "s/sh" in the transcription docs were ASCII
#             spellings of the same sound.
MEDIAL_UNITS = [("ch", "h"), ("sh", "š")]

# Single-glyph values outside the suffix slot.
#   y -> i    character_reference.py (Yer: EVA y, Croatian i, no position
#             condition), glyph_inventory.json (/i/), DUCTUS_ANALYSIS 6.2 #3
#             (initial and final y are the same glyph), gold anchors map
#             non-final y to i in 31 of 31 cases. Croatian spelling has no y.
GLYPH_VALUES = {"y": "i"}

# Validated terms, as compiler OUTPUT. "shol" was listed here before, but the
# compiler never emitted "shol"; EVA shol now compiles to "šol".
VALIDATED = {"ostol", "dain", "hol", "hor", "sal", "dar", "stor", "šol", "stol"}


def detect_operator(word):
    """Detect word-initial operator (longest match first)."""
    for eva, zfd in OPERATORS:
        if word.startswith(eva):
            return eva, zfd, word[len(eva):]
    return None, None, word


def detect_suffix(remainder):
    """Detect word-final suffix (longest match first)."""
    for eva, zfd in SUFFIXES:
        if remainder.endswith(eva):
            return eva, zfd, remainder[:-len(eva)]
    return None, None, remainder


def expand_stem(stem):
    """Expand bench gallows, ch/sh units, simple gallows and y in ONE pass.

    One left-to-right scan, so the output of one rule is never fed back into
    another. The old two-pass version expanded bench gallows first and then
    re-expanded the t/p inside their output: cth -> htr -> htrr,
    cfh -> hpr -> hplr.
    """
    out = []
    i = 0
    while i < len(stem):
        tri = stem[i:i + 3]
        if tri in BENCH_GALLOWS:
            out.append(BENCH_GALLOWS[tri])
            i += 3
        elif stem[i:i + 2] in dict(MEDIAL_UNITS):
            out.append(dict(MEDIAL_UNITS)[stem[i:i + 2]])
            i += 2
        elif stem[i] in GALLOWS:
            out.append(GALLOWS[stem[i]])
            i += 1
        else:
            out.append(GLYPH_VALUES.get(stem[i], stem[i]))
            i += 1
    return "".join(out)


def clean_eva_word(eva_word):
    """Apply IVTFF filler conventions (see the LSI_ivtff_0d.txt header).

    "!" means one vote for NO character here, so it is deleted.
    "%" means this transcription has no information here, so it is unknown.
    "?" is an unreadable glyph and stays "?".
    """
    return eva_word.replace("!", "").replace("%", "?")


def parse_word(eva_word):
    """Parse a single EVA word to ZFD Croatian."""
    clean = clean_eva_word(eva_word)
    if not clean:
        return "", None

    # Skip if entirely uncertain
    if all(c == "?" for c in clean):
        return "[???]", "D"

    # Step 0: ligature suffixes are claimed first (see LIGATURE_SUFFIXES)
    suf_eva = suf_zfd = None
    for eva, zfd in LIGATURE_SUFFIXES:
        if clean.endswith(eva):
            suf_eva, suf_zfd, clean = eva, zfd, clean[:-len(eva)]
            break

    # Step 1: Operator detection
    op_eva, op_zfd, remainder = detect_operator(clean)

    # Step 2: Suffix detection (unless a ligature suffix was already taken)
    if suf_eva is None:
        suf_eva, suf_zfd, stem = detect_suffix(remainder)
    else:
        stem = remainder

    # Step 3: Bench gallows, ch/sh units, simple gallows, y (single pass)
    stem = expand_stem(stem)

    # Step 4: Assemble
    result = (op_zfd or "") + stem + (suf_zfd or "")

    conf = assess_confidence(clean_eva_word(eva_word), result, op_eva, suf_eva)
    return result, conf


def assess_confidence(eva, zfd, op, suf):
    """Structural grade for a parsed word.

    These grades describe parse structure only. They are not measured
    accuracy: no grade here has been scored against a gold reading.
    """
    if zfd in VALIDATED:
        return "A"

    # Unreadable glyph in the source transliteration
    if "?" in eva:
        return "D"

    # Operator and/or suffix parsed. (The old code had separate AND and OR
    # branches that both returned "B"; merged, same behaviour.)
    if op or suf:
        return "B"

    # Simple/short words
    if len(eva) <= 3:
        return "B"

    return "C"


PLANT_MARK = "|"


def clean_eva_line(eva_line):
    """Turn an IVTFF text field into plain EVA with explicit breaks.

    "<->" is a drawing interruption, so it is ALWAYS a word break. With a
    <!plant> comment it becomes the plant mark "|"; any other "<->"
    (figure, fold, gap, ...) becomes ".". The old code deleted the
    non-plant ones, which glued the words on either side together
    (dykaly<-><!||>daiin -> dykalydaiin).
    """
    line = re.sub(r'<->\s*<!plant>', f' {PLANT_MARK} ', eva_line)
    line = line.replace('<->', '.')
    line = re.sub(r'<[^>]*>', '', line)  # comments, <$>, <%>
    return line.strip()


def eva_segments(eva_line):
    """List of word lists, one per plant-separated segment."""
    segments = []
    for seg in clean_eva_line(eva_line).split(PLANT_MARK):
        # "." definite break, "," dubious break, whitespace
        words = [w for w in re.split(r'[.,\s]+', seg) if w]
        segments.append(words)
    return segments


def parse_line(eva_line):
    """Parse a full EVA line to ZFD, handling plant breaks and word boundaries."""
    zfd_segments = []
    confidences = []

    for words in eva_segments(eva_line):
        out = []
        for word in words:
            zfd, conf = parse_word(word)
            if not zfd:  # word was only fillers
                continue
            out.append(zfd)
            confidences.append(conf)
        zfd_segments.append(". ".join(out))

    # Keep every plant mark, including line-initial/final ones
    zfd_text = f" {PLANT_MARK} ".join(zfd_segments).strip()

    # Overall line confidence
    if not confidences:
        return zfd_text, "D"

    conf_vals = {"A": 4, "B": 3, "C": 2, "D": 1}
    avg = sum(conf_vals.get(c, 2) for c in confidences) / len(confidences)
    if avg >= 3.5:
        line_conf = "A"
    elif avg >= 2.5:
        line_conf = "B"
    elif avg >= 1.5:
        line_conf = "C"
    else:
        line_conf = "D"

    return zfd_text, line_conf


def extract_eva_lines(eva_file, folio_id):
    """Extract EVA lines for a folio from the IVTFF file.

    Handles sub-section numbering like f67r1.1, f67r2.1, etc.
    These are merged into a single sequence with adjusted line numbers.
    """
    lines = {}
    # Match both "f67r.1" and "f67r1.1", "f67r2.1" patterns
    base = re.escape(folio_id)
    pattern = re.compile(rf'^<{base}\d*\.(\d+)')

    with open(eva_file, 'r', encoding='latin-1') as f:
        for raw_line in f:
            raw_line = raw_line.rstrip()
            m = pattern.match(raw_line)
            if m:
                line_num = int(m.group(1))
                # For sub-sections, offset line numbers to avoid collisions
                # Extract sub-section number if present
                sub_match = re.match(rf'^<{base}(\d+)\.', raw_line)
                if sub_match:
                    sub_num = int(sub_match.group(1))
                    # Offset: section 1 = lines 1-99, section 2 = lines 100-199, etc.
                    if sub_num > 1:
                        line_num += (sub_num - 1) * 100

                # Prefer H transcriber, then C or T
                if ';H>' in raw_line:
                    text = re.sub(r'^<[^>]+>\s*', '', raw_line)
                    lines[line_num] = text
                elif line_num not in lines and (';C>' in raw_line or ';T>' in raw_line):
                    text = re.sub(r'^<[^>]+>\s*', '', raw_line)
                    lines[line_num] = text

    return dict(sorted(lines.items()))


def read_page_header(eva_file, folio_id):
    """Read the IVTFF page-header variables for a page.

    Header lines look like:  <f1r>  <! $I=T $Q=A $P=A $L=A $H=1 $X=V>
    $Q quire letter, $I illustration type, $L Currier language, $H hand.
    Multi-panel pages (f67r1, f67r2, ...) take the first panel's header.
    """
    pattern = re.compile(rf'^<{re.escape(folio_id)}\d*>\s*<!(.*)>')
    with open(eva_file, 'r', encoding='latin-1') as f:
        for raw_line in f:
            m = pattern.match(raw_line)
            if m:
                return dict(re.findall(r'\$(\w)=(\w+)', m.group(1)))
    return {}


def list_ivtff_pages(eva_file):
    """Every page (multi-panel pages collapsed to their base id) with H text."""
    pages = set()
    pat = re.compile(r'^<(f\d+[rv])\d*\.\d+[^;]*;H>')
    with open(eva_file, 'r', encoding='latin-1') as f:
        for raw_line in f:
            m = pat.match(raw_line)
            if m:
                pages.add(m.group(1))
    return pages


def folio_sort_key(folio_id):
    m = re.match(r'f?(\d+)([rv]?)(\d*)', folio_id)
    return (int(m.group(1)), m.group(2), int(m.group(3) or 0))


_ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI",
          "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX"]


def quire_label(q_letter):
    """IVTFF $Q letter A..T is quire 1..20."""
    if not q_letter or not ("A" <= q_letter <= "T"):
        return "Unknown"
    return f"{q_letter} (Rene) / {_ROMAN[ord(q_letter) - ord('A')]} (Beinecke)"


def determine_section(folio_id):
    """Determine manuscript section from folio number."""
    fnum = int(re.search(r'(\d+)', folio_id).group(1))
    if fnum <= 57:
        return "herbal"
    elif fnum <= 66:
        return "herbal_large"  # Large herbal pages
    elif 67 <= fnum <= 69:
        return "cosmological"
    elif 70 <= fnum <= 73:
        return "zodiac"
    elif 75 <= fnum <= 84:
        return "biological"
    elif 85 <= fnum <= 86:
        return "rosettes"
    elif 87 <= fnum <= 102:
        return "pharmaceutical"
    elif 103 <= fnum <= 116:
        return "recipe"
    else:
        return "unknown"


ILLUSTRATION_TYPES = {
    "H": "herbal", "A": "astronomical", "C": "cosmological", "Z": "zodiac",
    "B": "biological", "P": "pharmaceutical", "S": "stars", "T": "text_only",
}


def generate_metadata(folio_id, iiif_id, num_lines, section=None, header=None):
    """Generate metadata.json content.

    Quire, Currier language and hand come from the IVTFF page header. The old
    version hardcoded language A / hand 1 for every page and guessed quires
    from folio number ranges.
    """
    header = header or {}
    if section is None:
        section = determine_section(folio_id)
    quire = quire_label(header.get("Q"))
    known_iiif = iiif_id not in (None, "", "unknown")

    section_descriptions = {
        "herbal": "Standard herbal folio with plant illustration and text.",
        "herbal_large": "Large herbal folio with detailed plant illustration.",
        "cosmological": "Cosmological diagram with celestial features.",
        "zodiac": "Zodiac diagram with nymph figures and labels.",
        "biological": "Biological section with bathing/anatomical illustrations.",
        "rosettes": "Rosette foldout with circular diagrams.",
        "pharmaceutical": "Pharmaceutical page with apparatus illustrations and recipe text.",
        "recipe": "Recipe section with dense text blocks.",
    }

    return {
        "folio": folio_id,
        "section": section,
        "illustration_type": ILLUSTRATION_TYPES.get(header.get("I"), header.get("I")),
        "quire": quire,
        "currier_language": header.get("L"),  # None where IVTFF gives none
        "currier_hand": header.get("H"),
        "iiif_id": str(iiif_id) if known_iiif else None,
        "iiif_url": (f"https://collections.library.yale.edu/iiif/2/{iiif_id}/full/full/0/default.jpg"
                     if known_iiif else None),
        "condition": section_descriptions.get(section, "Standard folio."),
        "layout": {
            "type": section,
            "text_lines": num_lines
        },
        "transcription_date": datetime.date.today().isoformat(),
        "transcription_method": ("Automated ZFD rule parsing (batch_transcribe.py) of the "
                                 "Takahashi (H) EVA transliteration in LSI_ivtff_0d.txt. "
                                 "Not a direct reading of the manuscript image.")
    }


def md_cell(text):
    """Escape a value for a markdown table cell."""
    return text.replace("|", "\\|")


def generate_transcription_md(folio_id, iiif_id, eva_lines, parsed_lines, metadata=None):
    """Generate TRANSCRIPTION.md content."""
    metadata = metadata or {}
    lines = []
    lines.append(f"# Folio {folio_id} -- Automated ZFD Transcription\n")
    section = metadata.get("section") or determine_section(folio_id)
    lines.append(f"**Section:** {section.replace('_', ' ').title()}")
    lines.append(f"**IIIF:** {metadata.get('iiif_url') or 'not in folio_iiif_map.json'}")
    lines.append(f"**Currier:** Language {metadata.get('currier_language') or '?'}, "
                 f"Hand {metadata.get('currier_hand') or '?'}\n")
    lines.append("---\n")
    lines.append("## Text\n")
    lines.append("| Line | Croatian | Conf | EVA |")
    lines.append("|------|----------|------|-----|")

    for line_num in sorted(eva_lines.keys()):
        eva = eva_lines[line_num]
        zfd, conf = parsed_lines[line_num]
        eva_display = clean_eva_line(eva)
        lines.append(f"| L{line_num} | {md_cell(zfd)} | {conf} | {md_cell(eva_display)} |")

    lines.append("")

    # Confidence distribution
    conf_counts = Counter(conf for _, conf in parsed_lines.values())
    lines.append("## Confidence Distribution\n")
    for grade in ["A", "B", "C", "D"]:
        count = conf_counts.get(grade, 0)
        lines.append(f"- **{grade}:** {count} lines")

    lines.append("")
    lines.append("Grades are parse-structure grades, not measured accuracy.")
    lines.append(f"\n---\n\n*Generated {datetime.date.today().isoformat()} by batch_transcribe.py: "
                 "automated ZFD rule parsing of the Takahashi (H) EVA transliteration.*\n")

    return "\n".join(lines)


def generate_line_data_jsonl(folio_id, eva_lines, parsed_lines):
    """Generate line_data.jsonl content."""
    entries = []
    for line_num in sorted(eva_lines.keys()):
        eva = eva_lines[line_num]
        zfd, conf = parsed_lines[line_num]
        eva_clean = clean_eva_line(eva)

        entry = {
            "folio": folio_id,
            "line": line_num,
            "type": "text",
            "eva_transliteration": eva_clean,
            "zfd_croatian": zfd,
            "confidence": conf,
            "confidence_notes": f"Automated ZFD parsing. {conf} = parse-structure grade, not measured accuracy.",
            "eva_divergences": [],
            "uncertain_readings": []
        }

        # Note gallows divergences. (The old filter `c not in 'qochtshda'`
        # silently dropped every "t", because "t" is in that string.)
        gallows_count = sum(1 for c in eva_clean if c in GALLOWS)
        if gallows_count > 0:
            entry["eva_divergences"].append({
                "type": "gallows_expansion",
                "count": gallows_count,
                "reason": "Gallows characters expanded as cluster abbreviations per ZFD rules"
            })

        entries.append(json.dumps(entry))

    return "\n".join(entries) + "\n"


def generate_notes_md(folio_id, eva_lines, parsed_lines):
    """Generate notes.md with brief observations."""
    lines = []
    lines.append(f"# Folio {folio_id} -- Transcription Notes\n")

    # Collect all EVA words and ZFD words
    all_eva_words = []
    all_zfd_words = []
    for lnum in sorted(eva_lines.keys()):
        for seg in eva_segments(eva_lines[lnum]):
            all_eva_words.extend(w for w in (clean_eva_word(x) for x in seg) if w)
        zfd = parsed_lines[lnum][0]
        for w in re.split(r'[.\s|]+', zfd):
            w = w.strip()
            if w:
                all_zfd_words.append(w)

    # Operator stats
    op_counts = Counter()
    for w in all_eva_words:
        # same order as parse_word: ligature suffix first, so daiin is not "da"
        for lig, _ in LIGATURE_SUFFIXES:
            if w.endswith(lig):
                w = w[:-len(lig)]
                break
        op_eva, op_zfd, _ = detect_operator(w)
        if op_eva:
            op_counts[f"{op_eva}→{op_zfd}"] += 1

    lines.append("## Operator Distribution\n")
    lines.append("| Operator | Count |")
    lines.append("|----------|-------|")
    for op, count in op_counts.most_common():
        lines.append(f"| {op} | {count} |")
    lines.append("")

    # Gallows stats
    gallows_counts = Counter()
    for w in all_eva_words:
        for g in "ktfp":
            gallows_counts[f"{g}→{GALLOWS[g]}"] += w.count(g)

    lines.append("## Gallows Distribution\n")
    lines.append("| Gallows | Count |")
    lines.append("|---------|-------|")
    for g, count in gallows_counts.most_common():
        if count > 0:
            lines.append(f"| {g} | {count} |")
    lines.append("")

    # Validated terms
    validated = {"ostol": "bone oil", "dain": "substance/given", "hol": "cook-oil",
                 "hor": "cook-agent", "sal": "salt", "dar": "give-agent",
                 "stor": "bone-agent", "šol": "with-oil", "stol": "bone-oil"}

    found = []
    for w in all_zfd_words:
        if w in validated and w not in [f[0] for f in found]:
            found.append((w, validated[w]))

    if found:
        lines.append("## Validated Terms Present\n")
        for term, gloss in found:
            lines.append(f"- **{term}** ({gloss})")
        lines.append("")

    # Confidence distribution
    conf_counts = Counter(conf for _, conf in parsed_lines.values())
    lines.append("## Confidence Summary\n")
    total = sum(conf_counts.values())
    for grade in ["A", "B", "C", "D"]:
        count = conf_counts.get(grade, 0)
        pct = count / total * 100 if total > 0 else 0
        lines.append(f"- {grade}: {count} ({pct:.0f}%)")
    lines.append("")

    # Key vocabulary
    word_freq = Counter(all_zfd_words)
    lines.append("## Most Frequent ZFD Words\n")
    for word, count in word_freq.most_common(10):
        if count > 1:
            lines.append(f"- {word}: {count}x")
    lines.append("")

    lines.append(f"\n---\n\n*Notes compiled {datetime.date.today().isoformat()}.*\n")

    return "\n".join(lines)


def write_text(path, text):
    # Explicit UTF-8: notes.md contains "→", which the Windows default
    # (cp1252) cannot encode, so the old open(path, "w") crashed there.
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def process_folio(folio_id, iiif_id, eva_file, output_dir):
    """Process a single folio: extract EVA, parse, generate all files."""
    eva_lines = extract_eva_lines(eva_file, folio_id)
    if not eva_lines:
        print(f"  WARNING: No EVA lines found for {folio_id}")
        return False

    parsed_lines = {ln: parse_line(text) for ln, text in eva_lines.items()}

    folio_dir = os.path.join(output_dir, folio_id)
    os.makedirs(folio_dir, exist_ok=True)

    header = read_page_header(eva_file, folio_id)
    metadata = generate_metadata(folio_id, iiif_id, len(eva_lines), header=header)
    write_text(os.path.join(folio_dir, "metadata.json"),
               json.dumps(metadata, indent=2, ensure_ascii=False) + "\n")
    write_text(os.path.join(folio_dir, "TRANSCRIPTION.md"),
               generate_transcription_md(folio_id, iiif_id, eva_lines, parsed_lines, metadata))
    write_text(os.path.join(folio_dir, "line_data.jsonl"),
               generate_line_data_jsonl(folio_id, eva_lines, parsed_lines))
    write_text(os.path.join(folio_dir, "notes.md"),
               generate_notes_md(folio_id, eva_lines, parsed_lines))

    print(f"  {folio_id}: {len(eva_lines)} lines, files written to {folio_dir}")
    return True


def load_iiif_map(map_file):
    """Load folio-to-IIIF-ID mapping."""
    with open(map_file, encoding="utf-8") as f:
        return json.load(f)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("folios", nargs="*", help="folio ids (default: every IVTFF page with H text)")
    ap.add_argument("--eva", default=str(DEFAULT_EVA))
    ap.add_argument("--iiif-map", default=str(DEFAULT_IIIF))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--skip-existing", action="store_true",
                    help="keep folios that already have output (old default; mixes rule versions)")
    args = ap.parse_args(argv)

    iiif_map = load_iiif_map(args.iiif_map)

    # Default page list comes from the IVTFF source, not the IIIF map. The
    # IIIF map has no entry for the multi-panel pages f70r, f72r, f89r, f95r,
    # f101r and f102r, so building the list from it skipped their text.
    folios = args.folios or sorted(list_ivtff_pages(args.eva), key=folio_sort_key)
    print(f"Processing {len(folios)} folios...")

    success = skipped = 0
    for folio_id in folios:
        if folio_id in ANCHORS:
            print(f"  {folio_id}: hand-transcribed anchor, not overwritten")
            skipped += 1
            continue
        folio_dir = os.path.join(args.out, folio_id)
        if args.skip_existing and os.path.exists(folio_dir) and len(os.listdir(folio_dir)) >= 4:
            print(f"  {folio_id}: already has output, skipping (--skip-existing)")
            skipped += 1
            continue
        iiif_id = iiif_map.get(folio_id, iiif_map.get(folio_id.lstrip('f'), "unknown"))
        if process_folio(folio_id, iiif_id, args.eva, args.out):
            success += 1

    print(f"\nDone: {success} written, {skipped} skipped, {len(folios)} requested.")


if __name__ == "__main__":
    main()
