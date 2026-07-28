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

## Executable visual form task and review receipts

`zfd-review create-task` accepts a frozen Stage A authority and a validated page
local visual receipt. It emits one `zfd.line_visual_form_review_task.v1` JSON file
and one lossless line crop. The task binds the page and image hash, line and
region geometry, every candidate component, both upstream receipt chains, and
the raw crop pixels. Its split is unassigned. It contains no label and carries
`sequence_authority_status=not_established`.

An observation draft covers every task component through a visible glyph,
merge, split, nontext disposition, or explicit unresolved disposition. Sealing
the draft rehashes the task crop and every proposed glyph span. The permitted
first pass class is a task local opaque form such as `opaque:0001`. A script
character, expanded reading, language assignment, or translation cannot enter
this receipt.

Two sealed observations use the roles `primary_annotator` and
`independent_reviewer`. `zfd-review seal-adjudication` requires a third distinct
identity, keeps both source observations, and records coded rationales. Every
source observation glyph must be cited by an adjudicated visual span or receive
an explicit controlled disposition. Grouped source references retain one to
many merge and split disagreements. Even a
fully resolved opaque sequence has `semantic_class_authority_count=0`,
`authority_promotion_eligible=false`,
`diplomatic_sequence_authority_eligible=false`, and
`accuracy_claim_allowed=false`. Promotion requires a separate byte bound
diplomatic label authority and leakage resistant split.

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
