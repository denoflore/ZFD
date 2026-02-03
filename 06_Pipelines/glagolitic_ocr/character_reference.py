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


def transliterate_to_croatian(glagolitic_text):
    """Convert Glagolitic text to modern Croatian."""
    result = []
    for char in glagolitic_text:
        if char in GLAGOLITIC_ALPHABET:
            cro = GLAGOLITIC_ALPHABET[char]['croatian']
            result.append(cro)
        else:
            result.append(char)
    return ''.join(result)


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
