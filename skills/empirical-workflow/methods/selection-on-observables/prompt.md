# Selection-on-observables analysis

Adapted from the `causal-design` unconfoundedness branch in
`ericluo04/claude-academic-workflow` at commit
`8958cc246e65cdf7c36604f397a1c1719b7e2c14`; see `THIRD_PARTY_NOTICES.md`.

Use this pack only after the treatment, outcome, estimand, population, and pre-treatment covariate
set are locked and conditional exchangeability is substantively defensible. A sophisticated
estimator does not repair an implausible unconfoundedness claim.

## Identification and overlap gates

1. Draw or state the causal adjustment argument. Every adjustment variable must be measured before
   treatment and must not be a descendant of treatment or outcome.
2. State conditional exchangeability, consistency, and positivity for the target population.
3. Inspect propensity overlap before estimating effects. Poor overlap changes who can be learned
   about: trim with a declared rule or switch to the overlap population, then rename the estimand.
4. Default to doubly robust estimation. Cross-fit flexible nuisance functions when model complexity
   warrants it; preserve held-out discipline for heterogeneity and policy learning.
5. Run calibrated unobserved-confounding sensitivity analysis. A result that fails under a
   confounder comparable to an observed benchmark is a design failure, not an estimator-selection
   prompt.

## Heterogeneity boundary

Distinguish describing conditional effects from learning a treatment policy. Honest CATE evidence
uses held-out or honest estimation. Policy value must be evaluated out of sample against a declared
policy class and cost rule. Post-result subgroup search remains exploratory.

## Required output

Report the target estimand and population, covariate timing audit, overlap plot and retained share,
balance, nuisance and cross-fitting choices, doubly robust estimate, assignment-consistent
uncertainty, sensitivity benchmark, limitations, and all gate dispositions. Use `template.R` as a
reference implementation, then register code, outputs, Evidence card, and governance records.
