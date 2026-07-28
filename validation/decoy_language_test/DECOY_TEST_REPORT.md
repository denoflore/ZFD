# Decoy Language Test, Tier 1: Results and Honest Interpretation

> [!WARNING]
> Legacy inherited transcription hypothesis. Image native OCR, translation, and provenance remain unconfirmed.

<!-- zfd-evidence-status
evidence_status: legacy_eva_derived_hypothesis
primary_input: inherited_transcription
image_native_confirmed: false
translation_confirmed: false
provenance_confirmed: false
-->

**Date:** June 9, 2026
**Verdict: NULL RESULT for language-specific discrimination. POSITIVE for word-structure.**

## Design

The strongest standing criticism of any Voynich decipherment is that a
flexible enough mapping will "decode" the manuscript into whatever language
it was aimed at. This test answers it on the axis nobody had run: hold the
EVA -> phoneme key fixed (19-character map, gallows expansions, operator
prefixes, suffix codebook, all independently motivated by Glagolitic
paleography) and swap ONLY the target dictionary. The ZFD Croatian lexicon
is not used anywhere in this test.

All 6,385 word types (35,812 tokens, all 201 folios) were transliterated
through the frozen key and matched against seven independent dictionaries
under byte-identical rules: Croatian, Slovenian (the cruelest control, a
South Slavic neighbor), Czech, Slovak, Polish, Italian, Latin. Because
larger dictionaries match more random strings, every language is calibrated
against its own null: the identical machinery run on character-shuffled
versions of the same word types. The headline statistic is
LIFT = real match rate / shuffled-null match rate, with bootstrap 95% CIs.

## Results (token-weighted, prefix4 tier)

| Language | Dict size | Real % | Null % | Lift | 95% CI |
|----------|-----------|--------|--------|------|--------|
| Croatian | 53,167 | 21.8 | 5.3 | 4.07 | [3.06, 5.56] |
| Slovenian | 242,205 | 26.2 | 7.1 | 3.70 | [2.82, 4.98] |
| Czech | 241,373 | 34.3 | 9.7 | 3.52 | [2.89, 4.43] |
| Slovak | 154,457 | 31.4 | 8.8 | 3.56 | [2.84, 4.53] |
| Polish | 297,133 | 38.0 | 10.8 | 3.52 | [2.86, 4.47] |
| Italian | 95,012 | 24.0 | 5.5 | 4.40 | [3.20, 6.28] |
| Latin | 48,370 | 21.3 | 4.3 | 4.93 | [3.44, 7.74] |

## What this does and does not show

**Does NOT show:** Croatian advantage. All seven languages cluster at
3.5-4.9x lift with overlapping confidence intervals; Latin is nominally
highest. At this tier's resolution (frozen key, generic modern wordlists,
no semantics), the transliteration does not discriminate Croatian from
European controls. This is a preserved negative result, in full.

**DOES show:** Voynichese character order is word-shaped. Every language
matches the real transliteration at ~4-5x the rate of its own
character-shuffled null. Random glyph sequences would lift at ~1.0. The
ordering information that shuffling destroys is precisely what makes the
strings match natural-language word shapes, uniformly across European
languages. A glyph-soup hoax is strongly disfavored by this result even
though no specific language is favored.

## Where the burden of proof now sits

This test deliberately excluded the ZFD lexicon to avoid circularity, and
the result sharpens the claim structure: language-specific evidence for
the Croatian reading does NOT live at the raw wordlist-matching layer. It
lives, if anywhere, in (a) the external provenance locks (V27 triple lock:
import/domestic taxonomy, temporal gating, recipe continuity), which no
dictionary flexibility can fit, and (b) demonstrated structure (positional
operator encoding, 5-6x diagonal; layered noise robustness). Claims in the
paper should be worded accordingly.

## Known caveats (cut both ways, do not rescue the strong claim)

- Modern hunspell lemma lists under-represent 15th-century vocabulary and
  Cakavian dialect forms; the Croatian dictionary is also the smallest
  (53k lemmas). Lift normalizes promiscuity but not lemma coverage of the
  relevant register.
- Slavic inflection is represented differently across hunspell lemma sets.
- Tier 2 (adversarially refit the full mapping per decoy language under an
  equal complexity budget, then run the downstream provenance locks) is the
  decisive version and is specced for CC implementation.

## Reproduce

```
python validation/decoy_language_test/run_decoy_test.py
```

Raw output: `decoy_results.json` (config- and dictionary-SHA stamped).
Dictionaries: LibreOffice hunspell (hr/sl/cs/sk/pl/it) + Whitaker's Words
stems (la), vendored in `dictionaries/`.
