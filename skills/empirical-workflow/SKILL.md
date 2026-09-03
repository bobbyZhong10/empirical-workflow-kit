---
name: empirical-workflow
description: Contract-driven workflow for panel-data empirical research, from source inventory through paper review. Use for empirical papers, causal identification, quasi-experiments, estimation, robustness, and research-stage planning.
---

# Empirical Workflow

This skill runs empirical research as a chain of documented contracts. The
repository, not the conversation, is the source of truth. Write user-facing
conversation in Chinese and durable repository artifacts in English.

## Router

Before selecting a stage, read in this order:

1. `RESEARCH_PROTOCOL.md`.
2. Active `research.yaml`, or `research.example.yaml` when no project
   configuration exists.
3. Project-root `_status.md`.
4. The current or most relevant Evidence card.
5. The tail of `decision-log.md`.

If a required project-state artifact does not yet exist, record that absence in
the next status artifact; do not invent its contents. Use `research.yaml` to
confirm the current stage, approved designs, authority level, languages, and
artifact conventions. Then load only the selected stage file immediately before
performing that stage; do not preload the stage directory.

| Stage | Contract file |
|---|---|
| 1. Dataset infrastructure | `stages/stage1-data-infra.md` |
| 2. Literature map | `stages/stage2-lit-map.md` |
| 3. Theory and hypotheses | `stages/stage3-theory-hypotheses.md` |
| 4. Variables map | `stages/stage4-variables.md` |
| 5. Measurement and validity | `stages/stage5-measurement.md` |
| 6a. Reduced form | `stages/stage6a-reduced-form.md` |
| 6b. Structural | `stages/stage6b-structural.md` |
| 7. Paper writing and review | `stages/stage7-writing.md` |

## Mandatory-pause routing

Proceed automatically through routine, reversible work that stays within the
approved design. Pause and request a recorded decision before a material design
change, failed identifying diagnostic, post-result specification, or external
publication or submission. The pause note must name the trigger, affected
artifacts, options, and decision needed to resume. Do not ask for confirmation
before every sub-step.

Changes to the main specification, estimation sample, clustering level, or
identifying strategy always require a Mandatory pause and a `decision-log.md`
entry before execution. A failed exit condition returns work to the responsible
earlier stage; it cannot be converted into a final caveat.

## Reference files

Read a reference only when the selected stage calls for it:

- `references/identification-decision-tree.md`: design and estimator choice.
- `references/robustness-checklists.md`: design-specific reader obligations.
- `references/r-standards.md`: R layout and verification helpers. **R is the
  default language for a project's empirical work**; read this before any
  construction, diagnostic, estimation, table or figure work.
- `references/python-standards.md`: Python layout and export rules; read only
  where an exception to the R default has been recorded in `decision-log.md`.
- `references/data-contract.md`: identity and validation contract across a
  language boundary; read when a stage produces, validates, or consumes
  analysis data across one.
- `references/delivery-contract.md`: what `output/` must contain before a
  submission is finished; read at Stage 7 and before Checkpoint C.
- `references/writing-standards.md`: the house prose style, four rules of which
  are checked; read before drafting and before the final pass.
- `references/elite-is-paper-standards.md`: contribution, construct, argument,
  and exhibit discipline for elite IS papers; read in Stages 2, 3, and 7.
- `templates/paper-story-template.md`: contribution-to-evidence planning
  template; complete in Stage 3 and update in Stage 7.
- `references/blindspot-audit.md`: four-quadrant audit and verdict rule.
- `references/latex-manuscript-adapter.md`: Stage 7 LaTeX binding of the
  manuscript to the registry; read only when the format adapter is applied.
- `references/writing-under-the-registry.md`: how to satisfy a writing check in
  the paper's own voice; read when a finding asks you to change prose.
- `references/operational-quality-loop.md`: planning, baseline reproduction,
  progressive validation, debugging, and completion evidence; read before
  changing research scripts, pipelines, validators, or registry logic.
- `references/research-writing.md`: durable prose, effect-interpretation,
  limitation, and quotation rules; read when producing or reviewing research
  prose.
- `references/execution-discipline.md`: work-value, object-inspection,
  verification, parallelism, destructive-action, and scope rules; read when a
  stage plans execution or review.
- `references/method-governance.md`: literature-first method choice,
  source-supplied boundaries, and the pilot/sweep decision rule; read before a
  method, metric, measurement, sample, or inference choice.
- `references/code-review.md`: concise research-code review taxonomy; read
  only when reviewing or simplifying code.
- `templates/status-template.md`: project status record.
- `templates/handoff-template.md`: cross-runtime transfer record.

Runtime-specific executable paths, caches, browser profiles, and connector
availability come from the project `runtime-profile.yaml`, initialized from
the repository-root `runtime-profile.example.yaml`. A missing optional tool
degrades the affected operation and must be reported; it does not authorize a
hard-coded personal path in a portable contract.

## Focused operation routing

Load a companion skill only for the operation at hand. Stage 2 routes known papers to
`research-sources`, topic searches to `literature-review`, and BibTeX files to
`bibliography-audit`. Stage 3 may invoke `preregister` prospectively. Stage 6a selects exactly one
pack under `methods/`. Stage 7 may invoke `research-council`, `manuscript-review`,
`referee-response`, `replication-release`, or the LaTeX and presentation skills. Companion outputs
must be registered in the current stage artifacts and may not bypass a checkpoint or mandatory
pause.

## Shared recordkeeping

At each stage exit, update `_status.md` with outputs, validations, remaining
risks, next stage, and unresolved pause. Create an Evidence card for each
material factual claim, data source, design choice, diagnostic, and result.
Record decisions and deviations with their timing in `decision-log.md`, the
sole append-only project history. Treat `_status.md` as a replaceable current
snapshot rather than a second decision log.
Raw data remains read-only; write cleaned and derived data separately. Keep
numbered research scripts direct and single-purpose, and document Python-to-R
data exchanges through stable artifacts such as Parquet.

## Checkpoint routing

Checkpoint A follows Stage 3, Checkpoint B follows Stage 5, and Checkpoint C
follows Stage 6. A checkpoint requires its stated evidence, a status update,
and a recorded proceed, revise, or pause decision. Only a passing checkpoint
authorizes the next stage. Run independent review where the protocol or project
configuration requires it.

### Checkpoint A: research design is answerable

1. The question can be answered with data actually in hand.
2. The identification strategy and its central assumption are stated in one
   sentence a skeptical reader could attack.
3. Each hypothesis has a precommitted specification, sample, and expected sign.
4. At least two competing explanations have a plan for empirical distinction.
5. The contribution remains interesting if the primary hypothesis is null.

### Checkpoint B: construction quality

1. Every core construct has a cited proxy justification.
2. Sample attrition is documented step by step, with counts and reasons.
3. The main treatment and outcome functional forms are locked and recorded.
4. Duplicate keys, coverage gaps, entry/exit, missingness, and outliers are
   explained or flagged in the descriptive integrity record.
5. Treatment timing is verified against the raw source.
6. The clustering level and number of clusters are fixed and justified.

### Checkpoint C: results are defensible and delivered

1. The identification assumption is paired with diagnostic evidence.
2. The baseline estimate is stable across the required diagnostic set.
3. Each hypothesis maps to a specific table and column.
4. The robustness evidence matrix reports every required, omitted, and failed
   check with its identifying threat, implication, severity, and disposition.
5. The blindspot audit verdict and flags are recorded.
6. The draft states what evidence would change the conclusion.
7. The delivery contract is met: `output/` carries `data/` with its merge note,
   `code/`, `result/` with a PNG per figure and a CSV or markdown per table,
   and `LaTeX/` with the compiled PDF. See
   `references/delivery-contract.md`.

## Backtracking

| Trigger | Required action |
|---|---|
| Parallel trends rejected | Return to Stage 4 or 5; reconsider comparison group, window, or treatment definition. Do not proceed with DID. |
| Weak first stage | Report it; use weak-instrument-robust inference or reconsider the design. |
| RDD density or covariate continuity fails | Stop and report; the cutoff is not valid. |
| Structural fit fails a targeted moment | Return to Stage 6b primitives before reparameterizing. |
| Review flags a material issue | Stabilize the current result before adding new work. |
| Primary result is null | Report it and assess the null as a contribution; do not search for a preferred result. |

Theory defines the justifiable specification search space. Result-dependent
selection outside that space is prohibited by the Mandatory-pause routing.
