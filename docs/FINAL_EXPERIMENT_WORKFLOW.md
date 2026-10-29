# Final HESTC-ClimateNLP Experimental Workflow

## End-to-end research pipeline

The project is now structured as the following reproducible sequence:

1. **HESTC-10K source corpus**
   - 11,034 English environmental concepts
   - institutional source traceability
   - provisional Hausa candidates
   - candidate validation status kept separate from scientific-source authority

2. **Corpus QA**
   - duplicate checks
   - required-field checks
   - source URL checks
   - regression tests

3. **Silver terminology benchmark**
   - 500 climate/environment terms
   - 50 per HESTC domain
   - engineering diagnostics only

4. **Human-reference sentence benchmark**
   - 800 English sentences
   - 80 per domain
   - 480 train / 120 dev / 200 held-out test

5. **Reviewer-assistance layer**
   - terminology-preserving Hausa machine pretranslation
   - NLLB Hausa draft
   - both explicitly labelled non-gold

6. **Human validation**
   - Hausa linguistic review
   - environmental-domain review
   - final Hausa reference
   - final validation status

7. **Held-out MT comparison**
   - System B1: NLLB baseline
   - System H1: NLLB + one designated HESTC lexical constraint

8. **Engineering diagnostics**
   - provisional terminology exact-match accuracy
   - lexical-constraint success
   - machine-draft proxy BLEU/chrF
   - these are NOT human-reference publication metrics

9. **Publication-grade evaluation**
   - only rows marked `Validated`
   - final human Hausa references
   - BLEU
   - chrF
   - terminology accuracy
   - per-domain results
   - paired bootstrap confidence interval for chrF delta

## Final evaluator

~~~bash
python src/final_publication_evaluation.py \
  --baseline results/sentence_nllb_hestc/baseline.csv \
  --grounded results/sentence_nllb_hestc/hestc_constrained.csv \
  --review reviewed/HESTC_Reviewer_Adjudicated_800.csv \
  --out results/final_publication_metrics.json
~~~

The evaluator exits without scoring if there are no validated human references.

## Reporting requirements

The manuscript must distinguish these result types:

### A. Corpus-construction results

Safe to report now:

- 11,034 HESTC concepts
- ten environmental domains
- domain distribution
- source-resource statistics
- translation-strategy distribution
- QA results

### B. Engineering results

Safe to report only as technical diagnostics:

- whether NLLB independently reproduces provisional HESTC candidates
- whether constrained decoding can insert a designated HESTC term
- machine-draft proxy BLEU/chrF

Always label these **provisional**, **silver**, or **engineering-only**.

### C. Publication-grade translation results

Report only after human adjudication:

- BLEU against final Hausa references
- chrF against final Hausa references
- validated terminology accuracy
- adequacy/fluency ratings
- reviewer agreement
- domain-level performance

## Human-review minimum

For the 200 held-out test sentences:

- all 200 should receive linguistic and domain review;
- at least 40 test sentences should be independently double-reviewed;
- disagreements should be adjudicated;
- reviewer roles should be recorded without exposing unnecessary personal information.

## Statistical comparison

The final evaluator reports a paired bootstrap confidence interval for the chrF difference.

Interpretation:

- CI entirely above 0: evidence that HESTC grounding improves chrF on the validated test set;
- CI crossing 0: no clear chrF improvement at the chosen confidence level;
- terminology accuracy should still be interpreted alongside adequacy/fluency because forced terminology can harm naturalness.

## Final scientific boundary

HESTC grounding is considered successful only if it improves terminology preservation **without unacceptable degradation in sentence quality**.

A constrained system should not be declared superior merely because it reproduces the glossary term.
