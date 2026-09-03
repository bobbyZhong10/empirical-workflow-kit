# Empirical Workflow v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Upgrade the workflow kit into a portable, high-autonomy protocol for IS, management, and economics panel causal research.

**Architecture:** Put runtime-independent research rules in RESEARCH_PROTOCOL.md, with thin Claude and Codex adapters. Use templates and evidence cards as the project source of truth, keep Python and R research code linear, and validate the kit with static contract tests plus a Python-R smoke test.

**Tech Stack:** Markdown, YAML, Python 3 with PyArrow, R with arrow, yaml, fixest, and modelsummary.

**Spec:** docs/superpowers/specs/2026-08-15-empirical-workflow-v2-design.md

## Global Constraints

- Communicate in the user's initial primary language; write repository artifacts and code comments in English.
- Target firm, platform, and market panel causal research. MS, ISR, and MISQ are targets; UTD 24, FT50, top economics journals, JAIS, and IJRM are reference pools.
- Keep CLAUDE.md and AGENTS.md thin. Put portable research rules only in RESEARCH_PROTOCOL.md.
- Use numbered, direct Python and R research scripts. Do not introduce research-code packages, classes, or deep abstraction.
- Python owns ingestion, merging, entity resolution, and Parquet exports. R owns construction, diagnostics, estimation, and tables.
- Never silently change a locked specification, sample, clustering level, or identifying strategy.
- Never overwrite raw data.
- The current Git top-level is /Users/bobbyzhong, not this workspace. Do not run git add or git commit unless git rev-parse --show-toplevel equals the workspace path exactly.
- Each task must pass its stated validation before the next task begins.

---

## File map

| Path | Responsibility |
|---|---|
| RESEARCH_PROTOCOL.md | Portable governance, authority levels, stage interfaces, handoff order, and red lines |
| CLAUDE.md | Claude Code adapter |
| AGENTS.md | Codex adapter |
| research.example.yaml | Copyable project start card |
| skills/empirical-workflow/SKILL.md | Skill router |
| skills/empirical-workflow/templates/ | Status, decision, evidence, literature, and data-contract templates |
| skills/empirical-workflow/references/ | Methods, outlet, audit, and coding standards |
| skills/empirical-workflow/stages/ | Seven stage contracts |
| tests/test_workflow_contract.py | Standard-library validation of required artifacts |
| tests/smoke/ | Simulated Python-R transfer and failure-stop fixture |
| README.md | Installation and use guide |

### Task 1: Portable protocol and project start card

**Files:**
- Create: RESEARCH_PROTOCOL.md
- Create: research.example.yaml
- Create: tests/test_workflow_contract.py
- Modify: README.md

**Interfaces:**
- Consumes: The approved v2 specification.
- Produces: Portable rules referenced by both adapters and an explicit configuration record.

- [ ] **Step 1: Write the failing static test**

Create tests/test_workflow_contract.py:

~~~python
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(path):
    return (ROOT / path).read_text(encoding="utf-8")

def test_portable_protocol_and_config():
    assert (ROOT / "RESEARCH_PROTOCOL.md").is_file()
    assert (ROOT / "research.example.yaml").is_file()
    body = read("RESEARCH_PROTOCOL.md")
    for phrase in ("Mandatory pause", "Executor", "Copilot",
                   "Quality auditor", "research.yaml",
                   "decision-log.md", "Evidence card"):
        assert phrase in body

def test_example_config_fields():
    body = read("research.example.yaml")
    for key in ("target_outlets:", "reference_pools:", "observation_unit:",
                "analysis_languages:", "allowed_designs:", "autonomy_mode:",
                "current_stage:"):
        assert key in body
~~~

- [ ] **Step 2: Verify the test fails**

Run: python3 -m pytest tests/test_workflow_contract.py -q

Expected: FAIL because RESEARCH_PROTOCOL.md and research.example.yaml do not exist.

- [ ] **Step 3: Create the portable protocol**

Write RESEARCH_PROTOCOL.md with these ordered headings: Purpose and scope; Source of truth and handoff; Roles; Authority levels; Mandatory pause; Stage interface; Checkpoints; Specification discipline; Python-R boundary; Evidence records; Independent review.

The Mandatory pause section must name: material design change, failed identifying diagnostic, post-result specification, and external publication or submission.

- [ ] **Step 4: Create the complete configuration example**

Write research.example.yaml:

~~~yaml
project_name: example_platform_adoption
target_outlets: [Management Science, ISR, MISQ]
reference_pools: [UTD24, FT50, TopEcon, JAIS, IJRM]
research_domain: platform_and_firm_panel_causal
observation_unit: firm_quarter
analysis_languages:
  etl: python
  estimation: r
allowed_designs: [fixed_effects, did, event_study, ddd, iv, rdd]
autonomy_mode: complete_with_red_lines
current_stage: stage_1_data_infrastructure
primary_data_format: parquet
conversation_language: initial_user_primary_language
artifact_language: English
~~~

- [ ] **Step 5: Update README install instructions**

State that a project copies RESEARCH_PROTOCOL.md, one or both adapters, research.example.yaml renamed to research.yaml, and the skill directory. Explain that the same project may move between Claude Code and Codex.

- [ ] **Step 6: Verify the tests pass**

Run: python3 -m pytest tests/test_workflow_contract.py -q

Expected: PASS.

- [ ] **Step 7: Apply the Git safety guard**

Run: test "$(git rev-parse --show-toplevel)" = "$PWD"

Expected currently: FAIL. Record that no commit was made. If it passes after repository repair, commit Task 1 with message: feat: add portable research protocol.

### Task 2: Runtime adapters and durable research records

**Files:**
- Modify: CLAUDE.md
- Create: AGENTS.md
- Modify: skills/empirical-workflow/templates/status-template.md
- Create: skills/empirical-workflow/templates/decision-log-template.md
- Create: skills/empirical-workflow/templates/evidence-card-template.md
- Create: skills/empirical-workflow/templates/literature-map-template.md
- Modify: tests/test_workflow_contract.py

**Interfaces:**
- Consumes: RESEARCH_PROTOCOL.md and research.yaml.
- Produces: Thin runtime adapters and uniform artifacts used by all roles.

- [ ] **Step 1: Add the failing adapter test**

Append:

~~~python
def test_adapters_and_records():
    required = (
        "CLAUDE.md", "AGENTS.md",
        "skills/empirical-workflow/templates/decision-log-template.md",
        "skills/empirical-workflow/templates/evidence-card-template.md",
        "skills/empirical-workflow/templates/literature-map-template.md",
    )
    for path in required:
        assert (ROOT / path).is_file()
    for path in ("CLAUDE.md", "AGENTS.md"):
        body = read(path)
        assert "RESEARCH_PROTOCOL.md" in body
        assert len(body.splitlines()) < 140
~~~

- [ ] **Step 2: Verify it fails**

Run: python3 -m pytest tests/test_workflow_contract.py::test_adapters_and_records -q

Expected: FAIL because AGENTS.md and the records are absent.

- [ ] **Step 3: Write the adapters**

Rewrite CLAUDE.md and create AGENTS.md. Both state initial-user-language conversation, English artifacts, mandatory reading of RESEARCH_PROTOCOL.md and research.yaml, and the cross-runtime handoff order. CLAUDE.md keeps only Claude-specific routing. AGENTS.md keeps only Codex-specific constraints. Neither repeats checkpoint or estimator details.

- [ ] **Step 4: Create record templates**

Decision log: append-only fields timestamp, decision, alternatives, reason, evidence state, authorized by, and downstream artifacts.

Evidence card: batch identifier, producer runtime, data version, data-contract path, sample rule, estimator and formula, fixed effects, clustering, output paths, key result, limitations, audit status, and decision-log reference.

Literature map: four tables titled Target Outlet, Theory, Empirical Precedent, and Method. Every row includes a verified source location and one purpose label.

Extend status-template.md with Current evidence card, Project configuration path, Runtime last used, and Open mandatory-pause item.

- [ ] **Step 5: Verify all tests pass**

Run: python3 -m pytest tests/test_workflow_contract.py -q

Expected: PASS.

- [ ] **Step 6: Apply the Git safety guard**

Run: test "$(git rev-parse --show-toplevel)" = "$PWD"

Expected currently: FAIL. If safe after repository repair, commit with message: feat: add cross-runtime research records.

### Task 3: Stages 1 to 5 as stage contracts

**Files:**
- Modify: skills/empirical-workflow/SKILL.md
- Modify: skills/empirical-workflow/stages/stage1-data-infra.md
- Modify: skills/empirical-workflow/stages/stage2-lit-map.md
- Modify: skills/empirical-workflow/stages/stage3-theory-hypotheses.md
- Modify: skills/empirical-workflow/stages/stage4-variables.md
- Modify: skills/empirical-workflow/stages/stage5-measurement.md
- Modify: tests/test_workflow_contract.py

**Interfaces:**
- Consumes: Protocol and templates.
- Produces: Named artifacts and deterministic exit gates for early research stages.

- [ ] **Step 1: Add the failing stage test**

Append:

~~~python
def test_stage_contracts():
    stages = sorted((ROOT / "skills/empirical-workflow/stages").glob("stage*.md"))
    assert len(stages) == 8
    headings = ("## Inputs", "## Automatic actions", "## Required artifacts",
                "## Red lines", "## Exit condition")
    for stage in stages:
        body = stage.read_text(encoding="utf-8")
        for heading in headings:
            assert heading in body, f"{stage.name} lacks {heading}"
~~~

- [ ] **Step 2: Verify it fails**

Run: python3 -m pytest tests/test_workflow_contract.py::test_stage_contracts -q

Expected: FAIL because current stage files lack the five headings.

- [ ] **Step 3: Update the router**

Make SKILL.md require reading RESEARCH_PROTOCOL.md, research.yaml, _status.md, the current evidence card, and the decision-log tail before stage selection. Retain on-demand stage loading. Remove global per-sub-step confirmation in favor of mandatory-pause routing.

- [ ] **Step 4: Rewrite stages 1 through 5**

Add the five headings to every file. Require these artifacts and checks:

- Stage 1: source/version inventory, panel dimensions, key integrity, merge-rate evidence, and entry-exit report.
- Stage 2: four-track literature map, verified bibliography, citation purpose label, and outlet-positioning memo.
- Stage 3: identifying-assumption sentence, null-interest test, alternatives, and locked hypothesis-to-estimate map.
- Stage 4: announcement/effective/actual treatment timeline, treatment exit, and post-treatment-selection warning.
- Stage 5: proxy justification, functional-form lock, data-contract validation, and descriptive integrity record.

- [ ] **Step 5: Verify all static tests pass**

Run: python3 -m pytest tests/test_workflow_contract.py -q

Expected: PASS.

- [ ] **Step 6: Apply the Git safety guard**

Run: test "$(git rev-parse --show-toplevel)" = "$PWD"

Expected currently: FAIL. If safe after repository repair, commit with message: feat: define early-stage research contracts.

### Task 4: Causal design, results, and writing protocol

**Files:**
- Modify: skills/empirical-workflow/stages/stage6a-reduced-form.md
- Modify: skills/empirical-workflow/stages/stage6b-structural.md
- Modify: skills/empirical-workflow/stages/stage7-writing.md
- Modify: skills/empirical-workflow/references/identification-decision-tree.md
- Modify: skills/empirical-workflow/references/robustness-checklists.md
- Create: skills/empirical-workflow/references/outlet-positioning.md
- Modify: tests/test_workflow_contract.py

**Interfaces:**
- Consumes: Locked designs, variable map, literature map, and data contract.
- Produces: Design-specific evidence cards, economics-style tables, and claim audits.

- [ ] **Step 1: Add the failing causal-policy test**

Append:

~~~python
def test_causal_platform_risks_and_traceability():
    tree = read("skills/empirical-workflow/references/identification-decision-tree.md").lower()
    for phrase in ("anticipation", "spillover", "treatment exit", "negative weights"):
        assert phrase in tree
    reduced = read("skills/empirical-workflow/stages/stage6a-reduced-form.md")
    assert "Evidence card" in reduced
    writing = read("skills/empirical-workflow/stages/stage7-writing.md").lower()
    assert "three-line" in writing
~~~

- [ ] **Step 2: Verify it fails**

Run: python3 -m pytest tests/test_workflow_contract.py::test_causal_platform_risks_and_traceability -q

Expected: FAIL until all risks and result records are stated.

- [ ] **Step 3: Upgrade method references**

Extend the decision tree for announcement versus actual treatment, anticipation, intensity, repeat treatment, treatment exit, spillover or interference, entry and exit, and assignment-consistent aggregation. Keep heterogeneity-robust staggered DID as main, TWFE reference-only, and negative-weight diagnostics mandatory.

Replace robustness pass-rate voting with an evidence matrix: check, identifying threat, pre-committed/exploratory status, result, implication, severity, disposition.

- [ ] **Step 4: Rewrite stages 6a, 6b, and 7**

Use the five stage-contract headings. Require an identification memo and an evidence card for every formal 6a batch. In 6b, each parameter must be identified or labeled calibrated. In 7, require three-line economics tables, a claim-to-evidence audit, verified citations, and independent-runtime review of identification.

Create outlet-positioning.md with rows for target outlet, framing anchor, theory source, empirical analogue, and method authority.

- [ ] **Step 5: Verify all static tests pass**

Run: python3 -m pytest tests/test_workflow_contract.py -q

Expected: PASS.

- [ ] **Step 6: Apply the Git safety guard**

Run: test "$(git rev-parse --show-toplevel)" = "$PWD"

Expected currently: FAIL. If safe after repository repair, commit with message: feat: strengthen causal and publication protocol.

### Task 5: Python-R contract and code standards

**Files:**
- Create: skills/empirical-workflow/references/data-contract.md
- Create: skills/empirical-workflow/templates/data-contract-template.yaml
- Modify: skills/empirical-workflow/references/r-standards.md
- Create: skills/empirical-workflow/references/python-standards.md
- Modify: tests/test_workflow_contract.py

**Interfaces:**
- Consumes: Python ETL exports.
- Produces: Parquet plus a YAML contract that R validates before formal analysis.

- [ ] **Step 1: Add the failing data-contract test**

Append:

~~~python
def test_data_contract_template():
    path = ROOT / "skills/empirical-workflow/templates/data-contract-template.yaml"
    assert path.is_file()
    body = path.read_text(encoding="utf-8")
    for key in ("data_version:", "producing_script:", "observation_unit:",
                "time_granularity:", "primary_key:", "row_count:",
                "unit_count:", "period_count:", "missingness:", "merge_rates:"):
        assert key in body
~~~

- [ ] **Step 2: Verify it fails**

Run: python3 -m pytest tests/test_workflow_contract.py::test_data_contract_template -q

Expected: FAIL because the template is absent.

- [ ] **Step 3: Create the contract specification and template**

Data-contract.md must require data version, source versions, data hash, producing script, keys and uniqueness result, row and panel counts, field types, missingness, value ranges, and merge rates.

The template must be valid YAML and fully populated with fictional firm_quarter data and primary key firm_id + year_qtr.

- [ ] **Step 4: Update both language standards**

R standards require contract validation before 01_construct.R and abort on failed key, count, or required-field checks. Python standards require numbered linear scripts, Parquet exports, concise English comments, and never writing raw data.

- [ ] **Step 5: Verify all static tests pass**

Run: python3 -m pytest tests/test_workflow_contract.py -q

Expected: PASS.

- [ ] **Step 6: Apply the Git safety guard**

Run: test "$(git rev-parse --show-toplevel)" = "$PWD"

Expected currently: FAIL. If safe after repository repair, commit with message: feat: define python r data contract.

### Task 6: Simulated Python-R smoke test and mandatory-stop check

**Files:**
- Create: tests/smoke/generate_panel.py
- Create: tests/smoke/panel-contract.yaml
- Create: tests/smoke/verify_panel.R
- Create: tests/smoke/run_smoke.sh
- Modify: README.md

**Interfaces:**
- Consumes: Data-contract template and coding standards.
- Produces: A repeatable fixture that tests handoff, a staggered-treatment-safe path, table output, and failed-contract stopping.

- [ ] **Step 1: Write the failing smoke runner**

Create tests/smoke/run_smoke.sh:

~~~bash
#!/usr/bin/env bash
set -euo pipefail
python3 tests/smoke/generate_panel.py
Rscript tests/smoke/verify_panel.R tests/smoke/panel-contract.yaml
if Rscript tests/smoke/verify_panel.R tests/smoke/invalid-contract.yaml; then
  echo "invalid contract unexpectedly passed" >&2
  exit 1
fi
test -f tests/smoke/output/smoke_table.md
~~~

- [ ] **Step 2: Verify it fails**

Run: bash tests/smoke/run_smoke.sh

Expected: FAIL because generator, R verifier, and contracts are absent.

- [ ] **Step 3: Implement the deterministic fixture**

generate_panel.py uses random.Random(20260815) and PyArrow to generate 12 firms across 8 quarters: four staggered cohorts and four never-treated firms. It writes panel.parquet with firm_id, year_qtr, treated, event_time, and outcome, plus a valid 96-row panel-contract.yaml. It also writes invalid-contract.yaml with row_count: 95.

- [ ] **Step 4: Implement the R verifier**

verify_panel.R reads its contract and panel.parquet, and stops with exactly Data contract validation failed if row count, key uniqueness, or required fields are inconsistent. On a valid contract it runs a small fixest::feols model with firm and quarter fixed effects and writes tests/smoke/output/smoke_table.md. The table note declares that the data are simulated and includes N, FE, and clustering.

- [ ] **Step 5: Verify the smoke test passes**

Run: bash tests/smoke/run_smoke.sh

Expected: exit 0; the invalid contract fails internally as expected; smoke_table.md exists.

- [ ] **Step 6: Document dependencies and command**

Add Python 3, PyArrow, R, arrow, yaml, fixest, and modelsummary to README. Document bash tests/smoke/run_smoke.sh and its expected invalid-contract behavior.

- [ ] **Step 7: Apply the Git safety guard**

Run: test "$(git rev-parse --show-toplevel)" = "$PWD"

Expected currently: FAIL. If safe after repository repair, commit with message: test: add empirical workflow smoke test.

### Task 7: Integration review and migration guide

**Files:**
- Create: docs/v2-migration-guide.md
- Modify: README.md
- Modify: tests/test_workflow_contract.py

**Interfaces:**
- Consumes: All prior artifacts.
- Produces: A migration path from the existing kit and a verified v2 release boundary.

- [ ] **Step 1: Add the final failing README test**

Append:

~~~python
def test_readme_cross_runtime_quickstart():
    body = read("README.md")
    for phrase in ("Claude Code", "Codex", "RESEARCH_PROTOCOL.md",
                   "research.yaml", "tests/smoke/run_smoke.sh"):
        assert phrase in body
~~~

- [ ] **Step 2: Verify it fails**

Run: python3 -m pytest tests/test_workflow_contract.py::test_readme_cross_runtime_quickstart -q

Expected: FAIL until final README text is present.

- [ ] **Step 3: Create the migration guide**

Write docs/v2-migration-guide.md with: retained v1 files, v2 replacements, cross-runtime new-project bootstrap, migration of an existing _status.md project, and required handoff order.

- [ ] **Step 4: Finalize README and run validations**

Add a plain-text architecture diagram, runtime selection, bootstrap sequence, evidence-card explanation, and smoke-test command.

Run:

~~~bash
python3 -m pytest tests/test_workflow_contract.py -q
bash tests/smoke/run_smoke.sh
~~~

Expected: both commands exit 0.

- [ ] **Step 5: Check coverage against the approved specification**

Add a table in docs/v2-migration-guide.md mapping every heading in the approved specification to at least one implemented artifact. If any heading lacks coverage, add its minimal missing artifact and rerun both validation commands.

- [ ] **Step 6: Apply the Git safety guard**

Run: test "$(git rev-parse --show-toplevel)" = "$PWD"

Expected currently: FAIL. If safe after repository repair, commit with message: docs: publish empirical workflow v2.
