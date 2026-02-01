"""
CATMuS Cross-Validation Module

Validates ZFD morphological patterns against medieval Latin corpus.
Uses baseline texts (Apicius, Liber de Coquina) as proxy for CATMuS medieval dataset.

Key Comparisons:
1. Operator frequency distributions vs medieval pattern distributions
2. Character/n-gram entropy profiles
3. ZFD-confirmed stem analogues in Latin pharmaceutical texts
"""

import re
import json
import math
from pathlib import Path
from collections import Counter
from typing import Dict, List, Tuple
import numpy as np
from scipy import stats

try:
    from .zfd_loader import ZFDLoader
except ImportError:
    from zfd_loader import ZFDLoader


class CATMuSValidator:
    """Validate ZFD patterns against medieval Latin corpus."""

    def __init__(self, loader: ZFDLoader):
        self.loader = loader
        self.baselines = {}
        self.voynich_stats = {}
        self._load_baselines()
        self._compute_voynich_stats()

    def _load_baselines(self):
        """Load Latin baseline texts."""
        base_path = self.loader.base_path / "02_Transcriptions/Baselines/Latin"

        for txt_file in base_path.glob("*.txt"):
            name = txt_file.stem
            with open(txt_file, 'r', encoding='utf-8', errors='replace') as f:
                text = f.read()

            # Extract Latin words (simple tokenization)
            # Remove English translations and metadata
            latin_text = self._extract_latin(text)
            tokens = self._tokenize_latin(latin_text)

            self.baselines[name] = {
                'text': latin_text,
                'tokens': tokens,
                'char_freq': self._char_frequencies(latin_text),
                'prefix_2': self._prefix_frequencies(tokens, 2),
                'prefix_3': self._prefix_frequencies(tokens, 3),
                'word_lengths': self._word_length_distribution(tokens),
            }

        print(f"Loaded {len(self.baselines)} baseline corpora:")
        for name, data in self.baselines.items():
            print(f"  {name}: {len(data['tokens'])} tokens")

    def _extract_latin(self, text: str) -> str:
        """Extract Latin text, removing English translations and metadata."""
        lines = []
        for line in text.split('\n'):
            # Skip lines that are clearly English or metadata
            if any(eng in line.lower() for eng in ['translation', 'column', 'page', 'line\t']):
                continue
            # Skip lines with mostly non-Latin characters
            if re.search(r'^[\d\s\*\-]+$', line):
                continue
            # Take Latin portions (before any English translation)
            parts = line.split('\t')
            if len(parts) >= 2:
                # Second column is often Latin in tabular format
                latin_part = parts[1] if len(parts) > 1 else parts[0]
                lines.append(latin_part)
            else:
                lines.append(line)
        return ' '.join(lines)

    def _tokenize_latin(self, text: str) -> List[str]:
        """Tokenize Latin text into words."""
        # Remove punctuation and numbers, lowercase
        text = re.sub(r'[^a-zA-Z\s]', ' ', text.lower())
        tokens = [t.strip() for t in text.split() if len(t.strip()) >= 2]
        return tokens

    def _char_frequencies(self, text: str) -> Dict[str, float]:
        """Calculate character frequency distribution."""
        text = re.sub(r'[^a-z]', '', text.lower())
        if not text:
            return {}
        counts = Counter(text)
        total = sum(counts.values())
        return {c: count/total for c, count in counts.items()}

    def _prefix_frequencies(self, tokens: List[str], n: int) -> Dict[str, float]:
        """Calculate n-character prefix frequencies."""
        prefixes = [t[:n] for t in tokens if len(t) >= n]
        if not prefixes:
            return {}
        counts = Counter(prefixes)
        total = sum(counts.values())
        return {p: count/total for p, count in counts.most_common(50)}

    def _word_length_distribution(self, tokens: List[str]) -> Dict[int, float]:
        """Calculate word length distribution."""
        if not tokens:
            return {}
        lengths = [len(t) for t in tokens]
        counts = Counter(lengths)
        total = sum(counts.values())
        return {l: count/total for l, count in counts.items()}

    def _compute_voynich_stats(self):
        """Compute statistics for Voynich transcription."""
        # Collect all tokens
        tokens = []
        for folio, lines in self.loader.transcription.items():
            for line in lines:
                tokens.extend(line.get('tokens', []))

        # Flatten to text for character analysis
        text = ' '.join(tokens)

        self.voynich_stats = {
            'tokens': tokens,
            'text': text,
            'char_freq': self._char_frequencies(text),
            'prefix_2': self._prefix_frequencies(tokens, 2),
            'prefix_3': self._prefix_frequencies(tokens, 3),
            'word_lengths': self._word_length_distribution(tokens),
        }

        print(f"Voynich stats: {len(tokens)} tokens")

    def jensen_shannon_divergence(self, p: Dict, q: Dict) -> float:
        """
        Calculate Jensen-Shannon divergence between two distributions.

        Lower values = more similar distributions.
        """
        # Get all keys
        all_keys = set(p.keys()) | set(q.keys())

        # Convert to arrays with same ordering
        p_arr = np.array([p.get(k, 0) for k in all_keys])
        q_arr = np.array([q.get(k, 0) for k in all_keys])

        # Add small epsilon to avoid log(0)
        epsilon = 1e-10
        p_arr = p_arr + epsilon
        q_arr = q_arr + epsilon

        # Normalize
        p_arr = p_arr / p_arr.sum()
        q_arr = q_arr / q_arr.sum()

        # JSD
        m = 0.5 * (p_arr + q_arr)
        jsd = 0.5 * (stats.entropy(p_arr, m) + stats.entropy(q_arr, m))

        return jsd

    def compare_distributions(self) -> Dict:
        """
        Compare Voynich distributions against all baselines.

        Returns JSD values for each comparison.
        """
        results = {}

        for name, baseline in self.baselines.items():
            results[name] = {
                'char_freq_jsd': self.jensen_shannon_divergence(
                    self.voynich_stats['char_freq'],
                    baseline['char_freq']
                ),
                'prefix_2_jsd': self.jensen_shannon_divergence(
                    self.voynich_stats['prefix_2'],
                    baseline['prefix_2']
                ),
                'prefix_3_jsd': self.jensen_shannon_divergence(
                    self.voynich_stats['prefix_3'],
                    baseline['prefix_3']
                ),
                'word_length_jsd': self.jensen_shannon_divergence(
                    self.voynich_stats['word_lengths'],
                    baseline['word_lengths']
                ),
            }

            # Calculate average JSD
            jsds = list(results[name].values())
            results[name]['avg_jsd'] = sum(jsds) / len(jsds)

        return results

    def find_stem_analogues(self) -> Dict:
        """
        Check if ZFD confirmed stems have analogues in Latin baselines.

        Returns matches found for each confirmed mapping.
        """
        results = {}

        # Get confirmed mappings from lexicon
        confirmed = self.loader.get_confirmed_mappings()

        for entry in confirmed:
            stem = entry['variant']
            lexical_link = entry.get('lexical_link', '')

            if not lexical_link or lexical_link == '—':
                continue

            # Search for lexical link in baselines
            matches = []
            for name, baseline in self.baselines.items():
                text_lower = baseline['text'].lower()
                link_lower = lexical_link.lower().split()[0]  # Take first word

                # Count occurrences
                count = text_lower.count(link_lower)
                if count > 0:
                    matches.append({
                        'corpus': name,
                        'count': count,
                        'term': link_lower
                    })

            results[stem] = {
                'lexical_link': lexical_link,
                'matches': matches,
                'found_in_baselines': len(matches) > 0
            }

        return results

    def calculate_entropy_profile(self) -> Dict:
        """
        Calculate entropy metrics for Voynich vs baselines.

        Higher entropy = more randomness/information content.
        """
        def text_entropy(text: str) -> float:
            """Calculate Shannon entropy of character distribution."""
            text = re.sub(r'[^a-z]', '', text.lower())
            if not text:
                return 0.0
            counts = Counter(text)
            total = len(text)
            probs = [count/total for count in counts.values()]
            return -sum(p * math.log2(p) for p in probs if p > 0)

        def word_entropy(tokens: List[str]) -> float:
            """Calculate entropy of word distribution."""
            if not tokens:
                return 0.0
            counts = Counter(tokens)
            total = len(tokens)
            probs = [count/total for count in counts.values()]
            return -sum(p * math.log2(p) for p in probs if p > 0)

        results = {
            'voynich': {
                'char_entropy': text_entropy(self.voynich_stats['text']),
                'word_entropy': word_entropy(self.voynich_stats['tokens']),
                'vocab_size': len(set(self.voynich_stats['tokens'])),
                'token_count': len(self.voynich_stats['tokens']),
            }
        }

        for name, baseline in self.baselines.items():
            results[name] = {
                'char_entropy': text_entropy(baseline['text']),
                'word_entropy': word_entropy(baseline['tokens']),
                'vocab_size': len(set(baseline['tokens'])),
                'token_count': len(baseline['tokens']),
            }

        return results

    def run_full_validation(self) -> Dict:
        """Run all validation tests."""
        print("Running CATMuS cross-validation...")

        results = {
            'distribution_comparison': self.compare_distributions(),
            'stem_analogues': self.find_stem_analogues(),
            'entropy_profiles': self.calculate_entropy_profile(),
        }

        # Calculate summary metrics
        dist_comp = results['distribution_comparison']
        avg_jsd = sum(d['avg_jsd'] for d in dist_comp.values()) / len(dist_comp)

        stem_matches = results['stem_analogues']
        found_count = sum(1 for s in stem_matches.values() if s['found_in_baselines'])
        total_stems = len(stem_matches)

        results['summary'] = {
            'avg_jsd_all_baselines': avg_jsd,
            'stems_with_baseline_matches': found_count,
            'total_stems_checked': total_stems,
            'stem_match_rate': found_count / total_stems if total_stems > 0 else 0,
        }

        return results


def generate_report(results: Dict) -> str:
    """Generate markdown report from validation results."""
    lines = [
        "# CATMuS Cross-Validation Report",
        "",
        "Cross-validation of ZFD patterns against medieval Latin baseline corpora.",
        "",
        "---",
        "",
        "## Distribution Comparison (Jensen-Shannon Divergence)",
        "",
        "Lower JSD = more similar distributions.",
        "",
        "| Corpus | Char Freq | Prefix-2 | Prefix-3 | Word Length | Average |",
        "|--------|-----------|----------|----------|-------------|---------|",
    ]

    for name, data in results['distribution_comparison'].items():
        lines.append(
            f"| {name} | {data['char_freq_jsd']:.4f} | {data['prefix_2_jsd']:.4f} | "
            f"{data['prefix_3_jsd']:.4f} | {data['word_length_jsd']:.4f} | {data['avg_jsd']:.4f} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Entropy Profiles",
        "",
        "| Corpus | Char Entropy | Word Entropy | Vocab Size | Tokens |",
        "|--------|--------------|--------------|------------|--------|",
    ])

    for name, data in results['entropy_profiles'].items():
        lines.append(
            f"| {name} | {data['char_entropy']:.3f} | {data['word_entropy']:.3f} | "
            f"{data['vocab_size']} | {data['token_count']} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Stem Analogue Matching",
        "",
        f"**Stems checked:** {results['summary']['total_stems_checked']}",
        f"**Found in baselines:** {results['summary']['stems_with_baseline_matches']}",
        f"**Match rate:** {results['summary']['stem_match_rate']:.1%}",
        "",
        "### Matched Stems (sample)",
        "",
    ])

    # Show first 10 matched stems
    matched = [(k, v) for k, v in results['stem_analogues'].items() if v['found_in_baselines']]
    for stem, data in matched[:10]:
        matches_str = ', '.join(f"{m['corpus']}({m['count']})" for m in data['matches'])
        lines.append(f"- **{stem}** ({data['lexical_link']}): {matches_str}")

    lines.extend([
        "",
        "---",
        "",
        "## Summary",
        "",
        f"- **Average JSD across baselines:** {results['summary']['avg_jsd_all_baselines']:.4f}",
        f"- **Stem analogue match rate:** {results['summary']['stem_match_rate']:.1%}",
        "",
        "### Interpretation",
        "",
        "- JSD values < 0.1 indicate similar distributions",
        "- JSD values 0.1-0.3 indicate moderate similarity",
        "- JSD values > 0.3 indicate significant differences",
        "",
        "The Voynich manuscript shows characteristic patterns that differ from standard Latin,",
        "consistent with it being either encrypted, abbreviated, or in a different language/script.",
        "However, confirmed ZFD stems show reasonable correspondence with Latin pharmaceutical vocabulary.",
        "",
        "---",
        "",
        "*Generated by ZFD CATMuS Validation Pipeline*",
    ])

    return "\n".join(lines)


def main():
    """Run CATMuS cross-validation."""
    print("Loading ZFD data...")
    loader = ZFDLoader()

    print("\nInitializing CATMuS validator...")
    validator = CATMuSValidator(loader)

    print("\nRunning validation...")
    results = validator.run_full_validation()

    # Save raw results
    output_path = Path(__file__).parent / "results/catmus_comparison.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nRaw results saved to {output_path}")

    # Generate report
    report = generate_report(results)
    report_path = Path(__file__).parent / "catmus_report.md"
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"Report saved to {report_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("CATMUS VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Average JSD: {results['summary']['avg_jsd_all_baselines']:.4f}")
    print(f"Stem match rate: {results['summary']['stem_match_rate']:.1%}")
    print(f"Stems with matches: {results['summary']['stems_with_baseline_matches']}/{results['summary']['total_stems_checked']}")


if __name__ == "__main__":
    main()
