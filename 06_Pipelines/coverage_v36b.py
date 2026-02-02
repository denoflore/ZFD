#!/usr/bin/env python3
"""
ZFD Coverage Analysis v3.6b
Simplified approach: check if word CONTAINS known morphemes
Friday's additions:
- he-, heo-, še-, šeo- as state markers
- -ei as state suffix
- ost- as medical bone register
"""

# ALL KNOWN MORPHEMES (substring matching)
KNOWN_MORPHEMES = {
    # Operators
    'qo', 'ko', 'ch', 'sh', 'da', 'ok', 'ot',
    # State markers (Friday's insight)
    'he', 'heo', 'še', 'šeo', 'ho', 'šo',
    # Bone - Slavic
    'kost',
    # Bone - Medical (Friday's insight)  
    'ost', 'oste', 'osteo',
    # Process kernel
    'ed', 'edy', 'rady',
    # Suffixes - active
    'edi', 'dy',
    # Suffixes - state (Friday's insight)
    'ei',
    # Suffixes - other
    'ain', 'in', 'al', 'ol', 'ar', 'or',
    # Liquids
    'vin', 'lac', 'mel', 'syr',
    # Core stems
    'sar', 'sal', 'dar', 'flor', 'ros', 'myr',
    'aloe', 'galb', 'stor', 'opop', 'camph',
    'anis', 'cori', 'ment', 'salv', 'fenn', 'ruta',
    'hyss', 'malv', 'verb', 'plant',
    'canel', 'zing', 'piper', 'nard',
    # Minerals
    'sul', 'arg', 'cupr', 'fer', 'salp', 'alum',
    # Animal
    'cera', 'axun', 'case', 'ova', 'ung',
    # Luxury
    'musc', 'ambra', 'perla', 'coral', 'ivor', 'lapis',
    # Heat/vessels
    'kair', 'kar', 'char', 'thor', 'okal', 'kal', 'phar',
    'shor', 'chor', 'chol',
    # Gallows clusters (treating as known)
    'ctr', 'hctr', 'csth', 'hcsth', 'tr', 'st',
    # Determiners
    'lh', 'lš', 'opl',
}

def has_morpheme(word):
    """Check if word contains any known morpheme"""
    for m in KNOWN_MORPHEMES:
        if m in word:
            return True, m
    return False, None

# Load words
words = []
with open('/home/claude/word_freq.csv', 'r') as f:
    next(f)
    for line in f:
        parts = line.strip().split(',')
        if len(parts) == 2:
            words.append((parts[0].strip(), int(parts[1])))

total_words = len(words)
total_tokens = sum(f for _, f in words)

# Classify
known = []
unknown = []
for word, freq in words:
    has_m, morpheme = has_morpheme(word)
    if has_m:
        known.append((word, freq, morpheme))
    else:
        unknown.append((word, freq))

known_tokens = sum(f for _, f, _ in known)
unknown_tokens = sum(f for _, f in unknown)

print("="*70)
print("ZFD COVERAGE v3.6b - Friday's Framework (Simplified)")
print("="*70)
print(f"Known morphemes: {len(KNOWN_MORPHEMES)}")
print(f"Total words: {total_words:,}")
print(f"Total tokens: {total_tokens:,}")
print()
print(f"WORD COVERAGE:")
print(f"  Known:   {len(known):,} ({100*len(known)/total_words:.1f}%)")
print(f"  Unknown: {len(unknown):,} ({100*len(unknown)/total_words:.1f}%)")
print()
print(f"TOKEN COVERAGE:")
print(f"  Known:   {known_tokens:,} ({100*known_tokens/total_tokens:.1f}%)")
print(f"  Unknown: {unknown_tokens:,} ({100*unknown_tokens/total_tokens:.1f}%)")
print()

# Breakdown by morpheme type
print("="*70)
print("COVERAGE BY MORPHEME CATEGORY")
print("="*70)

categories = {
    'State markers (NEW)': ['he', 'heo', 'še', 'šeo', 'ho', 'šo'],
    'Medical bone (NEW)': ['ost', 'oste', 'osteo'],
    'State suffix (NEW)': ['ei'],
    'Operators': ['qo', 'ko', 'ch', 'sh', 'da', 'ok', 'ot'],
    'Slavic bone': ['kost'],
    'Process kernel': ['ed', 'edy'],
    'Gallows clusters': ['ctr', 'hctr', 'csth', 'hcsth', 'tr', 'st'],
}

for cat_name, morphemes in categories.items():
    count = sum(f for w, f, m in known if m in morphemes)
    words_count = len([w for w, f, m in known if m in morphemes])
    print(f"  {cat_name}: {count:,} tokens ({words_count} words)")

print()
print("="*70)
print("TOP 40 REMAINING UNKNOWNS")
print("="*70)
for i, (word, freq) in enumerate(sorted(unknown, key=lambda x: -x[1])[:40], 1):
    print(f"{i:3}. {word:<20} {freq:>5}")

print()
print("="*70)
print("UNKNOWN STEM PATTERNS (for next lexicon expansion)")
print("="*70)
from collections import defaultdict
stems = defaultdict(list)
for word, freq in unknown:
    # Get first 2-3 chars as pattern
    pattern = word[:2] if len(word) >= 2 else word
    stems[pattern].append((word, freq))

stem_totals = [(p, sum(f for _, f in ws), len(ws)) for p, ws in stems.items()]
stem_totals.sort(key=lambda x: -x[1])

for pattern, total, count in stem_totals[:20]:
    examples = sorted(stems[pattern], key=lambda x: -x[1])[:3]
    ex_str = ', '.join(f"{w}({f})" for w, f in examples)
    print(f"  {pattern}: {total:>5} tokens, {count:>3} words  [{ex_str}]")
