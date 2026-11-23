"""Reader acceptance checks against real folio and panel source records."""

import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'zfd_decoder'))
sys.path.insert(0, str(ROOT / 'zfd_decoder' / 'src'))
from main import decode_for_reader
from folio_sources import image_for_folio, load_folio_source
from tokenizer import tokenize_folio


def test_foldout_source_preserves_drawing_boundaries_and_record_identity():
    text, source = load_folio_source('f102r1')
    words = [token.eva for line in tokenize_folio(text, 'f102r1') for token in line]
    assert len(words) == 109  # legacy recipe cleanup loses five drawing breaks
    assert source['text_sha256'] == '0443c68e6e9836be689189ab7266e53e746a111929d98da22cf67c42e904a2e9'
    assert source['kind'] == 'lsi_preferred'
    assert len(source['line_ids']) == 17
    assert all(value.startswith('f102r1.') and value.endswith(';H')
               for value in source['line_ids'].values())
    assert '<->' in text
    assert source['sha256'] == hashlib.sha256((ROOT / source['path']).read_bytes()).hexdigest()


def test_panel_images_preserve_partial_and_composite_labels():
    panel = image_for_folio('f102r1')
    assert panel['available'] and panel['base_folio'] == 'f102r'
    assert panel['label'] == '101v (part) and 102r'
    assert panel['identifier'] == '1006251'
    assert panel['image_url'].endswith('/1006251/full/1000,/0/default.jpg')
    alternatives = image_for_folio('f95v')['references']
    assert [(ref['label'], ref['identifier']) for ref in alternatives] == [
        ('95v (part)', '1006242'), ('95v', '1006243')]
    assert not image_for_folio('f999r')['available']


def test_source_selection_never_silently_replaces_a_panel_with_its_parent():
    with pytest.raises(ValueError, match='No exact raw EVA source'):
        load_folio_source('f102r1', selection='raw')
    with pytest.raises(ValueError, match='No exact lsi EVA source'):
        load_folio_source('f102r', selection='lsi')
    with pytest.raises(ValueError, match='No exact auto EVA source'):
        load_folio_source('f85v')  # image-only side has no exact text source


def test_lexicon_profiles_keep_shipping_data_separate_from_retained_candidates():
    shipping = decode_for_reader('f88r')
    candidate = decode_for_reader('f88r', profile='branch-candidates')
    frozen = decode_for_reader('f88r', profile='frozen')
    config = shipping['configuration']
    assert config['lexicon_sha256'] == '68fb55f2b4c7725b300cab5c438d7abbc25837f5a6b8a499747193241423741b'
    assert (config['lexicon_rows'], config['lexicon_unique_forms']) == (212, 208)
    assert config['compound_enabled'] is True
    assert candidate['configuration']['lexicon_rows'] == 185
    assert candidate['configuration']['compound_enabled'] is False
    assert frozen['configuration']['lexicon_rows'] == 92
    assert frozen['configuration']['compound_enabled'] is False
    receipt = json.loads((ROOT / 'zfd_decoder/data/candidates/FOLIO_BRANCH_RECONCILIATION.json').read_text())
    assert candidate['configuration']['lexicon_sha256'] == receipt['archived_sha256']


def test_cli_exports_utf8_reader_from_outside_repo_and_rejects_bad_input(tmp_path):
    source = tmp_path / 'input.txt'
    source.write_text('=== Folio f88r ===\n[Text]\nsar.ol.shol.orald\n', encoding='utf-8')
    out = tmp_path / 'reader'
    cmd = [sys.executable, str(ROOT / 'zfd_decoder/main.py'), 'f88r', str(source), '--out', str(out)]
    run = subprocess.run(cmd, cwd=tmp_path, capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    assert {path.name for path in out.iterdir()} == {
        'f88r_decode.json', 'f88r_reader.html', 'f88r_report.md', 'f88r_table.csv'}
    decoded = json.loads((out / 'f88r_decode.json').read_text(encoding='utf-8'))
    tokens = [token for line in decoded['lines'] for token in line]
    assert [token['eva'] for token in tokens] == ['sar', 'ol', 'shol', 'orald']
    assert tokens[-1]['matched_form'] == 'oral'
    assert tokens[-1]['croatian'] == 'oralno[d]'
    assert 'š' in (out / 'f88r_reader.html').read_text(encoding='utf-8')
    with (out / 'f88r_table.csv').open(encoding='utf-8', newline='') as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 4 and rows[-1]['matched_form'] == 'oral'
    invalid = subprocess.run([sys.executable, str(ROOT / 'zfd_decoder/main.py'), '../f88r', str(source), '--out', str(tmp_path / 'bad')], cwd=tmp_path, capture_output=True, text=True)
    assert invalid.returncode == 2 and not (tmp_path / 'bad').exists()
