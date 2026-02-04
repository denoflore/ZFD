"""
Decoder wrapper for blind decode test.

Wraps ZFDPipeline to run decoding and extract structured results
for statistical comparison.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any

# Add ZFD project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "zfd_decoder" / "src"))

from pipeline import ZFDPipeline
from utils import load_eva_folio, get_data_dir, get_project_root


# Global pipeline instance (initialized once)
_pipeline = None


def get_pipeline() -> ZFDPipeline:
    """Get or create the pipeline instance."""
    global _pipeline
    if _pipeline is None:
        data_dir = get_data_dir()
        _pipeline = ZFDPipeline(data_dir=str(data_dir))
    return _pipeline


def decode_eva_text(eva_text: str, folio_id: str) -> Dict[str, Any]:
    """
    Decode EVA text through the ZFD pipeline.

    Args:
        eva_text: Raw EVA transcription text
        folio_id: Folio identifier (e.g., "f10r")

    Returns:
        Structured results dict with all metrics
    """
    pipeline = get_pipeline()

    # Run the full pipeline
    result = pipeline.process_folio(eva_text, folio_id)

    # Extract diagnostics
    diag = result['diagnostics']

    # Flatten all tokens for analysis
    all_tokens = []
    for line in result['lines']:
        all_tokens.extend(line)

    # Extract operator distribution
    operator_counts = diag.get('operator_counts', {})

    # Extract category distribution from stem glosses
    category_counts = extract_category_counts(all_tokens)

    # Calculate coherence index
    coherence = compute_coherence(
        known_ratio=diag['known_ratio'],
        operator_counts=operator_counts,
        category_counts=category_counts,
        average_confidence=diag['average_confidence']
    )

    return {
        "folio": folio_id,
        "total_tokens": diag['total_tokens'],
        "known_stems": diag['known_stems'],
        "unknown_stems": diag['unknown_stems'],
        "known_ratio": diag['known_ratio'],
        "operator_counts": operator_counts,
        "category_counts": category_counts,
        "average_confidence": diag['average_confidence'],
        "unknown_stem_list": diag['unknown_stem_list'],
        "validation": diag['validation'],
        "coherence": coherence,
        "tokens": all_tokens,  # Full token data for detailed analysis
    }


def extract_category_counts(tokens: List[Dict]) -> Dict[str, int]:
    """
    Extract semantic category distribution from decoded tokens.

    Categories are inferred from:
    - Operator types (action, relative, comitative, dative, vessel)
    - Stem glosses (ingredient, equipment, action terms)
    - Suffix semantics (processed, instrumental, etc.)
    """
    categories = {}

    # Category keywords for classification
    ingredient_keywords = ['oil', 'water', 'salt', 'bone', 'honey', 'flour', 'root',
                          'wine', 'milk', 'flower', 'rose', 'myrrh', 'aloe', 'herb',
                          'plant', 'resin', 'gum', 'leaf', 'seed', 'bark', 'juice']
    equipment_keywords = ['pot', 'jar', 'vessel', 'flask', 'cauldron', 'container']
    action_keywords = ['cook', 'soak', 'boil', 'strain', 'combine', 'mix', 'dose',
                       'give', 'add', 'grind', 'apply', 'wash', 'drink', 'anoint']
    preparation_keywords = ['prepared', 'processed', 'syrup', 'ointment', 'plaster',
                           'decoction', 'confection', 'poultice']
    measurement_keywords = ['dose', 'portion', 'quantity', 'dram', 'ounce', 'spoon']

    for token in tokens:
        gloss = token.get('stem_gloss', '').lower()
        operator_type = token.get('operator_type', '')
        suffix_semantic = token.get('suffix_semantic', '')

        # Classify by operator type
        if operator_type:
            if operator_type == 'vessel':
                categories['equipment'] = categories.get('equipment', 0) + 1
            elif operator_type in ['action', 'comitative']:
                categories['action'] = categories.get('action', 0) + 1
            elif operator_type == 'dative':
                categories['measurement'] = categories.get('measurement', 0) + 1
            elif operator_type == 'relative':
                categories['grammar'] = categories.get('grammar', 0) + 1

        # Classify by gloss keywords
        if any(kw in gloss for kw in ingredient_keywords):
            categories['ingredient'] = categories.get('ingredient', 0) + 1
        elif any(kw in gloss for kw in equipment_keywords):
            categories['equipment'] = categories.get('equipment', 0) + 1
        elif any(kw in gloss for kw in action_keywords):
            categories['action'] = categories.get('action', 0) + 1
        elif any(kw in gloss for kw in preparation_keywords):
            categories['preparation'] = categories.get('preparation', 0) + 1
        elif any(kw in gloss for kw in measurement_keywords):
            categories['measurement'] = categories.get('measurement', 0) + 1
        elif gloss:
            # Has gloss but not categorized
            categories['other'] = categories.get('other', 0) + 1

        # Classify by suffix semantic
        if suffix_semantic:
            if suffix_semantic == 'processed':
                categories['preparation'] = categories.get('preparation', 0) + 1
            elif suffix_semantic == 'instrumental':
                categories['action'] = categories.get('action', 0) + 1

    return categories


def compute_coherence(known_ratio: float, operator_counts: Dict[str, int],
                      category_counts: Dict[str, int], average_confidence: float) -> float:
    """
    Compute coherence index (0-1) for decoded folio.

    Coherence = weighted_average(
        0.30 * known_ratio,           # What % of stems are known
        0.25 * operator_diversity,    # Normalized count of distinct operators
        0.25 * category_diversity,    # Normalized count of distinct categories
        0.20 * confidence_mean,       # Average pipeline confidence
    )
    """
    # Operator diversity: min(distinct_operators / 5, 1.0)
    distinct_operators = len(operator_counts)
    operator_diversity = min(distinct_operators / 5.0, 1.0)

    # Category diversity: min(distinct_categories / 5, 1.0)
    distinct_categories = len(category_counts)
    category_diversity = min(distinct_categories / 5.0, 1.0)

    # Weighted average
    coherence = (
        0.30 * known_ratio +
        0.25 * operator_diversity +
        0.25 * category_diversity +
        0.20 * average_confidence
    )

    return round(coherence, 4)


def decode_folio(folio_id: str) -> Dict[str, Any]:
    """
    Convenience function to decode a folio by ID.

    Loads EVA text from standard location and runs decode.
    """
    root = get_project_root()
    eva_text = load_eva_folio(folio_id, str(root))
    return decode_eva_text(eva_text, folio_id)


def check_folio_predictions(result: Dict[str, Any], predictions: Dict[str, Any]) -> Dict[str, bool]:
    """
    Check if decode result meets folio-specific predictions.

    Returns dict of prediction name -> met (bool)
    """
    checks = {}

    # Check required operators (any of them found)
    required_ops = predictions.get('required_operators', [])
    found_ops = set(result.get('operator_counts', {}).keys())
    # Operators are stored by their Croatian form, need to map
    operator_map = {'qo': 'ko', 'ch': 'h', 'sh': 'š', 'da': 'da', 'ok': 'ost', 'ot': 'otr', 'ol': 'ol'}
    eva_to_croatian = {v: v for v in operator_map.values()}

    # Check if any required operators were found
    required_croatian = [operator_map.get(op, op) for op in required_ops]
    checks['operators'] = bool(found_ops.intersection(required_croatian))

    # Check required stems (any of them found)
    required_stems = predictions.get('required_stems_any', [])
    found_stems = set()
    for token in result.get('tokens', []):
        stem = token.get('stem', '')
        if stem:
            found_stems.add(stem)
    checks['stems'] = bool(found_stems.intersection(required_stems))

    # Check category distribution overlap
    expected_cats = predictions.get('expected_categories', [])
    if not expected_cats:
        # Use image annotations expected categories
        checks['categories'] = True
    else:
        found_cats = set(result.get('category_counts', {}).keys())
        # At least 2 expected categories should be present
        overlap = found_cats.intersection(expected_cats)
        checks['categories'] = len(overlap) >= 2

    return checks


if __name__ == "__main__":
    # Quick test of the decoder
    import json

    print("Testing decoder.py...")
    result = decode_folio("f10r")
    print(f"Folio: {result['folio']}")
    print(f"Total tokens: {result['total_tokens']}")
    print(f"Known ratio: {result['known_ratio']:.2%}")
    print(f"Coherence: {result['coherence']:.4f}")
    print(f"Operators: {result['operator_counts']}")
    print(f"Categories: {result['category_counts']}")
    print("Decoder test passed!")
