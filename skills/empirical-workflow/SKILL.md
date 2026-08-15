---
name: empirical-workflow
description: End to end pipeline for panel data empirical research targeting ISR, MISQ, and Management Science, covering reduced form designs (OLS, fixed effects, IV, DID, DDD, event study, RDD) and structural models, with staged checkpoints, identification decision trees, robustness checklists, and a status log for context management. Use this skill whenever the user is working with panel or quasi experimental data, mentions identification, causal estimation, an empirical paper, a first year paper, a journal submission, robustness checks, or asks for help analyzing a dataset with a research question attached, even if they do not name a specific method.
---

# Empirical Workflow

This skill runs a full empirical paper from raw data to a submission ready
draft. It exists because the failure mode of AI assisted empirical work is not
bad code, it is a fluent paper built on an identification strategy nobody
examined and a specification that drifted while nobody was watching. The stage
gates and the status log are there to make drift visible.

## Pipeline

```
[1] Dataset Infra  ->  [2] Literature Map  ->  [3] Theory & Hypotheses
                                                        |
                                                  CHECKPOINT A
                                                        |
[4] Variables Map  ->  [5] Measurement & Validity
                                                        |
                                                  CHECKPOINT B
                                                        |
                        +-------------------------------+
                        |                               |
              [6a] Reduced Form                [6b] Structural
                        |                               |
                        +-------------------------------+
                                                        |
                                                  CHECKPOINT C
                                                        |
                                              [7] Paper Writing & Review
```

Stages 1, 2, 4, 5, and 7 are shared. The branch at Stage 6 is decided at the
end of Stage 3 and recorded in the status log. A project may run 6a only, 6b
only, or 6a followed by 6b (structural work almost always needs reduced form
companion evidence, see `stages/stage6b-structural.md`).

## How to run a stage

Read one stage file at a time, immediately before running that stage. Do not
preload the whole directory: the point of splitting the files is to keep the
working context on the stage at hand.

| Stage | File |
|---|---|
| 1 Dataset Infra | `stages/stage1-data-infra.md` |
| 2 Literature Map | `stages/stage2-lit-map.md` |
| 3 Theory & Hypotheses | `stages/stage3-theory-hypotheses.md` |
| 4 Variables Map | `stages/stage4-variables.md` |
| 5 Measurement & Validity | `stages/stage5-measurement.md` |
| 6a Reduced Form | `stages/stage6a-reduced-form.md` |
| 6b Structural | `stages/stage6b-structural.md` |
| 7 Paper Writing & Review | `stages/stage7-writing.md` |

Reference files, read when the stage tells you to:

- `references/identification-decision-tree.md`: design choice and estimator choice
- `references/robustness-checklists.md`: what each design owes the reader
- `references/r-standards.md`: project layout, packages, verification helpers
- `references/blindspot-audit.md`: the four quadrant self audit and its verdict rule
- `templates/status-template.md`: the status log

## Sub-step confirmation

Every stage is divided into numbered sub-steps. Before each one, state what you
will do, what the output will be, and what inputs are needed, then wait. This
is the single most important behavioral rule in the workflow, because most
irrecoverable errors in empirical work are cheap to prevent and expensive to
detect after the fact.

## Checkpoints

A checkpoint is a hard gate. Do not enter the next stage until every item passes
or the user explicitly waives it, and record any waiver in the Decision Log.
Present the checkpoint as a table with a pass, fail, or waived mark per item.

### Checkpoint A: research design is answerable

1. The question can be answered with the data actually in hand, not data the
   project hopes to obtain.
2. The identification strategy is named, and its central assumption is stated in
   one sentence a skeptical reader could attack.
3. Every hypothesis has a pre-committed specification, sample, and expected sign.
4. At least two competing explanations are named, with a stated plan to
   distinguish them empirically.
5. The contribution claim is one sentence, and the paper remains interesting if
   the primary hypothesis returns a null. If it does not, the design is a bet on
   a result rather than on a question.

### Checkpoint B: construction quality

1. Every core construct has a proxy justification with at least one citation to
   prior use.
2. Sample attrition is documented step by step with N at each step, and each
   drop has a stated reason.
3. The main functional form of the treatment and of the dependent variable is
   locked and recorded in the status log.
4. Descriptive statistics show no unexplained anomalies: missingness patterns,
   outliers, duplicate keys, calendar gaps, and unit entry and exit are all
   either explained or flagged.
5. Treatment timing is verified against the raw source, not against the
   constructed panel.
6. The clustering level and the number of clusters are fixed and justified.

### Checkpoint C: results are defensible

1. The identification assumption is stated together with the evidence offered
   for it, not merely asserted.
2. The baseline coefficient is stable across the diagnostic set required by the
   design.
3. Every hypothesis maps to a specific table and column.
4. The robustness pass rate is reported honestly, including the checks that
   failed and what they imply.
5. The blindspot audit has been run and its verdict is CLEAR or CONDITIONAL with
   the flags recorded.
6. There is an explicit statement of what evidence would change the conclusion.

## Backtracking

| Trigger | Action |
|---|---|
| Parallel trends rejected | Return to Stage 4 or 5. Reconsider the comparison group, the window, or the treatment definition. Do not proceed with the DID. |
| First stage F below the relevant threshold | Report it. Do not proceed to 2SLS as if nothing happened. Consider weak instrument robust inference or a different design. |
| Density or covariate continuity fails at the cutoff | The RDD is not valid at this cutoff. Stop and report. |
| Structural model fails to match a targeted moment | Return to 6b.1. Do not reparameterize until the fit is acceptable and call it a result. |
| A review pass flags an issue | Stabilize the current result before adding anything new. |
| The result is null | Report it. Consider whether the null is itself the paper. Do not search. |

Theory defines the search space of specifications. Data mining inside a
theory driven space is legitimate exploration. Data mining without theory is
not, and the difference is whether the specification was justifiable before the
result was seen.

## Status log

At the end of every stage, and immediately before any long running task, write
or update `_status.md` at the project root using `templates/status-template.md`.
The Decision Log and the Abandoned Approaches sections are the two that actually
save time later: without them a long session will circle back to options that
were already rejected and the reason for the rejection will be gone.

## Project layout

```
project/
├── _status.md
├── data/
│   ├── raw/          read only, never written to
│   └── derived/
├── code/             numbered scripts, see references/r-standards.md
├── results/
│   ├── tables/
│   ├── figures/
│   └── logs/         one markdown summary per results batch
├── docs/
│   ├── data_inventory.md
│   ├── lit_map.md
│   ├── theory_hypotheses.md
│   ├── variables_map.md
│   └── checkpoints/
└── paper/
```

## Language

Talk to the user in Chinese. Write every file, including code comments and this
project's documentation, in English.
