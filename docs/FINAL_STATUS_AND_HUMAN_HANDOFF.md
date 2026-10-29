# Final Project Status and Human Validation Handoff

## What is complete

The following stages are fully implemented and reproducible:

- HESTC-10K corpus assembly and QA
- 11,034-concept master corpus reconstruction
- 500-term silver ClimateNLP benchmark
- 200-term terminology validation pilot
- 800-sentence balanced human-reference benchmark
- 480/120/200 train/dev/test split
- 800 terminology-preserving Hausa machine pretranslations
- NLLB English→Hausa baseline implementation
- HESTC lexical-constrained NLLB implementation
- machine-draft proxy evaluation
- terminology accuracy evaluation
- reviewer workbook and four 200-sentence reviewer batches
- final publication evaluator
- paired bootstrap chrF comparison
- per-domain result reporting

## What cannot be automated honestly

The final Hausa references must be approved by human reviewers.

A language model, NLLB system, rule-based pretranslation, or HESTC candidate generator cannot legitimately change a record to human-validated status.

## Human handoff

For every held-out test sentence:

1. Hausa linguist reviews the machine draft.
2. Linguist records a decision and revision.
3. Environmental/domain expert checks scientific equivalence.
4. Disagreements are adjudicated.
5. Agreed Hausa sentence is entered as the final Hausa reference.
6. Final validation status is set to `Validated`.

Recommended minimum:

- all 200 test sentences: one linguistic + one domain review;
- at least 40 test sentences: independent double review for agreement analysis.

## Final command after review

~~~bash
python src/final_publication_evaluation.py \
  --baseline results/sentence_nllb_hestc/baseline.csv \
  --grounded results/sentence_nllb_hestc/hestc_constrained.csv \
  --review reviewed/HESTC_Reviewer_Adjudicated_800.csv \
  --out results/final_publication_metrics.json
~~~

The script intentionally exits instead of generating misleading results if no validated human references exist.

## Final outputs produced by the evaluator

- baseline BLEU
- HESTC-grounded BLEU
- BLEU delta
- baseline chrF
- HESTC-grounded chrF
- chrF delta
- baseline validated terminology accuracy
- HESTC-grounded validated terminology accuracy
- terminology wins/losses/ties
- per-domain BLEU and chrF
- paired-bootstrap 95% confidence interval for chrF delta

## Scientific completion criterion

The research is publication-ready only when:

- the test references are human validated;
- the final evaluator completes on those validated references; and
- terminology gains are interpreted together with sentence-level quality.

The project must not claim superiority from forced terminology inclusion alone.
