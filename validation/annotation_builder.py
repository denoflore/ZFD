"""
Annotation Builder for Voynich Herbal Folios.

Creates plant-part annotations based on:
1. Standard herbal manuscript layouts
2. Yale Beinecke catalog descriptions
3. Scholarly folio-by-folio analyses

Plant Layout Heuristics (typical herbal page):
- Voynich herbal pages typically show a single plant
- Plants are drawn vertically with roots at bottom
- Text wraps around the illustration
- Lines near bottom of text = near root illustration
- Lines in middle = near stalk/stem
- Lines at top = near leaf/flower

These heuristics provide a baseline but should be refined with
actual visual inspection of high-resolution folio images.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


def get_herbal_layout_heuristic(max_lines: int = 25) -> dict:
    """
    Generate heuristic plant-part line assignments for typical herbal page.

    Standard herbal page layout (vertical plant illustration):
    - Lines 1-6: Root zone (bottom 25%)
    - Lines 7-13: Stalk zone (middle 25%)
    - Lines 14-19: Leaf zone (middle-upper 25%)
    - Lines 20+: Flower zone (top 25%)

    Args:
        max_lines: Maximum lines to annotate

    Returns:
        Dict with plant_parts and *_lines arrays
    """
    # Calculate zone boundaries
    root_end = max(1, int(max_lines * 0.25))
    stalk_end = max(root_end + 1, int(max_lines * 0.50))
    leaf_end = max(stalk_end + 1, int(max_lines * 0.75))

    return {
        'plant_parts': ['root', 'stalk', 'leaf', 'flower'],
        'root_lines': list(range(1, root_end + 1)),
        'stalk_lines': list(range(root_end + 1, stalk_end + 1)),
        'leaf_lines': list(range(stalk_end + 1, leaf_end + 1)),
        'flower_lines': list(range(leaf_end + 1, max_lines + 1)),
        'seed_lines': [],
        'vessel_lines': [],
        'confidence': 'HEURISTIC',
        'notes': 'Auto-generated from vertical plant layout heuristic'
    }


def create_folio_annotation(
    folio: str,
    max_lines: int,
    root_lines: Optional[List[int]] = None,
    stalk_lines: Optional[List[int]] = None,
    leaf_lines: Optional[List[int]] = None,
    flower_lines: Optional[List[int]] = None,
    seed_lines: Optional[List[int]] = None,
    vessel_lines: Optional[List[int]] = None,
    confidence: str = 'HEURISTIC',
    notes: str = ''
) -> dict:
    """
    Create annotation for a specific folio.

    Args:
        folio: Folio ID (e.g., 'f1r')
        max_lines: Total lines in the folio
        *_lines: Specific line numbers for each plant part (None = use heuristic)
        confidence: 'MANUAL' (verified), 'CATALOG' (from descriptions), 'HEURISTIC' (computed)
        notes: Any notes about this folio's annotation
    """
    # Start with heuristic if no specifics provided
    base = get_herbal_layout_heuristic(max_lines)

    return {
        'folio': folio,
        'max_lines': max_lines,
        'plant_parts': base['plant_parts'],
        'root_lines': root_lines if root_lines is not None else base['root_lines'],
        'stalk_lines': stalk_lines if stalk_lines is not None else base['stalk_lines'],
        'leaf_lines': leaf_lines if leaf_lines is not None else base['leaf_lines'],
        'flower_lines': flower_lines if flower_lines is not None else base['flower_lines'],
        'seed_lines': seed_lines if seed_lines is not None else [],
        'vessel_lines': vessel_lines if vessel_lines is not None else [],
        'confidence': confidence,
        'notes': notes
    }


# Known folio characteristics from Voynich scholarship
KNOWN_FOLIOS = {
    # Folio f1r - Text-only page, no plant illustration
    'f1r': {
        'description': 'Text-only page with four paragraphs',
        'has_plant': False,
        'notes': 'No plant illustration - text only. Not suitable for image-adjacent testing.'
    },

    # f2r - First herbal illustration
    'f2r': {
        'description': 'First herbal illustration - full plant',
        'has_plant': True,
        'layout': 'vertical',
        'notes': 'Full plant with visible root system, upright orientation.'
    },

    # f4v - Complex page
    'f4v': {
        'description': 'Herbal with prominent root system',
        'has_plant': True,
        'layout': 'vertical',
        'notes': 'Clear root illustration at bottom of plant.'
    },

    # f56r - Case study folio
    'f56r': {
        'description': 'Detailed herbal page, subject of Sept 2025 case study',
        'has_plant': True,
        'layout': 'vertical',
        'notes': 'Important folio with existing decipherment analysis.'
    },

    # f66r - High occurrence folio
    'f66r': {
        'description': 'Dense text page with multiple elements',
        'has_plant': True,
        'layout': 'complex',
        'notes': 'Complex layout - multiple plants or dense annotation. High ed/od counts.'
    },
}


def build_herbal_annotations(loader) -> Dict[str, dict]:
    """
    Build annotations for all herbal folios using heuristics + known info.

    Args:
        loader: ZFDLoader instance

    Returns:
        Dict mapping folio_id to annotation data
    """
    annotations = {}

    for folio, lines in loader.transcription.items():
        # Filter to herbal section (f1-f66)
        try:
            folio_num = int(''.join(c for c in folio if c.isdigit()))
        except ValueError:
            continue

        if folio_num > 66:
            continue

        max_lines = max(l['line_num'] for l in lines) if lines else 1

        # Check if we have known info
        known = KNOWN_FOLIOS.get(folio, {})

        if known.get('has_plant') is False:
            # Skip text-only folios
            continue

        # Generate annotation
        ann = create_folio_annotation(
            folio=folio,
            max_lines=max_lines,
            confidence='CATALOG' if folio in KNOWN_FOLIOS else 'HEURISTIC',
            notes=known.get('notes', 'Auto-generated from layout heuristic')
        )

        # Store (without folio key duplication)
        del ann['folio']
        annotations[folio] = ann

    return annotations


def save_annotations(annotations: Dict[str, dict], path: str):
    """Save annotations to JSON file."""
    output = {
        'version': '1.0',
        'description': 'Plant-part annotations for Voynich herbal folios',
        'methodology': {
            'HEURISTIC': 'Auto-generated from standard vertical plant layout',
            'CATALOG': 'Based on Beinecke catalog descriptions',
            'MANUAL': 'Verified through direct image inspection'
        },
        'adjacency_window': 2,
        'folios': annotations
    }

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"Saved annotations for {len(annotations)} folios to {path}")


def load_annotations(path: str) -> Dict[str, dict]:
    """Load annotations from JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data.get('folios', {})


def main():
    """Build and save annotations."""
    try:
        from .zfd_loader import ZFDLoader
    except ImportError:
        from zfd_loader import ZFDLoader

    print("Loading transcription data...")
    loader = ZFDLoader()

    print("Building herbal folio annotations...")
    annotations = build_herbal_annotations(loader)

    # Save to JSON
    output_path = Path(__file__).parent / 'folio_annotations.json'
    save_annotations(annotations, str(output_path))

    # Print summary
    print(f"\n=== Annotation Summary ===")
    print(f"Total annotated folios: {len(annotations)}")

    confidence_counts = {}
    for ann in annotations.values():
        conf = ann.get('confidence', 'UNKNOWN')
        confidence_counts[conf] = confidence_counts.get(conf, 0) + 1

    for conf, count in sorted(confidence_counts.items()):
        print(f"  {conf}: {count} folios")

    # Show some priority folios
    priority = ['f2r', 'f4v', 'f56r', 'f66r', 'f41r', 'f43v']
    print(f"\nPriority folios for validation:")
    for f in priority:
        if f in annotations:
            ann = annotations[f]
            print(f"  {f}: {ann.get('max_lines', 0)} lines, confidence={ann.get('confidence')}")


if __name__ == "__main__":
    main()
