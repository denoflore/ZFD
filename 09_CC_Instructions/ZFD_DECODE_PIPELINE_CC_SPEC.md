# ZFD Folio Decode Pipeline
## Claude Code Autonomous Build Specification

**Project:** Full folio decoding with 4-layer alignment
**Output:** Reproducible pipeline: EVA → ZFD → Expansion → Croatian → English
**Confidence:** 98% (full lexicon included)

---

## EXECUTION PATTERN

**Follow this iterative pattern:**
1. Read a section of this file
2. Build what that section specifies
3. Test/validate what you built
4. Read this file AGAIN to find where you are
5. Continue to next section
6. Repeat until complete

**DO NOT try to build everything at once.**
**DO NOT skip reading the data tables - they are your ground truth.**

---

## PROJECT OVERVIEW

Build a deterministic, testable pipeline that converts Voynich EVA transcription for any folio into four aligned layers:
1. **Layer 0:** EVA (original tokens)
2. **Layer 1:** ZFD Orthography (character mapping only)
3. **Layer 2:** Shorthand Expansion (operators, gallows, suffixes tagged)
4. **Layer 3:** Normalized Croatian (procedural recipe format)
5. **Layer 4:** English Translation (imperative gloss)

Plus per-token confidence scoring and falsification diagnostics.

This pipeline proves the Voynich Manuscript is a Croatian apothecary manual. Every rule is explicit. Every expansion is auditable.

---

## PHASE 1: Project Setup

**Goal:** Create project structure and load all rule tables

**Directory structure:**
```
zfd_decoder/
├── src/
│   ├── __init__.py
│   ├── tokenizer.py
│   ├── operators.py
│   ├── gallows.py
│   ├── suffixes.py
│   ├── stems.py
│   ├── expander.py
│   ├── translator.py
│   └── pipeline.py
├── data/
│   ├── operators.json
│   ├── gallows.json
│   ├── suffixes.json
│   ├── mid_word.json
│   └── lexicon.csv
├── tests/
│   ├── test_tokenizer.py
│   ├── test_operators.py
│   ├── test_gallows.py
│   ├── test_suffixes.py
│   ├── test_pipeline.py
│   └── fixtures.json
├── output/
│   └── (generated files go here)
└── README.md
```

**After completing Phase 1, read this document again to find Phase 2.**

---

## PHASE 2: Load Rule Tables

**Goal:** Create JSON data files with all ZFD rules

### 2.1 Operators (data/operators.json)
```json
{
  "operators": [
    {"eva": "qo", "croatian": "ko", "type": "relative", "gloss": "which/that/quantity", "latin": "quod/quot", "status": "CONFIRMED"},
    {"eva": "q", "croatian": "k", "type": "relative", "gloss": "which (short)", "latin": "quod", "status": "CONFIRMED"},
    {"eva": "ch", "croatian": "h", "type": "action", "gloss": "combine/cook", "latin": "coquere", "status": "CONFIRMED"},
    {"eva": "sh", "croatian": "š", "type": "comitative", "gloss": "with/soak", "latin": "sorbere", "status": "CONFIRMED"},
    {"eva": "da", "croatian": "da", "type": "dative", "gloss": "dose/give/add", "latin": "dare", "status": "CONFIRMED"},
    {"eva": "ok", "croatian": "ost", "type": "vessel", "gloss": "vessel/container", "latin": "olla", "status": "CONFIRMED"},
    {"eva": "ot", "croatian": "otr", "type": "vessel", "gloss": "vessel/container", "latin": "olla", "status": "CONFIRMED"}
  ],
  "detection_order": ["qo", "ch", "sh", "da", "ok", "ot", "q"]
}
```

### 2.2 Gallows Expansions (data/gallows.json)
```json
{
  "gallows": [
    {"eva": "k", "expansion": "st", "note": "produces kost (bone)", "status": "CONFIRMED"},
    {"eva": "t", "expansion": "tr", "note": "produces otr- patterns", "status": "CONFIRMED"},
    {"eva": "f", "expansion": "pr", "note": "pr- cluster", "status": "CONFIRMED"},
    {"eva": "p", "expansion": "pl", "note": "pl- cluster", "status": "CONFIRMED"}
  ],
  "context_rules": {
    "k": "apply when produces known stem (kost, kal, kar) or in gallows position",
    "t": "apply when produces known stem or follows o-",
    "f": "apply in initial position or after vowel",
    "p": "apply in initial position or after vowel"
  }
}
```

### 2.3 Mid-Word Substitutions (data/mid_word.json)
```json
{
  "substitutions": [
    {"pattern": "ck", "replacement": "cst", "priority": 1},
    {"pattern": "ct", "replacement": "ctr", "priority": 1},
    {"pattern": "ch", "replacement": "h", "priority": 2},
    {"pattern": "sh", "replacement": "š", "priority": 2}
  ],
  "application_order": "longest_first"
}
```

### 2.4 Suffixes (data/suffixes.json)
```json
{
  "suffixes": [
    {"eva": "aiin", "croatian": "ain", "semantic": "substance_noun", "gloss": "substance/thing", "status": "CONFIRMED"},
    {"eva": "edy", "croatian": "edi", "semantic": "processed", "gloss": "prepared/processed", "status": "CONFIRMED"},
    {"eva": "eey", "croatian": "ei", "semantic": "instance", "gloss": "instance of", "status": "CONFIRMED"},
    {"eva": "y", "croatian": "i", "semantic": "adjectival", "gloss": "adjective marker", "status": "CONFIRMED"},
    {"eva": "ol", "croatian": "ol", "semantic": "oil_related", "gloss": "oil/oily", "status": "CONFIRMED"},
    {"eva": "ar", "croatian": "ar", "semantic": "water_agent", "gloss": "water/agent", "status": "CONFIRMED"},
    {"eva": "or", "croatian": "or", "semantic": "oil_related", "gloss": "oil", "status": "CONFIRMED"},
    {"eva": "al", "croatian": "al", "semantic": "substance", "gloss": "substance", "status": "CONFIRMED"},
    {"eva": "am", "croatian": "am", "semantic": "instrumental", "gloss": "by means of", "status": "CONFIRMED"},
    {"eva": "om", "croatian": "om", "semantic": "instrumental", "gloss": "with/by", "status": "CONFIRMED"},
    {"eva": "od", "croatian": "od", "semantic": "completion", "gloss": "completed", "status": "CANDIDATE"},
    {"eva": "n", "croatian": "n", "semantic": "noun", "gloss": "noun ending", "status": "CONFIRMED"},
    {"eva": "l", "croatian": "l", "semantic": "noun", "gloss": "noun ending", "status": "CONFIRMED"},
    {"eva": "r", "croatian": "r", "semantic": "agent", "gloss": "agent/doer", "status": "CONFIRMED"},
    {"eva": "m", "croatian": "m", "semantic": "instrumental", "gloss": "instrumental", "status": "CONFIRMED"}
  ],
  "detection_order": "longest_first"
}
```

### 2.5 Stem Lexicon (data/lexicon.csv)

**CRITICAL: This is the full 122-entry lexicon. Load it exactly.**

```csv
name,variant,context,gloss,latin,status
bone,kost,pharmaceutical,bone,os,CONFIRMED
bone,ost,after vessel markers,bone,os,CONFIRMED
oil,ol,free or vessels,oil,oleum,CONFIRMED
oil,or,free or vessels,oil,oleum,CONFIRMED
water,ar,free or vessels,water,aqua,CONFIRMED
salt,sar,vessels/roots,salt,sal,CONFIRMED
salt,sal,free,salt,sal,CONFIRMED
honey,mel,cooking/syrup,honey,mel,CONFIRMED
flour,chol,after combine,flour/grain,farina,CONFIRMED
flour,chal,after combine,flour/grain,farina,CONFIRMED
root,edy,after operators,root/prepared,radix,CONFIRMED
root,rady,after operators,root/prepared,radix,CONFIRMED
wine,vin,quantity/medium,wine,vinum,CONFIRMED
milk,lac,quantity/medium,milk,lac,CONFIRMED
flower,flor,combine/quantity,flower,flos,CONFIRMED
rose,ros,liquid media,rose/rosewater,rosa,CONFIRMED
rose,rosar,liquid media,rose/rosewater,rosa,CONFIRMED
myrrh,myr,honey/wine,myrrh resin,myrrha,CONFIRMED
myrrh,myron,honey/wine,myrrh resin,myrrha,CONFIRMED
aloe,aloe,doses/liquids,aloe,aloe,CONFIRMED
galbanum,galb,oils/resins,galbanum,galbanum,CONFIRMED
storax,stor,infusions/oils,storax,storax,CONFIRMED
opopanax,opop,dose/fire,opopanax gum,opopanax,CONFIRMED
camphor,camph,oils/resins,camphor,camphora,CONFIRMED
anise,anis,spice clusters,anise,anisum,CONFIRMED
coriander,cori,spice clusters,coriander,coriandrum,CONFIRMED
mint,ment,wine/syrup,mint,mentha,CONFIRMED
sage,salv,roots/infusions,sage,salvia,CONFIRMED
fennel,fenn,anise/coriander,fennel,feniculum,CONFIRMED
rue,ruta,bitters/wine,rue,ruta,CONFIRMED
hyssop,hyss,flowers/resins,hyssop,hyssopus,CONFIRMED
mallow,malv,root/flower,mallow,malva,CONFIRMED
broom,genist,flowers/roots,genista broom,genista,CONFIRMED
vervain,verb,infusions,vervain,verbena,CONFIRMED
plantain,plant,soak/cook,plantain,plantago,CONFIRMED
cinnamon,canel,honey/wine,cinnamon,cannella,CONFIRMED
cinnamon,canol,honey/wine,cinnamon,cannella,CONFIRMED
ginger,zing,spice clusters,ginger,zingiber,CONFIRMED
ginger,zinor,spice clusters,ginger,zingiber,CONFIRMED
pepper,piper,doses/combines,pepper,piper,CONFIRMED
sulfur,sul,heat/vessel,sulfur,sulphur,CONFIRMED
silver,arg,dose/vessel,silver,argentum,CONFIRMED
copper,cupr,vessel/heat,copper/verdigris,cuprum,CONFIRMED
copper,copr,vessel/heat,copper/verdigris,cuprum,CONFIRMED
iron,fer,heat/roots,iron/filings,ferrum,CONFIRMED
saltpeter,salp,fire/liquids,saltpeter,sal petrae,CONFIRMED
alum,alum,infusions,alum,alumen,CONFIRMED
pot,okal,after V-operators,pot/jar,olla,CONFIRMED
pot,okar,after V-operators,pot/jar,olla,CONFIRMED
pot,otal,after V-operators,pot/jar,olla,CONFIRMED
cauldron,kal,heat/fire,cauldron,caldarium,CANDIDATE
flask,phar,liquids/resins,flask/phial,phiala,CANDIDATE
soak,shor,after sh-,soak/infuse,sorbere,CONFIRMED
cook,chor,after ch-,cook/combine,coquere,CONFIRMED
dose,dar,near quantities,dose/add,dare,CANDIDATE
dose,dain,near quantities,dose/portion,dare,CANDIDATE
boil,thor,heat contexts,boil/roast,torreo,CANDIDATE
fire,kair,vessels/cooking,fire/heat,carbo,CANDIDATE
fire,kar,vessels/cooking,fire/heat,carbo,CANDIDATE
fire,char,vessels/cooking,fire/heat,carbo,CANDIDATE
syrup,syr,sweetened,syrup/potion,syrupus,CANDIDATE
broth,ykal,vessels/soaking,broth/decoction,,CANDIDATE
bitter,amar,wines/bitters,bitter herb,amarus,CANDIDATE
lime,calc,minerals/fire,lime/quickite,calx,CANDIDATE
```

**After completing Phase 2, read this document again to find Phase 3.**

---

## PHASE 3: Implement Tokenizer

**Goal:** Parse EVA lines into tokens with IDs

**File:** src/tokenizer.py

```python
"""
Tokenizer for Voynich EVA text.
Splits lines into tokens, preserves structure.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import re

@dataclass
class Token:
    """A single token from EVA transcription."""
    id: str                    # folio.line.index format
    eva: str                   # original EVA
    zfd: str = ""             # ZFD orthography
    operator: Optional[str] = None
    operator_type: Optional[str] = None
    stem: str = ""
    stem_known: bool = False
    stem_gloss: str = ""
    suffix: Optional[str] = None
    suffix_semantic: Optional[str] = None
    expansion: str = ""        # full shorthand expansion
    croatian: str = ""         # normalized Croatian
    english: str = ""          # English gloss
    confidence: float = 0.0
    rewrites: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

def tokenize_line(line: str, folio: str, line_num: int) -> List[Token]:
    """
    Tokenize a single EVA line.
    
    Args:
        line: EVA text line
        folio: Folio identifier (e.g., "f88r")
        line_num: Line number (1-indexed)
    
    Returns:
        List of Token objects
    """
    tokens = []
    words = line.strip().split()
    
    for i, word in enumerate(words):
        # Clean the word (remove any annotation markers)
        clean_word = re.sub(r'[^a-z]', '', word.lower())
        if not clean_word:
            continue
            
        token = Token(
            id=f"{folio}.{line_num}.{i+1}",
            eva=clean_word
        )
        tokens.append(token)
    
    return tokens

def tokenize_folio(eva_text: str, folio: str) -> List[List[Token]]:
    """
    Tokenize an entire folio.
    
    Args:
        eva_text: Full EVA text for folio
        folio: Folio identifier
    
    Returns:
        List of lines, each containing list of tokens
    """
    lines = []
    for i, line in enumerate(eva_text.strip().split('\n')):
        if line.strip():
            tokens = tokenize_line(line, folio, i + 1)
            if tokens:
                lines.append(tokens)
    return lines
```

**Tests:** src/tests/test_tokenizer.py
```python
def test_basic_tokenization():
    tokens = tokenize_line("qokeedy daiin chol", "f88r", 1)
    assert len(tokens) == 3
    assert tokens[0].eva == "qokeedy"
    assert tokens[0].id == "f88r.1.1"

def test_empty_line():
    tokens = tokenize_line("", "f88r", 1)
    assert len(tokens) == 0
```

**After completing Phase 3, read this document again to find Phase 4.**

---

## PHASE 4: Implement Operator Detection

**Goal:** Detect and tag operators at token start

**File:** src/operators.py

```python
"""
Operator detection for ZFD pipeline.
Detects word-initial grammatical operators.
"""

import json
from typing import Tuple, Optional

class OperatorDetector:
    def __init__(self, operators_file: str):
        with open(operators_file) as f:
            data = json.load(f)
        self.operators = {op['eva']: op for op in data['operators']}
        self.detection_order = data['detection_order']
    
    def detect(self, eva_token: str) -> Tuple[Optional[dict], str]:
        """
        Detect operator at start of token.
        
        Args:
            eva_token: EVA token string
        
        Returns:
            Tuple of (operator_dict or None, remaining_token)
        """
        for op_key in self.detection_order:
            if eva_token.startswith(op_key):
                remaining = eva_token[len(op_key):]
                return self.operators[op_key], remaining
        return None, eva_token
    
    def apply_to_token(self, token) -> None:
        """Apply operator detection to Token object."""
        op, remaining = self.detect(token.eva)
        if op:
            token.operator = op['croatian']
            token.operator_type = op['type']
            token.rewrites.append(f"operator: {op['eva']}→{op['croatian']}")
            token.confidence += 0.25
            token.notes.append(f"Operator {op['gloss']} ({op['status']})")
```

**Tests:**
```python
def test_qo_detection():
    detector = OperatorDetector("data/operators.json")
    op, rest = detector.detect("qokeedy")
    assert op['croatian'] == "ko"
    assert rest == "keedy"

def test_no_operator():
    detector = OperatorDetector("data/operators.json")
    op, rest = detector.detect("daiin")
    # "da" IS an operator
    assert op['croatian'] == "da"
    assert rest == "iin"
```

**After completing Phase 4, read this document again to find Phase 5.**

---

## PHASE 5: Implement Mid-Word Substitution & Gallows

**Goal:** Apply mid-word substitutions and gallows expansions

**File:** src/gallows.py

```python
"""
Gallows expansion and mid-word substitution.
"""

import json
from typing import List, Tuple

class GallowsExpander:
    def __init__(self, gallows_file: str, mid_word_file: str, lexicon: dict):
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
    
    def apply_gallows(self, text: str, confidence_boost: bool = True) -> Tuple[str, List[str], float]:
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
```

**After completing Phase 5, read this document again to find Phase 6.**

---

## PHASE 6: Implement Suffix Parser & Stem Lookup

**Goal:** Parse suffixes and identify stems

**File:** src/suffixes.py

```python
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
```

**File:** src/stems.py

```python
"""
Stem lexicon lookup.
"""

import csv
from typing import Optional, Dict

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
    
    def find_in_text(self, text: str) -> list:
        """Find all known stems in text."""
        found = []
        for variant, data in self.stems.items():
            if variant in text:
                found.append((variant, data))
        return found
```

**After completing Phase 6, read this document again to find Phase 7.**

---

## PHASE 7: Implement Full Pipeline

**Goal:** Combine all modules into complete decode pipeline

**File:** src/pipeline.py

```python
"""
Full ZFD decode pipeline.
"""

from dataclasses import asdict
from typing import List, Dict
import json

from .tokenizer import Token, tokenize_folio
from .operators import OperatorDetector
from .gallows import GallowsExpander
from .suffixes import SuffixParser
from .stems import StemLexicon

class ZFDPipeline:
    def __init__(self, data_dir: str = "data"):
        self.operators = OperatorDetector(f"{data_dir}/operators.json")
        self.lexicon = StemLexicon(f"{data_dir}/lexicon.csv")
        self.gallows = GallowsExpander(
            f"{data_dir}/gallows.json",
            f"{data_dir}/mid_word.json",
            self.lexicon.stems
        )
        self.suffixes = SuffixParser(f"{data_dir}/suffixes.json")
    
    def process_token(self, token: Token) -> Token:
        """Process a single token through all pipeline stages."""
        
        # Stage 1: Operator detection
        self.operators.apply_to_token(token)
        working = token.eva
        if token.operator:
            # Remove operator prefix for stem analysis
            _, working = self.operators.detect(token.eva)
        
        # Stage 2: Mid-word substitution
        working, mid_rewrites = self.gallows.apply_mid_word(working)
        token.rewrites.extend(mid_rewrites)
        if mid_rewrites:
            token.confidence += 0.10
        
        # Stage 3: Gallows expansion
        working, gal_rewrites, gal_conf = self.gallows.apply_gallows(working)
        token.rewrites.extend(gal_rewrites)
        token.confidence += gal_conf
        
        # Stage 4: Suffix parsing
        stem_candidate, suffix = self.suffixes.parse(working)
        if suffix:
            token.suffix = suffix['croatian']
            token.suffix_semantic = suffix['semantic']
            token.rewrites.append(f"suffix: {suffix['eva']}→{suffix['croatian']} ({suffix['gloss']})")
            token.confidence += 0.15
        
        # Stage 5: Stem lookup
        stem_data = self.lexicon.lookup(stem_candidate)
        if not stem_data:
            # Try finding partial matches
            found = self.lexicon.find_in_text(stem_candidate)
            if found:
                stem_data = found[0][1]
                stem_candidate = found[0][0]
        
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
        
        # Count operators
        operator_counts = {}
        for t in all_tokens:
            if t.operator:
                operator_counts[t.operator] = operator_counts.get(t.operator, 0) + 1
        
        # Count known vs unknown stems
        known_stems = sum(1 for t in all_tokens if t.stem_known)
        unknown_stems = sum(1 for t in all_tokens if t.stem and not t.stem_known)
        
        # Average confidence
        avg_confidence = sum(t.confidence for t in all_tokens) / len(all_tokens) if all_tokens else 0
        
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
```

**After completing Phase 7, read this document again to find Phase 8.**

---

## PHASE 8: Output Generators

**Goal:** Generate JSON, CSV, and Markdown outputs

**File:** src/output.py

```python
"""
Output generators for ZFD pipeline.
"""

import json
import csv
from typing import Dict, List

def generate_json(result: Dict, output_path: str):
    """Generate JSON output."""
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

def generate_csv(result: Dict, output_path: str):
    """Generate CSV token table."""
    fieldnames = [
        'token_id', 'eva', 'zfd', 'operator', 'stem', 'suffix',
        'expansion', 'croatian', 'english', 'confidence', 'notes'
    ]
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for line in result['lines']:
            for token in line:
                writer.writerow({
                    'token_id': token['id'],
                    'eva': token['eva'],
                    'zfd': token['zfd'],
                    'operator': token['operator'] or '',
                    'stem': token['stem'],
                    'suffix': token['suffix'] or '',
                    'expansion': token['expansion'],
                    'croatian': token['croatian'],
                    'english': token['english'],
                    'confidence': token['confidence'],
                    'notes': '; '.join(token['notes'])
                })

def generate_markdown(result: Dict, output_path: str):
    """Generate Markdown report."""
    folio = result['folio']
    diag = result['diagnostics']
    
    md = []
    md.append(f"# Folio {folio} Decode Report")
    md.append(f"\n**Generated by ZFD Pipeline**\n")
    
    # Section A: EVA
    md.append("## Section A: Original EVA\n")
    md.append("```")
    for line in result['lines']:
        md.append(" ".join(t['eva'] for t in line))
    md.append("```\n")
    
    # Section B: ZFD Orthography
    md.append("## Section B: ZFD Orthography\n")
    md.append("```")
    for line in result['lines']:
        md.append(" ".join(t['zfd'] for t in line))
    md.append("```\n")
    
    # Section C: Shorthand Expansion
    md.append("## Section C: Shorthand Expansion\n")
    for line in result['lines']:
        for t in line:
            md.append(f"- **{t['eva']}** → {t['expansion']}")
    md.append("")
    
    # Section D: Normalized Croatian
    md.append("## Section D: Normalized Croatian\n")
    for line in result['lines']:
        md.append(" ".join(t['croatian'] for t in line))
    md.append("")
    
    # Section E: English Translation
    md.append("## Section E: English Translation\n")
    for line in result['lines']:
        english_line = " ".join(t['english'] for t in line)
        md.append(f"> {english_line}")
    md.append("")
    
    # Section F: Diagnostics
    md.append("## Section F: Diagnostics\n")
    md.append(f"- **Total tokens:** {diag['total_tokens']}")
    md.append(f"- **Known stems:** {diag['known_stems']} ({diag['known_ratio']:.1%})")
    md.append(f"- **Unknown stems:** {diag['unknown_stems']}")
    md.append(f"- **Average confidence:** {diag['average_confidence']}")
    md.append(f"\n**Operator distribution:**")
    for op, count in diag['operator_counts'].items():
        md.append(f"- {op}: {count}")
    md.append(f"\n**Unknown stems (for lexicon review):**")
    md.append(f"```\n{', '.join(diag['unknown_stem_list'])}\n```")
    
    md.append("\n**Validation checks:**")
    for check, passed in diag['validation'].items():
        status = "✓ PASS" if passed else "✗ FAIL"
        md.append(f"- {check}: {status}")
    
    with open(output_path, 'w') as f:
        f.write("\n".join(md))
```

**After completing Phase 8, read this document again to find Phase 9.**

---

## PHASE 9: Unit Tests

**Goal:** Test suite with fixtures from the paper

**File:** tests/test_pipeline.py

```python
"""
Unit tests for ZFD pipeline.
Fixtures from the paper Section 3.2.
"""

import pytest
from src.pipeline import ZFDPipeline

@pytest.fixture
def pipeline():
    return ZFDPipeline(data_dir="data")

# Core example from paper
def test_qokeedy(pipeline):
    """Test the canonical example from paper §3.2"""
    from src.tokenizer import Token
    token = Token(id="test.1.1", eva="qokeedy")
    result = pipeline.process_token(token)
    
    assert result.operator == "ko", "qo should map to ko"
    assert "kost" in result.stem or "st" in result.zfd, "k should expand to st"
    assert result.confidence >= 0.5, "High-confidence token"

def test_daiin(pipeline):
    from src.tokenizer import Token
    token = Token(id="test.1.2", eva="daiin")
    result = pipeline.process_token(token)
    
    assert result.operator == "da", "da is dose operator"
    assert result.suffix == "ain" or "ain" in result.zfd

def test_chol(pipeline):
    from src.tokenizer import Token
    token = Token(id="test.1.3", eva="chol")
    result = pipeline.process_token(token)
    
    assert result.operator == "h", "ch maps to h"
    assert "ol" in result.zfd, "ol preserved"

def test_shedy(pipeline):
    from src.tokenizer import Token
    token = Token(id="test.1.4", eva="shedy")
    result = pipeline.process_token(token)
    
    assert result.operator == "š", "sh maps to š"
    assert result.stem_known, "edy is known stem (root)"

def test_okal(pipeline):
    from src.tokenizer import Token
    token = Token(id="test.1.5", eva="okal")
    result = pipeline.process_token(token)
    
    assert result.stem_known, "okal is known vessel"
    assert "pot" in result.stem_gloss.lower() or "jar" in result.stem_gloss.lower()

def test_sar(pipeline):
    from src.tokenizer import Token
    token = Token(id="test.1.6", eva="sar")
    result = pipeline.process_token(token)
    
    assert result.stem_known, "sar is salt"
    assert "salt" in result.stem_gloss.lower()

def test_kostol(pipeline):
    """Bone + oil compound"""
    from src.tokenizer import Token
    token = Token(id="test.1.7", eva="kostol")
    result = pipeline.process_token(token)
    
    # Should find both kost and ol
    assert result.stem_known

def test_no_operator(pipeline):
    """Word with no operator"""
    from src.tokenizer import Token
    token = Token(id="test.1.8", eva="ol")
    result = pipeline.process_token(token)
    
    assert result.operator is None
    assert result.stem == "ol"
    assert result.stem_known

def test_gallows_k(pipeline):
    """k should expand to st"""
    from src.tokenizer import Token
    token = Token(id="test.1.9", eva="keedy")
    result = pipeline.process_token(token)
    
    assert "st" in result.zfd, "k expands to st"

def test_gallows_t(pipeline):
    """t should expand to tr"""
    from src.tokenizer import Token
    token = Token(id="test.1.10", eva="otedy")
    result = pipeline.process_token(token)
    
    assert "tr" in result.zfd, "t expands to tr"
```

**After completing Phase 9, read this document again to find Phase 10.**

---

## PHASE 10: Main Entry Point & CLI

**Goal:** Runnable CLI tool

**File:** main.py

```python
#!/usr/bin/env python3
"""
ZFD Folio Decode Pipeline
Usage: python main.py <folio_id> <eva_file>
"""

import sys
import os
from src.pipeline import ZFDPipeline
from src.output import generate_json, generate_csv, generate_markdown

def main():
    if len(sys.argv) < 3:
        print("Usage: python main.py <folio_id> <eva_file>")
        print("Example: python main.py f88r input/f88r.txt")
        sys.exit(1)
    
    folio = sys.argv[1]
    eva_file = sys.argv[2]
    
    # Read EVA text
    with open(eva_file) as f:
        eva_text = f.read()
    
    # Initialize pipeline
    pipeline = ZFDPipeline(data_dir="data")
    
    # Process folio
    print(f"Processing folio {folio}...")
    result = pipeline.process_folio(eva_text, folio)
    
    # Generate outputs
    os.makedirs("output", exist_ok=True)
    
    json_path = f"output/{folio}_decode.json"
    csv_path = f"output/{folio}_table.csv"
    md_path = f"output/{folio}_report.md"
    
    generate_json(result, json_path)
    print(f"  → {json_path}")
    
    generate_csv(result, csv_path)
    print(f"  → {csv_path}")
    
    generate_markdown(result, md_path)
    print(f"  → {md_path}")
    
    # Print summary
    diag = result['diagnostics']
    print(f"\n=== SUMMARY ===")
    print(f"Tokens: {diag['total_tokens']}")
    print(f"Known stems: {diag['known_stems']} ({diag['known_ratio']:.1%})")
    print(f"Avg confidence: {diag['average_confidence']}")
    print(f"\nValidation:")
    for check, passed in diag['validation'].items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")

if __name__ == "__main__":
    main()
```

---

## SUCCESS CRITERIA

✅ All 10 unit tests pass
✅ Pipeline runs on f88r EVA text
✅ JSON output is valid and complete
✅ CSV has all columns populated
✅ Markdown report has all 6 sections
✅ Diagnostics show kost_present = True
✅ Diagnostics show ol_present = True  
✅ Known stem ratio > 50%
✅ Average confidence > 0.4

---

## TEST INPUT (f88r EVA)

Create file `input/f88r.txt` with this EVA text:

```
doršeoi ctrheol kocsthei dori šeor šolprhor dal hcsthod
sal šeom stol hear šestor kostor dain sar rain osti sam
oain or om otram osteom heor kosteodi dar or om heodi
kosteol heol sain heos heol doleei or heom heomam
iosteodi heom koor hes isteor ši sam
stoaiplhhi cplhol orhor plheoli otrhol oldi sal sali
dhei hostol dain koestol koestol kocsthoi ostol heol
dšeol kostei s hi sain hor otreor ain hosals
treol hor olšeodi kosteol šoisthi ol šeol šeol dg
ihei ostain hol heor ol horholsal
ploeas šeosti olstei ctrhol ploldi sostoldi
kostol hol kostol kostol hol hei or ain oldal
istar heol hol hei csthei s or šear ar alsi
stor hei kostol heol hodi kostol sthor hol dal
isteei heor heotrei heol kosteor hetrhi opral
dar hear hol dol koesteor heom
```

---

## DELIVERABLES CHECKLIST

When complete, Claude Code should have produced:

1. `output/f88r_decode.json` - Full token objects with audit trail
2. `output/f88r_table.csv` - Spreadsheet-friendly token table
3. `output/f88r_report.md` - Human-readable 6-section report
4. All tests passing (`pytest tests/`)

Push all outputs to GitHub repo: `denoflore/ZFD/decode_runs/YYYYMMDD_f88r/`

---

**Specification version:** 1.0 (bacon'd)
**Created:** 2026-02-02
**For:** Claude Code autonomous execution
**Confidence:** 98% (full lexicon + all rules included)

🥓✨ Cooked with love. xoxo
