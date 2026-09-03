from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
METHOD_ROOT = ROOT / "skills" / "empirical-workflow" / "methods"
METHODS = [
    "causal-design",
    "conjoint",
    "did",
    "field-experiment",
    "fixed-effects",
    "iv",
    "rdd",
    "selection-on-observables",
    "synthetic-control",
]


def frontmatter(path):
    body = path.read_text(encoding="utf-8")
    _, raw, _ = body.split("---", 2)
    return yaml.safe_load(raw), body


def test_every_method_has_a_machine_readable_freshness_manifest():
    assert sorted(path.name for path in METHOD_ROOT.iterdir() if path.is_dir()) == METHODS
    for method in METHODS:
        path = METHOD_ROOT / method / "method.manifest.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data["schema_version"] == 1
        assert data["method"] == method
        assert str(data["reviewed_at"]).startswith("2026-")
        assert data["refresh"]["max_age_days"] > 0
        assert data["refresh"]["query"]
        assert data["refresh"]["approval_required"] is True
        assert data["software"]["language"] == "R"
        for source in data["sources"].values():
            assert (path.parent / source).is_file(), (method, source)


def test_method_facades_are_discoverable_and_route_to_one_canonical_prompt():
    contract = ROOT / "skills" / "empirical-workflow" / "references" / "method-facade-contract.md"
    assert contract.is_file()
    for method in METHODS:
        metadata, body = frontmatter(ROOT / "skills" / method / "SKILL.md")
        assert metadata["name"] == method
        assert metadata["description"]
        assert "method-facade-contract.md" in body
        canonical = f"../empirical-workflow/methods/{method}/prompt.md"
        assert canonical in body
        assert len(body.splitlines()) < 25


def test_facade_contract_preserves_stage_and_pause_gates():
    body = " ".join((
        ROOT / "skills" / "empirical-workflow" / "references" / "method-facade-contract.md"
    ).read_text(encoding="utf-8").split())
    for phrase in (
        "stage6a-reduced-form.md",
        "Mandatory pause",
        "must not run a focal analysis",
        "Failed identifying diagnostics",
        "Never copy a method prompt",
    ):
        assert phrase in body
