# Provenance and translation evidence status

## Current verdict

The broad Croatian Glagolitic hypothesis is a testable possibility. A specific
Ragusan or Dubrovnik origin is unproven. Existing commodity overlap and generated
decoder coverage do not identify a city, institution, author, or language.

The present repository contains legacy generated readings and translations.
Those records have not yet passed page pixel to region to OCR to diplomatic text
to terminology to translation parity. Complete translation remains blocked.

## Registered comparanda

- [Petrisov zbornik, 1468, NSK R 4001](https://digitalna.nsk.hr/admin/api.php?storage=iiif.m&ri=15967). The IIIF manifest identifies Croatian,
  Glagolitic script, and public domain rights. All 703 saved files map to 703
  canvases. STIN classifies Petrisov as book cursive. Its Croatian contains
  Chakavian, Kajkavian, and Old Slavonic elements across three unattributed
  hands. Page and line hand boundaries remain unresolved, so the assets stay
  quarantined.
- [GAMS Zrcalo, 1445](https://gams.uni-graz.at/context%3Aspeculum), Borg. L. VII. 9, represented in the Vatican IIIF service
  as Borg.ill.9. This is a dated angular Glagolitic book hand with TEI and
  facsimile access. The language is mostly Old Croatian with Croatian Church
  Slavonic and Old Czech elements. GAMS reports later transcription on Krk,
  while the manuscript origin remains unresolved. All 162 selected facsimiles
  have saved canvas mappings. Edition and image rights are tracked separately,
  and these images remain study only.
- [Istarski razvod, Kršan copy of 1546, NSK R 3677](https://digitalna.nsk.hr/admin/api.php?storage=iiif.m&ri=14616). It is a later control whose
  source documents span 1275 to 1395. STIN classifies this copy as office
  cursive. It cannot stand in for a fifteenth century hand.
- [Vinodolski zakon, early sixteenth century copy, NSK R 4080](https://digitalna.nsk.hr/admin/api.php?storage=iiif.m&ri=11569). It is a later
  control with an unresolved hand and cannot be dated to the 1288 original
  text.
- Misal kneza Novaka, 1368. The source carries contractual restrictions. The
  703 local files bearing this label are byte identical to the 703 Petrisov
  files and use the same R 4001 image identifiers. They are misidentified and
  excluded.
- [HAZU IV d 56](https://stin.hr/zgombicev-zbornik/hrvatskoglagoljski-medicinski-tekstovi/) is a late fourteenth century old or transitional semi-uncial
  medical witness in Croatian Chakavian with limited Church Slavonic elements.
  HAZU IV d 55 is dated 1401 to 1500 and contains formal and cursive Glagolitic
  plus Latin script. Image and reproduction access is unresolved while the HAZU
  archive reports its holdings unavailable during relocation.
- [Zbornik duhovnog štiva, HAZU IV a 48](https://stin.hr/zgombicev-zbornik/knjiski-kurziv/) is a late fifteenth century Croatian
  Glagolitic book cursive witness. STIN supplies the classification and
  shelfmark. Registered manuscript pixels, page mapping, and reproduction
  authorization remain absent, so it is reference only. No hand count is
  asserted.
- [Mavrov brevijar, NSK R 7822](https://digitalna.nsk.hr/admin/api.php?storage=iiif.m&ri=16161) is a public domain Croatian Glagolitic manuscript
  with a formal layer written by Blaž Baromić in 1460 and a calendar addition
  dated 1471. The 848 acquired files map to official canvases, while those two
  scribal layers have not been mapped to exact canvases. The whole source is
  therefore registered as 1460 to 1471 and remains quarantined pending hand
  boundaries and page or line level training lineage.
- [Frašćić Psalter, 1463, ÖNB Cod. slav. 77](https://data.onb.ac.at/rec/AC14377621)
  supplies 278 official canvases written by Petar Frašćić at Lindar in Croatian
  Church Slavonic semi-uncial. It is a dated longhand control. Its angular and
  cursive status are not asserted, no shorthand evidence is present, and all
  pixels remain quarantined pending hand boundaries, lineage, and resolution of
  the provider reuse terms because the IIIF manifest supplies no rights URI.
- [Berčić 6, 1460](https://nlr.ru/manuscripts/RA1527/elektronnyiy-katalog?ab=8AB79B29-8EC4-48ED-825E-D59299230ADA)
  and [Berčić 7, 1472](https://nlr.ru/manuscripts/RA1527/elektronnyiy-katalog?ab=361033B1-E34B-4752-A039-99E72655E014)
  are exact dated wills classified by the National Library of Russia as
  Glagolitic cursive. Their exhibition images are personal, noncommercial
  reference material. They are the strongest registered direct cursive
  controls and remain outside training. Two local reference images are bound by
  receipt SHA 256
  `14b26222ab01e09fdba6b65108389e6796809e63e9b55560e275e3d8a8cf22e2`
  under
  `F:\Dropbox\0 ZFD\00_GM\NLR_Bercic_cursive_wills_1460_1472_20260728`.
- [Hrvoje Missal, 1403 to 1404](https://digitalna.nsk.hr/admin/api.php?storage=iiif.m&ri=19404)
  supplies 538 official canvases of Butko's formal Glagolitic hand. Contractual
  restrictions on the digital copy keep it reference only.
- [Bodleian MS Canon. Liturg. 414](https://digital.bodleian.ox.ac.uk/objects/afd9b149-b484-4ed8-ac44-4c66083b8225/)
  supplies 144 CC BY-NC canvases. Its fifteenth century date and probable
  Dalmatian origin carry catalogue question marks, and its hand subtype remains
  unresolved. It is a book and abbreviation control, not a cursive training
  corpus.
- *Incipit Antidotarium Nicolai*, Venice, Nicolaus Jenson, 1471, is registered as
  a separate Latin print control. The Library of Congress copy has 94 scan
  canvases and is incomplete. It cannot supply the absent *Quid pro quo* or
  *Synonima* sections and cannot train a Glagolitic recognizer.

## Provenance falsifiers still required

- image native grapheme evidence that survives held-out testing
- period Croatian and Latin terminology with exact passage locators
- comparable non-Ragusan Croatian, Venetian, northern Italian, and central
  European controls
- direct Ragusan administrative and pharmacy records with expected negative
  cities and genre controls
- independent palaeographic and historical review

The claim ledger in `data/image_native/claim_ledger.json` is the machine authority
for publication language.

## Comparative asset receipt

The committed comparative ledger inventories 2,948 local files, 2,105 unique
pixel payloads, and 1,991 saved canvas mappings. It records 703 cross source
duplicate groups between Petrisov and the folder labelled Novak, plus 70 exact
Istarski triplicate groups. Petrisov, GAMS Zrcalo, Mavrov, and Frašćić have saved
file to canvas mapping. Zero comparative assets are training ready. No evidence
for a separately attested fifteenth century Glagolitic shorthand system has been
registered.
