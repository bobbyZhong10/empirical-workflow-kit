# Selection-on-observables canon

Current as of 2026-08-26. Verified through 2026-08-26 against the upstream causal-design canon and
details. Bibliographic keys live in `../causal-design/references.bib`.

## Imbens (2024)

- Role: assumptions-first authority for observational identification and estimand choice.
- Settles: doubly robust estimation as the default with many covariates; descendant controls as a
  common failure; overlap violations changing the target population; the graded sensitivity ladder.
- Binds when: conditional exchangeability is the identifying assumption.
- Implement: audit pre-treatment covariates, estimate overlap, use AIPW or DML, and report calibrated
  sensitivity.
- Scope limits: excludes dynamic treatment regimes and does not make high-dimensional text
  automatically sufficient for confounding control.
- Named disagreements: propensity-score matching is not the default when modern doubly robust
  alternatives are feasible.
- Excluded: no causal claim from predictive adjustment alone.

## Bang and Robins (2005); Chernozhukov et al. (2018)

- Role: doubly robust and orthogonal estimation foundations.
- Settles: consistency when one nuisance model is correct in the classical DR setting, and
  cross-fitted orthogonal scores for flexible nuisance estimation.
- Binds when: outcome and propensity nuisance functions are estimated rather than known.
- Implement: AIPW with declared nuisance learners, folds, seeds, and out-of-fold predictions.
- Scope limits: statistical robustness does not validate exchangeability, consistency, or positivity.
- Named disagreements: learner selection is project-specific and must be precommitted or labeled exploratory.
- Excluded: no automated causal identification from machine learning.

## Crump et al. (2009); Li, Morgan, and Zaslavsky (2018)

- Role: overlap and target-population authorities.
- Settles: principled trimming and overlap weighting when propensity support is weak.
- Binds when: estimated treatment probabilities approach zero or one.
- Implement: declare trimming or overlap weights before the focal estimate and report the resulting population.
- Scope limits: changing weights changes the estimand; it is not a cosmetic robustness check.
- Named disagreements: the common 0.1/0.9 cutoff is a rule of thumb, not a universal optimum.
- Excluded: no extrapolation to unsupported covariate regions.
