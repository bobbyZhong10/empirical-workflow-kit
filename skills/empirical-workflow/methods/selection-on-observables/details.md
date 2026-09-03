# Selection-on-observables implementation details

Current as of 2026-08-26. Package behavior and the longer sensitivity ladder remain traceable to
`../causal-design/details.md`.

## Mandatory sensitivity ladder

- Manski-style bounds remove exchangeability but are often wide; they state what the data alone say.
- Calibrated confounder models compare an omitted confounder with the strongest observed benchmark.
  Oster analysis must state proportional-selection and target-R-squared assumptions. Cinelli-Hazlett
  reporting states robustness values and benchmark bounds.
- Rosenbaum design sensitivity bounds assignment odds in matched designs.

Failure under mild, substantively plausible confounding qualifies or blocks the causal claim.

## Interface traps

- `sensemakr` identifies treatment by coefficient name; encode a binary treatment numerically and
  pass the actual coefficient name.
- `WeightIt` supports `estimand = "ATO"` only for compatible methods. Use weight-aware inference
  such as `lm_weightit()` rather than treating estimated weights as fixed.
- In `grf`, pass clusters when fitting the forest; `average_treatment_effect()` has no cluster argument.
- Evaluate RATE priorities or learned policies on observations not used to learn the ranking or policy.
- `policytree` actions are column indices of the score matrix, not necessarily the original 0/1 codes.
