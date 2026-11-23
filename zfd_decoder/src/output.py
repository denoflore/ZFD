"""Portable reading views and evidence-preserving ZFD exports."""

import csv
import html
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Dict
from urllib.parse import urlsplit


MATCH_LABELS = {
    "whole_word": "Whole word",
    "exact_stem": "Exact stem",
    "suffix": "Stem + suffix",
    "partial": "Partial",
    "compound": "Compound",
    "unresolved": "Unresolved",
    "not_recorded": "Not recorded",
}
MATCH_HELP = {
    "whole_word": "The full EVA token matched a lexicon entry.",
    "exact_stem": "The transformed stem matched a lexicon entry exactly.",
    "suffix": "The stem matched after a recognised suffix was removed.",
    "partial": "Only part of the stem matched. Inspect the unmatched residue.",
    "compound": "The parser proposed a combination of smaller entries.",
    "unresolved": "No lexical match was recorded.",
    "not_recorded": "This output predates recorded match provenance.",
}
# Foldout panel identifiers such as f67r1 are valid; arbitrary paths are not.
FOLIO_RE = re.compile(r"f[1-9]\d*[rv](?:[1-9]\d*)?\Z")


def _text(value):
    return "" if value is None else str(value)


def _esc(value):
    return html.escape(_text(value), quote=True)


def _json(value, pretty=False):
    return json.dumps(value, ensure_ascii=False, indent=2 if pretty else None)


def _match_type(token):
    value = token.get("match_type")
    return value if value in MATCH_LABELS else "not_recorded"


def _safe_url(value):
    """Allow external reference URLs, never executable or local URL schemes."""
    value = _text(value)
    if not value or any(ord(char) < 33 for char in value):
        return ""
    try:
        parsed = urlsplit(value)
        return value if parsed.scheme in {"https", "http"} and parsed.netloc else ""
    except ValueError:
        return ""


def _score(value):
    try:
        number = float(value)
        if math.isfinite(number):
            return f"{number:.3f}"
    except (ValueError, TypeError):
        pass
    return "Not recorded"


def _source_line(token):
    parts = _text(token.get("id")).rsplit(".", 2)
    return parts[-2] if len(parts) == 3 and parts[-2].isdigit() else ""


def _line_reference(result, line, index):
    numbers = {_source_line(token) for token in line} - {""}
    number = next(iter(numbers)) if len(numbers) == 1 else ""
    original = result.get("source", {}).get("line_ids", {}).get(number, "")
    label = _text(original) or (f"Source line {number}" if number else f"Text group {index + 1}")
    return number, _text(original), label


def _metadata(result):
    return {key: value for key, value in result.items() if key != "lines"}


def generate_json(result: Dict, output_path: str):
    """Write the complete result without dropping additive provenance fields."""
    Path(output_path).write_text(_json(result, pretty=True) + "\n", encoding="utf-8")


def generate_csv(result: Dict, output_path: str):
    """Write token rows with complete JSON records and reproducibility metadata.

    Existing scalar columns remain available. The first data row carries complete
    run metadata; every token has its complete JSON record. An empty decode gets
    an explicitly marked metadata row so it still identifies its input.
    """
    fieldnames = [
        "token_id", "eva", "zfd", "operator", "stem", "suffix", "expansion",
        "croatian", "english", "confidence", "notes", "record_type", "folio",
        "source_line", "source_line_id", "match_type", "matched_form",
        "matched_croatian", "matched_category", "matched_status", "matched_source",
        "stem_surface", "unmatched_prefix", "unmatched_suffix", "compound_parts_json",
        "rewrites_json", "notes_json", "token_json", "run_metadata_json",
    ]
    run_metadata = _json(_metadata(result))
    with open(output_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        count = 0
        for index, line in enumerate(result.get("lines", [])):
            number, original, _ = _line_reference(result, line, index)
            for token in line:
                row = {key: token.get(key, "") for key in fieldnames if key in token}
                notes = token.get("notes", [])
                row.update({
                    "folio": result.get("folio", ""),
                    "run_metadata_json": run_metadata if count == 0 else "",
                    "record_type": "token", "token_id": token.get("id", ""),
                    "source_line": number, "source_line_id": original,
                    "notes": "; ".join(map(str, notes)) if isinstance(notes, list) else _text(notes),
                    "compound_parts_json": _json(token.get("compound_parts", [])),
                    "rewrites_json": _json(token.get("rewrites", [])),
                    "notes_json": _json(notes), "token_json": _json(token),
                })
                writer.writerow(row)
                count += 1
        if not count:
            writer.writerow({"folio": result.get("folio", ""), "record_type": "metadata",
                             "run_metadata_json": run_metadata})


def _md(value):
    """Escape text inside Markdown headings and table cells, including raw HTML."""
    value = _esc(value).replace("\\", "\\\\")
    for character in ("`", "*", "_", "[", "]", "|", "#"):
        value = value.replace(character, "\\" + character)
    return value.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>")


def _fenced_json(value):
    content = _json(value, pretty=True)
    longest = max((len(run) for run in re.findall(r"`+", content)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}json\n{content}\n{fence}"


def _markdown_reference(label, url):
    url = _safe_url(url)
    if not url:
        return _md(label)
    for character, encoded in (("<", "%3C"), (">", "%3E"), ("\\", "%5C")):
        url = url.replace(character, encoded)
    return f"[{_md(label)}](<{url}>)"


def generate_markdown(result: Dict, output_path: str):
    """Write aligned readings plus complete source, configuration and token evidence."""
    md = [
        f"# Folio {_md(result.get('folio', ''))} Decode Report", "",
        "Croatian renderings and English glosses are outputs of the ZFD parser. "
        "Parser scores are rule-based scores, not calibrated probabilities.", "",
        "## Source, image and configuration", "",
        _fenced_json(_metadata(result)), "",
    ]
    image = result.get("image", {})
    references = image.get("references", [])
    if references:
        md.extend(["## Image references", ""])
        for reference in references:
            label = reference.get("label") or reference.get("identifier") or "Image reference"
            link = _markdown_reference(label, reference.get("full_url") or reference.get("image_url"))
            md.append(f"- {link}")
            if reference.get("scope"):
                md.extend(["", f"  Scope: {_md(reference['scope'])}"])
        md.append("")
    md.extend(["## Line-aligned reading", ""])
    for index, line in enumerate(result.get("lines", [])):
        _, _, label = _line_reference(result, line, index)
        md.extend([f"### {_md(label)}", "", "| Layer | Text |", "| --- | --- |"])
        for key, name in (("eva", "EVA"), ("zfd", "ZFD"),
                          ("croatian", "Croatian"), ("english", "English gloss")):
            md.append(f"| {name} | {' '.join(_md(token.get(key, '')) for token in line)} |")
        md.extend([
            "", "| Token | Match | Matched form | Stem surface | Prefix residue | Suffix residue | Lexicon status | Parser score |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ])
        for token in line:
            values = [token.get("id", ""), MATCH_LABELS[_match_type(token)],
                      token.get("matched_form", ""), token.get("stem_surface", ""),
                      token.get("unmatched_prefix", ""), token.get("unmatched_suffix", ""),
                      token.get("matched_status", ""), _score(token.get("confidence"))]
            md.append("| " + " | ".join(_md(value) for value in values) + " |")
        md.extend(["", "#### Complete token provenance", "", _fenced_json(line), ""])
    if not result.get("lines"):
        md.extend(["No tokens were produced for this input.", ""])
    Path(output_path).write_text("\n".join(md), encoding="utf-8")


def _badge(kind):
    return (f'<span class="badge match-{kind}" title="{_esc(MATCH_HELP[kind])}">'
            f'{_esc(MATCH_LABELS[kind])}</span>')


def _token_record(token, identifier):
    kind = _match_type(token)
    parts = [
        f'<details class="token-record match-{kind}" id="{identifier}" '
        f'data-match="{kind}" data-search="{_esc(_json(token).lower())}">',
        '<summary><span class="token-summary">',
        f'<code class="token-eva">{_esc(token.get("eva"))}</code>',
        _badge(kind),
        f'<span class="token-id">{_esc(token.get("id"))}</span>',
        f'<span class="score">Parser score {_esc(_score(token.get("confidence")))}</span>',
        '</span></summary><div class="token-body">',
    ]
    if kind == "partial":
        prefix = _esc(token.get("unmatched_prefix")) or "none recorded"
        suffix = _esc(token.get("unmatched_suffix")) or "none recorded"
        parts.append('<p class="residue-note"><strong>Unmatched residue:</strong> '
                     f'prefix <code>{prefix}</code> · suffix <code>{suffix}</code></p>')
    elif kind == "compound":
        parts.append('<p class="residue-note">Compound proposal. Its recorded parts appear below.</p>')
    parts.append('<dl class="evidence-grid">')
    for key, label in (
        ("stem_surface", "Stem surface"), ("matched_form", "Matched form"),
        ("matched_croatian", "Matched Croatian"), ("matched_category", "Lexicon category"),
        ("matched_status", "Lexicon status"), ("matched_source", "Lexicon source"),
        ("unmatched_prefix", "Unmatched prefix"), ("unmatched_suffix", "Unmatched suffix"),
        ("operator", "Operator"), ("suffix", "Suffix"),
        ("expansion", "Expansion"),
    ):
        parts.append(f'<div><dt>{label}</dt><dd>{_esc(token.get(key)) or "None recorded"}</dd></div>')
    parts.append('</dl>')
    if token.get("compound_parts"):
        parts.append('<h4>Compound parts</h4><pre>'
                     + _esc(_json(token["compound_parts"], pretty=True)) + '</pre>')
    for key, label in (("rewrites", "Recorded transformations"), ("notes", "Notes")):
        value = token.get(key)
        if value:
            items = value if isinstance(value, list) else [value]
            parts.append(f'<h4>{label}</h4><ul>'
                         + ''.join(f'<li>{_esc(item)}</li>' for item in items) + '</ul>')
    parts.append('<details class="raw-token"><summary>Full token record</summary><pre>'
                 + _esc(_json(token, pretty=True)) + '</pre></details></div></details>')
    return ''.join(parts)


def _image_panel(result):
    info = result.get("image", {})
    image_url = _safe_url(info.get("image_url")) if info.get("available") else ""
    full_url = _safe_url(info.get("full_url"))
    source_url = _safe_url(info.get("source_url"))
    parts = ['<aside class="manuscript-panel" aria-labelledby="manuscript-heading">',
             '<div class="panel-heading"><span class="eyebrow">The manuscript</span>',
             '<h2 id="manuscript-heading">Page reference</h2></div>']
    if info.get("label"):
        parts.append('<p class="image-selected">' + _esc(info["label"]) + '</p>')
    if image_url:
        parts.extend([
            '<figure class="manuscript-figure" id="image-figure">',
            f'<img id="manuscript-image" src="{_esc(image_url)}" '
            f'alt="Manuscript image for {_esc(result.get("folio"))}" decoding="async">',
            '<div class="image-fallback" id="image-fallback" hidden><span class="image-mark" aria-hidden="true">▧</span>',
            '<h3>Image unavailable</h3><p>The image could not be loaded. '
            'The complete reading and token records are available below.</p></div>',
            '<figcaption>Full-page reference. Text follows source-line order; '
            'individual words are not mapped to image coordinates.</figcaption></figure>',
        ])
    else:
        parts.append('<div class="image-fallback"><span class="image-mark" aria-hidden="true">▧</span>'
                     '<h3>No verified image mapping</h3><p>A manuscript image has not been attached '
                     'to this record. All text and provenance remain available.</p></div>')
    if info.get("identifier"):
        parts.append('<p class="image-identifier">Image identifier: <code>'
                     + _esc(info["identifier"]) + '</code></p>')
    if info.get("note"):
        parts.append('<p class="image-note">' + _esc(info["note"]) + '</p>')
    if info.get("scope"):
        parts.append('<p class="image-note">Scope: ' + _esc(info["scope"]) + '</p>')
    links = []
    for url, label in ((full_url, "Open full image ↗"), (source_url, "Collection record ↗")):
        if url:
            links.append(f'<a href="{_esc(url)}" target="_blank" rel="noopener noreferrer">{label}</a>')
    if links:
        parts.append('<div class="image-links">' + ''.join(links) + '</div>')
    if info.get("references"):
        parts.append('<div class="scan-references"><h3>Available scans</h3><ul>')
        for reference in info["references"]:
            label = reference.get("label") or reference.get("identifier") or "Image reference"
            url = _safe_url(reference.get("full_url")) or _safe_url(reference.get("image_url"))
            parts.append('<li>')
            if url:
                parts.append(f'<a href="{_esc(url)}" target="_blank" rel="noopener noreferrer">{_esc(label)}</a>')
            else:
                parts.append(_esc(label))
            if reference.get("scope"):
                parts.append('<span>' + _esc(reference["scope"]) + '</span>')
            parts.append('</li>')
        parts.append('</ul></div>')
    if image_url:
        parts.append('<p class="offline-note">The image needs a connection. '
                     'Text, filters and token records work offline.</p>')
    parts.append('</aside>')
    return ''.join(parts)


def generate_html(result: Dict, output_path: str):
    """Generate a standalone, accessible folio reader with no asset dependencies."""
    folio = _text(result.get("folio"))
    lines = result.get("lines", [])
    tokens = [token for line in lines for token in line]
    counts = Counter(_match_type(token) for token in tokens)
    source = result.get("source", {})
    source_kind = {
        "raw_eva": "Raw EVA input", "lsi_preferred": "Preferred LSI transcription", "file": "Input file"
    }.get(source.get("kind"), "Recorded input")
    parts = [
        '<!doctype html><html lang="en"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f'<title>{_esc(folio)} · ZFD folio reader</title><style>{_CSS}</style></head><body>',
        '<a class="skip-link" href="#reading">Skip to the reading</a>',
        '<header class="page-header"><div class="header-top"><a class="wordmark" href="#top">'
        'ZFD <span>FOLIO READER</span></a><nav class="exports" aria-label="Download exports">',
    ]
    if FOLIO_RE.fullmatch(folio):
        for extension, filename in (("JSON", f"{folio}_decode.json"), ("CSV", f"{folio}_table.csv"),
                                    ("Markdown", f"{folio}_report.md")):
            parts.append(f'<a href="{_esc(filename)}" download>{extension} <span aria-hidden="true">↗</span></a>')
    parts.extend([
        '</nav></div><div class="hero" id="top"><div><p class="eyebrow">Transcription / interpretation / evidence</p>',
        f'<h1>Folio <span>{_esc(folio)}</span></h1>',
        '<p class="intro">Read the manuscript alongside its recorded ZFD layers. '
        'Select any word to inspect the match behind it.</p></div>',
        '<dl class="hero-stats">',
        f'<div><dt>Source lines</dt><dd>{len(lines)}</dd></div>',
        f'<div><dt>Tokens</dt><dd>{len(tokens)}</dd></div>',
        f'<div><dt>Partial matches</dt><dd>{counts["partial"]}</dd></div>',
        '</dl></div><div class="source-strip"><span class="source-dot" aria-hidden="true"></span>',
        f'<strong>{_esc(source_kind)}</strong><span>{_esc(source.get("path", "Source path not recorded"))}</span>',
        '<a href="#provenance">Source &amp; configuration ↓</a></div></header>',
        '<main class="reader-layout">', _image_panel(result),
        '<section class="reading-panel" id="reading" aria-labelledby="reading-heading">',
        '<div class="reading-heading"><div><p class="eyebrow">The reading</p>',
        '<h2 id="reading-heading">Four layers, line by line</h2></div>',
        '<button id="expand-evidence" type="button" disabled>Expand evidence</button></div>',
        '<p class="reading-note">Croatian renderings and English glosses are ZFD parser outputs. '
        'Match labels describe the recorded lookup method.</p>',
        '<div class="toolbar"><label class="search-label" for="token-search">Search tokens',
        '<input id="token-search" type="search" placeholder="EVA, Croatian, gloss or token ID…" disabled></label>',
        '<label class="match-label" for="match-filter">Match type<select id="match-filter" disabled>',
        '<option value="all">All match types</option>',
    ])
    for kind, label in MATCH_LABELS.items():
        if counts[kind] or kind != "not_recorded":
            parts.append(f'<option value="{kind}">{label} ({counts[kind]})</option>')
    parts.extend([
        '</select></label><button type="button" id="reset-filter" disabled>Reset</button></div>',
        f'<p class="filter-status" id="filter-status" role="status">{len(tokens)} tokens across {len(lines)} source lines</p>',
        '<p class="filter-hint">Matching words stay highlighted; surrounding line context remains visible.</p>',
        '<noscript><p>Search needs JavaScript. All source lines and token records are included below.</p></noscript>',
        '<div class="match-legend" aria-label="Recorded match types">',
    ])
    for kind in MATCH_LABELS:
        if counts[kind]:
            parts.append('<span>' + _badge(kind) + f'<span class="legend-count">{counts[kind]}</span></span>')
    parts.append('</div><div class="source-lines">')
    for index, line in enumerate(lines):
        _, _, label = _line_reference(result, line, index)
        line_id = f"line-{index + 1}"
        parts.extend([
            f'<article class="source-line" id="{line_id}">',
            '<div class="line-heading">',
            f'<h3><a href="#{line_id}">{_esc(label)}</a></h3>',
            f'<span>{len(line)} tokens</span></div><dl class="text-layers">',
        ])
        for key, layer_label in (("eva", "EVA"), ("zfd", "ZFD"),
                                 ("croatian", "Croatian"), ("english", "English gloss")):
            parts.append(f'<div class="layer-row layer-{key}"><dt>{layer_label}</dt><dd>')
            for token_index, token in enumerate(line):
                identifier = f"token-{index + 1}-{token_index + 1}"
                kind = _match_type(token)
                parts.append(f'<a class="word match-{kind}" href="#{identifier}" '
                             f'data-inspect="{identifier}" title="{_esc(MATCH_LABELS[kind])} · '
                             f'{_esc(token.get("id"))}">{_esc(token.get(key)) or "[empty]"}</a> ')
            parts.append('</dd></div>')
        parts.append('</dl><details class="line-evidence"><summary>'
                     f'Inspect <span class="line-token-count">{len(line)}</span> token records'
                     '</summary><div class="token-records">')
        for token_index, token in enumerate(line):
            parts.append(_token_record(token, f"token-{index + 1}-{token_index + 1}"))
        parts.append('</div></details></article>')
    parts.append('</div><p id="no-results" class="empty-state" hidden>No tokens match these filters.</p>')
    if not tokens:
        parts.append('<p class="empty-state">No tokens were produced for this input.</p>')
    parts.extend([
        '</section></main><section class="provenance" id="provenance" aria-labelledby="provenance-heading">',
        '<div><p class="eyebrow">Trace the result</p><h2 id="provenance-heading">Source &amp; configuration</h2>',
        '<p>Input selection, file hashes, lexicon settings and image references travel with the exports.</p>',
        '<p>Parser scores describe rule-based support; they are not calibrated probabilities.</p>',
        f'<p class="line-numbering">Line numbering: {_esc(source.get("line_numbering", "Taken from token IDs where available"))}.</p>',
        '</div><details class="metadata"><summary>View the complete run metadata</summary><pre>',
        _esc(_json(_metadata(result), pretty=True)), '</pre></details></section>',
        '<footer class="page-footer"><span>ZFD · Folio reader</span>',
        '<a href="#top">Back to top ↑</a></footer>',
        f'<script>{_JS}</script></body></html>',
    ])
    Path(output_path).write_text(''.join(parts), encoding="utf-8")


_CSS = """
:root{color-scheme:light;--paper:#f7f5ef;--card:#fffefa;--ink:#202b2a;--muted:#64716b;--line:#dcded4;--green:#27634d;--amber:#936010;--red:#944e42;--purple:#6d557b}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:1rem}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.6 ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}a{color:inherit}button,input,select{font:inherit}button,a,input,select,summary{touch-action:manipulation}button,summary{cursor:pointer}button:disabled,input:disabled,select:disabled{opacity:.6;cursor:default}a:focus-visible,button:focus-visible,summary:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid #7da792;outline-offset:4px}code,pre,.layer-eva dd,.layer-zfd dd{font-family:ui-monospace,SFMono-Regular,Consolas,"Liberation Mono",monospace}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px;line-height:1.7;background:#f1f2eb;border:1px solid var(--line);border-radius:8px;padding:16px;max-width:100%;margin:12px 0}h1,h2,h3,h4,p,dl,figure{margin:0}h1,h2{font-family:Georgia,"Times New Roman",serif;font-weight:400}h2{font-size:27px;line-height:1.2}h3{font-size:15px}h4{font-size:12px;margin-top:14px}button{background:var(--card);border:1px solid #c9cec1;border-radius:7px;padding:8px 12px;color:var(--ink);font-size:12px;font-weight:600}button:hover{background:#edf1e8}[hidden]{display:none!important}.skip-link{position:fixed;left:1rem;top:-5rem;z-index:10;padding:10px 15px;background:var(--ink);color:white}.skip-link:focus{top:1rem}.page-header,.reader-layout,.provenance,.page-footer{max-width:1560px;margin-inline:auto;padding-inline:42px}.header-top{min-height:78px;display:flex;justify-content:space-between;align-items:center;gap:20px;border-bottom:1px solid var(--line)}.wordmark{font-weight:800;letter-spacing:.06em;text-decoration:none;font-size:21px}.wordmark span{font-weight:500;font-size:10px;letter-spacing:.17em;margin-left:12px;vertical-align:middle}.exports{display:flex;gap:20px;font-size:12px;font-weight:600}.exports a{text-decoration:none}.exports a span{color:var(--green);margin-left:5px}.hero{display:flex;justify-content:space-between;align-items:flex-end;gap:30px;padding:38px 0 30px}.eyebrow{font-size:10px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);margin-bottom:10px}.hero h1{font-size:58px;line-height:1.08;letter-spacing:-.04em}.hero h1 span{color:var(--green)}.intro{font-size:14px;color:var(--muted);margin-top:16px;max-width:560px}.hero-stats{display:flex;gap:35px;flex-shrink:0;padding-bottom:4px}.hero-stats div{display:flex;flex-direction:column-reverse}.hero-stats dd{margin:0;font:38px/1.1 Georgia,serif;font-variant-numeric:tabular-nums}.hero-stats dt{font-size:10px;color:var(--muted);margin-top:8px;text-transform:uppercase;letter-spacing:.06em}.source-strip{border-block:1px solid var(--line);display:flex;align-items:center;gap:10px;padding:12px 0;font-size:11px;min-width:0}.source-strip>span:not(.source-dot){overflow:hidden;text-overflow:ellipsis;white-space:nowrap;min-width:0;color:var(--muted)}.source-strip strong{white-space:nowrap;font-weight:600}.source-strip a{margin-left:auto;white-space:nowrap;color:var(--green);text-decoration:none}.source-dot{width:6px;height:6px;flex-shrink:0;border-radius:50%;background:var(--green)}.reader-layout{display:grid;grid-template-columns:minmax(270px,.82fr) minmax(0,1.5fr);gap:34px;padding-top:34px;align-items:start}.manuscript-panel{position:sticky;top:22px;background:#ecece2;border:1px solid #d4d8ca;border-radius:13px;overflow:hidden;padding:22px}.panel-heading{margin-bottom:20px}.panel-heading h2{font-size:24px}.panel-heading .eyebrow{font-size:9px}.manuscript-figure img{display:block;width:100%;height:auto;max-height:60vh;object-fit:contain;background:#e5e4d8;border:1px solid #d7d5c6;border-radius:3px}.manuscript-figure figcaption{font-size:11px;line-height:1.7;color:var(--muted);padding-top:14px}.image-fallback{border:1px dashed #bdc5b7;padding:32px 20px;text-align:center;background:#f5f4eb;border-radius:6px}.image-mark{font-size:38px;font-weight:300;color:#7d8a78}.image-fallback h3{margin:12px 0 6px;font-size:15px}.image-fallback p{font-size:12px;color:var(--muted);max-width:290px;margin:auto}.image-note,.image-identifier{font-size:11px;overflow-wrap:anywhere;margin-top:12px;color:var(--muted)}.image-links{display:flex;gap:16px;flex-wrap:wrap;margin-top:16px;font-size:12px;font-weight:600}.image-links a{color:var(--green);text-underline-offset:4px}.offline-note{font-size:10px;color:var(--muted);margin-top:16px}.reading-heading{display:flex;align-items:center;justify-content:space-between;gap:14px}.reading-heading .eyebrow{margin-bottom:8px}.reading-note{font-size:12px;line-height:1.7;color:var(--muted);margin-top:14px;max-width:660px}.toolbar{display:flex;align-items:flex-end;gap:9px;margin-top:22px}.toolbar label{display:flex;flex-direction:column;gap:5px;font-size:10px;text-transform:uppercase;letter-spacing:.07em;font-weight:700;color:var(--muted)}.search-label{flex:1;min-width:80px}.match-label{width:175px;flex-shrink:0}.toolbar input,.toolbar select{width:100%;border:1px solid #cdd2c5;background:var(--card);border-radius:6px;padding:10px 11px;height:40px;font-size:12px;letter-spacing:normal;text-transform:none;color:var(--ink);font-weight:400}.toolbar button{height:40px}.filter-status{font-size:11px;font-weight:600;color:var(--green);margin-top:13px}.filter-hint{font-size:10px;color:var(--muted);margin-top:2px}.match-legend{display:flex;gap:8px 14px;flex-wrap:wrap;padding:17px 0 20px;border-bottom:1px solid var(--line);margin-bottom:20px}.match-legend>span{display:inline-flex;gap:6px;align-items:center}.legend-count{font-size:10px;color:var(--muted);font-variant-numeric:tabular-nums}.badge{display:inline-block;font-size:9px;line-height:1.7;padding:2px 6px;border-radius:4px;white-space:nowrap;font-weight:600;letter-spacing:.02em;background:#e8ece4;color:var(--green)}.badge.match-whole_word,.badge.match-exact_stem{background:#e3eee6;color:#24543e}.badge.match-suffix{background:#e5eef0;color:#355e68}.badge.match-partial{background:#f6ebd3;color:#82540a}.badge.match-compound{background:#ece5f1;color:#694e7b}.badge.match-unresolved,.badge.match-not_recorded{background:#f3e6e0;color:#8e493a}.source-line{background:var(--card);border:1px solid var(--line);border-radius:9px;margin-bottom:16px;overflow:hidden;scroll-margin-top:18px}.line-heading{display:flex;justify-content:space-between;gap:12px;align-items:center;padding:13px 18px;border-bottom:1px solid #e6e8de;background:#f2f3ec}.line-heading h3{font-size:12px;font-weight:650;overflow-wrap:anywhere}.line-heading a{text-decoration:none}.line-heading>span{font-size:10px;white-space:nowrap;color:var(--muted)}.text-layers{padding:13px 18px 7px}.layer-row{display:grid;grid-template-columns:72px minmax(0,1fr);gap:12px;padding:8px 0}.layer-row dt{font-size:9px;letter-spacing:.05em;text-transform:uppercase;font-weight:700;color:#6d786f;padding-top:5px}.layer-row dd{margin:0;overflow-wrap:anywhere;font-size:13px;line-height:1.95}.layer-croatian{border-top:1px dashed #e0e3d7;margin-top:3px;padding-top:11px}.layer-english dd{font-family:Georgia,"Times New Roman",serif;font-size:15px;line-height:1.85}.word{text-decoration:none;border-bottom:1px solid #a8bca9;border-radius:2px;padding:1px 1px;box-decoration-break:clone;-webkit-box-decoration-break:clone;transition:opacity .12s,background .12s}.word:hover{background:#e9eee1}.word.match-partial{border-bottom:2px dotted #c89a4a}.word.match-compound{border-bottom:2px dashed #a38ab4}.word.match-unresolved,.word.match-not_recorded{border-bottom:2px dotted #b87566}.word.is-filtered{opacity:.28;border-color:transparent}.line-evidence{border-top:1px solid #eceee5}.line-evidence>summary{padding:11px 18px;font-size:10px;font-weight:600;color:var(--green)}.line-evidence[open]>summary{background:#f3f5ee}.token-records{padding:0 12px 12px}.token-record{margin-top:8px;border:1px solid #dee3d8;border-left:3px solid #83a18a;border-radius:5px;scroll-margin-top:18px;background:#fffefa}.token-record.match-partial{border-left-color:#c99b4d}.token-record.match-compound{border-left-color:#a38ab4}.token-record.match-unresolved,.token-record.match-not_recorded{border-left-color:#b87566}.token-record>summary{padding:10px 12px}.token-summary{display:inline-flex;align-items:center;gap:9px;flex-wrap:wrap;width:calc(100% - 18px);vertical-align:middle}.token-eva{font-size:13px;font-weight:600;overflow-wrap:anywhere;max-width:100%}.token-id{font-size:9px;color:var(--muted);overflow-wrap:anywhere}.score{margin-left:auto;font-size:9px;white-space:nowrap;color:var(--muted)}.token-body{border-top:1px solid #e8eadf;padding:12px 14px;font-size:12px}.residue-note{padding:9px 11px;background:#faf0db;border-radius:5px;font-size:11px;margin-bottom:12px;overflow-wrap:anywhere}.evidence-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px 18px}.evidence-grid dt{font-size:9px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}.evidence-grid dd{margin:3px 0 0;overflow-wrap:anywhere;font-size:12px}.token-body ul{padding-left:18px;font-size:11px;overflow-wrap:anywhere}.raw-token{margin-top:12px}.raw-token>summary{font-size:10px;color:var(--green)}.raw-token pre{margin-bottom:0}.empty-state{padding:30px;border:1px dashed var(--line);text-align:center;color:var(--muted);border-radius:8px}.provenance{margin-top:40px;padding-top:28px;padding-bottom:30px;border-top:1px solid var(--line);display:grid;grid-template-columns:1fr 1.4fr;gap:40px}.provenance h2{font-size:25px}.provenance p:not(.eyebrow){font-size:12px;color:var(--muted);margin-top:12px}.provenance .line-numbering{font-size:11px}.metadata{min-width:0;border:1px solid var(--line);border-radius:8px;background:var(--card);align-self:start}.metadata summary{font-size:12px;font-weight:600;padding:16px}.metadata pre{margin:0 12px 12px}.page-footer{display:flex;justify-content:space-between;border-top:1px solid var(--line);padding-top:20px;padding-bottom:28px;font-size:10px;color:var(--muted)}.page-footer a{text-decoration:none}
.image-selected{font-size:12px;font-weight:600;margin:-8px 0 15px;overflow-wrap:anywhere}.scan-references{border-top:1px solid #d3d8ca;margin-top:18px;padding-top:14px}.scan-references h3{font-size:10px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}.scan-references ul{padding-left:17px;margin:8px 0 0;font-size:11px}.scan-references li{margin-top:8px;overflow-wrap:anywhere}.scan-references a{color:var(--green);text-underline-offset:3px}.scan-references span{display:block;color:var(--muted);font-size:10px}
@media(min-width:1600px){.reader-layout{grid-template-columns:minmax(300px,1fr) minmax(0,1.55fr)}}
@media(max-width:1100px){.page-header,.reader-layout,.provenance,.page-footer{padding-inline:26px}.reader-layout{gap:22px;grid-template-columns:minmax(230px,.75fr) minmax(0,1.5fr)}.hero-stats{gap:22px}.hero h1{font-size:51px}.manuscript-panel{padding:17px}.reading-heading h2{font-size:24px}.reading-heading{align-items:flex-start}.match-label{width:150px}.toolbar{flex-wrap:wrap}.search-label{flex-basis:100%}.match-label{flex:1}.layer-row{grid-template-columns:62px minmax(0,1fr);gap:9px}}
@media(max-width:780px){.page-header,.reader-layout,.provenance,.page-footer{padding-inline:20px}.header-top{min-height:66px}.exports{gap:12px;font-size:10px}.wordmark{font-size:18px}.wordmark span{font-size:8px;margin-left:7px}.hero{padding:27px 0 23px;display:block}.hero h1{font-size:47px}.hero-stats{margin-top:24px;gap:35px}.hero-stats dd{font-size:30px}.hero-stats dt{font-size:9px}.source-strip{flex-wrap:wrap;gap:6px 9px}.source-strip>span:not(.source-dot){flex:1}.source-strip a{flex-basis:100%;margin:2px 0 0 15px}.reader-layout{display:block;padding-top:22px}.manuscript-panel{position:static;margin-bottom:30px}.manuscript-figure img{max-height:56vh}.image-fallback{padding:23px 18px}.reading-heading{align-items:center}.reading-heading h2{font-size:27px}.toolbar{flex-wrap:nowrap}.search-label{flex-basis:auto}.match-label{width:148px;flex:0 0 148px}.provenance{display:block;margin-top:28px;padding-top:24px}.metadata{margin-top:22px}.text-layers{padding-inline:14px}.line-heading{padding-inline:14px}}
@media(max-width:480px){.page-header,.reader-layout,.provenance,.page-footer{padding-inline:15px}.wordmark span{display:none}.hero h1{font-size:43px}.eyebrow{font-size:9px}.intro{font-size:13px}.toolbar{flex-wrap:wrap}.search-label{flex-basis:100%}.match-label{flex:1}.reading-heading h2{font-size:24px}.reading-heading button{font-size:10px;padding:7px 9px}.layer-row{display:block;padding:7px 0}.layer-row dt{padding:0;margin-bottom:3px;font-size:8px}.layer-row dd{font-size:12px}.layer-english dd{font-size:15px}.evidence-grid{grid-template-columns:1fr}.score{margin-left:0}.source-strip strong{font-size:10px}.token-records{padding-inline:8px}.hero-stats{gap:29px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.word{transition:none}}
@media print{body{background:white;font-size:11px}.page-header,.reader-layout,.provenance,.page-footer{padding-inline:0}.reader-layout{display:block}.manuscript-panel{position:static;break-inside:avoid;margin-bottom:20px}.manuscript-figure img{max-height:360px}.toolbar,.filter-hint,.exports,.reading-heading button,.skip-link{display:none}.source-line{break-inside:avoid}.provenance{display:block}.hero{padding-block:20px}.hero h1{font-size:36px}}
"""

_JS = """
(function () {
  'use strict';
  var search = document.getElementById('token-search');
  var select = document.getElementById('match-filter');
  var reset = document.getElementById('reset-filter');
  var expand = document.getElementById('expand-evidence');
  var records = Array.from(document.querySelectorAll('.token-record'));
  var lines = Array.from(document.querySelectorAll('.source-line'));
  var words = Array.from(document.querySelectorAll('[data-inspect]'));
  [search, select, reset, expand].forEach(function (control) { control.disabled = false; });
  function filter() {
    var query = search.value.trim().toLocaleLowerCase();
    var wanted = select.value;
    var matches = new Set();
    records.forEach(function (record) {
      var visible = (wanted === 'all' || record.dataset.match === wanted) &&
        (!query || record.dataset.search.indexOf(query) !== -1);
      record.hidden = !visible;
      if (visible) matches.add(record.id);
    });
    words.forEach(function (word) {
      word.classList.toggle('is-filtered', !matches.has(word.dataset.inspect));
    });
    var visibleLines = 0;
    lines.forEach(function (line) {
      var count = Array.from(line.querySelectorAll('.token-record')).filter(function (record) {
        return !record.hidden;
      }).length;
      line.hidden = count === 0;
      line.querySelector('.line-token-count').textContent = count;
      if (count) visibleLines += 1;
    });
    document.getElementById('filter-status').textContent = matches.size + ' of ' + records.length +
      ' tokens · ' + visibleLines + ' source lines';
    document.getElementById('no-results').hidden = matches.size !== 0 || records.length === 0;
  }
  search.addEventListener('input', filter);
  select.addEventListener('change', filter);
  reset.addEventListener('click', function () {
    search.value = ''; select.value = 'all'; filter(); search.focus();
  });
  expand.addEventListener('click', function () {
    var open = expand.getAttribute('aria-expanded') !== 'true';
    document.querySelectorAll('.line-evidence,.token-record').forEach(function (item) {
      if (!item.hidden) item.open = open;
    });
    expand.setAttribute('aria-expanded', String(open));
    expand.textContent = open ? 'Collapse evidence' : 'Expand evidence';
  });
  expand.setAttribute('aria-expanded', 'false');
  function reveal(identifier) {
    var record = document.getElementById(identifier);
    if (!record || !record.classList.contains('token-record')) return;
    if (record.hidden) { search.value = ''; select.value = 'all'; filter(); }
    var group = record.closest('.line-evidence');
    if (group) group.open = true;
    record.open = true;
  }
  words.forEach(function (word) {
    word.addEventListener('click', function () { reveal(word.dataset.inspect); });
  });
  function revealHash() {
    try { reveal(decodeURIComponent(window.location.hash.slice(1))); } catch (error) { /* invalid hash */ }
  }
  window.addEventListener('hashchange', revealHash);
  revealHash();
  var manuscript = document.getElementById('manuscript-image');
  if (manuscript) {
    function unavailable() {
      manuscript.hidden = true;
      document.getElementById('image-fallback').hidden = false;
    }
    manuscript.addEventListener('error', unavailable);
    if (manuscript.complete && manuscript.naturalWidth === 0) unavailable();
  }
}());
"""
