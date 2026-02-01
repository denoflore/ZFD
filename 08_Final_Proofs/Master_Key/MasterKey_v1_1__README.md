# Voynich Master Key v1.1 — Unified Table

This update fuses the v1.0 operator mechanics with folio-scale validation and suffix promotions from the 10-folio batch.
It retains the **prefix-operator spine + stem + suffix/nomenclator** model and records manuscript-wide behavior.

## What changed from v1.0 → v1.1
- **Suffix promotions (evidence-based):** `-dy` and `-in` ⇒ **CONFIRMED** (improve template coverage in a majority of folios).
- `-ol` and `-al` ⇒ remain **PROVISIONAL** (section-limited effect, strongest in Herbal/Recipe pages).
- Added **historical analogue notes** per operator role (for context; not prescriptive lexemes).
- Aggregated a **top-500 stem list** with category guesses from operator-signature clustering (random 10 folios).

## Evidence snapshot (10-folio batch)
- Mean template coverage ≈ **93%**; mean H(3|12) ≈ **0.38** (prefix-gated third-slot persists page-by-page).
- Procedural **cadence** (e.g., Q→C→S→…) is strong in **Herbal/Recipe** sections; weaker or absent in Astronomical/Zodiac/Bio.
- Stem clusters partition by section: INGREDIENT/PROCESS families concentrate in Herbal/Recipe.

## Files
- Operators: `MasterKey_v1_1__operators.csv`
- Suffixes: `MasterKey_v1_1__suffixes.csv`
- Stems (top 500): `MasterKey_v1_1__stems_top500.csv`

## Apply the key
1. Segment tokens as **OP** + **STEM** (+ **SUF?**). Prefer 2-letter operators (`qo/ch/sh/da/ok/ot`).  
2. Tag roles (Q,C,S,D,V1,V2); run clustering to assign {{INGR}}/{{UNIT}}/{{PROC}}/{{VESSEL}}.  
3. Treat **-dy**, **-in** as active nomenclators; consider **-ol**, **-al** in Herbal/Recipe pages.  
4. Promote/demote only if they increase coverage or cadence fit on held-out folios (p<0.05).

_No vibes: every addition must buy predictability, coverage, or adjacency fit._
