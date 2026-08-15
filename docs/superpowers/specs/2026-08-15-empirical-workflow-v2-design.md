# Empirical Workflow v2 Design

## Status and purpose

**Status:** approved design, awaiting user review before implementation.

Empirical Workflow v2 is a portable research operating system for panel causal research in information systems, management, and economics. It supports firm technology adoption, platform changes, and market or two-sided platform data. Its target outlets are Management Science, ISR, and MISQ. Its reference pool may include UTD 24, FT50, leading economics journals, JAIS, IJRM, and related high-quality outlets.

The system serves three roles from one evidence base: autonomous executor, research copilot, and independent quality auditor. It must work in both Claude Code and Codex without allowing conversation history to become the source of truth.

## Design principles

1. **Protocol first.** Research rules, stage contracts, checkpoints, and evidence formats are runtime independent. `CLAUDE.md` and `AGENTS.md` are thin adapters, not competing protocol copies.
2. **High autonomy with hard red lines.** After project setup approval, routine work proceeds automatically through a complete result package and paper draft. Design-changing or irreversible actions pause for the user.
3. **Identification before results.** A main specification is locked before estimation. Diagnostics are evidence for assumptions, not optional robustness decorations.
4. **Research code over software architecture.** Scripts are linear, numbered, readable, and easily edited. The system avoids packages, classes, and unnecessary abstraction.
5. **Evidence over conversation.** A result, decision, and claim must be traceable to a project artifact.

## Repository architecture

```text
project/
├── RESEARCH_PROTOCOL.md
├── CLAUDE.md
├── AGENTS.md
├── research.yaml
├── _status.md
├── decision-log.md
├── docs/
│   ├── literature/
│   ├── design/
│   ├── variables/
│   └── checkpoints/
├── evidence/
│   ├── data/
│   ├── estimates/
│   └── audits/
├── data/
│   ├── raw/
│   ├── intermediate/
│   └── analysis/
├── code/
│   ├── py/
│   └── r/
├── results/
│   ├── tables/
│   ├── figures/
│   └── logs/
└── paper/
```

`research.yaml` is the small project start card. It records target outlets, research context, observation unit, analysis languages, allowed methods, approval mode, current stage, and project-specific choices. `_status.md` is a replaceable current-state snapshot. `decision-log.md` is append-only and preserves the reasoning behind every material choice.

## Runtime adapters and project handoff

`RESEARCH_PROTOCOL.md` holds portable research rules. `CLAUDE.md` routes Claude Code into that protocol and states Claude-specific behavioral and tool constraints. `AGENTS.md` does the equivalent for Codex. Neither adapter duplicates methodological rules.

Before continuing a project, any runtime must read, in order:

1. `research.yaml`
2. `_status.md`
3. The most recent relevant evidence card
4. The tail of `decision-log.md`

It may then continue the current stage. It must not infer project facts from a prior chat alone.

## Roles and authority model

The same system can be invoked in three bounded modes.

| Mode | Responsibility | Prohibited behavior |
|---|---|---|
| Executor | Build data, run the locked analysis, produce tables, figures, logs, and draft prose | Changing the main specification or concealing failed diagnostics |
| Copilot | Frame decisions, surface anomalies, maintain status and evidence records | Making an unapproved material research decision |
| Quality auditor | Independently inspect data, identification, outputs, citations, and claims | Searching specifications for preferred results |

After user approval of the project start card, the default is full autonomous execution through analysis, paper draft, and internal audit.

| Authority | Actions |
|---|---|
| Automatic | Literature collection, data profiling, planned Python ETL, planned R estimation, diagnostics, pre-committed robustness checks, tables, draft prose, and evidence cards |
| Configurable | New non-core proxies, new data sources, exploratory analyses, and expensive external tasks |
| Mandatory pause | A change to the main specification, sample, clustering, or identification strategy; a failed identifying diagnostic; a post-result specification; external publication or submission |

At every mandatory pause, the agent reports the issue, options, consequences, and a recommendation, then waits for explicit direction.

## Stage protocol

The seven-stage workflow and Checkpoints A, B, and C remain. Each stage has a standard contract: **inputs, automatic actions, required artifacts, red lines, and exit condition**.

1. Dataset infrastructure
2. Literature map
3. Theory and hypotheses, then Checkpoint A
4. Variables map
5. Measurement and validity, then Checkpoint B
6. Reduced form and/or structural analysis, then Checkpoint C
7. Paper writing and review

Checkpoint A locks the answerable question, identifying assumption, planned tests, alternatives, and contribution under a null primary result. Checkpoint B locks construction, sample attrition, functional forms, timing, clustering, and measurement validity. Checkpoint C verifies identification evidence, result traceability, complete reporting, audit disposition, and conclusion boundaries.

## Literature and outlet positioning

The literature map has four explicit tracks rather than one undifferentiated bibliography:

1. **Target-outlet track:** contribution types, framing, and reviewer expectations in MS, ISR, and MISQ.
2. **Theory track:** causal mechanisms, boundary conditions, and competing explanations.
3. **Empirical precedent track:** close settings, measures, and empirical strategies from the selected broad pool.
4. **Method track:** identification practice and statistical standards from leading economics and methods work.

Every core citation has a purpose label: theory, measure precedent, identification precedent, methodological requirement, or counterargument. Its bibliographic facts and source location must be verified before it supports a claim. The workflow records whether a paper is a submission target, framing anchor, theory source, empirical analogue, or method authority.

## Causal design protocol

The system activates only the required branch among FE or OLS, DID or event study, DDD, IV, RDD, and structural models. All projects begin from the source of variation and an identifying assumption, never from a preferred estimator.

For firm, platform, and market settings, the decision tree explicitly checks:

- Announcement, effective, actual-adoption, and anticipation dates.
- Treatment intensity, repeated treatment, treatment exit, and staggered adoption.
- Spillovers, interference, equilibrium response, and the scope of SUTVA.
- Entry, exit, and post-treatment sample selection.
- Unit and time aggregation consistent with treatment assignment.

The specification is locked before primary estimation. A null is a result. A post-result specification is allowed only when labeled and logged as post hoc. For staggered adoption, a heterogeneity-robust estimator is the main result; two-way fixed effects is reference-only and weight diagnostics are reported.

## Python-R workflow and data contract

Python is used for ingestion, cleaning, cross-source merging, entity resolution, text or API processing, and exports. It uses direct numbered scripts such as `01_ingest.py`, `02_merge.py`, `03_entities.py`, and `04_export.py`.

R is used for analysis construction, descriptives, identification diagnostics, estimation, robustness, and publication tables. It uses direct numbered scripts such as `01_construct.R`, `02_descriptives.R`, `03_main.R`, `04_diagnostics.R`, `05_robustness.R`, and `06_tables.R`.

Python exports analysis data as Parquet plus a data-contract record. The record states data version and source, producing script, unit and time granularity, keys and uniqueness checks, row and panel counts, missingness, field types and ranges, and merge rates. R validates this contract before estimating. A failed contract stops the analysis.

Variable names are concise and meaningful, for example `ai_adopt`, `treated`, `post`, `sales_ln`, `firm_id`, and `year_qtr`. A variable dictionary records full definitions, units, sources, transformations, and time availability. Comments are concise English comments for non-obvious research or technical decisions.

## Results and tables

The default output follows a rigorous economics style: three-line tables, coefficient estimates, parenthesized standard errors, significance notation, fixed effects, clustering, number of clusters, N, relevant dependent-variable means, and self-contained notes. The main result is a specification ladder. Required identification diagnostics appear in the main paper rather than being hidden in an appendix.

Every formal estimation batch writes:

- A machine-readable estimate record.
- A short human-readable markdown summary.
- A result evidence card with data version, sample rule, specification, output paths, conclusion, and binding limitations.

The table renderer provides a journal-specific final formatting adapter only after the scientific content is stable. It does not modify estimates or their reported evidence.

## Audit, error handling, and recovery

The quality auditor runs four packages:

1. Data integrity: keys, merges, duplicates, missingness, coverage, attrition, and timing.
2. Identification: assumption, potential violations, diagnostic evidence, and backtracking requirements.
3. Results: traceability of every reported number and consistency of tables, prose, samples, fixed effects, clustering, and significance annotations.
4. Manuscript: mapping from contribution to evidence, mechanism to tests, hypothesis to columns, and stated limitations to actual constraints.

Before submission, an independent runtime should audit the identification section and its evidence. Audit findings are recorded as CLEAR, CONDITIONAL, or HOLD. HOLD blocks progress; CONDITIONAL requires a tracked resolution.

## Validation and implementation boundary

Implementation will include a small simulated-panel smoke test. It must verify the Python-R contract, a DID path, staggered-adoption protections, table generation, status recovery by another runtime, and forced stopping when an identification diagnostic fails.

This document specifies v2 only. No implementation begins until the user reviews and approves it. Implementation then begins with a separate detailed plan that decomposes the portable protocol, adapters, templates, reference files, and smoke test.

