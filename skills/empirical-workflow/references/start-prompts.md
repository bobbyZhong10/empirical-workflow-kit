# Workflow Start Prompts

Use one of these prompts from the root of a project initialized with Empirical
Workflow Kit. The mode selects an execution posture; it does not change the
research contract, weaken a checkpoint, or grant authority for external
publication, submission, communication, or destructive actions.

For an external project, this file is exposed as `WORKFLOW_START.md`. In the kit
checkout, its canonical path is named by
`workflow.manifest.yaml:canonical_source.start_prompts`.

## Choose a mode

| Situation | Mode |
|---|---|
| Start a new project or carry an existing project through all remaining stages | `AUTONOMOUS_WITH_RED_LINES` |
| Resume after Claude/Codex handoff, context loss, interruption, or partial prior work | `TAKEOVER_AND_RESUME` |

`AUTONOMOUS_WITH_RED_LINES` is the highest supported autonomy level. It means
that routine and reversible work continues without step-by-step confirmation;
it never means ignoring a mandatory pause or inventing research authority.

## Autonomous execution prompt

Copy the block below and replace the bracketed project-specific fields. Keep
constraints short; the repository already contains the operating contract.

```text
Use Empirical Workflow Kit in AUTONOMOUS_WITH_RED_LINES mode.

Objective: [state the concrete research outcome]
Starting point: [new project, or summarize the work already present]
Priority: [for example, reproduce and verify the data pipeline before writing]
Constraints: [project-specific boundaries; preserve existing user-authored work]

Work from this repository's durable state, not from assumptions or conversation
memory. Resolve canonical paths from workflow.manifest.yaml. Read
RESEARCH_PROTOCOL.md, research.yaml, and the empirical-workflow router before
substantive work. Communicate with me in the primary language of my first
substantive request and write every repository artifact in English.

Run the runtime doctor and the applicable Claude/Codex parity check. Inspect the
working tree and inventory existing data, code, results, manuscript files,
evidence, decisions, and status before changing anything. Preserve raw data,
existing project instructions, user-authored prose, and unrelated changes.
Determine the real current stage from both the records and the artifacts; do
not trust a stage label that the files contradict.

If an existing data or analysis pipeline is present, reproduce its baseline
before extending it. Compare identity, schema, row counts, keys, merge audits,
outputs, and material numerical results, and record any discrepancy. Reuse
valid completed work instead of rebuilding it. If required project fields are
missing and the answer would change the design, authority, sample, outcome, or
identifying strategy, ask one consolidated question and record the answer.
Otherwise make only reversible, explicitly recorded assumptions.

Proceed automatically through the applicable stages, checks, literature and
theory work, analysis, writing, and internal review needed for the objective.
At every stage exit, update the evidence, decision log, status, validation
result, risks, and next action. A gated milestone is complete only when its
applicable executable checkpoint reports zero blocking findings. Do not run
final Checkpoint C before Stage 7 is complete.

Pause only when RESEARCH_PROTOCOL.md requires it, when required access or
evidence is unavailable, or when continuing would require new authority. A
pause must name the trigger, affected artifacts, options, and exact decision
needed to resume. Do not publish, submit, message third parties, overwrite raw
data, or make a material design change without the required authority.

Continue until the objective is complete or a genuine mandatory pause is
reached. At completion, report changed artifacts, commands and checkpoint
counts, remaining limitations, and the next optional action.
```

## Takeover and resume prompt

Use this mode even when the same runtime resumes after context compaction. A
handoff is useful when present, but the durable project records remain
authoritative.

```text
Use Empirical Workflow Kit in TAKEOVER_AND_RESUME mode.

Objective: [state what should be resumed or completed]
Known interruption or handoff: [path or short description, if any]
Constraints: [project-specific boundaries; preserve existing user-authored work]

Do not restart the project or create a second workflow state. Resolve canonical
paths from workflow.manifest.yaml. Communicate with me in the primary language
of my first substantive request and write every repository artifact in English.

Recover state by reading, in this order: RESEARCH_PROTOCOL.md, research.yaml,
_status.md, the current evidence card named there, and the tail of
decision-log.md. Then read the latest relevant handoff record if one exists.
Read the empirical-workflow router and only the stage and reference files needed
for the recovered current task.

Inspect the working tree and compare the recorded status, current stage,
completed outputs, open risks, mandatory pause, and next action against the
actual files. Run the runtime doctor, the applicable Claude/Codex parity check,
and the checkpoint appropriate to the recovered phase. Treat stale or
contradictory records as findings: preserve the underlying artifacts, correct
the replaceable status record, and append any material resolution to
decision-log.md.

Resume from the first unverified atomic task. Do not rerun valid completed work
unless an input, dependency, contract, or downstream artifact is stale; record
the reason when rerunning is necessary. Do not silently revive an abandoned
approach or overwrite another runtime's unfinished changes. Preserve the same
evidence, language, R-first, checkpoint, and mandatory-pause rules as any other
workflow run.

After recovery, continue autonomously through routine and reversible work until
the objective is complete or a genuine mandatory pause is reached. At the next
handoff or completion, update durable state and report the recovered stage,
work reused, work rerun, changed artifacts, validation and checkpoint counts,
open risks, and next action.
```
