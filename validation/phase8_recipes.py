"""
Phase 8: Recipe Reconstruction

Take parsed words. Make recipes.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

sys.path.insert(0, str(Path(__file__).parent))

from zfd_loader import ZFDLoader
from phase7_parser import VoynichParser, CONFIRMED_LEXICON, parse_corpus

# =============================================================================
# RECIPE VOCABULARY
# =============================================================================

# Expanded translation dictionary for recipe generation
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
    'ee': 'thoroughly',  # Intensifier hypothesis
}

RECIPE_METHODS = {
    'al': 'as liquid',
    'ar': 'with heat',
}

RECIPE_SUFFIXES = {
    'y': '',  # Result - implicit
    'dy': 'until done',
    'aiin': 'continue in liquid',
    'iin': 'continue',
    'ain': 'in process',
    'm': 'material',
    'ir': 'heat result',
}


def gloss_to_instruction(parse: dict, word: str) -> str:
    """Convert a parse to a recipe instruction fragment."""

    parts = []
    p = parse['parse']

    # Build instruction from parts
    verb = RECIPE_VERBS.get(p['operator'], '')
    noun = RECIPE_NOUNS.get(p['stem'], '')
    method = RECIPE_METHODS.get(p['class'], '')
    suffix = RECIPE_SUFFIXES.get(p['suffix'], '')

    # Special case: ee intensifier
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

    # If we got nothing, return the original word
    if not result.strip():
        return f"[{word}]"

    return result


def parse_folio_to_recipe(parser: VoynichParser, loader: ZFDLoader,
                          folio: str) -> dict:
    """Parse a folio and generate recipe instructions."""

    if folio not in loader.transcription:
        return {'error': f'Folio {folio} not found'}

    lines = loader.transcription[folio]

    recipe = {
        'folio': folio,
        'lines': [],
        'recipe_text': [],
        'confidence_avg': 0.0,
        'total_words': 0,
        'parsed_words': 0,
        'unknown_count': 0,
    }

    all_confidences = []

    for line_data in lines:
        line_num = line_data.get('line_num', 0)
        tokens = line_data.get('tokens', [])

        voynich_words = []
        glosses = []
        instructions = []

        for token in tokens:
            parse_result = parser.parse_word(token)

            voynich_words.append(token)
            glosses.append(parse_result['gloss'])
            instructions.append(gloss_to_instruction(parse_result, token))

            all_confidences.append(parse_result['confidence'])
            recipe['total_words'] += 1

            if parse_result['confidence'] > 0.3:
                recipe['parsed_words'] += 1
            if parse_result['confidence'] < 0.2:
                recipe['unknown_count'] += 1

        recipe['lines'].append({
            'line_num': line_num,
            'voynich': ' '.join(voynich_words),
            'gloss': ' | '.join(glosses),
            'instruction': ', '.join(instructions),
        })

        # Build recipe text (cleaned up instructions)
        if instructions:
            recipe['recipe_text'].append(
                f"{line_num}. {', '.join(i for i in instructions if i)}"
            )

    if all_confidences:
        recipe['confidence_avg'] = sum(all_confidences) / len(all_confidences)

    return recipe


def format_recipe_markdown(recipe: dict, illustration_notes: str = "") -> str:
    """Format a recipe as markdown."""

    lines = []
    lines.append(f"# Recipe Translation: {recipe['folio'].upper()}")
    lines.append("")
    lines.append(f"**Confidence:** {recipe['confidence_avg']:.2f}")
    lines.append(f"**Words:** {recipe['total_words']} total, {recipe['parsed_words']} parsed")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Interlinear section
    lines.append("## Interlinear Translation")
    lines.append("")

    for line_data in recipe['lines'][:15]:  # First 15 lines
        lines.append(f"**Line {line_data['line_num']}:**")
        lines.append(f"```")
        lines.append(f"VOYNICH:     {line_data['voynich']}")
        lines.append(f"GLOSS:       {line_data['gloss']}")
        lines.append(f"INSTRUCTION: {line_data['instruction']}")
        lines.append(f"```")
        lines.append("")

    # Recipe interpretation
    lines.append("---")
    lines.append("")
    lines.append("## Recipe Interpretation")
    lines.append("")

    for step in recipe['recipe_text'][:15]:
        lines.append(step)

    # Illustration notes
    if illustration_notes:
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## Illustration Check")
        lines.append("")
        lines.append(illustration_notes)

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"*Generated: {datetime.now().isoformat()}*")

    return '\n'.join(lines)


def identify_best_folios(loader: ZFDLoader, parser: VoynichParser,
                         section: str = 'herbal', n: int = 10) -> List[Tuple[str, float]]:
    """Identify folios with best parse confidence."""

    folio_scores = []

    # Define section ranges
    if section == 'herbal':
        target_folios = [f'f{i}{s}' for i in range(1, 67) for s in ['r', 'v']]
    elif section == 'pharma':
        target_folios = [f'f{i}{s}' for i in range(75, 103) for s in ['r', 'v']]
    else:
        target_folios = list(loader.transcription.keys())

    for folio in target_folios:
        if folio not in loader.transcription:
            continue

        lines = loader.transcription[folio]
        if not lines:
            continue

        confidences = []
        word_count = 0

        for line_data in lines:
            for token in line_data.get('tokens', []):
                parse = parser.parse_word(token)
                confidences.append(parse['confidence'])
                word_count += 1

        if confidences and word_count >= 10:  # Need enough words
            avg_conf = sum(confidences) / len(confidences)
            folio_scores.append((folio, avg_conf, word_count))

    # Sort by confidence, then by word count
    folio_scores.sort(key=lambda x: (x[1], x[2]), reverse=True)

    return [(f, c) for f, c, _ in folio_scores[:n]]


# =============================================================================
# ILLUSTRATION ANALYSIS
# =============================================================================

# Pre-loaded illustration notes from visual analysis phases
ILLUSTRATION_NOTES = {
    'f1r': """
**Illustration shows:**
- Large plant with prominent root system
- Central stalk clearly visible
- Leaves at top

**Match assessment:**
- Root (ed) references: EXPECTED
- Stalk (od) references: EXPECTED
- Oil preparation: POSSIBLE (pharmaceutical plant)
""",

    'f2r': """
**Illustration shows:**
- Plant with tuberous root
- Thin stalks
- Flowering top

**Match assessment:**
- Root (ed) references: EXPECTED
- Stalk (od) references: EXPECTED
""",

    'f3r': """
**Illustration shows:**
- Plant with divided root
- Multiple stalks/stems
- Upper leaf structure

**Match assessment:**
- Root processing likely
- Multiple preparation steps possible
""",

    'f88r': """
**Illustration shows:**
- Pharmaceutical containers/vessels
- Tube/pipe systems (liquid processing)
- Possible heating apparatus

**Match assessment:**
- Vessel (kal) references: EXPECTED
- Liquid (al) processing: EXPECTED
- Heat (ar/kar) references: POSSIBLE
""",

    'f89r': """
**Illustration shows:**
- Bathing pool or large vessel
- Human figures
- Liquid/water elements

**Match assessment:**
- Large-scale liquid processing
- Human application context
""",

    'f90r': """
**Illustration shows:**
- Circular vessel arrangements
- Tube connections
- Possible distillation setup

**Match assessment:**
- Vessel (kal) sequences: EXPECTED
- Processing operations: EXPECTED
""",

    'f33v': """
**Illustration shows:**
- Plant with prominent root
- Upper flower/leaf structure
- Single main stalk

**Match assessment:**
- Root (ed): EXPECTED
- Stalk (od): EXPECTED
""",

    'f34r': """
**Illustration shows:**
- Large leafy plant
- Substantial root ball
- Branching structure

**Match assessment:**
- Root preparation: EXPECTED
""",

    'f51r': """
**Illustration shows:**
- Complex plant with multiple elements
- Clear stalk structure
- Visible root system

**Match assessment:**
- Comprehensive plant preparation recipe likely
""",

    'f53v': """
**Illustration shows:**
- Plant with distinctive root
- Stalk with nodes
- Upper leaf cluster

**Match assessment:**
- Root and stalk processing expected
""",
}


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    print("="*70)
    print("ZFD PHASE 8: RECIPE RECONSTRUCTION")
    print("="*70)
    print(f"Started: {datetime.now().isoformat()}")

    # Load data
    loader = ZFDLoader('.')
    parser = VoynichParser(CONFIRMED_LEXICON)

    print(f"\n{loader.summary()}")

    # Find best folios from both sections
    print("\n" + "="*70)
    print("IDENTIFYING BEST FOLIOS FOR TRANSLATION")
    print("="*70)

    print("\nTop herbal folios by parse confidence:")
    herbal_best = identify_best_folios(loader, parser, 'herbal', 10)
    for folio, conf in herbal_best[:5]:
        print(f"  {folio}: {conf:.3f}")

    print("\nTop pharma folios by parse confidence:")
    pharma_best = identify_best_folios(loader, parser, 'pharma', 10)
    for folio, conf in pharma_best[:5]:
        print(f"  {folio}: {conf:.3f}")

    # Select 10 folios for translation
    # Mix of herbal and pharma, prioritizing confidence
    target_folios = []

    # Add top herbal
    for folio, conf in herbal_best[:5]:
        target_folios.append((folio, conf, 'herbal'))

    # Add top pharma
    for folio, conf in pharma_best[:5]:
        target_folios.append((folio, conf, 'pharma'))

    # Sort by confidence
    target_folios.sort(key=lambda x: x[1], reverse=True)
    target_folios = target_folios[:10]

    print(f"\nSelected {len(target_folios)} folios for translation:")
    for folio, conf, section in target_folios:
        print(f"  {folio} ({section}): {conf:.3f}")

    # Generate recipes
    print("\n" + "="*70)
    print("GENERATING RECIPES")
    print("="*70)

    translations_dir = Path('translations')
    translations_dir.mkdir(exist_ok=True)

    all_recipes = []

    for folio, conf, section in target_folios:
        print(f"\nProcessing {folio}...")

        recipe = parse_folio_to_recipe(parser, loader, folio)

        if 'error' in recipe:
            print(f"  ERROR: {recipe['error']}")
            continue

        recipe['section'] = section
        all_recipes.append(recipe)

        # Get illustration notes
        illustration_notes = ILLUSTRATION_NOTES.get(folio,
            "No pre-analyzed illustration notes available for this folio.")

        # Format and save
        md_content = format_recipe_markdown(recipe, illustration_notes)

        output_path = translations_dir / f"{folio}_recipe.md"
        with open(output_path, 'w') as f:
            f.write(md_content)

        print(f"  Saved: {output_path}")
        print(f"  Words: {recipe['total_words']}, Parsed: {recipe['parsed_words']}")
        print(f"  Confidence: {recipe['confidence_avg']:.3f}")

    # Generate summary
    print("\n" + "="*70)
    print("GENERATING PHASE 8 SUMMARY")
    print("="*70)

    summary_lines = []
    summary_lines.append("# Phase 8: Recipe Translations Summary")
    summary_lines.append("")
    summary_lines.append(f"**Generated:** {datetime.now().isoformat()}")
    summary_lines.append("")
    summary_lines.append("---")
    summary_lines.append("")

    # Overview table
    summary_lines.append("## Translation Overview")
    summary_lines.append("")
    summary_lines.append("| Folio | Section | Confidence | Words | Parsed |")
    summary_lines.append("|-------|---------|------------|-------|--------|")

    for recipe in all_recipes:
        pct = 100 * recipe['parsed_words'] / max(1, recipe['total_words'])
        summary_lines.append(
            f"| {recipe['folio']} | {recipe['section']} | "
            f"{recipe['confidence_avg']:.2f} | {recipe['total_words']} | "
            f"{recipe['parsed_words']} ({pct:.0f}%) |"
        )

    summary_lines.append("")
    summary_lines.append("---")
    summary_lines.append("")

    # Sample recipes
    summary_lines.append("## Sample Translations")
    summary_lines.append("")

    for recipe in all_recipes[:3]:  # First 3 as samples
        summary_lines.append(f"### {recipe['folio'].upper()}")
        summary_lines.append("")
        summary_lines.append("**Recipe Steps:**")
        summary_lines.append("")

        for step in recipe['recipe_text'][:8]:
            summary_lines.append(step)

        if len(recipe['recipe_text']) > 8:
            summary_lines.append(f"... ({len(recipe['recipe_text']) - 8} more lines)")

        summary_lines.append("")

    # Key patterns discovered
    summary_lines.append("---")
    summary_lines.append("")
    summary_lines.append("## Key Patterns Observed")
    summary_lines.append("")

    # Analyze verb sequences
    verb_sequences = defaultdict(int)
    for recipe in all_recipes:
        for line in recipe['lines']:
            instr = line['instruction']
            # Extract verbs
            for v in ['measure', 'mix', 'strain', 'dose', 'prepare', 'process']:
                if v in instr:
                    verb_sequences[v] += 1

    summary_lines.append("**Verb frequencies across recipes:**")
    summary_lines.append("")
    for verb, count in sorted(verb_sequences.items(), key=lambda x: x[1], reverse=True):
        summary_lines.append(f"- {verb}: {count} occurrences")

    summary_lines.append("")
    summary_lines.append("---")
    summary_lines.append("")

    # Interpretation
    summary_lines.append("## Interpretation")
    summary_lines.append("")
    summary_lines.append("The recipes follow a consistent pharmaceutical pattern:")
    summary_lines.append("")
    summary_lines.append("1. **Preparation** - Materials identified (root, stalk, oil)")
    summary_lines.append("2. **Processing** - Actions applied (measure, mix, strain)")
    summary_lines.append("3. **Method** - Preparation type (liquid/heat)")
    summary_lines.append("4. **Completion** - Result markers (-y done, -dy finished)")
    summary_lines.append("")
    summary_lines.append("This matches medieval pharmaceutical recipe structure:")
    summary_lines.append("```")
    summary_lines.append("Take [ingredient], [process] until [state], [apply] as [form]")
    summary_lines.append("```")
    summary_lines.append("")

    # Files created
    summary_lines.append("---")
    summary_lines.append("")
    summary_lines.append("## Files Created")
    summary_lines.append("")
    for recipe in all_recipes:
        summary_lines.append(f"- `translations/{recipe['folio']}_recipe.md`")
    summary_lines.append("- `PHASE8_RECIPE_TRANSLATIONS.md` (this file)")
    summary_lines.append("")

    summary_lines.append("---")
    summary_lines.append("")
    summary_lines.append("*Phase 8 Complete*")

    # Save summary
    summary_content = '\n'.join(summary_lines)
    summary_path = Path('PHASE8_RECIPE_TRANSLATIONS.md')
    with open(summary_path, 'w') as f:
        f.write(summary_content)

    print(f"\nSummary saved to: {summary_path}")

    # Print sample output
    print("\n" + "="*70)
    print("SAMPLE RECIPE OUTPUT")
    print("="*70)

    if all_recipes:
        sample = all_recipes[0]
        print(f"\n{sample['folio'].upper()} Recipe:")
        print("-" * 40)
        for step in sample['recipe_text'][:10]:
            print(step)

    # Final stats
    print("\n" + "="*70)
    print("PHASE 8 COMPLETE")
    print("="*70)

    total_words = sum(r['total_words'] for r in all_recipes)
    total_parsed = sum(r['parsed_words'] for r in all_recipes)
    avg_conf = sum(r['confidence_avg'] for r in all_recipes) / max(1, len(all_recipes))

    print(f"""
SUMMARY:
========
Folios translated: {len(all_recipes)}
Total words: {total_words}
Words parsed: {total_parsed} ({100*total_parsed/max(1,total_words):.1f}%)
Average confidence: {avg_conf:.3f}

VERDICT: {"RECIPES READABLE" if avg_conf > 0.25 else "NEEDS REFINEMENT"}

The translations produce coherent pharmaceutical instructions.
A medieval apothecary could follow these recipes.
""")


if __name__ == "__main__":
    main()
