"""
Shuffled baseline generator for blind decode test.

Generates and decodes shuffled versions of each folio to establish
the null hypothesis distribution.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
import statistics

# Add project paths
sys.path.insert(0, str(Path(__file__).parent))

from config import SHUFFLE_SEED, SHUFFLE_ITERATIONS
from utils import load_eva_folio, shuffle_eva_text, get_project_root
from decoder import decode_eva_text


def generate_baselines(folio_id: str, iterations: int = None,
                       verbose: bool = False) -> Dict[str, Any]:
    """
    Generate and decode shuffled baselines for a folio.

    Args:
        folio_id: Folio identifier (e.g., "f10r")
        iterations: Number of shuffle iterations (default from config)
        verbose: Print progress for each iteration

    Returns:
        Dict containing all individual results and summary statistics
    """
    if iterations is None:
        iterations = SHUFFLE_ITERATIONS

    # Load original EVA text
    root = get_project_root()
    eva_text = load_eva_folio(folio_id, str(root))

    # Collect results from all iterations
    coherence_scores = []
    known_ratios = []
    operator_diversities = []
    category_diversities = []
    confidence_means = []

    # Also track individual iteration data for detailed analysis
    iteration_data = []

    for i in range(iterations):
        # Use deterministic seed: SHUFFLE_SEED + iteration_number
        seed = SHUFFLE_SEED + i

        # Shuffle the EVA text
        shuffled_text = shuffle_eva_text(eva_text, seed)

        # Decode through the pipeline
        result = decode_eva_text(shuffled_text, f"{folio_id}_shuffled_{i}")

        # Extract metrics
        coherence_scores.append(result['coherence'])
        known_ratios.append(result['known_ratio'])
        operator_diversities.append(len(result['operator_counts']))
        category_diversities.append(len(result['category_counts']))
        confidence_means.append(result['average_confidence'])

        # Store individual iteration data (without full tokens to save space)
        iteration_data.append({
            'iteration': i,
            'seed': seed,
            'coherence': result['coherence'],
            'known_ratio': result['known_ratio'],
            'operator_count': len(result['operator_counts']),
            'category_count': len(result['category_counts']),
            'average_confidence': result['average_confidence'],
            'operators': result['operator_counts'],
            'categories': result['category_counts'],
        })

        if verbose:
            print(f"    Iteration {i+1}/{iterations}: coherence={result['coherence']:.3f}")

    # Compute statistics
    stats = compute_statistics(coherence_scores, known_ratios,
                               operator_diversities, category_diversities,
                               confidence_means)

    return {
        'folio': folio_id,
        'iterations': iterations,
        'base_seed': SHUFFLE_SEED,
        'coherence_scores': coherence_scores,
        'known_ratios': known_ratios,
        'operator_diversities': operator_diversities,
        'category_diversities': category_diversities,
        'confidence_means': confidence_means,
        'iteration_data': iteration_data,
        'stats': stats,
    }


def compute_statistics(coherence_scores: List[float], known_ratios: List[float],
                       operator_diversities: List[int], category_diversities: List[int],
                       confidence_means: List[float]) -> Dict[str, float]:
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

    # Operator diversity statistics
    stats['operator_diversity_mean'] = round(statistics.mean(operator_diversities), 2)
    stats['operator_diversity_std'] = round(statistics.stdev(operator_diversities) if len(operator_diversities) > 1 else 0, 2)

    # Category diversity statistics
    stats['category_diversity_mean'] = round(statistics.mean(category_diversities), 2)
    stats['category_diversity_std'] = round(statistics.stdev(category_diversities) if len(category_diversities) > 1 else 0, 2)

    # Confidence statistics
    stats['confidence_mean'] = round(statistics.mean(confidence_means), 4)
    stats['confidence_std'] = round(statistics.stdev(confidence_means) if len(confidence_means) > 1 else 0, 4)

    return stats


def generate_all_baselines(folios: List[str], iterations: int = None,
                          progress_callback=None) -> Dict[str, Dict]:
    """
    Generate baselines for multiple folios.

    Args:
        folios: List of folio IDs
        iterations: Number of shuffle iterations per folio
        progress_callback: Optional callback(folio, iteration, total) for progress

    Returns:
        Dict mapping folio_id -> baseline results
    """
    results = {}
    for folio in folios:
        if progress_callback:
            progress_callback(folio, 0, iterations or SHUFFLE_ITERATIONS)
        results[folio] = generate_baselines(folio, iterations)
    return results


if __name__ == "__main__":
    # Quick test with 5 iterations
    print("Testing baseline.py with 5 iterations...")
    result = generate_baselines("f10r", iterations=5, verbose=True)
    print(f"\nFolio: {result['folio']}")
    print(f"Iterations: {result['iterations']}")
    print(f"Coherence scores: {result['coherence_scores']}")
    print(f"\nStatistics:")
    for key, value in result['stats'].items():
        print(f"  {key}: {value}")
    print("\nBaseline test passed!")
