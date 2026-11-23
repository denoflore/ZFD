"""Repo-local EVA selection and labelled Yale image references for the reader."""

from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / 'voynich_data' / 'raw_eva'
LSI_PATH = ROOT / '02_Transcriptions' / 'LSI_ivtff_0d.txt'
ROOT_MAP = ROOT / 'folio_iiif_map.json'
LABELLED_MAP = ROOT / '06_Pipelines' / 'glagolitic_ocr' / 'data' / 'folio_iiif_map.json'
YALE_CATALOGUE = 'https://collections.library.yale.edu/catalog/2002046'
FOLIO_ID = re.compile(r'f[1-9]\d*[rv](?:[1-9]\d*)?\Z')


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def portable_path(path):
    path = Path(path).resolve()
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def validate_folio(folio):
    folio = folio.lower()
    if not FOLIO_ID.fullmatch(folio):
        raise ValueError('Use a folio ID such as f88r or f102r1.')
    return folio


def folio_sort_key(folio):
    match = re.fullmatch(r'f(\d+)([rv])(\d*)', folio)
    return int(match[1]), match[2], int(match[3] or 0)


@lru_cache(maxsize=1)
def lsi_records():
    # Reuse the established transcriber preference and record parser. Do not
    # call eva_text_for/clean_eva: the recipe helper removes drawing breaks.
    sys.path.insert(0, str(ROOT / '06_Pipelines'))
    from complete_missing_folios import parse_lsi, TRANSCRIBER_PREFERENCE
    return parse_lsi(), tuple(TRANSCRIBER_PREFERENCE)


def available_folios():
    pages, _ = lsi_records()
    return sorted({p.stem for p in RAW_DIR.glob('f*.txt')} | set(pages), key=folio_sort_key)


def load_folio_source(folio, eva_file=None, selection='auto'):
    """Select an exact raw file or LSI identifier; never substitute a panel.

    LSI readings retain markup until the shared tokenizer processes it, so
    drawing interruptions survive as word boundaries. Every chosen record is
    identified in the output provenance.
    """
    folio = validate_folio(folio)
    if selection not in {'auto', 'raw', 'lsi'}:
        raise ValueError(f'Unknown source selection: {selection}')
    if eva_file is not None and selection != 'auto':
        raise ValueError('An explicit EVA file cannot be combined with --source.')
    raw_path = RAW_DIR / f'{folio}.txt'
    if eva_file is not None or (selection != 'lsi' and raw_path.is_file()):
        path = Path(eva_file) if eva_file is not None else raw_path
        text = path.read_text(encoding='utf-8-sig')
        source = {
            'kind': 'file' if eva_file is not None else 'raw_eva',
            'path': portable_path(path), 'sha256': sha256_file(path),
            'selection': 'Explicit input file.' if eva_file is not None else 'Exact raw_eva filename; all recorded readings retained.',
            'line_numbering': 'physical input-file lines', 'line_ids': {},
        }
    else:
        pages, preference = lsi_records()
        if selection == 'raw' or folio not in pages:
            alternatives = [f for f in available_folios()
                            if re.sub(r'(?<=[rv])\d+$', '', f) == re.sub(r'(?<=[rv])\d+$', '', folio)]
            hint = f" Available related IDs: {', '.join(alternatives)}." if alternatives else ''
            raise ValueError(f'No exact {selection} EVA source for {folio}.{hint}')
        selected = []
        line_ids = {}
        for line_id, readings in pages[folio].items():
            transcriber = next((t for t in preference if t in readings), next(iter(readings)))
            selected.append(readings[transcriber])
            line_ids[str(len(selected))] = f'{folio}.{line_id};{transcriber}'
        text = '\n'.join(selected)
        source = {
            'kind': 'lsi_preferred', 'path': portable_path(LSI_PATH),
            'sha256': sha256_file(LSI_PATH),
            'selection': 'One preferred transcriber per exact LSI record; raw drawing boundaries retained.',
            'transcriber_preference': list(preference),
            'line_numbering': 'selected LSI record sequence', 'line_ids': line_ids,
        }
    source['text_sha256'] = hashlib.sha256(text.encode('utf-8')).hexdigest()
    return text, source


@lru_cache(maxsize=1)
def image_inventory():
    root_map = json.loads(ROOT_MAP.read_text(encoding='utf-8'))
    labels = json.loads(LABELLED_MAP.read_text(encoding='utf-8'))
    by_base = {}
    for label, service in labels.items():
        if not re.fullmatch(r'https://collections\.library\.yale\.edu/iiif/2/\d+', service):
            raise ValueError(f'Unsupported image service in labelled map: {service}')
        identifier = service.rsplit('/', 1)[-1]
        for base in dict.fromkeys(re.findall(r'(?<!\d)(\d+[rv])\b', label)):
            by_base.setdefault(base, []).append({
                'label': label, 'identifier': identifier, 'service_url': service,
                'image_url': service + '/full/1000,/0/default.jpg',
                'full_url': service + '/full/full/0/default.jpg',
                'in_root_map': root_map.get(base) == identifier,
                'scope': 'folio reference' if label == base else 'labelled partial or composite reference',
            })
    for refs in by_base.values():
        refs.sort(key=lambda ref: int(ref['identifier']))
    return by_base


def image_for_folio(folio):
    folio = validate_folio(folio)
    base = re.match(r'f(\d+[rv])', folio)[1]
    references = [dict(ref) for ref in image_inventory().get(base, [])]
    result = {
        'available': bool(references), 'folio': folio, 'base_folio': 'f' + base,
        'source_url': YALE_CATALOGUE, 'references': references,
        'mapping_sha256': {portable_path(p): sha256_file(p) for p in (ROOT_MAP, LABELLED_MAP)},
    }
    if references:
        first = references[0]
        result.update({k: first[k] for k in ('identifier', 'label', 'image_url', 'full_url', 'scope')})
        result['note'] = ('References preserve the source map labels. Panel IDs refer to their parent side; '
                          'no panel crop or word coordinates are inferred. Multiple references are in image-ID order.')
    else:
        result['note'] = 'No labelled image reference is available for this folio.'
    return result
