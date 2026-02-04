#!/usr/bin/env python3
"""
Add Beinecke IIIF folio images to all recipe markdown files.

This script:
1. Loads the folio-to-IIIF-image-ID mapping from folio_iiif_map.json
2. For each recipe .md file in the translation directories
3. Extracts the folio ID from the filename (e.g., f88r_recipe.md -> 88r)
4. Inserts a centered image block after the title line, before the first **Section:** line
5. Skips files that already have images (idempotent)
"""

import json
import os
import re
import sys
from pathlib import Path


def load_folio_map(repo_root: Path) -> dict:
    """Load the folio-to-IIIF-image-ID mapping."""
    map_path = repo_root / "folio_iiif_map.json"
    with open(map_path, "r") as f:
        return json.load(f)


def extract_folio_id(filename: str) -> str | None:
    """Extract folio ID from filename like f88r_recipe.md -> 88r."""
    match = re.match(r"f(\d+[rv])_recipe\.md", filename, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def build_image_block(folio_id: str, image_id: str) -> str:
    """Build the centered image block with click-to-zoom."""
    base_url = "https://collections.library.yale.edu/iiif/2"
    preview_url = f"{base_url}/{image_id}/full/600,/0/default.jpg"
    full_url = f"{base_url}/{image_id}/full/full/0/default.jpg"

    # Format folio display (e.g., 88r -> Folio 88r)
    folio_display = f"Folio {folio_id}"

    return f'''
<p align="center">
<a href="{full_url}">
<img src="{preview_url}" width="500" alt="{folio_display} of the Voynich Manuscript (Beinecke MS 408)">
</a>
<br><sub>{folio_display}. Beinecke MS 408. Click for full resolution. Image: Yale Beinecke Library (public domain).</sub>
</p>
'''


def has_existing_image(content: str) -> bool:
    """Check if file already has an image tag near the top."""
    # Check first 1000 chars for an img tag
    top_content = content[:1000]
    return "<img" in top_content.lower()


def insert_image_after_title(content: str, image_block: str) -> str:
    """Insert image block after the title line (# F...) and before **Section:**."""
    lines = content.split('\n')

    # Find the title line (starts with # F)
    title_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith('# F') or line.strip().startswith('# f'):
            title_idx = i
            break

    if title_idx is None:
        # No title found, insert at beginning
        return image_block + '\n' + content

    # Insert after title line (with blank line)
    new_lines = lines[:title_idx + 1] + [image_block] + lines[title_idx + 1:]
    return '\n'.join(new_lines)


def process_file(filepath: Path, folio_map: dict, stats: dict) -> bool:
    """Process a single recipe file. Returns True if modified."""
    filename = filepath.name
    folio_id = extract_folio_id(filename)

    if folio_id is None:
        stats['skipped_no_folio_id'] += 1
        print(f"  SKIP (no folio ID): {filename}")
        return False

    if folio_id not in folio_map:
        stats['skipped_not_in_map'] += 1
        print(f"  SKIP (not in map): {filename} -> {folio_id}")
        return False

    image_id = folio_map[folio_id]

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if has_existing_image(content):
        stats['skipped_has_image'] += 1
        print(f"  SKIP (already has image): {filename}")
        return False

    image_block = build_image_block(folio_id, image_id)
    new_content = insert_image_after_title(content, image_block)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    stats['updated'] += 1
    print(f"  UPDATED: {filename} -> {image_id}")
    return True


def main():
    repo_root = Path(__file__).parent.parent

    print("Loading folio map...")
    folio_map = load_folio_map(repo_root)
    print(f"  Loaded {len(folio_map)} folio mappings")

    # Directories to process
    dirs_to_process = [
        repo_root / "translations" / "recipes",
        repo_root / "translations" / "biological",
        repo_root / "translations" / "herbal",
        repo_root / "translations" / "pharmaceutical",
    ]

    stats = {
        'total': 0,
        'updated': 0,
        'skipped_no_folio_id': 0,
        'skipped_not_in_map': 0,
        'skipped_has_image': 0,
    }

    for dir_path in dirs_to_process:
        if not dir_path.exists():
            print(f"Directory not found: {dir_path}")
            continue

        print(f"\nProcessing: {dir_path}")

        for filepath in sorted(dir_path.glob("*_recipe.md")):
            stats['total'] += 1
            process_file(filepath, folio_map, stats)

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Total files found:      {stats['total']}")
    print(f"Files updated:          {stats['updated']}")
    print(f"Skipped (no folio ID):  {stats['skipped_no_folio_id']}")
    print(f"Skipped (not in map):   {stats['skipped_not_in_map']}")
    print(f"Skipped (has image):    {stats['skipped_has_image']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
