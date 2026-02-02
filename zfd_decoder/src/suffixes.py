"""
Suffix parsing for ZFD pipeline.
"""

import json
from typing import Tuple, Optional


class SuffixParser:
    def __init__(self, suffixes_file: str):
        with open(suffixes_file) as f:
            data = json.load(f)
        # Sort by length (longest first)
        self.suffixes = sorted(
            data['suffixes'],
            key=lambda x: -len(x['eva'])
        )

    def parse(self, text: str) -> Tuple[str, Optional[dict]]:
        """
        Parse suffix from end of text.

        Returns:
            Tuple of (stem, suffix_dict or None)
        """
        for suf in self.suffixes:
            if text.endswith(suf['eva']):
                stem = text[:-len(suf['eva'])]
                if stem:  # Don't strip entire word
                    return stem, suf
        return text, None
