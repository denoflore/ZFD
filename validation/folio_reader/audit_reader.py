#!/usr/bin/env python3
"""Exercise every reader source and record exact token/mapping denominators."""

import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'zfd_decoder'))
from main import decode_for_reader
from src.folio_sources import available_folios, sha256_file


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    counts, matches, source_kinds = Counter(), Counter(), Counter()
    failures, folios = [], {}
    configuration = image_hashes = None
    for folio in available_folios():
        try:
            result = decode_for_reader(folio)
            diag = result['diagnostics']
            if sum(diag['match_type_counts'].values()) != diag['total_tokens']:
                raise ValueError('Match-type counts do not sum to token count')
            if result['source']['kind'] == 'lsi_preferred':
                for line in result['lines']:
                    for token in line:
                        number = token['id'].rsplit('.', 2)[1]
                        if number not in result['source']['line_ids']:
                            raise ValueError(f'Missing LSI source identity: {token["id"]}')
            counts.update({'identifiers': 1, 'tokens': diag['total_tokens'],
                           'with_image': int(result['image']['available'])})
            source_kinds[result['source']['kind']] += 1
            matches.update(diag['match_type_counts'])
            configuration = result['configuration']
            image_hashes = result['image']['mapping_sha256']
            folios[folio] = {
                'tokens': diag['total_tokens'], 'source': result['source']['kind'],
                'source_sha256': result['source']['sha256'],
                'text_sha256': result['source']['text_sha256'],
                'match_type_counts': diag['match_type_counts'],
                'image_ids': [image['identifier'] for image in result['image']['references']],
            }
        except (OSError, ValueError) as error:
            failures.append({'folio': folio, 'error': str(error)})
    report = {
        'base_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'scope': 'Reader auto selection: exact raw file first, otherwise preferred raw LSI records with drawing boundaries intact. Includes 18 whole-page aliases beside component panels.',
        'configuration': configuration, 'image_mapping_sha256': image_hashes,
        'audit_script_sha256': sha256_file(__file__), 'counts': dict(counts),
        'source_kinds': dict(source_kinds), 'match_type_counts': dict(matches),
        'failures': failures, 'by_folio': folios,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: report[key] for key in ('counts', 'source_kinds', 'match_type_counts', 'failures')}, indent=2))
    return 1 if failures or counts['identifiers'] != len(available_folios()) or counts['with_image'] != counts['identifiers'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
