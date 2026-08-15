# Robustness Checklists

The checklist is derived from the identification strategy, not chosen by taste.
Run the design specific block, then the universal block. Report every check that
was run, with coefficients and standard errors, including the ones that failed.

## Reporting rules

- A check that failed is reported with an interpretation of what it implies. A
  robustness section in which everything passes is not credible.
- Report the robustness pass rate as a number at Checkpoint C.
- Each check states what it would take for the check to overturn the main
  finding.

## DID, not staggered

1. Event study with leads and lags, normalized at the period before treatment.
2. Pre trend sensitivity, reporting the size of violation that would overturn
   the result.
3. Placebo treatment dates in the pre period.
4. Alternative comparison groups.
5. Alternative event windows.
6. Dropping the treated group with the largest weight, one at a time for the
   largest few.

## DID, staggered

Everything above, plus:

7. The main estimate from at least two heterogeneity robust estimators that use
   different comparison groups.
8. A weight diagnostic: Goodman Bacon decomposition or a negative weight check.
9. Cohort specific estimates, shown rather than only averaged.
10. A not yet treated versus never treated comparison, since these can differ
    substantially.

## DDD

Everything from the DID block, plus:

11. Each underlying double difference reported separately.
12. A placebo third dimension.

## RDD

1. Bandwidth sensitivity across a range around the data driven choice.
2. Polynomial order sensitivity, local rather than global.
3. Density test for manipulation of the running variable.
4. Continuity of predetermined covariates at the cutoff.
5. Placebo cutoffs away from the true threshold.
6. Donut specification excluding observations immediately at the threshold.

## IV

1. First stage strength with the appropriate effective F statistic.
2. Reduced form reported alongside.
3. Ordinary least squares reported alongside, with the direction of the
   difference discussed.
4. Weak instrument robust confidence sets.
5. Overidentification test where the model is overidentified, with the caveat
   that it tests the joint null and not exclusion by itself.
6. An explicit written treatment of the most plausible violation of exclusion.

## Fixed effects and selection on observables

1. Coefficient stability across nested control sets.
2. A bounding exercise for selection on unobservables relative to observables.
3. Alternative fixed effect structures.
4. Explicitly non causal language in the interpretation.

## Universal

1. Winsorizing or trimming the outcome and the continuous treatment.
2. Alternative measures of the dependent variable.
3. Alternative functional forms of the treatment, all reported.
4. Alternative time windows and, for panels, alternative aggregation levels.
5. Alternative clustering levels, including a more conservative level.
6. Excluding influential units or periods, identified rather than guessed.
7. Sample restrictions that address the most plausible confounder.
8. Multiple hypothesis adjustment when the paper tests many outcomes.

## Structural

Use the Checkpoint C structural variant in `stages/stage6b-structural.md`. The
robustness object there is fit on untargeted moments, sensitivity of parameters
to moments, and re estimation under relaxed tractability assumptions.
