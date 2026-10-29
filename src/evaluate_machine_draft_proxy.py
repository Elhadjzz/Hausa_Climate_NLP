#!/usr/bin/env python3
"""Engineering-only proxy evaluation against machine-assisted Hausa drafts.

These metrics MUST NOT be reported as human-reference MT quality. They compare
model outputs with an AI-assisted review draft to help diagnose the systems
before human reference adjudication is complete.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--system-output", type=Path, required=True)
    ap.add_argument("--machine-reference", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args=ap.parse_args()

    try:
        import sacrebleu
    except ImportError as exc:
        raise SystemExit("Install requirements-experiment.txt") from exc

    refs={r["sentence_id"]:r for r in read_csv(args.machine_reference)}
    rows=read_csv(args.system_output)

    hypotheses=[]
    references=[]
    used=[]
    for row in rows:
        ref=refs.get(row["sentence_id"],{}).get("machine_hausa_pretranslation","").strip()
        hyp=row.get("translation","").strip()
        if ref and hyp:
            hypotheses.append(hyp)
            references.append(ref)
            used.append(row["sentence_id"])

    report={
        "n":len(used),
        "BLEU_proxy":sacrebleu.corpus_bleu(hypotheses,[references]).score if used else None,
        "chrF_proxy":sacrebleu.corpus_chrf(hypotheses,[references]).score if used else None,
        "reference_type":"AI-assisted machine pretranslation; NOT human gold",
        "publication_warning":(
            "These scores are engineering diagnostics only. Replace the machine "
            "drafts with independently reviewed final Hausa references before "
            "reporting BLEU/chrF as publication results."
        ),
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
