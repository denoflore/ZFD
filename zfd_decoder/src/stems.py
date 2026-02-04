"""
Stem lexicon lookup.

Supports both v1 (6 columns) and v2 (9 columns) lexicon formats.
v2 adds: croatian, category, source columns.
"""

import csv
from typing import Optional, Dict, List, Tuple


# Confidence values for different status levels
STATUS_CONFIDENCE = {
    'CONFIRMED': 0.30,
    'CANDIDATE': 0.15,
    'MISCELLANY': 0.10,
}


class StemLexicon:
    def __init__(self, lexicon_file: str):
        self.stems: Dict[str, dict] = {}
        self._is_v2 = False

        with open(lexicon_file) as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []

            # Detect v2 format by presence of 'croatian' column
            self._is_v2 = 'croatian' in fieldnames

            for row in reader:
                variant = row['variant']
                self.stems[variant] = {
                    'name': row['name'],
                    'gloss': row['gloss'],
                    'latin': row['latin'],
                    'status': row['status'],
                    'context': row['context'],
                    # v2 fields with defaults for v1 compatibility
                    'croatian': row.get('croatian', ''),
                    'category': row.get('category', 'ingredient'),
                    'source': row.get('source', 'lexicon_v1'),
                }

    @property
    def is_v2(self) -> bool:
        """Return True if using v2 lexicon format."""
        return self._is_v2

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
        """Return the category for a stem, or 'unknown' if not found."""
        data = self.stems.get(stem)
        if data:
            return data.get('category', 'unknown')
        return 'unknown'

    def get_croatian(self, stem: str) -> str:
        """Return the Croatian form for a stem, or empty string if not found."""
        data = self.stems.get(stem)
        if data:
            return data.get('croatian', '')
        return ''

    def confidence_for_status(self, status: str) -> float:
        """Return confidence boost value for a status level.

        CONFIRMED -> 0.30
        CANDIDATE -> 0.15
        MISCELLANY -> 0.10
        """
        return STATUS_CONFIDENCE.get(status, 0.10)
