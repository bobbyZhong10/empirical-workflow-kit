# Development and architecture

[Documentation index](README.md) · [Project home](../README.md)

Run commands from the kit checkout unless a step explicitly changes directories.

## One workflow, two runtimes

There is exactly one editable implementation:

```text
skills/                              canonical skill source
├── empirical-workflow/             staged research workflow
└── <focused-operation>/            literature, review, release, slides
.claude/skills/<name>                relative link to ../../skills/<name>
.agents/skills/<name>                relative link to ../../skills/<name>
```

`workflow.manifest.yaml` inventories every managed skill, records the workflow
version, identifies the primary upstream baseline, and declares all runtime
views. The files under `.claude/skills/` and `.agents/skills/` are discovery
views only. Never edit them. A change to `skills/` is immediately visible to
both runtimes.

After preparing the development environment below, verify this invariant with:

```bash
.venv/bin/python scripts/verify_runtime_parity.py --project --all --repo .
```

The command fails on missing links, wrong targets, broken links, copied
implementations, stale managed entries, and version mismatches.

## Repository map

```text
RESEARCH_PROTOCOL.md                 portable research contract and red lines
workflow.manifest.yaml               canonical-source and runtime-view manifest
research.example.yaml                project configuration template
runtime-profile.example.yaml         machine-specific tool and path template
upstream.lock.yaml                   machine-readable upstream source ledger
CLAUDE.md                            thin Claude Code runtime adapter
AGENTS.md                            thin Codex runtime adapter
skills/empirical-workflow/
├── SKILL.md                         stage and operation router
├── stages/                          stage input/output contracts
├── methods/                         identification-specific prompt packs
├── references/                      shared standards and decision rules
├── scripts/                         governance checks
└── templates/                       durable project records
skills/*/                            focused operations outside the stage core
agents/tikz-reviewer.md              rendered-figure review contract
presentation-tooling/                Quarto theme, staging, and visual gates
tools/validate_registry.py           shared checkpoint validator
scripts/                             runtime-view installation and verification
scripts/bootstrap_project.py         safe attachment for an existing project
scripts/ewf.py                       runtime profile loader, doctor, and tool runner
examples/                            executable talk and lecture acceptance fixtures
tests/                               contracts, validators, scanners, and smoke test
THIRD_PARTY_NOTICES.md               licenses and imported-source notices
docs/upstream-absorption-audit.md    upstream-to-canonical absorption record
```

The repository is the source of truth for project state. Conversation history
is not a research record.

## Development environment

Prerequisites:

- Python 3.11 or newer
- R 4.1 or newer
- network access during dependency bootstrap
- Node 22 or newer for presentation gates
- Quarto 1.10 or newer for deck rendering
- TeX Live or MacTeX with `latexmk` for LaTeX production

Create the repository-local test environment:

```bash
bash tests/bootstrap_test_environment.sh
```

The bootstrap creates `.venv`, installs the dependencies specified in
`requirements-dev.txt` (a mix of version ranges and unpinned packages), and
installs `arrow`, `yaml`, `fixest`, and `modelsummary` into `.r-lib`. The test
runner never silently falls back to a system Python or installs packages during
a workflow test.

Run the automated checks required for the affected components:

```bash
.venv/bin/python -m pytest -q
bash tests/run_contract_tests.sh
bash tests/smoke/run_smoke.sh
bash tests/smoke/run_presentation_smoke.sh
.venv/bin/python scripts/verify_runtime_parity.py --project --all --repo .
```

The smoke runner intentionally invokes several failing cases. Those cases pass
only when the workflow blocks them with the documented errors.

The presentation smoke renders both neutral examples and then runs the fit,
staging, and offline gates. If the default Node installation is unavailable,
set `EWF_NODE_COMMAND` to a working Node 22+ executable or configure
`presentation.node_command` in the ignored runtime profile.

## Upstream update audit

The absorption mapping is executable:

```bash
.venv/bin/python scripts/audit_upstream.py --offline
.venv/bin/python scripts/audit_upstream.py --fail-on-change
```

The offline command verifies that every destination declared in
`upstream.lock.yaml` exists. The online command compares the pinned Git object
IDs with the primary upstream's `HEAD`, reporting unchanged, changed, missing,
or inconsistent source objects alongside local destination checks. The lock
tracks the original absorption baseline; subsequent selective adaptations and
additional sources are documented in
[the upstream audit](upstream-absorption-audit.md). Consequently,
`--fail-on-change` can report differences even when selected parts were reviewed.
It does not audit every reference repository listed below.

