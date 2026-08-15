from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def test_portable_protocol_contract():
    assert (ROOT / "RESEARCH_PROTOCOL.md").is_file()
    assert (ROOT / "research.example.yaml").is_file()
    body = read("RESEARCH_PROTOCOL.md")
    headings = (
        "## Purpose and scope",
        "## Source of truth and handoff",
        "## Roles",
        "## Authority levels",
        "## Mandatory pause",
        "## Stage interface",
        "## Checkpoints",
        "## Specification discipline",
        "## Python-R boundary",
        "## Evidence records",
        "## Independent review",
    )
    assert [body.index(heading) for heading in headings] == sorted(
        body.index(heading) for heading in headings
    )
    normalized_body = " ".join(body.split())
    for phrase in (
        "Executor",
        "Copilot",
        "Quality auditor",
        "research.yaml",
        "decision-log.md",
        "Evidence card",
        "material design change",
        "failed identifying diagnostic",
        "post-result specification",
        "external publication or submission",
        "Raw data is never overwritten",
        "Research scripts are numbered and direct",
        "main specification",
        "estimation sample",
        "clustering level",
        "identifying strategy",
        "recorded decision before execution",
    ):
        assert phrase in normalized_body


def test_v21_spec_has_per_evaluation_post_hoc_and_figure_revalidation():
    body = read("docs/superpowers/specs/2026-08-15-claim-governance-v2.1-design.md")
    assert "first_formal_batch_at" in body
    assert "target: {kind: claim_revision | reported_figure, id: ...}" in body
    assert "Checkpoint C reports post-hoc evaluations" in body


def test_example_config_values():
    config = yaml.safe_load(read("research.example.yaml"))
    assert config == {
        "project_name": "example_platform_adoption",
        "target_outlets": ["Management Science", "ISR", "MISQ"],
        "reference_pools": ["UTD24", "FT50", "TopEcon", "JAIS", "IJRM"],
        "research_domain": "platform_and_firm_panel_causal",
        "observation_unit": "firm_quarter",
        "analysis_languages": {"etl": "python", "estimation": "r"},
        "allowed_designs": ["fixed_effects", "did", "event_study", "ddd", "iv", "rdd"],
        "autonomy_mode": "complete_with_red_lines",
        "current_stage": "stage_1_data_infrastructure",
        "primary_data_format": "parquet",
        "conversation_language": "Chinese",
        "artifact_language": "English",
        "analysis_input_contract": {
            "data_version": "firm_quarter_v2026_08_15",
            "dataset_path": "data/analysis/firm_quarter.parquet",
            "producing_script": "code/py/04_export.py",
            "time_granularity": "quarter",
            "primary_key": ["firm_id", "year_qtr"],
        },
    }


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
        handoff = body.split("## Cross-runtime handoff", maxsplit=1)[1].lower()
        continuation_order = (
            "research_protocol.md",
            "research.yaml",
            "_status.md",
            "most relevant/current evidence card",
            "decision-log.md",
        )
        assert [handoff.index(item) for item in continuation_order] == sorted(
            handoff.index(item) for item in continuation_order
        )


def test_codex_install_uses_discovered_agents_skill_path():
    for path in ("README.md", "docs/v2-migration-guide.md"):
        body = read(path)
        assert ".agents/skills/empirical-workflow" in body
        assert ".codex/skills/empirical-workflow" not in body


def test_stage_contracts():
    stages = sorted((ROOT / "skills/empirical-workflow/stages").glob("stage*.md"))
    assert len(stages) == 8
    headings = (
        "## Inputs",
        "## Automatic actions",
        "## Required artifacts",
        "## Red lines",
        "## Exit condition",
    )
    for stage in stages:
        body = stage.read_text(encoding="utf-8")
        for heading in headings:
            assert heading in body, f"{stage.name} lacks {heading}"


def test_shared_standards_are_routed_to_producer_and_consumers():
    router = read("skills/empirical-workflow/SKILL.md")
    for reference in ("references/data-contract.md", "references/python-standards.md", "references/r-standards.md"):
        assert reference in router

    stage1 = read("skills/empirical-workflow/stages/stage1-data-infra.md")
    assert "references/python-standards.md" in stage1
    assert "references/data-contract.md" in stage1
    for stage in ("stage5-measurement.md", "stage6a-reduced-form.md", "stage6b-structural.md"):
        body = read(f"skills/empirical-workflow/stages/{stage}")
        assert "references/data-contract.md" in body
        assert "references/r-standards.md" in body


def test_decision_log_is_the_only_append_only_history_and_checkpoints_have_no_waivers():
    status = read("skills/empirical-workflow/templates/status-template.md")
    normalized = " ".join(status.split()).lower()
    assert "decision-log.md is the sole append-only history" in normalized
    assert "## 6. Decision log" not in status
    assert "## 7. Abandoned approaches (append only)" not in status

    governed = "\n".join(
        read(path)
        for path in (
            "RESEARCH_PROTOCOL.md",
            "skills/empirical-workflow/SKILL.md",
            "skills/empirical-workflow/stages/stage3-theory-hypotheses.md",
            "skills/empirical-workflow/stages/stage5-measurement.md",
        )
    ).lower()
    assert "waiver" not in governed


def test_causal_platform_risks_and_traceability():
    tree = read("skills/empirical-workflow/references/identification-decision-tree.md").lower()
    for phrase in ("anticipation", "spillover", "treatment exit", "negative weights"):
        assert phrase in tree
    reduced = read("skills/empirical-workflow/stages/stage6a-reduced-form.md")
    assert "Evidence card" in reduced
    writing = read("skills/empirical-workflow/stages/stage7-writing.md").lower()
    assert "three-line" in writing


def test_data_contract_template():
    path = ROOT / "skills/empirical-workflow/templates/data-contract-template.yaml"
    assert path.is_file()
    body = path.read_text(encoding="utf-8")
    for key in (
        "project_name:",
        "data_version:",
        "producing_script:",
        "observation_unit:",
        "time_granularity:",
        "primary_key:",
        "row_count:",
        "unit_count:",
        "period_count:",
        "missingness:",
        "merge_rates:",
        "merge_audit:",
    ):
        assert key in body
    contract = yaml.safe_load(body)
    project = yaml.safe_load(read("research.example.yaml"))
    expected_identity = project["analysis_input_contract"]
    assert contract["project_name"] == project["project_name"]
    assert contract["observation_unit"] == project["observation_unit"]
    for key in ("data_version", "dataset_path", "producing_script", "time_granularity"):
        assert contract[key] == expected_identity[key]
    assert contract["primary_key"]["columns"] == expected_identity["primary_key"]
    audit_path = ROOT / "skills/empirical-workflow/templates/merge-audit-template.yaml"
    assert audit_path.is_file()
    audit = yaml.safe_load(audit_path.read_text(encoding="utf-8"))
    assert contract["merge_audit"]["data_version"] == audit["data_version"]
    assert audit["output_dataset"]["path"] == contract["dataset_path"]
    assert audit["output_dataset"]["row_count"] == contract["row_count"]
    step = audit["merge_steps"][0]
    assert step["matched_left_row_count"] + step["unmatched_left_row_count"] == step["left_source"]["input_row_count"]
    assert step["left_match_rate"] == step["matched_left_row_count"] / step["left_source"]["input_row_count"]


def test_r_standards_start_after_python_etl():
    body = read("skills/empirical-workflow/references/r-standards.md")
    contract = read("skills/empirical-workflow/references/data-contract.md")
    assert "01_validate_contract.R" in body
    assert "02_construct.R" in body
    assert "01_ingest.R" not in body
    assert "02_clean.R" not in body
    assert "Python owns raw ingestion, cleaning, entity resolution, and merging." in body
    assert "`code/r/01_validate_contract.R` is the prerequisite" in contract
    assert "before `code/r/02_construct.R`" in contract


def test_smoke_covers_expected_identity_handoff_and_failed_identification():
    runner = read("tests/smoke/run_smoke.sh")
    verifier = read("tests/smoke/verify_panel.R")
    recovery = read("tests/smoke/recover_handoff.py")
    for expected in (
        "handoff-fixture/research.yaml",
        "recover_handoff.py",
        "failed-identification.yaml",
        "Failed identifying diagnostic: formal analysis blocked",
    ):
        assert expected in runner
    for identity in (
        "project_name",
        "data_version",
        "dataset_path",
        "producing_script",
        "observation_unit",
        "time_granularity",
        "primary_key",
    ):
        assert identity in verifier
    assert "READ_ORDER" in recovery
    assert "decision-log.md" in recovery


def test_readme_cross_runtime_quickstart():
    body = read("README.md")
    for phrase in (
        "Claude Code",
        "Codex",
        "RESEARCH_PROTOCOL.md",
        "research.yaml",
        "tests/smoke/run_smoke.sh",
    ):
        assert phrase in body
