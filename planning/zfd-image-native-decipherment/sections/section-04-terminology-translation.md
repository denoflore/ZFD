# section-04-terminology-translation: Terminology translation

> Self-contained, context-isolated build unit. An implementer can execute this
> file alone. The section manifest records its dependency position.

## Context

This unit records historical interpretation without collapsing observation,
reconstruction, normalization, and translation into one string. It supports
fifteenth century Croatian Glagolitic angular, office cursive, shorthand and
longhand comparanda, period Latin controls, modern Croatian, and English. It
retains alternatives and unresolved terms whenever dated evidence cannot choose.

## Inputs

- Section 01 registered comparative sources with date, hand/style, rights,
  stable locator, checksum, control group, and evidentiary role.
- Section 03 parity safe diplomatic grapheme and sequence records whose pixel
  parent, geometry, OCR alternatives, and review state are fixed.
- Primary or authoritative passage records containing exact source ID, date
  range, folio/page/entry locator, observed spelling, script, language, context,
  transcription responsibility, and source checksum.
- Independent fields for diplomatic form, expanded form, normalized historical
  reading, reconstructed form, Latin parallel, modern Croatian equivalent,
  literal English, fluent English, alternatives, confidence, and speculation.

## Outputs

- `TerminologyRecord` validation that requires dated, locatable evidence and
  preserves observed and reconstructed forms separately.
- Per-region interpretation and translation records joined to the exact OCR
  record and image geometry, with reviewer and adjudicator states.
- Comparative evidence tables separated by script, hand, region, century,
  genre, and control role. Latin parallels cannot silently become Croatian
  readings, and modern equivalents cannot become historical spellings.
- Modern Croatian, literal English, and fluent English outputs only where the
  preceding layers exist. All other rows carry explicit alternatives or an
  unresolved disposition.

## Tests

- Missing source date, passage locator, stable locator, or source checksum fails
  a terminology record.
- A semantic reading without an exact diplomatic parent fails.
- A translation whose page or region hash differs from its OCR parent fails.
- OCR confidence cannot be copied into terminology or semantic confidence.
- A speculative reconstruction presented as an observed form fails.
- Any page called translated without modern Croatian, both English layers, and
  required adjudication fails Section 03 parity.

## Dependencies

Sections 01 and 03.
