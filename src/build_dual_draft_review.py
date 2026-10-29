#!/usr/bin/env python3
"""Build a human-review CSV containing two independent machine aids.

Draft A: HESTC terminology-preserving pretranslation.
Draft B: unconstrained NLLB Hausa translation.

Neither draft is a gold reference. Reviewers must produce a final Hausa
reference after linguistic and environmental-domain adjudication.
"""
from __future__ import annotations
import argparse
import csv
from pathlib import Path


def load(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def index(rows):
    return {r["sentence_id"]: r for r in rows}


FIELDS = [
    "sentence_id","split","domain","subdomain","HESTC_ID","English term",
    "english_sentence","provisional_hestc_candidate","translation_strategy",
    "hestc_preserving_draft","nllb_baseline_draft",
    "linguist_preferred_starting_draft","linguist_decision","linguist_revision",
    "linguist_notes","domain_expert_decision","domain_expert_revision",
    "domain_expert_notes","final_hausa_reference","terminology_preserved",
    "final_validation_status","source institution","source URL",
]


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--pretranslation", type=Path, required=True)
    ap.add_argument("--nllb-drafts", type=Path, required=True)
    ap.add_argument("--key", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args=ap.parse_args()

    pre=index(load(args.pretranslation))
    nllb=index(load(args.nllb_drafts))
    key=index(load(args.key))

    common=sorted(set(pre) & set(nllb) & set(key))
    if not common:
        raise SystemExit("No matching sentence_id values across inputs")

    out=[]
    for sid in common:
        p=pre[sid]
        n=nllb[sid]
        k=key[sid]
        out.append({
            "sentence_id":sid,
            "split":p.get("split",""),
            "domain":p.get("domain",""),
            "subdomain":p.get("subdomain",""),
            "HESTC_ID":p.get("HESTC_ID",""),
            "English term":p.get("English term",""),
            "english_sentence":p.get("english_sentence",""),
            "provisional_hestc_candidate":p.get("provisional Hausa candidate",""),
            "translation_strategy":p.get("translation strategy",""),
            "hestc_preserving_draft":p.get("machine_hausa_pretranslation",""),
            "nllb_baseline_draft":n.get("hausa_reference_draft", n.get("translation","")),
            "linguist_preferred_starting_draft":"",
            "linguist_decision":"",
            "linguist_revision":"",
            "linguist_notes":"",
            "domain_expert_decision":"",
            "domain_expert_revision":"",
            "domain_expert_notes":"",
            "final_hausa_reference":"",
            "terminology_preserved":"",
            "final_validation_status":"Awaiting linguistic review",
            "source institution":p.get("source institution",""),
            "source URL":p.get("source identifier/link",""),
        })

    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS)
        w.writeheader()
        w.writerows(out)

    print(f"Wrote {len(out)} dual-draft review rows to {args.out}")


if __name__=="__main__":
    main()
