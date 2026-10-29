# HESTC-ClimateNLP Experimental Protocol

## Research objective

Evaluate whether HESTC terminology grounding improves preservation of specialized climate and environmental terminology in English→Hausa machine translation.

## Research questions

**RQ1.** How accurately does a general multilingual NLLB model translate HESTC climate/environment terminology into Hausa?

**RQ2.** Does HESTC-constrained decoding improve terminology fidelity compared with unconstrained NLLB?

**RQ3.** On independently human-translated climate sentences, does terminology grounding improve terminology accuracy without materially degrading sentence-level translation quality?

## Hypotheses

- **H1:** HESTC-constrained NLLB will achieve higher terminology accuracy than unconstrained NLLB.
- **H2:** Gains will be largest for specialized hybrid/descriptive terminology.
- **H3:** On a human-reference sentence benchmark, HESTC constraints will improve terminology fidelity while maintaining comparable chrF/BLEU.

## Two benchmark levels

### Level A — Silver terminology benchmark

Generate `data/benchmarks/hestc_climate_silver_terms.csv` with `src/build_climate_benchmark.py`.

The default **core** benchmark contains 50 terms from each of the ten domains, for **500 terms total**. It uses only `Existing Hausa technical term`, `Direct equivalence`, and `Descriptive translation`. `Hybrid translation`, `Borrowing/transliteration`, and `Needs expert coinage` are excluded from the core benchmark. Hybrid candidates can be added explicitly with `--include-hybrid` for a separate stress test.

The Hausa targets are **provisional HESTC candidates**. Therefore this benchmark is appropriate for engineering and baseline diagnosis, but **not** for claiming human-reference machine-translation quality.

Recommended use:

1. quantify how often NLLB independently produces the same provisional terminology;
2. identify domains and strategies with weak baseline coverage;
3. test the constrained-decoding pipeline;
4. select difficult examples for human review.

### Level B — Human sentence benchmark

Use `data/benchmarks/human_sentence_benchmark_template.csv`.

This is the publication-grade evaluation layer. Populate it with independently translated English climate-information sentences and review each Hausa reference by a Hausa linguist and a climate/environment specialist.

Recommended size: **500–1,000 sentences**, with a held-out test set of at least 200 sentences.

## Systems

### B1 — NLLB baseline

Model: `facebook/nllb-200-distilled-600M`

Direction:

- source language: `eng_Latn`
- target language: `hau_Latn`

The implementation loads the model directly with `AutoTokenizer` and `AutoModelForSeq2SeqLM`.

### H1 — NLLB + HESTC constrained decoding

The source sentence is matched against HESTC preferred English terms. Up to three non-overlapping detected concepts are selected. By default, only the more conservative HESTC strategies are eligible for lexical constraints; hybrid candidates require an explicit `--include-hybrid` option. Eligible Hausa forms are tokenized and supplied to constrained beam search as required target phrases.

This is preferable to simply appending glossary translations after generation because terminology is enforced during decoding and the model optimizes the surrounding output jointly.

## Metrics

### Terminology Accuracy

For each expected term:

`TermAcc = correctly preserved expected Hausa terms / expected Hausa terms`

Report overall TermAcc and breakdowns by:

- HESTC domain;
- translation strategy;
- terminology type.

### Constraint Success Rate

Percentage of constrained outputs that contain every requested HESTC target phrase.

### Sentence-level quality

Only report these when independently reviewed Hausa sentence references are present:

- corpus BLEU;
- chrF;
- optionally COMET in a later experiment.

## Human validation

Do not convert silver HESTC candidates into “gold” references automatically. Publication results should use independently reviewed Hausa sentence references.

At minimum, each test sentence should have:

1. a Hausa translator or linguist;
2. a climate/environment domain reviewer;
3. recorded HESTC IDs for terminology being tested.

## Reproducible commands

Build the corpus and silver benchmark:

~~~bash
python src/merge_corpus_parts.py
python src/build_climate_benchmark.py   --corpus data/HESTC10K_master.csv   --out data/benchmarks/hestc_climate_silver_terms.csv
~~~

Install experimental dependencies:

~~~bash
pip install -r requirements-experiment.txt
~~~

Run baseline and HESTC-constrained NLLB:

~~~bash
python src/run_experiment.py   --benchmark data/benchmarks/hestc_climate_silver_terms.csv   --corpus data/HESTC10K_master.csv   --out-dir results/silver_nllb
~~~

For publication-grade sentence evaluation, use the completed human benchmark and set the source column to `english_sentence`.

## Reporting rule

The paper should clearly distinguish:

- silver/provisional terminology results;
- human-reference sentence results;
- HESTC validation status;
- model version and decoding settings.

Do not present a constrained model's silver exact-match score as evidence of independent translation correctness because the constraint itself is derived from HESTC.
