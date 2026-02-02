"""
Voynich-Glagolitic Glyph Validation

Tests the hypothesis that Voynichese is abbreviated Angular Glagolitic.
Preregistered success/failure criteria per instruction document.
"""

import json
import csv
import sys
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
import math

sys.path.insert(0, str(Path(__file__).parent / 'validation'))

from zfd_loader import ZFDLoader

# =============================================================================
# CROATIAN LETTER FREQUENCY DATA
# Source: Croatian linguistic studies (approximate values)
# =============================================================================

CROATIAN_LETTER_FREQ = {
    'a': 11.1,
    'i': 9.8,
    'o': 8.9,
    'e': 8.5,
    'n': 6.6,
    'r': 5.9,
    's': 5.6,
    't': 5.1,
    'j': 5.0,
    'u': 4.3,
    'k': 3.6,
    'l': 3.2,
    'd': 3.1,
    'p': 2.9,
    'm': 2.9,
    'v': 2.8,
    'z': 2.3,
    'g': 1.6,
    'b': 1.5,
    'c': 1.3,
    'h': 1.0,
    'š': 0.9,
    'č': 0.8,
    'ž': 0.6,
    'f': 0.2,
}

# Proposed Glagolitic mapping
GLYPH_MAPPING = {
    # Gallows -> Consonants
    'k': {'glagolitic': 'Ⰼ', 'sound': '/k/', 'type': 'consonant'},
    't': {'glagolitic': 'Ⱅ', 'sound': '/t/', 'type': 'consonant'},
    'f': {'glagolitic': 'Ⱇ', 'sound': '/f/', 'type': 'consonant'},
    'p': {'glagolitic': 'Ⱂ', 'sound': '/p/', 'type': 'consonant'},

    # Vowels
    'o': {'glagolitic': 'Ⱁ', 'sound': '/o/', 'type': 'vowel'},
    'a': {'glagolitic': 'Ⰰ', 'sound': '/a/', 'type': 'vowel'},
    'e': {'glagolitic': 'Ⰵ', 'sound': '/e/', 'type': 'vowel'},
    'i': {'glagolitic': 'Ⰹ', 'sound': '/i/', 'type': 'vowel'},
    'y': {'glagolitic': 'Ⱏ', 'sound': '/ɨ/', 'type': 'vowel'},

    # Consonant clusters
    'ch': {'glagolitic': 'Ⱈ', 'sound': '/x/', 'type': 'consonant'},
    'sh': {'glagolitic': 'Ⱊ', 'sound': '/ʃ/', 'type': 'consonant'},

    # Other consonants
    'd': {'glagolitic': 'Ⰴ', 'sound': '/d/', 'type': 'consonant'},
    'l': {'glagolitic': 'Ⰽ', 'sound': '/l/', 'type': 'consonant'},
    'r': {'glagolitic': 'Ⱃ', 'sound': '/r/', 'type': 'consonant'},
    's': {'glagolitic': 'Ⱄ', 'sound': '/s/', 'type': 'consonant'},
    'n': {'glagolitic': 'Ⰿ', 'sound': '/n/', 'type': 'consonant'},
    'm': {'glagolitic': 'Ⰾ', 'sound': '/m/', 'type': 'consonant'},
}

GALLOWS = ['k', 't', 'f', 'p']
PROPOSED_VOWELS = ['o', 'a', 'e', 'i', 'y']
PROPOSED_CONSONANTS = ['k', 't', 'f', 'p', 'd', 'l', 'r', 's', 'n', 'm', 'c', 'h', 'g', 'q']


def extract_all_words(loader):
    """Extract all words from the corpus."""
    words = []
    for folio, lines in loader.transcription.items():
        for line in lines:
            for token in line.get('tokens', []):
                # Clean token
                token = token.lower().strip()
                # Remove common transcription artifacts
                token = token.replace('plant', '').replace('figure', '').replace('$', '')
                if token and len(token) >= 2:
                    words.append(token)
    return words


def calculate_glyph_frequencies(words):
    """Calculate frequency of each glyph."""
    total_chars = 0
    glyph_counts = Counter()

    for word in words:
        for char in word:
            glyph_counts[char] += 1
            total_chars += 1

    frequencies = {}
    for glyph, count in glyph_counts.items():
        frequencies[glyph] = {
            'count': count,
            'frequency': count / total_chars * 100 if total_chars > 0 else 0
        }

    return frequencies, total_chars


def calculate_positional_distribution(words):
    """Calculate where each glyph appears (initial, medial, final)."""
    position_counts = defaultdict(lambda: {'initial': 0, 'medial': 0, 'final': 0, 'total': 0})

    for word in words:
        if len(word) < 1:
            continue

        # Initial position
        position_counts[word[0]]['initial'] += 1
        position_counts[word[0]]['total'] += 1

        # Final position
        if len(word) > 1:
            position_counts[word[-1]]['final'] += 1
            position_counts[word[-1]]['total'] += 1

        # Medial positions
        if len(word) > 2:
            for char in word[1:-1]:
                position_counts[char]['medial'] += 1
                position_counts[char]['total'] += 1

    # Calculate percentages
    results = {}
    for glyph, counts in position_counts.items():
        total = counts['total']
        if total > 0:
            results[glyph] = {
                'total': total,
                'initial': counts['initial'],
                'initial_pct': counts['initial'] / total * 100,
                'medial': counts['medial'],
                'medial_pct': counts['medial'] / total * 100,
                'final': counts['final'],
                'final_pct': counts['final'] / total * 100,
            }

    return results


def calculate_following_char(words):
    """Calculate what follows each glyph."""
    following = defaultdict(lambda: {'vowel': 0, 'consonant': 0, 'total': 0})

    for word in words:
        for i in range(len(word) - 1):
            char = word[i]
            next_char = word[i + 1]

            following[char]['total'] += 1

            if next_char in PROPOSED_VOWELS:
                following[char]['vowel'] += 1
            else:
                following[char]['consonant'] += 1

    results = {}
    for glyph, counts in following.items():
        total = counts['total']
        if total > 0:
            results[glyph] = {
                'total': total,
                'followed_by_vowel': counts['vowel'],
                'followed_by_vowel_pct': counts['vowel'] / total * 100,
                'followed_by_consonant': counts['consonant'],
                'followed_by_consonant_pct': counts['consonant'] / total * 100,
            }

    return results


def test_gallows_hypothesis(positional, following):
    """Test: Do gallows behave as consonants?"""
    results = []

    for g in GALLOWS:
        if g not in positional:
            results.append({
                'glyph': g,
                'status': 'NO_DATA',
                'initial_pct': None,
                'final_pct': None,
                'followed_by_vowel_pct': None,
            })
            continue

        pos = positional[g]
        fol = following.get(g, {})

        initial_pct = pos['initial_pct']
        final_pct = pos['final_pct']
        vowel_pct = fol.get('followed_by_vowel_pct', 0)

        # Criteria: initial > 60%, final < 10%, +vowel > 50%
        passes_initial = initial_pct > 60
        passes_final = final_pct < 10
        passes_vowel = vowel_pct > 50

        status = 'PASS' if (passes_initial and passes_final and passes_vowel) else 'PARTIAL' if (passes_initial or passes_vowel) else 'FAIL'

        results.append({
            'glyph': g,
            'status': status,
            'initial_pct': initial_pct,
            'final_pct': final_pct,
            'followed_by_vowel_pct': vowel_pct,
            'passes_initial': passes_initial,
            'passes_final': passes_final,
            'passes_vowel': passes_vowel,
        })

    return results


def test_vowel_hypothesis(positional, words):
    """Test: Do proposed vowels behave as vowels?"""
    results = []

    # Calculate CVC pattern frequency
    cvc_counts = defaultdict(lambda: {'cvc': 0, 'total': 0})

    for word in words:
        for i in range(1, len(word) - 1):
            char = word[i]
            prev_char = word[i - 1]
            next_char = word[i + 1]

            cvc_counts[char]['total'] += 1

            # CVC pattern: consonant-vowel-consonant
            if prev_char not in PROPOSED_VOWELS and next_char not in PROPOSED_VOWELS:
                cvc_counts[char]['cvc'] += 1

    for v in PROPOSED_VOWELS:
        if v not in positional:
            results.append({
                'glyph': v,
                'status': 'NO_DATA',
                'final_pct': None,
                'cvc_pct': None,
            })
            continue

        pos = positional[v]
        cvc = cvc_counts.get(v, {'cvc': 0, 'total': 1})

        final_pct = pos['final_pct']
        cvc_pct = cvc['cvc'] / max(1, cvc['total']) * 100

        # Criteria: final > 30% (Croatian words often end in vowels)
        passes_final = final_pct > 30
        passes_cvc = cvc_pct > 40  # CVC pattern common

        status = 'PASS' if passes_final else 'PARTIAL' if passes_cvc else 'FAIL'

        results.append({
            'glyph': v,
            'status': status,
            'final_pct': final_pct,
            'cvc_pct': cvc_pct,
            'passes_final': passes_final,
            'passes_cvc': passes_cvc,
        })

    return results


def calculate_frequency_correlation(voynich_freq, croatian_freq):
    """Calculate correlation between Voynich and Croatian letter frequencies."""
    # Map Voynich glyphs to Croatian equivalents
    mapping = {
        'o': 'o', 'a': 'a', 'e': 'e', 'i': 'i',
        'k': 'k', 't': 't', 'p': 'p', 'd': 'd',
        'l': 'l', 'r': 'r', 's': 's', 'n': 'n', 'm': 'm',
    }

    v_values = []
    c_values = []

    for v_glyph, c_glyph in mapping.items():
        if v_glyph in voynich_freq and c_glyph in croatian_freq:
            v_values.append(voynich_freq[v_glyph]['frequency'])
            c_values.append(croatian_freq[c_glyph])

    if len(v_values) < 3:
        return None, "Insufficient data"

    # Pearson correlation
    n = len(v_values)
    sum_v = sum(v_values)
    sum_c = sum(c_values)
    sum_vc = sum(v * c for v, c in zip(v_values, c_values))
    sum_v2 = sum(v * v for v in v_values)
    sum_c2 = sum(c * c for c in c_values)

    numerator = n * sum_vc - sum_v * sum_c
    denominator = math.sqrt((n * sum_v2 - sum_v**2) * (n * sum_c2 - sum_c**2))

    if denominator == 0:
        return 0, "Zero variance"

    r = numerator / denominator
    return r, "OK"


def transliterate_word(word):
    """Apply proposed sound values to a word."""
    result = []
    i = 0

    while i < len(word):
        # Check for digraphs first
        if i < len(word) - 1:
            digraph = word[i:i+2]
            if digraph in ['ch', 'sh']:
                if digraph == 'ch':
                    result.append('h')  # /x/ -> h
                elif digraph == 'sh':
                    result.append('š')
                i += 2
                continue

        char = word[i]

        # Apply mapping
        if char == 'q':
            result.append('k')  # qo -> ko
        elif char == 'y':
            result.append('i')  # y -> i (reduced vowel)
        elif char in GLYPH_MAPPING:
            sound = GLYPH_MAPPING[char]['sound']
            # Extract letter from /x/ format
            result.append(sound.strip('/'))
        else:
            result.append(char)

        i += 1

    return ''.join(result)


def generate_candidate_readings(words, top_n=50):
    """Generate candidate Croatian readings for common words."""
    word_freq = Counter(words)
    candidates = []

    for word, count in word_freq.most_common(top_n):
        transliteration = transliterate_word(word)

        candidates.append({
            'voynich': word,
            'count': count,
            'transliteration': transliteration,
            'phonotactic_valid': is_phonotactically_valid(transliteration),
        })

    return candidates


def is_phonotactically_valid(word):
    """Check if word follows basic Croatian phonotactics."""
    if not word:
        return False

    vowels = set('aeiouə')

    # Check for vowel presence
    has_vowel = any(c in vowels for c in word)

    # Check for excessive consonant clusters (>3 consonants)
    consonant_run = 0
    max_consonant_run = 0
    for c in word:
        if c not in vowels:
            consonant_run += 1
            max_consonant_run = max(max_consonant_run, consonant_run)
        else:
            consonant_run = 0

    # Croatian allows some clusters but not excessive ones
    reasonable_clusters = max_consonant_run <= 4

    return has_vowel and reasonable_clusters


def main():
    print("="*70)
    print("VOYNICH-GLAGOLITIC GLYPH VALIDATION")
    print("="*70)
    print(f"Started: {datetime.now().isoformat()}")

    # Load corpus
    loader = ZFDLoader('.')
    words = extract_all_words(loader)

    print(f"\nCorpus loaded: {len(words)} words")

    # Phase 1: Frequency Analysis
    print("\n" + "="*70)
    print("PHASE 1: FREQUENCY ANALYSIS")
    print("="*70)

    frequencies, total_chars = calculate_glyph_frequencies(words)

    print(f"\nTotal characters: {total_chars}")
    print("\nTop 20 glyphs by frequency:")
    print(f"{'Glyph':<8} {'Count':>8} {'Freq %':>8}")
    print("-" * 26)

    sorted_freq = sorted(frequencies.items(), key=lambda x: x[1]['frequency'], reverse=True)
    for glyph, data in sorted_freq[:20]:
        print(f"{glyph:<8} {data['count']:>8} {data['frequency']:>7.2f}%")

    # Phase 2: Positional Distribution
    print("\n" + "="*70)
    print("PHASE 2: POSITIONAL DISTRIBUTION")
    print("="*70)

    positional = calculate_positional_distribution(words)
    following = calculate_following_char(words)

    print("\nGallows positional analysis:")
    print(f"{'Glyph':<8} {'Initial%':>10} {'Medial%':>10} {'Final%':>10} {'Total':>8}")
    print("-" * 50)

    for g in GALLOWS:
        if g in positional:
            p = positional[g]
            print(f"{g:<8} {p['initial_pct']:>9.1f}% {p['medial_pct']:>9.1f}% {p['final_pct']:>9.1f}% {p['total']:>8}")

    print("\nProposed vowels positional analysis:")
    for v in PROPOSED_VOWELS:
        if v in positional:
            p = positional[v]
            print(f"{v:<8} {p['initial_pct']:>9.1f}% {p['medial_pct']:>9.1f}% {p['final_pct']:>9.1f}% {p['total']:>8}")

    # Phase 3: Hypothesis Tests
    print("\n" + "="*70)
    print("PHASE 3: HYPOTHESIS TESTS")
    print("="*70)

    # Test 1: Gallows as consonants
    print("\n### TEST 1: Gallows → Consonants ###")
    print("Criteria: initial > 60%, final < 10%, followed by vowel > 50%")
    print()

    gallows_results = test_gallows_hypothesis(positional, following)

    gallows_pass = 0
    for r in gallows_results:
        status_icon = "✅" if r['status'] == 'PASS' else "⚠️" if r['status'] == 'PARTIAL' else "❌"
        if r['initial_pct'] is not None:
            print(f"{status_icon} {r['glyph']}: initial={r['initial_pct']:.1f}%, final={r['final_pct']:.1f}%, +vowel={r['followed_by_vowel_pct']:.1f}%")
            if r['status'] == 'PASS':
                gallows_pass += 1

    # Test 2: Vowel distribution
    print("\n### TEST 2: Vowel Distribution ###")
    print("Criteria: word-final > 30%")
    print()

    vowel_results = test_vowel_hypothesis(positional, words)

    vowel_pass = 0
    for r in vowel_results:
        status_icon = "✅" if r['status'] == 'PASS' else "⚠️" if r['status'] == 'PARTIAL' else "❌"
        if r['final_pct'] is not None:
            print(f"{status_icon} {r['glyph']}: final={r['final_pct']:.1f}%, CVC={r['cvc_pct']:.1f}%")
            if r['status'] == 'PASS':
                vowel_pass += 1

    # Test 3: Frequency correlation
    print("\n### TEST 3: Croatian Frequency Correlation ###")

    correlation, status = calculate_frequency_correlation(frequencies, CROATIAN_LETTER_FREQ)

    if correlation is not None:
        corr_status = "✅ PASS" if correlation > 0.5 else "⚠️ WEAK" if correlation > 0.2 else "❌ FAIL"
        print(f"Correlation coefficient: r = {correlation:.3f} {corr_status}")
    else:
        print(f"Correlation: {status}")

    # Phase 4: Candidate Readings
    print("\n" + "="*70)
    print("PHASE 4: CANDIDATE READINGS")
    print("="*70)

    candidates = generate_candidate_readings(words, 30)

    print("\nTop 30 words with transliterations:")
    print(f"{'Voynich':<15} {'Count':>6} {'Croatian':>15} {'Valid':>6}")
    print("-" * 45)

    valid_count = 0
    for c in candidates:
        valid_icon = "✓" if c['phonotactic_valid'] else "✗"
        print(f"{c['voynich']:<15} {c['count']:>6} {c['transliteration']:>15} {valid_icon:>6}")
        if c['phonotactic_valid']:
            valid_count += 1

    # Phase 5: Final Assessment
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)

    print("\n### SUCCESS CRITERIA CHECK ###\n")

    # Criterion 1: Gallows initial > 60%
    avg_gallows_initial = sum(r['initial_pct'] for r in gallows_results if r['initial_pct']) / max(1, len([r for r in gallows_results if r['initial_pct']]))
    crit1 = avg_gallows_initial > 60
    print(f"{'✅' if crit1 else '❌'} Gallows initial position: {avg_gallows_initial:.1f}% (target: >60%)")

    # Criterion 2: Vowels final > 30%
    avg_vowel_final = sum(r['final_pct'] for r in vowel_results if r['final_pct']) / max(1, len([r for r in vowel_results if r['final_pct']]))
    crit2 = avg_vowel_final > 30
    print(f"{'✅' if crit2 else '❌'} Vowels final position: {avg_vowel_final:.1f}% (target: >30%)")

    # Criterion 3: Correlation > 0.5
    crit3 = correlation is not None and correlation > 0.5
    corr_str = f"{correlation:.3f}" if correlation is not None else "N/A"
    print(f"{'✅' if crit3 else '❌'} Croatian frequency correlation: r={corr_str} (target: >0.5)")

    # Criterion 4: Phonotactically valid readings
    valid_pct = valid_count / len(candidates) * 100
    crit4 = valid_pct > 60
    print(f"{'✅' if crit4 else '❌'} Phonotactically valid readings: {valid_pct:.1f}% (target: >60%)")

    # Overall verdict
    criteria_passed = sum([crit1, crit2, crit3, crit4])

    print(f"\n### OVERALL VERDICT ###")
    print(f"Criteria passed: {criteria_passed}/4")

    if criteria_passed >= 3:
        verdict = "SUPPORTED"
        print(f"\n🟢 GLAGOLITIC HYPOTHESIS: {verdict}")
    elif criteria_passed >= 2:
        verdict = "PARTIALLY SUPPORTED"
        print(f"\n🟡 GLAGOLITIC HYPOTHESIS: {verdict}")
    else:
        verdict = "NOT SUPPORTED"
        print(f"\n🔴 GLAGOLITIC HYPOTHESIS: {verdict}")

    # Save results
    print("\n" + "="*70)
    print("SAVING OUTPUT FILES")
    print("="*70)

    analysis_dir = Path('analysis')
    analysis_dir.mkdir(exist_ok=True)

    # Save frequency data
    freq_path = analysis_dir / 'glyph_frequency_analysis.csv'
    with open(freq_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['glyph', 'count', 'frequency_pct'])
        for glyph, data in sorted_freq:
            writer.writerow([glyph, data['count'], f"{data['frequency']:.4f}"])
    print(f"Saved: {freq_path}")

    # Save positional data
    pos_path = analysis_dir / 'positional_distribution.csv'
    with open(pos_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['glyph', 'total', 'initial', 'initial_pct', 'medial', 'medial_pct', 'final', 'final_pct'])
        for glyph, data in positional.items():
            writer.writerow([
                glyph, data['total'], data['initial'], f"{data['initial_pct']:.2f}",
                data['medial'], f"{data['medial_pct']:.2f}",
                data['final'], f"{data['final_pct']:.2f}"
            ])
    print(f"Saved: {pos_path}")

    # Save candidate readings
    readings_path = analysis_dir / 'candidate_readings.md'
    with open(readings_path, 'w') as f:
        f.write("# Candidate Croatian Readings\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")
        f.write("| Voynich | Count | Croatian | Valid |\n")
        f.write("|---------|-------|----------|-------|\n")
        for c in candidates:
            valid = "✓" if c['phonotactic_valid'] else "✗"
            f.write(f"| {c['voynich']} | {c['count']} | {c['transliteration']} | {valid} |\n")
    print(f"Saved: {readings_path}")

    # Save validation summary
    summary_path = analysis_dir / 'validation_summary.md'
    with open(summary_path, 'w') as f:
        f.write("# Voynich-Glagolitic Hypothesis Validation Summary\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"**Verdict:** {verdict}\n\n")
        f.write("---\n\n")
        f.write("## Success Criteria\n\n")
        f.write(f"| Criterion | Result | Target | Status |\n")
        f.write(f"|-----------|--------|--------|--------|\n")
        f.write(f"| Gallows initial position | {avg_gallows_initial:.1f}% | >60% | {'PASS' if crit1 else 'FAIL'} |\n")
        f.write(f"| Vowels final position | {avg_vowel_final:.1f}% | >30% | {'PASS' if crit2 else 'FAIL'} |\n")
        f.write(f"| Croatian correlation | r={corr_str} | >0.5 | {'PASS' if crit3 else 'FAIL'} |\n")
        f.write(f"| Phonotactic validity | {valid_pct:.1f}% | >60% | {'PASS' if crit4 else 'FAIL'} |\n")
        f.write(f"\n**Criteria Passed:** {criteria_passed}/4\n\n")
        f.write("---\n\n")
        f.write("## Interpretation\n\n")
        if verdict == "SUPPORTED":
            f.write("The statistical evidence supports the hypothesis that Voynichese is an abbreviated form of Angular Glagolitic.\n")
        elif verdict == "PARTIALLY SUPPORTED":
            f.write("The evidence partially supports the Glagolitic hypothesis. Some criteria pass while others need further investigation.\n")
        else:
            f.write("The statistical evidence does not support the Glagolitic hypothesis based on the preregistered criteria.\n")
    print(f"Saved: {summary_path}")

    print(f"\nValidation complete: {datetime.now().isoformat()}")

    return verdict


if __name__ == "__main__":
    main()
