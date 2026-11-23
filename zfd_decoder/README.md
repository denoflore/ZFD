# ZFD folio reader

Read a labelled manuscript scan beside its EVA transcription, ZFD expansion,
proposed Croatian forms and English glosses. Each word opens its source and
parser record. The reader is a standalone HTML file; its manuscript image
loads from Yale's IIIF service.

## Generate a reader

Python 3.10 or later is sufficient for the reader; it uses the standard library.
From the repository root:

```bash
python zfd_decoder/main.py f88r --out /tmp/zfd-reader
```

Open `/tmp/zfd-reader/f88r_reader.html` in a browser. Keep the four generated
files together so its export links work:

| File | Contents |
|---|---|
| `f88r_reader.html` | Scan, four reading layers, search, match filters and expandable token evidence |
| `f88r_decode.json` | Complete tokens, diagnostics, source identity, configuration and image references |
| `f88r_table.csv` | One row per token, complete token JSON and run metadata in the first row |
| `f88r_report.md` | Four reading layers, token records and complete run metadata |

The text and token evidence work offline. An unavailable image leaves a clear
fallback and the source links. GitHub displays HTML source rather than running
the reader, so download an example's four files or generate them locally.

Committed examples: [f88r reader](examples/f88r_reader.html),
[f88r JSON](examples/f88r_decode.json), [f88r CSV](examples/f88r_table.csv),
[f88r Markdown](examples/f88r_report.md), and the foldout-panel
[f102r1 reader](examples/f102r1_reader.html) with its
[JSON](examples/f102r1_decode.json), [CSV](examples/f102r1_table.csv) and
[Markdown](examples/f102r1_report.md).

## Sources and panels

```bash
python zfd_decoder/main.py --list
python zfd_decoder/main.py f102r1 --source lsi --out /tmp/zfd-panel
python zfd_decoder/main.py f88r /path/to/input.txt --out /tmp/custom-reader
```

`--source auto`, the default, uses an exact `voynich_data/raw_eva/` file when
one exists, otherwise the exact LSI identifier with one preferred transcriber
per record. `raw` and `lsi` select explicitly. A panel is never silently
replaced with its parent page's text. An explicit UTF-8 input file, including
a UTF-8 BOM, is supported through the second positional argument.

There are **244 source identifiers: 201 exact raw files and 43 LSI-only IDs**.
They include 18 whole-page aliases alongside component panels. This is a
source inventory, not a count of non-overlapping physical manuscript pages.
Raw-file token IDs retain physical input line numbers. LSI exports also record
the original line/transcriber ID for each selected record.

Drawing markers such as `<->` reach the shared tokenizer and remain word
boundaries. On f102r1, this retains **109 tokens in 17 selected records**;
the older recipe extractor joins five of those boundaries and yields 104.
That separate recipe path and its published denominators are unchanged.

Images use the repository's labelled Yale map. A foldout may have a partial
or composite scan, and some sides have multiple references. The reader keeps
every matching reference with its actual label. A panel ID refers to a scan
of its parent side; no panel crop or word coordinates are inferred. For
example, f102r1 links to the scan labelled **“101v (part) and 102r”**. Image-only
f85v and f86r have references but no exact text source for this decoder.

## Reading the match labels

| Label | Recorded parser operation |
|---|---|
| Whole word | Complete word matched a CSV entry before further splitting |
| Exact stem | Complete expanded stem matched a CSV entry |
| Stem + suffix | A recognised suffix was removed and the remaining stem matched exactly |
| Partial | Only part of the expanded stem matched a CSV entry |
| Compound | The compound analyser proposed a decomposition; its parts and scores are retained |
| Unresolved | No accepted dictionary or compound match |

ZFD preserves the complete expanded stem. Croatian and English partial
readings retain unmatched pieces in brackets. For example, `orald` carries
the `oral` dictionary row and renders as Croatian `oralno[d]` and English
`by mouth [d]`. The `d` has not disappeared into an apparently complete
translation. Compound proposals also retain their parts and unmatched text;
they do not acquire invented Croatian dictionary equivalents.

Token evidence records the matched form, Croatian value, category, status,
source, expanded stem, unmatched prefix/suffix, operators and rewrites.
The displayed score is the existing additive parser score. A dictionary
entry's historical `CONFIRMED` status and a high parser score do not measure
independently established translation correctness.

On f88r's **150 tokens**, the shipping reader records **26 whole-word,
14 exact-stem, six stem-plus-suffix, 81 partial and 23 compound** matches.
The legacy known-stem ratio is 100% here; those separate match counts describe
what actually produced it.

## Explicit lexicon profiles

| Profile | CSV rows | Distinct forms | Compound analysis by default |
|---|---:|---:|---|
| `shipping` | 212 | 208 | On |
| `frozen` | 92 | 89 | Off |
| `branch-candidates` | 185 | 182 | Off |

```bash
python zfd_decoder/main.py f88r --profile frozen --out /tmp/f88r-frozen
python zfd_decoder/main.py f88r --profile branch-candidates --out /tmp/f88r-candidates
python zfd_decoder/main.py f88r --lexicon /path/to/lexicon.csv --compound off --out /tmp/f88r-custom
```

All profiles use the current parser. `frozen` freezes the older CSV and disables
compound analysis; it does not run the historical implementation.
`branch-candidates` exposes the retained branch CSV without changing the
shipping lexicon. [Its reconciliation record](data/candidates/README.md)
preserves 89 forms absent from shipping and all differing shared rows.
For duplicate forms the existing last-CSV-row-wins policy is recorded in every
export. `--compound on|off` overrides the selected profile. Custom CSVs use
shipping compound behaviour unless explicitly overridden.

Each run records its source and selected-text hashes, lexicon hash, exact
row/form counts, data and code hashes, image-map hashes and compound setting.
The CSV's `run_metadata_json` is populated only on its first token row;
`token_json` preserves each complete token record.

## Verification and reproduction

```bash
python -m pytest -q
python validation/folio_reader/audit_reader.py --output /tmp/zfd-reader-audit.json
python zfd_decoder/main.py f88r --out zfd_decoder/examples
python zfd_decoder/main.py f102r1 --out zfd_decoder/examples
```

The acceptance audit decodes all 244 IDs with the shipping profile, checks
token accounting and LSI line identities, and records every source hash and
image reference. It reports **49,359 tokens**, including aliases, with labelled
image references for **244/244 IDs**. These are the CSV reader's own source
and processing counts, separate from the recipe decoder's 48,379-token union.

[Completion record](../validation/folio_reader/COMPLETION_2026-11-23.md)
| [Full acceptance JSON](../validation/folio_reader/ACCEPTANCE_2026-11-23.json)
| [Current validation controls](../validation/blind_decode_test/results_v3/V3_DUAL_CONFIG_REPORT.md)
