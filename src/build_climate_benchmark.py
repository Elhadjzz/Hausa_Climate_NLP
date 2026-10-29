#!/usr/bin/env python3
"""Build a deterministic silver HESTC terminology benchmark.

The default "core" benchmark uses only the more conservative HESTC strategies:
Existing Hausa technical term, Direct equivalence, and Descriptive translation.
Hybrid candidates can be included explicitly for stress testing.

The benchmark is intentionally labelled silver: Hausa targets are provisional
HESTC candidates, not human gold-standard translations.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
from collections import Counter, defaultdict
from pathlib import Path

CLIMATE_KEYWORDS = {
    "climate", "weather", "meteorolog", "atmospher", "carbon", "greenhouse",
    "emission", "mitigation", "adaptation", "resilien", "drought", "flood",
    "disaster", "hazard", "risk", "water", "hydrolog", "agricultur", "soil",
    "land", "forest", "biodivers", "ecosystem", "pollution", "energy",
    "renewable", "finance", "governance", "monitor", "satellite", "remote",
    "earth observation", "temperature", "precipitation", "rainfall", "warning",
}

DEFAULT_ALLOWED_STRATEGIES = {
    "Existing Hausa technical term",
    "Direct equivalence",
    "Descriptive translation",
}

FIELDS = [
    "benchmark_id", "HESTC_ID", "English term", "Hausa candidate", "domain",
    "subdomain", "terminology type", "translation strategy", "concise definition",
    "source institution", "source identifier/link", "reference_status", "split",
]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def climate_relevance(row: dict[str, str]) -> int:
    haystack = " ".join(
        normalize(row.get(k, "")).casefold()
        for k in ("English term", "subdomain", "concise definition", "domain")
    )
    return sum(1 for kw in CLIMATE_KEYWORDS if kw in haystack)


def stable_score(seed: int, hestc_id: str) -> int:
    digest = hashlib.sha256(f"{seed}:{hestc_id}".encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def split_for_index(i: int, n: int) -> str:
    frac = (i + 0.5) / n
    if frac <= 0.70:
        return "train"
    if frac <= 0.85:
        return "dev"
    return "test"


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def build(
    rows: list[dict[str, str]],
    per_domain: int,
    seed: int,
    include_hybrid: bool = False,
):
    allowed = set(DEFAULT_ALLOWED_STRATEGIES)
    if include_hybrid:
        allowed.add("Hybrid translation")

    eligible = []
    for row in rows:
        if row.get("validation status") != "Candidate drafted":
            continue
        if row.get("translation strategy") not in allowed:
            continue
        if not normalize(row.get("Hausa candidate", "")):
            continue
        relevance = climate_relevance(row)
        if relevance == 0:
            continue
        item = dict(row)
        item["_relevance"] = relevance
        item["_stable"] = stable_score(seed, row["ID"])
        eligible.append(item)

    by_domain: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in eligible:
        by_domain[row["domain"]].append(row)

    selected = []
    for domain in sorted(by_domain):
        candidates = sorted(
            by_domain[domain],
            key=lambda r: (-r["_relevance"], r["_stable"]),
        )[:per_domain]
        if len(candidates) < per_domain:
            raise RuntimeError(
                f"Only {len(candidates)} eligible rows in {domain}; need {per_domain}."
            )
        candidates = sorted(candidates, key=lambda r: r["_stable"])
        for i, row in enumerate(candidates):
            selected.append((row, split_for_index(i, len(candidates))))

    selected.sort(key=lambda x: (x[0]["domain"], x[0]["ID"]))

    output = []
    for idx, (row, split) in enumerate(selected, start=1):
        output.append({
            "benchmark_id": f"HCLIM-{idx:04d}",
            "HESTC_ID": row["ID"],
            "English term": normalize(row["English term"]),
            "Hausa candidate": normalize(row["Hausa candidate"]),
            "domain": row["domain"],
            "subdomain": row["subdomain"],
            "terminology type": row["terminology type"],
            "translation strategy": row["translation strategy"],
            "concise definition": normalize(row["concise definition"]),
            "source institution": row["source institution"],
            "source identifier/link": row["source identifier/link"],
            "reference_status": "provisional_silver_candidate",
            "split": split,
        })
    return output


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--per-domain", type=int, default=50)
    ap.add_argument("--seed", type=int, default=20261029)
    ap.add_argument(
        "--include-hybrid",
        action="store_true",
        help="Include provisional Hybrid translation candidates for stress testing",
    )
    args = ap.parse_args()

    rows = build(
        load_csv(args.corpus),
        args.per_domain,
        args.seed,
        include_hybrid=args.include_hybrid,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} silver benchmark rows to {args.out}")
    print("Split counts:", dict(Counter(r["split"] for r in rows)))
    print("Strategy counts:", dict(Counter(r["translation strategy"] for r in rows)))
    print("Domain counts:", dict(Counter(r["domain"] for r in rows)))


if __name__ == "__main__":
    main()
