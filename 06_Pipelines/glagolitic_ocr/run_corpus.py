#!/usr/bin/env python3
"""
Full Corpus Transcription Run - Phase 4 of Glagolitic OCR Pipeline

Runs the transliteration engine across all parsed IVTFF folios and produces:
- Per-folio JSON transcriptions
- Per-folio Markdown transcriptions
- Corpus-wide statistics

Output directories:
- transcriptions/json/f{folio}.json
- transcriptions/md/f{folio}.md
"""

import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

from transliteration_engine import TransliterationEngine, TransliteratedWord


class CorpusRunner:
    """Orchestrates full corpus transliteration."""

    # IIIF URL patterns
    IA_IIIF_BASE = "https://iiif.archive.org/image/iiif/3/voynich%24"
    IA_IIIF_SUFFIX = "/full/800,/0/default.jpg"

    def __init__(self, data_dir: Path, output_dir: Path):
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.engine = TransliterationEngine()

        # Load parsed IVTFF data
        self.ivtff_data = self._load_json(data_dir / 'ivtff_parsed.json')

        # Load IIIF mapping
        iiif_map_path = data_dir / 'folio_iiif_map.json'
        if iiif_map_path.exists():
            iiif_data = self._load_json(iiif_map_path)
            self.iiif_map = iiif_data.get('folios', {})
        else:
            self.iiif_map = {}

        # Statistics
        self.stats = {
            'total_folios': 0,
            'total_lines': 0,
            'total_words': 0,
            'high_confidence': 0,
            'medium_confidence': 0,
            'low_confidence': 0,
            'unmapped_chars': set(),
            'per_folio': {}
        }

    def _load_json(self, path: Path) -> dict:
        """Load JSON file."""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _get_iiif_url(self, folio_id: str) -> str:
        """Get IIIF URL for a folio."""
        page_num = self.iiif_map.get(folio_id)
        if page_num:
            return f"{self.IA_IIIF_BASE}{page_num}{self.IA_IIIF_SUFFIX}"
        return f"https://via.placeholder.com/600x800?text={folio_id.upper()}"

    def process_folio(self, folio_id: str, folio_data: dict) -> dict:
        """Process a single folio through the transliteration engine."""
        result = self.engine.transliterate_folio(folio_data)

        # Add folio metadata
        result['folio'] = folio_id
        result['iiif_url'] = self._get_iiif_url(folio_id)

        # Update global statistics
        stats = result['statistics']
        self.stats['total_words'] += stats['total_words']
        self.stats['high_confidence'] += stats['high_confidence']
        self.stats['medium_confidence'] += stats['medium_confidence']
        self.stats['low_confidence'] += stats['low_confidence']
        self.stats['unmapped_chars'].update(stats['unmapped_chars'])

        # Store per-folio stats
        self.stats['per_folio'][folio_id] = {
            'total_words': stats['total_words'],
            'high_confidence': stats['high_confidence'],
            'medium_confidence': stats['medium_confidence'],
            'low_confidence': stats['low_confidence'],
            'avg_confidence': (
                sum(line['confidence_avg'] for line in result['lines']) /
                len(result['lines']) if result['lines'] else 0.0
            )
        }

        return result

    def save_json(self, folio_id: str, result: dict):
        """Save folio transcription as JSON."""
        output_path = self.output_dir / 'json' / f'{folio_id}.json'
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    def save_markdown(self, folio_id: str, result: dict):
        """Save folio transcription as Markdown."""
        output_path = self.output_dir / 'md' / f'{folio_id}.md'
        output_path.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            f"# Folio {folio_id.upper()} - Glagolitic Transcription",
            "",
            f"**IIIF:** [View scan]({result['iiif_url']})",
            "",
            f"**Statistics:** {result['statistics']['total_words']} words, "
            f"{result['statistics']['high_confidence']} high confidence, "
            f"{result['statistics']['medium_confidence']} medium, "
            f"{result['statistics']['low_confidence']} low",
            "",
        ]

        for line_data in result['lines']:
            line_num = line_data['line_num']
            layers = line_data['layers']

            lines.extend([
                f"## Line {line_num}",
                "",
                "| Layer | Text |",
                "|-------|------|",
                f"| EVA | {layers['eva']} |",
                f"| Glagolitic | {layers['glagolitic']} |",
                f"| Latin | {layers['latin']} |",
                f"| Croatian | {layers['croatian_short']} |",
                f"| English | {layers['croatian_expanded']} |",
                "",
            ])

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    def run(self) -> dict:
        """Run transliteration across all folios."""
        total = len(self.ivtff_data)
        print(f"Processing {total} folios...")

        for i, (folio_id, folio_data) in enumerate(self.ivtff_data.items(), 1):
            if i % 50 == 0 or i == total:
                print(f"  [{i}/{total}] Processing {folio_id}...")

            result = self.process_folio(folio_id, folio_data)

            # Save outputs
            self.save_json(folio_id, result)
            self.save_markdown(folio_id, result)

            self.stats['total_folios'] += 1
            self.stats['total_lines'] += len(result['lines'])

        # Convert set to list for JSON serialization
        self.stats['unmapped_chars'] = list(self.stats['unmapped_chars'])

        return self.stats


class CorpusStatistics:
    """Generate corpus-wide statistics."""

    def __init__(self, stats: dict, output_dir: Path):
        self.stats = stats
        self.output_dir = output_dir

    def save_json(self):
        """Save statistics as JSON."""
        output_path = self.output_dir / 'CORPUS_STATISTICS.json'

        # Calculate averages
        total_words = self.stats['total_words']
        if total_words > 0:
            avg_confidence = (
                self.stats['high_confidence'] * 0.9 +
                self.stats['medium_confidence'] * 0.65 +
                self.stats['low_confidence'] * 0.3
            ) / total_words
        else:
            avg_confidence = 0.0

        output = {
            'generated': datetime.now().isoformat(),
            'summary': {
                'total_folios': self.stats['total_folios'],
                'total_lines': self.stats['total_lines'],
                'total_words': total_words,
                'average_confidence': round(avg_confidence, 3),
            },
            'confidence_distribution': {
                'high': self.stats['high_confidence'],
                'medium': self.stats['medium_confidence'],
                'low': self.stats['low_confidence'],
            },
            'unmapped_characters': sorted(self.stats['unmapped_chars']),
            'per_folio': self.stats['per_folio']
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"Saved: {output_path}")

    def save_markdown(self):
        """Save statistics as Markdown."""
        output_path = self.output_dir / 'CORPUS_STATISTICS.md'

        total_words = self.stats['total_words']
        if total_words > 0:
            high_pct = self.stats['high_confidence'] / total_words * 100
            med_pct = self.stats['medium_confidence'] / total_words * 100
            low_pct = self.stats['low_confidence'] / total_words * 100
        else:
            high_pct = med_pct = low_pct = 0

        lines = [
            "# Glagolitic Transcription Corpus Statistics",
            "",
            f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
            "## Summary",
            "",
            f"- **Total folios:** {self.stats['total_folios']}",
            f"- **Total lines:** {self.stats['total_lines']}",
            f"- **Total words:** {total_words}",
            "",
            "## Confidence Distribution",
            "",
            f"- **High confidence (>80%):** {self.stats['high_confidence']} ({high_pct:.1f}%)",
            f"- **Medium confidence (50-80%):** {self.stats['medium_confidence']} ({med_pct:.1f}%)",
            f"- **Low confidence (<50%):** {self.stats['low_confidence']} ({low_pct:.1f}%)",
            "",
            "## Unmapped Characters",
            "",
        ]

        if self.stats['unmapped_chars']:
            lines.append(f"The following EVA characters could not be mapped: `{'`, `'.join(sorted(self.stats['unmapped_chars']))}`")
        else:
            lines.append("All characters were successfully mapped.")

        lines.extend([
            "",
            "## Per-Folio Breakdown",
            "",
            "| Folio | Words | High | Med | Low | Avg Conf |",
            "|-------|-------|------|-----|-----|----------|",
        ])

        # Sort folios naturally
        def sort_key(f):
            import re
            m = re.match(r'f(\d+)([rv])(\d*)', f)
            if m:
                return (int(m.group(1)), m.group(2), int(m.group(3) or 0))
            return (999, f, 0)

        for folio_id in sorted(self.stats['per_folio'].keys(), key=sort_key):
            fs = self.stats['per_folio'][folio_id]
            lines.append(
                f"| {folio_id} | {fs['total_words']} | {fs['high_confidence']} | "
                f"{fs['medium_confidence']} | {fs['low_confidence']} | "
                f"{fs['avg_confidence']:.2f} |"
            )

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"Saved: {output_path}")


def validate_output(output_dir: Path, stats: dict) -> bool:
    """Run validation checks on output."""
    print("\n" + "=" * 60)
    print("VALIDATION CHECKS")
    print("=" * 60)

    passed = True

    # Check JSON file count
    json_files = list((output_dir / 'json').glob('*.json'))
    expected = stats['total_folios']
    status = "PASS" if len(json_files) == expected else "FAIL"
    print(f"[{status}] JSON files: {len(json_files)} (expected: {expected})")
    if status == "FAIL":
        passed = False

    # Check MD file count
    md_files = list((output_dir / 'md').glob('*.md'))
    status = "PASS" if len(md_files) == expected else "FAIL"
    print(f"[{status}] Markdown files: {len(md_files)} (expected: {expected})")
    if status == "FAIL":
        passed = False

    # Check no zero-word folios
    zero_word = [f for f, s in stats['per_folio'].items() if s['total_words'] == 0]
    if zero_word:
        print(f"[FAIL] {len(zero_word)} folios have 0 words: {zero_word[:5]}")
        passed = False
    else:
        print("[PASS] No zero-word folios")

    # Check f13v output exists and has content
    f13v_path = output_dir / 'json' / 'f13v.json'
    if f13v_path.exists():
        with open(f13v_path, 'r') as f:
            f13v_data = json.load(f)
        if f13v_data.get('statistics', {}).get('total_words', 0) > 0:
            print("[PASS] f13v has transcription content")
        else:
            print("[FAIL] f13v has no words")
            passed = False
    else:
        print("[FAIL] f13v.json not found")
        passed = False

    # Check statistics files exist
    stats_json = output_dir / 'CORPUS_STATISTICS.json'
    stats_md = output_dir / 'CORPUS_STATISTICS.md'
    if stats_json.exists() and stats_md.exists():
        print("[PASS] Corpus statistics generated")
    else:
        print("[FAIL] Corpus statistics missing")
        passed = False

    return passed


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Run full corpus transliteration')
    parser.add_argument('--data-dir', '-d',
                        default='data',
                        help='Directory containing ivtff_parsed.json')
    parser.add_argument('--output-dir', '-o',
                        default='transcriptions',
                        help='Output directory for transcriptions')
    parser.add_argument('--validate', '-v', action='store_true',
                        help='Run validation checks')
    parser.add_argument('--sample', '-s', type=str,
                        help='Only process specified folio (for testing)')

    args = parser.parse_args()

    # Resolve paths relative to script location
    script_dir = Path(__file__).parent
    data_dir = script_dir / args.data_dir
    output_dir = script_dir / args.output_dir

    # Create output directories
    (output_dir / 'json').mkdir(parents=True, exist_ok=True)
    (output_dir / 'md').mkdir(parents=True, exist_ok=True)

    # Run corpus
    runner = CorpusRunner(data_dir, output_dir)

    if args.sample:
        # Process single folio for testing
        if args.sample in runner.ivtff_data:
            print(f"Processing sample folio: {args.sample}")
            result = runner.process_folio(args.sample, runner.ivtff_data[args.sample])
            runner.save_json(args.sample, result)
            runner.save_markdown(args.sample, result)
            runner.stats['total_folios'] = 1
            runner.stats['total_lines'] = len(result['lines'])
            print(f"Saved: {output_dir}/json/{args.sample}.json")
            print(f"Saved: {output_dir}/md/{args.sample}.md")
        else:
            print(f"Error: Folio {args.sample} not found in parsed data")
            return
    else:
        # Full corpus run
        stats = runner.run()

    # Generate statistics
    stats_gen = CorpusStatistics(runner.stats, output_dir)
    stats_gen.save_json()
    stats_gen.save_markdown()

    # Print summary
    print("\n" + "=" * 60)
    print("CORPUS TRANSCRIPTION SUMMARY")
    print("=" * 60)
    print(f"Folios processed: {runner.stats['total_folios']}")
    print(f"Total lines:      {runner.stats['total_lines']}")
    print(f"Total words:      {runner.stats['total_words']}")
    print(f"High confidence:  {runner.stats['high_confidence']}")
    print(f"Medium confidence:{runner.stats['medium_confidence']}")
    print(f"Low confidence:   {runner.stats['low_confidence']}")
    if runner.stats['unmapped_chars']:
        print(f"Unmapped chars:   {runner.stats['unmapped_chars']}")

    # Validate
    if args.validate:
        validate_output(output_dir, runner.stats)


if __name__ == '__main__':
    main()
