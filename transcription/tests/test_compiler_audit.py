"""
Regression tests for the 2026-11 audit of the transcription compiler and the
transcription robustness harness. Each test pins one bug that was found in
the committed code (see transcription/AUDIT_2026-11.md).
"""

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "transcription" / "scripts"))
sys.path.insert(0, str(ROOT / "validation" / "transcription_robustness"))
sys.path.insert(0, str(ROOT / "zfd_decoder" / "src"))

import batch_transcribe as bt  # noqa: E402
import _common  # noqa: E402

EVA = ROOT / "02_Transcriptions" / "LSI_ivtff_0d.txt"


# ---------------------------------------------------------------- compiler

@pytest.mark.parametrize("eva,zfd", [
    ("cthy", "htri"), ("ckhy", "hsti"), ("cphy", "hpli"), ("cfhy", "hpri"),
])
def test_bench_gallows_expand_once(eva, zfd):
    # was htrri / hstri / hplli / hplri: bench output re-fed to simple gallows
    assert bt.parse_word(eva)[0] == zfd


def test_ivtff_bang_filler_is_no_glyph():
    # "!" = one vote for no character here (LSI_ivtff_0d.txt header)
    assert bt.parse_word("sholdy!")[0] == "šoldi"       # was soldy?
    assert bt.parse_word("cth!res")[0] == "htrres"      # was htrr?res
    assert bt.parse_word("sholdy!")[1] != "D"
    assert bt.parse_line("qo!.!.chol")[0] == "ko. hol"


def test_aiin_ligature_not_split_by_da_operator():
    assert bt.parse_word("daiin")[0] == "dain"           # was daiin
    assert bt.parse_word("qokaiin")[0] == "kostain"      # unchanged
    assert bt.parse_word("okaiin")[0] == "ostain"        # unchanged


def test_aiiin_suffix_from_rules_spec():
    assert bt.parse_word("qokaiiin")[0] == "kostain"     # was kostaiiin


def test_medial_ch_matches_gold_anchor():
    # f88r label 1, Curio-validated reading
    assert bt.parse_word("otorchety")[0] == "otrorhetri"  # was otrorchetri
    assert bt.parse_word("chckhod")[0] == "hhstod"


def test_validated_set_uses_compiler_output():
    assert bt.parse_word("shol") == ("šol", "A")


@pytest.mark.parametrize("eva,zfd", [
    ("shol", "šol"),        # operator: canon š (lexicon v3, operators.json)
    ("qoshedy", "košedi"),  # medial sh, was left as raw EVA "sh"
    ("sheor", "šeor"),      # gold f88r spells it "sheor" (sh digraph = š)
])
def test_sh_is_croatian_sh_everywhere(eva, zfd):
    assert bt.parse_word(eva)[0] == zfd


@pytest.mark.parametrize("eva,zfd", [
    ("ykeor", "isteor"), ("otyda", "otrida"), ("ychey", "ihei"),  # gold anchor readings
])
def test_non_final_y_is_i(eva, zfd):
    assert bt.parse_word(eva)[0] == zfd


def test_non_plant_drawing_break_is_word_break():
    z, _ = bt.parse_line("dykaly<-><!||>daiin.chedy")
    assert z.split(". ") == ["distali", "dain", "hedi"]  # was dystalidaiin...


def test_plant_mark_survives_and_is_escaped_in_markdown():
    eva = {1: "kodalchy.chpady<-><!plant>doiin.chor"}
    parsed = {1: bt.parse_line(eva[1])}
    assert " | " in parsed[1][0]
    md = bt.generate_transcription_md("f4r", "x", eva, parsed, {"section": "herbal"})
    row = next(l for l in md.splitlines() if l.startswith("| L1 "))
    assert len(re.split(r"(?<!\\)\|", row)) - 2 == 4


def test_gallows_divergence_counts_t():
    jl = bt.generate_line_data_jsonl("fx", {1: "otol"}, {1: bt.parse_line("otol")})
    assert '"count": 1' in jl  # "t" used to be filtered out


def test_metadata_comes_from_ivtff_header():
    md = bt.generate_metadata("f80v", "1", 1, header=bt.read_page_header(EVA, "f80v"))
    assert (md["currier_language"], md["currier_hand"]) == ("B", "2")  # was A / 1
    assert md["quire"].startswith("M ")
    md = bt.generate_metadata("f67r", "1", 1, header=bt.read_page_header(EVA, "f67r"))
    assert md["quire"].startswith("I ")                                 # was K


def test_page_list_includes_multipanel_pages():
    pages = bt.list_ivtff_pages(EVA)
    for p in ["f70r", "f72r", "f89r", "f95r", "f101r", "f102r"]:
        assert p in pages and bt.extract_eva_lines(EVA, p)


def test_outputs_are_utf8(tmp_path):
    p = tmp_path / "n.md"
    bt.write_text(p, "k→st\n")
    assert p.read_bytes() == "k→st\n".encode("utf-8")


# ----------------------------------------------------- robustness harness

def test_seeds_do_not_depend_on_pythonhashseed():
    code = ("import sys; sys.path.insert(0, %r); import _common; "
            "print(_common.stable_seed('f10r', 0.05, 3))"
            % str(ROOT / "validation" / "transcription_robustness"))
    outs = {subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                           env={**os.environ, "PYTHONHASHSEED": s}).stdout for s in ("1", "2")}
    assert len(outs) == 1


def test_header_and_markup_never_reach_the_decoder():
    from tokenizer import tokenize_folio
    raw = (ROOT / "voynich_data" / "raw_eva" / "f10r.txt").read_text(encoding="utf-8")
    toks = [t.eva for line in tokenize_folio(_common.clean_folio_text(raw), "f10r") for t in line]
    assert not any(t in ("folio", "fr", "text") or "plant" in t for t in toks)


def test_word_positions_align_with_decoder_tokens():
    # the v2 layer test compared token i with EVA word i, which were 3+ apart
    # on raw files. After cleaning, word i of the text IS decoder token i.
    from tokenizer import tokenize_folio
    for f in ["f10r", "f89r", "f101v"]:
        text = _common.clean_folio_text(
            (ROOT / "voynich_data" / "raw_eva" / f"{f}.txt").read_text(encoding="utf-8"))
        toks = [t.eva for line in tokenize_folio(text, f) for t in line]
        words = [re.sub(r"[^a-z]", "", w) for line in text.splitlines() for w in line.split(".")]
        assert toks == [w for w in words if w]


def test_fingerprint_reports_non_discriminating_when_null_passes():
    import run_robustness as rr
    flat_graded = {"f": {"clean_coverage": 1.0, "rates": {
        str(r): {"coverage_mean": 1.0, "stem_identity_mean": 1 - r} for r in rr.RATES}}}
    _, flat, graded = rr.fingerprint(flat_graded)
    assert flat and graded  # a null decoder produces exactly this shape
