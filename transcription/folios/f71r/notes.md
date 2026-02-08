# Folio f71r -- Transcription Notes

## Key Observations

### Section Context
This is a **zodiac folio** ("Aries light"), fundamentally different from the pharmaceutical section folios (e.g., f88r). The circular diagram layout with nymphs in barrels, stars, and a central animal is characteristic of the manuscript's astrological/astronomical section. The ZFD parsing rules were developed primarily against pharmaceutical vocabulary, so their application to zodiac content should be treated with caution.

### No Validated Labels
Unlike f88r, which has two gold-standard validated labels ("ostol" and "otrorhetri"), f71r has **no validated readings**. The closest candidate is "!!okol" in L12 (word 15), which parses identically to the validated "ostol" (bone oil) from f88r, but the double uncertainty marks (!!) in the EVA transcription indicate the original transcriber was not confident in the character readings. This is not a strong anchor.

### Operator Dominance: ot(otr) and ok(ost)
The folio is overwhelmingly dominated by two word-initial operators:
- **ot(otr):** ~28 occurrences across all lines and labels. Every inner band nymph label (L13--L17) begins with ot-. Most outer band labels also use ot-.
- **ok(ost):** ~12 occurrences. Used in ring text and some outer labels.
- **ch(h):** ~8 occurrences. More frequent in the inner ring (L18) where 4 of 10 words begin with ch-.
- **sh(sh):** ~4 occurrences. Appears in ring text and one outer label (L32 "shoekey").

This distribution differs from f88r where qo(ko, "which") was the most common operator. The absence of qo- in f71r may reflect a different discourse type: f88r is a recipe ("which bone-oil..."), while f71r is a diagram with labels.

### Suffix Distribution
- **-y(i) adjective:** Most common suffix, appearing in nearly all labels and many ring text words.
- **-ar (water/agent):** Common in labels (L2, L5, L8, L10) and ring text.
- **-al (substance):** Frequent, sometimes doubled (L11: otralali).
- **-ol (oil):** Appears in several labels (L13, L15, L16) and ring text. Inner band labels show particular affinity for -ol.
- **-aiin(ain) substance:** Three occurrences in L1, one in L12. Consistent pharmaceutical morpheme.
- **-am (instrumental):** Rare; appears in L3 (ostldam) and L14 (otroloaram).

### Gallows Frequency
- **k-gallows (st):** ~15 medial occurrences across ring text. The ost- (bone) stem appears frequently.
- **t-gallows (tr):** ~3 medial occurrences. Less frequent than k-gallows.
- **Bench gallows ckh (hst):** 2 occurrences (L1 "shckhey", L12 "ockhey"). This compound form is relatively rare.
- **No f-gallows (pr) or p-gallows (pl)** observed in any line. This contrasts with f88r which had several.

The complete absence of f- and p-gallows is notable and may distinguish zodiac vocabulary from pharmaceutical vocabulary.

### Unusual Morphological Patterns

1. **Doubled suffixes:** L11 "otalaly" (otralali) has doubled -al-al- before the final -i. L2 "arar" has doubled -ar. These are uncommon in pharmaceutical text and may be zodiac-specific patterns (e.g., emphasizers or nymph-name morphology).

2. **Consonant-final words:** L16 "otolchd" (otrolhd) ends on consonant 'd' without a vowel suffix. This is unusual for Voynich word structure, which overwhelmingly ends in vowels or -l/-r/-n.

3. **Very short words:** L12 contains "shs" (3 EVA chars) and L18 has "chs" (3 chars). These minimal words may be connectives or abbreviated forms.

4. **Initial 'l' words:** L12 word 5 "lsheotey" and word 16 "lkchol" begin with 'l', which is not a standard ZFD operator. The 'l' may function as a determiner ("the") or have a different structural role in zodiac text.

5. **Long compound in L1:** Word 16 "okeo!keo!keody" produces "osteosteosteodi" -- a 15-character Croatian form with tripled ost-e-o- pattern. This is likely either a scribal repetition, a word-boundary error in the EVA transcription, or a genuinely complex compound term. The two uncertain k readings (!) add to the difficulty.

### Comparison with f88r

| Feature | f88r (Pharmaceutical) | f71r (Zodiac) |
|---------|----------------------|---------------|
| Layout | Three horizontal registers | Circular diagram with rings |
| Dominant operator | qo(ko) "which" | ot(otr) "vessel/treated" |
| Gallows diversity | k, t, f, p all present | k dominant; t rare; f, p absent |
| Validated words | 2 (ostol, otrorhetri) | 0 |
| Label structure | Short, 1-word labels | Mixed: 1-word and 2-word labels |
| Text function | Recipe instructions | Circular text (function unclear) |
| Overall confidence | B | C--D |

### The "ostol" Question

Word 15 of L12 reads "!!okol" in EVA, which parses identically to the validated "ostol" from f88r (ok(ost)+o+l = ost+o+l = "ostol"). If this reading is correct, it would be the first occurrence of the validated "bone oil" term outside the pharmaceutical section. However:
- The double uncertainty marks (!!) indicate the EVA transcriber was unsure of the reading.
- The zodiac context provides no obvious reason for a "bone oil" reference.
- Without independent confirmation from the manuscript image, this remains speculative.

Similarly, word 10 of L18 "okeol" = "osteol" (ok(ost)+e+o+l) is morphologically close to "ostol" but has an extra vowel 'e', producing a different form. This could be a variant spelling, a different word, or a scribal variation.

### Clock Positions and Nymph Distribution

The outer band nymph labels occupy positions from 10:30 clockwise to 09:00, covering approximately the full circle but with uneven spacing:
- Dense cluster from 10:30 to 03:15 (6 nymphs, ~150 degrees)
- Sparser from 03:15 to 09:00 (4 nymphs, ~210 degrees)

The inner band has 5 nymphs more evenly distributed from 11:00 to 09:00.

### Non-Voynich Text

The "ab\*i\*l" annotation below the central animal is written in non-Voynich script. Similar non-Voynich annotations appear on other zodiac folios and may represent:
- A later owner's identification of the zodiac sign (cf. Latin "Aries" or a Semitic language)
- A folio numbering or organizational mark
- A scholar's annotation from any period between the 15th century and the modern era

This annotation is explicitly excluded from ZFD parsing as it uses a different writing system.

### Confidence Distribution
- **A:** 0 entries
- **B:** 8 entries (simple function words: ar, or, al, ain, sal, dain; and well-parsed short forms)
- **C:** 23 entries (most labels and ring text words with plausible but unvalidated parsings)
- **D:** 7 entries (words with unusual clusters, uncertainty marks, or opaque morphology)

The overall confidence for this folio is significantly lower than f88r. This reflects both the zodiac context (where pharmaceutical glosses may not apply) and the higher density of uncertainty marks in the EVA transcription.

### Divergence from Existing Recipe Decoder Output

The existing ZFD decoder v2.0 output (`translations/recipes/f71r_recipe.md`) differs from this paleographic transcription in several ways:
1. **Gallows expansion:** The recipe decoder inconsistently expands t-gallows. This transcription consistently applies ot(otr) word-initially and t(tr) medially.
2. **Operator application:** The recipe decoder sometimes leaves ot- unexpanded (e.g., "oteody" instead of "otreodi"). This transcription follows the f88r gold-standard convention of always expanding operators.
3. **Morpheme glosses:** The recipe decoder uses automated lexicon lookup producing verbose glosses. This transcription provides terse morpheme-level glosses with explicit confidence ratings.

---

*Transcription notes completed 2026-02-07.*
