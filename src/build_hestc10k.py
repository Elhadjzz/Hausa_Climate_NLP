#!/usr/bin/env python3
"""Reproducible HESTC-10K corpus assembly and QA pipeline.

This script rebuilds the assembly logic from curated staging records. It does
not scrape institutional websites or replace the intellectual work of deciding
which environmental concepts belong in the corpus.

Expected curated staging columns:
    English term
    synonym/abbreviation
    terminology type
    domain
    subdomain
    concise definition
    source_id

Optional Hausa-candidate file columns:
    ID
    Hausa candidate
    translation strategy
    preferred Hausa
    validation status
    reviewer notes
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

from hestc_schema import (
    DOMAIN_PREFIXES,
    SCHEMA,
    TERMINOLOGY_TYPES,
    TRANSLATION_STRATEGIES,
    VALIDATION_STATUSES,
)


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def canonical_term(value: str) -> str:
    return normalize_space(value).casefold()


def is_http_url(value: str) -> bool:
    try:
        parsed = urlparse(normalize_space(value))
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def load_source_registry(path: Path) -> dict[str, dict[str, str]]:
    registry: dict[str, dict[str, str]] = {}

    for row in read_csv(path):
        source_id = normalize_space(row.get("Source ID", ""))
        if not source_id:
            continue
        if source_id in registry:
            raise ValueError(f"Duplicate Source ID: {source_id}")

        url = normalize_space(row.get("URL", ""))
        if url and not is_http_url(url):
            raise ValueError(f"Invalid source URL for {source_id}: {url}")

        registry[source_id] = row

    return registry


def collect_staging_records(raw_dir: Path) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []

    for path in sorted(raw_dir.glob("*.csv")):
        for row in read_csv(path):
            row["_source_file"] = path.name
            records.append(row)

    return records


def deduplicate(records: list[dict[str, str]]):
    """Keep the first occurrence of each normalized preferred English label."""
    seen: dict[str, str] = {}
    kept: list[dict[str, str]] = []
    excluded: list[dict[str, str]] = []

    for row in records:
        term = normalize_space(row.get("English term", ""))
        key = canonical_term(term)

        if not term:
            row["_exclusion_reason"] = "blank preferred English label"
            excluded.append(row)
            continue

        if key in seen:
            row["_exclusion_reason"] = f"duplicate of {seen[key]}"
            excluded.append(row)
            continue

        seen[key] = term
        kept.append(row)

    return kept, excluded


def join_sources(
    records: list[dict[str, str]],
    registry: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    joined = []

    for row in records:
        source_id = normalize_space(row.get("source_id", ""))

        if source_id not in registry:
            raise ValueError(
                f"Unknown source_id {source_id!r} for {row.get('English term')!r}"
            )

        source = registry[source_id]
        result = dict(row)
        result["source institution"] = normalize_space(source.get("Institution", ""))
        result["source identifier/link"] = normalize_space(source.get("URL", ""))
        joined.append(result)

    return joined


def validate_english_record(row: dict[str, str]) -> None:
    required = [
        "English term",
        "terminology type",
        "domain",
        "subdomain",
        "concise definition",
        "source institution",
        "source identifier/link",
    ]

    for column in required:
        if not normalize_space(row.get(column, "")):
            raise ValueError(f"Missing {column!r} for {row.get('English term')!r}")

    if row["terminology type"] not in TERMINOLOGY_TYPES:
        raise ValueError(f"Invalid terminology type: {row['terminology type']}")

    if row["domain"] not in DOMAIN_PREFIXES:
        raise ValueError(f"Unknown domain: {row['domain']}")

    if not is_http_url(row["source identifier/link"]):
        raise ValueError(
            f"Invalid source URL for {row['English term']}: "
            f"{row['source identifier/link']}"
        )


def assign_ids(records: list[dict[str, str]]) -> list[dict[str, str]]:
    counters: defaultdict[str, int] = defaultdict(int)
    output = []

    for row in records:
        domain = row["domain"]
        counters[domain] += 1
        result = dict(row)
        result["ID"] = f"HESTC-{DOMAIN_PREFIXES[domain]}-{counters[domain]:04d}"
        output.append(result)

    return output


def initialize_translation_fields(records: list[dict[str, str]]):
    output = []

    for row in records:
        result = dict(row)
        result.setdefault("Hausa candidate", "")
        result.setdefault(
            "translation strategy",
            "Deferred — English-source curation phase",
        )
        result.setdefault("preferred Hausa", "")
        result.setdefault("validation status", "Not translated")
        result.setdefault("reviewer notes", "")
        output.append(result)

    return output


def merge_hausa_candidates(
    records: list[dict[str, str]],
    candidate_file: Path | None,
):
    """Merge provisional Hausa candidates by stable HESTC ID."""
    if candidate_file is None:
        return records

    candidates = {
        normalize_space(row["ID"]): row
        for row in read_csv(candidate_file)
    }

    output = []

    for row in records:
        result = dict(row)
        candidate = candidates.get(result["ID"])

        if candidate:
            strategy = normalize_space(candidate.get("translation strategy", ""))
            status = normalize_space(candidate.get("validation status", ""))

            if strategy not in TRANSLATION_STRATEGIES:
                raise ValueError(
                    f"Invalid translation strategy for {result['ID']}: {strategy}"
                )

            if status not in VALIDATION_STATUSES:
                raise ValueError(
                    f"Invalid validation status for {result['ID']}: {status}"
                )

            for column in [
                "Hausa candidate",
                "translation strategy",
                "preferred Hausa",
                "validation status",
                "reviewer notes",
            ]:
                result[column] = normalize_space(candidate.get(column, ""))

        output.append(result)

    return output


def qa(records: list[dict[str, str]]) -> dict:
    ids = [row["ID"] for row in records]
    terms = [canonical_term(row["English term"]) for row in records]

    return {
        "total_records": len(records),
        "duplicate_ids": [
            key for key, count in Counter(ids).items() if count > 1
        ],
        "duplicate_preferred_english_labels": [
            key for key, count in Counter(terms).items() if count > 1
        ],
        "missing_source_records": [
            row["ID"]
            for row in records
            if not row["source institution"] or not row["source identifier/link"]
        ],
        "invalid_source_urls": [
            row["ID"]
            for row in records
            if not is_http_url(row["source identifier/link"])
        ],
        "missing_hausa_candidates": [
            row["ID"]
            for row in records
            if not normalize_space(row.get("Hausa candidate", ""))
        ],
        "validation_status_counts": dict(
            Counter(row["validation status"] for row in records)
        ),
        "translation_strategy_counts": dict(
            Counter(row["translation strategy"] for row in records)
        ),
        "needs_expert_coinage_count": sum(
            1
            for row in records
            if row.get("translation strategy") == "Needs expert coinage"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sources",
        type=Path,
        required=True,
        help="HESTC institutional source catalogue CSV",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        required=True,
        help="Directory containing curated English staging CSV files",
    )
    parser.add_argument(
        "--hausa-candidates",
        type=Path,
        help="Optional Hausa-candidate CSV keyed by HESTC ID",
    )
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    registry = load_source_registry(args.sources)
    raw = collect_staging_records(args.raw_dir)
    deduped, excluded = deduplicate(raw)
    enriched = join_sources(deduped, registry)

    for row in enriched:
        validate_english_record(row)

    built = assign_ids(enriched)
    built = initialize_translation_fields(built)
    built = merge_hausa_candidates(built, args.hausa_candidates)

    report = qa(built)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "HESTC10K_master.csv", built, SCHEMA)

    if excluded:
        excluded_fields = sorted({key for row in excluded for key in row})
        write_csv(
            args.out_dir / "HESTC10K_duplicates_excluded.csv",
            excluded,
            excluded_fields,
        )

    priority = [
        row
        for row in built
        if row.get("translation strategy") == "Needs expert coinage"
    ]
    write_csv(args.out_dir / "HESTC10K_review_priority.csv", priority, SCHEMA)

    (args.out_dir / "HESTC10K_QA.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
