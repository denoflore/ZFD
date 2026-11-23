"""
Layer-Stratified Perturbation Test (Exposure-Normalized Matrix)
===============================================================

Why this test exists
--------------------
ZFD claims Voynichese is a positional three-layer shorthand:

    [OPERATOR] + [STEM + GALLOWS ABBREVIATION MARKS] + [SUFFIX]

That claim predicts DIFFERENTIAL sensitivity: an edit in a layer's home
position should maximally disturb that layer's parsed output field.

Design (v3, aligned)
--------------------
Exactly ONE character edit per touched word, identical dose across layers:
  - gallows edit:   swap one gallows char (k/t/p/f cluster marks)
  - operator edit:  swap the word-initial operator char (q/o/d/s)
  - suffix edit:    swap one i/n/r/l char in the final-3 zone
Each edited word is decoded with pipeline.process_token and compared to
the clean decode OF THE SAME WORD (process_token is context-free, so this
equals the folio decode). Fields: stem identity, operator class
(class-aware via operators.json), parsed suffix.

Control: the same matrix on glyph-shuffled gibberish (same word lengths
and glyph inventory). A diagonal only counts as evidence about the
manuscript if it is stronger on the real text than on gibberish; a
diagonal that gibberish also shows is a property of the parser.

RETRACTION 1 (kept per project policy): a first version used whitespace
word-splitting on period-separated EVA and reported a large
gallows-vs-suffix stem differential. That was a segmentation artifact.

RETRACTION 2 (2026-11 audit): v2 compared decoder token i with EVA word i.
The decoder tokenizes the header ("=== Folio f10r ===" -> "folio", "fr";
"[Text]" -> "text") and some comment-only fields as tokens, so token i was
EVA word i-3 at the start of every folio, drifting further as comment-only
fields added tokens (up to 12 positions on f89r). Every v2 measurement
looked at a word several positions BEFORE the one that was edited. The v2 matrix
(operator class change ~0.40 vs ~0.08, "5-6x") is an alignment artifact.
Aligned, the real-text operator ratio is about 3.0-3.3x across seeds, and
glyph-shuffled gibberish gives 10-13x: word-initial edits flip the
operator class because the parser reads the operator from the word
start, whatever the text is. Gallows edits also flip the operator ~25% of
the time on real text (ok/ot operators contain a gallows), so "edits
elsewhere essentially never do" does not hold. Current numbers live in
layer_stratified_results.json.

Usage:
    python validation/transcription_robustness/run_layer_stratified.py
"""

import sys
import json
import random
import hashlib
import datetime
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "zfd_decoder" / "src"))

from _common import stable_seed, clean_folio_text, words_of, shuffle_glyphs  # noqa: E402
from pipeline import ZFDPipeline  # noqa: E402
from tokenizer import Token  # noqa: E402

FOLIOS = ["f10r", "f23v", "f47r", "f89r", "f101v"]
EVA_DIR = ROOT / "voynich_data" / "raw_eva"
DATA_DIR = ROOT / "zfd_decoder" / "data"
GALLOWS = "ktpf"
OPS = "qods"
SUFF = "inrl"
LAYERS = ["gallows", "operator", "suffix"]
HOME_FIELD = {"gallows": "stem_change", "operator": "op_class_change", "suffix": "suffix_change"}
DIAGONAL_RATIO = 3.0


def one_edit(w: str, layer: str, rng: random.Random):
    """Exactly one character edit in the layer's home position.
    Returns the edited word, or None if the word is not eligible."""
    if layer == "gallows":
        sites = [i for i, c in enumerate(w) if c in GALLOWS]
        if not sites:
            return None
        i = rng.choice(sites)
        return w[:i] + rng.choice(
            [c for c in GALLOWS if c != w[i]]) + w[i + 1:]
    if layer == "operator":
        if not w or w[0] not in OPS:
            return None
        return rng.choice([c for c in OPS if c != w[0]]) + w[1:]
    if layer == "suffix":
        zone = range(max(0, len(w) - 3), len(w))
        sites = [i for i in zone if w[i] in SUFF]
        if not sites:
            return None
        i = rng.choice(sites)
        return w[:i] + rng.choice(
            [c for c in SUFF if c != w[i]]) + w[i + 1:]
    raise ValueError(layer)


def run_matrix(pipeline, op_class, folio_words, tag):
    def decode(w):
        return pipeline.process_token(Token(id="x", eva=w))

    def opc(t):
        f = t.operator or ""
        return op_class.get(f, f)

    res = {L: {"stem": 0, "op": 0, "suf": 0, "n": 0} for L in LAYERS}
    for folio, ws in folio_words.items():
        for L in LAYERS:
            rng = random.Random(stable_seed(tag, folio, L))
            for w in ws:
                e = one_edit(w, L, rng)
                if e is None:
                    continue
                a, b = decode(w), decode(e)
                d = res[L]
                d["n"] += 1
                d["stem"] += a.stem != b.stem
                d["op"] += opc(a) != opc(b)
                d["suf"] += (a.suffix or "") != (b.suffix or "")
    matrix = {}
    for L in LAYERS:
        d = res[L]
        n = max(d["n"], 1)
        matrix[L] = {"n_edits": d["n"],
                     "stem_change": round(d["stem"] / n, 4),
                     "op_class_change": round(d["op"] / n, 4),
                     "suffix_change": round(d["suf"] / n, 4)}
    return matrix


def diagonal_ratios(matrix):
    out = {}
    for L in LAYERS:
        field = HOME_FIELD[L]
        diag = matrix[L][field]
        off = max(matrix[o][field] for o in LAYERS if o != L)
        out[L] = round(diag / max(off, 1e-9), 2)
    return out


def main():
    lex = DATA_DIR / "lexicon_v2.csv"
    pipeline = ZFDPipeline(data_dir=str(DATA_DIR), lexicon_file=str(lex))
    op_class = {e["eva"]: e["type"] for e in json.loads(
        (DATA_DIR / "operators.json").read_text(encoding="utf-8"))["operators"]}

    real_words, gib_words = {}, {}
    for folio in FOLIOS:
        text = clean_folio_text((EVA_DIR / f"{folio}.txt").read_text(encoding="utf-8"))
        real_words[folio] = words_of(text)
        gib_words[folio] = words_of(shuffle_glyphs(text, random.Random(stable_seed(folio, "shuffle"))))

    real = run_matrix(pipeline, op_class, real_words, "real")
    gib = run_matrix(pipeline, op_class, gib_words, "gibberish")
    r_ratio, g_ratio = diagonal_ratios(real), diagonal_ratios(gib)

    verdict = {}
    for L in LAYERS:
        passes = r_ratio[L] > DIAGONAL_RATIO
        verdict[L] = {
            "real_ratio": r_ratio[L],
            "gibberish_ratio": g_ratio[L],
            "diagonal_on_real_text": passes,
            "evidence_about_manuscript": passes and r_ratio[L] > g_ratio[L],
        }

    results = {
        "test_date": datetime.datetime.now().isoformat(),
        "design": "v3: one edit per touched word, per-word aligned decode, "
                  "class-aware operators, glyph-shuffled gibberish control",
        "config": {
            "lexicon_file": lex.name,
            "lexicon_sha256": hashlib.sha256(lex.read_bytes()).hexdigest(),
            "compound_decomposer": pipeline.compound is not None,
            "seeding": "sha256(tag|folio|layer)",
            "diagonal_ratio_threshold": DIAGONAL_RATIO,
        },
        "matrix": real,
        "gibberish_matrix": gib,
        "verdict": verdict,
    }

    for name, m in [("REAL", real), ("GIBBERISH", gib)]:
        print(f"\n{name}\n{'edited layer':14}{'n':>6}{'stem_change':>13}"
              f"{'op_class_change':>17}{'suffix_change':>15}")
        for L in LAYERS:
            row = m[L]
            print(f"{L:14}{row['n_edits']:>6}{row['stem_change']:>13.3f}"
                  f"{row['op_class_change']:>17.3f}{row['suffix_change']:>15.3f}")
    print("\nDiagonal ratios (home-field change / max other-layer change):")
    for L in LAYERS:
        v = verdict[L]
        print(f"  {L:9} real {v['real_ratio']:>6}x  gibberish {v['gibberish_ratio']:>6}x  "
              f"evidence about manuscript: {v['evidence_about_manuscript']}")

    out = HERE / "layer_stratified_results.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Results written to {out}")


if __name__ == "__main__":
    main()
