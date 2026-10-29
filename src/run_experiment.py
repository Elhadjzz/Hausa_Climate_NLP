#!/usr/bin/env python3
"""Run baseline and HESTC-constrained NLLB experiments on a benchmark CSV."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd):
    print("+", " ".join(str(x) for x in cmd))
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--benchmark", type=Path, required=True)
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, default=Path("results/nllb_hestc"))
    ap.add_argument("--model", default="facebook/nllb-200-distilled-600M")
    ap.add_argument("--source-column", default="English term")
    ap.add_argument(
        "--constraint-column",
        default=None,
        help="Optional benchmark column containing the one Hausa term to constrain",
    )
    ap.add_argument("--device", default=None)
    ap.add_argument("--baseline-batch-size", type=int, default=1)
    ap.add_argument("--num-beams", type=int, default=5)
    ap.add_argument("--max-new-tokens", type=int, default=128)
    args = ap.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    py = sys.executable

    common = [
        py,
        "src/nllb_translate.py",
        "--input",
        str(args.benchmark),
        "--corpus",
        str(args.corpus),
        "--model",
        args.model,
        "--source-column",
        args.source_column,
    ]
    if args.constraint_column:
        common += ["--constraint-column", args.constraint_column]
    if args.device:
        common += ["--device", args.device]

    baseline = args.out_dir / "baseline.csv"
    grounded = args.out_dir / "hestc_constrained.csv"

    run(common + [
        "--mode", "baseline",
        "--output", str(baseline),
        "--batch-size", str(args.baseline_batch_size),
        "--max-new-tokens", str(args.max_new_tokens),
    ])
    run(common + [
        "--mode", "hestc_constrained",
        "--output", str(grounded),
        "--num-beams", str(args.num_beams),
        "--max-new-tokens", str(args.max_new_tokens),
    ])

    run([
        py,
        "src/evaluate_translation.py",
        "--input",
        str(baseline),
        "--output-json",
        str(args.out_dir / "baseline_metrics.json"),
    ])
    run([
        py,
        "src/evaluate_translation.py",
        "--input",
        str(grounded),
        "--output-json",
        str(args.out_dir / "hestc_constrained_metrics.json"),
    ])

    print(f"Experiment complete. Results: {args.out_dir}")


if __name__ == "__main__":
    main()
