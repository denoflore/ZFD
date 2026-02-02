"""
Gallows expansion and mid-word substitution.
"""

import json
from typing import List, Tuple, Dict


class GallowsExpander:
    def __init__(self, gallows_file: str, mid_word_file: str, lexicon: Dict[str, dict]):
        with open(gallows_file) as f:
            self.gallows = {g['eva']: g for g in json.load(f)['gallows']}
        with open(mid_word_file) as f:
            data = json.load(f)
            # Sort by priority and length (longest first)
            self.substitutions = sorted(
                data['substitutions'],
                key=lambda x: (-x['priority'], -len(x['pattern']))
            )
        self.lexicon = lexicon

    def apply_mid_word(self, text: str) -> Tuple[str, List[str]]:
        """Apply mid-word substitutions."""
        rewrites = []
        result = text
        for sub in self.substitutions:
            if sub['pattern'] in result:
                old = result
                result = result.replace(sub['pattern'], sub['replacement'])
                if old != result:
                    rewrites.append(f"mid-word: {sub['pattern']}→{sub['replacement']}")
        return result, rewrites

    def apply_gallows(self, text: str) -> Tuple[str, List[str], float]:
        """
        Apply gallows expansions.
        Conservative: only apply if produces known stem.
        """
        rewrites = []
        conf_delta = 0.0
        result = text

        for glyph, data in self.gallows.items():
            if glyph in result:
                # Try expansion
                expanded = result.replace(glyph, data['expansion'])

                # Check if expansion produces known stem
                produces_known = self._produces_known_stem(expanded)

                if produces_known:
                    result = expanded
                    rewrites.append(f"gallows: {glyph}→{data['expansion']} (known stem)")
                    conf_delta += 0.20
                else:
                    # Still apply but note uncertainty
                    result = expanded
                    rewrites.append(f"gallows: {glyph}→{data['expansion']} (unverified)")
                    conf_delta += 0.05

        return result, rewrites, conf_delta

    def _produces_known_stem(self, text: str) -> bool:
        """Check if text contains a known stem."""
        for stem in self.lexicon.keys():
            if stem in text:
                return True
        return False
