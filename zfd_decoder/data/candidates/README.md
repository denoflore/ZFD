# Retained folio-branch lexicon

`lexicon_v2_folio_branch_2026-02-04.csv` preserves the exact bytes of
`zfd_decoder/data/lexicon_v2.csv` at commit
`47ddb6977337bec64de843f923ae6f79b0bf12d1`, the retained
`claude/zfd-folio-images-croatian-OrR8L` branch tip before completion.

Its SHA-256 is
`9c49cac6fc1add3e30b96ff983e6d9c35cfb79d05d9d09af19c00a0b0fce067e`.
The file has **185 rows and 182 distinct forms**, correcting the historical
181-form headline. The shipping CSV has **212 rows and 208 distinct forms**.

[FOLIO_BRANCH_RECONCILIATION.json](FOLIO_BRANCH_RECONCILIATION.json) records:

- **89 forms** present only in the retained branch CSV;
- **115 forms** present only in shipping;
- **33 shared forms** whose row data differ, with both sets of complete rows.

The 89 branch-only forms include 77 entries marked `MISCELLANY` and 12 marked
`CONFIRMED` in that historical file. Those are retained source labels, not new
validation decisions. Differences include semantic/category changes, so a
blind union would silently choose between incompatible entries.

Use the archived candidates explicitly:

```bash
python zfd_decoder/main.py f88r --profile branch-candidates --out /tmp/f88r-candidates
```

This profile uses the current parser with compound analysis off by default.
It preserves the old branch's candidate work for inspection and comparison
while leaving the shipping and frozen profiles unchanged. The original CSV,
full reconciliation and branch history remain available after branch retirement.

The shipping CSV's unchanged SHA-256 is
`68fb55f2b4c7725b300cab5c438d7abbc25837f5a6b8a499747193241423741b`.
