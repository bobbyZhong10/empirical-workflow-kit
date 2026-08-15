# Empirical Workflow Kit

A portable, staged workflow for panel-data empirical research in information
systems economics. It supports reduced-form and structural work targeting ISR,
MISQ, and Management Science, and can move cleanly between Claude Code and
Codex.

## Contents

```
RESEARCH_PROTOCOL.md                     portable execution rules and red lines
research.example.yaml                    project start card; rename to research.yaml
CLAUDE.md                                Claude Code adapter, always loaded
AGENTS.md                                Codex adapter
skills/empirical-workflow/
├── SKILL.md                             stage router, checkpoints, backtracking
├── stages/                              one file per stage, loaded on demand
├── references/                          decision trees, checklists, standards
└── templates/status-template.md         the status log
```

## Architecture

```text
Claude Code adapter (CLAUDE.md) ─┐
                                 ├─> RESEARCH_PROTOCOL.md ─> stage contracts
Codex adapter (AGENTS.md) ───────┘              │                   │
                                                v                   v
                         research.yaml, _status.md, decision-log.md, evidence cards
                                                │
                                                v
                              Python ETL ─ Parquet + contract ─ R estimation
```

The protocol contains the research rules. The runtime adapters only route
Claude Code or Codex into those rules. Durable artifacts—not a chat
conversation—are the project source of truth.

## Install

At the project level, copy the portable protocol, one or both adapters,
`research.example.yaml` renamed to `research.yaml`, and the skill directory.
Choose `CLAUDE.md` for Claude Code, `AGENTS.md` for Codex, or both for a
cross-runtime project. Retain the protocol, configuration, decision records,
and skills when changing runtimes.

```
cp RESEARCH_PROTOCOL.md /path/to/project/RESEARCH_PROTOCOL.md
cp research.example.yaml /path/to/project/research.yaml
cp CLAUDE.md /path/to/project/CLAUDE.md  # Claude Code adapter
cp AGENTS.md /path/to/project/AGENTS.md  # Codex adapter
cp -r skills/empirical-workflow /path/to/project/.claude/skills/
```

User level, available in every project:

```
cp -r skills/empirical-workflow ~/.claude/skills/
```

`CLAUDE.md` is loaded on every turn, so it is kept short deliberately. The stage
files are loaded only when the stage runs. This is the reason the kit is split
rather than written as one large instruction file: a long always loaded file
dilutes attention across the whole session and pays a context cost on every
turn.

## Bootstrap and handoff

1. Fill out `research.yaml`, then create `_status.md` and `decision-log.md`
   from the supplied templates.
2. Start the appropriate staged workflow and complete its required artifacts.
3. Create an evidence card for every material source, decision, diagnostic, and
   result. Each card links a claim to its source artifact and states its method,
   limitation, and unresolved uncertainty.
4. Before a new runtime continues the work, it reads `RESEARCH_PROTOCOL.md`,
   `research.yaml`, `_status.md`, the most relevant/current evidence card, and
   the tail of `decision-log.md`, in that order.

See [the v2 migration guide](docs/v2-migration-guide.md) for moving an existing
project and converting a v1 `_status.md` record.

## Development

Install test dependencies (`pytest` and PyYAML) in a repository-local environment with
`python3 -m venv .venv && .venv/bin/python -m pip install -r requirements-dev.txt`.
Run the workflow contract tests with
`.venv/bin/python -m pytest tests/test_workflow_contract.py -q`.

### Python-R smoke test

The cross-runtime smoke test requires Python 3 with PyArrow and R with the
`arrow`, `yaml`, `fixest`, and `modelsummary` packages. It generates a
deterministic 96-row staggered-treatment panel, validates its Python-to-R
contract (including its versioned merge audit), estimates a fixed-effects
event-study model, and writes a simulated-results table.

```bash
bash tests/smoke/run_smoke.sh
```

The command intentionally invokes the R verifier a second time with an invalid
contract. That invocation must stop with `Data contract validation failed`; the
shell runner treats that expected failure as a passing mandatory-stop check.

## Design decisions worth knowing before editing

1. **Checkpoints are gates, not summaries.** Their value comes entirely from
   refusing to proceed. Softening them into progress reports removes the point.
2. **The main specification is locked before estimation.** Rule 3 in `CLAUDE.md`
   and section 4 of the status template exist together to make specification
   drift visible rather than to prohibit exploration.
3. **Staggered adoption gets its own branch in the decision tree.** Without it
   the default output is two way fixed effects, which is the wrong main
   specification for most staggered settings.
4. **The blindspot audit is run by the same model that did the analysis** and
   therefore shares its blind spots. Cross model review is a separate step, and
   the identification section is the part that most needs it.
5. **The writing order is a control, not a style preference.** Writing the
   introduction last is what keeps the contribution claim tied to the results.

## What to customize first

- `references/r-standards.md`: package choices and the project layout.
- `stages/stage2-lit-map.md`: the literature search tools available to you.
- `references/robustness-checklists.md`: add the checks your target outlets and
  your advisors actually demand.
- `stages/stage6b-structural.md`: language and solver for structural work.
- `CLAUDE.md` Rule 2 table: add the failure modes you personally hit.
