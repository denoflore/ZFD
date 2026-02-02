"""
Phase 9: Complete Pharmaceutical Section Translator

Translate individual folios to recipe format with proper annotation.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent))

from zfd_loader import ZFDLoader
from phase7_parser import VoynichParser, CONFIRMED_LEXICON

# =============================================================================
# ENHANCED RECIPE VOCABULARY
# =============================================================================

RECIPE_VERBS = {
    'qo': 'measure',
    'ch': 'mix',
    'da': 'dose',
    'ok': 'process',
    'ot': 'prepare',
    'sh': 'strain',
    'so': 'soak',
    'sa': 'salt',
    'yk': 'yield',
    'pc': 'pound',
    'tc': 'apply',
}

RECIPE_NOUNS = {
    'ed': 'root',
    'od': 'stalk',
    'ol': 'oil',
    'or': 'oil',
    'kal': 'vessel',
    'kar': 'fire',
    'k': 'vessel',
    'ee': 'thoroughly',
}

RECIPE_METHODS = {
    'al': 'as liquid',
    'ar': 'with heat',
}

RECIPE_SUFFIXES = {
    'y': '',
    'dy': 'until done',
    'aiin': 'continue in liquid',
    'iin': 'continue',
    'ain': 'in process',
    'm': 'material',
    'ir': 'heat result',
}

# Visual content notes for pharmaceutical folios
PHARMA_VISUAL_NOTES = {
    'f88r': """
**Visual Content (f88r):**
- Pharmaceutical section opener
- Jars/containers with plant material
- Some containers appear to hold liquid
- Plant parts (roots, leaves) shown separately from containers

**Expected correlations:**
- kal (vessel): Should appear frequently
- al/ar (liquid/heat methods): Expected
- ed/od (plant parts): Visible in illustrations
""",

    'f88v': """
**Visual Content (f88v):**
- Continuation of pharmaceutical containers
- Mix of simple and decorated vessels
- Plant material alongside containers
- Some text labels near containers

**Expected correlations:**
- Vessel operations (qokal, okal)
- Preparation methods (al, ar)
""",

    'f99r': """
**Visual Content (f99r):**
- Quire 19 pharmaceutical section
- Simple cylindrical containers
- Open-topped vessels (no lids)
- Light yellow paint on container tops (early construction)

**Expected correlations:**
- kal references for vessels
- Simple preparation instructions
""",

    'f99v': """
**Visual Content (f99v):**
- Continuation of container illustrations
- Some containers with colored contents
- Plant roots/leaves shown
- Faded paints suggest original coloring

**Expected correlations:**
- Oil/liquid preparations (ol, al)
- Root processing (ed)
""",

    'f100r': """
**Visual Content (f100r):**
- Container illustrations continue
- "Pepper" identification in upper right (per O'Neill)
- Mix of cylindrical containers

**Expected correlations:**
- Spice/plant preparations
- Vessel measurements
""",

    'f100v': """
**Visual Content (f100v):**
- Container section continues
- Simple vessel shapes
- Some with decorative elements

**Expected correlations:**
- Consistent vessel vocabulary
""",

    'f101r': """
**Visual Content (f101r):**
- Transition to more complex containers
- Some elaborate vessel shapes emerging

**Expected correlations:**
- Process operations (ok-)
- Preparation sequences
""",

    'f101v': """
**Visual Content (f101v):**
- More elaborate container designs
- Complex vessel shapes
- Transition toward Q15 style

**Expected correlations:**
- Complex preparation instructions
- Multiple step recipes
""",
}


def gloss_to_instruction(parse: dict, word: str) -> str:
    """Convert a parse to a recipe instruction fragment."""
    parts = []
    p = parse['parse']

    verb = RECIPE_VERBS.get(p['operator'], '')
    noun = RECIPE_NOUNS.get(p['stem'], '')
    method = RECIPE_METHODS.get(p['class'], '')
    suffix = RECIPE_SUFFIXES.get(p['suffix'], '')

    # Handle intensifier
    if p['stem'] == 'ee':
        if verb:
            parts.append(f"{verb} thoroughly")
        else:
            parts.append("(intensify)")
    elif verb and noun:
        parts.append(f"{verb} {noun}")
    elif verb:
        parts.append(verb)
    elif noun:
        parts.append(noun)

    if method:
        parts.append(method)
    if suffix:
        parts.append(suffix)

    result = ' '.join(parts)

    if not result.strip():
        return f"[{word}]"

    return result


def translate_folio(loader: ZFDLoader, parser: VoynichParser,
                    folio: str, section: str = "pharmaceutical") -> dict:
    """Translate a single folio to recipe format."""

    if folio not in loader.transcription:
        return {'error': f'Folio {folio} not found in transcription'}

    lines = loader.transcription[folio]

    result = {
        'folio': folio,
        'section': section,
        'generated': datetime.now().isoformat(),
        'lines': [],
        'recipe_steps': [],
        'stats': {
            'total_words': 0,
            'parsed_words': 0,
            'unknown_words': 0,
            'confidence_sum': 0.0,
        },
        'morpheme_counts': defaultdict(int),
    }

    for line_data in lines:
        line_num = line_data.get('line_num', 0)
        tokens = line_data.get('tokens', [])

        voynich_words = []
        glosses = []
        instructions = []

        for token in tokens:
            parse = parser.parse_word(token)

            voynich_words.append(token)
            glosses.append(parse['gloss'])
            instructions.append(gloss_to_instruction(parse, token))

            result['stats']['total_words'] += 1
            result['stats']['confidence_sum'] += parse['confidence']

            if parse['confidence'] > 0.3:
                result['stats']['parsed_words'] += 1
            else:
                result['stats']['unknown_words'] += 1

            # Count morphemes
            p = parse['parse']
            if p['operator']:
                result['morpheme_counts'][f"op:{p['operator']}"] += 1
            if p['stem']:
                result['morpheme_counts'][f"stem:{p['stem']}"] += 1
            if p['class']:
                result['morpheme_counts'][f"class:{p['class']}"] += 1
            if p['suffix']:
                result['morpheme_counts'][f"suffix:{p['suffix']}"] += 1

        result['lines'].append({
            'line_num': line_num,
            'voynich': ' '.join(voynich_words),
            'gloss': ' | '.join(glosses),
            'instruction': ', '.join(instructions),
        })

        # Build recipe step
        if instructions:
            step = f"{line_num}. {', '.join(i for i in instructions if i and not i.startswith('['))}"
            if step.strip() != f"{line_num}. ":
                result['recipe_steps'].append(step)

    # Calculate confidence
    if result['stats']['total_words'] > 0:
        result['stats']['confidence_avg'] = (
            result['stats']['confidence_sum'] / result['stats']['total_words']
        )
    else:
        result['stats']['confidence_avg'] = 0.0

    # Convert morpheme counts to regular dict
    result['morpheme_counts'] = dict(result['morpheme_counts'])

    return result


def format_recipe_markdown(translation: dict) -> str:
    """Format translation as markdown recipe file."""

    folio = translation['folio']
    lines = []

    # Header
    lines.append(f"# Recipe Translation: {folio.upper()}")
    lines.append("")
    lines.append(f"**Section:** {translation['section'].title()}")
    lines.append(f"**Generated:** {translation['generated']}")
    lines.append(f"**Confidence:** {translation['stats']['confidence_avg']:.2f}")
    lines.append(f"**Words:** {translation['stats']['total_words']} total, "
                 f"{translation['stats']['parsed_words']} parsed "
                 f"({100*translation['stats']['parsed_words']/max(1,translation['stats']['total_words']):.0f}%)")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Visual notes
    visual_notes = PHARMA_VISUAL_NOTES.get(folio,
        "No pre-analyzed visual notes available for this folio.")
    lines.append("## Visual Context")
    lines.append("")
    lines.append(visual_notes)
    lines.append("")
    lines.append("---")
    lines.append("")

    # Interlinear translation
    lines.append("## Interlinear Translation")
    lines.append("")

    for line_data in translation['lines']:
        lines.append(f"**Line {line_data['line_num']}:**")
        lines.append("```")
        lines.append(f"VOYNICH:     {line_data['voynich']}")
        lines.append(f"GLOSS:       {line_data['gloss']}")
        lines.append(f"INSTRUCTION: {line_data['instruction']}")
        lines.append("```")
        lines.append("")

    lines.append("---")
    lines.append("")

    # Recipe interpretation
    lines.append("## Recipe Interpretation")
    lines.append("")

    for step in translation['recipe_steps']:
        lines.append(step)

    lines.append("")
    lines.append("---")
    lines.append("")

    # Morpheme analysis
    lines.append("## Morpheme Analysis")
    lines.append("")

    # Group by type
    ops = {k: v for k, v in translation['morpheme_counts'].items() if k.startswith('op:')}
    stems = {k: v for k, v in translation['morpheme_counts'].items() if k.startswith('stem:')}
    classes = {k: v for k, v in translation['morpheme_counts'].items() if k.startswith('class:')}
    suffixes = {k: v for k, v in translation['morpheme_counts'].items() if k.startswith('suffix:')}

    if ops:
        lines.append("**Operators (Verbs):**")
        for k, v in sorted(ops.items(), key=lambda x: x[1], reverse=True):
            name = k.replace('op:', '')
            meaning = RECIPE_VERBS.get(name, '?')
            lines.append(f"- {name} ({meaning}): {v}")
        lines.append("")

    if stems:
        lines.append("**Stems (Nouns):**")
        for k, v in sorted(stems.items(), key=lambda x: x[1], reverse=True):
            name = k.replace('stem:', '')
            meaning = RECIPE_NOUNS.get(name, '?')
            lines.append(f"- {name} ({meaning}): {v}")
        lines.append("")

    if classes:
        lines.append("**Class Markers (Methods):**")
        for k, v in sorted(classes.items(), key=lambda x: x[1], reverse=True):
            name = k.replace('class:', '')
            meaning = RECIPE_METHODS.get(name, '?').replace('as ', '').replace('with ', '')
            lines.append(f"- {name} ({meaning}): {v}")
        lines.append("")

    if suffixes:
        lines.append("**Suffixes (States):**")
        for k, v in sorted(suffixes.items(), key=lambda x: x[1], reverse=True):
            name = k.replace('suffix:', '')
            lines.append(f"- {name}: {v}")
        lines.append("")

    lines.append("---")
    lines.append("")

    # Confidence assessment
    conf = translation['stats']['confidence_avg']
    if conf >= 0.4:
        conf_level = "HIGH"
        assessment = "Translation is well-supported by confirmed morphemes."
    elif conf >= 0.3:
        conf_level = "MEDIUM"
        assessment = "Translation has reasonable morpheme coverage with some uncertainties."
    else:
        conf_level = "LOW"
        assessment = "Translation has significant gaps; many tokens unrecognized."

    lines.append("## Confidence Assessment")
    lines.append("")
    lines.append(f"**Level:** {conf_level}")
    lines.append(f"**Score:** {conf:.2f}")
    lines.append(f"**Assessment:** {assessment}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"*Translated as part of ZFD Phase 9 - {datetime.now().strftime('%Y-%m-%d')}*")

    return '\n'.join(lines)


def translate_and_save(folio: str, output_dir: Path = None):
    """Translate a folio and save to file."""

    output_dir = output_dir or Path('translations')
    output_dir.mkdir(exist_ok=True)

    loader = ZFDLoader('.')
    parser = VoynichParser(CONFIRMED_LEXICON)

    print(f"Translating {folio}...")

    translation = translate_folio(loader, parser, folio, "pharmaceutical")

    if 'error' in translation:
        print(f"  ERROR: {translation['error']}")
        return None

    # Format and save
    md_content = format_recipe_markdown(translation)
    output_path = output_dir / f"{folio}_recipe.md"

    with open(output_path, 'w') as f:
        f.write(md_content)

    print(f"  Saved: {output_path}")
    print(f"  Words: {translation['stats']['total_words']}, "
          f"Parsed: {translation['stats']['parsed_words']} "
          f"({100*translation['stats']['parsed_words']/max(1,translation['stats']['total_words']):.0f}%)")
    print(f"  Confidence: {translation['stats']['confidence_avg']:.3f}")

    return translation


def main():
    """Translate all available pharmaceutical folios."""

    print("="*70)
    print("ZFD PHASE 9: PHARMACEUTICAL SECTION TRANSLATOR")
    print("="*70)

    loader = ZFDLoader('.')

    # List of pharmaceutical folios to translate
    pharma_folios = [
        'f88r', 'f88v',  # Quire 15
        'f99r', 'f99v', 'f100r', 'f100v', 'f101r', 'f101v',  # Quire 19
    ]

    output_dir = Path('translations')
    output_dir.mkdir(exist_ok=True)

    results = []

    for folio in pharma_folios:
        if folio not in loader.transcription:
            print(f"\n{folio}: NOT AVAILABLE in transcription data")
            continue

        translation = translate_and_save(folio, output_dir)
        if translation:
            results.append(translation)

    # Summary
    print("\n" + "="*70)
    print("TRANSLATION SUMMARY")
    print("="*70)

    total_words = sum(r['stats']['total_words'] for r in results)
    total_parsed = sum(r['stats']['parsed_words'] for r in results)
    avg_conf = sum(r['stats']['confidence_avg'] for r in results) / max(1, len(results))

    print(f"\nFolios translated: {len(results)}")
    print(f"Total words: {total_words}")
    print(f"Words parsed: {total_parsed} ({100*total_parsed/max(1,total_words):.1f}%)")
    print(f"Average confidence: {avg_conf:.3f}")

    print("\n" + "="*70)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        # Translate specific folio
        folio = sys.argv[1]
        translate_and_save(folio)
    else:
        # Translate all
        main()
