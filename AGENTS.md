# Codex Runtime Adapter

<!-- shared-contract: generated, identical in CLAUDE.md and AGENTS.md -->

**Workflow version: 2.5.** Every project records `kit_version` in its
registry, and `tools/validate_registry.py` blocks at Checkpoint C when the two
disagree. Check with `tools/validate_registry --version`.

This repository uses [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) as its
portable research contract. Before acting, read it and the active
`research.yaml` (or [research.example.yaml](research.example.yaml) until a
project configuration exists).

Communicate with the user in the primary language used in their first
substantive request. Keep that language unless the user explicitly asks to
switch. Write all repository artifacts in English.

## What makes the two runtimes the same workflow

Not these files. `tools/validate_registry.py` is the contract: the same
registry produces the same verdict whoever runs it, and no instruction file can
soften a check. Anything a runtime is told here that the validator does not
enforce is guidance; anything the validator enforces is binding on both.

Two checkpoints gate the work, and both are run by the same command:

```bash
tools/validate_registry <registry> --checkpoint B   # construction
tools/validate_registry <registry> --checkpoint C   # submission
```

A stage is not complete until its checkpoint returns zero blocking findings.
Report the count, not an impression of it.

The canonical `skills/` tree is the workflow source of truth; its inventory and
runtime views are declared by `workflow.manifest.yaml`. Claude Code and Codex
discover the same files through committed relative links under `.claude/skills`
and `.agents/skills`. Never edit those views or maintain a runtime-specific copy. Run
`scripts/verify_runtime_parity.py --project --all` before a handoff. If it
reports a stale user-level install, use `scripts/install_runtime_views.py`
rather than copying files by hand.

## Required reading, in order

1. `RESEARCH_PROTOCOL.md` for the contract, the language rule, and the delivery
   contract.
2. `skills/empirical-workflow/SKILL.md` for the stage router. Read only the
   stage file the current stage names.
3. The reference file that stage names, and no others.

The substantive rules live under `skills/empirical-workflow/`. They are
ordinary files: read them by path. In particular
`references/writing-standards.md` before drafting prose,
`references/delivery-contract.md` before calling a submission finished, and
`references/r-standards.md` before writing analysis code, because R is the
default language and any exception must be recorded in `decision-log.md`.

## Shared recordkeeping

Durable decisions, evidence, and status belong in repository artifacts, not in
runtime context. Update `_status.md` at each stage exit. Append to
`decision-log.md`, which is the sole append-only history. Create an evidence
card for every material factual claim, data source, design choice, diagnostic,
and result.

Resolve optional tools and machine-specific paths from `runtime-profile.yaml`,
or from `runtime-profile.example.yaml` until a project profile exists. Run
`scripts/ewf.py doctor` before relying on a configured capability and use
`scripts/ewf.py run <tool>` so the selected command and environment bindings
actually govern execution. Durable writing, execution, method-choice, and
code-review rules live in the focused references routed by the skill; do not
duplicate them in this adapter.

## Cross-runtime handoff

1. Finish the current atomic task and update its durable artifacts.
2. Record decisions and evidence, then update the project status.
3. Run both checkpoints and record the counts in the handoff.
4. Write a handoff with the completed stage, changed artifacts, open risks,
   next action, and unresolved pause.
5. Before continuing, the receiving runtime reads, in this order:
   `RESEARCH_PROTOCOL.md`, `research.yaml`, `_status.md`, the most
   relevant current evidence card, then the tail of `decision-log.md`.

<!-- end-shared-contract -->

## Runtime notes

Codex discovers `.agents/skills/empirical-workflow`, which resolves to the
canonical `skills/empirical-workflow/` tree, and routes through its stage file.
Named method facades in the same view route to the canonical Stage 6a packs.
Keep project state in repository artifacts rather than in task context, and
preserve unrelated working-tree changes while implementing the assigned task.
