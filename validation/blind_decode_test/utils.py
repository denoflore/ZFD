"""Shared utilities for blind decode test."""

import hashlib
import json
import random
from pathlib import Path
from typing import List, Dict


def sha256_file(filepath: str) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def load_eva_folio(folio_id: str, data_dir: str) -> str:
    """Load EVA transcription for a folio."""
    filepath = Path(data_dir) / "voynich_data" / "raw_eva" / f"{folio_id}.txt"
    if not filepath.exists():
        raise FileNotFoundError(f"EVA file not found: {filepath}")
    with open(filepath, encoding='utf-8') as f:
        return f.read()


def shuffle_eva_text(eva_text: str, seed: int) -> str:
    """
    Shuffle EVA text while preserving word boundaries and line structure.

    This creates a null baseline: same vocabulary, same word count per line,
    but words randomly reassigned to different positions.
    """
    rng = random.Random(seed)

    lines = eva_text.strip().split('\n')
    # Collect all words
    all_words = []
    line_lengths = []
    for line in lines:
        words = line.strip().split()
        # Skip comment lines, headers, section markers, and empty lines
        if not words or words[0].startswith('#') or words[0].startswith('<') or words[0].startswith('=') or words[0].startswith('['):
            line_lengths.append(0)
            continue
        all_words.extend(words)
        line_lengths.append(len(words))

    # Shuffle all words
    rng.shuffle(all_words)

    # Reconstruct with original line lengths
    shuffled_lines = []
    word_idx = 0
    for i, length in enumerate(line_lengths):
        if length == 0:
            shuffled_lines.append(lines[i])  # preserve comments/headers
        else:
            line_words = all_words[word_idx:word_idx + length]
            shuffled_lines.append(' '.join(line_words))
            word_idx += length

    return '\n'.join(shuffled_lines)


def save_json(data: dict, filepath: str):
    """Save data as formatted JSON."""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(filepath: str) -> dict:
    """Load JSON data."""
    with open(filepath, encoding='utf-8') as f:
        return json.load(f)


def get_project_root() -> Path:
    """Get the project root directory (ZFD)."""
    # Navigate up from validation/blind_decode_test to ZFD
    return Path(__file__).parent.parent.parent


def get_lexicon_path() -> Path:
    """Get path to the lexicon file used by the pipeline."""
    return get_project_root() / "zfd_decoder" / "data" / "lexicon.csv"


def get_data_dir() -> Path:
    """Get path to the zfd_decoder data directory."""
    return get_project_root() / "zfd_decoder" / "data"
