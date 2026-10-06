# Kit maintenance status

- Updated: 2026-10-05.
- Workflow: 2.8, consistent across validator, manifest, and runtime adapters.
- Completed task: revise progression, validation, and writing rules around
  question, evidence, and inference across supported research methods.
- Follow-up completed: adjudication before repair, mechanical-only/background
  decisions, evidence dependence, actor/conflict cold read, and reader-judgment
  stopping rules. Existing review phrase gates were replaced.
- Cross-method sweep completed: shared organization, economic meaning,
  contribution and behavioral interpretation across all nine method packs and
  structural/noncausal stage paths; see migration transfer cases.
- Econometric workflow integration: identification review, rendered figures,
  research-code correctness and replication diagnosis; see upstream audit.
- Latest maintenance: README scope, installation and verification descriptions
  aligned with the implementation; upstream acknowledgments added.
  Validation: 34 contract tests passed; project parity reported zero errors.
- Current evidence: docs/evidence/workflow-2.8-iteration-review.md.
- Migration and illustrative scenarios: docs/workflow-2.8-migration.md.
- Handoff: docs/workflow-2.8-handoff.md.
- Research configuration: no active research.yaml; research.example.yaml remains
  an example, not an assertion that this maintenance task is a Stage 1 project.
- Research Checkpoints B/C: not applicable to kit maintenance. No empirical
  project was advanced or certified, and final C was not run on the kit.
- Open mandatory pause: none for this authorized maintenance task.

## Prior implementation verification

Full test suite: **448 passed**, no failures, using the existing repository .venv
through the manifest runtime CLI and a temporary test profile. `git diff --check`
is clean. Project and user parity checks both report **zero errors** for Claude
and Codex, version 2.8. The validator CLI reports `empirical-workflow 2.8`.

Runtime doctor: zero blocks, five unrelated optional/tool warnings (Node loader,
Quarto version, and three source credentials). No dependency installation or
runtime-view repair was necessary.

## Separate judgments

| Dimension | Current assessment |
|---|---|
| Data/code reproducibility | Kit test commands are reproducible in the existing test environment; no empirical pipeline was rerun. |
| Credibility of research claims | Software verification does not establish empirical claim validity. |
| Discussion readiness | Revised workflow and scenario replay are available for review; no independent manuscript cold read was performed in this maintenance task. |
| Submission delivery | Not applicable; this is a kit change, not a manuscript release. |

## Constraints and next action

Preserve immutable raw data, prospective interpretation, failure history,
reproduction, and the append-only decision log. Do not silently migrate an
existing project's kit_version or close its gates. Do not claim that passing
tests establishes improved paper quality or measured reductions in rework.

Concurrent Management Science template replacement is preserved; see its separate
decision and evidence record. This task does not claim authorship or validation
of that replacement. Shared adapter edits retain its updated template paths.

Stop further kit editing for this request. Reopen for a concrete regression or
prospective use/reader evidence; do not add another check merely to increase the
count. The next project can adopt 2.8 through the documented migration procedure.
