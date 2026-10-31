#!/usr/bin/env python3
"""Corpus-wide quality assurance for HESTC-10K."""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

REQUIRED = [
    "ID",
    "English term",
    "Hausa term",
    "terminology type",
    "domain",
    "subdomain",
    "concise definition",
    "source institution",
    "source identifier/link",
    "Hausa candidate",
    "translation strategy",
    "preferred Hausa",
    "validation status",
    "reviewer notes",
]


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def canonical(value: str) -> str:
    return normalize(value).casefold()


def valid_url(value: str) -> bool:
    try:
        parsed = urlparse(normalize(value))
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


def open_text(path: Path):
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8-sig", newline="")
    return path.open("r", encoding="utf-8-sig", newline="")


def load_rows(path: Path) -> list[dict[str, str]]:
    with open_text(path) as handle:
        return list(csv.DictReader(handle))


def audit(rows: list[dict[str, str]]) -> dict:
    missing_columns = [c for c in REQUIRED if not rows or c not in rows[0]]
    ids = [normalize(r.get("ID", "")) for r in rows]
    terms = [canonical(r.get("English term", "")) for r in rows]

    missing = {
        col: sum(1 for row in rows if not normalize(row.get(col, "")))
        for col in REQUIRED
    }

    duplicate_ids = [k for k, count in Counter(ids).items() if k and count > 1]
    duplicate_terms = [k for k, count in Counter(terms).items() if k and count > 1]

    return {
        "total_records": len(rows),
        "missing_columns": missing_columns,
        "duplicate_ids": duplicate_ids,
        "duplicate_preferred_english_labels": duplicate_terms,
        "missing_values_by_column": missing,
        "invalid_source_urls": [
            r.get("ID", "")
            for r in rows
            if not valid_url(r.get("source identifier/link", ""))
        ],
        "validation_status_counts": dict(
            Counter(r.get("validation status", "") for r in rows)
        ),
        "translation_strategy_counts": dict(
            Counter(r.get("translation strategy", "") for r in rows)
        ),
        "domain_counts": dict(Counter(r.get("domain", "") for r in rows)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    report = audit(load_rows(args.corpus))
    output = json.dumps(report, ensure_ascii=False, indent=2)
    print(output)

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(output, encoding="utf-8")

    hard_fail = (
        report["total_records"] == 0
        or bool(report["missing_columns"])
        or bool(report["duplicate_ids"])
        or bool(report["duplicate_preferred_english_labels"])
        or bool(report["invalid_source_urls"])
        or report["missing_values_by_column"]["ID"] > 0
        or report["missing_values_by_column"]["English term"] > 0
        or report["missing_values_by_column"]["Hausa term"] > 0
        or report["missing_values_by_column"]["concise definition"] > 0
        or report["missing_values_by_column"]["source identifier/link"] > 0
    )
    raise SystemExit(1 if hard_fail else 0)


if __name__ == "__main__":
    main()
