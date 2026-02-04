# ZFD Morpheme Gap Analysis: What's Missing and How to Fill It

**Date:** February 3, 2026
**Status:** Strategic assessment for CC pipeline enrichment
**Author:** Claudette (Opus 4.5)

---

## The Problem in Numbers

CC's `character_reference.py` has **21 morphemes** in CROATIAN_MORPHEMES.
The `zfd_decoder/data/lexicon.csv` has **89 entries** (the canonical lexicon).
The `PHARMACEUTICAL_MORPHEMES.md` has another **~30 categorized morphemes**.

But looking at the recipe output (e.g., f103r), **54 out of 54 ENG lines show "?"**. Zero resolved to English. The pipeline goes EVA -> CRO -> EXP -> ENG, and the ENG column is almost entirely blank because:

1. CC's CROATIAN_MORPHEMES dict (21 entries) was never synced with lexicon.csv (89 entries)
2. The decoder pipeline (`zfd_decoder/`) uses JSON/CSV configs but the OCR pipeline (`06_Pipelines/`) has its own hardcoded dict
3. Neither pipeline does full word-level resolution. They decompose, but don't reconstruct meaning

**The real coverage:** lexicon.csv has 89 stem variants covering ~40 distinct concepts. The manuscript has ~7,859 unique word forms. Even with operator+stem+suffix decomposition, the morpheme dictionary needs to cover the stems that appear in the remaining ~3.2% uncovered tokens (325 words), plus provide *semantic resolution* for the 96.8% that parse structurally but don't yet yield English glosses.

---

## What Exists (Inventory)

### Source 1: `zfd_decoder/data/lexicon.csv` (CANONICAL)
89 entries. Categories:
- **Ingredients:** bone, oil, water, salt, honey, flour, root, wine, milk, flower, rose, myrrh, aloe, galbanum, storax, opopanax, camphor, anise, coriander, mint, sage, fennel, rue, hyssop, mallow, broom, vervain, plantain, cinnamon, ginger, pepper, sulfur, silver, copper, iron, saltpeter, alum
- **Equipment:** pot (okal/okar/otal/ostal/ostar), cauldron (kal/stal), flask (phar)
- **Actions:** soak (shor/šor), cook (chor/hor), dose (dar/dain), boil (thor/tror), strain (šei), combine (hei)
- **Properties:** fire/heat (kair/kar/star/char), syrup, broth, bitter, lime, old, new, dry, wet, cold, warm, pain, burn, peace
- **Grammar:** give (da/dain), self (sam), gift (dar), day (dan), vessel (otrai/ostai), walk (hodi)

### Source 2: `character_reference.py` CROATIAN_MORPHEMES (CC's dict)
21 entries. Subset of lexicon.csv plus operators (ko, o, s) and Latin (oral).

### Source 3: `PHARMACEUTICAL_MORPHEMES.md`
Operators (ch-, qo-, ok-, sh-, da-, ot-, sa-, so-, yk-, pc-, tc-), stems (ol, or, k, ee, od, ed, kal, kar), class markers (-al, -ar), suffixes (-y, -iin, -aiin, -dy, -m, -ain, -ir).

### Source 4: `FINAL_CHARACTER_MAP_v1.md`
The master theory document. 5 operators, 4 gallows, 3 stem vowels, 5 suffixes, plus pharmaceutical vocabulary candidates.

### Source 5: `LATIN_PHARMACEUTICAL_VOCABULARY.md`
6 exact Latin matches (oral, orolaly, dolor, sal, da, ana) plus variants.

---

## What's Missing

### Gap 1: SINGLE SOURCE OF TRUTH
Three different morpheme stores exist and none are synced:
- lexicon.csv (89 entries, most complete, used by zfd_decoder)
- CROATIAN_MORPHEMES dict (21 entries, used by OCR pipeline)
- PHARMACEUTICAL_MORPHEMES.md (prose, not machine-readable)

**Fix:** One canonical JSON/CSV. Everything else imports from it.

### Gap 2: BOTANICAL SECTION VOCABULARY
The lexicon is heavily pharmaceutical. The herbal section (folios 1-66) uses plant-specific vocabulary that isn't well represented. We need:

| Missing Domain | Examples Expected | Source to Pull From |
|----------------|-------------------|---------------------|
| Plant parts beyond "root" | leaf (list), stem (stabljika), bark (kora), seed (sjeme), berry (bobica), flower (cvijet), petal | Croatian botanical dictionaries, Glagolitic herbals |
| Plant actions | grow (rasti), bloom (cvjetati), wilt (venuti), dry (sušiti) | Croatian verb forms |
| Seasonal/temporal | spring (proljeće), harvest (žetva), morning (jutro) | Recipe timing vocabulary |
| Preparation (herbal-specific) | infuse (uliti), distill, macerate, decoct, tincture | Latin-Croatian pharma glossaries |

### Gap 3: BIOLOGICAL SECTION VOCABULARY
Folios 75-86 (the "biological" or "balneological" section) have distinct vocabulary:

| Missing Domain | Examples | Source |
|----------------|----------|--------|
| Body parts | head (glava), stomach (želudac/trbuh), liver (jetra), heart (srce), skin (koža), eye (oko) | Medical Latin-Croatian glossaries |
| Bodily fluids | blood (krv), bile (žuč), urine (mokraća), phlegm (sluz) | Humoral medicine terminology |
| Conditions | fever (groznica), swelling (oteklina), wound (rana), poison (otrov) | 15th c. medical vocabulary |

### Gap 4: ASTRONOMICAL/COSMOLOGICAL VOCABULARY
Folios 67-73 (the "astronomical" section):

| Missing Domain | Examples | Source |
|----------------|----------|--------|
| Celestial bodies | star (zvijezda), moon (mjesec), sun (sunce) | Croatian astronomical terms |
| Time markers | night (noć), day (dan), month (mjesec) | Already partially in lexicon |

### Gap 5: FULL CROATIAN VERB CONJUGATION
The operator system captures verb prefixes, but the pipeline doesn't resolve full verb forms. Croatian verbs conjugate:
- kuhati (cook) -> kuham, kuhaš, kuha, kuhamo...
- miješati (mix) -> miješam, miješaš...
- dati (give) -> dajem, daješ, daje... or dam, daš, da...

The shorthand likely truncates these, but the reconstruction layer needs to handle the common patterns.

### Gap 6: LATIN PHARMACEUTICAL CORPUS
The apothecary manual comparison text exists but isn't systematically mined. That 55-page Latin manual has hundreds of terms that should be cross-referenced with Voynich word forms:

| What to Extract | Why It Matters |
|-----------------|---------------|
| Recipe formulae structure | "Recipe X, et Y, cum Z" patterns map to operator+stem sequences |
| Dosage vocabulary | Beyond "da" and "ana", there are dozens of measurement/admin terms |
| Preparation verbs | Latin verbs for cook, soak, strain, grind, dissolve, etc. |
| Body part / condition pairs | "Pro dolore X" / "Ad morbum Y" patterns |
| Ingredient co-occurrence | Which ingredients appear together in recipes |

---

## Best Practice: The Fill Strategy

### Phase 1: Consolidate (Can Do Now)

**Merge all existing morpheme data into one canonical file.**

Take lexicon.csv (89 entries) as the base. Add:
- The 6 Latin terms from LATIN_PHARMACEUTICAL_VOCABULARY.md
- Operators from operators.json (7 entries)
- Suffixes from suffixes.json (15 entries)
- Class markers from PHARMACEUTICAL_MORPHEMES.md (-al, -ar)
- Mid-word substitutions from mid_word.json (7 entries)

Produce: `lexicon_v2.csv` with columns: `name, variant, context, gloss, latin, croatian, category, status, section_affinity`

Then have CC regenerate CROATIAN_MORPHEMES from this single source.

**This alone would jump the ENG resolution rate from near-zero to probably 30-40%** because the existing 89 lexicon entries aren't being used by the recipe pipeline at all.

### Phase 2: Mine the Pharmaceutical Miscellany (Can Do Now)

The 55-page Latin apothecary manual (Beinecke Pharma Miscellany) that David Landino has seen. Systematically extract:

1. Every ingredient noun (Latin + English gloss)
2. Every preparation verb
3. Every administration route
4. Every condition/ailment
5. Every measurement term
6. Every body part reference

Cross-reference each against the Voynich word frequency list. Any Latin term that appears as a substring of a Voynich EVA word (after operator stripping) is a candidate morpheme.

**What you need:** The full text of that miscellany. If it's already in Dropbox as `LAT_ENG_Pharmamiscellany_2066895.txt`, we can pull it directly.

### Phase 3: Croatian Botanical Enrichment (Needs Source Text)

**What you need:**
- A Croatian-Latin botanical glossary or herbal (ideally 15th-16th century)
- The Glagolitic herbals catalogued in Croatian archives (if digitized)
- Modern Croatian pharmaceutical dictionaries that include traditional/folk medicine terms

Specific texts to look for:
1. **Libri de simplicibus** (Nicolaus Salernitan, widely copied) for Latin plant names
2. **Ljekobilje** entries from Croatian dictionaries (folk herbal medicine vocabulary)
3. Croatian Academy (HAZU) digitized manuscripts (Glagolitic medical/botanical texts)
4. The **Vinodolski zakon** and other Glagolitic legal/practical texts for general vocabulary

### Phase 4: Frequency-Driven Gap Filling (Can Do Now With Scripts)

Instead of guessing what words mean, work backwards from the data:

1. Run the full decoder on all 37,026 words
2. Collect every word that parses to operator+stem+suffix but the stem is UNKNOWN
3. Rank unknown stems by frequency
4. For each high-frequency unknown stem, look at:
   - Which section does it appear in (herbal vs pharma vs bio)?
   - What operators precede it most often?
   - What suffixes follow it?
   - What illustrations are adjacent on those folios?

The top 20 unknown stems by frequency would cover a disproportionate chunk of the remaining gaps.

### Phase 5: Georgie Validation Loop (Needs Human)

For every proposed Croatian word reconstruction, Georgie can assess:
- "Does this sound like a real Croatian word/morpheme?"
- "Is this phonotactically valid in Croatian?"
- "What historical or dialectal form might this be?"

This is your validation layer. No amount of computational morpheme matching replaces a native speaker's ear for "that sounds right" vs "that's gibberish."

---

## Materials Needed (Summary)

| Material | Status | Where to Get It |
|----------|--------|-----------------|
| Pharmaceutical Miscellany full text | Probably in Dropbox | Pull LAT_ENG_Pharmamiscellany_2066895.txt |
| Croatian botanical dictionary | NEEDED | HAZU digital archives, Croatian National Library |
| Latin herbal (Libri de simplicibus or similar) | NEEDED | Available on Internet Archive / Google Books |
| Ragusan notarial documents | NEEDED | Croatian State Archives, Dubrovnik Archives |
| Glagolitic medical manuscripts (if any digitized) | NEEDED | HAZU, Staroslavenski institut |
| Complete Voynich word frequency list by folio | Can generate | Run decoder on full IVTFF corpus |
| Voynich word-to-illustration adjacency map | Partially exists | validation/folio_annotations.json (81.7KB) |

---

## Recommended Execution Order

1. **IMMEDIATE (tonight/tomorrow):** Merge lexicon.csv into CC's pipeline. One PR. Massive jump in resolution.
2. **THIS WEEK:** Pull pharma miscellany text, systematic extraction of every Latin term.
3. **THIS WEEK:** Run frequency analysis on unknown stems, rank by occurrence.
4. **NEXT WEEK:** Source Croatian botanical references. HAZU digital library search.
5. **ONGOING:** Georgie validation loop on every batch of new morpheme candidates.
6. **STRETCH:** Ragusan archival documents for scribal convention comparison.

---

*The dictionary isn't empty. It's fragmented across 3-4 files that don't talk to each other. Step one is consolidation. Step two is mining what you already have. New source texts are step three.*
