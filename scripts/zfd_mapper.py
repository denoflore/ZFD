#!/usr/bin/env python3
"""
ZFD Character Mapper - EVA to Croatian orthography conversion
Based on the Glagolitic Shorthand Character Map v1.0

Applies the three-layer system:
1. OPERATORS (word-initial) → Prefixes/prepositions
2. ABBREVIATION MARKS (medial gallows) → Consonant clusters
3. STEMS + SUFFIXES → Root morphemes + grammatical endings
"""

import re


def map_eva_to_croatian(eva_word):
    """
    Convert a single EVA word to Croatian orthography.
    Applies ZFD mapping rules in correct order.
    """
    word = eva_word.lower().strip()
    if not word:
        return ''

    result = ''
    i = 0

    # =========================================================================
    # PHASE 1: Word-Initial Operators
    # =========================================================================
    if word.startswith('qo'):
        result += 'ko'
        i = 2
    elif word.startswith('q'):
        result += 'k'
        i = 1
    elif word.startswith('ch'):
        result += 'h'
        i = 2
    elif word.startswith('sh'):
        result += 'š'
        i = 2

    # =========================================================================
    # PHASE 2: Process remaining characters
    # =========================================================================
    while i < len(word):
        # Check for multi-character sequences first (longest match)

        # Look ahead for digraphs/trigraphs
        remaining = word[i:]

        # Suffix patterns (check at end of word)
        if i == len(word) - 4 and remaining == 'aiin':
            result += 'ain'
            break
        if i == len(word) - 3 and remaining == 'iin':
            result += 'in'
            break
        if i == len(word) - 3 and remaining == 'eey':
            result += 'ei'
            break
        if i == len(word) - 3 and remaining == 'edy':
            result += 'edi'
            break

        # Check 2-character sequences
        if i + 1 < len(word):
            pair = word[i:i+2]

            # Mid-word digraphs
            if pair == 'ch':
                result += 'h'
                i += 2
                continue
            elif pair == 'sh':
                result += 'š'
                i += 2
                continue
            elif pair == 'ck':
                result += 'cst'
                i += 2
                continue
            elif pair == 'ct':
                result += 'ctr'
                i += 2
                continue
            # Vowel sequences
            elif pair == 'ee':
                result += 'e'
                i += 2
                continue
            elif pair == 'ii':
                result += 'i'
                i += 2
                continue
            elif pair == 'ai':
                result += 'ai'
                i += 2
                continue
            elif pair == 'oi':
                result += 'oi'
                i += 2
                continue

        # Single character mappings
        c = word[i]

        # Gallows → Consonant clusters (ABBREVIATION MARKS)
        if c == 'k':
            result += 'st'
        elif c == 't':
            result += 'tr'
        elif c == 'f':
            result += 'pr'
        elif c == 'p':
            result += 'pl'

        # Vowels (pass through)
        elif c in 'oeia':
            result += c

        # Suffix consonants
        elif c == 'y':
            result += 'i'
        elif c in 'nrlm':
            result += c

        # Other consonants
        elif c == 'd':
            result += 'd'
        elif c == 's':
            result += 's'
        elif c == 'c':
            result += 'c'
        elif c == 'g':
            result += 'g'

        # 'h' - usually part of digraph, but keep if standalone
        elif c == 'h':
            result += 'h'

        # Unknown - pass through
        else:
            result += c

        i += 1

    return result


def map_line(eva_line):
    """
    Convert a full line of EVA text to Croatian.
    Preserves word boundaries and punctuation.
    """
    # Remove markup tags like <!plant>, <$>, <->, etc.
    clean = re.sub(r'<[^>]+>', '', eva_line)

    # Split into words (on dots and spaces)
    words = re.split(r'([.\s]+)', clean)

    result = []
    for part in words:
        if re.match(r'^[.\s]+$', part):
            # Preserve separators
            result.append(part.replace('.', ' '))
        else:
            # Clean and convert word
            word = re.sub(r'[^a-z]', '', part.lower())
            if word:
                result.append(map_eva_to_croatian(word))

    return ''.join(result).strip()


def convert_folio(eva_data):
    """
    Convert a full folio's data to Croatian.

    Input: {'labels': [...], 'text': [...]}
    Output: {'labels': [...], 'text': [...]} in Croatian
    """
    croatian = {
        'labels': [],
        'text': []
    }

    for label in eva_data.get('labels', []):
        croatian['labels'].append(map_line(label))

    for text in eva_data.get('text', []):
        croatian['text'].append(map_line(text))

    return croatian


# =============================================================================
# TEST CASES
# =============================================================================

TEST_CASES = [
    ('qokeedy', 'kostedi'),      # Contains "kost" (bone)
    ('daiin', 'dain'),           # "given"
    ('chedy', 'hedi'),           # h-ed-i
    ('shedy', 'šedi'),           # š-ed-i
    ('qokain', 'kostain'),       # kost-ain
    ('otedy', 'otredi'),         # o-tr-ed-i
    ('chol', 'hol'),             # h-ol
    ('shol', 'šol'),             # š-ol
    ('ol', 'ol'),                # oil
    ('dar', 'dar'),              # gift
    ('qokeey', 'kostei'),        # kost-ei
    ('aiin', 'ain'),             # -ain ending
    ('okaiin', 'ostain'),        # o-st-ain
]


def run_tests():
    """Run all test cases."""
    print("ZFD Mapper - Test Cases")
    print("=" * 50)

    passed = 0
    failed = 0

    for eva, expected in TEST_CASES:
        result = map_eva_to_croatian(eva)
        status = '✓' if result == expected else '✗'

        if result == expected:
            passed += 1
        else:
            failed += 1
            print(f"{status} {eva} → {result} (expected: {expected})")

    print(f"\nResults: {passed}/{len(TEST_CASES)} passed")

    if failed == 0:
        print("All tests passed!")
    else:
        print(f"{failed} tests failed")

    return failed == 0


if __name__ == "__main__":
    run_tests()
