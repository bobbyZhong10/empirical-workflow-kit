# Robustness Checklists and Evidence Matrix

Derive checks from the identification strategy, not from attractive results.
Select applicable checks from the design and universal blocks; state the
threat and decision each addresses before adding computation. Do not vote checks up
or down or report a robustness pass rate: checks address different threats and
cannot be traded off against each other.

## Evidence matrix

Create one row for every required, run, omitted, or exploratory check. This is
the internal robustness record used at Checkpoint C. Select reader-relevant
diagnostics for the paper; do not copy the whole matrix into table notes.

| Check / target | Assumption or error | Prospective/exploratory rule and why it fits | Execution result and artifact | Interpretation: claim change and what is not excluded | Severity / disposition |
|---|---|---|---|---|---|
| Placebo date | Differential pre-treatment change | State statistic, reference distribution, threshold and timing rationale | Estimate, interval, sample, output | Timing evidence; does not rule out coincident shocks | Retain, narrow, backtrack, or pause |

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
4. Interpretation matched to the defended identification argument. Adjustment
   or fixed effects alone do not establish causality; without that argument,
   report the conditional association. See the selected pack for assumptions.

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

## Execution is not interpretation

For each important diagnostic, review the assumption/error, the rule and its
appropriateness for this design, how the result changes the claim, and what it
cannot exclude. Record execution success separately from that substantive review.
A wrong decision rule must be corrected transparently, retaining its prior result
and timing; it is not evidence that the design necessarily failed.

- Non-significance does not establish no effect. Use the interval and an
  economically meaningful bound for an absence/equivalence claim; state the
  relevant test, assumptions, and decision. An MDE describes detectability under
  its design assumptions, not an observed-effect bound. If an MDE does not enter
  the decision, omit it from the decision table rather than decorate that table.
- A sensitivity breakdown value reports where a particular interval or conclusion
  changes under the specified deviations. It neither estimates the actual
  deviation nor separates causal validity from invalidity or effect from no effect.
- Many correlated rows are not many independent policy experiments. Distinguish
  observations, clusters, assignment units, and independent policy shocks; use
  inference appropriate to the source of variation and acknowledge its limits.

## Dependence between pieces of evidence

In each diagnostic interpretation, state what changes relative to the main
analysis and which inputs or counterfactual it shares. Reparameterizations,
identity transformations, and estimates sharing the same identifying
counterfactual are not independent corroboration of that assumption. Own-platform
DiD and a platform-gap DDD can answer different questions while both relying on
the same cross-year counterfactual. City-week covariance addresses dependence,
not endogenous policy timing. Overlapping placebo dates are not independent
policy experiments; interpret their reference distribution and timing assumptions.

Do not confuse dependence with identical estimands: an early-period level and a
late-minus-early change can be distinct tests, whereas a reparameterization of
the same contrast adds no new test. Preserve supported change estimates while
separately evaluating equivalence, mechanism, and causal attribution.

## Estimand crosswalk

Before interpreting or comparing results, add this crosswalk to the existing
analysis memo or Evidence card. Link to it from exhibits instead of duplicating
specifications in several records.

| Analysis/exhibit | Outcome and units | Sample | Treatment and comparison | Window | Reference period | Weights | Aggregation | Target quantity |
|---|---|---|---|---|---|---|---|---|
| Main result | | | | | | | | |
| Main figure | | | | | | | | |
| Dynamics | | | | | | | | |
| Sensitivity | | | | | | | | |
| Magnitude conversion | | | | | | | | |

Omit inapplicable rows with a reason. Differences may answer different questions;
explain which element differs and what comparison or inference is no longer
valid. A relative gap is not one group's absolute change. A sensitivity analysis
for a related dynamic or aggregated target cannot validate the main target.
Conversions retain denominators, units, weighting, and conditioning assumptions.
