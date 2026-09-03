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
├── methods/                             focused causal method packs
├── references/                          decision trees, checklists, standards
├── scripts/validate_governance.py       publication-eligibility validator
└── templates/                           status, evidence, governance, review records
skills/*/SKILL.md                        focused research operations
runtime-profile.example.yaml            portable local-tool configuration
presentation-tooling/                    shared Quarto theme and deterministic gates
agents/tikz-reviewer.md                  rendered-figure review contract
THIRD_PARTY_NOTICES.md                   imported-source attribution and licenses
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

The stage router loads only the active stage and selected method pack. Focused companion skills
handle source retrieval, literature review, bibliography audits, preregistration, adversarial
review, referee responses, replication release, LaTeX, and presentation production. Their outputs
enter the same evidence, decision, and governance registry rather than creating a parallel state.

## Capability map

| Research operation | Focused skill or location |
|---|---|
| Known paper, DOI, or author | `research-sources` |
| Topic-level synthesis | `literature-review` |
| Existing BibTeX verification | `bibliography-audit` |
| Prospective commitment | `preregister` |
| Causal design and estimation | `empirical-workflow/methods/<selected-method>/` |
| Independent adversarial panel | `research-council` |
| Full draft review | `manuscript-review` |
| Decision-letter response | `referee-response` |
| Staged reproducibility archive | `replication-release` |
| LaTeX diagnostics and figures | `latex-production` |
| Research and teaching decks | `research-talk`, `teaching-lecture` |
| Rendered slide audit | `slide-review` |
| Course website | `course-site` |

A common project sequence is `research-sources → literature-review → preregister → method pack`.
Near release, use `manuscript-review → referee-response → replication-release`. These are routing
defaults, not permission to skip stage exits or mandatory pauses.

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
cp runtime-profile.example.yaml /path/to/project/runtime-profile.yaml
mkdir -p /path/to/project/.claude/skills /path/to/project/.agents/skills
cp -r skills/* /path/to/project/.claude/skills/
cp -r skills/* /path/to/project/.agents/skills/
cp -r presentation-tooling agents /path/to/project/
```

User level, available in every project:

```
cp -r skills/* ~/.claude/skills/
cp -r skills/* ~/.agents/skills/
```

`CLAUDE.md` is loaded on every turn, so it is kept short deliberately. The stage
files are loaded only when the stage runs. This is the reason the kit is split
rather than written as one large instruction file: a long always loaded file
dilutes attention across the whole session and pays a context cost on every
turn.

For Codex, install the repository skill at
`.agents/skills/empirical-workflow/SKILL.md` using the second copy command
above, then start Codex from the project root. `AGENTS.md` instructs Codex to
load the `empirical-workflow` skill; the discovered skill's router selects the
current stage. Claude Code uses the corresponding `.claude/skills/` copy.

Fill `runtime-profile.yaml` with local cache, PDF helper, browser, manuscript-root, and
presentation-asset paths. Do not put those paths into `CLAUDE.md`, `AGENTS.md`, method prompts, or
the protocol. Preserve `THIRD_PARTY_NOTICES.md` when redistributing adapted prompts or tooling.

## Bootstrap and handoff

1. Fill out `research.yaml`, including the locked `analysis_input_contract`
   before a Python export is consumed by R, then create `_status.md` and
   `decision-log.md` from the supplied templates.
2. Start the appropriate staged workflow and complete its required artifacts.
3. Create an evidence card for every material source, decision, diagnostic, and
   result. Each card links a claim to its source artifact and states its method,
   limitation, and unresolved uncertainty.
4. Before a new runtime continues the work, it reads `RESEARCH_PROTOCOL.md`,
   `research.yaml`, `_status.md`, the most relevant/current evidence card, and
   the tail of `decision-log.md`, in that order.

The governance registry is the machine-readable release view of pipelines, claims, figures,
acceptance gates, applicability, and reconciliation. Validate it before circulation. For a
replication archive, packaging follows a successful reproduction attempt; complete current
official policy verification and a confidentiality/redistribution check before writing the final
archive.

See [the v2 migration guide](docs/v2-migration-guide.md) for moving an existing
project and converting a v1 `_status.md` record.

## Development

Create the complete repository-local test environment before running checks:

```bash
bash tests/bootstrap_test_environment.sh
```

The bootstrap creates `.venv`, installs the Python test dependencies (including
PyArrow), and installs the smoke-test R packages (`arrow`, `yaml`, `fixest`, and
`modelsummary`) into `.r-lib`. It requires Python 3, R, and network access to
CRAN. The smoke runner only uses `.venv/bin/python`; it never falls back to the
system Python and never installs dependencies implicitly.

Run either formal checkpoint through the same repository-local environment:

```bash
tools/validate_registry <registry> --checkpoint B
tools/validate_registry <registry> --checkpoint C
```

The wrapper reports the bootstrap command if `.venv` is absent.

Run the workflow contract tests with the project-local command:

```bash
bash tests/run_contract_tests.sh
```

### Python-R smoke test

The cross-runtime smoke test uses the repository-local `.venv` and `.r-lib`
prepared above. It generates a
deterministic 96-row staggered-treatment panel, validates its Python-to-R
contract (including its versioned merge audit), estimates a fixed-effects
event-study model, and writes a simulated-results table. It also recovers a
cross-runtime handoff from durable state in the required read order and proves
that a failed identifying diagnostic writes a mandatory-pause record and blocks
formal estimation.

```bash
bash tests/smoke/run_smoke.sh
```

The runner starts from the repository root and prepends `.r-lib/` to `R_LIBS`
when that repository-local library exists.
Before generating data or invoking the workflow verifier, it confirms the local
Python dependencies and checks each R package in a separate R process. If the
environment is absent, incomplete, or a package cannot load safely, it stops
with the bootstrap command instead of treating an R package failure as a
workflow failure.

The command intentionally invokes the R verifier with a failed identifying
diagnostic, an invalid row count, and a mismatched project identity. Those
invocations must stop with their documented errors; the shell runner treats
the expected failures as passing mandatory-stop checks.

## Design decisions worth knowing before editing

1. **Checkpoints are gates, not summaries.** Their value comes entirely from
   refusing to proceed. Softening them into progress reports removes the point.
2. **The main specification is locked before estimation.** The Specification
   discipline section of `RESEARCH_PROTOCOL.md` and section 4 of the status
   template make specification drift visible without prohibiting labeled
   exploration.
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
- `RESEARCH_PROTOCOL.md` Authority levels and Mandatory pause sections: add
  project-specific decision boundaries without duplicating them in an adapter.
