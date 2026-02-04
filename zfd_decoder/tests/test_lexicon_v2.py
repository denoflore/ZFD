"""
Schema validation tests for lexicon_v2.csv.
Phase 1: Ensure the new lexicon file is valid and well-formed.
"""

import csv
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

DATA_DIR = Path(__file__).parent.parent / "data"
LEXICON_V2_PATH = DATA_DIR / "lexicon_v2.csv"

# Expected schema
EXPECTED_COLUMNS = ['name', 'variant', 'context', 'gloss', 'latin', 'croatian', 'category', 'status', 'source']

# Valid values for enum fields
VALID_STATUS = {'CONFIRMED', 'CANDIDATE', 'MISCELLANY'}
VALID_CATEGORIES = {
    'ingredient', 'action', 'body_part', 'grammar', 'condition',
    'equipment', 'preparation', 'latin_pharma', 'measurement',
    'timing', 'modifier'
}


def test_lexicon_v2_exists():
    """lexicon_v2.csv file exists in data directory."""
    assert LEXICON_V2_PATH.exists(), f"lexicon_v2.csv not found at {LEXICON_V2_PATH}"


def test_lexicon_v2_has_nine_columns():
    """File has exactly 9 columns with correct names."""
    with open(LEXICON_V2_PATH) as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

    assert fieldnames is not None, "Could not read fieldnames"
    assert len(fieldnames) == 9, f"Expected 9 columns, got {len(fieldnames)}: {fieldnames}"
    assert fieldnames == EXPECTED_COLUMNS, f"Column mismatch. Expected {EXPECTED_COLUMNS}, got {fieldnames}"


def test_lexicon_v2_entry_count():
    """File has exactly 185 entries."""
    with open(LEXICON_V2_PATH) as f:
        reader = csv.DictReader(f)
        entries = list(reader)

    assert len(entries) == 185, f"Expected 185 entries, got {len(entries)}"


def test_all_entries_parse():
    """All 185 entries parse without error."""
    with open(LEXICON_V2_PATH) as f:
        reader = csv.DictReader(f)
        errors = []
        for i, row in enumerate(reader, start=2):  # Line 2 is first data row
            # Check all required columns exist
            for col in EXPECTED_COLUMNS:
                if col not in row:
                    errors.append(f"Line {i}: Missing column '{col}'")

        assert len(errors) == 0, f"Parse errors: {errors}"


def test_no_duplicate_variants():
    """No duplicate variant values within same name context."""
    with open(LEXICON_V2_PATH) as f:
        reader = csv.DictReader(f)
        seen = {}
        duplicates = []

        for i, row in enumerate(reader, start=2):
            key = (row['variant'], row['context'])
            if key in seen:
                duplicates.append(f"Line {i}: Duplicate variant '{row['variant']}' in context '{row['context']}' (first seen line {seen[key]})")
            else:
                seen[key] = i

    assert len(duplicates) == 0, f"Duplicate variants found: {duplicates}"


def test_valid_status_values():
    """All status values are CONFIRMED, CANDIDATE, or MISCELLANY."""
    with open(LEXICON_V2_PATH) as f:
        reader = csv.DictReader(f)
        invalid = []

        for i, row in enumerate(reader, start=2):
            status = row['status']
            if status not in VALID_STATUS:
                invalid.append(f"Line {i}: Invalid status '{status}'")

    assert len(invalid) == 0, f"Invalid status values: {invalid}"


def test_valid_category_values():
    """All category values are one of the 11 defined categories."""
    with open(LEXICON_V2_PATH) as f:
        reader = csv.DictReader(f)
        invalid = []

        for i, row in enumerate(reader, start=2):
            category = row['category']
            if category not in VALID_CATEGORIES:
                invalid.append(f"Line {i}: Invalid category '{category}'")

    assert len(invalid) == 0, f"Invalid category values: {invalid}"


def test_non_empty_required_fields():
    """Every entry has a non-empty variant and gloss."""
    with open(LEXICON_V2_PATH) as f:
        reader = csv.DictReader(f)
        empty = []

        for i, row in enumerate(reader, start=2):
            if not row['variant'].strip():
                empty.append(f"Line {i}: Empty variant")
            if not row['gloss'].strip():
                empty.append(f"Line {i}: Empty gloss")

    assert len(empty) == 0, f"Empty required fields: {empty}"


def test_status_distribution():
    """Verify status distribution matches expectations."""
    with open(LEXICON_V2_PATH) as f:
        reader = csv.DictReader(f)
        counts = {'CONFIRMED': 0, 'CANDIDATE': 0, 'MISCELLANY': 0}

        for row in reader:
            counts[row['status']] += 1

    # Just verify we have entries in each category
    assert counts['CONFIRMED'] > 0, "No CONFIRMED entries"
    assert counts['CANDIDATE'] > 0, "No CANDIDATE entries"
    assert counts['MISCELLANY'] > 0, "No MISCELLANY entries"

    # Verify rough distribution (v1 had mostly CONFIRMED, v2 adds MISCELLANY)
    total = sum(counts.values())
    assert total == 185, f"Total entries should be 185, got {total}"
    print(f"Status distribution: {counts}")


def test_category_distribution():
    """Verify we have multiple categories represented."""
    with open(LEXICON_V2_PATH) as f:
        reader = csv.DictReader(f)
        categories = set()

        for row in reader:
            categories.add(row['category'])

    # Should have at least 8 different categories
    assert len(categories) >= 8, f"Expected at least 8 categories, got {len(categories)}: {categories}"

    # Must have the core categories
    assert 'ingredient' in categories, "Missing 'ingredient' category"
    assert 'action' in categories, "Missing 'action' category"
    assert 'body_part' in categories, "Missing 'body_part' category"
    assert 'grammar' in categories, "Missing 'grammar' category"


def test_source_values():
    """Source values are reasonable."""
    with open(LEXICON_V2_PATH) as f:
        reader = csv.DictReader(f)
        sources = set()

        for row in reader:
            sources.add(row['source'])

    # Should have lexicon_v1 and at least one new source
    assert 'lexicon_v1' in sources, "Missing 'lexicon_v1' source"
    assert len(sources) >= 2, f"Expected at least 2 sources, got {sources}"


def run_all_tests():
    """Run all schema validation tests."""
    print("=" * 60)
    print("LEXICON V2 SCHEMA VALIDATION TESTS")
    print("=" * 60)
    print()

    tests = [
        test_lexicon_v2_exists,
        test_lexicon_v2_has_nine_columns,
        test_lexicon_v2_entry_count,
        test_all_entries_parse,
        test_no_duplicate_variants,
        test_valid_status_values,
        test_valid_category_values,
        test_non_empty_required_fields,
        test_status_distribution,
        test_category_distribution,
        test_source_values,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            print(f"PASS {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR {test.__name__}: {e}")
            failed += 1

    print()
    print("=" * 60)
    print(f"Results: {passed}/{len(tests)} passed")
    if failed == 0:
        print("ALL SCHEMA TESTS PASSED")
    else:
        print(f"{failed} TESTS FAILED")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
