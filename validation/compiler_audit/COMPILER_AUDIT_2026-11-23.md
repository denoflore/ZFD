# ZFD recipe decoder and pharmacy concordance audit

**Audit date:** 23 November 2026
**Repository base:** `e1ec81081b9f41ccaa04001f646f7543e74ebb01`
**Decoder audited:** `06_Pipelines/zfd_decoder_v2.py::ZFDDecoder`
**Lexicon:** `08_Final_Proofs/Master_Key/unified_lexicon_v3.json`, version 3.0.0

## Result

The published recipe extraction reproduces **46,578 / 48,379 = 96.2773104%**
combined full-or-partial parser coverage. All **244 committed recipe files**
match freshly rendered output byte for byte.

The source union includes overlapping whole-page/panel representations and
parallel transcriber readings. Using the existing LSI selection functions to
choose one preferred transcription for each line gives **35,568 / 36,959 =
96.2363700%**, across **226 LSI identifiers**. This is a separately labelled
source-selection comparison. The committed recipe corpus has not been replaced.

The recipe decoder and lexicon mappings were not changed by this audit. The
standing verification command was strengthened to enforce its documented
comparison with committed outputs.

## Which implementation was checked?

This document audits `06_Pipelines/zfd_decoder_v2.py::ZFDDecoder`, the recipe
decoder using unified lexicon v3. Its repository-local paths, per-folio
statistics reset and regenerated recipes come from the August 2026 changes
in [`d4dcd050`](https://github.com/denoflore/ZFD/commit/d4dcd0502d8abe3d92552ab57d7f1fd5b06f895c).

The newer November work in [PR #8](https://github.com/denoflore/ZFD/pull/8),
starting at `e1ec81081b9f41ccaa04001f646f7543e74ebb01`, fixes the separate
`transcription/scripts/batch_transcribe.py` compiler and robustness harness.
Those changes were reviewed and incorporated in the integration audited on
23 November. The corrected compiler/report measurements and clean-input
blind-decode rerun are described in the [integrated audit](INTEGRATION_2026-11-23.md).

The third implementation, `zfd_decoder/src/pipeline.py::ZFDPipeline`, uses CSV
lexicons and optional compound decomposition. Its 5/5 frozen and 4/5 shipping
blind-decode results are not recipe-decoder coverage. The actual repository
changes were retrieved; a Claude chat transcript was not available, so no
claim is made about additional uncommitted chat-only edits.

## Exact counts and definitions

| Measure | Published recipe extraction | Preferred-LSI comparison |
|---|---:|---:|
| Source identifiers | 244 | 226 |
| Decoder tokens | 48,379 | 36,959 |
| `fully_resolved` | 30,954 | 23,686 |
| `partially_resolved` | 15,624 | 11,882 |
| Combined `resolved` | 46,578 | 35,568 |
| Combined percentage | 96.2773104% | 96.2363700% |
| `unknown` | 1,801 | 1,391 |
| Empty unmatched residue | 12,707 | 9,897 |
| Empty-residue percentage | 26.2655284% | 26.7783219% |
| Latin-match field present | 6,216 | 4,701 |

`fully_resolved` is the program's label for a rounded match score of at least
0.70. `partially_resolved` means at least 0.30 and below 0.70. The score is
mainly matched-character fraction, rounded to two decimal places; an exact
Latin-term case receives 0.95. It is not a calibrated probability.

In the published extraction, **18,247** tokens in the `fully_resolved` class
still have unmatched residue. Empty residue is a stricter parsing diagnostic,
but it also does not establish semantic correctness. Coverage, complete
character matching and independently verified translation accuracy must be
reported as distinct quantities.

The earlier **92.1%** number comes from a different analysis. The repository's
`06_Pipelines/coverage_v36b.py` tests whether a word contains any listed
morpheme and still reads `/home/claude/word_freq.csv`. It was not the source of
the current measurements, and the difference between its headline percentage
and 96.2773% is not a controlled improvement estimate.

## Lexicon inventory

| Family | Entries |
|---|---:|
| Operators | 22 |
| Stems | 304 |
| Suffixes | 22 |
| State markers | 4 |
| Latin terms | 10 |
| **Family entries** | **362** |
| **Distinct key strings across these families** | **336** |

The additional **36 botanical reference entries** are not loaded into the
recipe decoder's stem dictionary. The structural audit returns **zero
failures and 21 warnings**. This is a structural integrity result, not
independent validation of the glosses. The stem dictionary has **36** entries
explicitly categorized as `action`; the old 91-term inventory is a different
classification and must not be presented as this compiler's observed output.

## Why the denominators differ

The canonical source loader takes **201 raw EVA files** and adds **43 LSI
identifiers** not already present under exactly the same filename. Of those
201 raw identifiers, 183 directly match LSI identifiers and 18 represent whole
pages whose panel IDs are also included.

The overlapping whole-page identifiers are f67r, f67v, f68r, f68v, f70r,
f70v, f72r, f72v, f85r, f86v, f89r, f89v, f90r, f90v, f95r, f95v, f102r
and f102v. Their complete panel mapping appears in the JSON receipt under
`whole_page_aliases`.

For example, the 238 tokens from f102r are also represented by f102r1 and
f102r2. The 18 whole-page aliases contribute **6,041 tokens**. Some source
normalization differs between the two routes, so this is not simply an
identical-file deduplication exercise.

Twelve dense raw folios also retain both H and T transcription readings:
f105v, f106r, f106v, f107r, f107v, f108r, f108v, f111r, f111v, f112r,
f112v and f113r. For example, f111r has 108 raw lines representing 54 LSI line
identifiers with two readings; its raw-file count is 1,199 tokens versus 615
under the preferred-LSI selector.

Across the 183 shared identifiers, duplicate readings and other selection or
normalization differences contribute a net **5,379** tokens. The full
denominator difference is therefore:

`48,379 - 36,959 = 6,041 whole-page-alias tokens + 5,379 other source differences`.

The comparison uses `parse_lsi()` and `eva_text_for()` unchanged, with
preference H, C, F, U, D, G, J, L, M, V, X, Z and the existing fallback. It
counts tokens under those normalization rules, not an externally established
number of physical manuscript words.

## Product and folio concordance

The complete source-bounded list of 18 named preparations or categories is in
the README's [Ingredient Match register](../../README.md#the-ingredient-match).
The register distinguishes documented product names from full recipes and
current stock. It supplies source dates and leaves unmatched products without
invented folio assignments.

The strongest specific rose candidates emitted by this decoder are:

| Folio | Preferred-LSI `ros` emissions | Transliterated form | Score | Unmatched residue |
|---|---:|---|---:|---|
| f9v | 1 | `rostyddaly` | 0.40 | `tyddal` |
| f105v | 1 | `rostaix` | 0.43 | `taix` |
| f115v | 1 | `rosteedy` | 0.75 | `te` |
| f115v | 1 | `rosy` | 1.00 | empty |

These four emitted stems are comparison candidates for the documented rose
preparations. Their scores and residues remain visible. The canonical input
union includes another reading on f105v, yielding five emissions across the
same three folios. `rosar` and `rosol` are not emitted in either run.

On **f13v**, the token `octrros` is decomposed as `ctrr` plus suffix `s`, with
residue `oo`; `ros` is not emitted. The former specific rose-cream identification
is not reproduced by this decoder. On **f88r**, `stor` is emitted three times
and `sal` once, alongside oil and water stems, but no rose stem is emitted.

Corpus-wide, `stor` has 132 emitted matches across 82 identifiers in the
published extraction, versus 108 across 72 in the preferred-LSI run. The
active wax forms `cer` and `cera` are never emitted. A generic oil stem cannot
establish an almond-oil formula, and a single resin cannot identify theriac.

The pharmacy interview supports changes to ingredients over time, with no
individual replacement dates or causes specified. The documented 1667 archive
loss and 1901 pharmacy modernization do not supply those missing dates. The
README provides the direct source links and withdraws the unsupported
bone-oil-to-beeswax and post-1667-storax assertions.

## Verification correction

The original `regenerate_corpus.py --check` compared two newly generated
renderings, but never compared either with the committed file it had read.
It could pass with stale or missing published output. Its original tests
compared five selected recipe pages with their committed counterparts.

This patch makes check mode reject missing or changed recipe files,
unexpected recipe files, and a missing or changed summary. Three regression
cases exercise changed-page, missing-page and changed-summary failures. The regression cases pass in the integrated suite. All 244 actual recipe
files and the full summary pass the
strengthened check. The parser and lexicon are unchanged.

The misleading name/comment of a non-None decomposition test was also
corrected: the recipe decoder does not perform the whole-word grammar
preservation that the old test comment claimed.

## Reproduce

From the repository root:

```bash
python -m pytest -q
python 06_Pipelines/lexicon_audit.py
python 06_Pipelines/regenerate_corpus.py --check
python validation/compiler_audit/audit_current_corpus.py --output /tmp/zfd-audit.json
```

The [JSON receipt](RESULTS_2026-11-23.json) includes input SHA-256 hashes,
per-identifier statistics, complete by-folio counts for the selected stems,
rose-token decompositions and the all-page comparison result. A plain-text
[continuation](CONTINUATION.md) is supplied separately for the original comment.

## Version and verification receipts

The machine-readable receipt identifies the checked base and input hashes.
The integration includes the November transcription fixes and the recipe
verification correction described here. Test and gate receipts are stored
alongside this audit; the [integrated audit](INTEGRATION_2026-11-23.md) is the
current entry point across the three processing paths.
