"""
Decoy Language Test (Tier 1: Fixed Key, Swapped Dictionary)
===========================================================

The criticism this test answers
-------------------------------
"Any sufficiently flexible morpheme lexicon will 'decode' Voynichese into
whatever language you aimed it at."

Design
------
The EVA -> phoneme key is HELD FIXED (it is motivated independently by
Glagolitic paleography: the 19-character map, gallows cluster expansions
k->st t->tr f->pr p->pl, operator prefixes, suffix codebook). The ZFD
Croatian lexicon is NOT used anywhere in this test. Every Voynich word
type in the full 201-folio corpus is transliterated through the frozen
key into a phoneme string, then matched against SEVEN independent
dictionaries under byte-identical rules:

    Croatian (hr), Slovenian (sl), Czech (cs), Slovak (sk),
    Polish (pl), Italian (it), Latin (la)

Slovenian is the cruelest control (South Slavic neighbor). Czech/Slovak/
Polish are West Slavic controls. Italian/Latin are the Romance/regional
controls a Dalmatian-coast hypothesis must beat.

Dictionary-size fairness
------------------------
Bigger dictionaries match more random strings. Every language is
therefore calibrated against its OWN null: the identical machinery run
on character-shuffled versions of the same word types. The headline
statistic is LIFT = real match rate / shuffled match rate, per language,
with bootstrap confidence intervals over word types. Lift cancels
dictionary size and promiscuity.

Matching rules (identical for every language)
---------------------------------------------
For each EVA word type, candidate phoneme strings are generated from the
frozen key: optional operator-prefix strip x optional suffix strip x
gallows literal/expanded, transliterated, ASCII-folded, core length >= 3.
A word matches a language if ANY candidate is an EXACT dictionary word,
or (PREFIX4 rule) a candidate of length >= 4 is a prefix of a dictionary
word. Exact and prefix tiers are reported separately.

Usage:
    python validation/decoy_language_test/run_decoy_test.py
"""

import sys
import json
import random
import hashlib
import unicodedata
import statistics
import datetime
from bisect import bisect_left
from pathlib import Path
from collections import Counter

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
EVA_DIR = ROOT / "voynich_data" / "raw_eva"
DATA_DIR = ROOT / "zfd_decoder" / "data"
DICT_DIR = Path(__file__).parent / "dictionaries"

# ---------------------------------------------------------------------------
# The frozen key (from 06_Pipelines/glagolitic_ocr/character_reference.py and
# zfd_decoder/data/gallows.json; suffix codebook from MasterKey_v1_parameters)
# ---------------------------------------------------------------------------
CHAR_KEY = {
    "ch": "h", "sh": "š",
    "a": "a", "e": "e", "i": "i", "o": "o", "y": "i",
    "g": "g", "d": "d", "k": "k", "p": "p", "t": "t",
    "s": "s", "f": "f", "c": "c", "l": "l", "m": "m",
    "n": "n", "r": "r",
}
GALLOWS_EXPANSION = {"k": "st", "t": "tr", "f": "pr", "p": "pl"}
SUFFIX_CODEBOOK = ["dy", "in", "an", "ol", "al", "um", "us",
                   "nt", "la", "pl", "ts", "ro", "lf", "y"]
NULL_SHUFFLES = 3
BOOTSTRAP = 500
MIN_CORE = 3


def load_operator_prefixes():
    ops = json.loads((DATA_DIR / "operators.json").read_text())
    forms = sorted({e["eva"] for e in ops["operators"]},
                   key=len, reverse=True)
    return forms


OPERATOR_PREFIXES = load_operator_prefixes()


def fold(s: str) -> str:
    """Uniform ASCII fold + lowercase, applied to candidates AND
    dictionary words alike."""
    s = s.lower().replace("đ", "d")
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if c.isascii() and c.isalpha())


def transliterate(eva: str) -> str:
    out, i = [], 0
    while i < len(eva):
        if eva[i:i + 2] in CHAR_KEY:
            out.append(CHAR_KEY[eva[i:i + 2]])
            i += 2
        else:
            out.append(CHAR_KEY.get(eva[i], eva[i]))
            i += 1
    return "".join(out)


def expand_gallows(eva: str) -> str:
    return "".join(GALLOWS_EXPANSION.get(c, c) for c in eva)


def candidates(eva_word: str) -> set:
    """All candidate phoneme strings for one EVA word under the frozen
    key. Identical generation for every target language."""
    bases = {eva_word}
    for op in OPERATOR_PREFIXES:
        if eva_word.startswith(op) and len(eva_word) - len(op) >= MIN_CORE:
            bases.add(eva_word[len(op):])
            break  # longest-match operator strip only
    with_suffix = set(bases)
    for b in bases:
        for suf in SUFFIX_CODEBOOK:
            if b.endswith(suf) and len(b) - len(suf) >= MIN_CORE:
                with_suffix.add(b[:-len(suf)])
                break  # longest-match suffix strip only
    cands = set()
    for b in with_suffix:
        for variant in (b, expand_gallows(b)):
            ph = fold(transliterate(variant))
            if len(ph) >= MIN_CORE:
                cands.add(ph)
    return cands


class Dictionary:
    def __init__(self, name: str, path: Path, encodings=("utf-8",
                                                         "iso-8859-2",
                                                         "latin-1")):
        raw = path.read_bytes()
        for enc in encodings:
            try:
                txt = raw.decode(enc)
                break
            except UnicodeDecodeError:
                continue
        words = set()
        for line in txt.splitlines()[1:]:
            w = line.split("/")[0].split("\t")[0].strip()
            w = fold(w)
            if len(w) >= MIN_CORE:
                words.add(w)
        self.name = name
        self.words = words
        self.sorted = sorted(words)
        self.sha256 = hashlib.sha256(raw).hexdigest()

    def match(self, cand: str):
        exact = cand in self.words
        prefix = False
        if not exact and len(cand) >= 4:
            i = bisect_left(self.sorted, cand)
            if i < len(self.sorted) and self.sorted[i].startswith(cand):
                prefix = True
        return exact, (exact or prefix)


def corpus_word_types():
    counts = Counter()
    for f in sorted(EVA_DIR.glob("*.txt")):
        for line in f.read_text().splitlines():
            s = line.strip()
            if not s or s.startswith("===") or s.startswith("["):
                continue
            for w in s.split("."):
                w = w.strip()
                if w and w.isalpha():
                    counts[w] += 1
    return counts


def main():
    counts = corpus_word_types()
    types = sorted(counts)
    print(f"corpus: {sum(counts.values())} tokens, {len(types)} types "
          f"from {len(list(EVA_DIR.glob('*.txt')))} folios")

    langs = {}
    for name, fn in [("croatian", "hr_HR.dic"), ("slovenian", "sl_SI.dic"),
                     ("czech", "cs_CZ.dic"), ("slovak", "sk_SK.dic"),
                     ("polish", "pl_PL.dic"), ("italian", "it_IT.dic"),
                     ("latin", "la_words.txt")]:
        langs[name] = Dictionary(name, DICT_DIR / fn)
        print(f"  dict {name}: {len(langs[name].words)} entries")

    # Real and null candidate sets per type
    rng = random.Random(20260609)
    real_c = {t: candidates(t) for t in types}
    null_c = {}
    for t in types:
        shuf = []
        for _ in range(NULL_SHUFFLES):
            chars = list(t)
            rng.shuffle(chars)
            shuf.append("".join(chars))
        null_c[t] = [candidates(s) for s in shuf]

    # Per-type, per-language match booleans
    results = {"exact": {}, "prefix4": {}}
    matrix = {}
    for lname, d in langs.items():
        re_ex, re_pf = [], []
        nu_ex, nu_pf = [], []
        for t in types:
            ex = pf = False
            for c in real_c[t]:
                e, p = d.match(c)
                ex |= e
                pf |= p
            re_ex.append(ex)
            re_pf.append(pf)
            nx = np_ = 0.0
            for cset in null_c[t]:
                sx = sp = False
                for c in cset:
                    e, p = d.match(c)
                    sx |= e
                    sp |= p
                nx += sx
                np_ += sp
            nu_ex.append(nx / NULL_SHUFFLES)
            nu_pf.append(np_ / NULL_SHUFFLES)
        matrix[lname] = (re_ex, re_pf, nu_ex, nu_pf)

    weights = [counts[t] for t in types]
    tot_w = sum(weights)
    out = {
        "test_date": datetime.datetime.now().isoformat(),
        "design": "Tier 1 decoy: frozen EVA->phoneme key, swapped "
                  "dictionaries, per-language shuffled-null lift",
        "corpus": {"tokens": tot_w, "types": len(types),
                   "folios": len(list(EVA_DIR.glob("*.txt")))},
        "frozen_key": {"char_key": CHAR_KEY,
                       "gallows": GALLOWS_EXPANSION,
                       "suffixes": SUFFIX_CODEBOOK,
                       "operator_prefixes": OPERATOR_PREFIXES},
        "languages": {},
    }

    idx = list(range(len(types)))
    rngb = random.Random(424242)
    print(f"\n{'language':11}{'dict':>8}{'exact%':>8}{'null%':>7}"
          f"{'lift':>6}{'pfx4%':>7}{'null%':>7}{'lift':>6}"
          f"{'  lift 95% CI (pfx4)':>22}")
    for lname, (re_ex, re_pf, nu_ex, nu_pf) in matrix.items():
        r_ex = sum(b * w for b, w in zip(re_ex, weights)) / tot_w
        r_pf = sum(b * w for b, w in zip(re_pf, weights)) / tot_w
        n_ex = sum(v * w for v, w in zip(nu_ex, weights)) / tot_w
        n_pf = sum(v * w for v, w in zip(nu_pf, weights)) / tot_w
        lift_ex = r_ex / n_ex if n_ex else float("inf")
        lift_pf = r_pf / n_pf if n_pf else float("inf")
        boots = []
        for _ in range(BOOTSTRAP):
            sample = [idx[int(rngb.random() * len(idx))]
                      for _ in range(len(idx))]
            rw = sum(re_pf[i] * weights[i] for i in sample)
            nw = sum(nu_pf[i] * weights[i] for i in sample)
            if nw:
                boots.append(rw / nw)
        boots.sort()
        lo = boots[int(0.025 * len(boots))]
        hi = boots[int(0.975 * len(boots))]
        out["languages"][lname] = {
            "dict_size": len(langs[lname].words),
            "dict_sha256": langs[lname].sha256,
            "token_weighted": {
                "exact_rate": round(r_ex, 4),
                "exact_null": round(n_ex, 4),
                "exact_lift": round(lift_ex, 3),
                "prefix4_rate": round(r_pf, 4),
                "prefix4_null": round(n_pf, 4),
                "prefix4_lift": round(lift_pf, 3),
                "prefix4_lift_ci95": [round(lo, 3), round(hi, 3)],
            },
        }
        print(f"{lname:11}{len(langs[lname].words):>8}{r_ex*100:>8.2f}"
              f"{n_ex*100:>7.2f}{lift_ex:>6.2f}{r_pf*100:>7.2f}"
              f"{n_pf*100:>7.2f}{lift_pf:>6.2f}"
              f"   [{lo:.2f}, {hi:.2f}]")

    hr = out["languages"]["croatian"]["token_weighted"]["prefix4_lift"]
    others = {k: v["token_weighted"]["prefix4_lift"]
              for k, v in out["languages"].items() if k != "croatian"}
    out["verdict"] = {
        "croatian_lift": hr,
        "best_decoy": max(others, key=others.get),
        "best_decoy_lift": max(others.values()),
        "croatian_beats_all_decoys": hr > max(others.values()),
    }
    print("\nVerdict:", json.dumps(out["verdict"], indent=1))
    (HERE / "decoy_results.json").write_text(json.dumps(out, indent=2))
    print(f"Results written to {HERE / 'decoy_results.json'}")


if __name__ == "__main__":
    main()
