# Empirical Workflow Kit

A shared research workflow for **Claude Code and Codex**, from the research
question and data to analysis, interpretation, writing, and review.

The kit provides reusable skills, method guides, project templates, and a
mechanical validator. Research decisions and evidence stay in your project
files, so work can resume across sessions and runtimes. It is intended for
empirical researchers in information systems, economics, and quantitative
marketing.

[Quick start](#quick-start) · [Workflow](#research-workflow) ·
[Skills](#focused-skills) · [Project records](#project-records-and-delivery) ·
[Documentation](docs/README.md) · [Contributing](CONTRIBUTING.md)

## What you can do

- Organize data sources, variable definitions, evidence, and research decisions.
- Read papers, build literature maps, and audit citations.
- Work through observational designs, experiments, descriptive analysis, and
  structural or conditional models with explicit evidence boundaries.
- Draft and review manuscripts, prepare referee responses, and assemble
  replication packages.
- Build research talks, teaching lectures, and Quarto course sites.

Both runtimes use the same canonical files under `skills/`. Claude Code
uses `.claude/skills/empirical-workflow`; Codex uses
`.agents/skills/empirical-workflow`. The repository includes workflow
instructions and supporting tools; you supply the research question, data,
runtime access, and tools needed for the selected task.

You can attach the kit to an existing data project, start a new study in an
empty research directory, or use a focused operation such as bibliography
auditing or slide review. The full workflow supports measurement, descriptive
and institutional analysis as well as causal research. It organizes work around
the question and available evidence rather than requiring every study to use
the same estimator or make a causal claim.

## Quick start

Use a separate research directory so your project records do not replace this
kit's maintenance records. The commands below use a POSIX shell and symlinks.

### 1. Install the kit

You need Git, Python 3.11+, and Claude Code or Codex. R 4.1+ is required for
the default empirical workflow. Presentation and LaTeX tools are needed only
for those operations; see [dependencies](docs/development.md#development-environment).

```bash
git clone https://github.com/bobbyZhong10/empirical-workflow-kit.git
cd empirical-workflow-kit
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/install_runtime_views.py --project --all --repo .
.venv/bin/python scripts/verify_runtime_parity.py --project --all --repo .
```

The last command should report `PARITY OK`. Keep this checkout available:
attached projects link to its canonical skills.

### 2. Attach your research directory

From the kit checkout, replace the example path with an existing project
folder. For a new project, create an empty folder first.

```bash
.venv/bin/python scripts/bootstrap_project.py /absolute/path/to/research-project --all
cd /absolute/path/to/research-project
.workflow/bin/ewf doctor
```

Use `--codex` or `--claude` instead of `--all` for a single runtime. The
bootstrap preserves existing research configuration and adds workflow records,
runtime links, and local command wrappers after checking for collisions.

Edit `research.yaml` for your research question and approved scope, and
`runtime-profile.yaml` for machine-specific tools and paths. The doctor reports
missing capabilities; resolve required-tool blocks before relying on them.
See [setup and usage](docs/getting-started.md) for profile configuration,
user-level discovery, and moving a project to another machine.

### 3. Start or resume work

Open the research directory in Claude Code or Codex. Open the generated
`WORKFLOW_START.md`, choose a startup prompt, and fill in its project header:

- **`AUTONOMOUS_WITH_RED_LINES`** starts or continues the remaining workflow.
- **`TAKEOVER_AND_RESUME`** reconstructs progress from existing project records.

The [research protocol](RESEARCH_PROTOCOL.md) governs both modes. Routine work
can proceed autonomously; material design changes and external publication
require recorded authority. R is the default analysis language, with justified
exceptions recorded in the project decision log.

## Research workflow

| Stage | Main task |
|---|---|
| 1. Data infrastructure | Establish sources, keys, coverage, and lineage |
| 2. Literature | Map prior evidence, constructs, methods, and open questions |
| 3. Theory and hypotheses | Define the question, alternatives, and evidence strategy |
| 4. Variables | Connect constructs to fields, transformations, and sample rules |
| 5. Measurement | Check validity and lock the main specification |
| 6a / 6b. Analysis | Run reduced-form, descriptive, structural, or conditional analysis |
| 7. Writing and review | Explain findings, assess claims, and prepare delivery |

Method packs cover causal-design triage, selection on observables, fixed
effects, difference-in-differences, instrumental variables, regression
discontinuity, synthetic control, field experiments, and conjoint experiments.
See the [workflow guide](docs/workflow-guide.md) for stage outputs, focused
skills, and checkpoint rules.

The shared `tools/validate_registry` command checks registry requirements at
Checkpoints B and C. Stage 6 exits through analysis readiness; final Checkpoint C
follows Stage 7. **A mechanical pass does not establish causal validity,
research contribution, or publication readiness.** Substantive review and
independent reading remain necessary.

### Methods and checkpoints

Each method pack combines an operational prompt, methodological references,
implementation guidance, and a manifest recording its review date and software
boundary. Packs include R reference implementations where applicable. The
workflow asks for the identifying assumptions, diagnostic evidence, economic
meaning, and limits of an estimate, alongside its numerical results.

| Milestone | What it establishes |
|---|---|
| Checkpoint A, after Stage 3 | The question is answerable with the available data and evidence strategy |
| Checkpoint B, after Stage 5 | Construction, measurement, sample rules, and the main specification are ready for analysis |
| Analysis readiness, after Stage 6 | Results and their interpretation are sufficiently documented to begin writing |
| Checkpoint C, after Stage 7 | Mechanical delivery requirements are met, with separate substantive and editorial assessments |

Failed diagnostics remain part of the research record. A changed sample,
identifying strategy, or main specification requires a recorded decision;
exploratory work remains distinguishable from prospective tests. Current claims
must reflect the evidence and limitations, including results that narrow or
contradict the original hypothesis.

## Focused skills

The stage router can invoke focused operations as the project needs them.
These skills also provide entry points for a specific task:

| Task | Skill |
|---|---|
| Read a known paper, title, or DOI | [research-sources](skills/research-sources/SKILL.md) |
| Search and synthesize literature | [literature-review](skills/literature-review/SKILL.md) |
| Check a BibTeX database | [bibliography-audit](skills/bibliography-audit/SKILL.md) |
| Prepare a prospective preregistration | [preregister](skills/preregister/SKILL.md) |
| Examine a research plan or argument from multiple perspectives | [research-council](skills/research-council/SKILL.md) |
| Review a manuscript and prepare referee responses | [manuscript-review](skills/manuscript-review/SKILL.md), [referee-response](skills/referee-response/SKILL.md) |
| Assemble a replication release | [replication-release](skills/replication-release/SKILL.md) |
| Compile and inspect LaTeX output | [latex-production](skills/latex-production/SKILL.md) |
| Build talks and teaching materials | [research-talk](skills/research-talk/SKILL.md), [teaching-lecture](skills/teaching-lecture/SKILL.md) |
| Review rendered slides or build a course site | [slide-review](skills/slide-review/SKILL.md), [course-site](skills/course-site/SKILL.md) |

Named method skills such as `did`, `iv`, and `rdd` route to the canonical
Stage 6a packs. Compatibility names such as `bibcheck`, `litreview`, and
`review-paper` route to their current equivalents. Focused operations retain
the same evidence and authority requirements as the full workflow.

## Project records and delivery

Attaching a project creates missing workflow records while preserving existing
research configuration. The main files have distinct roles:

| File or directory | Purpose |
|---|---|
| `research.yaml` | Research scope, stage, approved designs, and analysis contract |
| `runtime-profile.yaml` | Local commands, paths, and optional capabilities |
| `_status.md` | Current progress, checks, risks, and next action |
| `decision-log.md` | Append-only decisions and deviations |
| `evidence/` | Source, design, diagnostic, and result evidence cards |
| `WORKFLOW_START.md` | Shared prompts for starting or resuming work |
| `workflow.manifest.yaml` | Canonical workflow paths and version |

During a handoff, the receiving runtime reads the protocol, research
configuration, status, relevant evidence, and recent decisions before continuing.
This lets Claude Code and Codex share research state without depending on either
runtime's conversation history. The conversation follows the user's language;
durable repository artifacts are written in English.

A completed submission uses the following delivery layout, populated during the
research workflow rather than by the initial bootstrap:

```text
output/
├── data/     final analysis data and an assembly note
├── code/     code that reproduces the empirical work
├── result/   PNG figures and CSV or Markdown table exports
└── LaTeX/    manuscript sources and the compiled PDF
```

The [delivery contract](skills/empirical-workflow/references/delivery-contract.md)
defines the requirements. Packaging alone does not establish reproducibility
or authorize redistribution of data.

## Configuration and validation

The runtime profile declares Python and R commands, cache locations, and optional
document, browser, scholarly-source, and presentation capabilities. In an attached
research project, use the generated wrapper to inspect or run those bindings:

```bash
.workflow/bin/ewf doctor
.workflow/bin/ewf env
.workflow/bin/ewf run rscript --vanilla code/01_ingest.R
```

The script path above is an example; substitute a script from your project.
`doctor` reports required-tool blocks and optional-capability warnings. Keep API
keys in the environment variables named by the profile. For slides, configure
Node 22+ and Quarto 1.10+; LaTeX production uses `latexmk` with a TeX installation.

When a project reaches an applicable checkpoint, run its registry through the
same validator used by both runtimes:

```bash
.workflow/bin/validate_registry <registry.yaml> --checkpoint B
.workflow/bin/validate_registry <registry.yaml> --checkpoint C
```

Replace `<registry.yaml>` with the project's registry path and run only the
checkpoint appropriate to its stage. Reports identify mechanical blocking
findings; reproducibility, claim credibility, discussion readiness, and
submission delivery are assessed separately.

## Documentation

| Looking for | Start here |
|---|---|
| Installation, configuration, and handoffs | [Setup and usage](docs/getting-started.md) |
| Stages, methods, focused skills, and validation | [Workflow guide](docs/workflow-guide.md) |
| Claude Code or Codex configuration | [Runtime recipes](docs/runtime-recipes/README.md) |
| Architecture, tests, and upstream updates | [Development guide](docs/development.md) |
| Slides and course materials | [Presentation tooling](presentation-tooling/README.md) |
| Adopting workflow 2.8 | [Migration guide](docs/workflow-2.8-migration.md) |
| Changes and bug reports | [Contributing](CONTRIBUTING.md) |

The [documentation index](docs/README.md) distinguishes current guides from
historical design and maintenance records.

## Public repository contents

The repository includes skills, tools, synthetic test fixtures, and licensed
presentation dependencies. Local reading PDFs and journal template downloads
are excluded. Obtain journal assets separately before using the
[LaTeX adapter](skills/empirical-workflow/references/latex-manuscript-adapter.md).
Environment files, credentials, runtime profiles, and common caches are ignored.

Keep confidential research data and manuscripts in an appropriately controlled
project repository. Ignore rules prevent accidental additions for matched paths;
they do not remove files already present in Git history.

## Development

After the Python setup above, run the contract checks and runtime parity check:

```bash
bash tests/run_contract_tests.sh
.venv/bin/python scripts/verify_runtime_parity.py --project --all --repo .
```

The [development guide](docs/development.md#development-environment) covers the
full test suite and dependency bootstrap. The empirical smoke test,
`tests/smoke/run_smoke.sh`, requires R packages as well as Python dependencies.

## License and acknowledgments

The kit is available under the [MIT License](LICENSE). Bundled third-party
components retain their own licenses; see [Third-Party Notices](THIRD_PARTY_NOTICES.md).

This work adapts research skills and presentation tooling from
[ericluo04/claude-academic-workflow](https://github.com/ericluo04/claude-academic-workflow)
and econometric review practices from
[pedrohcgs/claude-code-my-workflow](https://github.com/pedrohcgs/claude-code-my-workflow).
[Attribution](docs/upstream-attribution.md) and the
[upstream audit](docs/upstream-absorption-audit.md) record source revisions and
adaptation scope.
