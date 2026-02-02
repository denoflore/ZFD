"""
Tokenizer for Voynich EVA text.
Splits lines into tokens, preserves structure.
"""

from dataclasses import dataclass, field
from typing import List, Optional
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
    tokens = []
    words = line.strip().split()

    for i, word in enumerate(words):
        # Clean the word (remove any annotation markers)
        clean_word = re.sub(r'[^a-zšžčćđ]', '', word.lower())
        if not clean_word:
            continue

        token = Token(
            id=f"{folio}.{line_num}.{i+1}",
            eva=clean_word
        )
        tokens.append(token)

    return tokens


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
    for i, line in enumerate(eva_text.strip().split('\n')):
        if line.strip():
            tokens = tokenize_line(line, folio, i + 1)
            if tokens:
                lines.append(tokens)
    return lines
