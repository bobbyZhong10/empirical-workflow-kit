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
        "allowed_designs": ["fixed_effects", "did", "event_study", "ddd", "iv", "rdd"],
        "autonomy_mode": "complete_with_red_lines",
        "current_stage": "stage_1_data_infrastructure",
        "primary_data_format": "parquet",
        "conversation_language": "Chinese",
        "artifact_language": "English",
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
