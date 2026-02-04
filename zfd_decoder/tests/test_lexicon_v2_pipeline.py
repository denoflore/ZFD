"""
Tests for lexicon_v2 features in the ZFD pipeline.
Phase 5: Validate v2-specific functionality and backward compatibility.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tokenizer import Token
from pipeline import ZFDPipeline

# Initialize paths
DATA_DIR = Path(__file__).parent.parent / "data"


def test_v2_entry_count():
    """Lexicon v2 has at least 185 entries (may have fewer unique stems due to duplicates)."""
    pipeline = ZFDPipeline(data_dir=str(DATA_DIR))
    assert len(pipeline.lexicon.stems) >= 180, f"Expected 180+ stems, got {len(pipeline.lexicon.stems)}"
    assert pipeline.lexicon.is_v2, "Pipeline should load v2 by default"
    print(f"PASS v2 entry count: {len(pipeline.lexicon.stems)} stems")


def test_miscellany_confidence():
    """MISCELLANY entries get lower confidence than CONFIRMED."""
    pipeline = ZFDPipeline(data_dir=str(DATA_DIR))

    # Find a CONFIRMED entry (kost - bone)
    confirmed_data = pipeline.lexicon.lookup('kost')
    assert confirmed_data is not None, "kost should be in lexicon"
    assert confirmed_data['status'] == 'CONFIRMED'
    confirmed_conf = pipeline.lexicon.confidence_for_status(confirmed_data['status'])

    # Find a MISCELLANY entry (glav - head)
    miscellany_data = pipeline.lexicon.lookup('glav')
    assert miscellany_data is not None, "glav should be in lexicon v2"
    assert miscellany_data['status'] == 'MISCELLANY'
    miscellany_conf = pipeline.lexicon.confidence_for_status(miscellany_data['status'])

    # MISCELLANY should have lower confidence
    assert miscellany_conf < confirmed_conf, f"MISCELLANY ({miscellany_conf}) should be less than CONFIRMED ({confirmed_conf})"
    assert confirmed_conf == 0.30, f"CONFIRMED should be 0.30, got {confirmed_conf}"
    assert miscellany_conf == 0.10, f"MISCELLANY should be 0.10, got {miscellany_conf}"
    print(f"PASS MISCELLANY confidence ({miscellany_conf}) < CONFIRMED ({confirmed_conf})")


def test_croatian_output():
    """Croatian layer produces actual Croatian words."""
    pipeline = ZFDPipeline(data_dir=str(DATA_DIR))

    # Test sar -> sol (salt in Croatian)
    token = Token(id="test.v2.1", eva="sar")
    result = pipeline.process_token(token)

    # With v2, the croatian field should use the actual Croatian word
    assert result.stem_known, "sar should be recognized"
    stem_data = pipeline.lexicon.lookup('sar')
    assert stem_data is not None
    assert stem_data['croatian'] == 'sol', f"sar croatian should be 'sol', got {stem_data['croatian']}"

    # The _build_croatian should use the Croatian form
    assert 'sol' in result.croatian, f"croatian output should contain 'sol', got {result.croatian}"
    print(f"PASS croatian output: sar -> {result.croatian}")


def test_new_body_part_entries():
    """Body part entries from miscellany mining are accessible."""
    pipeline = ZFDPipeline(data_dir=str(DATA_DIR))

    # Check for new body part entries
    body_parts = ['glav', 'ok', 'nos', 'src', 'ruk']

    found = 0
    for part in body_parts:
        data = pipeline.lexicon.lookup(part)
        if data:
            assert data['category'] == 'body_part', f"{part} should be body_part category"
            found += 1

    assert found >= 3, f"Expected at least 3 body part entries, found {found}"
    print(f"PASS body part entries: found {found} of {len(body_parts)}")


def test_new_action_entries():
    """Action verb entries from miscellany mining are accessible."""
    pipeline = ZFDPipeline(data_dir=str(DATA_DIR))

    # Check for new action entries
    actions = ['sat', 'tuc', 'mij', 'grij', 'per']

    found = 0
    for action in actions:
        data = pipeline.lexicon.lookup(action)
        if data:
            assert data['category'] == 'action', f"{action} should be action category"
            found += 1

    assert found >= 3, f"Expected at least 3 action entries, found {found}"
    print(f"PASS action entries: found {found} of {len(actions)}")


def test_category_in_diagnostics():
    """Diagnostics include category distribution."""
    pipeline = ZFDPipeline(data_dir=str(DATA_DIR))

    result = pipeline.process_folio("qokeedy.chol.sar", "test")
    diag = result["diagnostics"]

    assert "category_distribution" in diag, "Diagnostics should include category_distribution"
    assert isinstance(diag["category_distribution"], dict), "category_distribution should be a dict"

    # Should have at least one category
    assert len(diag["category_distribution"]) >= 1, "Should have at least one category in distribution"

    # Check for miscellany_stems count
    assert "miscellany_stems" in diag, "Diagnostics should include miscellany_stems"
    assert isinstance(diag["miscellany_stems"], int), "miscellany_stems should be an int"

    print(f"PASS diagnostics: category_distribution={diag['category_distribution']}, miscellany_stems={diag['miscellany_stems']}")


def test_backward_compat_v1():
    """Pipeline works with old lexicon.csv format."""
    old_pipeline = ZFDPipeline(
        data_dir=str(DATA_DIR),
        lexicon_file=str(DATA_DIR / "lexicon.csv")
    )

    assert not old_pipeline.lexicon.is_v2, "Should detect v1 format"

    token = Token(id="test.v1.1", eva="sar")
    result = old_pipeline.process_token(token)

    assert result.stem_known, "sar should be recognized in v1"
    assert "salt" in result.stem_gloss.lower(), f"gloss should be salt, got {result.stem_gloss}"

    # v1 should have empty croatian
    stem_data = old_pipeline.lexicon.lookup('sar')
    assert stem_data['croatian'] == '', "v1 should default croatian to empty string"

    print(f"PASS backward compat v1: sar -> {result.english}")


def test_get_category_method():
    """get_category returns correct values."""
    pipeline = ZFDPipeline(data_dir=str(DATA_DIR))

    assert pipeline.lexicon.get_category("kost") == "ingredient", "kost should be ingredient"
    assert pipeline.lexicon.get_category("hor") == "action", "hor should be action"
    assert pipeline.lexicon.get_category("nonexistent") == "unknown", "nonexistent should be unknown"

    print("PASS get_category method works correctly")


def test_get_croatian_method():
    """get_croatian returns correct values."""
    pipeline = ZFDPipeline(data_dir=str(DATA_DIR))

    assert pipeline.lexicon.get_croatian("kost") == "kost", "kost croatian should be 'kost'"
    assert pipeline.lexicon.get_croatian("ol") == "ulje", "ol croatian should be 'ulje'"
    assert pipeline.lexicon.get_croatian("nonexistent") == "", "nonexistent should return empty string"

    print("PASS get_croatian method works correctly")


def run_all_tests():
    """Run all v2 feature tests."""
    print("=" * 60)
    print("LEXICON V2 PIPELINE TESTS")
    print("=" * 60)
    print()

    tests = [
        test_v2_entry_count,
        test_miscellany_confidence,
        test_croatian_output,
        test_new_body_part_entries,
        test_new_action_entries,
        test_category_in_diagnostics,
        test_backward_compat_v1,
        test_get_category_method,
        test_get_croatian_method,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
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
        print("ALL V2 FEATURE TESTS PASSED")
    else:
        print(f"{failed} TESTS FAILED")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
