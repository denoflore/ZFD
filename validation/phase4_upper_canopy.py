"""
Phase 4: Upper Canopy Validation

Tests "al" (leaf) and "ar" (flower) hypotheses using embodied visual annotation.
Building on Phase 3 confirmation of "ed" (root) and "od" (stalk).
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add validation directory to path
sys.path.insert(0, str(Path(__file__).parent))

from zfd_loader import ZFDLoader
from image_adjacent import ImageAdjacentValidator

# =============================================================================
# PHASE 4 VISUAL ANNOTATIONS
# =============================================================================

PHASE4_VISUAL_ANNOTATIONS = {
    # =========================================================================
    # FLOWER-FOCUSED FOLIOS
    # =========================================================================

    "f58r": {
        "annotation_method": "VISUAL",
        "annotator": "claude_code_phase4",
        "annotation_date": "2026-02-01",
        "max_lines": 14,
        "illustration_analysis": {
            "plant_type": "umbellifer with multiple flower heads",
            "layout": "plant centered, text in two columns below",
            "dominant_feature": "FLOWER",
            "root_depicted": True,
            "root_style": "prominent branching roots",
            "stalk_depicted": True,
            "stalk_style": "multiple green branching stems",
            "leaf_depicted": True,
            "leaf_style": "minimal - few small leaves on stems",
            "flower_depicted": True,
            "flower_style": "VERY PROMINENT - numerous umbel flower heads, blue flower at top",
            "notes": "FLOWER-DOMINANT. Highest al (128) and ar (70). Perfect test case."
        },
        "plant_parts": ["root", "stalk", "leaf", "flower"],
        "root_lines": [12, 13, 14],  # Bottom 21%
        "stalk_lines": [6, 7, 8, 9, 10, 11],  # Middle 43%
        "leaf_lines": [5, 6, 7, 8],  # Sparse, along stems
        "flower_lines": [1, 2, 3, 4, 5, 6, 7, 8],  # Upper 57% - flowers dominate
        "seed_lines": [],
        "vessel_lines": [],
        "confidence": "VISUAL_HIGH",
        "phase4_notes": {
            "flower_prominence": "VERY_HIGH",
            "leaf_prominence": "LOW",
            "expected_ar_correlation": "HIGH",
            "expected_al_correlation": "LOW"
        }
    },

    "f34r": {
        "annotation_method": "VISUAL",
        "annotator": "claude_code_phase4",
        "annotation_date": "2026-02-01",
        "max_lines": 16,
        "illustration_analysis": {
            "plant_type": "bulbous plant with striking flower",
            "layout": "plant right side, text in two paragraphs left",
            "dominant_feature": "FLOWER",
            "root_depicted": True,
            "root_style": "thin root at bottom",
            "stalk_depicted": True,
            "stalk_style": "pink/red central stem",
            "leaf_depicted": True,
            "leaf_style": "large olive-tan calyx/bulb structure",
            "flower_depicted": True,
            "flower_style": "VERY PROMINENT - striking blue curved petals with red center",
            "notes": "FLOWER-DOMINANT. The flower is the clear focal point."
        },
        "plant_parts": ["root", "stalk", "leaf", "flower"],
        "root_lines": [15, 16],  # Bottom 12%
        "stalk_lines": [10, 11, 12, 13, 14],  # Middle
        "leaf_lines": [6, 7, 8, 9, 10, 11],  # Calyx/bulb area
        "flower_lines": [1, 2, 3, 4, 5, 6],  # Top 37% - flower prominent
        "seed_lines": [],
        "vessel_lines": [],
        "confidence": "VISUAL_HIGH",
        "phase4_notes": {
            "flower_prominence": "VERY_HIGH",
            "leaf_prominence": "MEDIUM",
            "expected_ar_correlation": "HIGH",
            "expected_al_correlation": "MEDIUM"
        }
    },

    "f33v": {
        "annotation_method": "VISUAL",
        "annotator": "claude_code_phase4",
        "annotation_date": "2026-02-01",
        "max_lines": 14,
        "illustration_analysis": {
            "plant_type": "tree-like plant with fruits and flower",
            "layout": "plant right side, text above in two paragraphs",
            "dominant_feature": "FLOWER_AND_FRUIT",
            "root_depicted": True,
            "root_style": "branching roots with animal figure",
            "stalk_depicted": True,
            "stalk_style": "tree-like branching trunk",
            "leaf_depicted": False,
            "leaf_style": "structures appear to be fruits, not leaves",
            "flower_depicted": True,
            "flower_style": "PROMINENT white/cream detailed flower at top",
            "fruit_depicted": True,
            "fruit_style": "numerous green/brown oval fruits on branches",
            "notes": "FLOWER + FRUIT focused. Unusual - fruits may be the 'seed' element."
        },
        "plant_parts": ["root", "stalk", "flower", "seed"],
        "root_lines": [12, 13, 14],  # Bottom with animal
        "stalk_lines": [7, 8, 9, 10, 11],  # Trunk
        "leaf_lines": [],  # No true leaves
        "flower_lines": [1, 2, 3, 4, 5, 6],  # Top - flower
        "seed_lines": [5, 6, 7, 8, 9, 10, 11],  # Fruits throughout
        "vessel_lines": [],
        "confidence": "VISUAL_HIGH",
        "phase4_notes": {
            "flower_prominence": "HIGH",
            "leaf_prominence": "NONE",
            "expected_ar_correlation": "HIGH",
            "expected_al_correlation": "LOW"
        }
    },

    "f17v": {
        "annotation_method": "VISUAL",
        "annotator": "claude_code_phase4",
        "annotation_date": "2026-02-01",
        "max_lines": 20,
        "illustration_analysis": {
            "plant_type": "herbaceous plant with paired leaves and flower",
            "layout": "plant right side, text left wrapping",
            "dominant_feature": "BALANCED_LEAF_FLOWER",
            "root_depicted": True,
            "root_style": "branching tan roots",
            "stalk_depicted": True,
            "stalk_style": "green central stem",
            "leaf_depicted": True,
            "leaf_style": "VERY PROMINENT - many paired oval/oblong leaves",
            "flower_depicted": True,
            "flower_style": "PROMINENT - blue flower cluster with red center at top",
            "notes": "BALANCED - both leaves and flower prominent. High ol (44) and or (31)."
        },
        "plant_parts": ["root", "stalk", "leaf", "flower"],
        "root_lines": [18, 19, 20],  # Bottom 15%
        "stalk_lines": [8, 9, 10, 11, 12, 13, 14, 15, 16, 17],  # Middle
        "leaf_lines": [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],  # Throughout - 65%
        "flower_lines": [1, 2, 3, 4, 5],  # Top 25%
        "seed_lines": [],
        "vessel_lines": [],
        "confidence": "VISUAL_HIGH",
        "phase4_notes": {
            "flower_prominence": "HIGH",
            "leaf_prominence": "VERY_HIGH",
            "expected_ar_correlation": "MEDIUM",
            "expected_al_correlation": "HIGH"
        }
    },

    # =========================================================================
    # LEAF-FOCUSED FOLIOS
    # =========================================================================

    "f3r": {
        "annotation_method": "VISUAL",
        "annotator": "claude_code_phase4",
        "annotation_date": "2026-02-01",
        "max_lines": 31,
        "illustration_analysis": {
            "plant_type": "large compound-leaved plant",
            "layout": "plant right side, text left in 4 paragraphs",
            "dominant_feature": "LEAF",
            "root_depicted": True,
            "root_style": "prominent branching brown roots",
            "stalk_depicted": True,
            "stalk_style": "central pale/green stem",
            "leaf_depicted": True,
            "leaf_style": "EXTREMELY PROMINENT - large feathery compound leaves, red/green",
            "flower_depicted": False,
            "flower_style": "NO FLOWER DEPICTED",
            "notes": "LEAF-DOMINANT. NO FLOWER. High ol (31). Perfect NEGATIVE control for ar."
        },
        "plant_parts": ["root", "stalk", "leaf"],
        "root_lines": [28, 29, 30, 31],  # Bottom 13%
        "stalk_lines": [15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27],  # Middle
        "leaf_lines": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27],  # 87% - leaves dominate
        "flower_lines": [],  # NO FLOWER
        "seed_lines": [],
        "vessel_lines": [],
        "confidence": "VISUAL_HIGH",
        "phase4_notes": {
            "flower_prominence": "NONE",
            "leaf_prominence": "EXTREME",
            "expected_ar_correlation": "LOW/ZERO",
            "expected_al_correlation": "VERY_HIGH",
            "negative_control": True,
            "negative_control_for": "ar/flower"
        }
    },

    "f55r": {
        "annotation_method": "VISUAL",
        "annotator": "claude_code_phase4",
        "annotation_date": "2026-02-01",
        "max_lines": 26,
        "illustration_analysis": {
            "plant_type": "fern-like plant with feathery fronds",
            "layout": "plant right side, text left in two paragraphs",
            "dominant_feature": "LEAF",
            "root_depicted": True,
            "root_style": "small red root at bottom",
            "stalk_depicted": False,
            "stalk_style": "minimal - plant emerges directly into leaves",
            "leaf_depicted": True,
            "leaf_style": "VERY PROMINENT - large dark green feathery fronds",
            "flower_depicted": True,
            "flower_style": "small decorative flower at top right corner",
            "notes": "LEAF-DOMINANT. Small flower present but leaves dominate."
        },
        "plant_parts": ["root", "leaf", "flower"],
        "root_lines": [25, 26],  # Bottom 8%
        "stalk_lines": [],  # Minimal stalk
        "leaf_lines": [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],  # 77% - leaves dominate
        "flower_lines": [1, 2, 3, 4],  # Small flower top right
        "seed_lines": [],
        "vessel_lines": [],
        "confidence": "VISUAL_HIGH",
        "phase4_notes": {
            "flower_prominence": "LOW",
            "leaf_prominence": "VERY_HIGH",
            "expected_ar_correlation": "LOW",
            "expected_al_correlation": "HIGH"
        }
    },

    "f42r": {
        "annotation_method": "VISUAL",
        "annotator": "claude_code_phase4",
        "annotation_date": "2026-02-01",
        "max_lines": 18,
        "illustration_analysis": {
            "plant_type": "multiple plants - curling leaves center, narrow leaves left",
            "layout": "plants in lower half, text above in two paragraphs",
            "dominant_feature": "LEAF",
            "root_depicted": True,
            "root_style": "fibrous roots/base visible",
            "stalk_depicted": True,
            "stalk_style": "central base with multiple stems",
            "leaf_depicted": True,
            "leaf_style": "PROMINENT - curling green leaves center, narrow leaves left",
            "flower_depicted": False,
            "flower_style": "dried seed heads on right plant only",
            "snake_figure": True,
            "notes": "LEAF-FOCUSED with multiple plant elements. Snake figure present."
        },
        "plant_parts": ["root", "stalk", "leaf", "seed"],
        "root_lines": [16, 17, 18],  # Bottom
        "stalk_lines": [12, 13, 14, 15],  # Lower middle
        "leaf_lines": [8, 9, 10, 11, 12, 13, 14, 15],  # Middle - 44%
        "flower_lines": [],  # No true flowers
        "seed_lines": [9, 10, 11],  # Seed heads
        "vessel_lines": [],
        "confidence": "VISUAL_MEDIUM",
        "phase4_notes": {
            "flower_prominence": "NONE",
            "leaf_prominence": "HIGH",
            "expected_ar_correlation": "LOW",
            "expected_al_correlation": "MEDIUM"
        }
    },
}


def load_annotations():
    """Load current folio annotations."""
    ann_path = Path(__file__).parent / "folio_annotations.json"
    with open(ann_path, 'r') as f:
        return json.load(f)


def save_annotations(data):
    """Save updated annotations."""
    ann_path = Path(__file__).parent / "folio_annotations.json"
    with open(ann_path, 'w') as f:
        json.dump(data, f, indent=2)


def update_annotations_with_phase4():
    """Apply Phase 4 visual annotations."""
    data = load_annotations()

    # Update metadata
    data['version'] = "4.0"
    data['description'] = "Plant-part annotations with Phase 4 (leaf/flower) visual analysis"
    data['phase'] = "4"
    data['last_updated'] = datetime.now().isoformat()

    # Apply Phase 4 annotations
    print("Applying Phase 4 visual annotations...")
    for folio_id, ann in PHASE4_VISUAL_ANNOTATIONS.items():
        if folio_id not in data['folios']:
            data['folios'][folio_id] = {}
        data['folios'][folio_id].update(ann)
        print(f"  Updated {folio_id}")

    save_annotations(data)
    print(f"Saved {len(PHASE4_VISUAL_ANNOTATIONS)} Phase 4 annotations")
    return data


def analyze_stem_distribution(loader, stems, part_name):
    """Analyze folio-level distribution of stems."""
    print(f"\n{'='*60}")
    print(f"STEM DISTRIBUTION: {part_name.upper()}")
    print(f"{'='*60}")

    for stem in stems:
        occs = loader.find_stem_occurrences(stem, section='herbal')
        if not occs:
            print(f"  {stem}: 0 occurrences")
            continue

        folio_counts = defaultdict(int)
        for o in occs:
            folio_counts[o['folio']] += 1

        sorted_folios = sorted(folio_counts.items(), key=lambda x: -x[1])[:8]
        total = len(occs)
        n_folios = len(folio_counts)

        print(f"\n  '{stem}': {total} occurrences in {n_folios} folios")
        print(f"  Top folios: {', '.join(f'{f}({c})' for f, c in sorted_folios)}")


def run_phase4_validation(loader, annotations):
    """Run Phase 4 statistical validation for al/ar."""
    print("\n" + "="*60)
    print("PHASE 4: STATISTICAL VALIDATION")
    print("="*60)

    validator = ImageAdjacentValidator(loader, annotations)

    results = {}

    # Test leaf candidates
    print("\n--- LEAF HYPOTHESIS (al/ol) ---")
    leaf_stems = ['al', 'ol', 'chol']
    for stem in leaf_stems:
        result = validator.test_mapping(stem, 'leaf', n_shuffles=1000)
        results[f'{stem}_leaf'] = result
        print(f"\n  {stem} → leaf:")
        print(f"    Match rate: {result['match_rate']:.1%}")
        print(f"    Baseline:   {result['baseline_rate']:.1%}")
        print(f"    P-value:    {result['p_value']:.3f}")
        print(f"    Verdict:    {result['verdict']}")

    # Test flower candidates
    print("\n--- FLOWER HYPOTHESIS (ar/or) ---")
    flower_stems = ['ar', 'or']
    for stem in flower_stems:
        result = validator.test_mapping(stem, 'flower', n_shuffles=1000)
        results[f'{stem}_flower'] = result
        print(f"\n  {stem} → flower:")
        print(f"    Match rate: {result['match_rate']:.1%}")
        print(f"    Baseline:   {result['baseline_rate']:.1%}")
        print(f"    P-value:    {result['p_value']:.3f}")
        print(f"    Verdict:    {result['verdict']}")

    # Run forbid checks
    print("\n--- FORBID CHECKS ---")
    for stem, claimed in [('al', 'leaf'), ('ar', 'flower')]:
        forbid = validator.run_forbid_check(stem, claimed)
        results[f'{stem}_forbid'] = forbid
        print(f"\n  {stem} → {claimed} forbid check:")
        for part, rate in forbid['wrong_part_rates'].items():
            flag = " ⚠️" if rate > 0.20 else ""
            print(f"    {part}: {rate:.1%}{flag}")
        print(f"    Max wrong: {forbid['max_wrong_part']} ({forbid['max_wrong_rate']:.1%})")
        print(f"    Violated:  {forbid['forbid_violated']}")

    # Cross-validation: compare al in flower-focused vs leaf-focused folios
    print("\n--- CROSS-VALIDATION ---")

    flower_folios = ['f58r', 'f34r', 'f33v']
    leaf_folios = ['f3r', 'f55r', 'f42r']

    for stem_type, stem in [('al', 'al'), ('ar', 'ar')]:
        occs = loader.find_stem_occurrences(stem, section='herbal')

        flower_count = sum(1 for o in occs if o['folio'] in flower_folios)
        leaf_count = sum(1 for o in occs if o['folio'] in leaf_folios)

        print(f"\n  '{stem}' distribution:")
        print(f"    In flower-focused folios: {flower_count}")
        print(f"    In leaf-focused folios:   {leaf_count}")

        # f3r specific (negative control for flower)
        f3r_count = sum(1 for o in occs if o['folio'] == 'f3r')
        print(f"    In f3r (NO FLOWER):       {f3r_count}")

    return results


def generate_verdict(results):
    """Generate Phase 4 verdict."""
    print("\n" + "="*60)
    print("PHASE 4 VERDICT")
    print("="*60)

    # Evaluate al → leaf
    al_result = results.get('al_leaf', {})
    al_match = al_result.get('match_rate', 0)
    al_p = al_result.get('p_value', 1)
    al_forbid = results.get('al_forbid', {})

    print(f"\n'al' → leaf:")
    print(f"  Match rate: {al_match:.1%} (threshold: ≥40%)")
    print(f"  P-value:    {al_p:.3f} (threshold: <0.05)")

    if al_match >= 0.40 and al_p < 0.05:
        al_verdict = "CONFIRMED"
    elif al_match >= 0.40:
        al_verdict = "BORDERLINE"
    else:
        al_verdict = "NOT_CONFIRMED"

    print(f"  Verdict:    {al_verdict}")

    # Evaluate ar → flower
    ar_result = results.get('ar_flower', {})
    ar_match = ar_result.get('match_rate', 0)
    ar_p = ar_result.get('p_value', 1)
    ar_forbid = results.get('ar_forbid', {})

    print(f"\n'ar' → flower:")
    print(f"  Match rate: {ar_match:.1%} (threshold: ≥40%)")
    print(f"  P-value:    {ar_p:.3f} (threshold: <0.05)")

    if ar_match >= 0.40 and ar_p < 0.05:
        ar_verdict = "CONFIRMED"
    elif ar_match >= 0.40:
        ar_verdict = "BORDERLINE"
    else:
        ar_verdict = "NOT_CONFIRMED"

    print(f"  Verdict:    {ar_verdict}")

    # Summary
    print("\n" + "-"*60)
    print("PLANT MORPHOLOGY VOCABULARY STATUS:")
    print("-"*60)
    print(f"  ed → root:   CONFIRMED (Phase 3)")
    print(f"  od → stalk:  CONDITIONALLY CONFIRMED (Phase 3)")
    print(f"  al → leaf:   {al_verdict}")
    print(f"  ar → flower: {ar_verdict}")

    return {
        'al_leaf': al_verdict,
        'ar_flower': ar_verdict,
        'al_match_rate': al_match,
        'ar_match_rate': ar_match,
        'al_p_value': al_p,
        'ar_p_value': ar_p
    }


def main():
    print("="*60)
    print("ZFD PHASE 4: UPPER CANOPY VALIDATION")
    print("="*60)
    print(f"Started: {datetime.now().isoformat()}")

    # Load data
    print("\nLoading ZFD data...")
    loader = ZFDLoader('.')

    # Update annotations
    print("\nUpdating annotations with Phase 4 data...")
    annotations_data = update_annotations_with_phase4()

    # Analyze stem distributions
    analyze_stem_distribution(loader, ['al', 'ol', 'chol', 'dal'], 'leaf candidates')
    analyze_stem_distribution(loader, ['ar', 'or', 'dar', 'kar'], 'flower candidates')

    # Run validation
    results = run_phase4_validation(loader, annotations_data['folios'])

    # Generate verdict
    verdict = generate_verdict(results)

    # Save results
    results_path = Path(__file__).parent / "results" / "phase4_results.json"
    results_path.parent.mkdir(exist_ok=True)

    with open(results_path, 'w') as f:
        json.dump({
            'generated': datetime.now().isoformat(),
            'validation_results': results,
            'verdict': verdict
        }, f, indent=2, default=str)

    print(f"\nResults saved to: {results_path}")
    print(f"\nCompleted: {datetime.now().isoformat()}")

    return verdict


if __name__ == "__main__":
    main()
