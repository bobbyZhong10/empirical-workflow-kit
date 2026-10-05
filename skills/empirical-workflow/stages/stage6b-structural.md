# Stage 6b: Structural Analysis

## Inputs

- Router prerequisites and the approved structural branch from Stage 3.
- Locked primitives, hypotheses, variable map, measurement record, data
  contract, reduced-form facts where available, and target counterfactuals.
- The current status, decision-log tail, relevant Evidence cards, and method
  authorities for estimation and inference.

Read `references/research-writing.md` for economic meaning, contribution, and
behavioral inference. Read `references/data-contract.md` and `references/operational-quality-loop.md`
before consuming analysis data. If the structural branch uses R, read
`references/r-standards.md` before validation,
construction, diagnostics, or estimation.

## Automatic actions

- Use the router's question-evidence-inference contract before and after each
  module. A conditional model exercise can be valuable without identified
  parameters; state which assumptions, calibration, and observations discipline
  it and which conclusions remain conditional. Apply solver/estimation checks
  only when a solver/estimator is used, with a reason for inapplicable items.
- Reconcile outcomes, samples, comparisons, windows, baselines, weights,
  aggregation, and target quantities across exhibits and counterfactuals using
  `references/robustness-checklists.md`. A formula payment scenario is not an
  identified income or welfare loss; an inverted variable is not independent
  mechanism evidence. Distinguish assumed preferences, beliefs, information, and
  equilibrium behavior from evidence that discriminates among them. Explain whose
  objective changes, including costs/transfers and distribution when relevant;
  fit, solver success, and parameter precision alone do not establish contribution.

- Review material solver or simulation changes using `references/code-review.md`;
  retain failed runs and verify uncertainty and random streams. Apply the figure
  and saved-result rules in `references/r-standards.md` to reported exhibits.
- Before a formal solver run, verify the data and objective on a small,
  deterministic case; where an inherited implementation exists, reproduce a
  known baseline before accepting extension results.
- State agents, choice sets, information, timing, objectives, equilibrium, and
  tractability assumptions. Explain what the structure delivers that a reduced
  form cannot: a bounded counterfactual, welfare object, or parameter of
  intrinsic interest.
- Create the parameter-identification table before estimation. Every parameter
  is either identified by data variation and a moment/likelihood component or
  explicitly labeled **calibrated** with its source and fixed value.
- Keep `identified` and `calibrated` substantively distinct in structural records
  and manuscript sites. State identification as a property delivered by data
  variation and a moment/likelihood component (including passive forms or
  "only X can be identified"); state calibration as an analyst-authored
  setting with its fixed value and source.
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
- Register `identified → simulated` as a downgrade when an estimated object
  becomes a simulation output. Type every such assertion site as
  `model_internal`, mark it `as_modeled: true`, and record
  `underlying_precision.has_sampling_distribution: false` unless a sampling
  distribution was actually constructed.
- Internally register every qualifier governing multiple counterfactuals as a
  `scope_declaration` with an explicit manuscript coverage range. A body
  declaration does not cover a title, abstract, or conclusion site outside
  that range. State conditions naturally where needed for interpretation;
  coverage metadata does not require repeating a label at every mention.

## Required artifacts

- `docs/structural_primitives.md` and a parameter-identification table:

  | Parameter | Status: identified or calibrated | Data variation or calibration source | Moment or likelihood component | What would break identification |
  |---|---|---|---|---|

- Estimation code, versioned settings, multiple-start convergence log,
  objective values, simulation settings, and inference record.
- Targeted/untargeted fit table, structural evidence matrix, sensitivity and
  profile records, reduced-form companion output, counterfactual record, and
  an Evidence card for each reported estimate or counterfactual.
- Assertion-registry entries for structural results and counterfactuals,
  including identified/calibrated status, any `identified → simulated`
  downgrade, model-internal typing, precision, and scope declarations.
- Economics-style three-line tables, `docs/checkpoints/analysis_readiness.md`,
  decision-log entries, and updated status.

## Red lines

- Never call a calibrated parameter estimated, omit a parameter from the
  identification table, or present a flat objective direction as precision.
- Never present a simulated model-internal quantity as identified empirical
  evidence or use `significant` for it without a sampling distribution.
- Do not report a single-start optimum as convergence, target-only fit as
  validation, or a counterfactual outside support without its boundary and
  uncertainty.
- Pause before changing approved primitives, moments, sample, equilibrium,
  estimator, or counterfactual after results are observed.

## Exit condition

The structural analysis-readiness record shows that every parameter is identified or
labeled calibrated and sourced; multiple starts and uncertainty are reported;
targeted and untargeted fit, sensitivity, and reduced-form discipline are
visible; and each counterfactual has a support boundary. Every planned claim
traces to its Evidence card and output. The module states what was learned,
which alternatives remain unresolved, its economic meaning and contribution or
background value, and why to continue, demote, narrow/delete, or stop. This record authorizes drafting, not
circulation or submission.

## 6b operating sequence

1. Lock primitives, parameter statuses, identification table, and estimation
   plan before running the solver.
2. Estimate from multiple starts; record convergence, targeted and untargeted
   fit, and parameter uncertainty.
3. Run sensitivity and reduced-form companion checks; return to primitives on
   a material fit failure.
4. Produce bounded counterfactuals, evidence cards, three-line tables, and the
   structural analysis-readiness record.
