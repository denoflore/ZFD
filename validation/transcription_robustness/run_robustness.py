"""
Transcription Robustness Test: i/n/r/l Confusion Injection
==========================================================

Motivation
----------
EVA transcriptions impose discrete Latin-alphabet segmentation on a
connected cursive script with hooks, loops, and modifiers. The ZFD
paleographic hand analysis (Feb 2026) documented an inherent 5-20%
i/n/r/l confusion floor at manuscript resolution. Any transcription-based
result must therefore survive its own error band.

What this test measures
-----------------------
1. STRUCTURAL robustness: coverage (known_ratio) under noise.
2. SEMANTIC sensitivity: fraction of tokens that decode to the SAME stem
   as the clean decode.

CORRECTION (2026-11 audit). The original docstring said an accept-anything
decoder is flat on both metrics, so "flat coverage + graded stem decay"
fingerprints a layered real system. That is false. Any decoder that
accepts a fixed share of strings and derives its stem from the input
shows exactly that pattern: coverage stays at its acceptance rate, and
stem identity falls with the noise rate because the input changed. A
coin-flip null decoder (stem = the raw word) earned the old
LAYERED-REAL-SYSTEM verdict. The verdict now requires the real decoder to
pass AND the null to fail; otherwise it reports NON-DISCRIMINATING. The
null's numbers and a glyph-shuffled gibberish coverage control are written
next to the real ones so the gap (if any) is visible.

Other 2026-11 fixes: seeds no longer use the per-process randomized
hash(); header lines and <...> markup are stripped before decoding and
before noise injection (they used to become tokens: "folio", "text",
"dyplantchy").

The June 2026 numbers that used to be quoted here came from the old
harness. Current numbers live in robustness_results.json.

Usage:
    python validation/transcription_robustness/run_robustness.py
"""

import sys
import json
import random
import statistics
import datetime
import hashlib
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "validation" / "blind_decode_test"))
sys.path.insert(0, str(ROOT / "zfd_decoder" / "src"))

from _common import stable_seed, clean_folio_text, shuffle_glyphs  # noqa: E402
from pipeline import ZFDPipeline  # noqa: E402
from decoder import decode_eva_text  # noqa: E402
from tokenizer import tokenize_folio  # noqa: E402

FOLIOS = ["f10r", "f23v", "f47r", "f89r", "f101v"]
EVA_DIR = ROOT / "voynich_data" / "raw_eva"
DATA_DIR = ROOT / "zfd_decoder" / "data"
CONFUSION_SET = "inrl"  # documented paleographic confusion class
RATES = [0.05, 0.10, 0.20]  # documented error floor band
ITERS = 20


def perturb(text: str, rate: float, rng: random.Random) -> str:
    """Swap i/n/r/l glyphs. Expects markup-free text from clean_folio_text."""
    out = []
    for ch in text:
        if ch in CONFUSION_SET and rng.random() < rate:
            out.append(rng.choice([c for c in CONFUSION_SET if c != ch]))
        else:
            out.append(ch)
    return "".join(out)


def make_null_decoder(accept_rate: float):
    """Zero-content control: 'known' is a coin flip keyed on the string,
    at the real decoder's clean acceptance rate; stem = the raw word."""
    cut = int(round(accept_rate * 1000))

    def null_decode(eva_text, folio, pipeline=None):
        toks = [t.eva for line in tokenize_folio(eva_text, folio) for t in line]
        known = [int(hashlib.sha1(w.encode()).hexdigest(), 16) % 1000 < cut for w in toks]
        kr = sum(known) / len(toks) if toks else 0.0
        return {"known_ratio": kr, "coherence": kr,
                "tokens": [{"stem": w, "stem_gloss": w if k else ""} for w, k in zip(toks, known)]}
    return null_decode


def run_decoder(decode, eva, folio, pipeline):
    clean = decode(eva, folio, pipeline=pipeline)
    clean_stems = [t.get("stem", "") for t in clean["tokens"]]
    clean_gloss = [t.get("stem_gloss", "") for t in clean["tokens"]]
    entry = {"clean_coverage": round(clean["known_ratio"], 4),
             "clean_coherence": round(clean["coherence"], 4), "rates": {}}
    for rate in RATES:
        cov, coh, stem_s, gloss_s = [], [], [], []
        for i in range(ITERS):
            rng = random.Random(stable_seed(folio, rate, i))
            r = decode(perturb(eva, rate, rng), folio, pipeline=pipeline)
            cov.append(r["known_ratio"])
            coh.append(r["coherence"])
            ps = [t.get("stem", "") for t in r["tokens"]]
            pg = [t.get("stem_gloss", "") for t in r["tokens"]]
            # perturb() never touches "." so token counts match
            assert len(ps) == len(clean_stems), (folio, len(ps), len(clean_stems))
            n = len(ps) or 1
            stem_s.append(sum(a == b for a, b in zip(ps, clean_stems)) / n)
            gloss_s.append(sum(a == b for a, b in zip(pg, clean_gloss)) / n)
        entry["rates"][str(rate)] = {
            "coverage_mean": round(statistics.mean(cov), 4),
            "coherence_mean": round(statistics.mean(coh), 4),
            "stem_identity_mean": round(statistics.mean(stem_s), 4),
            "stem_identity_std": round(statistics.pstdev(stem_s), 4),
            "gloss_identity_mean": round(statistics.mean(gloss_s), 4),
        }
    return entry


def fingerprint(folios: dict):
    agg = {str(r): {
        "coverage": round(statistics.mean(folios[f]["rates"][str(r)]["coverage_mean"] for f in folios), 4),
        "stem_identity": round(statistics.mean(folios[f]["rates"][str(r)]["stem_identity_mean"] for f in folios), 4),
    } for r in RATES}
    clean_cov = statistics.mean(folios[f]["clean_coverage"] for f in folios)
    keys = [str(r) for r in RATES]
    flat = all(abs(agg[k]["coverage"] - clean_cov) < 0.02 for k in keys)
    graded = all(agg[a]["stem_identity"] > agg[b]["stem_identity"] for a, b in zip(keys, keys[1:]))
    return agg, flat, graded


def main():
    lex = DATA_DIR / "lexicon_v2.csv"
    pipeline = ZFDPipeline(data_dir=str(DATA_DIR), lexicon_file=str(lex))

    results = {
        "test_date": datetime.datetime.now().isoformat(),
        "config": {
            "lexicon_file": lex.name,
            "lexicon_sha256": hashlib.sha256(lex.read_bytes()).hexdigest(),
            "compound_decomposer": pipeline.compound is not None,
            "seeding": "sha256(folio|rate|iter)",
            "input": "raw_eva text lines, markup and '!' fillers stripped",
        },
        "confusion_set": CONFUSION_SET,
        "rates": RATES,
        "iterations": ITERS,
        "folios": {},
        "null_folios": {},
        "gibberish_coverage": {},
    }

    texts = {f: clean_folio_text((EVA_DIR / f"{f}.txt").read_text(encoding="utf-8")) for f in FOLIOS}

    print(f"{'folio':8}{'rate':>6}{'coverage':>10}{'stem_stable':>13}{'null_stem':>11}")
    for folio in FOLIOS:
        real = run_decoder(decode_eva_text, texts[folio], folio, pipeline)
        null = run_decoder(make_null_decoder(real["clean_coverage"]), texts[folio], folio, None)
        gib = decode_eva_text(shuffle_glyphs(texts[folio], random.Random(stable_seed(folio, "shuffle"))),
                              folio, pipeline=pipeline)["known_ratio"]
        results["folios"][folio] = real
        results["null_folios"][folio] = null
        results["gibberish_coverage"][folio] = {"real_text": real["clean_coverage"],
                                                "glyph_shuffled": round(gib, 4)}
        for rate in RATES:
            r, n = real["rates"][str(rate)], null["rates"][str(rate)]
            print(f"{folio:8}{rate:>6.2f}{r['coverage_mean']:>10.3f}"
                  f"{r['stem_identity_mean']:>13.3f}{n['stem_identity_mean']:>11.3f}")

    agg, flat, graded = fingerprint(results["folios"])
    nagg, nflat, ngraded = fingerprint(results["null_folios"])
    real_pass = flat and graded
    null_pass = nflat and ngraded
    results["aggregate"] = agg
    results["null_aggregate"] = nagg
    results["fingerprint"] = {
        "structural_flat": flat,
        "semantic_graded_degradation": graded,
        "null_structural_flat": nflat,
        "null_semantic_graded_degradation": ngraded,
        "stem_identity_real_minus_null": {k: round(agg[k]["stem_identity"] - nagg[k]["stem_identity"], 4)
                                          for k in agg},
        "verdict": ("LAYERED-REAL-SYSTEM" if real_pass and not null_pass
                    else "NON-DISCRIMINATING" if real_pass and null_pass
                    else "CHECK-FAILED"),
    }
    print("\nAggregate:", json.dumps(agg))
    print("Null aggregate:", json.dumps(nagg))
    print("Gibberish coverage:", json.dumps(results["gibberish_coverage"]))
    print("Fingerprint verdict:", results["fingerprint"]["verdict"])

    out = HERE / "robustness_results.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Results written to {out}")


if __name__ == "__main__":
    main()
