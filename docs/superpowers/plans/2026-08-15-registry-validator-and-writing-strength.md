# Registry Validator and Writing Strength Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make v2.1 claim governance executable, then add the v2.2 writing-strength specification and validator extension without changing the workflow's stages, checkpoints, or mandatory pauses.

**Architecture:** A Python command reads reviewable YAML registries and derives Checkpoint B/C reports from one dependency traversal. Registry validation is kept separate from Stage 7 assertion-site validation, but both use the same parsed registry state and JSON report schema. Shell smoke tests invoke the command over small YAML fixtures, while unit tests exercise individual failures.

**Tech Stack:** Python 3, PyYAML, pytest, bash smoke runner, Markdown specifications.

**Spec:** `docs/superpowers/specs/2026-08-15-claim-governance-v2.1-design.md` and `docs/superpowers/specs/2026-08-15-codex-brief-v2.1-corrections-and-v2.2.md`

## Global Constraints

- Registry files are human-editable YAML kept in the repository; every state change must be reviewable as text.
- Do not change stage boundaries, checkpoint placement, or mandatory-pause triggers.
- Cascade is monotone: the system adds derived bad states; authored revalidation/resolution improves them with author, timestamp, and evidence.
- `post_hoc` is derived per gate evaluation using its pipeline's `first_formal_batch_at`.
- Assertion type precedes tier; only `world` assertions use T0–T4.
- Run `bash tests/run_contract_tests.sh` and `bash tests/smoke/run_smoke.sh` before committing every task.

---

### Task 1: Correct and lock the v2.1 contract

**Files:**
- Modify: `docs/superpowers/specs/2026-08-15-claim-governance-v2.1-design.md`
- Modify: `tests/test_workflow_contract.py`

**Interfaces:**
- Produces: canonical field names consumed by `tools/validate_registry.py`: `pipeline.first_formal_batch_at`, `gate_evaluation.post_hoc`, and `revalidation.target`.

- [ ] **Step 1: Add a failing contract assertion for the corrected prose**

```python
def test_v21_spec_has_per_evaluation_post_hoc_and_figure_revalidation():
    body = read("docs/superpowers/specs/2026-08-15-claim-governance-v2.1-design.md")
    assert "first_formal_batch_at" in body
    assert "target: {kind: claim_revision | reported_figure, id: ...}" in body
    assert "Checkpoint C reports post-hoc evaluations" in body
```

- [ ] **Step 2: Run the focused test and confirm it fails**

Run: `python3 -m pytest tests/test_workflow_contract.py -q`

Expected: FAIL because the existing prose puts `post_hoc` on a definition and lacks a reported-figure target.

- [ ] **Step 3: Apply A-1 through A-7 exactly**

Update the design document to:

```yaml
pipeline:
  pipeline_id: p03
  first_formal_batch_at: 2026-04-17T00:00:00Z

gate_evaluation:
  gate_id: G-004
  pipeline_id: p03
  post_hoc: derived

revalidation:
  target: {kind: claim_revision | reported_figure, id: ...}
```

Specify the A-2 recomputation rule, A-3 moot trigger set, A-4 live-support recomputation, A-5 inapplicable fields/reporting, A-6 fixtures, and A-7 no-overlap wording.

- [ ] **Step 4: Run both regression suites**

Run: `bash tests/run_contract_tests.sh && bash tests/smoke/run_smoke.sh`

Expected: both exit 0.

- [ ] **Step 5: Commit the phase gate**

```bash
git add docs/superpowers/specs/2026-08-15-claim-governance-v2.1-design.md tests/test_workflow_contract.py
git commit -m "docs: correct v2.1 registry contract"
```

### Task 2: Implement the v2.1 registry validator and fixtures

**Files:**
- Create: `tools/validate_registry.py`
- Create: `tests/test_registry_validator.py`
- Create: `tests/smoke/registry-fixtures/`
- Modify: `tests/smoke/run_smoke.sh`
- Modify: `requirements-dev.txt`

**Interfaces:**
- Consumes: a registry directory containing `pipelines.yaml`, `claims.yaml`, `evidence_cards.yaml`, `evidence_relations.yaml`, `reported_figures.yaml`, `outputs.yaml`, `gates.yaml`, `semantics.yaml`, `derived_fields.yaml`, and `applicability.yaml`.
- Produces: `python3 tools/validate_registry.py REGISTRY_DIR --checkpoint B|C --format json`, a JSON object with `checkpoint`, `blocking`, `reports`, and `derived`.
- Produces: exit code 0 only when `blocking` is empty.

- [ ] **Step 1: Write failing unit tests for parser, invariants, cascade, and export eligibility**

```python
def test_superseded_pipeline_derives_stale_and_blocks_export(tmp_path):
    write_registry(tmp_path, pipeline_status="superseded")
    report = validate_registry(tmp_path, checkpoint="C")
    assert any(item["code"] == "STALE_CLAIM" for item in report["derived"])
    assert any(item["code"] == "PUBLICATION_INELIGIBLE" for item in report["blocking"])
```

Add tests for semantic coverage, semantic bottom-layer violations, reference cycles, same-pipeline claim bindings, mixed outputs, reconciliation retaining stale, all gate closures, reported-figure revalidation, and all four A-6 regressions.

- [ ] **Step 2: Run the focused suite and confirm it fails**

Run: `python3 -m pytest tests/test_registry_validator.py -q`

Expected: FAIL because `tools/validate_registry.py` does not exist.

- [ ] **Step 3: Implement a focused validator**

Implement these public functions and CLI:

```python
def load_registry(root: Path) -> dict: ...
def validate_registry(registry: dict, checkpoint: str) -> dict: ...
def main(argv: list[str] | None = None) -> int: ...
```

Validate required fields, semantic intervals, no-derived semantic verification, reference graph acyclicity, all three pipeline/output invariants, gate timing/coverage/closure, applicability substitutes, cascade order, revalidation, reported-figure transform recomputation, and publication eligibility. Emit stable codes and JSON only when `--format json` is requested.

- [ ] **Step 4: Add smoke fixtures and shell assertions**

Create the seven baseline scenarios and four A-6 scenarios. The smoke runner must assert each expected pass/fail using the CLI exit status and a JSON code check:

```bash
if python3 tools/validate_registry.py tests/smoke/registry-fixtures/mixed-output --checkpoint C --format json; then
  echo "mixed output unexpectedly passed" >&2
  exit 1
fi
```

- [ ] **Step 5: Run full suites**

Run: `bash tests/run_contract_tests.sh && bash tests/smoke/run_smoke.sh`

Expected: both exit 0; smoke proves pipeline stale, machine revalidation, semantic correction, semantic disclosure, incomplete release, handoff, failed identification, per-evaluation post-hoc, mixed output, reconciliation, and incomplete substitute behavior.

- [ ] **Step 6: Commit the validator phase gate**

```bash
git add tools/validate_registry.py tests/test_registry_validator.py tests/smoke requirements-dev.txt
git commit -m "feat: validate claim governance registries"
```

### Task 3: Author the v2.2 writing-strength design and route it into workflow contracts

**Files:**
- Create: `docs/superpowers/specs/2026-08-15-writing-strength-v2.2-design.md`
- Modify: `skills/empirical-workflow/stages/stage6b-structural.md`
- Modify: `skills/empirical-workflow/stages/stage7-writing.md`
- Modify: `tests/test_workflow_contract.py`

**Interfaces:**
- Produces: assertion-site YAML fields consumed by Task 4: `assertion_type`, `declared_tier`, `qualifier_scope`, `counterevidence_prominence`, `underlying_precision`, `scope_declaration`, `power_basis`, and `upgrade_justification`.

- [ ] **Step 1: Write failing contract assertions for v2.2 routing**

```python
def test_writing_strength_design_routes_structural_and_stage7_rules():
    design = read("docs/superpowers/specs/2026-08-15-writing-strength-v2.2-design.md")
    assert "Assertion type is prior to tier" in design
    assert "overclaim_residual" in design
    assert "Low lexical strength is normal" in design
    assert "identified" in read("skills/empirical-workflow/stages/stage6b-structural.md")
```

- [ ] **Step 2: Run the focused suite and confirm it fails**

Run: `python3 -m pytest tests/test_workflow_contract.py -q`

Expected: FAIL because the v2.2 design and contract routes do not yet exist.

- [ ] **Step 3: Write the design from Part B without copying the evidence paper**

Specify the five assertion types, world-only T0–T4 ladder, all modifiers, registered-sites-only lexical scan, residual and its outcomes, the four checks, scope declarations, project-extensible semantic classes, and structural-estimation wording. State that abstract/title upgrades require a recorded trace and only WARN.

- [ ] **Step 4: Update Stage 6b and Stage 7 contracts**

Add `identified` versus `calibrated` lexical distinction, typed `identified → simulated` model-internal outputs, registered counterfactual scope declarations, and Stage 7 registry/validator use. Do not alter stage exits or pause triggers.

- [ ] **Step 5: Run full suites and commit**

Run: `bash tests/run_contract_tests.sh && bash tests/smoke/run_smoke.sh`

```bash
git add docs/superpowers/specs/2026-08-15-writing-strength-v2.2-design.md skills/empirical-workflow/stages tests/test_workflow_contract.py
git commit -m "docs: add v2.2 writing strength design"
```

### Task 4: Extend the validator with v2.2 assertion-site checks

**Files:**
- Modify: `tools/validate_registry.py`
- Modify: `tests/test_registry_validator.py`
- Create: `tests/smoke/registry-fixtures/writing-strength/`
- Modify: `tests/smoke/run_smoke.sh`

**Interfaces:**
- Consumes: claim assertion sites and source files relative to the registry directory.
- Produces: `OVERCLAIM_RESIDUAL`, `NARROWING_NOT_PROPAGATED`, `COUNTEREVIDENCE_BURIED` blockers; `IMMEDIATE_RECOVERY`, `UPGRADE_TRACE_MISSING`, and underclaim residual reports.

- [ ] **Step 1: Write failing tests for type-specific rules, residual, and four checks**

```python
def test_discriminating_site_with_low_lexical_strength_is_not_an_underclaim():
    report = validate_registry(load_fixture("discriminating-low-lexical"), checkpoint="C")
    assert "OVERCLAIM_RESIDUAL" not in report_codes(report)
    assert "UNDERCLAIM_RESIDUAL" not in report_codes(report)
```

Cover missing negative `power_basis`, model-internal `significant` without sampling distribution, positive/negative residuals, narrowing propagation, identifying-assumption disclosure prominence, immediate recovery, and abstract/title upgrade traces.

- [ ] **Step 2: Run the focused suite and confirm it fails**

Run: `python3 -m pytest tests/test_registry_validator.py -q`

Expected: FAIL because no assertion-site validator exists.

- [ ] **Step 3: Implement v2.2 checks within the existing traversal**

Add a registered-site-only lexical classifier with project-configurable causal, scope-qualifying, associational, descriptive, and framing markers. Compute evidence strength from v2.1 state and `underlying_precision`; only `world` uses the residual. Keep `discriminating` low lexical strength neutral. Make positive residual, propagation, and buried identifying counterevidence blocking; make immediate recovery and upgrade trace reporting-only.

- [ ] **Step 4: Add smoke assertions for blocking and warning cases**

Use fixture text anchored by stable markers. Assert that a stronger abstract/title with an upgrade justification emits no blocker and that it still emits a warning when the trace is absent.

- [ ] **Step 5: Run full suites and commit**

Run: `bash tests/run_contract_tests.sh && bash tests/smoke/run_smoke.sh`

```bash
git add tools/validate_registry.py tests/test_registry_validator.py tests/smoke
git commit -m "feat: validate writing strength assertions"
```

## Self-Review

| Requirement | Task |
|---|---|
| A-1 through A-7 prose corrections | 1 |
| Validator before writing-strength work | 2 before 3 |
| Human-reviewable YAML and v2.1 cascade | 2 |
| Seven baseline plus A-6 smoke cases | 2 |
| Type-first, residual, and corpus-calibrated warning/block rules | 3 and 4 |
| Stage 6b structural and Stage 7 routing | 3 |

The plan has no placeholders, all exported interfaces are named in their producing task, and each task runs both required project suites before committing.
