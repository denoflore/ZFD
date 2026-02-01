"""
Phase 4 Addendum: Geometric Topology Test

Tests "al" and "ar" as GEOMETRIC markers:
- 'al' = lateral divergence (branch points)
- 'ar' = terminal divergence (endpoints)

Based on Curio's insight: "If 'od' is the vertical vector,
then 'al' and 'ar' must be the diverging vectors."
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent))

from zfd_loader import ZFDLoader
from image_adjacent import ImageAdjacentValidator

# =============================================================================
# GEOMETRIC ANNOTATIONS
# Based on topological analysis of plant structure
# =============================================================================

GEOMETRIC_ANNOTATIONS = {
    # =========================================================================
    # HIGH al/ar - Should have RICH geometric structure
    # =========================================================================

    "f58r": {
        "annotation_method": "GEOMETRIC",
        "max_lines": 14,
        "geometric_analysis": {
            "axis_prominence": "MEDIUM",
            "branch_count": "MANY",  # Multiple stem branches
            "terminal_count": "MANY",  # Many flower heads
            "branch_density": "HIGH",
            "terminal_density": "HIGH",
            "geometry_type": "UMBELLIFER",
            "notes": "Multiple branching stems, each ending in flower head"
        },
        # Geometric zones (not plant-part zones)
        "axis_lines": [8, 9, 10, 11, 12],  # Central stalk area
        "branch_lines": [4, 5, 6, 7, 8, 9, 10],  # Where stems diverge
        "terminal_lines": [1, 2, 3, 4, 5, 6],  # Where flower heads are
        "anchor_lines": [12, 13, 14],  # Root area
        "expected_al": "HIGH",
        "expected_ar": "HIGH",
        "confidence": "HIGH"
    },

    "f34r": {
        "annotation_method": "GEOMETRIC",
        "max_lines": 16,
        "geometric_analysis": {
            "axis_prominence": "HIGH",
            "branch_count": "FEW",  # Single main stem
            "terminal_count": "ONE",  # One dramatic flower
            "branch_density": "LOW",
            "terminal_density": "HIGH",  # But very prominent
            "geometry_type": "SINGLE_TERMINAL",
            "notes": "Single stem leads to dramatic terminal flower"
        },
        "axis_lines": [8, 9, 10, 11, 12, 13, 14],  # Long stem
        "branch_lines": [6, 7, 8, 9],  # Calyx area where structure changes
        "terminal_lines": [1, 2, 3, 4, 5, 6],  # Dramatic flower at top
        "anchor_lines": [15, 16],  # Root at bottom
        "expected_al": "LOW",
        "expected_ar": "HIGH",
        "confidence": "HIGH"
    },

    "f17v": {
        "annotation_method": "GEOMETRIC",
        "max_lines": 20,
        "geometric_analysis": {
            "axis_prominence": "HIGH",
            "branch_count": "MANY",  # Paired leaves = many branch points
            "terminal_count": "ONE",  # Flower cluster at top
            "branch_density": "HIGH",
            "terminal_density": "MEDIUM",
            "geometry_type": "PAIRED_BRANCHES",
            "notes": "Regular paired leaf branches along axis, terminal flower"
        },
        "axis_lines": [8, 9, 10, 11, 12, 13, 14, 15, 16, 17],  # Long stem
        "branch_lines": [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],  # Many branch points
        "terminal_lines": [1, 2, 3, 4, 5],  # Flower at top
        "anchor_lines": [18, 19, 20],  # Roots
        "expected_al": "HIGH",
        "expected_ar": "MEDIUM",
        "confidence": "HIGH"
    },

    # =========================================================================
    # LOW al/ar - Should have SIMPLE geometric structure
    # =========================================================================

    "f3r": {
        "annotation_method": "GEOMETRIC",
        "max_lines": 31,
        "geometric_analysis": {
            "axis_prominence": "HIGH",
            "branch_count": "NONE",  # Compound leaf = ONE unit
            "terminal_count": "NONE",  # No flower
            "branch_density": "NONE",
            "terminal_density": "NONE",
            "geometry_type": "SIMPLE_AXIS",
            "notes": "Single stem with compound leaf (one unit), no terminal"
        },
        "axis_lines": [15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27],  # Stem
        "branch_lines": [],  # Compound leaf = not counted as branches!
        "terminal_lines": [],  # No flower terminal
        "anchor_lines": [28, 29, 30, 31],  # Roots
        "expected_al": "LOW",
        "expected_ar": "LOW",
        "confidence": "HIGH",
        "negative_control": True
    },

    "f51r": {
        "annotation_method": "GEOMETRIC",
        "max_lines": 15,
        "geometric_analysis": {
            "axis_prominence": "VERY_HIGH",  # Stalk dominant
            "branch_count": "MODERATE",  # Some stem branches
            "terminal_count": "FEW",  # Small flower bud
            "branch_density": "MEDIUM",
            "terminal_density": "LOW",
            "geometry_type": "AXIS_DOMINANT",
            "notes": "Strong vertical axis, moderate branching, minimal terminal"
        },
        "axis_lines": [5, 6, 7, 8, 9, 10, 11, 12],  # Dominant stalk
        "branch_lines": [4, 5, 6, 7, 8, 9],  # Branch junctions
        "terminal_lines": [1, 2, 3],  # Small bud at top
        "anchor_lines": [13, 14, 15],  # Stylized root
        "expected_al": "MEDIUM",
        "expected_ar": "LOW",
        "confidence": "HIGH"
    },

    "f20r": {
        "annotation_method": "GEOMETRIC",
        "max_lines": 17,
        "geometric_analysis": {
            "axis_prominence": "LOW",  # No single main axis
            "branch_count": "MANY",  # Multiple branching stems
            "terminal_count": "MANY",  # Tips with seed heads
            "branch_density": "VERY_HIGH",
            "terminal_density": "HIGH",
            "geometry_type": "MULTI_BRANCH",
            "notes": "Highly branched with no dominant axis, many terminals"
        },
        "axis_lines": [],  # No single dominant axis
        "branch_lines": [8, 9, 10, 11, 12, 13, 14, 15, 16, 17],  # Extensive branching
        "terminal_lines": [8, 9, 10, 11, 12],  # Multiple branch tips
        "anchor_lines": [],  # No clear root
        "expected_al": "HIGH",
        "expected_ar": "MEDIUM",
        "confidence": "HIGH"
    },

    "f53v": {
        "annotation_method": "GEOMETRIC",
        "max_lines": 20,
        "geometric_analysis": {
            "axis_prominence": "HIGH",  # Clear central stem
            "branch_count": "MODERATE",  # Leaves and berries branch off
            "terminal_count": "MANY",  # Berry clusters at ends
            "branch_density": "MEDIUM",
            "terminal_density": "HIGH",
            "geometry_type": "AXIS_WITH_CLUSTERS",
            "notes": "Main axis with lateral berries/leaves as terminals"
        },
        "axis_lines": [7, 8, 9, 10, 11, 12, 13, 14, 15, 16],  # Central stem
        "branch_lines": [6, 7, 8, 9, 10, 11, 12],  # Where leaves/berries attach
        "terminal_lines": [4, 5, 6, 7, 8, 9, 10],  # Berry clusters
        "anchor_lines": [17, 18, 19, 20],  # Bulbous root
        "expected_al": "MEDIUM",
        "expected_ar": "HIGH",
        "confidence": "HIGH"
    }
}


def load_annotations():
    """Load current folio annotations."""
    ann_path = Path(__file__).parent / "folio_annotations.json"
    with open(ann_path, 'r') as f:
        return json.load(f)


def run_geometric_correlation(loader, annotations):
    """Test al/ar against geometric zones instead of plant-part zones."""

    print("="*70)
    print("GEOMETRIC CORRELATION TEST")
    print("="*70)

    results = {}

    for folio_id, geo_ann in GEOMETRIC_ANNOTATIONS.items():
        print(f"\n--- {folio_id} ---")
        print(f"Geometry type: {geo_ann['geometric_analysis']['geometry_type']}")

        # Get al/ar occurrences in this folio
        al_occs = [o for o in loader.find_stem_occurrences('al', section='herbal')
                   if o['folio'] == folio_id]
        ar_occs = [o for o in loader.find_stem_occurrences('ar', section='herbal')
                   if o['folio'] == folio_id]

        # Count in geometric zones
        al_in_branch = sum(1 for o in al_occs if o['line_num'] in geo_ann.get('branch_lines', []))
        al_in_terminal = sum(1 for o in al_occs if o['line_num'] in geo_ann.get('terminal_lines', []))
        al_in_axis = sum(1 for o in al_occs if o['line_num'] in geo_ann.get('axis_lines', []))

        ar_in_branch = sum(1 for o in ar_occs if o['line_num'] in geo_ann.get('branch_lines', []))
        ar_in_terminal = sum(1 for o in ar_occs if o['line_num'] in geo_ann.get('terminal_lines', []))
        ar_in_axis = sum(1 for o in ar_occs if o['line_num'] in geo_ann.get('axis_lines', []))

        al_total = len(al_occs)
        ar_total = len(ar_occs)

        print(f"  'al' total: {al_total}")
        if al_total > 0:
            branch_pct = al_in_branch / al_total * 100
            terminal_pct = al_in_terminal / al_total * 100
            axis_pct = al_in_axis / al_total * 100
            print(f"    in BRANCH zone: {al_in_branch} ({branch_pct:.0f}%)")
            print(f"    in TERMINAL zone: {al_in_terminal} ({terminal_pct:.0f}%)")
            print(f"    in AXIS zone: {al_in_axis} ({axis_pct:.0f}%)")

        print(f"  'ar' total: {ar_total}")
        if ar_total > 0:
            branch_pct = ar_in_branch / ar_total * 100
            terminal_pct = ar_in_terminal / ar_total * 100
            axis_pct = ar_in_axis / ar_total * 100
            print(f"    in BRANCH zone: {ar_in_branch} ({branch_pct:.0f}%)")
            print(f"    in TERMINAL zone: {ar_in_terminal} ({terminal_pct:.0f}%)")
            print(f"    in AXIS zone: {ar_in_axis} ({axis_pct:.0f}%)")

        print(f"  Expected: al={geo_ann['expected_al']}, ar={geo_ann['expected_ar']}")

        results[folio_id] = {
            'al_total': al_total,
            'ar_total': ar_total,
            'al_in_branch': al_in_branch,
            'al_in_terminal': al_in_terminal,
            'ar_in_branch': ar_in_branch,
            'ar_in_terminal': ar_in_terminal,
            'expected_al': geo_ann['expected_al'],
            'expected_ar': geo_ann['expected_ar'],
            'geometry_type': geo_ann['geometric_analysis']['geometry_type']
        }

    return results


def analyze_geometric_hypothesis(results):
    """Analyze whether al correlates with branches, ar with terminals."""

    print("\n" + "="*70)
    print("GEOMETRIC HYPOTHESIS ANALYSIS")
    print("="*70)

    # Calculate overall correlations
    total_al = sum(r['al_total'] for r in results.values())
    total_ar = sum(r['ar_total'] for r in results.values())

    al_in_branch = sum(r['al_in_branch'] for r in results.values())
    al_in_terminal = sum(r['al_in_terminal'] for r in results.values())
    ar_in_branch = sum(r['ar_in_branch'] for r in results.values())
    ar_in_terminal = sum(r['ar_in_terminal'] for r in results.values())

    print(f"\nOverall 'al' distribution (n={total_al}):")
    if total_al > 0:
        print(f"  In BRANCH zones: {al_in_branch} ({al_in_branch/total_al*100:.1f}%)")
        print(f"  In TERMINAL zones: {al_in_terminal} ({al_in_terminal/total_al*100:.1f}%)")

    print(f"\nOverall 'ar' distribution (n={total_ar}):")
    if total_ar > 0:
        print(f"  In BRANCH zones: {ar_in_branch} ({ar_in_branch/total_ar*100:.1f}%)")
        print(f"  In TERMINAL zones: {ar_in_terminal} ({ar_in_terminal/total_ar*100:.1f}%)")

    # Test the key prediction: al should prefer branches, ar should prefer terminals
    print("\n" + "-"*70)
    print("KEY GEOMETRIC PREDICTIONS:")
    print("-"*70)

    if total_al > 0 and total_ar > 0:
        al_branch_rate = al_in_branch / total_al
        al_terminal_rate = al_in_terminal / total_al
        ar_branch_rate = ar_in_branch / total_ar
        ar_terminal_rate = ar_in_terminal / total_ar

        print(f"\n  Prediction 1: 'al' should cluster in BRANCH zones more than 'ar'")
        print(f"    al in branches: {al_branch_rate*100:.1f}%")
        print(f"    ar in branches: {ar_branch_rate*100:.1f}%")
        if al_branch_rate > ar_branch_rate:
            print(f"    → SUPPORTED: al has {al_branch_rate/ar_branch_rate:.2f}x more branch preference")
        else:
            print(f"    → NOT SUPPORTED")

        print(f"\n  Prediction 2: 'ar' should cluster in TERMINAL zones more than 'al'")
        print(f"    ar in terminals: {ar_terminal_rate*100:.1f}%")
        print(f"    al in terminals: {al_terminal_rate*100:.1f}%")
        if ar_terminal_rate > al_terminal_rate:
            print(f"    → SUPPORTED: ar has {ar_terminal_rate/al_terminal_rate:.2f}x more terminal preference")
        else:
            print(f"    → NOT SUPPORTED")

    # Geometry type analysis
    print("\n" + "-"*70)
    print("BY GEOMETRY TYPE:")
    print("-"*70)

    by_type = defaultdict(lambda: {'al': 0, 'ar': 0, 'count': 0})
    for folio_id, r in results.items():
        gtype = r['geometry_type']
        by_type[gtype]['al'] += r['al_total']
        by_type[gtype]['ar'] += r['ar_total']
        by_type[gtype]['count'] += 1

    for gtype, counts in sorted(by_type.items()):
        al_avg = counts['al'] / counts['count']
        ar_avg = counts['ar'] / counts['count']
        print(f"\n  {gtype}:")
        print(f"    avg al: {al_avg:.1f}, avg ar: {ar_avg:.1f}")


def main():
    print("="*70)
    print("PHASE 4 ADDENDUM: GEOMETRIC TOPOLOGY TEST")
    print("="*70)
    print(f"Based on Curio's branching insight")
    print(f"Started: {datetime.now().isoformat()}")

    # Load data
    loader = ZFDLoader('.')
    annotations = load_annotations()

    # Run geometric correlation
    results = run_geometric_correlation(loader, annotations['folios'])

    # Analyze geometric hypothesis
    analyze_geometric_hypothesis(results)

    # Save results
    results_path = Path(__file__).parent / "results" / "phase4_geometric_results.json"
    with open(results_path, 'w') as f:
        json.dump({
            'generated': datetime.now().isoformat(),
            'results': results
        }, f, indent=2)

    print(f"\n\nResults saved to: {results_path}")
    print(f"Completed: {datetime.now().isoformat()}")


if __name__ == "__main__":
    main()
