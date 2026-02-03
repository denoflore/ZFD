#!/usr/bin/env python3
"""
IVTFF Parser - Phase 2 of Glagolitic OCR Pipeline

Parses the IVTFF consensus transcription file into structured per-folio,
per-line data with clean EVA tokens. Uses ;H (Takahashi) transcriptions
as primary source.

Output: data/ivtff_parsed.json
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict


class IVTFFParser:
    """Parser for IVTFF (Interlinear Voynich Transcript File Format)"""

    # Regex to match data lines: <folio.line,panel;transcriber>  text
    LINE_PATTERN = re.compile(
        r'^<(f\d+[rv]\d?)\.'        # folio id (f1r, f13v, f101r2, etc)
        r'(\d+[a-e]?),'             # line number (1, 2, 0a, etc)
        r'([^;]+);'                 # panel/unit info (@P0, +P0, etc)
        r'([A-Z])>\s*'              # transcriber code (H, C, F, etc)
        r'(.*)$'                    # text content
    )

    # Page header pattern
    PAGE_PATTERN = re.compile(r'^<(f\d+[rv]\d?)>\s+')

    def __init__(self, ivtff_path: str):
        self.ivtff_path = Path(ivtff_path)
        self.folios: Dict[str, dict] = {}
        self.stats = {
            'total_folios': 0,
            'total_lines': 0,
            'total_words': 0,
            'transcriber_counts': defaultdict(int)
        }

    def parse(self) -> Dict[str, dict]:
        """Parse the IVTFF file and return structured folio data."""
        print(f"Parsing IVTFF file: {self.ivtff_path}")

        with open(self.ivtff_path, 'r', encoding='utf-8', errors='replace') as f:
            for line_num, line in enumerate(f, 1):
                line = line.rstrip()

                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue

                # Try to match data line
                match = self.LINE_PATTERN.match(line)
                if match:
                    self._process_data_line(match, line_num)

        # Calculate statistics
        self._calculate_stats()

        return self.folios

    def _process_data_line(self, match: re.Match, source_line: int):
        """Process a matched IVTFF data line."""
        folio_id = match.group(1)
        line_num_str = match.group(2)
        panel = match.group(3)
        transcriber = match.group(4)
        raw_text = match.group(5)

        self.stats['transcriber_counts'][transcriber] += 1

        # Only process ;H (Takahashi) transcriptions as primary
        if transcriber != 'H':
            return

        # Initialize folio if needed
        if folio_id not in self.folios:
            self.folios[folio_id] = {
                'lines': [],
                'total_lines': 0,
                'total_words': 0
            }

        # Parse line number (handle 1, 2, 0a, 0b format)
        try:
            if line_num_str[-1].isalpha():
                line_num = int(line_num_str[:-1])
                line_suffix = line_num_str[-1]
            else:
                line_num = int(line_num_str)
                line_suffix = ''
        except ValueError:
            line_num = 0
            line_suffix = line_num_str

        # Parse the text content
        eva_raw, eva_words, uncertain, illegible = self._parse_text(raw_text)

        line_data = {
            'line_num': line_num,
            'line_num_str': line_num_str,
            'panel': panel.strip(),
            'eva_raw': eva_raw,
            'eva_words': eva_words,
            'uncertain_positions': uncertain,
            'illegible_positions': illegible,
            'has_continuation': '<->' in raw_text,
            'is_paragraph_end': '<$>' in raw_text,
            'source_line': source_line
        }

        self.folios[folio_id]['lines'].append(line_data)

    def _parse_text(self, raw_text: str) -> Tuple[str, List[str], List[int], List[int]]:
        """
        Parse raw IVTFF text and extract clean EVA tokens.

        Returns:
            eva_raw: Clean EVA string (markers removed)
            eva_words: List of EVA words
            uncertain: List of uncertain character positions
            illegible: List of illegible character positions
        """
        uncertain = []
        illegible = []

        # Remove inline comments <!...>
        text = re.sub(r'<![^>]*>', '', raw_text)

        # Remove continuation and paragraph markers
        text = text.replace('<->', '').replace('<$>', '')

        # Track uncertain (!) and illegible (*) positions before removing
        pos = 0
        for i, char in enumerate(text):
            if char == '!':
                uncertain.append(pos)
            elif char == '*':
                illegible.append(pos)
            elif char not in '.!* ':
                pos += 1

        # Remove uncertainty and illegibility markers for clean EVA
        text = text.replace('!', '').replace('*', '').replace('?', '')

        # Split on word boundaries (.)
        eva_raw = text.strip()

        # Split into words, filter empty
        words = [w.strip() for w in eva_raw.split('.') if w.strip()]

        # Clean EVA raw (join words with space for readability)
        eva_clean = ' '.join(words)

        return eva_clean, words, uncertain, illegible

    def _calculate_stats(self):
        """Calculate corpus statistics."""
        total_lines = 0
        total_words = 0

        for folio_id, folio_data in self.folios.items():
            folio_lines = len(folio_data['lines'])
            folio_words = sum(len(line['eva_words']) for line in folio_data['lines'])

            folio_data['total_lines'] = folio_lines
            folio_data['total_words'] = folio_words

            total_lines += folio_lines
            total_words += folio_words

        self.stats['total_folios'] = len(self.folios)
        self.stats['total_lines'] = total_lines
        self.stats['total_words'] = total_words

    def save_json(self, output_path: str):
        """Save parsed data to JSON file."""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        with open(output, 'w', encoding='utf-8') as f:
            json.dump(self.folios, f, indent=2, ensure_ascii=False)

        print(f"Saved parsed IVTFF to: {output}")

    def print_summary(self):
        """Print parsing summary."""
        print("\n" + "=" * 60)
        print("IVTFF PARSING SUMMARY")
        print("=" * 60)
        print(f"Total folios:  {self.stats['total_folios']}")
        print(f"Total lines:   {self.stats['total_lines']}")
        print(f"Total words:   {self.stats['total_words']}")
        print(f"\nTranscriber counts:")
        for transcriber, count in sorted(self.stats['transcriber_counts'].items()):
            print(f"  ;{transcriber}: {count} lines")

    def validate(self) -> bool:
        """Run validation checks."""
        print("\n" + "=" * 60)
        print("VALIDATION CHECKS")
        print("=" * 60)

        passed = True

        # Check f13v has exactly 10 lines
        if 'f13v' in self.folios:
            f13v_lines = len(self.folios['f13v']['lines'])
            status = "PASS" if f13v_lines == 10 else "FAIL"
            print(f"[{status}] f13v has {f13v_lines} lines (expected: 10)")
            if f13v_lines != 10:
                passed = False
        else:
            print("[FAIL] f13v not found in parsed data")
            passed = False

        # Check f1r line 1 starts with expected content
        if 'f1r' in self.folios and self.folios['f1r']['lines']:
            f1r_line1 = self.folios['f1r']['lines'][0]
            first_word = f1r_line1['eva_words'][0] if f1r_line1['eva_words'] else ''
            expected_start = 'fachys'
            status = "PASS" if first_word == expected_start else "FAIL"
            print(f"[{status}] f1r line 1 starts with '{first_word}' (expected: '{expected_start}')")
            if first_word != expected_start:
                passed = False
        else:
            print("[FAIL] f1r not found or has no lines")
            passed = False

        # Check for zero-line folios
        zero_line_folios = [fid for fid, fd in self.folios.items() if fd['total_lines'] == 0]
        if zero_line_folios:
            print(f"[FAIL] Found {len(zero_line_folios)} folios with 0 lines: {zero_line_folios[:5]}")
            passed = False
        else:
            print("[PASS] No zero-line folios")

        # Check for unreasonable word counts
        high_word_folios = [fid for fid, fd in self.folios.items() if fd['total_words'] > 500]
        if high_word_folios:
            print(f"[WARN] {len(high_word_folios)} folios have >500 words (may be normal for large folios)")

        # Verify reasonable total counts
        if self.stats['total_words'] < 1000:
            print(f"[FAIL] Total words ({self.stats['total_words']}) seems too low")
            passed = False
        else:
            print(f"[PASS] Total words ({self.stats['total_words']}) is reasonable")

        return passed


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Parse IVTFF transcription file')
    parser.add_argument('--input', '-i',
                        default='../../02_Transcriptions/LSI_ivtff_0d.txt',
                        help='Path to IVTFF file')
    parser.add_argument('--output', '-o',
                        default='data/ivtff_parsed.json',
                        help='Output JSON path')
    parser.add_argument('--validate', '-v', action='store_true',
                        help='Run validation checks')
    parser.add_argument('--sample', '-s', type=str,
                        help='Print sample folio data (e.g., f13v)')

    args = parser.parse_args()

    # Resolve paths relative to script location
    script_dir = Path(__file__).parent
    input_path = script_dir / args.input
    output_path = script_dir / args.output

    # Parse
    ivtff = IVTFFParser(input_path)
    ivtff.parse()
    ivtff.print_summary()

    # Save
    ivtff.save_json(output_path)

    # Validate
    if args.validate:
        ivtff.validate()

    # Print sample
    if args.sample and args.sample in ivtff.folios:
        print(f"\n{'=' * 60}")
        print(f"SAMPLE: {args.sample}")
        print('=' * 60)
        folio = ivtff.folios[args.sample]
        print(json.dumps(folio, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
