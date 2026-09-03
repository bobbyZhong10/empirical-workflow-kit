# Empirical Workflow Kit

Empirical Workflow Kit is a portable research operating system for Claude Code
and Codex. It turns an empirical project into a staged chain of contracts,
evidence, decisions, diagnostics, and release gates. Both runtimes discover the
same canonical skills and apply the same validator, so switching tools does not
fork the research method or the project record.

The kit is designed for panel-data, causal-inference, experimental, and
structural research in information systems, economics, and quantitative
marketing. Its conventions transfer to other empirical fields.

## One workflow, two runtimes

There is exactly one editable implementation:

```text
skills/                                      canonical skill source
├── empirical-workflow/                     staged research workflow
└── <focused-operation>/                    literature, review, release, slides
       │
       ├── .claude/skills/<name>            committed relative symlink
       └── .agents/skills/<name>            committed relative symlink
```

`workflow.manifest.yaml` inventories every managed skill, records the workflow
version, names the upstream commit that was inspected, and declares all runtime
views. The files under `.claude/skills/` and `.agents/skills/` are discovery
views only. Never edit them. A change to `skills/` is immediately visible to
both runtimes.

Verify this invariant at any time:

```bash
python3 scripts/verify_runtime_parity.py --project --all --repo .
```

The command fails on missing links, wrong targets, broken links, copied
implementations, stale managed entries, and version mismatches.

## Repository map

```text
RESEARCH_PROTOCOL.md                 portable research contract and red lines
workflow.manifest.yaml               canonical-source and runtime-view manifest
research.example.yaml                project configuration template
runtime-profile.example.yaml         machine-specific tool and path template
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
tests/                               contracts, validators, scanners, and smoke test
THIRD_PARTY_NOTICES.md               licenses and imported-source notices
docs/upstream-absorption-audit.md    upstream-to-canonical absorption record
```

The repository is the source of truth for project state. Conversation history
is not a research record.

## Research lifecycle

The router in `skills/empirical-workflow/SKILL.md` selects one stage file at a
time.

| Stage | Purpose | Representative outputs |
|---|---|---|
| 1. Dataset infrastructure | Establish source identity, keys, coverage, and lineage | inventories, merge audits, panel dimensions, versioned exports |
| 2. Literature map | Build a verified map of constructs, theories, methods, and open questions | source records, synthesis, evidence cards |
| 3. Theory and hypotheses | Define the mechanism, alternatives, and prospective tests | theory map, hypotheses, preregistration inputs |
| 4. Variables map | Bind constructs to fields, transformations, and samples | variable registry, sample rules, analysis contract |
| 5. Measurement and validity | Test construct quality and lock the main specification | validity evidence, attrition record, Checkpoint B inputs |
| 6a. Reduced form | Select and execute one causal or associational design | estimates, diagnostics, robustness matrix, blindspot audit |
| 6b. Structural | Define primitives, identification, estimation, and fit checks | model contract, targeted moments, counterfactual limits |
| 7. Writing and review | Trace every claim to evidence and prepare release | manuscript, review findings, response matrix, release record |

Three checkpoints prevent stage completion by assertion alone:

- Checkpoint A asks whether the design is answerable.
- Checkpoint B asks whether construction and measurement are defensible.
- Checkpoint C asks whether the results and release claims are defensible.

Material changes to the identifying strategy, main specification, estimation
sample, clustering level, or post-result interpretation trigger a mandatory
pause and a recorded decision.

## Method packs

Stage 6a selects exactly one pack under
`skills/empirical-workflow/methods/`. Each mature pack separates four kinds of
material:

- `prompt.md`: the operational procedure and questions the runtime follows.
- `canon.md`: what the cited methodological literature settles.
- `details.md`: implementation details, diagnostics, and package behavior.
- `template.R`: an executable reference implementation.

Available packs cover causal-design triage, selection on observables, fixed
effects, difference-in-differences, instrumental variables, regression
discontinuity, synthetic control, field experiments, and conjoint experiments.
The shared method-governance rules require current literature, maintained
implementations, explicit judgment when the literature does not settle a
choice, and a recorded reason for every non-obvious default.

## Focused operations

| Need | Canonical skill |
|---|---|
| Read one known paper, DOI, title, or author | `research-sources` |
| Search and synthesize a topic | `literature-review` |
| Audit an existing BibTeX database | `bibliography-audit` |
| Draft a prospective preregistration | `preregister` |
| Convene independent critics | `research-council` |
| Simulate a full manuscript review | `manuscript-review` |
| Verify and draft a referee response | `referee-response` |
| Build a sanitized replication release | `replication-release` |
| Compile LaTeX and inspect TikZ figures | `latex-production` |
| Build a research talk | `research-talk` |
| Build a teaching lecture | `teaching-lecture` |
| Audit rendered slides | `slide-review` |
| Build a Quarto course site | `course-site` |

Focused operations write into the same evidence, decision, status, and
governance records. They cannot bypass a checkpoint or mandatory pause.

## Install for a project

Clone the repository and keep its canonical tree intact:

```bash
git clone https://github.com/bobbyZhong10/empirical-workflow-kit.git
cd empirical-workflow-kit
python3 scripts/install_runtime_views.py --project --all --repo .
python3 scripts/verify_runtime_parity.py --project --all --repo .
```

The committed project views normally make the installation command a no-op.
It is useful after an archive tool or file transfer has stripped symlinks.
Claude Code discovers `.claude/skills/empirical-workflow`; Codex discovers
`.agents/skills/empirical-workflow`. Both paths resolve to the same canonical
directory.

To repair only one runtime:

```bash
python3 scripts/install_runtime_views.py --project --claude --repo .
python3 scripts/install_runtime_views.py --project --codex --repo .
```

The installer does not overwrite a regular file or directory. If a previous
Empirical Workflow Kit copy must be replaced, use `--replace-managed`; the
installer first moves it to a timestamped sibling backup. A directory that
does not carry this kit's ownership markers is reported as `UNMANAGED` and is
left untouched.

## Optional user-level discovery

Project-level discovery is the recommended setup because it pins each project
to its checkout. To expose this checkout in every project on the machine:

```bash
python3 scripts/install_runtime_views.py --user --all --repo .
python3 scripts/verify_runtime_parity.py --user --all --repo .
```

User-level links are absolute links to the selected canonical checkout. Run
the installer again with `--replace-managed` after moving the checkout. The
installer changes only names listed in `workflow.manifest.yaml` and refuses to
replace another package that happens to use the same skill name.

Do not install by copying `skills/*` separately into `~/.claude/skills` and
`~/.agents/skills`. Independent copies are the split-brain condition this
repository prevents.

## Start a research project

1. Copy `research.example.yaml` to `research.yaml` and fill in the observation
   unit, designs, authority, languages, and analysis-input contract.
2. Copy `runtime-profile.example.yaml` to `runtime-profile.yaml` and enter
   machine-specific paths and optional tool availability. Never embed personal
   paths in a skill, prompt, adapter, or protocol.
3. Create `_status.md`, `decision-log.md`, and the first evidence records from
   the templates routed by `empirical-workflow`.
4. Start Claude Code or Codex at the repository root. The runtime adapter reads
   the same protocol, manifest, router, and project state.

At every cross-runtime handoff, the receiver reads, in order:

1. `RESEARCH_PROTOCOL.md`
2. `research.yaml`
3. `_status.md`
4. the most relevant current evidence card
5. the tail of `decision-log.md`

The sender records the completed stage, changed artifacts, checks run, open
risks, next action, and unresolved pause.

## Python-to-R contract

Python is the default producer for ingestion, cleaning, joins, and portable
analysis data. R is the default estimation consumer when the chosen method
uses its econometric implementation. Their boundary is a versioned Parquet
file plus a contract that records project identity, data version, producing
script, row count, schema, primary key, and merge audit.

The smoke test exercises this boundary end to end. It creates a deterministic
96-row staggered-treatment panel in Python, validates identity and row-count
failures, reads the Parquet artifact in R, estimates a fixed-effects event
study, writes a simulated-results table, tests mandatory-pause behavior after
a failed identifying diagnostic, and reconstructs a handoff from durable
state.

## Development environment

Prerequisites:

- Python 3
- R 4.1 or newer
- network access during dependency bootstrap
- Node 22 or newer for presentation gates
- Quarto 1.10 or newer for deck rendering
- TeX Live or MacTeX with `latexmk` for LaTeX production

Create the repository-local test environment:

```bash
bash tests/bootstrap_test_environment.sh
```

The bootstrap creates `.venv`, installs pinned Python dependencies, and
installs `arrow`, `yaml`, `fixest`, and `modelsummary` into `.r-lib`. The test
runner never silently falls back to a system Python or installs packages during
a workflow test.

Run the complete automated suite:

```bash
.venv/bin/python -m pytest -q
bash tests/run_contract_tests.sh
bash tests/smoke/run_smoke.sh
python3 scripts/verify_runtime_parity.py --project --all --repo .
```

The smoke runner intentionally invokes several failing cases. Those cases pass
only when the workflow blocks them with the documented errors.

## Release validation

`tools/validate_registry.py` is shared by both runtimes:

```bash
tools/validate_registry <registry.yaml> --checkpoint B
tools/validate_registry <registry.yaml> --checkpoint C
```

The registry ties pipelines, claims, evidence, figures, acceptance gates,
applicability decisions, and reconciliation records to the running kit version.
A stage or release is complete only when the required checkpoint exits with
zero blocking findings. Packaging a directory is not a reproduction
certificate, and local possession of data is not redistribution authority.

## Language and portability rules

- Speak with the user in the language selected by the project configuration.
- Keep repository artifacts in English.
- Keep raw data read-only and write derived data separately.
- Keep secrets outside the repository.
- Resolve optional tools and personal paths through `runtime-profile.yaml`.
- Verify time-sensitive journal, registry, and release policies against current
  official sources before external circulation.

## Upstream lineage

The focused operations, method prompts, causal canon, and presentation tooling
were adapted from Lan E. Luo's
[`ericluo04/claude-academic-workflow`](https://github.com/ericluo04/claude-academic-workflow).
The import was decomposed into the canonical stage, method, reference,
operation, runtime-profile, and tooling locations instead of copying its global
`CLAUDE.md` into either adapter. `docs/upstream-absorption-audit.md` records the
inspected commit and the disposition of every upstream source family.

See `THIRD_PARTY_NOTICES.md` and `docs/upstream-attribution.md` for licenses and
detailed lineage. Retain those files when redistributing the adapted material.

## Design principles

- Checkpoints are executable gates, not narrative summaries.
- Main specifications are locked before result interpretation.
- Claims contract when diagnostics fail; caveats do not convert a failed gate
  into a pass.
- Every material claim points to evidence, a result, a citation, or an explicit
  argument.
- Limitations appear beside the choice or result they constrain.
- Status, evidence, and decisions survive a runtime switch because they live in
  files, not chat history.
