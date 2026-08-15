# Empirical Workflow Kit

A thin `CLAUDE.md` plus a staged skill for panel data empirical research in
information systems economics. Reduced form and structural, targeting ISR,
MISQ, and Management Science.

## Contents

```
RESEARCH_PROTOCOL.md                     portable execution rules and red lines
research.example.yaml                    project start card; rename to research.yaml
CLAUDE.md                                Claude Code adapter, always loaded
skills/empirical-workflow/
├── SKILL.md                             stage router, checkpoints, backtracking
├── stages/                              one file per stage, loaded on demand
├── references/                          decision trees, checklists, standards
└── templates/status-template.md         the status log
```

## Install

At the project level, copy the portable protocol, one or both adapters,
`research.example.yaml` renamed to `research.yaml`, and the skill directory.
The same project can move between Claude Code and Codex: retain the protocol,
configuration, decision records, and skills, then use the adapter for the tool
currently running it.

```
cp RESEARCH_PROTOCOL.md /path/to/project/RESEARCH_PROTOCOL.md
cp research.example.yaml /path/to/project/research.yaml
cp CLAUDE.md /path/to/project/CLAUDE.md  # Claude Code adapter
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

## Development

Install test dependencies in a repository-local environment with
`python3 -m venv .venv && .venv/bin/python -m pip install -r requirements-dev.txt`.
Run the workflow contract tests with
`.venv/bin/python -m pytest tests/test_workflow_contract.py -q`.

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
