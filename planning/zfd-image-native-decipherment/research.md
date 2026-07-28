# ABSORB: research for zfd-image-native-decipherment

> Phase ABSORB. The repository and primary sources were inspected before design.
> Observed facts, inferences, and open questions remain separate throughout.

## Substrate NSL first move

- `brain_nsl_scan`: unavailable in the active Codex tool inventory.
- `unified_scan`: unavailable in the active Codex tool inventory.
- `unified_query`: unavailable in the active Codex tool inventory.
- Knowledge Board fallback: four semantic searches were started in parallel and
  produced no usable result before the tool host became stale after about twelve
  minutes. No prior ZFD result was imported from that attempt.
- Integration directive: record the failed first move, make no claim that the
  substrate was searched successfully, and continue from the checked out source
  plus directly inspected external records.

## Repository identity and pull receipt

- GitHub authority: `https://github.com/denoflore/ZFD`, owned by Chris under the
  `denoflore` account.
- Pulled commit: `3193695b69fa8983734af8917cf3c791118033fd` on `main`.
- Remote tree: 2,453 tracked blobs in 2,728 tree entries, 183,288,971 bytes, not
  truncated by the GitHub tree API.
- Target: `F:\Dropbox\0 ZFD`, which already contained a much larger local research
  corpus and was not a Git checkout.
- Collision audit: seven tracked paths already existed and all seven were byte
  identical. No differing destination path was overwritten.
- Copy: 2,434 tracked files were added through an additive `robocopy`. Forty one
  Microsoft placeholder paths were skipped by that pass and then copied one at a
  time after confirming that each destination was absent.
- Verification: local `HEAD`, local `origin/main`, and live GitHub `main` all
  resolved to the same commit. Tracked change count and deletion count were zero,
  `git diff --exit-code` returned zero, and `git fsck --full` returned `FSCK_OK`.

## Codebase walk

### Actual data flow

1. `scripts/eva_parser.py` reads `02_Transcriptions/LSI_ivtff_0d.txt` and writes
   per folio EVA files under `voynich_data/raw_eva`.
2. `scripts/batch_converter.py` sends EVA through `scripts/zfd_mapper.py` and
   writes Croatian orthographic forms under `voynich_data/croatian`.
3. `06_Pipelines/zfd_decoder_v2.py` performs EVA to Croatian character mapping,
   greedy operator, stem, and suffix decomposition, then composes English token
   glosses.
4. `transcription/scripts/batch_transcribe.py` also reads IVTFF EVA, selects the
   H transcription when available, and mechanically generates the claimed direct
   palaeographic transcription package.
5. `translations`, `output`, and the static edition present those generated
   layers as manuscript readings and translations.

This route has no image observation boundary between the manuscript and the
claimed reading. It cannot independently test glyph segmentation, identify a
script, or validate a translation.

### Measured corpus state

- `voynich_data/raw_eva`: 201 files, 5,784 source records comprising 5,385 text
  lines and 399 labels.
- `voynich_data/croatian`: 199 files. `f85r` and `f86v` are absent relative to the
  raw EVA set.
- `translations/recipes`: 201 files and 5,704 EVA, CRO, EXP, ENG blocks. That is
  generated coverage of the EVA records, with no independent image check.
- `transcription/folios`: 197 directories and 4,944 line records. These comprise
  4,883 text records, 53 labels, 4 titles, 3 ring text records, and 1 diagram.
  Only 142 records have a nonempty English gloss.
- Raw EVA folios absent from `transcription/folios`: `f70r`, `f72r`, `f89r`,
  `f95r`, `f101r`, and `f102r`. Extra transcription directories are `f85v` and
  `f116v`.
- `translations/PIPELINE_SUMMARY_v2.json`: 42,357 tokens, with 26,965 called
  fully resolved, 13,724 called partially resolved, and 1,668 called unknown.
  The reported 96.1 percent combines full and partial character coverage.
- `zfd_decoder/output/full_manuscript/voynich_zfd_complete.json`: 200 folios,
  26,844 tokens, 11,199 known stems, a known stem ratio of 0.417188, and 2,049
  unknown stem types.
- `FOLIO_INDEX.md`: semantic translation status is 39 of 225 indexed units,
  or 17 percent.

### Confidence semantics

- `06_Pipelines/zfd_decoder_v2.py:202-230` permits a lexicon stem anywhere within
  the remaining token.
- `06_Pipelines/zfd_decoder_v2.py:246-249` calculates confidence as matched
  characters divided by token length.
- `06_Pipelines/zfd_decoder_v2.py:387-394` calls 70 percent character coverage
  fully resolved and 30 percent partially resolved.
- This confidence measures the decoder's ability to cover its own mapped token.
  It is not OCR confidence, reading accuracy, language identification, or
  translation accuracy.

### Image OCR state

- `06_Pipelines/glagolitic_ocr/glagolitic_ocr.py` starts with an empty template
  dictionary and returns `(None, 0.0)` when the caller supplies no templates.
- No template set, labelled glyph images, trained model, line truth, held out
  split, CER, WER, calibration report, or manuscript OCR output is committed.
- `CC_INSTRUCTIONS_GLAGOLITIC_OCR_PIPELINE.md` records only Phase 1 as complete
  and leaves every stated OCR success criterion open.
- Its planned Phase 2 begins from IVTFF EVA. Completing that plan would retain
  the same transcription dependency.
- A live probe on a repository folio found 2 line regions and 587 contours, then
  classified 0 glyphs with confidence 0 and emitted question marks.

### Reproducibility state

- Default Windows collection of `zfd_decoder/tests` fails because UTF 8 JSON is
  opened through the cp1252 locale in `zfd_decoder/src/compound.py`.
- With `PYTHONUTF8=1`, all 32 decoder mechanics tests pass. They contain no
  manuscript image truth, human translation truth, or provenance truth.
- `scripts/test_mapper.py` crashes under the default Windows console while
  printing Unicode check marks. Under UTF 8 it prints successful cases, while
  its Croatian pattern routine always returns true and the script has no
  aggregate failure exit.
- `06_Pipelines/coverage_v36b.py` and `coverage_v40.py` fail because they open
  `/home/claude/word_freq.csv`. Several other scripts contain `/home/claude` or
  `/home/user/ZFD` paths.
- The repository has no root `pyproject.toml`, lock file, unified dependency
  declaration, or Windows and Linux continuous integration gate.

## Canonical claim contradictions

| Published claim | Repository counterevidence | Required disposition |
|---|---|---|
| Structural decipherment complete | `METHODOLOGY.md` leaves semantics, palaeography, independent replication, and peer review open | Rename to corpus wide EVA derived structural hypothesis |
| Entire manuscript translated | `FOLIO_INDEX.md` reports 39 of 225 units, 17 percent | Call the all folio artefact an orthographic rendering with token glosses |
| Direct image transcription replaced EVA | The batch transcriber reads IVTFF EVA for 192 automated folios | Separate five claimed image anchors from the EVA derived batch corpus |
| Pharmaceutical folios f87r to f102v complete | Phase 9 tracker reports 8 of 17 panels and the document omits f91, f92, and f95 through f102 | Relabel as selected hypothesis readings |
| OCR implemented | The recogniser has no templates or model and emits no classified glyphs | Replace with an image native pilot and measurable truth set |
| Ragusan provenance locked | The evidence lacks registered alternatives, null distribution, comparison cities, and temporally controlled independent records | Treat Ragusa as one candidate and run a preregistered provenance test |

## External primary and institutional research

### Voynich image authority

- Yale Beinecke, `MS 408`: `https://beinecke.library.yale.edu/beinecke/collections/beinecke-cipher-voynich-manuscript`.
- Authority: holding institution.
- Support: unidentified script and author, high resolution images of the complete
  manuscript available for research, six broad illustrative sections, and the
  documented custody chain from Rudolph II forward.
- Limit: Yale does not endorse decipherment theories. Material consistency with
  the fifteenth century does not establish writing date, language, genre, or
  production place.
- Integration directive: use Yale IIIF pixels and catalogue foliation as the
  manuscript observation authority. Record the exact Yale rights statement per
  asset before redistribution.

### Croatian angular and cursive Glagolitic context

- Old Church Slavonic Institute, `https://stin.hr/en/glagolitic-script/`.
- Authority: central Croatian academic institute for Glagolitic studies.
- Support: angular Croatian Glagolitic follows the twelfth century; the
  fourteenth and fifteenth centuries are its golden period; semi formal and
  cursive forms emerge in the second half of the fourteenth century for books,
  legal documents, and office records.
- Limit: this establishes chronological and regional plausibility only. It gives
  no Voynich glyph identification.
- Integration directive: use its script classification and named manuscript
  corpus to define comparative controls.

### Croatian Glagolitic medical genre

- Marija Ana Duerrigl and Stella Fatovic Ferencic, *Hrvatskoglagoljske
  ljekaruse, zapisi izmedju retorike i empirije*, Slovo 74 (2024), pages 17 to
  43, DOI `https://doi.org/10.31745/s.74.5`, open PDF
  `https://hrcak.srce.hr/file/470862`.
- Authority: peer reviewed original research by the Old Church Slavonic
  Institute and the Croatian Academy's history of medicine department.
- Support: Croatian Glagolitic medical recipe texts survive from the fourteenth
  century onward and combine empirical, religious, medical, narrative, and
  performative discourse.
- Limit: genre compatibility cannot identify the Voynich text or locate it in
  Dubrovnik.
- Integration directive: derive genre features and candidate manuscript
  shelfmarks from the paper, then evaluate them against image anchored readings.

### Dated image and text benchmark

- University of Graz GAMS, *Zrcalo člověčaskogo spasenja* (1445),
  `https://gams.uni-graz.at/context%3Aspeculum`.
- Authority: scholarly digital edition by the Institute of Croatian Language and
  Linguistics with University of Graz infrastructure.
- Support: 81 folios of angular Glagolitic written on Krk in 1445, displayed as
  facsimile plus TEI semi diplomatic transcription.
- Rights: edition metadata displays CC BY 4.0. Vatican Library facsimiles are
  displayed with permission and require separate rights review for reuse.
- Limit: book hand, normalised Latin transcription, resolved ligatures, and
  expanded abbreviations make it unsuitable as unmodified glyph truth.
- Integration directive: acquire TEI and IIIF metadata, preserve raw line images
  under source restrictions, and create diplomatic Glagolitic Unicode labels
  through expert correction.

### Existing OCR baselines

- Achim Rabus, `achimrabus/crnn-ctc-glagolitic`,
  `https://huggingface.co/achimrabus/crnn-ctc-glagolitic`.
- Authority: model publisher's repository.
- Support: Apache 2.0 CRNN CTC weights, about 42.7 MB, trained on 23,203 lines and
  validated on 1,361 lines from two fourteenth and fifteenth century Glagolitic
  manuscripts. The model card reports 5.33 percent validation CER.
- Limit: the output is Latin transliteration, abbreviations are expanded, and
  the validation manuscripts do not represent an unknown Voynich hand. The
  training image rights require independent verification.
- Integration directive: quarantine as a comparative baseline and optional
  encoder initialisation. Never treat its Latin output as manuscript truth.

### Dubrovnik archival controls

- State Archives in Dubrovnik catalogue, fonds HR-DADU-09 Diversa Notariae,
  `https://arhiv.jas-center.eu/index.php/diversa-notariae-various-documents-of-the-public-notary%3Bisad?sf_culture=en`.
- Authority: official archival description.
- Support: 147 volumes spanning relevant fifteenth century dates, fully
  accessible to researchers. The catalogue describes the Latin and Italian
  notarial record system and its relationship to Diversa Cancellariae and the
  Slavic Chancellery.
- Limit: the catalogue alone provides no Voynich link and no evidence that the
  relevant Ragusan records used Glagolitic.
- Integration directive: request the 1438 Serrano, 1454 Garbo, 1482 Bozidarevic,
  and 1553 Angelik pharmacy inventories, plus Dogana records for 1432 to 1440.
  Register exact shelfmarks, document languages, hands, and negative findings.

## Provenance assessment after ABSORB

Observed:

- Croatian angular and cursive Glagolitic is chronologically compatible with the
  manuscript's material period.
- Croatian Glagolitic medical writing is a real historical genre.
- Direct fifteenth century Ragusan pharmacy and customs records exist and can
  provide better controlled commodity evidence.
- The present ZFD Ragusan tests match broad commodities and a repository written
  pharmacy narrative spanning 1317 to the present. They do not supply a null,
  comparison cities, effect size, multiplicity correction, or independent
  temporal control.
- The current repository's own Vetranovic comparison shows zero Italian exact
  terms and stems in a text dated to the 1540s. Zero Italian cannot by itself
  date the Voynich text before 1450.

Inference:

- The broad Croatian Glagolitic medical hypothesis remains plausible enough to
  test.
- A specifically Ragusan origin currently has weaker direct support than the
  wider Croatian Glagolitic hypothesis. Dubrovnik's documented administrative
  controls also require Cyrillic and Latin alternatives to be tested.

Open:

- Whether any Voynich glyph sequence can be read reproducibly as Glagolitic from
  the images before language knowledge enters.
- Whether a sealed image reading favours Croatian over Church Slavonic, Czech,
  Slovenian, Latin, Italian, German, cipher, abbreviation system, constructed
  script, or nonlinguistic generation.
- Whether any independently identified recipe or commodity distribution has
  geographic power after registered nulls and multiple testing correction.

## Integration directives for HARDEN

1. Freeze all existing decipherment outputs as historical hypothesis artefacts.
2. Create one canonical manifest joining Yale surfaces, folio labels, all text
   regions, local files, hashes, and explicit exclusions.
3. Define an evidence record that separates pixel observation, segmentation,
   grapheme alternatives, script attribution, transliteration, linguistic
   analysis, literal gloss, fluent translation, and provenance claims.
4. Build the primary OCR entry point with zero EVA, IVTFF, ZL, or legacy
   transcription imports. Enforce that boundary with source scanning and runtime
   dependency tests.
5. Start with a stratified ten folio gold pilot across scribes, sections, labels,
   dense text, diagrams, and foldouts. Use independent annotation and adjudication.
6. Split by source manuscript and Voynich folio group before fitting. Keep
   synthetic variants with their parents.
7. Report inventory coverage, line detection, sequence CER, grapheme confusion,
   calibration, and translation review coverage as separate metrics.
8. Make unresolved a valid terminal state. Completeness means every region has a
   record and disposition, not that every region has a forced reading.
9. Replace the current completion language with a claim ledger that can block a
   public assertion when its receipts are missing.
10. Test Ragusa after the image reading is frozen, using primary archive records,
    registered alternative cities, negative controls, and corrected significance.
