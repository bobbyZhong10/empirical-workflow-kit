# Fixed-effects panel analysis

Adapted from the `causal-design` panel branch in `ericluo04/claude-academic-workflow` at commit
`8958cc246e65cdf7c36604f397a1c1719b7e2c14`; see `THIRD_PARTY_NOTICES.md`.

Use this pack only for a locked plain panel fixed-effects design with time-varying treatment,
within-unit variation, and no design-specific comparison event. An adoption date with untreated or
not-yet-treated comparisons routes to `../did/prompt.md`; simultaneity or feedback requiring an
instrument routes to `../iv/prompt.md`.

## Identification gate

State the estimand and defend strict exogeneity conditional on the unit effect:
`E[epsilon_it | D_i1, ..., D_iT, unit_i] = 0` for every period. Unit effects remove time-invariant
confounding only. They do not remove time-varying confounding, reverse causality, simultaneity,
anticipation, spillovers, or selection into observation. If past outcomes determine current
treatment, HOLD the causal claim and backtrack to design selection.

Before estimation:

1. Lock unit, period, treatment, outcome, sample, covariates, time effects, weights, and estimand.
2. Verify within-unit treatment variation and report how many units contribute no identifying
   variation.
3. Exclude treatment descendants and post-treatment controls.
4. Justify clustering from sampling and assignment, not residual correlation alone.
5. State whether effects are assumed constant. A non-absorbing treatment with heterogeneous
   effects requires explicit weighting diagnostics and may route to DiD methods.

## Required execution and evidence

Run the pooled-versus-within comparison in `template.R`, the locked specification ladder, and
diagnostics for timing, support, influential units, residual dependence relevant to inference,
entry/exit, and missingness. Report coefficient, uncertainty, clusters, N, unit and time effects,
within variation, dependent-variable mean, units, and substantive magnitude. A fixed-effects
coefficient may be described causally only when the strict-exogeneity argument and all applicable
gates remain supported.

## Required handoff

Record the selected canon date, identifying assumption, within-variation counts, clustering basis,
diagnostic disposition, code/output paths, and any HOLD in the identification memo, estimate record,
Evidence card, governance registry, and decision log.
