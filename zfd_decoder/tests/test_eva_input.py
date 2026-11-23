"""Regressions for raw EVA metadata leaking into real and null decodes."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "zfd_decoder" / "src"))
sys.path.insert(0, str(ROOT / "validation" / "blind_decode_test"))
sys.path.insert(0, str(ROOT / "validation" / "transcription_robustness"))

from tokenizer import tokenize_folio, words_from_eva_line
from v2_generators import (generate_char_shuffled, generate_random_latin,
                           generate_synthetic_eva)
from _common import clean_folio_text


def test_metadata_and_drawing_markup_are_not_glyph_words():
    raw = "\n=== Folio f10r ===\n[Text]\n# transcription comment\nqo!.dy<-><!plant>chy,daiin<$>\n"
    lines = tokenize_folio(raw, "f10r")
    assert [[t.eva for t in line] for line in lines] == [["qo", "dy", "chy", "daiin"]]
    assert [t.id for t in lines[0]] == [f"f10r.5.{i}" for i in range(1, 5)]


def test_raw_blind_folios_match_independently_cleaned_glyph_inputs():
    for folio in ("f10r", "f23v", "f47r", "f89r", "f101v"):
        raw = (ROOT / "voynich_data" / "raw_eva" / f"{folio}.txt").read_text(encoding="utf-8")
        words = lambda text: [t.eva for line in tokenize_folio(text, folio) for t in line]
        assert words(raw) == words(clean_folio_text(raw)), folio
        assert not any(w in ("folio", "fr", "text") or "plant" in w for w in words(raw))


def test_null_generators_preserve_effective_word_counts_and_shuffle_inventory():
    raw = "=== Folio f10r ===\n[Text]\nqo!.dy<-><!plant>chy,daiin<$>\nchol.shol\n"
    def rows(text):
        return [words_from_eva_line(line) for line in text.splitlines()]
    real = rows(raw)
    for generator in (generate_char_shuffled, generate_synthetic_eva, generate_random_latin):
        generated = rows(generator(raw, 31337))
        assert list(map(len, generated)) == list(map(len, real))
        if generator is generate_char_shuffled:
            assert [[sorted(w) for w in line] for line in generated] == [
                [sorted(w) for w in line] for line in real]
