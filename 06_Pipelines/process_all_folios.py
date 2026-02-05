#!/usr/bin/env python3
"""
ZFD Full Folio Pipeline v2.0
=============================
1. Downloads raw EVA text for all folios from GitHub
2. Decodes through unified lexicon
3. Generates recipe markdown files with:
   - Beinecke IIIF image links
   - Section identification
   - 4-layer interlinear (EVA > CRO > EXP > ENG)
   - Ingredient/method tables
   - Confidence scores
4. Generates summary statistics

Usage:
    python3 process_all_folios.py           # Process all
    python3 process_all_folios.py f88r      # Process single folio
    python3 process_all_folios.py --stats   # Show stats only
"""

import json
import os
import re
import sys
import subprocess
from pathlib import Path
from collections import defaultdict, Counter

# Import the decoder
sys.path.insert(0, str(Path(__file__).parent))
from zfd_decoder_v2 import ZFDDecoder

PIPELINE_DIR = Path("/home/claude/zfd/pipeline")
OUTPUT_DIR = Path("/home/claude/zfd/output/recipes")
EVA_DIR = Path("/home/claude/zfd/eva_source")
LEXICON_SOURCES = Path("/home/claude/zfd/lexicon_sources")

TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = "denoflore/ZFD"

# Section classification based on folio ranges
FOLIO_SECTIONS = {
    # Herbal A: f1r-f57v (single plant illustrations)
    "herbal_a": {"range": (1, 57), "label": "Herbal A", "description": "Single plant illustrations with text"},
    # Herbal B: f58r-f66v (larger plant illustrations) 
    "herbal_b": {"range": (58, 66), "label": "Herbal B", "description": "Larger plant illustrations, more text"},
    # Astronomical: f67r-f73v
    "astronomical": {"range": (67, 73), "label": "Astronomical", "description": "Circular diagrams, celestial imagery"},
    # Biological/Balneological: f75r-f86v
    "biological": {"range": (75, 86), "label": "Biological/Balneological", "description": "Human figures, pipes, vessels"},
    # Pharmaceutical: f87r-f90v + f93r-f96v + f99r-f116r
    "pharmaceutical": {"range": (87, 116), "label": "Pharmaceutical", "description": "Dense text, recipes, containers"},
}


def get_folio_section(folio_id):
    """Determine which manuscript section a folio belongs to"""
    # Extract number from folio_id like "f88r" -> 88
    m = re.match(r'f(\d+)', folio_id)
    if not m:
        return "unknown", "Unknown"
    num = int(m.group(1))
    
    for section_key, info in FOLIO_SECTIONS.items():
        lo, hi = info["range"]
        if lo <= num <= hi:
            return section_key, info["label"]
    
    return "unknown", "Unknown"


def load_iiif_map():
    """Load folio -> IIIF image ID mapping"""
    path = LEXICON_SOURCES / "folio_iiif_map.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def download_eva_files():
    """Download all raw EVA files from GitHub"""
    EVA_DIR.mkdir(parents=True, exist_ok=True)
    
    # List all files in voynich_data/raw_eva/
    cmd = f'curl -s -H "Authorization: token {TOKEN}" "https://api.github.com/repos/{REPO}/contents/voynich_data/raw_eva"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    files = json.loads(result.stdout)
    
    print(f"Downloading {len(files)} EVA source files...")
    
    count = 0
    for f in files:
        name = f["name"]
        outpath = EVA_DIR / name
        if outpath.exists() and outpath.stat().st_size > 10:
            count += 1
            continue
        
        dl_cmd = f'curl -s -H "Authorization: token {TOKEN}" -H "Accept: application/vnd.github.v3.raw" "https://api.github.com/repos/{REPO}/contents/voynich_data/raw_eva/{name}"'
        result = subprocess.run(dl_cmd, shell=True, capture_output=True, text=True)
        outpath.write_text(result.stdout)
        count += 1
    
    print(f"  {count} files ready in {EVA_DIR}")
    return sorted(EVA_DIR.glob("*.txt"))


def extract_ingredients(decoded_lines):
    """Extract ingredient table from decoded folio data"""
    stem_counts = Counter()
    stem_info = {}
    
    for line in decoded_lines:
        for word_data in line.get("words", []):
            if not word_data:
                continue
            stem = word_data.get("stem")
            if stem:
                form = stem["form"]
                stem_counts[form] += 1
                if form not in stem_info:
                    stem_info[form] = stem
    
    # Build table: only stems in ingredient/material categories
    ingredient_cats = {"liquid", "plant_part", "animal", "mineral", "herb", "resin", "spice", "botanical", "body"}
    ingredients = []
    for form, count in stem_counts.most_common():
        info = stem_info.get(form, {})
        cat = info.get("category", "")
        if cat in ingredient_cats or count >= 3:
            ingredients.append({
                "stem": form,
                "english": info.get("meaning_en", "?"),
                "latin": info.get("latin", ""),
                "category": cat,
                "count": count,
                "confidence": "CONFIRMED" if cat in ingredient_cats else "CANDIDATE",
            })
    
    return ingredients[:20]  # Top 20


def extract_methods(decoded_lines):
    """Extract preparation methods from decoded folio data"""
    op_counts = Counter()
    op_info = {}
    
    for line in decoded_lines:
        for word_data in line.get("words", []):
            if not word_data:
                continue
            op = word_data.get("operator")
            if op:
                form = op["form"]
                op_counts[form] += 1
                op_info[form] = op
    
    methods = []
    for form, count in op_counts.most_common():
        info = op_info.get(form, {})
        methods.append({
            "operator": form,
            "english": info.get("meaning", "?"),
            "count": count,
        })
    
    return methods[:15]


def extract_latin_terms(decoded_lines):
    """Extract detected Latin pharmaceutical terms"""
    latin_found = Counter()
    latin_info = {}
    
    for line in decoded_lines:
        for word_data in line.get("words", []):
            if not word_data:
                continue
            lat = word_data.get("latin_match")
            if lat:
                form = lat["form"]
                latin_found[form] += 1
                latin_info[form] = lat
    
    terms = []
    for form, count in latin_found.most_common():
        info = latin_info[form]
        terms.append({
            "form": form,
            "latin_full": info.get("latin_full", form),
            "english": info["meaning_en"],
            "count": count,
        })
    
    return terms


def generate_recipe_markdown(folio_id, decoded, iiif_map):
    """Generate the recipe markdown file for a folio"""
    section_key, section_label = get_folio_section(folio_id)
    lines = decoded["lines"]
    confidence = decoded["folio_confidence"]
    stats = decoded["stats"]
    
    # Get IIIF image ID (map keys don't have 'f' prefix)
    iiif_key = folio_id.lstrip('f')
    iiif_id = iiif_map.get(iiif_key, iiif_map.get(folio_id, ""))
    
    # Count words
    total_words = stats["total_words"]
    resolved = stats["fully_resolved"] + stats["partially_resolved"]
    
    # Extract tables
    ingredients = extract_ingredients(lines)
    methods = extract_methods(lines)
    latin_terms = extract_latin_terms(lines)
    
    # Build markdown
    md = []
    md.append(f"# {folio_id.upper()}: Recipe Extraction\n")
    
    # Image
    if iiif_id:
        md.append(f'<p align="center">')
        md.append(f'<a href="https://collections.library.yale.edu/iiif/2/{iiif_id}/full/full/0/default.jpg">')
        md.append(f'<img src="https://collections.library.yale.edu/iiif/2/{iiif_id}/full/600,/0/default.jpg" width="500" alt="Folio {folio_id} of the Voynich Manuscript (Beinecke MS 408)">')
        md.append(f'</a>')
        md.append(f'<br><sub>Folio {folio_id}. Beinecke MS 408. Click for full resolution. Image: Yale Beinecke Library (public domain).</sub>')
        md.append(f'</p>\n')
    
    # Metadata
    md.append(f"**Section:** {section_label}")
    md.append(f"**Confidence:** {confidence:.0%}")
    md.append(f"**Words:** {total_words} total, {resolved} resolved ({resolved/total_words:.0%})" if total_words > 0 else "**Words:** 0")
    md.append(f"**Decoder:** ZFD v2.0 (unified lexicon, 309 morphemes)")
    md.append(f"\n---\n")
    
    # Ingredients table
    if ingredients:
        md.append("## Ingredients Identified\n")
        md.append("| Stem | English | Latin | Category | Occurrences | Status |")
        md.append("|------|---------|-------|----------|-------------|--------|")
        for ing in ingredients:
            latin = f"*{ing['latin']}*" if ing['latin'] else ""
            md.append(f"| **{ing['stem']}** | {ing['english']} | {latin} | {ing['category']} | {ing['count']} | {ing['confidence']} |")
        md.append("")
    
    # Methods table
    if methods:
        md.append("## Preparation Methods\n")
        md.append("| Operator | English | Occurrences |")
        md.append("|----------|---------|-------------|")
        for meth in methods:
            md.append(f"| **{meth['operator']}-** | {meth['english']} | {meth['count']} |")
        md.append("")
    
    # Latin terms
    if latin_terms:
        md.append("## Latin Pharmaceutical Terms\n")
        for lt in latin_terms:
            md.append(f"- **{lt['form']}** -> *{lt['latin_full']}* ({lt['english']}) -- {lt['count']}x")
        md.append("")
    
    # Interlinear translation
    md.append("## Interlinear Translation\n")
    
    for i, line in enumerate(lines):
        md.append("```")
        md.append(f"EVA: {line['eva']}")
        md.append(f"CRO: {line['cro']}")
        md.append(f"EXP: {line['exp']}")
        md.append(f"ENG: {line['eng']}")
        md.append("```")
        # Confidence indicator
        conf = line["line_confidence"]
        if conf >= 0.7:
            bar = "█" * int(conf * 10) + "░" * (10 - int(conf * 10))
        elif conf >= 0.4:
            bar = "▓" * int(conf * 10) + "░" * (10 - int(conf * 10))
        else:
            bar = "░" * 10
        md.append(f"<sub>[{bar}] {conf:.0%} confidence</sub>\n")
    
    # Footer
    md.append("---\n")
    md.append(f"*Generated by ZFD Decoder v2.0 | Unified Lexicon (309 morphemes) | {folio_id}*")
    
    return "\n".join(md)


def process_single_folio(folio_id, decoder, iiif_map):
    """Process a single folio through the pipeline"""
    eva_path = EVA_DIR / f"{folio_id}.txt"
    if not eva_path.exists():
        return None, None
    
    eva_text = eva_path.read_text()
    if not eva_text.strip():
        return None, None
    
    decoder.reset_stats()
    decoded = decoder.decode_folio(eva_text, folio_id=folio_id)
    recipe_md = generate_recipe_markdown(folio_id, decoded, iiif_map)
    
    return decoded, recipe_md


def process_all_folios():
    """Process all folios through the pipeline"""
    print("=" * 70)
    print("ZFD FULL FOLIO PIPELINE v2.0")
    print("=" * 70)
    
    # Download EVA source files
    eva_files = download_eva_files()
    
    # Load IIIF map
    iiif_map = load_iiif_map()
    print(f"IIIF map: {len(iiif_map)} folio->image mappings")
    
    # Initialize decoder
    decoder = ZFDDecoder()
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Process each folio
    total_stats = {
        "folios_processed": 0,
        "total_words": 0,
        "fully_resolved": 0,
        "partially_resolved": 0,
        "unknown": 0,
        "latin_detected": 0,
        "section_counts": defaultdict(int),
        "section_confidence": defaultdict(list),
    }
    
    folio_results = {}
    
    for eva_file in eva_files:
        folio_id = eva_file.stem  # e.g., "f88r"
        
        decoded, recipe_md = process_single_folio(folio_id, decoder, iiif_map)
        if not decoded or not recipe_md:
            continue
        
        # Write recipe file
        outpath = OUTPUT_DIR / f"{folio_id}_recipe.md"
        outpath.write_text(recipe_md)
        
        # Track stats
        stats = decoded["stats"]
        section_key, section_label = get_folio_section(folio_id)
        
        total_stats["folios_processed"] += 1
        total_stats["total_words"] += stats["total_words"]
        total_stats["fully_resolved"] += stats["fully_resolved"]
        total_stats["partially_resolved"] += stats["partially_resolved"]
        total_stats["unknown"] += stats["unknown"]
        total_stats["latin_detected"] += stats["latin_detected"]
        total_stats["section_counts"][section_label] += 1
        total_stats["section_confidence"][section_label].append(decoded["folio_confidence"])
        
        folio_results[folio_id] = {
            "confidence": decoded["folio_confidence"],
            "words": stats["total_words"],
            "resolved": stats["fully_resolved"] + stats["partially_resolved"],
            "section": section_label,
        }
        
        # Progress
        if total_stats["folios_processed"] % 20 == 0:
            print(f"  Processed {total_stats['folios_processed']} folios...")
    
    # Print summary
    print(f"\n{'=' * 70}")
    print(f"PIPELINE COMPLETE")
    print(f"{'=' * 70}")
    print(f"  Folios processed:    {total_stats['folios_processed']}")
    print(f"  Total words:         {total_stats['total_words']:,}")
    print(f"  Fully resolved:      {total_stats['fully_resolved']:,} ({total_stats['fully_resolved']/max(total_stats['total_words'],1):.1%})")
    print(f"  Partially resolved:  {total_stats['partially_resolved']:,} ({total_stats['partially_resolved']/max(total_stats['total_words'],1):.1%})")
    print(f"  Unknown:             {total_stats['unknown']:,} ({total_stats['unknown']/max(total_stats['total_words'],1):.1%})")
    print(f"  Latin terms found:   {total_stats['latin_detected']:,}")
    
    print(f"\n  By Section:")
    for section, count in sorted(total_stats["section_counts"].items()):
        confs = total_stats["section_confidence"][section]
        avg_conf = sum(confs) / len(confs) if confs else 0
        print(f"    {section:30s}: {count:3d} folios, avg confidence {avg_conf:.0%}")
    
    # Write summary stats
    summary = {
        "pipeline_version": "2.0",
        "lexicon_version": "1.0.0 (309 morphemes)",
        "generated": "2026-02-05",
        "totals": {k: v for k, v in total_stats.items() if not isinstance(v, defaultdict)},
        "sections": {s: {"count": c, "avg_confidence": round(sum(total_stats["section_confidence"][s])/len(total_stats["section_confidence"][s]), 3)} 
                     for s, c in total_stats["section_counts"].items()},
        "folios": folio_results,
    }
    
    summary_path = OUTPUT_DIR / "PIPELINE_SUMMARY.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n  Summary: {summary_path}")
    
    return total_stats, folio_results


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] != "--stats":
        # Single folio mode
        folio_id = sys.argv[1]
        eva_files = download_eva_files()
        iiif_map = load_iiif_map()
        decoder = ZFDDecoder()
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        decoded, recipe_md = process_single_folio(folio_id, decoder, iiif_map)
        if recipe_md:
            outpath = OUTPUT_DIR / f"{folio_id}_recipe.md"
            outpath.write_text(recipe_md)
            print(f"Wrote {outpath}")
            print(f"Confidence: {decoded['folio_confidence']:.0%}")
            print(f"Stats: {decoded['stats']}")
        else:
            print(f"No EVA source found for {folio_id}")
    else:
        process_all_folios()
