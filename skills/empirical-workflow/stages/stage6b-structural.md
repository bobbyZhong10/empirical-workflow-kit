# Stage 6b: Structural Analysis

Goal: estimate a model whose parameters have an economic interpretation, and
produce counterfactuals whose limits are stated. The gate logic differs from
6a: in structural work the identification argument must be settled before
estimation, because estimation cannot reveal that a parameter was never
identified.

## Inputs

The approved structural branch, locked Stage 3 commitments, Stage 4 and 5
construction records, and current project-state records.

## Automatic actions

Specify primitives and identification, estimate with documented convergence,
assess fit and sensitivity, and report bounded counterfactuals.

## Required artifacts

The parameter-identification table, estimation and fit logs, sensitivity and
counterfactual records, Checkpoint C record, Evidence cards, and updated status.

## Red lines

Do not label a calibrated parameter as estimated or use a counterfactual beyond
its disclosed support. Pause before changing the approved structural design.

## Exit condition

The structural Checkpoint C record is complete and all reported claims trace to
identified parameters, documented fit, and bounded counterfactual evidence.

## 6b.1 Primitives and justification

State the model: agents, choice sets, information, timing, objective functions,
and the parameters to be estimated. Then answer the question that decides
whether this stage should exist at all: what does the structure buy that a
reduced form estimate cannot deliver? Acceptable answers are a counterfactual
outside the observed support, a welfare quantity, or a structural parameter that
is itself the object of interest. An answer of "it is more rigorous" is not one.

State every assumption that is made for tractability rather than for realism,
and which results depend on it.

## 6b.2 Identification argument

Produce the table that referees will look for first:

| Parameter | Variation in the data that identifies it | Moment or likelihood component | What would break identification |

Every parameter needs a row. A parameter with no row is calibrated, not
estimated, and must be labeled as calibrated with its source.

## 6b.3 Estimation

Declare the language, the solver, and the estimator (generalized method of
moments, maximum likelihood, simulated method of moments, nested fixed point,
or a two step approach) before writing code.

Report: starting values and how they were chosen, the optimizer, convergence
criteria, whether multiple starts converge to the same optimum, and the standard
error method including any simulation adjustment.

Multiple starting values are mandatory. A single optimizer run reports a local
optimum and nothing more.

## 6b.4 Fit

Report targeted moments against their data counterparts, and at least one
untargeted moment. Fit on untargeted moments is the credible evidence; fit on
targeted moments is close to mechanical.

If a targeted moment is not matched, return to 6b.1. Do not reparameterize until
the fit is acceptable and then present the fit as validation.

## 6b.5 Sensitivity

Report how the estimated parameters respond to the moments, using a local
sensitivity measure, and report profile likelihood or objective function slices
for the parameters that carry the counterfactual. Flat directions in the
objective function are an identification problem and must be disclosed.

Re estimate under the main tractability assumptions relaxed where feasible.

## 6b.6 Counterfactuals

For each counterfactual state: the policy change, which parameters are held
fixed and why that is defensible under the change, whether the counterfactual
lies inside the observed support, and the equilibrium concept used. Report
uncertainty in the counterfactual, not only a point estimate.

An extrapolation boundary statement is required: name the range over which the
model is being asked to speak and note where it stops being credible.

## 6b.7 Reduced form companion

Produce at least one descriptive or reduced form fact that the structural model
must reproduce, and show that it does. This is what convinces a reader that the
structure is disciplined by the data rather than by the assumptions.

## Checkpoint C, structural variant

1. Every estimated parameter has an identification row.
2. Calibrated parameters are labeled and sourced.
3. Convergence is demonstrated from multiple starting values.
4. Untargeted moment fit is reported.
5. Sensitivity and flat directions are disclosed.
6. Counterfactuals state the fixed parameters and the extrapolation boundary.
7. The reduced form companion fact is reproduced by the model.
