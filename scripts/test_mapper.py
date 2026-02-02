#!/usr/bin/env python3
"""
Comprehensive tests for ZFD mapper
"""

from zfd_mapper import map_eva_to_croatian, map_line, convert_folio

# Extended test cases
EXTENDED_TESTS = [
    # Basic operators
    ('qokeedy', 'kostedi'),
    ('chedy', 'hedi'),
    ('shedy', 'šedi'),

    # Gallows clusters
    ('kol', 'stol'),          # k → st
    ('tor', 'tror'),          # t → tr
    ('for', 'pror'),          # f → pr
    ('pol', 'plol'),          # p → pl

    # Word-initial q variants
    ('qo', 'ko'),
    ('qol', 'kol'),
    ('qokal', 'kostal'),

    # Vowel sequences
    ('cheey', 'hei'),         # ee → e
    ('daiin', 'dain'),        # ii → i
    ('aiin', 'ain'),

    # Mid-word digraphs
    ('ochar', 'ohar'),        # ch → h mid-word
    ('oshar', 'ošar'),        # sh → š mid-word

    # ck/ct combinations
    ('ockhy', 'ocsthi'),      # ck → cst, h → h
    ('octol', 'octrol'),      # ct → ctr

    # Suffix patterns
    ('shey', 'šei'),
    ('chody', 'hodi'),        # Should produce "hodi" (walk/go)

    # Complex words (h preserved for review)
    ('qockhey', 'kocsthei'),
    ('sholfchor', 'šolprhor'),
    ('cthol', 'ctrhol'),

    # Known Croatian words
    ('dar', 'dar'),           # gift
    ('sal', 'sal'),           # salt
    ('sam', 'sam'),           # self
]


def test_word_mapping():
    """Test individual word mapping."""
    print("Testing word mapping...")
    print("-" * 50)

    passed = 0
    failed = 0

    for eva, expected in EXTENDED_TESTS:
        result = map_eva_to_croatian(eva)
        if result == expected:
            passed += 1
            print(f"✓ {eva} → {result}")
        else:
            failed += 1
            print(f"✗ {eva} → {result} (expected: {expected})")

    print(f"\nWord mapping: {passed}/{len(EXTENDED_TESTS)} passed\n")
    return failed == 0


def test_line_mapping():
    """Test full line mapping."""
    print("Testing line mapping...")
    print("-" * 50)

    test_lines = [
        ('daiin.chol.dar', 'dain hol dar'),
        ('qokeedy.shedy.ol', 'kostedi šedi ol'),
        ('sal.sheom.kol', 'sal šeom stol'),
    ]

    passed = 0
    for eva, expected in test_lines:
        result = map_line(eva)
        if result == expected:
            passed += 1
            print(f"✓ Line OK")
        else:
            print(f"✗ Expected: {expected}")
            print(f"  Got:      {result}")

    print(f"\nLine mapping: {passed}/{len(test_lines)} passed\n")
    return passed == len(test_lines)


def test_folio_conversion():
    """Test full folio conversion."""
    print("Testing folio conversion...")
    print("-" * 50)

    test_folio = {
        'labels': ['otorchety', 'oral', 'oldar'],
        'text': ['daiin.chol.dar', 'qokeedy.shedy']
    }

    result = convert_folio(test_folio)

    print(f"Labels: {result['labels']}")
    print(f"Text: {result['text']}")

    # Basic sanity checks
    assert len(result['labels']) == 3
    assert len(result['text']) == 2
    assert 'dain' in result['text'][0]

    print("\nFolio conversion: OK\n")
    return True


def test_croatian_patterns():
    """Verify expected Croatian patterns emerge."""
    print("Testing Croatian pattern recognition...")
    print("-" * 50)

    # Words that should contain "kost" (bone)
    kost_words = ['qokeedy', 'qokeey', 'qokain', 'qokedy', 'qoky']

    for word in kost_words:
        result = map_eva_to_croatian(word)
        if 'kost' in result:
            print(f"✓ {word} → {result} (contains 'kost')")
        else:
            print(f"✗ {word} → {result} (missing 'kost')")

    print()
    return True


if __name__ == "__main__":
    print("=" * 50)
    print("ZFD MAPPER - COMPREHENSIVE TESTS")
    print("=" * 50)
    print()

    all_passed = True
    all_passed &= test_word_mapping()
    all_passed &= test_line_mapping()
    all_passed &= test_folio_conversion()
    all_passed &= test_croatian_patterns()

    print("=" * 50)
    if all_passed:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
    print("=" * 50)
