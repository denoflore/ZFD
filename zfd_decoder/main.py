#!/usr/bin/env python3
"""
ZFD Folio Decode Pipeline
Usage: python main.py <folio_id> <eva_file> [--lexicon <path>]
"""

import argparse
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pipeline import ZFDPipeline
from output import generate_json, generate_csv, generate_markdown


def main():
    parser = argparse.ArgumentParser(
        description='ZFD Folio Decode Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Example: python main.py f88r input/f88r.txt'
    )
    parser.add_argument('folio', help='Folio ID (e.g., f88r)')
    parser.add_argument('eva_file', help='Path to EVA transcription file')
    parser.add_argument('--lexicon', '-l', help='Path to custom lexicon CSV file')

    args = parser.parse_args()

    folio = args.folio
    eva_file = args.eva_file

    # Read EVA text
    with open(eva_file, encoding='utf-8') as f:
        eva_text = f.read()

    # Initialize pipeline
    data_dir = Path(__file__).parent / "data"
    pipeline = ZFDPipeline(data_dir=str(data_dir), lexicon_file=args.lexicon)

    # Process folio
    print(f"Processing folio {folio}...")
    result = pipeline.process_folio(eva_text, folio)

    # Generate outputs
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    json_path = output_dir / f"{folio}_decode.json"
    csv_path = output_dir / f"{folio}_table.csv"
    md_path = output_dir / f"{folio}_report.md"

    generate_json(result, str(json_path))
    print(f"  → {json_path}")

    generate_csv(result, str(csv_path))
    print(f"  → {csv_path}")

    generate_markdown(result, str(md_path))
    print(f"  → {md_path}")

    # Print summary
    diag = result['diagnostics']
    print(f"\n=== SUMMARY ===")
    print(f"Tokens: {diag['total_tokens']}")
    print(f"Known stems: {diag['known_stems']} ({diag['known_ratio']:.1%})")
    print(f"Avg confidence: {diag['average_confidence']}")
    print(f"\nValidation:")
    for check, passed in diag['validation'].items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")


if __name__ == "__main__":
    main()
