"""Write CLAUDE.md and AGENTS.md from one shared body.

Two runtimes read two files, and nobody reads both, so any drift between them
is invisible until a project run by one runtime stops matching a project run by
the other. The shared block is generated into both and compared byte for byte
by ``tests/test_registry_validator.py``; only the runtime notes beneath it may
differ.

    python3 tools/render_runtime_adapters.py
"""

from pathlib import Path
import sys
sys.path.insert(0, "tools")
from validate_registry import KIT_VERSION

SHARED = f"""<!-- shared-contract: generated, identical in CLAUDE.md and AGENTS.md -->

**Workflow version: {KIT_VERSION}.** Every project registry records `kit_version`, and the
validator named by `workflow.manifest.yaml:canonical_source.registry_validator`
blocks at Checkpoint C when the two disagree. In the kit checkout that file is
`tools/validate_registry.py`. Check with the manifest-named `registry_cli` and
its `--version` option.

This repository uses [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) as its
portable research contract. Before acting, read it and the active
`research.yaml` (or [research.example.yaml](research.example.yaml) until a
project configuration exists).

Communicate with the user in the primary language used in their first
substantive request. Keep that language unless the user explicitly asks to
switch. Write all repository artifacts in English.

## What makes the two runtimes the same workflow

Not these files. The manifest-named registry validator is the contract: the same
registry produces the same verdict whoever runs it, and no instruction file can
soften a check. Anything a runtime is told here that the validator does not
enforce is guidance; anything the validator enforces is binding on both.

Two registry checkpoints are executable through the manifest-named command:

```bash
<registry_cli> <registry> --checkpoint B   # construction
<registry_cli> <registry> --checkpoint C   # final writing and delivery
```

A gated milestone is not complete until its checkpoint returns zero blocking
findings. Report the count, not an impression of it. Stage 6 instead exits
through the analysis-readiness record; final Checkpoint C follows Stage 7.

The canonical skill tree named by `workflow.manifest.yaml:canonical_source.skills_root`
is the workflow source of truth. Claude Code and Codex discover the same files
through relative links under `.claude/skills` and `.agents/skills`. Never edit
those views or maintain a runtime-specific copy. Run the manifest-named
`parity_cli` with `--project --all --repo .` before a handoff. If it reports a
stale user-level install, use the manifest-named `installer_cli` rather than
copying files by hand.

## Required reading, in order

1. `RESEARCH_PROTOCOL.md` for the contract, the language rule, and the delivery
   contract.
2. `<skills_root>/empirical-workflow/SKILL.md` for the stage router. Resolve
   `<skills_root>` from `workflow.manifest.yaml`, then read only the stage file
   the current stage names.
3. The reference file that stage names, and no others.

The substantive rules live under the manifest-named empirical-workflow skill.
They are ordinary files: read them by path. Within that skill, read
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
or from `runtime-profile.example.yaml` until a project profile exists. Run the
manifest-named `runtime_cli` with `doctor` before relying on a configured
capability and use it with `run <tool>` so the selected command and environment bindings
actually govern execution. Durable writing, execution, method-choice, and
code-review rules live in the focused references routed by the skill; do not
duplicate them in this adapter.

## Cross-runtime handoff

1. Finish the current atomic task and update its durable artifacts.
2. Record decisions and evidence, then update the project status.
3. Run the checkpoint applicable to the current phase and record its blocking
   count; do not run final Checkpoint C before Stage 7 is complete.
4. Write a handoff with the completed stage, changed artifacts, open risks,
   next action, and unresolved pause.
5. Before continuing, the receiving runtime reads, in this order:
   `RESEARCH_PROTOCOL.md`, `research.yaml`, `_status.md`, the most
   relevant current evidence card, then the tail of `decision-log.md`.

<!-- end-shared-contract -->
"""

RUNTIMES = {
    "CLAUDE.md": (
        "# Claude Runtime Adapter",
        """## Runtime notes

Claude discovers `.claude/skills/empirical-workflow`, which resolves to the
manifest-named canonical skill tree, and routes through its stage file.
Named method facades in the same view route to the canonical Stage 6a packs.
Claude keeps its reasoning in the conversation; nothing durable may live
there. Where a task list is used it reflects the stages above, not a parallel
plan.
""",
    ),
    "AGENTS.md": (
        "# Codex Runtime Adapter",
        """## Runtime notes

Codex discovers `.agents/skills/empirical-workflow`, which resolves to the
manifest-named canonical skill tree, and routes through its stage file.
Named method facades in the same view route to the canonical Stage 6a packs.
Keep project state in repository artifacts rather than in task context, and
preserve unrelated working-tree changes while implementing the assigned task.
""",
    ),
}

for name, (title, notes) in RUNTIMES.items():
    Path(name).write_text(f"{title}\n\n{SHARED}\n{notes}", encoding="utf-8")
print("wrote", ", ".join(RUNTIMES))
