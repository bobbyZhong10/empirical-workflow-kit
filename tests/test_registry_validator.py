from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
import yaml

from tools.validate_registry import load_registry, main, validate_registry


REGISTRY_FILES = (
    "pipelines.yaml",
    "claims.yaml",
    "evidence_cards.yaml",
    "evidence_relations.yaml",
    "reported_figures.yaml",
    "outputs.yaml",
    "gates.yaml",
    "semantics.yaml",
    "derived_fields.yaml",
    "applicability.yaml",
)


def base_registry() -> dict:
    return {
        "pipelines": {
            "pipelines": [
                {
                    "pipeline_id": "p1",
                    "status": "current",
                    "first_formal_batch_at": "2026-01-01T00:00:00Z",
                }
            ]
        },
        "claims": {
            "claims": [
                {
                    "claim_key": "H1",
                    "claim_revision_id": "H1.r1",
                    "pipeline_id": "p1",
                    "availability": "current",
                    "assessment": "supported",
                }
            ]
        },
        "evidence_cards": {
            "evidence_cards": [
                {
                    "evidence_card_id": "EC-1",
                    "pipeline_id": "p1",
                    "provenance": "confirmatory",
                    "status": "current",
                    "depends_on": [{"kind": "raw_field", "id": "outcome"}],
                }
            ]
        },
        "evidence_relations": {
            "evidence_relations": [
                {
                    "relation_id": "ER-1",
                    "evidence_card_id": "EC-1",
                    "claim_revision_id": "H1.r1",
                    "relation": "supports",
                    "status": "current",
                    "author": "analyst",
                    "date": "2026-02-01",
                    "rationale": "Confirmatory estimate supports H1.",
                }
            ]
        },
        "reported_figures": {
            "reported_figures": [
                {
                    "figure_id": "RF-1",
                    "pipeline_id": "p1",
                    "value": 2.0,
                    "source_artifact": "results/p1.json",
                    "source_locator": "estimate",
                    "paper_locations": ["paper/results.md#estimate"],
                }
            ],
            "revalidations": [],
        },
        "outputs": {
            "outputs": [
                {
                    "output_id": "paper",
                    "kind": "submission",
                    "status": "current",
                    "pipeline_id": "p1",
                    "claim_revision_ids": ["H1.r1"],
                    "reported_figure_ids": ["RF-1"],
                }
            ]
        },
        "gates": {
            "gate_set_confirmation": {
                "checkpoint": "B",
                "complete": True,
                "signed_by": "authority",
                "signed_at": "2025-12-01T00:00:00Z",
            },
            "gate_definitions": [
                {
                    "gate_id": "G-1",
                    "applies_to": [{"kind": "claim_key", "id": "H1"}],
                    "metric": "diagnostic",
                    "allowed_band": "pass",
                    "failure_policy": "STOP",
                    "declared_at": "2025-12-01T00:00:00Z",
                    "declared_by": "authority",
                    "frozen": True,
                    "compensation": {
                        "action": "Investigate failure.",
                        "required_artifact": "evidence/gates/G-1.md",
                    },
                }
            ],
            "gate_evaluations": [
                {
                    "gate_id": "G-1",
                    "pipeline_id": "p1",
                    "evaluated_against": {"kind": "claim_key", "id": "H1"},
                    "status": "passed",
                    "coverage": {
                        "declared_scope": "all observations",
                        "evaluated_scope": "all observations",
                        "complete": True,
                    },
                    "evidence_card": "EC-1",
                }
            ],
        },
        "semantics": {
            "analysis_window": ["2024-01-01", "2024-12-31"],
            "used_fields": ["outcome"],
            "semantic_facts": [
                {
                    "fact_key": "SEM-outcome",
                    "fact_revision_id": "SEM-outcome.r1",
                    "field": "outcome",
                    "statement": "Observed outcome.",
                    "valid_range": ["2024-01-01", None],
                    "authority": {"status": "sourced", "source": "dictionary.md"},
                    "verification": {
                        "method": "source_review",
                        "result": "pass",
                        "performed_by": "analyst",
                        "performed_at": "2026-01-01T00:00:00Z",
                        "depends_on": [{"kind": "raw_field", "id": "outcome"}],
                    },
                }
            ],
            "semantic_equivalence_decisions": [],
        },
        "derived_fields": {"derived_fields": []},
        "applicability": {
            "applicability": [
                {"requirement_id": "REQ-core", "status": "completed"}
            ]
        },
    }


def write_registry(root: Path, registry: dict | None = None) -> Path:
    registry = copy.deepcopy(registry or base_registry())
    root.mkdir(parents=True, exist_ok=True)
    for filename in REGISTRY_FILES:
        key = filename.removesuffix(".yaml")
        (root / filename).write_text(
            yaml.safe_dump(registry[key], sort_keys=False), encoding="utf-8"
        )
    return root


def codes(report: dict, section: str) -> set[str]:
    return {item["code"] for item in report[section]}


def test_load_registry_reads_all_human_editable_yaml_files(tmp_path):
    loaded = load_registry(write_registry(tmp_path))
    assert set(loaded["_sources"]) == set(REGISTRY_FILES)
    assert loaded["pipelines"][0]["pipeline_id"] == "p1"
    assert loaded["analysis_window"] == ["2024-01-01", "2024-12-31"]


def test_validate_registry_accepts_a_registry_directory(tmp_path):
    report = validate_registry(write_registry(tmp_path), checkpoint="C")
    assert report["blocking"] == []
    assert "REGISTRY_VALID" in codes(report, "reports")


def test_missing_registry_file_is_a_stable_blocking_error(tmp_path):
    root = write_registry(tmp_path)
    (root / "claims.yaml").unlink()
    report = validate_registry(load_registry(root), checkpoint="B")
    assert "REGISTRY_FILE_MISSING" in codes(report, "blocking")


def test_missing_required_object_field_blocks_validation(tmp_path):
    registry = base_registry()
    del registry["claims"]["claims"][0]["claim_revision_id"]
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "MISSING_REQUIRED_FIELD" in codes(report, "blocking")


@pytest.mark.parametrize(
    ("valid_ranges", "expected_code"),
    [
        (
            [["2024-01-01", "2024-05-31"], ["2024-07-01", None]],
            "SEMANTIC_COVERAGE_GAP",
        ),
        (
            [["2024-01-01", "2024-07-01"], ["2024-06-01", None]],
            "SEMANTIC_COVERAGE_OVERLAP",
        ),
    ],
)
def test_semantic_intervals_require_exactly_one_revision_at_each_point(
    tmp_path, valid_ranges, expected_code
):
    registry = base_registry()
    first = registry["semantics"]["semantic_facts"][0]
    registry["semantics"]["semantic_facts"] = [
        {**copy.deepcopy(first), "fact_revision_id": f"SEM-outcome.r{i + 1}", "valid_range": interval}
        for i, interval in enumerate(valid_ranges)
    ]
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "B")
    assert expected_code in codes(report, "blocking")


def test_semantic_verification_cannot_depend_on_a_derived_field(tmp_path):
    registry = base_registry()
    registry["semantics"]["semantic_facts"][0]["verification"]["depends_on"] = [
        {"kind": "derived_field", "id": "margin"}
    ]
    registry["derived_fields"]["derived_fields"] = [
        {
            "derived_field_id": "margin",
            "fact_key": "SEM-outcome",
            "status": "verified",
            "depends_on": [{"kind": "semantic_fact", "id": "SEM-outcome"}],
        }
    ]
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "B")
    assert "SEMANTIC_BOTTOM_LAYER_VIOLATION" in codes(report, "blocking")


def test_reference_graph_must_be_acyclic(tmp_path):
    registry = base_registry()
    registry["derived_fields"]["derived_fields"] = [
        {
            "derived_field_id": "a",
            "fact_key": "SEM-outcome",
            "status": "verified",
            "depends_on": [{"kind": "derived_field", "id": "b"}],
        },
        {
            "derived_field_id": "b",
            "fact_key": "SEM-outcome",
            "status": "verified",
            "depends_on": [{"kind": "derived_field", "id": "a"}],
        },
    ]
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "B")
    assert "REFERENCE_CYCLE" in codes(report, "blocking")


def test_claim_revision_bindings_must_come_from_one_pipeline(tmp_path):
    registry = base_registry()
    registry["pipelines"]["pipelines"].append(
        {
            "pipeline_id": "p2",
            "status": "current",
            "first_formal_batch_at": "2026-03-01T00:00:00Z",
        }
    )
    registry["evidence_cards"]["evidence_cards"].append(
        {
            "evidence_card_id": "EC-2",
            "pipeline_id": "p2",
            "provenance": "confirmatory",
            "status": "current",
            "depends_on": [{"kind": "raw_field", "id": "outcome"}],
        }
    )
    registry["evidence_relations"]["evidence_relations"].append(
        {
            "relation_id": "ER-2",
            "evidence_card_id": "EC-2",
            "claim_revision_id": "H1.r1",
            "relation": "challenges",
            "status": "current",
            "author": "auditor",
            "date": "2026-03-02",
            "rationale": "Contradictory pipeline result.",
        }
    )
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "CROSS_PIPELINE_CLAIM_BINDING" in codes(report, "blocking")


def test_superseded_pipeline_derives_stale_and_blocks_export(tmp_path):
    registry = base_registry()
    registry["pipelines"]["pipelines"][0]["status"] = "superseded"
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "STALE_CLAIM" in codes(report, "derived")
    assert "STALE_REPORTED_FIGURE" in codes(report, "derived")
    assert "STALE_OUTPUT" in codes(report, "derived")
    assert "PUBLICATION_INELIGIBLE" in codes(report, "blocking")


def test_mixed_pipeline_output_is_rejected(tmp_path):
    registry = base_registry()
    registry["pipelines"]["pipelines"].append(
        {
            "pipeline_id": "p2",
            "status": "current",
            "first_formal_batch_at": "2026-03-01T00:00:00Z",
        }
    )
    registry["reported_figures"]["reported_figures"].append(
        {
            "figure_id": "RF-2",
            "pipeline_id": "p2",
            "value": 3.0,
            "source_artifact": "results/p2.json",
            "source_locator": "estimate",
            "paper_locations": ["paper/results.md#other"],
        }
    )
    registry["outputs"]["outputs"][0]["reported_figure_ids"].append("RF-2")
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "MIXED_PIPELINE_OUTPUT" in codes(report, "blocking")


def test_reconciliation_can_quote_stale_history_without_restoring_it(tmp_path):
    registry = base_registry()
    registry["pipelines"]["pipelines"][0]["status"] = "superseded"
    registry["pipelines"]["pipelines"].append(
        {
            "pipeline_id": "p2",
            "status": "current",
            "first_formal_batch_at": "2026-03-01T00:00:00Z",
        }
    )
    registry["claims"]["claims"].append(
        {
            "claim_key": "H1",
            "claim_revision_id": "H1.r2",
            "pipeline_id": "p2",
            "availability": "current",
            "assessment": "supported",
            "supersedes": "H1.r1",
            "revision_reason": "new pipeline",
        }
    )
    registry["evidence_cards"]["evidence_cards"].append(
        {
            "evidence_card_id": "EC-2",
            "pipeline_id": "p2",
            "provenance": "confirmatory",
            "status": "current",
            "depends_on": [{"kind": "raw_field", "id": "outcome"}],
        }
    )
    registry["evidence_relations"]["evidence_relations"].append(
        {
            "relation_id": "ER-2",
            "evidence_card_id": "EC-2",
            "claim_revision_id": "H1.r2",
            "relation": "supports",
            "status": "current",
            "author": "analyst",
            "date": "2026-03-02",
            "rationale": "Updated estimate supports H1.",
        }
    )
    registry["outputs"]["outputs"][0] = {
        "output_id": "reconciliation",
        "kind": "submission",
        "status": "current",
        "cross_pipeline": "reconciliation",
        "spanned_pipelines": ["p1", "p2"],
        "claim_revision_ids": ["H1.r2"],
        "historical_claim_revision_ids": ["H1.r1"],
        "reported_figure_ids": [],
    }
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "STALE_CLAIM" in codes(report, "derived")
    assert "STALE_OUTPUT" not in codes(report, "derived")
    assert "REVALIDATED_OUTPUT" not in codes(report, "derived")
    assert "PUBLICATION_INELIGIBLE" not in codes(report, "blocking")
    assert "MIXED_PIPELINE_OUTPUT" not in codes(report, "blocking")


def test_machine_revalidation_restores_pipeline_stale_but_keeps_assessment(tmp_path):
    registry = base_registry()
    registry["pipelines"]["pipelines"][0]["status"] = "superseded"
    registry["pipelines"]["pipelines"].append(
        {
            "pipeline_id": "p2",
            "status": "current",
            "first_formal_batch_at": "2026-03-01T00:00:00Z",
        }
    )
    registry["outputs"]["outputs"][0]["pipeline_id"] = "p2"
    registry["reported_figures"]["reported_figures"][0]["source_artifact"] = (
        "results/{pipeline_id}.yaml"
    )
    registry["reported_figures"]["revalidations"] = [
        {
            "target": {"kind": "claim_revision", "id": "H1.r1"},
            "from_pipeline": "p1",
            "to_pipeline": "p2",
            "method": "machine",
            "tolerance": "abs(delta) <= 0.01 and sign unchanged",
            "result": "revalidated",
            "performed_by": "validator",
            "performed_at": "2026-03-02T00:00:00Z",
            "evidence_card": "EC-1",
        },
        {
            "target": {"kind": "reported_figure", "id": "RF-1"},
            "from_pipeline": "p1",
            "to_pipeline": "p2",
            "method": "machine",
            "tolerance": "abs(delta) <= 0.01 and sign unchanged",
            "result": "revalidated",
            "performed_by": "validator",
            "performed_at": "2026-03-02T00:00:00Z",
            "evidence_card": "EC-1",
        },
    ]
    root = write_registry(tmp_path, registry)
    (root / "results").mkdir()
    (root / "results" / "p2.yaml").write_text("estimate: 2.005\n", encoding="utf-8")
    report = validate_registry(load_registry(root), "C")
    claim = report["state"]["claims"]["H1.r1"]
    figure = report["state"]["reported_figures"]["RF-1"]
    assert claim["availability"] == "current"
    assert claim["assessment"] == "supported"
    assert figure["pipeline_id"] == "p2"
    assert figure["value"] == pytest.approx(2.005)
    assert "REVALIDATED_CLAIM" in codes(report, "derived")
    assert "REVALIDATED_REPORTED_FIGURE" in codes(report, "derived")


def test_revalidated_upstream_recomputes_a_derived_reported_figure(tmp_path):
    registry = base_registry()
    registry["pipelines"]["pipelines"].append(
        {
            "pipeline_id": "p2",
            "status": "current",
            "first_formal_batch_at": "2026-03-01T00:00:00Z",
        }
    )
    registry["reported_figures"]["reported_figures"].append(
        {
            "figure_id": "RF-percent",
            "pipeline_id": "p1",
            "value": 200.0,
            "source_artifact": "computed",
            "source_locator": "RF-1",
            "paper_locations": ["paper/results.md#percent"],
            "derived_from": "RF-1",
            "transform": {"operation": "multiply", "operand": 100},
        }
    )
    registry["reported_figures"]["reported_figures"][0]["source_artifact"] = (
        "results/{pipeline_id}.yaml"
    )
    registry["reported_figures"]["revalidations"] = [
        {
            "target": {"kind": "reported_figure", "id": "RF-1"},
            "from_pipeline": "p1",
            "to_pipeline": "p2",
            "method": "machine",
            "tolerance": "abs(delta) <= 1 and sign unchanged",
            "result": "revalidated",
            "performed_by": "validator",
            "performed_at": "2026-03-02T00:00:00Z",
            "evidence_card": "EC-1",
        }
    ]
    root = write_registry(tmp_path, registry)
    (root / "results").mkdir()
    (root / "results" / "p2.yaml").write_text("estimate: 2.5\n", encoding="utf-8")
    report = validate_registry(load_registry(root), "C")
    derived = report["state"]["reported_figures"]["RF-percent"]
    assert derived["value"] == 250.0
    assert derived["pipeline_id"] == "p2"
    assert "RECOMPUTED_REPORTED_FIGURE" in codes(report, "derived")


def test_semantic_correction_stays_stale_after_machine_revalidation(tmp_path):
    registry = base_registry()
    fact = registry["semantics"]["semantic_facts"][0]
    fact.update({"supersedes": "SEM-outcome.r0", "revision_reason": "corrected"})
    registry["derived_fields"]["derived_fields"] = [
        {
            "derived_field_id": "outcome_scaled",
            "fact_key": "SEM-outcome",
            "status": "verified",
            "depends_on": [{"kind": "semantic_fact", "id": "SEM-outcome"}],
        }
    ]
    registry["evidence_cards"]["evidence_cards"][0]["depends_on"] = [
        {"kind": "derived_field", "id": "outcome_scaled"}
    ]
    registry["reported_figures"]["revalidations"] = [
        {
            "target": {"kind": "claim_revision", "id": "H1.r1"},
            "from_pipeline": "p1",
            "to_pipeline": "p1",
            "method": "machine",
            "tolerance": "abs(delta) <= 0.01 and sign unchanged",
            "result": "revalidated",
            "performed_by": "validator",
            "performed_at": "2026-03-02T00:00:00Z",
            "evidence_card": "EC-1",
        }
    ]
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert report["state"]["claims"]["H1.r1"]["availability"] == "stale"
    assert "SEMANTIC_STALE_CLAIM" in codes(report, "derived")
    assert "MACHINE_REVALIDATION_FORBIDDEN" in codes(report, "blocking")


def test_multi_revision_semantics_requires_disclosure_and_challenges_claim(tmp_path):
    registry = base_registry()
    first = registry["semantics"]["semantic_facts"][0]
    registry["semantics"]["semantic_facts"] = [
        {**copy.deepcopy(first), "valid_range": ["2024-01-01", "2024-06-30"]},
        {
            **copy.deepcopy(first),
            "fact_revision_id": "SEM-outcome.r2",
            "valid_range": ["2024-07-01", None],
        },
    ]
    registry["derived_fields"]["derived_fields"] = [
        {
            "derived_field_id": "outcome_scaled",
            "fact_key": "SEM-outcome",
            "status": "verified",
            "depends_on": [{"kind": "semantic_fact", "id": "SEM-outcome"}],
        }
    ]
    registry["evidence_cards"]["evidence_cards"][0]["depends_on"] = [
        {"kind": "derived_field", "id": "outcome_scaled"}
    ]
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "SEMANTIC_DISCLOSURE_REQUIRED" in codes(report, "reports")
    assert "SEMANTIC_CHANGE_CHALLENGE" in codes(report, "derived")
    assert report["state"]["claims"]["H1.r1"]["assessment"] == "challenged"


def test_withdrawing_every_supporting_relation_restores_unresolved(tmp_path):
    registry = base_registry()
    registry["evidence_relations"]["evidence_relations"][0]["status"] = "withdrawn"
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert report["state"]["claims"]["H1.r1"]["assessment"] == "unresolved"
    assert "ASSESSMENT_UNRESOLVED" in codes(report, "derived")
    assert "PUBLICATION_INELIGIBLE" in codes(report, "blocking")


def _gate_report(tmp_path: Path, status: str, **updates) -> dict:
    registry = base_registry()
    evaluation = registry["gates"]["gate_evaluations"][0]
    evaluation["status"] = status
    evaluation.update(updates)
    return validate_registry(load_registry(write_registry(tmp_path, registry)), "C")


@pytest.mark.parametrize(
    ("status", "updates", "expected"),
    [
        ("triggered", {}, "GATE_TRIGGERED"),
        ("not_evaluated", {}, "GATE_NOT_EVALUATED"),
        ("passed", {"coverage": {"complete": False}}, "GATE_COVERAGE_INCOMPLETE"),
        ("satisfied", {}, "GATE_SATISFIED_INCOMPLETE"),
        ("released", {"release": {"reason": "obsolete"}}, "GATE_RELEASE_INCOMPLETE"),
        ("inapplicable", {}, "GATE_INAPPLICABLE_INCOMPLETE"),
    ],
)
def test_checkpoint_c_blocks_each_incomplete_gate_closure(
    tmp_path, status, updates, expected
):
    report = _gate_report(tmp_path, status, **updates)
    assert expected in codes(report, "blocking")


@pytest.mark.parametrize(
    ("status", "updates", "report_code"),
    [
        (
            "satisfied",
            {
                "compensation_artifact": "evidence/gates/G-1.md",
                "accepted_by": "authority",
                "accepted_at": "2026-02-01T00:00:00Z",
            },
            None,
        ),
        (
            "released",
            {
                "release": {
                    "triggering_change_id": "D-1",
                    "reason": "measure retired",
                    "authorized_by": "authority",
                    "timing": "pre_result",
                    "evidence_card": "EC-1",
                    "compensation_disposition": "not required",
                }
            },
            "GATE_RELEASED",
        ),
        (
            "inapplicable",
            {
                "applicability_reason": "Not measured for this population.",
                "declared_by": "analyst",
                "accepted_by": "authority",
            },
            "GATE_INAPPLICABLE",
        ),
    ],
)
def test_complete_gate_closures_do_not_block(tmp_path, status, updates, report_code):
    report = _gate_report(tmp_path, status, **updates)
    assert not any(item["code"].startswith("GATE_") for item in report["blocking"])
    if report_code:
        assert report_code in codes(report, "reports")


def test_retired_and_withdrawn_claims_derive_moot_gate_evaluations(tmp_path):
    for availability in ("retired", "withdrawn"):
        registry = base_registry()
        registry["claims"]["claims"][0]["availability"] = availability
        registry["claims"]["claims"][0]["change_id"] = f"D-{availability}"
        registry["gates"]["gate_evaluations"][0]["status"] = "triggered"
        report = validate_registry(
            load_registry(write_registry(tmp_path / availability, registry)), "C"
        )
        assert "GATE_MOOT" in codes(report, "derived")
        assert "GATE_TRIGGERED" not in codes(report, "blocking")


def test_moot_gate_without_an_end_of_life_target_is_rejected(tmp_path):
    report = _gate_report(
        tmp_path, "moot", triggering_change_id="D-unrelated"
    )
    assert "GATE_MOOT_INVALID" in codes(report, "blocking")


def test_post_hoc_is_derived_per_pipeline_evaluation(tmp_path):
    registry = base_registry()
    registry["pipelines"]["pipelines"][0]["first_formal_batch_at"] = (
        "2026-01-01T00:00:00Z"
    )
    registry["pipelines"]["pipelines"].append(
        {
            "pipeline_id": "p2",
            "status": "current",
            "first_formal_batch_at": "2026-07-01T00:00:00Z",
        }
    )
    registry["gates"]["gate_definitions"][0]["declared_at"] = (
        "2026-04-01T00:00:00Z"
    )
    second = copy.deepcopy(registry["gates"]["gate_evaluations"][0])
    second["pipeline_id"] = "p2"
    registry["gates"]["gate_evaluations"].append(second)
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    post_hoc = {
        item["pipeline_id"]: item["post_hoc"]
        for item in report["reports"]
        if item["code"] == "GATE_POST_HOC"
    }
    assert post_hoc == {"p1": True, "p2": False}


def test_inapplicable_requirement_requires_completed_substitutes(tmp_path):
    registry = base_registry()
    registry["applicability"]["applicability"] = [
        {
            "requirement_id": "REQ-original",
            "status": "inapplicable",
            "applicability_reason": "No panel timing.",
            "declared_by": "analyst",
            "accepted_by": "authority",
            "substituted_by": ["REQ-substitute"],
        },
        {"requirement_id": "REQ-substitute", "status": "pending"},
    ]
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "APPLICABILITY_SUBSTITUTE_INCOMPLETE" in codes(report, "blocking")


def test_cli_emits_json_and_exit_status_matches_blocking(tmp_path, capsys):
    valid_root = write_registry(tmp_path / "valid")
    assert main([str(valid_root), "--checkpoint", "C", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert set(payload) >= {"checkpoint", "blocking", "reports", "derived"}
    assert "REGISTRY_VALID" in codes(payload, "reports")

    invalid = base_registry()
    invalid["pipelines"]["pipelines"][0]["status"] = "superseded"
    invalid_root = write_registry(tmp_path / "invalid", invalid)
    assert main([str(invalid_root), "--checkpoint", "C", "--format", "json"]) == 1
    assert "PUBLICATION_INELIGIBLE" in {
        item["code"] for item in json.loads(capsys.readouterr().out)["blocking"]
    }
