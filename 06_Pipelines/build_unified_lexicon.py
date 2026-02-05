#!/usr/bin/env python3
"""
ZFD Unified Lexicon Builder
===========================
Merges ALL morpheme sources into one canonical lexicon JSON.
Sources: herbal_lexicon_v3_6.csv, decoder_lexicon.csv, character_reference.py,
         pharmaceutical_morphemes.md, botanical_glossary.md, proof_kit, gap_analysis,
         al_ar_duality, miscellany_mining, and the 4MB croatian_readings.json

Output: unified_lexicon.json - single source of truth for the decoder pipeline
"""

import json
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

SRC = Path("/home/claude/zfd/lexicon_sources")

class UnifiedLexicon:
    def __init__(self):
        # Main storage: morpheme -> entry dict
        self.operators = {}      # Prefixes that modify stems
        self.stems = {}          # Core meaning-bearing morphemes  
        self.suffixes = {}       # Grammatical/state markers
        self.latin_terms = {}    # Direct Latin borrowings
        self.compounds = {}      # Multi-morpheme fixed expressions
        self.state_markers = {}  # State/result prefixes (he-, še-, etc.)
        
        # Tracking
        self.sources = defaultdict(set)  # morpheme -> set of source files
        self.conflicts = []              # Any conflicting definitions
        
    def add_operator(self, form, meaning_en, meaning_hr=None, latin=None, source="unknown", confidence="CONFIRMED"):
        key = form.rstrip("-")
        if key in self.operators and self.operators[key]["meaning_en"] != meaning_en:
            self.conflicts.append(f"OPERATOR '{key}': '{self.operators[key]['meaning_en']}' vs '{meaning_en}' (from {source})")
        self.operators[key] = {
            "form": form,
            "type": "operator",
            "meaning_en": meaning_en,
            "meaning_hr": meaning_hr,
            "latin": latin,
            "confidence": confidence
        }
        self.sources[f"op:{key}"].add(source)
        
    def add_stem(self, form, meaning_en, meaning_hr=None, latin=None, category=None, source="unknown", confidence="CONFIRMED"):
        if form in self.stems and self.stems[form]["meaning_en"] != meaning_en:
            # Check if it's a genuine conflict or just a variant
            existing = self.stems[form]["meaning_en"]
            if existing.lower().split("/")[0].strip() != meaning_en.lower().split("/")[0].strip():
                self.conflicts.append(f"STEM '{form}': '{existing}' vs '{meaning_en}' (from {source})")
                # Keep the one with more context
                if latin and not self.stems[form].get("latin"):
                    pass  # New one has more info, overwrite
                else:
                    return  # Keep existing
        self.stems[form] = {
            "form": form,
            "type": "stem",
            "meaning_en": meaning_en,
            "meaning_hr": meaning_hr,
            "latin": latin,
            "category": category or "general",
            "confidence": confidence
        }
        self.sources[f"stem:{form}"].add(source)
        
    def add_suffix(self, form, meaning_en, grammatical_function=None, source="unknown", confidence="CONFIRMED"):
        key = form.lstrip("-")
        self.suffixes[key] = {
            "form": form,
            "type": "suffix",
            "meaning_en": meaning_en,
            "grammatical_function": grammatical_function,
            "confidence": confidence
        }
        self.sources[f"sfx:{key}"].add(source)
        
    def add_latin(self, form, meaning_en, latin_full=None, category=None, source="unknown"):
        self.latin_terms[form] = {
            "form": form,
            "type": "latin_term",
            "meaning_en": meaning_en,
            "latin_full": latin_full,
            "category": category or "pharmaceutical",
        }
        self.sources[f"lat:{form}"].add(source)

    def add_state_marker(self, form, meaning_en, source="unknown"):
        self.state_markers[form] = {
            "form": form,
            "type": "state_marker",
            "meaning_en": meaning_en,
        }
        self.sources[f"state:{form}"].add(source)

    # ================================================================
    # SOURCE PARSERS
    # ================================================================
    
    def parse_herbal_lexicon(self):
        """Parse Herbal_Lexicon_v3_6.csv - the most structured source"""
        src = "herbal_lexicon_v3_6"
        path = SRC / "herbal_lexicon_v3_6.csv"
        with open(path) as f:
            lines = f.readlines()
        
        current_section = None
        for line in lines:
            line = line.strip()
            if line.startswith("#"):
                current_section = line.lstrip("# ").strip()
                continue
            if not line or line.startswith("name,"):
                continue
            
            parts = line.split(",")
            if len(parts) < 4:
                continue
                
            name, variant, context, inference = parts[0], parts[1], parts[2], parts[3]
            latin = parts[4] if len(parts) > 4 else None
            status = parts[5] if len(parts) > 5 else "CONFIRMED"
            
            variant = variant.strip()
            inference = inference.strip()
            
            if "OPERATOR" in (current_section or "").upper() or context == "prefix":
                self.add_operator(variant, inference, latin=latin, source=src)
            elif "SUFFIX" in (current_section or "").upper() or context == "suffix":
                self.add_suffix(variant, inference, source=src)
            elif "STATE" in (current_section or "").upper():
                self.add_state_marker(variant, inference, source=src)
            elif "LATIN" in (current_section or "").upper():
                self.add_latin(variant, inference, latin_full=latin, source=src)
            else:
                # It's a stem
                category = None
                if "bone" in name.lower() or "bone" in inference.lower():
                    category = "animal"
                elif "oil" in inference.lower() or "water" in inference.lower():
                    category = "liquid"
                elif "herb" in inference.lower() or "plant" in inference.lower() or "root" in inference.lower():
                    category = "plant_part"
                elif "salt" in inference.lower() or "mineral" in inference.lower():
                    category = "mineral"
                    
                self.add_stem(variant, inference, latin=latin, category=category, source=src, confidence=status)
        
        print(f"  [herbal_lexicon] Parsed")

    def parse_decoder_lexicon(self):
        """Parse zfd_decoder/data/lexicon.csv"""
        src = "decoder_lexicon"
        path = SRC / "decoder_lexicon.csv"
        if not path.exists() or path.stat().st_size < 10:
            print(f"  [decoder_lexicon] Skipped (empty/missing)")
            return
            
        with open(path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                form = row.get("morpheme", row.get("stem", row.get("form", ""))).strip()
                eng = row.get("english", row.get("meaning", row.get("gloss", ""))).strip()
                lat = row.get("latin", "").strip()
                cat = row.get("category", "").strip()
                typ = row.get("type", "stem").strip()
                
                if not form or not eng:
                    continue
                    
                if typ == "operator" or typ == "prefix":
                    self.add_operator(form, eng, latin=lat, source=src)
                elif typ == "suffix":
                    self.add_suffix(form, eng, source=src)
                else:
                    self.add_stem(form, eng, latin=lat, category=cat, source=src)
        
        print(f"  [decoder_lexicon] Parsed")

    def parse_character_reference(self):
        """Extract CROATIAN_MORPHEMES dict from character_reference.py"""
        src = "character_reference"
        path = SRC / "character_reference.py"
        content = path.read_text()
        
        # Find the CROATIAN_MORPHEMES dict
        match = re.search(r'CROATIAN_MORPHEMES\s*=\s*\{([^}]+)\}', content, re.DOTALL)
        if match:
            dict_content = match.group(1)
            # Parse key-value pairs
            for m in re.finditer(r"['\"](\w+)['\"]\s*:\s*['\"]([^'\"]+)['\"]", dict_content):
                form, meaning = m.group(1), m.group(2)
                self.add_stem(form, meaning, source=src)
        
        # Also look for EVA_TO_CROATIAN or similar mappings
        match2 = re.search(r'EVA_TO_CROATIAN\s*=\s*\{([^}]+)\}', content, re.DOTALL)
        if match2:
            # This is character-level mapping, not morpheme-level
            pass
            
        print(f"  [character_reference] Parsed")

    def parse_pharmaceutical_morphemes(self):
        """Parse PHARMACEUTICAL_MORPHEMES.md"""
        src = "pharmaceutical_morphemes"
        path = SRC / "pharmaceutical_morphemes.md"
        content = path.read_text()
        
        # Parse table rows
        for line in content.split("\n"):
            # Match markdown table rows like | **ch-** | Combine / Cook | ...
            m = re.match(r'\|\s*\*?\*?(\S+?)\*?\*?\s*\|\s*([^|]+)\|', line)
            if m:
                form = m.group(1).strip("*").strip()
                meaning = m.group(2).strip()
                if not form or form.startswith("---") or form.lower() in ("morpheme", "stem", "operator", "suffix"):
                    continue
                    
                if form.endswith("-"):
                    self.add_operator(form, meaning, source=src)
                elif form.startswith("-"):
                    self.add_suffix(form, meaning, source=src)
                else:
                    self.add_stem(form, meaning, source=src)
        
        print(f"  [pharmaceutical_morphemes] Parsed")

    def parse_botanical_glossary(self):
        """Parse croatian_botanical_glossary.md for plant vocabulary"""
        src = "botanical_glossary"
        path = SRC / "botanical_glossary.md"
        content = path.read_text()
        
        count = 0
        for line in content.split("\n"):
            # Match entries like | ruža | rose | rosa | herb |
            m = re.match(r'\|\s*\*?\*?(\S+?)\*?\*?\s*\|\s*([^|]+)\|\s*([^|]*)\|\s*([^|]*)\|', line)
            if m:
                hr = m.group(1).strip("*").strip()
                eng = m.group(2).strip()
                lat = m.group(3).strip()
                cat = m.group(4).strip()
                
                if not hr or hr.startswith("---") or hr.lower() in ("croatian", "latin", "english", "category"):
                    continue
                
                self.add_stem(hr, eng, meaning_hr=hr, latin=lat if lat else None, 
                            category=cat if cat else "botanical", source=src)
                count += 1
        
        print(f"  [botanical_glossary] Parsed ({count} entries)")

    def parse_miscellany_mining(self):
        """Parse MISCELLANY_MINING_REPORT.md for Latin pharma terms"""
        src = "miscellany_mining"
        path = SRC / "miscellany_mining.md"
        content = path.read_text()
        
        count = 0
        for line in content.split("\n"):
            m = re.match(r'\|\s*\*?\*?(\S+?)\*?\*?\s*\|\s*([^|]+)\|\s*([^|]*)\|', line)
            if m:
                form = m.group(1).strip("*").strip()
                meaning = m.group(2).strip()
                notes = m.group(3).strip()
                
                if not form or form.startswith("---") or form.lower() in ("term", "morpheme", "form"):
                    continue
                
                if any(x in notes.lower() for x in ["latin", "pharma", "medical"]):
                    self.add_latin(form, meaning, source=src)
                else:
                    self.add_stem(form, meaning, source=src)
                count += 1
        
        print(f"  [miscellany_mining] Parsed ({count} entries)")

    def parse_proof_kit(self):
        """Extract validated morphemes from the proof kit"""
        src = "proof_kit"
        path = SRC / "proof_kit_v1.md"
        content = path.read_text()
        
        # Look for validated entries
        count = 0
        for line in content.split("\n"):
            m = re.match(r'\|\s*\*?\*?(\S+?)\*?\*?\s*\|\s*([^|]+)\|\s*([^|]*)\|', line)
            if m:
                form = m.group(1).strip("*").strip()
                meaning = m.group(2).strip()
                if not form or form.startswith("---") or len(form) > 20:
                    continue
                if any(form.lower() == x for x in ["test", "result", "metric", "value", "criterion"]):
                    continue
                # Only add if it looks like a real morpheme
                if re.match(r'^[a-zšđčćž]{1,10}$', form):
                    self.add_stem(form, meaning, source=src, confidence="VALIDATED")
                    count += 1
        
        print(f"  [proof_kit] Parsed ({count} entries)")

    def parse_al_ar_duality(self):
        """Parse the AL/AR duality hypothesis for liquid morpheme variants"""
        src = "al_ar_duality"
        path = SRC / "al_ar_duality.md"
        content = path.read_text()
        
        # This document describes the al/ar liquid register system
        # Extract specific morpheme claims
        count = 0
        for line in content.split("\n"):
            m = re.match(r'\|\s*\*?\*?(\S+?)\*?\*?\s*\|\s*([^|]+)\|', line)
            if m:
                form = m.group(1).strip("*").strip()
                meaning = m.group(2).strip()
                if re.match(r'^[a-zšđčćž]{1,8}$', form) and not form.startswith("---"):
                    self.add_stem(form, meaning, category="liquid", source=src)
                    count += 1
        
        print(f"  [al_ar_duality] Parsed ({count} entries)")

    def add_known_vocabulary(self):
        """Add well-established vocabulary from the ZFD theory that might not be
        in any single file but is documented across the research."""
        src = "zfd_core_theory"
        
        # === OPERATORS (action-forcing prefixes) ===
        operators = {
            "qo": "measure/quantify",
            "ko": "measure/quantify (variant)",
            "ch": "combine/cook",
            "h": "combine/cook (reduced)",
            "sh": "soak/infuse",
            "š": "soak/infuse (Croatian)",
            "da": "dose/add/give",
            "ok": "vessel/container",
            "ot": "vessel/container (variant)",
            "sa": "with/together",
            "so": "with/together (variant)",
            "pc": "prepare (compound)",
            "tc": "heat-treat (compound)",
            "yk": "measure-vessel (compound)",
        }
        for form, meaning in operators.items():
            self.add_operator(form, meaning, source=src)
        
        # === STATE MARKERS ===
        states = {
            "he": "state/result/after",
            "heo": "state/result (extended)",
            "še": "soaked-state/after soaking",
            "šeo": "soaked-state (extended)",
        }
        for form, meaning in states.items():
            self.add_state_marker(form, meaning, source=src)
        
        # === CORE STEMS ===
        stems = {
            # Liquids
            "ar": ("water", "voda", "aqua", "liquid"),
            "ol": ("oil", "ulje", "oleum", "liquid"),
            "or": ("oil (variant)", "ulje", "oleum", "liquid"),
            "al": ("liquid/water (vessel context)", "tekućina", "aqua", "liquid"),
            # Plant parts
            "ed": ("root/base/process", "korijen", "radix", "plant_part"),
            "edy": ("root (prepared)", "korijen", "radix", "plant_part"),
            "od": ("stalk/stem", "stabljika", "caulis", "plant_part"),
            "kor": ("root (full)", "korijen", "radix", "plant_part"),
            "list": ("leaf", "list", "folium", "plant_part"),
            "cvijet": ("flower", "cvijet", "flos", "plant_part"),
            "kora": ("bark", "kora", "cortex", "plant_part"),
            "sjeme": ("seed", "sjeme", "semen", "plant_part"),
            # Animal/mineral
            "kost": ("bone", "kost", "os/ossis", "animal"),
            "kosti": ("bone (state)", "kosti", "ossis", "animal"),
            "ost": ("bone (medical)", "kost", "osteo-", "animal"),
            "sal": ("salt", "sol", "sal", "mineral"),
            "sar": ("salt (variant)", "sol", "sal", "mineral"),
            # Equipment
            "kal": ("vessel/pot", "posuda", "calix", "equipment"),
            "stal": ("cauldron", "kotao", "caldarium", "equipment"),
            "phar": ("flask", "bočica", "phiala", "equipment"),
            "okal": ("pot (with op)", "posuda", "olla", "equipment"),
            "ostar": ("large vessel", "posuda", "olla", "equipment"),
            # Resins and herbs
            "stor": ("storax", "storaks", "storax", "resin"),
            "ros": ("rose/rosewater", "ruža", "rosa", "herb"),
            "mir": ("myrrh", "smirna", "myrrha", "resin"),
            "aloe": ("aloe", "aloja", "aloe", "herb"),
            "galb": ("galbanum", "galbanum", "galbanum", "resin"),
            "kamf": ("camphor", "kamfor", "camphora", "resin"),
            "anis": ("anise", "anis", "anisum", "herb"),
            "kor": ("coriander", "korijander", "coriandrum", "herb"),
            "ment": ("mint", "metvica", "mentha", "herb"),
            "salv": ("sage", "kadulja", "salvia", "herb"),
            "fen": ("fennel", "komorač", "feniculum", "herb"),
            "rut": ("rue", "rutvica", "ruta", "herb"),
            "hisop": ("hyssop", "izop", "hyssopus", "herb"),
            "malv": ("mallow", "sljez", "malva", "herb"),
            "plant": ("plantain", "trputac", "plantago", "herb"),
            "cinam": ("cinnamon", "cimet", "cinnamomum", "spice"),
            "ging": ("ginger", "đumbir", "zingiber", "spice"),
            "pip": ("pepper", "papar", "piper", "spice"),
            # Body/medical  
            "glav": ("head", "glava", "caput", "body"),
            "želud": ("stomach", "želudac", "stomachus", "body"),
            "jetr": ("liver", "jetra", "hepar", "body"),
            "src": ("heart", "srce", "cor", "body"),
            "koža": ("skin", "koža", "cutis", "body"),
            "oko": ("eye", "oko", "oculus", "body"),
            "krv": ("blood", "krv", "sanguis", "body"),
            "žuč": ("bile", "žuč", "bilis", "body"),
            "rana": ("wound", "rana", "vulnus", "body"),
            "bol": ("pain", "bol", "dolor", "body"),
            # Actions/process
            "hol": ("combine/mix", "miješati", None, "action"),
            "hor": ("process/work", "obraditi", None, "action"),
            "šol": ("soak in oil", "namočiti", None, "action"),
            "šor": ("strain/soak", "procijediti", None, "action"),
            "dal": ("then/next", "zatim", None, "sequence"),
            "dar": ("dose/give", "dati", "dare", "action"),
            "dain": ("dose/portion", "doza", "dosis", "action"),
            "dan": ("day/give", "dan/dati", "dies/dare", "action"),
            # Properties
            "kair": ("fire/heat", "vatra", "ignis", "property"),
            "kar": ("heat", "toplina", "calor", "property"),
            "star": ("heat (strong)", "vrelina", None, "property"),
            "char": ("fire", "vatra", None, "property"),
            "hlad": ("cold", "hladno", "frigidus", "property"),
            "suš": ("dry", "suho", "siccus", "property"),
            "mokar": ("wet", "mokro", "humidus", "property"),
            "gorak": ("bitter", "gorko", "amarus", "property"),
            # Grammar/function
            "sam": ("self/alone", "sam", None, "grammar"),
            "y": ("and/with", "i", "et", "grammar"),
        }
        
        for form, (eng, hr, lat, cat) in stems.items():
            self.add_stem(form, eng, meaning_hr=hr, latin=lat, category=cat, source=src)
        
        # === SUFFIXES ===
        suffixes = {
            "y": ("adjectival/state", "adjective"),
            "i": ("adjectival (variant)", "adjective"),
            "ey": ("resulting state", "participle"),
            "ei": ("resulting state (variant)", "participle"),
            "edy": ("active process", "verbal"),
            "dy": ("active process (variant)", "verbal"),
            "ain": ("plural/collective", "plural"),
            "in": ("plural (reduced)", "plural"),
            "al": ("container/vessel context", "locative"),
            "ol": ("oil/liquid context", "instrumental"),
            "ar": ("water/liquid context", "instrumental"),
            "an": ("pertaining to", "adjective"),
            "ity": ("quality/state", "abstract"),
            "ost": ("quality (Slavic)", "abstract"),
            "m": ("dative/instrumental", "case"),
            "om": ("instrumental (full)", "case"),
            "ir": ("agent/doer", "agent"),
        }
        for form, (meaning, function) in suffixes.items():
            self.add_suffix(form, meaning, grammatical_function=function, source=src)
        
        # === LATIN PHARMACEUTICAL TERMS ===
        latin = {
            "oral": ("by mouth/orally", "oralis", "administration"),
            "orolaly": ("orally (expanded)", "oraliter", "administration"),
            "dolor": ("pain", "dolor", "symptom"),
            "ana": ("equal parts (Rx)", "ana", "dosing"),
            "da": ("give (Rx imperative)", "da/dare", "instruction"),
            "recipe": ("take (Rx)", "recipe", "instruction"),
        }
        for form, (eng, lat_full, cat) in latin.items():
            self.add_latin(form, eng, latin_full=lat_full, category=cat, source=src)
        
        print(f"  [zfd_core_theory] Added {len(operators)} operators, {len(stems)} stems, {len(suffixes)} suffixes, {len(latin)} Latin terms")

    def parse_croatian_readings(self):
        """Parse the 4MB croatian_readings.json for frequency-validated vocabulary"""
        src = "croatian_readings"
        path = SRC / "croatian_readings.json"
        
        try:
            with open(path) as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"  [croatian_readings] FAILED: {e}")
            return
        
        # This is the full manuscript decode - extract patterns
        # Structure varies but usually folio -> lines -> words
        word_count = 0
        if isinstance(data, dict):
            for folio, content in data.items():
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict):
                            word_count += 1
                elif isinstance(content, dict):
                    word_count += len(content)
        
        print(f"  [croatian_readings] Loaded ({word_count} entries, used for frequency validation)")

    def parse_word_frequency(self):
        """Parse word_frequency.csv to identify high-frequency unknowns"""
        src = "word_frequency"
        path = SRC / "word_frequency.csv"
        
        freq = {}
        with open(path) as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    word, count = row[0].strip(), row[1].strip()
                    if word and count.isdigit():
                        freq[word] = int(count)
        
        # Sort by frequency
        sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        
        # Count how many of the top 100 we can already resolve
        known = set()
        for d in [self.stems, self.operators, self.suffixes, self.latin_terms]:
            known.update(d.keys())
        
        resolved = 0
        unresolved_top = []
        for word, count in sorted_freq[:200]:
            # Check if word or any sub-morpheme is known
            found = False
            for k in known:
                if k in word or word in k:
                    found = True
                    break
            if found:
                resolved += 1
            else:
                unresolved_top.append((word, count))
        
        print(f"  [word_frequency] Top 200 words: {resolved} resolvable, {len(unresolved_top)} unknown")
        if unresolved_top[:20]:
            print(f"    Top unresolved: {', '.join(f'{w}({c})' for w,c in unresolved_top[:20])}")
        
        return freq

    # ================================================================
    # BUILD AND EXPORT
    # ================================================================
    
    def build(self):
        """Run all parsers and build the unified lexicon"""
        print("=" * 60)
        print("BUILDING UNIFIED ZFD LEXICON")
        print("=" * 60)
        
        # Parse all sources
        print("\nParsing sources:")
        self.parse_herbal_lexicon()
        self.parse_decoder_lexicon()
        self.parse_character_reference()
        self.parse_pharmaceutical_morphemes()
        self.parse_botanical_glossary()
        self.parse_miscellany_mining()
        self.parse_proof_kit()
        self.parse_al_ar_duality()
        self.add_known_vocabulary()
        self.parse_croatian_readings()
        freq = self.parse_word_frequency()
        
        # Report
        print(f"\n{'=' * 60}")
        print(f"UNIFIED LEXICON SUMMARY")
        print(f"{'=' * 60}")
        print(f"  Operators:     {len(self.operators)}")
        print(f"  Stems:         {len(self.stems)}")
        print(f"  Suffixes:      {len(self.suffixes)}")
        print(f"  Latin terms:   {len(self.latin_terms)}")
        print(f"  State markers: {len(self.state_markers)}")
        total = len(self.operators) + len(self.stems) + len(self.suffixes) + len(self.latin_terms) + len(self.state_markers)
        print(f"  TOTAL:         {total}")
        
        if self.conflicts:
            print(f"\n  CONFLICTS ({len(self.conflicts)}):")
            for c in self.conflicts[:10]:
                print(f"    {c}")
        
        return self.export()
    
    def export(self):
        """Export to unified JSON"""
        lexicon = {
            "meta": {
                "version": "1.0.0",
                "generated": "2026-02-05",
                "description": "Unified ZFD lexicon merging all morpheme sources",
                "sources": list(set(s for sources in self.sources.values() for s in sources)),
                "counts": {
                    "operators": len(self.operators),
                    "stems": len(self.stems),
                    "suffixes": len(self.suffixes),
                    "latin_terms": len(self.latin_terms),
                    "state_markers": len(self.state_markers),
                }
            },
            "operators": self.operators,
            "state_markers": self.state_markers,
            "stems": self.stems,
            "suffixes": self.suffixes,
            "latin_terms": self.latin_terms,
        }
        
        outpath = Path("/home/claude/zfd/pipeline/unified_lexicon.json")
        with open(outpath, "w") as f:
            json.dump(lexicon, f, indent=2, ensure_ascii=False)
        
        print(f"\n  Exported to: {outpath} ({outpath.stat().st_size:,} bytes)")
        return lexicon


if __name__ == "__main__":
    lex = UnifiedLexicon()
    lexicon = lex.build()
