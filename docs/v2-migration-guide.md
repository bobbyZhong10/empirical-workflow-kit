# Migrating to Empirical Workflow v2

V2 keeps the project-facing workflow intentionally plain: durable files, direct
numbered research scripts, and a thin adapter for the runtime currently doing
the work. It does not require rewriting a completed project or discarding v1
history.

## What remains from v1

Keep the project data, numbered analysis scripts, paper, citations, prior
outputs, and the existing `_status.md` as historical evidence. Keep any useful
v1 skill customizations, especially outlet-specific literature sources,
robustness checks, and structural-model tooling. Do not overwrite raw data or
silently replace old results; version any regenerated artifact.

## V2 replacements and additions

| V1 practice or file | V2 artifact or practice |
|---|---|
| A large runtime instruction file | `RESEARCH_PROTOCOL.md` plus a thin `CLAUDE.md` and/or `AGENTS.md` adapter |
| Chat summary as project state | `research.yaml`, `_status.md`, evidence cards, and append-only `decision-log.md` |
| Free-form stage notes | Stage contracts in `skills/empirical-workflow/stages/` with inputs, actions, artifacts, red lines, and exit conditions |
| Unstructured source or result notes | Literature maps and evidence cards in `skills/empirical-workflow/templates/` |
| Informal Python-to-R transfer | Parquet plus a versioned data contract and merge audit |
| Estimation before recorded validation | R contract validation, identification diagnostics, and mandatory-stop routing |

## Bootstrap a new cross-runtime project

1. Copy `RESEARCH_PROTOCOL.md`, `research.example.yaml` as `research.yaml`,
   `skills/empirical-workflow/`, and the adapter for each intended runtime.
2. Copy `CLAUDE.md` when using Claude Code and `AGENTS.md` when using Codex.
   Keep both if the project will switch runtimes.
3. Create `_status.md`, `decision-log.md`, and the appropriate evidence-card
   directory from the included templates. Fill `research.yaml` before work
   begins.
4. Start through the workflow router. The active runtime reads the portable
   protocol and project record, then loads only the current stage contract.
5. At a handoff, finish an atomic task, write the decision and evidence,
   update status, and record changed artifacts, open risks, next action, and
   unresolved mandatory pauses.

## Migrate an existing `_status.md` project

1. Preserve the v1 status file; make a dated copy if its format must change.
2. Create `research.yaml` from the example and record the actual observation
   unit, languages, target outlets, current stage, and approval mode.
3. Convert the latest status facts into the v2 status template: completed
   work, artifacts, validation, risks, next action, and active pause.
4. Add past material design choices and their rationale to `decision-log.md`.
   Mark reconstructed entries as historical rather than pretending they were
   contemporaneously logged.
5. Create evidence cards for the current data version, locked specification,
   key diagnostics, and reported results. Link to the original artifacts.
6. Validate the Python-to-R boundary before the next estimation run; do not
   retroactively overwrite prior data or estimates merely to fit v2 naming.

## Required handoff order

The receiving runtime reads these artifacts in order before it continues:

1. `RESEARCH_PROTOCOL.md`
2. `research.yaml`
3. `_status.md`
4. The most relevant/current evidence card
5. The tail of `decision-log.md`

The runtime then continues the current stage. It must not infer missing project
facts from the preceding Claude Code or Codex conversation.

## Approved-specification coverage

| Approved specification heading | Implemented artifact(s) |
|---|---|
| Status and purpose | `RESEARCH_PROTOCOL.md` purpose; `research.example.yaml` |
| Design principles | `RESEARCH_PROTOCOL.md`; `CLAUDE.md`; `AGENTS.md` |
| Repository architecture | `README.md` architecture diagram; `skills/empirical-workflow/` |
| Runtime adapters and project handoff | `CLAUDE.md`; `AGENTS.md`; `RESEARCH_PROTOCOL.md` handoff section |
| Roles and authority model | `RESEARCH_PROTOCOL.md` roles, authority, and pause sections |
| Stage protocol | `skills/empirical-workflow/SKILL.md`; all files in `stages/` |
| Literature and outlet positioning | `stages/stage2-lit-map.md`; `references/outlet-positioning.md`; literature-map template |
| Causal design protocol | `references/identification-decision-tree.md`; `stages/stage6a-reduced-form.md`; robustness checklists |
| Python-R workflow and data contract | Python and R standards; data-contract and merge-audit templates; `tests/smoke/` |
| Results and tables | `stages/stage7-writing.md`; evidence-card template; smoke table renderer |
| Audit, error handling, and recovery | `references/blindspot-audit.md`; protocol independent review; status and decision-log templates |
| Validation and implementation boundary | `tests/test_workflow_contract.py`; `tests/smoke/run_smoke.sh` |
