#!/usr/bin/env python3
"""Merge machine-assisted Hausa drafts into the 800-sentence review CSV.

The output remains a review file. It does not promote any sentence to gold or
any HESTC term to Validated.
"""
from __future__ import annotations
import argparse
import csv
from pathlib import Path


def load(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--review", type=Path, required=True)
    ap.add_argument("--drafts", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args=ap.parse_args()

    review=load(args.review)
    drafts={r["sentence_id"]:r for r in load(args.drafts)}

    for row in review:
        d=drafts.get(row["sentence_id"])
        if not d:
            continue
        row["independent_hausa_reference"]=""
        row["machine_hausa_draft"]=d.get("hausa_reference_draft","")
        row["machine_model"]=d.get("model","")
        row["machine_system"]=d.get("system","")
        row["final_validation_status"]="Machine draft available; awaiting human review"

    fields=list(review[0].keys())
    # Insert machine fields before reviewer decisions when newly added.
    for field in ["machine_hausa_draft","machine_model","machine_system"]:
        if field not in fields:
            fields.append(field)

    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        w.writerows(review)
    print(f"Merged {sum(1 for r in review if r.get('machine_hausa_draft'))} drafts into {args.out}")


if __name__=="__main__":
    main()
