"""
Tokenizer for Voynich EVA text.
Splits lines into tokens, preserves structure.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class Token:
    """A single token from EVA transcription."""
    id: str                    # folio.line.index format
    eva: str                   # original EVA
    zfd: str = ""             # ZFD orthography
    operator: Optional[str] = None
    operator_type: Optional[str] = None
    stem: str = ""
    stem_known: bool = False
    stem_gloss: str = ""
    suffix: Optional[str] = None
    suffix_semantic: Optional[str] = None
    expansion: str = ""        # full shorthand expansion
    croatian: str = ""         # normalized Croatian
    english: str = ""          # English gloss
    confidence: float = 0.0
    rewrites: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    # Match provenance is additive: stem retains the parser's legacy value,
    # while stem_surface preserves all expanded characters around a match.
    match_type: str = "unresolved"
    matched_form: str = ""
    matched_croatian: str = ""
    matched_category: str = ""
    matched_status: str = ""
    matched_source: str = ""
    stem_surface: str = ""
    unmatched_prefix: str = ""
    unmatched_suffix: str = ""
    compound_parts: List[Dict] = field(default_factory=list)


def words_from_eva_line(line: str) -> List[str]:
    """Read glyph words, excluding file metadata and IVTFF annotations.

    Drawing interruptions and commas are word boundaries. IVTFF ``!`` is
    filler (no glyph), and other angle-bracket annotations are not text.
    Keep this normalization shared with the null-baseline generators so
    that the real and synthetic inputs have the same effective word counts.
    """
    line = line.strip()
    if not line or line.startswith(("===", "[", "#")):
        return []
    line = line.replace("<->", ".")
    line = re.sub(r"<[^>]*>", "", line).replace("!", "")
    words = (re.sub(r"[^a-zšžčćđ]", "", word.lower())
             for word in re.split(r"[.,\s]+", line))
    return [word for word in words if word]


def tokenize_line(line: str, folio: str, line_num: int) -> List[Token]:
    """
    Tokenize a single EVA line.

    Args:
        line: EVA text line
        folio: Folio identifier (e.g., "f88r")
        line_num: Line number (1-indexed)

    Returns:
        List of Token objects
    """
    return [Token(id=f"{folio}.{line_num}.{i}", eva=word)
            for i, word in enumerate(words_from_eva_line(line), 1)]


def tokenize_folio(eva_text: str, folio: str) -> List[List[Token]]:
    """
    Tokenize an entire folio.

    Args:
        eva_text: Full EVA text for folio
        folio: Folio identifier

    Returns:
        List of lines, each containing list of tokens
    """
    lines = []
    for i, line in enumerate(eva_text.splitlines()):
        if line.strip():
            tokens = tokenize_line(line, folio, i + 1)
            if tokens:
                lines.append(tokens)
    return lines
