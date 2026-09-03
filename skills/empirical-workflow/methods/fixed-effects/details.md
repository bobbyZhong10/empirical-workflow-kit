# Fixed-effects implementation details

Current as of 2026-08-26. This file narrows the upstream causal-design details to plain panel fixed
effects.

## Failure modes

- No within-unit variation: the unit contributes no identifying treatment variation.
- Treatment descendants: adding tenure, exposure, behavior, or status caused by treatment can open
  biasing paths; temporal labels alone do not make a control pre-treatment.
- Feedback: lagged outcomes setting treatment violates strict exogeneity even when unit effects fit.
- Simultaneity: a shared period shock or same-period outcome response can reverse the coefficient.
- Attrition and entry: treatment-dependent observation changes the target population and estimand.
- Heterogeneous effects: the within coefficient may be an opaque weighted average; state the
  constant-effect scope or provide a method-specific weighting argument.

## `fixest` interface traps

In `feols(y ~ d | unit + period, cluster = ~assignment_cluster)`, the bar separates regressors from
fixed effects. The treatment stays to the left. `cluster` takes a formula. Units without within
variation are absorbed; count them explicitly before fitting. A time-invariant covariate cannot be
separately identified with unit effects.

For `estimatr::lm_robust`, `fixed_effects` is a right-sided formula while `clusters` is a bare column
name. `se_type = "stata"` matches the familiar clustered FE correction only when clusters are
actually supplied.
