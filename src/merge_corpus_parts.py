#!/usr/bin/env python3
"""Merge canonical HESTC part CSVs into the 11,034-row master corpus.

The GitHub distribution stores HESTC in part-level CSV files to keep each
source artifact human-auditable and connector/GitHub friendly. This script
reconstructs:

- data/HESTC10K_master.csv
- data/HESTC10K_review_priority.csv
- data/HESTC10K_merge_QA.json

No terminology is generated or modified by this script.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
PART_DIR = ROOT / "data" / "corpus_parts"
DATA_DIR = ROOT / "data"

PART_FILES = [
    "Part1A_Terms.csv",
    "Part1B_Terms.csv",
    "Part1C_Terms.csv",
    "Part2A_Terms.csv",
    "Part2B_Terms.csv",
    "Part2C_Terms.csv",
    "Part3A_Terms.csv",
    "Part3B_Terms.csv",
    "Part3C_Terms.csv",
    "Part4A_Terms.csv",
    "Part4B_Terms.csv",
    "Part4C_Terms.csv",
    "Part5A_Terms.csv",
    "Part5B_Terms.csv",
    "Part6A_Terms.csv",
    "Part6B_Terms.csv",
    "Part7A_Terms.csv",
    "Part7B_Terms.csv",
    "Part8A_Terms.csv",
    "Part8B_Terms.csv",
    "Part9A_Terms.csv",
    "Part9B_Terms.csv",
    "Part10A_Terms.csv",
    "Part10B_Terms.csv",
]

EXPECTED_COUNTS = {
    "Part1A_Terms.csv": 330,
    "Part1B_Terms.csv": 408,
    "Part1C_Terms.csv": 329,
    "Part2A_Terms.csv": 369,
    "Part2B_Terms.csv": 391,
    "Part2C_Terms.csv": 361,
    "Part3A_Terms.csv": 440,
    "Part3B_Terms.csv": 454,
    "Part3C_Terms.csv": 306,
    "Part4A_Terms.csv": 507,
    "Part4B_Terms.csv": 449,
    "Part4C_Terms.csv": 224,
    "Part5A_Terms.csv": 522,
    "Part5B_Terms.csv": 614,
    "Part6A_Terms.csv": 587,
    "Part6B_Terms.csv": 468,
    "Part7A_Terms.csv": 537,
    "Part7B_Terms.csv": 473,
    "Part8A_Terms.csv": 489,
    "Part8B_Terms.csv": 487,
    "Part9A_Terms.csv": 593,
    "Part9B_Terms.csv": 500,
    "Part10A_Terms.csv": 576,
    "Part10B_Terms.csv": 620,
}

SCHEMA = [
    "ID",
    "English term",
    "synonym/abbreviation",
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

EXPECTED_TOTAL = 11034


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


def read_part(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != SCHEMA:
            raise ValueError(
                f"{path.name}: unexpected schema.\n"
                f"Expected: {SCHEMA}\nFound: {reader.fieldnames}"
            )
        return list(reader)


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SCHEMA)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    all_rows: list[dict[str, str]] = []
    observed_counts = {}

    for filename in PART_FILES:
        path = PART_DIR / filename
        if not path.exists():
            raise FileNotFoundError(path)

        rows = read_part(path)
        observed_counts[filename] = len(rows)

        expected = EXPECTED_COUNTS[filename]
        if len(rows) != expected:
            raise ValueError(
                f"{filename}: expected {expected} records, found {len(rows)}"
            )

        all_rows.extend(rows)

    ids = [normalize(row["ID"]) for row in all_rows]
    english = [canonical(row["English term"]) for row in all_rows]

    duplicate_ids = [key for key, n in Counter(ids).items() if key and n > 1]
    duplicate_terms = [
        key for key, n in Counter(english).items() if key and n > 1
    ]
    missing_definitions = [
        row["ID"] for row in all_rows if not normalize(row["concise definition"])
    ]
    missing_sources = [
        row["ID"]
        for row in all_rows
        if not normalize(row["source institution"])
        or not normalize(row["source identifier/link"])
    ]
    invalid_source_urls = [
        row["ID"]
        for row in all_rows
        if not valid_url(row["source identifier/link"])
    ]
    missing_hausa = [
        row["ID"] for row in all_rows if not normalize(row["Hausa candidate"])
    ]

    if len(all_rows) != EXPECTED_TOTAL:
        raise ValueError(
            f"Expected {EXPECTED_TOTAL} total records, found {len(all_rows)}"
        )
    if duplicate_ids:
        raise ValueError(f"Duplicate IDs detected: {duplicate_ids[:10]}")
    if duplicate_terms:
        raise ValueError(
            f"Duplicate preferred English labels detected: {duplicate_terms[:10]}"
        )
    if missing_definitions:
        raise ValueError(f"Missing definitions: {missing_definitions[:10]}")
    if missing_sources:
        raise ValueError(f"Missing sources: {missing_sources[:10]}")
    if invalid_source_urls:
        raise ValueError(f"Invalid source URLs: {invalid_source_urls[:10]}")
    if missing_hausa:
        raise ValueError(f"Missing Hausa candidates: {missing_hausa[:10]}")

    master_path = DATA_DIR / "HESTC10K_master.csv"
    review_path = DATA_DIR / "HESTC10K_review_priority.csv"

    write_rows(master_path, all_rows)

    review_rows = [
        row
        for row in all_rows
        if row["translation strategy"] == "Needs expert coinage"
    ]
    write_rows(review_path, review_rows)

    report = {
        "total_records": len(all_rows),
        "part_counts": observed_counts,
        "duplicate_ids": len(duplicate_ids),
        "duplicate_preferred_english_labels": len(duplicate_terms),
        "missing_definitions": len(missing_definitions),
        "missing_sources": len(missing_sources),
        "invalid_source_urls": len(invalid_source_urls),
        "missing_hausa_candidates": len(missing_hausa),
        "review_priority_records": len(review_rows),
        "validation_status_counts": dict(
            Counter(row["validation status"] for row in all_rows)
        ),
        "translation_strategy_counts": dict(
            Counter(row["translation strategy"] for row in all_rows)
        ),
    }

    qa_path = DATA_DIR / "HESTC10K_merge_QA.json"
    qa_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\nWrote: {master_path}")
    print(f"Wrote: {review_path}")
    print(f"Wrote: {qa_path}")


if __name__ == "__main__":
    main()
