#!/usr/bin/env python3
"""Generate a source-linked folio reader and reproducible JSON/CSV/Markdown exports."""

import argparse
import csv
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE / 'src'))

from folio_sources import (available_folios, image_for_folio, load_folio_source,
                          portable_path, sha256_file, validate_folio)
from pipeline import ZFDPipeline
from output import generate_json, generate_csv, generate_markdown, generate_html

PROFILES = {
    'shipping': ('lexicon_v2.csv', True),
    'frozen': ('lexicon.csv', False),
    'branch-candidates': ('candidates/lexicon_v2_folio_branch_2026-02-04.csv', False),
}


def build_parser():
    parser = argparse.ArgumentParser(
        description='Read a Voynich folio with its scan, EVA, proposed Croatian forms and English glosses.',
        epilog='Examples: python zfd_decoder/main.py f88r --out /tmp/f88r\n'
               '          python zfd_decoder/main.py f102r1 --source lsi --out /tmp/panel\n'
               '          python zfd_decoder/main.py --list',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('folio', nargs='?', help='Exact folio or panel ID, such as f88r or f102r1')
    parser.add_argument('eva_file', nargs='?', type=Path, help='Optional explicit UTF-8 EVA file (legacy CLI form)')
    parser.add_argument('--source', choices=('auto', 'raw', 'lsi'), default='auto',
                        help='auto: exact raw file first, then exact preferred-LSI identifier')
    choice = parser.add_mutually_exclusive_group()
    choice.add_argument('--profile', choices=tuple(PROFILES), help='Lexicon/compound profile; default: shipping')
    choice.add_argument('--lexicon', '-l', type=Path, help='Explicit CSV lexicon, with current parser rules')
    parser.add_argument('--compound', choices=('auto', 'on', 'off'), default='auto',
                        help='Override compound decomposition; auto follows the selected profile')
    parser.add_argument('--out', '--output-dir', dest='output_dir', type=Path, default=HERE / 'output',
                        help='Directory for the reader and JSON, CSV and Markdown exports')
    parser.add_argument('--list', action='store_true', help='List available exact text-source identifiers')
    return parser


def decode_for_reader(folio, eva_file=None, source='auto', profile='shipping', lexicon_file=None,
                      compound='auto'):
    folio = validate_folio(folio)
    text, provenance = load_folio_source(folio, eva_file, source)
    profile_path, profile_compound = PROFILES[profile]
    lexicon = Path(lexicon_file) if lexicon_file is not None else HERE / 'data' / profile_path
    pipeline = ZFDPipeline(data_dir=str(HERE / 'data'), lexicon_file=str(lexicon))
    enable_compound = profile_compound if compound == 'auto' else compound == 'on'
    if not enable_compound:
        pipeline.compound = None
    elif pipeline.compound is None:
        raise ValueError('Compound decomposition was requested but its lexicon is unavailable.')
    result = pipeline.process_folio(text, folio)
    if not result['diagnostics']['total_tokens']:
        raise ValueError(f'No EVA glyph words found for {folio}.')
    result['source'] = provenance
    result['configuration'] = {
        'reader_version': 1, 'profile': 'custom' if lexicon_file is not None else profile,
        'lexicon_file': portable_path(lexicon), 'lexicon_sha256': sha256_file(lexicon),
        'lexicon_rows': pipeline.lexicon.row_count,
        'lexicon_unique_forms': pipeline.lexicon.distinct_key_count,
        'duplicate_variants': pipeline.lexicon.duplicate_variant_count,
        'duplicate_policy': 'Last CSV row for a variant wins; overlapping entries are retained in the source file.',
        'compound_enabled': pipeline.compound is not None,
        'data_sha256': {portable_path(p): sha256_file(p) for p in sorted((HERE / 'data').glob('*.json'))},
        'code_sha256': {portable_path(p): sha256_file(p) for p in sorted([HERE / 'main.py', *(HERE / 'src').glob('*.py'), ROOT / '06_Pipelines' / 'complete_missing_folios.py'])},
        'score_definition': 'Additive parser score, not a probability of translation correctness.',
    }
    result['image'] = image_for_folio(folio)
    return result


def write_reader(result, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    folio = result['folio']
    outputs = (
        (generate_json, directory / f'{folio}_decode.json'),
        (generate_csv, directory / f'{folio}_table.csv'),
        (generate_markdown, directory / f'{folio}_report.md'),
        (generate_html, directory / f'{folio}_reader.html'),
    )
    for generator, path in outputs:
        generator(result, str(path))
    return [path for _, path in outputs]


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.list:
        if args.folio or args.eva_file:
            parser.error('--list does not take a folio or input file.')
        folios = available_folios()
        print('\n'.join(folios))
        print(f'{len(folios)} text-source IDs (including whole-page aliases and component panels).', file=sys.stderr)
        return 0
    if not args.folio:
        parser.error('Provide a folio ID, or use --list.')
    try:
        result = decode_for_reader(args.folio, args.eva_file, args.source,
                                   args.profile or 'shipping', args.lexicon, args.compound)
        paths = write_reader(result, args.output_dir)
    except (OSError, ValueError, csv.Error) as error:
        parser.error(str(error))
    diag = result['diagnostics']
    print(f"{result['folio']}: {diag['total_tokens']} tokens; {result['configuration']['profile']} profile")
    print('Match types: ' + ', '.join(f'{k}={v}' for k, v in diag['match_type_counts'].items()))
    for path in paths:
        print(path)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
