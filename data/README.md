# HESTC data files

- `HESTC10K_master.csv.gz` — compressed canonical 11,034-record corpus.
- `HESTC10K_source_catalogue.csv` — full institutional source registry.
- `HESTC10K_review_priority.csv.gz` — compressed expert-review queue.
- `HESTC_10K_Full_Hausa_Candidate_Corpus.xlsx` — formatted research workbook.
- `QA_report.json` — corpus QA summary.

To unpack the master corpus:

```bash
python - <<'PY'
import gzip, shutil
with gzip.open("data/HESTC10K_master.csv.gz", "rb") as src, open("data/HESTC10K_master.csv", "wb") as dst:
    shutil.copyfileobj(src, dst)
PY
```

All Hausa entries in this release are provisional candidates and should not be described as officially validated terminology.
