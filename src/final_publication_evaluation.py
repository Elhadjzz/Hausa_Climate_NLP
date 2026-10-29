#!/usr/bin/env python3
"""Publication-grade evaluation for the HESTC-ClimateNLP experiment.

This script deliberately refuses to score unvalidated references as gold.
It expects an adjudicated review CSV and includes only rows whose final
validation status is exactly "Validated" and whose final Hausa reference is
non-empty.

It reports:
- BLEU and chrF for baseline and HESTC-grounded systems
- exact terminology inclusion accuracy
- per-domain breakdowns
- paired bootstrap confidence intervals for chrF difference
- paired exact-term win/loss/tie counts
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def norm(text: str) -> str:
    text = re.sub(r"[^\w\sƙƘɗƊɓƁƴƳʼ'-]", " ", (text or "").casefold())
    return re.sub(r"\s+", " ", text).strip()


def contains_phrase(text: str, phrase: str) -> bool:
    return bool(norm(phrase)) and norm(phrase) in norm(text)


def indexed(rows):
    return {r["sentence_id"]: r for r in rows}


def choose_final_term(review_row):
    # Prefer explicit final term if a later review schema adds it.
    for col in (
        "final_hausa_term",
        "final preferred Hausa",
        "domain expert revision",
        "domain_expert_revision",
        "linguist revision",
        "linguist_revision",
        "provisional Hausa candidate",
        "provisional_hestc_candidate",
    ):
        value=(review_row.get(col) or "").strip()
        if value:
            return value
    return ""


def corpus_metrics(hypotheses, references):
    import sacrebleu
    return {
        "BLEU": sacrebleu.corpus_bleu(hypotheses, [references]).score,
        "chrF": sacrebleu.corpus_chrf(hypotheses, [references]).score,
    }


def bootstrap_chrf_delta(base_h, ground_h, refs, iterations=1000, seed=20261029):
    import sacrebleu
    rng=random.Random(seed)
    n=len(refs)
    deltas=[]
    for _ in range(iterations):
        idx=[rng.randrange(n) for _ in range(n)]
        b=[base_h[i] for i in idx]
        g=[ground_h[i] for i in idx]
        r=[refs[i] for i in idx]
        bd=sacrebleu.corpus_chrf(b,[r]).score
        gd=sacrebleu.corpus_chrf(g,[r]).score
        deltas.append(gd-bd)
    deltas.sort()
    lo=deltas[int(0.025*iterations)]
    hi=deltas[min(iterations-1,int(0.975*iterations))]
    return {
        "mean_delta_chrF": sum(deltas)/len(deltas),
        "95pct_CI": [lo,hi],
        "iterations": iterations,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--baseline", type=Path, required=True)
    ap.add_argument("--grounded", type=Path, required=True)
    ap.add_argument("--review", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--bootstrap", type=int, default=1000)
    args=ap.parse_args()

    base=indexed(read_csv(args.baseline))
    ground=indexed(read_csv(args.grounded))
    review=indexed(read_csv(args.review))

    eligible=[]
    for sid,row in review.items():
        status=(row.get("final validation status") or row.get("final_validation_status") or "").strip()
        reference=(row.get("final Hausa reference") or row.get("final_hausa_reference") or "").strip()
        if status=="Validated" and reference and sid in base and sid in ground:
            eligible.append((sid,row,reference))

    if not eligible:
        raise SystemExit(
            "No publication-grade rows found. Human review must populate final Hausa "
            "references and mark final validation status as Validated."
        )

    base_h=[]
    ground_h=[]
    refs=[]
    domains=[]
    term_rows=[]

    for sid,row,ref in eligible:
        bh=base[sid]["translation"].strip()
        gh=ground[sid]["translation"].strip()
        term=choose_final_term(row)
        domain=row.get("domain") or base[sid].get("domain","")
        base_h.append(bh)
        ground_h.append(gh)
        refs.append(ref)
        domains.append(domain)
        term_rows.append((term,bh,gh,domain))

    base_metrics=corpus_metrics(base_h,refs)
    ground_metrics=corpus_metrics(ground_h,refs)

    base_term=[contains_phrase(bh,t) for t,bh,gh,d in term_rows if t]
    ground_term=[contains_phrase(gh,t) for t,bh,gh,d in term_rows if t]

    wins=losses=ties=0
    for t,bh,gh,d in term_rows:
        if not t:
            continue
        b=contains_phrase(bh,t)
        g=contains_phrase(gh,t)
        if g and not b:
            wins+=1
        elif b and not g:
            losses+=1
        else:
            ties+=1

    domain_report={}
    for domain in sorted(set(domains)):
        idx=[i for i,d in enumerate(domains) if d==domain]
        b=[base_h[i] for i in idx]
        g=[ground_h[i] for i in idx]
        r=[refs[i] for i in idx]
        domain_report[domain]={
            "n":len(idx),
            "baseline":corpus_metrics(b,r),
            "grounded":corpus_metrics(g,r),
        }

    report={
        "reference_type":"independently reviewed human Hausa references",
        "validated_sentence_count":len(eligible),
        "baseline":base_metrics,
        "hestc_grounded":ground_metrics,
        "delta":{
            "BLEU":ground_metrics["BLEU"]-base_metrics["BLEU"],
            "chrF":ground_metrics["chrF"]-base_metrics["chrF"],
        },
        "terminology_accuracy":{
            "n":len(base_term),
            "baseline":sum(base_term)/len(base_term) if base_term else None,
            "hestc_grounded":sum(ground_term)/len(ground_term) if ground_term else None,
            "grounded_wins":wins,
            "baseline_wins":losses,
            "ties":ties,
        },
        "bootstrap_chrF_delta":bootstrap_chrf_delta(
            base_h,ground_h,refs,iterations=args.bootstrap
        ) if len(eligible)>=20 else {
            "note":"At least 20 validated sentences are recommended for bootstrap inference."
        },
        "by_domain":domain_report,
    }

    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
