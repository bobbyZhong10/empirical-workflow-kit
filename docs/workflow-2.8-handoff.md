# Workflow 2.8 handoff

- Completed atomic task: economic question/evidence/inference workflow revision.
- Phase: kit maintenance, not a research-stage exit.
- Completed: 2026-10-05, America/New_York.
- Canonical changes: protocol and router; Stages 1, 3–7; focused execution,
  validation, robustness, writing, and delivery references; existing Evidence
  card, story, status, and handoff templates; manuscript-review and response
  repair guidance; validator reporting/severity; versioned adapters and fixtures.
- Historical evidence and acceptance: evidence/workflow-2.8-iteration-review.md
  and workflow-2.8-migration.md.
- Current-state record: ../_status.md; decisions: ../decision-log.md.

## Verification and result

The temporary `.research-state/kit-tests-runtime.yaml` profile binds Python to
the existing repository .venv. It is local runtime configuration, not a portable
project requirement. Commands executed from the kit root:

```sh
tools/validate_registry --version
.venv/bin/python scripts/ewf.py --profile .research-state/kit-tests-runtime.yaml doctor
.venv/bin/python scripts/ewf.py --profile .research-state/kit-tests-runtime.yaml run python -- -m pytest -q
.venv/bin/python scripts/ewf.py --profile .research-state/kit-tests-runtime.yaml run python -- scripts/verify_runtime_parity.py --project --all --repo . --json
.venv/bin/python scripts/ewf.py --profile .research-state/kit-tests-runtime.yaml run python -- scripts/verify_runtime_parity.py --user --all --repo . --json
git diff --check
```

Results: version 2.8; doctor zero blocks and five unrelated warnings; **447 tests
passed**; both parity reports have **zero errors**; diff whitespace check clean.
Raw execution logs are retained locally in .research-state/final-tests.txt and
the two parity JSON files. Research checkpoint counts are not applicable to this
task; B/C fixture tests are software validation, not certification of a paper.

The tests retain failures for corrupted numbers, missing sources/anchors, stale
dependencies, current successor failures, and incomplete gate closure. New tests
show advisory patterns do not alone make CLI failure, while a deliberately
corrupted figure value or disclosure anchor still does. Mechanical success
explicitly leaves reproduction, claim credibility, and reader understanding
unassessed.

## Risks, state, and next action

Existing projects need an explicit version migration; no external project was
modified. Historical v2.1/v2.2 design documents are retained as history, with the
new migration note identifying superseded lexical severity rules. Prior failures
need supported closure, not deletion or a relabeled pass.

The scenario replay and implementation review were performed by the implementer;
they are not an independent code review or manuscript cold read. Prospective
improvement in rework/clarity has not been measured. These limitations are
separate from the completed software tests and the installed rule changes.

Parallel Management Science template work, its evidence card, and decision-log
entry are preserved. Shared LaTeX-adapter edits were limited to separating
traceability from text display and limiting anchor-based assurance. No commit,
publication, or empirical project migration was performed.

Next action: use the migration note in the next authorized project. Stop further
homogeneous kit changes unless a specific regression or new reader/use evidence
would change the decision. No unresolved mandatory pause in this maintenance task.

## Follow-up completion: concrete historical feedback

Additional changed execution files:

- `skills/empirical-workflow/SKILL.md`
- `skills/empirical-workflow/stages/stage6a-reduced-form.md`
- `skills/empirical-workflow/stages/stage7-writing.md`
- `skills/empirical-workflow/references/execution-discipline.md`
- `skills/empirical-workflow/references/operational-quality-loop.md`
- `skills/empirical-workflow/references/research-writing.md`
- `skills/empirical-workflow/references/robustness-checklists.md`
- `skills/empirical-workflow/references/blindspot-audit.md`
- `skills/empirical-workflow/templates/evidence-card-template.md`
- `skills/empirical-workflow/templates/paper-story-template.md`
- `skills/empirical-workflow/templates/review-finding-template.yaml`
- `skills/empirical-workflow/templates/response-matrix-template.yaml`
- `skills/manuscript-review/SKILL.md`
- `skills/research-council/SKILL.md`
- `skills/referee-response/SKILL.md`

Updated maintenance artifacts: the existing change plan, migration/replay,
evidence card, this handoff, `_status.md`, and append-only `decision-log.md`.
No new checker, version, or state system. The user installation resolves to
this canonical skill tree, so these are changes to the actual execution path.

Follow-up verification: 447 tests passed (`.research-state/followup-tests.txt`);
both existing YAML templates parse; doctor has zero blocks/five unrelated
warnings; project and user parity have zero errors/no notices, version 2.8
(`followup-project-parity.json`, `followup-user-parity.json`); whitespace check
clean. The subsequent changes only refine review prose and maintenance records.
Manual historical replay now explicitly preserves mistaken reviewer premises,
correct criticisms, and unresolved causal/data limits. It does not claim an
independent manuscript reading or measured reduction in rework.

## Generalization completion

In addition to earlier changes, this round updated RESEARCH_PROTOCOL.md; the
router; Stages 1–7 as applicable; research-writing, method-facade-contract,
method-governance, identification-decision-tree, robustness, elite-IS, writing
standards and startup references; all nine method prompt.md files; causal-design
shared-rules.md and details.md; existing story, literature-map and status
templates; literature-review, preregister, research-talk, manuscript-review and
latex-production companion entries; and tests/test_workflow_contract.py.

The central contract now covers manuscript organization, economic meaning,
knowledge increment, behavioral explanations, and strategy-specific inferential
boundaries. New method extensions must use it, but still need a defensible method
and implementation review. Empirical method canons and R templates were not
revalidated or changed. The migration note records hypothetical transfer cases
across the supported work, distinct from congestion-pricing historical replay.

Verification: 448 tests passed in .research-state/generalization-tests.txt;
runtime doctor zero blocks/five unrelated warnings. The new test verifies direct
method-pack routing only, not interpretation quality. State and decisions remain
in existing artifacts. Stop here pending a concrete new issue or user request.


Generalization verification completed: project and user parity both zero errors.
The routing test accepted a valid temporary pack and rejected removal of its
shared-reference link; log: .research-state/generalization-routing-fault.txt.
This demonstrates wiring coverage only. Final diff whitespace check is clean.
