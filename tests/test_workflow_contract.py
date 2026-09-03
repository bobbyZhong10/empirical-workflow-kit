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


def test_example_config_values():
    config = yaml.safe_load(read("research.example.yaml"))
    assert config == {
        "project_name": "example_platform_adoption",
        "target_outlets": ["Management Science", "ISR", "MISQ"],
        "reference_pools": ["UTD24", "FT50", "TopEcon", "JAIS", "IJRM"],
        "research_domain": "platform_and_firm_panel_causal",
        "observation_unit": "firm_quarter",
        "analysis_languages": {"etl": "python", "estimation": "r"},
        "allowed_designs": [
            "fixed_effects",
            "selection_on_observables",
            "did",
            "event_study",
            "ddd",
            "iv",
            "rdd",
            "synthetic_control",
            "field_experiment",
            "conjoint",
        ],
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


def test_absorbed_global_instructions_are_portably_routed():
    required = (
        "skills/empirical-workflow/references/research-writing.md",
        "skills/empirical-workflow/references/execution-discipline.md",
        "skills/empirical-workflow/references/method-governance.md",
        "skills/empirical-workflow/references/code-review.md",
        "skills/empirical-workflow/templates/handoff-template.md",
        "runtime-profile.example.yaml",
        "THIRD_PARTY_NOTICES.md",
    )
    for path in required:
        assert (ROOT / path).is_file(), path

    protocol = read("RESEARCH_PROTOCOL.md")
    router = read("skills/empirical-workflow/SKILL.md")
    for phrase in (
        "Research judgment and verification",
        "Research writing and source use",
        "Publication, confidentiality, and release",
    ):
        assert phrase in protocol
    for path in required[:4]:
        assert path.removeprefix("skills/empirical-workflow/") in router

    profile = yaml.safe_load(read("runtime-profile.example.yaml"))
    assert profile["runtime_profile"]["scholarly_sources"]["cache_dir"]
    assert profile["runtime_profile"]["presentation"]["assets_path"]
    assert profile["runtime_profile"]["browser"]["public_profile"]
    for name in (
        "EWF_CACHE_DIR",
        "EWF_STATE_DIR",
        "EWF_PDF_HELPER",
        "EWF_PRESENTATION_ASSETS",
        "EWF_COURSE_ROOT",
    ):
        assert name in profile["runtime_profile"]["environment_bindings"]

    for adapter in ("CLAUDE.md", "AGENTS.md"):
        body = read(adapter)
        assert len(body.splitlines()) < 140
        assert "runtime-profile" in body


def test_claim_governance_and_preregistration_are_routed():
    required = (
        "skills/empirical-workflow/templates/governance-registry-template.yaml",
        "skills/empirical-workflow/templates/preregistration-template.yaml",
        "skills/empirical-workflow/scripts/validate_governance.py",
        "skills/preregister/SKILL.md",
    )
    for path in required:
        assert (ROOT / path).is_file(), path

    stage3 = read("skills/empirical-workflow/stages/stage3-theory-hypotheses.md")
    stage5 = read("skills/empirical-workflow/stages/stage5-measurement.md")
    prereg = read("skills/preregister/SKILL.md")
    assert "preregistration-template.yaml" in stage3
    assert "acceptance-gate" in stage5.lower()
    for phrase in (
        "focal outcome",
        "focal analysis",
        "refuse",
        "falsification",
        "retrospective",
    ):
        assert phrase in prereg.lower()

    registry = yaml.safe_load(read(required[0]))
    prereg_template = yaml.safe_load(read(required[1]))
    assert registry["registry_version"]
    assert prereg_template["preregistration"]["outcome_seen"] is False
    assert prereg_template["preregistration"]["focal_analysis_run"] is False


def test_research_source_skills_are_routed_and_honest_about_coverage():
    required = (
        "skills/research-sources/SKILL.md",
        "skills/research-sources/REFERENCE.md",
        "skills/research-sources/scripts/paper.py",
        "skills/literature-review/SKILL.md",
        "skills/bibliography-audit/SKILL.md",
    )
    for path in required:
        assert (ROOT / path).is_file(), path

    source_skill = read(required[0]).lower()
    literature_skill = read(required[3]).lower()
    bibliography_skill = read(required[4]).lower()
    stage2 = read("skills/empirical-workflow/stages/stage2-lit-map.md")
    stage7 = read("skills/empirical-workflow/stages/stage7-writing.md")

    for phrase in ("version_read", "source_rung", "abstract only", "coverage"):
        assert phrase in source_skill
    assert "source coverage" in literature_skill
    assert "never overwrites" in bibliography_skill
    assert "metadata" in bibliography_skill and "claim support" in bibliography_skill
    assert "literature-review" in stage2 and "bibliography-audit" in stage2
    assert "bibliography-audit" in stage7

    portable_files = required + (
        "skills/empirical-workflow/stages/stage2-lit-map.md",
        "skills/empirical-workflow/stages/stage7-writing.md",
    )
    for path in portable_files:
        assert "~/.claude" not in read(path)


def test_method_specific_causal_packs_are_selectively_routed():
    methods_root = ROOT / "skills/empirical-workflow/methods"
    expected = (
        "causal-design",
        "fixed-effects",
        "selection-on-observables",
        "did",
        "iv",
        "rdd",
        "synthetic-control",
        "field-experiment",
        "conjoint",
    )
    for method in expected:
        pack = methods_root / method
        for name in ("prompt.md", "canon.md", "details.md", "template.R"):
            assert (pack / name).is_file(), f"{method} lacks {name}"
        prompt = (pack / "prompt.md").read_text(encoding="utf-8")
        canon = (pack / "canon.md").read_text(encoding="utf-8")
        assert "8958cc246e65cdf7c36604f397a1c1719b7e2c14" in prompt
        for phrase in (
            "Current as of",
            "Verified through",
            "Role:",
            "Settles:",
            "Binds when:",
            "Implement:",
            "Scope limits:",
            "Named disagreements:",
            "Excluded:",
        ):
            assert phrase in canon, f"{method} canon lacks {phrase}"

    config = yaml.safe_load(read("research.example.yaml"))
    for design in (
        "selection_on_observables",
        "synthetic_control",
        "field_experiment",
        "conjoint",
    ):
        assert design in config["allowed_designs"]

    stage = read("skills/empirical-workflow/stages/stage6a-reduced-form.md")
    tree = read("skills/empirical-workflow/references/identification-decision-tree.md")
    assert "methods/<selected-method>/prompt.md" in stage
    assert "Load only the selected method pack" in stage
    for method in expected:
        assert f"methods/{method}/prompt.md" in tree


def test_review_response_and_replication_release_are_governed():
    skills = (
        "skills/research-council/SKILL.md",
        "skills/manuscript-review/SKILL.md",
        "skills/referee-response/SKILL.md",
        "skills/replication-release/SKILL.md",
    )
    templates = (
        "skills/empirical-workflow/templates/review-finding-template.yaml",
        "skills/empirical-workflow/templates/response-matrix-template.yaml",
        "skills/empirical-workflow/templates/replication-checklist-template.md",
    )
    scanners = tuple(
        f"skills/replication-release/scripts/{name}.py"
        for name in ("scan_headers", "scan_values", "scan_qsf", "sample_open_text")
    )
    for path in skills + templates + scanners:
        assert (ROOT / path).is_file(), path

    council = read(skills[0]).lower()
    response = read(skills[2]).lower()
    release = read(skills[3]).lower()
    stage7 = read("skills/empirical-workflow/stages/stage7-writing.md")
    assert "never by vote count" in council
    assert "verify every pin" in response
    assert "confidential" in release
    assert "policy" in release and "current" in release
    assert "staging" in release and "never" in release and "source" in release
    for name in ("research-council", "manuscript-review", "referee-response", "replication-release"):
        assert name in stage7

    finding = yaml.safe_load(read(templates[0]))
    response_matrix = yaml.safe_load(read(templates[1]))
    assert finding["finding"]["severity"]
    assert response_matrix["comments"][0]["pin_verification"]["verified"] is False


def test_latex_and_presentation_production_are_portable():
    skill_roots = (
        "skills/latex-production",
        "skills/research-talk",
        "skills/teaching-lecture",
        "skills/slide-review",
        "skills/course-site",
    )
    for root in skill_roots:
        body = read(f"{root}/SKILL.md")
        assert "8958cc246e65cdf7c36604f397a1c1719b7e2c14" in body
        assert "runtime-profile.yaml" in body
    required = (
        "agents/tikz-reviewer.md",
        "presentation-tooling/README.md",
        "presentation-tooling/_extensions/starter/_extension.yml",
        "presentation-tooling/_extensions/starter/stage-slide.lua",
        "presentation-tooling/_extensions/starter/starter-theme.scss",
        "presentation-tooling/deck-check.mjs",
        "presentation-tooling/stage-check.mjs",
        "presentation-tooling/check-offline.py",
        "skills/slide-review/scripts/probe.js",
        "skills/slide-review/scripts/figure-ground.js",
    )
    for path in required:
        assert (ROOT / path).is_file(), path

    text_suffixes = {".md", ".py", ".js", ".mjs", ".lua", ".qmd", ".scss", ".yml"}
    roots = [ROOT / path for path in skill_roots] + [ROOT / "presentation-tooling", ROOT / "agents"]
    for root in roots:
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in text_suffixes:
                body = path.read_text(encoding="utf-8", errors="replace")
                assert "~/.claude" not in body, path
                assert "/Users/" not in body, path


def test_documentation_maps_full_absorbed_workflow():
    bodies = [read("README.md"), read("docs/v2-migration-guide.md")]
    combined = "\n".join(bodies)
    for name in (
        "research-sources",
        "literature-review",
        "bibliography-audit",
        "preregister",
        "research-council",
        "manuscript-review",
        "referee-response",
        "replication-release",
        "latex-production",
        "research-talk",
        "teaching-lecture",
        "slide-review",
        "course-site",
    ):
        assert name in combined
    for phrase in (
        "runtime-profile.yaml",
        "THIRD_PARTY_NOTICES.md",
        "governance registry",
        "method pack",
        "policy verification",
        "confidentiality",
    ):
        assert phrase in combined
    assert "research-sources → literature-review → preregister" in combined
    assert "manuscript-review → referee-response → replication-release" in combined
