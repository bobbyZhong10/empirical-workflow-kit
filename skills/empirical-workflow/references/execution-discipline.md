# Execution Discipline

## Work-value test

Before adding work or acting on a mid-task finding, identify the registered
claim, gate, reported figure, or reviewer objection it affects. If the work
moves no reported figure, resolves no gate, supports no claim, and answers no
credible objection, record it as an optional follow-up and do not expand the
current task. A third iteration of a measurement triggers a step-back review of
whether the measurement still belongs in the study.

Read the plan of record at the start of each phase and after a material pivot.
Check whether an analysis already running will answer the new question before
starting another one.

## Inspect before judging

Look at the object before building or applying a classifier, score, or
measurement. Open the file, data record, table, log, image, slide, or figure.
For a visual defect, inspect the relevant region at sufficient resolution
before deciding whether labels overlap, text is unreadable, or contrast fails.

A job state, file content, table value, external-tool response, or reviewer
claim remains unverified until inspected. State what was checked and how. Mark
anything else unconfirmed.

## Concurrency and independent work

Parallelize independent reads, searches, and review lenses when the runtime
supports it and the user or runtime policy authorizes parallel workers. Keep
synthesis, coupled design choices, and tasks that share mutable state in one
context. Browser sessions and other singleton resources remain serialized.

An independent worker at a decision point returns options and a recommendation
but does not exercise authority it was not granted. Resume a stalled worker
with the established facts and a finish-only request before replacing it. All
worker output is inspected before it enters project evidence.

## Scope and change control

- Finish the named atomic task. Pre-existing bugs, performance issues, missing
  documentation, and unrelated cleanup become follow-ups unless the requested
  behavior cannot work without them.
- Edit the smallest relevant region. Preserve unrelated working-tree changes
  and show diffs for author prose.
- Deleting research files, force-pushing, and overwriting data in place require
  explicit authorization at the time of action. Replacement artifacts are
  verified end to end before an old version is retired.
- Never infer sign-off from a question or request for clarification. Record the
  exact approved option and its scope.
- A known implementation ceiling receives a comment naming the ceiling and the
  upgrade condition.

## Verification and thresholds

Every non-obvious threshold and default carries a one-line literature basis or
a labeled judgment rationale. Search terms and candidate values come from the
source index, field list, schema, or documented vocabulary. A failed exact
search is reported; do not silently switch to a remembered near-synonym.

Fresh verification precedes a claim that a build, test, analysis, stage,
handoff, or release passed. The evidence includes the command or procedure,
the inspected output, the time, and any omitted checks.
