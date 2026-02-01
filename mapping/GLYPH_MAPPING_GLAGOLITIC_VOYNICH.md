# Voynich-Glagolitic Glyph Mapping: Working Hypothesis

**Version:** 1.0
**Date:** February 1, 2026
**Status:** PRELIMINARY - Requires validation

---

## Overview

This document provides a preliminary mapping between Voynichese glyphs (EVA transcription) and Angular Glagolitic letterforms. The mapping is based on:

1. Behavioral paleographic analysis (positional, functional)
2. Visual structural similarity 
3. Known Glagolitic cursive abbreviation patterns
4. Phonological plausibility for Croatian/Slavic substrate

**CRITICAL CAVEAT:** These mappings are HYPOTHESES, not confirmed identifications. Each requires systematic validation against the corpus.

---

## Tier 1: High-Confidence Mappings (Behavioral + Visual Alignment)

### 1.1 Gallows Characters → Glagolitic Tall Ascenders

| EVA | Voynich Shape | Glagolitic Source | Sound | Confidence | Evidence |
|-----|---------------|-------------------|-------|------------|----------|
| k | Bench gallows (simple) | Ⰼ (Kako) cursive | /k/ | MEDIUM | Position-initial operator behavior |
| t | Bench gallows (crossed) | Ⱅ (Tvrdo) cursive | /t/ | MEDIUM | Position-initial operator behavior |
| f | Tall looped gallows | Ⱇ (Frьtъ) cursive | /f/ | LOW | Less common, structural match |
| p | Tall plain gallows | Ⱂ (Pokoj) cursive | /p/ | LOW | Rare, needs validation |

**Behavioral Note:** Gallows appear disproportionately at word-initial position in Voynichese, matching the "operator" function of prepositions and prefixes in Glagolitic texts.

### 1.2 Common Voynich Clusters → Glagolitic Consonant Clusters

| EVA Cluster | Frequency | Proposed Glagolitic | Sound | Confidence |
|-------------|-----------|---------------------|-------|------------|
| ch- | Very high | Ⱈ (Xěrъ) | /x/ or /h/ | MEDIUM |
| sh- | Very high | Ⱊ (Ša) | /ʃ/ | MEDIUM |
| qo- | High | Ⰼ+Ⱁ ligature | /ko-/ | LOW |
| cth- | Medium | Ⱉ (Cy) + Ⱅ (Tvrdo) | /ts/ + /t/ | LOW |

### 1.3 Vowel-Like Glyphs → Glagolitic Vowels

| EVA | Voynich Shape | Glagolitic Source | Sound | Confidence |
|-----|---------------|-------------------|-------|------------|
| o | Circle/loop | Ⱁ (Onъ) | /o/ | HIGH |
| a | Connected loop | Ⰰ (Az) cursive | /a/ | MEDIUM |
| e | Small curl | Ⰵ (Est) cursive | /e/ | MEDIUM |
| i | Vertical tick | Ⰹ (Iže) | /i/ | MEDIUM |
| y | Trailing curve | Ⱏ (Jerъ) | /ə/ or /ɨ/ | LOW |

---

## Tier 2: Morpheme-Based Mappings (From ZFD Analysis)

These mappings derive from the morpheme system identified in prior ZFD work, now interpreted through Glagolitic phonology.

### 2.1 Identified Prefixes (Operators)

| ZFD Morpheme | Proposed Glagolitic | Croatian Parallel | Meaning/Function |
|--------------|---------------------|-------------------|------------------|
| qo- | ko- | Croatian "ko" (who) or prefix | Interrogative/relative |
| ch- | h-/x- | Croatian "h" (into, for) | Directional/purposive |
| sh- | š- | Croatian "š" (with) | Comitative |
| da- | da- | Croatian "da" (that, to) | Subordinator/infinitive |
| o- | o- | Croatian "o" (about) | Topic marker |

### 2.2 Identified Stems

| ZFD Morpheme | Proposed Glagolitic | Croatian Parallel | Possible Meaning |
|--------------|---------------------|-------------------|------------------|
| ed | -ed/-jet | Root element | "root, base" (botanical) |
| od | -od | Croatian "-od" | "from, origin" |
| ol | -ol | Latin loan "-ol" | Oil/liquid (pharma) |
| or | -or | Latin loan "-or" | Agent/substance |

### 2.3 Identified Suffixes

| ZFD Morpheme | Proposed Glagolitic | Croatian Parallel | Function |
|--------------|---------------------|-------------------|----------|
| -y | -i/-y | Croatian "-i" | Adjective/genitive |
| -al | -al | Latin loan "-al" | Property marker |
| -ar | -ar | Croatian "-ar" | Agent/instrument |
| -aiin | -ajin/-ain | Compound suffix | Complex nominal |

---

## Tier 3: Structural Mappings (Shape-Based, Lower Confidence)

### 3.1 Glagolitic Letterform → Voynich Candidate

| Glagolitic | Unicode | Name | Sound | Voynich Candidate | Notes |
|------------|---------|------|-------|-------------------|-------|
| Ⰰ | U+2C00 | Az | /a/ | EVA 'a' variant | Loop forms |
| Ⰱ | U+2C01 | Buky | /b/ | Unknown | Rare in cursive |
| Ⰲ | U+2C02 | Vede | /v/ | Unknown | May merge with 'u' |
| Ⰳ | U+2C03 | Glagoli | /g/ | Unknown | Possible 'g' gallows |
| Ⰴ | U+2C04 | Dobro | /d/ | EVA 'd' | Good structural match |
| Ⰵ | U+2C05 | Est | /e/ | EVA 'e' | Curl forms |
| Ⰶ | U+2C06 | Živete | /ʒ/ | Unknown | Rare |
| Ⰷ | U+2C07 | Dzělo | /dz/ | Unknown | Rare |
| Ⰸ | U+2C08 | Zemlja | /z/ | Unknown | Possible 'z' variant |
| Ⰹ | U+2C09 | Iže | /i/ | EVA 'i' | Tick mark |
| Ⰺ | U+2C0A | I | /i/ | EVA 'ii' | Double tick |
| Ⰻ | U+2C0B | Djervь | /ɟ/ | Unknown | Very rare |
| Ⰼ | U+2C0C | Kako | /k/ | EVA 'k' gallows | HIGH confidence |
| Ⰽ | U+2C0D | Ljudie | /l/ | EVA 'l' | Loop + stem |
| Ⰾ | U+2C0E | Myslite | /m/ | Unknown | Tall form |
| Ⰿ | U+2C0F | Našь | /n/ | EVA 'n' variant | Common |
| Ⱀ | U+2C10 | Onъ | /o/ | EVA 'o' | Circle - CERTAIN |
| Ⱁ | U+2C11 | Pokoj | /p/ | EVA 'p' gallows | Tall form |
| Ⱂ | U+2C12 | Rьci | /r/ | EVA 'r' | Common stem |
| Ⱃ | U+2C13 | Slovo | /s/ | EVA 's' | Descender |
| Ⱄ | U+2C14 | Tvrdo | /t/ | EVA 't' gallows | HIGH confidence |
| Ⱅ | U+2C15 | Ukъ | /u/ | EVA 'u' variant | May merge with 'o' |
| Ⱆ | U+2C16 | Frьtъ | /f/ | EVA 'f' gallows | Looped tall |
| Ⱇ | U+2C17 | Xěrъ | /x/ | EVA 'ch' | Aspirate cluster |
| Ⱈ | U+2C18 | Cy | /ts/ | Unknown | Affricate |
| Ⱉ | U+2C19 | Črьvь | /tʃ/ | EVA 'c' variant | Palatal |
| Ⱊ | U+2C1A | Ša | /ʃ/ | EVA 'sh' | Sibilant cluster |
| Ⱋ | U+2C1B | Šta | /ʃt/ | Unknown | Cluster |

---

## Tier 4: Abbreviation System Hypothesis

Angular Glagolitic uses systematic abbreviation marks. Proposed Voynich parallels:

### 4.1 Superscript Markers

| Glagolitic Convention | Voynich Parallel | Function |
|----------------------|------------------|----------|
| Titlo (overline) | Gallows "cap" element | Abbreviation marker |
| Superscript vowel | -aiin sequences | Vowel indication |
| Suspension mark | Final -y | Word truncation |

### 4.2 Ligature Compression

| Type | Glagolitic Example | Voynich Example |
|------|-------------------|-----------------|
| Horizontal bind | Adjacent letters share stroke | ch-, sh- clusters |
| Vertical stack | Letters stacked | Gallows + o |
| Loop chain | Connected curves | -aiin, -ain |

---

## Validation Requirements

Each mapping requires:

1. **Frequency analysis**: Does Voynich glyph frequency match expected Glagolitic letter frequency?
2. **Positional distribution**: Does the glyph appear in positions consistent with the proposed sound?
3. **Combinatorial patterns**: Do the combinations make phonotactic sense for Croatian/Slavic?
4. **Cross-validation**: Do multiple independent analyses converge?

---

## Testing Protocol

### Test 1: Gallows as Consonants
**Hypothesis:** If gallows = /k/, /t/, /p/, /f/, then:
- They should appear primarily at syllable onsets
- They should be followed by vowel-like glyphs
- They should not cluster at word-final position

### Test 2: Vowel Distribution
**Hypothesis:** If EVA 'o', 'a', 'e', 'i' = vowels, then:
- They should alternate with consonant-like glyphs
- They should show frequency patterns matching Croatian vowel distribution
- Word-final position should show vowel prevalence (Croatian words often end in vowels)

### Test 3: Morpheme Reconstruction
**Hypothesis:** If the morpheme system is valid, then:
- qo-ed-y → Croatian equivalent should be meaningful
- ch-ol-ar → Should relate to pharmaceutical terminology
- sh-od-al → Should parse as grammatical Croatian

---

## Current Status Matrix

| Component | Status | Confidence | Validation Needed |
|-----------|--------|------------|-------------------|
| Gallows → tall consonants | PROPOSED | MEDIUM | Frequency analysis |
| Vowel mappings | PROPOSED | MEDIUM | Distribution test |
| Prefix system | PROPOSED | MEDIUM | Semantic validation |
| Stem system | PROPOSED | LOW | Cross-linguistic check |
| Suffix system | PROPOSED | MEDIUM | Grammatical analysis |
| Abbreviation marks | PROPOSED | LOW | Systematic comparison |

---

## For Claude Code: Implementation Priorities

1. **Build frequency tables** for all Voynich glyphs
2. **Map positional distribution** (initial, medial, final)
3. **Compare to Croatian/Glagolitic frequency data**
4. **Test morpheme boundaries** with proposed sound values
5. **Generate candidate readings** for known pharmaceutical plants

---

*This is a working document. All mappings subject to revision based on empirical testing.*
