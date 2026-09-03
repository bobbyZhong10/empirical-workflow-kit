# Academic Workflow Absorption Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the full governed academic-research operations layer described in the approved absorption design.

**Architecture:** Preserve the thin runtime adapters and the stage-governed core. Put durable rules in the protocol and focused references, method depth in selectively loaded method packs, and orthogonal operations in companion skills. Deterministic scripts produce records that the core governance validator can accept.

**Tech Stack:** Markdown skill contracts, YAML records, Python 3 with PyYAML and httpx/lxml/pypdf through `uv`, R reference scripts, Node.js validation gates, pytest.

**Spec:** `docs/superpowers/specs/2026-09-02-academic-workflow-absorption-design.md`

## Global Constraints

- Speak with the user in Chinese and write repository artifacts in English.
- Preserve `RESEARCH_PROTOCOL.md` as the portable source of governance truth.
- Keep `CLAUDE.md` and `AGENTS.md` under 140 lines and free of duplicated method rules.
- Never overwrite raw data, a source bibliography, a manuscript, or a third-party source tree.
- Keep project state in durable artifacts and preserve the required cross-runtime handoff order.
- Load one selected stage and one selected method pack at a time.
- Adapted material from commit `8958cc246e65cdf7c36604f397a1c1719b7e2c14` retains MIT attribution.
- Do not add generated HTML, rendered decks, or example outputs.

---

### Task 1: Portable governance and decomposed global instructions

**Files:**
- Modify: `RESEARCH_PROTOCOL.md`
- Modify: `skills/empirical-workflow/SKILL.md`
- Create: `skills/empirical-workflow/references/research-writing.md`
- Create: `skills/empirical-workflow/references/execution-discipline.md`
- Create: `skills/empirical-workflow/references/method-governance.md`
- Create: `skills/empirical-workflow/references/code-review.md`
- Create: `skills/empirical-workflow/templates/handoff-template.md`
- Create: `runtime-profile.example.yaml`
- Create: `THIRD_PARTY_NOTICES.md`
- Modify: `tests/test_workflow_contract.py`

**Interfaces:**
- Consumes: the existing protocol and adapters.
- Produces: portable reference paths used by every later task.

- [x] Add failing assertions that the protocol routes writing, execution, method governance, code review, runtime profiles, attribution, and the strengthened handoff record.
- [x] Run `bash tests/run_contract_tests.sh` and confirm the new assertions fail because the files and routes do not exist.
- [x] Add the references, protocol routes, runtime profile, handoff template, and third-party notice.
- [x] Run `bash tests/run_contract_tests.sh` and confirm the Task 1 assertions pass.

### Task 2: Claim governance and preregistration

**Files:**
- Create: `skills/empirical-workflow/templates/governance-registry-template.yaml`
- Create: `skills/empirical-workflow/templates/preregistration-template.yaml`
- Create: `skills/empirical-workflow/scripts/validate_governance.py`
- Create: `skills/preregister/SKILL.md`
- Modify: `skills/empirical-workflow/stages/stage3-theory-hypotheses.md`
- Modify: `skills/empirical-workflow/stages/stage5-measurement.md`
- Modify: `tests/test_workflow_contract.py`
- Create: `tests/test_governance_validator.py`

**Interfaces:**
- Consumes: pipeline, claim, gate, applicability, and publication records in one YAML registry.
- Produces: exit code 0 with an eligibility report, or exit code 1 with invariant violations.

- [x] Write failing unit tests for mixed-pipeline rejection, reconciliation acceptance, post-hoc gate derivation, unresolved gate blocking, incomplete substitute rejection, and retrospective preregistration refusal language.
- [x] Run `python3 -m pytest tests/test_governance_validator.py -q` and confirm failures identify the missing validator.
- [x] Implement the validator, templates, preregistration skill, and Stage 3/5 routes.
- [x] Run the governance unit tests and the contract suite.

### Task 3: Research-source and bibliography operations

**Files:**
- Create: `skills/research-sources/SKILL.md`
- Create: `skills/research-sources/REFERENCE.md`
- Create: `skills/research-sources/scripts/paper.py`
- Create: `skills/literature-review/SKILL.md`
- Create: `skills/bibliography-audit/SKILL.md`
- Modify: `skills/empirical-workflow/stages/stage2-lit-map.md`
- Modify: `skills/empirical-workflow/stages/stage7-writing.md`
- Create: `tests/test_research_sources.py`
- Modify: `tests/test_workflow_contract.py`

**Interfaces:**
- Consumes: DOI, arXiv identifier, URL, title, author, or topic.
- Produces: normalized JSON source records plus Stage 2 and bibliography-audit artifacts.

- [x] Write failing tests for title normalization, DOI/arXiv/title identity keys, source-record merging, section selection, and abstract-only claim limits.
- [x] Run `python3 -m pytest tests/test_research_sources.py -q` and confirm the module is missing.
- [x] Adapt the source CLI and the three focused prompts to project-relative paths and portable caches.
- [x] Run source unit tests and contract tests without making live network calls.

### Task 4: Method-specific causal packs

**Files:**
- Create: `skills/empirical-workflow/methods/causal-design/**`
- Create: `skills/empirical-workflow/methods/did/**`
- Create: `skills/empirical-workflow/methods/iv/**`
- Create: `skills/empirical-workflow/methods/rdd/**`
- Create: `skills/empirical-workflow/methods/synthetic-control/**`
- Create: `skills/empirical-workflow/methods/field-experiment/**`
- Create: `skills/empirical-workflow/methods/conjoint/**`
- Modify: `skills/empirical-workflow/references/identification-decision-tree.md`
- Modify: `skills/empirical-workflow/stages/stage6a-reduced-form.md`
- Modify: `research.example.yaml`
- Modify: `tests/test_workflow_contract.py`

**Interfaces:**
- Consumes: a locked design and the selected `allowed_designs` entry.
- Produces: one selectively loaded prompt/canon/details/template pack and its required evidence.

- [x] Add failing contract tests for pack inventory, canon fields, prompt routing, reference implementations, verified-through dates, and the expanded design list.
- [x] Run the contract suite and confirm the method-pack assertions fail.
- [x] Import and adapt the seven upstream method families, then split fixed effects and selection
  on observables from the general router into two additional focused packs; preserve prompt depth
  and source attribution.
- [x] Parse every imported R script with `Rscript -e 'parse(file=...)'` when R is available, then run contract tests.

### Task 5: Review, referee response, and release operations

**Files:**
- Create: `skills/research-council/SKILL.md`
- Create: `skills/manuscript-review/SKILL.md`
- Create: `skills/referee-response/SKILL.md`
- Create: `skills/replication-release/SKILL.md`
- Create: `skills/replication-release/scripts/*.py`
- Create: `skills/empirical-workflow/templates/review-finding-template.yaml`
- Create: `skills/empirical-workflow/templates/response-matrix-template.yaml`
- Create: `skills/empirical-workflow/templates/replication-checklist-template.md`
- Modify: `skills/empirical-workflow/stages/stage7-writing.md`
- Create: `tests/test_release_scanners.py`
- Modify: `tests/test_workflow_contract.py`

**Interfaces:**
- Consumes: manuscript, decision letter, code root, paper root, and governed evidence.
- Produces: review records, verified response pins, a staged release archive, and a release checklist.

- [x] Write failing tests for scanner masking, direct-identifier detection, QSF inspection, review schemas, non-majority synthesis, confidentiality gates, and pin verification.
- [x] Run scanner and contract tests and confirm the missing implementations fail.
- [x] Add the four companion skills, scripts, templates, and Stage 7 routing.
- [x] Run scanner tests and the complete contract suite.

### Task 6: LaTeX and presentation production

**Files:**
- Create: `skills/latex-production/**`
- Create: `skills/research-talk/**`
- Create: `skills/teaching-lecture/**`
- Create: `skills/slide-review/**`
- Create: `skills/course-site/**`
- Create: `agents/tikz-reviewer.md`
- Create: `presentation-tooling/**`
- Modify: `tests/test_workflow_contract.py`

**Interfaces:**
- Consumes: manuscripts or Quarto sources plus runtime-profile tool paths.
- Produces: ranked compile diagnostics, visually reviewed figures, rendered decks, and gate reports.

- [x] Add failing contract tests for skill inventory, runtime-profile routing, required references/assets, and the absence of personal absolute paths.
- [x] Run the contract suite and confirm the production-tool assertions fail.
- [x] Import and adapt the prompts, source templates, reviewer, and shared tooling without rendered output.
- [x] Run `node --check` over JavaScript files, `python3 -m py_compile` over Python helpers, and the contract suite.

### Task 7: Installation, documentation, and complete verification

**Files:**
- Modify: `README.md`
- Modify: `docs/v2-migration-guide.md`
- Modify: `CLAUDE.md`
- Modify: `AGENTS.md`
- Modify: `tests/test_workflow_contract.py`

**Interfaces:**
- Consumes: all new core and companion skills.
- Produces: cross-runtime installation and use instructions with a verified capability map.

- [x] Add failing documentation assertions for every companion skill, method-pack installation, runtime profile, attribution, and release sequence.
- [x] Run the contract suite and confirm documentation assertions fail.
- [x] Update installation, architecture, stage routing, migration, and setup documentation while keeping adapters thin.
- [x] Run `bash tests/run_contract_tests.sh`, all Python unit tests, Python compilation, R parsing when available, Node syntax checks, and `git diff --check`.
- [x] Compare the completed tree against every section of the approved design and record any remaining gap before reporting completion.

## Verification record

- `bash tests/run_contract_tests.sh`: 19 passed.
- `.venv/bin/python -m pytest -q`: 33 passed.
- Python compilation, all nine method-template R parses, bundled-Node syntax checks, YAML parsing,
  portability scans, and `git diff --check`: passed.
- `bash tests/smoke/run_smoke.sh`: attempted but not completed. The host R installation lacks a
  working `arrow` namespace and segfaults when the smoke harness checks the package set. Individual
  checks show `yaml`, `fixest`, and `modelsummary` available and `arrow` unavailable. No smoke-test
  source or expected output was changed to hide this environment failure.
