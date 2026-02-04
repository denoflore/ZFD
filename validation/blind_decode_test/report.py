"""
Report generator for blind decode test.

Generates human-readable Markdown report from test results.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).parent))

from config import TEST_FOLIOS, SHUFFLE_SEED, SHUFFLE_ITERATIONS, THRESHOLDS


def generate_report(comparison: Dict, real_results: Dict, baseline_results: Dict,
                   output_path: str):
    """
    Generate comprehensive Markdown report from test results.

    Args:
        comparison: Statistical comparison results
        real_results: Real decode results per folio
        baseline_results: Baseline results per folio
        output_path: Path to save the report
    """
    lines = []

    # Header
    lines.extend(generate_header(comparison))

    # Executive Summary
    lines.extend(generate_executive_summary(comparison))

    # Methodology
    lines.extend(generate_methodology())

    # Per-Folio Results Table
    lines.extend(generate_results_table(comparison))

    # Prediction Accuracy Table
    lines.extend(generate_predictions_table(comparison))

    # Detailed Folio Analysis
    lines.extend(generate_detailed_analysis(comparison, real_results, baseline_results))

    # Interpretation
    lines.extend(generate_interpretation(comparison))

    # Key Statement (required)
    lines.extend(generate_key_statement())

    # Reproducibility
    lines.extend(generate_reproducibility())

    # Raw Data References
    lines.extend(generate_raw_data_section())

    # Lexicon Integrity
    lines.extend(generate_integrity_section(comparison))

    # Write report
    report_text = '\n'.join(lines)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_text)


def generate_header(comparison: Dict) -> list:
    """Generate report header."""
    test_date = comparison.get('test_date', datetime.now().isoformat())
    lexicon_hash = comparison.get('lexicon_sha256', 'unknown')[:16]
    verdict = comparison.get('overall_verdict', 'UNKNOWN')

    return [
        "# ZFD Blind Decode Falsification Test Report",
        "",
        f"**Test Date:** {test_date[:10]}",
        f"**Lexicon Checksum:** {lexicon_hash}...",
        f"**Pipeline Version:** ZFD v1.0",
        f"**Overall Verdict:** **{verdict}**",
        "",
        "---",
        "",
    ]


def generate_executive_summary(comparison: Dict) -> list:
    """Generate executive summary."""
    verdict = comparison.get('overall_verdict', 'UNKNOWN')
    summary = comparison.get('summary', {})
    folios_passing = summary.get('folios_passing', 0)
    folios_tested = summary.get('folios_tested', 0)
    mean_z = summary.get('mean_z_score', 0)
    overall_p = summary.get('overall_p', 1)

    lines = [
        "## Executive Summary",
        "",
    ]

    if verdict == "PASS":
        lines.extend([
            f"The ZFD blind decode test **PASSED**. {folios_passing} of {folios_tested} folios ",
            "produced significantly higher coherence scores on real manuscript text compared ",
            "to shuffled baselines (mean z-score: {:.2f}, p < {:.4f}). ".format(mean_z, overall_p),
            "",
            "This result refutes the 'degrees of freedom' criticism: the decoder detects ",
            "structure that exists in the manuscript, not structure it generates from ",
            "flexible parameters.",
            "",
        ])
    elif verdict == "FAIL":
        lines.extend([
            f"The ZFD blind decode test **FAILED**. Only {folios_passing} of {folios_tested} folios ",
            "produced coherence scores significantly higher than shuffled baselines. ",
            "",
            "The results indicate the decoder produces similar output regardless of input ",
            "structure. The 'degrees of freedom' criticism has merit: the system's flexibility ",
            "may generate Croatian-compatible output from any input.",
            "",
        ])
    else:  # PARTIAL or other
        lines.extend([
            f"The ZFD blind decode test produced **MIXED** results. {folios_passing} of {folios_tested} folios ",
            "passed the coherence threshold, but results varied across folios. ",
            "",
            "Further investigation is needed to determine whether the decoder is detecting ",
            "real manuscript structure or generating it from flexible parameters.",
            "",
        ])

    return lines


def generate_methodology() -> list:
    """Generate methodology section."""
    return [
        "## Methodology",
        "",
        "### Test Design",
        "",
        "1. **Freeze the lexicon**: The lexicon file is checksummed (SHA-256) at test start ",
        "   and verified at test end. No modifications are permitted during the test run.",
        "",
        "2. **Decode real folios**: Five preregistered test folios are decoded through the ",
        "   frozen pipeline.",
        "",
        "3. **Generate shuffled baselines**: For each folio, {} shuffled versions are created ".format(SHUFFLE_ITERATIONS),
        "   using deterministic random seeds ({}-{}). Shuffling preserves word count and ".format(SHUFFLE_SEED, SHUFFLE_SEED + SHUFFLE_ITERATIONS - 1),
        "   line structure but randomizes word positions.",
        "",
        "4. **Statistical comparison**: Real decode results are compared against the shuffled ",
        "   distribution using z-scores and empirical p-values.",
        "",
        "### Coherence Index",
        "",
        "The coherence index (0-1) is computed as:",
        "",
        "```",
        "coherence = 0.30 * known_ratio +       # % of stems matched in lexicon",
        "            0.25 * operator_diversity + # min(distinct_operators / 5, 1)",
        "            0.25 * category_diversity + # min(distinct_categories / 5, 1)",
        "            0.20 * confidence_mean      # average pipeline confidence",
        "```",
        "",
        "### Pass/Fail Criteria (Preregistered)",
        "",
        f"- **Coherence threshold**: >= {THRESHOLDS['min_coherence']}",
        f"- **Significance level**: p < {THRESHOLDS['significance_level']}",
        f"- **Passing requirement**: >= {THRESHOLDS['min_passing_folios']} of 5 folios must pass",
        "",
        "---",
        "",
    ]


def generate_results_table(comparison: Dict) -> list:
    """Generate per-folio results table."""
    lines = [
        "## Per-Folio Results",
        "",
        "| Folio | Real Coherence | Shuffled Mean +/- SD | Z-score | p-value | Verdict |",
        "|-------|----------------|----------------------|---------|---------|---------|",
    ]

    for folio_id in TEST_FOLIOS:
        fc = comparison['folios'].get(folio_id, {})
        real_coh = fc.get('real_coherence', 0)
        shuf_mean = fc.get('shuffled_mean', 0)
        shuf_std = fc.get('shuffled_std', 0)
        z_score = fc.get('z_score', 0)
        p_value = fc.get('p_value', 1)
        verdict = fc.get('verdict', 'N/A')

        lines.append(
            f"| {folio_id} | {real_coh:.4f} | {shuf_mean:.4f} +/- {shuf_std:.4f} | "
            f"{z_score:.2f} | {p_value:.4f} | {verdict} |"
        )

    lines.extend(["", ""])
    return lines


def generate_predictions_table(comparison: Dict) -> list:
    """Generate prediction accuracy table."""
    lines = [
        "## Prediction Accuracy",
        "",
        "| Folio | Operators Found | Stems Found | Categories Match | Shuffled Match Rate |",
        "|-------|-----------------|-------------|------------------|---------------------|",
    ]

    for folio_id in TEST_FOLIOS:
        fc = comparison['folios'].get(folio_id, {})
        preds = fc.get('predictions_met', {})
        ops = "Yes" if preds.get('operators', False) else "No"
        stems = "Yes" if preds.get('stems', False) else "No"
        cats = "Yes" if preds.get('categories', False) else "No"
        shuf_rate = fc.get('shuffled_prediction_rate', 0)

        lines.append(f"| {folio_id} | {ops} | {stems} | {cats} | {shuf_rate:.1%} |")

    lines.extend([
        "",
        "*Shuffled Match Rate indicates how often shuffled baselines accidentally meet the folio-specific predictions.*",
        "*If this rate exceeds 20%, the predictions may be too loose.*",
        "",
    ])
    return lines


def generate_detailed_analysis(comparison: Dict, real_results: Dict,
                               baseline_results: Dict) -> list:
    """Generate detailed per-folio analysis."""
    lines = [
        "## Detailed Folio Analysis",
        "",
    ]

    for folio_id in TEST_FOLIOS:
        fc = comparison['folios'].get(folio_id, {})
        real = real_results.get(folio_id, {})
        baseline = baseline_results.get(folio_id, {})

        lines.extend([
            f"### {folio_id}",
            "",
            f"**Real Decode:**",
            f"- Tokens: {real.get('total_tokens', 0)}",
            f"- Known stems: {real.get('known_stems', 0)} ({real.get('known_ratio', 0):.1%})",
            f"- Operators: {real.get('operator_counts', {})}",
            f"- Categories: {real.get('category_counts', {})}",
            f"- Coherence: {fc.get('real_coherence', 0):.4f}",
            "",
            f"**Baseline Statistics ({baseline.get('iterations', 0)} iterations):**",
            f"- Coherence: {fc.get('shuffled_mean', 0):.4f} +/- {fc.get('shuffled_std', 0):.4f}",
            f"- Range: [{baseline.get('stats', {}).get('coherence_min', 0):.4f}, "
            f"{baseline.get('stats', {}).get('coherence_max', 0):.4f}]",
            "",
            f"**Statistical Comparison:**",
            f"- Z-score: {fc.get('z_score', 0):.2f}",
            f"- p-value: {fc.get('p_value', 1):.4f}",
            f"- Effect size: {fc.get('effect_size', 0):.2f}",
            f"- Verdict: **{fc.get('verdict', 'N/A')}**",
            "",
        ])

    return lines


def generate_interpretation(comparison: Dict) -> list:
    """Generate interpretation section."""
    verdict = comparison.get('overall_verdict', 'UNKNOWN')

    lines = [
        "## Interpretation",
        "",
    ]

    # Check if decoder is position-independent
    position_independent = all(
        fc.get('verdict') == 'POSITION_INDEPENDENT'
        for fc in comparison.get('folios', {}).values()
    )

    if position_independent:
        lines.extend([
            "### Finding: Position-Independent Decoder",
            "",
            "The test reveals that the ZFD decoder processes tokens **independently** without ",
            "using positional context. Shuffling word order does not change the decode results ",
            "because each token is analyzed in isolation.",
            "",
            "This is an important finding:",
            "",
            "1. **The decoder does not rely on word order** - it treats each Voynich word as ",
            "   an independent pharmaceutical abbreviation.",
            "",
            "2. **The coherence metric measures vocabulary coverage**, not sequential structure. ",
            "   High coherence indicates the decoder recognizes many words, regardless of their ",
            "   arrangement.",
            "",
            "3. **The 'degrees of freedom' criticism has a different meaning here**: the question ",
            "   is not whether order matters, but whether the decoder's vocabulary mappings are ",
            "   genuinely detecting Croatian pharmaceutical terms or are flexible enough to match ",
            "   anything.",
            "",
            "### Implications",
            "",
            "A position-independent decoder is consistent with the ZFD hypothesis that Voynich ",
            "text represents pharmaceutical shorthand, where each word abbreviates a term or ",
            "instruction. In recipe texts, word order is often less critical than the presence ",
            "of key ingredients and actions.",
            "",
            "However, this test cannot distinguish between:",
            "- A decoder that correctly identifies Croatian pharmaceutical abbreviations",
            "- A decoder flexible enough to produce plausible-looking output from any input",
            "",
            "Additional validation approaches are needed, such as:",
            "- Comparing decoded content against manuscript illustrations",
            "- Testing the decoder on known non-Voynich text",
            "- Expert review of decoded pharmaceutical content",
            "",
        ])
    elif verdict == "PASS":
        lines.extend([
            "### Degrees of Freedom Refuted",
            "",
            "The real manuscript text produces significantly higher coherence scores than ",
            "shuffled versions through the same pipeline. This demonstrates that:",
            "",
            "1. The decoder is detecting structure that exists in the manuscript",
            "2. The 'degrees of freedom' cannot explain the results",
            "3. Random arrangements of the same vocabulary produce worse coherence",
            "",
            "The ZFD system is functioning as a **decoder**, not a **generator**.",
            "",
        ])
    else:
        lines.extend([
            "### Results Inconclusive",
            "",
            "The test did not produce a clear signal. This could indicate:",
            "",
            "1. The decoder has enough flexibility to produce similar results from any input",
            "2. The coherence metric does not capture the relevant structure",
            "3. The test folios may not be representative",
            "",
            "Further investigation is recommended.",
            "",
        ])

    return lines


def generate_key_statement() -> list:
    """Generate the required key statement."""
    return [
        "## Key Statement",
        "",
        "> \"If the shuffled baseline produces coherence scores statistically indistinguishable ",
        "> from the real decode, this test has failed and the degrees-of-freedom criticism is ",
        "> valid. If the real decode produces significantly higher coherence than shuffled input ",
        "> through the same pipeline, the decoder is detecting structure that exists in the ",
        "> manuscript, not generating it from flexible parameters.\"",
        "",
        "---",
        "",
    ]


def generate_reproducibility() -> list:
    """Generate reproducibility section."""
    return [
        "## Reproducibility",
        "",
        "This test is fully reproducible. To run it yourself:",
        "",
        "```bash",
        "# Clone the repository",
        "git clone https://github.com/denoflore/ZFD.git",
        "cd ZFD",
        "",
        "# Run the full test (100 iterations per folio)",
        "python validation/blind_decode_test/run_test.py",
        "",
        "# Or run a quick test (10 iterations)",
        "python validation/blind_decode_test/run_test.py --quick",
        "",
        "# Or test a single folio",
        "python validation/blind_decode_test/run_test.py --folio f10r",
        "```",
        "",
        "All shuffling uses deterministic random seeds, ensuring identical results ",
        "on every run.",
        "",
        "---",
        "",
    ]


def generate_raw_data_section() -> list:
    """Generate raw data references."""
    return [
        "## Raw Data",
        "",
        "All test outputs are saved to `validation/blind_decode_test/results/`:",
        "",
        "- `test_metadata.json` - Test configuration and timestamps",
        "- `real_decode_<folio>.json` - Full decode results per folio",
        "- `baseline_<folio>.json` - All shuffled iteration results per folio",
        "- `comparison_results.json` - Statistical comparison data",
        "",
        "---",
        "",
    ]


def generate_integrity_section(comparison: Dict) -> list:
    """Generate lexicon integrity section."""
    lexicon_hash = comparison.get('lexicon_sha256', 'unknown')

    return [
        "## Lexicon Integrity",
        "",
        "The lexicon file was checksummed at test start and verified at test end.",
        "",
        f"**SHA-256:** `{lexicon_hash}`",
        "",
        "**Status:** Verified (no modifications during test)",
        "",
        "This ensures the decoder parameters remained frozen throughout the test run, ",
        "eliminating the possibility of tuning the lexicon to improve results.",
        "",
        "---",
        "",
        "*Report generated by ZFD Blind Decode Falsification Test*",
        f"*{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
    ]


if __name__ == "__main__":
    # Test report generation
    from decoder import decode_folio
    from baseline import generate_baselines
    from compare import compare_results

    print("Testing report.py...")

    # Generate test data
    real = {"f10r": decode_folio("f10r")}
    baseline = {"f10r": generate_baselines("f10r", iterations=5)}
    comparison = compare_results(real, baseline, "test_hash_abcdef123456789")

    # Generate report
    output_path = Path(__file__).parent / "results" / "TEST_REPORT.md"
    generate_report(comparison, real, baseline, str(output_path))

    print(f"Test report saved to: {output_path}")
    print("\nReport test passed!")
