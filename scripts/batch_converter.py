#!/usr/bin/env python3
"""
Batch Converter - Process folios to Croatian orthography
"""

import re
from pathlib import Path
from zfd_mapper import map_line
from eva_parser import parse_ivtff, extract_words


def convert_folio_file(input_path, output_path):
    """
    Convert a single folio file from EVA to Croatian.
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse the file structure
    lines = content.split('\n')
    output_lines = []
    in_labels = False
    in_text = False

    for line in lines:
        if line.startswith('=== Folio'):
            output_lines.append(line)
        elif line == '[Labels]':
            output_lines.append(line)
            in_labels = True
            in_text = False
        elif line == '[Text]':
            output_lines.append(line)
            in_labels = False
            in_text = True
        elif line.strip() == '':
            output_lines.append(line)
        elif in_labels or in_text:
            # Convert EVA to Croatian
            croatian = map_line(line)
            output_lines.append(croatian)
        else:
            output_lines.append(line)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))


def process_section(section_name, start_folio, end_folio, input_dir, output_dir):
    """
    Process all folios in a section.
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get all folio files
    all_files = sorted(input_dir.glob('f*.txt'))

    # Filter to section range
    def folio_number(path):
        match = re.match(r'f(\d+)', path.stem)
        return int(match.group(1)) if match else 0

    def folio_in_range(path):
        num = folio_number(path)
        start_num = int(re.match(r'f(\d+)', start_folio).group(1))
        end_num = int(re.match(r'f(\d+)', end_folio).group(1))
        return start_num <= num <= end_num

    section_files = [f for f in all_files if folio_in_range(f)]

    print(f"\n{'=' * 60}")
    print(f"Processing: {section_name}")
    print(f"Range: {start_folio} to {end_folio}")
    print(f"Files found: {len(section_files)}")
    print('=' * 60)

    processed = 0
    for input_path in section_files:
        output_path = output_dir / input_path.name
        try:
            convert_folio_file(input_path, output_path)
            processed += 1
            if processed % 10 == 0:
                print(f"  Processed {processed} folios...")
        except Exception as e:
            print(f"  ERROR processing {input_path.name}: {e}")

    print(f"Completed: {processed} folios saved to {output_dir}")
    return processed


def process_all_sections():
    """
    Process all manuscript sections.
    """
    sections = [
        ('Herbal A', 'f1r', 'f66v'),
        ('Astronomical', 'f67r', 'f73v'),
        ('Biological', 'f75r', 'f84v'),
        ('Pharmaceutical', 'f87r', 'f102v'),
        ('Recipes', 'f103r', 'f116v'),
    ]

    input_dir = Path('voynich_data/raw_eva')
    output_base = Path('voynich_data/croatian')

    total = 0
    for section_name, start, end in sections:
        output_dir = output_base / section_name.lower().replace(' ', '_')
        count = process_section(section_name, start, end, input_dir, output_dir)
        total += count

    print(f"\n{'=' * 60}")
    print(f"TOTAL PROCESSED: {total} folios")
    print('=' * 60)

    return total


def spot_check(folio_ids):
    """
    Spot check specific folios.
    """
    print("\n" + "=" * 60)
    print("SPOT CHECK")
    print("=" * 60)

    for folio_id in folio_ids:
        # Find the folio in croatian output
        for cro_file in Path('voynich_data/croatian').rglob(f'{folio_id}.txt'):
            print(f"\n--- {folio_id} ---")
            with open(cro_file, 'r', encoding='utf-8') as f:
                content = f.read()
            # Show first 500 chars
            print(content[:500])
            if len(content) > 500:
                print("...")
            break
        else:
            print(f"\n--- {folio_id} ---")
            print("NOT FOUND")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--herbal':
        # Process just herbal section
        process_section(
            'Herbal A', 'f1r', 'f66v',
            'voynich_data/raw_eva',
            'voynich_data/croatian/herbal_a'
        )
        spot_check(['f1r', 'f25r', 'f50r'])
    else:
        # Process all sections
        process_all_sections()
        spot_check(['f1r', 'f88r', 'f103r'])
