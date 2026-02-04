#!/usr/bin/env python3
"""
ZFD Blind Decode Falsification Test v2: Vocabulary Specificity

Tests whether the ZFD pipeline's vocabulary mappings are specific to
Voynich manuscript text or flexible enough to produce comparable output
from any input.

Three non-Voynich baselines:
1. Synthetic EVA: Random characters matching manuscript statistics
2. Character-shuffled: Real words with morphology destroyed
3. Random Latin: Medieval pharmaceutical vocabulary

Usage:
    python run_test_v2.py              # Full test (100 iterations)
    python run_test_v2.py --quick      # Quick test (10 iterations)
    python run_test_v2.py --folio f10r # Single folio
    python run_test_v2.py --baseline synthetic_eva  # Single baseline type
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path

# Ensure we can import from this directory
sys.path.insert(0, str(Path(__file__).parent))

from v2_config import TEST_FOLIOS, V2_ITERATIONS
from v2_baselines import run_all_baselines, save_baseline_results
from v2_compare import compare_v2_results, load_real_results
from v2_report import generate_v2_report
from utils import sha256_file, save_json, get_project_root, get_lexicon_path


def print_banner():
    """Print test banner."""
    print("=" * 70)
    print("     ZFD BLIND DECODE FALSIFICATION TEST v2: VOCABULARY SPECIFICITY")
    print("=" * 70)
    print()
    print("  Purpose: Test whether ZFD vocabulary mappings are specific to")
    print("           Voynich text or flexible enough to match any input.")
    print()
    print("  Baselines:")
    print("    1. Synthetic EVA: Random characters, manuscript statistics")
    print("    2. Character-shuffled: Real words, morphology destroyed")
    print("    3. Random Latin: Medieval pharmaceutical vocabulary")
    print()
    print("=" * 70)
    print()


def verify_prerequisites(folios: list) -> bool:
    """Verify all required files exist."""
    print("[1/8] Verifying prerequisites...")

    root = get_project_root()
    all_ok = True

    # Check EVA files
    for folio_id in folios:
        eva_path = root / "voynich_data" / "raw_eva" / f"{folio_id}.txt"
        if eva_path.exists():
            print(f"  [OK] EVA file: {folio_id}.txt")
        else:
            print(f"  [FAIL] EVA file missing: {eva_path}")
            all_ok = False

    # Check lexicon
    lexicon_path = get_lexicon_path()
    if lexicon_path.exists():
        print(f"  [OK] Lexicon: {lexicon_path.name}")
    else:
        print(f"  [FAIL] Lexicon missing: {lexicon_path}")
        all_ok = False

    # Check v1.1 real decode results
    results_dir = root / "validation" / "blind_decode_test" / "results"
    for folio_id in folios:
        real_path = results_dir / f"real_decode_{folio_id}.json"
        if real_path.exists():
            print(f"  [OK] v1.1 results: real_decode_{folio_id}.json")
        else:
            print(f"  [FAIL] v1.1 results missing: {real_path}")
            all_ok = False

    # Check pipeline importable
    try:
        from decoder import decode_eva_text
        print("  [OK] Pipeline importable")
    except ImportError as e:
        print(f"  [FAIL] Pipeline import error: {e}")
        all_ok = False

    print()
    return all_ok


def run_test(
    folios: list = None,
    iterations: int = None,
    baseline_types: list = None,
    quick: bool = False
):
    """Run the complete v2 test."""

    print_banner()

    # Handle arguments
    if folios is None:
        folios = TEST_FOLIOS
    if iterations is None:
        iterations = 10 if quick else V2_ITERATIONS
    if baseline_types is None:
        baseline_types = ['synthetic_eva', 'char_shuffled', 'random_latin']

    print(f"Configuration:")
    print(f"  Folios: {', '.join(folios)}")
    print(f"  Baseline types: {', '.join(baseline_types)}")
    print(f"  Iterations per baseline: {iterations}")
    print(f"  Total baseline decodes: {len(folios) * len(baseline_types) * iterations}")
    print()

    # Verify prerequisites
    if not verify_prerequisites(folios):
        print("Prerequisites check failed. Aborting.")
        sys.exit(1)

    # Get paths
    root = get_project_root()
    lexicon_path = get_lexicon_path()
    results_dir = root / "validation" / "blind_decode_test" / "results"
    results_v2_dir = root / "validation" / "blind_decode_test" / "results_v2"
    results_v2_dir.mkdir(parents=True, exist_ok=True)

    # Record lexicon checksum (START)
    print("[2/8] Recording lexicon checksum...")
    lexicon_hash_start = sha256_file(str(lexicon_path))
    print(f"  SHA-256: {lexicon_hash_start[:16]}...")
    print()

    # Load v1.1 real decode results
    print("[3/8] Loading v1.1 real decode results...")
    real_results = load_real_results(str(results_dir))
    print(f"  Loaded {len(real_results)} folios")
    for folio_id, data in real_results.items():
        print(f"    {folio_id}: coherence={data.get('coherence', 0):.3f}, known={data.get('known_ratio', 0):.1%}")
    print()

    # Run baselines
    print(f"[4/8] Running baseline decodes ({len(baseline_types)} types x {len(folios)} folios x {iterations} iterations)...")
    baseline_results = run_all_baselines(
        folios=folios,
        iterations=iterations,
        baseline_types=baseline_types,
        verbose=True
    )
    print()

    # Save baseline results
    print("[5/8] Saving baseline results...")
    save_baseline_results(baseline_results, str(results_v2_dir))
    print(f"  Saved to: {results_v2_dir}")
    print()

    # Verify lexicon checksum (END)
    print("[6/8] Verifying lexicon integrity...")
    lexicon_hash_end = sha256_file(str(lexicon_path))
    if lexicon_hash_start == lexicon_hash_end:
        print(f"  [OK] Checksum verified: {lexicon_hash_end[:16]}...")
    else:
        print(f"  [FAIL] Lexicon modified during test!")
        print(f"    Start: {lexicon_hash_start}")
        print(f"    End:   {lexicon_hash_end}")
        print("  ABORTING - Test integrity compromised")
        sys.exit(1)
    print()

    # Run statistical comparison
    print("[7/8] Running statistical comparison...")
    comparison = compare_v2_results(real_results, baseline_results, lexicon_hash_end)
    save_json(comparison, str(results_v2_dir / "v2_comparison_results.json"))

    verdict = comparison.get('overall_verdict', 'UNKNOWN')
    summary = comparison.get('summary', {})
    print(f"  Overall verdict: {verdict}")
    print(f"  Folios discriminating: {summary.get('folios_discriminating', 0)}/{summary.get('folios_tested', 0)}")
    print()

    # Generate report
    print("[8/8] Generating report...")
    report_path = results_v2_dir / "V2_VOCABULARY_SPECIFICITY_REPORT.md"
    generate_v2_report(comparison, baseline_results, str(report_path))
    print(f"  Report saved to: {report_path}")
    print()

    # Save test metadata
    metadata = {
        'test_version': 'v2',
        'test_date': datetime.now().isoformat(),
        'folios_tested': folios,
        'baseline_types': baseline_types,
        'iterations_per_baseline': iterations,
        'total_baseline_decodes': len(folios) * len(baseline_types) * iterations,
        'lexicon_sha256': lexicon_hash_end,
        'overall_verdict': verdict,
    }
    save_json(metadata, str(results_v2_dir / "v2_test_metadata.json"))

    # Print summary
    print("=" * 70)
    print(f"  TEST COMPLETE: {verdict}")
    print("=" * 70)
    print()

    if verdict == "PASS":
        print("  The ZFD pipeline produces significantly higher coherence on real")
        print("  Voynich text than on synthetic EVA, character-shuffled words, or")
        print("  medieval Latin vocabulary.")
        print()
        print("  The decoder's vocabulary mappings are specific to Voynich")
        print("  morphological patterns. The degrees-of-freedom criticism is")
        print("  empirically refuted.")
    elif verdict == "FAIL":
        print("  The ZFD pipeline does not reliably discriminate between real")
        print("  Voynich text and non-Voynich baselines.")
        print()
        print("  The degrees-of-freedom criticism is supported: the decoder's")
        print("  flexibility allows comparable output from arbitrary input.")
    else:
        print("  Mixed results. Some folios discriminate, others do not.")
        print("  Further investigation needed.")

    print()
    print(f"  Full results: {results_v2_dir}")
    print()

    return comparison


def main():
    """Parse arguments and run test."""
    parser = argparse.ArgumentParser(
        description="ZFD Blind Decode Falsification Test v2: Vocabulary Specificity"
    )
    parser.add_argument(
        '--quick', action='store_true',
        help='Quick mode: 10 iterations instead of 100'
    )
    parser.add_argument(
        '--folio', type=str,
        help='Test single folio (e.g., f10r)'
    )
    parser.add_argument(
        '--baseline', type=str,
        help='Test single baseline type (synthetic_eva, char_shuffled, random_latin)'
    )
    parser.add_argument(
        '--iterations', type=int,
        help='Number of iterations per baseline'
    )

    args = parser.parse_args()

    # Determine test parameters
    folios = [args.folio] if args.folio else None
    baseline_types = [args.baseline] if args.baseline else None
    iterations = args.iterations

    run_test(
        folios=folios,
        iterations=iterations,
        baseline_types=baseline_types,
        quick=args.quick
    )


if __name__ == "__main__":
    main()
