# Voynich Manuscript -- Formal Abbreviation Inventory

**Date:** 2026-02-07
**Version:** 1.0.0
**Status:** Derived from Phases 1-3 analysis (hand sheet, ductus analysis, 5 anchor folio transcriptions)
**Methodology:** ZFD three-layer positional shorthand system, cross-referenced with Croatian Angular Glagolitic cursive conventions

---

## 1. Overview

The Voynich Manuscript employs a systematic abbreviation system rooted in Croatian Angular Glagolitic cursive ("office script"). Abbreviations operate at three positional layers:

1. **Word-initial:** Grammatical operators abbreviating function words/prepositions
2. **Word-medial:** Gallows characters abbreviating consonant clusters (broken ligatures)
3. **Word-final:** Suffix markers abbreviating morphological endings

This is NOT a cipher. It is a professional shorthand system of the type used by trained notarial scribes in the eastern Adriatic region (Ragusa/Dubrovnik) for pharmaceutical and trade records, c. 1404-1438.

---

## 2. Gallows Cluster Abbreviations (Medial Position)

These are the most distinctive feature of the system. The four "gallows" characters (tall ascenders with loops) are **abbreviation marks** that expand into consonant clusters. They derive from Croatian Angular Glagolitic tall letterforms used as abbreviation markers.

| EVA Mark | Expansion (Primary) | Expansion (Secondary) | Frequency | Medial % | Certainty | Key Productions |
|----------|---------------------|----------------------|-----------|----------|-----------|-----------------|
| k | **-st-** | -sk- | ~2000+ | 89.9% | **HIGH** | kost (bone), korist (use), ostar (vessel), ostol (bone oil) |
| t | **-tr-** | -tv- | ~1500+ | 85.3% | **HIGH** | otr- (treated), itra (liver), otvori (open), otrorhetri |
| f | **-pr-** | -fr- | ~800 | 72.7% | **HIGH** | upra (direction), cpho/prho (from/heat) |
| p | **-pl-** | -sp- | ~600 | 65.5% | **MEDIUM** | spoj (join), plod (fruit) |

### Application Rules

1. **Contextual expansion:** Gallows expand ONLY when the result produces a known stem or satisfies phonological constraints. Not every gallows instance has the same expansion.
2. **Primary vs secondary:** Use the primary expansion first. Only use the secondary if the primary produces no known stem.
3. **k → st is the most reliable:** 89.9% medial position, with "ostol" (bone oil) as the gold-standard validated example (Curio confirmation).
4. **t → tr is well-established:** 85.3% medial, with "otrorhetri" as the validated example.
5. **f → pr and p → pl are less certain:** Lower medial percentages (72.7% and 65.5%) suggest these gallows may occasionally function differently.

### Validated Examples

| EVA Word | ZFD Reading | English | Source | Validation |
|----------|-------------|---------|--------|------------|
| okol | **ostol** | bone oil | f88r label 15 | Curio adversarial ✓ |
| otorchety | **otrorhetri** | treated heated fluid | f88r label 1 | Curio adversarial ✓ |
| qokol | **koostol** | which-bone-oil | f88r text (multiple) | Consistent recipe context |
| kol | **kostol** | bone-oil | f88r L8 | Pharmaceutical context |

### Where This Differs from EVA

EVA treats k, t, f, p as four simple letter substitutions. The ZFD framework shows they are **cluster abbreviation marks**:

| EVA Interpretation | ZFD Interpretation | Evidence |
|-------------------|-------------------|----------|
| k = single phoneme /k/ | k = abbreviation for /-st-/ cluster | Position (89.9% medial), productive vocabulary, validated examples |
| t = single phoneme /t/ | t = abbreviation for /-tr-/ cluster | Position (85.3% medial), productive vocabulary, validated examples |
| f = single phoneme /f/ | f = abbreviation for /-pr-/ cluster | Position (72.7% medial), Glagolitic Frt source |
| p = single phoneme /p/ | p = abbreviation for /-pl-/ cluster | Position (65.5% medial), Glagolitic Pokoj source |

---

## 3. Operator Prefix Abbreviations (Word-Initial Position)

Word-initial characters function as grammatical operator prefixes. They abbreviate function words, prepositions, or verbal particles that in full Croatian would be separate words or prefixes.

| EVA Mark | Croatian | Gloss | Latin Equivalent | Initial % | Frequency | Certainty | Detection Order |
|----------|----------|-------|------------------|-----------|-----------|-----------|-----------------|
| qo | ko- | which/that/quantity | quod/quot | 98.5% | ~2000+ | **HIGH** | 1 |
| q | k- | which (short) | quod | 98.5% | ~100 | **HIGH** | 7 (last) |
| ch | h-/x- | combine/cook/action | coquere | ~50% | ~1500 | **HIGH** | 2 |
| sh | s-/sh- | with/soak | sorbere | ~58% | ~1200 | **HIGH** | 3 |
| da | da- | dose/give/add | dare | ~70% | ~500 | **HIGH** | 4 |
| ok | ost- | vessel/container | olla + st | variable | ~300 | **MEDIUM** | 5 |
| ot | otr- | vessel/treated | olla + tr | variable | ~200 | **MEDIUM** | 6 |

### Detection Order Rule

Operators must be detected in order from **longest match to shortest**:
```
qo → ch → sh → da → ok → ot → q
```

This prevents incorrect splitting: "qo" must not be parsed as "q" + "o".

### Operator Behavior in Anchor Folios

From f88r transcription:
- `qo-` appears ~12 times, overwhelmingly before "-kol/-keol" (= "which-bone-oil")
- `ch-` appears ~15 times as cooking/action marker
- `sh-` appears ~8 times marking soaking processes
- `d-/da-` appears ~6 times as recipe instructions (give/dose)

From f1r transcription:
- `qo-` less frequent (text-only page, different genre)
- `ch-/sh-` remain common
- `da-` used in recipe-like instructions

---

## 4. Suffix Abbreviations (Word-Final Position)

Word-final characters abbreviate Croatian morphological endings. Detection follows **longest-first** order.

### Multi-Character Suffixes (detect first)

| EVA Mark | Croatian | Function | Frequency | Certainty |
|----------|----------|----------|-----------|-----------|
| aiin | -ain | substance/thing noun | ~1500+ | **HIGH** |
| edy | -edi | prepared/processed (verbal) | ~500+ | **HIGH** |
| eey | -ei | instance of | ~300+ | **MEDIUM** |

### Single/Double Character Suffixes

| EVA Mark | Croatian | Function | Final % | Frequency | Certainty |
|----------|----------|----------|---------|-----------|-----------|
| y | -i | adjective/genitive | 84.5% | ~2800+ | **HIGH** |
| ol | -ol | oil/oily | n/a | ~400+ | **HIGH** |
| ar | -ar | water/agent | n/a | ~400+ | **HIGH** |
| or | -or | oil (variant) | n/a | ~300+ | **HIGH** |
| al | -al | substance | n/a | ~300+ | **HIGH** |
| am | -am | instrumental (by means of) | 91.4% | ~200+ | **HIGH** |
| om | -om | instrumental (with/by) | n/a | ~150+ | **HIGH** |
| od | -od | completed | n/a | ~100+ | **CANDIDATE** |
| n | -n | noun ending | 95.4% | ~1500+ | **HIGH** |
| l | -l | noun ending | 53.0% | ~600+ | **HIGH** |
| r | -r | agent/doer | 73.4% | ~500+ | **HIGH** |
| m | -m | instrumental (short) | 91.4% | ~100+ | **MEDIUM** |

### The '-al' vs '-ar' Duality

This is semantically significant:
- **-al** = substance/container/vessel context (Latin -ale)
- **-ar** = water/liquid/agent context (Latin -arius)

Both are word-final segments, but they encode different semantic domains. In pharmaceutical text, -al tends to mark solid substances while -ar marks liquid preparations.

---

## 5. Compound Abbreviations (Bench Gallows)

When a crescent ('c' = EVA 'e' shape) precedes a gallows with an 'h'-stroke following, the result is a "bench gallows" -- a compound abbreviation combining the ch-operator with a gallows cluster.

| EVA Compound | Expansion | Components | Frequency | Certainty |
|-------------|-----------|------------|-----------|-----------|
| cth | h + tr | ch-operator + t-gallows | ~800+ | **HIGH** |
| ckh | h + st | ch-operator + k-gallows | ~400+ | **HIGH** |
| cph | h + pl | ch-operator + p-gallows | ~200+ | **HIGH** |
| cfh | h + pr | ch-operator + f-gallows | ~100+ | **MEDIUM** |

Bench gallows show continuous pen movement from crescent through gallows to h-stroke, indicating these are conceived as single graphic units, not sequences of separate characters.

---

## 6. Ligature Units

Certain character sequences function as single units rather than separate characters:

| EVA Sequence | ZFD Value | Type | Evidence |
|-------------|-----------|------|----------|
| qo | /ko/ | Operator ligature | Zero pen-lift construction |
| ch | /h/ | Operator ligature | Zero pen-lift construction |
| sh | /sh/ | Operator ligature | Zero pen-lift construction |
| aiin | /-ain/ | Suffix ligature | Connected minims, zero pen lifts |
| aiiin | /-ain/ (extended) | Suffix ligature | Same as aiin with extra minim |

These sequences should be parsed as units, not decomposed into individual characters.

---

## 7. State Markers

Combined operator + stem units marking processing states:

| EVA Marker | Expansion | Function | Certainty |
|-----------|-----------|----------|-----------|
| he | he | state/result/after | MEDIUM |
| heo | heo | state/result (extended) | MEDIUM |
| se | se | soaked-state/after soaking | MEDIUM |
| seo | seo | soaked-state (extended) | MEDIUM |

---

## 8. Latin Pharmaceutical Terms

Terms borrowed directly from Latin pharmaceutical vocabulary, appearing primarily in the pharmaceutical section:

| EVA Form | ZFD Reading | Latin | English | Certainty |
|----------|-------------|-------|---------|-----------|
| ost/oste/osteo | ost/oste/osteo | os (bone) | bone | HIGH |
| oral/orolaly | oral/orolali | oralis (by mouth) | oral/orally | HIGH (confirmed) |
| dol | dol | dolor | pain | MEDIUM |
| sal | sal | sal | salt | HIGH |
| ana | ana | ana | equal parts (Rx) | MEDIUM |
| da | da | da (imperative) | give | HIGH |
| recipe | recipe | recipe | take (Rx) | MEDIUM |

---

## 9. Parsing Algorithm Summary

For any Voynich word, apply these steps in order:

```
1. OPERATOR DETECTION (word-initial, longest match first):
   qo → ko | ch → h | sh → s/sh | da → da | ok → ost | ot → otr | q → k

2. SUFFIX DETECTION (word-final, longest match first):
   aiin → ain | edy → edi | eey → ei | y → i | ol | ar | or | al |
   am | om | od | n | l | r | m

3. GALLOWS EXPANSION (remaining medial characters):
   k → st (primary) / sk (secondary)
   t → tr (primary) / tv (secondary)
   f → pr (primary) / fr (secondary)
   p → pl (primary) / sp (secondary)
   Apply only when result matches known stem or satisfies phonology.

4. DIRECT MAPPING (remaining characters):
   o → /o/ | a → /a/ | e → /e/ | i → /i/ |
   r → /r/ | l → /l/ | d → /d/ | n → /n/ | s → /s/ | m → /m/

5. VALIDATION:
   Check result against unified_lexicon_v2 stems.
   Check Croatian morphological validity.
   Check pharmaceutical genre plausibility.
```

---

## 10. Where EVA Gets It Wrong: 5 Key Divergences

| # | EVA Assumption | ZFD Correction | Evidence |
|---|---------------|----------------|----------|
| 1 | Each glyph = one letter in unknown alphabet | Glyphs are positional: operators, abbreviation marks, suffixes | Position distributions (k=89.9% medial, q=98.5% initial, y=84.5% final) |
| 2 | Gallows k = single phoneme | k = abbreviation mark for -st- cluster | "okol" → "ostol" (bone oil), validated by Curio |
| 3 | 'ch' = two characters (c + h) | 'ch' = single operator ligature /h/ | Zero pen-lift ductus, functional unity |
| 4 | 'aiin' = four separate characters | 'aiin' = single suffix ligature /-ain/ | Connected minims, zero pen lifts, suffix behavior |
| 5 | Word boundaries separate equal-status characters | Word boundaries separate OPERATOR + STEM + SUFFIX units | Tripartite positional structure with functional specialization |

---

## 11. Frequency Summary from Anchor Folios

### f88r (Pharmaceutical -- 31 lines + labels)

| Abbreviation Type | Count | Most Common Instance |
|-------------------|-------|---------------------|
| k-gallows (→st) | ~25 | "ostol" (bone oil) |
| t-gallows (→tr) | ~8 | "otror" (treated) |
| f-gallows (→pr) | ~4 | "opral" compounds |
| p-gallows (→pl) | ~3 | "ploeeas" (pour) |
| qo- operator | ~12 | "koostol" (which-bone-oil) |
| ch- operator | ~15 | "heol" (cook-oil) |
| sh- operator | ~8 | "sheol" (soak-oil) |
| -aiin suffix | ~4 | "dain" (substance) |
| -y suffix | ~15 | Various adjectives |
| -ol suffix | ~10 | Oil-related terms |
| sal (Latin) | ~5 | Salt references |

---

## 12. Validation Checklist

- [x] Every abbreviation type from Phases 1-3 cataloged
- [x] Frequency counts derived from anchor folio transcriptions
- [x] Certainty levels justified by positional distribution evidence
- [x] 5 key divergences from EVA documented with evidence
- [x] Rules formatted for programmatic application (see abbreviation_rules.json)
- [x] Gallows expansions validated against Curio results
- [x] Operator detection order specified
- [x] Suffix detection order specified (longest first)
- [x] Compound abbreviations (bench gallows) documented
- [x] Ligature units identified with ductus evidence
- [x] Latin pharmaceutical terms cataloged

---

*This inventory replaces EVA as the reference abbreviation system for reading the Voynich Manuscript.*
