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

        with open(lexicon_file) as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            self.v2 = 'croatian' in fieldnames

            for row in reader:
                variant = row['variant']
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

    def lookup(self, stem: str) -> Optional[dict]:
        """Look up a stem in the lexicon."""
        return self.stems.get(stem)

    def find_in_text(self, text: str) -> List[Tuple[str, dict]]:
        """Find all known stems in text."""
        found = []
        # Sort by length (longest first) to prefer longer matches
        for variant in sorted(self.stems.keys(), key=len, reverse=True):
            if variant in text:
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
