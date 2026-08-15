# Robustness Checklists and Evidence Matrix

Derive checks from the identification strategy, not from attractive results.
Run the applicable design block and the universal block. Do not vote checks up
or down or report a robustness pass rate: checks address different threats and
cannot be traded off against each other.

## Evidence matrix

Create one row for every required, run, omitted, or exploratory check. This is
the robustness record used at Checkpoint C and in the paper's table notes.

| Check | Identifying threat | Status: pre-committed or exploratory | Result | Implication | Severity | Disposition |
|---|---|---|---|---|---|---|
| Example: placebo date | Differential pre-treatment trend | Pre-committed | Estimate, uncertainty, output link | Supports or challenges timing assumption | Low / medium / high | Retain, qualify, backtrack, or pause |

"Result" reports the estimate, uncertainty, sample, and output path where
relevant, including null or failed checks. "Implication" says what the check
does and does not establish. A high-severity failure triggers the protocol's
Mandatory pause and backtracking rule; no number of low-severity successes can
offset it. An omitted required check needs a recorded reason and limitation.

## DID, single adoption date

1. Event study with leads/lags, normalized just before treatment.
2. Pre-trend sensitivity that states the violation needed to overturn the result.
3. Placebo treatment dates in the pre-period.
4. Alternative comparison groups and event windows.
5. Leave-one-important-treated-group-out estimates where assignment weights make that relevant.
6. Tree-0 timing, anticipation, treatment-exit, spillover, entry/exit, and aggregation checks.

## DID, staggered adoption

Complete the single-date block, plus:

7. Main estimates from heterogeneity-robust estimators using appropriately stated comparison groups.
8. Goodman-Bacon decomposition or a direct negative-weight diagnostic.
9. Cohort-specific estimates, not only an average.
10. Never-treated and not-yet-treated comparisons where both exist.
11. An estimator compatible with treatment exit, intensity, or repeat treatment when those occur.

TWFE is reference-only under staggered timing and must never displace the
heterogeneity-robust main result.

## DDD

Complete the relevant DID block, plus:

12. Each underlying double difference reported separately.
13. A placebo third dimension.

## RDD

1. Bandwidth sensitivity around the data-driven choice.
2. Local polynomial-order sensitivity.
3. Density test for running-variable manipulation.
4. Predetermined-covariate continuity.
5. Placebo cutoffs.
6. Donut specification when observations may heap at the threshold.

## IV

1. Appropriate first-stage strength statistic.
2. Reduced form beside the second stage.
3. OLS beside the second stage, with direction discussed.
4. Weak-instrument-robust confidence sets.
5. Overidentification test when applicable, with its limited interpretation.
6. Written treatment of the most plausible exclusion violation.

## Fixed effects and selection on observables

1. Coefficient stability across nested controls.
2. Bounding exercise for selection on unobservables relative to observables.
3. Alternative fixed-effect structures.
4. Interpretation that remains explicitly non-causal.

## Universal

1. Outcome and continuous-treatment trimming or winsorizing, when justified.
2. Alternative outcome measures.
3. Alternative treatment functional forms.
4. Alternative time windows and panel aggregation levels consistent with assignment.
5. Conservative alternative clustering levels.
6. Exclusion of identified influential units or periods.
7. Sample restrictions addressing the most plausible confounder without conditioning on post-treatment variables.
8. Multiple-hypothesis adjustment for families of outcomes.

## Structural

Use the Stage 6b parameter-identification table and structural evidence matrix:
targeted and untargeted fit, sensitivity to moments and tractability
assumptions, convergence from multiple starts, and counterfactual uncertainty.
