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
Two metrics with deliberately different failure modes:

1. STRUCTURAL robustness (coverage / coherence under noise):
   should stay roughly flat if the morphological system is layered.

2. SEMANTIC sensitivity (stem-identity stability):
   the fraction of tokens that decode to the SAME stem as the clean
   decode. This metric CAN fail, so it can actually prove something.
   - An accept-anything decoder is flat on BOTH metrics.
   - A brittle cipher collapses on BOTH.
   - A layered real system is flat on (1) and degrades roughly
     linearly on (2). That is the fingerprint this test looks for.

Interpretation of the June 2026 run
-----------------------------------
Coverage stays ~0.985 from 0% to 20% noise (structural robustness).
Stem identity degrades linearly: ~0.95 at 5%, ~0.90 at 10%, ~0.81 at 20%
(semantic sensitivity). High-frequency ingredient identifications
(kost, ol) are aggregate counts over thousands of tokens and remain
statistically stable at the worst-case error floor.

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
sys.path.insert(0, str(ROOT / "validation" / "blind_decode_test"))
sys.path.insert(0, str(ROOT / "zfd_decoder" / "src"))

from pipeline import ZFDPipeline  # noqa: E402
from decoder import decode_eva_text  # noqa: E402

FOLIOS = ["f10r", "f23v", "f47r", "f89r", "f101v"]
EVA_DIR = ROOT / "voynich_data" / "raw_eva"
DATA_DIR = ROOT / "zfd_decoder" / "data"
CONFUSION_SET = "inrl"  # documented paleographic confusion class
RATES = [0.05, 0.10, 0.20]  # documented error floor band
ITERS = 20


def perturb(text: str, rate: float, rng: random.Random) -> str:
    out = []
    for ch in text:
        if ch in CONFUSION_SET and rng.random() < rate:
            out.append(rng.choice([c for c in CONFUSION_SET if c != ch]))
        else:
            out.append(ch)
    return "".join(out)


def main():
    # Pin the current shipping configuration explicitly.
    lex = DATA_DIR / "lexicon_v2.csv"
    pipeline = ZFDPipeline(data_dir=str(DATA_DIR), lexicon_file=str(lex))

    results = {
        "test_date": datetime.datetime.now().isoformat(),
        "config": {
            "lexicon_file": lex.name,
            "lexicon_sha256": hashlib.sha256(lex.read_bytes()).hexdigest(),
            "compound_decomposer": pipeline.compound is not None,
        },
        "confusion_set": CONFUSION_SET,
        "rates": RATES,
        "iterations": ITERS,
        "folios": {},
    }

    print(f"{'folio':8}{'rate':>6}{'coverage':>10}{'coherence':>11}"
          f"{'stem_stable':>13}{'gloss_stable':>14}")
    for folio in FOLIOS:
        eva = (EVA_DIR / f"{folio}.txt").read_text()
        clean = decode_eva_text(eva, folio, pipeline=pipeline)
        clean_stems = [t.get("stem", "") for t in clean["tokens"]]
        clean_gloss = [t.get("stem_gloss", "") for t in clean["tokens"]]
        fentry = {
            "clean_coverage": round(clean["known_ratio"], 4),
            "clean_coherence": round(clean["coherence"], 4),
            "rates": {},
        }
        for rate in RATES:
            cov, coh, stem_s, gloss_s = [], [], [], []
            for i in range(ITERS):
                rng = random.Random(7919 * i + hash(folio) % 104729)
                r = decode_eva_text(perturb(eva, rate, rng), folio,
                                    pipeline=pipeline)
                cov.append(r["known_ratio"])
                coh.append(r["coherence"])
                ps = [t.get("stem", "") for t in r["tokens"]]
                pg = [t.get("stem_gloss", "") for t in r["tokens"]]
                n = min(len(ps), len(clean_stems))
                stem_s.append(sum(a == b for a, b in
                                  zip(ps[:n], clean_stems[:n])) / n)
                gloss_s.append(sum(a == b for a, b in
                                   zip(pg[:n], clean_gloss[:n])) / n)
            row = {
                "coverage_mean": round(statistics.mean(cov), 4),
                "coherence_mean": round(statistics.mean(coh), 4),
                "stem_identity_mean": round(statistics.mean(stem_s), 4),
                "stem_identity_std": round(statistics.pstdev(stem_s), 4),
                "gloss_identity_mean": round(statistics.mean(gloss_s), 4),
            }
            fentry["rates"][str(rate)] = row
            print(f"{folio:8}{rate:>6.2f}{row['coverage_mean']:>10.3f}"
                  f"{row['coherence_mean']:>11.3f}"
                  f"{row['stem_identity_mean']:>13.3f}"
                  f"{row['gloss_identity_mean']:>14.3f}")
        results["folios"][folio] = fentry

    # Aggregate fingerprint check
    agg = {}
    for rate in RATES:
        agg[str(rate)] = {
            "coverage": round(statistics.mean(
                results["folios"][f]["rates"][str(rate)]["coverage_mean"]
                for f in FOLIOS), 4),
            "stem_identity": round(statistics.mean(
                results["folios"][f]["rates"][str(rate)]["stem_identity_mean"]
                for f in FOLIOS), 4),
        }
    results["aggregate"] = agg
    clean_cov = statistics.mean(
        results["folios"][f]["clean_coverage"] for f in FOLIOS)
    structural_flat = all(
        abs(agg[str(r)]["coverage"] - clean_cov) < 0.02 for r in RATES)
    semantic_graded = (agg["0.05"]["stem_identity"]
                       > agg["0.1"]["stem_identity"]
                       > agg["0.2"]["stem_identity"])
    results["fingerprint"] = {
        "structural_flat": structural_flat,
        "semantic_graded_degradation": semantic_graded,
        "verdict": ("LAYERED-REAL-SYSTEM" if structural_flat
                    and semantic_graded else "CHECK-FAILED"),
    }
    print("\nAggregate:", json.dumps(agg, indent=1))
    print("Fingerprint verdict:", results["fingerprint"]["verdict"])

    out = HERE / "robustness_results.json"
    out.write_text(json.dumps(results, indent=2))
    print(f"Results written to {out}")


if __name__ == "__main__":
    main()
