#!/usr/bin/env python3
"""Summarize human review decisions for the HESTC ClimateNLP benchmark."""
from __future__ import annotations
import argparse,csv,json
from collections import Counter
from pathlib import Path


def load(path):
    with Path(path).open("r",encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("review_csv")
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    rows=load(args.review_csv)

    report={
        "sentences":len(rows),
        "linguist_decisions":dict(Counter(r.get("linguist_decision","") or "blank" for r in rows)),
        "domain_expert_decisions":dict(Counter(r.get("domain_expert_decision","") or "blank" for r in rows)),
        "terminology_preserved":dict(Counter(r.get("terminology_preserved","") or "blank" for r in rows)),
        "final_validation_status":dict(Counter(r.get("final_validation_status","") or "blank" for r in rows)),
        "final_references_populated":sum(bool((r.get("final_hausa_reference") or "").strip()) for r in rows),
    }
    text=json.dumps(report,ensure_ascii=False,indent=2)
    print(text)
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(text,encoding="utf-8")


if __name__=="__main__":
    main()
