# Image aligned gold annotation protocol

## Unit of annotation

Annotate directly on registered pixels. Every region, line, and grapheme polygon
must carry the exact page ID and image SHA 256. Preserve uncertain boundaries and
unknown glyphs explicitly. Do not consult inherited Voynich text during primary
annotation.

## Diplomatic labels

Record the visible grapheme form without expansion. Use an opaque glyph class
when palaeographic identity is unresolved. Expansions, normalized readings, and
language analysis are later layers. Ligatures and abbreviation marks keep their
own polygons and alternatives.

## Review

Each gold row requires an annotator ID. Held-out evaluation rows require an
independent reviewer and adjudicator. Disagreements retain both observations and
the adjudication rationale. Expert uncertainty is a valid final state.

## Leakage resistant splits

Split by lineage root, manuscript, hand, and style. Exact duplicates, crops,
adjacent derivatives, and pages from the same hand cannot cross train, validation,
or held-out boundaries. Synthetic material stays in a separate report.

Every metric run requires an explicit `LineageAuthorityRecord` inventory for
both training assets and evaluated gold assets. Each authority row records the
record ID, corpus role, manuscript, hand, style, exact source SHA 256,
derivative SHA 256, lineage root, and assigned split. Gold sequence and
segmentation rows must match their authority row field for field. Empty or
missing authority blocks an accuracy claim. Supplementary hash lists cannot
stand in for this inventory.

The metric gate rejects any exact hash, derivative hash, lineage root,
manuscript, or hand that crosses split assignments. It also rejects missing
prediction rows and prediction hashes that do not align with the gold pixels.

## Required reporting

- region and line segmentation precision, recall, and IoU
- character error rate and sequence error
- grapheme confusion counts
- unknown rejection true positive, false positive, and false negative counts
- expected calibration error
- results by manuscript, hand, and style
- the exact gold and prediction receipt hashes

Character errors use one deterministic minimum edit alignment. Insertions have
the reference class `<INSERTION>` and deletions have the predicted class
`<DELETION>` in the confusion table. Unknown rejection pairs each gold grapheme
with the prediction selected by that alignment, so an earlier insertion or
deletion cannot shift later scores onto the wrong grapheme.

Without adjudicated gold, the metrics status is `not_measured`.
