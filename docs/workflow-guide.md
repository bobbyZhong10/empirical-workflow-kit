# Workflow guide

[Documentation index](README.md) · [Project home](../README.md)

Run commands from the kit checkout unless a step explicitly changes directories.

## Research lifecycle

The router in `skills/empirical-workflow/SKILL.md` selects one stage file at a
time.

| Stage | Purpose | Representative outputs |
|---|---|---|
| 1. Dataset infrastructure | Establish source identity, keys, coverage, and lineage | inventories, merge audits, panel dimensions, versioned exports |
| 2. Literature map | Build a verified map of constructs, theories, methods, and open questions | source records, synthesis, evidence cards |
| 3. Theory and hypotheses | Define the question, alternatives, and evidence strategy | question-to-evidence map, applicable hypotheses and prospective tests |
| 4. Variables map | Bind constructs to fields, transformations, and samples | variable registry, sample rules, analysis contract |
| 5. Measurement and validity | Test construct quality and lock the main specification | validity evidence, attrition record, Checkpoint B inputs |
| 6a. Reduced form and description | Execute the selected design or descriptive/accounting analysis | results, interpreted diagnostics, analysis-readiness record |
| 6b. Structural and conditional models | Define primitives, parameter status, fit, and counterfactual assumptions | model contract, targeted/untargeted fit, bounded scenarios |
| 7. Writing and review | Explain the question, economic meaning, and contribution with supported claims | manuscript, adjudicated reviews, cold read, release record |

Three checkpoints structure progression:

- Checkpoint A asks whether the design is answerable.
- Checkpoint B asks whether construction and measurement are defensible.
- Checkpoint C combines mechanical release checks with separate substantive and
  editorial assessments.

B and C have executable registry checks. Stage 6 exits through an
analysis-readiness record; final Checkpoint C follows Stage 7. A validator pass
does not certify identification, economic contribution, or reader understanding.

Material changes to the identifying strategy, main specification, estimation
sample, clustering level, or post-result interpretation trigger a mandatory
pause and a recorded decision.

## Method packs

For a supported causal or associational design, Stage 6a selects one pack under
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
routes through Stage 6a and the common mandatory-pause contract. Noncausal
measurement and accounting retain evidence and interpretation discipline without
selecting an irrelevant causal pack.

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

## Release validation

`tools/validate_registry.py` is shared by both runtimes:

```bash
tools/validate_registry <registry.yaml> --checkpoint B
tools/validate_registry <registry.yaml> --checkpoint C
```

The registry ties pipelines, claims, evidence, figures, acceptance gates,
applicability decisions, and reconciliation records to the running kit version.
A gated milestone requires zero mechanical blocking findings from the applicable
checkpoint, plus the relevant substantive and editorial reviews. Version 2.8
reports mechanical scope and blocking areas separately from reproducibility,
claim credibility, discussion readiness, and submission delivery. Lexical and
house-style findings are advisory; neither a regex nor an anchor verifies a
proposition. Packaging a directory is not a reproduction certificate, and local
possession of data is not redistribution authority.

Progress is organized around question, evidence, and inference in existing
Evidence cards. Draft from the economic argument, not prediction IDs or gate
counts. Retain historical failures with reasoned closure; stop repeated revision
when core defects are repaired and further work would not change a judgment.
See [the 2.8 migration and interpretation guide](workflow-2.8-migration.md).

## Language and portability rules

The public kit excludes local reading copies (`Classic Paper/`), journal
template downloads (`Template_for_Management_Science_Journal/`), and disposable
PR drafts (`PR_BODY.md`). Obtain journal assets separately before following the
[LaTeX adapter](../skills/empirical-workflow/references/latex-manuscript-adapter.md).
Environment files, credentials, editor state, and common build caches are also
ignored. Keep sanitized example configurations and intentional test fixtures
under version control. Ignore rules do not remove files from prior commits.

- Communicate in the primary language used in the user's first substantive
  request, unless the user explicitly asks to switch.
- Keep repository artifacts in English.
- Keep raw data read-only and write derived data separately.
- Keep secrets outside the repository.
- Resolve optional tools and personal paths through `runtime-profile.yaml`.
- Verify time-sensitive journal, registry, and release policies against current
  official sources before external circulation.

## Design principles

- Mechanical checkpoint checks and substantive review have distinct roles.
- Main specifications are locked before result interpretation.
- Diagnostic concerns require interpretation and adjudication. Correct the
  calculation, reconsider the design, or narrow the claim as the evidence requires.
- Every material claim points to evidence, a result, a citation, or an explicit
  argument.
- Limitations appear beside the choice or result they constrain.
- Status, evidence, and decisions survive a runtime switch because they live in
  files, not chat history.

