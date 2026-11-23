"""
Stem lexicon lookup.
Supports both v1 (6-column) and v2 (9-column) lexicon formats.
"""

import csv
from typing import Optional, Dict, List, Tuple


class StemLexicon:
    def __init__(self, lexicon_file: str):
        self.stems: Dict[str, dict] = {}
        self.v2 = False
        self.row_count = 0
        # Number of additional rows reusing an earlier variant key. Keep the
        # established last-row-wins policy, but make its effect inspectable.
        self.duplicate_variant_count = 0

        with open(lexicon_file, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            self.v2 = 'croatian' in fieldnames

            for row in reader:
                self.row_count += 1
                variant = row['variant']
                if variant in self.stems:
                    self.duplicate_variant_count += 1
                entry = {
                    'name': row['name'],
                    'gloss': row['gloss'],
                    'latin': row['latin'],
                    'status': row['status'],
                    'context': row['context'],
                    'croatian': row.get('croatian', ''),
                    'category': row.get('category', 'ingredient'),
                    'source': row.get('source', 'lexicon_v1'),
                }
                self.stems[variant] = entry

    @property
    def is_v2(self) -> bool:
        """Compatibility alias for the existing v2 format flag."""
        return self.v2

    @property
    def distinct_key_count(self) -> int:
        """Number of lookup keys after duplicate-row resolution."""
        return len(self.stems)

    @property
    def distinct_keys(self) -> Tuple[str, ...]:
        """Lookup keys in their established CSV insertion order."""
        return tuple(self.stems)

    def lookup(self, stem: str) -> Optional[dict]:
        """Look up a stem in the lexicon."""
        return self.stems.get(stem)

    def find_in_text(self, text: str, min_length: int = 1) -> List[Tuple[str, dict]]:
        """Find known stems, optionally excluding short substring matches."""
        found = []
        # Sort by length (longest first) to prefer longer matches
        for variant in sorted(self.stems.keys(), key=len, reverse=True):
            if len(variant) >= min_length and variant in text:
                found.append((variant, self.stems[variant]))
        return found

    def get_category(self, stem: str) -> str:
        """Return the semantic category for a stem, or 'unknown'."""
        entry = self.stems.get(stem)
        if entry:
            return entry.get('category', 'unknown')
        return 'unknown'

    def get_croatian(self, stem: str) -> str:
        """Return the Croatian form for a stem, or empty string."""
        entry = self.stems.get(stem)
        if entry:
            return entry.get('croatian', '')
        return ''

    def confidence_for_status(self, status: str) -> float:
        """Return confidence boost based on entry status tier."""
        return {
            'CONFIRMED': 0.30,
            'CANDIDATE': 0.15,
            'MISCELLANY': 0.10,
        }.get(status, 0.10)
