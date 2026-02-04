"""
Glagolitic Character Reference Data

Complete Angular Glagolitic alphabet with Unicode points, sounds,
and mappings to EVA transcription system for Voynich comparison.
"""

# Complete Glagolitic Alphabet (Angular/Croatian variant)
GLAGOLITIC_ALPHABET = {
    # Vowels
    'Ⰰ': {
        'unicode': 'U+2C00',
        'name': 'Az',
        'sound': '/a/',
        'ipa': 'a',
        'eva': 'a',
        'croatian': 'a',
        'type': 'vowel',
        'frequency': 'high'
    },
    'Ⰵ': {
        'unicode': 'U+2C05',
        'name': 'Est',
        'sound': '/e/',
        'ipa': 'e',
        'eva': 'e',
        'croatian': 'e',
        'type': 'vowel',
        'frequency': 'high'
    },
    'Ⰹ': {
        'unicode': 'U+2C09',
        'name': 'Izhe',
        'sound': '/i/',
        'ipa': 'i',
        'eva': 'i',
        'croatian': 'i',
        'type': 'vowel',
        'frequency': 'high'
    },
    'Ⱁ': {
        'unicode': 'U+2C11',
        'name': 'On',
        'sound': '/o/',
        'ipa': 'o',
        'eva': 'o',
        'croatian': 'o',
        'type': 'vowel',
        'frequency': 'high'
    },
    'Ⱆ': {
        'unicode': 'U+2C16',
        'name': 'Uk',
        'sound': '/u/',
        'ipa': 'u',
        'eva': None,
        'croatian': 'u',
        'type': 'vowel',
        'frequency': 'medium'
    },
    'Ⱏ': {
        'unicode': 'U+2C1F',
        'name': 'Yat',
        'sound': '/ja/',
        'ipa': 'ja',
        'eva': None,
        'croatian': 'ja/je',
        'type': 'vowel',
        'frequency': 'medium'
    },
    'Ⱍ': {
        'unicode': 'U+2C1D',
        'name': 'Yer',
        'sound': '/ɨ/',
        'ipa': 'ɨ',
        'eva': 'y',
        'croatian': 'i',
        'type': 'vowel',
        'frequency': 'high',
        'note': 'Reduced vowel, often written as y in EVA'
    },

    # Consonants - Stops
    'Ⰱ': {
        'unicode': 'U+2C01',
        'name': 'Buky',
        'sound': '/b/',
        'ipa': 'b',
        'eva': None,
        'croatian': 'b',
        'type': 'consonant',
        'frequency': 'medium'
    },
    'Ⰳ': {
        'unicode': 'U+2C03',
        'name': 'Glagoli',
        'sound': '/g/',
        'ipa': 'g',
        'eva': 'g',
        'croatian': 'g',
        'type': 'consonant',
        'frequency': 'low'
    },
    'Ⰴ': {
        'unicode': 'U+2C04',
        'name': 'Dobro',
        'sound': '/d/',
        'ipa': 'd',
        'eva': 'd',
        'croatian': 'd',
        'type': 'consonant',
        'frequency': 'high'
    },
    'Ⰼ': {
        'unicode': 'U+2C0C',
        'name': 'Kako',
        'sound': '/k/',
        'ipa': 'k',
        'eva': 'k',
        'croatian': 'k',
        'type': 'consonant',
        'frequency': 'high',
        'note': 'Gallows character in EVA'
    },
    'Ⱂ': {
        'unicode': 'U+2C12',
        'name': 'Pokoj',
        'sound': '/p/',
        'ipa': 'p',
        'eva': 'p',
        'croatian': 'p',
        'type': 'consonant',
        'frequency': 'medium',
        'note': 'Gallows character in EVA'
    },
    'Ⱅ': {
        'unicode': 'U+2C15',
        'name': 'Tvrdo',
        'sound': '/t/',
        'ipa': 't',
        'eva': 't',
        'croatian': 't',
        'type': 'consonant',
        'frequency': 'high',
        'note': 'Gallows character in EVA'
    },

    # Consonants - Fricatives
    'Ⰲ': {
        'unicode': 'U+2C02',
        'name': 'Vede',
        'sound': '/v/',
        'ipa': 'v',
        'eva': None,
        'croatian': 'v',
        'type': 'consonant',
        'frequency': 'medium'
    },
    'Ⰶ': {
        'unicode': 'U+2C06',
        'name': 'Zhivete',
        'sound': '/ʒ/',
        'ipa': 'ʒ',
        'eva': None,
        'croatian': 'ž',
        'type': 'consonant',
        'frequency': 'low'
    },
    'Ⰸ': {
        'unicode': 'U+2C08',
        'name': 'Zemlja',
        'sound': '/z/',
        'ipa': 'z',
        'eva': None,
        'croatian': 'z',
        'type': 'consonant',
        'frequency': 'medium'
    },
    'Ⱄ': {
        'unicode': 'U+2C14',
        'name': 'Slovo',
        'sound': '/s/',
        'ipa': 's',
        'eva': 's',
        'croatian': 's',
        'type': 'consonant',
        'frequency': 'high'
    },
    'Ⱇ': {
        'unicode': 'U+2C17',
        'name': 'Frt',
        'sound': '/f/',
        'ipa': 'f',
        'eva': 'f',
        'croatian': 'f',
        'type': 'consonant',
        'frequency': 'low',
        'note': 'Gallows character in EVA'
    },
    'Ⱈ': {
        'unicode': 'U+2C18',
        'name': 'Xer',
        'sound': '/x/',
        'ipa': 'x',
        'eva': 'ch',
        'croatian': 'h',
        'type': 'consonant',
        'frequency': 'medium',
        'note': 'Maps to EVA ch- prefix'
    },
    'Ⱊ': {
        'unicode': 'U+2C1A',
        'name': 'Sha',
        'sound': '/ʃ/',
        'ipa': 'ʃ',
        'eva': 'sh',
        'croatian': 'š',
        'type': 'consonant',
        'frequency': 'medium',
        'note': 'Maps to EVA sh- prefix'
    },

    # Consonants - Affricates
    'Ⰷ': {
        'unicode': 'U+2C07',
        'name': 'Dzelo',
        'sound': '/dz/',
        'ipa': 'dz',
        'eva': None,
        'croatian': 'dz',
        'type': 'consonant',
        'frequency': 'low'
    },
    'Ⱉ': {
        'unicode': 'U+2C19',
        'name': 'Tsi',
        'sound': '/ts/',
        'ipa': 'ts',
        'eva': 'c',
        'croatian': 'c',
        'type': 'consonant',
        'frequency': 'medium'
    },
    'Ⱋ': {
        'unicode': 'U+2C1B',
        'name': 'Chrv',
        'sound': '/tʃ/',
        'ipa': 'tʃ',
        'eva': None,
        'croatian': 'č',
        'type': 'consonant',
        'frequency': 'low'
    },
    'Ⱌ': {
        'unicode': 'U+2C1C',
        'name': 'Shta',
        'sound': '/ʃt/',
        'ipa': 'ʃt',
        'eva': None,
        'croatian': 'št',
        'type': 'consonant',
        'frequency': 'low'
    },

    # Consonants - Sonorants
    'Ⰽ': {
        'unicode': 'U+2C0D',
        'name': 'Ljudie',
        'sound': '/l/',
        'ipa': 'l',
        'eva': 'l',
        'croatian': 'l',
        'type': 'consonant',
        'frequency': 'high'
    },
    'Ⰾ': {
        'unicode': 'U+2C0E',
        'name': 'Myslete',
        'sound': '/m/',
        'ipa': 'm',
        'eva': 'm',
        'croatian': 'm',
        'type': 'consonant',
        'frequency': 'medium'
    },
    'Ⰿ': {
        'unicode': 'U+2C0F',
        'name': 'Nash',
        'sound': '/n/',
        'ipa': 'n',
        'eva': 'n',
        'croatian': 'n',
        'type': 'consonant',
        'frequency': 'high'
    },
    'Ⱃ': {
        'unicode': 'U+2C13',
        'name': 'Rtsi',
        'sound': '/r/',
        'ipa': 'r',
        'eva': 'r',
        'croatian': 'r',
        'type': 'consonant',
        'frequency': 'high'
    },

    # Special characters
    'Ⰺ': {
        'unicode': 'U+2C0A',
        'name': 'I',
        'sound': '/i/',
        'ipa': 'i',
        'eva': 'i',
        'croatian': 'i',
        'type': 'vowel',
        'frequency': 'medium',
        'note': 'Variant of Izhe'
    },
    'Ⰻ': {
        'unicode': 'U+2C0B',
        'name': 'Djerv',
        'sound': '/dʒ/',
        'ipa': 'dʒ',
        'eva': None,
        'croatian': 'đ',
        'type': 'consonant',
        'frequency': 'low'
    },
    'Ⱎ': {
        'unicode': 'U+2C1E',
        'name': 'Yeri',
        'sound': '/ɨ/',
        'ipa': 'ɨ',
        'eva': 'y',
        'croatian': 'i',
        'type': 'vowel',
        'frequency': 'low'
    },
    'Ⱐ': {
        'unicode': 'U+2C20',
        'name': 'Yo',
        'sound': '/jo/',
        'ipa': 'jo',
        'eva': None,
        'croatian': 'jo',
        'type': 'vowel',
        'frequency': 'low'
    },
    'Ⱑ': {
        'unicode': 'U+2C21',
        'name': 'Yu',
        'sound': '/ju/',
        'ipa': 'ju',
        'eva': None,
        'croatian': 'ju',
        'type': 'vowel',
        'frequency': 'low'
    },
}

# EVA to Glagolitic reverse mapping
EVA_TO_GLAGOLITIC = {
    char_data['eva']: char
    for char, char_data in GLAGOLITIC_ALPHABET.items()
    if char_data['eva'] is not None
}

# Characters with EVA equivalents (important for Voynich comparison)
VOYNICH_RELEVANT_CHARS = {
    char: data for char, data in GLAGOLITIC_ALPHABET.items()
    if data['eva'] is not None
}

# Gallows characters in EVA (structural importance in Voynich)
GALLOWS_MAPPING = {
    'k': 'Ⰼ',  # Kako
    't': 'Ⱅ',  # Tvrdo
    'f': 'Ⱇ',  # Frt
    'p': 'Ⱂ',  # Pokoj
}

# Common abbreviation marks in medieval Glagolitic
ABBREVIATION_MARKS = {
    'titlo': {
        'description': 'Overline mark indicating abbreviation',
        'usage': 'Placed over abbreviated words, especially nomina sacra',
        'voynich_parallel': 'Gallows may function similarly'
    },
    'superscript': {
        'description': 'Letters written above baseline',
        'usage': 'Indicate omitted letters in abbreviation',
        'voynich_parallel': 'Some EVA glyphs may be superscript indicators'
    },
    'contraction': {
        'description': 'Omission of middle letters',
        'usage': 'Common in liturgical manuscripts',
        'voynich_parallel': 'May explain missing vowels in some words'
    }
}

# Ligatures common in Angular Glagolitic
COMMON_LIGATURES = {
    'qo': {
        'glagolitic': 'Ⰼ+Ⱁ',  # k + o
        'sound': '/ko/',
        'eva': 'qo',
        'meaning': 'Relative pronoun "which, who"',
        'note': 'Very common prefix in Voynich'
    },
    'st': {
        'glagolitic': 'Ⱄ+Ⱅ',  # s + t
        'sound': '/st/',
        'eva': 'kt',  # or represented by gallows
        'meaning': 'Common cluster',
        'note': 'May be represented by single glyph'
    }
}


def get_char_by_eva(eva_code):
    """Get Glagolitic character data by EVA code."""
    return EVA_TO_GLAGOLITIC.get(eva_code)


def get_char_by_unicode(unicode_point):
    """Get Glagolitic character data by Unicode point."""
    for char, data in GLAGOLITIC_ALPHABET.items():
        if data['unicode'] == unicode_point:
            return char, data
    return None, None


def get_vowels():
    """Get all vowel characters."""
    return {c: d for c, d in GLAGOLITIC_ALPHABET.items() if d['type'] == 'vowel'}


def get_consonants():
    """Get all consonant characters."""
    return {c: d for c, d in GLAGOLITIC_ALPHABET.items() if d['type'] == 'consonant'}


def transliterate_to_eva(glagolitic_text):
    """Convert Glagolitic text to EVA transcription."""
    result = []
    for char in glagolitic_text:
        if char in GLAGOLITIC_ALPHABET:
            eva = GLAGOLITIC_ALPHABET[char]['eva']
            if eva:
                result.append(eva)
            else:
                result.append('?')  # No EVA equivalent
        else:
            result.append(char)  # Pass through non-Glagolitic
    return ''.join(result)


def normalize_glagolitic(char):
    """
    Normalize Glagolitic character to uppercase (canonical form).

    Glagolitic Unicode ranges:
    - Uppercase: U+2C00 to U+2C2E
    - Lowercase: U+2C30 to U+2C5E

    The lowercase codepoint is exactly 0x30 (48) higher than uppercase.
    """
    code = ord(char)
    # Check if in lowercase Glagolitic range
    if 0x2C30 <= code <= 0x2C5E:
        # Convert to uppercase by subtracting 0x30
        return chr(code - 0x30)
    return char


def transliterate_to_croatian(glagolitic_text):
    """
    Convert Glagolitic text to modern Croatian phonemic representation.

    Phase 4 of the pipeline: Glagolitic Unicode -> Croatian phonemes.
    Handles both uppercase and lowercase Glagolitic by normalizing to uppercase.
    """
    result = []
    for char in glagolitic_text:
        # Normalize lowercase Glagolitic to uppercase
        normalized = normalize_glagolitic(char)
        if normalized in GLAGOLITIC_ALPHABET:
            cro = GLAGOLITIC_ALPHABET[normalized]['croatian']
            result.append(cro)
        else:
            # Pass through non-Glagolitic characters (spaces, punctuation, etc.)
            result.append(char)
    return ''.join(result)


# Morpheme database for Phase 5 reconstruction
CROATIAN_MORPHEMES = {
    # Ingredient stems
    'ol': {'croatian': 'ulje', 'english': 'oil', 'category': 'ingredient'},
    'or': {'croatian': 'ulje', 'english': 'oil', 'category': 'ingredient'},
    'kost': {'croatian': 'kost', 'english': 'bone', 'category': 'ingredient'},
    'sal': {'croatian': 'sol', 'english': 'salt', 'category': 'ingredient'},
    'sar': {'croatian': 'sol', 'english': 'salt', 'category': 'ingredient'},
    'ar': {'croatian': 'voda', 'english': 'water', 'category': 'ingredient'},
    'ros': {'croatian': 'ruza', 'english': 'rose', 'category': 'ingredient'},
    'stor': {'croatian': 'storaks', 'english': 'storax', 'category': 'ingredient'},
    'ed': {'croatian': 'korijen', 'english': 'root', 'category': 'ingredient'},
    'edy': {'croatian': 'korijen', 'english': 'root', 'category': 'ingredient'},

    # Method stems
    'hor': {'croatian': 'kuhati', 'english': 'cook/boil', 'category': 'method'},
    'hol': {'croatian': 'mijesati', 'english': 'mix/combine', 'category': 'method'},
    'dal': {'croatian': 'zatim', 'english': 'then/next', 'category': 'method'},
    'dar': {'croatian': 'dati', 'english': 'give/dose', 'category': 'method'},
    'dain': {'croatian': 'dati', 'english': 'give/dose', 'category': 'method'},
    'daiin': {'croatian': 'dati', 'english': 'give/dose', 'category': 'method'},
    'sol': {'croatian': 'natopiti', 'english': 'soak', 'category': 'method'},

    # Operators (prefixes)
    'ko': {'croatian': 'koji', 'english': 'which/who', 'category': 'operator'},
    'o': {'croatian': 'o', 'english': 'about', 'category': 'operator'},
    's': {'croatian': 's', 'english': 'with', 'category': 'operator'},

    # Latin terms
    'oral': {'croatian': 'oralno', 'english': 'by mouth', 'category': 'latin'},
}


def phonemic_to_croatian(phonemic_text):
    """
    Convert Croatian phonemic representation to readable Croatian.

    Phase 5 of the pipeline: Croatian phonemes -> readable Croatian words.
    Identifies known morphemes and expands them to full Croatian words.
    """
    words = phonemic_text.split()
    result = []

    for word in words:
        # Check if the word matches a known morpheme
        word_lower = word.lower()

        # Try exact match first
        if word_lower in CROATIAN_MORPHEMES:
            morpheme = CROATIAN_MORPHEMES[word_lower]
            result.append(morpheme['croatian'])
            continue

        # Try to identify morphemes within the word
        expanded = expand_word(word_lower)
        result.append(expanded)

    return ' '.join(result)


def expand_word(word):
    """
    Expand a Croatian phonemic word by identifying morphemes.

    Uses the operator-stem-suffix model from the character map:
    - Check for operator prefixes (ko-, o-, s-)
    - Identify stem morphemes (ol, kost, sal, etc.)
    - Handle suffixes
    """
    if not word:
        return word

    result_parts = []
    remaining = word

    # Check for operator prefixes
    for op in ['ko', 'o', 's']:
        if remaining.startswith(op) and len(remaining) > len(op):
            if op in CROATIAN_MORPHEMES:
                result_parts.append(CROATIAN_MORPHEMES[op]['croatian'])
                remaining = remaining[len(op):]
            break

    # Look for known stems in the remaining text
    found_stem = False
    for stem in sorted(CROATIAN_MORPHEMES.keys(), key=len, reverse=True):
        if stem in remaining and CROATIAN_MORPHEMES[stem]['category'] in ['ingredient', 'method']:
            morpheme = CROATIAN_MORPHEMES[stem]
            # Replace stem with Croatian equivalent
            remaining = remaining.replace(stem, morpheme['croatian'], 1)
            found_stem = True
            break

    if result_parts:
        return '-'.join(result_parts) + '-' + remaining if remaining else '-'.join(result_parts)
    return remaining


def full_transliterate(glagolitic_text):
    """
    Full pipeline: Glagolitic -> Croatian phonemic -> readable Croatian.

    Combines Phase 4 and Phase 5 for complete translation.
    Returns a dict with all layers.
    """
    # Phase 4: Glagolitic to Croatian phonemic
    phonemic = transliterate_to_croatian(glagolitic_text)

    # Phase 5: Phonemic to readable Croatian
    readable = phonemic_to_croatian(phonemic)

    return {
        'glagolitic': glagolitic_text,
        'phonemic': phonemic,
        'croatian': readable
    }


if __name__ == '__main__':
    # Print character reference
    print("Glagolitic Alphabet Reference")
    print("=" * 60)

    print("\n## Vowels")
    for char, data in get_vowels().items():
        eva = data['eva'] or '-'
        print(f"  {char} ({data['name']}): {data['sound']} -> EVA: {eva}")

    print("\n## Consonants")
    for char, data in get_consonants().items():
        eva = data['eva'] or '-'
        print(f"  {char} ({data['name']}): {data['sound']} -> EVA: {eva}")

    print("\n## Voynich-Relevant Characters (have EVA mapping)")
    for char, data in VOYNICH_RELEVANT_CHARS.items():
        print(f"  {char} ({data['name']}): {data['sound']} = EVA '{data['eva']}'")

    print(f"\nTotal characters: {len(GLAGOLITIC_ALPHABET)}")
    print(f"With EVA mapping: {len(VOYNICH_RELEVANT_CHARS)}")
