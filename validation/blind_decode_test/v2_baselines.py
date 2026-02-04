"""
v2 Baseline Runner: Run all three baseline types through the decoder.

Generates and decodes:
1. Synthetic EVA (100 iterations)
2. Character-shuffled Voynich (100 iterations)
3. Random Latin (100 iterations)

For each of the 5 test folios.
"""

import sys
import statistics
from pathlib import Path
from typing import Dict, List, Any, Callable

# Ensure we can import from this directory
sys.path.insert(0, str(Path(__file__).parent))

from v2_config import (
    TEST_FOLIOS, V2_ITERATIONS,
    SEED_SYNTHETIC, SEED_CHAR_SHUFFLE, SEED_RANDOM_LATIN
)
from v2_generators import generate_synthetic_eva, generate_char_shuffled, generate_random_latin
from decoder import decode_eva_text
from utils import load_eva_folio, get_project_root, save_json


def run_baseline_iterations(
    folio_id: str,
    generator: Callable[[str, int], str],
    seed_base: int,
    iterations: int,
    baseline_name: str,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Run a single baseline type for one folio.

    Args:
        folio_id: Folio identifier (e.g., "f10r")
        generator: Function that generates baseline text
        seed_base: Starting seed for this baseline type
        iterations: Number of iterations to run
        baseline_name: Name of baseline type for logging
        verbose: Print progress

    Returns:
        Dict with all iteration results and statistics
    """
    root = get_project_root()
    real_eva_text = load_eva_folio(folio_id, str(root))

    coherence_scores = []
    known_ratios = []
    category_counts_total = {}
    iteration_data = []

    for i in range(iterations):
        seed = seed_base + i

        # Generate baseline text
        baseline_text = generator(real_eva_text, seed)

        # Decode through the pipeline
        result = decode_eva_text(baseline_text, f"{folio_id}_{baseline_name}_{i}")

        # Collect metrics
        coherence_scores.append(result['coherence'])
        known_ratios.append(result['known_ratio'])

        # Aggregate category counts
        for cat, count in result['category_counts'].items():
            category_counts_total[cat] = category_counts_total.get(cat, 0) + count

        # Store iteration data (without full tokens to save space)
        iteration_data.append({
            'iteration': i,
            'seed': seed,
            'coherence': result['coherence'],
            'known_ratio': result['known_ratio'],
            'total_tokens': result['total_tokens'],
            'known_stems': result['known_stems'],
            'operator_counts': result['operator_counts'],
            'category_counts': result['category_counts'],
        })

        if verbose and (i + 1) % 10 == 0:
            print(f"      {baseline_name} iteration {i+1}/{iterations}")

    # Compute statistics
    stats = compute_baseline_stats(coherence_scores, known_ratios)

    return {
        'folio': folio_id,
        'baseline_type': baseline_name,
        'iterations': iterations,
        'seed_base': seed_base,
        'coherence_scores': coherence_scores,
        'known_ratios': known_ratios,
        'category_counts_summary': category_counts_total,
        'iteration_data': iteration_data,
        'stats': stats,
    }


def compute_baseline_stats(coherence_scores: List[float], known_ratios: List[float]) -> Dict[str, float]:
    """Compute summary statistics for baseline distribution."""

    def percentile(data: List[float], p: float) -> float:
        """Compute percentile without numpy."""
        sorted_data = sorted(data)
        k = (len(sorted_data) - 1) * p / 100
        f = int(k)
        c = f + 1 if f + 1 < len(sorted_data) else f
        return sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f])

    stats = {}

    # Coherence statistics
    stats['coherence_mean'] = round(statistics.mean(coherence_scores), 4)
    stats['coherence_std'] = round(statistics.stdev(coherence_scores) if len(coherence_scores) > 1 else 0, 4)
    stats['coherence_min'] = round(min(coherence_scores), 4)
    stats['coherence_max'] = round(max(coherence_scores), 4)
    stats['coherence_p5'] = round(percentile(coherence_scores, 5), 4)
    stats['coherence_p25'] = round(percentile(coherence_scores, 25), 4)
    stats['coherence_p50'] = round(percentile(coherence_scores, 50), 4)
    stats['coherence_p75'] = round(percentile(coherence_scores, 75), 4)
    stats['coherence_p95'] = round(percentile(coherence_scores, 95), 4)

    # Known ratio statistics
    stats['known_ratio_mean'] = round(statistics.mean(known_ratios), 4)
    stats['known_ratio_std'] = round(statistics.stdev(known_ratios) if len(known_ratios) > 1 else 0, 4)
    stats['known_ratio_min'] = round(min(known_ratios), 4)
    stats['known_ratio_max'] = round(max(known_ratios), 4)

    return stats


def run_all_baselines(
    folios: List[str] = None,
    iterations: int = None,
    baseline_types: List[str] = None,
    verbose: bool = True
) -> Dict[str, Dict[str, Dict]]:
    """
    Run all baseline types for all folios.

    Args:
        folios: List of folio IDs (default: TEST_FOLIOS)
        iterations: Number of iterations (default: V2_ITERATIONS)
        baseline_types: List of baseline types to run (default: all three)
        verbose: Print progress

    Returns:
        Nested dict: {baseline_type: {folio_id: results}}
    """
    if folios is None:
        folios = TEST_FOLIOS
    if iterations is None:
        iterations = V2_ITERATIONS
    if baseline_types is None:
        baseline_types = ['synthetic_eva', 'char_shuffled', 'random_latin']

    # Map baseline names to generators and seed bases
    baseline_config = {
        'synthetic_eva': (generate_synthetic_eva, SEED_SYNTHETIC),
        'char_shuffled': (generate_char_shuffled, SEED_CHAR_SHUFFLE),
        'random_latin': (generate_random_latin, SEED_RANDOM_LATIN),
    }

    results = {}
    total_ops = len(baseline_types) * len(folios) * iterations
    completed = 0

    for baseline_name in baseline_types:
        if baseline_name not in baseline_config:
            print(f"Unknown baseline type: {baseline_name}")
            continue

        generator, seed_base = baseline_config[baseline_name]
        results[baseline_name] = {}

        if verbose:
            print(f"  Running {baseline_name} baselines...")

        for folio_id in folios:
            if verbose:
                print(f"    Processing {folio_id}...")

            folio_results = run_baseline_iterations(
                folio_id=folio_id,
                generator=generator,
                seed_base=seed_base,
                iterations=iterations,
                baseline_name=baseline_name,
                verbose=verbose
            )
            results[baseline_name][folio_id] = folio_results

            completed += iterations
            if verbose:
                pct = (completed / total_ops) * 100
                mean_coh = folio_results['stats']['coherence_mean']
                std_coh = folio_results['stats']['coherence_std']
                print(f"      Done: coherence={mean_coh:.3f} +/- {std_coh:.3f} ({pct:.0f}% complete)")

    return results


def save_baseline_results(results: Dict[str, Dict[str, Dict]], output_dir: str):
    """Save all baseline results to JSON files."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for baseline_name, folio_results in results.items():
        for folio_id, data in folio_results.items():
            filename = f"v2_{baseline_name}_{folio_id}.json"
            save_json(data, str(output_path / filename))


if __name__ == "__main__":
    # Quick test with 5 iterations
    print("Testing v2_baselines.py with 5 iterations per baseline...")

    results = run_all_baselines(
        folios=['f10r'],
        iterations=5,
        verbose=True
    )

    print("\nResults summary:")
    for baseline_name, folio_results in results.items():
        for folio_id, data in folio_results.items():
            stats = data['stats']
            print(f"  {baseline_name} / {folio_id}:")
            print(f"    Coherence: {stats['coherence_mean']:.4f} +/- {stats['coherence_std']:.4f}")
            print(f"    Known ratio: {stats['known_ratio_mean']:.4f} +/- {stats['known_ratio_std']:.4f}")

    print("\nBaseline runner test passed!")
