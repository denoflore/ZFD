
#!/usr/bin/env python3
import argparse, hashlib, os, re, sys
from collections import Counter, defaultdict
import pandas as pd

EXPECTED_SHA256 = "3f3f2af18cde10efe75c582f49b07b651c3397022fcbfa5854fecc424c121afa"

DEFAULT_OPERATORS = ['qo','ch','sh','ct','qk','ck','qch','qsh','cth']  # edit if needed

def sha256_hex(path: str) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

def load_and_clean(path: str) -> list[str]:
    text = open(path, "r", encoding="utf-8", errors="ignore").read()
    lines = text.splitlines()
    # Keep only paragraph lines by unit codes
    keep = []
    for ln in lines:
        if re.search(r'\b(\+P0|\*P0|@P0|=P0|\+P1)\b', ln):
            keep.append(ln)
    stream = "\n".join(keep)
    # Remove editorial markers
    stream = re.sub(r'[{}*!?\<\>\$]', ' ', stream)
    # Replace break symbols with spaces
    stream = re.sub(r'[.,\-_=]', ' ', stream)
    # Lowercase
    stream = stream.lower()
    # Restrict to a–z and spaces
    stream = re.sub(r'[^a-z\s]', ' ', stream)
    # Normalize whitespace
    stream = re.sub(r'\s+', ' ', stream).strip()
    tokens = [t for t in stream.split(' ') if t]
    return tokens

def glyph_frequencies(tokens: list[str]) -> pd.DataFrame:
    all_chars = "".join(tokens)
    total = len(all_chars)
    c = Counter(all_chars)
    rows = []
    for g, cnt in sorted(c.items(), key=lambda x: (-x[1], x[0])):
        pct = cnt / total * 100 if total else 0
        rows.append({"glyph": g, "count": cnt, "percent_of_corpus": round(pct, 3)})
    return pd.DataFrame(rows)

def prefix_frequencies(tokens: list[str], n_max=3) -> pd.DataFrame:
    rows = []
    for n in range(1, n_max+1):
        c = Counter([t[:n] for t in tokens if len(t) >= n])
        total = sum(c.values())
        for pref, cnt in sorted(c.items(), key=lambda x: (-x[1], x[0])):
            rows.append({
                "n": n,
                "prefix": pref,
                "count": cnt,
                "percent": round(cnt/total*100, 3) if total else 0
            })
    return pd.DataFrame(rows)

def operator_distribution(tokens: list[str], operators=DEFAULT_OPERATORS) -> pd.DataFrame:
    # Longest-match operator at the start
    ops_sorted = sorted(operators, key=len, reverse=True)
    c = Counter()
    total_with_any_op = 0
    for t in tokens:
        found = None
        for op in ops_sorted:
            if t.startswith(op):
                found = op
                break
        if found:
            c[found] += 1
            total_with_any_op += 1
    rows = []
    for op, cnt in sorted(c.items(), key=lambda x: (-x[1], x[0])):
        rows.append({
            "operator": op,
            "count": cnt,
            "percent_of_tokens": round(cnt/len(tokens)*100, 3) if tokens else 0
        })
    rows.append({
        "operator": "_any_operator_token_",
        "count": total_with_any_op,
        "percent_of_tokens": round(total_with_any_op/len(tokens)*100, 3) if tokens else 0
    })
    return pd.DataFrame(rows)

def suffix_productivity(tokens: list[str], min_len=2, max_suffix=3) -> pd.DataFrame:
    records = []
    for n in range(1, max_suffix+1):
        bucket = defaultdict(list)  # suffix -> stems
        for t in tokens:
            if len(t) >= min_len and len(t) > n:
                sfx = t[-n:]
                stem = t[:-n]
                bucket[sfx].append(stem)
        for sfx, stems in bucket.items():
            total = len(stems)
            distinct_stems = len(set(stems))
            productivity = distinct_stems / total if total else 0
            records.append({
                "suffix_len": n,
                "suffix": sfx,
                "total_occurrences": total,
                "distinct_stems": distinct_stems,
                "productivity": round(productivity, 4)
            })
    df = pd.DataFrame(records).sort_values(
        ["suffix_len","total_occurrences","distinct_stems"],
        ascending=[True, False, False]
    )
    return df

def write_csvs(tokens: list[str], out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    df_g = glyph_frequencies(tokens)
    df_p = prefix_frequencies(tokens, 3)
    df_o = operator_distribution(tokens, DEFAULT_OPERATORS)
    df_s = suffix_productivity(tokens, min_len=2, max_suffix=3)
    df_g.to_csv(os.path.join(out_dir, "glyph_freq.csv"), index=False)
    df_p.to_csv(os.path.join(out_dir, "prefix_freq.csv"), index=False)
    df_o.to_csv(os.path.join(out_dir, "operator_list.csv"), index=False)
    df_s.to_csv(os.path.join(out_dir, "suffix_list.csv"), index=False)
    return {
        "glyph_freq.csv": len(df_g),
        "prefix_freq.csv": len(df_p),
        "operator_list.csv": len(df_o),
        "suffix_list.csv": len(df_s),
    }

def main():
    ap = argparse.ArgumentParser(description="Voynich replication exports")
    ap.add_argument("--corpus", required=True, help="Path to Takahashi EVA interlinear file, e.g., SET_PATH_HERE/LSI_ivtff_0d.txt")
    ap.add_argument("--out-dir", required=True, help="Directory where CSVs will be written")
    args = ap.parse_args()

    if not os.path.exists(args.corpus):
        print(f"ERROR: Corpus not found at {args.corpus}", file=sys.stderr)
        sys.exit(2)

    actual = sha256_hex(args.corpus)
    if actual.lower() != EXPECTED_SHA256.lower():
        print("ERROR: SHA-256 mismatch.", file=sys.stderr)
        print(f"Expected: {EXPECTED_SHA256}", file=sys.stderr)
        print(f"Got     : {actual}", file=sys.stderr)
        print("Refuse to proceed to prevent silently diverging results.", file=sys.stderr)
        sys.exit(3)

    tokens = load_and_clean(args.corpus)
    if len(tokens) != 31888:
        # This is a guardrail to catch pipeline drift. Adjust only if you intentionally changed filtering.
        print(f\"WARNING: Token count = {len(tokens)} but expected 31888. Check your file and cleaning rules.\", file=sys.stderr)

    counts = write_csvs(tokens, args.out_dir)
    print(\"Exports written:\")
    for name, rows in counts.items():
        print(f\" - {name}  ({rows} rows)\")
    print(\"Done.\")

if __name__ == \"__main__\":
    main()
