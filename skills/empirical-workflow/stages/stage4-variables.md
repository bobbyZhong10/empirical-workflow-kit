# Stage 4: Variables Map

Goal: turn constructs into variables, and fix the estimation sample, the fixed
effects, and the clustering level before anything is estimated.

Output: `docs/variables_map.md`, plus construction scripts.

## 4.1 Construct to variable table

| Construct | Variable | Definition and formula | Source columns | Unit | Precedent |

Every row needs a precedent from the Stage 2 construct table, or an explicit
note that this measure is new and therefore needs its own validity argument in
Stage 5.

## 4.2 Treatment definition and timing

State the treatment variable, the exact date or threshold that defines it, and
the source of that date. Verify the timing against the raw source rather than
against a constructed variable.

For staggered settings, tabulate the cohort structure: how many units are
treated in each period, how many are never treated, and whether any unit exits
treatment. Units that turn treatment off require a different estimator family
and this must be caught here rather than in Stage 6.

## 4.3 Sample construction and attrition log

Build the estimation sample as an explicit sequence of filters, and log N after
each one:

| Step | Filter | Reason | N units | N observations |

The last row is the estimation sample. This table goes into the paper. A filter
whose reason is "to make the sample cleaner" is not a reason.

Flag any filter that conditions on a variable realized after treatment. Sample
selection on a post treatment variable induces bias exactly like a bad control.

## 4.4 Controls

For each control, state why it belongs and confirm it is determined before
treatment. Run the bad control check explicitly:

- Is this variable plausibly affected by the treatment? If yes, it is a bad
  control. Move it to a mechanism test or drop it.
- Is this variable a proxy for the outcome? If yes, drop it.
- Would the coefficient of interest be interpreted differently with and without
  it? If yes, report both.

Controls that survive go into the main specification. The set is then frozen.

## 4.5 Fixed effects and clustering

State the fixed effects and what variation each one absorbs. Verify that the
treatment variable is not absorbed by the fixed effect structure.

Clustering: cluster at the level at which treatment is assigned, not at the
level of observation. Report the number of clusters. Below roughly 40 clusters,
plan for wild cluster bootstrap inference and say so now. Two way clustering
requires a stated reason.

## Handoff

`docs/variables_map.md` contains: variable table, treatment definition and
cohort structure, attrition log, control justification, fixed effects and
clustering plan. Update `_status.md`.
