# Stage 6a: Reduced Form Analysis

Goal: produce a baseline estimate whose identification is defensible, and a
robustness set that a referee would recognize as complete. This stage ends at
Checkpoint C.

## Inputs

The locked Stage 3 hypothesis-to-estimate map, Stage 4 construction plan, Stage
5 measurement record, approved design, and current project-state records.

## Automatic actions

Execute the precommitted reduced-form design, its identifying diagnostics, and
the required robustness and mechanism evidence; record all outcomes.

## Required artifacts

The identification memo, estimation outputs, diagnostic and robustness records,
Checkpoint C record, Evidence cards, decision-log entries, and updated status.

## Red lines

Do not reinterpret a failed identifying diagnostic as robustness. Pause for a
recorded decision before changing a locked specification or identifying design.

## Exit condition

Checkpoint C is recorded as pass, revise, or authorized pause, with the result
traceable to the locked hypothesis-to-estimate map.

Read `references/identification-decision-tree.md` before 6a.1 and
`references/robustness-checklists.md` before 6a.4.

## 6a.1 Identification and estimator

Walk the decision tree. Output a short identification memo:

- what creates variation in the treatment
- which design that variation supports
- the central identifying assumption in one sentence
- the estimator, and why this estimator rather than the obvious alternative
- what would violate the assumption, and whether the data can detect it

For staggered adoption, the memo must state explicitly whether the main estimate
is a heterogeneity robust estimator. Two way fixed effects with staggered timing
is a reference specification, not a main specification.

## 6a.2 Baseline

Estimate the specification that was pre committed in Stage 3. Report the
coefficient, standard error, N, number of clusters, fixed effects, and the mean
of the dependent variable in the estimation sample.

Build the baseline table as a specification ladder: no controls, plus controls,
plus fixed effects, full specification. The reader learns more from how the
coefficient moves across the ladder than from any single column.

Interpret the magnitude in substantive units before moving on. A coefficient
that is statistically significant and economically trivial is a finding that
should be named as such.

## 6a.3 Design specific diagnostics

Run the diagnostics that the chosen design requires. These are not robustness
checks, they are the evidence for the identifying assumption, and they belong in
the main body. See the design sections of
`references/robustness-checklists.md`.

If a diagnostic fails, apply the backtracking rule in `SKILL.md`. Do not proceed
to robustness checks on an identification strategy that has already failed.

## 6a.4 Robustness

Derive the checklist automatically from the identification strategy, then run
it. Report every check that was run, including the ones that failed, with the
coefficient and standard error, not merely a statement that results are robust.

The robustness pass rate is a reported number at Checkpoint C.

## 6a.5 Mechanism

Test the observable arrows identified in Stage 3.2. A mechanism test is
persuasive only when it also discriminates against the competing explanations
from Stage 3.4. Report the discriminating implication explicitly.

Mediation analysis on observational data identifies a causal mechanism only
under assumptions that are usually indefensible here. Prefer heterogeneity that
the mechanism predicts and the alternatives do not, or a direct test on an
intermediate outcome.

## 6a.6 Heterogeneity

Subgroups come from theory, stated in advance. Report the interaction, not two
separate subsample coefficients compared by eye. If subgroups were chosen after
seeing results, label them exploratory in the table note and in the text.

## 6a.7 Blindspot audit

Mandatory once the first complete table set exists. Read
`references/blindspot-audit.md` and run it. Record the verdict.

## Checkpoint C

Run the Checkpoint C table from `SKILL.md`. Write the result to
`docs/checkpoints/checkpoint_c.md`.
