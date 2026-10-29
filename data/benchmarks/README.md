# HESTC-ClimateNLP benchmarks

## Silver terminology benchmark

The 500-term silver benchmark is generated deterministically rather than stored as a canonical source file.

~~~bash
python src/merge_corpus_parts.py
python src/build_climate_benchmark.py \
  --corpus data/HESTC10K_master.csv \
  --out data/benchmarks/hestc_climate_silver_terms.csv
~~~

Default composition:

- 500 total terms
- 50 terms from each of the 10 HESTC domains
- deterministic seed: `20261029`
- provisional Hausa candidates only
- core benchmark uses `Existing Hausa technical term`, `Direct equivalence`, and `Descriptive translation`
- `Hybrid translation`, `Borrowing/transliteration`, and `Needs expert coinage` are excluded from the core benchmark
- use `--include-hybrid` only for a separate stress-test benchmark
- approximate 70/15/15 train/dev/test split

The GitHub CI workflow also generates this benchmark and publishes it as a workflow artifact.

## Human sentence benchmark

`human_sentence_benchmark_template.csv` defines the publication-grade schema.

Do not auto-fill its `hausa_reference` field from HESTC candidate strings. Hausa sentence references should be independently translated and reviewed.

Recommended target:

- 500–1,000 climate-information sentences
- at least 200 held-out test sentences
- Hausa linguistic review
- climate/environment domain review
- explicit HESTC concept IDs for terminology evaluation
