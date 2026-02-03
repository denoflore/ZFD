#!/usr/bin/env python3
"""
Voynich ZFD Recipe Extraction Pipeline
=======================================
Parses INTERLINEAR_QUADRILINGUAL.md and extracts all recipes,
instructions, preparations, and pharmaceutical content.

Generates:
  - Individual recipe files per folio
  - Master RECIPE_INDEX.md with summary statistics  
  - INGREDIENT_CONCORDANCE.md (every ingredient, every folio)
  - PREPARATION_METHODS.md (every process verb, organized)

/bacon - Cook it with love. Care is the anti-decay operator.
"""

import re
import json
from collections import defaultdict, Counter
from pathlib import Path

# =============================================================================
# LEXICON: From Herbal_Lexicon_v3_5_full.csv (the canonical vocabulary)
# =============================================================================

OPERATORS = {
    'qo': {'meaning': 'measure/quantify', 'latin': '—', 'status': 'CONFIRMED'},
    'ko': {'meaning': 'measure/quantify', 'latin': '—', 'status': 'CONFIRMED'},
    'ch': {'meaning': 'combine/cook', 'latin': 'coquere', 'status': 'CONFIRMED'},
    'h':  {'meaning': 'combine/cook', 'latin': 'coquere', 'status': 'CONFIRMED'},
    'sh': {'meaning': 'soak/infuse', 'latin': 'sorbere', 'status': 'CONFIRMED'},
    'š':  {'meaning': 'soak/infuse', 'latin': 'sorbere', 'status': 'CONFIRMED'},
    'da': {'meaning': 'dose/add/give', 'latin': 'dare', 'status': 'CONFIRMED'},
    'ok': {'meaning': 'vessel/container', 'latin': 'olla/calix', 'status': 'CONFIRMED'},
    'ot': {'meaning': 'vessel/container', 'latin': 'olla/calix', 'status': 'CONFIRMED'},
}

INGREDIENTS = {
    # Core materials - CONFIRMED
    'kost': {'english': 'bone', 'latin': 'os/ossis', 'category': 'animal', 'status': 'CONFIRMED'},
    'ol': {'english': 'oil', 'latin': 'oleum', 'category': 'liquid', 'status': 'CONFIRMED'},
    'or': {'english': 'oil', 'latin': 'oleum', 'category': 'liquid', 'status': 'CONFIRMED'},
    'ar': {'english': 'water', 'latin': 'aqua', 'category': 'liquid', 'status': 'CONFIRMED'},
    'sal': {'english': 'salt', 'latin': 'sal', 'category': 'mineral', 'status': 'CONFIRMED'},
    'sar': {'english': 'salt', 'latin': 'sal', 'category': 'mineral', 'status': 'CONFIRMED'},
    'mel': {'english': 'honey', 'latin': 'mel', 'category': 'liquid', 'status': 'CONFIRMED'},
    'vin': {'english': 'wine', 'latin': 'vinum', 'category': 'liquid', 'status': 'CONFIRMED'},
    'lac': {'english': 'milk', 'latin': 'lac', 'category': 'liquid', 'status': 'CONFIRMED'},
    'cera': {'english': 'wax', 'latin': 'cera', 'category': 'material', 'status': 'CONFIRMED'},
    'ova': {'english': 'egg', 'latin': 'ovum', 'category': 'animal', 'status': 'CONFIRMED'},
    
    # Plant stems - CONFIRMED
    'edy': {'english': 'root/prepared root', 'latin': 'radix', 'category': 'plant_part', 'status': 'CONFIRMED'},
    'rady': {'english': 'root', 'latin': 'radix', 'category': 'plant_part', 'status': 'CONFIRMED'},
    'flor': {'english': 'flower', 'latin': 'flos', 'category': 'plant_part', 'status': 'CONFIRMED'},
    'chol': {'english': 'flour/grain', 'latin': 'farina', 'category': 'plant_part', 'status': 'CONFIRMED'},
    
    # Named herbs & spices - CONFIRMED
    'ros': {'english': 'rose/rosewater', 'latin': 'rosa', 'category': 'herb', 'status': 'CONFIRMED'},
    'myr': {'english': 'myrrh', 'latin': 'myrrha', 'category': 'resin', 'status': 'CONFIRMED'},
    'aloe': {'english': 'aloe', 'latin': 'aloe', 'category': 'herb', 'status': 'CONFIRMED'},
    'galb': {'english': 'galbanum', 'latin': 'galbanum', 'category': 'resin', 'status': 'CONFIRMED'},
    'stor': {'english': 'storax', 'latin': 'storax', 'category': 'resin', 'status': 'CONFIRMED'},
    'opop': {'english': 'opopanax', 'latin': 'opopanax', 'category': 'resin', 'status': 'CONFIRMED'},
    'camph': {'english': 'camphor', 'latin': 'camphora', 'category': 'herb', 'status': 'CONFIRMED'},
    'anis': {'english': 'anise', 'latin': 'anisum', 'category': 'spice', 'status': 'CONFIRMED'},
    'cori': {'english': 'coriander', 'latin': 'coriandrum', 'category': 'spice', 'status': 'CONFIRMED'},
    'ment': {'english': 'mint', 'latin': 'mentha', 'category': 'herb', 'status': 'CONFIRMED'},
    'salv': {'english': 'sage', 'latin': 'salvia', 'category': 'herb', 'status': 'CONFIRMED'},
    'fenn': {'english': 'fennel', 'latin': 'feniculum', 'category': 'herb', 'status': 'CONFIRMED'},
    'ruta': {'english': 'rue', 'latin': 'ruta', 'category': 'herb', 'status': 'CONFIRMED'},
    'hyss': {'english': 'hyssop', 'latin': 'hyssopus', 'category': 'herb', 'status': 'CONFIRMED'},
    'malv': {'english': 'mallow', 'latin': 'malva', 'category': 'herb', 'status': 'CONFIRMED'},
    'genist': {'english': 'broom', 'latin': 'genista', 'category': 'herb', 'status': 'CONFIRMED'},
    'verb': {'english': 'vervain', 'latin': 'verbena', 'category': 'herb', 'status': 'CONFIRMED'},
    'plant': {'english': 'plantain', 'latin': 'plantago', 'category': 'herb', 'status': 'CONFIRMED'},
    'canel': {'english': 'cinnamon', 'latin': 'cannella', 'category': 'spice', 'status': 'CONFIRMED'},
    'zing': {'english': 'ginger', 'latin': 'zingiber', 'category': 'spice', 'status': 'CONFIRMED'},
    'piper': {'english': 'pepper', 'latin': 'piper', 'category': 'spice', 'status': 'CONFIRMED'},
    'nard': {'english': 'spikenard', 'latin': 'nardus', 'category': 'herb', 'status': 'CONFIRMED'},
    'croc': {'english': 'saffron', 'latin': 'crocus', 'category': 'spice', 'status': 'CONFIRMED'},
    'cost': {'english': 'costus root', 'latin': 'costus', 'category': 'herb', 'status': 'CONFIRMED'},
    'galg': {'english': 'galangal', 'latin': 'galanga', 'category': 'spice', 'status': 'CONFIRMED'},
    'scam': {'english': 'scammony', 'latin': 'scammonium', 'category': 'herb', 'status': 'CONFIRMED'},
    'licor': {'english': 'licorice', 'latin': 'liquiritia', 'category': 'herb', 'status': 'CANDIDATE'},
    
    # Minerals & metals - CONFIRMED
    'sul': {'english': 'sulfur', 'latin': 'sulphur', 'category': 'mineral', 'status': 'CONFIRMED'},
    'arg': {'english': 'silver', 'latin': 'argentum', 'category': 'metal', 'status': 'CONFIRMED'},
    'cupr': {'english': 'copper/verdigris', 'latin': 'cuprum', 'category': 'metal', 'status': 'CONFIRMED'},
    'fer': {'english': 'iron', 'latin': 'ferrum', 'category': 'metal', 'status': 'CONFIRMED'},
    'salp': {'english': 'saltpeter', 'latin': 'sal petrae', 'category': 'mineral', 'status': 'CONFIRMED'},
    'alum': {'english': 'alum', 'latin': 'alumen', 'category': 'mineral', 'status': 'CONFIRMED'},
    'lapis': {'english': 'lapis/stone', 'latin': 'lapis', 'category': 'mineral', 'status': 'CONFIRMED'},
    
    # Animal products - CONFIRMED
    'axun': {'english': 'lard/fat', 'latin': 'axungia', 'category': 'animal', 'status': 'CONFIRMED'},
    'case': {'english': 'cheese/curd', 'latin': 'caseus', 'category': 'animal', 'status': 'CONFIRMED'},
    'musc': {'english': 'musk', 'latin': 'muscus', 'category': 'animal', 'status': 'CONFIRMED'},
    'ambra': {'english': 'ambergris', 'latin': 'ambra', 'category': 'animal', 'status': 'CONFIRMED'},
    'perla': {'english': 'pearl', 'latin': 'perla', 'category': 'mineral', 'status': 'CONFIRMED'},
    'coral': {'english': 'coral', 'latin': 'corallium', 'category': 'mineral', 'status': 'CONFIRMED'},
    'ivor': {'english': 'ivory', 'latin': 'ebur', 'category': 'animal', 'status': 'CONFIRMED'},
    
    # Dosage forms - CONFIRMED
    'ung': {'english': 'ointment/salve', 'latin': 'unguentum', 'category': 'form', 'status': 'CONFIRMED'},
}

PROCESSES = {
    'hor': {'english': 'process/work', 'category': 'general'},
    'hol': {'english': 'combine', 'category': 'mixing'},
    'hedi': {'english': 'cook/prepare', 'category': 'heat'},
    'šedi': {'english': 'soak/infuse', 'category': 'liquid'},
    'šol': {'english': 'soak in oil', 'category': 'liquid'},
    'šor': {'english': 'strain/soak', 'category': 'liquid'},
    'dar': {'english': 'dose/give', 'category': 'dosing'},
    'dain': {'english': 'dose/portion', 'category': 'dosing'},
    'dal': {'english': 'then/next', 'category': 'sequence'},
    'kal': {'english': 'cauldron/heat vessel', 'category': 'equipment'},
    'thor': {'english': 'boil/roast', 'category': 'heat'},
    'chor': {'english': 'cook/combine', 'category': 'heat'},
    'shor': {'english': 'soak/infuse', 'category': 'liquid'},
}

LATIN_TERMS = {
    'oral': {'latin': 'oralis', 'english': 'by mouth', 'category': 'administration'},
    'orolaly': {'latin': 'oraliter', 'english': 'orally', 'category': 'administration'},
    'dolor': {'latin': 'dolor', 'english': 'pain', 'category': 'condition'},
    'ana': {'latin': 'ana', 'english': 'equal parts', 'category': 'measurement'},
}

# Folio section classifications
SECTIONS = {
    'herbal_a': {'range': 'f1r-f57v', 'type': 'Herbal', 'description': 'Plant illustrations with preparation instructions'},
    'herbal_b': {'range': 'f65r-f73v', 'type': 'Herbal', 'description': 'Additional plant illustrations'},
    'astronomical': {'range': 'f67r-f73v', 'type': 'Astronomical', 'description': 'Circular diagrams'},
    'biological': {'range': 'f75r-f84v', 'type': 'Biological', 'description': 'Baths, pipes, body preparations'},
    'cosmological': {'range': 'f85r-f86v', 'type': 'Cosmological', 'description': 'Fold-out diagrams'},
    'pharmaceutical': {'range': 'f87r-f102v', 'type': 'Pharmaceutical', 'description': 'Dense recipe text'},
    'recipes_stars': {'range': 'f103r-f116v', 'type': 'Recipes/Stars', 'description': 'Text with star markers'},
}


def folio_number(folio_id):
    """Extract numeric part for sorting: f88r -> 88"""
    m = re.search(r'(\d+)', folio_id)
    return int(m.group(1)) if m else 0


def classify_folio(folio_id):
    """Classify a folio into its manuscript section"""
    num = folio_number(folio_id)
    if num <= 57: return 'Herbal A'
    if 58 <= num <= 64: return 'Herbal A (cont.)'
    if 65 <= num <= 73: return 'Herbal B / Astronomical'
    if 75 <= num <= 84: return 'Biological'
    if 85 <= num <= 86: return 'Cosmological'
    if 87 <= num <= 102: return 'Pharmaceutical'
    if 103 <= num <= 116: return 'Recipes/Stars'
    return 'Other'


def parse_quadrilingual(filepath):
    """Parse INTERLINEAR_QUADRILINGUAL.md into structured folio data"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by folio headers
    folio_pattern = re.compile(r'^## (F\d+[RV])\s*$', re.MULTILINE | re.IGNORECASE)
    splits = folio_pattern.split(content)
    
    folios = {}
    i = 1
    while i < len(splits) - 1:
        folio_id = splits[i].strip().lower()
        folio_content = splits[i + 1]
        
        # Parse labels and text
        labels = []
        text_lines = []
        
        # Extract label blocks
        label_section = re.search(r'\*\*Labels:\*\*(.+?)(?:\*\*Text:\*\*|\Z)', folio_content, re.DOTALL)
        if label_section:
            label_blocks = re.findall(r'```\n(.+?)\n```', label_section.group(1), re.DOTALL)
            for block in label_blocks:
                label_data = {}
                for line in block.strip().split('\n'):
                    if ':' in line:
                        key, val = line.split(':', 1)
                        label_data[key.strip()] = val.strip()
                if label_data:
                    labels.append(label_data)
        
        # Extract text blocks
        text_section = re.search(r'\*\*Text:\*\*(.+?)(?:\*\*Labels:\*\*|\Z)', folio_content, re.DOTALL)
        if text_section:
            text_blocks = re.findall(r'```\n(.+?)\n```', text_section.group(1), re.DOTALL)
            for block in text_blocks:
                line_data = {}
                for line in block.strip().split('\n'):
                    if ':' in line:
                        key, val = line.split(':', 1)
                        line_data[key.strip()] = val.strip()
                if line_data:
                    text_lines.append(line_data)
        
        folios[folio_id] = {
            'id': folio_id,
            'section': classify_folio(folio_id),
            'labels': labels,
            'text': text_lines,
            'raw': folio_content
        }
        
        i += 2
    
    return folios


def analyze_folio(folio_data):
    """Analyze a folio for recipe content"""
    analysis = {
        'ingredients_found': defaultdict(int),
        'processes_found': defaultdict(int),
        'latin_terms_found': defaultdict(int),
        'operators_found': defaultdict(int),
        'ingredient_details': [],
        'process_details': [],
        'has_recipe_content': False,
        'recipe_confidence': 0.0,
        'word_count': 0,
        'parsed_words': 0,
    }
    
    # Collect all text: from labels and running text
    all_text = []
    
    for label in folio_data.get('labels', []):
        for key in ['CRO', 'EXP', 'ENG']:
            if key in label:
                all_text.append(label[key].lower())
    
    for text_line in folio_data.get('text', []):
        for key in ['CRO', 'EXP', 'ENG']:
            if key in text_line:
                all_text.append(text_line[key].lower())
    
    combined = ' '.join(all_text)
    words = re.findall(r'[a-zšžćčđ]+', combined)
    analysis['word_count'] = len(words)
    
    # Scan for ingredients
    for word in words:
        for stem, info in INGREDIENTS.items():
            if stem in word:
                analysis['ingredients_found'][stem] += 1
                if stem not in [d['stem'] for d in analysis['ingredient_details']]:
                    analysis['ingredient_details'].append({
                        'stem': stem,
                        'english': info['english'],
                        'latin': info['latin'],
                        'category': info['category'],
                        'status': info['status'],
                    })
    
    # Scan for processes
    for word in words:
        for proc, info in PROCESSES.items():
            if proc in word:
                analysis['processes_found'][proc] += 1
                if proc not in [d['stem'] for d in analysis['process_details']]:
                    analysis['process_details'].append({
                        'stem': proc,
                        'english': info['english'],
                        'category': info['category'],
                    })
    
    # Scan for Latin terms
    for word in words:
        for term, info in LATIN_TERMS.items():
            if term == word or (term in word and len(word) <= len(term) + 3):
                analysis['latin_terms_found'][term] += 1
    
    # Scan for operators
    for word in words:
        for op, info in OPERATORS.items():
            if word.startswith(op):
                analysis['operators_found'][op] += 1
    
    # Compute recipe confidence
    score = 0
    if analysis['ingredients_found']: score += min(len(analysis['ingredients_found']) * 10, 40)
    if analysis['processes_found']: score += min(len(analysis['processes_found']) * 10, 30)
    if analysis['latin_terms_found']: score += 15
    if analysis['operators_found']: score += min(len(analysis['operators_found']) * 5, 15)
    
    analysis['recipe_confidence'] = min(score, 100) / 100.0
    analysis['has_recipe_content'] = analysis['recipe_confidence'] >= 0.20
    analysis['parsed_words'] = sum(analysis['ingredients_found'].values()) + \
                                sum(analysis['processes_found'].values()) + \
                                sum(analysis['latin_terms_found'].values())
    
    return analysis


def generate_recipe_md(folio_data, analysis):
    """Generate a structured recipe markdown file for a folio"""
    fid = folio_data['id'].upper()
    section = folio_data['section']
    conf = analysis['recipe_confidence']
    
    lines = []
    lines.append(f"# {fid}: Recipe Extraction")
    lines.append(f"")
    lines.append(f"**Section:** {section}")
    lines.append(f"**Confidence:** {conf:.0%}")
    lines.append(f"**Words:** {analysis['word_count']} total, {analysis['parsed_words']} recipe-relevant")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")
    
    # Ingredients table
    if analysis['ingredient_details']:
        lines.append(f"## Ingredients Identified")
        lines.append(f"")
        lines.append(f"| Stem | English | Latin | Category | Occurrences | Status |")
        lines.append(f"|------|---------|-------|----------|-------------|--------|")
        for ing in sorted(analysis['ingredient_details'], key=lambda x: analysis['ingredients_found'].get(x['stem'], 0), reverse=True):
            count = analysis['ingredients_found'].get(ing['stem'], 0)
            lines.append(f"| **{ing['stem']}** | {ing['english']} | *{ing['latin']}* | {ing['category']} | {count} | {ing['status']} |")
        lines.append(f"")
    
    # Processes table
    if analysis['process_details']:
        lines.append(f"## Preparation Methods")
        lines.append(f"")
        lines.append(f"| Stem | English | Category | Occurrences |")
        lines.append(f"|------|---------|----------|-------------|")
        for proc in sorted(analysis['process_details'], key=lambda x: analysis['processes_found'].get(x['stem'], 0), reverse=True):
            count = analysis['processes_found'].get(proc['stem'], 0)
            lines.append(f"| **{proc['stem']}** | {proc['english']} | {proc['category']} | {count} |")
        lines.append(f"")
    
    # Latin terms
    if analysis['latin_terms_found']:
        lines.append(f"## Latin Pharmaceutical Terms")
        lines.append(f"")
        for term, count in analysis['latin_terms_found'].items():
            info = LATIN_TERMS[term]
            lines.append(f"- **{term}** → *{info['latin']}* ({info['english']}) — {count}× [{info['category']}]")
        lines.append(f"")
    
    # Raw interlinear (labels)
    if folio_data.get('labels'):
        lines.append(f"## Labels (Interlinear)")
        lines.append(f"")
        for label in folio_data['labels']:
            lines.append(f"```")
            for key in ['EVA', 'CRO', 'EXP', 'ENG']:
                if key in label:
                    lines.append(f"{key}: {label[key]}")
            lines.append(f"```")
            lines.append(f"")
    
    # Raw interlinear (text)
    if folio_data.get('text'):
        lines.append(f"## Running Text (Interlinear)")
        lines.append(f"")
        for tl in folio_data['text']:
            lines.append(f"```")
            for key in ['EVA', 'CRO', 'EXP', 'ENG']:
                if key in tl:
                    lines.append(f"{key}: {tl[key]}")
            lines.append(f"```")
            lines.append(f"")
    
    lines.append(f"---")
    lines.append(f"*Generated by ZFD Recipe Extraction Pipeline v1.0*")
    
    return '\n'.join(lines)


def generate_recipe_index(all_analyses, folios):
    """Generate the master RECIPE_INDEX.md"""
    lines = []
    lines.append("# Voynich Manuscript: Complete Recipe Index")
    lines.append("")
    lines.append("## The Zuger Functional Decipherment — All Recipes Extracted")
    lines.append("")
    lines.append("This index catalogs every recipe, preparation instruction, and pharmaceutical")
    lines.append("procedure identified across all 201 folios of the Voynich Manuscript.")
    lines.append("")
    lines.append("**No one fabricates 179 pages of bone poultice instructions for a prank.**")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Summary statistics
    total_folios = len(all_analyses)
    recipe_folios = sum(1 for a in all_analyses.values() if a['has_recipe_content'])
    total_ingredients = Counter()
    total_processes = Counter()
    total_latin = Counter()
    
    for a in all_analyses.values():
        total_ingredients.update(a['ingredients_found'])
        total_processes.update(a['processes_found'])
        total_latin.update(a['latin_terms_found'])
    
    lines.append("## Summary Statistics")
    lines.append("")
    lines.append(f"- **Folios analyzed:** {total_folios}")
    lines.append(f"- **Folios with recipe content:** {recipe_folios} ({recipe_folios/total_folios*100:.0f}%)")
    lines.append(f"- **Unique ingredients identified:** {len(total_ingredients)}")
    lines.append(f"- **Total ingredient mentions:** {sum(total_ingredients.values())}")
    lines.append(f"- **Unique preparation methods:** {len(total_processes)}")
    lines.append(f"- **Latin pharmaceutical terms found:** {len(total_latin)}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Top ingredients
    lines.append("## Top 20 Ingredients (by frequency)")
    lines.append("")
    lines.append("| Rank | Stem | English | Latin | Total Mentions |")
    lines.append("|------|------|---------|-------|----------------|")
    for rank, (stem, count) in enumerate(total_ingredients.most_common(20), 1):
        info = INGREDIENTS.get(stem, {})
        eng = info.get('english', '?')
        lat = info.get('latin', '?')
        lines.append(f"| {rank} | **{stem}** | {eng} | *{lat}* | {count} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Top processes
    lines.append("## Preparation Methods (by frequency)")
    lines.append("")
    lines.append("| Stem | English | Category | Total Mentions |")
    lines.append("|------|---------|----------|----------------|")
    for stem, count in total_processes.most_common():
        info = PROCESSES.get(stem, {})
        eng = info.get('english', '?')
        cat = info.get('category', '?')
        lines.append(f"| **{stem}** | {eng} | {cat} | {count} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Latin terms
    if total_latin:
        lines.append("## Latin Pharmaceutical Vocabulary")
        lines.append("")
        lines.append("| Term | Latin | English | Category | Occurrences |")
        lines.append("|------|-------|---------|----------|-------------|")
        for term, count in total_latin.most_common():
            info = LATIN_TERMS.get(term, {})
            lines.append(f"| **{term}** | *{info.get('latin', '?')}* | {info.get('english', '?')} | {info.get('category', '?')} | {count} |")
        lines.append("")
        lines.append("---")
        lines.append("")
    
    # Per-section breakdown
    section_data = defaultdict(list)
    for fid, a in sorted(all_analyses.items(), key=lambda x: folio_number(x[0])):
        if a['has_recipe_content']:
            section = folios[fid]['section']
            section_data[section].append((fid, a))
    
    lines.append("## Recipes by Manuscript Section")
    lines.append("")
    
    for section in ['Herbal A', 'Herbal A (cont.)', 'Herbal B / Astronomical', 
                     'Biological', 'Pharmaceutical', 'Recipes/Stars', 'Cosmological', 'Other']:
        if section not in section_data:
            continue
        
        entries = section_data[section]
        lines.append(f"### {section} ({len(entries)} folios)")
        lines.append("")
        lines.append(f"| Folio | Confidence | Key Ingredients | Key Processes | Latin Terms |")
        lines.append(f"|-------|------------|-----------------|---------------|-------------|")
        
        for fid, a in entries:
            conf = f"{a['recipe_confidence']:.0%}"
            top_ing = ', '.join([f"{s}" for s, _ in sorted(a['ingredients_found'].items(), key=lambda x: -x[1])[:4]])
            top_proc = ', '.join([f"{s}" for s, _ in sorted(a['processes_found'].items(), key=lambda x: -x[1])[:3]])
            latin = ', '.join(a['latin_terms_found'].keys()) if a['latin_terms_found'] else '—'
            link = f"[{fid.upper()}](recipes/{fid}_recipe.md)"
            lines.append(f"| {link} | {conf} | {top_ing} | {top_proc} | {latin} |")
        
        lines.append("")
    
    lines.append("---")
    lines.append("")
    lines.append("## Ingredient Concordance")
    lines.append("")
    lines.append("Which folios contain which ingredients:")
    lines.append("")
    
    # Build ingredient → folio mapping
    ing_to_folios = defaultdict(list)
    for fid, a in all_analyses.items():
        for stem in a['ingredients_found']:
            ing_to_folios[stem].append(fid)
    
    for stem in sorted(ing_to_folios.keys(), key=lambda s: -len(ing_to_folios[s])):
        info = INGREDIENTS.get(stem, {})
        eng = info.get('english', '?')
        fids = sorted(ing_to_folios[stem], key=folio_number)
        lines.append(f"**{stem}** ({eng}): {', '.join([f.upper() for f in fids[:30]])}" + 
                     (f" ...+{len(fids)-30} more" if len(fids) > 30 else ""))
    
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Generated by ZFD Recipe Extraction Pipeline v1.0*")
    lines.append("*Source: INTERLINEAR_QUADRILINGUAL.md (201 folios, 4-layer format)*")
    lines.append(f"*Total folios with recipe content: {recipe_folios}/{total_folios}*")
    
    return '\n'.join(lines)


def main():
    print("=" * 60)
    print("ZFD Recipe Extraction Pipeline v1.0")
    print("/bacon — Cooking with love 🥓")
    print("=" * 60)
    
    # Parse
    print("\n[1/5] Parsing INTERLINEAR_QUADRILINGUAL.md...")
    folios = parse_quadrilingual('/home/claude/INTERLINEAR_QUADRILINGUAL.md')
    print(f"       Parsed {len(folios)} folios")
    
    # Analyze
    print("\n[2/5] Analyzing recipe content...")
    all_analyses = {}
    for fid, fdata in folios.items():
        analysis = analyze_folio(fdata)
        all_analyses[fid] = analysis
    
    recipe_count = sum(1 for a in all_analyses.values() if a['has_recipe_content'])
    print(f"       Found recipe content in {recipe_count}/{len(folios)} folios")
    
    # Generate individual recipe files
    print("\n[3/5] Generating individual recipe files...")
    output_dir = Path('/home/claude/recipe_output')
    recipes_dir = output_dir / 'recipes'
    recipes_dir.mkdir(parents=True, exist_ok=True)
    
    generated = 0
    for fid in sorted(all_analyses.keys(), key=folio_number):
        analysis = all_analyses[fid]
        if analysis['has_recipe_content']:
            recipe_md = generate_recipe_md(folios[fid], analysis)
            recipe_path = recipes_dir / f"{fid}_recipe.md"
            recipe_path.write_text(recipe_md, encoding='utf-8')
            generated += 1
    
    print(f"       Generated {generated} recipe files")
    
    # Generate master index
    print("\n[4/5] Generating RECIPE_INDEX.md...")
    index_md = generate_recipe_index(all_analyses, folios)
    (output_dir / 'RECIPE_INDEX.md').write_text(index_md, encoding='utf-8')
    
    # Stats summary
    print("\n[5/5] Summary Statistics:")
    total_ingredients = Counter()
    total_processes = Counter()
    for a in all_analyses.values():
        total_ingredients.update(a['ingredients_found'])
        total_processes.update(a['processes_found'])
    
    print(f"       Unique ingredients: {len(total_ingredients)}")
    print(f"       Total ingredient mentions: {sum(total_ingredients.values())}")
    print(f"       Top 5 ingredients:")
    for stem, count in total_ingredients.most_common(5):
        info = INGREDIENTS.get(stem, {})
        print(f"         {stem} ({info.get('english', '?')}): {count}")
    
    print(f"\n       Unique processes: {len(total_processes)}")
    print(f"       Top 5 processes:")
    for stem, count in total_processes.most_common(5):
        info = PROCESSES.get(stem, {})
        print(f"         {stem} ({info.get('english', '?')}): {count}")
    
    # High-confidence folios
    print(f"\n       High-confidence recipe folios (>60%):")
    for fid in sorted(all_analyses.keys(), key=folio_number):
        a = all_analyses[fid]
        if a['recipe_confidence'] >= 0.60:
            top_ing = ', '.join(list(a['ingredients_found'].keys())[:4])
            print(f"         {fid.upper()} ({a['recipe_confidence']:.0%}): {top_ing}")
    
    print("\n" + "=" * 60)
    print("✅ Done! Output in /home/claude/recipe_output/")
    print("=" * 60)


if __name__ == '__main__':
    main()
