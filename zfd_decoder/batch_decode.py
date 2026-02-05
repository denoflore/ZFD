#!/usr/bin/env python3
"""
ZFD Batch Decoder
Process all folios through the pipeline, generate per-folio reports
and corpus-wide statistics.
"""

import sys
import json
import os
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent / 'src'))
from pipeline import ZFDPipeline


def get_folio_section(folio_id):
    """Classify folio into manuscript section."""
    import re
    m = re.match(r'f(\d+)', folio_id)
    if not m:
        return 'unknown'
    num = int(m.group(1))
    
    if num <= 57:
        return 'herbal_a'
    elif num <= 66:
        return 'herbal_b'
    elif num <= 73:
        return 'astronomical'
    elif num <= 86:
        return 'biological'
    elif num <= 116:
        return 'pharmaceutical'
    else:
        return 'unknown'


def natural_sort_key(folio_id):
    """Sort folios naturally: f1r, f1v, f2r, f2v, ..."""
    import re
    m = re.match(r'f(\d+)([rv])(\d*)', folio_id)
    if m:
        num = int(m.group(1))
        side = 0 if m.group(2) == 'r' else 1
        sub = int(m.group(3)) if m.group(3) else 0
        return (num, side, sub)
    return (999, 0, 0)


def process_all(input_dir='input', data_dir='data', output_dir='output/folios'):
    """Process all folio files and generate reports."""
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize pipeline
    pipeline = ZFDPipeline(data_dir=data_dir)
    
    # Find all folio files
    folio_files = sorted(input_path.glob('f*.txt'), key=lambda p: natural_sort_key(p.stem))
    
    print(f'ZFD Batch Decoder')
    print(f'Folios found: {len(folio_files)}')
    print(f'Pipeline: lexicon={len(pipeline.lexicon.stems)} stems'
          f', compound={"yes" if pipeline.compound else "no"}')
    print('=' * 60)
    
    # Corpus-wide stats
    corpus_stats = {
        'total_folios': 0,
        'total_tokens': 0,
        'total_known': 0,
        'total_unknown': 0,
        'section_stats': defaultdict(lambda: {'folios': 0, 'tokens': 0, 'known': 0}),
        'all_unknown_stems': Counter(),
        'all_categories': Counter(),
        'folio_results': [],
    }
    
    for folio_file in folio_files:
        folio_id = folio_file.stem
        
        with open(folio_file) as f:
            text = f.read().strip()
        
        if not text:
            continue
        
        # Process
        result = pipeline.process_folio(text, folio_id)
        diag = result['diagnostics']
        
        known = diag['known_stems']
        unknown = diag['unknown_stems']
        total = known + unknown
        ratio = diag['known_ratio']
        section = get_folio_section(folio_id)
        
        # Update corpus stats
        corpus_stats['total_folios'] += 1
        corpus_stats['total_tokens'] += total
        corpus_stats['total_known'] += known
        corpus_stats['total_unknown'] += unknown
        corpus_stats['section_stats'][section]['folios'] += 1
        corpus_stats['section_stats'][section]['tokens'] += total
        corpus_stats['section_stats'][section]['known'] += known
        
        for stem in diag.get('unknown_stem_list', []):
            corpus_stats['all_unknown_stems'][stem] += 1
        for cat, count in diag.get('category_distribution', {}).items():
            corpus_stats['all_categories'][cat] += count
        
        corpus_stats['folio_results'].append({
            'folio': folio_id,
            'section': section,
            'tokens': total,
            'known': known,
            'ratio': ratio,
            'avg_conf': diag['average_confidence'],
        })
        
        # Write per-folio decode
        write_folio_report(output_path, folio_id, section, result)
        
        # Progress
        bar = '#' * int(ratio * 20) + '-' * (20 - int(ratio * 20))
        print(f'  {folio_id:10s} [{bar}] {ratio:5.1%}  ({known}/{total})  {section}')
    
    # Write corpus summary
    write_corpus_summary(output_path, corpus_stats)
    
    # Print summary
    print()
    print('=' * 60)
    total = corpus_stats['total_tokens']
    known = corpus_stats['total_known']
    ratio = known / total if total else 0
    print(f'CORPUS: {corpus_stats["total_folios"]} folios, {total} tokens')
    print(f'KNOWN: {known}/{total} ({ratio:.1%})')
    print()
    print('BY SECTION:')
    for section, stats in sorted(corpus_stats['section_stats'].items()):
        s_ratio = stats['known'] / stats['tokens'] if stats['tokens'] else 0
        print(f'  {section:20s}: {stats["folios"]:3d} folios, '
              f'{stats["known"]:5d}/{stats["tokens"]:5d} ({s_ratio:.1%})')
    print()
    print(f'Top 20 unknown stems:')
    for stem, count in corpus_stats['all_unknown_stems'].most_common(20):
        print(f'  {stem:20s} x{count}')


def write_folio_report(output_path, folio_id, section, result):
    """Write per-folio markdown decode report."""
    filepath = output_path / f'{folio_id}.md'
    diag = result['diagnostics']
    
    with open(filepath, 'w') as f:
        f.write(f'# {folio_id} - {section}\n\n')
        f.write(f'Known: {diag["known_stems"]}/{diag["known_stems"]+diag["unknown_stems"]} ')
        f.write(f'({diag["known_ratio"]:.1%}) | ')
        f.write(f'Avg confidence: {diag["average_confidence"]:.3f}\n\n')
        
        f.write('## Interlinear Decode\n\n')
        for i, line in enumerate(result['lines']):
            if not line:
                continue
            eva_tokens = [t['eva'] for t in line]
            eng_tokens = [t['english'] or t['stem_gloss'] or f'?{t["stem"]}?' for t in line]
            
            f.write(f'**L{i+1}** EVA: `{" ".join(eva_tokens)}`\n')
            f.write(f'ENG: {" | ".join(eng_tokens)}\n\n')


def write_corpus_summary(output_path, stats):
    """Write corpus-wide summary JSON."""
    summary = {
        'total_folios': stats['total_folios'],
        'total_tokens': stats['total_tokens'],
        'total_known': stats['total_known'],
        'corpus_ratio': stats['total_known'] / stats['total_tokens'] if stats['total_tokens'] else 0,
        'section_stats': {k: dict(v) for k, v in stats['section_stats'].items()},
        'top_unknown_stems': stats['all_unknown_stems'].most_common(50),
        'category_distribution': dict(stats['all_categories']),
        'folio_results': stats['folio_results'],
    }
    
    with open(output_path / 'corpus_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Also write markdown summary
    with open(output_path / 'CORPUS_SUMMARY.md', 'w') as f:
        f.write('# ZFD Corpus Decode Summary\n\n')
        ratio = summary['corpus_ratio']
        f.write(f'**{stats["total_folios"]} folios | '
                f'{stats["total_tokens"]} tokens | '
                f'{ratio:.1%} resolution**\n\n')
        
        f.write('## By Section\n\n')
        f.write('| Section | Folios | Tokens | Known | Ratio |\n')
        f.write('|---------|--------|--------|-------|-------|\n')
        for section, s in sorted(stats['section_stats'].items()):
            s_ratio = s['known'] / s['tokens'] if s['tokens'] else 0
            f.write(f'| {section} | {s["folios"]} | {s["tokens"]} | '
                    f'{s["known"]} | {s_ratio:.1%} |\n')
        
        f.write('\n## Per-Folio Results\n\n')
        f.write('| Folio | Section | Tokens | Ratio | Confidence |\n')
        f.write('|-------|---------|--------|-------|------------|\n')
        for fr in stats['folio_results']:
            f.write(f'| {fr["folio"]} | {fr["section"]} | {fr["tokens"]} | '
                    f'{fr["ratio"]:.1%} | {fr["avg_conf"]:.3f} |\n')


if __name__ == '__main__':
    process_all()
