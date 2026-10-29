#!/usr/bin/env python3
"""Build the 800-sentence HESTC ClimateNLP human-reference benchmark.

Design:
- 80 sentences per HESTC domain = 800 total.
- Split within every domain: 48 train, 12 dev, 20 test.
- Blind translation data hide provisional Hausa terminology.
- A separate terminology key supports later adjudication.
- Hausa reference sentences remain blank until independently translated.
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

DOMAIN_CONTEXTS = {
    "Climate, Meteorology & Atmospheric Science": [
        "seasonal forecasting and early-warning services",
        "climate monitoring and weather-risk communication",
        "forecast verification and climate-service delivery",
        "preparedness for extreme weather and climate variability",
    ],
    "Water, Hydrology & Sanitation": [
        "drought preparedness and water-security planning",
        "flood management and freshwater-resource protection",
        "safe water services under changing climate conditions",
        "climate-resilient water and sanitation management",
    ],
    "Land, Soil, Drought & Desertification": [
        "drought resilience and sustainable land management",
        "soil protection and land-restoration programmes",
        "desertification control and climate adaptation",
        "productive landscapes under increasing climate stress",
    ],
    "Biodiversity, Ecology & Conservation": [
        "species conservation and protected-area planning",
        "ecosystem restoration and climate-impact assessment",
        "habitat protection and biodiversity monitoring",
        "nature-based adaptation and ecological resilience",
    ],
    "Forestry, Agriculture & Natural Resources": [
        "climate-smart agriculture and food-security planning",
        "forest management and climate adaptation",
        "sustainable natural-resource management",
        "agricultural resilience to changing rainfall and temperature",
    ],
    "Pollution, Chemicals, Waste & Circular Economy": [
        "pollution prevention and climate-resilient environmental services",
        "chemical safety and environmental-health protection",
        "waste management and circular-economy planning",
        "control of environmental contamination under climate stress",
    ],
    "Energy, Emissions & Environmental Technology": [
        "low-carbon development and energy-transition planning",
        "emissions reduction and climate-mitigation policy",
        "renewable-energy deployment and system resilience",
        "climate-resilient environmental technology",
    ],
    "Disaster Risk, Adaptation & Resilience": [
        "climate adaptation and disaster-risk reduction",
        "community preparedness and early warning",
        "resilience planning for climate-related hazards",
        "recovery and risk-informed development",
    ],
    "Environmental Policy, Law, Governance & Finance": [
        "climate governance and environmental policy",
        "adaptation finance and accountable decision-making",
        "environmental law and climate-policy implementation",
        "public investment for resilient and low-carbon development",
    ],
    "Environmental Monitoring, GIS, Remote Sensing & Scientific Methods": [
        "Earth observation and environmental monitoring",
        "spatial analysis for climate-risk assessment",
        "remote sensing of environmental change",
        "scientific evidence for climate and ecosystem decisions",
    ],
}

TEMPLATES = [
    "Reliable information on {term} supports {context}.",
    "Decision-makers consider {term} when planning for {context}.",
    "Monitoring {term} can strengthen {context}.",
    "Understanding {term} helps practitioners improve {context}.",
    "Assessments of {term} provide evidence for {context}.",
    "Changes in {term} can affect decisions related to {context}.",
    "Field programmes track {term} to support {context}.",
    "Researchers analyse {term} when evaluating {context}.",
    "Information about {term} can support {context}.",
    "Effective management of {term} can contribute to {context}.",
    "Public agencies use data on {term} to guide {context}.",
    "{term_cap} is relevant to decisions about {context}.",
    "Planning teams evaluate {term} when developing strategies for {context}.",
    "Evidence about {term} can improve {context}.",
    "Technical specialists document {term} to inform {context}.",
    "Institutions may consider {term} when designing programmes for {context}.",
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
    if not 3 <= len(term) <= 80 or len(term.split()) > 9:
        return False
    if re.match(r"^\d", term):
        return False
    if any(ch in term for ch in ("=", "→", "≥", "≤", "{", "}")):
        return False
    if term.isupper() and len(term) <= 8:
        return False
    return True


def choose_context(row: dict[str, str], seed: int) -> str:
    term = norm(row["English term"]).casefold()
    contexts = DOMAIN_CONTEXTS[row["domain"]]
    start = stable(seed + 31, row["ID"]) % len(contexts)
    ordered = contexts[start:] + contexts[:start]
    for context in ordered:
        if term not in context.casefold():
            return context
    return ordered[0]


def make_sentence(row: dict[str, str], seed: int) -> str:
    term = norm(row["English term"])
    context = choose_context(row, seed)

    if term in {"Extinct", "Endangered"}:
        return (
            f"The category {term} is used when assessing species status in "
            f"{context}."
        )

    term_low = term.casefold()
    candidates = list(range(len(TEMPLATES)))
    if term_low.startswith("monitor") and 2 in candidates:
        candidates.remove(2)
    if "management" in term_low and 9 in candidates:
        candidates.remove(9)
    if term_low.startswith("assessment") and 4 in candidates:
        candidates.remove(4)
    if term_low.startswith("evidence") and 13 in candidates:
        candidates.remove(13)
    if term_low.startswith("data") and 10 in candidates:
        candidates.remove(10)

    idx = candidates[stable(seed + 29, row["ID"]) % len(candidates)]
    return TEMPLATES[idx].format(
        term=term,
        term_cap=term[0].upper() + term[1:] if term else term,
        context=context,
    )


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
    for domain in sorted(DOMAIN_CONTEXTS):
        core = [r for r in by_domain[domain] if r["translation strategy"] in CORE]
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
                r for r in by_domain[domain]
                if r["ID"] not in used and r["translation strategy"] in FILL
            ]
            fill.sort(
                key=lambda r: (
                    -r["_relevance"],
                    abs(len(r["English term"].split()) - 3),
                    r["_stable"],
                )
            )
            chosen.extend(fill[:per_domain - len(chosen)])

        if len(chosen) != per_domain:
            raise RuntimeError(
                f"{domain}: selected {len(chosen)}, expected {per_domain}"
            )

        chosen.sort(key=lambda r: stable(seed + 17, r["ID"]))
        for i, row in enumerate(chosen):
            split = "train" if i < 48 else ("dev" if i < 60 else "test")
            selected.append((row, split))

    return selected


def build_records(selected, seed: int):
    blind, key, review = [], [], []
    for index, (row, split) in enumerate(selected, start=1):
        sid = f"HCLIM-SENT-{index:04d}"
        sentence = make_sentence(row, seed)
        term = norm(row["English term"])

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

    write(
        args.out_dir / "HESTC_ClimateNLP_Human_Benchmark_800_Blind.csv",
        blind,
        BLIND_FIELDS,
    )
    write(
        args.out_dir / "HESTC_ClimateNLP_Human_Benchmark_800_Key.csv",
        key,
        KEY_FIELDS,
    )
    write(
        args.out_dir / "HESTC_ClimateNLP_Human_Benchmark_800_Review.csv",
        review,
        REVIEW_FIELDS,
    )

    print("Total sentences:", len(blind))
    print("Split counts:", dict(Counter(r["split"] for r in blind)))
    print("Domain counts:", dict(Counter(r["domain"] for r in blind)))
    print("Strategy counts:", dict(Counter(r["translation strategy"] for r in key)))


if __name__ == "__main__":
    main()
