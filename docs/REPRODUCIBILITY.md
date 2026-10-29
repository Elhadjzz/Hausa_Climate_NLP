# Reproducibility

## Canonical data files

- `data/HESTC10K_master.csv.gz` — compressed canonical 11,034-record corpus
- `data/HESTC10K_source_catalogue.csv` — institutional source registry
- `data/HESTC10K_review_priority.csv.gz` — expert-review queue
- `data/HESTC_10K_Full_Hausa_Candidate_Corpus.xlsx` — formatted research workbook
- `data/QA_report.json` — verified corpus QA summary

## Environment

Core assembly and QA scripts target Python 3.10+ and use the Python standard library. `pytest` is used for optional tests.

The original interactive corpus-development workflow also used:

- structured spreadsheet tooling for workbook construction and QA;
- web access to official institutional resources; and
- large-language-model assistance for provisional Hausa candidate drafting.

## Unpack the master corpus

```bash
python - <<'PY'
import gzip, shutil
with gzip.open("data/HESTC10K_master.csv.gz", "rb") as src:
    with open("data/HESTC10K_master.csv", "wb") as dst:
        shutil.copyfileobj(src, dst)
PY
```

## Run QA

```bash
python src/qa_corpus.py data/HESTC10K_master.csv --json-out build/qa.json
```

## Run tests

```bash
pytest -q
```

## Rebuild from curated staging files

The builder expects:

- a source catalogue;
- one or more curated English staging CSV files;
- optional Hausa candidate data keyed by stable HESTC ID.

Example:

```bash
python src/build_hestc10k.py   --sources data/HESTC10K_source_catalogue.csv   --raw-dir staging/   --hausa-candidates staging/hausa_candidates.csv   --out-dir build/
```

## Methodological boundary

The builder reproduces the corpus assembly and QA logic. It does not automate the intellectual decision of deciding which institutional concepts should be included, nor does it replace Hausa linguistic or environmental domain validation.

## Reproducibility principles

A reproducible HESTC workflow maintains three logical layers:

1. authoritative institutional source registry;
2. curated English concept records; and
3. Hausa candidate/validation records keyed by stable HESTC ID.

This separation permits corrections to terminology and validation without losing provenance.
