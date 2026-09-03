# Stage 5: Measurement and Validity

## Inputs

- Router prerequisites; Stage 1 quality reports, Stage 2 measurement precedent,
  Stage 3 locked hypothesis-to-estimate map, and Stage 4 variables, timeline,
  attrition, and inference plan.
- Versioned derived data and construction scripts subject to the project data
  contract.

Read `references/data-contract.md` and `references/r-standards.md` before
validating or consuming the Python analysis export. Lock the expected contract
identity fields in `research.yaml` before validation.

## Automatic actions

- Write a proxy justification for every core construct: what it captures and
  misses, expected bias direction, limits, and prior-use citation.
- Choose the main treatment and outcome functional forms on substantive grounds
  and lock them before estimation; mark alternatives as predeclared robustness
  checks rather than result-selection options.
- Execute data-contract validation in code: unique keys, expected row counts,
  required fields, missingness, value ranges, timing, and nonmissing clustering
  identifiers.
- Produce and adversarially review descriptives, missingness, outliers, mass
  points, pre-period comparability, and within-fixed-effect variation.
- Freeze the acceptance-gate definitions that apply to construction,
  measurement, sample eligibility, and treatment timing. Evaluate coverage for
  every declared scope; `not_evaluated` and incomplete coverage block
  Checkpoint B.

## Required artifacts

- `docs/measurement_validity.md`: proxy justifications, citations, limitations,
  bias-direction assessment, and validity conclusions.
- `docs/functional_form_lock.md`: locked treatment and outcome forms, rationale,
  date, and predeclared alternative forms.
- `docs/data_contract_validation.md`: executable validation results, input data
  version, assertions, failures, remediation, and rerun status.
- `docs/descriptive_integrity_record.md`: descriptive statistics, balance or
  pre-period checks, anomalies, missingness, outliers, and resolution status.
- `docs/checkpoints/checkpoint_b.md`, relevant Evidence cards, decision-log
  entries, and an updated `_status.md`.
- The project governance registry initialized from
  `templates/governance-registry-template.yaml`, with authority-signed frozen
  gate definitions and completed applicability records.

## Red lines

- Do not choose a proxy or functional form after inspecting the main estimate,
  or replace a failed validation assertion with a manual visual check.
- Never hide anomalous descriptives, missingness related to treatment, or a
  proxy limitation with an unknown or material bias direction.
- Pause for a recorded decision before changing the main outcome, treatment
  form, specification, estimation sample, clustering, or identifying strategy.

## Exit condition

Checkpoint B passes. A revise or pause outcome does not authorize Stage 6.
Every core proxy is justified, functional forms are locked, the data contract
validates against the expected project and analysis-input identities, and the
descriptive integrity record resolves or exposes material anomalies. The status
record identifies the selected Stage 6 branch and remaining risks.
