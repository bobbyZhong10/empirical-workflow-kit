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

**Workflow version: {KIT_VERSION}.** Every project records `kit_version` in its
registry, and `tools/validate_registry.py` blocks at Checkpoint C when the two
disagree. Check with `tools/validate_registry --version`.

This repository uses [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) as its
portable research contract. Before acting, read it and the active
`research.yaml` (or [research.example.yaml](research.example.yaml) until a
project configuration exists).

Speak with the user in Chinese. Write all repository artifacts in English.

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
"""

RUNTIMES = {
    "CLAUDE.md": (
        "# Claude Runtime Adapter",
        """## Runtime notes

Claude loads `skills/empirical-workflow/` as a skill and routes through its
stage file. Claude keeps its reasoning in the conversation; nothing durable may
live there. Where a task list is used it reflects the stages above, not a
parallel plan.
""",
    ),
    "AGENTS.md": (
        "# Codex Runtime Adapter",
        """## Runtime notes

Codex has no skill mechanism. Read `skills/empirical-workflow/SKILL.md` and the
stage files as ordinary repository files, by path. Keep project state in
repository artifacts rather than in task context, and preserve unrelated
working-tree changes while implementing the assigned task.
""",
    ),
}

for name, (title, notes) in RUNTIMES.items():
    Path(name).write_text(f"{title}\n\n{SHARED}\n{notes}", encoding="utf-8")
print("wrote", ", ".join(RUNTIMES))
