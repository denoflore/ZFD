# mirror review - zfd-image-native-decipherment

> Independent adversarial read. Paste the reviewer's findings here, then
> reconcile them in integration-notes.md (accept + change, or reject + reason).

Historical-source and terminology review performed on 2026-07-28. Verdict:
source registration and terminology validation contain claim-authority defects.

## Critical findings

1. A real Mavrov source record combined with invented passage hashes, reviewer
   identities, confidence, and terminology text passed `validate_terminology`.
   Evidence objects were self-asserted and did not join to a registered asset,
   source image, OCR record, diplomatic record, reviewer, or adjudication.
2. Comparative assets accepted any training disposition beginning with `train`.
   This bypassed source-level quarantine and lacked a mandatory join to the source
   register, hand lineage, line lineage, and split authority.

## Source corrections

1. The GAMS manuscript is Borg. L. VII. 9, IIIF identifier Borg.ill.9. Its origin
   is unknown. The language is predominantly Old Croatian with some Croatian
   Church Slavonic and traces of Old Czech. `Vatican Slavic 73` identifies a
   different manuscript and must be removed.
2. Petrisov zbornik contains Croatian with Chakavian, Kajkavian, and Old Slavonic
   elements. It is book cursive in three unattributed hands.
3. Mavrov's 1460 formal Baromic hand and Jure's 1471 calendar addition require
   separate bounded records or asset-level dates.
4. Istarski razvod is office cursive according to STIN. The Vinodolski longhand
   label lacks support and must remain unresolved.
5. HAZU IV d 56 is old or transitional semi-uncial, Croatian Chakavian with a
   limited Church Slavonic component. HAZU IV d 55 combines formal Glagolitic,
   cursive Glagolitic, and Latin and is dated 1401 to 1500. The unsupported IV a
   48 two-hand assertion must be removed.

## Authority sources used for correction

- GAMS TEI manuscript description for Borg. L. VII. 9
- STIN book-cursive and office-cursive palaeography pages
- the medical manuscript study at Hrčak
- HAZU archive access records
- the National and University Library Mavrov IIIF manifest

VERIFY must remain open until these facts and joins are executable validator
requirements, with the current zero training-ready state preserved.
