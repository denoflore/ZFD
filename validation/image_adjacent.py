"""
Image-Adjacent Testing Framework for ZFD Semantic Validation.

Tests proposed semantic mappings using preregistered falsification protocols.
For any proposed mapping (e.g., "od" = stalk), we:
1. Find all occurrences of the target stem in herbal folios
2. Check if the stem appears on lines ADJACENT to illustrations of the claimed plant part
3. Compare to shuffled baseline (random distribution)
4. Calculate statistical significance
"""

import random
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
import numpy as np
from scipy import stats

try:
    from .zfd_loader import ZFDLoader
except ImportError:
    from zfd_loader import ZFDLoader


class ImageAdjacentValidator:
    """
    Validates semantic mappings using image-adjacent correlation testing.

    The core hypothesis: If a stem truly means a plant part (root, stalk, etc.),
    it should appear more frequently on lines adjacent to where that part is
    illustrated in the manuscript.
    """

    # Adjacency window: how many lines from a plant-part marker counts as "adjacent"
    ADJACENCY_WINDOW = 2

    # Thresholds
    PASS_THRESHOLD = 0.40  # 40% correlation required
    FORBID_THRESHOLD = 0.20  # 20% wrong-part correlation triggers concern
    P_VALUE_THRESHOLD = 0.01  # Statistical significance level

    # All plant parts we track
    PLANT_PARTS = ['root', 'stalk', 'leaf', 'flower', 'seed', 'vessel']

    def __init__(self, loader: ZFDLoader, folio_annotations: Dict[str, dict]):
        """
        Initialize the validator.

        Args:
            loader: ZFDLoader instance with transcription data
            folio_annotations: Dict mapping folio_id to annotation data:
                {folio_id: {
                    'plant_parts': ['root', 'stalk', 'leaf', 'flower', 'seed'],
                    'root_lines': [1, 2, 3],  # lines where root is depicted
                    'stalk_lines': [4, 5],
                    'leaf_lines': [6, 7, 8],
                    'flower_lines': [9, 10],
                    'seed_lines': [11],
                    'vessel_lines': []
                }}
        """
        self.loader = loader
        self.annotations = folio_annotations
        self._build_adjacency_maps()

    def _build_adjacency_maps(self):
        """Build lookup tables for quick adjacency checking."""
        # For each (folio, line), what plant parts are adjacent?
        self.adjacent_parts: Dict[Tuple[str, int], set] = defaultdict(set)

        for folio, ann in self.annotations.items():
            for part in self.PLANT_PARTS:
                part_lines = ann.get(f'{part}_lines', [])
                for pline in part_lines:
                    # Mark lines within adjacency window
                    for offset in range(-self.ADJACENCY_WINDOW, self.ADJACENCY_WINDOW + 1):
                        self.adjacent_parts[(folio, pline + offset)].add(part)

    def _find_stem_positions(self, stem: str, section: str = 'herbal') -> List[Tuple[str, int]]:
        """
        Find all (folio, line_num) positions where stem appears.

        Args:
            stem: The stem pattern to search for
            section: 'herbal' or 'all'

        Returns:
            List of (folio, line_num) tuples
        """
        occurrences = self.loader.find_stem_occurrences(stem, section=section)
        return [(occ['folio'], occ['line_num']) for occ in occurrences]

    def _count_adjacencies(self, positions: List[Tuple[str, int]], claimed_part: str) -> Tuple[int, int]:
        """
        Count how many positions are adjacent to the claimed plant part.

        Returns:
            (adjacent_count, total_in_annotated_folios)
        """
        adjacent = 0
        total = 0

        for folio, line_num in positions:
            # Only count if we have annotations for this folio
            if folio in self.annotations:
                total += 1
                if claimed_part in self.adjacent_parts.get((folio, line_num), set()):
                    adjacent += 1

        return adjacent, total

    def _count_wrong_part_adjacencies(self, positions: List[Tuple[str, int]],
                                       claimed_part: str) -> Dict[str, Tuple[int, int]]:
        """
        Count adjacencies to WRONG plant parts (for forbid check).

        Returns:
            Dict mapping other_part -> (adjacent_count, total_in_annotated_folios)
        """
        results = {}

        for other_part in self.PLANT_PARTS:
            if other_part == claimed_part:
                continue

            adjacent = 0
            total = 0

            for folio, line_num in positions:
                if folio in self.annotations:
                    total += 1
                    if other_part in self.adjacent_parts.get((folio, line_num), set()):
                        adjacent += 1

            results[other_part] = (adjacent, total)

        return results

    def _shuffle_test(self, positions: List[Tuple[str, int]], claimed_part: str,
                      n_shuffles: int = 1000) -> Tuple[float, float]:
        """
        Run shuffled baseline comparison.

        Shuffles line numbers within each folio to create null distribution.

        Returns:
            (baseline_rate, p_value)
        """
        observed_adj, total = self._count_adjacencies(positions, claimed_part)

        if total == 0:
            return 0.0, 1.0

        observed_rate = observed_adj / total

        # Build shuffled distribution
        shuffled_rates = []

        for _ in range(n_shuffles):
            shuffled_adj = 0
            shuffled_total = 0

            # Group by folio for shuffling
            folio_lines = defaultdict(list)
            for folio, line_num in positions:
                if folio in self.annotations:
                    folio_lines[folio].append(line_num)

            for folio, lines in folio_lines.items():
                ann = self.annotations[folio]
                # Get all possible lines in this folio from transcription
                folio_data = self.loader.transcription.get(folio, [])
                all_lines = [l['line_num'] for l in folio_data]

                if not all_lines:
                    continue

                # Shuffle: randomly pick len(lines) positions
                for _ in lines:
                    rand_line = random.choice(all_lines)
                    shuffled_total += 1
                    if claimed_part in self.adjacent_parts.get((folio, rand_line), set()):
                        shuffled_adj += 1

            if shuffled_total > 0:
                shuffled_rates.append(shuffled_adj / shuffled_total)

        if not shuffled_rates:
            return 0.0, 1.0

        baseline_rate = np.mean(shuffled_rates)

        # Calculate p-value: proportion of shuffled >= observed
        p_value = np.mean([r >= observed_rate for r in shuffled_rates])

        return baseline_rate, p_value

    def test_mapping(self, stem: str, claimed_part: str,
                     n_shuffles: int = 1000, section: str = 'herbal') -> dict:
        """
        Test a proposed semantic mapping.

        Args:
            stem: The stem to test (e.g., 'od', 'ed')
            claimed_part: The claimed plant part (e.g., 'stalk', 'root')
            n_shuffles: Number of shuffle iterations for baseline
            section: Which section to search ('herbal', 'all')

        Returns:
            {
                'stem': str,
                'claimed_part': str,
                'occurrences': int,
                'occurrences_in_annotated': int,
                'adjacent_matches': int,
                'match_rate': float,
                'baseline_rate': float,
                'p_value': float,
                'verdict': 'PASS' | 'FAIL' | 'BORDERLINE' | 'INSUFFICIENT_DATA'
            }
        """
        positions = self._find_stem_positions(stem, section)
        adjacent, total = self._count_adjacencies(positions, claimed_part)

        result = {
            'stem': stem,
            'claimed_part': claimed_part,
            'occurrences': len(positions),
            'occurrences_in_annotated': total,
            'adjacent_matches': adjacent,
            'match_rate': adjacent / total if total > 0 else 0.0,
            'baseline_rate': 0.0,
            'p_value': 1.0,
            'verdict': 'INSUFFICIENT_DATA'
        }

        if total < 10:
            return result

        baseline_rate, p_value = self._shuffle_test(positions, claimed_part, n_shuffles)

        result['baseline_rate'] = baseline_rate
        result['p_value'] = p_value

        # Determine verdict
        match_rate = result['match_rate']

        if match_rate >= self.PASS_THRESHOLD and p_value < self.P_VALUE_THRESHOLD:
            result['verdict'] = 'PASS'
        elif match_rate < 0.30 or p_value > 0.05:
            result['verdict'] = 'FAIL'
        else:
            result['verdict'] = 'BORDERLINE'

        return result

    def run_forbid_check(self, stem: str, claimed_part: str,
                         section: str = 'herbal') -> dict:
        """
        Check if stem correlates with WRONG parts at >20% (forbid check).

        Args:
            stem: The stem to check
            claimed_part: The claimed correct part
            section: Which section to search

        Returns:
            {
                'stem': str,
                'claimed_part': str,
                'wrong_part_rates': {part: rate},
                'max_wrong_rate': float,
                'max_wrong_part': str,
                'forbid_violated': bool,
                'verdict': 'CLEAN' | 'SUSPECT' | 'VIOLATED'
            }
        """
        positions = self._find_stem_positions(stem, section)
        wrong_counts = self._count_wrong_part_adjacencies(positions, claimed_part)

        wrong_rates = {}
        for part, (adj, total) in wrong_counts.items():
            wrong_rates[part] = adj / total if total > 0 else 0.0

        max_wrong_rate = max(wrong_rates.values()) if wrong_rates else 0.0
        max_wrong_part = max(wrong_rates.keys(), key=lambda k: wrong_rates[k]) if wrong_rates else ''

        result = {
            'stem': stem,
            'claimed_part': claimed_part,
            'wrong_part_rates': wrong_rates,
            'max_wrong_rate': max_wrong_rate,
            'max_wrong_part': max_wrong_part,
            'forbid_violated': max_wrong_rate > self.FORBID_THRESHOLD
        }

        if max_wrong_rate > 0.25:
            result['verdict'] = 'VIOLATED'
        elif max_wrong_rate > self.FORBID_THRESHOLD:
            result['verdict'] = 'SUSPECT'
        else:
            result['verdict'] = 'CLEAN'

        return result

    def test_all_parts(self, stem: str, n_shuffles: int = 1000,
                       section: str = 'herbal') -> List[dict]:
        """
        Test a stem against all possible plant parts.

        Returns sorted list of results (best match first).
        """
        results = []
        for part in self.PLANT_PARTS:
            result = self.test_mapping(stem, part, n_shuffles, section)
            results.append(result)

        # Sort by match_rate descending
        results.sort(key=lambda x: x['match_rate'], reverse=True)
        return results

    def summary_report(self, stem: str, claimed_part: str,
                       n_shuffles: int = 1000, section: str = 'herbal') -> str:
        """Generate a summary report for a stem mapping test."""
        mapping_result = self.test_mapping(stem, claimed_part, n_shuffles, section)
        forbid_result = self.run_forbid_check(stem, claimed_part, section)

        lines = [
            f"=== Mapping Test: '{stem}' → {claimed_part} ===",
            "",
            "Occurrence Statistics:",
            f"  Total occurrences: {mapping_result['occurrences']}",
            f"  In annotated folios: {mapping_result['occurrences_in_annotated']}",
            f"  Adjacent to {claimed_part}: {mapping_result['adjacent_matches']}",
            "",
            "Correlation Rates:",
            f"  Match rate: {mapping_result['match_rate']:.1%}",
            f"  Baseline rate: {mapping_result['baseline_rate']:.1%}",
            f"  p-value: {mapping_result['p_value']:.4f}",
            "",
            f"VERDICT: {mapping_result['verdict']}",
            "",
            "Forbid Check (wrong-part correlations):",
        ]

        for part, rate in sorted(forbid_result['wrong_part_rates'].items(),
                                  key=lambda x: x[1], reverse=True):
            flag = " [!]" if rate > self.FORBID_THRESHOLD else ""
            lines.append(f"  {part}: {rate:.1%}{flag}")

        lines.append("")
        lines.append(f"Forbid verdict: {forbid_result['verdict']}")

        return "\n".join(lines)


def create_synthetic_annotations() -> Dict[str, dict]:
    """
    Create synthetic/placeholder annotations for testing.
    Uses heuristics based on typical herbal manuscript layouts.
    """
    annotations = {}

    # For herbal folios f1r-f66v, create basic layout annotations
    # Heuristic: lower lines = root, middle = stalk, upper = leaf/flower
    for i in range(1, 67):
        for side in ['r', 'v']:
            folio = f'f{i}{side}'

            # Typical herbal page has ~20-30 lines
            # Lower 1/3: root area (lines 1-8)
            # Middle 1/3: stalk area (lines 9-16)
            # Upper 1/3: leaf/flower area (lines 17-24)

            annotations[folio] = {
                'plant_parts': ['root', 'stalk', 'leaf', 'flower'],
                'root_lines': list(range(1, 9)),
                'stalk_lines': list(range(9, 17)),
                'leaf_lines': list(range(17, 22)),
                'flower_lines': list(range(22, 28)),
                'seed_lines': [],
                'vessel_lines': []
            }

    return annotations


def main():
    """Test the validator with synthetic annotations."""
    print("Loading ZFD data...")
    loader = ZFDLoader()

    print("Creating synthetic annotations...")
    annotations = create_synthetic_annotations()

    print("Initializing validator...")
    validator = ImageAdjacentValidator(loader, annotations)

    print("\n" + "=" * 50)
    print("Testing with SYNTHETIC annotations (placeholder)")
    print("Real validation requires manual folio annotations")
    print("=" * 50)

    # Test 'ed' (validated root mapping)
    print("\n--- Testing 'ed' → root (CONFIRMED mapping) ---")
    print(validator.summary_report('ed', 'root', n_shuffles=500))

    # Test 'od' (borderline stalk mapping)
    print("\n--- Testing 'od' → stalk (CANDIDATE mapping) ---")
    print(validator.summary_report('od', 'stalk', n_shuffles=500))

    # Test all parts for 'od'
    print("\n--- Testing 'od' against all plant parts ---")
    all_results = validator.test_all_parts('od', n_shuffles=500)
    for r in all_results:
        print(f"  {r['claimed_part']}: {r['match_rate']:.1%} (p={r['p_value']:.3f}) - {r['verdict']}")


if __name__ == "__main__":
    main()
