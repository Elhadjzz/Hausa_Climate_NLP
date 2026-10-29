# HESTC human terminology validation pilot

Before scaling the NLLB+HESTC experiment, HESTC Hausa candidates should be reviewed by humans. The smoke experiment demonstrated why: exact glossary inclusion can be enforced computationally, but the provisional candidate itself may still have unnatural word order or an imprecise technical meaning.

## Build the 200-term pilot

~~~bash
python src/merge_corpus_parts.py
python src/build_validation_pilot.py \
  --corpus data/HESTC10K_master.csv \
  --out data/validation/hestc_validation_pilot_200.csv
~~~

Default design:

- 200 terms total
- 20 terms from each of the 10 HESTC domains
- approximately half core candidates and half difficult candidates per domain
- source institution, URL and definition included for reviewer context

## Review stages

### 1. Hausa linguistic review

Record whether the candidate is natural, grammatically acceptable, orthographically correct and understandable.

Suggested decisions: `Accept`, `Minor revision`, `Major revision`, `Reject`, `Needs consultation`.

### 2. Environmental domain review

Confirm that the Hausa form preserves the scientific or policy meaning of the English concept and definition.

### 3. Harmonization

Resolve terminology-family consistency across domains.

### 4. Final status

Only after both reviews should a term be promoted to `Validated`.

## Publication use

Use validated terms to construct the human sentence benchmark. Do not use provisional candidates as gold-standard sentence references.
