# Folio f102r1 Decode Report

Croatian renderings and English glosses are outputs of the ZFD parser. Parser scores are rule-based scores, not calibrated probabilities.

## Source, image and configuration

```json
{
  "folio": "f102r1",
  "diagnostics": {
    "total_tokens": 109,
    "operator_counts": {
      "da": 7,
      "otr": 4,
      "š": 10,
      "ko": 15,
      "ost": 6,
      "h": 6
    },
    "known_stems": 109,
    "unknown_stems": 0,
    "known_ratio": 1.0,
    "average_confidence": 0.553,
    "unknown_stem_list": [],
    "category_distribution": {
      "ingredient": 54,
      "latin_pharma": 1,
      "compound": 22,
      "preparation": 17,
      "grammar": 15
    },
    "miscellany_stems": 0,
    "match_type_counts": {
      "partial": 66,
      "whole_word": 7,
      "compound": 22,
      "exact_stem": 6,
      "suffix": 8
    },
    "validation": {
      "kost_present": false,
      "ol_present": true,
      "operators_found": true
    }
  },
  "source": {
    "kind": "lsi_preferred",
    "path": "02_Transcriptions/LSI_ivtff_0d.txt",
    "sha256": "3f3f2af18cde10efe75c582f49b07b651c3397022fcbfa5854fecc424c121afa",
    "selection": "One preferred transcriber per exact LSI record; raw drawing boundaries retained.",
    "transcriber_preference": [
      "H",
      "C",
      "F",
      "U",
      "D",
      "G",
      "J",
      "L",
      "M",
      "V",
      "X",
      "Z"
    ],
    "line_numbering": "selected LSI record sequence",
    "line_ids": {
      "1": "f102r1.1,@Lc;H",
      "2": "f102r1.7,@Lc;H",
      "3": "f102r1.12,@Lc;H",
      "4": "f102r1.2,@Lf;H",
      "5": "f102r1.3,@P0;H",
      "6": "f102r1.4,+P0;H",
      "7": "f102r1.5,+P0;H",
      "8": "f102r1.6,+P0;H",
      "9": "f102r1.8,@P0;H",
      "10": "f102r1.9,+P0;H",
      "11": "f102r1.10,+P0;H",
      "12": "f102r1.11,+P0;H",
      "13": "f102r1.13,@P0;H",
      "14": "f102r1.14,+P0;H",
      "15": "f102r1.15,+P0;H",
      "16": "f102r1.16,+P0;H",
      "17": "f102r1.17,+P0;H"
    },
    "text_sha256": "0443c68e6e9836be689189ab7266e53e746a111929d98da22cf67c42e904a2e9"
  },
  "configuration": {
    "reader_version": 1,
    "profile": "shipping",
    "lexicon_file": "zfd_decoder/data/lexicon_v2.csv",
    "lexicon_sha256": "68fb55f2b4c7725b300cab5c438d7abbc25837f5a6b8a499747193241423741b",
    "lexicon_rows": 212,
    "lexicon_unique_forms": 208,
    "duplicate_variants": 4,
    "duplicate_policy": "Last CSV row for a variant wins; overlapping entries are retained in the source file.",
    "compound_enabled": true,
    "data_sha256": {
      "zfd_decoder/data/gallows.json": "4b92a22ca5b34981e8382132a38cdf3bf757c03c7b4b2e5cc75461992fdc2c14",
      "zfd_decoder/data/mid_word.json": "befae478f26852dfa1dc5bca16992ee3cbced8a7890eb5a15e18a95ed5962a76",
      "zfd_decoder/data/operators.json": "9094d28efbf4f49f04e3b351484683cacc231afddcdedf712ea4e21ad0566e12",
      "zfd_decoder/data/suffixes.json": "31a0128c3dfb28f87cf78f8ecc14ec962b28c7e31ae720b5beb59f9e1241fde8",
      "zfd_decoder/data/unified_lexicon_v2.json": "ca4283c4fcf2c42f82e1b4658875fab67561166702115cdaa14446d11b664c29"
    },
    "code_sha256": {
      "06_Pipelines/complete_missing_folios.py": "2254af868619925d189fcecf261b65dfac1b2245406d7b3791ec178070fd379e",
      "zfd_decoder/main.py": "3335b799f10bc0baef93ba6db1ca35a66dd548e2949fc2d3f0d108a25b285265",
      "zfd_decoder/src/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "zfd_decoder/src/compound.py": "a30533277ad6fdfad1efe782617365950d1c15d3708dc043da7b35c38c668670",
      "zfd_decoder/src/folio_sources.py": "32cefa718799c18c2b10cccbbffaf36f95e533ef1f7605fe27362f22e6ea316b",
      "zfd_decoder/src/gallows.py": "da493003bbf8800f750bdb19531a92ae15ed9e3fd1dcc391f264a2a7f58b1b56",
      "zfd_decoder/src/operators.py": "b9cfc426174bac1dfe3acb32e509002fda3ad7f71cd08dfd163543fd7afb41c0",
      "zfd_decoder/src/output.py": "72ce03a8b2248970a8b2d073f4a320ebe382bedffe33118f27ac66567e8aa3b3",
      "zfd_decoder/src/pipeline.py": "e4eef80ef791b1677c2386f8f2b88ef23b61267d2d2d6d9cdf9ec5c14079ef9b",
      "zfd_decoder/src/stems.py": "c23d803fe87ca6ccb8d688d82407f91c499c8f1d3e37c9a202cde55ab03360e6",
      "zfd_decoder/src/suffixes.py": "8078d5c62cf7b65d341e48daae73aa4c3a3f364089c226d29855187fbf1f4ddf",
      "zfd_decoder/src/tokenizer.py": "7a2e0cb37c7df47ba80d9d05dbbfefe1ccb550bb80026cea268c8b1b3948f5f0"
    },
    "score_definition": "Additive parser score, not a probability of translation correctness."
  },
  "image": {
    "available": true,
    "folio": "f102r1",
    "base_folio": "f102r",
    "source_url": "https://collections.library.yale.edu/catalog/2002046",
    "references": [
      {
        "label": "101v (part) and 102r",
        "identifier": "1006251",
        "service_url": "https://collections.library.yale.edu/iiif/2/1006251",
        "image_url": "https://collections.library.yale.edu/iiif/2/1006251/full/1000,/0/default.jpg",
        "full_url": "https://collections.library.yale.edu/iiif/2/1006251/full/full/0/default.jpg",
        "in_root_map": false,
        "scope": "labelled partial or composite reference"
      }
    ],
    "mapping_sha256": {
      "folio_iiif_map.json": "0022e1fdab774e6deada3bb92009562590d5749ff072cec6e2ead9c189aeb3bc",
      "06_Pipelines/glagolitic_ocr/data/folio_iiif_map.json": "ac1e4e38d6d1db7d99ac5c4d1c8b78310d9f177766fd3340d02f760cfbd67726"
    },
    "identifier": "1006251",
    "label": "101v (part) and 102r",
    "image_url": "https://collections.library.yale.edu/iiif/2/1006251/full/1000,/0/default.jpg",
    "full_url": "https://collections.library.yale.edu/iiif/2/1006251/full/full/0/default.jpg",
    "scope": "labelled partial or composite reference",
    "note": "References preserve the source map labels. Panel IDs refer to their parent side; no panel crop or word coordinates are inferred. Multiple references are in image-ID order."
  }
}
```

## Image references

- [101v (part) and 102r](<https://collections.library.yale.edu/iiif/2/1006251/full/full/0/default.jpg>)

  Scope: labelled partial or composite reference

## Line-aligned reading

### f102r1.1,@Lc;H

| Layer | Text |
| --- | --- |
| EVA | dordod |
| ZFD | dordod |
| Croatian | \[d\]ulje\[d\]od |
| English gloss | \[d\] oil \[d\] |

| Token | Match | Matched form | Stem surface | Prefix residue | Suffix residue | Lexicon status | Parser score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| f102r1.1.1 | Partial | or | dord | d | d | CONFIRMED | 0.450 |

#### Complete token provenance

```json
[
  {
    "id": "f102r1.1.1",
    "eva": "dordod",
    "zfd": "dordod",
    "operator": null,
    "operator_type": null,
    "stem": "or",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": "od",
    "suffix_semantic": "completion",
    "expansion": "[RESIDUE:d][STEM:or=oil][RESIDUE:d][SUF:od=completion]",
    "croatian": "[d]ulje[d]od",
    "english": "[d] oil [d]",
    "confidence": 0.44999999999999996,
    "rewrites": [
      "suffix: od→od (completed)"
    ],
    "notes": [
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "or",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "dord",
    "unmatched_prefix": "d",
    "unmatched_suffix": "d",
    "compound_parts": []
  }
]
```

### f102r1.7,@Lc;H

| Layer | Text |
| --- | --- |
| EVA | orolaly |
| ZFD | orolaly |
| Croatian | oralno |
| English gloss | orally (adverb) |

| Token | Match | Matched form | Stem surface | Prefix residue | Suffix residue | Lexicon status | Parser score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| f102r1.2.1 | Whole word | orolaly | orolaly |  |  | CONFIRMED | 0.300 |

#### Complete token provenance

```json
[
  {
    "id": "f102r1.2.1",
    "eva": "orolaly",
    "zfd": "orolaly",
    "operator": null,
    "operator_type": null,
    "stem": "orolaly",
    "stem_known": true,
    "stem_gloss": "orally (adverb)",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[STEM:orolaly=orally (adverb)]",
    "croatian": "oralno",
    "english": "orally (adverb)",
    "confidence": 0.3,
    "rewrites": [],
    "notes": [
      "Stem: oral (CONFIRMED) [whole-word]"
    ],
    "match_type": "whole_word",
    "matched_form": "orolaly",
    "matched_croatian": "oralno",
    "matched_category": "latin_pharma",
    "matched_status": "CONFIRMED",
    "matched_source": "miscellany+voynich",
    "stem_surface": "orolaly",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": []
  }
]
```

### f102r1.12,@Lc;H

| Layer | Text |
| --- | --- |
| EVA | dardsh |
| ZFD | dardš |
| Croatian | da\[rdš\] |
| English gloss | dose \[rdš\] |

| Token | Match | Matched form | Stem surface | Prefix residue | Suffix residue | Lexicon status | Parser score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| f102r1.3.1 | Compound |  | rdš |  |  | CANDIDATE | 0.600 |

#### Complete token provenance

```json
[
  {
    "id": "f102r1.3.1",
    "eva": "dardsh",
    "zfd": "dardš",
    "operator": "da",
    "operator_type": "dative",
    "stem": "rdš",
    "stem_known": true,
    "stem_gloss": "Add soak",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:da][COMPOUND:rdš=Add soak]",
    "croatian": "da[rdš]",
    "english": "dose [rdš]",
    "confidence": 0.6,
    "rewrites": [
      "operator: da→da",
      "mid-word: sh→š"
    ],
    "notes": [
      "Operator dose/give/add (CONFIRMED)",
      "Compound: [dar=Add / Portion / Seed] d [sh=soak/infuse]",
      "Stem: compound (CANDIDATE)"
    ],
    "match_type": "compound",
    "matched_form": "",
    "matched_croatian": "",
    "matched_category": "compound",
    "matched_status": "CANDIDATE",
    "matched_source": "unified_lexicon_v2.json",
    "stem_surface": "rdš",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": [
      {
        "eva": "dar",
        "type": "stem",
        "gloss": "Add / Portion / Seed",
        "content": true
      },
      {
        "eva": "d",
        "type": "suffix_char",
        "gloss": "past/done",
        "content": false
      },
      {
        "eva": "sh",
        "type": "operator",
        "gloss": "soak/infuse",
        "content": true
      }
    ]
  }
]
```

### f102r1.2,@Lf;H

| Layer | Text |
| --- | --- |
| EVA | otodeeodor |
| ZFD | otrodeodor |
| Croatian | otr\[odeod\]ulje |
| English gloss | vessel \[odeod\] oil |

| Token | Match | Matched form | Stem surface | Prefix residue | Suffix residue | Lexicon status | Parser score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| f102r1.4.1 | Partial | or | odeodor | odeod |  | CONFIRMED | 0.650 |

#### Complete token provenance

```json
[
  {
    "id": "f102r1.4.1",
    "eva": "otodeeodor",
    "zfd": "otrodeodor",
    "operator": "otr",
    "operator_type": "vessel",
    "stem": "odeodor",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:otr][RESIDUE:odeod][STEM:or=oil]",
    "croatian": "otr[odeod]ulje",
    "english": "vessel [odeod] oil",
    "confidence": 0.6499999999999999,
    "rewrites": [
      "operator: ot→otr",
      "mid-word: ee→e"
    ],
    "notes": [
      "Operator vessel/container (CONFIRMED)",
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "or",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "odeodor",
    "unmatched_prefix": "odeod",
    "unmatched_suffix": "",
    "compound_parts": []
  }
]
```

### f102r1.3,@P0;H

| Layer | Text |
| --- | --- |
| EVA | polaiin shocthy qoteol loiiin oteeor cpheodar sholdaiin |
| ZFD | plolain šoctrrhi kotreol loiin otreor cplheodar šoldain |
| Croatian | \[pl\]ulje\[ai\]n š\[o\]smjesa\[h\]i ko\[tre\]ulje \[loiin\] otr\[e\]ulje \[cpl\]ono što\[d\]ar šulje\[dai\]n |
| English gloss | \[pl\] oil \[ai\] with \[o\] compound mixture \[h\] which \[tre\] oil \[loiin\] vessel \[e\] oil \[cpl\] that which/the one \[d\] with oil \[dai\] |

| Token | Match | Matched form | Stem surface | Prefix residue | Suffix residue | Lexicon status | Parser score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| f102r1.5.1 | Partial | ol | plolai | pl | ai | CONFIRMED | 0.750 |
| f102r1.5.2 | Partial | ctrr | octrrh | o | h | CANDIDATE | 0.850 |
| f102r1.5.3 | Partial | ol | treol | tre |  | CONFIRMED | 0.750 |
| f102r1.5.4 | Compound |  | loiin |  |  | CANDIDATE | 0.350 |
| f102r1.5.5 | Partial | or | eor | e |  | CONFIRMED | 0.650 |
| f102r1.5.6 | Partial | heo | cplheod | cpl | d | CANDIDATE | 0.500 |
| f102r1.5.7 | Partial | ol | oldai |  | dai | CONFIRMED | 0.800 |

#### Complete token provenance

```json
[
  {
    "id": "f102r1.5.1",
    "eva": "polaiin",
    "zfd": "plolain",
    "operator": null,
    "operator_type": null,
    "stem": "ol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": "n",
    "suffix_semantic": "noun",
    "expansion": "[RESIDUE:pl][STEM:ol=oil][RESIDUE:ai][SUF:n=noun]",
    "croatian": "[pl]ulje[ai]n",
    "english": "[pl] oil [ai]",
    "confidence": 0.75,
    "rewrites": [
      "mid-word: ii→i",
      "gallows: p→pl (known stem)",
      "suffix: n→n (noun ending)"
    ],
    "notes": [
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "plolai",
    "unmatched_prefix": "pl",
    "unmatched_suffix": "ai",
    "compound_parts": []
  },
  {
    "id": "f102r1.5.2",
    "eva": "shocthy",
    "zfd": "šoctrrhi",
    "operator": "š",
    "operator_type": "comitative",
    "stem": "ctrr",
    "stem_known": true,
    "stem_gloss": "compound mixture",
    "suffix": "i",
    "suffix_semantic": "adjectival",
    "expansion": "[OP:š][RESIDUE:o][STEM:ctrr=compound mixture][RESIDUE:h][SUF:i=adjectival]",
    "croatian": "š[o]smjesa[h]i",
    "english": "with [o] compound mixture [h]",
    "confidence": 0.8500000000000001,
    "rewrites": [
      "operator: sh→š",
      "mid-word: ct→ctr",
      "gallows: t→tr (known stem)",
      "suffix: y→i (adjective marker)"
    ],
    "notes": [
      "Operator with/soak (CONFIRMED)",
      "Stem: ctrr (CANDIDATE)"
    ],
    "match_type": "partial",
    "matched_form": "ctrr",
    "matched_croatian": "smjesa",
    "matched_category": "preparation",
    "matched_status": "CANDIDATE",
    "matched_source": "morphology_analysis",
    "stem_surface": "octrrh",
    "unmatched_prefix": "o",
    "unmatched_suffix": "h",
    "compound_parts": []
  },
  {
    "id": "f102r1.5.3",
    "eva": "qoteol",
    "zfd": "kotreol",
    "operator": "ko",
    "operator_type": "relative",
    "stem": "treol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:ko][RESIDUE:tre][STEM:ol=oil]",
    "croatian": "ko[tre]ulje",
    "english": "which [tre] oil",
    "confidence": 0.75,
    "rewrites": [
      "operator: qo→ko",
      "gallows: t→tr (known stem)"
    ],
    "notes": [
      "Operator which/that/quantity (CONFIRMED)",
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "treol",
    "unmatched_prefix": "tre",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.5.4",
    "eva": "loiiin",
    "zfd": "loiin",
    "operator": null,
    "operator_type": null,
    "stem": "loiin",
    "stem_known": true,
    "stem_gloss": "The adjectival (variant) continuation",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[COMPOUND:loiin=The adjectival (variant) continuation]",
    "croatian": "[loiin]",
    "english": "[loiin]",
    "confidence": 0.35,
    "rewrites": [
      "mid-word: ii→i"
    ],
    "notes": [
      "Compound: [l=The / that (determin] o [i=adjectival (variant)] [iin=continuation]",
      "Stem: compound (CANDIDATE)"
    ],
    "match_type": "compound",
    "matched_form": "",
    "matched_croatian": "",
    "matched_category": "compound",
    "matched_status": "CANDIDATE",
    "matched_source": "unified_lexicon_v2.json",
    "stem_surface": "loiin",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": [
      {
        "eva": "l",
        "type": "operator",
        "gloss": "The / that (determiner)",
        "content": true
      },
      {
        "eva": "o",
        "type": "binding",
        "gloss": "binding vowel",
        "content": false
      },
      {
        "eva": "i",
        "type": "suffixe",
        "gloss": "adjectival (variant)",
        "content": true
      },
      {
        "eva": "iin",
        "type": "suffixe",
        "gloss": "continuation",
        "content": true
      }
    ]
  },
  {
    "id": "f102r1.5.5",
    "eva": "oteeor",
    "zfd": "otreor",
    "operator": "otr",
    "operator_type": "vessel",
    "stem": "eor",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:otr][RESIDUE:e][STEM:or=oil]",
    "croatian": "otr[e]ulje",
    "english": "vessel [e] oil",
    "confidence": 0.6499999999999999,
    "rewrites": [
      "operator: ot→otr",
      "mid-word: ee→e"
    ],
    "notes": [
      "Operator vessel/container (CONFIRMED)",
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "or",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "eor",
    "unmatched_prefix": "e",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.5.6",
    "eva": "cpheodar",
    "zfd": "cplheodar",
    "operator": null,
    "operator_type": null,
    "stem": "heo",
    "stem_known": true,
    "stem_gloss": "that which/the one",
    "suffix": "ar",
    "suffix_semantic": "water_agent",
    "expansion": "[RESIDUE:cpl][STEM:heo=that which/the one][RESIDUE:d][SUF:ar=water_agent]",
    "croatian": "[cpl]ono što[d]ar",
    "english": "[cpl] that which/the one [d]",
    "confidence": 0.5,
    "rewrites": [
      "gallows: p→pl (known stem)",
      "suffix: ar→ar (water/agent)"
    ],
    "notes": [
      "Stem: state_that_which (CANDIDATE)"
    ],
    "match_type": "partial",
    "matched_form": "heo",
    "matched_croatian": "ono što",
    "matched_category": "grammar",
    "matched_status": "CANDIDATE",
    "matched_source": "morphology_analysis",
    "stem_surface": "cplheod",
    "unmatched_prefix": "cpl",
    "unmatched_suffix": "d",
    "compound_parts": []
  },
  {
    "id": "f102r1.5.7",
    "eva": "sholdaiin",
    "zfd": "šoldain",
    "operator": "š",
    "operator_type": "comitative",
    "stem": "ol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": "n",
    "suffix_semantic": "noun",
    "expansion": "[OP:š][STEM:ol=oil][RESIDUE:dai][SUF:n=noun]",
    "croatian": "šulje[dai]n",
    "english": "with oil [dai]",
    "confidence": 0.8,
    "rewrites": [
      "operator: sh→š",
      "mid-word: ii→i",
      "suffix: n→n (noun ending)"
    ],
    "notes": [
      "Operator with/soak (CONFIRMED)",
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "oldai",
    "unmatched_prefix": "",
    "unmatched_suffix": "dai",
    "compound_parts": []
  }
]
```

### f102r1.4,+P0;H

| Layer | Text |
| --- | --- |
| EVA | dsheody okeeoy kody chkeeody daraiiin ctheoly qokcheo lolain |
| ZFD | dšeodi osteoy strody hstreodi darain ctrrheoli kostrheo lolain |
| Croatian | \[d\]sa onim\[d\]i osttim \[strody\] hsmolai da\[r\]stvar smjesa\[heol\]i ko\[str\]ono što \[l\]ulje\[ai\]n |
| English gloss | \[d\] with that which \[d\] vessel by/from that \[strody\] combine storax/resin preparation dose \[r\] substance/thing compound mixture \[heol\] which \[str\] that which/the one \[l\] oil \[ai\] |

| Token | Match | Matched form | Stem surface | Prefix residue | Suffix residue | Lexicon status | Parser score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| f102r1.6.1 | Partial | šeo | dšeod | d | d | CANDIDATE | 0.400 |
| f102r1.6.2 | Exact stem | eoy | eoy |  |  | CANDIDATE | 0.500 |
| f102r1.6.3 | Compound |  | strody |  |  | CANDIDATE | 0.350 |
| f102r1.6.4 | Stem + suffix | streod | streod |  |  | CANDIDATE | 0.900 |
| f102r1.6.5 | Partial | ain | rain | r |  | CONFIRMED | 0.650 |
| f102r1.6.6 | Partial | ctrr | ctrrheol |  | heol | CANDIDATE | 0.600 |
| f102r1.6.7 | Partial | heo | strheo | str |  | CANDIDATE | 0.900 |
| f102r1.6.8 | Partial | ol | lolai | l | ai | CONFIRMED | 0.450 |

#### Complete token provenance

```json
[
  {
    "id": "f102r1.6.1",
    "eva": "dsheody",
    "zfd": "dšeodi",
    "operator": null,
    "operator_type": null,
    "stem": "šeo",
    "stem_known": true,
    "stem_gloss": "with that which",
    "suffix": "i",
    "suffix_semantic": "adjectival",
    "expansion": "[RESIDUE:d][STEM:šeo=with that which][RESIDUE:d][SUF:i=adjectival]",
    "croatian": "[d]sa onim[d]i",
    "english": "[d] with that which [d]",
    "confidence": 0.4,
    "rewrites": [
      "mid-word: sh→š",
      "suffix: y→i (adjective marker)"
    ],
    "notes": [
      "Stem: state_with_that (CANDIDATE)"
    ],
    "match_type": "partial",
    "matched_form": "šeo",
    "matched_croatian": "sa onim",
    "matched_category": "grammar",
    "matched_status": "CANDIDATE",
    "matched_source": "morphology_analysis",
    "stem_surface": "dšeod",
    "unmatched_prefix": "d",
    "unmatched_suffix": "d",
    "compound_parts": []
  },
  {
    "id": "f102r1.6.2",
    "eva": "okeeoy",
    "zfd": "osteoy",
    "operator": "ost",
    "operator_type": "vessel",
    "stem": "eoy",
    "stem_known": true,
    "stem_gloss": "by/from that",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:ost][STEM:eoy=by/from that]",
    "croatian": "osttim",
    "english": "vessel by/from that",
    "confidence": 0.5,
    "rewrites": [
      "operator: ok→ost",
      "mid-word: ee→e"
    ],
    "notes": [
      "Operator vessel/container (CONFIRMED)",
      "Stem: eoy (CANDIDATE)"
    ],
    "match_type": "exact_stem",
    "matched_form": "eoy",
    "matched_croatian": "tim",
    "matched_category": "grammar",
    "matched_status": "CANDIDATE",
    "matched_source": "morphology_analysis",
    "stem_surface": "eoy",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.6.3",
    "eva": "kody",
    "zfd": "strody",
    "operator": null,
    "operator_type": null,
    "stem": "strody",
    "stem_known": true,
    "stem_gloss": "measure active process (variant)",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[COMPOUND:strody=measure active process (variant)]",
    "croatian": "[strody]",
    "english": "[strody]",
    "confidence": 0.35,
    "rewrites": [
      "gallows: k→st (unverified)",
      "gallows: t→tr (unverified)"
    ],
    "notes": [
      "Compound: [ko=measure/quantify (va] [dy=active process (vari]",
      "Stem: compound (CANDIDATE)"
    ],
    "match_type": "compound",
    "matched_form": "",
    "matched_croatian": "",
    "matched_category": "compound",
    "matched_status": "CANDIDATE",
    "matched_source": "unified_lexicon_v2.json",
    "stem_surface": "strody",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": [
      {
        "eva": "ko",
        "type": "operator",
        "gloss": "measure/quantify (variant)",
        "content": true
      },
      {
        "eva": "dy",
        "type": "suffixe",
        "gloss": "active process (variant)",
        "content": true
      }
    ]
  },
  {
    "id": "f102r1.6.4",
    "eva": "chkeeody",
    "zfd": "hstreodi",
    "operator": "h",
    "operator_type": "action",
    "stem": "streod",
    "stem_known": true,
    "stem_gloss": "storax/resin preparation",
    "suffix": "i",
    "suffix_semantic": "adjectival",
    "expansion": "[OP:h][STEM:streod=storax/resin preparation][SUF:i=adjectival]",
    "croatian": "hsmolai",
    "english": "combine storax/resin preparation",
    "confidence": 0.9,
    "rewrites": [
      "operator: ch→h",
      "mid-word: ee→e",
      "gallows: k→st (unverified)",
      "gallows: t→tr (known stem)",
      "suffix: y→i (adjective marker)"
    ],
    "notes": [
      "Operator combine/cook (CONFIRMED)",
      "Stem: streod (CANDIDATE)"
    ],
    "match_type": "suffix",
    "matched_form": "streod",
    "matched_croatian": "smola",
    "matched_category": "ingredient",
    "matched_status": "CANDIDATE",
    "matched_source": "morphology_analysis",
    "stem_surface": "streod",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.6.5",
    "eva": "daraiiin",
    "zfd": "darain",
    "operator": "da",
    "operator_type": "dative",
    "stem": "rain",
    "stem_known": true,
    "stem_gloss": "substance/thing",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:da][RESIDUE:r][STEM:ain=substance/thing]",
    "croatian": "da[r]stvar",
    "english": "dose [r] substance/thing",
    "confidence": 0.6499999999999999,
    "rewrites": [
      "operator: da→da",
      "mid-word: ii→i",
      "mid-word: aiin→ain"
    ],
    "notes": [
      "Operator dose/give/add (CONFIRMED)",
      "Stem: substance (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ain",
    "matched_croatian": "stvar",
    "matched_category": "grammar",
    "matched_status": "CONFIRMED",
    "matched_source": "morphology_analysis",
    "stem_surface": "rain",
    "unmatched_prefix": "r",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.6.6",
    "eva": "ctheoly",
    "zfd": "ctrrheoli",
    "operator": null,
    "operator_type": null,
    "stem": "ctrr",
    "stem_known": true,
    "stem_gloss": "compound mixture",
    "suffix": "i",
    "suffix_semantic": "adjectival",
    "expansion": "[STEM:ctrr=compound mixture][RESIDUE:heol][SUF:i=adjectival]",
    "croatian": "smjesa[heol]i",
    "english": "compound mixture [heol]",
    "confidence": 0.6000000000000001,
    "rewrites": [
      "mid-word: ct→ctr",
      "gallows: t→tr (known stem)",
      "suffix: y→i (adjective marker)"
    ],
    "notes": [
      "Stem: ctrr (CANDIDATE)"
    ],
    "match_type": "partial",
    "matched_form": "ctrr",
    "matched_croatian": "smjesa",
    "matched_category": "preparation",
    "matched_status": "CANDIDATE",
    "matched_source": "morphology_analysis",
    "stem_surface": "ctrrheol",
    "unmatched_prefix": "",
    "unmatched_suffix": "heol",
    "compound_parts": []
  },
  {
    "id": "f102r1.6.7",
    "eva": "qokcheo",
    "zfd": "kostrheo",
    "operator": "ko",
    "operator_type": "relative",
    "stem": "strheo",
    "stem_known": true,
    "stem_gloss": "that which/the one",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:ko][RESIDUE:str][STEM:heo=that which/the one]",
    "croatian": "ko[str]ono što",
    "english": "which [str] that which/the one",
    "confidence": 0.9,
    "rewrites": [
      "operator: qo→ko",
      "mid-word: ch→h",
      "gallows: k→st (known stem)",
      "gallows: t→tr (known stem)"
    ],
    "notes": [
      "Operator which/that/quantity (CONFIRMED)",
      "Stem: state_that_which (CANDIDATE)"
    ],
    "match_type": "partial",
    "matched_form": "heo",
    "matched_croatian": "ono što",
    "matched_category": "grammar",
    "matched_status": "CANDIDATE",
    "matched_source": "morphology_analysis",
    "stem_surface": "strheo",
    "unmatched_prefix": "str",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.6.8",
    "eva": "lolain",
    "zfd": "lolain",
    "operator": null,
    "operator_type": null,
    "stem": "ol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": "n",
    "suffix_semantic": "noun",
    "expansion": "[RESIDUE:l][STEM:ol=oil][RESIDUE:ai][SUF:n=noun]",
    "croatian": "[l]ulje[ai]n",
    "english": "[l] oil [ai]",
    "confidence": 0.44999999999999996,
    "rewrites": [
      "suffix: n→n (noun ending)"
    ],
    "notes": [
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "lolai",
    "unmatched_prefix": "l",
    "unmatched_suffix": "ai",
    "compound_parts": []
  }
]
```

### f102r1.5,+P0;H

| Layer | Text |
| --- | --- |
| EVA | ytol sheol she olaiin orain oraroekeol chol ekey qokol dain |
| ZFD | ytrol šeol še olain orain oraroestreol chol estrei kostrol dain |
| Croatian | \[ytr\]ulje š\[e\]ulje š\[e\] ulje\[ai\]n ulje\[ai\]n \[oraro\]melem\[e\]ol brasno melem\[e\]i ko\[str\]ulje dati |
| English gloss | \[ytr\] oil with \[e\] oil with \[e\] oil \[ai\] oil \[ai\] \[oraro\] plaster/poultice \[e\] flour/grain plaster/poultice \[e\] which \[str\] oil given/added |

| Token | Match | Matched form | Stem surface | Prefix residue | Suffix residue | Lexicon status | Parser score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| f102r1.7.1 | Partial | ol | ytrol | ytr |  | CONFIRMED | 0.500 |
| f102r1.7.2 | Partial | ol | eol | e |  | CONFIRMED | 0.550 |
| f102r1.7.3 | Compound |  | e |  |  | CANDIDATE | 0.500 |
| f102r1.7.4 | Partial | ol | olai |  | ai | CONFIRMED | 0.550 |
| f102r1.7.5 | Partial | or | orai |  | ai | CONFIRMED | 0.450 |
| f102r1.7.6 | Partial | estr | oraroestre | oraro | e | CANDIDATE | 0.700 |
| f102r1.7.7 | Whole word | chol | chol |  |  | CONFIRMED | 0.300 |
| f102r1.7.8 | Partial | estr | estre |  | e | CANDIDATE | 0.700 |
| f102r1.7.9 | Partial | ol | strol | str |  | CONFIRMED | 0.950 |
| f102r1.7.10 | Whole word | dain | dain |  |  | CONFIRMED | 0.300 |

#### Complete token provenance

```json
[
  {
    "id": "f102r1.7.1",
    "eva": "ytol",
    "zfd": "ytrol",
    "operator": null,
    "operator_type": null,
    "stem": "ytrol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[RESIDUE:ytr][STEM:ol=oil]",
    "croatian": "[ytr]ulje",
    "english": "[ytr] oil",
    "confidence": 0.5,
    "rewrites": [
      "gallows: t→tr (known stem)"
    ],
    "notes": [
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "ytrol",
    "unmatched_prefix": "ytr",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.7.2",
    "eva": "sheol",
    "zfd": "šeol",
    "operator": "š",
    "operator_type": "comitative",
    "stem": "eol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:š][RESIDUE:e][STEM:ol=oil]",
    "croatian": "š[e]ulje",
    "english": "with [e] oil",
    "confidence": 0.55,
    "rewrites": [
      "operator: sh→š"
    ],
    "notes": [
      "Operator with/soak (CONFIRMED)",
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "eol",
    "unmatched_prefix": "e",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.7.3",
    "eva": "she",
    "zfd": "še",
    "operator": "š",
    "operator_type": "comitative",
    "stem": "e",
    "stem_known": true,
    "stem_gloss": "state",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:š][COMPOUND:e=state]",
    "croatian": "š[e]",
    "english": "with [e]",
    "confidence": 0.5,
    "rewrites": [
      "operator: sh→š"
    ],
    "notes": [
      "Operator with/soak (CONFIRMED)",
      "Compound: [s=~15] [he=state/result/after]",
      "Stem: compound (CANDIDATE)"
    ],
    "match_type": "compound",
    "matched_form": "",
    "matched_croatian": "",
    "matched_category": "compound",
    "matched_status": "CANDIDATE",
    "matched_source": "unified_lexicon_v2.json",
    "stem_surface": "e",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": [
      {
        "eva": "s",
        "type": "suffixe",
        "gloss": "~15",
        "content": true
      },
      {
        "eva": "he",
        "type": "state_marker",
        "gloss": "state/result/after",
        "content": true
      }
    ]
  },
  {
    "id": "f102r1.7.4",
    "eva": "olaiin",
    "zfd": "olain",
    "operator": null,
    "operator_type": null,
    "stem": "ol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": "n",
    "suffix_semantic": "noun",
    "expansion": "[STEM:ol=oil][RESIDUE:ai][SUF:n=noun]",
    "croatian": "ulje[ai]n",
    "english": "oil [ai]",
    "confidence": 0.55,
    "rewrites": [
      "mid-word: ii→i",
      "suffix: n→n (noun ending)"
    ],
    "notes": [
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "olai",
    "unmatched_prefix": "",
    "unmatched_suffix": "ai",
    "compound_parts": []
  },
  {
    "id": "f102r1.7.5",
    "eva": "orain",
    "zfd": "orain",
    "operator": null,
    "operator_type": null,
    "stem": "or",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": "n",
    "suffix_semantic": "noun",
    "expansion": "[STEM:or=oil][RESIDUE:ai][SUF:n=noun]",
    "croatian": "ulje[ai]n",
    "english": "oil [ai]",
    "confidence": 0.44999999999999996,
    "rewrites": [
      "suffix: n→n (noun ending)"
    ],
    "notes": [
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "or",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "orai",
    "unmatched_prefix": "",
    "unmatched_suffix": "ai",
    "compound_parts": []
  },
  {
    "id": "f102r1.7.6",
    "eva": "oraroekeol",
    "zfd": "oraroestreol",
    "operator": null,
    "operator_type": null,
    "stem": "estr",
    "stem_known": true,
    "stem_gloss": "plaster/poultice",
    "suffix": "ol",
    "suffix_semantic": "oil_related",
    "expansion": "[RESIDUE:oraro][STEM:estr=plaster/poultice][RESIDUE:e][SUF:ol=oil_related]",
    "croatian": "[oraro]melem[e]ol",
    "english": "[oraro] plaster/poultice [e]",
    "confidence": 0.7000000000000001,
    "rewrites": [
      "gallows: k→st (known stem)",
      "gallows: t→tr (known stem)",
      "suffix: ol→ol (oil/oily)"
    ],
    "notes": [
      "Stem: emplastr (CANDIDATE)"
    ],
    "match_type": "partial",
    "matched_form": "estr",
    "matched_croatian": "melem",
    "matched_category": "preparation",
    "matched_status": "CANDIDATE",
    "matched_source": "MS650_cross_reference",
    "stem_surface": "oraroestre",
    "unmatched_prefix": "oraro",
    "unmatched_suffix": "e",
    "compound_parts": []
  },
  {
    "id": "f102r1.7.7",
    "eva": "chol",
    "zfd": "chol",
    "operator": null,
    "operator_type": null,
    "stem": "chol",
    "stem_known": true,
    "stem_gloss": "flour/grain",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[STEM:chol=flour/grain]",
    "croatian": "brasno",
    "english": "flour/grain",
    "confidence": 0.3,
    "rewrites": [],
    "notes": [
      "Stem: flour (CONFIRMED) [whole-word]"
    ],
    "match_type": "whole_word",
    "matched_form": "chol",
    "matched_croatian": "brasno",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "chol",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.7.8",
    "eva": "ekey",
    "zfd": "estrei",
    "operator": null,
    "operator_type": null,
    "stem": "estr",
    "stem_known": true,
    "stem_gloss": "plaster/poultice",
    "suffix": "i",
    "suffix_semantic": "adjectival",
    "expansion": "[STEM:estr=plaster/poultice][RESIDUE:e][SUF:i=adjectival]",
    "croatian": "melem[e]i",
    "english": "plaster/poultice [e]",
    "confidence": 0.7000000000000001,
    "rewrites": [
      "gallows: k→st (known stem)",
      "gallows: t→tr (known stem)",
      "suffix: y→i (adjective marker)"
    ],
    "notes": [
      "Stem: emplastr (CANDIDATE)"
    ],
    "match_type": "partial",
    "matched_form": "estr",
    "matched_croatian": "melem",
    "matched_category": "preparation",
    "matched_status": "CANDIDATE",
    "matched_source": "MS650_cross_reference",
    "stem_surface": "estre",
    "unmatched_prefix": "",
    "unmatched_suffix": "e",
    "compound_parts": []
  },
  {
    "id": "f102r1.7.9",
    "eva": "qokol",
    "zfd": "kostrol",
    "operator": "ko",
    "operator_type": "relative",
    "stem": "strol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:ko][RESIDUE:str][STEM:ol=oil]",
    "croatian": "ko[str]ulje",
    "english": "which [str] oil",
    "confidence": 0.95,
    "rewrites": [
      "operator: qo→ko",
      "gallows: k→st (known stem)",
      "gallows: t→tr (known stem)"
    ],
    "notes": [
      "Operator which/that/quantity (CONFIRMED)",
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "strol",
    "unmatched_prefix": "str",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.7.10",
    "eva": "dain",
    "zfd": "dain",
    "operator": null,
    "operator_type": null,
    "stem": "dain",
    "stem_known": true,
    "stem_gloss": "given/added",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[STEM:dain=given/added]",
    "croatian": "dati",
    "english": "given/added",
    "confidence": 0.3,
    "rewrites": [],
    "notes": [
      "Stem: give (CONFIRMED) [whole-word]"
    ],
    "match_type": "whole_word",
    "matched_form": "dain",
    "matched_croatian": "dati",
    "matched_category": "grammar",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "dain",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": []
  }
]
```

### f102r1.6,+P0;H

| Layer | Text |
| --- | --- |
| EVA | daiin ykeeol oldy okodaiin |
| ZFD | dain ystreol oldi ostodain |
| Croatian | da\[in\] \[ystre\]ulje ulje\[d\]i ost\[o\]dati\[i\]n |
| English gloss | dose \[in\] \[ystre\] oil oil \[d\] vessel \[o\] give/add \[i\] |

| Token | Match | Matched form | Stem surface | Prefix residue | Suffix residue | Lexicon status | Parser score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| f102r1.8.1 | Compound |  | in |  |  | CANDIDATE | 0.600 |
| f102r1.8.2 | Partial | ol | ystreol | ystre |  | CONFIRMED | 0.800 |
| f102r1.8.3 | Partial | ol | old |  | d | CONFIRMED | 0.450 |
| f102r1.8.4 | Partial | da | odai | o | i | CONFIRMED | 0.800 |

#### Complete token provenance

```json
[
  {
    "id": "f102r1.8.1",
    "eva": "daiin",
    "zfd": "dain",
    "operator": "da",
    "operator_type": "dative",
    "stem": "in",
    "stem_known": true,
    "stem_gloss": "Add (extended)",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:da][COMPOUND:in=Add (extended)]",
    "croatian": "da[in]",
    "english": "dose [in]",
    "confidence": 0.6,
    "rewrites": [
      "operator: da→da",
      "mid-word: ii→i"
    ],
    "notes": [
      "Operator dose/give/add (CONFIRMED)",
      "Compound: [daiin=Add (extended)]",
      "Stem: compound (CANDIDATE)"
    ],
    "match_type": "compound",
    "matched_form": "",
    "matched_croatian": "",
    "matched_category": "compound",
    "matched_status": "CANDIDATE",
    "matched_source": "unified_lexicon_v2.json",
    "stem_surface": "in",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": [
      {
        "eva": "daiin",
        "type": "stem",
        "gloss": "Add (extended)",
        "content": true
      }
    ]
  },
  {
    "id": "f102r1.8.2",
    "eva": "ykeeol",
    "zfd": "ystreol",
    "operator": null,
    "operator_type": null,
    "stem": "ystreol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[RESIDUE:ystre][STEM:ol=oil]",
    "croatian": "[ystre]ulje",
    "english": "[ystre] oil",
    "confidence": 0.8,
    "rewrites": [
      "mid-word: ee→e",
      "gallows: k→st (known stem)",
      "gallows: t→tr (known stem)"
    ],
    "notes": [
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "ystreol",
    "unmatched_prefix": "ystre",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.8.3",
    "eva": "oldy",
    "zfd": "oldi",
    "operator": null,
    "operator_type": null,
    "stem": "ol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": "i",
    "suffix_semantic": "adjectival",
    "expansion": "[STEM:ol=oil][RESIDUE:d][SUF:i=adjectival]",
    "croatian": "ulje[d]i",
    "english": "oil [d]",
    "confidence": 0.44999999999999996,
    "rewrites": [
      "suffix: y→i (adjective marker)"
    ],
    "notes": [
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "old",
    "unmatched_prefix": "",
    "unmatched_suffix": "d",
    "compound_parts": []
  },
  {
    "id": "f102r1.8.4",
    "eva": "okodaiin",
    "zfd": "ostodain",
    "operator": "ost",
    "operator_type": "vessel",
    "stem": "da",
    "stem_known": true,
    "stem_gloss": "give/add",
    "suffix": "n",
    "suffix_semantic": "noun",
    "expansion": "[OP:ost][RESIDUE:o][STEM:da=give/add][RESIDUE:i][SUF:n=noun]",
    "croatian": "ost[o]dati[i]n",
    "english": "vessel [o] give/add [i]",
    "confidence": 0.8,
    "rewrites": [
      "operator: ok→ost",
      "mid-word: ii→i",
      "suffix: n→n (noun ending)"
    ],
    "notes": [
      "Operator vessel/container (CONFIRMED)",
      "Stem: give (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "da",
    "matched_croatian": "dati",
    "matched_category": "grammar",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "odai",
    "unmatched_prefix": "o",
    "unmatched_suffix": "i",
    "compound_parts": []
  }
]
```

### f102r1.8,@P0;H

| Layer | Text |
| --- | --- |
| EVA | pshodaiin qoorar chopy chofol daiin oteol qoteol doly |
| ZFD | plšodain koorar hoply hoplrol dain otreol kotreol doli |
| Croatian | \[plšo\]dati\[i\]n kouljear h\[oply\] h\[o\]prašakol da\[in\] otr\[e\]ulje ko\[tre\]ulje \[d\]uljei |
| English gloss | \[plšo\] give/add \[i\] which oil combine \[oply\] combine \[o\] powder/pulverize dose \[in\] vessel \[e\] oil which \[tre\] oil \[d\] oil |

| Token | Match | Matched form | Stem surface | Prefix residue | Suffix residue | Lexicon status | Parser score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| f102r1.9.1 | Partial | da | plšodai | plšo | i | CONFIRMED | 0.750 |
| f102r1.9.2 | Stem + suffix | or | or |  |  | CONFIRMED | 0.700 |
| f102r1.9.3 | Compound |  | oply |  |  | CANDIDATE | 0.550 |
| f102r1.9.4 | Partial | plr | oplr | o |  | CANDIDATE | 0.950 |
| f102r1.9.5 | Compound |  | in |  |  | CANDIDATE | 0.600 |
| f102r1.9.6 | Partial | ol | eol | e |  | CONFIRMED | 0.550 |
| f102r1.9.7 | Partial | ol | treol | tre |  | CONFIRMED | 0.750 |
| f102r1.9.8 | Partial | ol | dol | d |  | CONFIRMED | 0.450 |

#### Complete token provenance

```json
[
  {
    "id": "f102r1.9.1",
    "eva": "pshodaiin",
    "zfd": "plšodain",
    "operator": null,
    "operator_type": null,
    "stem": "da",
    "stem_known": true,
    "stem_gloss": "give/add",
    "suffix": "n",
    "suffix_semantic": "noun",
    "expansion": "[RESIDUE:plšo][STEM:da=give/add][RESIDUE:i][SUF:n=noun]",
    "croatian": "[plšo]dati[i]n",
    "english": "[plšo] give/add [i]",
    "confidence": 0.75,
    "rewrites": [
      "mid-word: ii→i",
      "mid-word: sh→š",
      "gallows: p→pl (known stem)",
      "suffix: n→n (noun ending)"
    ],
    "notes": [
      "Stem: give (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "da",
    "matched_croatian": "dati",
    "matched_category": "grammar",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "plšodai",
    "unmatched_prefix": "plšo",
    "unmatched_suffix": "i",
    "compound_parts": []
  },
  {
    "id": "f102r1.9.2",
    "eva": "qoorar",
    "zfd": "koorar",
    "operator": "ko",
    "operator_type": "relative",
    "stem": "or",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": "ar",
    "suffix_semantic": "water_agent",
    "expansion": "[OP:ko][STEM:or=oil][SUF:ar=water_agent]",
    "croatian": "kouljear",
    "english": "which oil",
    "confidence": 0.7,
    "rewrites": [
      "operator: qo→ko",
      "suffix: ar→ar (water/agent)"
    ],
    "notes": [
      "Operator which/that/quantity (CONFIRMED)",
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "suffix",
    "matched_form": "or",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "or",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.9.3",
    "eva": "chopy",
    "zfd": "hoply",
    "operator": "h",
    "operator_type": "action",
    "stem": "oply",
    "stem_known": true,
    "stem_gloss": "combine adjectival",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:h][COMPOUND:oply=combine adjectival]",
    "croatian": "h[oply]",
    "english": "combine [oply]",
    "confidence": 0.55,
    "rewrites": [
      "operator: ch→h",
      "gallows: p→pl (unverified)"
    ],
    "notes": [
      "Operator combine/cook (CONFIRMED)",
      "Compound: [ch=combine/cook] o p [y=adjectival/state]",
      "Stem: compound (CANDIDATE)"
    ],
    "match_type": "compound",
    "matched_form": "",
    "matched_croatian": "",
    "matched_category": "compound",
    "matched_status": "CANDIDATE",
    "matched_source": "unified_lexicon_v2.json",
    "stem_surface": "oply",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": [
      {
        "eva": "ch",
        "type": "operator",
        "gloss": "combine/cook",
        "content": true
      },
      {
        "eva": "o",
        "type": "binding",
        "gloss": "binding vowel",
        "content": false
      },
      {
        "eva": "p",
        "type": "gallows",
        "gloss": "preparation (pl-)",
        "content": false
      },
      {
        "eva": "y",
        "type": "suffixe",
        "gloss": "adjectival/state",
        "content": true
      }
    ]
  },
  {
    "id": "f102r1.9.4",
    "eva": "chofol",
    "zfd": "hoplrol",
    "operator": "h",
    "operator_type": "action",
    "stem": "plr",
    "stem_known": true,
    "stem_gloss": "powder/pulverize",
    "suffix": "ol",
    "suffix_semantic": "oil_related",
    "expansion": "[OP:h][RESIDUE:o][STEM:plr=powder/pulverize][SUF:ol=oil_related]",
    "croatian": "h[o]prašakol",
    "english": "combine [o] powder/pulverize",
    "confidence": 0.9500000000000001,
    "rewrites": [
      "operator: ch→h",
      "gallows: f→pr (known stem)",
      "gallows: p→pl (known stem)",
      "suffix: ol→ol (oil/oily)"
    ],
    "notes": [
      "Operator combine/cook (CONFIRMED)",
      "Stem: pulv (CANDIDATE)"
    ],
    "match_type": "partial",
    "matched_form": "plr",
    "matched_croatian": "prašak",
    "matched_category": "preparation",
    "matched_status": "CANDIDATE",
    "matched_source": "MS650_cross_reference",
    "stem_surface": "oplr",
    "unmatched_prefix": "o",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.9.5",
    "eva": "daiin",
    "zfd": "dain",
    "operator": "da",
    "operator_type": "dative",
    "stem": "in",
    "stem_known": true,
    "stem_gloss": "Add (extended)",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:da][COMPOUND:in=Add (extended)]",
    "croatian": "da[in]",
    "english": "dose [in]",
    "confidence": 0.6,
    "rewrites": [
      "operator: da→da",
      "mid-word: ii→i"
    ],
    "notes": [
      "Operator dose/give/add (CONFIRMED)",
      "Compound: [daiin=Add (extended)]",
      "Stem: compound (CANDIDATE)"
    ],
    "match_type": "compound",
    "matched_form": "",
    "matched_croatian": "",
    "matched_category": "compound",
    "matched_status": "CANDIDATE",
    "matched_source": "unified_lexicon_v2.json",
    "stem_surface": "in",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": [
      {
        "eva": "daiin",
        "type": "stem",
        "gloss": "Add (extended)",
        "content": true
      }
    ]
  },
  {
    "id": "f102r1.9.6",
    "eva": "oteol",
    "zfd": "otreol",
    "operator": "otr",
    "operator_type": "vessel",
    "stem": "eol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:otr][RESIDUE:e][STEM:ol=oil]",
    "croatian": "otr[e]ulje",
    "english": "vessel [e] oil",
    "confidence": 0.55,
    "rewrites": [
      "operator: ot→otr"
    ],
    "notes": [
      "Operator vessel/container (CONFIRMED)",
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "eol",
    "unmatched_prefix": "e",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.9.7",
    "eva": "qoteol",
    "zfd": "kotreol",
    "operator": "ko",
    "operator_type": "relative",
    "stem": "treol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:ko][RESIDUE:tre][STEM:ol=oil]",
    "croatian": "ko[tre]ulje",
    "english": "which [tre] oil",
    "confidence": 0.75,
    "rewrites": [
      "operator: qo→ko",
      "gallows: t→tr (known stem)"
    ],
    "notes": [
      "Operator which/that/quantity (CONFIRMED)",
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "treol",
    "unmatched_prefix": "tre",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.9.8",
    "eva": "doly",
    "zfd": "doli",
    "operator": null,
    "operator_type": null,
    "stem": "ol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": "i",
    "suffix_semantic": "adjectival",
    "expansion": "[RESIDUE:d][STEM:ol=oil][SUF:i=adjectival]",
    "croatian": "[d]uljei",
    "english": "[d] oil",
    "confidence": 0.44999999999999996,
    "rewrites": [
      "suffix: y→i (adjective marker)"
    ],
    "notes": [
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "dol",
    "unmatched_prefix": "d",
    "unmatched_suffix": "",
    "compound_parts": []
  }
]
```

### f102r1.9,+P0;H

| Layer | Text |
| --- | --- |
| EVA | daiin orsheoldy qokeol oteeody lshody keodal qokshdy sy |
| ZFD | dain oršeoldi kostreol otreody lšody streodal kostršdy sy |
| Croatian | da\[in\] \[or\]sa onim\[ld\]i ko\[stre\]ulje otr\[eody\] \[lšody\] smolaal ko\[stršdy\] \[sy\] |
| English gloss | dose \[in\] \[or\] with that which \[ld\] which \[stre\] oil vessel \[eody\] \[lšody\] storax/resin preparation which \[stršdy\] \[sy\] |

| Token | Match | Matched form | Stem surface | Prefix residue | Suffix residue | Lexicon status | Parser score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| f102r1.10.1 | Compound |  | in |  |  | CANDIDATE | 0.600 |
| f102r1.10.2 | Partial | šeo | oršeold | or | ld | CANDIDATE | 0.400 |
| f102r1.10.3 | Partial | ol | streol | stre |  | CONFIRMED | 0.950 |
| f102r1.10.4 | Compound |  | eody |  |  | CANDIDATE | 0.600 |
| f102r1.10.5 | Compound |  | lšody |  |  | CANDIDATE | 0.350 |
| f102r1.10.6 | Stem + suffix | streod | streod |  |  | CANDIDATE | 0.700 |
| f102r1.10.7 | Compound |  | stršdy |  |  | CANDIDATE | 0.700 |
| f102r1.10.8 | Compound |  | sy |  |  | CANDIDATE | 0.250 |

#### Complete token provenance

```json
[
  {
    "id": "f102r1.10.1",
    "eva": "daiin",
    "zfd": "dain",
    "operator": "da",
    "operator_type": "dative",
    "stem": "in",
    "stem_known": true,
    "stem_gloss": "Add (extended)",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:da][COMPOUND:in=Add (extended)]",
    "croatian": "da[in]",
    "english": "dose [in]",
    "confidence": 0.6,
    "rewrites": [
      "operator: da→da",
      "mid-word: ii→i"
    ],
    "notes": [
      "Operator dose/give/add (CONFIRMED)",
      "Compound: [daiin=Add (extended)]",
      "Stem: compound (CANDIDATE)"
    ],
    "match_type": "compound",
    "matched_form": "",
    "matched_croatian": "",
    "matched_category": "compound",
    "matched_status": "CANDIDATE",
    "matched_source": "unified_lexicon_v2.json",
    "stem_surface": "in",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": [
      {
        "eva": "daiin",
        "type": "stem",
        "gloss": "Add (extended)",
        "content": true
      }
    ]
  },
  {
    "id": "f102r1.10.2",
    "eva": "orsheoldy",
    "zfd": "oršeoldi",
    "operator": null,
    "operator_type": null,
    "stem": "šeo",
    "stem_known": true,
    "stem_gloss": "with that which",
    "suffix": "i",
    "suffix_semantic": "adjectival",
    "expansion": "[RESIDUE:or][STEM:šeo=with that which][RESIDUE:ld][SUF:i=adjectival]",
    "croatian": "[or]sa onim[ld]i",
    "english": "[or] with that which [ld]",
    "confidence": 0.4,
    "rewrites": [
      "mid-word: sh→š",
      "suffix: y→i (adjective marker)"
    ],
    "notes": [
      "Stem: state_with_that (CANDIDATE)"
    ],
    "match_type": "partial",
    "matched_form": "šeo",
    "matched_croatian": "sa onim",
    "matched_category": "grammar",
    "matched_status": "CANDIDATE",
    "matched_source": "morphology_analysis",
    "stem_surface": "oršeold",
    "unmatched_prefix": "or",
    "unmatched_suffix": "ld",
    "compound_parts": []
  },
  {
    "id": "f102r1.10.3",
    "eva": "qokeol",
    "zfd": "kostreol",
    "operator": "ko",
    "operator_type": "relative",
    "stem": "streol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:ko][RESIDUE:stre][STEM:ol=oil]",
    "croatian": "ko[stre]ulje",
    "english": "which [stre] oil",
    "confidence": 0.95,
    "rewrites": [
      "operator: qo→ko",
      "gallows: k→st (known stem)",
      "gallows: t→tr (known stem)"
    ],
    "notes": [
      "Operator which/that/quantity (CONFIRMED)",
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "streol",
    "unmatched_prefix": "stre",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.10.4",
    "eva": "oteeody",
    "zfd": "otreody",
    "operator": "otr",
    "operator_type": "vessel",
    "stem": "eody",
    "stem_known": true,
    "stem_gloss": "vessel stalk adjectival",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:otr][COMPOUND:eody=vessel stalk adjectival]",
    "croatian": "otr[eody]",
    "english": "vessel [eody]",
    "confidence": 0.6,
    "rewrites": [
      "operator: ot→otr",
      "mid-word: ee→e"
    ],
    "notes": [
      "Operator vessel/container (CONFIRMED)",
      "Compound: [ot=vessel/container (va] [ee=(intensifier)] [od=stalk/stem] [y=adjectival/state]",
      "Stem: compound (CANDIDATE)"
    ],
    "match_type": "compound",
    "matched_form": "",
    "matched_croatian": "",
    "matched_category": "compound",
    "matched_status": "CANDIDATE",
    "matched_source": "unified_lexicon_v2.json",
    "stem_surface": "eody",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": [
      {
        "eva": "ot",
        "type": "operator",
        "gloss": "vessel/container (variant)",
        "content": true
      },
      {
        "eva": "ee",
        "type": "stem",
        "gloss": "(intensifier)",
        "content": true
      },
      {
        "eva": "od",
        "type": "stem",
        "gloss": "stalk/stem",
        "content": true
      },
      {
        "eva": "y",
        "type": "suffixe",
        "gloss": "adjectival/state",
        "content": true
      }
    ]
  },
  {
    "id": "f102r1.10.5",
    "eva": "lshody",
    "zfd": "lšody",
    "operator": null,
    "operator_type": null,
    "stem": "lšody",
    "stem_known": true,
    "stem_gloss": "The soak stalk adjectival",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[COMPOUND:lšody=The soak stalk adjectival]",
    "croatian": "[lšody]",
    "english": "[lšody]",
    "confidence": 0.35,
    "rewrites": [
      "mid-word: sh→š"
    ],
    "notes": [
      "Compound: [l=The / that (determin] [sh=soak/infuse] [od=stalk/stem] [y=adjectival/state]",
      "Stem: compound (CANDIDATE)"
    ],
    "match_type": "compound",
    "matched_form": "",
    "matched_croatian": "",
    "matched_category": "compound",
    "matched_status": "CANDIDATE",
    "matched_source": "unified_lexicon_v2.json",
    "stem_surface": "lšody",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": [
      {
        "eva": "l",
        "type": "operator",
        "gloss": "The / that (determiner)",
        "content": true
      },
      {
        "eva": "sh",
        "type": "operator",
        "gloss": "soak/infuse",
        "content": true
      },
      {
        "eva": "od",
        "type": "stem",
        "gloss": "stalk/stem",
        "content": true
      },
      {
        "eva": "y",
        "type": "suffixe",
        "gloss": "adjectival/state",
        "content": true
      }
    ]
  },
  {
    "id": "f102r1.10.6",
    "eva": "keodal",
    "zfd": "streodal",
    "operator": null,
    "operator_type": null,
    "stem": "streod",
    "stem_known": true,
    "stem_gloss": "storax/resin preparation",
    "suffix": "al",
    "suffix_semantic": "substance",
    "expansion": "[STEM:streod=storax/resin preparation][SUF:al=substance]",
    "croatian": "smolaal",
    "english": "storax/resin preparation",
    "confidence": 0.7000000000000001,
    "rewrites": [
      "gallows: k→st (known stem)",
      "gallows: t→tr (known stem)",
      "suffix: al→al (substance)"
    ],
    "notes": [
      "Stem: streod (CANDIDATE)"
    ],
    "match_type": "suffix",
    "matched_form": "streod",
    "matched_croatian": "smola",
    "matched_category": "ingredient",
    "matched_status": "CANDIDATE",
    "matched_source": "morphology_analysis",
    "stem_surface": "streod",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.10.7",
    "eva": "qokshdy",
    "zfd": "kostršdy",
    "operator": "ko",
    "operator_type": "relative",
    "stem": "stršdy",
    "stem_known": true,
    "stem_gloss": "measure vessel (short) soak active process (variant)",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:ko][COMPOUND:stršdy=measure vessel (short) soak active process (variant)]",
    "croatian": "ko[stršdy]",
    "english": "which [stršdy]",
    "confidence": 0.7,
    "rewrites": [
      "operator: qo→ko",
      "mid-word: sh→š",
      "gallows: k→st (unverified)",
      "gallows: t→tr (unverified)"
    ],
    "notes": [
      "Operator which/that/quantity (CONFIRMED)",
      "Compound: [qo=measure/quantify] [k=vessel (short)] [sh=soak/infuse] [dy=active process (vari]",
      "Stem: compound (CANDIDATE)"
    ],
    "match_type": "compound",
    "matched_form": "",
    "matched_croatian": "",
    "matched_category": "compound",
    "matched_status": "CANDIDATE",
    "matched_source": "unified_lexicon_v2.json",
    "stem_surface": "stršdy",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": [
      {
        "eva": "qo",
        "type": "operator",
        "gloss": "measure/quantify",
        "content": true
      },
      {
        "eva": "k",
        "type": "stem",
        "gloss": "vessel (short)",
        "content": true
      },
      {
        "eva": "sh",
        "type": "operator",
        "gloss": "soak/infuse",
        "content": true
      },
      {
        "eva": "dy",
        "type": "suffixe",
        "gloss": "active process (variant)",
        "content": true
      }
    ]
  },
  {
    "id": "f102r1.10.8",
    "eva": "sy",
    "zfd": "sy",
    "operator": null,
    "operator_type": null,
    "stem": "sy",
    "stem_known": true,
    "stem_gloss": "adjectival",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[COMPOUND:sy=adjectival]",
    "croatian": "[sy]",
    "english": "[sy]",
    "confidence": 0.25,
    "rewrites": [],
    "notes": [
      "Compound: [s=~15] [y=adjectival/state]",
      "Stem: compound (CANDIDATE)"
    ],
    "match_type": "compound",
    "matched_form": "",
    "matched_croatian": "",
    "matched_category": "compound",
    "matched_status": "CANDIDATE",
    "matched_source": "unified_lexicon_v2.json",
    "stem_surface": "sy",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": [
      {
        "eva": "s",
        "type": "suffixe",
        "gloss": "~15",
        "content": true
      },
      {
        "eva": "y",
        "type": "suffixe",
        "gloss": "adjectival/state",
        "content": true
      }
    ]
  }
]
```

### f102r1.10,+P0;H

| Layer | Text |
| --- | --- |
| EVA | ycheol sholdy chol chol ykeeol dol doleodaiin dol cthedy |
| ZFD | yheol šoldi chol chol ystreol dol doleodain dol ctrrhedi |
| Croatian | \[y\]ov/tajol šulje\[d\]i brasno brasno \[ystre\]ulje \[d\]ulje \[d\]ulje\[eodai\]n \[d\]ulje smjesa\[h\]edi |
| English gloss | \[y\] the/this (demonstrative) with oil \[d\] flour/grain flour/grain \[ystre\] oil \[d\] oil \[d\] oil \[eodai\] \[d\] oil compound mixture \[h\] prepared |

| Token | Match | Matched form | Stem surface | Prefix residue | Suffix residue | Lexicon status | Parser score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| f102r1.11.1 | Partial | he | yhe | y |  | CANDIDATE | 0.400 |
| f102r1.11.2 | Partial | ol | old |  | d | CONFIRMED | 0.700 |
| f102r1.11.3 | Whole word | chol | chol |  |  | CONFIRMED | 0.300 |
| f102r1.11.4 | Whole word | chol | chol |  |  | CONFIRMED | 0.300 |
| f102r1.11.5 | Partial | ol | ystreol | ystre |  | CONFIRMED | 0.800 |
| f102r1.11.6 | Partial | ol | dol | d |  | CONFIRMED | 0.300 |
| f102r1.11.7 | Partial | ol | doleodai | d | eodai | CONFIRMED | 0.550 |
| f102r1.11.8 | Partial | ol | dol | d |  | CONFIRMED | 0.300 |
| f102r1.11.9 | Partial | ctrr | ctrrh |  | h | CANDIDATE | 0.600 |

#### Complete token provenance

```json
[
  {
    "id": "f102r1.11.1",
    "eva": "ycheol",
    "zfd": "yheol",
    "operator": null,
    "operator_type": null,
    "stem": "he",
    "stem_known": true,
    "stem_gloss": "the/this (demonstrative)",
    "suffix": "ol",
    "suffix_semantic": "oil_related",
    "expansion": "[RESIDUE:y][STEM:he=the/this (demonstrative)][SUF:ol=oil_related]",
    "croatian": "[y]ov/tajol",
    "english": "[y] the/this (demonstrative)",
    "confidence": 0.4,
    "rewrites": [
      "mid-word: ch→h",
      "suffix: ol→ol (oil/oily)"
    ],
    "notes": [
      "Stem: state_this (CANDIDATE)"
    ],
    "match_type": "partial",
    "matched_form": "he",
    "matched_croatian": "ov/taj",
    "matched_category": "grammar",
    "matched_status": "CANDIDATE",
    "matched_source": "morphology_analysis",
    "stem_surface": "yhe",
    "unmatched_prefix": "y",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.11.2",
    "eva": "sholdy",
    "zfd": "šoldi",
    "operator": "š",
    "operator_type": "comitative",
    "stem": "ol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": "i",
    "suffix_semantic": "adjectival",
    "expansion": "[OP:š][STEM:ol=oil][RESIDUE:d][SUF:i=adjectival]",
    "croatian": "šulje[d]i",
    "english": "with oil [d]",
    "confidence": 0.7,
    "rewrites": [
      "operator: sh→š",
      "suffix: y→i (adjective marker)"
    ],
    "notes": [
      "Operator with/soak (CONFIRMED)",
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "old",
    "unmatched_prefix": "",
    "unmatched_suffix": "d",
    "compound_parts": []
  },
  {
    "id": "f102r1.11.3",
    "eva": "chol",
    "zfd": "chol",
    "operator": null,
    "operator_type": null,
    "stem": "chol",
    "stem_known": true,
    "stem_gloss": "flour/grain",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[STEM:chol=flour/grain]",
    "croatian": "brasno",
    "english": "flour/grain",
    "confidence": 0.3,
    "rewrites": [],
    "notes": [
      "Stem: flour (CONFIRMED) [whole-word]"
    ],
    "match_type": "whole_word",
    "matched_form": "chol",
    "matched_croatian": "brasno",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "chol",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.11.4",
    "eva": "chol",
    "zfd": "chol",
    "operator": null,
    "operator_type": null,
    "stem": "chol",
    "stem_known": true,
    "stem_gloss": "flour/grain",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[STEM:chol=flour/grain]",
    "croatian": "brasno",
    "english": "flour/grain",
    "confidence": 0.3,
    "rewrites": [],
    "notes": [
      "Stem: flour (CONFIRMED) [whole-word]"
    ],
    "match_type": "whole_word",
    "matched_form": "chol",
    "matched_croatian": "brasno",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "chol",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.11.5",
    "eva": "ykeeol",
    "zfd": "ystreol",
    "operator": null,
    "operator_type": null,
    "stem": "ystreol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[RESIDUE:ystre][STEM:ol=oil]",
    "croatian": "[ystre]ulje",
    "english": "[ystre] oil",
    "confidence": 0.8,
    "rewrites": [
      "mid-word: ee→e",
      "gallows: k→st (known stem)",
      "gallows: t→tr (known stem)"
    ],
    "notes": [
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "ystreol",
    "unmatched_prefix": "ystre",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.11.6",
    "eva": "dol",
    "zfd": "dol",
    "operator": null,
    "operator_type": null,
    "stem": "dol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[RESIDUE:d][STEM:ol=oil]",
    "croatian": "[d]ulje",
    "english": "[d] oil",
    "confidence": 0.3,
    "rewrites": [],
    "notes": [
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "dol",
    "unmatched_prefix": "d",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.11.7",
    "eva": "doleodaiin",
    "zfd": "doleodain",
    "operator": null,
    "operator_type": null,
    "stem": "ol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": "n",
    "suffix_semantic": "noun",
    "expansion": "[RESIDUE:d][STEM:ol=oil][RESIDUE:eodai][SUF:n=noun]",
    "croatian": "[d]ulje[eodai]n",
    "english": "[d] oil [eodai]",
    "confidence": 0.55,
    "rewrites": [
      "mid-word: ii→i",
      "suffix: n→n (noun ending)"
    ],
    "notes": [
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "doleodai",
    "unmatched_prefix": "d",
    "unmatched_suffix": "eodai",
    "compound_parts": []
  },
  {
    "id": "f102r1.11.8",
    "eva": "dol",
    "zfd": "dol",
    "operator": null,
    "operator_type": null,
    "stem": "dol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[RESIDUE:d][STEM:ol=oil]",
    "croatian": "[d]ulje",
    "english": "[d] oil",
    "confidence": 0.3,
    "rewrites": [],
    "notes": [
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "dol",
    "unmatched_prefix": "d",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.11.9",
    "eva": "cthedy",
    "zfd": "ctrrhedi",
    "operator": null,
    "operator_type": null,
    "stem": "ctrr",
    "stem_known": true,
    "stem_gloss": "compound mixture",
    "suffix": "edi",
    "suffix_semantic": "processed",
    "expansion": "[STEM:ctrr=compound mixture][RESIDUE:h][SUF:edi=processed]",
    "croatian": "smjesa[h]edi",
    "english": "compound mixture [h] prepared",
    "confidence": 0.6000000000000001,
    "rewrites": [
      "mid-word: ct→ctr",
      "gallows: t→tr (known stem)",
      "suffix: edy→edi (prepared/processed)"
    ],
    "notes": [
      "Stem: ctrr (CANDIDATE)"
    ],
    "match_type": "partial",
    "matched_form": "ctrr",
    "matched_croatian": "smjesa",
    "matched_category": "preparation",
    "matched_status": "CANDIDATE",
    "matched_source": "morphology_analysis",
    "stem_surface": "ctrrh",
    "unmatched_prefix": "",
    "unmatched_suffix": "h",
    "compound_parts": []
  }
]
```

### f102r1.11,+P0;H

| Layer | Text |
| --- | --- |
| EVA | dcheo qockhy sol sheey okeody qokeodol shockhey oleeol |
| ZFD | dheo kocstrhi sol šey osteody kostreodol šocstrhei oleol |
| Croatian | \[d\]ono što kozgušnjeni\[h\]i \[s\]ulje š\[ey\] ost\[eody\] kosmolaol š\[o\]zgušnjeni\[he\]i ulje\[e\]ol |
| English gloss | \[d\] that which/the one which concentrated preparation \[h\] \[s\] oil with liquid/fluid vessel \[eody\] which storax/resin preparation with \[o\] concentrated preparation \[he\] oil \[e\] |

| Token | Match | Matched form | Stem surface | Prefix residue | Suffix residue | Lexicon status | Parser score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| f102r1.12.1 | Partial | heo | dheo | d |  | CANDIDATE | 0.250 |
| f102r1.12.2 | Partial | cstr | cstrh |  | h | CANDIDATE | 0.850 |
| f102r1.12.3 | Partial | ol | sol | s |  | CONFIRMED | 0.300 |
| f102r1.12.4 | Exact stem | ey | ey |  |  | CANDIDATE | 0.500 |
| f102r1.12.5 | Compound |  | eody |  |  | CANDIDATE | 0.500 |
| f102r1.12.6 | Stem + suffix | streod | streod |  |  | CANDIDATE | 0.950 |
| f102r1.12.7 | Partial | cstr | ocstrhe | o | he | CANDIDATE | 0.850 |
| f102r1.12.8 | Partial | ol | ole |  | e | CONFIRMED | 0.550 |

#### Complete token provenance

```json
[
  {
    "id": "f102r1.12.1",
    "eva": "dcheo",
    "zfd": "dheo",
    "operator": null,
    "operator_type": null,
    "stem": "dheo",
    "stem_known": true,
    "stem_gloss": "that which/the one",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[RESIDUE:d][STEM:heo=that which/the one]",
    "croatian": "[d]ono što",
    "english": "[d] that which/the one",
    "confidence": 0.25,
    "rewrites": [
      "mid-word: ch→h"
    ],
    "notes": [
      "Stem: state_that_which (CANDIDATE)"
    ],
    "match_type": "partial",
    "matched_form": "heo",
    "matched_croatian": "ono što",
    "matched_category": "grammar",
    "matched_status": "CANDIDATE",
    "matched_source": "morphology_analysis",
    "stem_surface": "dheo",
    "unmatched_prefix": "d",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.12.2",
    "eva": "qockhy",
    "zfd": "kocstrhi",
    "operator": "ko",
    "operator_type": "relative",
    "stem": "cstr",
    "stem_known": true,
    "stem_gloss": "concentrated preparation",
    "suffix": "i",
    "suffix_semantic": "adjectival",
    "expansion": "[OP:ko][STEM:cstr=concentrated preparation][RESIDUE:h][SUF:i=adjectival]",
    "croatian": "kozgušnjeni[h]i",
    "english": "which concentrated preparation [h]",
    "confidence": 0.8500000000000001,
    "rewrites": [
      "operator: qo→ko",
      "mid-word: ck→cst",
      "gallows: t→tr (known stem)",
      "suffix: y→i (adjective marker)"
    ],
    "notes": [
      "Operator which/that/quantity (CONFIRMED)",
      "Stem: cstr (CANDIDATE)"
    ],
    "match_type": "partial",
    "matched_form": "cstr",
    "matched_croatian": "zgušnjeni",
    "matched_category": "preparation",
    "matched_status": "CANDIDATE",
    "matched_source": "morphology_analysis",
    "stem_surface": "cstrh",
    "unmatched_prefix": "",
    "unmatched_suffix": "h",
    "compound_parts": []
  },
  {
    "id": "f102r1.12.3",
    "eva": "sol",
    "zfd": "sol",
    "operator": null,
    "operator_type": null,
    "stem": "sol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[RESIDUE:s][STEM:ol=oil]",
    "croatian": "[s]ulje",
    "english": "[s] oil",
    "confidence": 0.3,
    "rewrites": [],
    "notes": [
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "sol",
    "unmatched_prefix": "s",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.12.4",
    "eva": "sheey",
    "zfd": "šey",
    "operator": "š",
    "operator_type": "comitative",
    "stem": "ey",
    "stem_known": true,
    "stem_gloss": "liquid/fluid",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:š][STEM:ey=liquid/fluid]",
    "croatian": "š[ey]",
    "english": "with liquid/fluid",
    "confidence": 0.5,
    "rewrites": [
      "operator: sh→š",
      "mid-word: ee→e"
    ],
    "notes": [
      "Operator with/soak (CONFIRMED)",
      "Stem: ey (CANDIDATE)"
    ],
    "match_type": "exact_stem",
    "matched_form": "ey",
    "matched_croatian": "",
    "matched_category": "preparation",
    "matched_status": "CANDIDATE",
    "matched_source": "corpus_frequency",
    "stem_surface": "ey",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.12.5",
    "eva": "okeody",
    "zfd": "osteody",
    "operator": "ost",
    "operator_type": "vessel",
    "stem": "eody",
    "stem_known": true,
    "stem_gloss": "vessel stalk adjectival",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:ost][COMPOUND:eody=vessel stalk adjectival]",
    "croatian": "ost[eody]",
    "english": "vessel [eody]",
    "confidence": 0.5,
    "rewrites": [
      "operator: ok→ost"
    ],
    "notes": [
      "Operator vessel/container (CONFIRMED)",
      "Compound: [ok=vessel/container] e [od=stalk/stem] [y=adjectival/state]",
      "Stem: compound (CANDIDATE)"
    ],
    "match_type": "compound",
    "matched_form": "",
    "matched_croatian": "",
    "matched_category": "compound",
    "matched_status": "CANDIDATE",
    "matched_source": "unified_lexicon_v2.json",
    "stem_surface": "eody",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": [
      {
        "eva": "ok",
        "type": "operator",
        "gloss": "vessel/container",
        "content": true
      },
      {
        "eva": "e",
        "type": "binding",
        "gloss": "case vowel",
        "content": false
      },
      {
        "eva": "od",
        "type": "stem",
        "gloss": "stalk/stem",
        "content": true
      },
      {
        "eva": "y",
        "type": "suffixe",
        "gloss": "adjectival/state",
        "content": true
      }
    ]
  },
  {
    "id": "f102r1.12.6",
    "eva": "qokeodol",
    "zfd": "kostreodol",
    "operator": "ko",
    "operator_type": "relative",
    "stem": "streod",
    "stem_known": true,
    "stem_gloss": "storax/resin preparation",
    "suffix": "ol",
    "suffix_semantic": "oil_related",
    "expansion": "[OP:ko][STEM:streod=storax/resin preparation][SUF:ol=oil_related]",
    "croatian": "kosmolaol",
    "english": "which storax/resin preparation",
    "confidence": 0.9500000000000001,
    "rewrites": [
      "operator: qo→ko",
      "gallows: k→st (known stem)",
      "gallows: t→tr (known stem)",
      "suffix: ol→ol (oil/oily)"
    ],
    "notes": [
      "Operator which/that/quantity (CONFIRMED)",
      "Stem: streod (CANDIDATE)"
    ],
    "match_type": "suffix",
    "matched_form": "streod",
    "matched_croatian": "smola",
    "matched_category": "ingredient",
    "matched_status": "CANDIDATE",
    "matched_source": "morphology_analysis",
    "stem_surface": "streod",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.12.7",
    "eva": "shockhey",
    "zfd": "šocstrhei",
    "operator": "š",
    "operator_type": "comitative",
    "stem": "cstr",
    "stem_known": true,
    "stem_gloss": "concentrated preparation",
    "suffix": "i",
    "suffix_semantic": "adjectival",
    "expansion": "[OP:š][RESIDUE:o][STEM:cstr=concentrated preparation][RESIDUE:he][SUF:i=adjectival]",
    "croatian": "š[o]zgušnjeni[he]i",
    "english": "with [o] concentrated preparation [he]",
    "confidence": 0.8500000000000001,
    "rewrites": [
      "operator: sh→š",
      "mid-word: ck→cst",
      "gallows: t→tr (known stem)",
      "suffix: y→i (adjective marker)"
    ],
    "notes": [
      "Operator with/soak (CONFIRMED)",
      "Stem: cstr (CANDIDATE)"
    ],
    "match_type": "partial",
    "matched_form": "cstr",
    "matched_croatian": "zgušnjeni",
    "matched_category": "preparation",
    "matched_status": "CANDIDATE",
    "matched_source": "morphology_analysis",
    "stem_surface": "ocstrhe",
    "unmatched_prefix": "o",
    "unmatched_suffix": "he",
    "compound_parts": []
  },
  {
    "id": "f102r1.12.8",
    "eva": "oleeol",
    "zfd": "oleol",
    "operator": null,
    "operator_type": null,
    "stem": "ol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": "ol",
    "suffix_semantic": "oil_related",
    "expansion": "[STEM:ol=oil][RESIDUE:e][SUF:ol=oil_related]",
    "croatian": "ulje[e]ol",
    "english": "oil [e]",
    "confidence": 0.55,
    "rewrites": [
      "mid-word: ee→e",
      "suffix: ol→ol (oil/oily)"
    ],
    "notes": [
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "ole",
    "unmatched_prefix": "",
    "unmatched_suffix": "e",
    "compound_parts": []
  }
]
```

### f102r1.13,@P0;H

| Layer | Text |
| --- | --- |
| EVA | teesody qoeol olcheor qokey okshey qokeol sheo folcfhhy |
| ZFD | tresody koeol olheor kostrey ostšei kostreol šeo plrolcplrhhi |
| Croatian | \[tresody\] ko\[e\]ulje ulje\[he\]or ko\[str\]\[ey\] ostsa timi ko\[stre\]ulje š\[eo\] prašak\[olcplrhh\]i |
| English gloss | \[tresody\] which \[e\] oil oil \[he\] which \[str\] liquid/fluid vessel with the (comitative+article) which \[stre\] oil with \[eo\] powder/pulverize \[olcplrhh\] |

| Token | Match | Matched form | Stem surface | Prefix residue | Suffix residue | Lexicon status | Parser score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| f102r1.13.1 | Compound |  | tresody |  |  | CANDIDATE | 0.400 |
| f102r1.13.2 | Partial | ol | eol | e |  | CONFIRMED | 0.550 |
| f102r1.13.3 | Partial | ol | olhe |  | he | CONFIRMED | 0.550 |
| f102r1.13.4 | Partial | ey | strey | str |  | CANDIDATE | 0.800 |
| f102r1.13.5 | Stem + suffix | še | še |  |  | CANDIDATE | 0.650 |
| f102r1.13.6 | Partial | ol | streol | stre |  | CONFIRMED | 0.950 |
| f102r1.13.7 | Compound |  | eo |  |  | CANDIDATE | 0.500 |
| f102r1.13.8 | Partial | plr | plrolcplrhh |  | olcplrhh | CANDIDATE | 0.700 |

#### Complete token provenance

```json
[
  {
    "id": "f102r1.13.1",
    "eva": "teesody",
    "zfd": "tresody",
    "operator": null,
    "operator_type": null,
    "stem": "tresody",
    "stem_known": true,
    "stem_gloss": "with active process (variant)",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[COMPOUND:tresody=with active process (variant)]",
    "croatian": "[tresody]",
    "english": "[tresody]",
    "confidence": 0.4,
    "rewrites": [
      "mid-word: ee→e",
      "gallows: t→tr (unverified)"
    ],
    "notes": [
      "Compound: t [ee=(intensifier)] [so=with/together (varia] [dy=active process (vari]",
      "Stem: compound (CANDIDATE)"
    ],
    "match_type": "compound",
    "matched_form": "",
    "matched_croatian": "",
    "matched_category": "compound",
    "matched_status": "CANDIDATE",
    "matched_source": "unified_lexicon_v2.json",
    "stem_surface": "tresody",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": [
      {
        "eva": "t",
        "type": "gallows",
        "gloss": "compound marker (tr-)",
        "content": false
      },
      {
        "eva": "ee",
        "type": "stem",
        "gloss": "(intensifier)",
        "content": true
      },
      {
        "eva": "so",
        "type": "operator",
        "gloss": "with/together (variant)",
        "content": true
      },
      {
        "eva": "dy",
        "type": "suffixe",
        "gloss": "active process (variant)",
        "content": true
      }
    ]
  },
  {
    "id": "f102r1.13.2",
    "eva": "qoeol",
    "zfd": "koeol",
    "operator": "ko",
    "operator_type": "relative",
    "stem": "eol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:ko][RESIDUE:e][STEM:ol=oil]",
    "croatian": "ko[e]ulje",
    "english": "which [e] oil",
    "confidence": 0.55,
    "rewrites": [
      "operator: qo→ko"
    ],
    "notes": [
      "Operator which/that/quantity (CONFIRMED)",
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "eol",
    "unmatched_prefix": "e",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.13.3",
    "eva": "olcheor",
    "zfd": "olheor",
    "operator": null,
    "operator_type": null,
    "stem": "ol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": "or",
    "suffix_semantic": "oil_related",
    "expansion": "[STEM:ol=oil][RESIDUE:he][SUF:or=oil_related]",
    "croatian": "ulje[he]or",
    "english": "oil [he]",
    "confidence": 0.55,
    "rewrites": [
      "mid-word: ch→h",
      "suffix: or→or (oil)"
    ],
    "notes": [
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "olhe",
    "unmatched_prefix": "",
    "unmatched_suffix": "he",
    "compound_parts": []
  },
  {
    "id": "f102r1.13.4",
    "eva": "qokey",
    "zfd": "kostrey",
    "operator": "ko",
    "operator_type": "relative",
    "stem": "strey",
    "stem_known": true,
    "stem_gloss": "liquid/fluid",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:ko][RESIDUE:str][STEM:ey=liquid/fluid]",
    "croatian": "ko[str][ey]",
    "english": "which [str] liquid/fluid",
    "confidence": 0.8,
    "rewrites": [
      "operator: qo→ko",
      "gallows: k→st (known stem)",
      "gallows: t→tr (known stem)"
    ],
    "notes": [
      "Operator which/that/quantity (CONFIRMED)",
      "Stem: ey (CANDIDATE)"
    ],
    "match_type": "partial",
    "matched_form": "ey",
    "matched_croatian": "",
    "matched_category": "preparation",
    "matched_status": "CANDIDATE",
    "matched_source": "corpus_frequency",
    "stem_surface": "strey",
    "unmatched_prefix": "str",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.13.5",
    "eva": "okshey",
    "zfd": "ostšei",
    "operator": "ost",
    "operator_type": "vessel",
    "stem": "še",
    "stem_known": true,
    "stem_gloss": "with the (comitative+article)",
    "suffix": "i",
    "suffix_semantic": "adjectival",
    "expansion": "[OP:ost][STEM:še=with the (comitative+article)][SUF:i=adjectival]",
    "croatian": "ostsa timi",
    "english": "vessel with the (comitative+article)",
    "confidence": 0.65,
    "rewrites": [
      "operator: ok→ost",
      "mid-word: sh→š",
      "suffix: y→i (adjective marker)"
    ],
    "notes": [
      "Operator vessel/container (CONFIRMED)",
      "Stem: state_with_the (CANDIDATE)"
    ],
    "match_type": "suffix",
    "matched_form": "še",
    "matched_croatian": "sa tim",
    "matched_category": "grammar",
    "matched_status": "CANDIDATE",
    "matched_source": "morphology_analysis",
    "stem_surface": "še",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.13.6",
    "eva": "qokeol",
    "zfd": "kostreol",
    "operator": "ko",
    "operator_type": "relative",
    "stem": "streol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:ko][RESIDUE:stre][STEM:ol=oil]",
    "croatian": "ko[stre]ulje",
    "english": "which [stre] oil",
    "confidence": 0.95,
    "rewrites": [
      "operator: qo→ko",
      "gallows: k→st (known stem)",
      "gallows: t→tr (known stem)"
    ],
    "notes": [
      "Operator which/that/quantity (CONFIRMED)",
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "streol",
    "unmatched_prefix": "stre",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.13.7",
    "eva": "sheo",
    "zfd": "šeo",
    "operator": "š",
    "operator_type": "comitative",
    "stem": "eo",
    "stem_known": true,
    "stem_gloss": "state",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:š][COMPOUND:eo=state]",
    "croatian": "š[eo]",
    "english": "with [eo]",
    "confidence": 0.5,
    "rewrites": [
      "operator: sh→š"
    ],
    "notes": [
      "Operator with/soak (CONFIRMED)",
      "Compound: [s=~15] [heo=state/result (extend]",
      "Stem: compound (CANDIDATE)"
    ],
    "match_type": "compound",
    "matched_form": "",
    "matched_croatian": "",
    "matched_category": "compound",
    "matched_status": "CANDIDATE",
    "matched_source": "unified_lexicon_v2.json",
    "stem_surface": "eo",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": [
      {
        "eva": "s",
        "type": "suffixe",
        "gloss": "~15",
        "content": true
      },
      {
        "eva": "heo",
        "type": "state_marker",
        "gloss": "state/result (extended)",
        "content": true
      }
    ]
  },
  {
    "id": "f102r1.13.8",
    "eva": "folcfhhy",
    "zfd": "plrolcplrhhi",
    "operator": null,
    "operator_type": null,
    "stem": "plr",
    "stem_known": true,
    "stem_gloss": "powder/pulverize",
    "suffix": "i",
    "suffix_semantic": "adjectival",
    "expansion": "[STEM:plr=powder/pulverize][RESIDUE:olcplrhh][SUF:i=adjectival]",
    "croatian": "prašak[olcplrhh]i",
    "english": "powder/pulverize [olcplrhh]",
    "confidence": 0.7000000000000001,
    "rewrites": [
      "gallows: f→pr (known stem)",
      "gallows: p→pl (known stem)",
      "suffix: y→i (adjective marker)"
    ],
    "notes": [
      "Stem: pulv (CANDIDATE)"
    ],
    "match_type": "partial",
    "matched_form": "plr",
    "matched_croatian": "prašak",
    "matched_category": "preparation",
    "matched_status": "CANDIDATE",
    "matched_source": "MS650_cross_reference",
    "stem_surface": "plrolcplrhh",
    "unmatched_prefix": "",
    "unmatched_suffix": "olcplrhh",
    "compound_parts": []
  }
]
```

### f102r1.14,+P0;H

| Layer | Text |
| --- | --- |
| EVA | doeey keeol qokeo daor shey qoteol okol chos sor oeeaiin |
| ZFD | doey streol kostreo daor šey kotreol ostol hos sor oeain |
| Croatian | \[do\]\[ey\] \[stre\]ulje ko\[streo\] daulje š\[ey\] ko\[tre\]ulje ostulje h\[os\] \[s\]ulje \[oe\]stvar |
| English gloss | \[do\] liquid/fluid \[stre\] oil which \[streo\] dose oil with liquid/fluid which \[tre\] oil vessel oil combine \[os\] \[s\] oil \[oe\] substance/thing |

| Token | Match | Matched form | Stem surface | Prefix residue | Suffix residue | Lexicon status | Parser score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| f102r1.14.1 | Partial | ey | doey | do |  | CANDIDATE | 0.250 |
| f102r1.14.2 | Partial | ol | streol | stre |  | CONFIRMED | 0.800 |
| f102r1.14.3 | Compound |  | streo |  |  | CANDIDATE | 0.600 |
| f102r1.14.4 | Exact stem | or | or |  |  | CONFIRMED | 0.550 |
| f102r1.14.5 | Exact stem | ey | ey |  |  | CANDIDATE | 0.400 |
| f102r1.14.6 | Partial | ol | treol | tre |  | CONFIRMED | 0.750 |
| f102r1.14.7 | Exact stem | ol | ol |  |  | CONFIRMED | 0.550 |
| f102r1.14.8 | Compound |  | os |  |  | CANDIDATE | 0.500 |
| f102r1.14.9 | Partial | or | sor | s |  | CONFIRMED | 0.300 |
| f102r1.14.10 | Partial | ain | oeain | oe |  | CONFIRMED | 0.400 |

#### Complete token provenance

```json
[
  {
    "id": "f102r1.14.1",
    "eva": "doeey",
    "zfd": "doey",
    "operator": null,
    "operator_type": null,
    "stem": "doey",
    "stem_known": true,
    "stem_gloss": "liquid/fluid",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[RESIDUE:do][STEM:ey=liquid/fluid]",
    "croatian": "[do][ey]",
    "english": "[do] liquid/fluid",
    "confidence": 0.25,
    "rewrites": [
      "mid-word: ee→e"
    ],
    "notes": [
      "Stem: ey (CANDIDATE)"
    ],
    "match_type": "partial",
    "matched_form": "ey",
    "matched_croatian": "",
    "matched_category": "preparation",
    "matched_status": "CANDIDATE",
    "matched_source": "corpus_frequency",
    "stem_surface": "doey",
    "unmatched_prefix": "do",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.14.2",
    "eva": "keeol",
    "zfd": "streol",
    "operator": null,
    "operator_type": null,
    "stem": "streol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[RESIDUE:stre][STEM:ol=oil]",
    "croatian": "[stre]ulje",
    "english": "[stre] oil",
    "confidence": 0.8,
    "rewrites": [
      "mid-word: ee→e",
      "gallows: k→st (known stem)",
      "gallows: t→tr (known stem)"
    ],
    "notes": [
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "streol",
    "unmatched_prefix": "stre",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.14.3",
    "eva": "qokeo",
    "zfd": "kostreo",
    "operator": "ko",
    "operator_type": "relative",
    "stem": "streo",
    "stem_known": true,
    "stem_gloss": "measure vessel (short)",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:ko][COMPOUND:streo=measure vessel (short)]",
    "croatian": "ko[streo]",
    "english": "which [streo]",
    "confidence": 0.6,
    "rewrites": [
      "operator: qo→ko",
      "gallows: k→st (unverified)",
      "gallows: t→tr (unverified)"
    ],
    "notes": [
      "Operator which/that/quantity (CONFIRMED)",
      "Compound: [qo=measure/quantify] [k=vessel (short)] e o",
      "Stem: compound (CANDIDATE)"
    ],
    "match_type": "compound",
    "matched_form": "",
    "matched_croatian": "",
    "matched_category": "compound",
    "matched_status": "CANDIDATE",
    "matched_source": "unified_lexicon_v2.json",
    "stem_surface": "streo",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": [
      {
        "eva": "qo",
        "type": "operator",
        "gloss": "measure/quantify",
        "content": true
      },
      {
        "eva": "k",
        "type": "stem",
        "gloss": "vessel (short)",
        "content": true
      },
      {
        "eva": "e",
        "type": "binding",
        "gloss": "case vowel",
        "content": false
      },
      {
        "eva": "o",
        "type": "binding",
        "gloss": "binding vowel",
        "content": false
      }
    ]
  },
  {
    "id": "f102r1.14.4",
    "eva": "daor",
    "zfd": "daor",
    "operator": "da",
    "operator_type": "dative",
    "stem": "or",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:da][STEM:or=oil]",
    "croatian": "daulje",
    "english": "dose oil",
    "confidence": 0.55,
    "rewrites": [
      "operator: da→da"
    ],
    "notes": [
      "Operator dose/give/add (CONFIRMED)",
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "exact_stem",
    "matched_form": "or",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "or",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.14.5",
    "eva": "shey",
    "zfd": "šey",
    "operator": "š",
    "operator_type": "comitative",
    "stem": "ey",
    "stem_known": true,
    "stem_gloss": "liquid/fluid",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:š][STEM:ey=liquid/fluid]",
    "croatian": "š[ey]",
    "english": "with liquid/fluid",
    "confidence": 0.4,
    "rewrites": [
      "operator: sh→š"
    ],
    "notes": [
      "Operator with/soak (CONFIRMED)",
      "Stem: ey (CANDIDATE)"
    ],
    "match_type": "exact_stem",
    "matched_form": "ey",
    "matched_croatian": "",
    "matched_category": "preparation",
    "matched_status": "CANDIDATE",
    "matched_source": "corpus_frequency",
    "stem_surface": "ey",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.14.6",
    "eva": "qoteol",
    "zfd": "kotreol",
    "operator": "ko",
    "operator_type": "relative",
    "stem": "treol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:ko][RESIDUE:tre][STEM:ol=oil]",
    "croatian": "ko[tre]ulje",
    "english": "which [tre] oil",
    "confidence": 0.75,
    "rewrites": [
      "operator: qo→ko",
      "gallows: t→tr (known stem)"
    ],
    "notes": [
      "Operator which/that/quantity (CONFIRMED)",
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "treol",
    "unmatched_prefix": "tre",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.14.7",
    "eva": "okol",
    "zfd": "ostol",
    "operator": "ost",
    "operator_type": "vessel",
    "stem": "ol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:ost][STEM:ol=oil]",
    "croatian": "ostulje",
    "english": "vessel oil",
    "confidence": 0.55,
    "rewrites": [
      "operator: ok→ost"
    ],
    "notes": [
      "Operator vessel/container (CONFIRMED)",
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "exact_stem",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "ol",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.14.8",
    "eva": "chos",
    "zfd": "hos",
    "operator": "h",
    "operator_type": "action",
    "stem": "os",
    "stem_known": true,
    "stem_gloss": "combine",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:h][COMPOUND:os=combine]",
    "croatian": "h[os]",
    "english": "combine [os]",
    "confidence": 0.5,
    "rewrites": [
      "operator: ch→h"
    ],
    "notes": [
      "Operator combine/cook (CONFIRMED)",
      "Compound: [ch=combine/cook] o [s=~15]",
      "Stem: compound (CANDIDATE)"
    ],
    "match_type": "compound",
    "matched_form": "",
    "matched_croatian": "",
    "matched_category": "compound",
    "matched_status": "CANDIDATE",
    "matched_source": "unified_lexicon_v2.json",
    "stem_surface": "os",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": [
      {
        "eva": "ch",
        "type": "operator",
        "gloss": "combine/cook",
        "content": true
      },
      {
        "eva": "o",
        "type": "binding",
        "gloss": "binding vowel",
        "content": false
      },
      {
        "eva": "s",
        "type": "suffixe",
        "gloss": "~15",
        "content": true
      }
    ]
  },
  {
    "id": "f102r1.14.9",
    "eva": "sor",
    "zfd": "sor",
    "operator": null,
    "operator_type": null,
    "stem": "sor",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[RESIDUE:s][STEM:or=oil]",
    "croatian": "[s]ulje",
    "english": "[s] oil",
    "confidence": 0.3,
    "rewrites": [],
    "notes": [
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "or",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "sor",
    "unmatched_prefix": "s",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.14.10",
    "eva": "oeeaiin",
    "zfd": "oeain",
    "operator": null,
    "operator_type": null,
    "stem": "oeain",
    "stem_known": true,
    "stem_gloss": "substance/thing",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[RESIDUE:oe][STEM:ain=substance/thing]",
    "croatian": "[oe]stvar",
    "english": "[oe] substance/thing",
    "confidence": 0.4,
    "rewrites": [
      "mid-word: ee→e",
      "mid-word: ii→i"
    ],
    "notes": [
      "Stem: substance (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ain",
    "matched_croatian": "stvar",
    "matched_category": "grammar",
    "matched_status": "CONFIRMED",
    "matched_source": "morphology_analysis",
    "stem_surface": "oeain",
    "unmatched_prefix": "oe",
    "unmatched_suffix": "",
    "compound_parts": []
  }
]
```

### f102r1.15,+P0;H

| Layer | Text |
| --- | --- |
| EVA | or chol daiin dykeor sheey qokeody dor os ykeey kam |
| ZFD | or chol dain dystreor šey kostreodi dor os ystrey stram |
| Croatian | ulje brasno da\[in\] \[dystre\]ulje š\[ey\] kosmolai \[d\]ulje \[os\] \[ystr\]\[ey\] \[s\]\[tram\] |
| English gloss | oil flour/grain dose \[in\] \[dystre\] oil with liquid/fluid which storax/resin preparation \[d\] oil \[os\] \[ystr\] liquid/fluid \[s\] by compound means |

| Token | Match | Matched form | Stem surface | Prefix residue | Suffix residue | Lexicon status | Parser score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| f102r1.15.1 | Whole word | or | or |  |  | CONFIRMED | 0.300 |
| f102r1.15.2 | Whole word | chol | chol |  |  | CONFIRMED | 0.300 |
| f102r1.15.3 | Compound |  | in |  |  | CANDIDATE | 0.600 |
| f102r1.15.4 | Partial | or | dystreor | dystre |  | CONFIRMED | 0.700 |
| f102r1.15.5 | Exact stem | ey | ey |  |  | CANDIDATE | 0.500 |
| f102r1.15.6 | Stem + suffix | streod | streod |  |  | CANDIDATE | 0.800 |
| f102r1.15.7 | Partial | or | dor | d |  | CONFIRMED | 0.300 |
| f102r1.15.8 | Compound |  | os |  |  | CANDIDATE | 0.250 |
| f102r1.15.9 | Partial | ey | ystrey | ystr |  | CANDIDATE | 0.650 |
| f102r1.15.10 | Partial | tram | stram | s |  | CANDIDATE | 0.400 |

#### Complete token provenance

```json
[
  {
    "id": "f102r1.15.1",
    "eva": "or",
    "zfd": "or",
    "operator": null,
    "operator_type": null,
    "stem": "or",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[STEM:or=oil]",
    "croatian": "ulje",
    "english": "oil",
    "confidence": 0.3,
    "rewrites": [],
    "notes": [
      "Stem: oil (CONFIRMED) [whole-word]"
    ],
    "match_type": "whole_word",
    "matched_form": "or",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "or",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.15.2",
    "eva": "chol",
    "zfd": "chol",
    "operator": null,
    "operator_type": null,
    "stem": "chol",
    "stem_known": true,
    "stem_gloss": "flour/grain",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[STEM:chol=flour/grain]",
    "croatian": "brasno",
    "english": "flour/grain",
    "confidence": 0.3,
    "rewrites": [],
    "notes": [
      "Stem: flour (CONFIRMED) [whole-word]"
    ],
    "match_type": "whole_word",
    "matched_form": "chol",
    "matched_croatian": "brasno",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "chol",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.15.3",
    "eva": "daiin",
    "zfd": "dain",
    "operator": "da",
    "operator_type": "dative",
    "stem": "in",
    "stem_known": true,
    "stem_gloss": "Add (extended)",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:da][COMPOUND:in=Add (extended)]",
    "croatian": "da[in]",
    "english": "dose [in]",
    "confidence": 0.6,
    "rewrites": [
      "operator: da→da",
      "mid-word: ii→i"
    ],
    "notes": [
      "Operator dose/give/add (CONFIRMED)",
      "Compound: [daiin=Add (extended)]",
      "Stem: compound (CANDIDATE)"
    ],
    "match_type": "compound",
    "matched_form": "",
    "matched_croatian": "",
    "matched_category": "compound",
    "matched_status": "CANDIDATE",
    "matched_source": "unified_lexicon_v2.json",
    "stem_surface": "in",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": [
      {
        "eva": "daiin",
        "type": "stem",
        "gloss": "Add (extended)",
        "content": true
      }
    ]
  },
  {
    "id": "f102r1.15.4",
    "eva": "dykeor",
    "zfd": "dystreor",
    "operator": null,
    "operator_type": null,
    "stem": "dystreor",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[RESIDUE:dystre][STEM:or=oil]",
    "croatian": "[dystre]ulje",
    "english": "[dystre] oil",
    "confidence": 0.7,
    "rewrites": [
      "gallows: k→st (known stem)",
      "gallows: t→tr (known stem)"
    ],
    "notes": [
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "or",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "dystreor",
    "unmatched_prefix": "dystre",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.15.5",
    "eva": "sheey",
    "zfd": "šey",
    "operator": "š",
    "operator_type": "comitative",
    "stem": "ey",
    "stem_known": true,
    "stem_gloss": "liquid/fluid",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:š][STEM:ey=liquid/fluid]",
    "croatian": "š[ey]",
    "english": "with liquid/fluid",
    "confidence": 0.5,
    "rewrites": [
      "operator: sh→š",
      "mid-word: ee→e"
    ],
    "notes": [
      "Operator with/soak (CONFIRMED)",
      "Stem: ey (CANDIDATE)"
    ],
    "match_type": "exact_stem",
    "matched_form": "ey",
    "matched_croatian": "",
    "matched_category": "preparation",
    "matched_status": "CANDIDATE",
    "matched_source": "corpus_frequency",
    "stem_surface": "ey",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.15.6",
    "eva": "qokeody",
    "zfd": "kostreodi",
    "operator": "ko",
    "operator_type": "relative",
    "stem": "streod",
    "stem_known": true,
    "stem_gloss": "storax/resin preparation",
    "suffix": "i",
    "suffix_semantic": "adjectival",
    "expansion": "[OP:ko][STEM:streod=storax/resin preparation][SUF:i=adjectival]",
    "croatian": "kosmolai",
    "english": "which storax/resin preparation",
    "confidence": 0.8,
    "rewrites": [
      "operator: qo→ko",
      "gallows: k→st (unverified)",
      "gallows: t→tr (known stem)",
      "suffix: y→i (adjective marker)"
    ],
    "notes": [
      "Operator which/that/quantity (CONFIRMED)",
      "Stem: streod (CANDIDATE)"
    ],
    "match_type": "suffix",
    "matched_form": "streod",
    "matched_croatian": "smola",
    "matched_category": "ingredient",
    "matched_status": "CANDIDATE",
    "matched_source": "morphology_analysis",
    "stem_surface": "streod",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.15.7",
    "eva": "dor",
    "zfd": "dor",
    "operator": null,
    "operator_type": null,
    "stem": "dor",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[RESIDUE:d][STEM:or=oil]",
    "croatian": "[d]ulje",
    "english": "[d] oil",
    "confidence": 0.3,
    "rewrites": [],
    "notes": [
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "or",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "dor",
    "unmatched_prefix": "d",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.15.8",
    "eva": "os",
    "zfd": "os",
    "operator": null,
    "operator_type": null,
    "stem": "os",
    "stem_known": true,
    "stem_gloss": "(compound)",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[COMPOUND:os=(compound)]",
    "croatian": "[os]",
    "english": "[os]",
    "confidence": 0.25,
    "rewrites": [],
    "notes": [
      "Compound: o [s=~15]",
      "Stem: compound (CANDIDATE)"
    ],
    "match_type": "compound",
    "matched_form": "",
    "matched_croatian": "",
    "matched_category": "compound",
    "matched_status": "CANDIDATE",
    "matched_source": "unified_lexicon_v2.json",
    "stem_surface": "os",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": [
      {
        "eva": "o",
        "type": "binding",
        "gloss": "binding vowel",
        "content": false
      },
      {
        "eva": "s",
        "type": "suffixe",
        "gloss": "~15",
        "content": true
      }
    ]
  },
  {
    "id": "f102r1.15.9",
    "eva": "ykeey",
    "zfd": "ystrey",
    "operator": null,
    "operator_type": null,
    "stem": "ystrey",
    "stem_known": true,
    "stem_gloss": "liquid/fluid",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[RESIDUE:ystr][STEM:ey=liquid/fluid]",
    "croatian": "[ystr][ey]",
    "english": "[ystr] liquid/fluid",
    "confidence": 0.65,
    "rewrites": [
      "mid-word: ee→e",
      "gallows: k→st (known stem)",
      "gallows: t→tr (known stem)"
    ],
    "notes": [
      "Stem: ey (CANDIDATE)"
    ],
    "match_type": "partial",
    "matched_form": "ey",
    "matched_croatian": "",
    "matched_category": "preparation",
    "matched_status": "CANDIDATE",
    "matched_source": "corpus_frequency",
    "stem_surface": "ystrey",
    "unmatched_prefix": "ystr",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.15.10",
    "eva": "kam",
    "zfd": "stram",
    "operator": null,
    "operator_type": null,
    "stem": "stram",
    "stem_known": true,
    "stem_gloss": "by compound means",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[RESIDUE:s][STEM:tram=by compound means]",
    "croatian": "[s][tram]",
    "english": "[s] by compound means",
    "confidence": 0.4,
    "rewrites": [
      "gallows: k→st (unverified)",
      "gallows: t→tr (known stem)"
    ],
    "notes": [
      "Stem: tram (CANDIDATE)"
    ],
    "match_type": "partial",
    "matched_form": "tram",
    "matched_croatian": "",
    "matched_category": "grammar",
    "matched_status": "CANDIDATE",
    "matched_source": "morphology_analysis",
    "stem_surface": "stram",
    "unmatched_prefix": "s",
    "unmatched_suffix": "",
    "compound_parts": []
  }
]
```

### f102r1.16,+P0;H

| Layer | Text |
| --- | --- |
| EVA | ddor chordom soraiin ykeey dy okeol doeoeas saral dor |
| ZFD | ddor hordom sorain ystrey dy osteol doeoeas saral dor |
| Croatian | \[dd\]ulje hulje\[d\]om \[s\]ulje\[ai\]n \[ystr\]\[ey\] \[dy\] ost\[e\]ulje \[doeoeas\] solal \[d\]ulje |
| English gloss | \[dd\] oil with combine oil \[d\] \[s\] oil \[ai\] \[ystr\] liquid/fluid \[dy\] vessel \[e\] oil \[doeoeas\] salt \[d\] oil |

| Token | Match | Matched form | Stem surface | Prefix residue | Suffix residue | Lexicon status | Parser score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| f102r1.16.1 | Partial | or | ddor | dd |  | CONFIRMED | 0.300 |
| f102r1.16.2 | Partial | or | ord |  | d | CONFIRMED | 0.700 |
| f102r1.16.3 | Partial | or | sorai | s | ai | CONFIRMED | 0.550 |
| f102r1.16.4 | Partial | ey | ystrey | ystr |  | CANDIDATE | 0.650 |
| f102r1.16.5 | Compound |  | dy |  |  | CANDIDATE | 0.250 |
| f102r1.16.6 | Partial | ol | eol | e |  | CONFIRMED | 0.550 |
| f102r1.16.7 | Compound |  | doeoeas |  |  | CANDIDATE | 0.250 |
| f102r1.16.8 | Stem + suffix | sar | sar |  |  | CONFIRMED | 0.450 |
| f102r1.16.9 | Partial | or | dor | d |  | CONFIRMED | 0.300 |

#### Complete token provenance

```json
[
  {
    "id": "f102r1.16.1",
    "eva": "ddor",
    "zfd": "ddor",
    "operator": null,
    "operator_type": null,
    "stem": "ddor",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[RESIDUE:dd][STEM:or=oil]",
    "croatian": "[dd]ulje",
    "english": "[dd] oil",
    "confidence": 0.3,
    "rewrites": [],
    "notes": [
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "or",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "ddor",
    "unmatched_prefix": "dd",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.16.2",
    "eva": "chordom",
    "zfd": "hordom",
    "operator": "h",
    "operator_type": "action",
    "stem": "or",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": "om",
    "suffix_semantic": "instrumental",
    "expansion": "[OP:h][STEM:or=oil][RESIDUE:d][SUF:om=instrumental]",
    "croatian": "hulje[d]om",
    "english": "with combine oil [d]",
    "confidence": 0.7,
    "rewrites": [
      "operator: ch→h",
      "suffix: om→om (with/by)"
    ],
    "notes": [
      "Operator combine/cook (CONFIRMED)",
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "or",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "ord",
    "unmatched_prefix": "",
    "unmatched_suffix": "d",
    "compound_parts": []
  },
  {
    "id": "f102r1.16.3",
    "eva": "soraiin",
    "zfd": "sorain",
    "operator": null,
    "operator_type": null,
    "stem": "or",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": "n",
    "suffix_semantic": "noun",
    "expansion": "[RESIDUE:s][STEM:or=oil][RESIDUE:ai][SUF:n=noun]",
    "croatian": "[s]ulje[ai]n",
    "english": "[s] oil [ai]",
    "confidence": 0.55,
    "rewrites": [
      "mid-word: ii→i",
      "suffix: n→n (noun ending)"
    ],
    "notes": [
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "or",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "sorai",
    "unmatched_prefix": "s",
    "unmatched_suffix": "ai",
    "compound_parts": []
  },
  {
    "id": "f102r1.16.4",
    "eva": "ykeey",
    "zfd": "ystrey",
    "operator": null,
    "operator_type": null,
    "stem": "ystrey",
    "stem_known": true,
    "stem_gloss": "liquid/fluid",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[RESIDUE:ystr][STEM:ey=liquid/fluid]",
    "croatian": "[ystr][ey]",
    "english": "[ystr] liquid/fluid",
    "confidence": 0.65,
    "rewrites": [
      "mid-word: ee→e",
      "gallows: k→st (known stem)",
      "gallows: t→tr (known stem)"
    ],
    "notes": [
      "Stem: ey (CANDIDATE)"
    ],
    "match_type": "partial",
    "matched_form": "ey",
    "matched_croatian": "",
    "matched_category": "preparation",
    "matched_status": "CANDIDATE",
    "matched_source": "corpus_frequency",
    "stem_surface": "ystrey",
    "unmatched_prefix": "ystr",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.16.5",
    "eva": "dy",
    "zfd": "dy",
    "operator": null,
    "operator_type": null,
    "stem": "dy",
    "stem_known": true,
    "stem_gloss": "active process (variant)",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[COMPOUND:dy=active process (variant)]",
    "croatian": "[dy]",
    "english": "[dy]",
    "confidence": 0.25,
    "rewrites": [],
    "notes": [
      "Compound: [dy=active process (vari]",
      "Stem: compound (CANDIDATE)"
    ],
    "match_type": "compound",
    "matched_form": "",
    "matched_croatian": "",
    "matched_category": "compound",
    "matched_status": "CANDIDATE",
    "matched_source": "unified_lexicon_v2.json",
    "stem_surface": "dy",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": [
      {
        "eva": "dy",
        "type": "suffixe",
        "gloss": "active process (variant)",
        "content": true
      }
    ]
  },
  {
    "id": "f102r1.16.6",
    "eva": "okeol",
    "zfd": "osteol",
    "operator": "ost",
    "operator_type": "vessel",
    "stem": "eol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[OP:ost][RESIDUE:e][STEM:ol=oil]",
    "croatian": "ost[e]ulje",
    "english": "vessel [e] oil",
    "confidence": 0.55,
    "rewrites": [
      "operator: ok→ost"
    ],
    "notes": [
      "Operator vessel/container (CONFIRMED)",
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "eol",
    "unmatched_prefix": "e",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.16.7",
    "eva": "doeoeas",
    "zfd": "doeoeas",
    "operator": null,
    "operator_type": null,
    "stem": "doeoeas",
    "stem_known": true,
    "stem_gloss": "(compound)",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[COMPOUND:doeoeas=(compound)]",
    "croatian": "[doeoeas]",
    "english": "[doeoeas]",
    "confidence": 0.25,
    "rewrites": [],
    "notes": [
      "Compound: d o e o e a [s=~15]",
      "Stem: compound (CANDIDATE)"
    ],
    "match_type": "compound",
    "matched_form": "",
    "matched_croatian": "",
    "matched_category": "compound",
    "matched_status": "CANDIDATE",
    "matched_source": "unified_lexicon_v2.json",
    "stem_surface": "doeoeas",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": [
      {
        "eva": "d",
        "type": "suffix_char",
        "gloss": "past/done",
        "content": false
      },
      {
        "eva": "o",
        "type": "binding",
        "gloss": "binding vowel",
        "content": false
      },
      {
        "eva": "e",
        "type": "binding",
        "gloss": "case vowel",
        "content": false
      },
      {
        "eva": "o",
        "type": "binding",
        "gloss": "binding vowel",
        "content": false
      },
      {
        "eva": "e",
        "type": "binding",
        "gloss": "case vowel",
        "content": false
      },
      {
        "eva": "a",
        "type": "binding",
        "gloss": "case vowel",
        "content": false
      },
      {
        "eva": "s",
        "type": "suffixe",
        "gloss": "~15",
        "content": true
      }
    ]
  },
  {
    "id": "f102r1.16.8",
    "eva": "saral",
    "zfd": "saral",
    "operator": null,
    "operator_type": null,
    "stem": "sar",
    "stem_known": true,
    "stem_gloss": "salt",
    "suffix": "al",
    "suffix_semantic": "substance",
    "expansion": "[STEM:sar=salt][SUF:al=substance]",
    "croatian": "solal",
    "english": "salt",
    "confidence": 0.44999999999999996,
    "rewrites": [
      "suffix: al→al (substance)"
    ],
    "notes": [
      "Stem: salt (CONFIRMED)"
    ],
    "match_type": "suffix",
    "matched_form": "sar",
    "matched_croatian": "sol",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "sar",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.16.9",
    "eva": "dor",
    "zfd": "dor",
    "operator": null,
    "operator_type": null,
    "stem": "dor",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[RESIDUE:d][STEM:or=oil]",
    "croatian": "[d]ulje",
    "english": "[d] oil",
    "confidence": 0.3,
    "rewrites": [],
    "notes": [
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "or",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "dor",
    "unmatched_prefix": "d",
    "unmatched_suffix": "",
    "compound_parts": []
  }
]
```

### f102r1.17,+P0;H

| Layer | Text |
| --- | --- |
| EVA | ydar arody oldaiin sody chockhy oly |
| ZFD | ydar arodi oldain sody hocstrhi oli |
| Croatian | \[y\]dar voda\[od\]i ulje\[dai\]n \[sody\] h\[o\]zgušnjeni\[h\]i uljei |
| English gloss | \[y\] gift water \[od\] oil \[dai\] \[sody\] combine \[o\] concentrated preparation \[h\] oil |

| Token | Match | Matched form | Stem surface | Prefix residue | Suffix residue | Lexicon status | Parser score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| f102r1.17.1 | Partial | dar | ydar | y |  | CONFIRMED | 0.300 |
| f102r1.17.2 | Partial | ar | arod |  | od | CONFIRMED | 0.450 |
| f102r1.17.3 | Partial | ol | oldai |  | dai | CONFIRMED | 0.550 |
| f102r1.17.4 | Compound |  | sody |  |  | CANDIDATE | 0.250 |
| f102r1.17.5 | Partial | cstr | ocstrh | o | h | CANDIDATE | 0.850 |
| f102r1.17.6 | Stem + suffix | ol | ol |  |  | CONFIRMED | 0.450 |

#### Complete token provenance

```json
[
  {
    "id": "f102r1.17.1",
    "eva": "ydar",
    "zfd": "ydar",
    "operator": null,
    "operator_type": null,
    "stem": "ydar",
    "stem_known": true,
    "stem_gloss": "gift",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[RESIDUE:y][STEM:dar=gift]",
    "croatian": "[y]dar",
    "english": "[y] gift",
    "confidence": 0.3,
    "rewrites": [],
    "notes": [
      "Stem: gift (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "dar",
    "matched_croatian": "dar",
    "matched_category": "grammar",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "ydar",
    "unmatched_prefix": "y",
    "unmatched_suffix": "",
    "compound_parts": []
  },
  {
    "id": "f102r1.17.2",
    "eva": "arody",
    "zfd": "arodi",
    "operator": null,
    "operator_type": null,
    "stem": "ar",
    "stem_known": true,
    "stem_gloss": "water",
    "suffix": "i",
    "suffix_semantic": "adjectival",
    "expansion": "[STEM:ar=water][RESIDUE:od][SUF:i=adjectival]",
    "croatian": "voda[od]i",
    "english": "water [od]",
    "confidence": 0.44999999999999996,
    "rewrites": [
      "suffix: y→i (adjective marker)"
    ],
    "notes": [
      "Stem: water (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ar",
    "matched_croatian": "voda",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "arod",
    "unmatched_prefix": "",
    "unmatched_suffix": "od",
    "compound_parts": []
  },
  {
    "id": "f102r1.17.3",
    "eva": "oldaiin",
    "zfd": "oldain",
    "operator": null,
    "operator_type": null,
    "stem": "ol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": "n",
    "suffix_semantic": "noun",
    "expansion": "[STEM:ol=oil][RESIDUE:dai][SUF:n=noun]",
    "croatian": "ulje[dai]n",
    "english": "oil [dai]",
    "confidence": 0.55,
    "rewrites": [
      "mid-word: ii→i",
      "suffix: n→n (noun ending)"
    ],
    "notes": [
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "partial",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "oldai",
    "unmatched_prefix": "",
    "unmatched_suffix": "dai",
    "compound_parts": []
  },
  {
    "id": "f102r1.17.4",
    "eva": "sody",
    "zfd": "sody",
    "operator": null,
    "operator_type": null,
    "stem": "sody",
    "stem_known": true,
    "stem_gloss": "with active process (variant)",
    "suffix": null,
    "suffix_semantic": null,
    "expansion": "[COMPOUND:sody=with active process (variant)]",
    "croatian": "[sody]",
    "english": "[sody]",
    "confidence": 0.25,
    "rewrites": [],
    "notes": [
      "Compound: [so=with/together (varia] [dy=active process (vari]",
      "Stem: compound (CANDIDATE)"
    ],
    "match_type": "compound",
    "matched_form": "",
    "matched_croatian": "",
    "matched_category": "compound",
    "matched_status": "CANDIDATE",
    "matched_source": "unified_lexicon_v2.json",
    "stem_surface": "sody",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": [
      {
        "eva": "so",
        "type": "operator",
        "gloss": "with/together (variant)",
        "content": true
      },
      {
        "eva": "dy",
        "type": "suffixe",
        "gloss": "active process (variant)",
        "content": true
      }
    ]
  },
  {
    "id": "f102r1.17.5",
    "eva": "chockhy",
    "zfd": "hocstrhi",
    "operator": "h",
    "operator_type": "action",
    "stem": "cstr",
    "stem_known": true,
    "stem_gloss": "concentrated preparation",
    "suffix": "i",
    "suffix_semantic": "adjectival",
    "expansion": "[OP:h][RESIDUE:o][STEM:cstr=concentrated preparation][RESIDUE:h][SUF:i=adjectival]",
    "croatian": "h[o]zgušnjeni[h]i",
    "english": "combine [o] concentrated preparation [h]",
    "confidence": 0.8500000000000001,
    "rewrites": [
      "operator: ch→h",
      "mid-word: ck→cst",
      "gallows: t→tr (known stem)",
      "suffix: y→i (adjective marker)"
    ],
    "notes": [
      "Operator combine/cook (CONFIRMED)",
      "Stem: cstr (CANDIDATE)"
    ],
    "match_type": "partial",
    "matched_form": "cstr",
    "matched_croatian": "zgušnjeni",
    "matched_category": "preparation",
    "matched_status": "CANDIDATE",
    "matched_source": "morphology_analysis",
    "stem_surface": "ocstrh",
    "unmatched_prefix": "o",
    "unmatched_suffix": "h",
    "compound_parts": []
  },
  {
    "id": "f102r1.17.6",
    "eva": "oly",
    "zfd": "oli",
    "operator": null,
    "operator_type": null,
    "stem": "ol",
    "stem_known": true,
    "stem_gloss": "oil",
    "suffix": "i",
    "suffix_semantic": "adjectival",
    "expansion": "[STEM:ol=oil][SUF:i=adjectival]",
    "croatian": "uljei",
    "english": "oil",
    "confidence": 0.44999999999999996,
    "rewrites": [
      "suffix: y→i (adjective marker)"
    ],
    "notes": [
      "Stem: oil (CONFIRMED)"
    ],
    "match_type": "suffix",
    "matched_form": "ol",
    "matched_croatian": "ulje",
    "matched_category": "ingredient",
    "matched_status": "CONFIRMED",
    "matched_source": "lexicon_v1",
    "stem_surface": "ol",
    "unmatched_prefix": "",
    "unmatched_suffix": "",
    "compound_parts": []
  }
]
```
