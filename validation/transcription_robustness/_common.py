"""
Shared helpers for the transcription robustness tests.

Added in the 2026-11 audit. Three problems in the original harness lived
here in duplicate:

1. Seeds used Python's built-in hash(), which is randomized per process
   (PYTHONHASHSEED), so no run could be reproduced.
2. Raw voynich_data/raw_eva files were fed straight to the decoder. The
   decoder's tokenizer keeps every letter it sees, so the header line
   "=== Folio f10r ===" became tokens "folio" and "fr", "[Text]" became
   "text", and "<!plant>" comments were glued into words ("dyplantchy").
   On the five test folios that is 68 junk tokens out of 849. The noise
   injection also perturbed those header and comment letters.
3. Word positions from a "."-split of the raw file did not line up with
   decoder token positions (off by 3+ per folio), see run_layer_stratified.
"""

import hashlib
import random
import re

FILLERS = "!"  # IVTFF filler = no glyph here (LSI_ivtff_0d.txt header)


def stable_seed(*parts) -> int:
    """Deterministic seed, identical across processes and machines."""
    h = hashlib.sha256("|".join(str(p) for p in parts).encode("utf-8")).hexdigest()
    return int(h, 16) % (2 ** 32)


def is_text_line(line: str) -> bool:
    s = line.strip()
    return bool(s) and not s.startswith("===") and not s.startswith("[")


def clean_text_line(line: str) -> str:
    """Strip IVTFF markup from one text line; keep only glyphs and '.' breaks."""
    line = line.replace("<->", ".")          # drawing interruption = word break
    line = re.sub(r"<[^>]*>", "", line)      # comments, <$>, <%>
    for f in FILLERS:
        line = line.replace(f, "")
    line = line.replace(",", ".")            # dubious break -> break
    return re.sub(r"\.+", ".", line).strip(".")


def clean_folio_text(raw: str) -> str:
    """Raw EVA file -> text lines only, markup stripped. Safe to perturb."""
    return "\n".join(c for c in (clean_text_line(l) for l in raw.splitlines()
                                 if is_text_line(l)) if c)


def words_of(clean_text: str):
    """Words made only of EVA glyphs. Words with an unreadable "?" are left
    out: there is no clean reading to perturb."""
    return [w for line in clean_text.splitlines() for w in line.split(".")
            if re.fullmatch(r"[a-z]+", w)]


def shuffle_glyphs(clean_text: str, rng: random.Random) -> str:
    """Gibberish control: same line/word lengths and glyph inventory,
    glyph order shuffled across the whole folio."""
    pool = [c for c in clean_text if c.isalpha()]
    rng.shuffle(pool)
    it = iter(pool)
    return "".join(next(it) if c.isalpha() else c for c in clean_text)
