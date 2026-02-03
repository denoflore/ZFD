#!/usr/bin/env python3
"""
Transliteration Engine - Phase 3 of Glagolitic OCR Pipeline

Converts EVA token sequences to five-layer interlinear output:
1. EVA (input from IVTFF)
2. Glagolitic Unicode
3. Latin transliteration
4. Croatian shorthand
5. Expanded Croatian + English

Uses character_reference.py as foundation. Processes digraphs before singles.
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Import existing character reference (DO NOT MODIFY that file)
from character_reference import (
    GLAGOLITIC_ALPHABET,
    EVA_TO_GLAGOLITIC,
    transliterate_to_croatian as glag_to_croatian
)


@dataclass
class TransliteratedWord:
    """Five-layer representation of a transliterated word."""
    eva: str
    glagolitic: str
    latin: str
    croatian_short: str
    croatian_expanded: str
    english: str
    confidence: float
    unmapped: List[str]


# =============================================================================
# EVA TO GLAGOLITIC MAPPINGS (from FINAL_CHARACTER_MAP_v1.md)
# =============================================================================

# DIGRAPHS - process FIRST (longest match wins)
DIGRAPH_MAP = {
    # Compound gallows (3-char)
    'cth': 'ⰽⱅⱈ',   # k+t+h compound
    'cph': 'ⰽⱂⱈ',   # k+p+h compound
    'ckh': 'ⰽⰼⱈ',   # k+k+h compound
    'cfh': 'ⰽⱇⱈ',   # k+f+h compound

    # Standard digraphs (2-char)
    'ch': 'Ⱈ',      # U+2C18, Xer, /x/
    'sh': 'Ⱊ',      # U+2C1A, Sha, /sh/
    'ii': 'ⰹⰹ',     # doubled i
    'ee': 'ⰵⰵ',     # doubled e (rare)
    'ai': 'ⰰⰹ',     # a+i sequence
    'oi': 'ⱁⰹ',     # o+i sequence
}

# SINGLE CHARACTER MAP
SINGLE_MAP = {
    'a': 'Ⰰ',   # U+2C00, Az, /a/
    'd': 'Ⰴ',   # U+2C04, Dobro, /d/
    'e': 'Ⰵ',   # U+2C05, Est, /e/
    'f': 'Ⱇ',   # U+2C17, Frt, /f/
    'g': 'Ⰳ',   # U+2C03, Glagoli, /g/
    'i': 'Ⰹ',   # U+2C09, Izhe, /i/
    'k': 'Ⰼ',   # U+2C0C, Kako, /k/
    'l': 'Ⰾ',   # U+2C0E, Ljudie, /l/  (note: using correct lowercase variant)
    'm': 'Ⰿ',   # U+2C0F, Myslete, /m/
    'n': 'Ⱀ',   # U+2C10, Nash, /n/
    'o': 'Ⱁ',   # U+2C11, On, /o/
    'p': 'Ⱂ',   # U+2C12, Pokoj, /p/
    'q': 'ⰼⱁ',  # ko ligature (represents /ko/)
    'r': 'Ⱃ',   # U+2C13, Rtsi, /r/
    's': 'Ⱄ',   # U+2C14, Slovo, /s/
    't': 'Ⱅ',   # U+2C15, Tvrdo, /t/
    'y': 'Ⱏ',   # U+2C1F, Yat, represents reduced vowel
    'h': 'Ⱈ',   # U+2C18, maps to Xer when standalone
    'c': 'Ⱉ',   # U+2C19, Tsi, /ts/ - standalone c before vowels
    'x': 'Ⱈ',   # rare, maps to Xer
}

# =============================================================================
# GLAGOLITIC TO LATIN TRANSLITERATION
# =============================================================================

GLAGOLITIC_TO_LATIN = {
    'Ⰰ': 'a', 'ⰰ': 'a',
    'Ⰱ': 'b', 'ⰱ': 'b',
    'Ⰲ': 'v', 'ⰲ': 'v',
    'Ⰳ': 'g', 'ⰳ': 'g',
    'Ⰴ': 'd', 'ⰴ': 'd',
    'Ⰵ': 'e', 'ⰵ': 'e',
    'Ⰶ': 'ž', 'ⰶ': 'ž',
    'Ⰷ': 'dz', 'ⰷ': 'dz',
    'Ⰸ': 'z', 'ⰸ': 'z',
    'Ⰹ': 'i', 'ⰹ': 'i',
    'Ⰺ': 'i', 'ⰺ': 'i',
    'Ⰻ': 'đ', 'ⰻ': 'đ',
    'Ⰼ': 'k', 'ⰼ': 'k',
    'Ⰽ': 'l', 'ⰽ': 'l',
    'Ⰾ': 'l', 'ⰾ': 'l',
    'Ⰿ': 'm', 'ⰿ': 'm',
    'Ⱀ': 'n', 'ⱀ': 'n',
    'Ⱁ': 'o', 'ⱁ': 'o',
    'Ⱂ': 'p', 'ⱂ': 'p',
    'Ⱃ': 'r', 'ⱃ': 'r',
    'Ⱄ': 's', 'ⱄ': 's',
    'Ⱅ': 't', 'ⱅ': 't',
    'Ⱆ': 'u', 'ⱆ': 'u',
    'Ⱇ': 'f', 'ⱇ': 'f',
    'Ⱈ': 'h', 'ⱈ': 'h',
    'Ⱉ': 'c', 'ⱉ': 'c',
    'Ⱊ': 'š', 'ⱊ': 'š',
    'Ⱋ': 'č', 'ⱋ': 'č',
    'Ⱌ': 'št', 'ⱌ': 'št',
    'Ⱍ': 'y', 'ⱍ': 'y',
    'Ⱎ': 'y', 'ⱎ': 'y',
    'Ⱏ': 'y', 'ⱏ': 'y',
    'Ⱐ': 'jo', 'ⱐ': 'jo',
    'Ⱑ': 'ju', 'ⱑ': 'ju',
}

# =============================================================================
# MORPHEME DATABASE (validated pharmaceutical terms)
# =============================================================================

MORPHEMES = {
    # Core validated morphemes from ZFD research
    'ol': ('ulje', 'oil'),
    'kost': ('kost', 'bone'),
    'ed': ('korijen', 'root/base'),
    'dain': ('dati', 'give/dose'),
    'daiin': ('dati', 'give/dose'),
    'thor': ('kuhati', 'boil'),
    'kor': ('korijen', 'root'),
    'kar': ('vatra', 'fire/heat'),
    'sol': ('sol', 'salt'),
    'ros': ('ruža', 'rose'),

    # Additional pharmaceutical terms
    'chor': ('kuhati', 'cook/boil'),
    'chol': ('žuč', 'bile/gall'),
    'sho': ('šuti', 'pour'),
    'cho': ('čuvati', 'preserve'),
    'chy': ('čist', 'clean/pure'),
    'tal': ('talog', 'sediment'),
    'dal': ('daljnji', 'further/next'),
    'kal': ('kal', 'mud/clay'),
    'okal': ('okal', 'vessel/container'),
    'qo': ('ko', 'which/who'),
    'qok': ('kok', 'bone/stem'),
    'otch': ('otac', 'father/origin'),
    'fol': ('folija', 'leaf/foil'),
    'cph': ('kupiti', 'buy/gather'),
    'okos': ('oko', 'eye'),
    'koky': ('kuhati', 'to cook'),
    'shoin': ('šuma', 'forest'),
}

# Prefix patterns (operators in pharmaceutical shorthand)
PREFIXES = {
    'o': 'with/of',
    'qo': 'which/that',
    'ko': 'bone/hard',
    'da': 'give/dose',
    'ot': 'from/away',
    'y': 'and/to',
}

# Suffix patterns
SUFFIXES = {
    'y': '-y (adj)',
    'in': '-in (noun)',
    'iin': '-iin (noun.pl)',
    'dy': '-dy (place)',
    'al': '-al (relating to)',
    'ol': '-ol (oil/liquid)',
    'or': '-or (agent)',
}


class TransliterationEngine:
    """Five-layer EVA to Glagolitic/Croatian/English transliterator."""

    def __init__(self):
        # Sort digraphs by length (longest first) for proper matching
        self.digraph_keys = sorted(DIGRAPH_MAP.keys(), key=len, reverse=True)
        self.single_keys = sorted(SINGLE_MAP.keys())

    def eva_to_glagolitic(self, eva_word: str) -> Tuple[str, List[str], float]:
        """
        Convert EVA word to Glagolitic Unicode.

        Processes digraphs before single characters.

        Returns:
            glagolitic: The Glagolitic Unicode string
            unmapped: List of characters that couldn't be mapped
            confidence: Mapping confidence (1.0 = all mapped)
        """
        result = []
        unmapped = []
        i = 0
        eva_lower = eva_word.lower()

        while i < len(eva_lower):
            matched = False

            # Try digraphs first (longest match)
            for digraph in self.digraph_keys:
                if eva_lower[i:].startswith(digraph):
                    result.append(DIGRAPH_MAP[digraph])
                    i += len(digraph)
                    matched = True
                    break

            if not matched:
                # Try single character
                char = eva_lower[i]
                if char in SINGLE_MAP:
                    result.append(SINGLE_MAP[char])
                    matched = True
                elif char in ' .,!?':
                    # Pass through punctuation
                    result.append(char)
                    matched = True
                else:
                    # Unmapped character
                    unmapped.append(char)
                    result.append(f'[?{char}]')

                i += 1

        glagolitic = ''.join(result)
        total_chars = len(eva_lower)
        mapped_chars = total_chars - len(unmapped)
        confidence = mapped_chars / total_chars if total_chars > 0 else 1.0

        return glagolitic, unmapped, confidence

    def glagolitic_to_latin(self, glagolitic: str) -> str:
        """Convert Glagolitic Unicode to Latin transliteration."""
        result = []
        for char in glagolitic:
            if char in GLAGOLITIC_TO_LATIN:
                result.append(GLAGOLITIC_TO_LATIN[char])
            elif char.startswith('[?') and char.endswith(']'):
                # Pass through unmapped markers
                result.append(char)
            else:
                result.append(char)
        return ''.join(result)

    def identify_morphemes(self, eva_word: str, latin: str) -> Tuple[str, str, str]:
        """
        Identify morpheme structure and provide Croatian/English meanings.

        Returns:
            croatian_short: Abbreviated Croatian form
            croatian_expanded: Full Croatian translation
            english: English translation
        """
        eva_lower = eva_word.lower()

        # Check if full word is in morpheme database
        if eva_lower in MORPHEMES:
            cro, eng = MORPHEMES[eva_lower]
            return eva_lower, cro, eng

        # Try to decompose into prefix + stem + suffix
        croatian_parts = []
        english_parts = []
        short_form = eva_lower

        # Check for known prefixes
        prefix_found = ''
        for prefix, meaning in PREFIXES.items():
            if eva_lower.startswith(prefix) and len(eva_lower) > len(prefix):
                prefix_found = prefix
                english_parts.append(meaning)
                break

        # Check for known suffixes
        suffix_found = ''
        for suffix, meaning in SUFFIXES.items():
            if eva_lower.endswith(suffix) and len(eva_lower) > len(suffix):
                suffix_found = suffix
                break

        # Extract stem
        stem = eva_lower
        if prefix_found:
            stem = stem[len(prefix_found):]
        if suffix_found:
            stem = stem[:-len(suffix_found)]

        # Check if stem is a known morpheme
        if stem in MORPHEMES:
            cro, eng = MORPHEMES[stem]
            croatian_parts.append(cro)
            english_parts.append(eng)
        elif stem:
            # Unknown stem - use Latin form
            croatian_parts.append(self.glagolitic_to_latin(
                self.eva_to_glagolitic(stem)[0]
            ))
            english_parts.append(f'[{stem}]')

        # Build output
        if suffix_found:
            english_parts.append(SUFFIXES.get(suffix_found, ''))

        croatian_short = short_form
        croatian_expanded = ' '.join(croatian_parts) if croatian_parts else latin
        english = ' '.join(english_parts) if english_parts else f'[{eva_lower}]'

        return croatian_short, croatian_expanded, english

    def transliterate_word(self, eva_word: str) -> TransliteratedWord:
        """
        Convert EVA word to five-layer transliteration.

        Returns TransliteratedWord with all layers populated.
        """
        # Layer 1: EVA (clean input)
        eva = eva_word.strip()

        # Layer 2: Glagolitic Unicode
        glagolitic, unmapped, confidence = self.eva_to_glagolitic(eva)

        # Layer 3: Latin transliteration
        latin = self.glagolitic_to_latin(glagolitic)

        # Layers 4 & 5: Croatian shorthand, expanded, English
        croatian_short, croatian_expanded, english = self.identify_morphemes(eva, latin)

        return TransliteratedWord(
            eva=eva,
            glagolitic=glagolitic,
            latin=latin,
            croatian_short=croatian_short,
            croatian_expanded=croatian_expanded,
            english=english,
            confidence=confidence,
            unmapped=unmapped
        )

    def transliterate_line(self, eva_line: str) -> List[TransliteratedWord]:
        """
        Transliterate a line of EVA text.

        Splits on spaces, transliterates each word.
        """
        words = eva_line.strip().split()
        return [self.transliterate_word(word) for word in words if word]

    def transliterate_folio(self, folio_data: dict) -> dict:
        """
        Process all lines in a folio.

        Args:
            folio_data: Dict with 'lines' list, each containing 'eva_words'

        Returns:
            Dict with transliterated lines and statistics
        """
        result = {
            'lines': [],
            'statistics': {
                'total_words': 0,
                'high_confidence': 0,    # > 0.8
                'medium_confidence': 0,  # 0.5-0.8
                'low_confidence': 0,     # < 0.5
                'unmapped_chars': []
            }
        }

        for line_data in folio_data.get('lines', []):
            eva_words = line_data.get('eva_words', [])

            transliterated_words = []
            for eva_word in eva_words:
                tw = self.transliterate_word(eva_word)
                transliterated_words.append(tw)

                # Update statistics
                result['statistics']['total_words'] += 1
                if tw.confidence > 0.8:
                    result['statistics']['high_confidence'] += 1
                elif tw.confidence >= 0.5:
                    result['statistics']['medium_confidence'] += 1
                else:
                    result['statistics']['low_confidence'] += 1

                result['statistics']['unmapped_chars'].extend(tw.unmapped)

            # Build layer strings for the line
            line_result = {
                'line_num': line_data.get('line_num', 0),
                'layers': {
                    'eva': ' '.join(tw.eva for tw in transliterated_words),
                    'glagolitic': ' '.join(tw.glagolitic for tw in transliterated_words),
                    'latin': ' '.join(tw.latin for tw in transliterated_words),
                    'croatian_short': ' '.join(tw.croatian_short for tw in transliterated_words),
                    'croatian_expanded': ' '.join(tw.croatian_expanded for tw in transliterated_words),
                },
                'words': [
                    {
                        'eva': tw.eva,
                        'glagolitic': tw.glagolitic,
                        'latin': tw.latin,
                        'confidence': tw.confidence
                    }
                    for tw in transliterated_words
                ],
                'confidence_avg': (
                    sum(tw.confidence for tw in transliterated_words) / len(transliterated_words)
                    if transliterated_words else 0.0
                )
            }
            result['lines'].append(line_result)

        # Deduplicate unmapped chars
        result['statistics']['unmapped_chars'] = list(set(
            result['statistics']['unmapped_chars']
        ))

        return result


def validate_engine():
    """Run validation tests for the transliteration engine."""
    engine = TransliterationEngine()

    print("\n" + "=" * 60)
    print("TRANSLITERATION ENGINE VALIDATION")
    print("=" * 60)

    tests = [
        ('qokol', 'ⰼⱁ', 'ko ligature for q'),
        ('daiin', 'ⰴ', 'contains d mapping'),  # Check lowercase variant
        ('daiin', 'Ⰴ', 'contains D mapping'),  # Or uppercase variant
        ('chtoiin', 'Ⱈ', 'ch digraph first'),
        ('shedy', 'Ⱊ', 'sh digraph'),
        ('cthody', 'ⰽⱅⱈ', 'cth compound gallows'),
    ]

    all_passed = True

    for eva, expected_contains, description in tests:
        result = engine.transliterate_word(eva)
        if expected_contains in result.glagolitic:
            print(f"[PASS] {eva}: contains {expected_contains} ({description})")
        else:
            print(f"[FAIL] {eva}: expected {expected_contains}, got {result.glagolitic}")
            all_passed = False

    # Test unknown character handling
    result = engine.transliterate_word('xyz')
    if '[?x]' in result.glagolitic or '[?z]' in result.glagolitic:
        print("[PASS] Unknown chars produce [?X] markers")
    else:
        print(f"[FAIL] Unknown char handling: {result.glagolitic}")
        all_passed = False

    # Test all 5 layers populated
    result = engine.transliterate_word('daiin')
    layers_ok = all([
        result.eva,
        result.glagolitic,
        result.latin,
        result.croatian_short,
        result.croatian_expanded or result.english
    ])
    if layers_ok:
        print("[PASS] All 5 layers populated")
    else:
        print("[FAIL] Missing layers")
        all_passed = False

    # Print 3 test words with full 5-layer output
    print("\n" + "-" * 60)
    print("SAMPLE 5-LAYER OUTPUT")
    print("-" * 60)

    sample_words = ['daiin', 'qokol', 'chtoiin']
    for eva in sample_words:
        result = engine.transliterate_word(eva)
        print(f"\n{eva}:")
        print(f"  1. EVA:         {result.eva}")
        print(f"  2. Glagolitic:  {result.glagolitic}")
        print(f"  3. Latin:       {result.latin}")
        print(f"  4. Cro short:   {result.croatian_short}")
        print(f"  5. Cro/Eng:     {result.croatian_expanded} / {result.english}")
        print(f"     Confidence:  {result.confidence:.2f}")

    return all_passed


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Glagolitic Transliteration Engine')
    parser.add_argument('--validate', '-v', action='store_true',
                        help='Run validation tests')
    parser.add_argument('--word', '-w', type=str,
                        help='Transliterate a single word')
    parser.add_argument('--line', '-l', type=str,
                        help='Transliterate a line of EVA text')

    args = parser.parse_args()

    engine = TransliterationEngine()

    if args.validate:
        validate_engine()
    elif args.word:
        result = engine.transliterate_word(args.word)
        print(f"EVA:        {result.eva}")
        print(f"Glagolitic: {result.glagolitic}")
        print(f"Latin:      {result.latin}")
        print(f"Croatian:   {result.croatian_short} -> {result.croatian_expanded}")
        print(f"English:    {result.english}")
        print(f"Confidence: {result.confidence:.2f}")
    elif args.line:
        results = engine.transliterate_line(args.line)
        for r in results:
            print(f"{r.eva} -> {r.glagolitic} ({r.confidence:.2f})")
    else:
        # Default: run validation
        validate_engine()


if __name__ == '__main__':
    main()
