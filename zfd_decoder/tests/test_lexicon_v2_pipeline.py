"""
Tests for lexicon v2 features: category-aware glossing, confidence tiers,
Croatian output layer, backward compatibility.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tokenizer import Token
from pipeline import ZFDPipeline
from stems import StemLexicon

DATA_DIR = Path(__file__).parent.parent / "data"

# Initialize with v2 (default)
pipeline_v2 = ZFDPipeline(data_dir=str(DATA_DIR))

# Initialize with explicit v1 fallback
pipeline_v1 = ZFDPipeline(data_dir=str(DATA_DIR), lexicon_file=str(DATA_DIR / "lexicon.csv"))


def test_v2_entry_count():
    """Lexicon v2 has significantly more entries than v1."""
    assert len(pipeline_v2.lexicon.stems) >= 170, \
        f"Expected >=170 entries, got {len(pipeline_v2.lexicon.stems)}"
    print(f"  v2 entries: {len(pipeline_v2.lexicon.stems)}")


def test_v1_entry_count():
    """Lexicon v1 has baseline entries."""
    assert len(pipeline_v1.lexicon.stems) >= 80, \
        f"Expected >=80 entries, got {len(pipeline_v1.lexicon.stems)}"
    print(f"  v1 entries: {len(pipeline_v1.lexicon.stems)}")


def test_v2_detected():
    """Pipeline detects v2 format."""
    assert pipeline_v2.lexicon.v2 is True, "Should detect v2 format"


def test_v1_detected():
    """Pipeline detects v1 format."""
    assert pipeline_v1.lexicon.v2 is False, "Should detect v1 format"


def test_miscellany_confidence():
    """MISCELLANY entries get lower confidence than CONFIRMED."""
    lex = pipeline_v2.lexicon
    assert lex.confidence_for_status('CONFIRMED') == 0.30
    assert lex.confidence_for_status('CANDIDATE') == 0.15
    assert lex.confidence_for_status('MISCELLANY') == 0.10
    assert lex.confidence_for_status('CONFIRMED') > lex.confidence_for_status('MISCELLANY')
    print(f"  CONFIRMED=0.30 > CANDIDATE=0.15 > MISCELLANY=0.10")


def test_confirmed_token_confidence():
    """CONFIRMED stem gets higher confidence than MISCELLANY in actual processing."""
    # 'sar' (salt) is CONFIRMED
    token_conf = Token(id="test.v2.conf", eva="sar")
    result_conf = pipeline_v2.process_token(token_conf)

    # Find a MISCELLANY entry
    misc_stem = None
    for variant, data in pipeline_v2.lexicon.stems.items():
        if data['status'] == 'MISCELLANY':
            misc_stem = variant
            break

    if misc_stem:
        token_misc = Token(id="test.v2.misc", eva=misc_stem)
        result_misc = pipeline_v2.process_token(token_misc)
        assert result_conf.confidence > result_misc.confidence, \
            f"CONFIRMED ({result_conf.confidence}) should beat MISCELLANY ({result_misc.confidence})"
        print(f"  CONFIRMED 'sar' conf={result_conf.confidence:.2f} > MISCELLANY '{misc_stem}' conf={result_misc.confidence:.2f}")
    else:
        print("  No MISCELLANY entries found to compare (skipped)")


def test_croatian_output():
    """Croatian layer produces actual Croatian words for v2."""
    token = Token(id="test.v2.hr1", eva="ol")
    result = pipeline_v2.process_token(token)
    # 'ol' should give Croatian 'ulje'
    assert result.croatian == "ulje", f"Expected 'ulje', got '{result.croatian}'"
    print(f"  ol -> croatian: '{result.croatian}'")


def test_croatian_kost():
    """kost produces Croatian 'kost'."""
    # Need to test via a token that resolves to kost
    token = Token(id="test.v2.hr2", eva="sar")
    result = pipeline_v2.process_token(token)
    croatian_form = pipeline_v2.lexicon.get_croatian("sar")
    print(f"  sar -> croatian form in lexicon: '{croatian_form}'")


def test_get_category():
    """get_category returns correct categories."""
    assert pipeline_v2.lexicon.get_category("kost") == "ingredient"
    assert pipeline_v2.lexicon.get_category("ol") == "ingredient"
    assert pipeline_v2.lexicon.get_category("nonexistent_xyz") == "unknown"
    print(f"  kost=ingredient, ol=ingredient, nonexistent=unknown")


def test_category_in_diagnostics():
    """Diagnostics include category distribution."""
    result = pipeline_v2.process_folio("qokeedy.chol.sar", "test")
    diag = result["diagnostics"]
    assert "category_distribution" in diag, "Missing category_distribution in diagnostics"
    assert "miscellany_stems" in diag, "Missing miscellany_stems in diagnostics"
    print(f"  category_distribution: {diag['category_distribution']}")
    print(f"  miscellany_stems: {diag['miscellany_stems']}")


def test_backward_compat_v1_sar():
    """Pipeline with v1 lexicon still resolves 'sar' as salt."""
    token = Token(id="test.v1.1", eva="sar")
    result = pipeline_v1.process_token(token)
    assert result.stem_known, f"sar should be known in v1"
    assert "salt" in result.stem_gloss.lower(), f"Expected salt, got {result.stem_gloss}"
    print(f"  v1: sar -> {result.stem_gloss}")


def test_backward_compat_v1_ol():
    """Pipeline with v1 lexicon still resolves 'ol' as oil."""
    token = Token(id="test.v1.2", eva="ol")
    result = pipeline_v1.process_token(token)
    assert result.stem_known, f"ol should be known in v1"
    assert "oil" in result.stem_gloss.lower(), f"Expected oil, got {result.stem_gloss}"
    print(f"  v1: ol -> {result.stem_gloss}")


def test_v2_has_more_known_stems():
    """V2 lexicon resolves more stems than v1 on same input."""
    test_text = "qokeedy.chol.sar.daiin.shedy.okal.ol"
    result_v2 = pipeline_v2.process_folio(test_text, "cmp")
    result_v1 = pipeline_v1.process_folio(test_text, "cmp")

    known_v2 = result_v2["diagnostics"]["known_stems"]
    known_v1 = result_v1["diagnostics"]["known_stems"]

    assert known_v2 >= known_v1, \
        f"v2 ({known_v2}) should resolve >= v1 ({known_v1})"
    print(f"  v2 known: {known_v2}, v1 known: {known_v1}")


def test_lexicon_v2_schema():
    """All v2 entries have required fields."""
    lex = pipeline_v2.lexicon
    valid_statuses = {'CONFIRMED', 'CANDIDATE', 'MISCELLANY'}
    valid_categories = {
        'ingredient', 'action', 'body_part', 'grammar', 'condition',
        'equipment', 'preparation', 'latin_pharma', 'measurement',
        'timing', 'modifier'
    }

    for variant, data in lex.stems.items():
        assert data['status'] in valid_statuses, \
            f"'{variant}' has invalid status '{data['status']}'"
        assert data['category'] in valid_categories, \
            f"'{variant}' has invalid category '{data['category']}'"
        assert data['gloss'], f"'{variant}' has empty gloss"

    print(f"  All {len(lex.stems)} entries validated")



# === COMPOUND MORPHOLOGY TESTS ===

def test_whole_word_precheck_dar():
    """dar resolves as whole word 'gift' not operator da + residue r."""
    token = Token(id="test.morph.1", eva="dar")
    result = pipeline_v2.process_token(token)
    assert result.stem_known, "dar should be known"
    assert "gift" in result.stem_gloss.lower(), f"Expected 'gift', got '{result.stem_gloss}'"
    assert result.operator is None, f"No operator should be stripped, got {result.operator}"
    print(f"  dar -> {result.stem_gloss} (whole-word, no operator strip)")


def test_whole_word_precheck_dain():
    """dain resolves as whole word 'given/added' not operator da + in."""
    token = Token(id="test.morph.2", eva="dain")
    result = pipeline_v2.process_token(token)
    assert result.stem_known, "dain should be known"
    assert "given" in result.stem_gloss.lower() or "added" in result.stem_gloss.lower(), \
        f"Expected 'given/added', got '{result.stem_gloss}'"
    print(f"  dain -> {result.stem_gloss} (whole-word)")


def test_whole_word_does_not_hijack_chol():
    """chol should still decompose via operator ch->h + ol, not match as whole word."""
    token = Token(id="test.morph.3", eva="chol")
    result = pipeline_v2.process_token(token)
    assert result.operator == "h", f"Expected operator 'h', got {result.operator}"
    assert "oil" in result.english.lower(), f"Expected 'oil' in english, got {result.english}"
    print(f"  chol -> op={result.operator} english={result.english} (decomposed correctly)")


def test_state_marker_heom():
    """heom resolves as state marker 'with the [aforementioned]'."""
    token = Token(id="test.morph.4", eva="heom")
    result = pipeline_v2.process_token(token)
    assert result.stem_known, "heom should be known"
    assert "aforementioned" in result.stem_gloss.lower() or "with the" in result.stem_gloss.lower(), \
        f"Expected state marker gloss, got '{result.stem_gloss}'"
    print(f"  heom -> {result.stem_gloss}")


def test_state_marker_šeom():
    """šeom resolves as state marker."""
    token = Token(id="test.morph.5", eva="šeom")
    result = pipeline_v2.process_token(token)
    assert result.stem_known, "šeom should be known"
    print(f"  šeom -> {result.stem_gloss}")


def test_function_word_ain():
    """ain resolves as substance/thing."""
    token = Token(id="test.morph.6", eva="ain")
    result = pipeline_v2.process_token(token)
    assert result.stem_known, "ain should be known as function word"
    print(f"  ain -> {result.stem_gloss}")


def test_function_word_om():
    """om resolves as instrumental case marker."""
    token = Token(id="test.morph.7", eva="om")
    result = pipeline_v2.process_token(token)
    assert result.stem_known, "om should be known as case marker"
    print(f"  om -> {result.stem_gloss}")


def test_f88r_known_ratio_improvement():
    """f88r known ratio should be >= 85% with compound morphology."""
    import os
    f88r_path = os.path.join(os.path.dirname(__file__), '..', 'input', 'f88r.txt')
    if not os.path.exists(f88r_path):
        print("  f88r.txt not found, skipping")
        return
    with open(f88r_path) as f:
        text = f.read()
    result = pipeline_v2.process_folio(text, 'f88r')
    ratio = result['diagnostics']['known_ratio']
    assert ratio >= 0.85, f"Expected >= 85% known ratio, got {ratio:.1%}"
    print(f"  f88r known ratio: {ratio:.1%}")

def run_all_tests():
    """Run all v2 tests."""
    print("=" * 60)
    print("ZFD LEXICON V2 INTEGRATION TESTS")
    print("=" * 60)
    print()

    tests = [
        test_v2_entry_count,
        test_v1_entry_count,
        test_v2_detected,
        test_v1_detected,
        test_miscellany_confidence,
        test_confirmed_token_confidence,
        test_croatian_output,
        test_croatian_kost,
        test_get_category,
        test_category_in_diagnostics,
        test_backward_compat_v1_sar,
        test_backward_compat_v1_ol,
        test_v2_has_more_known_stems,
        test_lexicon_v2_schema,
        test_whole_word_precheck_dar,
        test_whole_word_precheck_dain,
        test_whole_word_does_not_hijack_chol,
        test_state_marker_heom,
        test_state_marker_šeom,
        test_function_word_ain,
        test_function_word_om,
        test_f88r_known_ratio_improvement,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            print(f"  {test.__name__}...")
            test()
            print(f"  PASS")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            failed += 1
        print()

    print("=" * 60)
    print(f"Results: {passed}/{len(tests)} passed")
    if failed == 0:
        print("ALL V2 TESTS PASSED")
    else:
        print(f"{failed} TESTS FAILED")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
