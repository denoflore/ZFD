#!/usr/bin/env python3
"""
ZFD Blind Decode Falsification Test - Main Runner

Usage:
    python run_test.py              # Full test (100 iterations)
    python run_test.py --quick      # Quick test (10 iterations)
    python run_test.py --folio f10r # Single folio only
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import TEST_FOLIOS, SHUFFLE_SEED, SHUFFLE_ITERATIONS, THRESHOLDS
from utils import sha256_file, get_project_root, get_lexicon_path, save_json


def print_banner():
    """Print test banner."""
    print("=" * 70)
    print("     ZFD BLIND DECODE FALSIFICATION TEST")
    print("=" * 70)
    print()
    print("  Purpose: Test whether ZFD detects real structure or generates")
    print("           Croatian-compatible output from any input.")
    print()
    print("  Method:  Compare real decode vs shuffled baseline through")
    print("           the SAME frozen pipeline.")
    print()
    print("=" * 70)
    print()


def verify_prerequisites():
    """Verify all prerequisites are met."""
    print("[1/7] Verifying prerequisites...")

    root = get_project_root()
    errors = []

    # Check EVA files exist
    for folio in TEST_FOLIOS:
        eva_path = root / "voynich_data" / "raw_eva" / f"{folio}.txt"
        if not eva_path.exists():
            errors.append(f"  Missing EVA file: {eva_path}")
        else:
            print(f"  [OK] EVA file: {folio}.txt")

    # Check lexicon exists
    lexicon_path = get_lexicon_path()
    if not lexicon_path.exists():
        errors.append(f"  Missing lexicon: {lexicon_path}")
    else:
        print(f"  [OK] Lexicon: {lexicon_path.name}")

    # Check pipeline can be imported
    try:
        sys.path.insert(0, str(root / "zfd_decoder" / "src"))
        from pipeline import ZFDPipeline
        print("  [OK] Pipeline importable")
    except ImportError as e:
        errors.append(f"  Cannot import pipeline: {e}")

    if errors:
        print("\nPrerequisite errors:")
        for err in errors:
            print(err)
        return False

    print()
    return True


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="ZFD Blind Decode Falsification Test")
    parser.add_argument("--quick", action="store_true",
                        help="Quick test with 10 iterations instead of 100")
    parser.add_argument("--folio", type=str,
                        help="Run test for single folio only")
    args = parser.parse_args()

    # Print banner
    print_banner()

    # Determine test parameters
    iterations = 10 if args.quick else SHUFFLE_ITERATIONS
    folios = [args.folio] if args.folio else TEST_FOLIOS

    print(f"Configuration:")
    print(f"  Folios: {', '.join(folios)}")
    print(f"  Shuffle iterations: {iterations}")
    print(f"  Seed: {SHUFFLE_SEED}")
    print()

    # Verify prerequisites
    if not verify_prerequisites():
        print("\nTest aborted due to prerequisite failures.")
        sys.exit(1)

    # Record lexicon checksum (START)
    print("[2/7] Recording lexicon checksum...")
    lexicon_path = get_lexicon_path()
    lexicon_hash_start = sha256_file(str(lexicon_path))
    print(f"  SHA-256: {lexicon_hash_start[:16]}...")
    print()

    # Import decoder module
    from decoder import decode_folio
    from baseline import generate_baselines
    from compare import compare_results
    from report import generate_report

    # Create results directory
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)

    # Run real decode on all folios
    print("[3/7] Decoding real folios...")
    real_results = {}
    for folio in folios:
        print(f"  Processing {folio}...", end=" ", flush=True)
        result = decode_folio(folio)
        real_results[folio] = result
        save_json(result, str(results_dir / f"real_decode_{folio}.json"))
        print(f"coherence={result['coherence']:.3f}, known={result['known_ratio']:.1%}")
    print()

    # Run shuffled baselines
    print(f"[4/7] Generating shuffled baselines ({iterations} iterations per folio)...")
    baseline_results = {}
    for folio in folios:
        print(f"  Processing {folio}...", end=" ", flush=True)
        baseline = generate_baselines(folio, iterations)
        baseline_results[folio] = baseline
        save_json(baseline, str(results_dir / f"baseline_{folio}.json"))
        print(f"mean_coherence={baseline['stats']['coherence_mean']:.3f} +/- {baseline['stats']['coherence_std']:.3f}")
    print()

    # Verify lexicon checksum (END)
    print("[5/7] Verifying lexicon integrity...")
    lexicon_hash_end = sha256_file(str(lexicon_path))
    if lexicon_hash_start != lexicon_hash_end:
        print("  [ABORT] Lexicon was modified during test!")
        print(f"    Start: {lexicon_hash_start}")
        print(f"    End:   {lexicon_hash_end}")
        print("\n  TEST INVALIDATED - Lexicon tampering detected.")
        sys.exit(2)
    print(f"  [OK] Checksum verified: {lexicon_hash_end[:16]}...")
    print()

    # Run statistical comparison
    print("[6/7] Running statistical comparison...")
    comparison = compare_results(real_results, baseline_results, lexicon_hash_end)
    save_json(comparison, str(results_dir / "comparison_results.json"))
    print(f"  Overall verdict: {comparison['overall_verdict']}")
    print(f"  Folios passing: {comparison['summary']['folios_passing']}/{len(folios)}")
    print()

    # Generate report
    print("[7/7] Generating report...")
    report_path = results_dir / "BLIND_DECODE_REPORT.md"
    generate_report(comparison, real_results, baseline_results, str(report_path))
    print(f"  Report saved to: {report_path}")
    print()

    # Save test metadata
    metadata = {
        "test_date": datetime.now().isoformat(),
        "folios_tested": folios,
        "shuffle_iterations": iterations,
        "shuffle_seed": SHUFFLE_SEED,
        "lexicon_sha256": lexicon_hash_end,
        "thresholds": THRESHOLDS,
        "overall_verdict": comparison['overall_verdict'],
    }
    save_json(metadata, str(results_dir / "test_metadata.json"))

    # Print final summary
    print("=" * 70)
    print(f"  TEST COMPLETE: {comparison['overall_verdict']}")
    print("=" * 70)
    print()

    if comparison['overall_verdict'] == "PASS":
        print("  The ZFD pipeline detects semantic structure that exists in")
        print("  the manuscript. Shuffled input through the same 'degrees of")
        print("  freedom' produces statistically worse results.")
        print()
        print("  The system is not a generator. It is a decoder.")
    elif comparison['overall_verdict'] == "FAIL":
        print("  The ZFD pipeline produces similar output regardless of input")
        print("  structure. The degrees-of-freedom criticism is valid.")
        print()
        print("  The coverage metrics reflect system flexibility, not")
        print("  decipherment accuracy.")
    else:  # PARTIAL
        print("  Results are mixed. Some folios show significant structure")
        print("  detection, others do not. Further investigation needed.")

    print()
    print(f"  Full results: {results_dir}/")
    print()

    return 0 if comparison['overall_verdict'] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
