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

## Language

**R is the default language for a project's empirical work**, end to end:
panel construction, estimation, inference, tables, and figures. A project that
uses something else is making a choice, and the choice has to be recorded and
justified.

Python is permitted where R cannot do the work, or cannot do it at the required
scale or precision. Typical grounds are a library with no R equivalent, a
performance ceiling reached in R, or an upstream dependency that only emits
Python. Record the reason in `decision-log.md` at the point of the exception,
name the boundary in the code, and exchange data across it through a
documented, stable file such as Parquet. "It was faster to write" is not a
ground.

The rule exists because a mixed codebase is a codebase nobody can rerun. Where
an exception is taken, the two halves must still compose into one runnable
pipeline, and the delivered `output/code` must contain both.

## Delivery contract

A finished project delivers into `output/`. This is not a filing preference; it
is what "finished" means, and Checkpoint C enforces it.

```
output/
  data/     the final data the paper was produced from, plus a markdown note
            saying how it was assembled -- sources, joins, filters, row counts
  code/     the code that runs the paper's empirical work, R unless an
            exception is recorded
  result/   every figure the paper shows, as PNG, and every table, as CSV or
            markdown
  LaTeX/    the sources that compile the final PDF, and the PDF
```

Three rules govern it:

1. **The data note is not optional.** A reader cannot infer a merge from its
   output. `output/data` needs a markdown file that says where each input came
   from, what was joined to what on which key, what was dropped and why, and
   what the row count was at each step.
2. **Every typeset table has an export.** A table a reader can only get by
   compiling LaTeX is a table they cannot check. One CSV or markdown file per
   table in the paper.
3. **Every figure is a PNG.** Whatever the paper embeds, `output/result` also
   carries a raster a reader can open.

The validator reports `OUTPUT_ROOT_MISSING`, `OUTPUT_DIRECTORY_MISSING`,
`OUTPUT_DIRECTORY_EMPTY`, `OUTPUT_DATA_NOTE_MISSING`, `OUTPUT_PDF_MISSING` and
`OUTPUT_TABLE_EXPORT_INCOMPLETE` against this contract, and `OUTPUT_DELIVERY`
as the summary.

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
