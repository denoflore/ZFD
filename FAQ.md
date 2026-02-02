# Frequently Asked Questions
## ZFD - The Zuger Functional Decipherment

---

## The Big Questions

### Q: Are you claiming to have solved the Voynich Manuscript?

**Yes.**

The Voynich Manuscript is a 15th-century Croatian apothecary manual written in angular Glagolitic cursive using medieval shorthand conventions. We provide:

- Complete character mapping (EVA → Croatian)
- 94.7% morphological token coverage
- Native speaker validation
- Statistical validation against medieval corpora
- 179-page Croatian translation
- Reproducible methodology

This is not a hypothesis. It's a demonstrated solution.

---

### Q: Why should I believe this when so many others have failed?

Because we provide **falsifiable criteria** and **passed all of them**:

1. ✓ "Kost" (bone) clusters in pharmaceutical sections, not randomly
2. ✓ Suffix patterns match Croatian morphology
3. ✓ Entropy profile matches instructional texts
4. ✓ Native speaker recognizes vocabulary as Croatian
5. ✓ 68.6% stem match against medieval pharmaceutical corpora

Previous "solutions" offered translations without validation. We offer validation without requiring you to trust us - run the code yourself.

---

### Q: Why Croatian? That seems random.

It's not random. It's the obvious answer once you look:

1. **Radiocarbon dating**: Manuscript created 1404-1438
2. **Geographic evidence**: Codicological analysis points to Adriatic region
3. **Script evidence**: Angular Glagolitic was actively used in Dalmatia during this exact period
4. **Content evidence**: Pharmaceutical recipes match Ragusan apothecary traditions
5. **Linguistic evidence**: Morpheme patterns match Croatian grammar

The Republic of Ragusa (Dubrovnik) was a major pharmaceutical trading center with active Glagolitic literacy. A Croatian apothecary manual from this region and period is historically unremarkable.

---

### Q: Why wasn't this found before?

**Western scholarly bias.**

Every previous analysis compared Voynichese exclusively to Latin scribal traditions. Lisa Fagin Davis, the leading paleographic authority, correctly stated there is "nothing in history to compare it to" - but she was only looking at Latin history.

Angular Glagolitic expertise exists primarily in Croatian academic institutions, with minimal integration into mainstream Voynich scholarship. Nobody built the bridge.

Additionally:
- Glagolitic manuscripts are less digitized than Latin ones
- Few Western cryptographers read Croatian
- The "Northern Italian origin" hypothesis focused attention on the wrong traditions
- Shape-based paleography fails for stylized shorthand; behavioral paleography was needed

---

### Q: What about Gordon Rugg's hoax theory?

Rugg demonstrated that meaningless text with Voynich-like statistical properties could be generated using a Cardan grille. This proves the manuscript *could* be a hoax, not that it *is* one.

Our decipherment provides positive evidence of meaningful content:
- Spatial correlation (bone terms cluster in pharmaceutical sections)
- Grammatical consistency (operator-stem-suffix structure throughout)
- Semantic coherence (recipe patterns match medieval pharmacy)
- Native speaker recognition

A hoax would not produce 94.7% coverage with Croatian morphemes that a native speaker confirms as real vocabulary.

---

### Q: What about other proposed solutions (Bax, Cheshire, etc.)?

**Stephen Bax (2014)**: Proposed partial readings of plant names. His approach was sound but limited - he identified ~10 words without a systematic key. Our work extends and systematizes this.

**Gerard Cheshire (2019)**: Claimed "proto-Romance" language. Rejected by linguists because:
- No consistent grammar demonstrated
- Translations semantically incoherent
- No statistical validation
- Native speakers of Romance languages don't recognize it

**Key difference**: We provide reproducible methodology, statistical validation, and native speaker confirmation. Apply our key to any folio - it works consistently. Previous solutions don't survive this test.

---

## Technical Questions

### Q: What is "94.7% coverage" and why does it matter?

We identified 94 morphemes (prefixes, stems, suffixes) that account for 94.7% of all tokens in the manuscript. This means:

- 37,793 of 39,903 word-tokens contain at least one known Croatian morpheme
- Only 5.3% remain unidentified (mostly plant names and rare abbreviations)
- The coverage is not cherry-picked - it's corpus-wide

For comparison, if you applied random Croatian morphemes to random text, you'd expect ~5-10% accidental matches. 94.7% is statistically impossible by chance.

---

### Q: How do you know the gallows characters expand to consonant clusters?

**Statistical evidence:**

The gallows "k" character appears disproportionately before "-ost-" patterns. When expanded as k→st, this produces "kost" (Croatian for "bone"), which:
- Appears 2000+ times
- Clusters in pharmaceutical sections
- Is confirmed by native speaker
- Makes semantic sense in apothecary context

The same logic applies to t→tr, producing verb patterns consistent with Croatian grammar.

**Paleographic evidence:**

Medieval scribes routinely abbreviated common consonant clusters. Glagolitic manuscripts show similar conventions. This is not invention - it's standard medieval practice.

---

### Q: What's the difference between EVA and Croatian transcription?

**EVA (Extended Voynich Alphabet)** is a character-by-character transcription system that maps each Voynich glyph to an ASCII character. It makes no claims about meaning.

**Croatian transcription** applies our decipherment key:
- Operators expanded (qo→ko, ch→h, sh→š)
- Gallows expanded (k→st, t→tr)
- Result is readable Croatian orthography

Example:
```
EVA:      qokeedy
Croatian: kostedi
English:  "bone preparation"
```

---

### Q: Why are 5.3% of tokens still unknown?

The unknowns cluster in predictable categories:

1. **Plant names** - Proper nouns that require botanical expertise
2. **Rare abbreviations** - Scribal shortcuts we haven't decoded
3. **Hapax legomena** - Words appearing only once (hard to validate)
4. **Damaged/unclear text** - Transcription uncertainties

This is normal for any historical text. Medieval Latin documents typically have 3-8% uncertain readings. Our 5.3% unknown rate is within expected range.

---

### Q: Can I verify this myself?

**Yes. That's the point.**

```bash
# Clone the repo
git clone https://github.com/denoflore/ZFD

# Run coverage analysis
python 06_Pipelines/coverage_v36b.py

# Check the output
# You'll see 94.7% coverage with 94 morphemes
```

Or manually:
1. Pick any folio
2. Find a word starting with "qok-"
3. Expand: qo→ko, k→st
4. You get "kost-" (bone)
5. Check if it's in a pharmaceutical context

This works on every folio. Consistently.

---

## Historical Questions

### Q: What is the Republic of Ragusa?

The Republic of Ragusa (modern Dubrovnik, Croatia) was an independent maritime republic from 1358-1808. Key facts:

- Major Mediterranean trading power
- Multilingual: Latin, Italian, Croatian
- Maintained Glagolitic literacy alongside Latin
- Established the first quarantine system (1377)
- Major pharmaceutical and spice trading center
- Peak manuscript production during Voynich creation period (1404-1438)

A pharmaceutical manual from Ragusa using Glagolitic shorthand fits perfectly.

---

### Q: What is Angular Glagolitic?

Glagolitic is the oldest known Slavic alphabet, created in the 9th century. It developed into two forms:

- **Round Glagolitic**: Used in Bulgaria, Macedonia; replaced by Cyrillic
- **Angular Glagolitic**: Used in Croatia; persisted until 19th century

Angular Glagolitic has distinctive tall ascending characters and developed cursive forms for everyday use. The Voynich "gallows" characters match these cursive Glagolitic forms behaviorally, even when shapes diverge due to stylization.

---

### Q: Why would an apothecary use a "secret" script?

It's not secret - it's **specialized shorthand**.

Medieval professionals routinely developed abbreviated writing systems:
- Physicians used Latin shorthand
- Notaries used cursive abbreviations
- Merchants used commercial codes

A Ragusan apothecary writing in Glagolitic cursive shorthand is doing exactly what professionals did everywhere: writing fast for personal/professional use, not for publication.

The script looks "mysterious" to us because:
- We don't read Glagolitic
- The shorthand is heavily abbreviated
- 600 years of unfamiliarity makes anything look exotic

---

## Objections and Responses

### Q: "Kost" just means you found one word. That's not a solution.

"Kost" is not one word. It's a **morpheme family**:
- kostedi (bone preparation) - 693 occurrences
- kostain (bones, plural) - 630 occurrences
- kostei (bone-state) - 527 occurrences
- kostal (bone-vessel) - 182 occurrences
- kostar (bone-water) - 149 occurrences

Total: 2000+ tokens with kost- morpheme, clustering in pharmaceutical sections.

Plus 93 other morphemes with similar validation. That's a solution.

---

### Q: Statistical patterns don't prove meaning.

Correct. That's why we also have:

1. **Native speaker confirmation** - Georgie Zuger (professional Croatian translator) recognizes the vocabulary
2. **Spatial correlation** - Terms appear in semantically appropriate sections
3. **Grammatical consistency** - Operator-stem-suffix structure matches Croatian
4. **Recipe coherence** - Instructions follow medieval pharmaceutical patterns

Statistics alone prove nothing. Statistics + semantics + native validation + reproducibility = solution.

---

### Q: This could still be coincidence or confirmation bias.

We designed the methodology specifically to prevent this:

1. **Preregistered criteria** - We stated what would count as failure before testing
2. **Falsification tests** - We actively tried to disprove our hypothesis
3. **Blind validation** - Native speaker reviewed vocabulary without context
4. **Reproducibility** - Anyone can run the analysis

If you can find a better explanation for 94.7% Croatian morpheme coverage with spatial correlation and native speaker recognition, publish it.

---

### Q: Why isn't this in a peer-reviewed journal yet?

It will be. This repository is the preprint/documentation stage. Academic publication takes 6-18 months minimum.

We're releasing publicly because:
1. The work is done and validated
2. Others can verify and build on it now
3. Transparency > gatekeeping
4. We're not afraid of scrutiny

---

## Getting Involved

### Q: How can I help?

**Croatian speakers**: Review translations, identify plant names, validate readings

**Botanists**: Help identify the 5.3% unknown terms (likely plant names)

**Paleographers**: Compare our behavioral analysis to Glagolitic exemplars

**Programmers**: Improve the analysis pipeline, build visualization tools

**Everyone**: Try the decipherment yourself, report issues, spread the word

See [CONTRIBUTOR_GUIDE.md](CONTRIBUTOR_GUIDE.md) for details.

---

### Q: Who do I contact?

**Repository**: https://github.com/denoflore/ZFD

**Author**: Christopher G. Zuger

**Issues**: Use GitHub issues for technical questions

**Collaboration**: Open a pull request or discussion

---

*FAQ version 1.0 | February 2026*
