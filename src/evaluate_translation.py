#!/usr/bin/env python3
"""Evaluate Hausa climate translation outputs.

Supports terminology exact-match accuracy, lexical-constraint success, BLEU and
chrF when independent Hausa sentence references are available, and domain- and
strategy-level breakdowns.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path


def norm(text: str) -> str:
    text = re.sub(r"[^\w\sƙƘɗƊɓƁƴƳʼ'-]", " ", (text or "").casefold())
    return re.sub(r"\s+", " ", text).strip()


def contains_phrase(text: str, phrase: str) -> bool:
    return bool(phrase) and norm(phrase) in norm(text)


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def safe_div(a, b):
    return a / b if b else None


def term_metrics(rows, output_col, expected_col):
    usable = [r for r in rows if r.get(expected_col, "").strip()]
    hits = [
        contains_phrase(r.get(output_col, ""), r.get(expected_col, ""))
        for r in usable
    ]
    return {
        "n": len(usable),
        "exact_term_accuracy": safe_div(sum(hits), len(hits)),
    }


def grouped_term_metrics(rows, key, output_col, expected_col):
    groups = defaultdict(list)
    for row in rows:
        groups[row.get(key, "UNKNOWN")].append(row)
    return {
        group: term_metrics(group_rows, output_col, expected_col)
        for group, group_rows in sorted(groups.items())
    }


def sentence_metrics(rows, output_col, reference_col):
    paired = [
        (r.get(output_col, "").strip(), r.get(reference_col, "").strip())
        for r in rows
        if r.get(output_col, "").strip() and r.get(reference_col, "").strip()
    ]
    if not paired:
        return {"n": 0, "BLEU": None, "chrF": None}

    try:
        import sacrebleu
    except ImportError as exc:
        raise SystemExit(
            "sacrebleu is required for sentence-level BLEU/chrF. "
            "Install requirements-experiment.txt"
        ) from exc

    hypotheses = [h for h, _ in paired]
    references = [[r for _, r in paired]]
    return {
        "n": len(paired),
        "BLEU": sacrebleu.corpus_bleu(hypotheses, references).score,
        "chrF": sacrebleu.corpus_chrf(hypotheses, references).score,
    }


def constraint_success(rows, output_col):
    checked = 0
    success = 0
    for row in rows:
        terms = [
            t.strip()
            for t in row.get("forced_hausa_terms", "").split(";")
            if t.strip()
        ]
        if not terms:
            continue
        checked += 1
        if all(contains_phrase(row.get(output_col, ""), term) for term in terms):
            success += 1
    return {
        "n": checked,
        "constraint_success_rate": safe_div(success, checked),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--output-json", type=Path, required=True)
    ap.add_argument("--output-column", default="translation")
    ap.add_argument("--expected-term-column", default="Hausa candidate")
    ap.add_argument("--reference-column", default="hausa_reference")
    args = ap.parse_args()

    rows = read_csv(args.input)
    report = {
        "terminology": term_metrics(
            rows, args.output_column, args.expected_term_column
        ),
        "constraint_success": constraint_success(rows, args.output_column),
        "by_domain": grouped_term_metrics(
            rows, "domain", args.output_column, args.expected_term_column
        ),
        "by_translation_strategy": grouped_term_metrics(
            rows,
            "translation strategy",
            args.output_column,
            args.expected_term_column,
        ),
        "sentence_metrics": sentence_metrics(
            rows, args.output_column, args.reference_column
        ),
        "interpretation_warning": (
            "HESTC Hausa candidates are provisional. Silver terminology accuracy "
            "must not be reported as human-reference MT quality. Publication-grade "
            "sentence metrics require independently reviewed Hausa references."
        ),
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
