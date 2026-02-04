"""
Blind Decode Falsification Test v2 Configuration
Vocabulary Specificity Test
All values are preregistered. Do not modify during testing.
"""

# Inherit folio list from v1
from config import TEST_FOLIOS, THRESHOLDS

# v2 seed bases (different from v1 to avoid any overlap)
SEED_SYNTHETIC = 1000     # Seeds 1000-1099
SEED_CHAR_SHUFFLE = 2000  # Seeds 2000-2099
SEED_RANDOM_LATIN = 3000  # Seeds 3000-3099

# Iterations per baseline type
V2_ITERATIONS = 100

# EVA character frequency distribution (from 1411-word manuscript sample)
# Used by synthetic EVA generator to produce plausible-looking fake words
EVA_CHAR_FREQUENCIES = {
    'o': 0.137, 'e': 0.105, 'h': 0.098, 'y': 0.090,
    'a': 0.070, 'c': 0.065, 'k': 0.063, 'l': 0.057,
    'd': 0.055, 'i': 0.053, 's': 0.051, 'r': 0.040,
    't': 0.034, 'n': 0.031, 'q': 0.024, 'p': 0.008,
    'm': 0.005, 'f': 0.004,
}

# EVA word length distribution (from 1411-word manuscript sample)
# Used by synthetic EVA generator to match real word length patterns
EVA_LENGTH_DISTRIBUTION = {
    1: 0.052, 2: 0.048, 3: 0.082, 4: 0.184,
    5: 0.272, 6: 0.213, 7: 0.089, 8: 0.028,
    9: 0.021, 10: 0.004, 11: 0.004,
}

# Medieval Latin vocabulary for random Latin baseline
# Common words from pharmaceutical/herbalist texts
# This gives Latin its BEST shot -- we use domain-relevant vocabulary
LATIN_VOCABULARY = [
    "aqua", "oleum", "radix", "herba", "folium", "flos", "semen",
    "cortex", "sal", "mel", "vinum", "lac", "cera", "resina",
    "pulvis", "unguentum", "emplastrum", "decoctum", "infusum",
    "recipe", "misce", "adde", "cola", "fiat", "detur", "solve",
    "contere", "coque", "distilla", "filtra", "digere", "macera",
    "dosis", "drachma", "uncia", "libra", "manipulus", "gutta",
    "ana", "quantum", "satis", "ad", "cum", "in", "per", "pro",
    "bis", "ter", "quotidie", "mane", "vespere", "nocte",
    "calidus", "frigidus", "siccus", "humidus", "dulcis", "amarus",
    "vas", "mortarium", "pistillum", "cucurbita", "alembicum",
    "fornax", "ignis", "balneum", "hora", "dies", "mensis",
    "purgatio", "digestio", "calcinatio", "sublimatio", "fixatio",
    "tinctura", "essentia", "spiritus", "extractum", "syrupus",
    "confectio", "electuarium", "cataplasma", "linimentum",
    "absinthe", "aloe", "camphora", "cassia", "cinnamomum",
    "crocus", "gentiana", "glycyrrhiza", "myrrha", "opium",
    "piper", "rhabarbarum", "rosa", "salvia", "thymum",
]

# v2 pass/fail thresholds
V2_THRESHOLDS = {
    # If real Voynich coherence exceeds ALL three baselines by this z-score,
    # the pipeline is Voynich-specific
    "min_z_score": 2.0,

    # If any baseline type scores within this range of real, pipeline is too flexible
    "flexibility_threshold": 0.10,  # If baseline mean is within 0.10 of real coherence

    # Minimum folios where real must significantly beat all baselines
    "min_discriminating_folios": 4,

    # P-value threshold
    "significance_level": 0.01,
}
