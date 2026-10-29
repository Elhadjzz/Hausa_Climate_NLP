# Hausa_Climate_NLP

**Hausa_Climate_NLP** is the reproducibility repository for the **Hausa Environmental Scientific Terminology Corpus (HESTC-10K)** and its use in climate-change and environmental natural language processing.

## Corpus at a glance

- **11,034** unique preferred English environmental concepts
- **10** environmental and climate-related domains
- **14 fields** per terminology record
- **243** curated institutional source-resource records
- **236** distinct source URLs
- Complete row-level source traceability
- Hausa candidate terminology for all 11,034 concepts
- All Hausa forms currently remain **Candidate drafted**
- Specialist entries requiring linguistic/domain coinage are isolated in the review-priority data

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
├── .gitignore
├── LICENSE_NOTE.md
├── data/
│   ├── HESTC10K_master.csv.gz
│   ├── HESTC10K_source_catalogue.csv
│   ├── HESTC10K_review_priority.csv.gz
│   ├── HESTC_10K_Full_Hausa_Candidate_Corpus.xlsx
│   ├── QA_report.json
│   └── README.md
├── docs/
│   ├── CORPUS_METHODOLOGY.md
│   ├── SOURCES.md
│   ├── VALIDATION_PROTOCOL.md
│   └── REPRODUCIBILITY.md
├── src/
│   ├── build_hestc10k.py
│   ├── qa_corpus.py
│   ├── hausa_candidate_engine.py
│   └── hestc_schema.py
├── examples/
│   └── climate_terminology_grounding.py
└── tests/
    └── test_corpus_qa.py
```

## Corpus schema

Each record contains 14 fields: ID, English term, synonym/abbreviation, terminology type, domain, subdomain, concise definition, source institution, source identifier/link, Hausa candidate, translation strategy, preferred Hausa, validation status, and reviewer notes.

## Reproducible QA

The canonical master CSV is stored compressed to keep the repository compact. First unpack it:

```bash
python - <<'PY'
import gzip, shutil
with gzip.open("data/HESTC10K_master.csv.gz", "rb") as src, open("data/HESTC10K_master.csv", "wb") as dst:
    shutil.copyfileobj(src, dst)
PY
python src/qa_corpus.py data/HESTC10K_master.csv
```

Expected core checks: 11,034 records, zero duplicate preferred English labels, zero missing definitions, zero missing source URLs, zero missing Hausa candidates, and current validation status `Candidate drafted`.

## Example climate-NLP terminology grounding

```bash
python examples/climate_terminology_grounding.py   --corpus data/HESTC10K_master.csv   --text "Climate adaptation and early warning systems reduce disaster risk."
```

The script detects HESTC concepts and returns available Hausa candidate terminology and definitions. It can serve as a terminology layer before machine translation, retrieval, question answering or LLM generation.

## Method

HESTC-10K used an **institution-first terminology-engineering workflow**: define the schema and domains; identify authoritative institutional resources; curate reusable scientific and policy concepts; prepare concise definitions; classify terms; preserve source traceability; deduplicate preferred English labels corpus-wide; assign stable HESTC IDs; draft Hausa candidates using controlled translation strategies; flag terms needing expert coinage; and run corpus-wide QA.

See [docs/CORPUS_METHODOLOGY.md](docs/CORPUS_METHODOLOGY.md).

## Sources

Major source families include WMO, IPCC, UNFCCC, FAO, WHO, UNESCO, UNEP, UNCCD, CBD, IUCN, CITES, UNDRR, IEA, IRENA, World Bank, Green Climate Fund, NASA, USGS, NIST and OGC.

## Climate-NLP research uses

HESTC can support terminology-aware English–Hausa machine translation, climate concept recognition, bilingual climate-information retrieval, RAG and question answering, climate-policy classification, agricultural and early-warning communication, terminology consistency checking, and climate chatbot/mobile applications.

## Reproducibility note

The code reconstructs the corpus-building and QA workflow used during HESTC development. The original project involved iterative institutional source curation, manual conceptual decisions, spreadsheet QA, and AI-assisted candidate drafting. It was **not** generated by a single web scraper or one automatic translation script.

## License

A publication license has not yet been selected. See `LICENSE_NOTE.md` before redistributing the dataset.
