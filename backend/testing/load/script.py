#!/usr/bin/env python3
"""
compute_percentile_averages.py

Simple tool to compute average values for percentiles (P99, P90, P80, P70, P60, P50)
from a CSV file (e.g. Locust results CSV).

Usage:
  python compute_percentile_averages.py --input results_stats.csv
  python compute_percentile_averages.py -i results_stats_history.csv -o out.csv

Output:
  Prints averages to stdout and optionally writes CSV to --output (default: percentile_averages.csv).
"""
from __future__ import annotations
import argparse
import csv
import re
from statistics import mean
from typing import Dict, List, Optional

PERCENTILES = [99, 90, 80, 70, 60, 50]

def extract_digits(s: str) -> str:
    return ''.join(re.findall(r'\d+', s))

def find_percentile_columns(headers: List[str]) -> Dict[int, List[str]]:
    """Return mapping percentile -> list of matching header names."""
    matches: Dict[int, List[str]] = {p: [] for p in PERCENTILES}
    for h in headers:
        cleaned = (h or "").strip().lower()
        digits = extract_digits(cleaned)
        for p in PERCENTILES:
            if digits == str(p):
                matches[p].append(h)
            else:
                # also accept forms like 'p99', '99%', '99th', 'percentile_99'
                if re.search(rf'\b(p{p}|{p}th|{p}%|percentile{p}|percent{p}|pct{p})\b', cleaned):
                    matches[p].append(h)
    return matches

def parse_number(s: str) -> Optional[float]:
    if s is None:
        return None
    s = s.strip()
    if s == '' or s.lower() in ('na', 'n/a', '-'):
        return None
    # try remove trailing '%' if present
    if s.endswith('%'):
        s = s[:-1]
    try:
        return float(s)
    except Exception:
        return None

def compute_averages(path: str) -> Dict[int, Optional[float]]:
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        pct_cols = find_percentile_columns(headers)
        # prepare container
        accum: Dict[int, List[float]] = {p: [] for p in PERCENTILES}
        for row in reader:
            for p, cols in pct_cols.items():
                for c in cols:
                    val = parse_number(row.get(c, ""))
                    if val is not None:
                        accum[p].append(val)
        # compute means
        results: Dict[int, Optional[float]] = {}
        for p in PERCENTILES:
            vals = accum[p]
            results[p] = mean(vals) if vals else None
        return results

def write_output(path: str, results: Dict[int, Optional[float]]):
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(["percentile", "average"])
        for p in sorted(results.keys(), reverse=True):
            val = results[p]
            w.writerow([f"P{p}", "" if val is None else f"{val:.3f}"])

def main():
    ap = argparse.ArgumentParser(description="Compute averages for P99..P50 from a CSV file.")
    ap.add_argument("--input", "-i", required=True, help="Input CSV file (e.g. results_stats.csv)")
    ap.add_argument("--output", "-o", default="percentile_averages.csv", help="Output CSV file")
    args = ap.parse_args()

    results = compute_averages(args.input)
    print(f"Averages computed from: {args.input}")
    for p in sorted(results.keys(), reverse=True):
        v = results[p]
        if v is None:
            print(f"P{p}: (no data found)")
        else:
            print(f"P{p}: {v:.3f}")
    write_output(args.output, results)
    print(f"Wrote CSV -> {args.output}")

if __name__ == "__main__":
    main()