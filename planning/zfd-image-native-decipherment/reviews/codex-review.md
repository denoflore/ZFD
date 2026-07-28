# codex review - zfd-image-native-decipherment

> Independent adversarial read. Paste the reviewer's findings here, then
> reconcile them in integration-notes.md (accept + change, or reject + reason).

Review performed against the staged branch and current v2 corpus receipts on
2026-07-28. Verdict: VERIFY must remain open.

## Critical findings

1. Pixel acquisition reused an existing `<iiif_id>.jpg` without proving that its
   bytes matched a registered page hash. Receipt freshness also failed to rehash
   current source pixels. A changed source image therefore left validation green.
2. A fabricated set of minimal self-hashed page and region rows could authorize
   `complete_translation`. The claim gate did not call the seven-layer parity
   validator or bind the records to the canonical 210-page authority.
3. The default clean-clone test invoked model validation with `require_cache=True`
   even though the model cache is intentionally ignored.
4. The inherited-transcription boundary test scanned only four primary modules.
   CLI, receipt, I/O, and model paths could acquire a forbidden dependency without
   failing that gate.

## High-priority findings

1. Metric lineage defaults were permissive and the confusion and calibration
   accounting paired sequences positionally after insertions and deletions.
2. Publication scanning missed direct completion and provenance formulations such
   as `fully translated` and `provenance is confirmed`.
3. The v2 OCR page receipt ledger is 1,170,540,526 bytes because 4,953,273 rejected
   component rows are embedded in one JSONL file. Freeze and validation materialize
   the ledger in memory. This is not a portable evidence package.
4. Documentation showed a freeze output path capable of overwriting the retained
   v1 archive.
5. The whole-corpus Kraken comparison was linked to stale v1 receipts. Rabus had
   one correctly quarantined probe and no corpus evaluation.

## Required disposition

Repair each critical and high-priority finding, rerun the whole test and validator
surface from clean declared environments, regenerate the current receipts after
the implementation hash changes, and keep OCR, translation, provenance, and
accuracy claims blocked until their direct evidence exists.

## Second adversarial pass

After the first repairs, executable synthetic authorities exposed four further
false-positive paths:

1. A chain with one conserved unknown grapheme and a resolved translation passed.
2. Malformed polygon geometry, nonhash passage evidence, invalid date types,
   arbitrary locators, and internally inconsistent source or reviewer identities
   passed after resealing.
3. One translated region plus 209 self-declared nontext pages produced an allowed
   complete-manuscript claim.
4. A parity-shaped receipt could satisfy the separately named expert adjudication
   requirement. Several JSON-representable list and null types also raised runtime
   exceptions instead of returning blocked reasons.

These findings are critical. The claim gate requires a code-pinned Yale page
identity, registered page layers for all 210 surfaces, distinct typed receipt
validators, explicit unknown rejection at translation confirmation, strict
polygon and historical field validation, internal authority identity checks,
safe type handling, and pixel-bound independent nontext adjudication.
