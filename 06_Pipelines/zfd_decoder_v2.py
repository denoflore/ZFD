#!/usr/bin/env python3
"""
ZFD Folio Decoder Pipeline v2.0
================================
Takes EVA transcription, applies unified lexicon, produces 4-layer interlinear:
  EVA > CRO (Croatian transliteration) > EXP (expanded morphemes) > ENG (English gloss)

Uses the unified_lexicon.json as single source of truth.
Outputs per-word confidence and flags unknowns explicitly.
"""

import json
import re
import sys
from pathlib import Path
from collections import defaultdict

PIPELINE_DIR = Path("/home/claude/zfd/pipeline")
LEXICON_PATH = PIPELINE_DIR / "unified_lexicon.json"

# ================================================================
# EVA TO CROATIAN CHARACTER MAP
# ================================================================
# Standard ZFD transliteration from EVA alphabet to Croatian/Latin characters

EVA_TO_CRO = {
    # Consonant clusters
    "cth": "ctrr",
    "ckh": "cst",
    "cph": "cpll",
    "cfh": "cpll",
    "pch": "ph",
    "tch": "th",
    "sch": "šh",
    # Gallows characters
    "ch": "h",
    "sh": "š",
    "ck": "st",
    "cf": "pl",
    "cp": "pl",
    # Simple consonants
    "k": "st",
    "t": "t",
    "p": "p",
    "f": "f",
    "d": "d",
    "l": "l",
    "r": "r",
    "s": "s",
    "n": "n",
    "m": "m",
    "g": "g",
    "q": "k",
    # Vowels
    "a": "a",
    "o": "o",
    "e": "e",
    "i": "i",
    "y": "y",
    "u": "u",
}

# Longer sequences first for greedy matching
EVA_SORTED = sorted(EVA_TO_CRO.keys(), key=len, reverse=True)


class ZFDDecoder:
    def __init__(self, lexicon_path=LEXICON_PATH):
        with open(lexicon_path) as f:
            self.lexicon = json.load(f)
        
        self.operators = self.lexicon["operators"]
        self.stems = self.lexicon["stems"]
        self.suffixes = self.lexicon["suffixes"]
        self.latin_terms = self.lexicon["latin_terms"]
        self.state_markers = self.lexicon.get("state_markers", {})
        
        # Build lookup tables sorted by length (longest first for greedy match)
        self.op_keys = sorted(self.operators.keys(), key=len, reverse=True)
        self.stem_keys = sorted(self.stems.keys(), key=len, reverse=True)
        self.sfx_keys = sorted(self.suffixes.keys(), key=len, reverse=True)
        self.latin_keys = sorted(self.latin_terms.keys(), key=len, reverse=True)
        self.state_keys = sorted(self.state_markers.keys(), key=len, reverse=True)
        
        # Stats
        self.stats = {
            "total_words": 0,
            "fully_resolved": 0,
            "partially_resolved": 0,
            "unknown": 0,
            "latin_detected": 0,
        }
    
    def eva_to_croatian(self, eva_text):
        """Convert EVA alphabet to Croatian/Latin characters"""
        result = []
        i = 0
        text = eva_text.lower().strip()
        
        while i < len(text):
            matched = False
            for seq in EVA_SORTED:
                if text[i:i+len(seq)] == seq:
                    result.append(EVA_TO_CRO[seq])
                    i += len(seq)
                    matched = True
                    break
            if not matched:
                result.append(text[i])
                i += 1
        
        return "".join(result)
    
    def decompose_word(self, cro_word):
        """
        Decompose a Croatian-transliterated word into operator + stem + suffix.
        Returns: {
            "operator": {"form": str, "meaning": str} or None,
            "state": {"form": str, "meaning": str} or None,
            "stem": {"form": str, "meaning_en": str, "meaning_hr": str, "latin": str} or None,
            "suffix": {"form": str, "meaning": str} or None,
            "latin_match": {"form": str, "meaning_en": str} or None,
            "residue": str,  # unmatched portion
            "confidence": float,  # 0.0 to 1.0
        }
        """
        word = cro_word.lower().strip()
        if not word:
            return None
        
        result = {
            "original": word,
            "operator": None,
            "state": None,
            "stem": None,
            "suffix": None,
            "latin_match": None,
            "residue": "",
            "confidence": 0.0,
        }
        
        # 1. Check for exact Latin term match first
        for lt in self.latin_keys:
            if word == lt or word.startswith(lt):
                entry = self.latin_terms[lt]
                result["latin_match"] = {
                    "form": lt,
                    "meaning_en": entry["meaning_en"],
                    "latin_full": entry.get("latin_full", lt),
                }
                if word == lt:
                    result["confidence"] = 0.95
                    result["residue"] = word[len(lt):]
                    return result
                else:
                    # Partial Latin match, continue decomposing the rest
                    result["residue"] = word[len(lt):]
                    result["confidence"] = 0.7
        
        remaining = word
        chars_matched = 0
        
        # 2. Check for operator prefix
        for op in self.op_keys:
            if remaining.startswith(op) and len(remaining) > len(op):
                entry = self.operators[op]
                result["operator"] = {
                    "form": op,
                    "meaning": entry["meaning_en"],
                }
                remaining = remaining[len(op):]
                chars_matched += len(op)
                break
        
        # 3. Check for state marker (after operator, before stem)
        for st in self.state_keys:
            if remaining.startswith(st) and len(remaining) > len(st):
                entry = self.state_markers[st]
                result["state"] = {
                    "form": st,
                    "meaning": entry["meaning_en"],
                }
                remaining = remaining[len(st):]
                chars_matched += len(st)
                break
        
        # 4. Check for suffix (from end)
        suffix_found = None
        for sfx in self.sfx_keys:
            if remaining.endswith(sfx) and len(remaining) > len(sfx):
                entry = self.suffixes[sfx]
                suffix_found = {
                    "form": sfx,
                    "meaning": entry["meaning_en"],
                    "function": entry.get("grammatical_function", ""),
                }
                remaining = remaining[:-len(sfx)]
                chars_matched += len(sfx)
                break
        
        # 5. Match stem in remaining
        best_stem = None
        best_stem_len = 0
        for stem in self.stem_keys:
            if stem in remaining and len(stem) > best_stem_len:
                # Prefer stems that match from the beginning of remaining
                if remaining.startswith(stem) or remaining == stem:
                    entry = self.stems[stem]
                    best_stem = {
                        "form": stem,
                        "meaning_en": entry["meaning_en"],
                        "meaning_hr": entry.get("meaning_hr", ""),
                        "latin": entry.get("latin", ""),
                        "category": entry.get("category", ""),
                    }
                    best_stem_len = len(stem)
        
        # Also check non-prefix stem match
        if not best_stem:
            for stem in self.stem_keys:
                if stem in remaining and len(stem) > best_stem_len:
                    entry = self.stems[stem]
                    best_stem = {
                        "form": stem,
                        "meaning_en": entry["meaning_en"],
                        "meaning_hr": entry.get("meaning_hr", ""),
                        "latin": entry.get("latin", ""),
                        "category": entry.get("category", ""),
                    }
                    best_stem_len = len(stem)
        
        if best_stem:
            result["stem"] = best_stem
            # Calculate residue
            idx = remaining.find(best_stem["form"])
            before = remaining[:idx]
            after = remaining[idx + len(best_stem["form"]):]
            result["residue"] = (before + after).strip()
            chars_matched += best_stem_len
        else:
            result["residue"] = remaining
        
        if suffix_found:
            result["suffix"] = suffix_found
        
        # 6. Calculate confidence
        total_chars = len(word)
        if total_chars > 0:
            result["confidence"] = round(chars_matched / total_chars, 2)
        
        return result
    
    def gloss_word(self, decomposition):
        """Generate English gloss from decomposition"""
        if not decomposition:
            return "?"
        
        parts = []
        
        # Latin match takes priority
        if decomposition["latin_match"]:
            parts.append(decomposition["latin_match"]["meaning_en"].upper())
            if decomposition["residue"]:
                parts.append(f"+{decomposition['residue']}")
            return " ".join(parts)
        
        # Build from components
        if decomposition["operator"]:
            parts.append(decomposition["operator"]["meaning"])
        
        if decomposition["state"]:
            parts.append(f"({decomposition['state']['meaning']})")
        
        if decomposition["stem"]:
            stem_gloss = decomposition["stem"]["meaning_en"]
            if decomposition["stem"]["meaning_hr"]:
                # Use English primary
                pass
            parts.append(stem_gloss)
        
        if decomposition["suffix"]:
            sfx = decomposition["suffix"]
            parts.append(f"[{sfx['function'] or sfx['meaning']}]")
        
        if not parts:
            if decomposition["residue"]:
                return f"?{decomposition['residue']}?"
            return "?"
        
        gloss = " ".join(parts)
        
        # Add residue indicator
        if decomposition["residue"] and decomposition["confidence"] < 0.5:
            gloss += f" +?{decomposition['residue']}"
        
        return gloss
    
    def expand_word(self, cro_word, decomposition):
        """Generate expanded Croatian form"""
        if not decomposition:
            return cro_word
        
        parts = []
        
        if decomposition["latin_match"]:
            return f"{decomposition['latin_match']['latin_full'].upper()} [Lat.]"
        
        if decomposition["operator"]:
            op = decomposition["operator"]
            # Map operator to Croatian verb prefix
            op_map = {
                "measure/quantify": "ko-",
                "combine/cook": "kuhaj-",
                "soak/infuse": "namoci-",
                "dose/add/give": "daj-",
                "vessel/container": "posuda-",
                "with/together": "s-",
                "prepare (compound)": "pripremi-",
                "heat-treat (compound)": "zagrij-",
            }
            # Use first matching pattern
            for key_frag, cro_prefix in op_map.items():
                if key_frag in op["meaning"].lower():
                    parts.append(cro_prefix)
                    break
            else:
                parts.append(f"{op['form']}-")
        
        if decomposition["stem"]:
            stem = decomposition["stem"]
            if stem["meaning_hr"]:
                parts.append(stem["meaning_hr"])
            elif stem["latin"]:
                parts.append(stem["latin"])
            else:
                parts.append(stem["form"])
        else:
            parts.append(decomposition.get("residue", cro_word))
        
        if decomposition["suffix"]:
            parts.append(f"+{decomposition['suffix']['form']}")
        
        return "".join(parts)
    
    def decode_line(self, eva_line):
        """
        Decode a single line of EVA text into 4-layer interlinear.
        Returns: {
            "eva": str,
            "cro": str,
            "exp": str,
            "eng": str,
            "words": [decomposition dicts],
            "line_confidence": float,
        }
        """
        eva_words = eva_line.strip().split()
        if not eva_words:
            return None
        
        cro_words = []
        exp_words = []
        eng_words = []
        decompositions = []
        confidences = []
        
        for eva_word in eva_words:
            # Step 1: EVA -> Croatian transliteration
            cro = self.eva_to_croatian(eva_word)
            cro_words.append(cro)
            
            # Step 2: Decompose
            decomp = self.decompose_word(cro)
            decompositions.append(decomp)
            
            if decomp:
                # Step 3: Expand
                expanded = self.expand_word(cro, decomp)
                exp_words.append(expanded)
                
                # Step 4: English gloss
                eng = self.gloss_word(decomp)
                eng_words.append(eng)
                
                confidences.append(decomp["confidence"])
                
                # Update stats
                self.stats["total_words"] += 1
                if decomp["confidence"] >= 0.7:
                    self.stats["fully_resolved"] += 1
                elif decomp["confidence"] >= 0.3:
                    self.stats["partially_resolved"] += 1
                else:
                    self.stats["unknown"] += 1
                if decomp["latin_match"]:
                    self.stats["latin_detected"] += 1
            else:
                exp_words.append(cro)
                eng_words.append("?")
                confidences.append(0.0)
                self.stats["total_words"] += 1
                self.stats["unknown"] += 1
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            "eva": " ".join(eva_words),
            "cro": " ".join(cro_words),
            "exp": " ".join(exp_words),
            "eng": " ".join(eng_words),
            "words": decompositions,
            "line_confidence": round(avg_confidence, 2),
        }
    
    def clean_eva_token(self, token):
        """Clean a single EVA token by removing annotations and uncertainty markers"""
        # Remove inline annotations like <!@K>, <!@T>, <!@252>, <!@o'>
        token = re.sub(r'<[^>]*>', '', token)
        # Remove uncertainty markers
        token = token.replace('!', '').replace('?', '')
        # Remove trailing paragraph markers
        token = token.strip()
        return token
    
    def parse_eva_line(self, line):
        """Parse a line from IVTFF format EVA text.
        Words are separated by dots, with annotations inline."""
        # Remove paragraph end markers
        line = line.replace('<$>', '').strip()
        
        # Split on dots (word separator in IVTFF)
        raw_tokens = line.split('.')
        
        # Clean each token
        tokens = []
        for t in raw_tokens:
            cleaned = self.clean_eva_token(t)
            if cleaned and len(cleaned) > 0:
                tokens.append(cleaned)
        
        return tokens
    
    def is_eva_line(self, line):
        """Determine if a line contains actual EVA text vs headers/metadata"""
        line = line.strip()
        if not line:
            return False
        if line.startswith('==='):
            return False
        if line.startswith('[') and line.endswith(']'):
            return False
        if line.startswith('#'):
            return False
        # Must contain at least some alphabetic EVA characters
        alpha_count = sum(1 for c in line if c.isalpha())
        return alpha_count >= 2
    
    def decode_eva_tokens(self, eva_tokens):
        """Decode a list of EVA tokens into 4-layer interlinear"""
        if not eva_tokens:
            return None
        
        cro_words = []
        exp_words = []
        eng_words = []
        decompositions = []
        confidences = []
        
        for eva_word in eva_tokens:
            # Step 1: EVA -> Croatian transliteration
            cro = self.eva_to_croatian(eva_word)
            cro_words.append(cro)
            
            # Step 2: Decompose
            decomp = self.decompose_word(cro)
            decompositions.append(decomp)
            
            if decomp:
                # Step 3: Expand
                expanded = self.expand_word(cro, decomp)
                exp_words.append(expanded)
                
                # Step 4: English gloss
                eng = self.gloss_word(decomp)
                eng_words.append(eng)
                
                confidences.append(decomp["confidence"])
                
                # Update stats
                self.stats["total_words"] += 1
                if decomp["confidence"] >= 0.7:
                    self.stats["fully_resolved"] += 1
                elif decomp["confidence"] >= 0.3:
                    self.stats["partially_resolved"] += 1
                else:
                    self.stats["unknown"] += 1
                if decomp["latin_match"]:
                    self.stats["latin_detected"] += 1
            else:
                exp_words.append(cro)
                eng_words.append("?")
                confidences.append(0.0)
                self.stats["total_words"] += 1
                self.stats["unknown"] += 1
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            "eva": " ".join(eva_tokens),
            "cro": " ".join(cro_words),
            "exp": " ".join(exp_words),
            "eng": " ".join(eng_words),
            "words": decompositions,
            "line_confidence": round(avg_confidence, 2),
        }

    def decode_folio(self, eva_text, folio_id=None):
        """Decode an entire folio's EVA text (IVTFF format)"""
        lines = eva_text.strip().split("\n")
        
        decoded_lines = []
        for line in lines:
            if not self.is_eva_line(line):
                continue
            
            # Parse the IVTFF line into clean tokens
            tokens = self.parse_eva_line(line)
            if not tokens:
                continue
            
            result = self.decode_eva_tokens(tokens)
            if result:
                decoded_lines.append(result)
        
        # Calculate folio-level stats
        total_conf = [l["line_confidence"] for l in decoded_lines]
        avg_conf = sum(total_conf) / len(total_conf) if total_conf else 0.0
        
        return {
            "folio_id": folio_id,
            "lines": decoded_lines,
            "folio_confidence": round(avg_conf, 2),
            "stats": dict(self.stats),
        }
    
    def reset_stats(self):
        self.stats = {
            "total_words": 0,
            "fully_resolved": 0,
            "partially_resolved": 0,
            "unknown": 0,
            "latin_detected": 0,
        }


def test_decoder():
    """Quick test with real folio data"""
    decoder = ZFDDecoder()
    
    # Test with actual IVTFF formatted text from f88r
    test_eva = """=== Folio f88r ===

[Labels]
otorchety
oral
orald
oldar
otoky
otaly

[Text]
dorsheoy.ctheol.qockhey.dory.sheor.sholfchor.dal.chckhod
sal.sheom.kol.chear.shekor.qokor.daiin.sar.raiin.oky.sam
"""
    
    print("=" * 70)
    print("ZFD DECODER v2.0 TEST (IVTFF format)")
    print("=" * 70)
    
    decoded = decoder.decode_folio(test_eva, folio_id="f88r_test")
    
    for line in decoded["lines"]:
        print(f"\nEVA: {line['eva']}")
        print(f"CRO: {line['cro']}")
        print(f"EXP: {line['exp']}")
        print(f"ENG: {line['eng']}")
        print(f"     [confidence: {line['line_confidence']:.0%}]")
    
    print(f"\n{'=' * 70}")
    print(f"Folio confidence: {decoded['folio_confidence']:.0%}")
    print(f"STATS: {decoded['stats']}")
    
    # Test with f1r first line
    print(f"\n{'=' * 70}")
    print("F1R FIRST LINE TEST")
    print(f"{'=' * 70}")
    decoder.reset_stats()
    test_f1r = "fachys.ykal.ar.ataiin.shol.shory.cth!res.y.kor.sholdy!"
    tokens = decoder.parse_eva_line(test_f1r)
    result = decoder.decode_eva_tokens(tokens)
    if result:
        print(f"\nEVA: {result['eva']}")
        print(f"CRO: {result['cro']}")
        print(f"EXP: {result['exp']}")
        print(f"ENG: {result['eng']}")
        print(f"     [confidence: {result['line_confidence']:.0%}]")


if __name__ == "__main__":
    test_decoder()
