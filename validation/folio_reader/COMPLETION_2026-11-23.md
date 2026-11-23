# Folio images and Croatian reader completion

## Completed scope

The retained `claude/zfd-folio-images-croatian-OrR8L` branch ended at
`47ddb6977337bec64de843f923ae6f79b0bf12d1`. This completion adapts its useful
CLI, lexicon and Croatian-rendering work to main at
`4f542fe0f29d967c5775ca7fa877dd72eebae8e7`, after the compiler audit in PR #8.

The result is an executable folio reader with labelled Yale image references,
four aligned reading layers, searchable token records, match-type filters,
responsive layout and JSON, CSV and Markdown exports. All exports retain
source, configuration and parser provenance. The two committed examples are
[f88r](../../zfd_decoder/examples/f88r_reader.html) and
[f102r1](../../zfd_decoder/examples/f102r1_reader.html).

## Corrected reading behaviour

The parser now carries the matched CSV row through rendering instead of
looking up a shortened stem again. The original `stem` compatibility field,
parser decisions and additive scores remain available. `stem_surface` retains
all expanded characters, including unmatched material previously dropped by
ZFD rendering. Croatian and English output bracket that material.

For example, `orald` keeps the complete ZFD surface and renders the matched
`oral` entry as `oralno[d]` / `by mouth [d]`. Compound proposals retain their
decomposition records and score; they receive no invented Croatian entry.
Exact, suffix-derived, partial, compound and unresolved cases have separate
match types. Partial and suffix-derived dictionary lookups require at least
two characters. Data files are read explicitly as UTF-8, including on Windows.

The shipping f88r example has 150 tokens: 26 whole-word, 14 exact-stem,
six stem-plus-suffix, 81 partial and 23 compound matches. The legacy 100%
known-stem ratio on this folio includes the partial and compound cases.

## Complete source and image-reference accounting

[ACCEPTANCE_2026-11-23.json](ACCEPTANCE_2026-11-23.json) records every identifier,
source/text hash, match count and image ID under the shipping profile.

| Measurement | Result |
|---|---:|
| Exact text-source identifiers decoded | 244 |
| Exact raw files selected | 201 |
| Additional preferred-LSI identifiers | 43 |
| Identifiers with labelled scan references | 244 |
| Reader tokens, including whole-page/panel overlap | 49,359 |
| Whole-word matches | 4,452 |
| Exact-stem matches | 7,593 |
| Stem-plus-suffix matches | 1,424 |
| Partial matches | 22,338 |
| Compound proposals | 13,516 |
| Unresolved tokens | 36 |
| Source/accounting failures | 0 |

The inventory retains 18 whole-page aliases alongside component panels.
These are source identifiers, not 244 independent physical pages. The reader
uses the CSV pipeline and preserves drawing boundaries in the selected LSI
records; its 49,359-token count is separate from the recipe decoder's
48,379-token canonical union and 36,959-token preferred-LSI comparison.

The f102r1 example selects 17 original LSI records with 109 tokens. Keeping
`<->` until shared tokenization preserves five word boundaries removed by the
older recipe extraction helper. Exports retain each selected record's
original line/transcriber ID. Explicit source selection fails when the exact
requested identifier is unavailable, instead of substituting another panel.

Image references preserve the descriptive map's exact labels, multiple
references and partial/composite scope. For example, f102r1 references
**“101v (part) and 102r”**, image 1006251. No panel crop or token coordinates
are invented. All 244 IDs resolve in the maps; browser acceptance additionally
checked the f88r image loading from Yale at 1,000 pixels wide.

The f85v stub had linked to image 1006219, labelled f80v. Its metadata and
transcription document now link to 1006231, labelled **“85v and 86r (foldout)”**.
Only the image reference and explanatory label changed. f85v/f86r remain
image-only sides without an exact source for this text reader.

## Preserved lexicon work

The shipping CSV is unchanged: **212 rows / 208 distinct forms**, SHA-256
`68fb55f2b4c7725b300cab5c438d7abbc25837f5a6b8a499747193241423741b`.
The frozen CSV remains **92 rows / 89 forms**.

The old branch CSV is archived byte for byte as
[`lexicon_v2_folio_branch_2026-02-04.csv`](../../zfd_decoder/data/candidates/lexicon_v2_folio_branch_2026-02-04.csv),
with **185 rows / 182 forms**, SHA-256
`9c49cac6fc1add3e30b96ff983e6d9c35cfb79d05d9d09af19c00a0b0fce067e`.
The [reconciliation JSON](../../zfd_decoder/data/candidates/FOLIO_BRANCH_RECONCILIATION.json)
retains all 89 branch-only forms, 115 shipping-only forms and complete rows for
33 shared forms whose data differ. Historical source statuses are preserved.

`--profile branch-candidates` makes the archive executable with the current
parser and compound analysis disabled by default. It leaves the shipping
profile unchanged. The original branch history is reconciled as a parent
of the completion, preserving ancestry as well as the candidate data.

## Verification

- **97 tests pass**, covering the existing compiler/recipe checks and 19 new
  reader, export and match-provenance regressions. The one warning comes from
  the installed anyio pytest plugin. [Test receipt](TEST_RECEIPT.txt).
- The recipe gate decodes all 244 recipe identifiers twice and confirms every
  committed recipe and the summary byte for byte. Its count remains
  **46,578 / 48,379**. [Gate receipt](RECIPE_GATE_RECEIPT.txt).
- The full transcription JSONL remains byte-identical, SHA-256
  `bad16667165237add812481525d3e0c130692a26d15035aef534bb1062e009bc`.
- The refreshed dual-configuration v3 report retains **5/5 frozen** and
  **4/5 shipping**, with the hierarchy true in both. Shipping f23v still fails
  the declared z-score threshold against character-shuffling. Numerical
  results are unchanged; the receipt identifies the current code hashes.
- The refreshed robustness result remains **NON-DISCRIMINATING**. Layer
  perturbation retains operator ratios **3.03 real / 12.92 shuffled** and no
  layer classified as independent manuscript evidence.
- Native Chromium acceptance on the exact committed f88r HTML verifies
  successful Yale image loading, token-ID search, 81 partial-filter results,
  empty-filter behaviour, expansion of all 150 token records, mobile layout
  without horizontal overflow, and the blocked-image fallback, with no page
  script errors. Desktop and mobile screenshots were also inspected.
  [Browser receipt](UI_RECEIPT_2026-11-23.json).

## Reproduce

```bash
python -m pytest -q
python validation/folio_reader/audit_reader.py --output /tmp/zfd-reader-audit.json
python zfd_decoder/main.py f88r --out zfd_decoder/examples
python zfd_decoder/main.py f102r1 --out zfd_decoder/examples
python 06_Pipelines/regenerate_corpus.py --check
python validation/blind_decode_test/run_test_v3.py
python validation/transcription_robustness/run_robustness.py
python validation/transcription_robustness/run_layer_stratified.py
```

Optional UI acceptance requires Playwright and its Chromium browser:

```bash
python validation/folio_reader/verify_reader_ui.py zfd_decoder/examples/f88r_reader.html --output /tmp/zfd-reader-ui.json
```

The reader itself requires no browser-automation dependency. Text and token
records remain readable if JavaScript or the remote image is unavailable.
