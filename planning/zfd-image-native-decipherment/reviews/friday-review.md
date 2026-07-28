# friday review - zfd-image-native-decipherment

> Independent adversarial read. Paste the reviewer's findings here, then
> reconcile them in integration-notes.md (accept + change, or reject + reason).

Independent corpus audit performed on the frozen v2 run on 2026-07-28. Verdict:
the pixel and geometry joins are internally consistent, while the evidence package
and downstream comparison bindings remain incomplete.

## Reproduced receipts

- 210 page images and 210 OCR page files rehashed with zero byte mismatches.
- Page IDs, source IDs, image hashes, OCR hashes, region IDs, and geometry joins
  reconciled with zero mismatches.
- 670 regions, 30,141 lines, and 356,739 grapheme candidates were present.
- All 356,739 grapheme candidates remained explicitly unknown and unrecognized.
- 4,953,273 rejected components plus the retained graphemes formed 5,310,012
  explicit component dispositions, with zero independently reproduced partition
  errors.
- 125 pages used provisional Cartesian segmentation. 85 pages require layout
  review. Curved and radial line geometry is absent.

## Blocking findings

1. The 1,170,540,526-byte page receipt ledger embeds all rejected components.
   Freezing and validation materialize it. The archive is exact and operationally
   nonportable.
2. Receipt validation did not independently rehash the live page pixels and OCR
   artifacts represented by each receipt.
3. The Kraken corpus comparison used stale v1 receipt authority.
4. Page parity had no production caller anchored to the canonical manifest and
   evidence authority.
5. Current v1 data files are untracked in the staged branch, so `checked in` and
   `committed` language is premature until a validated commit exists.

The run establishes complete provisional segmentation accounting. It establishes
no OCR character accuracy, diplomatic transcription, translation, script identity,
language identity, genre, or provenance.
