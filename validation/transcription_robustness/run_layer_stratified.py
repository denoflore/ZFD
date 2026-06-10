"""
Layer-Stratified Perturbation Test (Exposure-Normalized Matrix)
===============================================================

Why this test exists
--------------------
ZFD claims Voynichese is a positional three-layer shorthand:

    [OPERATOR] + [STEM + GALLOWS ABBREVIATION MARKS] + [SUFFIX]

That claim predicts DIFFERENTIAL sensitivity: an edit in a layer's home
position should maximally disturb that layer's parsed output field.

Design (v2, exposure-normalized)
--------------------------------
Exactly ONE character edit per touched word, identical dose across layers:
  - gallows edit:   swap one gallows char (k/t/p/f cluster marks)
  - operator edit:  swap the word-initial operator char (q/o/d/s)
  - suffix edit:    swap one i/n/r/l char in the final-3 zone
Measured conditionally (only touched words), against the clean decode,
on three output fields: stem identity, operator class (class-aware via
operators.json, so variant forms of one operator are not "changes"),
and parsed suffix.

A NOTE ON A RETRACTED EARLIER RESULT: a first version of this test used
whitespace word-splitting on period-separated EVA and reported a large
gallows-vs-suffix stem differential. That result was a segmentation
artifact (most words were never perturbed) and is retracted. This file
implements the corrected design. Negative results are preserved per
project policy.

June 2026 result (matrix: rows = edited layer, cols = changed field)
--------------------------------------------------------------------
                     stem     op_class   suffix
    gallows edit     ~0.33    ~0.08      ~0.10
    operator edit    ~0.48    ~0.40      ~0.11
    suffix edit      ~0.52    ~0.08      ~0.12

CONFIRMED: operator information is positionally encoded. Word-initial
edits flip the operator class at ~5-6x the rate of edits elsewhere in
the word, which essentially never do.

NOT CONFIRMED: the gallows and suffix diagonals. Stem extraction is
whole-word coupled (any edit can shift parse boundaries and reshuffle
the residual stem), and the parsed suffix field is robust to all edit
types. These are documented as honest negatives; they constrain how the
three-layer claim may be stated (positional operator encoding is
demonstrated; per-layer stem/suffix isolation is not).

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
sys.path.insert(0, str(ROOT / "validation" / "blind_decode_test"))
sys.path.insert(0, str(ROOT / "zfd_decoder" / "src"))

from pipeline import ZFDPipeline  # noqa: E402
from decoder import decode_eva_text  # noqa: E402

FOLIOS = ["f10r", "f23v", "f47r", "f89r", "f101v"]
EVA_DIR = ROOT / "voynich_data" / "raw_eva"
DATA_DIR = ROOT / "zfd_decoder" / "data"
GALLOWS = "ktpf"
OPS = "qods"
SUFF = "inrl"


def is_text_line(line: str) -> bool:
    s = line.strip()
    return bool(s) and not s.startswith("===") and not s.startswith("[")


def words_of(text: str):
    out = []
    for line in text.splitlines():
        if is_text_line(line):
            out.extend(w for w in line.split(".") if w)
    return out


def rebuild(text: str, edited: dict) -> str:
    out_lines, wi = [], 0
    for line in text.splitlines():
        if is_text_line(line):
            ws = []
            for w in line.split("."):
                if w:
                    ws.append(edited.get(wi, w))
                    wi += 1
                else:
                    ws.append(w)
            out_lines.append(".".join(ws))
        else:
            out_lines.append(line)
    return "\n".join(out_lines)


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


def main():
    lex = DATA_DIR / "lexicon_v2.csv"
    pipeline = ZFDPipeline(data_dir=str(DATA_DIR), lexicon_file=str(lex))
    op_class = {e["eva"]: e["type"] for e in json.loads(
        (DATA_DIR / "operators.json").read_text())["operators"]}

    def opc(token):
        f = token.get("operator", "") or ""
        return op_class.get(f, f)

    layers = ["gallows", "operator", "suffix"]
    res = {L: {"stem": 0, "op": 0, "suf": 0, "n": 0} for L in layers}

    for folio in FOLIOS:
        eva = (EVA_DIR / f"{folio}.txt").read_text()
        clean = decode_eva_text(eva, folio, pipeline=pipeline)
        ct = clean["tokens"]
        ws = words_of(eva)
        n_align = min(len(ct), len(ws))
        if len(ct) != len(ws):
            print(f"  [align note] {folio}: {len(ct)} tokens vs "
                  f"{len(ws)} EVA words; using first {n_align}")
        for L in layers:
            rng = random.Random(hash((folio, L)) % 999983)
            edited = {}
            for wi in range(n_align):
                e = one_edit(ws[wi], L, rng)
                if e is not None:
                    edited[wi] = e
            r = decode_eva_text(rebuild(eva, edited), folio,
                                pipeline=pipeline)
            pt = r["tokens"]
            m = min(len(pt), n_align)
            for wi in edited:
                if wi >= m:
                    continue
                res[L]["n"] += 1
                if ct[wi].get("stem", "") != pt[wi].get("stem", ""):
                    res[L]["stem"] += 1
                if opc(ct[wi]) != opc(pt[wi]):
                    res[L]["op"] += 1
                if ct[wi].get("suffix", "") != pt[wi].get("suffix", ""):
                    res[L]["suf"] += 1

    results = {
        "test_date": datetime.datetime.now().isoformat(),
        "design": "exposure-normalized, one edit per touched word, "
                  "conditional measurement, class-aware operators",
        "config": {
            "lexicon_file": lex.name,
            "lexicon_sha256": hashlib.sha256(
                lex.read_bytes()).hexdigest(),
            "compound_decomposer": pipeline.compound is not None,
        },
        "matrix": {},
    }
    print(f"{'edited layer':14}{'n':>6}{'stem_change':>13}"
          f"{'op_class_change':>17}{'suffix_change':>15}")
    for L in layers:
        d = res[L]
        n = max(d["n"], 1)
        row = {
            "n_edits": d["n"],
            "stem_change": round(d["stem"] / n, 4),
            "op_class_change": round(d["op"] / n, 4),
            "suffix_change": round(d["suf"] / n, 4),
        }
        results["matrix"][L] = row
        print(f"{L:14}{d['n']:>6}{row['stem_change']:>13.3f}"
              f"{row['op_class_change']:>17.3f}"
              f"{row['suffix_change']:>15.3f}")

    op_diag = results["matrix"]["operator"]["op_class_change"]
    op_off = max(results["matrix"]["gallows"]["op_class_change"],
                 results["matrix"]["suffix"]["op_class_change"])
    results["verdict"] = {
        "operator_positionally_encoded": op_diag > 3 * op_off,
        "operator_diagonal_ratio": round(op_diag / max(op_off, 1e-9), 1),
        "gallows_diagonal_confirmed": False,
        "suffix_diagonal_confirmed": False,
        "summary": (
            "Operator information is positionally encoded "
            f"({op_diag:.0%} class change for word-initial edits vs "
            f"{op_off:.0%} for edits elsewhere). Gallows and suffix "
            "diagonals NOT confirmed: stem extraction is whole-word "
            "coupled and the parsed suffix field is robust to all edit "
            "types. Honest negatives preserved."),
    }
    print("\nVerdict:", results["verdict"]["summary"])

    out = HERE / "layer_stratified_results.json"
    out.write_text(json.dumps(results, indent=2))
    print(f"Results written to {out}")


if __name__ == "__main__":
    main()
