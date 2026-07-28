"""Canonical whole corpus pixel to translation parity materialisation."""

from .core import (
    CorpusParityBundle,
    PARITY_FILES,
    build_corpus_parity,
    read_corpus_parity,
    validate_corpus_parity_bundle,
    write_corpus_parity_new,
)

__all__ = [
    "CorpusParityBundle",
    "PARITY_FILES",
    "build_corpus_parity",
    "read_corpus_parity",
    "validate_corpus_parity_bundle",
    "write_corpus_parity_new",
]


__version__ = "0.1.0"
