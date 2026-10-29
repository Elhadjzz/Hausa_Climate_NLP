#!/usr/bin/env python3
"""Build a stratified HESTC Hausa terminology validation pilot.

Default: 200 terms = 20 per domain. Within each domain the script seeks a mix
of core candidates and difficult candidates so reviewer effort is informative.
No row is automatically marked Validated.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
from collections import Counter, defaultdict
from pathlib import Path

CORE = {
    "Existing Hausa technical term",
    "Direct equivalence",
    "Descriptive translation",
}
HARD = {
    "Hybrid translation",
    "Borrowing/transliteration",
    "Needs expert coinage",
}

OUTPUT_FIELDS = [
    "validation_id", "HESTC_ID", "English term", "synonym/abbreviation",
    "concise definition", "domain", "subdomain", "terminology type",
    "source institution", "source identifier/link", "provisional Hausa candidate",
    "translation strategy", "current validation status", "linguist decision",
    "linguist revision", "linguist notes", "domain-expert decision",
    "domain-expert revision", "domain-expert notes", "final preferred Hausa",
    "harmonization notes", "final validation status",
]


def stable(seed: int, value: str) -> int:
    digest = hashlib.sha256(f"{seed}:{value}".encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def load(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def select(rows, per_domain: int, seed: int):
    by_domain = defaultdict(list)
    for row in rows:
        if row.get("validation status") != "Candidate drafted":
            continue
        item = dict(row)
        item["_stable"] = stable(seed, row["ID"])
        by_domain[row["domain"]].append(item)

    selected = []
    core_target = per_domain // 2
    hard_target = per_domain - core_target

    for domain in sorted(by_domain):
        core = sorted(
            [r for r in by_domain[domain] if r["translation strategy"] in CORE],
            key=lambda r: r["_stable"],
        )[:core_target]
        hard = sorted(
            [r for r in by_domain[domain] if r["translation strategy"] in HARD],
            key=lambda r: r["_stable"],
        )[:hard_target]
        chosen = core + hard

        if len(chosen) < per_domain:
            used = {r["ID"] for r in chosen}
            fill = sorted(
                [r for r in by_domain[domain] if r["ID"] not in used],
                key=lambda r: r["_stable"],
            )[: per_domain - len(chosen)]
            chosen.extend(fill)

        if len(chosen) != per_domain:
            raise RuntimeError(f"Could not select {per_domain} rows for {domain}")
        selected.extend(chosen)

    selected.sort(key=lambda r: (r["domain"], r["ID"]))
    return selected


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--per-domain", type=int, default=20)
    ap.add_argument("--seed", type=int, default=20261029)
    args = ap.parse_args()

    rows = select(load(args.corpus), args.per_domain, args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)

    with args.out.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for i, row in enumerate(rows, 1):
            writer.writerow({
                "validation_id": f"HVAL-{i:04d}",
                "HESTC_ID": row["ID"],
                "English term": row["English term"],
                "synonym/abbreviation": row["synonym/abbreviation"],
                "concise definition": row["concise definition"],
                "domain": row["domain"],
                "subdomain": row["subdomain"],
                "terminology type": row["terminology type"],
                "source institution": row["source institution"],
                "source identifier/link": row["source identifier/link"],
                "provisional Hausa candidate": row["Hausa candidate"],
                "translation strategy": row["translation strategy"],
                "current validation status": row["validation status"],
                "linguist decision": "",
                "linguist revision": "",
                "linguist notes": "",
                "domain-expert decision": "",
                "domain-expert revision": "",
                "domain-expert notes": "",
                "final preferred Hausa": "",
                "harmonization notes": "",
                "final validation status": "Under linguistic review",
            })

    print(f"Wrote {len(rows)} validation rows to {args.out}")
    print("Domains:", dict(Counter(r["domain"] for r in rows)))
    print("Strategies:", dict(Counter(r["translation strategy"] for r in rows)))


if __name__ == "__main__":
    main()
