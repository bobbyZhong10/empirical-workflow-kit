# Fixed-effects canon

Current as of 2026-08-26. Verified through 2026-08-26 against the read records inherited from the
upstream causal-design canon. Bibliographic keys live in `../causal-design/references.bib`.

## Wooldridge (2010), *Econometric Analysis of Cross Section and Panel Data*

- Role: formal source for the unobserved-effects model and strict-exogeneity condition.
- Settles: what the within transformation removes; why treatment may correlate with the unit effect;
  why feedback, simultaneity, and time-varying omitted variables remain identification failures.
- Binds when: a causal interpretation is proposed for a plain within-unit panel regression.
- Implement: within estimator with explicit unit effects; add time effects only when justified by the
  assignment and outcome process.
- Scope limits: this pack excludes dynamic-panel, random-effects, Mundlak-Chamberlain, DiD, and IV
  estimators.
- Named disagreements: none adjudicated here; estimator choice cannot repair failed strict exogeneity.
- Excluded: no claim that fixed effects automatically solve endogeneity.

## Abadie, Athey, Imbens, and Wooldridge (2023)

- Role: assignment- and sampling-based clustering authority.
- Settles: whether and where to cluster comes from sampling and treatment assignment, not merely
  within-cluster outcome correlation.
- Binds when: choosing uncertainty estimates for the fixed-effects coefficient.
- Implement: record the sampling and assignment cluster before choosing robust or clustered variance.
- Scope limits: linear estimators and a many-cluster asymptotic framework.
- Named disagreements: conventional automatic clustering may be conservative or inappropriate under
  unit-level random assignment.
- Excluded: no software-specific few-cluster solution is supplied by this source.
