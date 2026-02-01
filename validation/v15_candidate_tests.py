"""
V1.5 Semantic Candidate Batch Testing

Tests CANDIDATE entries from Herbal_Lexicon_v3_5_full.csv
using image-adjacent correlation and contextual analysis.
"""

import json
import random
from datetime import datetime
from collections import Counter, defaultdict
from typing import Dict, List, Tuple

try:
    from .zfd_loader import ZFDLoader
    from .image_adjacent import ImageAdjacentValidator
    from .annotation_builder import load_annotations
except ImportError:
    from zfd_loader import ZFDLoader
    from image_adjacent import ImageAdjacentValidator
    from annotation_builder import load_annotations


# Candidate definitions with all variants and expected contexts
V15_CANDIDATES = [
    {
        'name': 'syrup',
        'variants': ['syr', 'syrop'],
        'claimed_context': 'preparation_terminal',
        'description': 'Syrup/potion - terminal media/sweetened',
        'expected_operators': ['ch', 'sh'],  # cooking/infusion contexts
    },
    {
        'name': 'broth',
        'variants': ['ykal'],
        'claimed_context': 'vessel_infusion',
        'description': 'Broth/decoction - vessels and soaking',
        'expected_operators': ['ok', 'ot', 'sh'],
    },
    {
        'name': 'dose_seed',
        'variants': ['dar', 'dain', 'daiin'],
        'claimed_context': 'dose_quantity',
        'description': 'Add/Portion/Measure/Seed - dose contexts',
        'expected_operators': ['da', 'qo'],
    },
    {
        'name': 'boil_roast',
        'variants': ['thor', 'thar'],
        'claimed_context': 'heat_process',
        'description': 'Boil/roast/scorch - heat contexts',
        'expected_operators': ['ch'],
    },
    {
        'name': 'fire_heat',
        'variants': ['kair', 'fair', 'kar', 'char'],
        'claimed_context': 'heat_source',
        'description': 'Fire/heat - cooking contexts',
        'expected_operators': ['ch', 'ok', 'ot'],
    },
    {
        'name': 'flask_phial',
        'variants': ['phar'],
        'claimed_context': 'vessel_liquid',
        'description': 'Flask/phial - liquid contexts',
        'expected_operators': ['ok', 'ot', 'qo'],
    },
    {
        'name': 'bitter_herb',
        'variants': ['amar'],
        'claimed_context': 'wine_bitter',
        'description': 'Bitter herb/resin - wines/bitters',
        'expected_operators': ['ch', 'sh'],
    },
    {
        'name': 'cauldron',
        'variants': ['kal'],
        'claimed_context': 'heated_vessel',
        'description': 'Cauldron/heated vessel',
        'expected_operators': ['ok', 'ot', 'ch'],
    },
    {
        'name': 'zedoary',
        'variants': ['zel', 'zedo', 'zedor'],
        'claimed_context': 'root_rare',
        'description': 'Zedoary root - rare root ingredient',
        'expected_operators': ['qo', 'ch', 'sh'],
    },
    {
        'name': 'lime',
        'variants': ['calc'],
        'claimed_context': 'mineral_fire',
        'description': 'Lime/quickite - minerals + fire',
        'expected_operators': ['ch'],
    },
    {
        'name': 'licorice',
        'variants': ['licor'],
        'claimed_context': 'sweet_root',
        'description': 'Licorice root - honey/sweets',
        'expected_operators': ['qo', 'ch'],
    },
    {
        'name': 'electuary',
        'variants': ['elec'],
        'claimed_context': 'compound_paste',
        'description': 'Electuary - compound paste/mixture',
        'expected_operators': ['ch', 'sh'],
    },
]


def analyze_operator_context(loader: ZFDLoader, variants: List[str],
                             expected_ops: List[str]) -> Dict:
    """
    Analyze what operators precede these stem variants.

    Checks raw tokens containing variants and looks for known operator prefixes.

    Returns:
        {
            'total_occurrences': int,
            'operator_counts': {op: count},
            'expected_op_rate': float,
            'top_operators': [(op, count, pct)],
            'context_score': float  # 0-1, higher = better match
        }
    """
    # Known 2-letter operator prefixes
    OPERATORS = ['qo', 'ch', 'sh', 'da', 'ok', 'ot', 'so', 'yc', 'sa', 'yk', 'dc', 'pc', 'po', 'tc', 'ds', 'ys']

    operator_counts = Counter()
    total = 0

    # Find all occurrences of variants in transcription
    for variant in variants:
        occurrences = loader.find_stem_occurrences(variant, section='herbal')
        for occ in occurrences:
            token = occ['token']
            total += 1

            # Check which operator prefix this token starts with
            found_op = None
            for op in OPERATORS:
                if token.startswith(op):
                    found_op = op
                    break

            if found_op:
                operator_counts[found_op] += 1
            else:
                operator_counts['(none)'] += 1

    if total == 0:
        return {
            'total_occurrences': 0,
            'operator_counts': {},
            'expected_op_rate': 0.0,
            'top_operators': [],
            'context_score': 0.0
        }

    # Calculate expected operator rate
    expected_count = sum(operator_counts.get(op, 0) for op in expected_ops)
    expected_rate = expected_count / total

    # Top operators
    top_ops = [(op, count, count/total) for op, count in operator_counts.most_common(5)]

    # Context score: ratio of expected operators to total
    context_score = expected_rate

    return {
        'total_occurrences': total,
        'operator_counts': dict(operator_counts),
        'expected_op_rate': expected_rate,
        'top_operators': top_ops,
        'context_score': context_score
    }


def test_candidate(loader: ZFDLoader, validator: ImageAdjacentValidator,
                   candidate: Dict, n_shuffles: int = 500) -> Dict:
    """
    Run full test suite on a candidate.

    Returns comprehensive results including:
    - Occurrence counts
    - Operator context analysis
    - Image-adjacent results (if applicable)
    - Overall confidence score
    """
    name = candidate['name']
    variants = candidate['variants']
    expected_ops = candidate.get('expected_operators', [])

    result = {
        'name': name,
        'variants': variants,
        'description': candidate['description'],
        'claimed_context': candidate['claimed_context'],
    }

    # Count total occurrences across all variants
    all_occurrences = []
    for variant in variants:
        occs = loader.find_stem_occurrences(variant, section='herbal')
        all_occurrences.extend(occs)

    result['total_occurrences'] = len(all_occurrences)
    result['in_herbal'] = len(all_occurrences)

    # Operator context analysis
    op_analysis = analyze_operator_context(loader, variants, expected_ops)
    result['operator_analysis'] = op_analysis

    # Image-adjacent testing for plant-part contexts
    # Test against multiple plant parts
    ia_results = {}
    for part in ['root', 'stalk', 'leaf', 'flower']:
        # Test each variant
        for variant in variants:
            if len(loader.find_stem_occurrences(variant, 'herbal')) >= 5:
                r = validator.test_mapping(variant, part, n_shuffles=n_shuffles)
                key = f'{variant}_{part}'
                ia_results[key] = {
                    'match_rate': r['match_rate'],
                    'p_value': r['p_value'],
                    'verdict': r['verdict']
                }

    result['image_adjacent_results'] = ia_results

    # Calculate overall confidence score
    # Based on: occurrences (needs ≥10), operator context, consistency
    confidence = 0.0

    if result['total_occurrences'] >= 10:
        confidence += 0.25  # Sufficient occurrences
    elif result['total_occurrences'] >= 5:
        confidence += 0.10

    if op_analysis['context_score'] >= 0.40:
        confidence += 0.35  # Strong operator context match
    elif op_analysis['context_score'] >= 0.20:
        confidence += 0.15

    # Check if any image-adjacent test passed
    any_pass = any(r['verdict'] == 'PASS' for r in ia_results.values())
    if any_pass:
        confidence += 0.40
    elif any(r['verdict'] == 'BORDERLINE' for r in ia_results.values()):
        confidence += 0.15

    result['confidence_score'] = confidence

    # Determine verdict
    if confidence >= 0.60:
        result['verdict'] = 'PROMOTE_TO_CONFIRMED'
    elif confidence >= 0.35:
        result['verdict'] = 'KEEP_AS_CANDIDATE'
    elif result['total_occurrences'] < 5:
        result['verdict'] = 'INSUFFICIENT_DATA'
    else:
        result['verdict'] = 'DEMOTE_TO_LOW'

    return result


def run_batch_tests(n_shuffles: int = 500) -> List[Dict]:
    """Run tests on all V1.5 candidates."""
    print("Loading data...")
    loader = ZFDLoader()
    annotations = load_annotations('validation/folio_annotations.json')
    validator = ImageAdjacentValidator(loader, annotations)

    results = []

    print(f"\nTesting {len(V15_CANDIDATES)} candidates...")
    print("=" * 60)

    for i, candidate in enumerate(V15_CANDIDATES, 1):
        print(f"\n[{i}/{len(V15_CANDIDATES)}] Testing {candidate['name']} ({', '.join(candidate['variants'])})")

        result = test_candidate(loader, validator, candidate, n_shuffles)
        results.append(result)

        print(f"  Occurrences: {result['total_occurrences']}")
        print(f"  Operator context score: {result['operator_analysis']['context_score']:.1%}")
        print(f"  Confidence: {result['confidence_score']:.2f}")
        print(f"  Verdict: {result['verdict']}")

    # Sort by confidence
    results.sort(key=lambda x: x['confidence_score'], reverse=True)

    return results


def generate_report(results: List[Dict]) -> str:
    """Generate markdown report from results."""
    lines = [
        "# V1.5 Semantic Candidate Batch Test Results",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Candidates Tested:** {len(results)}",
        "",
        "---",
        "",
        "## Summary",
        "",
        "| Rank | Name | Variants | Occurrences | Context Score | Confidence | Verdict |",
        "|------|------|----------|-------------|---------------|------------|---------|",
    ]

    for i, r in enumerate(results, 1):
        vars_str = ', '.join(r['variants'][:3])
        lines.append(
            f"| {i} | {r['name']} | {vars_str} | {r['total_occurrences']} | "
            f"{r['operator_analysis']['context_score']:.1%} | {r['confidence_score']:.2f} | {r['verdict']} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Verdict Distribution",
        "",
    ])

    verdict_counts = Counter(r['verdict'] for r in results)
    for verdict, count in sorted(verdict_counts.items()):
        lines.append(f"- **{verdict}:** {count}")

    lines.extend([
        "",
        "---",
        "",
        "## Top 3 Candidates for CONFIRMED Upgrade",
        "",
    ])

    top_3 = [r for r in results if r['confidence_score'] >= 0.35][:3]
    for r in top_3:
        lines.extend([
            f"### {r['name']}",
            "",
            f"**Variants:** {', '.join(r['variants'])}",
            f"**Description:** {r['description']}",
            f"**Occurrences:** {r['total_occurrences']}",
            f"**Confidence Score:** {r['confidence_score']:.2f}",
            "",
            "**Top Operators:**",
        ])

        for op, count, pct in r['operator_analysis']['top_operators'][:5]:
            lines.append(f"- {op}: {count} ({pct:.1%})")

        lines.append("")

    lines.extend([
        "---",
        "",
        "## Detailed Results",
        "",
    ])

    for r in results:
        lines.extend([
            f"### {r['name']}",
            "",
            f"- **Variants:** {', '.join(r['variants'])}",
            f"- **Description:** {r['description']}",
            f"- **Total occurrences:** {r['total_occurrences']}",
            f"- **Operator context score:** {r['operator_analysis']['context_score']:.1%}",
            f"- **Confidence score:** {r['confidence_score']:.2f}",
            f"- **Verdict:** {r['verdict']}",
            "",
        ])

    lines.extend([
        "---",
        "",
        "*Generated by ZFD V1.5 Candidate Testing Pipeline*",
    ])

    return "\n".join(lines)


def main():
    """Run batch tests and generate reports."""
    random.seed(42)

    results = run_batch_tests(n_shuffles=500)

    # Save raw results
    output = {
        'generated': datetime.now().isoformat(),
        'n_candidates': len(results),
        'results': results
    }

    with open('validation/results/v15_batch_results.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print("\nRaw results saved to validation/results/v15_batch_results.json")

    # Generate report
    report = generate_report(results)
    with open('validation/v15_candidates_report.md', 'w') as f:
        f.write(report)
    print("Report saved to validation/v15_candidates_report.md")

    # Print summary
    print("\n" + "=" * 60)
    print("BATCH TEST SUMMARY")
    print("=" * 60)

    verdict_counts = Counter(r['verdict'] for r in results)
    for verdict, count in sorted(verdict_counts.items()):
        print(f"  {verdict}: {count}")

    print("\nTop 3 candidates by confidence:")
    for r in results[:3]:
        print(f"  {r['name']}: {r['confidence_score']:.2f} ({r['verdict']})")


if __name__ == "__main__":
    main()
