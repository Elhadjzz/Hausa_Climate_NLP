#!/usr/bin/env python3
"""Detect HESTC concepts in climate text and return Hausa terminology context."""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import re
from pathlib import Path


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def open_text(path: Path):
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8-sig", newline="")
    return path.open("r", encoding="utf-8-sig", newline="")


def load_corpus(path: Path):
    with open_text(path) as handle:
        return list(csv.DictReader(handle))


def detect_terms(text: str, rows):
    normalized_text = normalize(text).casefold()
    hits = []
    occupied = []

    for row in sorted(rows, key=lambda r: len(r["English term"]), reverse=True):
        term = normalize(row["English term"])
        if len(term) < 3:
            continue

        match = re.search(
            r"(?<!\w)" + re.escape(term.casefold()) + r"(?!\w)",
            normalized_text,
        )
        if not match:
            continue

        span = match.span()
        if any(not (span[1] <= start or span[0] >= end) for start, end in occupied):
            continue

        occupied.append(span)
        hits.append(
            {
                "ID": row["ID"],
                "English term": term,
                "Hausa candidate": row["Hausa candidate"],
                "preferred Hausa": row["preferred Hausa"],
                "definition": row["concise definition"],
                "domain": row["domain"],
                "subdomain": row["subdomain"],
                "translation strategy": row["translation strategy"],
                "validation status": row["validation status"],
                "source": row["source identifier/link"],
            }
        )

    return sorted(hits, key=lambda item: item["English term"].casefold())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--text", required=True)
    args = parser.parse_args()

    result = {
        "input_text": args.text,
        "detected_concepts": detect_terms(args.text, load_corpus(args.corpus)),
        "grounding_note": (
            "Use HESTC forms as terminology context. Do not claim a Hausa term "
            "is validated unless its validation status is explicitly Validated."
        ),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
