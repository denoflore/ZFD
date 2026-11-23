"""Reader/export regressions for escaping, source identity and match evidence."""

import csv
import json
import sys
from copy import deepcopy
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from output import generate_csv, generate_html, generate_json, generate_markdown


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.elements = []
        self.text = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

    def handle_data(self, data):
        self.text.append(data)

    def attributes(self, tag):
        return [attrs for kind, attrs in self.elements if kind == tag]



def sample_result():
    return {
        "folio": "f88r",
        "lines": [[{
            "id": "f88r.7.1", "eva": "xoly", "zfd": "xoly", "operator": None,
            "stem": "xoly", "suffix": None, "expansion": "[STEM:xoly=oil]",
            "croatian": "xuljey", "english": "oil", "confidence": 0.3,
            "notes": ["Partial entry", "č, š\nsecond line"], "rewrites": [],
            "match_type": "partial", "matched_form": "ol", "matched_croatian": "ulje",
            "matched_category": "ingredient", "matched_status": "CONFIRMED",
            "matched_source": "locked_lexicon", "stem_surface": "xoly",
            "unmatched_prefix": "x", "unmatched_suffix": "y", "compound_parts": [],
        }, {
            "id": "f88r.7.2", "eva": "abcdef", "zfd": "abcdef", "operator": None,
            "stem": "abcdef", "suffix": None, "expansion": "[STEM:abcdef=part + part]",
            "croatian": "[abcdef]", "english": "part + part", "confidence": 0.25,
            "notes": [], "rewrites": [], "match_type": "compound", "matched_form": "",
            "matched_croatian": "", "matched_category": "compound",
            "matched_status": "CANDIDATE", "matched_source": "unified_lexicon",
            "stem_surface": "abcdef", "unmatched_prefix": "", "unmatched_suffix": "",
            "compound_parts": [{"form": "abc", "gloss": "part"}, {"form": "def", "gloss": "part"}],
        }]],
        "diagnostics": {"total_tokens": 2, "average_confidence": 0.275},
        "source": {
            "kind": "lsi_preferred", "path": "data/LSI.txt", "sha256": "source-hash",
            "text_sha256": "text-hash", "selection": {"folio": "f88r", "transcriber": "H"},
            "line_numbering": "selected LSI record sequence", "line_ids": {"7": "f88r.P.3;H"},
        },
        "configuration": {
            "lexicon_file": "data/lexicon_v2.csv", "lexicon_sha256": "lexicon-hash",
            "lexicon_rows": 200, "lexicon_unique_forms": 240, "duplicate_variants": 3,
            "compound_enabled": True, "code_sha256": {"pipeline.py": "code-hash"},
        },
        "image": {"available": False, "folio": "f88r", "note": "No verified panel mapping."},
    }


def render(tmp_path, result):
    target = tmp_path / "reader.html"
    generate_html(result, target)
    return target.read_text(encoding="utf-8")


def test_html_escapes_all_record_values_and_rejects_executable_urls(tmp_path):
    result = sample_result()
    payload = '\"><img src=x onerror="alert(1)"><script>unsafe()</script>& č'
    result["folio"] = payload
    result["lines"][0][0]["eva"] = payload
    result["lines"][0][0]["matched_source"] = payload
    result["source"]["path"] = "</pre><script>unsafe()</script>"
    result["source"]["line_ids"]["7"] = payload
    result["configuration"]["lexicon_file"] = payload
    result["image"] = {
        "available": True, "image_url": "javascript:unsafe()",
        "full_url": "data:text/html,<script>unsafe()</script>",
        "source_url": "javascript:unsafe()", "note": payload,
    }
    text = render(tmp_path, result)
    document = Document(text)
    assert len(document.attributes("script")) == 1  # only the static local reader script
    assert not document.attributes("img")
    assert not any(key.startswith("on") for _, attrs in document.elements for key in attrs)
    assert all(not attrs.get("href", "").startswith(("javascript:", "data:"))
               for attrs in document.attributes("a"))
    assert "&lt;img" in text and "&lt;/pre&gt;&lt;script&gt;" in text
    assert payload in "".join(document.text)
    assert not any("download" in attrs for attrs in document.attributes("a"))


def test_partial_and_compound_evidence_preserves_original_source_identity(tmp_path):
    text = render(tmp_path, sample_result())
    document = Document(text)
    details = document.attributes("details")
    assert {attrs.get("data-match") for attrs in details} >= {"partial", "compound"}
    visible = "".join(document.text)
    assert "f88r.P.3;H" in visible
    assert "Source line 1" not in visible
    assert "Unmatched residue:" in visible
    assert "prefix x · suffix y" in visible
    assert "locked_lexicon" in visible
    assert "ulje" in visible and "[abcdef]" in visible
    assert "Compound parts" in visible
    assert "Parser score 0.300" in visible
    assert "30%" not in visible
    assert "Lexicon status" in visible
    assert '"code_sha256"' in visible
    assert all("src" not in attrs for attrs in document.attributes("script"))
    assert not document.attributes("link")  # no external stylesheet dependency
    downloads = {attrs["href"] for attrs in document.attributes("a") if "download" in attrs}
    assert downloads == {"f88r_decode.json", "f88r_table.csv", "f88r_report.md"}


def test_missing_image_and_legacy_tokens_remain_readable(tmp_path):
    result = sample_result()
    result["source"].pop("line_ids")
    for token in result["lines"][0]:
        token.pop("match_type")
    text = render(tmp_path, result)
    document = Document(text)
    visible = "".join(document.text)
    assert "No verified image mapping" in visible
    assert "Source line 7" in visible
    assert "xoly" in visible and "oil" in visible
    assert not document.attributes("img")
    assert "Not recorded" in visible
    assert any(attrs.get("data-match") == "not_recorded" for attrs in document.attributes("details"))


def test_verified_image_has_offline_fallback_without_invented_word_coordinates(tmp_path):
    result = sample_result()
    result["folio"] = "f67r1"
    result["image"] = {
        "available": True, "folio": "f67r1", "identifier": "123456",
        "image_url": "https://images.example.org/123456/full/800,/0/default.jpg",
        "full_url": "https://images.example.org/123456/full/max/0/default.jpg",
        "source_url": "https://collections.example.org/catalog/123456?x=1&y=2",
    }
    text = render(tmp_path, result)
    document = Document(text)
    assert len(document.attributes("img")) == 1
    assert document.attributes("img")[0]["src"] == result["image"]["image_url"]
    assert "Image unavailable" in "".join(document.text)
    assert "image-fallback" in text
    assert "individual words are not mapped to image coordinates" in text
    assert not document.attributes("map")
    assert "f67r1_decode.json" in text


def test_csv_and_json_round_trip_all_provenance(tmp_path):
    result = sample_result()
    result["lines"][0][0]["future_field"] = {"accent": "đ", "list": [1, "two"]}
    result["future_run_field"] = {"version": 3}
    original = deepcopy(result)
    csv_path, json_path = tmp_path / "tokens.csv", tmp_path / "result.json"
    generate_csv(result, csv_path)
    generate_json(result, json_path)
    assert json.loads(json_path.read_text(encoding="utf-8")) == original
    with csv_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 2
    assert [json.loads(row["token_json"]) for row in rows] == result["lines"][0]
    metadata = {key: value for key, value in result.items() if key != "lines"}
    assert json.loads(rows[0]["run_metadata_json"]) == metadata
    assert rows[1]["run_metadata_json"] == ""
    for row in rows:
        assert row["record_type"] == "token"
        assert row["source_line"] == "7"
        assert row["source_line_id"] == "f88r.P.3;H"
    assert rows[0]["unmatched_prefix"] == "x"
    assert rows[0]["unmatched_suffix"] == "y"
    assert rows[0]["matched_croatian"] == "ulje"
    assert json.loads(rows[1]["compound_parts_json"]) == result["lines"][0][1]["compound_parts"]
    assert result == original  # no renderer mutates the pipeline result


def test_markdown_keeps_metadata_residues_and_utf8(tmp_path):
    result = sample_result()
    result["lines"][0][0]["notes"].append("A code fence: ``` and <script>text</script>")
    path = tmp_path / "report.md"
    generate_markdown(result, path)
    text = path.read_text(encoding="utf-8")
    assert "f88r.P.3;H" in text
    assert "| Prefix residue | Suffix residue |" in text
    assert '"matched_source": "locked_lexicon"' in text
    assert '"compound_parts"' in text
    assert '"configuration"' in text and '"image"' in text and '"source"' in text
    assert '"sha256": "source-hash"' in text
    assert "č, š" in text
    assert "````json" in text  # embedded backticks cannot close the evidence fence
    assert "Parser score" in text and "Average confidence" not in text


def test_empty_export_still_retains_run_metadata(tmp_path):
    result = sample_result()
    result["lines"] = []
    path = tmp_path / "empty.csv"
    generate_csv(result, path)
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 1 and rows[0]["record_type"] == "metadata"
    assert rows[0]["token_id"] == ""
    assert json.loads(rows[0]["run_metadata_json"])["source"] == result["source"]
    assert "No tokens were produced for this input" in render(tmp_path, result)


def test_multiple_image_references_keep_exact_labels_and_scopes(tmp_path):
    result = sample_result()
    result["folio"] = "f1234v12"
    result["image"].update({
        "label": "Scan one: f88r + adjoining panel",
        "scope": "Full scan, two panels",
        "references": [
            {"label": "Scan one: f88r + adjoining panel", "identifier": "111",
             "full_url": "https://images.example.org/111/full/max/0/default.jpg",
             "scope": "Full scan, two panels", "in_root_map": True},
            {"label": "Second scan <annotated>", "identifier": "222",
             "image_url": "https://images.example.org/222/full/800,/0/default.jpg",
             "scope": "Alternative view", "in_root_map": False},
        ],
    })
    document = Document(render(tmp_path, result))
    links = {attrs["href"] for attrs in document.attributes("a")}
    for reference in result["image"]["references"]:
        assert (reference.get("full_url") or reference.get("image_url")) in links
        assert reference["label"] in "".join(document.text)
        assert reference["scope"] in "".join(document.text)
    assert "f1234v12_decode.json" in links
    path = tmp_path / "references.md"
    generate_markdown(result, path)
    markdown = path.read_text(encoding="utf-8")
    assert "## Image references" in markdown
    assert "[Second scan &lt;annotated&gt;](<https://images.example.org/222/full/800,/0/default.jpg>)" in markdown
    assert "Scope: Alternative view" in markdown
