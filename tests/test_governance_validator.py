import json
import subprocess
from copy import deepcopy
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "skills/empirical-workflow/scripts/validate_governance.py"


def base_registry():
    return {
        "registry_version": "1.0",
        "project_name": "governed_example",
        "pipelines": [
            {
                "pipeline_id": "p01",
                "status": "authoritative",
                "first_formal_batch_at": "2026-06-01T00:00:00Z",
            }
        ],
        "claims": [
            {
                "claim_key": "H1_effect",
                "claim_revision_id": "H1_effect.r1",
                "availability": "current",
                "assessment": "supported",
                "pipeline_id": "p01",
                "supporting_evidence": ["E-001"],
                "adjacent_disclosures": [],
            }
        ],
        "reported_figures": [
            {
                "figure_id": "F-001",
                "pipeline_id": "p01",
                "source_artifact": "results/estimates.json",
                "source_locator": "H1.main",
                "value": 0.12,
            }
        ],
        "gate_definitions": [
            {
                "gate_id": "G-001",
                "declared_at": "2026-05-01T00:00:00Z",
                "failure_policy": "STOP",
            }
        ],
        "gate_evaluations": [
            {
                "gate_id": "G-001",
                "pipeline_id": "p01",
                "status": "passed",
                "coverage": {"complete": True},
            }
        ],
        "applicability_records": [
            {"requirement_id": "A-001", "status": "completed"}
        ],
        "outputs": [
            {
                "output_id": "paper",
                "pipeline_ids": ["p01"],
                "claim_revisions": ["H1_effect.r1"],
                "reported_figures": ["F-001"],
            }
        ],
        "publication": {"output_id": "paper"},
    }


def run_validator(tmp_path, registry):
    path = tmp_path / "registry.yaml"
    path.write_text(yaml.safe_dump(registry, sort_keys=False), encoding="utf-8")
    result = subprocess.run(
        [str(ROOT / ".venv/bin/python"), str(VALIDATOR), str(path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result, json.loads(result.stdout)


def test_valid_registry_is_publication_eligible(tmp_path):
    result, report = run_validator(tmp_path, base_registry())
    assert result.returncode == 0
    assert report["eligible"] is True
    assert report["errors"] == []
    assert report["derived"]["post_hoc"]["G-001@p01"] is False


def test_mixed_pipeline_output_is_rejected(tmp_path):
    registry = base_registry()
    registry["pipelines"].append(
        {
            "pipeline_id": "p02",
            "status": "superseded",
            "first_formal_batch_at": "2026-04-01T00:00:00Z",
        }
    )
    registry["outputs"][0]["pipeline_ids"] = ["p01", "p02"]
    result, report = run_validator(tmp_path, registry)
    assert result.returncode == 1
    assert any("mixes pipelines" in error for error in report["errors"])


def test_declared_reconciliation_accepts_historical_stale_claim(tmp_path):
    registry = base_registry()
    registry["pipelines"].append(
        {
            "pipeline_id": "p00",
            "status": "superseded",
            "first_formal_batch_at": "2026-03-01T00:00:00Z",
        }
    )
    registry["claims"].append(
        {
            "claim_key": "H1_effect",
            "claim_revision_id": "H1_effect.r0",
            "availability": "stale",
            "assessment": "supported",
            "pipeline_id": "p00",
            "supporting_evidence": ["E-000"],
            "adjacent_disclosures": [],
        }
    )
    registry["outputs"][0].update(
        {
            "pipeline_ids": ["p00", "p01"],
            "claim_revisions": ["H1_effect.r0", "H1_effect.r1"],
            "cross_pipeline": "reconciliation",
            "reconciliation": {
                "pipelines": ["p00", "p01"],
                "historical_claim_revisions": ["H1_effect.r0"],
            },
        }
    )
    result, report = run_validator(tmp_path, registry)
    assert result.returncode == 0
    assert report["eligible"] is True
    assert report["derived"]["claim_availability"]["H1_effect.r0"] == "stale"


def test_post_hoc_is_derived_per_pipeline(tmp_path):
    registry = base_registry()
    registry["pipelines"].append(
        {
            "pipeline_id": "p02",
            "status": "superseded",
            "first_formal_batch_at": "2026-04-01T00:00:00Z",
        }
    )
    registry["gate_evaluations"].append(
        {
            "gate_id": "G-001",
            "pipeline_id": "p02",
            "status": "passed",
            "coverage": {"complete": True},
        }
    )
    result, report = run_validator(tmp_path, registry)
    assert result.returncode == 0
    assert report["derived"]["post_hoc"] == {
        "G-001@p01": False,
        "G-001@p02": True,
    }


def test_triggered_gate_and_incomplete_substitute_block_publication(tmp_path):
    registry = base_registry()
    registry["gate_evaluations"][0]["status"] = "triggered"
    registry["applicability_records"] = [
        {
            "requirement_id": "A-001",
            "status": "inapplicable",
            "reason": "No merge occurs in this project.",
            "declared_by": "research_author",
            "accepted_by": "decision_authority",
            "substituted_by": ["A-002"],
        },
        {"requirement_id": "A-002", "status": "pending"},
    ]
    result, report = run_validator(tmp_path, registry)
    assert result.returncode == 1
    assert any("unresolved gate" in error for error in report["errors"])
    assert any("substitute A-002 is not completed" in error for error in report["errors"])


def test_inapplicable_gate_requires_authored_justification(tmp_path):
    registry = deepcopy(base_registry())
    registry["gate_evaluations"][0]["status"] = "inapplicable"
    result, report = run_validator(tmp_path, registry)
    assert result.returncode == 1
    assert any("inapplicable gate" in error for error in report["errors"])
