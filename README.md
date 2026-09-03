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

Each pack has a machine-readable `method.manifest.yaml` with its review date,
refresh query, refresh interval, software boundary, and canonical source files.
Thin skills such as `skills/did/SKILL.md` and `skills/rdd/SKILL.md` make named
methods directly discoverable without copying their prompts. Every facade
routes through Stage 6a and the common mandatory-pause contract.

Short `SKILL.md` files are intentional only when declared in
`workflow.manifest.yaml` as compatibility aliases or when they are method
discovery facades. Contract tests require every other managed skill to remain a
single substantive canonical implementation and reject duplicate frontmatter
names.

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

The literature workflow centralizes venue coverage in
`skills/literature-review/references/journal-scope.md`. Its current scope covers
every UTD 24 and FT 50 journal, prioritizes information systems, operations
management, marketing, and management and organization science, and adds top
economics and industrial-organization venues. List membership controls the
coverage audit, not a paper's relevance or evidentiary weight.

All 20 skill names from the inspected upstream workflow remain directly
discoverable. Renamed operations use thin compatibility aliases—`bibcheck`,
`compile-latex`, `council`, `litreview`, `reading-papers`,
`replication-package`, and `review-paper`—that route to the canonical skills in
the table above. The aliases retain familiar invocation names without copying
or forking the underlying prompts.

## Install the kit checkout

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

Claude Code gives a personal skill priority over a project skill with the same
name. A pre-existing regular directory under `~/.claude/skills` can therefore
hide this repository's project view. Run the user-level parity check when a
runtime appears to use old instructions. If the installer reports `UNMANAGED`,
archive or rename that third-party skill only after confirming its ownership;
the installer will not make that decision for you. See the
[Claude Code skill-scope documentation](https://code.claude.com/docs/en/slash-commands#where-skills-live).

Do not install by copying `skills/*` separately into `~/.claude/skills` and
`~/.agents/skills`. Independent copies are the split-brain condition this
repository prevents.

## Attach an existing research project

Keep the project's current data, code, results, and instructions in place. From
the kit checkout, attach the canonical workflow to that project:

```bash
python3 scripts/bootstrap_project.py /absolute/path/to/research-project --claude
```

Use `--all` when both Claude Code and Codex will work in the project. The
bootstrapper performs a collision preflight before writing, preserves an
existing `research.yaml`, and appends a bounded workflow adapter to an existing
`CLAUDE.md` or `AGENTS.md`. It creates project-owned protocol, status, decision,
evidence, profile, and manifest files. Runtime discovery links remain relative
and resolve through the ignored local `.workflow/kit` binding, so both runtimes
execute this checkout's one canonical skill tree rather than copied prompts.

Then enter the research project, complete `research.yaml`, and diagnose it:

```bash
cd /absolute/path/to/research-project
.workflow/bin/ewf doctor
```

The bootstrap also creates `WORKFLOW_START.md`, a relative link to the kit's
canonical startup prompts. Commit the link with the project; it gives Claude
Code and Codex the same entry instructions without copying a prompt into both
runtime adapters.

On another machine, check out the project's recorded kit version and rerun the
same bootstrap command to recreate the ignored local binding. Commit the project
records and runtime-view links, but never commit `.workflow/kit` itself.

## Start a research project

1. For work inside the kit checkout, copy `research.example.yaml` to
   `research.yaml`. For an external existing project, use the bootstrap command
   above. Fill in the observation unit, designs, authority, languages, and
   analysis-input contract.
2. Inside the kit checkout, copy `runtime-profile.example.yaml` to
   `runtime-profile.yaml`; the external bootstrapper creates the corresponding
   file automatically. Enter machine-specific paths and optional tool
   availability. Never embed personal paths in a skill, prompt, adapter, or
   protocol.
3. Resolve and diagnose that profile:

   ```bash
   python3 scripts/ewf.py env
   python3 scripts/ewf.py doctor
   ```

4. Create `_status.md`, `decision-log.md`, and the first evidence records from
   the templates routed by `empirical-workflow`.
5. Start Claude Code or Codex at the repository root. The runtime adapter reads
   the same protocol, manifest, router, and project state.

## Start or resume a workflow

Open `WORKFLOW_START.md` in an attached external project. When working directly
inside the kit checkout, open the manifest-named canonical file at
`skills/empirical-workflow/references/start-prompts.md`. Copy one prompt, fill
only its short project-specific header, and send it to Claude Code or Codex.

### New project or automatic completion

Use `AUTONOMOUS_WITH_RED_LINES` when starting a new project or asking the
workflow to carry an existing project through all remaining stages. For an
existing data project, set the priority explicitly, for example:

```text
Objective: Reproduce and verify the existing data work, then complete the
literature review, theory development, analysis, manuscript, and internal review.
Starting point: The project already contains substantially complete data work.
Priority: Reproduce the data pipeline before relying on any existing result.
Constraints: Preserve existing data, code, results, project instructions, and
user-authored README content.
```

This is the highest-autonomy mode: routine reversible work continues without
step-by-step approval, while mandatory pauses and external-action authority
remain binding.

### Take over work already in progress

Use `TAKEOVER_AND_RESUME` after a Claude/Codex handoff, context compaction,
interruption, or partial run. Point it at the latest handoff when one exists.
The runtime reconstructs state from the protocol, project configuration,
status, current evidence, and decision log, validates that record against the
actual files, and resumes from the first unverified atomic task. It does not
create a fresh project state or blindly rerun completed work.

The two modes change only how work begins and resumes. They use the same stages,
evidence records, checkpoints, language policy, R-first rule, and mandatory
pauses. Switching between Claude Code and Codex therefore does not require a
different prompt or a separate project version.

Run configured commands through the logical tool runner so the profile affects
execution rather than documentation alone:

```bash
python3 scripts/ewf.py run rscript --vanilla analysis.R
python3 scripts/ewf.py run quarto render talk.qmd
python3 scripts/ewf.py run node presentation-tooling/deck-check.mjs fit talk.html
```

See `docs/runtime-recipes/` for Claude Code and Codex discovery, handoff,
browser, document, secret, and optional-capability guidance.

At every cross-runtime handoff, the receiver reads, in order:

1. `RESEARCH_PROTOCOL.md`
2. `research.yaml`
3. `_status.md`
4. the most relevant current evidence card
5. the tail of `decision-log.md`

The sender records the completed stage, changed artifacts, checks run, open
risks, next action, and unresolved pause.

## Analysis-data contract

R is the default language for ingestion, cleaning, joins, construction,
estimation, inference, tables, and figures. A project may retain or introduce
Python only when the protocol's exception criteria are met and the reason is
recorded in `decision-log.md`. Any producer writes a versioned Parquet file
plus a contract that records project identity, data version, producing script,
row count, schema, primary key, and merge audit.

The smoke test deliberately exercises the supported Python-to-R exception. It
creates a deterministic 96-row staggered-treatment panel in Python, validates
identity and row-count failures, reads the Parquet artifact in R, estimates a
fixed-effects event study, writes a simulated-results table, tests mandatory-pause behavior after
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
bash tests/smoke/run_presentation_smoke.sh
python3 scripts/verify_runtime_parity.py --project --all --repo .
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
python3 scripts/audit_upstream.py --offline
python3 scripts/audit_upstream.py --fail-on-change
```

The offline command verifies that every destination declared in
`upstream.lock.yaml` exists. The online command compares the pinned Git object
IDs with upstream `HEAD` and reports only changed or missing source families.

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

- Communicate in the primary language used in the user's first substantive
  request, unless the user explicitly asks to switch.
- Keep repository artifacts in English.
- Keep raw data read-only and write derived data separately.
- Keep secrets outside the repository.
- Resolve optional tools and personal paths through `runtime-profile.yaml`.
- Verify time-sensitive journal, registry, and release policies against current
  official sources before external circulation.

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
