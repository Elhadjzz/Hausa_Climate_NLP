#!/usr/bin/env python3
"""Build the 800-sentence HESTC ClimateNLP human-reference benchmark.

Design:
- 80 sentences per HESTC domain = 800 total.
- Split within every domain: 48 train, 12 dev, 20 test.
- The blind translation file hides provisional Hausa terminology.
- A separate terminology key supports later linguistic/domain adjudication.
- Hausa reference sentences remain blank until independently translated.

The script prefers higher-confidence terminology strategies and fills a domain
shortfall from Hybrid translation only when needed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
from collections import Counter, defaultdict
from pathlib import Path

CORE = {
    "Existing Hausa technical term",
    "Direct equivalence",
    "Descriptive translation",
}
FILL = {"Hybrid translation"}
STRATEGY_PRIORITY = {
    "Existing Hausa technical term": 0,
    "Direct equivalence": 1,
    "Descriptive translation": 2,
    "Hybrid translation": 3,
}

CLIMATE_KEYWORDS = {
    "climate", "weather", "meteorolog", "atmospher", "carbon", "greenhouse",
    "emission", "mitigation", "adaptation", "resilien", "drought", "flood",
    "disaster", "hazard", "risk", "water", "hydrolog", "agricultur", "soil",
    "land", "forest", "biodivers", "ecosystem", "pollution", "energy",
    "renewable", "finance", "governance", "monitor", "satellite", "remote",
    "earth observation", "temperature", "precipitation", "rainfall", "warning",
}

DOMAIN_CONTEXT = {
    "Climate, Meteorology & Atmospheric Science":
        "weather forecasting, climate monitoring, and early-warning services",
    "Water, Hydrology & Sanitation":
        "water security, drought preparedness, flood management, and safe water services",
    "Land, Soil, Drought & Desertification":
        "land restoration, drought resilience, soil protection, and sustainable land management",
    "Biodiversity, Ecology & Conservation":
        "biodiversity conservation, ecosystem resilience, and climate-impact assessment",
    "Forestry, Agriculture & Natural Resources":
        "climate-smart agriculture, forest management, food security, and natural-resource planning",
    "Pollution, Chemicals, Waste & Circular Economy":
        "pollution prevention, chemical safety, waste management, and climate-resilient environmental services",
    "Energy, Emissions & Environmental Technology":
        "low-carbon development, energy transition, emissions management, and climate-resilient technology",
    "Disaster Risk, Adaptation & Resilience":
        "climate adaptation, disaster-risk reduction, preparedness, and community resilience",
    "Environmental Policy, Law, Governance & Finance":
        "climate governance, environmental policy, adaptation finance, and accountable decision-making",
    "Environmental Monitoring, GIS, Remote Sensing & Scientific Methods":
        "Earth observation, environmental monitoring, spatial analysis, and climate-risk assessment",
}

TEMPLATES = [
    "Reliable information on {term} supports {context}.",
    "Decision-makers consider {term} when planning for {context}.",
    "Monitoring {term} can strengthen {context}.",
    "Understanding {term} helps practitioners improve {context}.",
    "Assessments of {term} provide evidence for {context}.",
    "Changes in {term} can affect decisions related to {context}.",
    "Field programmes track {term} to support {context}.",
    "Researchers analyse {term} as part of {context}.",
    "Communities benefit when information about {term} is incorporated into {context}.",
    "Effective management of {term} can contribute to {context}.",
    "Public agencies use data on {term} to guide {context}.",
    "The concept of {term} is relevant to {context}.",
    "Planning teams evaluate {term} when developing strategies for {context}.",
    "Evidence about {term} can improve {context}.",
    "Technical specialists document {term} to inform {context}.",
    "Local and national institutions may consider {term} in {context}.",
]

BLIND_FIELDS = [
    "sentence_id", "english_sentence", "HESTC_ID", "English term", "domain",
    "subdomain", "terminology type", "source institution",
    "source identifier/link", "split", "translator_id", "hausa_reference",
    "translation_notes", "reference_status",
]

KEY_FIELDS = [
    "sentence_id", "HESTC_ID", "English term", "provisional Hausa candidate",
    "translation strategy", "concise definition", "domain", "subdomain",
    "terminology type", "source institution", "source identifier/link", "split",
    "reference_status",
]

REVIEW_FIELDS = [
    "sentence_id", "english_sentence", "HESTC_ID", "English term",
    "independent_hausa_reference", "provisional_hestc_candidate",
    "translation_strategy", "linguist_decision", "linguist_revision",
    "linguist_notes", "domain_expert_decision", "domain_expert_revision",
    "domain_expert_notes", "final_hausa_reference", "terminology_preserved",
    "final_validation_status", "split",
]


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def stable(seed: int, value: str) -> int:
    return int(hashlib.sha256(f"{seed}:{value}".encode()).hexdigest()[:16], 16)


def climate_relevance(row: dict[str, str]) -> int:
    text = " ".join(
        norm(row.get(k, "")).casefold()
        for k in ("English term", "subdomain", "concise definition", "domain")
    )
    return sum(1 for keyword in CLIMATE_KEYWORDS if keyword in text)


def valid_term(term: str) -> bool:
    term = norm(term)
    if not 3 <= len(term) <= 80:
        return False
    if len(term.split()) > 9:
        return False
    if re.match(r"^\d", term):
        return False
    if any(ch in term for ch in ("=", "→", "≥", "≤", "{", "}")):
        return False
    if term.isupper() and len(term) <= 8:
        return False
    return True


def load(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def select(rows, per_domain: int, seed: int):
    by_domain = defaultdict(list)
    for row in rows:
        if row.get("validation status") != "Candidate drafted":
            continue
        if row.get("translation strategy") not in CORE | FILL:
            continue
        if not valid_term(row.get("English term", "")):
            continue
        item = dict(row)
        item["_relevance"] = climate_relevance(row)
        item["_stable"] = stable(seed, row["ID"])
        item["_priority"] = STRATEGY_PRIORITY.get(row["translation strategy"], 99)
        by_domain[row["domain"]].append(item)

    selected = []
    for domain in sorted(DOMAIN_CONTEXT):
        candidates = by_domain[domain]
        core = [r for r in candidates if r["translation strategy"] in CORE]
        core.sort(
            key=lambda r: (
                -r["_relevance"],
                r["_priority"],
                abs(len(r["English term"].split()) - 3),
                r["_stable"],
            )
        )
        chosen = core[:per_domain]

        if len(chosen) < per_domain:
            used = {r["ID"] for r in chosen}
            fill = [
                r for r in candidates
                if r["ID"] not in used and r["translation strategy"] in FILL
            ]
            fill.sort(
                key=lambda r: (
                    -r["_relevance"],
                    abs(len(r["English term"].split()) - 3),
                    r["_stable"],
                )
            )
            chosen.extend(fill[: per_domain - len(chosen)])

        if len(chosen) != per_domain:
            raise RuntimeError(
                f"{domain}: selected {len(chosen)}, expected {per_domain}"
            )

        # Stable random-like ordering for split assignment.
        chosen.sort(key=lambda r: stable(seed + 17, r["ID"]))
        for i, row in enumerate(chosen):
            if i < 48:
                split = "train"
            elif i < 60:
                split = "dev"
            else:
                split = "test"
            selected.append((row, split))

    return selected


def build_records(selected, seed: int):
    blind, key, review = [], [], []

    for index, (row, split) in enumerate(selected, start=1):
        sid = f"HCLIM-SENT-{index:04d}"
        term = norm(row["English term"])
        context = DOMAIN_CONTEXT[row["domain"]]
        template = TEMPLATES[stable(seed + 29, row["ID"]) % len(TEMPLATES)]
        sentence = template.format(term=term, context=context)

        blind.append({
            "sentence_id": sid,
            "english_sentence": sentence,
            "HESTC_ID": row["ID"],
            "English term": term,
            "domain": row["domain"],
            "subdomain": row["subdomain"],
            "terminology type": row["terminology type"],
            "source institution": row["source institution"],
            "source identifier/link": row["source identifier/link"],
            "split": split,
            "translator_id": "",
            "hausa_reference": "",
            "translation_notes": "",
            "reference_status": "Awaiting independent Hausa translation",
        })

        key.append({
            "sentence_id": sid,
            "HESTC_ID": row["ID"],
            "English term": term,
            "provisional Hausa candidate": norm(row["Hausa candidate"]),
            "translation strategy": row["translation strategy"],
            "concise definition": norm(row["concise definition"]),
            "domain": row["domain"],
            "subdomain": row["subdomain"],
            "terminology type": row["terminology type"],
            "source institution": row["source institution"],
            "source identifier/link": row["source identifier/link"],
            "split": split,
            "reference_status": "Provisional terminology key; not gold reference",
        })

        review.append({
            "sentence_id": sid,
            "english_sentence": sentence,
            "HESTC_ID": row["ID"],
            "English term": term,
            "independent_hausa_reference": "",
            "provisional_hestc_candidate": norm(row["Hausa candidate"]),
            "translation_strategy": row["translation strategy"],
            "linguist_decision": "",
            "linguist_revision": "",
            "linguist_notes": "",
            "domain_expert_decision": "",
            "domain_expert_revision": "",
            "domain_expert_notes": "",
            "final_hausa_reference": "",
            "terminology_preserved": "",
            "final_validation_status": "Awaiting independent translation",
            "split": split,
        })

    return blind, key, review


def write(path: Path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--per-domain", type=int, default=80)
    ap.add_argument("--seed", type=int, default=20261029)
    args = ap.parse_args()

    selected = select(load(args.corpus), args.per_domain, args.seed)
    blind, key, review = build_records(selected, args.seed)

    write(args.out_dir / "HESTC_ClimateNLP_Human_Benchmark_800_Blind.csv", blind, BLIND_FIELDS)
    write(args.out_dir / "HESTC_ClimateNLP_Human_Benchmark_800_Key.csv", key, KEY_FIELDS)
    write(args.out_dir / "HESTC_ClimateNLP_Human_Benchmark_800_Review.csv", review, REVIEW_FIELDS)

    print("Total sentences:", len(blind))
    print("Split counts:", dict(Counter(r["split"] for r in blind)))
    print("Domain counts:", dict(Counter(r["domain"] for r in blind)))
    print("Strategy counts:", dict(Counter(r["translation strategy"] for r in key)))


if __name__ == "__main__":
    main()
