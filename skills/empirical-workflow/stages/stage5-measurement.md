# Stage 5: Measurement and Validity

Goal: establish that the variables measure the constructs, and lock the
functional forms. This stage ends at Checkpoint B.

## 5.1 Proxy justification

For every core construct, write a short paragraph: what the proxy captures, what
it misses, in which direction the mismatch would bias the estimate, and at least
one citation of prior use. A proxy whose bias direction is unknown is a
limitation that must appear in the paper.

## 5.2 Functional form, declared and locked

Consider the plausible forms of the treatment and of the dependent variable
(level, log, inverse hyperbolic sine, binary, share) and choose the main form on
substantive grounds, before estimation. Record the choice and the reason.

Two rules that prevent a common referee objection:

- For a skewed non negative outcome with zeros, prefer Poisson pseudo maximum
  likelihood on the level over a log of one plus the variable. The coefficient
  from a log of one plus transformation depends on the units of the variable and
  is not an elasticity.
- For a treatment that is a dose, do not discretize without a stated reason.

Alternative forms are robustness checks in Stage 6, reported in full. They are
never a menu presented for selection after the results are known.

## 5.3 Descriptive statistics

Produce the descriptive table that will go into the paper: N, mean, standard
deviation, and the relevant percentiles for every variable, split by treatment
status where applicable.

Then read it adversarially. Look for: impossible values, mass points, unexpected
zeros, variables with near zero variance within the fixed effect structure,
missingness that correlates with treatment, and any moment that disagrees with
what the source documentation implies.

## 5.4 Balance and pre period comparability

Where the design has a treated and a comparison group, report pre treatment
balance on the covariates and on the outcome level and trend. Imbalance is not
disqualifying by itself, but it must be visible and addressed.

## 5.5 Integrity checks in code

Write assertions into the construction script rather than checking by eye:
unique keys, expected row counts, no missing values in the treatment or outcome,
value ranges, and the clustering variable never missing. See
`references/r-standards.md` for the helper pattern.

## Checkpoint B

Run the Checkpoint B table from `SKILL.md`. Write the result to
`docs/checkpoints/checkpoint_b.md`. Do not begin Stage 6 until this is signed
off.
