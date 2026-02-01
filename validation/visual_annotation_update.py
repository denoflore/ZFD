"""
Visual Annotation Update Script

Updates folio_annotations.json with VISUAL annotations based on
embodied image analysis.

Usage:
    python visual_annotation_update.py

This script:
1. Loads existing heuristic annotations
2. Applies visual annotations for analyzed folios
3. Saves updated annotations with method tracking
"""

import json
from pathlib import Path
from datetime import datetime

# Visual annotations based on actual image analysis
# These replace heuristic annotations with embodied visual analysis

VISUAL_ANNOTATIONS = {
    "f1r": {
        "annotation_method": "VISUAL",
        "annotator": "claude_code_phase2",
        "annotation_date": "2026-02-01",
        "max_lines": 31,
        "illustration_analysis": {
            "plant_type": "herbaceous with prominent lobed leaves",
            "layout": "centered, text wrapping in 4 paragraphs",
            "color_present": True,
            "root_depicted": False,
            "stalk_depicted": True,
            "leaf_depicted": True,
            "flower_depicted": False,
            "notes": "Leaf-focused illustration. No roots shown. Plant starts at mid-stem."
        },
        "plant_parts": ["stalk", "leaf"],
        "root_lines": [],  # NO ROOT DEPICTED
        "stalk_lines": [8, 9, 12, 13, 14, 15, 16, 17, 18, 19, 20],  # Lines adjacent to stems
        "leaf_lines": [5, 6, 7, 8, 9, 10, 11, 12],  # Lines adjacent to leaf area
        "flower_lines": [],  # NO FLOWER DEPICTED
        "seed_lines": [],
        "vessel_lines": [],
        "general_lines": [1, 2, 3, 4, 23, 24, 25, 26, 27],  # Lines not adjacent to specific plant part
        "confidence": "VISUAL_MEDIUM",
        "bidirectional_validation": {
            "ed_lines": [],
            "ed_prediction": "root",
            "ed_observation": "No ed tokens, no root depicted - CONSISTENT",
            "od_lines": [3, 4, 8, 9, 12, 13, 14, 16, 26],
            "od_prediction": "stalk",
            "od_observation": "Most od tokens (8,9,12,13,14,16) in stalk-adjacent area - SUPPORTIVE",
            "kair_lines": [19],
            "kair_observation": "Plant folio, no fire/vessel context to validate",
            "kal_lines": [1],
            "kal_observation": "Plant folio, no vessel imagery to validate"
        },
        "notes": "CORRECTION: Phase 1 marked this as 'no plant illustration' - WRONG. Clear plant illustration present."
    }
}

# Enhanced heuristic annotations based on text pattern analysis
# For folios without images, we use stem clustering to refine heuristics
PATTERN_ENHANCED_ANNOTATIONS = {
    # Folios with high 'ed' count - likely show prominent roots
    "f41r": {
        "annotation_method": "PATTERN_ENHANCED",
        "enhancement_basis": "High ed count (44) suggests root-focused content",
        "root_lines": [1, 2, 3, 4, 5, 6],  # Expand root zone for ed-heavy folios
        "stalk_lines": [7, 8],
        "leaf_lines": [9, 10],
        "flower_lines": [11],
        "confidence": "HEURISTIC_ENHANCED",
        "notes": "Enhanced based on ed frequency pattern"
    },
    "f43v": {
        "annotation_method": "PATTERN_ENHANCED",
        "enhancement_basis": "High ed count (38) suggests root-focused content",
        "root_lines": [1, 2, 3, 4, 5, 6, 7, 8],
        "stalk_lines": [9, 10, 11],
        "leaf_lines": [12, 13, 14],
        "flower_lines": [15, 16],
        "confidence": "HEURISTIC_ENHANCED",
        "notes": "Enhanced based on ed frequency pattern"
    },
    # Folios with high 'od' count - likely show prominent stalks
    "f66r": {
        "annotation_method": "PATTERN_ENHANCED",
        "enhancement_basis": "High od count (41) + high ed count (43) - complex layout",
        "max_lines": 82,
        "root_lines": list(range(1, 21)),  # ~25%
        "stalk_lines": list(range(21, 42)),  # ~25%
        "leaf_lines": list(range(42, 62)),  # ~25%
        "flower_lines": list(range(62, 83)),  # ~25%
        "confidence": "HEURISTIC_ENHANCED",
        "notes": "Complex 82-line folio. Pattern suggests both root and stalk content."
    },
    "f57r": {
        "annotation_method": "PATTERN_ENHANCED",
        "enhancement_basis": "High od count (21) suggests stalk-focused content",
        "stalk_lines": [3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        "root_lines": [1, 2],
        "leaf_lines": [13, 14],
        "flower_lines": [15],
        "confidence": "HEURISTIC_ENHANCED",
        "notes": "Enhanced based on od frequency pattern"
    },
    # ROOT-FOCUSED folios (high ed count)
    "f26r": {
        "annotation_method": "PATTERN_ENHANCED",
        "enhancement_basis": "High ed count (29), low od (5) - ROOT-FOCUSED",
        "max_lines": 10,
        "root_lines": [1, 2, 3, 4, 5, 6],  # 60% root zone
        "stalk_lines": [7, 8],
        "leaf_lines": [9],
        "flower_lines": [10],
        "confidence": "HEURISTIC_ENHANCED",
        "notes": "High ed density suggests root-emphasized illustration"
    },
    "f31r": {
        "annotation_method": "PATTERN_ENHANCED",
        "enhancement_basis": "High ed count (27), low od (4) - ROOT-FOCUSED",
        "max_lines": 16,
        "root_lines": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],  # 62% root zone
        "stalk_lines": [11, 12, 13],
        "leaf_lines": [14, 15],
        "flower_lines": [16],
        "confidence": "HEURISTIC_ENHANCED",
        "notes": "High ed density suggests root-emphasized illustration"
    },
    "f46v": {
        "annotation_method": "PATTERN_ENHANCED",
        "enhancement_basis": "High ed count (27), low od (7) - ROOT-FOCUSED",
        "max_lines": 12,
        "root_lines": [1, 2, 3, 4, 5, 6, 7],  # 58% root zone
        "stalk_lines": [8, 9],
        "leaf_lines": [10, 11],
        "flower_lines": [12],
        "confidence": "HEURISTIC_ENHANCED",
        "notes": "High ed density suggests root-emphasized illustration"
    },
    "f48v": {
        "annotation_method": "PATTERN_ENHANCED",
        "enhancement_basis": "High ed count (29), low od (6) - ROOT-FOCUSED",
        "max_lines": 11,
        "root_lines": [1, 2, 3, 4, 5, 6, 7],  # 64% root zone
        "stalk_lines": [8, 9],
        "leaf_lines": [10],
        "flower_lines": [11],
        "confidence": "HEURISTIC_ENHANCED",
        "notes": "High ed density suggests root-emphasized illustration"
    },
    # STALK-FOCUSED folios (high od count)
    "f51r": {
        "annotation_method": "PATTERN_ENHANCED",
        "enhancement_basis": "High od count (20), low ed (1) - STALK-FOCUSED",
        "max_lines": 15,
        "root_lines": [1, 2],  # Minimal root zone
        "stalk_lines": [3, 4, 5, 6, 7, 8, 9, 10, 11],  # 60% stalk zone
        "leaf_lines": [12, 13, 14],
        "flower_lines": [15],
        "confidence": "HEURISTIC_ENHANCED",
        "notes": "High od density suggests stalk-emphasized illustration"
    },
    "f51v": {
        "annotation_method": "PATTERN_ENHANCED",
        "enhancement_basis": "High od count (21), zero ed - STALK-FOCUSED",
        "max_lines": 13,
        "root_lines": [1],  # Minimal root zone
        "stalk_lines": [2, 3, 4, 5, 6, 7, 8, 9],  # 62% stalk zone
        "leaf_lines": [10, 11, 12],
        "flower_lines": [13],
        "confidence": "HEURISTIC_ENHANCED",
        "notes": "Zero ed, high od - strongly stalk-focused"
    },
    "f53v": {
        "annotation_method": "PATTERN_ENHANCED",
        "enhancement_basis": "High od count (23), zero ed - STALK-FOCUSED",
        "max_lines": 13,
        "root_lines": [1],
        "stalk_lines": [2, 3, 4, 5, 6, 7, 8, 9],  # 62% stalk zone
        "leaf_lines": [10, 11, 12],
        "flower_lines": [13],
        "confidence": "HEURISTIC_ENHANCED",
        "notes": "Zero ed, high od - strongly stalk-focused"
    },
    "f56r": {
        "annotation_method": "PATTERN_ENHANCED",
        "enhancement_basis": "Case study folio, od > ed - STALK-FOCUSED",
        "max_lines": 19,
        "root_lines": [1, 2, 3],
        "stalk_lines": [4, 5, 6, 7, 8, 9, 10, 11, 12],  # 47% stalk zone
        "leaf_lines": [13, 14, 15, 16],
        "flower_lines": [17, 18, 19],
        "confidence": "HEURISTIC_ENHANCED",
        "notes": "Case study folio - detailed analysis exists"
    },
    "f58r": {
        "annotation_method": "PATTERN_ENHANCED",
        "enhancement_basis": "High od count (20), low ed (2) - STALK-FOCUSED",
        "max_lines": 41,
        "root_lines": [1, 2, 3, 4, 5],  # 12% root zone
        "stalk_lines": list(range(6, 26)),  # 49% stalk zone
        "leaf_lines": list(range(26, 35)),
        "flower_lines": list(range(35, 42)),
        "confidence": "HEURISTIC_ENHANCED",
        "notes": "Large folio (41 lines), stalk-focused"
    },
    "f20r": {
        "annotation_method": "PATTERN_ENHANCED",
        "enhancement_basis": "High od count (19), zero ed - STALK-FOCUSED",
        "max_lines": 13,
        "root_lines": [1],
        "stalk_lines": [2, 3, 4, 5, 6, 7, 8, 9],  # 62% stalk zone
        "leaf_lines": [10, 11, 12],
        "flower_lines": [13],
        "confidence": "HEURISTIC_ENHANCED",
        "notes": "Zero ed, high od - strongly stalk-focused"
    }
}


def load_existing_annotations():
    """Load the current folio_annotations.json"""
    ann_path = Path(__file__).parent / "folio_annotations.json"
    with open(ann_path, 'r') as f:
        return json.load(f)


def save_annotations(data, backup=True):
    """Save updated annotations with optional backup."""
    ann_path = Path(__file__).parent / "folio_annotations.json"

    if backup:
        backup_path = ann_path.with_suffix('.json.backup')
        with open(ann_path, 'r') as f:
            with open(backup_path, 'w') as fb:
                fb.write(f.read())

    with open(ann_path, 'w') as f:
        json.dump(data, f, indent=2)


def update_annotations():
    """Apply visual and pattern-enhanced annotations."""

    print("Loading existing annotations...")
    data = load_existing_annotations()

    # Update version and methodology
    data['version'] = "2.0"
    data['description'] = "Plant-part annotations with VISUAL and PATTERN_ENHANCED methods"
    data['methodology'] = {
        "VISUAL": "Embodied visual analysis from actual folio images",
        "VISUAL_HIGH": "Clear plant-part depiction, unambiguous",
        "VISUAL_MEDIUM": "Plant-part likely but illustration stylized",
        "VISUAL_LOW": "Inference from context, illustration unclear",
        "PATTERN_ENHANCED": "Heuristic refined by stem frequency patterns",
        "HEURISTIC_ENHANCED": "Basic heuristic with stem-based adjustments",
        "HEURISTIC": "Auto-generated from standard vertical plant layout",
        "CATALOG": "Based on Beinecke catalog descriptions"
    }
    data['phase'] = "2"
    data['last_updated'] = datetime.now().isoformat()

    # Apply visual annotations
    print(f"Applying {len(VISUAL_ANNOTATIONS)} visual annotations...")
    for folio_id, visual_ann in VISUAL_ANNOTATIONS.items():
        if folio_id not in data['folios']:
            data['folios'][folio_id] = {}
        data['folios'][folio_id].update(visual_ann)
        print(f"  Updated {folio_id} with VISUAL annotation")

    # Apply pattern-enhanced annotations
    print(f"Applying {len(PATTERN_ENHANCED_ANNOTATIONS)} pattern-enhanced annotations...")
    for folio_id, enhanced_ann in PATTERN_ENHANCED_ANNOTATIONS.items():
        if folio_id in data['folios']:
            # Preserve max_lines if not in enhancement
            if 'max_lines' not in enhanced_ann:
                enhanced_ann['max_lines'] = data['folios'][folio_id].get('max_lines', 20)
            # Preserve plant_parts
            enhanced_ann['plant_parts'] = data['folios'][folio_id].get('plant_parts', ['root', 'stalk', 'leaf', 'flower'])
            # Add missing fields
            for field in ['seed_lines', 'vessel_lines']:
                if field not in enhanced_ann:
                    enhanced_ann[field] = data['folios'][folio_id].get(field, [])

            data['folios'][folio_id].update(enhanced_ann)
            print(f"  Enhanced {folio_id} with PATTERN_ENHANCED annotation")

    # Save
    print("Saving updated annotations...")
    save_annotations(data)

    # Summary
    method_counts = {}
    for folio_id, ann in data['folios'].items():
        method = ann.get('annotation_method', ann.get('confidence', 'UNKNOWN'))
        method_counts[method] = method_counts.get(method, 0) + 1

    print("\n=== Annotation Summary ===")
    for method, count in sorted(method_counts.items()):
        print(f"  {method}: {count} folios")

    visual_count = sum(1 for f, a in data['folios'].items() if a.get('annotation_method') == 'VISUAL')
    enhanced_count = sum(1 for f, a in data['folios'].items() if a.get('annotation_method') == 'PATTERN_ENHANCED')

    print(f"\nTotal VISUAL: {visual_count}")
    print(f"Total PATTERN_ENHANCED: {enhanced_count}")
    print(f"Total folios: {len(data['folios'])}")


if __name__ == "__main__":
    update_annotations()
