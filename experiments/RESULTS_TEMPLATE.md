# Results Template for the HESTC-ClimateNLP Paper

## Corpus results

| Measure | Value |
|---|---:|
| HESTC concepts | 11,034 |
| Environmental domains | 10 |
| Institutional source-resource records | 243 |
| Unique source URLs | 236 |
| Hausa candidate coverage | 11,034 / 11,034 |
| Duplicate preferred English labels | 0 |
| Needs expert coinage | 1,965 |

## Benchmark design

| Split | Sentences |
|---|---:|
| Train | 480 |
| Development | 120 |
| Held-out test | 200 |
| **Total** | **800** |

Each of the ten HESTC domains contributes 80 sentences.

## Engineering-only model diagnostics

Report these separately from human-reference results.

| Metric | NLLB baseline | NLLB + HESTC | Delta |
|---|---:|---:|---:|
| Provisional terminology accuracy | TBD | TBD | TBD |
| Constraint success | N/A | TBD | N/A |
| Machine-draft proxy BLEU | TBD | TBD | TBD |
| Machine-draft proxy chrF | TBD | TBD | TBD |

**Mandatory note:** machine-draft BLEU/chrF are diagnostics, not publication-grade translation quality.

## Publication-grade held-out results

Populate only after the Hausa references are independently reviewed and marked `Validated`.

| Metric | NLLB baseline | NLLB + HESTC | Delta |
|---|---:|---:|---:|
| BLEU | TBD | TBD | TBD |
| chrF | TBD | TBD | TBD |
| Validated terminology accuracy | TBD | TBD | TBD |
| Adequacy score | TBD | TBD | TBD |
| Fluency score | TBD | TBD | TBD |

## Statistical comparison

Report:

- paired bootstrap 95% confidence interval for chrF delta;
- HESTC-grounded terminology wins;
- baseline terminology wins;
- ties;
- results by HESTC domain.

## Human review

For the 200 held-out test sentences report:

- number linguistically reviewed;
- number domain reviewed;
- number validated;
- number requiring revision;
- double-reviewed subset size;
- Cohen's kappa or another appropriate agreement statistic.

## Interpretation rule

Do not claim the grounded model is better solely because it contains more glossary terms.

A successful result should show:

1. improved validated terminology preservation; and
2. no unacceptable degradation in sentence-level adequacy or fluency.
