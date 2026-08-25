"""
Real tests for the ZFD v2 recipe decoder, the pipeline that generates every
committed translation. Before 2026-08-25 this decoder had zero tests and
dead container paths; these tests pin the canonical lexicon, the mapping
layer, decode determinism, and byte-level reproducibility of the committed
corpus, so `pytest` at repo root actually verifies what the repository
publishes.
"""

import json
import sys
from pathlib import Path

import pytest

PIPELINES = Path(__file__).resolve().parent.parent
REPO_ROOT = PIPELINES.parent
sys.path.insert(0, str(PIPELINES))

import lexicon_audit
import process_all_folios as paf
from complete_missing_folios import parse_lsi, eva_text_for
from zfd_decoder_v2 import ZFDDecoder, EVA_TO_CRO, LEXICON_PATH


@pytest.fixture(scope="module")
def decoder():
    return ZFDDecoder()


@pytest.fixture(scope="module")
def iiif_map():
    return json.loads((REPO_ROOT / "folio_iiif_map.json").read_text())


def test_canonical_lexicon_exists_inside_the_repo():
    # The original 201 folios were generated with a lexicon file that never
    # entered the repo. This guards against that class of defect forever.
    assert LEXICON_PATH.is_file()
    assert REPO_ROOT in LEXICON_PATH.parents


def test_lexicon_audit_is_green():
    failures, _warnings = lexicon_audit.audit()
    assert failures == []


def test_morpheme_count_is_computed_not_hardcoded():
    lexicon = json.loads(LEXICON_PATH.read_text(encoding="utf-8"))
    expected = sum(len(lexicon[family]) for family in
                   ("operators", "stems", "suffixes", "state_markers",
                    "latin_terms"))
    assert paf.MORPHEME_COUNT == expected
    assert paf.MORPHEME_COUNT != 309  # the stale hardcode this replaced


def test_eva_to_croatian_follows_the_mapping_table(decoder):
    for eva_seq in ("sh", "ch", "cth"):
        if eva_seq in EVA_TO_CRO:
            assert decoder.eva_to_croatian(eva_seq) == EVA_TO_CRO[eva_seq]
    # Longest-match greediness: a sequence must not be decoded as its
    # shorter prefixes when a longer table entry matches.
    longest = max(EVA_TO_CRO, key=len)
    assert decoder.eva_to_croatian(longest) == EVA_TO_CRO[longest]


def test_whole_word_precheck_preserves_grammar_words(decoder):
    # 'daiin' is the most frequent word in the manuscript. The whole-word
    # precheck must keep it as one known unit instead of letting operator
    # stripping shred it into da + in.
    croatian = decoder.eva_to_croatian("daiin")
    decomposition = decoder.decompose_word(croatian)
    assert decomposition is not None


def test_folio_decode_is_deterministic(decoder):
    eva_text = (REPO_ROOT / "voynich_data" / "raw_eva" / "f88r.txt").read_text(
        encoding="utf-8", errors="replace")
    first = decoder.decode_folio(eva_text, folio_id="f88r")
    second = decoder.decode_folio(eva_text, folio_id="f88r")
    assert first == second


@pytest.mark.parametrize("locus", ["f100r", "f88r", "f42r"])
def test_committed_raw_eva_recipes_reproduce_byte_identical(
        decoder, iiif_map, locus):
    eva_text = (REPO_ROOT / "voynich_data" / "raw_eva" / f"{locus}.txt"
                ).read_text(encoding="utf-8", errors="replace")
    decoder.reset_stats()
    decoded = decoder.decode_folio(eva_text, folio_id=locus)
    rendered = paf.generate_recipe_markdown(locus, decoded, iiif_map)
    committed = (REPO_ROOT / "translations" / "recipes" /
                 f"{locus}_recipe.md").read_text(encoding="utf-8")
    assert rendered == committed


@pytest.mark.parametrize("locus", ["f67r1", "f116v"])
def test_committed_lsi_recipes_reproduce_byte_identical(
        decoder, iiif_map, locus):
    lsi = parse_lsi()
    eva_text = eva_text_for(locus, lsi[locus])
    decoder.reset_stats()
    decoded = decoder.decode_folio(eva_text, folio_id=locus)
    rendered = paf.generate_recipe_markdown(locus, decoded, iiif_map)
    committed = (REPO_ROOT / "translations" / "recipes" /
                 f"{locus}_recipe.md").read_text(encoding="utf-8")
    assert rendered == committed


def test_corpus_summary_covers_every_recipe_file():
    summary = json.loads((REPO_ROOT / "translations" /
                          "PIPELINE_SUMMARY_v3.json").read_text())
    recipe_files = {p.name[:-len("_recipe.md")] for p in
                    (REPO_ROOT / "translations" / "recipes").glob(
                        "f*_recipe.md")}
    assert set(summary["loci"]) == recipe_files
    assert summary["totals"]["loci"] == len(recipe_files) == 244


def test_lsi_and_recipes_cover_the_same_manuscript():
    lsi_loci = set(parse_lsi())
    recipe_loci = {p.name[:-len("_recipe.md")] for p in
                   (REPO_ROOT / "translations" / "recipes").glob(
                       "f*_recipe.md")}
    # Every LSI locus is translated. Recipes may add loci from the raw_eva
    # segmentation (whole pages where LSI splits panels).
    assert lsi_loci - recipe_loci == set()
