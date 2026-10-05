---
name: empirical-workflow
description: Question-driven workflow for empirical research, from source inventory through paper review. Use for measurement, descriptive and institutional analysis, experiments, causal identification, structural and behavioral interpretation, economic significance, contribution, estimation, and research writing.
---

# Empirical Workflow

This file is the canonical Empirical Workflow Kit implementation. Runtime views
defined in `workflow.manifest.yaml` link here; edit only the canonical tree.

This skill advances empirical research through question, evidence, and inference.
Documented contracts preserve that reasoning and its provenance. The
repository, not the conversation, is the source of truth. Communicate in the
primary language used in the user's first substantive request, unless the user
explicitly asks to switch, and write durable repository artifacts in English.

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

## Module contract

Before each analysis module, use the existing Evidence card to state the economic
question, why it matters, competing explanations, what is observed, what the
design can distinguish, and the result that would change the judgment. Close
with what was learned, what remains indistinguishable, and whether to continue,
demote to background, narrow/delete, or stop. Before estimation, ask whether even
a successful estimate would yield only a mechanical fact and what knowledge it
would add to this paper. Read `references/execution-discipline.md` for this work-value
and stopping rule. Do not create a new tracker or equate coefficients, prediction
counts, or checkpoint verdicts with knowledge gained.

Description, measurement, institutional accounting, and conditional models are
valid branches. Apply identification obligations to causal claims, not to every
useful finding. Keep internal audit records separate from reader-facing prose.

Before interpreting or writing results in any branch, read
`references/research-writing.md`: question-led organization, economic meaning,
contribution, and behavioral inference apply across all methods. The selected
pack adds technical obligations; it cannot turn its methods paragraph into the
paper's organizing principle or make a passed diagnostic a contribution.

## Mandatory-pause routing

Proceed automatically through routine, reversible work that stays within the
approved design. Pause and request a recorded decision before a material design
change, failed identifying diagnostic, post-result specification, or external
publication or submission. The pause note must name the trigger, affected
artifacts, options, and decision needed to resume. Do not ask for confirmation
before every sub-step.

Changes to the main specification, estimation sample, clustering level, or
identifying strategy always require a Mandatory pause and a `decision-log.md`
entry before execution. A current unresolved exit failure returns work to the responsible stage.
Record whether it remains active, is repaired, closes with claim withdrawal, or
is retained as a disclosed limitation that the remaining claim can bear. Preserve
the failed record and closure evidence; a caveat alone cannot rescue a claim.

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
- `references/writing-standards.md`: the house prose style, with four advisory pattern checks; read before drafting and before the final pass.
- `references/elite-is-paper-standards.md`: contribution, construct, argument,
  and exhibit discipline for elite IS papers; read in Stages 2, 3, and 7 when
  IS positioning is relevant. The shared research-writing contract applies to all.
- `templates/paper-story-template.md`: contribution-to-evidence planning
  template; complete in Stage 3 and update in Stage 7.
- `references/blindspot-audit.md`: four-quadrant audit and verdict rule.
- `references/latex-manuscript-adapter.md`: Stage 7 LaTeX binding of the
  manuscript to the registry; read only when the format adapter is applied.
- `references/writing-under-the-registry.md`: how to interpret advisory writing checks without turning
  internal records into prose; read when a finding asks you to change prose.
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
- `references/start-prompts.md`: user-facing autonomous and takeover entry
  prompts; read only when the user selects one of those startup modes.
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
pack under `methods/`. Named-method facade skills provide direct discovery but route back through
the shared method-entry contract and the same canonical pack; they never own a second prompt.
Stage 7 may invoke `research-council`, `manuscript-review`,
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

Checkpoint A follows Stage 3, Checkpoint B follows Stage 5, and Checkpoint C follows Stage 7.
Stage 6 exits through a documented analysis-readiness review so evidence-backed
writing can begin without pretending that the not-yet-written submission has
already passed its final gate. A checkpoint requires its stated evidence, a
status update, and a recorded proceed, revise, or pause decision. A passing A
or B authorizes its next analysis phase; a passing C satisfies mechanical release requirements only. Completion also
requires substantive and editorial review and the recorded release decision.
Report reproducibility, claim credibility, discussion readiness, and submission
delivery separately in `_status.md`; a single blocking count cannot replace them. Run independent review where the protocol or project
configuration requires it.

### Checkpoint A: research design is answerable

1. The question can be answered with data actually in hand.
2. The evidence strategy and its central assumptions are stated; causal claims
   also name identifying variation and a challengeable identifying assumption.
3. Confirmatory hypotheses have prospective specifications and interpretation
   rules. Description and accounting define the target and measurement rules.
4. Plausible competing explanations have a plan for distinction, or an explicit
   account of what the available data cannot distinguish.
5. The question has value even if the preferred explanation is unsupported.

### Checkpoint B: construction quality

1. Every core construct has a cited proxy justification.
2. Sample attrition is documented step by step, with counts and reasons.
3. The main treatment and outcome functional forms are locked and recorded.
4. Duplicate keys, coverage gaps, entry/exit, missingness, and outliers are
   explained or flagged in the descriptive integrity record.
5. Treatment timing is verified against the raw source.
6. The clustering level and number of clusters are fixed and justified.

### Checkpoint C: results are defensible and delivered

1. Each important claim has a checked inferential bridge; causal claims pair
   their identifying assumptions with diagnostic evidence and its interpretation.
2. Main results, figures, dynamics, sensitivities, and magnitude conversions
   target compatible objects, or explain differences and their consequences.
3. Each retained claim maps internally to evidence that answers the question;
   instability narrows the conclusion rather than triggering a search for stability.
4. The robustness evidence matrix reports every required, omitted, and failed
   check with its identifying threat, implication, severity, and disposition.
5. The blindspot audit verdict and flags are recorded.
6. An independent cold reader can explain the question, main finding, contribution,
   and evidence boundary; unresolved substantive issues remain explicit.
7. The delivery contract is met: `output/` carries `data/` with its merge note,
   `code/`, `result/` with a PNG per figure and a CSV or markdown per table,
   and `LaTeX/` with the compiled PDF. See
   `references/delivery-contract.md`.

## Backtracking

| Trigger | Required action |
|---|---|
| Pre-trend evidence challenges the design | Pause the affected causal claim; inspect the diagnostic target, rule, power, and implication. Reconsider the design or narrow the claim with a recorded decision. |
| Weak first stage | Report it; use weak-instrument-robust inference or reconsider the design. |
| RDD density or covariate continuity raises a concern | Pause the affected causal claim and investigate sorting, measurement, and specification; a test alone does not establish cutoff validity or invalidity. |
| Structural fit fails a targeted moment | Return to Stage 6b primitives before reparameterizing. |
| Review flags a material issue | Stabilize the current result before adding new work. |
| Primary result is null | Report it and assess the null as a contribution; do not search for a preferred result. |

Theory defines the justifiable specification search space. Result-dependent
selection outside that space is prohibited by the Mandatory-pause routing.
