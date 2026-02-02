#!/usr/bin/env python3
"""
Voynich → Croatian Translator v1.0
Based on the Glagolitic Shorthand Character Map

Applies the three-layer system:
1. OPERATORS (word-initial) → Prefixes/prepositions
2. ABBREVIATION MARKS (medial gallows) → Compressed syllable clusters
3. STEMS + SUFFIXES → Root morphemes + grammatical endings
"""

import json
import re
from pathlib import Path
from collections import Counter
from datetime import datetime

# =============================================================================
# CHARACTER MAP (from Claudette's Final Map v1.0)
# =============================================================================

# Operators - word initial
OPERATORS = {
    'q': 'ko',
    'ch': 'h',
    'sh': 'š',
    's': 's',
    'c': 'c',
}

# Abbreviation marks (gallows) - medial position, expand to clusters
ABBREVIATION_MARKS = {
    'k': ['st', 'sk'],  # Primary, alternate
    't': ['tr', 'tv'],
    'f': ['pr', 'fr'],
    'p': ['pl', 'sp'],
}

# Stem vowels - medial
STEMS = {
    'o': 'o',
    'e': 'e',
    'i': 'i',
    'a': 'a',
}

# Suffixes - word final
SUFFIXES = {
    'y': 'i',
    'n': 'n',
    'r': 'r',
    'l': 'l',
    'm': 'm',
}

# Additional mappings
OTHER = {
    'd': 'd',
    'h': '',  # Part of ch/sh, not standalone
    'ii': 'i',  # Double i = single i
    'ee': 'e',  # Double e = single e (or intensifier)
    'aiin': 'ain',
    'ain': 'ain',
}


def parse_word(eva_word):
    """
    Parse EVA word into positional components.
    Returns: (operator, stem_parts, suffix)
    """
    word = eva_word.lower().strip()
    if not word:
        return None, [], None

    operator = None
    suffix = None

    # Check for operators at start
    for op in ['qo', 'ch', 'sh', 'q']:  # Longer first
        if word.startswith(op):
            if op == 'qo':
                operator = 'ko'
                word = word[2:]
            elif op == 'q':
                operator = 'ko'
                word = word[1:]
            elif op == 'ch':
                operator = 'h'
                word = word[2:]
            elif op == 'sh':
                operator = 'š'
                word = word[2:]
            break

    # Check for suffix at end
    for suf in ['aiin', 'ain', 'iin', 'in', 'y', 'n', 'r', 'l', 'm']:
        if word.endswith(suf) and len(word) > len(suf):
            if suf == 'aiin':
                suffix = 'ain'
            elif suf == 'ain':
                suffix = 'ain'
            elif suf == 'iin':
                suffix = 'in'
            elif suf == 'in':
                suffix = 'in'
            else:
                suffix = SUFFIXES.get(suf, suf)
            word = word[:-len(suf)]
            break

    # What remains is the stem with possible abbreviation marks
    stem_parts = word

    return operator, stem_parts, suffix


def expand_stem(stem):
    """
    Expand stem, converting abbreviation marks to clusters.
    Returns list of possible expansions.
    """
    if not stem:
        return ['']

    results = ['']
    i = 0

    while i < len(stem):
        char = stem[i]

        # Check for digraphs
        if i + 1 < len(stem):
            digraph = stem[i:i+2]
            if digraph == 'ee':
                results = [r + 'e' for r in results]
                i += 2
                continue
            elif digraph == 'ii':
                results = [r + 'i' for r in results]
                i += 2
                continue

        # Abbreviation marks - expand to clusters
        if char in ABBREVIATION_MARKS:
            clusters = ABBREVIATION_MARKS[char]
            new_results = []
            for r in results:
                for cluster in clusters:
                    new_results.append(r + cluster)
            results = new_results
        # Vowels
        elif char in STEMS:
            results = [r + STEMS[char] for r in results]
        # Other consonants
        elif char == 'd':
            results = [r + 'd' for r in results]
        elif char == 'h':
            pass  # Skip standalone h (part of ch/sh)
        elif char == 's':
            results = [r + 's' for r in results]
        elif char == 'c':
            results = [r + 'c' for r in results]
        else:
            # Unknown - keep as is
            results = [r + char for r in results]

        i += 1

    return results


def translate_word(eva_word):
    """
    Translate EVA word to Croatian candidates.
    Returns list of possible Croatian readings.
    """
    operator, stem, suffix = parse_word(eva_word)

    # Expand stem
    stem_expansions = expand_stem(stem)

    # Build full words
    results = []
    for exp in stem_expansions:
        word = ''
        if operator:
            word += operator
        word += exp
        if suffix:
            word += suffix
        results.append(word)

    return results


def translate_corpus(corpus_path):
    """
    Translate entire corpus.
    """
    with open(corpus_path, 'r') as f:
        corpus = json.load(f)

    translations = {}
    word_counts = Counter()

    for word, count in corpus.items():
        croatian = translate_word(word)
        translations[word] = {
            'count': count,
            'croatian': croatian,
            'primary': croatian[0] if croatian else '',
        }
        word_counts[croatian[0] if croatian else ''] += count

    return translations, word_counts


def main():
    print("=" * 70)
    print("VOYNICH → CROATIAN TRANSLATOR v1.0")
    print("=" * 70)
    print(f"Started: {datetime.now().isoformat()}\n")

    # Build corpus from IVTFF transcription
    print("Building word frequency corpus from IVTFF...")
    words = Counter()
    transcription_file = Path('02_Transcriptions/LSI_ivtff_0d.txt')

    with open(transcription_file, encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            # Only process lines with folio markers that have transcription
            if not line.startswith('<f'):
                continue
            # Skip header lines
            if '>>' in line or '$' in line:
                continue

            # Extract the text portion after the '>'
            if '>' in line:
                text_part = line.split('>', 1)[1].strip()
            else:
                continue

            # Use only Takahashi transcription (;H lines) for consistency
            if ';H>' not in line and ';T>' not in line:
                continue

            # Extract words (split on . and whitespace)
            for part in re.split(r'[.\s]+', text_part):
                word = part.strip()
                # Clean word - only keep EVA characters
                word = re.sub(r'[^a-z]', '', word.lower())
                if word and len(word) >= 2:
                    words[word] += 1

    corpus = dict(words.most_common())
    print(f"Built corpus: {len(words)} unique words, {sum(words.values())} total tokens\n")

    print(f"Corpus loaded: {len(corpus)} unique words\n")

    # Translate top words
    print("=" * 70)
    print("TOP 50 TRANSLATIONS")
    print("=" * 70)
    print(f"{'EVA':<15} {'Count':>6}  {'Croatian (primary)':<20} {'Alternates'}")
    print("-" * 70)

    translations = {}
    for word, count in list(corpus.items())[:50]:
        croatian = translate_word(word)
        translations[word] = croatian

        primary = croatian[0] if croatian else '?'
        alts = ', '.join(croatian[1:3]) if len(croatian) > 1 else ''

        print(f"{word:<15} {count:>6}  {primary:<20} {alts}")

    # Full corpus translation
    print("\n" + "=" * 70)
    print("FULL CORPUS TRANSLATION")
    print("=" * 70)

    all_translations = {}
    croatian_words = Counter()

    for word, count in corpus.items():
        croatian = translate_word(word)
        all_translations[word] = {
            'count': count,
            'croatian': croatian,
        }
        if croatian:
            croatian_words[croatian[0]] += count

    # Save translations
    output_dir = Path('translations')
    output_dir.mkdir(exist_ok=True)

    with open(output_dir / 'croatian_readings.json', 'w') as f:
        json.dump(all_translations, f, indent=2, ensure_ascii=False)
    print(f"Saved: translations/croatian_readings.json")

    # Save Croatian word frequencies
    with open(output_dir / 'croatian_frequencies.json', 'w') as f:
        json.dump(dict(croatian_words.most_common()), f, indent=2, ensure_ascii=False)
    print(f"Saved: translations/croatian_frequencies.json")

    # Generate readable output
    with open(output_dir / 'CROATIAN_TRANSLATIONS.md', 'w') as f:
        f.write("# Voynich → Croatian Translations\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**Words translated:** {len(all_translations)}\n\n")
        f.write("---\n\n")

        f.write("## Top 100 Words\n\n")
        f.write("| EVA | Count | Croatian | Alternates |\n")
        f.write("|-----|-------|----------|------------|\n")

        for word, count in list(corpus.items())[:100]:
            croatian = all_translations[word]['croatian']
            primary = croatian[0] if croatian else '?'
            alts = ', '.join(croatian[1:3]) if len(croatian) > 1 else '-'
            f.write(f"| {word} | {count} | {primary} | {alts} |\n")

        f.write("\n---\n\n")
        f.write("## Most Common Croatian Readings\n\n")
        f.write("| Croatian | Frequency |\n")
        f.write("|----------|----------|\n")
        for word, freq in croatian_words.most_common(50):
            f.write(f"| {word} | {freq} |\n")

    print(f"Saved: translations/CROATIAN_TRANSLATIONS.md")

    # Stats
    print("\n" + "=" * 70)
    print("STATISTICS")
    print("=" * 70)
    print(f"Total unique EVA words: {len(corpus)}")
    print(f"Total unique Croatian readings: {len(croatian_words)}")
    if len(croatian_words) > 0:
        print(f"Compression ratio: {len(corpus)/len(croatian_words):.2f}x")

    print("\nTop 10 Croatian words:")
    for word, freq in croatian_words.most_common(10):
        print(f"  {word}: {freq}")

    print(f"\nTranslation complete: {datetime.now().isoformat()}")


if __name__ == "__main__":
    main()
