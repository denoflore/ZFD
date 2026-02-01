"""
ZFD Data Loader
Loads all Master Key CSVs, transcription, and morphological triples.
"""

import re
import csv
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional


class ZFDLoader:
    """Load and parse ZFD Voynich Manuscript data structures."""

    def __init__(self, base_path: str = None):
        if base_path is None:
            base_path = Path(__file__).parent.parent
        self.base_path = Path(base_path)

        # Data containers
        self.operators: Dict[str, dict] = {}
        self.suffixes: Dict[str, dict] = {}
        self.lexicon: List[dict] = []
        self.lexicon_by_status: Dict[str, List[dict]] = defaultdict(list)
        self.transcription: Dict[str, List[dict]] = {}  # folio -> lines
        self.morphological_triples: List[dict] = []
        self.triple_counts: Dict[Tuple[str, str, str], int] = {}

        # Load all data
        self._load_operators()
        self._load_suffixes()
        self._load_lexicon()
        self._load_transcription()
        self._load_morphological_triples()

    def _load_operators(self):
        """Load operators from MasterKey_v1_1__operators.csv."""
        path = self.base_path / "08_Final_Proofs/Master_Key/MasterKey_v1_1__operators.csv"
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                prefix = row.get('first2', '').strip()
                if prefix:
                    self.operators[prefix] = {
                        'role': row.get('role', ''),
                        'share_pct': float(row.get('share_pct', 0) or 0),
                        'analogue': row.get('analogue_note', '')
                    }

    def _load_suffixes(self):
        """Load suffixes from MasterKey_v1_1__suffixes.csv."""
        path = self.base_path / "08_Final_Proofs/Master_Key/MasterKey_v1_1__suffixes.csv"
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                suffix = row.get('suffix', '').strip()
                if suffix:
                    self.suffixes[suffix] = {
                        'role': row.get('hypothesized_role', ''),
                        'status': row.get('status', '')
                    }

    def _load_lexicon(self):
        """Load Herbal Lexicon with status tracking."""
        path = self.base_path / "08_Final_Proofs/Master_Key/Herbal_Lexicon_v3_5_full.csv"
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                entry = {
                    'name': row.get('name', ''),
                    'variant': row.get('variant', ''),
                    'context': row.get('variant_context', ''),
                    'inference': row.get('inference', ''),
                    'lexical_link': row.get('lexical_link', ''),
                    'status': row.get('status', '')
                }
                if entry['variant']:
                    self.lexicon.append(entry)
                    self.lexicon_by_status[entry['status']].append(entry)

    def _load_transcription(self):
        """
        Parse transcription into folio -> lines -> tokens structure.

        Uses Takahashi's transcription (;T suffix) as primary when available,
        falls back to other transcribers.
        """
        path = self.base_path / "02_Transcriptions/LSI_ivtff_0d.txt"

        # Regex to parse line identifiers: <f1r.1,@P0;H> or <f1r.2,+P0;C>
        # Note: unit can start with @ or +
        line_pattern = re.compile(r'^<(f\d+[rv]\d?)\.([\w.]+),[@+]([^;]+);([A-Z])>\s*(.*)$')

        current_folio = None
        folio_lines = defaultdict(lambda: defaultdict(dict))  # folio -> line_num -> transcriber -> text

        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.strip()

                # Skip comments and empty lines
                if line.startswith('#') or not line:
                    continue

                # Check for folio header
                if line.startswith('<f') and '>' in line and '.' not in line.split('>')[0]:
                    # Folio header like <f1r>
                    match = re.match(r'<(f\d+[rv](?:\d)?)>', line)
                    if match:
                        current_folio = match.group(1)
                    continue

                # Parse transcription line
                match = line_pattern.match(line)
                if match:
                    folio = match.group(1)
                    line_num = match.group(2)
                    unit = match.group(3)
                    transcriber = match.group(4)
                    text = match.group(5)

                    # Clean trailing markers
                    text = text.rstrip('!-=')

                    folio_lines[folio][line_num][transcriber] = {
                        'unit': unit,
                        'text': text,
                        'tokens': self._tokenize(text)
                    }

        # Consolidate - prefer Takahashi (T), then Currier (C), then others
        transcriber_priority = ['T', 'C', 'H', 'F', 'N', 'U']

        def line_sort_key(x):
            """Sort line numbers: extract leading digits."""
            m = re.match(r'^(\d+)', x)
            return int(m.group(1)) if m else 0

        for folio, lines in folio_lines.items():
            self.transcription[folio] = []
            for line_num in sorted(lines.keys(), key=line_sort_key):
                line_data = lines[line_num]

                # Pick best available transcriber
                chosen = None
                for t in transcriber_priority:
                    if t in line_data:
                        chosen = line_data[t]
                        chosen['line_num'] = line_sort_key(line_num)
                        chosen['transcriber'] = t
                        break

                if chosen is None and line_data:
                    # Take first available
                    t = list(line_data.keys())[0]
                    chosen = line_data[t]
                    chosen['line_num'] = line_sort_key(line_num)
                    chosen['transcriber'] = t

                if chosen:
                    self.transcription[folio].append(chosen)

    def _tokenize(self, text: str) -> List[str]:
        """Split text into tokens, handling . and , as separators."""
        # Replace separators with space
        text = re.sub(r'[.,]', ' ', text)
        # Remove special markers
        text = re.sub(r'[!\-=<>{}*?@]', '', text)
        # Split and filter
        tokens = [t.strip() for t in text.split() if t.strip()]
        return tokens

    def _load_morphological_triples(self):
        """Load morphological triples counts."""
        path = self.base_path / "08_Final_Proofs/Final_Report/morphological_triples_counts.csv"
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                op = row.get('operator', '').strip()
                stem = row.get('stem', '').strip()
                suffix = row.get('suffix', '').strip()
                count_str = row.get('count', '0').strip()

                # Skip malformed rows
                if not count_str.isdigit():
                    continue

                count = int(count_str)

                entry = {
                    'operator': op,
                    'stem': stem,
                    'suffix': suffix,
                    'count': count
                }
                self.morphological_triples.append(entry)
                self.triple_counts[(op, stem, suffix)] = count

    def get_word_count(self) -> int:
        """Get total word count from transcription."""
        total = 0
        for folio, lines in self.transcription.items():
            for line in lines:
                total += len(line.get('tokens', []))
        return total

    def get_unique_triples(self) -> int:
        """Get count of unique morphological triples."""
        return len(self.morphological_triples)

    def get_confirmed_mappings(self) -> List[dict]:
        """Get all CONFIRMED lexicon entries."""
        return self.lexicon_by_status.get('CONFIRMED', [])

    def get_candidate_mappings(self) -> List[dict]:
        """Get all CANDIDATE lexicon entries."""
        return self.lexicon_by_status.get('CANDIDATE', [])

    def find_stem_occurrences(self, stem: str, section: str = 'herbal') -> List[dict]:
        """
        Find all occurrences of a stem in specified section.

        Args:
            stem: The stem pattern to search for
            section: 'herbal' (f1-f66), 'pharma' (f87-f102), or 'all'

        Returns:
            List of {folio, line_num, token, context}
        """
        occurrences = []

        # Define folio ranges for sections
        herbal_folios = set()
        for i in range(1, 67):
            herbal_folios.add(f'f{i}r')
            herbal_folios.add(f'f{i}v')

        pharma_folios = set()
        for i in range(87, 103):
            pharma_folios.add(f'f{i}r')
            pharma_folios.add(f'f{i}v')

        for folio, lines in self.transcription.items():
            # Filter by section
            if section == 'herbal' and folio not in herbal_folios:
                continue
            if section == 'pharma' and folio not in pharma_folios:
                continue

            for line in lines:
                for i, token in enumerate(line.get('tokens', [])):
                    if stem in token:
                        # Get context (surrounding tokens)
                        tokens = line['tokens']
                        context_start = max(0, i - 2)
                        context_end = min(len(tokens), i + 3)
                        context = tokens[context_start:context_end]

                        occurrences.append({
                            'folio': folio,
                            'line_num': line.get('line_num', 0),
                            'token': token,
                            'context': context
                        })

        return occurrences

    def get_stem_frequency(self, stem: str) -> int:
        """Get total frequency of a stem from morphological triples."""
        total = 0
        for entry in self.morphological_triples:
            if stem in entry['stem']:
                total += entry['count']
        return total

    def summary(self) -> str:
        """Generate summary of loaded data."""
        lines = [
            "=== ZFD Data Loader Summary ===",
            f"Operators: {len(self.operators)}",
            f"Suffixes: {len(self.suffixes)}",
            f"Lexicon entries: {len(self.lexicon)}",
            f"  - CONFIRMED: {len(self.lexicon_by_status.get('CONFIRMED', []))}",
            f"  - CANDIDATE: {len(self.lexicon_by_status.get('CANDIDATE', []))}",
            f"  - LOW: {len(self.lexicon_by_status.get('LOW', []))}",
            f"  - PROVISIONAL: {len(self.lexicon_by_status.get('PROVISIONAL', []))}",
            f"Folios parsed: {len(self.transcription)}",
            f"Total words: {self.get_word_count()}",
            f"Unique morphological triples: {self.get_unique_triples()}",
        ]
        return "\n".join(lines)


def main():
    """Test the loader."""
    loader = ZFDLoader()
    print(loader.summary())

    # Test stem search
    print("\n--- Sample 'ed' occurrences (first 5) ---")
    ed_occ = loader.find_stem_occurrences('ed', section='herbal')[:5]
    for occ in ed_occ:
        print(f"  {occ['folio']}:{occ['line_num']} - {occ['token']} | context: {' '.join(occ['context'])}")

    # Test 'od' occurrences
    print("\n--- Sample 'od' occurrences (first 5) ---")
    od_occ = loader.find_stem_occurrences('od', section='herbal')[:5]
    for occ in od_occ:
        print(f"  {occ['folio']}:{occ['line_num']} - {occ['token']} | context: {' '.join(occ['context'])}")


if __name__ == "__main__":
    main()
