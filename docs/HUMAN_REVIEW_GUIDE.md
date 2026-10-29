# HESTC-ClimateNLP Human Review and Adjudication Guide

## Purpose

The final 800-sentence Hausa benchmark must be based on human-reviewed references, not on automatic output.

Reviewers may use two machine outputs as aids:

1. **HESTC-preserving draft** — designed to retain the provisional HESTC terminology;
2. **NLLB baseline draft** — generated independently by `facebook/nllb-200-distilled-600M`.

Neither is a gold reference.

## Reviewer roles

### Hausa linguist

Assess:

- grammatical Hausa;
- natural word order;
- orthography and diacritics where relevant;
- semantic clarity;
- avoidance of unnecessary English carry-over;
- whether the terminology is understandable to the intended audience.

### Environmental-domain expert

Assess:

- scientific equivalence;
- climate/environmental meaning;
- correct interpretation of the HESTC definition;
- policy/legal/technical precision;
- whether the final Hausa expression could mislead a user.

## Recommended adjudication workflow

### Stage 1 — Blind linguistic assessment

Read the English sentence and both drafts.

Choose the better starting point:

- HESTC-preserving draft
- NLLB baseline draft
- Neither / rewrite

Do not accept a draft solely because it contains the glossary candidate.

### Stage 2 — Terminology check

Compare the target concept with:

- English preferred term;
- HESTC concise definition;
- provisional Hausa candidate;
- institutional source.

The reviewer may keep, revise or replace the candidate.

### Stage 3 — Domain review

The domain reviewer confirms that the revised Hausa sentence preserves the scientific or policy meaning.

### Stage 4 — Final reference

Populate `final_hausa_reference` only after both reviews.

Use `Validated` only when:

- the Hausa sentence is linguistically acceptable;
- the environmental meaning is correct;
- terminology is adjudicated; and
- the final reference is suitable for benchmark evaluation.

## Recommended decisions

For linguistic and domain review:

- Accept
- Minor revision
- Major revision
- Reject
- Needs consultation

For terminology preservation:

- Yes
- Partly
- No

## Inter-annotator agreement

For publication, independently double-review at least **20% of the held-out test set**.

With a 200-sentence test set, this means at least **40 sentences** should receive independent decisions from two reviewers before adjudication.

Report agreement for categorical decisions using **Cohen's kappa** where two reviewers are used. For more than two reviewers, consider Fleiss' kappa or Krippendorff's alpha.

## Publication-quality reference set

Only rows with:

`final_validation_status = Validated`

should be used for final human-reference BLEU/chrF reporting.

The provisional HESTC candidate and both machine drafts should remain in the audit dataset, but they must not be used as substitute gold references.

## Data split

Current benchmark design:

- Train: 480 sentences
- Development: 120 sentences
- Held-out test: 200 sentences
- 80 sentences from each of 10 HESTC domains

The held-out test set should remain untouched during system development.
