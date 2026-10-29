# HESTC-10K Corpus Methodology

## 1. Objective

The Hausa Environmental Scientific Terminology Corpus (HESTC-10K) was developed as a structured English–Hausa environmental terminology resource for climate-change communication, environmental education, scientific information access and low-resource natural language processing.

The corpus was not constructed through unrestricted web scraping or by directly translating arbitrary English vocabulary. It follows an **institution-first terminology-engineering workflow** in which environmental concepts were curated from authoritative scientific and policy institutions, normalized, classified, deduplicated, linked to their sources, assigned stable identifiers, and only then supplied with provisional Hausa terminology.

## 2. Corpus scope

The corpus contains **11,034 unique preferred English concepts** across ten domains:

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

The multi-domain structure reflects the interdisciplinary nature of climate change. Climate risks and responses depend on atmospheric science, water, land, biodiversity, agriculture, energy, pollution, disasters, governance, finance and Earth observation.

## 3. Corpus schema

Every record has fourteen fields:

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

This schema separates:

- the authority and meaning of the English-source concept;
- the method used to create the Hausa candidate; and
- the human validation status of that Hausa form.

This distinction is essential because an AI-assisted translation candidate must not be treated as standardized terminology merely because it is fluent.

## 4. Controlled terminology types

Each concept is assigned to one of seven terminology types:

- Scientific
- Technical
- Policy
- Legal/governance
- Operational
- Economic/finance
- Social/development

## 5. Authoritative source selection

Source selection followed an institution-first policy. Priority was given to:

- United Nations agencies;
- treaty and convention secretariats;
- international scientific organizations;
- intergovernmental technical bodies;
- standards-oriented organizations;
- specialist government scientific agencies; and
- official monitoring, indicator and technical guidance resources.

Commercial glossary websites, unattributed term lists and Wikipedia were not treated as primary terminology authorities.

The source catalogue records the institution, resource title, scope used in HESTC, URL and a curation note. At term level, the responsible source institution and source URL are retained.

## 6. Concept extraction and curation

Candidate terminology was curated from:

- official glossaries;
- technical manuals;
- assessment reports;
- scientific guidance;
- monitoring manuals;
- indicator metadata;
- convention and treaty terminology;
- policy frameworks;
- environmental standards resources; and
- official scientific-method documentation.

Extraction was concept-oriented rather than word-frequency-oriented. A word was included when it represented a reusable scientific, technical, policy, legal, operational, economic or development concept relevant to the environment.

Where appropriate, official acronyms and synonyms were retained in the synonym/abbreviation field rather than counted as separate preferred concepts.

## 7. Definition preparation

Institutional meanings were converted into concise corpus definitions.

Definitions were normalized for terminology lookup, corpus processing and later translation. Long institutional passages were not reproduced wholesale. The objective was to preserve the scientific or policy meaning while providing a compact and consistent definition.

## 8. Domain and subdomain classification

Every concept was assigned to one top-level domain and a more specific subdomain.

Examples include:

- atmospheric thermodynamics;
- cloud physics;
- numerical weather prediction;
- hydrometry;
- groundwater;
- wastewater treatment;
- soil morphology;
- land degradation neutrality;
- conservation genetics;
- biosafety;
- integrated pest management;
- chemical safety;
- circular economy;
- renewable energy;
- early warning;
- environmental law;
- climate finance;
- GIS;
- remote sensing;
- geostatistics; and
- scientific methods.

Classification is concept-based rather than institution-based. A concept published by FAO, UNEP or the World Bank is classified according to its scientific meaning.

## 9. Terminology normalization

Preferred English labels were normalized by:

- trimming leading and trailing whitespace;
- collapsing repeated whitespace; and
- using case-insensitive comparison for duplicate detection.

The original preferred label is retained for display.

## 10. Corpus-wide deduplication

Deduplication was conducted across the complete corpus, not only within individual batches or institutions.

A normalized preferred English label already present in the corpus was excluded from later batches. Synonyms and abbreviations were preserved as metadata rather than introduced as new preferred concepts.

This procedure prevents common cross-domain concepts such as *monitoring*, *climate risk*, *environmental flow*, *restoration*, *ecosystem service* and *resource efficiency* from being counted repeatedly.

The completed master corpus contains **zero duplicate preferred English labels**.

## 11. Stable identifiers

Accepted concepts were assigned stable domain-specific HESTC identifiers, for example:

- `HESTC-CMA-0001`
- `HESTC-WHS-0001`
- `HESTC-LSDD-0001`
- `HESTC-BEC-0001`
- `HESTC-EPLGF-0001`

Stable IDs allow terminology, translation and validation fields to be updated without changing the identity of the source concept.

## 12. Source traceability

Every accepted concept is required to contain both:

- a source institution; and
- an institutional source URL or resource identifier.

The separate source catalogue contains:

- Source ID
- Institution
- Resource
- Scope used in HESTC
- URL
- Curation note

No source-less concept is intended for inclusion in the canonical English-source corpus.

## 13. Hausa candidate drafting

Hausa candidate drafting was performed only after the English-source corpus structure had stabilized.

The controlled strategies are:

### Existing Hausa technical term
Used when a well-established Hausa form was available.

### Direct equivalence
Used when an accurate and natural Hausa equivalent could be expressed directly.

### Descriptive translation
Used when a concise explanatory Hausa phrase better preserved the scientific meaning than a literal lexical equivalent.

### Borrowing/transliteration
Used for scientific names, formal labels, chemical terminology, acronyms or highly specialized terms where international borrowing was preferable.

### Hybrid translation
Used when a Hausa descriptive frame was combined with a retained international scientific element or abbreviation.

### Needs expert coinage
Used when generating a fluent-looking translation would risk scientific inaccuracy and a Hausa linguist or domain specialist should create or approve the technical expression.

### Deferred — English-source curation phase
Used before systematic Hausa candidate drafting began.

## 14. AI assistance and validation boundary

Large-language-model assistance was used to support provisional Hausa candidate drafting and terminology harmonization.

AI output was treated as candidate terminology only.

The current corpus uses the validation status:

`Candidate drafted`

No form is promoted to `Validated` solely because it was generated by a model.

## 15. Recommended human validation workflow

The recommended sequence is:

1. priority review of `Needs expert coinage`;
2. Hausa linguistic/terminological review;
3. environmental domain-expert review;
4. cross-domain terminology-family harmonization;
5. approval of the preferred Hausa form;
6. change validation status to `Validated`; and
7. record reviewer rationale.

## 16. Quality assurance

The completed corpus was checked for:

- duplicate preferred English labels;
- duplicate or missing IDs;
- missing definitions;
- missing source institutions;
- missing source URLs;
- blank Hausa candidate fields;
- blank translation strategies;
- blank preferred-Hausa fields;
- inconsistent validation statuses;
- field-order errors; and
- spreadsheet formula errors.

The current release contains:

- 11,034 records;
- zero duplicate preferred English labels;
- zero missing concise definitions;
- zero missing source links;
- zero missing Hausa candidate fields; and
- all 11,034 rows marked `Candidate drafted`.

## 17. Translation-strategy distribution

| Strategy | Concepts |
|---|---:|
| Existing Hausa technical term | 197 |
| Direct equivalence | 1,294 |
| Descriptive translation | 832 |
| Hybrid translation | 6,291 |
| Borrowing/transliteration | 455 |
| Needs expert coinage | 1,965 |
| **Total** | **11,034** |

The high proportion of hybrid terminology reflects the challenge of communicating specialized scientific concepts in a low-resource technical vocabulary while preserving internationally recognizable scientific forms.

## 18. Reproducibility

The repository provides code for:

- source-registry validation;
- controlled schema validation;
- normalization;
- case-insensitive deduplication;
- source joining;
- stable ID assignment;
- candidate merging;
- QA reporting;
- expert-review queue generation; and
- terminology grounding for climate-NLP applications.

The code reproduces the assembly and QA logic, but it does not pretend that scientific concept selection can be reduced to a fully automatic scraper. Human corpus curation remains part of the methodology.

## 19. Ethical and scholarly considerations

HESTC contains terminology rather than human-subject data.

Institutional source attribution is retained at row level. Definitions are concise normalized summaries rather than wholesale reproduction of source material.

The distinction between provisional candidate terminology and human-validated terminology is maintained throughout the repository to avoid presenting generated Hausa forms as official standards before expert review.
