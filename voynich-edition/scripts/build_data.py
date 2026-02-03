#!/usr/bin/env python3
"""
Voynich Digital Edition - Data Pipeline
Phase 1: Transform ZFD repository data into structured JSON for the edition.

This script parses:
- Recipe files (201 folios) -> folio_metadata.json
- FOLIO_INDEX.md -> section_data.json
- RECIPE_INDEX.md -> ingredient_index.json
- Ingredient overlaps -> sop_graph.json
"""

import json
import re
import os
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any, Optional, Tuple

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent
RECIPES_DIR = REPO_ROOT / "translations" / "recipes"
FOLIO_INDEX = REPO_ROOT / "FOLIO_INDEX.md"
RECIPE_INDEX = REPO_ROOT / "translations" / "RECIPE_INDEX.md"
OUTPUT_DIR = Path(__file__).parent.parent / "data"
GLAGOLITIC_TRANSCRIPTIONS = REPO_ROOT / "06_Pipelines" / "glagolitic_ocr" / "transcriptions" / "json"

# Beinecke IIIF base URL pattern
# Yale's IIIF manifest for Voynich: https://collections.library.yale.edu/catalog/2002046
BEINECKE_IIIF_BASE = "https://collections.library.yale.edu/iiif/2"


def parse_recipe_file(filepath: Path) -> Optional[Dict[str, Any]]:
    """Parse a single recipe markdown file into structured data."""
    content = filepath.read_text(encoding='utf-8')

    # Extract folio ID from filename (e.g., f103r_recipe.md -> f103r)
    folio_id = filepath.stem.replace('_recipe', '')

    data = {
        "folio_id": folio_id,
        "section": None,
        "confidence": None,
        "words_total": None,
        "words_recipe_relevant": None,
        "ingredients": [],
        "preparation_methods": [],
        "latin_terms": [],
        "interlinear_blocks": []
    }

    # Parse header metadata
    section_match = re.search(r'\*\*Section:\*\*\s*(.+)', content)
    if section_match:
        data["section"] = section_match.group(1).strip()

    confidence_match = re.search(r'\*\*Confidence:\*\*\s*(\d+)%', content)
    if confidence_match:
        data["confidence"] = int(confidence_match.group(1))

    words_match = re.search(r'\*\*Words:\*\*\s*(\d+)\s*total,\s*(\d+)\s*recipe-relevant', content)
    if words_match:
        data["words_total"] = int(words_match.group(1))
        data["words_recipe_relevant"] = int(words_match.group(2))

    # Parse ingredients table
    ingredients_section = re.search(
        r'## Ingredients Identified\s*\n\s*\|[^\n]+\n\s*\|[-|\s]+\n((?:\|[^\n]+\n)*)',
        content
    )
    if ingredients_section:
        for row in ingredients_section.group(1).strip().split('\n'):
            cells = [c.strip() for c in row.split('|')[1:-1]]
            if len(cells) >= 6:
                stem = cells[0].replace('**', '').strip()
                data["ingredients"].append({
                    "stem": stem,
                    "english": cells[1].strip(),
                    "latin": cells[2].replace('*', '').strip(),
                    "category": cells[3].strip(),
                    "occurrences": int(cells[4].strip()) if cells[4].strip().isdigit() else 0,
                    "status": cells[5].strip()
                })

    # Parse preparation methods table
    methods_section = re.search(
        r'## Preparation Methods\s*\n\s*\|[^\n]+\n\s*\|[-|\s]+\n((?:\|[^\n]+\n)*)',
        content
    )
    if methods_section:
        for row in methods_section.group(1).strip().split('\n'):
            cells = [c.strip() for c in row.split('|')[1:-1]]
            if len(cells) >= 4:
                stem = cells[0].replace('**', '').strip()
                data["preparation_methods"].append({
                    "stem": stem,
                    "english": cells[1].strip(),
                    "category": cells[2].strip(),
                    "occurrences": int(cells[3].strip()) if cells[3].strip().isdigit() else 0
                })

    # Parse Latin pharmaceutical terms
    latin_section = re.search(
        r'## Latin Pharmaceutical Terms\s*\n((?:\s*-\s*\*\*[^\n]+\n)*)',
        content
    )
    if latin_section:
        for match in re.finditer(r'-\s*\*\*(\w+)\*\*\s*.*?\*(\w+)\*\s*\(([^)]+)\)', latin_section.group(1)):
            data["latin_terms"].append({
                "term": match.group(1),
                "latin": match.group(2),
                "meaning": match.group(3)
            })

    # Parse interlinear blocks
    interlinear_blocks = re.findall(
        r'```\s*\nEVA:\s*([^\n]+)\nCRO:\s*([^\n]+)\nEXP:\s*([^\n]+)\nENG:\s*([^\n]+)\n```',
        content
    )
    for eva, cro, exp, eng in interlinear_blocks:
        data["interlinear_blocks"].append({
            "eva": eva.strip(),
            "croatian": cro.strip(),
            "expanded": exp.strip(),
            "english": eng.strip()
        })

    return data


def parse_folio_index(filepath: Path) -> Dict[str, Any]:
    """Parse FOLIO_INDEX.md into structured section data."""
    content = filepath.read_text(encoding='utf-8')

    sections = []
    folios_by_section = defaultdict(list)

    # Parse section overview table
    overview_match = re.search(
        r'## Section Overview\s*\n\s*\|[^\n]+\n\s*\|[-|\s]+\n((?:\|[^\n]+\n)*)',
        content
    )
    if overview_match:
        for row in overview_match.group(1).strip().split('\n'):
            cells = [c.strip() for c in row.split('|')[1:-1]]
            if len(cells) >= 4:
                section_name = cells[0].replace('**', '').strip()
                sections.append({
                    "name": section_name,
                    "folios_range": cells[1].strip(),
                    "content_type": cells[2].strip(),
                    "dominant_morphemes": cells[3].strip()
                })

    # Parse individual section tables for folio details
    section_patterns = [
        (r'## Herbal Section A.*?\n((?:\|[^\n]+\n)+)', 'Herbal A'),
        (r'## Herbal Section B.*?\n((?:\|[^\n]+\n)+)', 'Herbal B'),
        (r'## Astronomical Section.*?\n((?:\|[^\n]+\n)+)', 'Astronomical'),
        (r'## Biological Section.*?\n((?:\|[^\n]+\n)+)', 'Biological'),
        (r'## Cosmological Section.*?\n((?:\|[^\n]+\n)+)', 'Cosmological'),
        (r'## Pharmaceutical Section.*?\n((?:\|[^\n]+\n)+)', 'Pharmaceutical'),
        (r'## Recipe/Stars Section.*?\n((?:\|[^\n]+\n)+)', 'Recipes/Stars'),
    ]

    for pattern, section_name in section_patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            for row in match.group(1).strip().split('\n'):
                if row.startswith('|') and 'Folio' not in row and '---' not in row:
                    cells = [c.strip() for c in row.split('|')[1:-1]]
                    if len(cells) >= 3 and cells[0].startswith('f'):
                        folio_id = cells[0].lower()
                        folios_by_section[section_name].append({
                            "folio_id": folio_id,
                            "lines": int(cells[1]) if cells[1].isdigit() else 0,
                            "top_words": cells[2] if len(cells) > 2 else "",
                            "section_type": cells[3] if len(cells) > 3 else section_name
                        })

    # Parse key statistics
    stats = {}
    stats_match = re.search(r'## Key Statistics\s*\n\s*\|[^\n]+\n\s*\|[-|\s]+\n((?:\|[^\n]+\n)*)', content)
    if stats_match:
        for row in stats_match.group(1).strip().split('\n'):
            cells = [c.strip() for c in row.split('|')[1:-1]]
            if len(cells) >= 2:
                key = cells[0].replace('**', '').strip().lower().replace(' ', '_')
                value = cells[1].strip()
                # Try to parse as int
                try:
                    value = int(re.search(r'\d+', value).group())
                except:
                    pass
                stats[key] = value

    return {
        "sections": sections,
        "folios_by_section": dict(folios_by_section),
        "statistics": stats
    }


def parse_recipe_index(filepath: Path) -> Dict[str, Any]:
    """Parse RECIPE_INDEX.md into ingredient index."""
    content = filepath.read_text(encoding='utf-8')

    data = {
        "summary": {},
        "ingredients": [],
        "preparation_methods": [],
        "latin_vocabulary": [],
        "ingredient_concordance": {}
    }

    # Parse summary statistics
    summary_section = re.search(r'## Summary Statistics\s*\n((?:-\s*\*\*[^\n]+\n)*)', content)
    if summary_section:
        for match in re.finditer(r'-\s*\*\*([^:]+):\*\*\s*(\d+)', summary_section.group(1)):
            key = match.group(1).strip().lower().replace(' ', '_')
            data["summary"][key] = int(match.group(2))

    # Parse top ingredients table
    ingredients_match = re.search(
        r'## Top 20 Ingredients.*?\n\s*\|[^\n]+\n\s*\|[-|\s]+\n((?:\|[^\n]+\n)*)',
        content
    )
    if ingredients_match:
        for row in ingredients_match.group(1).strip().split('\n'):
            cells = [c.strip() for c in row.split('|')[1:-1]]
            if len(cells) >= 5:
                data["ingredients"].append({
                    "rank": int(cells[0]) if cells[0].isdigit() else 0,
                    "stem": cells[1].replace('**', '').strip(),
                    "english": cells[2].strip(),
                    "latin": cells[3].replace('*', '').strip(),
                    "total_mentions": int(cells[4]) if cells[4].isdigit() else 0
                })

    # Parse preparation methods table
    methods_match = re.search(
        r'## Preparation Methods.*?\n\s*\|[^\n]+\n\s*\|[-|\s]+\n((?:\|[^\n]+\n)*)',
        content
    )
    if methods_match:
        for row in methods_match.group(1).strip().split('\n'):
            cells = [c.strip() for c in row.split('|')[1:-1]]
            if len(cells) >= 4:
                data["preparation_methods"].append({
                    "stem": cells[0].replace('**', '').strip(),
                    "english": cells[1].strip(),
                    "category": cells[2].strip(),
                    "total_mentions": int(cells[3]) if cells[3].isdigit() else 0
                })

    # Parse Latin vocabulary
    latin_match = re.search(
        r'## Latin Pharmaceutical Vocabulary\s*\n\s*\|[^\n]+\n\s*\|[-|\s]+\n((?:\|[^\n]+\n)*)',
        content
    )
    if latin_match:
        for row in latin_match.group(1).strip().split('\n'):
            cells = [c.strip() for c in row.split('|')[1:-1]]
            if len(cells) >= 5:
                data["latin_vocabulary"].append({
                    "term": cells[0].replace('**', '').strip(),
                    "latin": cells[1].replace('*', '').strip(),
                    "english": cells[2].strip(),
                    "category": cells[3].strip(),
                    "occurrences": int(cells[4]) if cells[4].isdigit() else 0
                })

    # Parse ingredient concordance
    concordance_match = re.search(r'## Ingredient Concordance\s*\n((?:\*\*[^\n]+\n)*)', content)
    if concordance_match:
        for match in re.finditer(r'\*\*(\w+)\*\*\s*\([^)]+\):\s*([^\n]+)', concordance_match.group(1)):
            stem = match.group(1)
            folios_str = match.group(2)
            # Extract folio IDs
            folios = [f.strip().lower() for f in re.findall(r'F\d+[RV]?', folios_str, re.IGNORECASE)]
            # Handle "...+N more"
            more_match = re.search(r'\+(\d+)\s*more', folios_str)
            more_count = int(more_match.group(1)) if more_match else 0
            data["ingredient_concordance"][stem] = {
                "folios_shown": folios,
                "additional_count": more_count
            }

    return data


def build_sop_graph(folio_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build the SOP dependency graph based on ingredient overlaps.

    This creates edges between folios that share ingredients,
    weighted by the number of shared ingredients and their frequencies.
    """
    graph = {
        "nodes": [],
        "edges": [],
        "ingredient_overlap_matrix": {}
    }

    # Build ingredient index per folio
    folio_ingredients = {}
    for folio in folio_data:
        fid = folio["folio_id"]
        ingredients = {ing["stem"]: ing["occurrences"] for ing in folio.get("ingredients", [])}
        folio_ingredients[fid] = ingredients

        # Add node
        graph["nodes"].append({
            "id": fid,
            "section": folio.get("section"),
            "confidence": folio.get("confidence"),
            "ingredient_count": len(ingredients),
            "total_ingredient_mentions": sum(ingredients.values())
        })

    # Calculate pairwise ingredient overlap
    folio_ids = list(folio_ingredients.keys())
    for i, fid1 in enumerate(folio_ids):
        for fid2 in folio_ids[i+1:]:
            ing1 = set(folio_ingredients[fid1].keys())
            ing2 = set(folio_ingredients[fid2].keys())
            shared = ing1 & ing2

            if shared:
                # Calculate overlap score (Jaccard + frequency weighting)
                jaccard = len(shared) / len(ing1 | ing2)
                freq1 = sum(folio_ingredients[fid1].get(ing, 0) for ing in shared)
                freq2 = sum(folio_ingredients[fid2].get(ing, 0) for ing in shared)

                graph["edges"].append({
                    "source": fid1,
                    "target": fid2,
                    "shared_ingredients": list(shared),
                    "overlap_count": len(shared),
                    "jaccard_similarity": round(jaccard, 3),
                    "frequency_score": freq1 + freq2
                })

    # Sort edges by overlap for easier processing
    graph["edges"].sort(key=lambda x: (-x["overlap_count"], -x["frequency_score"]))

    # Build section-level aggregation
    section_ingredients = defaultdict(lambda: defaultdict(int))
    for folio in folio_data:
        section = folio.get("section", "Unknown")
        for ing in folio.get("ingredients", []):
            section_ingredients[section][ing["stem"]] += ing["occurrences"]

    graph["section_ingredients"] = {
        section: dict(sorted(ings.items(), key=lambda x: -x[1])[:10])
        for section, ings in section_ingredients.items()
    }

    return graph


def load_glagolitic_transcription(folio_id: str) -> Optional[Dict[str, Any]]:
    """Load Glagolitic transcription JSON for a folio if available."""
    transcription_path = GLAGOLITIC_TRANSCRIPTIONS / f"{folio_id}.json"
    if transcription_path.exists():
        try:
            with open(transcription_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    return None


def get_beinecke_iiif_url(folio_id: str) -> str:
    """
    Generate Beinecke IIIF URL for a folio.

    Note: The actual manifest IDs need to be mapped from Yale's collection.
    This is a placeholder pattern that will need refinement.
    """
    # Yale Beinecke Voynich IIIF manifest is at:
    # https://collections.library.yale.edu/manifests/2002046.json
    # Individual images follow pattern in the manifest
    return f"{BEINECKE_IIIF_BASE}/beinecke:voynich_{folio_id}/full/1000,/0/default.jpg"


def main():
    """Run the complete data pipeline."""
    print("=" * 60)
    print("Voynich Digital Edition - Data Pipeline")
    print("=" * 60)

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Parse all recipe files
    print("\n[1/5] Parsing recipe files...")
    recipe_files = sorted(RECIPES_DIR.glob("*_recipe.md"))
    folio_data = []

    for rf in recipe_files:
        data = parse_recipe_file(rf)
        if data:
            folio_data.append(data)

    print(f"  Parsed {len(folio_data)} recipe files")

    # Add IIIF URLs and Glagolitic transcriptions to folio data
    glagolitic_count = 0
    for folio in folio_data:
        folio["iiif_url"] = get_beinecke_iiif_url(folio["folio_id"])

        # Load Glagolitic transcription if available
        glag_transcription = load_glagolitic_transcription(folio["folio_id"])
        if glag_transcription:
            folio["glagolitic_transcription"] = glag_transcription
            glagolitic_count += 1
        else:
            folio["glagolitic_transcription"] = None

    print(f"  Loaded {glagolitic_count} Glagolitic transcriptions")

    # Save folio metadata
    folio_output = OUTPUT_DIR / "folio_metadata.json"
    with open(folio_output, 'w', encoding='utf-8') as f:
        json.dump(folio_data, f, indent=2, ensure_ascii=False)
    print(f"  Saved: {folio_output}")

    # Step 2: Parse FOLIO_INDEX.md
    print("\n[2/5] Parsing FOLIO_INDEX.md...")
    section_data = parse_folio_index(FOLIO_INDEX)

    section_output = OUTPUT_DIR / "section_data.json"
    with open(section_output, 'w', encoding='utf-8') as f:
        json.dump(section_data, f, indent=2, ensure_ascii=False)
    print(f"  Saved: {section_output}")
    print(f"  Sections found: {len(section_data['sections'])}")

    # Step 3: Parse RECIPE_INDEX.md
    print("\n[3/5] Parsing RECIPE_INDEX.md...")
    ingredient_data = parse_recipe_index(RECIPE_INDEX)

    ingredient_output = OUTPUT_DIR / "ingredient_index.json"
    with open(ingredient_output, 'w', encoding='utf-8') as f:
        json.dump(ingredient_data, f, indent=2, ensure_ascii=False)
    print(f"  Saved: {ingredient_output}")
    print(f"  Ingredients indexed: {len(ingredient_data['ingredients'])}")

    # Step 4: Build SOP graph
    print("\n[4/5] Building SOP dependency graph...")
    sop_graph = build_sop_graph(folio_data)

    sop_output = OUTPUT_DIR / "sop_graph.json"
    with open(sop_output, 'w', encoding='utf-8') as f:
        json.dump(sop_graph, f, indent=2, ensure_ascii=False)
    print(f"  Saved: {sop_output}")
    print(f"  Nodes: {len(sop_graph['nodes'])}")
    print(f"  Edges: {len(sop_graph['edges'])}")

    # Step 5: Generate summary statistics
    print("\n[5/5] Generating summary...")

    summary = {
        "generated": "2026-02-03",
        "version": "1.0.0",
        "source": "ZFD Repository",
        "folio_count": len(folio_data),
        "sections": [s["name"] for s in section_data["sections"]],
        "total_ingredients": ingredient_data["summary"].get("unique_ingredients_identified", 0),
        "total_ingredient_mentions": ingredient_data["summary"].get("total_ingredient_mentions", 0),
        "total_preparation_methods": ingredient_data["summary"].get("unique_preparation_methods", 0),
        "sop_graph_edges": len(sop_graph["edges"]),
        "files_generated": [
            "folio_metadata.json",
            "section_data.json",
            "ingredient_index.json",
            "sop_graph.json"
        ]
    }

    summary_output = OUTPUT_DIR / "build_summary.json"
    with open(summary_output, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("Pipeline Complete!")
    print("=" * 60)
    print(f"  Folios processed: {len(folio_data)}")
    print(f"  Output directory: {OUTPUT_DIR}")
    print(f"  Files generated: {len(summary['files_generated']) + 1}")

    return summary


if __name__ == "__main__":
    main()
