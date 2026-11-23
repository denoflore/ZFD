"""
Non-Voynich text generators for vocabulary specificity testing.

Three generators that produce text the decoder should NOT be able to decode well:
1. Synthetic EVA: Random character combinations matching manuscript statistics
2. Character-shuffled: Real words with internal characters scrambled
3. Random Latin: Medieval pharmaceutical Latin vocabulary
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "zfd_decoder" / "src"))
from tokenizer import words_from_eva_line
from v2_config import EVA_CHAR_FREQUENCIES, EVA_LENGTH_DISTRIBUTION, LATIN_VOCABULARY


def generate_synthetic_eva(real_eva_text: str, seed: int) -> str:
    """
    Generate synthetic EVA text matching the manuscript's statistical profile.

    Produces fake words that:
    - Use EVA characters at manuscript-matching frequencies
    - Match the manuscript's word length distribution
    - Preserve the original folio's line structure (words per line)
    - Are sampled without using the real word's spelling

    This tests whether the decoder's mappings are specific to real Voynich
    morphology or will match any EVA-alphabet string.
    """
    rng = random.Random(seed)

    # Build character sampling weights
    chars = list(EVA_CHAR_FREQUENCIES.keys())
    weights = list(EVA_CHAR_FREQUENCIES.values())

    # Build length sampling weights
    possible_lengths = list(EVA_LENGTH_DISTRIBUTION.keys())
    length_weights = list(EVA_LENGTH_DISTRIBUTION.values())

    # Parse the real text to get line structure
    lines = real_eva_text.strip().split('\n')
    output_lines = []

    for line in lines:
        line = line.strip()
        # Preserve non-text lines (headers, markup, comments)
        if not line or line.startswith('#') or line.startswith('===') or line.startswith('['):
            output_lines.append(line)
            continue

        # Count real words on this line
        real_words = words_from_eva_line(line)
        word_count = len(real_words)

        # Generate that many synthetic words
        synthetic_words = []
        for _ in range(word_count):
            # Pick a length from the distribution
            length = rng.choices(possible_lengths, weights=length_weights, k=1)[0]
            # Generate random characters at that length
            word = ''.join(rng.choices(chars, weights=weights, k=length))
            synthetic_words.append(word)

        output_lines.append('.'.join(synthetic_words))

    return '\n'.join(output_lines)


def generate_char_shuffled(real_eva_text: str, seed: int) -> str:
    """
    Shuffle characters WITHIN each word while preserving word lengths and line structure.

    This destroys morphological structure (operator-stem-suffix patterns) while
    keeping the exact same character distribution per word. If the decoder relies
    on specific character sequences (like 'qo' as operator prefix or 'edy' as
    root stem), character shuffling will break those patterns.

    If the decoder still produces high coherence on character-shuffled words,
    it means the mappings are matching individual characters rather than
    meaningful morphological units.
    """
    rng = random.Random(seed)

    lines = real_eva_text.strip().split('\n')
    output_lines = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('===') or line.startswith('['):
            output_lines.append(line)
            continue

        # Use exactly the glyph words consumed by the real decoder.
        real_words = words_from_eva_line(line)

        shuffled_words = []
        for word in real_words:
            # Shuffle characters within the word
            char_list = list(word)
            rng.shuffle(char_list)
            shuffled_words.append(''.join(char_list))

        output_lines.append('.'.join(shuffled_words))

    return '\n'.join(output_lines)


def generate_random_latin(real_eva_text: str, seed: int) -> str:
    """
    Replace Voynich words with random medieval Latin pharmaceutical vocabulary.

    Uses domain-relevant Latin vocabulary (herbs, preparations, instructions,
    measurements) to give the Latin baseline its BEST possible shot. If the
    decoder produces high coherence even on Latin pharmaceutical text, the
    mappings are truly language-agnostic.

    Preserves the original folio's line structure (words per line).
    """
    rng = random.Random(seed)

    lines = real_eva_text.strip().split('\n')
    output_lines = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('===') or line.startswith('['):
            output_lines.append(line)
            continue

        real_words = words_from_eva_line(line)
        word_count = len(real_words)

        # Pick random Latin words
        latin_words = [rng.choice(LATIN_VOCABULARY) for _ in range(word_count)]

        output_lines.append('.'.join(latin_words))

    return '\n'.join(output_lines)


if __name__ == "__main__":
    # Quick test of generators
    import sys
    sys.path.insert(0, str(__file__).rsplit('/', 1)[0])
    from utils import load_eva_folio, get_project_root

    print("Testing v2 generators...")
    root = get_project_root()
    eva_text = load_eva_folio("f10r", str(root))

    print("\n--- Original (first 3 lines) ---")
    for line in eva_text.strip().split('\n')[:3]:
        print(line[:80])

    print("\n--- Synthetic EVA (seed=1000) ---")
    synth = generate_synthetic_eva(eva_text, 1000)
    for line in synth.strip().split('\n')[:3]:
        print(line[:80])

    print("\n--- Character Shuffled (seed=2000) ---")
    shuf = generate_char_shuffled(eva_text, 2000)
    for line in shuf.strip().split('\n')[:3]:
        print(line[:80])

    print("\n--- Random Latin (seed=3000) ---")
    latin = generate_random_latin(eva_text, 3000)
    for line in latin.strip().split('\n')[:3]:
        print(line[:80])

    # Verify determinism
    synth2 = generate_synthetic_eva(eva_text, 1000)
    assert synth == synth2, "Synthetic EVA not deterministic!"

    print("\nAll generators working correctly!")
