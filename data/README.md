# HESTC-10K data

## Canonical GitHub distribution

The complete 11,034-record corpus is stored in:

`data/corpus_parts/`

There are 24 part-level CSV files corresponding to HESTC Parts 1A–10B. Each uses the same 14-column schema.

`data/corpus_parts/MANIFEST.csv` records the exact expected count for every file.

## Build the master corpus

Run from the repository root:

```bash
python src/merge_corpus_parts.py
```

This generates:

- `data/HESTC10K_master.csv` — complete 11,034-record corpus
- `data/HESTC10K_review_priority.csv` — all records with `Needs expert coinage`
- `data/HESTC10K_merge_QA.json` — merge and integrity report

These generated files are ignored by Git because the canonical source data are the part CSVs.

## Source catalogue

`HESTC10K_source_catalogue.csv` contains the complete registry of **243 institutional resources** used during corpus curation.

## QA report

`QA_report.json` records verified release-level statistics.

## Validation warning

Every Hausa entry in the current release remains **Candidate drafted**. Do not describe the corpus as an officially standardized Hausa environmental dictionary until the validation protocol in `docs/VALIDATION_PROTOCOL.md` has been completed.

## Formatted workbook

The research workflow also maintains a formatted Excel workbook with dashboards and review sheets. The canonical GitHub data distribution is CSV-based because it is diffable, reproducible and easier to audit programmatically.
