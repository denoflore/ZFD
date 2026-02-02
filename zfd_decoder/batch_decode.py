#!/usr/bin/env python3
"""
Batch decode entire Voynich manuscript through ZFD pipeline.
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pipeline import ZFDPipeline
from output import generate_json, generate_csv, generate_markdown


def parse_eva_file(filepath: Path) -> str:
    """Parse EVA file and extract tokens."""
    with open(filepath, encoding='utf-8', errors='replace') as f:
        content = f.read()

    # Extract text section
    lines = []
    in_text = False
    for line in content.split('\n'):
        if '[Text]' in line:
            in_text = True
            continue
        if in_text and line.strip():
            # Clean the line: remove comments, line markers
            clean = line.strip()
            # Remove anything after # or !
            clean = re.sub(r'[#!].*', '', clean)
            # Replace dots with spaces (word separators)
            clean = clean.replace('.', ' ')
            # Remove special markers like <-> etc
            clean = re.sub(r'<[^>]+>', '', clean)
            # Remove remaining punctuation except letters
            clean = re.sub(r'[^a-zA-Z\s]', '', clean)
            if clean.strip():
                lines.append(clean.strip())

    return '\n'.join(lines)


def main():
    eva_dir = Path(__file__).parent.parent / "voynich_data" / "raw_eva"
    output_dir = Path(__file__).parent / "output" / "full_manuscript"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize pipeline
    data_dir = Path(__file__).parent / "data"
    pipeline = ZFDPipeline(data_dir=str(data_dir))

    # Collect all results
    all_results = []
    total_tokens = 0
    total_known = 0
    all_unknown_stems = set()

    eva_files = sorted(eva_dir.glob("*.txt"))
    print(f"Processing {len(eva_files)} folios...")
    print("=" * 60)

    for i, eva_file in enumerate(eva_files):
        folio = eva_file.stem

        try:
            # Parse EVA
            eva_text = parse_eva_file(eva_file)
            if not eva_text.strip():
                continue

            # Process through pipeline
            result = pipeline.process_folio(eva_text, folio)
            all_results.append(result)

            # Accumulate stats
            diag = result['diagnostics']
            total_tokens += diag['total_tokens']
            total_known += diag['known_stems']
            all_unknown_stems.update(diag['unknown_stem_list'])

            # Progress
            if (i + 1) % 20 == 0:
                print(f"  Processed {i + 1}/{len(eva_files)} folios...")

        except Exception as e:
            print(f"  Error on {folio}: {e}")
            continue

    print("=" * 60)
    print(f"Processed {len(all_results)} folios")
    print(f"Total tokens: {total_tokens}")
    print(f"Known stems: {total_known} ({100*total_known/total_tokens:.1f}%)")
    print(f"Unique unknown stems: {len(all_unknown_stems)}")

    # Generate master outputs
    master_result = {
        "generated": datetime.now().isoformat(),
        "total_folios": len(all_results),
        "total_tokens": total_tokens,
        "known_stems": total_known,
        "known_ratio": total_known / total_tokens if total_tokens > 0 else 0,
        "unknown_stem_count": len(all_unknown_stems),
        "unknown_stems": sorted(all_unknown_stems),
        "folios": all_results
    }

    # Write master JSON
    master_json = output_dir / "voynich_zfd_complete.json"
    with open(master_json, 'w', encoding='utf-8') as f:
        json.dump(master_result, f, indent=2, ensure_ascii=False)
    print(f"\n→ {master_json}")

    # Write master markdown summary
    master_md = output_dir / "voynich_zfd_summary.md"
    with open(master_md, 'w', encoding='utf-8') as f:
        f.write("# Voynich Manuscript ZFD Decode - Complete\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write("## Statistics\n\n")
        f.write(f"- **Total folios:** {len(all_results)}\n")
        f.write(f"- **Total tokens:** {total_tokens}\n")
        f.write(f"- **Known stems:** {total_known} ({100*total_known/total_tokens:.1f}%)\n")
        f.write(f"- **Unknown stems:** {len(all_unknown_stems)}\n\n")

        f.write("## Layer Samples (First 5 Folios)\n\n")
        for result in all_results[:5]:
            folio = result['folio']
            f.write(f"### {folio}\n\n")
            f.write("**EVA:**\n```\n")
            for line in result['lines'][:3]:
                f.write(" ".join(t['eva'] for t in line) + "\n")
            f.write("```\n\n")
            f.write("**ZFD:**\n```\n")
            for line in result['lines'][:3]:
                f.write(" ".join(t['zfd'] for t in line) + "\n")
            f.write("```\n\n")
            f.write("**English:**\n")
            for line in result['lines'][:3]:
                english = " ".join(t['english'] for t in line)
                f.write(f"> {english}\n")
            f.write("\n---\n\n")

        f.write("## Unknown Stems (for lexicon expansion)\n\n")
        f.write("```\n")
        f.write(", ".join(sorted(all_unknown_stems)[:100]))
        if len(all_unknown_stems) > 100:
            f.write(f"\n... and {len(all_unknown_stems) - 100} more")
        f.write("\n```\n")

    print(f"→ {master_md}")
    print("\nDone!")


if __name__ == "__main__":
    main()
