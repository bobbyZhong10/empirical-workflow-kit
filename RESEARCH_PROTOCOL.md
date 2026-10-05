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
remaining risks, and the next stage. Use question, evidence, and inference as the unit of progress. Before each
analysis module, state the economic question and its importance, the competing
explanations, what the data observe and the design can distinguish, and what
result would change the current judgment. At its end, state what was learned,
what remains indistinguishable, and whether further work could change a decision.
Keep these short entries in the existing Evidence card, not a new register.
Coefficients, standard errors, prediction counts, and gate verdicts alone cannot
complete a module. Measurement, description, institutional accounting, and
conditional models can answer valuable questions without being causal designs.
Do not treat a stage as complete merely
because code ran. Research scripts are numbered and direct: their filenames
make execution order clear, and each script has one plainly stated purpose.

## Checkpoints

Checkpoints are gates. They require the specified evidence, a status update,
and a decision to proceed, revise, or pause. A current unresolved failure returns work to the responsible stage. Classify
its root cause before acting: repair computation, reconsider design, correct or
withdraw an inference, improve exposition, or disclose an intrinsic data limit.
A historical failure is retained with a reasoned, evidence-linked disposition:
active against a current claim, resolved by repair, closed by claim withdrawal,
or retained as a disclosed limitation. A disclosed limitation can close an issue
only when the remaining claim is supported; disclosure cannot rescue a design
that does not support that claim. Existing gate closure and authorization rules
apply, and closure is never a retroactive pass. Checkpoints A and B authorize their next analysis phases;
Checkpoint C is the final writing, delivery, and release-readiness gate.

## Specification discipline

Define and version the main specification before interpreting results. Separate
confirmatory work from exploration, label deviations, and record their
rationale and timing in `decision-log.md`. Do not promote a result-dependent
choice to the main specification without a Mandatory pause decision.

## Runtime parity

Two runtimes execute this workflow. What makes them the same workflow is not
their instruction files but `tools/validate_registry.py`: the same registry
produces the same verdict whoever runs it, and no instruction file can soften a
check.

- `CLAUDE.md` and `AGENTS.md` carry a generated block that is identical in both,
  bounded by `<!-- shared-contract -->` markers. Only the runtime notes beneath
  it may differ, and a test in the kit compares the two blocks byte for byte.
- The workflow carries one version number, defined once in
  `tools/validate_registry.py` and reported by
  `tools/validate_registry --version`. The wrapper always uses the
  repository-local Python environment created by the documented bootstrap.
- Every registry records `kit_version`. The scaffold writes it; the validator
  reports `KIT_VERSION_UNDECLARED` or `KIT_VERSION_MISMATCH` and blocks at
  Checkpoint C, so a project cannot be carried forward under rules it was never
  checked against, and a verdict always names the rules that produced it.

A gated milestone requires zero mechanical blocking findings from its applicable
checkpoint, but this is not a sufficient research completion criterion. Report
the count with its scope. Separately assess data/code reproducibility, credibility
of current claims, readiness for scholarly discussion, and submission delivery.
A draft can be ready for discussion while submission requirements remain open;
external circulation still requires the recorded authority decision. Automated
validation does not certify source support, identification, contribution, or
reader comprehension. Regexes and anchors check limited patterns and locations,
not proposition meaning. Substantive review and editorial cold reading remain
independent of the mechanical verdict.

## Language

Communicate with the user in the primary language they use at the start of the
conversation. Infer it from the first substantive request rather than a greeting
or quoted material, keep using it when later messages mix languages, and switch
only when the user explicitly asks. If the opening request has no clear primary
language, use the language in which the user states the task. Write all durable
repository artifacts, including prose, metadata, code comments, and handoffs,
in English.

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
is what "finished" means, and Checkpoint C enforces it. Checkpoint C requires at
least one `kind: submission` output and a nonempty, resolvable
`manuscript_sources` list for each submission; omitting either is blocking.

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
`OUTPUT_DIRECTORY_EMPTY`, `OUTPUT_DATA_NOTE_MISSING`, `OUTPUT_PDF_MISSING`,
`OUTPUT_LATEX_SOURCE_MISSING`, `OUTPUT_TABLE_EXPORT_MISSING` and
`OUTPUT_FIGURE_EXPORT_MISSING` against this contract, and `OUTPUT_DELIVERY` as
the summary. Exhibits are counted by their `\label`, not by the environment
they are wrapped in, and exports may live in nested result directories.

## Evidence records

Create an Evidence card for every material factual claim, design choice, data
source, diagnostic, and result used to support a conclusion. Each card links to
its source artifact, records the method and date, distinguishes observation
from inference, and identifies any limitation or unresolved uncertainty.

## Public documentation boundary

Public repository documentation records publishable decisions and verification
using repository-relative paths. Do not copy personal filesystem locations,
private project identifiers, unpublished findings, reviewer correspondence, or
private-source hashes into public logs, examples, status files, or handoffs.
Keep necessary restricted provenance in an appropriate private project record,
not a public appendix. Label hypothetical examples and disclose when motivating
inputs are unavailable to public readers; do not present them as reproducible
public evidence. Preserve decision substance when authorized privacy redaction
is needed, and record the redaction without reproducing the removed details.

## Independent review

The Quality auditor reviews the relevant evidence and implementation without
relying solely on the Executor's summary. The review checks traceability from
claim to Evidence card, adherence to the approved specification, identifying
assumptions and diagnostics, and whether limitations are stated proportionally.
Record findings and required follow-up in `decision-log.md`.

## Research judgment and verification

Before adding work, state which economic uncertainty or current judgment it
could change. A registry slot, gate, or reviewer request is not itself a research
reason. Stop homogeneous revision when core defects are repaired and evidence
boundaries are accurate. Reopen only for new evidence, a specific unresolved
error, or reader feedback that could change the argument. Data limits that
cannot be resolved by available evidence do not justify endless checks or
qualifiers. Seek external reader feedback on whether the contribution matters,
subject to circulation authority. Inspect the underlying object before classifying
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

Across every supported method and evidence strategy, organize the paper around
the question, evidence, economic meaning, and knowledge increment. The selected
method determines technical obligations, not the paper's story. Use the shared
`references/research-writing.md` contract before interpreting results as well as
before writing. It distinguishes findings, behavioral explanations, contributions,
and decision implications; apply it to measurement, description, experiments,
observational designs, prediction/measurement components, and conditional models.
Do not force theoretical novelty, strategic intent, or a policy prescription onto
evidence that answers a different useful question.

Every substantive claim must be supported by a citation, registered evidence,
a reported figure, or an explicit argument. Effect statements give direction,
magnitude, and a meaningful benchmark. Statistical significance never stands
in for substantive size.

Put a limitation beside the choice or result it constrains. State whether the
limitation comes from the data, design, method, or model and name its cost in
power, identification, scope, or generalizability. Disclose material deviations affecting interpretation, with their reason and
timing where they first matter. Keep the decision-log reference and complete
history internally. The manuscript need not narrate routine revisions.

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

## Internal records and reader-facing claims

Keep prediction identifiers, gate verdicts, registry and ledger vocabulary,
unused-design defenses, and immaterial exploration or repair history in internal
records. Traceability does not require printing every traceable number. The paper
selects the numbers needed for its argument, magnitude, and uncertainty.

Review each important proposition against its actual basis: observation,
statistical estimate, identity, model derivation, or conditional scenario, plus
the assumptions needed to reach its interpretation. Labels alone cannot enforce
a boundary. Use precise wording and necessary conditions in prose, without
repeating evidence labels or disclaimers in each paragraph.

Preserve cross-version constraints in the current paper story and status, linked
to decisions: advisor requirements, withdrawn propositions and reasons, settled
variable meanings and forbidden inferences, current contribution, main result,
and unresolved questions. Review these before revising. The decision log remains
the sole append-only history; withdrawal must survive paraphrase.
