"""
Blind Decode Falsification Test Configuration
All values are preregistered. Do not modify during testing.
"""

# Test folios (from Protocol v1, preregistered September 2025)
TEST_FOLIOS = ["f10r", "f23v", "f47r", "f89r", "f101v"]

# Random seed for shuffled baseline (deterministic reproducibility)
SHUFFLE_SEED = 42

# Number of shuffle iterations for statistical significance
SHUFFLE_ITERATIONS = 100

# Pass/fail thresholds (preregistered)
THRESHOLDS = {
    # Minimum coherence index (0-1) for a folio to "pass"
    "min_coherence": 0.70,

    # Minimum folios that must pass (out of 5)
    "min_passing_folios": 4,

    # Minimum p-value threshold for real vs shuffled comparison
    "significance_level": 0.01,

    # Minimum semantic category diversity (unique categories per folio)
    "min_category_diversity": 3,

    # Minimum known stem ratio per folio
    "min_known_ratio": 0.30,
}

# Folio-specific predictions (from preregistered Protocol v1)
FOLIO_PREDICTIONS = {
    "f10r": {
        "expected_process_class": "wash_strain",
        "required_operators": ["qo", "ol", "ch"],
        "required_stems_any": ["edy", "edi", "rady"],  # root terms
        "forbidden_dominant_category": None,
    },
    "f23v": {
        "expected_process_class": "heat_treatment",
        "required_operators": ["ok", "qo"],
        "required_stems_any": ["ol", "or"],  # oil terms
        "forbidden_dominant_category": None,
    },
    "f47r": {
        "expected_process_class": "herbal_preparation",
        "required_operators": ["qo", "ch", "sh"],
        "required_stems_any": ["edy", "edi", "flor", "list"],
        "forbidden_dominant_category": None,
    },
    "f89r": {
        "expected_process_class": "pharmaceutical_recipe",
        "required_operators": ["qo", "da", "ok"],
        "required_stems_any": ["kost", "ost", "ol", "or", "mel"],
        "forbidden_dominant_category": None,
    },
    "f101v": {
        "expected_process_class": "dosage_grid",
        "required_operators": ["qo", "da"],
        "required_stems_any": ["da", "dar"],  # dose terms
        "forbidden_dominant_category": None,
    },
}

# Image-adjacency annotations (preregistered before test run)
# Maps folio regions to expected semantic categories based on illustrations
# These annotations are made by a human looking at the images BEFORE decoding
IMAGE_ANNOTATIONS = {
    "f10r": {
        "description": "Plant with prominent root system, leaves, possible flowers",
        "expected_categories": ["ingredient", "preparation", "action"],
        "key_plant_parts": ["root", "leaf"],
        "has_vessels": False,
        "has_text_blocks": True,
    },
    "f23v": {
        "description": "Plant illustration with distinct parts, possible distillation context",
        "expected_categories": ["ingredient", "action", "equipment"],
        "key_plant_parts": ["leaf", "flower", "oil"],
        "has_vessels": False,
        "has_text_blocks": True,
    },
    "f47r": {
        "description": "Herbal illustration with roots and upper parts visible",
        "expected_categories": ["ingredient", "preparation", "action"],
        "key_plant_parts": ["root", "flower", "leaf"],
        "has_vessels": False,
        "has_text_blocks": True,
    },
    "f89r": {
        "description": "Pharmaceutical section with jars, vessels, processing equipment",
        "expected_categories": ["ingredient", "equipment", "action", "preparation"],
        "key_plant_parts": [],
        "has_vessels": True,
        "has_text_blocks": True,
    },
    "f101v": {
        "description": "Grid-like layout, recipe organization, possible dosage tables",
        "expected_categories": ["measurement", "ingredient", "timing", "action"],
        "key_plant_parts": [],
        "has_vessels": False,
        "has_text_blocks": True,
    },
}
