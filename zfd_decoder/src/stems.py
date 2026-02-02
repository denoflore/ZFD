"""
Stem lexicon lookup.
"""

import csv
from typing import Optional, Dict, List, Tuple


class StemLexicon:
    def __init__(self, lexicon_file: str):
        self.stems: Dict[str, dict] = {}
        with open(lexicon_file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                variant = row['variant']
                self.stems[variant] = {
                    'name': row['name'],
                    'gloss': row['gloss'],
                    'latin': row['latin'],
                    'status': row['status'],
                    'context': row['context']
                }

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
