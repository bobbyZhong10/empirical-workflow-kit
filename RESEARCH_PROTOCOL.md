# Research protocol

## Purpose and scope

This protocol is the portable operating contract for an empirical research
project. It governs project setup, data work, design, estimation, writing, and
review. It is tool-neutral: a project can use either Claude Code or Codex, or
move between them, without changing the research record or the red lines.

## Source of truth and handoff

The repository is the source of truth. Keep the active project configuration in
`research.yaml`, the running decisions in the append-only `decision-log.md`,
and the current stage status in the project's replaceable status artifact.
`decision-log.md` is the sole append-only project history; status, handoff, and
evidence artifacts are versioned records or current snapshots rather than
parallel decision histories. A handoff records the completed
stage, artifacts changed, open risks, next action, and any pause that remains
unresolved. Raw data is never overwritten: preserve the received source and
write cleaned or derived data to separate, documented artifacts. Conversation
context is never a substitute for these files.

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
Changes to the main specification, estimation sample, clustering level, or
identifying strategy require a Mandatory pause and a recorded decision before
execution.

## Stage interface

Each stage consumes named upstream artifacts and produces named downstream
artifacts. Before starting, confirm the required inputs and constraints in
`research.yaml`; before completing, record outputs, validation performed,
remaining risks, and the next stage. Do not treat a stage as complete merely
because code ran. Research scripts are numbered and direct: their filenames
make execution order clear, and each script has one plainly stated purpose.

## Checkpoints

Checkpoints are gates. They require the specified evidence, a status update,
and a decision to proceed, revise, or pause. A failed checkpoint returns work
to the relevant earlier stage rather than being converted into a caveat at the
end of the workflow. Only a passing checkpoint authorizes the next stage.

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

## Research judgment and verification

Before adding work, state which registered claim it supports and what would
change if the work were omitted. Do not add an analysis, metric, source, or
iteration that moves no reported figure, resolves no gate, and answers no
credible reviewer objection. Inspect the underlying object before classifying
or measuring it. A description of a file, figure, slide, table, log, or record
is not evidence about that object.

Treat a job status, file content, reported number, external-tool result, and
reviewer output as unverified until inspected. Record the check and its method.
Give every non-obvious threshold or default a literature source or a labeled
judgment rationale. Search terms, field names, and candidate values come from
the source's actual index or schema when one exists; do not substitute a
near-synonym from memory.

Method, metric, sample, measurement, and inference decisions start from
current reputable literature and maintained implementations. When the
literature does not settle a choice, label it as research judgment and state
the reason a reviewer can evaluate. A sweep, pilot arm, or specification
search proceeds only when its result could change the decision, literature and
judgment cannot settle it, and its cost is proportionate to the uncertainty it
resolves.

## Research writing and source use

Every substantive claim must be supported by a citation, registered evidence,
a reported figure, or an explicit argument. Effect statements give direction,
magnitude, and a meaningful benchmark. Statistical significance never stands
in for substantive size.

Put a limitation beside the choice or result it constrains. State whether the
limitation comes from the data, design, method, or model and name its cost in
power, identification, scope, or generalizability. Disclose a deviation from a
preregistration or earlier plan where the deviation first affects the paper,
with its reason and decision-log reference.

Summarize sources in original language. Verbatim wording is quoted and tied to
a page, section, table, or other stable locator. State which version was read.
An abstract-only record cannot establish material claim support. Apply the
document rules in `references/research-writing.md` during Stage 7 and to any
research memo, review, response letter, or public-facing research artifact.

## Publication, confidentiality, and release

Before sending manuscript content to a generative or external service, record
who owns the manuscript, the service involved, the applicable venue or
institutional policy, and whether confidentiality permits the transfer. Do
not use a third party's confidential submission for automated review without
documented authorization.

External circulation, registry submission, journal submission, repository
publication, and release-archive upload require the authority stated in the
project configuration and a recorded decision. A release package follows a
successful reproduction check. Packaging, path sanitization, or manifest
generation alone is not reproducibility certification. Check time-sensitive
outlet rules against current official sources before the release decision.
