"""
Blind Decode Test v3: Dual-Configuration Vocabulary Specificity Audit
=====================================================================

Why v3 exists
-------------
The v2 test (Feb 2026) PASSED under a configuration that the shipping
pipeline no longer runs by default. Two post-publication changes silently
altered the validation config:

  1. ZFDPipeline auto-prefers lexicon_v2.csv when it exists
     (the v2 test ran against the frozen lexicon.csv, SHA 9c5e62...).
  2. The CompoundDecomposer auto-enables when unified_lexicon_v2.json
     exists (the v2 test ran without it).

v3 fixes this class of failure permanently:
  - Every configuration is EXPLICIT (lexicon file + compound flag).
  - Lexicon SHA-256 is ASSERTED at load time, not just documented.
  - The full configuration is stamped into every results record.
  - Both the frozen (Feb 2026) and current (shipping) configurations
    are run side by side, against identical baseline generators.

Honest interpretation contract
------------------------------
Absolute coverage is NOT evidence. Under the permissive current config,
character-shuffled gibberish reaches ~94% coverage. The evidential weight
of this test lives in the real-vs-null DELTAS, their statistical
significance, and the preserved ordering hierarchy:
    real > char_shuffled > synthetic_eva > random_latin

Usage:
    python validation/blind_decode_test/run_test_v3.py            # 30 iters
    python validation/blind_decode_test/run_test_v3.py --quick    # 10 iters
"""

import sys
import json
import hashlib
import statistics
import datetime
import argparse
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "zfd_decoder" / "src"))

from pipeline import ZFDPipeline  # noqa: E402
from decoder import decode_eva_text  # noqa: E402
from v2_generators import (  # noqa: E402
    generate_synthetic_eva,
    generate_char_shuffled,
    generate_random_latin,
)

FOLIOS = ["f10r", "f23v", "f47r", "f89r", "f101v"]
EVA_DIR = ROOT / "voynich_data" / "raw_eva"  # ships with the repo
DATA_DIR = ROOT / "zfd_decoder" / "data"

GENERATORS = {
    "char_shuffled": generate_char_shuffled,
    "synthetic_eva": generate_synthetic_eva,
    "random_latin": generate_random_latin,
}

# ---------------------------------------------------------------------------
# Pinned configurations. SHAs are asserted, not assumed.
# ---------------------------------------------------------------------------
CONFIGS = {
    "frozen_feb2026": {
        "description": "Configuration of the published v2 test (Feb 2026): "
                       "frozen v1 lexicon, no compound decomposition.",
        "lexicon_file": "lexicon.csv",
        "lexicon_sha256": "9c5e62619b00e3a3a357478404506ad729651146"
                          "faf892282a891bedc4be79b0",
        "compound_decomposer": False,
    },
    "current_shipping": {
        "description": "Default shipping configuration (auto-selected by "
                       "ZFDPipeline): lexicon_v2.csv + compound decomposer.",
        "lexicon_file": "lexicon_v2.csv",
        "lexicon_sha256": "68fb55f2b4c7725b300cab5c438d7abbc25837f5"
                          "a6b8a499747193241423741b",
        "compound_decomposer": True,
    },
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def build_pipeline(config: dict) -> ZFDPipeline:
    """Construct a pipeline with the EXACT pinned configuration.

    Raises if the on-disk lexicon does not match the pinned SHA-256.
    """
    lex_path = DATA_DIR / config["lexicon_file"]
    actual = sha256_file(lex_path)
    if actual != config["lexicon_sha256"]:
        raise RuntimeError(
            f"LEXICON SHA MISMATCH for {lex_path.name}:\n"
            f"  pinned: {config['lexicon_sha256']}\n"
            f"  actual: {actual}\n"
            f"Refusing to run: results would not be attributable to a "
            f"known configuration. Re-pin deliberately if the lexicon "
            f"changed on purpose."
        )
    p = ZFDPipeline(data_dir=str(DATA_DIR), lexicon_file=str(lex_path))
    if not config["compound_decomposer"]:
        p.compound = None
    return p


def empirical_p(real_value: float, baseline_values: list) -> float:
    """Empirical one-tailed p: P(baseline >= real)."""
    n = len(baseline_values)
    ge = sum(1 for v in baseline_values if v >= real_value)
    return (ge + 1) / (n + 1)


def run_config(name: str, config: dict, iters: int) -> dict:
    pipeline = build_pipeline(config)
    out = {
        "config_name": name,
        "config": dict(config),
        "iterations_per_baseline": iters,
        "folios": {},
    }
    for folio in FOLIOS:
        eva = (EVA_DIR / f"{folio}.txt").read_text()
        real = decode_eva_text(eva, folio, pipeline=pipeline)
        entry = {
            "real_coherence": round(real["coherence"], 4),
            "real_known_ratio": round(real["known_ratio"], 4),
            "eva_sha256": hashlib.sha256(eva.encode()).hexdigest(),
            "baselines": {},
        }
        discriminating = True
        for bname, gen in GENERATORS.items():
            coh, cov = [], []
            for i in range(iters):
                txt = gen(eva, seed=31337 + i)
                r = decode_eva_text(txt, folio, pipeline=pipeline)
                coh.append(r["coherence"])
                cov.append(r["known_ratio"])
            mean, std = statistics.mean(coh), statistics.pstdev(coh)
            z = (real["coherence"] - mean) / std if std > 1e-9 else float("inf")
            p_emp = empirical_p(real["coherence"], coh)
            significant = (z >= 1.645) and (p_emp < 0.05)
            if not significant:
                discriminating = False
            entry["baselines"][bname] = {
                "coherence_mean": round(mean, 4),
                "coherence_std": round(std, 4),
                "known_ratio_mean": round(statistics.mean(cov), 4),
                "z_score": round(z, 2),
                "empirical_p": round(p_emp, 4),
                "significant": significant,
            }
        entry["verdict"] = "DISCRIMINATING" if discriminating else "WEAK"
        out["folios"][folio] = entry
    n_disc = sum(1 for f in out["folios"].values()
                 if f["verdict"] == "DISCRIMINATING")
    out["discriminating_folios"] = n_disc
    out["hierarchy_holds"] = all(
        f["real_coherence"]
        > f["baselines"]["char_shuffled"]["coherence_mean"]
        > f["baselines"]["synthetic_eva"]["coherence_mean"]
        > f["baselines"]["random_latin"]["coherence_mean"]
        for f in out["folios"].values()
    )
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    iters = 10 if args.quick else 30

    results = {
        "test_date": datetime.datetime.now().isoformat(),
        "test_version": "v3-dual-config",
        "iterations_per_baseline": iters,
        "interpretation_contract": (
            "Absolute coverage is not evidence. Evidence = real-vs-null "
            "deltas, significance, and preserved ordering hierarchy."
        ),
        "configs": {},
    }
    for name, config in CONFIGS.items():
        print(f"\n=== CONFIG: {name} ===")
        r = run_config(name, config, iters)
        results["configs"][name] = r
        for folio, e in r["folios"].items():
            line = (f"{folio}: real coh {e['real_coherence']:.3f} "
                    f"cov {e['real_known_ratio']:.3f}")
            for bn, b in e["baselines"].items():
                line += (f" | {bn} {b['coherence_mean']:.3f} "
                         f"z={b['z_score']:.1f}")
            print(line, "->", e["verdict"])
        print(f"hierarchy holds: {r['hierarchy_holds']}, "
              f"discriminating folios: {r['discriminating_folios']}/5")

    out_dir = HERE / "results_v3"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "v3_dual_config_results.json"
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nResults written to {out_path}")


if __name__ == "__main__":
    main()
