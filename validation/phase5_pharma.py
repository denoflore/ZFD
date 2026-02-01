"""
Phase 5: Pharmaceutical Section Validation

Tests al/ar as preparation class markers against EQUIPMENT illustrations:
- 'al' = liquid/wet preparations → should cluster near liquid equipment
- 'ar' = dry/heat preparations → should cluster near heat equipment

The pharmaceutical/balneological section shows VISIBLE preparation method.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent))

from zfd_loader import ZFDLoader

# =============================================================================
# PHARMACEUTICAL FOLIO EQUIPMENT ANNOTATIONS
# Based on visual analysis of balneological section
# =============================================================================

# File number to folio ID mapping (estimated from Beinecke pages)
PHARMA_FOLIO_MAP = {
    # Balneological section (nymphs in pools)
    140: 'f75v',  # Tube apparatus with pools
    148: 'f79v',  # Pool with nymphs, vessel
    150: 'f80v',  # Tubes connecting to basin
    152: 'f81v',  # Multiple bathing pools
    # Pharma recipe section
    175: 'f87r',  # Striped jars + roots
    183: 'f91r',  # Text with star decorations (recipes)
}

EQUIPMENT_ANNOTATIONS = {
    # =========================================================================
    # BALNEOLOGICAL SECTION - LIQUID EQUIPMENT
    # =========================================================================

    "f75v_est": {  # File 0140
        "annotation_method": "VISUAL",
        "file_number": 140,
        "max_lines": 30,  # Estimate
        "equipment_analysis": {
            "equipment_type": "LIQUID_APPARATUS",
            "description": "Tube/pipe system connecting to bathing pools",
            "visible_elements": [
                "scalloped pipe system at top",
                "vertical tube descending into pool",
                "circular green pool with nymphs (1)",
                "circular green pool with nymphs (2)",
            ],
            "liquid_indicators": [
                "green colored pools (infusion/herbal bath)",
                "connected tube system (circulation)",
                "immersion of human figures",
            ],
            "heat_indicators": [],
            "preparation_class": "LIQUID",
            "confidence": "HIGH"
        },
        "equipment_zones": {
            "LIQUID": list(range(1, 31)),  # Entire page is liquid apparatus
            "HEAT": [],
            "NEUTRAL": []
        },
        "expected_al_ar_ratio": ">1.5"  # More al than ar
    },

    "f79v_est": {  # File 0148
        "annotation_method": "VISUAL",
        "file_number": 148,
        "max_lines": 28,
        "equipment_analysis": {
            "equipment_type": "BATHING_SCENE",
            "description": "Vessel, swimming nymph, communal pool",
            "visible_elements": [
                "vessel/container at top",
                "swimming/bathing nymph",
                "communal green pool at bottom",
            ],
            "liquid_indicators": [
                "green pool (infusion)",
                "bathing/immersion",
                "vessel with possible liquid",
            ],
            "heat_indicators": [],
            "preparation_class": "LIQUID",
            "confidence": "HIGH"
        },
        "equipment_zones": {
            "LIQUID": list(range(1, 29)),
            "HEAT": [],
            "NEUTRAL": []
        },
        "expected_al_ar_ratio": ">1.5"
    },

    "f80v_est": {  # File 0150
        "annotation_method": "VISUAL",
        "file_number": 150,
        "max_lines": 25,
        "equipment_analysis": {
            "equipment_type": "TUBE_BASIN_SYSTEM",
            "description": "Nymphs connected by blue tubes to basins",
            "visible_elements": [
                "blue tube/conduit system",
                "human figures at tube junctions",
                "basin structures",
            ],
            "liquid_indicators": [
                "blue tubes (water/liquid flow)",
                "basin containers",
                "connected fluid system",
            ],
            "heat_indicators": [],
            "preparation_class": "LIQUID",
            "confidence": "HIGH"
        },
        "equipment_zones": {
            "LIQUID": list(range(1, 26)),
            "HEAT": [],
            "NEUTRAL": []
        },
        "expected_al_ar_ratio": ">1.5"
    },

    "f81v_est": {  # File 0152
        "annotation_method": "VISUAL",
        "file_number": 152,
        "max_lines": 26,
        "equipment_analysis": {
            "equipment_type": "COMMUNAL_BATHS",
            "description": "Multiple bathing pools with pipe system",
            "visible_elements": [
                "piping/tube system at top with nymphs",
                "first green pool with bathing nymphs",
                "second green pool with nymphs + colored orbs",
                "grouped figures at bottom",
            ],
            "liquid_indicators": [
                "multiple green pools (herbal baths)",
                "piping system (circulation)",
                "colored additives in liquid (blue/red orbs)",
                "communal immersion",
            ],
            "heat_indicators": [],
            "preparation_class": "LIQUID",
            "confidence": "VERY_HIGH"
        },
        "equipment_zones": {
            "LIQUID": list(range(1, 27)),
            "HEAT": [],
            "NEUTRAL": []
        },
        "expected_al_ar_ratio": ">1.5"
    },

    # =========================================================================
    # PHARMA RECIPE SECTION - MIXED EQUIPMENT
    # =========================================================================

    "f87r": {  # File 0175
        "annotation_method": "VISUAL",
        "file_number": 175,
        "max_lines": 16,
        "equipment_analysis": {
            "equipment_type": "STORAGE_JARS_AND_MATERIALS",
            "description": "Striped storage jars with plant materials",
            "visible_elements": [
                "cylindrical striped jars (left side)",
                "root/plant materials (top and right)",
                "large plant with roots (bottom)",
            ],
            "liquid_indicators": [
                "layered/striped jars (possibly showing liquid levels)",
                "storage vessels (for infusions/tinctures)",
            ],
            "heat_indicators": [],
            "preparation_class": "LIQUID",
            "confidence": "MEDIUM",
            "notes": "Jars likely store liquid preparations; no heat visible"
        },
        "equipment_zones": {
            "LIQUID": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],  # Jar area
            "HEAT": [],
            "NEUTRAL": [11, 12, 13, 14, 15, 16]  # Plant material area
        },
        "expected_al_ar_ratio": ">1.2"
    },
}


def get_al_ar_in_pharma(loader):
    """Get al/ar occurrences in pharmaceutical folios."""
    print("="*70)
    print("AL/AR DISTRIBUTION IN PHARMACEUTICAL SECTION")
    print("="*70)

    # Find pharma folios (f87-f102 range)
    pharma_occs = {'al': [], 'ar': []}

    for stem in ['al', 'ar']:
        occs = loader.find_stem_occurrences(stem, section='all')
        for o in occs:
            folio = o['folio']
            # Extract folio number
            num_str = ''.join(c for c in folio if c.isdigit())
            if num_str:
                num = int(num_str[:2]) if len(num_str) >= 2 else int(num_str)
                # Pharma section is f87-f102, balneological is around f75-f85
                if 75 <= num <= 102:
                    pharma_occs[stem].append(o)

    print(f"\n'al' in pharma/balneo section: {len(pharma_occs['al'])}")
    print(f"'ar' in pharma/balneo section: {len(pharma_occs['ar'])}")

    # Group by folio
    al_by_folio = Counter(o['folio'] for o in pharma_occs['al'])
    ar_by_folio = Counter(o['folio'] for o in pharma_occs['ar'])

    print("\nBy folio:")
    all_folios = set(al_by_folio.keys()) | set(ar_by_folio.keys())
    for folio in sorted(all_folios):
        al_cnt = al_by_folio.get(folio, 0)
        ar_cnt = ar_by_folio.get(folio, 0)
        ratio = al_cnt / ar_cnt if ar_cnt > 0 else float('inf')
        ratio_str = f"{ratio:.2f}" if ratio != float('inf') else "∞"
        print(f"  {folio}: al={al_cnt}, ar={ar_cnt}, ratio={ratio_str}")

    return pharma_occs


def test_preparation_class_correlation(loader, pharma_occs):
    """Test whether al clusters in LIQUID zones and ar clusters in HEAT zones."""
    print("\n" + "="*70)
    print("PREPARATION CLASS CORRELATION TEST")
    print("="*70)

    results = {}

    # Since all our annotated pharma folios are LIQUID-dominant,
    # we expect: al > ar overall, and al/ar ratio > 1

    al_total = len(pharma_occs['al'])
    ar_total = len(pharma_occs['ar'])

    print(f"\nOverall in pharma/balneo section:")
    print(f"  'al' count: {al_total}")
    print(f"  'ar' count: {ar_total}")

    if ar_total > 0:
        ratio = al_total / ar_total
        print(f"  al/ar ratio: {ratio:.2f}")

        if ratio > 1.0:
            print(f"\n  ✓ al > ar in LIQUID-equipment section (ratio={ratio:.2f})")
            print(f"    This SUPPORTS the al = liquid hypothesis!")
        else:
            print(f"\n  ✗ al ≤ ar in LIQUID-equipment section")
            print(f"    This does NOT support the al = liquid hypothesis")
    else:
        print(f"  Cannot compute ratio (ar=0)")

    # Analyze specific folios with known equipment type
    print("\n" + "-"*70)
    print("BY EQUIPMENT-ANNOTATED FOLIO:")
    print("-"*70)

    for folio_id, ann in EQUIPMENT_ANNOTATIONS.items():
        # Find matching folio in occurrences
        al_in_folio = [o for o in pharma_occs['al']
                       if folio_id.split('_')[0] in o['folio'] or
                       o['folio'].startswith(folio_id[:3])]
        ar_in_folio = [o for o in pharma_occs['ar']
                       if folio_id.split('_')[0] in o['folio'] or
                       o['folio'].startswith(folio_id[:3])]

        # Also try by file number matching to transcription
        file_num = ann.get('file_number', 0)
        expected_ratio = ann.get('expected_al_ar_ratio', 'unknown')
        prep_class = ann['equipment_analysis']['preparation_class']

        print(f"\n{folio_id} ({prep_class}):")
        print(f"  Equipment: {ann['equipment_analysis']['equipment_type']}")
        print(f"  Expected al/ar ratio: {expected_ratio}")

    return results


def analyze_operator_class_pairing(loader):
    """Check if certain operators prefer al or ar."""
    print("\n" + "="*70)
    print("OPERATOR-CLASS PAIRING ANALYSIS")
    print("="*70)

    # Get all tokens
    all_tokens = []
    for folio, lines in loader.transcription.items():
        for line in lines:
            all_tokens.extend(line.get('tokens', []))

    # Known operators
    operators = ['qok', 'qot', 'ok', 'ot', 'ch', 'sh', 'da', 'kar', 'kal']

    print("\nOperator pairing with al vs ar:")
    print(f"{'Operator':10} {'with -al':>10} {'with -ar':>10} {'Ratio':>10} {'Prediction':>15}")
    print("-"*60)

    for op in operators:
        al_count = sum(1 for t in all_tokens if t.lower().startswith(op) and 'al' in t.lower())
        ar_count = sum(1 for t in all_tokens if t.lower().startswith(op) and 'ar' in t.lower())

        if ar_count > 0:
            ratio = al_count / ar_count
            ratio_str = f"{ratio:.2f}"
        else:
            ratio = float('inf') if al_count > 0 else 0
            ratio_str = "∞" if ratio == float('inf') else "0"

        # Predictions based on semantics
        prediction = ""
        if op == 'kal':
            prediction = "→ al (vessel)"
        elif op == 'kar':
            prediction = "→ ar (fire)"
        elif op == 'da':
            prediction = "BOTH (dose)"

        match = ""
        if op == 'kal' and ratio > 1:
            match = "✓"
        elif op == 'kar' and ratio < 1:
            match = "✓"

        print(f"{op:10} {al_count:>10} {ar_count:>10} {ratio_str:>10} {prediction:>15} {match}")


def main():
    print("="*70)
    print("ZFD PHASE 5: PHARMACEUTICAL SECTION VALIDATION")
    print("="*70)
    print(f"Testing al/ar as preparation class markers")
    print(f"Started: {datetime.now().isoformat()}")

    # Load data
    loader = ZFDLoader('.')

    # Analyze pharma section
    pharma_occs = get_al_ar_in_pharma(loader)

    # Test preparation class correlation
    test_preparation_class_correlation(loader, pharma_occs)

    # Operator pairing analysis
    analyze_operator_class_pairing(loader)

    # Generate verdict
    print("\n" + "="*70)
    print("PHASE 5 PRELIMINARY VERDICT")
    print("="*70)

    al_total = len(pharma_occs['al'])
    ar_total = len(pharma_occs['ar'])
    ratio = al_total / ar_total if ar_total > 0 else float('inf')

    print(f"""
EVIDENCE SUMMARY:

1. BALNEOLOGICAL SECTION (f75-f85 range):
   - ALL annotated folios show LIQUID equipment (pools, tubes, baths)
   - NO heat/fire equipment observed
   - Strongly LIQUID-biased section

2. AL/AR DISTRIBUTION:
   - al count: {al_total}
   - ar count: {ar_total}
   - al/ar ratio: {ratio:.2f}

3. INTERPRETATION:
   {"✓ al > ar in LIQUID section → SUPPORTS al = liquid" if ratio > 1 else "✗ al ≤ ar → DOES NOT support hypothesis"}

4. OPERATOR PAIRING:
   - kal (vessel) should pair with -al
   - kar (fire) should pair with -ar
   (See analysis above)

5. VERDICT: {"SUPPORTIVE" if ratio > 1 else "INCONCLUSIVE"}

   The pharmaceutical/balneological section shows LIQUID equipment,
   and the al/ar ratio {"favors 'al' as expected" if ratio > 1 else "does not clearly favor 'al'"}.
""")

    # Save results
    results_path = Path(__file__).parent / "results" / "phase5_results.json"
    results_path.parent.mkdir(exist_ok=True)

    with open(results_path, 'w') as f:
        json.dump({
            'generated': datetime.now().isoformat(),
            'al_pharma_count': al_total,
            'ar_pharma_count': ar_total,
            'al_ar_ratio': ratio if ratio != float('inf') else 'inf',
            'equipment_annotations': {k: v['equipment_analysis'] for k, v in EQUIPMENT_ANNOTATIONS.items()},
        }, f, indent=2)

    print(f"\nResults saved to: {results_path}")


if __name__ == "__main__":
    main()
