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
| One generic causal prompt | A selectively loaded method pack with prompt, canon, details, and R template |
| Ad hoc paper lookup and citation checks | `research-sources`, `literature-review`, and `bibliography-audit` |
| Informal commitments and release decisions | `preregister`, governance registry validation, and recorded gates |
| Chat-only critique or R&R drafting | `research-council`, `manuscript-review`, and pin-verified `referee-response` records |
| Hand-built submission archive | `replication-release` with policy verification, confidentiality review, scans, and manifest |
| Personal LaTeX/slide paths in global instructions | `runtime-profile.yaml`, `latex-production`, `research-talk`, `teaching-lecture`, `slide-review`, and `course-site` |

## Bootstrap a new cross-runtime project

1. Copy `RESEARCH_PROTOCOL.md`, `research.example.yaml` as `research.yaml`,
   all needed `skills/`, `runtime-profile.example.yaml` as `runtime-profile.yaml`,
   `presentation-tooling/`, `agents/`, `THIRD_PARTY_NOTICES.md`, and the adapter for each intended runtime.
2. Copy `CLAUDE.md` when using Claude Code and `AGENTS.md` when using Codex.
   Keep both if the project will switch runtimes.
   Install the skill in the runtime-specific location: copy it to
   `.claude/skills/empirical-workflow/` for Claude Code and to
   `.agents/skills/empirical-workflow/` for Codex. Start Codex from the project
   root so it discovers `SKILL.md`; `AGENTS.md` then routes empirical work to
   the `empirical-workflow` skill.
3. Create `_status.md`, `decision-log.md`, and the appropriate evidence-card
   directory from the included templates. Fill `research.yaml` before work
   begins; lock `analysis_input_contract` before R consumes a Python export.
   Initialize a governance registry when the project has confirmatory claims, acceptance gates,
   multiple analysis pipelines, or outputs intended for circulation.
4. Start through the workflow router. The active runtime reads the portable
   protocol and project record, then loads only the current stage contract.
5. At a handoff, finish an atomic task, write the decision and evidence,
   update status, and record changed artifacts, open risks, next action, and
   unresolved mandatory pauses.

## Operating sequence after migration

For discovery and design, the default route is `research-sources → literature-review → preregister
→ method pack`. A known paper uses `research-sources`; a topic uses `literature-review`; an existing
BibTeX database uses `bibliography-audit`. Stage 6a loads only the locked method pack and registers
any departure from its dated canon.

For writing and release, use `manuscript-review → referee-response → replication-release`.
`research-council` is available for a bounded adversarial panel before a full manuscript exists.
The release sequence requires a reproduction attempt, current official policy verification,
confidentiality and redistribution decisions, safety scans on source inputs, sanitization only on
staging copies, and a checksum manifest. Packaging by itself is not reproducibility certification.

LaTeX and presentation work is routed through `latex-production`, `research-talk`,
`teaching-lecture`, `slide-review`, and `course-site`. Their executables and assets come from
`runtime-profile.yaml`; migrate local paths there rather than into an adapter or prompt.

## Migrate an existing `_status.md` project

1. Preserve the v1 status file; make a dated copy if its format must change.
2. Create `research.yaml` from the example and record the actual observation
   unit, languages, target outlets, current stage, approval mode, and expected
   analysis-input contract identity.
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

## Reproducible validation

Run static workflow contracts through the repository-local virtual environment:

```bash
bash tests/run_contract_tests.sh
```

Run the Python-R smoke test with one command:

```bash
bash tests/smoke/run_smoke.sh
```

The smoke runner resolves the repository root and automatically uses `.r-lib/`
when present. It otherwise uses the active R library, which must contain
`arrow`, `yaml`, `fixest`, and `modelsummary`; the active Python 3 must contain
PyArrow.

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
| Source discovery and bibliography | `research-sources`; `literature-review`; `bibliography-audit` |
| Prospective commitments and claim governance | `preregister`; governance registry templates and validator |
| Method-specific causal execution | `skills/empirical-workflow/methods/`; Stage 6a selective routing |
| Review, response, and replication release | `research-council`; `manuscript-review`; `referee-response`; `replication-release` |
| LaTeX and presentation production | `latex-production`; `research-talk`; `teaching-lecture`; `slide-review`; `course-site`; `presentation-tooling/` |
