"""
Compound morpheme decomposer for ZFD pipeline.

Handles multi-morpheme tokens that the basic pipeline can't resolve
by decomposing them into known morphemes from the unified lexicon.

Uses scored recursive decomposition with sub-morphemic binding elements
(vowels, gallows chars, cluster markers) to bridge between content morphemes.
"""

import json
from typing import Optional, List, Tuple, Dict
from pathlib import Path


class CompoundDecomposer:
    """Decomposes compound EVA tokens into known morphemes."""

    def __init__(self, unified_lexicon_path: str):
        """Load morpheme dictionary from unified lexicon JSON."""
        with open(unified_lexicon_path) as f:
            unified = json.load(f)

        self.morphemes = {}

        # Content morphemes from unified lexicon
        for section in ['operators', 'state_markers', 'stems',
                        'suffixes', 'latin_terms']:
            for key, entry in unified.get(section, {}).items():
                self.morphemes[key] = {
                    'type': section.rstrip('s').replace('_term', ''),
                    'gloss': entry.get('meaning_en', '?'),
                    'content': True
                }

        # Sub-morphemic elements (binding vowels, gallows, clusters)
        sub = {
            'o': ('binding', 'binding vowel'),
            'a': ('binding', 'case vowel'),
            'e': ('binding', 'case vowel'),
            't': ('gallows', 'compound marker (tr-)'),
            'p': ('gallows', 'preparation (pl-)'),
            'r': ('suffix_char', 'agent/doer'),
            'n': ('suffix_char', 'noun marker'),
            'd': ('suffix_char', 'past/done'),
            'c': ('cluster', 'cluster onset'),
            'g': ('cluster', 'voiced stop'),
        }
        for key, (mtype, gloss) in sub.items():
            if key not in self.morphemes:
                self.morphemes[key] = {
                    'type': mtype, 'gloss': gloss, 'content': False
                }

    def decompose(self, eva_token: str,
                   max_depth: int = 8) -> Optional[List[Dict]]:
        """
        Decompose a compound EVA token into morphemes.

        Returns list of morpheme dicts or None if coverage < 60%.
        Each dict has: eva, type, gloss, content (bool).
        """
        if len(eva_token) <= 1:
            # Single char: check directly
            if eva_token in self.morphemes:
                m = self.morphemes[eva_token]
                return [{'eva': eva_token, 'type': m['type'],
                         'gloss': m['gloss'], 'content': m['content']}]
            return None

        parts, score = self._recurse(eva_token, 0, max_depth)
        if parts is None:
            return None

        # Check coverage: at least 60% by char count
        covered = sum(len(p['eva']) for p in parts)
        if covered / len(eva_token) < 0.6:
            return None

        return parts

    def _recurse(self, word: str, depth: int,
                  max_depth: int) -> Tuple[Optional[List[Dict]], float]:
        if not word:
            return ([], 0.0)
        if depth > max_depth:
            return (None, -999.0)

        best_parts = None
        best_score = -1.0

        for end in range(len(word), 0, -1):
            prefix = word[:end]
            if prefix not in self.morphemes:
                continue

            m = self.morphemes[prefix]
            prefix_score = self._score_match(prefix, m)

            remainder = word[end:]
            if not remainder:
                candidate = [self._make_part(prefix, m)]
                total_score = prefix_score
            else:
                rest_parts, rest_score = self._recurse(
                    remainder, depth + 1, max_depth)
                if rest_parts is None:
                    continue
                candidate = [self._make_part(prefix, m)] + rest_parts
                total_score = prefix_score + rest_score

            if total_score > best_score:
                best_parts = candidate
                best_score = total_score

        return (best_parts, best_score)

    def _score_match(self, text: str, morpheme: Dict) -> float:
        """Score a morpheme match. Rewards longer content morphemes."""
        mtype = morpheme['type']
        length = len(text)

        if length >= 3 and mtype in ('stem', 'latin'):
            return length * 5.0
        elif length >= 2 and mtype in ('stem', 'operator', 'state_marker'):
            return length * 3.0
        elif length == 2 and mtype == 'suffix':
            return length * 2.0
        elif not morpheme.get('content', True):
            return 0.3  # sub-morphemic: just bridges
        elif length == 1:
            return 0.5
        else:
            return float(length)

    def _make_part(self, eva: str, morpheme: Dict) -> Dict:
        return {
            'eva': eva,
            'type': morpheme['type'],
            'gloss': morpheme['gloss'],
            'content': morpheme.get('content', True)
        }

    def build_gloss(self, parts: List[Dict]) -> str:
        """Build readable English gloss from content morphemes only."""
        content = [p for p in parts if p['content']]
        if not content:
            return '(compound)'
        glosses = []
        for p in content:
            g = p['gloss']
            if '/' in g:
                g = g.split('/')[0].strip()
            if g.startswith('~') or g.startswith('('):
                continue  # skip numeric approximations and meta
            glosses.append(g)
        return ' '.join(glosses) if glosses else '(compound)'

    def format_decomposition(self, parts: List[Dict]) -> str:
        """Format for debug output."""
        segments = []
        for p in parts:
            if p['content']:
                segments.append(f"[{p['eva']}={p['gloss'][:20]}]")
            else:
                segments.append(p['eva'])
        return ' '.join(segments)
