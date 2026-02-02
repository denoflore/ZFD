"""
Full ZFD decode pipeline.
"""

from dataclasses import asdict
from typing import List, Dict
from pathlib import Path

try:
    from .tokenizer import Token, tokenize_folio
    from .operators import OperatorDetector
    from .gallows import GallowsExpander
    from .suffixes import SuffixParser
    from .stems import StemLexicon
except ImportError:
    from tokenizer import Token, tokenize_folio
    from operators import OperatorDetector
    from gallows import GallowsExpander
    from suffixes import SuffixParser
    from stems import StemLexicon


class ZFDPipeline:
    def __init__(self, data_dir: str = "data"):
        data_path = Path(data_dir)
        self.operators = OperatorDetector(str(data_path / "operators.json"))
        self.lexicon = StemLexicon(str(data_path / "lexicon.csv"))
        self.gallows = GallowsExpander(
            str(data_path / "gallows.json"),
            str(data_path / "mid_word.json"),
            self.lexicon.stems
        )
        self.suffixes = SuffixParser(str(data_path / "suffixes.json"))

    def process_token(self, token: Token) -> Token:
        """Process a single token through all pipeline stages."""

        # Stage 1: Operator detection
        working = self.operators.apply_to_token(token)

        # Stage 2: Mid-word substitution
        working, mid_rewrites = self.gallows.apply_mid_word(working)
        token.rewrites.extend(mid_rewrites)
        if mid_rewrites:
            token.confidence += 0.10

        # Stage 3: Gallows expansion
        working, gal_rewrites, gal_conf = self.gallows.apply_gallows(working)
        token.rewrites.extend(gal_rewrites)
        token.confidence += gal_conf

        # Stage 4: Stem lookup (try full word first)
        stem_candidate = working
        stem_data = self.lexicon.lookup(stem_candidate)
        suffix = None

        # Stage 5: If full word not found, try suffix parsing
        if not stem_data:
            stripped_stem, suffix = self.suffixes.parse(working)
            if suffix:
                # Check if stripped stem is in lexicon
                stripped_data = self.lexicon.lookup(stripped_stem)
                if stripped_data:
                    stem_candidate = stripped_stem
                    stem_data = stripped_data
                    token.suffix = suffix['croatian']
                    token.suffix_semantic = suffix['semantic']
                    token.rewrites.append(f"suffix: {suffix['eva']}→{suffix['croatian']} ({suffix['gloss']})")
                    token.confidence += 0.15
                else:
                    # Try partial match on stripped stem
                    found = self.lexicon.find_in_text(stripped_stem)
                    if found:
                        stem_candidate = found[0][0]
                        stem_data = found[0][1]
                        token.suffix = suffix['croatian']
                        token.suffix_semantic = suffix['semantic']
                        token.rewrites.append(f"suffix: {suffix['eva']}→{suffix['croatian']} ({suffix['gloss']})")
                        token.confidence += 0.15
                    else:
                        suffix = None  # No valid suffix, keep full word

        # Stage 6: If still not found, try partial match for gloss only (keep full stem)
        if not stem_data:
            found = self.lexicon.find_in_text(stem_candidate)
            if found:
                stem_data = found[0][1]
                # Keep the full stem_candidate, just use the match for the gloss

        token.stem = stem_candidate
        if stem_data:
            token.stem_known = True
            token.stem_gloss = stem_data['gloss']
            token.confidence += 0.30
            token.notes.append(f"Stem: {stem_data['name']} ({stem_data['status']})")

        # Stage 6: Build ZFD orthography (Layer 1)
        token.zfd = self._build_zfd(token)

        # Stage 7: Build expansion (Layer 2)
        token.expansion = self._build_expansion(token)

        # Stage 8: Build Croatian (Layer 3)
        token.croatian = self._build_croatian(token)

        # Stage 9: Build English (Layer 4)
        token.english = self._build_english(token)

        # Cap confidence
        token.confidence = min(1.0, token.confidence)

        return token

    def _build_zfd(self, token: Token) -> str:
        """Build Layer 1: ZFD Orthography."""
        parts = []
        if token.operator:
            parts.append(token.operator)
        parts.append(token.stem)
        if token.suffix:
            parts.append(token.suffix)
        return "".join(parts)

    def _build_expansion(self, token: Token) -> str:
        """Build Layer 2: Shorthand Expansion with tags."""
        parts = []
        if token.operator:
            parts.append(f"[OP:{token.operator}]")
        if token.stem:
            if token.stem_known:
                parts.append(f"[STEM:{token.stem}={token.stem_gloss}]")
            else:
                parts.append(f"[STEM:{token.stem}=?]")
        if token.suffix:
            parts.append(f"[SUF:{token.suffix}={token.suffix_semantic}]")
        return "".join(parts)

    def _build_croatian(self, token: Token) -> str:
        """Build Layer 3: Normalized Croatian."""
        # Keep as procedural shorthand, not full sentences
        return token.zfd

    def _build_english(self, token: Token) -> str:
        """Build Layer 4: English gloss."""
        parts = []

        # Operator gloss
        if token.operator_type == "relative":
            parts.append("which")
        elif token.operator_type == "action":
            parts.append("combine")
        elif token.operator_type == "comitative":
            parts.append("with")
        elif token.operator_type == "dative":
            parts.append("dose")
        elif token.operator_type == "vessel":
            parts.append("vessel")

        # Stem gloss
        if token.stem_gloss:
            parts.append(token.stem_gloss)
        elif token.stem:
            parts.append(f"[{token.stem}]")

        # Suffix gloss
        if token.suffix_semantic == "processed":
            parts.append("prepared")
        elif token.suffix_semantic == "adjectival":
            pass  # often implicit
        elif token.suffix_semantic == "instrumental":
            parts.insert(0, "with")

        return " ".join(parts) if parts else token.zfd

    def process_folio(self, eva_text: str, folio: str) -> Dict:
        """Process entire folio and generate outputs."""
        lines = tokenize_folio(eva_text, folio)

        all_tokens = []
        for line in lines:
            processed_line = []
            for token in line:
                processed_line.append(self.process_token(token))
            all_tokens.append(processed_line)

        return {
            "folio": folio,
            "lines": [[asdict(t) for t in line] for line in all_tokens],
            "diagnostics": self._generate_diagnostics(all_tokens)
        }

    def _generate_diagnostics(self, lines: List[List[Token]]) -> Dict:
        """Generate falsification diagnostics."""
        all_tokens = [t for line in lines for t in line]

        if not all_tokens:
            return {
                "total_tokens": 0,
                "operator_counts": {},
                "known_stems": 0,
                "unknown_stems": 0,
                "known_ratio": 0,
                "average_confidence": 0,
                "unknown_stem_list": [],
                "validation": {}
            }

        # Count operators
        operator_counts = {}
        for t in all_tokens:
            if t.operator:
                operator_counts[t.operator] = operator_counts.get(t.operator, 0) + 1

        # Count known vs unknown stems
        known_stems = sum(1 for t in all_tokens if t.stem_known)
        unknown_stems = sum(1 for t in all_tokens if t.stem and not t.stem_known)

        # Average confidence
        avg_confidence = sum(t.confidence for t in all_tokens) / len(all_tokens)

        # Find unknown stems for lexicon growth
        unknown_list = list(set(t.stem for t in all_tokens if t.stem and not t.stem_known))

        return {
            "total_tokens": len(all_tokens),
            "operator_counts": operator_counts,
            "known_stems": known_stems,
            "unknown_stems": unknown_stems,
            "known_ratio": known_stems / (known_stems + unknown_stems) if (known_stems + unknown_stems) > 0 else 0,
            "average_confidence": round(avg_confidence, 3),
            "unknown_stem_list": sorted(unknown_list),
            "validation": {
                "kost_present": any("kost" in t.stem or "ost" in t.stem for t in all_tokens),
                "ol_present": any(t.stem in ["ol", "or"] for t in all_tokens),
                "operators_found": len(operator_counts) > 0
            }
        }
