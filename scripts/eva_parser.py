#!/usr/bin/env python3
"""
EVA Parser - Extracts per-folio text from IVTFF interlinear file
"""

import re
from pathlib import Path
from collections import defaultdict

def parse_ivtff(filepath):
    """
    Parse IVTFF format EVA transcription.
    Returns dict: {folio_id: {'labels': [...], 'text': [...]}}
    """
    folios = defaultdict(lambda: {'labels': [], 'text': [], 'raw_lines': []})

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        current_folio = None

        for line in f:
            line = line.rstrip()

            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue

            # Match folio markers: <f1r.1,@P0;H>
            match = re.match(r'^<(f\d+[rv]?\d*)\.?', line)
            if match:
                folio_id = match.group(1)
                # Normalize folio ID (f1r, f88r, etc.)
                folio_id = re.match(r'(f\d+[rv]?)', folio_id).group(1)
                current_folio = folio_id

                # Only use Takahashi (;H) or main transcription
                if ';H>' not in line and ';T>' not in line:
                    continue

                # Extract text after the marker
                if '>' in line:
                    text_part = line.split('>', 1)[1].strip()

                    # Check if this is a label line (@L) or text line (@P)
                    if '@L' in line:
                        folios[current_folio]['labels'].append(text_part)
                    else:
                        folios[current_folio]['text'].append(text_part)

                    folios[current_folio]['raw_lines'].append(line)

    return dict(folios)


def extract_words(text_lines):
    """Extract clean EVA words from text lines."""
    words = []
    for line in text_lines:
        # Remove markup like <!plant>, <$>, <->, etc.
        clean = re.sub(r'<[^>]+>', '', line)
        # Split on dots and whitespace
        for part in re.split(r'[.\s]+', clean):
            # Keep only EVA characters
            word = re.sub(r'[^a-z]', '', part.lower())
            if word and len(word) >= 2:
                words.append(word)
    return words


def save_folios(folios, output_dir):
    """Save each folio as separate file."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for folio_id, data in folios.items():
        filepath = output_dir / f"{folio_id}.txt"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"=== Folio {folio_id} ===\n\n")

            if data['labels']:
                f.write("[Labels]\n")
                for label in data['labels']:
                    f.write(f"{label}\n")
                f.write("\n")

            if data['text']:
                f.write("[Text]\n")
                for text in data['text']:
                    f.write(f"{text}\n")

    return len(folios)


def main():
    print("EVA Parser - Voynich Manuscript")
    print("=" * 50)

    # Parse the IVTFF file
    eva_file = Path('02_Transcriptions/LSI_ivtff_0d.txt')
    print(f"Parsing: {eva_file}")

    folios = parse_ivtff(eva_file)
    print(f"Found {len(folios)} folios")

    # Save individual folio files
    output_dir = Path('voynich_data/raw_eva')
    count = save_folios(folios, output_dir)
    print(f"Saved {count} folio files to {output_dir}")

    # Test extraction
    print("\n--- Test Extraction ---")
    for test_folio in ['f1r', 'f88r', 'f116v']:
        if test_folio in folios:
            data = folios[test_folio]
            words = extract_words(data['text'])
            print(f"{test_folio}: {len(data['labels'])} labels, {len(data['text'])} text lines, {len(words)} words")
        else:
            print(f"{test_folio}: NOT FOUND")

    # List all folios
    print(f"\nAll folios: {sorted(folios.keys())[:20]}... ({len(folios)} total)")

    return folios


if __name__ == "__main__":
    main()
