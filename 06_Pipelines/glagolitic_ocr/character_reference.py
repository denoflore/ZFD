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
"""
CROATIAN_MORPHEMES - auto-generated from unified_lexicon_v3.json
Canonical source: zfd_decoder/data/lexicon_v2.csv
Total entries: 319 (was 21 before audit)
Last rebuilt: 2026-02-06
"""
CROATIAN_MORPHEMES = {
    # --- action (36) ---
    'add': {'croatian': 'dodati', 'english': 'add/include', 'category': 'action', 'confidence': 'MISCELLANY'},
    'amar': {'croatian': 'gorak', 'english': 'bitter herb', 'category': 'action', 'confidence': 'CANDIDATE'},
    'appon': {'croatian': 'staviti', 'english': 'apply/place on', 'category': 'action', 'confidence': 'MISCELLANY'},
    'bib': {'croatian': 'piti', 'english': 'drink/consume', 'category': 'action', 'confidence': 'MISCELLANY'},
    'calc': {'croatian': 'vapno', 'english': 'lime/ite', 'category': 'action', 'confidence': 'CANDIDATE'},
    'char': {'croatian': 'vatra', 'english': 'fire/heat', 'category': 'action', 'confidence': 'CANDIDATE'},
    'chor': {'croatian': 'kuhati', 'english': 'cook/combine', 'category': 'action', 'confidence': 'CONFIRMED'},
    'col': {'croatian': 'procijediti', 'english': 'strain/filter', 'category': 'action', 'confidence': 'MISCELLANY'},
    'comed': {'croatian': 'jesti', 'english': 'eat/consume', 'category': 'action', 'confidence': 'MISCELLANY'},
    'contund': {'croatian': 'stuci', 'english': 'crush/pound', 'category': 'action', 'confidence': 'MISCELLANY'},
    'distil': {'croatian': 'destilirati', 'english': 'distill', 'category': 'action', 'confidence': 'MISCELLANY'},
    'fric': {'croatian': 'trljati', 'english': 'rub/massage', 'category': 'action', 'confidence': 'MISCELLANY'},
    'hor': {'croatian': 'kuhati', 'english': 'cook/combine', 'category': 'action', 'confidence': 'CONFIRMED'},
    'infund': {'croatian': 'uliti', 'english': 'infuse/steep', 'category': 'action', 'confidence': 'MISCELLANY'},
    'instil': {'croatian': 'ukapati', 'english': 'instill/drop in', 'category': 'action', 'confidence': 'MISCELLANY'},
    'kair': {'croatian': 'vatra', 'english': 'fire/heat', 'category': 'action', 'confidence': 'CANDIDATE'},
    'kar': {'croatian': 'vatra', 'english': 'fire/heat', 'category': 'action', 'confidence': 'CANDIDATE'},
    'lav': {'croatian': 'oprati', 'english': 'wash/cleanse', 'category': 'action', 'confidence': 'MISCELLANY'},
    'maži': {'croatian': 'maži', 'english': 'unge', 'category': 'action', 'confidence': 'CONFIRMED'},
    'misc': {'croatian': 'mijesati', 'english': 'mix/blend', 'category': 'action', 'confidence': 'MISCELLANY'},
    'operi': {'croatian': 'operi', 'english': 'lava', 'category': 'action', 'confidence': 'CONFIRMED'},
    'pij': {'croatian': 'pij', 'english': 'bibe', 'category': 'action', 'confidence': 'CONFIRMED'},
    'pon': {'croatian': 'staviti', 'english': 'place/put', 'category': 'action', 'confidence': 'MISCELLANY'},
    'recip': {'croatian': 'uzeti', 'english': 'take (imperative)', 'category': 'action', 'confidence': 'MISCELLANY'},
    'satri': {'croatian': 'satri', 'english': 'tere', 'category': 'action', 'confidence': 'CONFIRMED'},
    'shor': {'croatian': 'natopiti', 'english': 'soak/infuse', 'category': 'action', 'confidence': 'CONFIRMED'},
    'stavi': {'croatian': 'stavi', 'english': 'appone', 'category': 'action', 'confidence': 'CONFIRMED'},
    'syr': {'croatian': 'sirup', 'english': 'syrup/potion', 'category': 'action', 'confidence': 'CANDIDATE'},
    'ter': {'croatian': 'satrti', 'english': 'grind/crush', 'category': 'action', 'confidence': 'MISCELLANY'},
    'thor': {'croatian': 'vreti', 'english': 'boil/roast', 'category': 'action', 'confidence': 'CANDIDATE'},
    'tror': {'croatian': 'vreti', 'english': 'boil/roast', 'category': 'action', 'confidence': 'CANDIDATE'},
    'ung': {'croatian': 'namazati', 'english': 'anoint/rub', 'category': 'action', 'confidence': 'MISCELLANY'},
    'uzmi': {'croatian': 'uzmi', 'english': 'recipe', 'category': 'action', 'confidence': 'CONFIRMED'},
    'ykal': {'croatian': 'juha', 'english': 'broth/decoction', 'category': 'action', 'confidence': 'CANDIDATE'},
    'šol': {'croatian': 'namočiti', 'english': 'soak in oil', 'category': 'action', 'confidence': 'CONFIRMED'},
    'šor': {'croatian': 'natopiti', 'english': 'soak/infuse', 'category': 'action', 'confidence': 'CONFIRMED'},
    # --- animal (1) ---
    'kosti': {'croatian': 'kosti', 'english': 'Bone + state', 'category': 'animal', 'confidence': 'CONFIRMED'},
    # --- body (13) ---
    'glav': {'croatian': 'glava', 'english': 'head', 'category': 'body', 'confidence': 'CONFIRMED'},
    'glava': {'croatian': 'glava', 'english': 'caput', 'category': 'body', 'confidence': 'CONFIRMED'},
    'jetr': {'croatian': 'jetra', 'english': 'liver', 'category': 'body', 'confidence': 'CONFIRMED'},
    'koža': {'croatian': 'koža', 'english': 'cutis', 'category': 'body', 'confidence': 'CONFIRMED'},
    'krv': {'croatian': 'krv', 'english': 'sanguis', 'category': 'body', 'confidence': 'CONFIRMED'},
    'oko': {'croatian': 'oko', 'english': 'eye', 'category': 'body', 'confidence': 'CONFIRMED'},
    'oči': {'croatian': 'oči', 'english': 'oculi', 'category': 'body', 'confidence': 'CONFIRMED'},
    'rana': {'croatian': 'rana', 'english': 'wound', 'category': 'body', 'confidence': 'CONFIRMED'},
    'rane': {'croatian': 'rane', 'english': 'vulnera', 'category': 'body', 'confidence': 'CONFIRMED'},
    'src': {'croatian': 'srce', 'english': 'heart', 'category': 'body', 'confidence': 'CONFIRMED'},
    'zubi': {'croatian': 'zubi', 'english': 'dentes', 'category': 'body', 'confidence': 'CONFIRMED'},
    'želud': {'croatian': 'želudac', 'english': 'stomach', 'category': 'body', 'confidence': 'CONFIRMED'},
    'žuč': {'croatian': 'žuč', 'english': 'bile', 'category': 'body', 'confidence': 'CONFIRMED'},
    # --- body_part (22) ---
    'aur': {'croatian': 'uho', 'english': 'ear', 'category': 'body_part', 'confidence': 'MISCELLANY'},
    'caput': {'croatian': 'glava', 'english': 'head', 'category': 'body_part', 'confidence': 'MISCELLANY'},
    'cor': {'croatian': 'srce', 'english': 'heart', 'category': 'body_part', 'confidence': 'MISCELLANY'},
    'dent': {'croatian': 'zub', 'english': 'tooth', 'category': 'body_part', 'confidence': 'MISCELLANY'},
    'dors': {'croatian': 'ledja', 'english': 'back', 'category': 'body_part', 'confidence': 'MISCELLANY'},
    'fac': {'croatian': 'lice', 'english': 'face', 'category': 'body_part', 'confidence': 'MISCELLANY'},
    'fauces': {'croatian': 'grlo', 'english': 'throat/fauces', 'category': 'body_part', 'confidence': 'MISCELLANY'},
    'hepat': {'croatian': 'jetra', 'english': 'liver', 'category': 'body_part', 'confidence': 'MISCELLANY'},
    'iunct': {'croatian': 'zglob', 'english': 'joint', 'category': 'body_part', 'confidence': 'MISCELLANY'},
    'lingu': {'croatian': 'jezik', 'english': 'tongue', 'category': 'body_part', 'confidence': 'MISCELLANY'},
    'mamm': {'croatian': 'dojka', 'english': 'breast', 'category': 'body_part', 'confidence': 'MISCELLANY'},
    'matr': {'croatian': 'maternica', 'english': 'womb', 'category': 'body_part', 'confidence': 'MISCELLANY'},
    'membr': {'croatian': 'ud', 'english': 'limb', 'category': 'body_part', 'confidence': 'MISCELLANY'},
    'nerv': {'croatian': 'zivac', 'english': 'nerve/sinew', 'category': 'body_part', 'confidence': 'MISCELLANY'},
    'ocul': {'croatian': 'oko', 'english': 'eye', 'category': 'body_part', 'confidence': 'MISCELLANY'},
    'pulm': {'croatian': 'pluca', 'english': 'lung', 'category': 'body_part', 'confidence': 'MISCELLANY'},
    'ren': {'croatian': 'bubreg', 'english': 'kidney', 'category': 'body_part', 'confidence': 'MISCELLANY'},
    'splen': {'croatian': 'slezena', 'english': 'spleen', 'category': 'body_part', 'confidence': 'MISCELLANY'},
    'stomac': {'croatian': 'zeludac', 'english': 'stomach', 'category': 'body_part', 'confidence': 'MISCELLANY'},
    'ventr': {'croatian': 'trbuh', 'english': 'belly', 'category': 'body_part', 'confidence': 'MISCELLANY'},
    'vesic': {'croatian': 'mjehur', 'english': 'bladder', 'category': 'body_part', 'confidence': 'MISCELLANY'},
    'vuln': {'croatian': 'rana', 'english': 'wound', 'category': 'body_part', 'confidence': 'MISCELLANY'},
    # --- condition (10) ---
    'adustio': {'croatian': 'opeklina', 'english': 'burn', 'category': 'condition', 'confidence': 'MISCELLANY'},
    'dysent': {'croatian': 'dizenterija', 'english': 'dysentery', 'category': 'condition', 'confidence': 'MISCELLANY'},
    'febr': {'croatian': 'groznica', 'english': 'fever', 'category': 'condition', 'confidence': 'MISCELLANY'},
    'flux': {'croatian': 'tok', 'english': 'flux/flow', 'category': 'condition', 'confidence': 'MISCELLANY'},
    'hern': {'croatian': 'kila', 'english': 'hernia', 'category': 'condition', 'confidence': 'MISCELLANY'},
    'lapis': {'croatian': 'kamen', 'english': 'stone (kidney)', 'category': 'condition', 'confidence': 'MISCELLANY'},
    'podag': {'croatian': 'kostobolja', 'english': 'gout', 'category': 'condition', 'confidence': 'MISCELLANY'},
    'tumor': {'croatian': 'oteklina', 'english': 'swelling/tumor', 'category': 'condition', 'confidence': 'MISCELLANY'},
    'tuss': {'croatian': 'kasalj', 'english': 'cough', 'category': 'condition', 'confidence': 'MISCELLANY'},
    'vertig': {'croatian': 'vrtoglavica', 'english': 'vertigo/dizziness', 'category': 'condition', 'confidence': 'MISCELLANY'},
    # --- equipment (8) ---
    'kal': {'croatian': 'kotao', 'english': 'cauldron', 'category': 'equipment', 'confidence': 'CANDIDATE'},
    'okal': {'croatian': 'lonac', 'english': 'pot/jar', 'category': 'equipment', 'confidence': 'CONFIRMED'},
    'okar': {'croatian': 'lonac', 'english': 'pot/jar', 'category': 'equipment', 'confidence': 'CONFIRMED'},
    'ostal': {'croatian': 'lonac', 'english': 'pot/jar', 'category': 'equipment', 'confidence': 'CONFIRMED'},
    'ostar': {'croatian': 'lonac', 'english': 'pot/jar', 'category': 'equipment', 'confidence': 'CONFIRMED'},
    'otal': {'croatian': 'lonac', 'english': 'pot/jar', 'category': 'equipment', 'confidence': 'CONFIRMED'},
    'phar': {'croatian': 'bocica', 'english': 'flask/phial', 'category': 'equipment', 'confidence': 'CANDIDATE'},
    'stal': {'croatian': 'kotao', 'english': 'cauldron', 'category': 'equipment', 'confidence': 'CANDIDATE'},
    # --- general (42) ---
    'ambra': {'croatian': 'ambra', 'english': 'Ambergris', 'category': 'general', 'confidence': 'CONFIRMED'},
    'asaf': {'croatian': 'asaf', 'english': 'Asafoetida', 'category': 'general', 'confidence': 'CANDIDATE'},
    'asafor': {'croatian': 'asafor', 'english': 'Asafoetida (variant)', 'category': 'general', 'confidence': 'CANDIDATE'},
    'asafot': {'croatian': 'asafot', 'english': 'Asafoetida (full)', 'category': 'general', 'confidence': 'CANDIDATE'},
    'axor': {'croatian': 'axor', 'english': 'Lard (variant)', 'category': 'general', 'confidence': 'CONFIRMED'},
    'axun': {'croatian': 'axun', 'english': 'Lard / animal fat', 'category': 'general', 'confidence': 'CONFIRMED'},
    'calide': {'croatian': 'calide', 'english': 'warm', 'category': 'general', 'confidence': 'CONFIRMED'},
    'case': {'croatian': 'case', 'english': 'Cheese / curd', 'category': 'general', 'confidence': 'CONFIRMED'},
    'cera': {'croatian': 'cera', 'english': 'Wax', 'category': 'general', 'confidence': 'CONFIRMED'},
    'cholal': {'croatian': 'cholal', 'english': 'ch + ol + al', 'category': 'general', 'confidence': 'CONFIRMED'},
    'coral': {'croatian': 'coral', 'english': 'Coral', 'category': 'general', 'confidence': 'CONFIRMED'},
    'csth': {'croatian': 'csth', 'english': 'Complex cluster', 'category': 'general', 'confidence': 'CANDIDATE'},
    'ctr': {'croatian': 'ctr', 'english': 'Center / control', 'category': 'general', 'confidence': 'CANDIDATE'},
    'cuper': {'croatian': 'cuper', 'english': 'Copper / verdigris', 'category': 'general', 'confidence': 'CONFIRMED'},
    'daiin': {'croatian': 'daiin', 'english': 'Add (extended)', 'category': 'general', 'confidence': 'CANDIDATE'},
    'darar': {'croatian': 'darar', 'english': 'da + ar + ar', 'category': 'general', 'confidence': 'CONFIRMED'},
    'ed': {'croatian': 'ed', 'english': '"Process kernel / do / treat"', 'category': 'general', 'confidence': 'CONFIRMED'},
    'ee': {'croatian': 'ee', 'english': '(intensifier)', 'category': 'general', 'confidence': 'CONFIRMED'},
    'fair': {'croatian': 'fair', 'english': 'Fire (variant)', 'category': 'general', 'confidence': 'CANDIDATE'},
    'fiat': {'croatian': 'fiat', 'english': 'let be made', 'category': 'general', 'confidence': 'CONFIRMED'},
    'hctr': {'croatian': 'hctr', 'english': 'Heated-center compound', 'category': 'general', 'confidence': 'CANDIDATE'},
    'ivor': {'croatian': 'ivor', 'english': 'Ivory (dust)', 'category': 'general', 'confidence': 'CONFIRMED'},
    'laco': {'croatian': 'laco', 'english': 'Milk (extended)', 'category': 'general', 'confidence': 'CONFIRMED'},
    'mane': {'croatian': 'mane', 'english': 'in the morning', 'category': 'general', 'confidence': 'CONFIRMED'},
    'melk': {'croatian': 'melk', 'english': 'Butter / clarified fat', 'category': 'general', 'confidence': 'CANDIDATE'},
    'musc': {'croatian': 'musc', 'english': 'Musk', 'category': 'general', 'confidence': 'CONFIRMED'},
    'myrrh': {'croatian': 'myrrh', 'english': 'Myrrh (full)', 'category': 'general', 'confidence': 'CONFIRMED'},
    'nard': {'croatian': 'nard', 'english': 'Spikenard', 'category': 'general', 'confidence': 'CONFIRMED'},
    'nardi': {'croatian': 'nardi', 'english': 'Spikenard (genitive)', 'category': 'general', 'confidence': 'CONFIRMED'},
    'nardor': {'croatian': 'nardor', 'english': 'Spikenard (extended)', 'category': 'general', 'confidence': 'CONFIRMED'},
    'okeey': {'croatian': 'okeey', 'english': 'ok + ee + y', 'category': 'general', 'confidence': 'CONFIRMED'},
    'ova': {'croatian': 'ova', 'english': 'Egg / yolk', 'category': 'general', 'confidence': 'CONFIRMED'},
    'perla': {'croatian': 'perla', 'english': 'Pearl (ground)', 'category': 'general', 'confidence': 'CONFIRMED'},
    'qokaldy': {'croatian': 'qokaldy', 'english': 'qo + kal + dy', 'category': 'general', 'confidence': 'CONFIRMED'},
    'shedy': {'croatian': 'shedy', 'english': 'sh + ed + y', 'category': 'general', 'confidence': 'CONFIRMED'},
    'st': {'croatian': 'st', 'english': 'Stand / place / position', 'category': 'general', 'confidence': 'CANDIDATE'},
    'syrop': {'croatian': 'syrop', 'english': 'Syrup / potion (full)', 'category': 'general', 'confidence': 'CANDIDATE'},
    'tr': {'croatian': 'tr', 'english': 'Through / trans', 'category': 'general', 'confidence': 'CANDIDATE'},
    'ty': {'croatian': 'ty', 'english': 'Preposition: in/with', 'category': 'general', 'confidence': 'CANDIDATE'},
    'valet': {'croatian': 'valet', 'english': 'it is effective', 'category': 'general', 'confidence': 'CONFIRMED'},
    'vinor': {'croatian': 'vinor', 'english': 'Wine (extended)', 'category': 'general', 'confidence': 'CONFIRMED'},
    'zinger': {'croatian': 'zinger', 'english': 'Ginger (full)', 'category': 'general', 'confidence': 'CONFIRMED'},
    # --- grammar (30) ---
    'ain': {'croatian': 'stvar', 'english': 'substance/thing', 'category': 'grammar', 'confidence': 'CONFIRMED'},
    'bol': {'croatian': 'bol', 'english': 'pain/ache', 'category': 'grammar', 'confidence': 'CANDIDATE'},
    'cum': {'croatian': 's/sa', 'english': 'with', 'category': 'grammar', 'confidence': 'MISCELLANY'},
    'dain': {'croatian': 'dati', 'english': 'given/added', 'category': 'grammar', 'confidence': 'CONFIRMED'},
    'dan': {'croatian': 'dan', 'english': 'day', 'category': 'grammar', 'confidence': 'CONFIRMED'},
    'dar': {'croatian': 'dar', 'english': 'gift', 'category': 'grammar', 'confidence': 'CONFIRMED'},
    'eos': {'croatian': 'ih', 'english': 'them/those', 'category': 'grammar', 'confidence': 'CANDIDATE'},
    'eoy': {'croatian': 'tim', 'english': 'by/from that', 'category': 'grammar', 'confidence': 'CANDIDATE'},
    'gor': {'croatian': 'gorjeti', 'english': 'burn/fire', 'category': 'grammar', 'confidence': 'CANDIDATE'},
    'hei': {'croatian': 'mijesati', 'english': 'combine/mix', 'category': 'grammar', 'confidence': 'CONFIRMED'},
    'heodi': {'croatian': 'tome', 'english': 'to/for the [aforementioned]', 'category': 'grammar', 'confidence': 'CANDIDATE'},
    'heom': {'croatian': 'sa tim', 'english': 'with the [aforementioned]', 'category': 'grammar', 'confidence': 'CANDIDATE'},
    'heos': {'croatian': 'od toga', 'english': 'of the [aforementioned]', 'category': 'grammar', 'confidence': 'CANDIDATE'},
    'hlad': {'croatian': 'hladan', 'english': 'cold/cool', 'category': 'grammar', 'confidence': 'CANDIDATE'},
    'hodi': {'croatian': 'hoditi', 'english': 'walk/go', 'category': 'grammar', 'confidence': 'CONFIRMED'},
    'mir': {'croatian': 'mir', 'english': 'peace/calm', 'category': 'grammar', 'confidence': 'CANDIDATE'},
    'mok': {'croatian': 'mokar', 'english': 'wet/moist', 'category': 'grammar', 'confidence': 'CANDIDATE'},
    'nov': {'croatian': 'nov', 'english': 'new/fresh', 'category': 'grammar', 'confidence': 'CANDIDATE'},
    'om': {'croatian': '-om', 'english': 'with/by (instrumental)', 'category': 'grammar', 'confidence': 'CONFIRMED'},
    'ostai': {'croatian': 'posuda', 'english': 'vessel/container', 'category': 'grammar', 'confidence': 'CONFIRMED'},
    'otrai': {'croatian': 'posuda', 'english': 'vessel/container', 'category': 'grammar', 'confidence': 'CONFIRMED'},
    'sain': {'croatian': 'solina', 'english': 'salt-substance/brine', 'category': 'grammar', 'confidence': 'CANDIDATE'},
    'sam': {'croatian': 'sam', 'english': 'self/alone', 'category': 'grammar', 'confidence': 'CONFIRMED'},
    'star': {'croatian': 'star', 'english': 'old/aged', 'category': 'grammar', 'confidence': 'CONFIRMED'},
    'suh': {'croatian': 'suh', 'english': 'dry/dried', 'category': 'grammar', 'confidence': 'CANDIDATE'},
    'super': {'croatian': 'na/nad', 'english': 'upon/over', 'category': 'grammar', 'confidence': 'MISCELLANY'},
    'topl': {'croatian': 'topao', 'english': 'warm/hot', 'category': 'grammar', 'confidence': 'CANDIDATE'},
    'tram': {'croatian': 'tram', 'english': 'by compound means', 'category': 'grammar', 'confidence': 'CANDIDATE'},
    'šei': {'croatian': 'cijediti', 'english': 'strain/filter', 'category': 'grammar', 'confidence': 'CONFIRMED'},
    'šeom': {'croatian': 'sa tim', 'english': 'with the [instrument]', 'category': 'grammar', 'confidence': 'CANDIDATE'},
    # --- herb (9) ---
    'fen': {'croatian': 'komorač', 'english': 'fennel', 'category': 'herb', 'confidence': 'CONFIRMED'},
    'glog': {'croatian': 'glog', 'english': 'Crataegus spp.', 'category': 'herb', 'confidence': 'CONFIRMED'},
    'hisop': {'croatian': 'izop', 'english': 'hyssop', 'category': 'herb', 'confidence': 'CONFIRMED'},
    'kor': {'croatian': 'korijander', 'english': 'coriander', 'category': 'herb', 'confidence': 'CONFIRMED'},
    'kuhai': {'croatian': 'kuhai', 'english': 'coque', 'category': 'herb', 'confidence': 'CONFIRMED'},
    'kuša': {'croatian': 'kuša', 'english': 'Salvia officinalis', 'category': 'herb', 'confidence': 'CONFIRMED'},
    'lipa': {'croatian': 'lipa', 'english': 'Tilia spp.', 'category': 'herb', 'confidence': 'CONFIRMED'},
    'rut': {'croatian': 'rutvica', 'english': 'rue', 'category': 'herb', 'confidence': 'CONFIRMED'},
    'sljez': {'croatian': 'sljez', 'english': 'Althaea officinalis', 'category': 'herb', 'confidence': 'CONFIRMED'},
    # --- ingredient (74) ---
    'absint': {'croatian': 'pelin', 'english': 'wormwood', 'category': 'ingredient', 'confidence': 'MISCELLANY'},
    'acet': {'croatian': 'ocat', 'english': 'vinegar', 'category': 'ingredient', 'confidence': 'MISCELLANY'},
    'aloe': {'croatian': 'aloja', 'english': 'aloe', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'aloin': {'croatian': 'aloin', 'english': 'aloe extract/aloin', 'category': 'ingredient', 'confidence': 'CANDIDATE'},
    'alum': {'croatian': 'stipsa', 'english': 'alum', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'amyl': {'croatian': 'skrob', 'english': 'starch', 'category': 'ingredient', 'confidence': 'MISCELLANY'},
    'anis': {'croatian': 'anis', 'english': 'anise', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'ar': {'croatian': 'voda', 'english': 'water', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'arg': {'croatian': 'srebro', 'english': 'silver', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'axung': {'croatian': 'mast', 'english': 'pig fat/lard', 'category': 'ingredient', 'confidence': 'MISCELLANY'},
    'camph': {'croatian': 'kamfor', 'english': 'camphor', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'canel': {'croatian': 'cimet', 'english': 'cinnamon', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'canol': {'croatian': 'cimet', 'english': 'cinnamon', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'cer': {'croatian': 'vosak', 'english': 'wax', 'category': 'ingredient', 'confidence': 'MISCELLANY'},
    'chal': {'croatian': 'brasno', 'english': 'flour/grain', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'chol': {'croatian': 'brasno', 'english': 'flour/grain', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'ciner': {'croatian': 'pepeo', 'english': 'ash', 'category': 'ingredient', 'confidence': 'MISCELLANY'},
    'copr': {'croatian': 'bakar', 'english': 'copper/verdigris', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'cori': {'croatian': 'korijander', 'english': 'coriander', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'cortic': {'croatian': 'kora', 'english': 'bark/rind', 'category': 'ingredient', 'confidence': 'MISCELLANY'},
    'croc': {'croatian': 'safran', 'english': 'saffron', 'category': 'ingredient', 'confidence': 'MISCELLANY'},
    'cupr': {'croatian': 'bakar', 'english': 'copper/verdigris', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'edi': {'croatian': 'korijen', 'english': 'root/prepared', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'edy': {'croatian': 'korijen', 'english': 'root/prepared', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'fenn': {'croatian': 'komorac', 'english': 'fennel', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'fer': {'croatian': 'zeljezo', 'english': 'iron/filings', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'flor': {'croatian': 'cvijet', 'english': 'flower', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'fol': {'croatian': 'list', 'english': 'leaf', 'category': 'ingredient', 'confidence': 'MISCELLANY'},
    'galb': {'croatian': 'galban', 'english': 'galbanum', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'genist': {'croatian': 'zukva', 'english': 'genista broom', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'glyc': {'croatian': 'sladak korijen', 'english': 'licorice', 'category': 'ingredient', 'confidence': 'MISCELLANY'},
    'gumm': {'croatian': 'guma', 'english': 'gum', 'category': 'ingredient', 'confidence': 'MISCELLANY'},
    'hol': {'croatian': 'brasno', 'english': 'flour/grain', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'hyss': {'croatian': 'izop', 'english': 'hyssop', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'kost': {'croatian': 'kost', 'english': 'bone', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'lac': {'croatian': 'mlijeko', 'english': 'milk', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'malv': {'croatian': 'sljez', 'english': 'mallow', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'mast': {'croatian': 'mastika', 'english': 'mastic', 'category': 'ingredient', 'confidence': 'MISCELLANY'},
    'mel': {'croatian': 'med', 'english': 'honey', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'ment': {'croatian': 'metvica', 'english': 'mint', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'myr': {'croatian': 'smirna', 'english': 'myrrh resin', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'myron': {'croatian': 'smirna', 'english': 'myrrh resin', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'ol': {'croatian': 'ulje', 'english': 'oil', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'olib': {'croatian': 'tamjan', 'english': 'frankincense', 'category': 'ingredient', 'confidence': 'MISCELLANY'},
    'opop': {'croatian': 'opopanaks', 'english': 'opopanax gum', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'or': {'croatian': 'ulje', 'english': 'oil', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'ov': {'croatian': 'jaje', 'english': 'egg', 'category': 'ingredient', 'confidence': 'MISCELLANY'},
    'papav': {'croatian': 'mak', 'english': 'poppy', 'category': 'ingredient', 'confidence': 'MISCELLANY'},
    'piper': {'croatian': 'papar', 'english': 'pepper', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'plant': {'croatian': 'trputac', 'english': 'plantain', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'pulv': {'croatian': 'prah', 'english': 'powder', 'category': 'ingredient', 'confidence': 'MISCELLANY'},
    'rady': {'croatian': 'korijen', 'english': 'root/prepared', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'resin': {'croatian': 'smola', 'english': 'resin', 'category': 'ingredient', 'confidence': 'MISCELLANY'},
    'ros': {'croatian': 'ruza', 'english': 'rose/rosewater', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'rosar': {'croatian': 'ruza', 'english': 'rose/rosewater', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'ruta': {'croatian': 'rutvica', 'english': 'rue', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'sacchar': {'croatian': 'secer', 'english': 'sugar', 'category': 'ingredient', 'confidence': 'MISCELLANY'},
    'sal': {'croatian': 'sol', 'english': 'salt', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'salp': {'croatian': 'salitra', 'english': 'saltpeter', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'salv': {'croatian': 'kadulja', 'english': 'sage', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'sambuc': {'croatian': 'bazga', 'english': 'elder', 'category': 'ingredient', 'confidence': 'MISCELLANY'},
    'sar': {'croatian': 'sol', 'english': 'salt', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'sem': {'croatian': 'sjeme', 'english': 'seed', 'category': 'ingredient', 'confidence': 'MISCELLANY'},
    'sterc': {'croatian': 'gnoj', 'english': 'dung/feces', 'category': 'ingredient', 'confidence': 'MISCELLANY'},
    'stor': {'croatian': 'storaks', 'english': 'storax', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'streod': {'croatian': 'smola', 'english': 'storax/resin preparation', 'category': 'ingredient', 'confidence': 'CANDIDATE'},
    'stroy': {'croatian': 'smola', 'english': 'storax/resin', 'category': 'ingredient', 'confidence': 'CANDIDATE'},
    'succ': {'croatian': 'sok', 'english': 'juice/sap', 'category': 'ingredient', 'confidence': 'MISCELLANY'},
    'sul': {'croatian': 'sumpor', 'english': 'sulfur', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'urtic': {'croatian': 'kopriva', 'english': 'nettle', 'category': 'ingredient', 'confidence': 'MISCELLANY'},
    'verb': {'croatian': 'verbena', 'english': 'vervain', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'vin': {'croatian': 'vino', 'english': 'wine', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'zing': {'croatian': 'djumbir', 'english': 'ginger', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    'zinor': {'croatian': 'djumbir', 'english': 'ginger', 'category': 'ingredient', 'confidence': 'CONFIRMED'},
    # --- latin (10) ---
    'ana': {'croatian': 'equal parts (Rx)', 'english': 'equal parts (Rx)', 'category': 'latin', 'confidence': 'CONFIRMED'},
    'coque': {'croatian': 'cook', 'english': 'cook', 'category': 'latin', 'confidence': 'CONFIRMED'},
    'da': {'croatian': 'give (Rx imperative)', 'english': 'give (Rx imperative)', 'category': 'latin', 'confidence': 'CONFIRMED'},
    'dolor': {'croatian': 'pain', 'english': 'pain', 'category': 'latin', 'confidence': 'CONFIRMED'},
    'oral': {'croatian': 'by mouth/orally', 'english': 'by mouth/orally', 'category': 'latin', 'confidence': 'CONFIRMED'},
    'orolaly': {'croatian': 'orally (expanded)', 'english': 'orally (expanded)', 'category': 'latin', 'confidence': 'CONFIRMED'},
    'ost': {'croatian': 'Bone (medical register)', 'english': 'Bone (medical register)', 'category': 'latin', 'confidence': 'CONFIRMED'},
    'oste': {'croatian': 'Bone (medical extended)', 'english': 'Bone (medical extended)', 'category': 'latin', 'confidence': 'CONFIRMED'},
    'osteo': {'croatian': 'Bone (full Latin)', 'english': 'Bone (full Latin)', 'category': 'latin', 'confidence': 'CONFIRMED'},
    'recipe': {'croatian': 'take (Rx)', 'english': 'take (Rx)', 'category': 'latin', 'confidence': 'CONFIRMED'},
    # --- liquid (8) ---
    'al': {'croatian': 'tekućina', 'english': 'liquid/water (vessel context)', 'category': 'liquid', 'confidence': 'CONFIRMED'},
    'dal': {'croatian': 'dal', 'english': 'da-l-al', 'category': 'liquid', 'confidence': 'CONFIRMED'},
    'okaly': {'croatian': 'okaly', 'english': 'ok-al-y', 'category': 'liquid', 'confidence': 'CONFIRMED'},
    'okary': {'croatian': 'okary', 'english': 'ok-ar-y', 'category': 'liquid', 'confidence': 'CONFIRMED'},
    'qokal': {'croatian': 'qokal', 'english': 'qo-kal-∅', 'category': 'liquid', 'confidence': 'CONFIRMED'},
    'qokar': {'croatian': 'qokar', 'english': 'qo-kar-∅', 'category': 'liquid', 'confidence': 'CONFIRMED'},
    'rosol': {'croatian': 'rosol', 'english': 'Rose-oil', 'category': 'liquid', 'confidence': 'CONFIRMED'},
    'thar': {'croatian': 'thar', 'english': 'Boil (variant)', 'category': 'liquid', 'confidence': 'CANDIDATE'},
    # --- measurement (3) ---
    'coclear': {'croatian': 'zlica', 'english': 'spoonful', 'category': 'measurement', 'confidence': 'MISCELLANY'},
    'dragm': {'croatian': 'dram', 'english': 'dram (weight)', 'category': 'measurement', 'confidence': 'MISCELLANY'},
    'unc': {'croatian': 'unca', 'english': 'ounce (weight)', 'category': 'measurement', 'confidence': 'MISCELLANY'},
    # --- modifier (2) ---
    'calid': {'croatian': 'toplo', 'english': 'warm/hot', 'category': 'modifier', 'confidence': 'MISCELLANY'},
    'frigid': {'croatian': 'hladno', 'english': 'cold', 'category': 'modifier', 'confidence': 'MISCELLANY'},
    # --- operator (18) ---
    'ch': {'croatian': 'combine/cook', 'english': 'combine/cook', 'category': 'operator', 'confidence': 'CONFIRMED'},
    'cth': {'croatian': '~20', 'english': '~20', 'category': 'operator', 'confidence': 'CONFIRMED'},
    'he': {'croatian': 'State / Result / After', 'english': 'State / Result / After', 'category': 'operator', 'confidence': 'CONFIRMED'},
    'heo': {'croatian': 'State / Result (extended)', 'english': 'State / Result (extended)', 'category': 'operator', 'confidence': 'CONFIRMED'},
    'ko': {'croatian': 'measure/quantify (variant)', 'english': 'measure/quantify (variant)', 'category': 'operator', 'confidence': 'CONFIRMED'},
    'lh': {'croatian': 'The (before h-)', 'english': 'The (before h-)', 'category': 'operator', 'confidence': 'CONFIRMED'},
    'lš': {'croatian': 'The (before š-)', 'english': 'The (before š-)', 'category': 'operator', 'confidence': 'CONFIRMED'},
    'ok': {'croatian': 'vessel/container', 'english': 'vessel/container', 'category': 'operator', 'confidence': 'CONFIRMED'},
    'ot': {'croatian': 'vessel/container (variant)', 'english': 'vessel/container (variant)', 'category': 'operator', 'confidence': 'CONFIRMED'},
    'pc': {'croatian': 'prepare (compound)', 'english': 'prepare (compound)', 'category': 'operator', 'confidence': 'CONFIRMED'},
    'qo': {'croatian': 'measure/quantify', 'english': 'measure/quantify', 'category': 'operator', 'confidence': 'CONFIRMED'},
    'sa': {'croatian': 'with/together', 'english': 'with/together', 'category': 'operator', 'confidence': 'CONFIRMED'},
    'sh': {'croatian': 'soak/infuse', 'english': 'soak/infuse', 'category': 'operator', 'confidence': 'CONFIRMED'},
    'so': {'croatian': 'with/together (variant)', 'english': 'with/together (variant)', 'category': 'operator', 'confidence': 'CONFIRMED'},
    'tc': {'croatian': 'heat-treat (compound)', 'english': 'heat-treat (compound)', 'category': 'operator', 'confidence': 'CONFIRMED'},
    'yk': {'croatian': 'measure-vessel (compound)', 'english': 'measure-vessel (compound)', 'category': 'operator', 'confidence': 'CONFIRMED'},
    'še': {'croatian': 'Soaked-state / After soaking', 'english': 'Soaked-state / After soaking', 'category': 'operator', 'confidence': 'CONFIRMED'},
    'šeo': {'croatian': 'Soaked-state (extended)', 'english': 'Soaked-state (extended)', 'category': 'operator', 'confidence': 'CONFIRMED'},
    # --- plant_part (5) ---
    'cvijet': {'croatian': 'cvijet', 'english': 'flower', 'category': 'plant_part', 'confidence': 'CONFIRMED'},
    'kora': {'croatian': 'kora', 'english': 'bark', 'category': 'plant_part', 'confidence': 'CONFIRMED'},
    'list': {'croatian': 'list', 'english': 'leaf', 'category': 'plant_part', 'confidence': 'CONFIRMED'},
    'od': {'croatian': 'stabljika', 'english': 'stalk/stem', 'category': 'plant_part', 'confidence': 'CONFIRMED'},
    'sjeme': {'croatian': 'sjeme', 'english': 'seed', 'category': 'plant_part', 'confidence': 'CONFIRMED'},
    # --- preparation (18) ---
    'airal': {'croatian': 'zracni', 'english': 'vapor vessel/alembic', 'category': 'preparation', 'confidence': 'CANDIDATE'},
    'catapl': {'croatian': 'oblog', 'english': 'poultice', 'category': 'preparation', 'confidence': 'MISCELLANY'},
    'confect': {'croatian': 'lijek', 'english': 'confection/electuary', 'category': 'preparation', 'confidence': 'MISCELLANY'},
    'cstr': {'croatian': 'zgušnjeni', 'english': 'concentrated preparation', 'category': 'preparation', 'confidence': 'CANDIDATE'},
    'ctrr': {'croatian': 'smjesa', 'english': 'compound mixture', 'category': 'preparation', 'confidence': 'CANDIDATE'},
    'decoct': {'croatian': 'odvar', 'english': 'decoction', 'category': 'preparation', 'confidence': 'MISCELLANY'},
    'eal': {'croatian': 'eal', 'english': 'vessel/container', 'category': 'preparation', 'confidence': 'CANDIDATE'},
    'eey': {'croatian': 'eey', 'english': 'distilled fluid', 'category': 'preparation', 'confidence': 'CANDIDATE'},
    'emplast': {'croatian': 'oblog', 'english': 'plaster', 'category': 'preparation', 'confidence': 'MISCELLANY'},
    'estr': {'croatian': 'melem', 'english': 'plaster/poultice', 'category': 'preparation', 'confidence': 'CANDIDATE'},
    'etr': {'croatian': 'ekstrakt', 'english': 'extract/tincture', 'category': 'preparation', 'confidence': 'CANDIDATE'},
    'ey': {'croatian': 'ey', 'english': 'liquid/fluid', 'category': 'preparation', 'confidence': 'CANDIDATE'},
    'gargar': {'croatian': 'grgljanje', 'english': 'gargle', 'category': 'preparation', 'confidence': 'MISCELLANY'},
    'lstry': {'croatian': 'lstry', 'english': 'the root-prepared', 'category': 'preparation', 'confidence': 'CANDIDATE'},
    'plr': {'croatian': 'prašak', 'english': 'powder/pulverize', 'category': 'preparation', 'confidence': 'CANDIDATE'},
    'syrup': {'croatian': 'sirup', 'english': 'syrup', 'category': 'preparation', 'confidence': 'MISCELLANY'},
    'trocisc': {'croatian': 'pastila', 'english': 'lozenge/troche', 'category': 'preparation', 'confidence': 'MISCELLANY'},
    'unguent': {'croatian': 'mast', 'english': 'ointment', 'category': 'preparation', 'confidence': 'MISCELLANY'},
    # --- property (3) ---
    'gorak': {'croatian': 'gorko', 'english': 'bitter', 'category': 'property', 'confidence': 'CONFIRMED'},
    'mokar': {'croatian': 'mokro', 'english': 'wet', 'category': 'property', 'confidence': 'CONFIRMED'},
    'suš': {'croatian': 'suho', 'english': 'dry', 'category': 'property', 'confidence': 'CONFIRMED'},
    # --- resin (2) ---
    'kamf': {'croatian': 'kamfor', 'english': 'camphor', 'category': 'resin', 'confidence': 'CONFIRMED'},
    'smreka': {'croatian': 'smreka', 'english': 'Picea albis / Juniperus', 'category': 'resin', 'confidence': 'CONFIRMED'},
    # --- spice (3) ---
    'cinam': {'croatian': 'cimet', 'english': 'cinnamon', 'category': 'spice', 'confidence': 'CONFIRMED'},
    'ging': {'croatian': 'đumbir', 'english': 'ginger', 'category': 'spice', 'confidence': 'CONFIRMED'},
    'pip': {'croatian': 'papar', 'english': 'pepper', 'category': 'spice', 'confidence': 'CONFIRMED'},
    # --- timing (2) ---
    'man': {'croatian': 'ujutro', 'english': 'in the morning', 'category': 'timing', 'confidence': 'MISCELLANY'},
    'noct': {'croatian': 'nocu', 'english': 'at night', 'category': 'timing', 'confidence': 'MISCELLANY'},
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
