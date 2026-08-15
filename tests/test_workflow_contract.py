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
