# Hausa_Climate_NLP

**Hausa_Climate_NLP** is the reproducibility repository for the **Hausa Environmental Scientific Terminology Corpus (HESTC-10K)** and its use in climate-change and environmental natural language processing.

## Corpus at a glance

- **11,034** unique preferred English environmental concepts
- **10** environmental and climate-related domains
- **24** canonical part-level CSV files
- **14 fields** per terminology record
- **243** curated institutional source-resource records
- Complete row-level source traceability
- Hausa candidate terminology for all 11,034 concepts
- All Hausa forms currently remain **Candidate drafted**
- **1,965** concepts are marked `Needs expert coinage`

> **Important:** HESTC-10K is not yet an officially standardized Hausa environmental dictionary. Hausa forms are provisional terminology candidates until they pass Hausa linguistic review, domain-expert review, cross-domain harmonization, and final validation.

## Ten HESTC domains

| # | Domain | Concepts |
|---|---|---:|
| 1 | Climate, Meteorology & Atmospheric Science | 1,067 |
| 2 | Water, Hydrology & Sanitation | 1,121 |
| 3 | Land, Soil, Drought & Desertification | 1,200 |
| 4 | Biodiversity, Ecology & Conservation | 1,180 |
| 5 | Forestry, Agriculture & Natural Resources | 1,136 |
| 6 | Pollution, Chemicals, Waste & Circular Economy | 1,055 |
| 7 | Energy, Emissions & Environmental Technology | 1,010 |
| 8 | Disaster Risk, Adaptation & Resilience | 976 |
| 9 | Environmental Policy, Law, Governance & Finance | 1,093 |
| 10 | Environmental Monitoring, GIS, Remote Sensing & Scientific Methods | 1,196 |
| | **Total** | **11,034** |

## Repository structure

```text
Hausa_Climate_NLP/
├── README.md
├── requirements.txt
├── LICENSE_NOTE.md
├── data/
│   ├── corpus_parts/
│   │   ├── Part1A_Terms.csv ... Part10B_Terms.csv
│   │   ├── MANIFEST.csv
│   │   └── README.md
│   ├── HESTC10K_source_catalogue.csv
│   ├── QA_report.json
│   └── README.md
├── docs/
│   ├── CORPUS_METHODOLOGY.md
│   ├── SOURCES.md
│   ├── VALIDATION_PROTOCOL.md
│   └── REPRODUCIBILITY.md
├── src/
│   ├── build_hestc10k.py
│   ├── merge_corpus_parts.py
│   ├── qa_corpus.py
│   ├── hausa_candidate_engine.py
│   └── hestc_schema.py
├── examples/
│   └── climate_terminology_grounding.py
└── tests/
    └── test_corpus_qa.py
```

## Corpus schema

Every record has 14 fields:

1. ID
2. English term
3. synonym/abbreviation
4. terminology type
5. domain
6. subdomain
7. concise definition
8. source institution
9. source identifier/link
10. Hausa candidate
11. translation strategy
12. preferred Hausa
13. validation status
14. reviewer notes

## Reconstruct the complete master corpus

The GitHub distribution stores the canonical corpus as 24 part-level CSV files. Reconstruct the full corpus with:

```bash
python src/merge_corpus_parts.py
```

The command creates:

- `data/HESTC10K_master.csv`
- `data/HESTC10K_review_priority.csv`
- `data/HESTC10K_merge_QA.json`

The merge process checks the expected count of every part and verifies the complete **11,034-record** corpus.

## Run corpus QA

After merging:

```bash
python src/qa_corpus.py data/HESTC10K_master.csv
```

Expected core checks:

- total records: 11,034
- duplicate IDs: 0
- duplicate preferred English labels: 0
- missing concise definitions: 0
- missing source URLs: 0
- missing Hausa candidates: 0
- validation status: `Candidate drafted` for the current release

## Run tests

```bash
pip install -r requirements.txt
pytest -q
```

## Example: climate-NLP terminology grounding

The example can use either the generated master CSV or an individual part.

```bash
python src/merge_corpus_parts.py

python examples/climate_terminology_grounding.py \
  --corpus data/HESTC10K_master.csv \
  --text "Climate adaptation and early warning systems reduce disaster risk."
```

The script detects HESTC concepts and returns available Hausa candidate terminology, definitions, domain metadata, source links and validation status.

## Method used to develop HESTC

HESTC-10K follows an **institution-first terminology-engineering workflow**:

1. define the environmental scope, domains and controlled schema;
2. identify authoritative institutional resources;
3. curate reusable scientific, technical, policy and governance concepts;
4. prepare concise normalized definitions;
5. classify each concept by domain, subdomain and terminology type;
6. preserve institutional provenance and source URL;
7. normalize and deduplicate preferred English labels corpus-wide;
8. assign stable HESTC identifiers;
9. draft provisional Hausa terminology using controlled translation strategies;
10. flag scientifically difficult concepts for expert coinage;
11. perform corpus-wide QA; and
12. keep candidate drafting distinct from human validation.

Full methodology: [docs/CORPUS_METHODOLOGY.md](docs/CORPUS_METHODOLOGY.md)

## Authoritative source families

HESTC uses resources from organizations including WMO, IPCC, UNFCCC, FAO, WHO, UNESCO, UNEP, UNCCD, CBD, IUCN, CITES, UNDRR, IEA, IRENA, World Bank, Green Climate Fund, NASA, USGS, NIST and OGC.

The complete registry is [data/HESTC10K_source_catalogue.csv](data/HESTC10K_source_catalogue.csv).

## Hausa candidate strategies

| Translation strategy | Concepts |
|---|---:|
| Existing Hausa technical term | 197 |
| Direct equivalence | 1,294 |
| Descriptive translation | 832 |
| Hybrid translation | 6,291 |
| Borrowing/transliteration | 455 |
| Needs expert coinage | 1,965 |
| **Total** | **11,034** |

## Climate-NLP research uses

HESTC can support:

- terminology-aware English–Hausa machine translation;
- climate concept recognition;
- bilingual climate-information retrieval;
- retrieval-augmented generation and question answering;
- climate-policy classification;
- agricultural and early-warning communication;
- terminology consistency checking;
- climate chatbots and mobile advisory systems.

## Phase 2 — HESTC-ClimateNLP experiment

The repository now includes an experimental English→Hausa machine-translation framework comparing:

- **B1:** unconstrained NLLB baseline;
- **H1:** NLLB with HESTC lexical constraints during beam-search decoding.

The default model is `facebook/nllb-200-distilled-600M`, with `eng_Latn` as the source language and `hau_Latn` as the Hausa target language.

### Build the 500-term silver benchmark

~~~bash
python src/merge_corpus_parts.py

python src/build_climate_benchmark.py \
  --corpus data/HESTC10K_master.csv \
  --out data/benchmarks/hestc_climate_silver_terms.csv
~~~

The builder selects **50 climate/environment-relevant terms from each HESTC domain**, for 500 terms total. It excludes `Needs expert coinage` and pure borrowing/transliteration entries.

This is a **silver benchmark**: its Hausa targets are provisional HESTC candidates, not independently validated gold references.

### Install NLLB experiment dependencies

~~~bash
pip install -r requirements-experiment.txt
~~~

### Run baseline versus HESTC-constrained NLLB

~~~bash
python src/run_experiment.py \
  --benchmark data/benchmarks/hestc_climate_silver_terms.csv \
  --corpus data/HESTC10K_master.csv \
  --out-dir results/silver_nllb
~~~

The evaluator reports:

- terminology exact-match accuracy;
- lexical-constraint success rate;
- results by HESTC domain;
- results by translation strategy;
- BLEU and chrF when independent Hausa sentence references are supplied.

### Publication-grade benchmark

Use `data/benchmarks/human_sentence_benchmark_template.csv` to create a manually translated and independently reviewed climate sentence benchmark. The paper should report BLEU/chrF only from this human-reference layer.

Detailed protocol: [experiments/EXPERIMENTAL_PROTOCOL.md](experiments/EXPERIMENTAL_PROTOCOL.md)

A manual GitHub Actions workflow is also available under **Actions → NLLB + HESTC ClimateNLP experiment**. It intentionally does not run on every push because the NLLB model is large and CPU inference is relatively expensive.

## Reproducibility boundary

The repository code reconstructs the corpus assembly and QA workflow. The original corpus involved iterative source curation, human conceptual decisions, spreadsheet QA, and AI-assisted **provisional** Hausa candidate drafting. It was not produced by a single automatic scraper or one automatic translation command.

## License

A publication license has not yet been selected. Review [LICENSE_NOTE.md](LICENSE_NOTE.md) before redistributing the dataset.
