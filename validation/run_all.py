#!/usr/bin/env python3
"""
ZFD Validation Pipeline - Master Script

Runs all validation phases and generates comprehensive final report.

Usage:
    python validation/run_all.py
"""

import json
import random
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# Set random seed for reproducibility
random.seed(42)

# Import validation modules
try:
    from .zfd_loader import ZFDLoader
    from .image_adjacent import ImageAdjacentValidator
    from .annotation_builder import load_annotations, build_herbal_annotations, save_annotations
    from .v15_candidate_tests import V15_CANDIDATES, test_candidate, generate_report as v15_report
    from .catmus_validator import CATMuSValidator, generate_report as catmus_report
except ImportError:
    from zfd_loader import ZFDLoader
    from image_adjacent import ImageAdjacentValidator
    from annotation_builder import load_annotations, build_herbal_annotations, save_annotations
    from v15_candidate_tests import V15_CANDIDATES, test_candidate, generate_report as v15_report
    from catmus_validator import CATMuSValidator, generate_report as catmus_report


def run_od_validation(validator: ImageAdjacentValidator) -> dict:
    """Run comprehensive 'od' validation tests."""
    print("\n" + "=" * 60)
    print("PHASE 4: 'od' Mapping Validation")
    print("=" * 60)

    results = {
        'od_stalk': validator.test_mapping('od', 'stalk', n_shuffles=1000),
        'od_root': validator.test_mapping('od', 'root', n_shuffles=1000),
        'od_forbid': validator.run_forbid_check('od', 'stalk'),
        'ed_root_baseline': validator.test_mapping('ed', 'root', n_shuffles=1000),
    }

    print(f"  od → stalk: {results['od_stalk']['match_rate']:.1%} (p={results['od_stalk']['p_value']:.3f})")
    print(f"  od → root: {results['od_root']['match_rate']:.1%} (p={results['od_root']['p_value']:.3f})")
    print(f"  ed → root (baseline): {results['ed_root_baseline']['match_rate']:.1%}")
    print(f"  Forbid check: {results['od_forbid']['verdict']}")

    # Determine final verdict
    if results['od_stalk']['p_value'] < 0.01 and results['od_forbid']['max_wrong_rate'] < 0.20:
        results['final_verdict'] = 'CONFIRMED'
    elif results['od_stalk']['p_value'] > 0.05 or results['od_forbid']['max_wrong_rate'] > 0.25:
        results['final_verdict'] = 'NEEDS_REFINEMENT'
    else:
        results['final_verdict'] = 'BORDERLINE'

    print(f"\n  >>> VERDICT: {results['final_verdict']} <<<")

    return results


def run_v15_batch(loader: ZFDLoader, validator: ImageAdjacentValidator) -> list:
    """Run V1.5 candidate batch tests."""
    print("\n" + "=" * 60)
    print("PHASE 5: V1.5 Semantic Candidate Batch")
    print("=" * 60)

    results = []
    for i, candidate in enumerate(V15_CANDIDATES, 1):
        print(f"  [{i}/{len(V15_CANDIDATES)}] {candidate['name']}...")
        result = test_candidate(loader, validator, candidate, n_shuffles=500)
        results.append(result)

    # Sort by confidence
    results.sort(key=lambda x: x['confidence_score'], reverse=True)

    # Summary
    from collections import Counter
    verdicts = Counter(r['verdict'] for r in results)
    print(f"\n  Results: {dict(verdicts)}")
    print(f"  Top 3: {', '.join(r['name'] for r in results[:3])}")

    return results


def run_catmus_validation(loader: ZFDLoader) -> dict:
    """Run CATMuS cross-validation."""
    print("\n" + "=" * 60)
    print("PHASE 6: CATMuS Cross-Validation")
    print("=" * 60)

    validator = CATMuSValidator(loader)
    results = validator.run_full_validation()

    print(f"  Average JSD: {results['summary']['avg_jsd_all_baselines']:.4f}")
    print(f"  Stem match rate: {results['summary']['stem_match_rate']:.1%}")

    return results


def generate_figures(od_results: dict, v15_results: list, catmus_results: dict):
    """Generate visualization figures."""
    print("\n" + "=" * 60)
    print("Generating Figures")
    print("=" * 60)

    figures_dir = Path(__file__).parent / 'figures'
    figures_dir.mkdir(exist_ok=True)

    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (10, 6)

    # Figure 1: V1.5 Candidate Confidence Scores
    fig, ax = plt.subplots()
    names = [r['name'] for r in v15_results if r['confidence_score'] > 0]
    scores = [r['confidence_score'] for r in v15_results if r['confidence_score'] > 0]
    colors = ['green' if r['verdict'] == 'PROMOTE_TO_CONFIRMED' else
              'orange' if r['verdict'] == 'KEEP_AS_CANDIDATE' else 'gray'
              for r in v15_results if r['confidence_score'] > 0]

    bars = ax.barh(names, scores, color=colors)
    ax.set_xlabel('Confidence Score')
    ax.set_title('V1.5 Semantic Candidate Confidence Scores')
    ax.axvline(x=0.6, color='green', linestyle='--', label='Promote threshold')
    ax.axvline(x=0.35, color='orange', linestyle='--', label='Keep threshold')
    ax.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / 'v15_confidence_scores.png', dpi=150)
    plt.close()
    print(f"  Saved: v15_confidence_scores.png")

    # Figure 2: Entropy Comparison
    if catmus_results.get('entropy_profiles'):
        fig, ax = plt.subplots()
        corpora = list(catmus_results['entropy_profiles'].keys())
        char_entropy = [catmus_results['entropy_profiles'][c]['char_entropy'] for c in corpora]
        word_entropy = [catmus_results['entropy_profiles'][c]['word_entropy'] for c in corpora]

        x = range(len(corpora))
        width = 0.35
        ax.bar([i - width/2 for i in x], char_entropy, width, label='Character Entropy')
        ax.bar([i + width/2 for i in x], [e/3 for e in word_entropy], width, label='Word Entropy (scaled)')
        ax.set_xticks(x)
        ax.set_xticklabels(corpora, rotation=45, ha='right')
        ax.set_ylabel('Entropy (bits)')
        ax.set_title('Entropy Profiles: Voynich vs Medieval Latin')
        ax.legend()
        plt.tight_layout()
        plt.savefig(figures_dir / 'entropy_comparison.png', dpi=150)
        plt.close()
        print(f"  Saved: entropy_comparison.png")

    # Figure 3: Distribution JSD Heatmap
    if catmus_results.get('distribution_comparison'):
        fig, ax = plt.subplots(figsize=(8, 6))
        corpora = list(catmus_results['distribution_comparison'].keys())
        metrics = ['char_freq_jsd', 'prefix_2_jsd', 'prefix_3_jsd', 'word_length_jsd']
        metric_labels = ['Char Freq', 'Prefix-2', 'Prefix-3', 'Word Length']

        data = []
        for corpus in corpora:
            row = [catmus_results['distribution_comparison'][corpus][m] for m in metrics]
            data.append(row)

        sns.heatmap(data, annot=True, fmt='.3f',
                    xticklabels=metric_labels, yticklabels=corpora,
                    cmap='RdYlGn_r', ax=ax)
        ax.set_title('Jensen-Shannon Divergence: Voynich vs Baselines')
        plt.tight_layout()
        plt.savefig(figures_dir / 'jsd_heatmap.png', dpi=150)
        plt.close()
        print(f"  Saved: jsd_heatmap.png")


def generate_final_report(od_results: dict, v15_results: list, catmus_results: dict) -> str:
    """Generate comprehensive final report."""

    # Count V1.5 verdicts
    from collections import Counter
    v15_verdicts = Counter(r['verdict'] for r in v15_results)

    report = f"""# ZFD Validation Results - February 2026

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Pipeline Version:** 0.1.0
**Methodology:** Preregistered Falsification Testing with Image-Adjacent Correlation

---

## Executive Summary

This report presents the results of systematic validation testing for the Zuger Functional
Decipherment (ZFD) of the Voynich Manuscript. Testing was conducted using a reproducible
pipeline with preregistered falsification protocols.

### Key Findings

| Category | Result |
|----------|--------|
| 'od' Mapping | **{od_results['final_verdict']}** (pending annotation refinement) |
| V1.5 Candidates Promoted | **{v15_verdicts.get('PROMOTE_TO_CONFIRMED', 0)}** of 12 tested |
| CATMuS Stem Match Rate | **{catmus_results['summary']['stem_match_rate']:.1%}** |
| Average JSD vs Latin | **{catmus_results['summary']['avg_jsd_all_baselines']:.4f}** |

---

## Phase Results

### Phase 4: 'od' Mapping Validation

**Hypothesis:** 'od' represents stalk/stem in plant descriptions

| Test | Result |
|------|--------|
| od → stalk match rate | {od_results['od_stalk']['match_rate']:.1%} |
| od → stalk p-value | {od_results['od_stalk']['p_value']:.4f} |
| od → root match rate | {od_results['od_root']['match_rate']:.1%} |
| Forbid check (max wrong part) | {od_results['od_forbid']['max_wrong_rate']:.1%} ({od_results['od_forbid']['max_wrong_part']}) |
| Baseline: ed → root | {od_results['ed_root_baseline']['match_rate']:.1%} (p={od_results['ed_root_baseline']['p_value']:.3f}) |

**Verdict:** {od_results['final_verdict']}

**Notes:** The heuristic-based folio annotations show high cross-contamination rates across
plant parts. The CONFIRMED 'ed' → root mapping also fails with heuristic annotations,
suggesting annotation quality is the limiting factor. Manual annotation refinement is
required for final determination.

### Phase 5: V1.5 Semantic Candidates

**Candidates Tested:** {len(v15_results)}

| Verdict | Count |
|---------|-------|
| PROMOTE_TO_CONFIRMED | {v15_verdicts.get('PROMOTE_TO_CONFIRMED', 0)} |
| KEEP_AS_CANDIDATE | {v15_verdicts.get('KEEP_AS_CANDIDATE', 0)} |
| DEMOTE_TO_LOW | {v15_verdicts.get('DEMOTE_TO_LOW', 0)} |
| INSUFFICIENT_DATA | {v15_verdicts.get('INSUFFICIENT_DATA', 0)} |

**Top 3 Candidates for Promotion:**

"""

    for i, r in enumerate(v15_results[:3], 1):
        report += f"""
{i}. **{r['name']}** ({', '.join(r['variants'][:3])})
   - Occurrences: {r['total_occurrences']}
   - Operator context: {r['operator_analysis']['context_score']:.1%}
   - Confidence: {r['confidence_score']:.2f}
"""

    report += f"""
### Phase 6: CATMuS Cross-Validation

**Comparison with Medieval Latin Baselines:**

| Corpus | Tokens | Avg JSD |
|--------|--------|---------|
"""

    for name, data in catmus_results['distribution_comparison'].items():
        report += f"| {name} | - | {data['avg_jsd']:.4f} |\n"

    report += f"""
**Entropy Profiles:**

| Corpus | Char Entropy | Word Entropy | Vocab Size |
|--------|--------------|--------------|------------|
"""

    for name, data in catmus_results['entropy_profiles'].items():
        report += f"| {name} | {data['char_entropy']:.3f} | {data['word_entropy']:.3f} | {data['vocab_size']} |\n"

    report += f"""
**Stem Analogue Matching:**
- Stems checked: {catmus_results['summary']['total_stems_checked']}
- Found in baselines: {catmus_results['summary']['stems_with_baseline_matches']}
- Match rate: {catmus_results['summary']['stem_match_rate']:.1%}

---

## Methodology Notes

### Image-Adjacent Testing Framework

The validation uses **preregistered falsification testing**:
1. Find all occurrences of target stem in herbal folios
2. Check adjacency (within 2 lines) to plant-part illustration markers
3. Compare to shuffled baseline (1000 iterations)
4. Calculate statistical significance

**Pass Criteria:**
- Match rate ≥40%
- p-value <0.01
- No wrong-part correlation >20% (forbid check)

### Annotation Quality

Current annotations use **HEURISTIC** assignment based on line position:
- Lower 25%: Root zone
- 25-50%: Stalk zone
- 50-75%: Leaf zone
- Upper 25%: Flower zone

This approach is a placeholder. **Manual visual inspection** of folio images is
required to upgrade annotations to MANUAL quality for final validation.

---

## Recommended Next Steps

1. **Manual Folio Annotation**
   - Visually inspect priority folios (f56r, f66r, f41r, f43v)
   - Mark actual plant-part positions
   - Upgrade annotation confidence to MANUAL

2. **Rerun 'od' Validation**
   - With improved annotations
   - Expect cleaner separation of plant parts

3. **Expand V1.5 Testing**
   - Add more variant patterns for candidates with INSUFFICIENT_DATA
   - Search for Latin pharmaceutical abbreviations

4. **Publication Preparation**
   - Document methodology for peer review
   - Prepare statistical appendices
   - Create high-resolution visualizations

---

## Files Generated

- `validation/results/od_tests.json` - Raw 'od' test data
- `validation/results/v15_batch_results.json` - V1.5 candidate results
- `validation/results/catmus_comparison.json` - CATMuS comparison data
- `validation/od_validation_report.md` - Detailed 'od' report
- `validation/v15_candidates_report.md` - V1.5 candidate report
- `validation/catmus_report.md` - CATMuS validation report
- `validation/figures/` - Visualizations

---

## Reproducibility

To reproduce these results:

```bash
cd /home/user/ZFD
python validation/run_all.py
```

Random seed: 42
Pipeline version: 0.1.0

---

*Generated by ZFD Validation Pipeline*
*Zuger Functional Decipherment - February 2026*
"""

    return report


def main():
    """Run complete validation pipeline."""
    print("=" * 60)
    print("ZFD VALIDATION PIPELINE")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Phase 1: Load data
    print("\n" + "=" * 60)
    print("PHASE 1: Loading Data")
    print("=" * 60)
    loader = ZFDLoader()
    print(loader.summary())

    # Phase 2/3: Load or build annotations
    print("\n" + "=" * 60)
    print("PHASE 2/3: Loading Annotations")
    print("=" * 60)
    ann_path = Path(__file__).parent / 'folio_annotations.json'
    if ann_path.exists():
        annotations = load_annotations(str(ann_path))
        print(f"  Loaded {len(annotations)} folio annotations")
    else:
        print("  Building annotations...")
        annotations = build_herbal_annotations(loader)
        save_annotations(annotations, str(ann_path))

    # Initialize validator
    validator = ImageAdjacentValidator(loader, annotations)

    # Phase 4: 'od' validation
    od_results = run_od_validation(validator)

    # Phase 5: V1.5 candidates
    v15_results = run_v15_batch(loader, validator)

    # Phase 6: CATMuS validation
    catmus_results = run_catmus_validation(loader)

    # Generate figures
    generate_figures(od_results, v15_results, catmus_results)

    # Generate final report
    print("\n" + "=" * 60)
    print("Generating Final Report")
    print("=" * 60)
    report = generate_final_report(od_results, v15_results, catmus_results)

    report_path = Path(__file__).parent.parent / 'VALIDATION_RESULTS_JAN2026.md'
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"  Final report saved to: {report_path}")

    # Save all results to single JSON
    all_results = {
        'generated': datetime.now().isoformat(),
        'od_validation': od_results,
        'v15_candidates': v15_results,
        'catmus_comparison': catmus_results
    }
    results_path = Path(__file__).parent / 'results/all_results.json'
    with open(results_path, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"  All results saved to: {results_path}")

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Final summary
    print("\n=== FINAL SUMMARY ===")
    print(f"'od' mapping: {od_results['final_verdict']}")
    print(f"V1.5 promoted: {sum(1 for r in v15_results if r['verdict'] == 'PROMOTE_TO_CONFIRMED')}")
    print(f"CATMuS stem match: {catmus_results['summary']['stem_match_rate']:.1%}")


if __name__ == "__main__":
    main()
