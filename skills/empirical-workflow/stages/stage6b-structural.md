# Stage 6b: Structural Analysis

## Inputs

- Router prerequisites and the approved structural branch from Stage 3.
- Locked primitives, hypotheses, variable map, measurement record, data
  contract, reduced-form facts where available, and target counterfactuals.
- The current status, decision-log tail, relevant Evidence cards, and method
  authorities for estimation and inference.

Read `references/data-contract.md` before consuming analysis data. If the
structural branch uses R, read `references/r-standards.md` before validation,
construction, diagnostics, or estimation.

## Automatic actions

- State agents, choice sets, information, timing, objectives, equilibrium, and
  tractability assumptions. Explain what the structure delivers that a reduced
  form cannot: a bounded counterfactual, welfare object, or parameter of
  intrinsic interest.
- Create the parameter-identification table before estimation. Every parameter
  is either identified by data variation and a moment/likelihood component or
  explicitly labeled **calibrated** with its source and fixed value.
- Predeclare solver, estimator, starting-value construction, convergence rule,
  simulation design, and standard-error method. Estimate from multiple starts,
  preserve logs, and report convergence or non-convergence.
- Compare targeted moments to data and report untargeted moments. Assess local
  moment sensitivity, objective/profile slices for counterfactual-bearing
  parameters, and feasible relaxations of tractability assumptions.
- Report each counterfactual's policy, fixed parameters and rationale,
  equilibrium concept, support/extrapolation boundary, and uncertainty.
  Reproduce at least one descriptive or reduced-form fact that disciplines the
  model.

## Required artifacts

- `docs/structural_primitives.md` and a parameter-identification table:

  | Parameter | Status: identified or calibrated | Data variation or calibration source | Moment or likelihood component | What would break identification |
  |---|---|---|---|---|

- Estimation code, versioned settings, multiple-start convergence log,
  objective values, simulation settings, and inference record.
- Targeted/untargeted fit table, structural evidence matrix, sensitivity and
  profile records, reduced-form companion output, counterfactual record, and
  an Evidence card for each reported estimate or counterfactual.
- Economics-style three-line tables, Checkpoint C structural record,
  decision-log entries, and updated status.

## Red lines

- Never call a calibrated parameter estimated, omit a parameter from the
  identification table, or present a flat objective direction as precision.
- Do not report a single-start optimum as convergence, target-only fit as
  validation, or a counterfactual outside support without its boundary and
  uncertainty.
- Pause before changing approved primitives, moments, sample, equilibrium,
  estimator, or counterfactual after results are observed.

## Exit condition

The structural Checkpoint C record shows that every parameter is identified or
labeled calibrated and sourced; multiple starts and uncertainty are reported;
targeted and untargeted fit, sensitivity, and reduced-form discipline are
visible; and each counterfactual has a support boundary. Every claim traces to
its Evidence card and output.

## 6b operating sequence

1. Lock primitives, parameter statuses, identification table, and estimation
   plan before running the solver.
2. Estimate from multiple starts; record convergence, targeted and untargeted
   fit, and parameter uncertainty.
3. Run sensitivity and reduced-form companion checks; return to primitives on
   a material fit failure.
4. Produce bounded counterfactuals, evidence cards, three-line tables, and the
   structural Checkpoint C record.
