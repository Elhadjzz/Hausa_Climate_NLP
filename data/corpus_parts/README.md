# Canonical HESTC corpus parts

This directory contains the canonical GitHub distribution of the **11,034-record HESTC-10K corpus**.

Each `Part*_Terms.csv` file is extracted from the corresponding validated workbook sheet structure and uses the same 14-column schema.

The files intentionally remain separated by corpus part so that:

- each source artifact stays small and human-auditable;
- researchers can work with individual environmental domains;
- GitHub diffs remain manageable; and
- the complete master corpus can be reconstructed deterministically.

## Reconstruct the master corpus

From the repository root:

```bash
python src/merge_corpus_parts.py
```

This creates:

- `data/HESTC10K_master.csv`
- `data/HESTC10K_review_priority.csv`
- `data/HESTC10K_merge_QA.json`

The merger verifies all expected part counts, **11,034 total records**, unique IDs, zero duplicate preferred English labels, complete definitions, valid source URLs, and populated Hausa candidates.

See `MANIFEST.csv` for the exact part counts.

> Hausa forms in this release remain **Candidate drafted** until linguistic and environmental-domain expert validation is completed.
