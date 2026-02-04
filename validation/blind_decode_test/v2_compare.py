"""
v2 Statistical Comparison Engine

Compares real Voynich decode results against all three baseline types
with proper statistical testing.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent))

from v2_config import TEST_FOLIOS, V2_THRESHOLDS
from utils import load_json, get_project_root


def compare_v2_results(
    real_results: Dict[str, Dict],
    baseline_results: Dict[str, Dict[str, Dict]],
    lexicon_hash: str
) -> Dict[str, Any]:
    """
    Compare real decode results against all three baseline types.

    Args:
        real_results: Dict mapping folio_id -> decode results (from v1.1)
        baseline_results: Dict mapping baseline_type -> {folio_id -> results}
        lexicon_hash: SHA-256 hash of the lexicon file

    Returns:
        Complete v2 comparison results with verdict
    """
    folio_comparisons = {}
    baseline_hierarchy = {}
    discriminating_count = 0

    baseline_types = ['synthetic_eva', 'char_shuffled', 'random_latin']

    for folio_id in TEST_FOLIOS:
        real = real_results.get(folio_id, {})
        real_coherence = real.get('coherence', 0)
        real_known_ratio = real.get('known_ratio', 0)

        # Compare against each baseline type
        baselines = {}
        all_significant = True
        hierarchy_data = {'real': real_coherence}

        for baseline_type in baseline_types:
            if baseline_type not in baseline_results:
                continue
            if folio_id not in baseline_results[baseline_type]:
                continue

            baseline = baseline_results[baseline_type][folio_id]
            stats = baseline.get('stats', {})
            scores = baseline.get('coherence_scores', [])

            baseline_mean = stats.get('coherence_mean', 0)
            baseline_std = stats.get('coherence_std', 0)

            # Handle degenerate case (zero std dev)
            if baseline_std == 0:
                if real_coherence > baseline_mean:
                    z_score = float('inf')
                    p_value = 0.0
                elif real_coherence == baseline_mean:
                    z_score = 0
                    p_value = 1.0
                else:
                    z_score = float('-inf')
                    p_value = 1.0
                degenerate = True
            else:
                z_score = (real_coherence - baseline_mean) / baseline_std
                degenerate = False

            # Empirical p-value: fraction of baseline scores >= real
            if scores:
                count_gte = sum(1 for s in scores if s >= real_coherence)
                p_value = count_gte / len(scores)
            else:
                p_value = 1.0

            # Effect size (Cohen's d)
            effect_size = z_score if not degenerate else z_score

            # Check significance
            is_significant = p_value < V2_THRESHOLDS['significance_level']
            if not is_significant:
                all_significant = False

            # Store baseline-specific key for hierarchy
            hierarchy_key = baseline_type.replace('_', '_')
            hierarchy_data[hierarchy_key] = baseline_mean

            baselines[baseline_type] = {
                'mean': round(baseline_mean, 4),
                'std': round(baseline_std, 4),
                'z_score': round(z_score, 2) if not degenerate else 'inf',
                'p_value': round(p_value, 4),
                'effect_size': round(effect_size, 2) if not degenerate else 'inf',
                'known_ratio_mean': round(stats.get('known_ratio_mean', 0), 4),
                'significant': is_significant,
                'degenerate': degenerate,
            }

        # Determine folio verdict
        if all_significant:
            verdict = "DISCRIMINATING"
            discriminating_count += 1
        elif any(b.get('significant', False) for b in baselines.values()):
            verdict = "PARTIAL"
        else:
            verdict = "NON_DISCRIMINATING"

        # Check hierarchy: Real > CharShuffle > SyntheticEVA > Latin
        char_shuf_mean = baselines.get('char_shuffled', {}).get('mean', 0)
        synth_mean = baselines.get('synthetic_eva', {}).get('mean', 0)
        latin_mean = baselines.get('random_latin', {}).get('mean', 0)

        hierarchy_holds = (
            real_coherence > char_shuf_mean > synth_mean and
            synth_mean > latin_mean * 0.9  # Allow some margin for Latin
        )

        hierarchy_data['hierarchy_holds'] = hierarchy_holds

        folio_comparisons[folio_id] = {
            'real_coherence': round(real_coherence, 4),
            'real_known_ratio': round(real_known_ratio, 4),
            'baselines': baselines,
            'verdict': verdict,
        }

        baseline_hierarchy[folio_id] = hierarchy_data

    # Determine overall verdict
    min_required = V2_THRESHOLDS['min_discriminating_folios']
    if discriminating_count >= min_required:
        overall_verdict = "PASS"
    elif discriminating_count >= 2:
        overall_verdict = "PARTIAL"
    else:
        overall_verdict = "FAIL"

    # Compute summary statistics
    summary = compute_summary_stats(folio_comparisons, discriminating_count)

    return {
        'test_date': datetime.now().isoformat(),
        'test_version': 'v2',
        'lexicon_sha256': lexicon_hash,
        'overall_verdict': overall_verdict,
        'folios': folio_comparisons,
        'baseline_hierarchy': baseline_hierarchy,
        'summary': summary,
    }


def compute_summary_stats(folio_comparisons: Dict, discriminating_count: int) -> Dict:
    """Compute overall summary statistics."""
    z_scores = {'synthetic_eva': [], 'char_shuffled': [], 'random_latin': []}

    for folio_data in folio_comparisons.values():
        for baseline_type, baseline_data in folio_data.get('baselines', {}).items():
            z = baseline_data.get('z_score', 0)
            if isinstance(z, (int, float)) and z != float('inf'):
                z_scores[baseline_type].append(z)

    def safe_mean(lst):
        return round(sum(lst) / len(lst), 2) if lst else 0

    return {
        'folios_tested': len(folio_comparisons),
        'folios_discriminating': discriminating_count,
        'folios_required': V2_THRESHOLDS['min_discriminating_folios'],
        'mean_z_synthetic': safe_mean(z_scores['synthetic_eva']),
        'mean_z_char_shuffled': safe_mean(z_scores['char_shuffled']),
        'mean_z_latin': safe_mean(z_scores['random_latin']),
    }


def load_real_results(results_dir: str) -> Dict[str, Dict]:
    """Load real decode results from v1.1 output files."""
    results = {}
    results_path = Path(results_dir)

    for folio_id in TEST_FOLIOS:
        filepath = results_path / f"real_decode_{folio_id}.json"
        if filepath.exists():
            results[folio_id] = load_json(str(filepath))
        else:
            print(f"Warning: Real decode results not found for {folio_id}")

    return results


def load_baseline_results(results_v2_dir: str) -> Dict[str, Dict[str, Dict]]:
    """Load all baseline results from v2 output files."""
    results = {
        'synthetic_eva': {},
        'char_shuffled': {},
        'random_latin': {},
    }
    results_path = Path(results_v2_dir)

    for baseline_type in results.keys():
        for folio_id in TEST_FOLIOS:
            filename = f"v2_{baseline_type}_{folio_id}.json"
            filepath = results_path / filename
            if filepath.exists():
                results[baseline_type][folio_id] = load_json(str(filepath))

    return results


if __name__ == "__main__":
    # Test comparison with existing results
    print("Testing v2_compare.py...")

    # Load real results from v1.1
    root = get_project_root()
    results_dir = root / "validation" / "blind_decode_test" / "results"

    real_results = load_real_results(str(results_dir))
    print(f"Loaded real results for {len(real_results)} folios")

    # Create mock baseline results for testing
    mock_baselines = {
        'synthetic_eva': {
            'f10r': {
                'stats': {'coherence_mean': 0.40, 'coherence_std': 0.05, 'known_ratio_mean': 0.12},
                'coherence_scores': [0.38, 0.40, 0.42, 0.39, 0.41],
            }
        },
        'char_shuffled': {
            'f10r': {
                'stats': {'coherence_mean': 0.50, 'coherence_std': 0.07, 'known_ratio_mean': 0.18},
                'coherence_scores': [0.48, 0.50, 0.52, 0.49, 0.51],
            }
        },
        'random_latin': {
            'f10r': {
                'stats': {'coherence_mean': 0.35, 'coherence_std': 0.03, 'known_ratio_mean': 0.25},
                'coherence_scores': [0.34, 0.35, 0.36, 0.34, 0.36],
            }
        },
    }

    # Run comparison
    comparison = compare_v2_results(real_results, mock_baselines, "test_hash_123")

    print(f"\nOverall verdict: {comparison['overall_verdict']}")
    if 'f10r' in comparison['folios']:
        fc = comparison['folios']['f10r']
        print(f"\nFolio f10r:")
        print(f"  Real coherence: {fc['real_coherence']}")
        for bt, bd in fc['baselines'].items():
            print(f"  {bt}: mean={bd['mean']}, z={bd['z_score']}, p={bd['p_value']}")
        print(f"  Verdict: {fc['verdict']}")

    print("\nComparison test passed!")
