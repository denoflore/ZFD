# Getting Started with the Zuger Functional Decipherment

## How to Read the Voynich Manuscript in 10 Minutes

This guide will teach you to decode Voynichese yourself. No special tools required.

---

## Step 1: Understand the Structure

Every Voynich word follows this pattern:

```
[OPERATOR] + [STEM] + [SUFFIX]
```

- **Operator** (optional): Word-initial, tells you what kind of action
- **Stem**: The core meaning (ingredient, object, concept)
- **Suffix**: Grammatical ending (plural, state, etc.)

---

## Step 2: Learn the Operators (5 minutes)

| EVA | Croatian | Meaning | Think of it as... |
|-----|----------|---------|-------------------|
| qo- / ko- | ko- | "which/quantity" | "the amount of..." |
| ch- | h- | "combine/cook" | "cook the..." |
| sh- / š- | š- | "soak/with" | "soak the..." |
| da- | da- | "dose/give" | "give/add..." |
| ok- / ot- | ost-/otr- | "vessel" | "in a vessel..." |

**Example:**
- `chol` = ch + ol = "combine" + "oil" = **"mix with oil"**
- `shar` = sh + ar = "soak" + "water" = **"soak in water"**

---

## Step 3: Learn the Gallows Expansions (2 minutes)

The tall "gallows" characters are abbreviations for consonant clusters:

| EVA | Expands to | Example |
|-----|------------|---------|
| k | st | qokeedy → ko-**st**-edi = **kost**edi (bone preparation) |
| t | tr | otaiin → o-**tr**-ain = **otr**ain (vessel-treatment) |
| f | pr | - | (less common) |
| p | pl | - | (less common) |

**The big one:** Any word with gallows-k that sounds like "kost" = **BONE**

---

## Step 4: Learn Common Stems (3 minutes)

| Croatian | English | Frequency | Context |
|----------|---------|-----------|---------|
| kost | bone | 2000+ | pharmaceutical preparations |
| ol | oil | 500+ | with vessels, cooking |
| ar | water | 300+ | liquids, solutions |
| dar | dose/gift | 280+ | measurements, additions |
| sar/sal | salt | 80+ | mineral preparations |
| mel | honey | 50+ | sweeteners, syrups |
| flor | flower | 40+ | botanical sections |
| ros | rose | 35+ | rose water, perfumes |

---

## Step 5: Learn the Suffixes

| Suffix | Type | Meaning |
|--------|------|---------|
| -edi | Active | "process of..." (being prepared) |
| -ei | State | "in the state of..." (prepared) |
| -ain | Plural/Collection | multiple items |
| -al | Container | vessel/container context |
| -ol | Oil-related | liquid/oil context |
| -i / -y | Adjectival | descriptive ending |

---

## Step 6: Practice Decoding

### Example 1: `qokeedy` (appears 301 times)
```
qo + k + ee + dy
↓    ↓    ↓    ↓
ko + st + e + di
= kostedi
= kost (bone) + -edi (preparation)
= "bone preparation"
```

### Example 2: `chedy` (appears 490 times)
```
ch + e + dy
↓    ↓   ↓
h + ed + i
= hedi
= h- (cook/process) + ed (root/base) + -i (state)
= "processed/cooked root"
```

### Example 3: `shol` (appears 174 times)
```
sh + ol
↓    ↓
š + ol
= šol
= š- (soak) + ol (oil)
= "oil infusion" or "soaked in oil"
```

### Example 4: `daiin` (appears 751 times - most frequent!)
```
da + iin
↓    ↓
da + in
= dain
= da- (dose/give) + -in (noun ending)
= "a dose" or "portion"
```

---

## Step 7: Try a Full Line

From folio f88r (pharmaceutical section):

**EVA:** `qokeedy dal chol ar shedy`

**Decode:**
- qokeedy → kostedi → "bone preparation"
- dal → dal → "of/from" (partitive)
- chol → hol → "combined oil"
- ar → ar → "water"
- shedy → šedi → "soaked root"

**Reading:** "Bone preparation, of combined oil, water, soaked root"

**Plain English:** "Prepare bone [powder] with oil and water [solution], [add] soaked root"

---

## Quick Reference Card

### Operators
| EVA | → | Croatian | Meaning |
|-----|---|----------|---------|
| qo/ko | → | ko | quantity |
| ch | → | h | combine |
| sh | → | š | soak |
| da | → | da | dose |
| ok/ot | → | ost/otr | vessel |

### Gallows
| EVA | → | Expansion |
|-----|---|-----------|
| k | → | st |
| t | → | tr |

### Top 10 Stems
| Croatian | English |
|----------|---------|
| kost | bone |
| ol | oil |
| ar | water |
| dar | dose |
| ed | root |
| sal | salt |
| mel | honey |
| flor | flower |
| ros | rose |
| vin | wine |

---

## Verify It Yourself

1. Pick any folio from the manuscript
2. Find a word starting with `qok-`
3. Expand the gallows: k → st
4. You'll get `kost-` (bone)
5. Check if it's in a pharmaceutical context

This works on every folio. That's how we know it's real.

---

## Common Patterns

| Pattern | Meaning | Example |
|---------|---------|---------|
| kost + suffix | bone preparation | kostedi, kostain, kostal |
| h + stem | cook/combine | hedi, hol, har |
| š + stem | soak/infuse | šedi, šol, šar |
| da + suffix | dose/portion | dain, dal, dar |
| stem + ol | with oil | chol, šol, dal |
| stem + ar | with water | char, šar, dar |
| stem + ain | plural/batch | kostain, dain, šain |

---

## Next Steps

1. **Read the paper:** `papers/ZFD_PAPER_DRAFT_v1.pdf`
2. **See the full translation:** `papers/voynich_croatian_complete.pdf`
3. **Check the lexicon:** `08_Final_Proofs/Master_Key/Herbal_Lexicon_v3_6.csv`
4. **Run the analysis:** `python 06_Pipelines/coverage_v36b.py`

---

## FAQ

**Q: Why Croatian?**
A: The manuscript was created in the Republic of Ragusa (modern Dubrovnik), a Croatian-speaking trading city with established Glagolitic literacy and pharmaceutical trade.

**Q: Why wasn't this found before?**
A: Western scholars only compared to Latin scripts. Nobody checked Croatian Glagolitic manuscripts.

**Q: How confident are you?**
A: 96.8% of tokens contain known morphemes. Native speaker validation confirms key vocabulary. Statistical profile matches medieval pharmaceutical texts.

**Q: Can I verify this myself?**
A: Yes. Apply the key to any folio. If "kost" (bone) appears in pharmaceutical contexts and "flor" (flower) in botanical contexts, the mapping is correct.

---

*Document version 1.0 | February 2026*
*Christopher G. Zuger | github.com/denoflore/ZFD*
