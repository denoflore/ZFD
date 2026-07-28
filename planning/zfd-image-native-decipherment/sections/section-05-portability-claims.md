# section-05-portability-claims: Portability claims

> Self-contained, context-isolated build unit. An implementer can execute this
> file alone. The section manifest records its dependency position.

## Context

This unit makes the package reproducible on clean Windows and aligns every public
statement with the machine claim ledger. It repairs the existing implicit system
encoding reads and mapper exit behaviour, documents exact commands, and keeps
legacy decoder output visibly quarantined from image native evidence.

## Inputs

- Root Python package metadata and a pinned Windows dependency file for Python
  3.13, pytest, OpenCV, NumPy, Pillow, and schema validation.
- Existing loaders in `zfd_decoder/src/compound.py`, `operators.py`, `gallows.py`,
  `suffixes.py`, and `stems.py`, plus remaining repository text reads found by
  the encoding audit.
- `scripts/test_mapper.py` and `scripts/zfd_mapper.py`.
- Section 03 claim decisions and Section 04 terminology status.
- Existing README, methodology, validation, and folio index publication claims.

## Outputs

- `pyproject.toml`, pinned requirements, pytest configuration, and documented
  commands for environment creation, tests, acquisition, OCR, validation, and
  claim inspection on Windows.
- Explicit UTF 8 encoding on all affected JSON, CSV, Markdown, and source reads
  and writes. Console output used by tests remains ASCII safe under cp1252.
- A mapper test runner that returns nonzero when any subtest fails and makes the
  Croatian pattern test contribute to that result.
- `docs/IMAGE_NATIVE_OCR.md`, `docs/EVIDENCE_BOUNDARY.md`,
  `docs/GOLD_ANNOTATION_PROTOCOL.md`, and `docs/PROVENANCE_STATUS.md`.
- Prominent publication status linking to the current claim ledger and removing
  unsupported completion, accuracy, and provenance certainty.

## Tests

- Tests must run without `PYTHONUTF8=1` on a cp1252 console.
- UTF 8 Croatian and Glagolitic fixtures must round trip through every loader.
- A forced mapper pattern failure must print `[FAIL]` and return nonzero.
- A clean environment install and the documented test command must succeed.
- Documentation claiming complete translation, measured OCR accuracy, or fixed
  Ragusan provenance fails while Section 03 blocks those claims.

## Dependencies

Sections 01 and 03.
