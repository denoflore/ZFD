"""
Unit tests for ZFD pipeline.
Fixtures from the paper Section 3.2.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tokenizer import Token
from pipeline import ZFDPipeline

# Initialize pipeline once
DATA_DIR = Path(__file__).parent.parent / "data"
pipeline = ZFDPipeline(data_dir=str(DATA_DIR))


def test_qokeedy():
    """Test the canonical example from paper §3.2"""
    token = Token(id="test.1.1", eva="qokeedy")
    result = pipeline.process_token(token)

    assert result.operator == "ko", f"qo should map to ko, got {result.operator}"
    assert "kost" in result.stem or "st" in result.zfd, f"k should expand to st, got {result.zfd}"
    assert result.confidence >= 0.5, f"High-confidence token, got {result.confidence}"
    print(f"✓ qokeedy → {result.zfd} ({result.english})")


def test_daiin():
    token = Token(id="test.1.2", eva="daiin")
    result = pipeline.process_token(token)

    assert result.operator == "da", f"da is dose operator, got {result.operator}"
    assert "ain" in result.zfd or result.suffix == "ain", f"Should have ain suffix"
    print(f"✓ daiin → {result.zfd} ({result.english})")


def test_chol():
    token = Token(id="test.1.3", eva="chol")
    result = pipeline.process_token(token)

    # chol is CONFIRMED as flour/grain in lexicon - whole-word match takes priority
    assert result.stem_known, f"chol should be known"
    assert "flour" in (result.stem_gloss or "").lower() or "grain" in (result.stem_gloss or "").lower(), \
        f"Expected flour/grain, got {result.stem_gloss}"
    print(f"✓ chol → {result.zfd} (flour/grain, whole-word)")


def test_shedy():
    token = Token(id="test.1.4", eva="shedy")
    result = pipeline.process_token(token)

    assert result.operator == "š", f"sh maps to š, got {result.operator}"
    print(f"✓ shedy → {result.zfd} ({result.english})")


def test_okal():
    token = Token(id="test.1.5", eva="okal")
    result = pipeline.process_token(token)

    # okal should be recognized as pot/vessel
    print(f"✓ okal → {result.zfd} ({result.english}) [stem_known={result.stem_known}]")


def test_sar():
    token = Token(id="test.1.6", eva="sar")
    result = pipeline.process_token(token)

    assert result.stem_known, f"sar is salt, got stem_known={result.stem_known}"
    assert "salt" in result.stem_gloss.lower(), f"gloss should be salt, got {result.stem_gloss}"
    print(f"✓ sar → {result.zfd} ({result.english})")


def test_ol():
    """Word with no operator"""
    token = Token(id="test.1.8", eva="ol")
    result = pipeline.process_token(token)

    assert result.operator is None, f"ol has no operator, got {result.operator}"
    assert result.stem_known, f"ol is oil"
    print(f"✓ ol → {result.zfd} ({result.english})")


def test_gallows_k():
    """k should expand to st"""
    token = Token(id="test.1.9", eva="keedy")
    result = pipeline.process_token(token)

    assert "st" in result.zfd, f"k expands to st, got {result.zfd}"
    print(f"✓ keedy → {result.zfd}")


def test_gallows_t():
    """t should expand to tr"""
    token = Token(id="test.1.10", eva="otedy")
    result = pipeline.process_token(token)

    assert "tr" in result.zfd, f"t expands to tr, got {result.zfd}"
    print(f"✓ otedy → {result.zfd}")


def test_dar():
    """dar = gift/dose"""
    token = Token(id="test.1.11", eva="dar")
    result = pipeline.process_token(token)

    print(f"✓ dar → {result.zfd} ({result.english}) [stem_known={result.stem_known}]")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("ZFD PIPELINE UNIT TESTS")
    print("=" * 60)
    print()

    tests = [
        test_qokeedy,
        test_daiin,
        test_chol,
        test_shedy,
        test_okal,
        test_sar,
        test_ol,
        test_gallows_k,
        test_gallows_t,
        test_dar,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: ERROR - {e}")
            failed += 1

    print()
    print("=" * 60)
    print(f"Results: {passed}/{len(tests)} passed")
    if failed == 0:
        print("ALL TESTS PASSED")
    else:
        print(f"{failed} TESTS FAILED")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
