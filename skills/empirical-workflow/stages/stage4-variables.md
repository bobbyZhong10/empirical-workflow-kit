# Stage 4: Variables Map

## Inputs

- Router prerequisites, Stage 1 data-quality artifacts, Stage 2 measurement
  precedents, and the locked Stage 3 hypothesis-to-estimate map.
- Raw timing evidence, available source columns, and the approved observation
  unit, sample rules, fixed effects, and clustering authority.

## Automatic actions

- Map each construct to a variable, formula, source column, unit, and Stage 2
  precedent; identify measures requiring Stage 5 validity support.
- Verify treatment timing against raw sources and produce an
  announcement/effective/actual treatment timeline. Tabulate cohorts, never-
  treated units, treatment reversals, and each treatment exit.
- Build the estimation sample as sequential filters with unit and observation
  counts. Test controls for post-treatment determination and identify variables
  that create a post-treatment-selection warning.
- State fixed effects, clustering level, cluster count, and the variation each
  choice preserves or absorbs; freeze the approved construction plan.

## Required artifacts

- `docs/variables_map.md`: construct-to-variable table, formulas, sources,
  units, precedent, controls, fixed effects, and clustering plan.
- `docs/treatment_timeline.md`: announcement, effective, and actual treatment
  timing; raw-source evidence; cohort structure; treatment exits and estimator
  implications.
- `docs/sample_attrition.md`: ordered sample filters, reasons, unit and
  observation counts, and post-treatment-selection warnings.
- Versioned construction scripts, relevant Evidence cards, decision-log entries
  for frozen choices, and an updated `_status.md`.

## Red lines

- Never infer treatment timing from a constructed panel when raw timing
  evidence is available, or ignore a treatment exit or reversal.
- Do not condition the main sample or controls on a post-treatment variable;
  flag the post-treatment-selection warning and move the choice to a mechanism
  test or pause for a decision.
- Pause for a recorded decision before changing the estimation sample, primary
  treatment, clustering level, fixed effects, or identifying strategy.

## Exit condition

Every core construct maps to a documented variable, the announcement/effective/
actual timeline and treatment exits are verified, attrition is reproducible, and
the post-treatment-selection review is resolved or paused. The construction and
inference plan is locked for Stage 5 and recorded in `_status.md`.
