#!/usr/bin/env python3
"""Split an 800-row review CSV into balanced reviewer batches."""
from __future__ import annotations
import argparse,csv
from collections import defaultdict
from pathlib import Path


def load(path):
    with Path(path).open("r",encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("input_csv")
    ap.add_argument("--out-dir",type=Path,required=True)
    ap.add_argument("--batches",type=int,default=4)
    args=ap.parse_args()

    rows=load(args.input_csv)
    buckets=[[] for _ in range(args.batches)]

    # Round-robin within domain + split keeps each batch approximately balanced.
    groups=defaultdict(list)
    for r in rows:
        groups[(r.get("domain",""),r.get("split",""))].append(r)

    for group in sorted(groups):
        for i,row in enumerate(sorted(groups[group],key=lambda x:x["sentence_id"])):
            buckets[i % args.batches].append(row)

    args.out_dir.mkdir(parents=True,exist_ok=True)
    for i,bucket in enumerate(buckets,1):
        bucket.sort(key=lambda r:(r.get("domain",""),r.get("split",""),r["sentence_id"]))
        p=args.out_dir/f"review_batch_{i:02d}.csv"
        with p.open("w",encoding="utf-8-sig",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(bucket)
        print(p, len(bucket))


if __name__=="__main__":
    main()
