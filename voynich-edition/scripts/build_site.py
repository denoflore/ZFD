#!/usr/bin/env python3
"""
Voynich Digital Edition - Static Site Generator
Phase 1: Generate HTML pages from JSON data.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
from html import escape

# Paths
SCRIPT_DIR = Path(__file__).parent
EDITION_ROOT = SCRIPT_DIR.parent
DATA_DIR = EDITION_ROOT / "data"
OUTPUT_DIR = EDITION_ROOT

# Internet Archive IIIF pattern
# Format: https://iiif.archive.org/image/iiif/3/voynich%24{page}/full/{size}/0/default.jpg
IA_IIIF_BASE = "https://iiif.archive.org/image/iiif/3/voynich%24"
IA_IIIF_SUFFIX = "/full/800,/0/default.jpg"

# Load data
def load_json(filename: str) -> Any:
    with open(DATA_DIR / filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def html_escape(text: str) -> str:
    """Safely escape HTML special characters."""
    return escape(str(text)) if text else ""


def get_folio_image_url(folio_id: str, page_mapping: Dict[str, int]) -> str:
    """Get the Internet Archive IIIF URL for a folio."""
    page_num = page_mapping.get(folio_id)
    if page_num:
        return f"{IA_IIIF_BASE}{page_num}{IA_IIIF_SUFFIX}"
    # Fallback to placeholder if no mapping
    return f"https://via.placeholder.com/600x800?text={folio_id.upper()}"


def get_confidence_class(confidence: int) -> str:
    """Return CSS class for confidence badge."""
    if confidence == 100:
        return "confidence-100"
    elif confidence >= 85:
        return "confidence-85"
    elif confidence >= 75:
        return "confidence-75"
    else:
        return "confidence-low"


def get_adjacent_folios(folio_id: str, all_folios: List[Dict]) -> tuple:
    """Find previous and next folios."""
    folio_ids = [f["folio_id"] for f in all_folios]
    try:
        idx = folio_ids.index(folio_id)
        prev_folio = folio_ids[idx - 1] if idx > 0 else None
        next_folio = folio_ids[idx + 1] if idx < len(folio_ids) - 1 else None
        return prev_folio, next_folio
    except ValueError:
        return None, None


def get_related_folios(folio_id: str, sop_graph: Dict, limit: int = 5) -> List[Dict]:
    """Get related folios from SOP graph."""
    related = []
    for edge in sop_graph.get("edges", []):
        if edge["source"] == folio_id:
            related.append({
                "folio_id": edge["target"],
                "shared": edge["shared_ingredients"],
                "type": "related"
            })
        elif edge["target"] == folio_id:
            related.append({
                "folio_id": edge["source"],
                "shared": edge["shared_ingredients"],
                "type": "related"
            })
        if len(related) >= limit:
            break
    return related


def render_interlinear_block(block: Dict) -> str:
    """Render an interlinear text block as HTML."""
    return f'''<div class="interlinear-block">
  <div class="line"><span class="label eva">EVA:</span> {html_escape(block.get("eva", ""))}</div>
  <div class="line"><span class="label cro">CRO:</span> {html_escape(block.get("croatian", ""))}</div>
  <div class="line"><span class="label exp">EXP:</span> {html_escape(block.get("expanded", ""))}</div>
  <div class="line"><span class="label eng">ENG:</span> {html_escape(block.get("english", ""))}</div>
</div>'''


def render_folio_page(folio: Dict, all_folios: List, sop_graph: Dict, section_data: Dict, page_mapping: Dict[str, int]) -> str:
    """Render a complete folio page."""
    folio_id = folio["folio_id"]
    section = folio.get("section", "Unknown")
    confidence = folio.get("confidence", 0)
    prev_folio, next_folio = get_adjacent_folios(folio_id, all_folios)
    related = get_related_folios(folio_id, sop_graph)

    # Build ingredients table
    ingredients_rows = ""
    for ing in folio.get("ingredients", []):
        stem = html_escape(ing.get("stem", ""))
        english = html_escape(ing.get("english", ""))
        latin = html_escape(ing.get("latin", ""))
        category = html_escape(ing.get("category", ""))
        occurrences = ing.get("occurrences", 0)
        status = html_escape(ing.get("status", ""))
        ingredients_rows += f'<tr><td><strong>{stem}</strong></td><td>{english}</td><td><em>{latin}</em></td><td>{category}</td><td class="num">{occurrences}</td><td><span class="tag tag-confirmed">{status}</span></td></tr>\n'

    # Build ingredients section HTML
    if ingredients_rows:
        ingredients_section = '''<table class="data-table">
        <thead><tr><th>Stem</th><th>English</th><th>Latin</th><th>Category</th><th>Count</th><th>Status</th></tr></thead>
        <tbody>''' + ingredients_rows + '</tbody></table>'
    else:
        ingredients_section = '<p class="text-muted">No ingredients identified.</p>'

    # Build methods table
    methods_rows = ""
    for method in folio.get("preparation_methods", []):
        stem = html_escape(method.get("stem", ""))
        english = html_escape(method.get("english", ""))
        category = html_escape(method.get("category", ""))
        occurrences = method.get("occurrences", 0)
        methods_rows += f'<tr><td><strong>{stem}</strong></td><td>{english}</td><td>{category}</td><td class="num">{occurrences}</td></tr>\n'

    # Build methods section HTML
    if methods_rows:
        methods_section = '''<table class="data-table">
        <thead><tr><th>Stem</th><th>English</th><th>Category</th><th>Count</th></tr></thead>
        <tbody>''' + methods_rows + '</tbody></table>'
    else:
        methods_section = '<p class="text-muted">No preparation methods identified.</p>'

    # Build interlinear blocks
    interlinear_html = ""
    for block in folio.get("interlinear_blocks", [])[:10]:  # Limit to first 10
        interlinear_html += render_interlinear_block(block)

    if not interlinear_html:
        interlinear_html = '<p class="text-muted">No interlinear data available for this folio.</p>'

    # Build related folios
    related_html = ""
    for rel in related:
        shared_str = ", ".join(rel["shared"][:3])
        rel_id = rel["folio_id"]
        related_html += f'<a href="{rel_id}.html" class="sop-link related">{rel_id.upper()} ({shared_str})</a>\n'

    if not related_html:
        related_html = '<span class="text-muted">No related folios found.</span>'

    # Latin terms
    latin_html = ""
    for lt in folio.get("latin_terms", []):
        term = html_escape(lt.get("term", ""))
        latin = html_escape(lt.get("latin", ""))
        meaning = html_escape(lt.get("meaning", ""))
        latin_html += f'<li><strong>{term}</strong> - <em>{latin}</em> ({meaning})</li>'

    # Latin section HTML
    if latin_html:
        latin_section = f'<section class="info-panel"><h3>Latin Pharmaceutical Terms</h3><ul>{latin_html}</ul></section>'
    else:
        latin_section = ''

    # Navigation
    prev_link = f'<a href="{prev_folio}.html">&larr; {prev_folio.upper()}</a>' if prev_folio else '<span></span>'
    next_link = f'<a href="{next_folio}.html">{next_folio.upper()} &rarr;</a>' if next_folio else '<span></span>'

    # Get IIIF image URL from Internet Archive
    image_url = get_folio_image_url(folio_id, page_mapping)

    # Pre-compute variables for template
    folio_upper = folio_id.upper()
    section_escaped = html_escape(section)
    section_anchor = section.lower().replace('/', '-')
    confidence_class = get_confidence_class(confidence)
    words_total = folio.get("words_total", "N/A")
    words_relevant = folio.get("words_recipe_relevant", "N/A")

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{folio_upper} - Voynich Digital Edition</title>
  <link rel="stylesheet" href="../css/edition.css">
</head>
<body>
  <header class="page-header">
    <div class="container">
      <nav class="breadcrumb">
        <a href="../index.html">Voynich Edition</a>
        <span>/</span>
        <a href="../index.html#{section_anchor}">{section_escaped}</a>
        <span>/</span>
        <span>{folio_upper}</span>
      </nav>
      <h1>{folio_upper}</h1>
      <p class="subtitle">{section_escaped} Section
        <span class="confidence-badge {confidence_class}">{confidence}% confidence</span>
      </p>
    </div>
  </header>

  <main class="container">
    <div class="folio-layout">
      <!-- Scan viewer -->
      <div class="scan-viewer">
        <img src="{image_url}" alt="Folio {folio_upper} scan" id="folio-image">
        <div class="viewer-controls">
          <button onclick="zoomIn()">Zoom +</button>
          <button onclick="zoomOut()">Zoom -</button>
          <button onclick="resetZoom()">Reset</button>
        </div>
      </div>

      <!-- Text content -->
      <div class="text-content">
        <section class="interlinear-section">
          <h2>Interlinear Decode</h2>
          <p class="text-muted">4-layer format: Voynichese (EVA) > Croatian > Expanded > English</p>
          {interlinear_html}
        </section>
      </div>
    </div>

    <!-- Ingredients -->
    <section class="info-panel">
      <h3>Ingredients Identified</h3>
      {ingredients_section}
    </section>

    <!-- Preparation Methods -->
    <section class="info-panel">
      <h3>Preparation Methods</h3>
      {methods_section}
    </section>

    {latin_section}

    <!-- SOP Chain -->
    <section class="info-panel">
      <h3>SOP Chain (Related Folios)</h3>
      <p class="text-muted mb-md">Folios sharing ingredients with {folio_upper}:</p>
      <div class="sop-chain">
        {related_html}
      </div>
    </section>

    <!-- Codicological Notes (placeholder) -->
    <section class="info-panel">
      <h3>Codicological Notes</h3>
      <dl>
        <dt>Section</dt>
        <dd>{section_escaped}</dd>
        <dt>Word Count</dt>
        <dd>{words_total} total, {words_relevant} recipe-relevant</dd>
        <dt>Confidence</dt>
        <dd>{confidence}%</dd>
      </dl>
    </section>

    <!-- Navigation -->
    <nav class="folio-nav">
      {prev_link}
      <a href="../index.html">All Folios</a>
      {next_link}
    </nav>
  </main>

  <footer class="page-footer">
    <div class="container">
      <p>Voynich Digital Edition - <a href="https://github.com/denoflore/ZFD">ZFD Project</a></p>
      <p class="text-muted">Based on the Zuger Functional Decipherment</p>
    </div>
  </footer>

  <script>
    let scale = 1;
    const img = document.getElementById('folio-image');
    const viewer = document.querySelector('.scan-viewer');

    // Image loading handling
    img.classList.add('loading');
    viewer.classList.add('loading');

    img.onload = function() {{
      img.classList.remove('loading');
      viewer.classList.remove('loading');
    }};

    img.onerror = function() {{
      img.classList.remove('loading');
      img.classList.add('error');
      viewer.classList.remove('loading');
      // Try placeholder as fallback
      if (!img.src.includes('placeholder')) {{
        img.src = 'https://via.placeholder.com/600x800?text={folio_upper}';
      }}
    }};

    function zoomIn() {{
      scale = Math.min(scale * 1.2, 4);
      img.style.transform = `scale(${{scale}})`;
    }}

    function zoomOut() {{
      scale = Math.max(scale / 1.2, 0.5);
      img.style.transform = `scale(${{scale}})`;
    }}

    function resetZoom() {{
      scale = 1;
      img.style.transform = 'scale(1)';
    }}
  </script>
</body>
</html>'''


def render_index_page(all_folios: List, section_data: Dict, ingredient_index: Dict) -> str:
    """Render the landing page."""

    # Group folios by section
    sections_html = ""
    section_groups = {}
    for folio in all_folios:
        sec = folio.get("section", "Unknown")
        if sec not in section_groups:
            section_groups[sec] = []
        section_groups[sec].append(folio)

    for section_name, folios in section_groups.items():
        folio_links = " ".join([
            f'<a href="folios/{f["folio_id"]}.html">{f["folio_id"].upper()}</a>'
            for f in folios[:20]
        ])
        more = f" (+{len(folios) - 20} more)" if len(folios) > 20 else ""

        sections_html += f'''<div class="section-card" id="{section_name.lower().replace('/', '-')}">
  <h3>{html_escape(section_name)}</h3>
  <div class="folio-count">{len(folios)}</div>
  <p>folios</p>
  <div class="folio-list">{folio_links}{more}</div>
</div>
'''

    # Top ingredients
    top_ingredients = ingredient_index.get("ingredients", [])[:10]
    ingredients_html = ""
    for ing in top_ingredients:
        ingredients_html += f'''<tr>
  <td><strong>{html_escape(ing.get("stem", ""))}</strong></td>
  <td>{html_escape(ing.get("english", ""))}</td>
  <td><em>{html_escape(ing.get("latin", ""))}</em></td>
  <td class="num">{ing.get("total_mentions", 0):,}</td>
</tr>'''

    # Statistics
    summary = ingredient_index.get("summary", {})

    # Build folio table rows
    folio_rows = ""
    for f in all_folios:
        fid = f["folio_id"]
        fsec = html_escape(f.get("section", ""))
        fconf = f.get("confidence", 0)
        fwords = f.get("words_total", 0)
        fings = ", ".join([i["stem"] for i in f.get("ingredients", [])[:4]])
        conf_class = get_confidence_class(fconf)
        folio_rows += f'''<tr class="folio-row" data-folio="{fid}" data-section="{fsec}">
            <td class="folio-id"><a href="folios/{fid}.html">{fid.upper()}</a></td>
            <td>{fsec}</td>
            <td><span class="confidence-badge {conf_class}">{fconf}%</span></td>
            <td class="num">{fwords}</td>
            <td>{fings}</td>
          </tr>'''

    # Summary stats
    folio_count = len(all_folios)
    ing_count = summary.get("unique_ingredients_identified", 13)
    mention_count = summary.get("total_ingredient_mentions", 0)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Voynich Digital Edition - ZFD</title>
  <link rel="stylesheet" href="css/edition.css">
</head>
<body>
  <header class="page-header">
    <div class="container">
      <h1>Voynich Digital Edition</h1>
      <p class="subtitle">The Zuger Functional Decipherment - An Annotated Pharmaceutical Manual</p>
    </div>
  </header>

  <main class="container">
    <!-- Introduction -->
    <section class="mb-lg">
      <h2>About This Edition</h2>
      <p>
        This digital edition presents the Voynich Manuscript as what the ZFD decipherment reveals it to be:
        a <strong>Ragusan pharmaceutical SOP manual</strong> from the 14th-15th century. Each folio is treated
        as a page in that manual, with interlinear translations, ingredient analysis, and cross-references
        to related preparations.
      </p>
      <p>
        <strong>{folio_count} folios</strong> | <strong>{ing_count} ingredients</strong> |
        <strong>{mention_count:,} mentions</strong>
      </p>
    </section>

    <!-- Search -->
    <section class="search-box">
      <input type="text" id="search" placeholder="Search folios, ingredients, or Croatian terms..." onkeyup="filterFolios()">
    </section>

    <!-- Sections -->
    <section class="mb-lg">
      <h2>Manuscript Sections</h2>
      <div class="section-grid">
        {sections_html}
      </div>
    </section>

    <!-- Top Ingredients -->
    <section class="info-panel">
      <h3>Top Ingredients Across All Folios</h3>
      <table class="data-table">
        <thead>
          <tr>
            <th>Stem</th>
            <th>English</th>
            <th>Latin</th>
            <th>Total Mentions</th>
          </tr>
        </thead>
        <tbody>
          {ingredients_html}
        </tbody>
      </table>
    </section>

    <!-- All Folios Table -->
    <section>
      <h2>All Folios</h2>
      <table class="data-table folio-list-table" id="folio-table">
        <thead>
          <tr>
            <th>Folio</th>
            <th>Section</th>
            <th>Confidence</th>
            <th>Words</th>
            <th>Top Ingredients</th>
          </tr>
        </thead>
        <tbody>
          {folio_rows}
        </tbody>
      </table>
    </section>
  </main>

  <footer class="page-footer">
    <div class="container">
      <p>Voynich Digital Edition - <a href="https://github.com/denoflore/ZFD">ZFD Project</a></p>
      <p class="text-muted">"No one fabricates 179 pages of bone poultice instructions for a prank."</p>
      <p class="text-muted">Based on the Zuger Functional Decipherment | CC BY-SA 4.0</p>
    </div>
  </footer>

  <script>
    function filterFolios() {{
      const query = document.getElementById('search').value.toLowerCase();
      const rows = document.querySelectorAll('.folio-row');

      rows.forEach(row => {{
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(query) ? '' : 'none';
      }});
    }}
  </script>
</body>
</html>'''


def main():
    """Build the static site."""
    print("=" * 60)
    print("Voynich Digital Edition - Static Site Generator")
    print("=" * 60)

    # Load data
    print("\nLoading data...")
    folio_data = load_json("folio_metadata.json")
    section_data = load_json("section_data.json")
    ingredient_index = load_json("ingredient_index.json")
    sop_graph = load_json("sop_graph.json")
    page_mapping_data = load_json("folio_page_mapping.json")
    page_mapping = page_mapping_data.get("folios", {})

    print(f"  Loaded {len(folio_data)} folios")
    print(f"  Loaded {len(page_mapping)} page mappings for IIIF")

    # Ensure output directories exist
    folios_dir = OUTPUT_DIR / "folios"
    folios_dir.mkdir(parents=True, exist_ok=True)

    # Generate index page
    print("\nGenerating index page...")
    index_html = render_index_page(folio_data, section_data, ingredient_index)
    with open(OUTPUT_DIR / "index.html", 'w', encoding='utf-8') as f:
        f.write(index_html)
    print(f"  Created: index.html")

    # Generate folio pages
    print("\nGenerating folio pages...")
    for i, folio in enumerate(folio_data):
        folio_html = render_folio_page(folio, folio_data, sop_graph, section_data, page_mapping)
        output_path = folios_dir / f"{folio['folio_id']}.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(folio_html)

        if (i + 1) % 50 == 0:
            print(f"  Generated {i + 1}/{len(folio_data)} pages...")

    print(f"  Created {len(folio_data)} folio pages")

    print("\n" + "=" * 60)
    print("Site Generation Complete!")
    print("=" * 60)
    print(f"  Index: {OUTPUT_DIR / 'index.html'}")
    print(f"  Folios: {folios_dir}")
    print(f"  Total pages: {len(folio_data) + 1}")


if __name__ == "__main__":
    main()
