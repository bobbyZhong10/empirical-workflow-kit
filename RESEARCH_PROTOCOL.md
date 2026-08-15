# Research protocol

## Purpose and scope

This protocol is the portable operating contract for an empirical research
project. It governs project setup, data work, design, estimation, writing, and
review. It is tool-neutral: a project can use either Claude Code or Codex, or
move between them, without changing the research record or the red lines.

## Source of truth and handoff

The repository is the source of truth. Keep the active project configuration in
`research.yaml`, the running decisions in `decision-log.md`, and the current
stage status in the project's status artifact. A handoff records the completed
stage, artifacts changed, open risks, next action, and any pause that remains
unresolved. Conversation context is never a substitute for these files.

## Roles

The Executor performs the assigned research work and records reproducible
artifacts. The Copilot helps plan, inspect, and challenge work, but does not
silently override the documented specification. The Quality auditor performs
an independent review of the relevant artifact, with special attention to
identification, reproducibility, and claims. One person or tool may fill more
than one role only when the review record makes that limitation explicit.

## Authority levels

Routine implementation choices within the approved design may proceed
autonomously. Reversible exploratory analyses may proceed when clearly labeled
as exploratory. Changes to the study's design, identifying assumptions,
outcomes, sample rules, or external communication require the authority stated
in the project configuration or an explicit human decision recorded in
`decision-log.md`.

## Mandatory pause

Pause work and request a recorded decision before a material design change, a
failed identifying diagnostic, a post-result specification, or external
publication or submission. The pause note must state what triggered it, which
artifacts are affected, options considered, and the decision needed to resume.

## Stage interface

Each stage consumes named upstream artifacts and produces named downstream
artifacts. Before starting, confirm the required inputs and constraints in
`research.yaml`; before completing, record outputs, validation performed,
remaining risks, and the next stage. Do not treat a stage as complete merely
because code ran.

## Checkpoints

Checkpoints are gates. They require the specified evidence, a status update,
and a decision to proceed, revise, or pause. A failed checkpoint returns work
to the relevant earlier stage rather than being converted into a caveat at the
end of the workflow.

## Specification discipline

Define and version the main specification before interpreting results. Separate
confirmatory work from exploration, label deviations, and record their
rationale and timing in `decision-log.md`. Do not promote a result-dependent
choice to the main specification without a Mandatory pause decision.

## Python-R boundary

Use Python for ingestion, cleaning, joins, validation, and portable data
artifacts unless the project documents another choice. Use R for estimation
when its model or inference implementation is selected. Exchange data through
documented, stable files such as Parquet; record versions, commands, and
parameters at the boundary.

## Evidence records

Create an Evidence card for every material factual claim, design choice, data
source, diagnostic, and result used to support a conclusion. Each card links to
its source artifact, records the method and date, distinguishes observation
from inference, and identifies any limitation or unresolved uncertainty.

## Independent review

The Quality auditor reviews the relevant evidence and implementation without
relying solely on the Executor's summary. The review checks traceability from
claim to Evidence card, adherence to the approved specification, identifying
assumptions and diagnostics, and whether limitations are stated proportionally.
Record findings and required follow-up in `decision-log.md`.
