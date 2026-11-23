"""Regressions for matched-row provenance and visible unresolved characters."""

import csv
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pipeline import ZFDPipeline
from stems import StemLexicon
from tokenizer import Token


DATA_DIR = Path(__file__).parent.parent / "data"


@pytest.fixture
def pipeline():
    return ZFDPipeline(data_dir=str(DATA_DIR))


def test_f88r_orald_uses_its_actual_matched_croatian_row(pipeline):
    # Previously the English gloss came from oral, but Croatian looked up
    # the unmatched surface orald again and silently lost the row.
    token = pipeline.process_token(Token(id="f88r.orald", eva="orald"))
    assert token.stem == token.stem_surface == "orald"
    assert token.match_type == "partial"
    assert token.matched_form == "oral"
    assert token.matched_croatian == "oralno"
    assert token.matched_category == "latin_pharma"
    assert token.matched_status == "CONFIRMED"
    assert token.matched_source == "miscellany+voynich"
    assert token.unmatched_prefix == ""
    assert token.unmatched_suffix == "d"
    assert token.zfd == "orald"
    assert token.croatian == "oralno[d]"
    assert token.english == "by mouth [d]"
    assert token.confidence == pytest.approx(0.30)


def test_suffix_partial_match_preserves_both_residual_sides(pipeline):
    # The old suffix-partial path retained only oral and rendered orali,
    # dropping both xx and d from all output layers.
    token = pipeline.process_token(Token(id="residual", eva="xxoraldy"))
    assert token.stem == "oral"  # legacy parser field remains compatible
    assert token.stem_surface == "xxorald"
    assert token.matched_form == "oral"
    assert (token.unmatched_prefix, token.unmatched_suffix) == ("xx", "d")
    assert token.suffix == "i"
    assert token.zfd == "xxoraldi"
    assert token.croatian == "[xx]oralno[d]i"
    assert token.english == "[xx] by mouth [d]"
    assert token.confidence == pytest.approx(0.45)


def test_partial_categories_and_miscellany_count_use_the_matched_rows(pipeline):
    result = pipeline.process_folio("orald.zcerz", "provenance")
    diagnostics = result["diagnostics"]
    assert diagnostics["category_distribution"] == {
        "latin_pharma": 1, "ingredient": 1,
    }
    assert diagnostics["miscellany_stems"] == 1
    assert diagnostics["match_type_counts"] == {"partial": 2}
    wax = result["lines"][0][1]
    assert wax["matched_form"] == "cer"
    assert wax["matched_source"] == "miscellany_new"
    assert wax["croatian"] == "[z]vosak[z]"


def test_one_character_rows_cannot_become_partial_or_suffix_matches(pipeline):
    # A one-character entry is still valid as an exact standalone word.
    # Disable compounds here so they cannot conceal a spurious CSV match.
    pipeline.compound = None
    pipeline.lexicon.stems["x"] = {
        "name": "fixture", "gloss": "fixture", "status": "CONFIRMED",
        "croatian": "iks", "category": "grammar", "source": "test",
    }
    exact = pipeline.process_token(Token(id="exact", eva="x"))
    assert exact.match_type == "whole_word"
    assert exact.croatian == "iks"
    for text in ("xy", "zx"):
        token = pipeline.process_token(Token(id=text, eva=text))
        assert token.match_type == "unresolved"
        assert not token.stem_known
        assert token.matched_form == ""
        assert token.suffix is None
        assert token.zfd == text
        assert token.croatian == f"[{text}]"


def test_compound_fallback_is_preserved_without_invented_croatian(pipeline):
    token = pipeline.process_token(Token(id="compound", eva="qor"))
    assert token.match_type == "compound"
    assert token.stem_known
    assert token.confidence == pytest.approx(0.50)
    assert token.matched_form == token.matched_croatian == ""
    assert token.matched_category == "compound"
    assert token.stem_gloss == "measure"  # existing proposal remains inspectable
    assert "".join(part["eva"] for part in token.compound_parts) == "qor"
    assert token.croatian == "ko[r]"
    assert token.english == "which [r]"


def test_utf8_lexicon_counts_expose_duplicate_rows_without_changing_resolution(tmp_path):
    lexicon_file = tmp_path / "lexicon.csv"
    with lexicon_file.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["name", "variant", "context", "gloss", "latin",
                         "croatian", "category", "status", "source"])
        writer.writerow(["first", "xy", "", "first", "", "prvo",
                         "ingredient", "CANDIDATE", "first"])
        writer.writerow(["other", "zz", "", "other", "", "drugo",
                         "ingredient", "CANDIDATE", "other"])
        writer.writerow(["last", "xy", "", "spoon", "", "žličica",
                         "equipment", "CONFIRMED", "last"])
    lexicon = StemLexicon(str(lexicon_file))
    assert lexicon.is_v2 is lexicon.v2 is True
    assert lexicon.row_count == 3
    assert lexicon.distinct_key_count == 2
    assert lexicon.distinct_keys == ("xy", "zz")
    assert lexicon.duplicate_variant_count == 1
    assert lexicon.lookup("xy")["croatian"] == "žličica"
    assert lexicon.lookup("xy")["source"] == "last"
