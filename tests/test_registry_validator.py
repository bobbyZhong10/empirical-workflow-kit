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
                    "comparison_endpoint": {
                        "artifact": "comparison/p1.yaml",
                        "locator": "estimate",
                    },
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
    comparison = root / "comparison"
    comparison.mkdir(exist_ok=True)
    (comparison / "p1.yaml").write_text("estimate: 2.0\n", encoding="utf-8")
    (comparison / "p2.yaml").write_text("estimate: 2.005\n", encoding="utf-8")
    return root


def codes(report: dict, section: str) -> set[str]:
    return {item["code"] for item in report[section]}


def report_codes(report: dict) -> set[str]:
    return {
        item["code"]
        for section in ("blocking", "reports", "derived")
        for item in report[section]
    }


def assertion_site(
    anchor: str,
    *,
    section_role: str = "results",
    assertion_type: str = "world",
    declared_tier: str | None = "T0",
    qualifier_scope: str = "sentence",
    counterevidence_prominence: str | None = None,
    significant_at: float | None = 0.05,
    has_sampling_distribution: bool | None = True,
    n: int | None = 1000,
    estimate_id: str | None = "EC-1#estimate",
    **conditional,
) -> dict:
    return {
        "path": "paper/assertions.md",
        "anchor": anchor,
        "section_role": section_role,
        "assertion_type": assertion_type,
        "declared_tier": declared_tier,
        "qualifier_scope": qualifier_scope,
        "counterevidence_prominence": counterevidence_prominence,
        "underlying_precision": {
            "estimate_id": estimate_id,
            "significant_at": significant_at,
            "has_sampling_distribution": has_sampling_distribution,
            "n": n,
        },
        "scope_declaration": None,
        "power_basis": None,
        "upgrade_justification": None,
        "alternative_explanation": None,
        "as_modeled": None,
        **conditional,
    }


def write_assertion_registry(
    root: Path, sites: list[dict], source: str, registry: dict | None = None
) -> dict:
    registry = copy.deepcopy(registry or base_registry())
    registry["claims"]["claims"][0]["assertion_sites"] = sites
    registry_root = write_registry(root, registry)
    paper = registry_root / "paper"
    paper.mkdir(exist_ok=True)
    (paper / "assertions.md").write_text(source, encoding="utf-8")
    return validate_registry(load_registry(registry_root), checkpoint="C")


def add_destination_evidence(registry: dict, claim_id: str = "H1.r1") -> None:
    registry["evidence_cards"]["evidence_cards"].append(
        {
            "evidence_card_id": "EC-2",
            "pipeline_id": "p2",
            "provenance": "confirmatory",
            "status": "current",
            "depends_on": [{"kind": "raw_field", "id": "outcome"}],
            "comparison_endpoint": {
                "artifact": "comparison/p2.yaml",
                "locator": "estimate",
            },
            "machine_comparison": {
                "source_evidence_card": "EC-1",
                "destination_evidence_card": "EC-2",
            },
        }
    )
    for relation in registry["evidence_relations"]["evidence_relations"]:
        if relation["claim_revision_id"] == claim_id:
            relation["status"] = "withdrawn"
    registry["evidence_relations"]["evidence_relations"].append(
        {
            "relation_id": "ER-2",
            "evidence_card_id": "EC-2",
            "claim_revision_id": claim_id,
            "relation": "supports",
            "status": "current",
            "author": "analyst",
            "date": "2026-03-02",
            "rationale": "Destination-pipeline comparison supports revalidation.",
        }
    )


def add_destination_gate_evaluation(
    registry: dict, *, status: str = "passed"
) -> None:
    second_evaluation = copy.deepcopy(registry["gates"]["gate_evaluations"][0])
    second_evaluation.update(
        {"pipeline_id": "p2", "evidence_card": "EC-2", "status": status}
    )
    registry["gates"]["gate_evaluations"].append(second_evaluation)


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


@pytest.mark.parametrize(
    "mutate",
    [
        lambda registry: registry["semantics"]["semantic_facts"].append("not-a-record"),
        lambda registry: registry["semantics"]["semantic_facts"][0].__setitem__(
            "verification", "not-a-mapping"
        ),
        lambda registry: registry["semantics"]["semantic_facts"][0][
            "verification"
        ].__setitem__("depends_on", "not-a-list"),
        lambda registry: registry["gates"]["gate_definitions"][0].__setitem__(
            "applies_to", ["not-a-target"]
        ),
        lambda registry: registry["gates"]["gate_evaluations"][0].__setitem__(
            "coverage", "not-a-mapping"
        ),
    ],
    ids=[
        "object",
        "verification",
        "dependencies",
        "gate-target",
        "coverage",
    ],
)
def test_malformed_nested_yaml_returns_blocking_json(tmp_path, capsys, mutate):
    registry = base_registry()
    mutate(registry)
    root = write_registry(tmp_path, registry)
    assert main([str(root), "--checkpoint", "C", "--format", "json"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert "SCHEMA_INVALID" in codes(payload, "blocking")


def test_syntactically_malformed_yaml_returns_blocking_json(tmp_path, capsys):
    root = write_registry(tmp_path)
    (root / "claims.yaml").write_text("claims: [unterminated\n", encoding="utf-8")
    assert main([str(root), "--checkpoint", "C", "--format", "json"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert "REGISTRY_YAML_INVALID" in codes(payload, "blocking")


@pytest.mark.parametrize(
    "mutate",
    [
        lambda registry: registry["pipelines"]["pipelines"][0].__setitem__(
            "pipeline_id", 1
        ),
        lambda registry: registry["evidence_relations"]["evidence_relations"][0].__setitem__(
            "author", {"name": "analyst"}
        ),
        lambda registry: registry["gates"]["gate_set_confirmation"].__setitem__(
            "signed_at", "not-a-time"
        ),
        lambda registry: registry["gates"]["gate_evaluations"][0][
            "coverage"
        ].__setitem__("complete", "yes"),
        lambda registry: registry["evidence_relations"]["evidence_relations"][0].__setitem__(
            "disclosure",
            {"adjacent": "yes", "paper_location": "paper/results.md#challenge"},
        ),
    ],
    ids=[
        "numeric-identity",
        "structured-author",
        "invalid-gate-signature-time",
        "nonboolean-coverage",
        "nonboolean-disclosure-adjacency",
    ],
)
def test_identity_and_nested_scalar_types_are_executable_schema(tmp_path, mutate):
    registry = base_registry()
    mutate(registry)
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "SCHEMA_INVALID" in codes(report, "blocking")


@pytest.mark.parametrize(
    ("mutate", "expected_code"),
    [
        (
            lambda registry: registry["pipelines"]["pipelines"].append(
                copy.deepcopy(registry["pipelines"]["pipelines"][0])
            ),
            "DUPLICATE_ID",
        ),
        (
            lambda registry: registry["evidence_relations"]["evidence_relations"][0].__setitem__(
                "evidence_card_id", "UNKNOWN"
            ),
            "UNKNOWN_REFERENCE",
        ),
        (
            lambda registry: registry["evidence_relations"]["evidence_relations"][0].__setitem__(
                "claim_revision_id", "UNKNOWN"
            ),
            "UNKNOWN_REFERENCE",
        ),
        (
            lambda registry: registry["claims"]["claims"][0].update(
                {"supersedes": "UNKNOWN", "revision_reason": "replacement"}
            ),
            "UNKNOWN_REFERENCE",
        ),
        (
            lambda registry: registry["reported_figures"]["reported_figures"][0].update(
                {
                    "derived_from": "UNKNOWN",
                    "transform": {"operation": "multiply", "operand": 2},
                }
            ),
            "UNKNOWN_REFERENCE",
        ),
        (
            lambda registry: registry["outputs"]["outputs"][0][
                "claim_revision_ids"
            ].append("UNKNOWN"),
            "UNKNOWN_REFERENCE",
        ),
        (
            lambda registry: registry["outputs"]["outputs"][0].update(
                {"historical_claim_revision_ids": ["UNKNOWN"]}
            ),
            "HISTORICAL_REFERENCE_FORBIDDEN",
        ),
        (
            lambda registry: registry["derived_fields"]["derived_fields"].append(
                {
                    "derived_field_id": "bad",
                    "fact_key": "SEM-outcome",
                    "status": "verified",
                    "depends_on": [{"kind": "derived_field", "id": "UNKNOWN"}],
                }
            ),
            "UNKNOWN_REFERENCE",
        ),
    ],
    ids=[
        "duplicate-pipeline",
        "relation-card",
        "relation-claim",
        "supersedes",
        "derived-figure",
        "output-active",
        "historical-outside-reconciliation",
        "derived-dependency",
    ],
)
def test_duplicate_and_dangling_references_block(tmp_path, mutate, expected_code):
    registry = base_registry()
    mutate(registry)
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert expected_code in codes(report, "blocking")


def test_unknown_historical_reconciliation_member_blocks(tmp_path):
    registry = base_registry()
    output = registry["outputs"]["outputs"][0]
    output.pop("pipeline_id")
    output.update(
        {
            "cross_pipeline": "reconciliation",
            "spanned_pipelines": ["p1"],
            "historical_claim_revision_ids": ["UNKNOWN"],
        }
    )
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "UNKNOWN_REFERENCE" in codes(report, "blocking")


def test_defective_field_challenge_propagates_through_derived_chain(tmp_path):
    registry = base_registry()
    registry["derived_fields"]["derived_fields"] = [
        {
            "derived_field_id": "a",
            "fact_key": "SEM-outcome",
            "status": "defective",
            "known_defects": ["Known unit conversion defect."],
            "depends_on": [{"kind": "semantic_fact", "id": "SEM-outcome"}],
        },
        {
            "derived_field_id": "b",
            "fact_key": "SEM-outcome",
            "status": "verified",
            "depends_on": [{"kind": "derived_field", "id": "a"}],
        },
    ]
    registry["evidence_cards"]["evidence_cards"][0]["depends_on"] = [
        {"kind": "derived_field", "id": "b"}
    ]
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    claim = report["state"]["claims"]["H1.r1"]
    assert claim["assessment"] == "challenged"
    assert "defective:a" in claim["_live_challenge_ids"]


def test_semantic_disclosure_challenge_propagates_through_three_hops(tmp_path):
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
            "derived_field_id": "a",
            "fact_key": "SEM-outcome",
            "status": "verified",
            "depends_on": [{"kind": "semantic_fact", "id": "SEM-outcome"}],
        },
        {
            "derived_field_id": "b",
            "fact_key": "SEM-outcome",
            "status": "verified",
            "depends_on": [{"kind": "derived_field", "id": "a"}],
        },
    ]
    registry["evidence_cards"]["evidence_cards"][0]["depends_on"] = [
        {"kind": "derived_field", "id": "b"}
    ]
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    claim = report["state"]["claims"]["H1.r1"]
    assert claim["assessment"] == "challenged"
    assert "semantic-change:SEM-outcome" in claim["_live_challenge_ids"]


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
    add_destination_gate_evaluation(registry)
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
    add_destination_gate_evaluation(registry)
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
    add_destination_evidence(registry)
    add_destination_gate_evaluation(registry)
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
            "comparison": {"from_value": 2.0, "to_value": 2.005},
            "result": "revalidated",
            "performed_by": "validator",
            "performed_at": "2026-03-02T00:00:00Z",
            "evidence_card": "EC-2",
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
            "evidence_card": "EC-2",
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
    assert "CROSS_PIPELINE_CLAIM_BINDING" not in codes(report, "blocking")


@pytest.mark.parametrize(
    ("mutation", "expected_code"),
    [
        ({"from_pipeline": "WRONG"}, "REVALIDATION_SOURCE_MISMATCH"),
        ({"to_pipeline": "MISSING"}, "REVALIDATION_PIPELINE_INVALID"),
        ({"performed_at": "not-a-date"}, "REVALIDATION_TIMESTAMP_INVALID"),
        ({"evidence_card": "MISSING"}, "REVALIDATION_EVIDENCE_INVALID"),
        ({"result": "bogus"}, "REVALIDATION_RESULT_INVALID"),
        (
            {"tolerance": "abs(delta) <= 0.001 and sign unchanged"},
            "REVALIDATION_RESULT_MISMATCH",
        ),
    ],
)
def test_invalid_claim_revalidation_cannot_improve_state(
    tmp_path, mutation, expected_code
):
    registry = base_registry()
    registry["pipelines"]["pipelines"][0]["status"] = "superseded"
    registry["pipelines"]["pipelines"].append(
        {
            "pipeline_id": "p2",
            "status": "current",
            "first_formal_batch_at": "2026-03-01T00:00:00Z",
        }
    )
    add_destination_evidence(registry)
    record = {
        "target": {"kind": "claim_revision", "id": "H1.r1"},
        "from_pipeline": "p1",
        "to_pipeline": "p2",
        "method": "machine",
        "tolerance": "abs(delta) <= 0.01 and sign unchanged",
        "comparison": {"from_value": 2.0, "to_value": 2.005},
        "result": "revalidated",
        "performed_by": "validator",
        "performed_at": "2026-03-02T00:00:00Z",
        "evidence_card": "EC-2",
    }
    record.update(mutation)
    registry["reported_figures"]["revalidations"] = [record]
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert expected_code in codes(report, "blocking")
    assert report["state"]["claims"]["H1.r1"]["availability"] == "stale"
    assert report["state"]["claims"]["H1.r1"]["pipeline_id"] == "p1"


def test_claim_revalidation_requires_destination_live_binding(tmp_path):
    registry = base_registry()
    registry["pipelines"]["pipelines"][0]["status"] = "superseded"
    registry["pipelines"]["pipelines"].append(
        {
            "pipeline_id": "p2",
            "status": "current",
            "first_formal_batch_at": "2026-03-01T00:00:00Z",
        }
    )
    registry["reported_figures"]["revalidations"] = [
        {
            "target": {"kind": "claim_revision", "id": "H1.r1"},
            "from_pipeline": "p1",
            "to_pipeline": "p2",
            "method": "machine",
            "tolerance": "abs(delta) <= 0.01 and sign unchanged",
            "comparison": {"from_value": 2.0, "to_value": 2.005},
            "result": "revalidated",
            "performed_by": "validator",
            "performed_at": "2026-03-02T00:00:00Z",
            "evidence_card": "EC-1",
        }
    ]
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "REVALIDATION_EVIDENCE_INVALID" in codes(report, "blocking")
    assert report["state"]["claims"]["H1.r1"]["availability"] == "stale"


def test_current_claim_cannot_be_moved_by_unneeded_revalidation(tmp_path):
    registry = base_registry()
    registry["pipelines"]["pipelines"].append(
        {
            "pipeline_id": "p2",
            "status": "current",
            "first_formal_batch_at": "2026-03-01T00:00:00Z",
        }
    )
    add_destination_evidence(registry)
    add_destination_gate_evaluation(registry)
    registry["reported_figures"]["revalidations"] = [
        {
            "target": {"kind": "claim_revision", "id": "H1.r1"},
            "from_pipeline": "p1",
            "to_pipeline": "p2",
            "method": "machine",
            "tolerance": "abs(delta) <= 0.01 and sign unchanged",
            "comparison": {"from_value": 2.0, "to_value": 2.005},
            "result": "revalidated",
            "performed_by": "validator",
            "performed_at": "2026-03-02T00:00:00Z",
            "evidence_card": "EC-2",
        }
    ]
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "REVALIDATION_NOT_REQUIRED" in codes(report, "blocking")
    assert report["state"]["claims"]["H1.r1"]["pipeline_id"] == "p1"


def test_machine_not_revalidated_record_is_valid_but_cannot_clear_stale(tmp_path):
    registry = base_registry()
    registry["pipelines"]["pipelines"][0]["status"] = "superseded"
    registry["pipelines"]["pipelines"].append(
        {
            "pipeline_id": "p2",
            "status": "current",
            "first_formal_batch_at": "2026-03-01T00:00:00Z",
        }
    )
    add_destination_evidence(registry)
    add_destination_gate_evaluation(registry)
    registry["reported_figures"]["revalidations"] = [
        {
            "target": {"kind": "claim_revision", "id": "H1.r1"},
            "from_pipeline": "p1",
            "to_pipeline": "p2",
            "method": "machine",
            "tolerance": "abs(delta) <= 0.01 and sign unchanged",
            "result": "not_revalidated",
            "performed_by": "validator",
            "performed_at": "2026-03-02T00:00:00Z",
            "evidence_card": "EC-2",
        }
    ]
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert not (
        {
            "REVALIDATION_COMPARISON_INVALID",
            "REVALIDATION_RESULT_MISMATCH",
            "REVALIDATION_SOURCE_INVALID",
        }
        & codes(report, "blocking")
    )
    assert report["state"]["claims"]["H1.r1"]["availability"] == "stale"


def test_failed_figure_revalidation_does_not_need_a_resolvable_result_artifact(
    tmp_path,
):
    registry = base_registry()
    registry["pipelines"]["pipelines"][0]["status"] = "superseded"
    registry["pipelines"]["pipelines"].append(
        {
            "pipeline_id": "p2",
            "status": "current",
            "first_formal_batch_at": "2026-03-01T00:00:00Z",
        }
    )
    add_destination_evidence(registry)
    add_destination_gate_evaluation(registry)
    registry["reported_figures"]["reported_figures"][0]["source_artifact"] = (
        "missing/{pipeline_id}.yaml"
    )
    registry["reported_figures"]["revalidations"] = [
        {
            "target": {"kind": "reported_figure", "id": "RF-1"},
            "from_pipeline": "p1",
            "to_pipeline": "p2",
            "method": "machine",
            "tolerance": "abs(delta) <= 0.01 and sign unchanged",
            "result": "not_revalidated",
            "performed_by": "validator",
            "performed_at": "2026-03-02T00:00:00Z",
            "evidence_card": "EC-2",
        }
    ]
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "REVALIDATION_SOURCE_INVALID" not in codes(report, "blocking")
    assert report["state"]["reported_figures"]["RF-1"]["status"] == "stale"


def test_revalidated_upstream_recomputes_a_derived_reported_figure(tmp_path):
    registry = base_registry()
    registry["pipelines"]["pipelines"][0]["status"] = "superseded"
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
    add_destination_evidence(registry)
    add_destination_gate_evaluation(registry)
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
            "evidence_card": "EC-2",
        }
    ]
    root = write_registry(tmp_path, registry)
    (root / "results").mkdir()
    (root / "results" / "p2.yaml").write_text("estimate: 2.5\n", encoding="utf-8")
    report = validate_registry(load_registry(root), "C")
    derived = report["state"]["reported_figures"]["RF-percent"]
    assert derived["value"] == 250.0
    assert derived["pipeline_id"] == "p2"
    assert derived["status"] == "current"
    assert derived["revalidation"]["derived_from"] == "RF-1"
    assert "RECOMPUTED_REPORTED_FIGURE" in codes(report, "derived")


def test_recomputation_without_upstream_transition_cannot_clear_derived_stale(tmp_path):
    registry = base_registry()
    registry["pipelines"]["pipelines"][0]["status"] = "superseded"
    registry["pipelines"]["pipelines"].append(
        {
            "pipeline_id": "p2",
            "status": "current",
            "first_formal_batch_at": "2026-03-01T00:00:00Z",
        }
    )
    registry["reported_figures"]["reported_figures"] = [
        {
            "figure_id": "RF-upstream",
            "pipeline_id": "p2",
            "value": 2.5,
            "source_artifact": "results/p2.yaml",
            "source_locator": "estimate",
            "paper_locations": ["paper/results.md#upstream"],
        },
        {
            "figure_id": "RF-derived",
            "pipeline_id": "p1",
            "value": 200.0,
            "source_artifact": "computed",
            "source_locator": "RF-upstream",
            "paper_locations": ["paper/results.md#derived"],
            "derived_from": "RF-upstream",
            "transform": {"operation": "multiply", "operand": 100},
        },
    ]
    registry["outputs"]["outputs"][0]["reported_figure_ids"] = ["RF-derived"]
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    derived_figure = report["state"]["reported_figures"]["RF-derived"]
    assert derived_figure["pipeline_id"] == "p1"
    assert derived_figure["status"] == "stale"
    assert derived_figure["_stale_reasons"] == ["pipeline_superseded"]


def test_semantic_correction_stays_stale_after_machine_revalidation(tmp_path):
    registry = base_registry()
    fact = registry["semantics"]["semantic_facts"][0]
    predecessor = copy.deepcopy(fact)
    predecessor.update(
        {
            "fact_revision_id": "SEM-outcome.r0",
            "valid_range": ["2023-01-01", "2023-12-31"],
        }
    )
    fact.update({"supersedes": "SEM-outcome.r0", "revision_reason": "corrected"})
    registry["semantics"]["semantic_facts"].insert(0, predecessor)
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
    registry["evidence_cards"]["evidence_cards"][0]["machine_comparison"] = {
        "source_evidence_card": "EC-source",
        "destination_evidence_card": "EC-1",
    }
    registry["evidence_cards"]["evidence_cards"].append(
        {
            "evidence_card_id": "EC-source",
            "pipeline_id": "p1",
            "provenance": "confirmatory",
            "status": "current",
            "depends_on": [{"kind": "raw_field", "id": "outcome"}],
            "comparison_endpoint": {
                "artifact": "comparison/p1-source.yaml",
                "locator": "estimate",
            },
        }
    )
    registry["reported_figures"]["revalidations"] = [
        {
            "target": {"kind": "claim_revision", "id": "H1.r1"},
            "from_pipeline": "p1",
            "to_pipeline": "p1",
            "method": "machine",
            "tolerance": "abs(delta) <= 0.01 and sign unchanged",
            "comparison": {"from_value": 2.0, "to_value": 2.005},
            "result": "revalidated",
            "performed_by": "validator",
            "performed_at": "2026-03-02T00:00:00Z",
            "evidence_card": "EC-1",
        }
    ]
    root = write_registry(tmp_path, registry)
    (root / "comparison" / "p1-source.yaml").write_text(
        "estimate: 2.0\n", encoding="utf-8"
    )
    report = validate_registry(load_registry(root), "C")
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
    if status == "released":
        registry["gates"]["changes"] = [
            {
                "change_id": "D-1",
                "object_kind": "claim_key",
                "object_id": "H1",
                "pipeline_id": "p1",
                "new_state": "changed",
                "authorized_by": "authority",
                "occurred_at": "2026-02-01T00:00:00Z",
                "evidence_card": "EC-1",
            }
        ]
    root = write_registry(tmp_path, registry)
    if status == "satisfied" and evaluation.get("compensation_artifact"):
        artifact = root / evaluation["compensation_artifact"]
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text("Gate compensation evidence.\n", encoding="utf-8")
    return validate_registry(load_registry(root), "C")


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


def test_checkpoint_c_blocks_missing_gate_evaluation(tmp_path):
    registry = base_registry()
    registry["gates"]["gate_evaluations"] = []
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "GATE_NOT_EVALUATED" in codes(report, "blocking")


def test_complete_gate_coverage_requires_both_matching_scopes(tmp_path):
    report = _gate_report(tmp_path, "passed", coverage={"complete": True})
    assert "GATE_COVERAGE_INCOMPLETE" in codes(report, "blocking")

    report = _gate_report(
        tmp_path / "mismatch",
        "passed",
        coverage={
            "declared_scope": "all observations",
            "evaluated_scope": "selected observations",
            "complete": True,
        },
    )
    assert "GATE_COVERAGE_MISMATCH" in codes(report, "blocking")


def test_gate_evaluation_target_must_match_frozen_definition(tmp_path):
    registry = base_registry()
    registry["gates"]["gate_evaluations"][0]["evaluated_against"] = {
        "kind": "claim_key",
        "id": "OTHER",
    }
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "GATE_SCOPE_MISMATCH" in codes(report, "blocking")


def test_duplicate_gate_evaluation_pair_blocks(tmp_path):
    registry = base_registry()
    registry["gates"]["gate_evaluations"].append(
        copy.deepcopy(registry["gates"]["gate_evaluations"][0])
    )
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "DUPLICATE_GATE_EVALUATION" in codes(report, "blocking")


def test_gate_evidence_must_belong_to_evaluation_pipeline(tmp_path):
    registry = base_registry()
    registry["pipelines"]["pipelines"].append(
        {
            "pipeline_id": "p2",
            "status": "current",
            "first_formal_batch_at": "2026-03-01T00:00:00Z",
        }
    )
    second = copy.deepcopy(registry["gates"]["gate_evaluations"][0])
    second["pipeline_id"] = "p2"
    registry["gates"]["gate_evaluations"].append(second)
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "GATE_EVIDENCE_INVALID" in codes(report, "blocking")


def test_stale_evidence_cannot_close_a_gate(tmp_path):
    registry = base_registry()
    registry["evidence_cards"]["evidence_cards"][0]["status"] = "stale"
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "GATE_EVIDENCE_INVALID" in codes(report, "blocking")


@pytest.mark.parametrize(
    ("release_update", "expected_code"),
    [
        ({"timing": "sometimes"}, "GATE_RELEASE_TIMING_INVALID"),
        ({"triggering_change_id": "UNKNOWN"}, "GATE_CHANGE_INVALID"),
        ({"evidence_card": "UNKNOWN"}, "GATE_EVIDENCE_INVALID"),
    ],
)
def test_release_requires_valid_timing_change_and_evidence(
    tmp_path, release_update, expected_code
):
    registry = base_registry()
    registry["gates"]["changes"] = [
        {
            "change_id": "D-1",
            "object_kind": "claim_key",
            "object_id": "H1",
            "pipeline_id": "p1",
            "new_state": "changed",
            "authorized_by": "authority",
            "occurred_at": "2026-02-01T00:00:00Z",
            "evidence_card": "EC-1",
        }
    ]
    evaluation = registry["gates"]["gate_evaluations"][0]
    evaluation["status"] = "released"
    evaluation["release"] = {
        "triggering_change_id": "D-1",
        "reason": "Measure changed.",
        "authorized_by": "authority",
        "timing": "pre_result",
        "evidence_card": "EC-1",
        "compensation_disposition": "not required",
    }
    evaluation["release"].update(release_update)
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert expected_code in codes(report, "blocking")


def test_release_change_must_match_gate_scope(tmp_path):
    registry = base_registry()
    registry["gates"]["changes"] = [
        {
            "change_id": "D-1",
            "object_kind": "dataset",
            "object_id": "OTHER",
            "pipeline_id": "p1",
            "new_state": "changed",
            "authorized_by": "authority",
            "occurred_at": "2026-02-01T00:00:00Z",
            "evidence_card": "EC-1",
        }
    ]
    evaluation = registry["gates"]["gate_evaluations"][0]
    evaluation.update(
        {
            "status": "released",
            "release": {
                "triggering_change_id": "D-1",
                "reason": "Unrelated change.",
                "authorized_by": "authority",
                "timing": "pre_result",
                "evidence_card": "EC-1",
                "compensation_disposition": "not required",
            },
        }
    )
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "GATE_CHANGE_INVALID" in codes(report, "blocking")


def test_retired_historical_claim_only_moots_its_own_pipeline_evaluation(tmp_path):
    registry = base_registry()
    registry["claims"]["claims"][0].update(
        {"availability": "retired", "change_id": "D-retired"}
    )
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
            "revision_reason": "destination pipeline",
        }
    )
    add_destination_evidence(registry, claim_id="H1.r2")
    registry["gates"]["changes"] = [
        {
            "change_id": "D-retired",
            "object_kind": "claim_revision",
            "object_id": "H1.r1",
            "pipeline_id": "p1",
            "new_state": "retired",
            "authorized_by": "authority",
            "occurred_at": "2026-03-01T00:00:00Z",
            "evidence_card": "EC-1",
        }
    ]
    add_destination_gate_evaluation(registry, status="triggered")
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    moot_pipelines = {
        item["pipeline_id"]
        for item in report["derived"]
        if item["code"] == "GATE_MOOT"
    }
    assert moot_pipelines == {"p1"}
    assert "GATE_TRIGGERED" in codes(report, "blocking")


def _add_challenge(
    registry: dict,
    relation_id: str,
    card_id: str,
    *,
    provenance: str = "confirmatory",
    status: str = "current",
) -> None:
    registry["evidence_cards"]["evidence_cards"].append(
        {
            "evidence_card_id": card_id,
            "pipeline_id": "p1",
            "provenance": provenance,
            "status": "current",
            "depends_on": [{"kind": "raw_field", "id": "outcome"}],
        }
    )
    registry["evidence_relations"]["evidence_relations"].append(
        {
            "relation_id": relation_id,
            "evidence_card_id": card_id,
            "claim_revision_id": "H1.r1",
            "relation": "challenges",
            "status": status,
            "author": "auditor",
            "date": "2026-02-02",
            "rationale": f"Challenge {relation_id}.",
        }
    )


def test_every_live_confirmatory_challenge_requires_identity_matched_disclosure(tmp_path):
    registry = base_registry()
    _add_challenge(registry, "ER-C1", "EC-C1")
    _add_challenge(registry, "ER-C2", "EC-C2")
    registry["claims"]["claims"][0]["challenge_disclosures"] = [
        {
            "challenge_id": "ER-C1",
            "paper_location": "paper/results.md#challenge-1",
            "adjacent": True,
        }
    ]
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert report["state"]["claims"]["H1.r1"]["_live_challenge_ids"] == [
        "ER-C1",
        "ER-C2",
    ]
    assert "PUBLICATION_INELIGIBLE" in codes(report, "blocking")


def test_all_identity_matched_challenge_disclosures_allow_challenged_claim(tmp_path):
    registry = base_registry()
    _add_challenge(registry, "ER-C1", "EC-C1")
    _add_challenge(registry, "ER-C2", "EC-C2")
    registry["claims"]["claims"][0]["challenge_disclosures"] = [
        {
            "challenge_id": challenge_id,
            "paper_location": f"paper/results.md#{challenge_id}",
            "adjacent": True,
        }
        for challenge_id in ("ER-C1", "ER-C2")
    ]
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert report["state"]["claims"]["H1.r1"]["assessment"] == "challenged"
    assert "PUBLICATION_INELIGIBLE" not in codes(report, "blocking")


def test_withdrawn_and_exploratory_challenges_do_not_require_disclosure(tmp_path):
    registry = base_registry()
    _add_challenge(registry, "ER-withdrawn", "EC-withdrawn", status="withdrawn")
    _add_challenge(registry, "ER-exploratory", "EC-exploratory", provenance="exploratory")
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    claim = report["state"]["claims"]["H1.r1"]
    assert claim["assessment"] == "supported"
    assert claim["_live_challenge_ids"] == []
    assert "PUBLICATION_INELIGIBLE" not in codes(report, "blocking")


def test_derived_challenges_do_not_propagate_through_exploratory_evidence(tmp_path):
    registry = base_registry()
    registry["derived_fields"]["derived_fields"] = [
        {
            "derived_field_id": "a",
            "fact_key": "SEM-outcome",
            "status": "defective",
            "known_defects": ["Known defect."],
            "depends_on": [{"kind": "semantic_fact", "id": "SEM-outcome"}],
        }
    ]
    registry["evidence_cards"]["evidence_cards"][0].update(
        {
            "provenance": "exploratory",
            "depends_on": [{"kind": "derived_field", "id": "a"}],
        }
    )
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    claim = report["state"]["claims"]["H1.r1"]
    assert claim["assessment"] == "unresolved"
    assert claim["_live_challenge_ids"] == []
    assert "DEFECTIVE_FIELD_CHALLENGE" not in codes(report, "derived")


def test_derived_challenge_requires_its_stable_identity_in_disclosure(tmp_path):
    registry = base_registry()
    registry["derived_fields"]["derived_fields"] = [
        {
            "derived_field_id": "a",
            "fact_key": "SEM-outcome",
            "status": "defective",
            "known_defects": ["Known defect."],
            "depends_on": [{"kind": "semantic_fact", "id": "SEM-outcome"}],
        }
    ]
    registry["evidence_cards"]["evidence_cards"][0]["depends_on"] = [
        {"kind": "derived_field", "id": "a"}
    ]
    registry["claims"]["claims"][0]["challenge_disclosures"] = [
        {
            "challenge_id": "wrong-id",
            "paper_location": "paper/results.md#defect",
            "adjacent": True,
        }
    ]
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "defective:a" in report["state"]["claims"]["H1.r1"]["_live_challenge_ids"]
    assert "PUBLICATION_INELIGIBLE" in codes(report, "blocking")


@pytest.mark.parametrize(
    "mutate",
    [
        lambda registry: registry["semantics"]["semantic_facts"][0][
            "verification"
        ].__setitem__("result", "maybe"),
        lambda registry: registry["semantics"]["semantic_facts"][0].__setitem__(
            "authority", {"status": "sourced"}
        ),
        lambda registry: registry["derived_fields"]["derived_fields"].append(
            {
                "derived_field_id": "defective",
                "fact_key": "SEM-outcome",
                "status": "defective",
                "depends_on": [{"kind": "semantic_fact", "id": "SEM-outcome"}],
            }
        ),
        lambda registry: registry["applicability"]["applicability"].append(
            {
                "requirement_id": "DG",
                "status": "completed",
                "record_type": "design_grid",
            }
        ),
        lambda registry: registry["applicability"]["applicability"].append(
            {
                "requirement_id": "SP",
                "status": "completed",
                "record_type": "sibling_parity",
                "dimension_results": [{"dimension": "sample", "result": "same"}],
            }
        ),
        lambda registry: registry["outputs"]["outputs"][0].__setitem__(
            "claim_revision_ids", [123]
        ),
    ],
    ids=[
        "verification-result",
        "sourced-authority",
        "known-defects",
        "design-grid",
        "sibling-parity",
        "output-member-type",
    ],
)
def test_conditional_registry_schema_rules_are_executable(tmp_path, mutate):
    registry = base_registry()
    mutate(registry)
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "SCHEMA_INVALID" in codes(report, "blocking")


@pytest.mark.parametrize(
    "mutate",
    [
        lambda registry: registry["gates"]["gate_definitions"][0].__setitem__(
            "frozen", False
        ),
        lambda registry: registry["gates"]["gate_definitions"][0].pop(
            "compensation"
        ),
    ],
    ids=["not-frozen", "missing-compensation"],
)
def test_gate_definition_schema_is_frozen_and_complete(tmp_path, mutate):
    registry = base_registry()
    mutate(registry)
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "SCHEMA_INVALID" in codes(report, "blocking")


def test_semantic_supersedes_must_keep_fact_key_and_revision_reason(tmp_path):
    registry = base_registry()
    predecessor = copy.deepcopy(registry["semantics"]["semantic_facts"][0])
    predecessor.update(
        {
            "fact_key": "SEM-other",
            "fact_revision_id": "SEM-other.r1",
            "field": "other",
            "valid_range": ["2023-01-01", "2023-12-31"],
        }
    )
    registry["semantics"]["semantic_facts"].append(predecessor)
    registry["semantics"]["semantic_facts"][0].update(
        {"supersedes": "SEM-other.r1", "revision_reason": "wrong identity"}
    )
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "SEMANTIC_REVISION_INCOHERENT" in codes(report, "blocking")


def test_failed_semantic_verification_blocks_analysis(tmp_path):
    registry = base_registry()
    registry["semantics"]["semantic_facts"][0]["verification"]["result"] = "fail"
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "B")
    assert "SEMANTIC_VERIFICATION_FAILED" in codes(report, "blocking")


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
        registry["gates"]["changes"] = [
            {
                "change_id": f"D-{availability}",
                "object_kind": "claim_revision",
                "object_id": "H1.r1",
                "pipeline_id": "p1",
                "new_state": availability,
                "authorized_by": "authority",
                "occurred_at": "2026-02-01T00:00:00Z",
                "evidence_card": "EC-1",
            }
        ]
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


def _artifact_authenticated_claim_revalidation(registry: dict) -> dict:
    registry["pipelines"]["pipelines"][0]["status"] = "superseded"
    registry["pipelines"]["pipelines"].append(
        {
            "pipeline_id": "p2",
            "status": "current",
            "first_formal_batch_at": "2026-03-01T00:00:00Z",
        }
    )
    registry["outputs"]["outputs"][0]["pipeline_id"] = "p2"
    registry["outputs"]["outputs"][0]["reported_figure_ids"] = []
    add_destination_evidence(registry)
    add_destination_gate_evaluation(registry)
    record = {
        "target": {"kind": "claim_revision", "id": "H1.r1"},
        "from_pipeline": "p1",
        "to_pipeline": "p2",
        "method": "machine",
        "tolerance": "abs(delta) <= 0.01 and sign unchanged",
        "result": "revalidated",
        "performed_by": "validator",
        "performed_at": "2026-03-02T00:00:00Z",
        "evidence_card": "EC-2",
    }
    registry["reported_figures"]["revalidations"] = [record]
    return record


def _write_comparison_artifacts(root: Path, source: float, destination: float) -> None:
    comparison = root / "comparison"
    comparison.mkdir(exist_ok=True)
    (comparison / "p1.yaml").write_text(
        f"estimate: {source}\n", encoding="utf-8"
    )
    (comparison / "p2.yaml").write_text(
        f"estimate: {destination}\n", encoding="utf-8"
    )


def test_machine_claim_revalidation_resolves_artifact_bound_comparison(tmp_path):
    registry = base_registry()
    _artifact_authenticated_claim_revalidation(registry)
    root = write_registry(tmp_path, registry)
    _write_comparison_artifacts(root, 2.0, 2.005)
    report = validate_registry(load_registry(root), "C")
    claim = report["state"]["claims"]["H1.r1"]
    assert report["blocking"] == []
    assert claim["pipeline_id"] == "p2"
    assert claim["revalidation"]["resolved_comparison"] == {
        "from_value": 2.0,
        "to_value": 2.005,
    }


def test_inline_machine_claim_values_cannot_override_artifact_comparison(tmp_path):
    registry = base_registry()
    record = _artifact_authenticated_claim_revalidation(registry)
    record["comparison"] = {"from_value": 999999.0, "to_value": 999999.0}
    root = write_registry(tmp_path, registry)
    _write_comparison_artifacts(root, 2.0, 9.0)
    report = validate_registry(load_registry(root), "C")
    assert "REVALIDATION_RESULT_MISMATCH" in codes(report, "blocking")
    claim = report["state"]["claims"]["H1.r1"]
    assert claim["pipeline_id"] == "p1"
    assert claim["availability"] == "stale"


def test_machine_comparison_rejects_source_endpoint_bound_to_destination_artifact(
    tmp_path,
):
    registry = base_registry()
    _artifact_authenticated_claim_revalidation(registry)
    registry["evidence_cards"]["evidence_cards"][0]["comparison_endpoint"] = {
        "artifact": "comparison/p2.yaml",
        "locator": "estimate",
    }
    root = write_registry(tmp_path, registry)
    _write_comparison_artifacts(root, 2.0, 2.005)
    report = validate_registry(load_registry(root), "C")
    assert "REVALIDATION_COMPARISON_INVALID" in codes(report, "blocking")
    claim = report["state"]["claims"]["H1.r1"]
    assert claim["pipeline_id"] == "p1"
    assert "REVALIDATED_CLAIM" not in codes(report, "derived")


@pytest.mark.parametrize(
    "source_endpoint",
    [
        {
            "artifact": "comparison/../comparison/p2.yaml",
            "locator": "estimate",
        },
        {
            "artifact": "comparison/p2.yaml",
            "locator": "/estimate",
        },
    ],
)
def test_machine_comparison_rejects_canonical_endpoint_aliases(
    tmp_path, source_endpoint
):
    registry = base_registry()
    _artifact_authenticated_claim_revalidation(registry)
    registry["evidence_cards"]["evidence_cards"][0]["comparison_endpoint"] = (
        source_endpoint
    )
    root = write_registry(tmp_path, registry)
    _write_comparison_artifacts(root, 2.0, 2.005)

    report = validate_registry(load_registry(root), "C")

    assert "REVALIDATION_COMPARISON_INVALID" in codes(report, "blocking")
    assert report["state"]["claims"]["H1.r1"]["pipeline_id"] == "p1"
    assert "REVALIDATED_CLAIM" not in codes(report, "derived")


@pytest.mark.parametrize(
    ("source_locator", "expected_code"),
    [
        ("values.1", "REVALIDATION_COMPARISON_INVALID"),
        ("values.01", "REVALIDATION_SOURCE_INVALID"),
        ("values.+1", "REVALIDATION_SOURCE_INVALID"),
        ("values.-1", "REVALIDATION_SOURCE_INVALID"),
    ],
)
def test_machine_comparison_rejects_list_index_locator_aliases(
    tmp_path, source_locator, expected_code
):
    registry = base_registry()
    _artifact_authenticated_claim_revalidation(registry)
    source_card, destination_card = registry["evidence_cards"]["evidence_cards"]
    source_card["comparison_endpoint"] = {
        "artifact": "comparison/p2.yaml",
        "locator": source_locator,
    }
    destination_card["comparison_endpoint"] = {
        "artifact": "comparison/p2.yaml",
        "locator": "/values/1",
    }
    root = write_registry(tmp_path, registry)
    (root / "comparison" / "p2.yaml").write_text(
        "values:\n  - 99\n  - 2.005\n", encoding="utf-8"
    )

    report = validate_registry(load_registry(root), "C")

    assert expected_code in codes(report, "blocking")
    assert report["state"]["claims"]["H1.r1"]["pipeline_id"] == "p1"
    assert "REVALIDATED_CLAIM" not in codes(report, "derived")


def test_machine_comparison_rejects_symlinked_endpoint_alias(tmp_path):
    registry = base_registry()
    _artifact_authenticated_claim_revalidation(registry)
    registry["evidence_cards"]["evidence_cards"][0]["comparison_endpoint"] = {
        "artifact": "comparison/p2-alias.yaml",
        "locator": "estimate",
    }
    root = write_registry(tmp_path, registry)
    _write_comparison_artifacts(root, 2.0, 2.005)
    (root / "comparison" / "p2-alias.yaml").symlink_to("p2.yaml")

    report = validate_registry(load_registry(root), "C")

    assert "REVALIDATION_COMPARISON_INVALID" in codes(report, "blocking")
    assert report["state"]["claims"]["H1.r1"]["pipeline_id"] == "p1"
    assert "REVALIDATED_CLAIM" not in codes(report, "derived")


def test_unknown_revalidation_target_is_eagerly_rejected(tmp_path):
    registry = base_registry()
    registry["reported_figures"]["revalidations"] = [
        {
            "target": {"kind": "claim_revision", "id": "MISSING"},
            "from_pipeline": "p1",
            "to_pipeline": "p1",
            "method": "manual",
            "result": "not_revalidated",
            "performed_by": "validator",
            "performed_at": "2026-03-02T00:00:00Z",
            "evidence_card": "EC-1",
        }
    ]
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "REVALIDATION_TARGET_UNKNOWN" in codes(report, "blocking")


@pytest.mark.parametrize(
    "target",
    [{}, {"kind": "claim_revision"}, {"kind": 3, "id": "H1.r1"}],
)
def test_revalidation_target_has_complete_typed_schema(tmp_path, target):
    registry = base_registry()
    registry["reported_figures"]["revalidations"] = [
        {
            "target": target,
            "from_pipeline": "p1",
            "to_pipeline": "p1",
            "method": "manual",
            "result": "not_revalidated",
            "performed_by": "validator",
            "performed_at": "2026-03-02T00:00:00Z",
            "evidence_card": "EC-1",
        }
    ]
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert codes(report, "blocking") == {"SCHEMA_INVALID"}


def test_malformed_revalidation_target_cli_returns_stable_json(tmp_path, capsys):
    registry = base_registry()
    registry["reported_figures"]["revalidations"] = [
        {
            "target": {},
            "from_pipeline": "p1",
            "to_pipeline": "p1",
            "method": "manual",
            "result": "not_revalidated",
            "performed_by": "validator",
            "performed_at": "2026-03-02T00:00:00Z",
            "evidence_card": "EC-1",
        }
    ]
    root = write_registry(tmp_path, registry)
    assert main([str(root), "--checkpoint", "C", "--format", "json"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert codes(payload, "blocking") == {"SCHEMA_INVALID"}
    assert "REGISTRY_VALIDATION_ERROR" not in codes(payload, "blocking")


@pytest.mark.parametrize(
    ("field", "value", "method"),
    [
        ("from_pipeline", [], "manual"),
        ("to_pipeline", {}, "manual"),
        ("method", [], "manual"),
        ("result", {}, "manual"),
        ("performed_by", ["validator"], "manual"),
        ("performed_at", ["2026-03-02T00:00:00Z"], "manual"),
        ("evidence_card", {"id": "EC-1"}, "manual"),
        (
            "tolerance",
            ["abs(delta) <= 0.01 and sign unchanged"],
            "machine",
        ),
    ],
)
def test_revalidation_fields_require_nonempty_strings_before_use(
    tmp_path, field, value, method
):
    registry = base_registry()
    record = {
        "target": {"kind": "claim_revision", "id": "H1.r1"},
        "from_pipeline": "p1",
        "to_pipeline": "p1",
        "method": method,
        "tolerance": "abs(delta) <= 0.01 and sign unchanged",
        "result": "not_revalidated",
        "performed_by": "validator",
        "performed_at": "2026-03-02T00:00:00Z",
        "evidence_card": "EC-1",
    }
    record[field] = value
    registry["reported_figures"]["revalidations"] = [record]
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert codes(report, "blocking") == {"SCHEMA_INVALID"}
    assert "REGISTRY_VALIDATION_ERROR" not in codes(report, "blocking")
    assert "REVALIDATED_CLAIM" not in codes(report, "derived")


def test_list_valued_tolerance_cannot_authorize_machine_revalidation(tmp_path):
    registry = base_registry()
    record = _artifact_authenticated_claim_revalidation(registry)
    record["tolerance"] = ["abs(delta) <= 0.01 and sign unchanged"]

    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")

    assert codes(report, "blocking") == {"SCHEMA_INVALID"}
    assert report["state"]["claims"]["H1.r1"]["pipeline_id"] == "p1"
    assert "REVALIDATED_CLAIM" not in codes(report, "derived")


def test_dormant_machine_comparison_artifact_is_eagerly_resolved(tmp_path):
    registry = base_registry()
    registry["evidence_cards"]["evidence_cards"].append(
        {
            "evidence_card_id": "EC-dormant",
            "pipeline_id": "p1",
            "provenance": "confirmatory",
            "status": "current",
            "depends_on": [],
            "comparison_endpoint": {
                "artifact": "comparison/missing.yaml",
                "locator": "estimate",
            },
            "machine_comparison": {
                "source_evidence_card": "EC-1",
                "destination_evidence_card": "EC-dormant",
            },
        }
    )
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "REVALIDATION_SOURCE_INVALID" in codes(report, "blocking")


def _split_semantic_window(registry: dict) -> None:
    first = registry["semantics"]["semantic_facts"][0]
    first["valid_range"] = ["2024-01-01", "2024-05-31"]
    second = copy.deepcopy(first)
    second.update(
        {
            "fact_revision_id": "SEM-outcome.r2",
            "supersedes": "SEM-outcome.r1",
            "revision_reason": "source definition changed",
            "statement": "Revised observed outcome.",
            "valid_range": ["2024-06-01", None],
        }
    )
    registry["semantics"]["semantic_facts"].append(second)


def test_semantic_equivalence_requires_typed_authorship_evidence_and_scope(tmp_path):
    registry = base_registry()
    _split_semantic_window(registry)
    registry["semantics"]["semantic_equivalence_decisions"] = [
        {
            "field": "outcome",
            "fact_revision_ids": ["SEM-outcome.r1", "SEM-outcome.r2"],
            "valid_range": ["2024-01-01", "2024-12-31"],
            "decision": "equivalent",
            "decided_by": {"bogus": True},
            "decided_at": "not-a-time",
        }
    ]
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "SCHEMA_INVALID" in codes(report, "blocking")


def test_list_valued_semantic_equivalence_decision_returns_stable_cli_json(
    tmp_path, capsys
):
    registry = base_registry()
    _split_semantic_window(registry)
    registry["semantics"]["semantic_equivalence_decisions"] = [
        {
            "field": "outcome",
            "fact_revision_ids": ["SEM-outcome.r1", "SEM-outcome.r2"],
            "valid_range": ["2024-01-01", "2024-12-31"],
            "decision": ["equivalent"],
            "decided_by": "semantic-authority",
            "decided_at": "2026-02-01T00:00:00Z",
            "evidence_card": "EC-1",
        }
    ]
    root = write_registry(tmp_path, registry)

    assert main([str(root), "--checkpoint", "C", "--format", "json"]) == 1
    payload = json.loads(capsys.readouterr().out)

    assert codes(payload, "blocking") == {"SCHEMA_INVALID"}
    assert "REGISTRY_VALIDATION_ERROR" not in codes(payload, "blocking")


def test_authenticated_semantic_equivalence_suppresses_only_its_resolved_scope(
    tmp_path,
):
    registry = base_registry()
    _split_semantic_window(registry)
    registry["semantics"]["semantic_equivalence_decisions"] = [
        {
            "field": "outcome",
            "fact_revision_ids": ["SEM-outcome.r1", "SEM-outcome.r2"],
            "valid_range": ["2024-01-01", "2024-12-31"],
            "decision": "equivalent",
            "decided_by": "semantic-authority",
            "decided_at": "2026-02-01T00:00:00Z",
            "evidence_card": "EC-1",
        }
    ]
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "SEMANTIC_DISCLOSURE_REQUIRED" not in codes(report, "reports")
    assert report["blocking"] == []


def test_semantic_equivalence_unknown_scope_reference_blocks(tmp_path):
    registry = base_registry()
    registry["semantics"]["semantic_equivalence_decisions"] = [
        {
            "field": "outcome",
            "fact_revision_ids": ["SEM-outcome.r1", "SEM-unknown.r1"],
            "valid_range": ["2024-01-01", "2024-12-31"],
            "decision": "equivalent",
            "decided_by": "semantic-authority",
            "decided_at": "2026-02-01T00:00:00Z",
            "evidence_card": "EC-1",
        }
    ]
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "UNKNOWN_REFERENCE" in codes(report, "blocking")


def test_semantic_equivalence_cannot_suppress_unlisted_fact_transition(tmp_path):
    registry = base_registry()
    _split_semantic_window(registry)
    third = copy.deepcopy(registry["semantics"]["semantic_facts"][-1])
    registry["semantics"]["semantic_facts"][-1]["valid_range"] = [
        "2024-06-01",
        "2024-08-31",
    ]
    third.update(
        {
            "fact_key": "SEM-other",
            "fact_revision_id": "SEM-other.r1",
            "supersedes": None,
            "valid_range": ["2024-09-01", None],
        }
    )
    registry["semantics"]["semantic_facts"].append(third)
    registry["semantics"]["semantic_equivalence_decisions"] = [
        {
            "field": "outcome",
            "fact_revision_ids": ["SEM-outcome.r1", "SEM-outcome.r2"],
            "valid_range": ["2024-01-01", "2024-08-31"],
            "decision": "equivalent",
            "decided_by": "semantic-authority",
            "decided_at": "2026-02-01T00:00:00Z",
            "evidence_card": "EC-1",
        }
    ]
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "SEMANTIC_DISCLOSURE_REQUIRED" in codes(report, "reports")


def test_semantic_equivalence_evidence_must_depend_on_compared_field(tmp_path):
    registry = base_registry()
    _split_semantic_window(registry)
    registry["evidence_cards"]["evidence_cards"][0]["depends_on"] = [
        {"kind": "raw_field", "id": "unrelated"}
    ]
    registry["semantics"]["semantic_equivalence_decisions"] = [
        {
            "field": "outcome",
            "fact_revision_ids": ["SEM-outcome.r1", "SEM-outcome.r2"],
            "valid_range": ["2024-01-01", "2024-12-31"],
            "decision": "equivalent",
            "decided_by": "semantic-authority",
            "decided_at": "2026-02-01T00:00:00Z",
            "evidence_card": "EC-1",
        }
    ]
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "SEMANTIC_EQUIVALENCE_EVIDENCE_INVALID" in codes(report, "blocking")


def test_claim_key_gate_requires_target_revision_on_evaluation_pipeline(tmp_path):
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
            "evidence_card_id": "EC-p2",
            "pipeline_id": "p2",
            "provenance": "confirmatory",
            "status": "current",
            "depends_on": [],
        }
    )
    evaluation = copy.deepcopy(registry["gates"]["gate_evaluations"][0])
    evaluation.update({"pipeline_id": "p2", "evidence_card": "EC-p2"})
    registry["gates"]["gate_evaluations"].append(evaluation)
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "GATE_TARGET_INSTANCE_MISSING" in codes(report, "blocking")


def test_same_pipeline_retired_revision_moots_gate_with_current_successor(tmp_path):
    registry = base_registry()
    registry["claims"]["claims"].append(
        {
            "claim_key": "H1",
            "claim_revision_id": "H1.r0",
            "pipeline_id": "p1",
            "availability": "retired",
            "assessment": "supported",
            "change_id": "D-retired",
        }
    )
    registry["gates"]["changes"] = [
        {
            "change_id": "D-retired",
            "object_kind": "claim_revision",
            "object_id": "H1.r0",
            "pipeline_id": "p1",
            "new_state": "retired",
            "authorized_by": "authority",
            "occurred_at": "2026-02-01T00:00:00Z",
            "evidence_card": "EC-1",
        }
    ]
    registry["gates"]["gate_evaluations"][0]["status"] = "triggered"
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "GATE_MOOT" in codes(report, "derived")
    assert "GATE_TRIGGERED" not in codes(report, "blocking")


def _add_second_gate_target(registry: dict) -> None:
    registry["claims"]["claims"].append(
        {
            "claim_key": "H2",
            "claim_revision_id": "H2.r1",
            "pipeline_id": "p1",
            "availability": "current",
            "assessment": "supported",
        }
    )
    registry["gates"]["gate_definitions"][0]["applies_to"].append(
        {"kind": "claim_key", "id": "H2"}
    )
    registry["gates"]["gate_evaluations"][0]["evaluated_against"] = {
        "kind": "claim_key",
        "id": "H2",
    }


def test_multi_target_gate_moot_uses_only_evaluated_claim(tmp_path):
    registry = base_registry()
    _add_second_gate_target(registry)
    registry["claims"]["claims"].append(
        {
            "claim_key": "H1",
            "claim_revision_id": "H1.r0",
            "pipeline_id": "p1",
            "availability": "retired",
            "assessment": "supported",
            "change_id": "D-H1-retired",
        }
    )
    registry["gates"]["changes"] = [
        {
            "change_id": "D-H1-retired",
            "object_kind": "claim_revision",
            "object_id": "H1.r0",
            "pipeline_id": "p1",
            "new_state": "retired",
            "authorized_by": "authority",
            "occurred_at": "2026-02-01T00:00:00Z",
            "evidence_card": "EC-1",
        }
    ]
    registry["gates"]["gate_evaluations"][0]["status"] = "triggered"
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "GATE_MOOT" not in codes(report, "derived")
    assert "GATE_TRIGGERED" in codes(report, "blocking")


def test_multi_target_gate_release_uses_only_evaluated_claim(tmp_path):
    registry = base_registry()
    _add_second_gate_target(registry)
    registry["gates"]["changes"] = [
        {
            "change_id": "D-H1-changed",
            "object_kind": "claim_key",
            "object_id": "H1",
            "pipeline_id": "p1",
            "new_state": "changed",
            "authorized_by": "authority",
            "occurred_at": "2026-02-01T00:00:00Z",
            "evidence_card": "EC-1",
        }
    ]
    registry["gates"]["gate_evaluations"][0].update(
        {
            "status": "released",
            "release": {
                "triggering_change_id": "D-H1-changed",
                "reason": "Unrelated H1 change.",
                "authorized_by": "authority",
                "timing": "pre_result",
                "evidence_card": "EC-1",
                "compensation_disposition": "not required",
            },
        }
    )
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "GATE_CHANGE_INVALID" in codes(report, "blocking")


def test_literal_at_pipeline_claim_key_is_not_mooted_as_a_different_claim(tmp_path):
    registry = base_registry()
    registry["claims"]["claims"][0].update(
        {"availability": "retired", "change_id": "D-H1-retired"}
    )
    registry["claims"]["claims"].append(
        {
            "claim_key": "H1@p1",
            "claim_revision_id": "literal.r1",
            "pipeline_id": "p1",
            "availability": "current",
            "assessment": "supported",
        }
    )
    registry["evidence_relations"]["evidence_relations"][0][
        "claim_revision_id"
    ] = "literal.r1"
    registry["outputs"]["outputs"][0]["claim_revision_ids"] = ["literal.r1"]
    registry["gates"]["gate_definitions"][0]["applies_to"] = [
        {"kind": "claim_key", "id": "H1@p1"}
    ]
    registry["gates"]["gate_evaluations"][0].update(
        {
            "evaluated_against": {"kind": "claim_key", "id": "H1@p1"},
            "status": "triggered",
        }
    )
    registry["gates"]["changes"] = [
        {
            "change_id": "D-H1-retired",
            "object_kind": "claim_revision",
            "object_id": "H1.r1",
            "pipeline_id": "p1",
            "new_state": "retired",
            "authorized_by": "authority",
            "occurred_at": "2026-02-01T00:00:00Z",
            "evidence_card": "EC-1",
        }
    ]

    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")

    assert "GATE_MOOT" not in codes(report, "derived")
    assert "GATE_TRIGGERED" in codes(report, "blocking")


def test_literal_at_pipeline_claim_key_rejects_another_claims_release(tmp_path):
    registry = base_registry()
    registry["claims"]["claims"].append(
        {
            "claim_key": "H1@p1",
            "claim_revision_id": "literal.r1",
            "pipeline_id": "p1",
            "availability": "current",
            "assessment": "supported",
        }
    )
    registry["evidence_relations"]["evidence_relations"][0][
        "claim_revision_id"
    ] = "literal.r1"
    registry["outputs"]["outputs"][0]["claim_revision_ids"] = ["literal.r1"]
    registry["gates"]["gate_definitions"][0]["applies_to"] = [
        {"kind": "claim_key", "id": "H1@p1"}
    ]
    registry["gates"]["gate_evaluations"][0].update(
        {
            "evaluated_against": {"kind": "claim_key", "id": "H1@p1"},
            "status": "released",
            "release": {
                "triggering_change_id": "D-H1-changed",
                "reason": "Unrelated H1 change.",
                "authorized_by": "authority",
                "timing": "pre_result",
                "evidence_card": "EC-1",
                "compensation_disposition": "not required",
            },
        }
    )
    registry["gates"]["changes"] = [
        {
            "change_id": "D-H1-changed",
            "object_kind": "claim_key",
            "object_id": "H1",
            "pipeline_id": "p1",
            "new_state": "changed",
            "authorized_by": "authority",
            "occurred_at": "2026-02-01T00:00:00Z",
            "evidence_card": "EC-1",
        }
    ]

    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")

    assert "GATE_CHANGE_INVALID" in codes(report, "blocking")
    assert "GATE_RELEASED" not in codes(report, "reports")


@pytest.mark.parametrize(
    "record",
    [
        {
            "requirement_id": "DG",
            "status": "completed",
            "record_type": "design_grid",
            "dimensions": ["sample", "sample"],
            "empty_cells": ["not-a-cell", 3, {}],
        },
        {
            "requirement_id": "SP",
            "status": "completed",
            "record_type": "sibling_parity",
            "dimensions": ["sample", "period"],
            "dimension_results": [
                {"dimension": "sample", "result": "match"},
                {"dimension": "sample", "result": "diverge"},
            ],
            "consequence_assessment": "No material consequence.",
        },
    ],
    ids=["design-grid-cells", "sibling-parity-coverage"],
)
def test_nested_applicability_records_require_unique_coherent_dimensions(
    tmp_path, record
):
    registry = base_registry()
    registry["applicability"]["applicability"].append(record)
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "SCHEMA_INVALID" in codes(report, "blocking")


def test_change_state_is_constrained_by_object_kind(tmp_path):
    registry = base_registry()
    registry["gates"]["changes"] = [
        {
            "change_id": "D-1",
            "object_kind": "claim_revision",
            "object_id": "H1.r1",
            "pipeline_id": "p1",
            "new_state": "end_of_life",
            "authorized_by": "authority",
            "occurred_at": "2026-02-01T00:00:00Z",
            "evidence_card": "EC-1",
        }
    ]
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "SCHEMA_INVALID" in codes(report, "blocking")


def test_claim_change_link_must_resolve_to_its_exact_claim(tmp_path):
    registry = base_registry()
    registry["claims"]["claims"][0]["change_id"] = "D-missing"
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "UNKNOWN_REFERENCE" in codes(report, "blocking")


def test_supersedes_lineage_does_not_propagate_old_evidence_defects(tmp_path):
    registry = base_registry()
    old_claim = registry["claims"]["claims"][0]
    old_claim.update(
        {
            "claim_revision_id": "H1.r0",
            "availability": "superseded",
            "assessment": "supported",
        }
    )
    registry["claims"]["claims"].append(
        {
            "claim_key": "H1",
            "claim_revision_id": "H1.r1",
            "pipeline_id": "p1",
            "supersedes": "H1.r0",
            "revision_reason": "independent clean estimate",
            "availability": "current",
            "assessment": "supported",
        }
    )
    registry["derived_fields"]["derived_fields"] = [
        {
            "derived_field_id": "bad",
            "fact_key": "SEM-outcome",
            "status": "defective",
            "known_defects": ["Old calculation is defective."],
            "depends_on": [{"kind": "semantic_fact", "id": "SEM-outcome"}],
        }
    ]
    old_card = registry["evidence_cards"]["evidence_cards"][0]
    old_card["depends_on"] = [{"kind": "derived_field", "id": "bad"}]
    old_relation = registry["evidence_relations"]["evidence_relations"][0]
    old_relation["claim_revision_id"] = "H1.r0"
    registry["evidence_cards"]["evidence_cards"].append(
        {
            "evidence_card_id": "EC-clean",
            "pipeline_id": "p1",
            "provenance": "confirmatory",
            "status": "current",
            "depends_on": [{"kind": "raw_field", "id": "outcome"}],
        }
    )
    registry["evidence_relations"]["evidence_relations"].append(
        {
            "relation_id": "ER-clean",
            "evidence_card_id": "EC-clean",
            "claim_revision_id": "H1.r1",
            "relation": "supports",
            "status": "current",
            "author": "analyst",
            "date": "2026-02-02",
            "rationale": "Independent clean support.",
        }
    )
    registry["outputs"]["outputs"][0]["claim_revision_ids"] = ["H1.r1"]
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    successor = report["state"]["claims"]["H1.r1"]
    assert successor["assessment"] == "supported"
    assert successor["_live_challenge_ids"] == []
    assert not any(
        item.get("claim_revision_id") == "H1.r1"
        and item["code"] == "DEFECTIVE_FIELD_CHALLENGE"
        for item in report["derived"]
    )


@pytest.mark.parametrize("kind", ["claim", "semantic"])
def test_lineage_cycles_block_without_becoming_evidence_dependencies(
    tmp_path, kind
):
    registry = base_registry()
    if kind == "claim":
        first = registry["claims"]["claims"][0]
        first.update({"supersedes": "H1.r0", "revision_reason": "cycle"})
        registry["claims"]["claims"].append(
            {
                "claim_key": "H1",
                "claim_revision_id": "H1.r0",
                "pipeline_id": "p1",
                "supersedes": "H1.r1",
                "revision_reason": "cycle",
                "availability": "superseded",
                "assessment": "supported",
            }
        )
    else:
        first = registry["semantics"]["semantic_facts"][0]
        first.update({"supersedes": "SEM-outcome.r0", "revision_reason": "cycle"})
        second = copy.deepcopy(first)
        second.update(
            {
                "fact_revision_id": "SEM-outcome.r0",
                "supersedes": "SEM-outcome.r1",
                "valid_range": ["2023-01-01", "2023-12-31"],
            }
        )
        registry["semantics"]["semantic_facts"].append(second)
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "B")
    assert "REFERENCE_CYCLE" in codes(report, "blocking")


@pytest.mark.parametrize(
    "mutate",
    [
        lambda registry: registry["gates"]["gate_evaluations"][0].update(
            {
                "status": "inapplicable",
                "applicability_reason": "Outside scope.",
                "declared_by": {"name": "analyst"},
                "accepted_by": "authority",
            }
        ),
        lambda registry: registry["applicability"]["applicability"][0].update(
            {
                "status": "inapplicable",
                "applicability_reason": "Outside scope.",
                "declared_by": ["analyst"],
                "accepted_by": "authority",
                "substituted_by": ["REQ-substitute"],
            }
        )
        or registry["applicability"]["applicability"].append(
            {"requirement_id": "REQ-substitute", "status": "completed"}
        ),
        lambda registry: registry["reported_figures"]["reported_figures"].append(
            {
                "figure_id": "RF-derived-invalid",
                "pipeline_id": "p1",
                "value": 4.0,
                "source_artifact": "computed",
                "source_locator": "RF-1",
                "paper_locations": ["paper/results.md#derived"],
                "derived_from": "RF-1",
                "transform": {"operation": "execute", "operand": "rm"},
            }
        ),
    ],
    ids=["gate-inapplicable-author", "applicability-author", "figure-transform"],
)
def test_remaining_nested_governance_records_have_typed_schemas(tmp_path, mutate):
    registry = base_registry()
    mutate(registry)
    report = validate_registry(load_registry(write_registry(tmp_path, registry)), "C")
    assert "SCHEMA_INVALID" in codes(report, "blocking")


def test_gate_release_nested_fields_are_typed_before_closure(tmp_path):
    report = _gate_report(
        tmp_path,
        "released",
        release={
            "triggering_change_id": "D-1",
            "reason": {"not": "human-editable prose"},
            "authorized_by": "authority",
            "timing": "pre_result",
            "evidence_card": "EC-1",
            "compensation_disposition": "not required",
        },
    )
    assert "SCHEMA_INVALID" in codes(report, "blocking")


def test_discriminating_site_with_low_lexical_strength_is_not_an_underclaim(
    tmp_path,
):
    site = assertion_site(
        "discriminating-site",
        assertion_type="discriminating",
        declared_tier=None,
        alternative_explanation="differential pre-trend selection",
    )
    report = write_assertion_registry(
        tmp_path,
        [site],
        "<!-- discriminating-site --> The pattern is difficult to reconcile with differential selection.\n",
    )
    assert "OVERCLAIM_RESIDUAL" not in report_codes(report)
    assert "UNDERCLAIM_RESIDUAL" not in report_codes(report)


def test_writing_strength_findings_run_at_checkpoint_c_without_changing_b(tmp_path):
    registry = base_registry()
    site = assertion_site(
        "checkpoint-site", declared_tier="T0", has_sampling_distribution=False
    )
    registry["claims"]["claims"][0]["assertion_sites"] = [site]
    root = write_registry(tmp_path, registry)
    paper = root / "paper"
    paper.mkdir()
    (paper / "assertions.md").write_text(
        "<!-- checkpoint-site --> Treatment causes retention.\n", encoding="utf-8"
    )
    report_b = validate_registry(load_registry(root), checkpoint="B")
    report_c = validate_registry(load_registry(root), checkpoint="C")
    assert "OVERCLAIM_RESIDUAL" not in report_codes(report_b)
    assert "OVERCLAIM_RESIDUAL" in codes(report_c, "blocking")


def test_negative_site_requires_complete_power_basis_and_prohibits_rule_out(
    tmp_path,
):
    site = assertion_site(
        "negative-site",
        assertion_type="negative",
        declared_tier=None,
    )
    report = write_assertion_registry(
        tmp_path,
        [site],
        "<!-- negative-site --> We rule out an effect on retention.\n",
    )
    assert "NEGATIVE_POWER_BASIS_REQUIRED" in codes(report, "blocking")
    assert "NEGATIVE_RULE_OUT_UNSUPPORTED" in codes(report, "blocking")


def test_complete_negative_power_basis_licenses_exclusion_wording(tmp_path):
    site = assertion_site(
        "powered-negative-site",
        assertion_type="negative",
        declared_tier=None,
        power_basis={
            "test": "equivalence_test",
            "sample_size": 1000,
            "minimum_detectable_effect": 0.03,
        },
    )
    report = write_assertion_registry(
        tmp_path,
        [site],
        "<!-- powered-negative-site --> We rule out an effect larger than three percentage points.\n",
    )
    assert "NEGATIVE_POWER_BASIS_REQUIRED" not in report_codes(report)
    assert "NEGATIVE_RULE_OUT_UNSUPPORTED" not in report_codes(report)


@pytest.mark.parametrize(
    ("as_modeled", "has_sampling_distribution", "expected_code"),
    [
        (None, False, "MODEL_INTERNAL_AS_MODELED_REQUIRED"),
        (True, False, "MODEL_INTERNAL_SIGNIFICANT_UNSUPPORTED"),
    ],
)
def test_model_internal_sites_require_model_marker_and_sampling_distribution(
    tmp_path, as_modeled, has_sampling_distribution, expected_code
):
    site = assertion_site(
        "model-site",
        assertion_type="model_internal",
        declared_tier=None,
        as_modeled=as_modeled,
        has_sampling_distribution=has_sampling_distribution,
        significant_at=None,
    )
    report = write_assertion_registry(
        tmp_path,
        [site],
        "<!-- model-site --> As modeled, the simulated effect is significant.\n",
    )
    assert expected_code in codes(report, "blocking")


def test_world_positive_and_negative_residuals_follow_derived_evidence_strength(
    tmp_path,
):
    registry = base_registry()
    registry["claims"]["claims"][0]["assessment"] = "challenged"
    registry["evidence_relations"]["evidence_relations"].append(
        {
            "relation_id": "ER-bound",
            "evidence_card_id": "EC-1",
            "claim_revision_id": "H1.r1",
            "relation": "bounds",
            "status": "current",
            "author": "analyst",
            "date": "2026-02-02",
            "rationale": "The diagnostic materially bounds the claim.",
        }
    )
    positive = assertion_site("positive-residual")
    report = write_assertion_registry(
        tmp_path / "positive",
        [positive],
        "<!-- positive-residual --> The intervention causes retention to increase.\n",
        registry,
    )
    finding = next(
        item for item in report["blocking"] if item["code"] == "OVERCLAIM_RESIDUAL"
    )
    assert finding["residual"] > 0

    negative = assertion_site(
        "negative-residual", declared_tier="T3", significant_at=0.01
    )
    report = write_assertion_registry(
        tmp_path / "negative",
        [negative],
        "<!-- negative-residual --> Retention is associated with treatment.\n",
    )
    finding = next(
        item for item in report["reports"] if item["code"] == "UNDERCLAIM_RESIDUAL"
    )
    assert finding["residual"] < 0


@pytest.mark.parametrize(
    ("mutate", "expected_strength", "expected_basis"),
    [
        (
            lambda registry, site: registry["evidence_cards"]["evidence_cards"][0].__setitem__(
                "provenance", "exploratory"
            ),
            0,
            "no_live_confirmatory_support",
        ),
        (
            lambda registry, site: registry["gates"]["gate_evaluations"][0].__setitem__(
                "status", "triggered"
            ),
            0,
            "applicable_gate_unresolved",
        ),
        (
            lambda registry, site: site["underlying_precision"].__setitem__(
                "significant_at", None
            ),
            1,
            "sampling_precision_not_significant",
        ),
    ],
    ids=["provenance", "gate", "precision"],
)
def test_evidence_strength_uses_provenance_gate_and_site_precision(
    tmp_path, mutate, expected_strength, expected_basis
):
    registry = base_registry()
    site = assertion_site("evidence-input-site")
    mutate(registry, site)
    report = write_assertion_registry(
        tmp_path,
        [site],
        "<!-- evidence-input-site --> Treatment causes retention.\n",
        registry,
    )
    finding = next(
        item for item in report["blocking"] if item["code"] == "OVERCLAIM_RESIDUAL"
    )
    assert finding["evidence_strength"] == expected_strength
    assert expected_basis in finding["evidence_basis"]


@pytest.mark.parametrize(
    ("estimate_id", "card_mutation"),
    [
        ("NOT-A-CARD", lambda registry: None),
        (
            "EC-1",
            lambda registry: registry["evidence_cards"]["evidence_cards"][0].__setitem__(
                "status", "stale"
            ),
        ),
        (
            "EC-1#estimate",
            lambda registry: registry["evidence_cards"]["evidence_cards"][0].__setitem__(
                "pipeline_id", "p2"
            )
            or registry["pipelines"]["pipelines"].append(
                {
                    "pipeline_id": "p2",
                    "status": "current",
                    "first_formal_batch_at": "2026-01-01T00:00:00Z",
                }
            ),
        ),
    ],
    ids=["unknown", "stale", "wrong-pipeline"],
)
def test_every_non_null_estimate_id_resolves_to_current_same_pipeline_evidence(
    tmp_path, estimate_id, card_mutation
):
    registry = base_registry()
    card_mutation(registry)
    site = assertion_site("precision-reference", estimate_id=estimate_id)
    report = write_assertion_registry(
        tmp_path,
        [site],
        "<!-- precision-reference --> Treatment causes retention.\n",
        registry,
    )
    assert "UNDERLYING_PRECISION_REFERENCE_INVALID" in codes(report, "blocking")
    site_state = report["state"]["claims"]["H1.r1"]["assertion_sites"][0]
    assert site_state["_evidence_strength"] == 0


def test_evidence_strength_uses_gate_status_derived_from_incomplete_coverage(
    tmp_path,
):
    registry = base_registry()
    registry["gates"]["gate_evaluations"][0]["coverage"]["complete"] = False
    site = assertion_site("effective-gate-site")
    report = write_assertion_registry(
        tmp_path,
        [site],
        "<!-- effective-gate-site --> Treatment causes retention.\n",
        registry,
    )
    finding = next(
        item for item in report["blocking"] if item["code"] == "OVERCLAIM_RESIDUAL"
    )
    assert finding["evidence_strength"] == 0
    assert "applicable_gate_unresolved" in finding["evidence_basis"]
    effective = report["state"]["gate_evaluations"]["G-1@p1"]
    assert effective["_declared_status"] == "passed"
    assert effective["effective_status"] == "not_evaluated"


def test_narrowing_must_propagate_strength_and_scope_to_high_visibility_sites(
    tmp_path,
):
    registry = base_registry()
    registry["claims"]["claims"][0]["revision_reason"] = "bounded_by_population"
    sites = [
        assertion_site(
            "bounded-result", declared_tier="T1", section_role="results"
        ),
        assertion_site(
            "unbounded-abstract", declared_tier="T0", section_role="abstract"
        ),
    ]
    report = write_assertion_registry(
        tmp_path,
        sites,
        "<!-- bounded-result --> Among urban firms, the intervention increases retention.\n"
        "<!-- unbounded-abstract --> The intervention increases retention.\n",
        registry,
    )
    assert "NARROWING_NOT_PROPAGATED" in codes(report, "blocking")


def test_identifying_assumption_counterevidence_must_be_a_main_text_sentence(
    tmp_path,
):
    registry = base_registry()
    registry["evidence_relations"]["evidence_relations"].append(
        {
            "relation_id": "ER-identification-bound",
            "evidence_card_id": "EC-1",
            "claim_revision_id": "H1.r1",
            "relation": "bounds",
            "status": "current",
            "author": "analyst",
            "date": "2026-02-02",
            "rationale": "The diagnostic bears on the identifying assumption.",
            "bears_on": "identifying_assumption",
        }
    )
    site = assertion_site(
        "buried-counterevidence",
        declared_tier="T2",
        counterevidence_prominence="clause_appended",
    )
    report = write_assertion_registry(
        tmp_path,
        [site],
        "<!-- buried-counterevidence --> Treatment increases retention, although pre-trends are imprecise.\n",
        registry,
    )
    assert "COUNTEREVIDENCE_BURIED" in codes(report, "blocking")


def test_identifying_counterevidence_declaration_must_match_contrastive_text(
    tmp_path,
):
    registry = base_registry()
    registry["evidence_relations"]["evidence_relations"].append(
        {
            "relation_id": "ER-identification-bound",
            "evidence_card_id": "EC-1",
            "claim_revision_id": "H1.r1",
            "relation": "bounds",
            "status": "current",
            "author": "analyst",
            "date": "2026-02-02",
            "rationale": "The diagnostic bears on the identifying assumption.",
            "identifying_assumption": True,
        }
    )
    site = assertion_site(
        "contrastive-counterevidence",
        declared_tier="T2",
        counterevidence_prominence="separate_contrastive_sentence",
    )
    report = write_assertion_registry(
        tmp_path,
        [site],
        "<!-- contrastive-counterevidence --> Treatment increases retention. "
        "However, differential pre-trends weaken the identifying assumption.\n",
        registry,
    )
    assert "COUNTEREVIDENCE_BURIED" not in report_codes(report)


def test_prominence_metadata_without_counterevidence_text_cannot_lower_strength(
    tmp_path,
):
    registry = base_registry()
    registry["evidence_relations"]["evidence_relations"].append(
        {
            "relation_id": "ER-ordinary-bound",
            "evidence_card_id": "EC-1",
            "claim_revision_id": "H1.r1",
            "relation": "bounds",
            "status": "current",
            "author": "analyst",
            "date": "2026-02-02",
            "rationale": "A subgroup diagnostic materially bounds the claim.",
        }
    )
    site = assertion_site(
        "false-parenthetical",
        declared_tier="T2",
        counterevidence_prominence="parenthetical",
    )
    report = write_assertion_registry(
        tmp_path,
        [site],
        "<!-- false-parenthetical --> Treatment causes retention.\n",
        registry,
    )
    assert "COUNTEREVIDENCE_PROMINENCE_UNCORROBORATED" in codes(
        report, "blocking"
    )
    finding = next(
        item for item in report["blocking"] if item["code"] == "OVERCLAIM_RESIDUAL"
    )
    assert finding["lexical_tier"] == "T0"


def test_resolved_site_disclosure_can_corroborate_prominence(tmp_path):
    registry = base_registry()
    registry["evidence_relations"]["evidence_relations"].append(
        {
            "relation_id": "ER-ordinary-bound",
            "evidence_card_id": "EC-1",
            "claim_revision_id": "H1.r1",
            "relation": "bounds",
            "status": "current",
            "author": "analyst",
            "date": "2026-02-02",
            "rationale": "A subgroup diagnostic materially bounds the claim.",
        }
    )
    site = assertion_site(
        "referenced-disclosure-site",
        declared_tier="T2",
        counterevidence_prominence="separate_contrastive_sentence",
        counterevidence_disclosure={
            "path": "paper/assertions.md",
            "anchor": "counterevidence-sentence",
        },
    )
    report = write_assertion_registry(
        tmp_path,
        [site],
        "<!-- referenced-disclosure-site --> Treatment increases retention.\n"
        "<!-- counterevidence-sentence --> However, subgroup estimates are imprecise.\n",
        registry,
    )
    assert "COUNTEREVIDENCE_PROMINENCE_UNCORROBORATED" not in report_codes(report)
    assert "OVERCLAIM_RESIDUAL" not in report_codes(report)


def test_immediate_recovery_is_reporting_only(tmp_path):
    site = assertion_site("recovery-site", declared_tier="T0")
    report = write_assertion_registry(
        tmp_path,
        [site],
        "<!-- recovery-site --> Although pre-trends are imprecise, the estimate is stable. "
        "However, the intervention causes retention to increase.\n",
    )
    finding = next(
        item for item in report["reports"] if item["code"] == "IMMEDIATE_RECOVERY"
    )
    assert finding["level"] == "WARN"
    assert "IMMEDIATE_RECOVERY" not in codes(report, "blocking")


def test_abstract_upgrade_without_trace_warns_but_does_not_block(tmp_path):
    sites = [
        assertion_site("result-site", declared_tier="T3", section_role="results"),
        assertion_site(
            "abstract-site",
            declared_tier="T1",
            section_role="abstract",
        ),
    ]
    report = write_assertion_registry(
        tmp_path,
        sites,
        "<!-- result-site --> Retention is associated with treatment.\n"
        "<!-- abstract-site --> Among urban firms, treatment increases retention.\n",
    )
    finding = next(
        item for item in report["reports"] if item["code"] == "UPGRADE_TRACE_MISSING"
    )
    assert finding["level"] == "WARN"
    assert "UPGRADE_TRACE_MISSING" not in codes(report, "blocking")


def test_title_upgrade_with_complete_trace_has_no_upgrade_warning(tmp_path):
    site_reference = "paper/assertions.md#result-site"
    sites = [
        assertion_site("result-site", declared_tier="T3", section_role="results"),
        assertion_site(
            "title-site",
            declared_tier="T1",
            section_role="title",
            upgrade_justification={
                "results_site": site_reference,
                "rationale": "The title states the estimand within the registered population.",
                "evidence_card": "EC-1",
                "recorded_by": "lead_author",
                "recorded_at": "2026-08-15T20:00:00Z",
            },
        ),
    ]
    report = write_assertion_registry(
        tmp_path,
        sites,
        "<!-- result-site --> Retention is associated with treatment.\n"
        "<!-- title-site --> Treatment increases retention among urban firms.\n",
    )
    assert "UPGRADE_TRACE_MISSING" not in report_codes(report)


def test_incomplete_upgrade_trace_remains_warning_only(tmp_path):
    sites = [
        assertion_site("result-site", declared_tier="T3", section_role="results"),
        assertion_site(
            "title-site",
            declared_tier="T1",
            section_role="title",
            upgrade_justification={},
        ),
    ]
    report = write_assertion_registry(
        tmp_path,
        sites,
        "<!-- result-site --> Retention is associated with treatment.\n"
        "<!-- title-site --> Among urban firms, treatment increases retention.\n",
    )
    finding = next(
        item for item in report["reports"] if item["code"] == "UPGRADE_TRACE_MISSING"
    )
    assert finding["trace_status"] == "invalid"
    assert "SCHEMA_INVALID" not in report_codes(report)
    assert "UPGRADE_TRACE_MISSING" not in codes(report, "blocking")


@pytest.mark.parametrize("assertion_type", ["methodological", "hypothesis"])
def test_non_empirical_untiered_sites_are_excluded_from_residuals(
    tmp_path, assertion_type
):
    site = assertion_site(
        "untiered-site", assertion_type=assertion_type, declared_tier=None
    )
    site.pop("upgrade_justification")
    report = write_assertion_registry(
        tmp_path,
        [site],
        "<!-- untiered-site --> Estimating a static model causes biased elasticities.\n",
    )
    assert "OVERCLAIM_RESIDUAL" not in report_codes(report)
    assert "UNDERCLAIM_RESIDUAL" not in report_codes(report)


def test_specific_one_word_discriminating_alternative_is_accepted(tmp_path):
    site = assertion_site(
        "seasonality-site",
        assertion_type="discriminating",
        declared_tier=None,
        alternative_explanation="seasonality",
    )
    report = write_assertion_registry(
        tmp_path,
        [site],
        "<!-- seasonality-site --> The timing is difficult to reconcile with seasonality.\n",
    )
    assert "DISCRIMINATING_ALTERNATIVE_REQUIRED" not in report_codes(report)


@pytest.mark.parametrize(
    ("assertion_type", "conditional"),
    [
        (
            "negative",
            {
                "power_basis": {
                    "test": "equivalence_test",
                    "sample_size": 1000,
                    "minimum_detectable_effect": 0.03,
                }
            },
        ),
        ("methodological", {}),
        (
            "discriminating",
            {"alternative_explanation": "differential pre-trend selection"},
        ),
        ("model_internal", {"as_modeled": True}),
    ],
)
def test_identifying_prominence_check_covers_all_empirical_untiered_types(
    tmp_path, assertion_type, conditional
):
    registry = base_registry()
    registry["evidence_relations"]["evidence_relations"].append(
        {
            "relation_id": "ER-identification-bound",
            "evidence_card_id": "EC-1",
            "claim_revision_id": "H1.r1",
            "relation": "bounds",
            "status": "current",
            "author": "analyst",
            "date": "2026-02-02",
            "rationale": "This diagnostic bears on the identifying assumption.",
        }
    )
    site = assertion_site(
        "untiered-identification-site",
        assertion_type=assertion_type,
        declared_tier=None,
        counterevidence_prominence="clause_appended",
        **conditional,
    )
    report = write_assertion_registry(
        tmp_path,
        [site],
        "<!-- untiered-identification-site --> The diagnostic supports the account, "
        "although differential pre-trends remain imprecise.\n",
        registry,
    )
    assert "COUNTEREVIDENCE_BURIED" in codes(report, "blocking")
    assert "OVERCLAIM_RESIDUAL" not in report_codes(report)
    assert "UNDERCLAIM_RESIDUAL" not in report_codes(report)


def test_identifying_prominence_scope_excludes_hypotheses_awaiting_test(tmp_path):
    registry = base_registry()
    registry["evidence_relations"]["evidence_relations"].append(
        {
            "relation_id": "ER-identification-bound",
            "evidence_card_id": "EC-1",
            "claim_revision_id": "H1.r1",
            "relation": "bounds",
            "status": "current",
            "author": "analyst",
            "date": "2026-02-02",
            "rationale": "This diagnostic bears on the identifying assumption.",
        }
    )
    site = assertion_site(
        "hypothesis-identification-site",
        assertion_type="hypothesis",
        declared_tier=None,
        counterevidence_prominence="clause_appended",
    )
    report = write_assertion_registry(
        tmp_path,
        [site],
        "<!-- hypothesis-identification-site --> We hypothesize a retention effect, "
        "although differential pre-trends may be imprecise.\n",
        registry,
    )
    assert "COUNTEREVIDENCE_BURIED" not in report_codes(report)


def test_lexical_scan_is_limited_to_registered_sites(tmp_path):
    site = assertion_site("registered-description", declared_tier="T4")
    report = write_assertion_registry(
        tmp_path,
        [site],
        "The unregistered literature review claims treatment causes every outcome.\n"
        "<!-- registered-description --> We report the observed retention rate.\n",
    )
    assert "OVERCLAIM_RESIDUAL" not in report_codes(report)


@pytest.mark.parametrize(
    ("lexical_class", "marker", "text"),
    [
        ("causal", "supercharges", "Treatment supercharges retention."),
        ("scope_qualifying", "inside metro firms", "Treatment increases retention inside metro firms."),
        ("associational", "co-moves with", "Retention co-moves with treatment."),
        ("descriptive", "enumerates", "The table enumerates retention rates."),
        ("framing", "granting that", "Granting that precision is limited, the estimate remains stable."),
    ],
)
def test_project_can_extend_each_registered_site_lexical_class(
    tmp_path, lexical_class, marker, text
):
    registry = base_registry()
    registry["claims"]["writing_strength"] = {
        "lexical_markers": {lexical_class: [marker]}
    }
    site = assertion_site("custom-marker", declared_tier="T0")
    report = write_assertion_registry(
        tmp_path,
        [site],
        f"<!-- custom-marker --> {text}\n",
        registry,
    )
    site_state = report["state"]["claims"]["H1.r1"]["assertion_sites"][0]
    assert marker in site_state["_matched_lexical_classes"][lexical_class]


@pytest.mark.parametrize(
    "causal_configuration",
    [
        {"replace": []},
        {"remove": ["causes"]},
    ],
    ids=["empty-replacement", "default-removal"],
)
def test_project_configuration_cannot_erase_baseline_causal_enforcement(
    tmp_path, causal_configuration
):
    registry = base_registry()
    registry["claims"]["writing_strength"] = {
        "lexical_markers": {"causal": causal_configuration}
    }
    site = assertion_site(
        "protected-causal", declared_tier="T0", has_sampling_distribution=False
    )
    report = write_assertion_registry(
        tmp_path,
        [site],
        "<!-- protected-causal --> Treatment causes retention.\n",
        registry,
    )
    assert "OVERCLAIM_RESIDUAL" in codes(report, "blocking")
    site_state = report["state"]["claims"]["H1.r1"]["assertion_sites"][0]
    assert "causes" in site_state["_matched_lexical_classes"]["causal"]


@pytest.mark.parametrize(
    ("anchor", "source"),
    [
        ("missing-anchor", "No registered marker is present.\n"),
        ("duplicate-anchor", "duplicate-anchor\nduplicate-anchor\n"),
    ],
    ids=["missing", "ambiguous"],
)
def test_assertion_site_anchor_must_resolve_unambiguously(tmp_path, anchor, source):
    report = write_assertion_registry(
        tmp_path,
        [assertion_site(anchor, declared_tier="T4")],
        source,
    )
    assert "ASSERTION_ANCHOR_INVALID" in codes(report, "blocking")


@pytest.mark.parametrize(
    "mutate",
    [
        lambda site: site.__setitem__("assertion_type", "anecdote"),
        lambda site: site.__setitem__("declared_tier", None),
        lambda site: site["underlying_precision"].pop("estimate_id"),
        lambda site: site.__setitem__("qualifier_scope", "section"),
    ],
    ids=["type", "world-tier", "precision", "scope-declaration"],
)
def test_assertion_site_declarations_have_an_executable_schema(tmp_path, mutate):
    site = assertion_site("typed-site")
    mutate(site)
    report = write_assertion_registry(
        tmp_path,
        [site],
        "<!-- typed-site --> Treatment causes retention.\n",
    )
    assert "SCHEMA_INVALID" in codes(report, "blocking")


def test_untiered_types_reject_world_tiers_and_generic_alternatives(tmp_path):
    site = assertion_site(
        "generic-alternative",
        assertion_type="discriminating",
        declared_tier="T3",
        alternative_explanation="selection",
    )
    report = write_assertion_registry(
        tmp_path,
        [site],
        "<!-- generic-alternative --> The pattern differs from selection.\n",
    )
    assert "UNTIERED_ASSERTION_TIERED" in codes(report, "blocking")
    assert "DISCRIMINATING_ALTERNATIVE_REQUIRED" in codes(report, "blocking")


def test_line_range_anchor_reads_only_the_registered_lines(tmp_path):
    site = assertion_site("L2-L2", declared_tier="T4")
    report = write_assertion_registry(
        tmp_path,
        [site],
        "Treatment causes every outcome.\nWe report the observed retention rate.\n",
    )
    assert "ASSERTION_ANCHOR_INVALID" not in report_codes(report)
    assert "OVERCLAIM_RESIDUAL" not in report_codes(report)


def test_assertion_source_path_cannot_escape_the_registry(tmp_path):
    site = assertion_site("external-anchor", declared_tier="T4")
    site["path"] = str(Path(__file__).resolve())
    report = write_assertion_registry(
        tmp_path,
        [site],
        "<!-- external-anchor --> We report the observed rate.\n",
    )
    assert "ASSERTION_SOURCE_INVALID" in codes(report, "blocking")


def test_registered_paragraph_scope_must_bound_the_site_and_qualify_its_tier(
    tmp_path,
):
    registry = base_registry()
    registry["claims"]["claims"][0]["revision_reason"] = "bounded_by_population"
    site = assertion_site(
        "bounded-site",
        section_role="abstract",
        declared_tier="T1",
        qualifier_scope="paragraph",
        scope_declaration={
            "path": "paper/assertions.md",
            "anchor": "scope-statement",
            "coverage": {
                "path": "paper/assertions.md",
                "start_anchor": "coverage-start",
                "end_anchor": "coverage-end",
            },
        },
    )
    report = write_assertion_registry(
        tmp_path,
        [site],
        "<!-- scope-statement --> Among participating firms, the following claim applies.\n"
        "<!-- coverage-start -->\n"
        "<!-- bounded-site --> Treatment increases retention.\n"
        "<!-- coverage-end -->\n",
        registry,
    )
    assert "SCOPE_DECLARATION_INVALID" not in report_codes(report)
    assert "OVERCLAIM_RESIDUAL" not in report_codes(report)
    assert "NARROWING_NOT_PROPAGATED" not in report_codes(report)


def test_scope_declaration_outside_coverage_does_not_qualify_the_site(tmp_path):
    site = assertion_site(
        "outside-site",
        declared_tier="T1",
        qualifier_scope="paragraph",
        scope_declaration={
            "path": "paper/assertions.md",
            "anchor": "scope-statement",
            "coverage": {
                "path": "paper/assertions.md",
                "start_anchor": "coverage-start",
                "end_anchor": "coverage-end",
            },
        },
    )
    report = write_assertion_registry(
        tmp_path,
        [site],
        "<!-- scope-statement --> Among participating firms, the following claim applies.\n"
        "<!-- coverage-start -->\n"
        "<!-- coverage-end -->\n"
        "<!-- outside-site --> Treatment increases retention.\n",
    )
    assert "SCOPE_DECLARATION_INVALID" in codes(report, "blocking")


def test_sentence_scope_does_not_leak_to_a_neighboring_causal_sentence(tmp_path):
    registry = base_registry()
    registry["claims"]["claims"][0]["revision_reason"] = "bounded_by_population"
    site = assertion_site(
        "neighboring-sentence",
        section_role="abstract",
        declared_tier="T1",
    )
    report = write_assertion_registry(
        tmp_path,
        [site],
        "<!-- neighboring-sentence --> Among urban firms, data were collected. "
        "Treatment increases retention.\n",
        registry,
    )
    assert "OVERCLAIM_RESIDUAL" in codes(report, "blocking")
    assert "NARROWING_NOT_PROPAGATED" in codes(report, "blocking")


def test_closed_scope_must_contain_the_full_line_range_site(tmp_path):
    registry = base_registry()
    registry["claims"]["claims"][0]["revision_reason"] = "bounded_by_population"
    site = assertion_site(
        "L2-L4",
        section_role="abstract",
        declared_tier="T1",
        qualifier_scope="paragraph",
        scope_declaration={
            "path": "paper/assertions.md",
            "anchor": "scope-statement",
            "coverage": {
                "path": "paper/assertions.md",
                "start_anchor": "coverage-start",
                "end_anchor": "coverage-end",
            },
        },
    )
    report = write_assertion_registry(
        tmp_path,
        [site],
        "<!-- scope-statement --> Among urban firms, the following claim applies.\n"
        "<!-- coverage-start --><!-- coverage-end --> Treatment increases retention.\n"
        "Treatment increases output.\n"
        "Treatment increases sales.\n",
        registry,
    )
    assert "SCOPE_DECLARATION_INVALID" in codes(report, "blocking")
    assert "NARROWING_NOT_PROPAGATED" in codes(report, "blocking")


def test_duplicate_assertion_site_for_one_claim_is_rejected(tmp_path):
    site = assertion_site("duplicate-site", declared_tier="T4")
    report = write_assertion_registry(
        tmp_path,
        [site, copy.deepcopy(site)],
        "<!-- duplicate-site --> We report the observed retention rate.\n",
    )
    assert "DUPLICATE_ASSERTION_SITE" in codes(report, "blocking")


def test_malformed_assertion_scalar_types_return_schema_errors(tmp_path):
    site = assertion_site("malformed-site")
    site["assertion_type"] = {"not": "a scalar"}
    report = write_assertion_registry(
        tmp_path,
        [site],
        "<!-- malformed-site --> Treatment causes retention.\n",
    )
    assert "SCHEMA_INVALID" in codes(report, "blocking")


def test_world_overclaim_and_model_internal_simulation_are_separate_failures(
    tmp_path,
):
    """A narrowed world claim asserted unqualified is an overclaim residual.

    A model-internal simulation that borrows the word ``significant`` is a
    different failure with a different remedy. The two paths must not be
    reachable through one another: a residual block must not depend on a
    missing sampling distribution, and a model-internal block must not be
    laundered into a residual.
    """

    world = base_registry()
    world["claims"]["claims"][0]["revision_reason"] = "bounded_by_sensitivity"
    world_report = write_assertion_registry(
        tmp_path / "world",
        [
            assertion_site(
                "unqualified-world-claim",
                section_role="results",
                declared_tier="T0",
            )
        ],
        "<!-- unqualified-world-claim --> The intervention causes retention "
        "to increase.\n",
        world,
    )
    world_blocking = codes(world_report, "blocking")
    assert "OVERCLAIM_RESIDUAL" in world_blocking
    assert "MODEL_INTERNAL_SIGNIFICANT_UNSUPPORTED" not in world_blocking
    residual = next(
        item
        for item in world_report["blocking"]
        if item["code"] == "OVERCLAIM_RESIDUAL"
    )
    assert residual["lexical_strength"] == 4
    assert residual["evidence_strength"] == 3
    assert "bounded_by_sensitivity" in residual["evidence_basis"]
    assert "no_sampling_distribution" not in residual["evidence_basis"]

    model_internal = base_registry()
    site = assertion_site(
        "counterfactual-gain",
        section_role="results",
        declared_tier=None,
    )
    site["assertion_type"] = "model_internal"
    site["as_modeled"] = True
    site["underlying_precision"] = {
        "estimate_id": None,
        "significant_at": None,
        "has_sampling_distribution": False,
        "n": None,
    }
    model_report = write_assertion_registry(
        tmp_path / "model",
        [site],
        "<!-- counterfactual-gain --> As we model, the subsidy has a "
        "significant effect on the simulated net gain.\n",
        model_internal,
    )
    model_blocking = codes(model_report, "blocking")
    assert "MODEL_INTERNAL_SIGNIFICANT_UNSUPPORTED" in model_blocking
    assert "OVERCLAIM_RESIDUAL" not in model_blocking
    assert "UNDERCLAIM_RESIDUAL" not in codes(model_report, "reports")


LATEX_SOURCE = """\\documentclass{article}
\\usepackage{claimsite}
\\TITLE{Treatment increases retention}
\\begin{abstract}
\\claimsite{abstract-retention}Treatment increases retention for participating firms.
\\end{abstract}
\\section{Results}
\\claimsite{result-retention}Treatment increases retention for participating firms. % however, this comment must not count
\\claimsite{numeric-retention}Retention rises by 7.68\\% for participating firms.
"""


def _latex_registry(tmp_path, sites, registry=None, source=LATEX_SOURCE):
    registry = copy.deepcopy(registry or base_registry())
    registry["claims"]["claims"][0]["assertion_sites"] = sites
    root = write_registry(tmp_path, registry)
    paper = root / "paper"
    paper.mkdir(exist_ok=True)
    (paper / "manuscript.tex").write_text(source, encoding="utf-8")
    return validate_registry(load_registry(root), checkpoint="C")


def _tex_site(anchor, section_role, **overrides):
    site = assertion_site(anchor, section_role=section_role, declared_tier="T1")
    site["path"] = "paper/manuscript.tex"
    site.update(overrides)
    return site


def test_latex_section_role_is_resolved_from_the_source_not_self_declared(
    tmp_path,
):
    report = _latex_registry(
        tmp_path / "role",
        [_tex_site("abstract-retention", "results")],
    )
    mismatches = [
        item
        for item in report["blocking"]
        if item["code"] == "SECTION_ROLE_MISMATCH"
    ]
    assert mismatches
    assert mismatches[0]["declared_section_role"] == "results"
    assert mismatches[0]["resolved_section_role"] == "abstract"


def test_latex_comment_cannot_supply_a_counterevidence_cue(tmp_path):
    site = _tex_site(
        "result-retention",
        "results",
        counterevidence_prominence="separate_contrastive_sentence",
    )
    report = _latex_registry(tmp_path / "comment", [site])
    assert "COUNTEREVIDENCE_PROMINENCE_UNCORROBORATED" in codes(
        report, "blocking"
    )


def test_quantitative_value_typed_into_latex_is_rejected(tmp_path):
    report = _latex_registry(
        tmp_path / "numeral",
        [_tex_site("numeric-retention", "results")],
    )
    literals = [
        item
        for item in report["blocking"]
        if item["code"] == "QUANTITATIVE_VALUE_NOT_REGISTERED"
    ]
    assert literals
    assert literals[0]["literals"] == ["7.68"]


def test_registered_figure_macro_is_not_a_bare_numeral(tmp_path):
    report = _latex_registry(
        tmp_path / "macro",
        [_tex_site("macro-retention", "results")],
        source=(
            "\\section{Results}\n"
            "\\claimsite{macro-retention}Retention rises by "
            "\\figval{retention_pp} for participating firms.\n"
        ),
    )
    assert "QUANTITATIVE_VALUE_NOT_REGISTERED" not in codes(report, "blocking")


def test_stale_reported_figure_is_withheld_from_the_latex_macro_file(tmp_path):
    """A retired value must fail the build, not reach the PDF."""

    from tools.render_figure_macros import render

    fixtures = Path(__file__).resolve().parents[1] / "tests/smoke/registry-fixtures"
    body, withheld = render(fixtures / "pipeline-stale")
    assert withheld == ["RF-1"]
    assert "\\defineFigureValue{RF-1}" not in body

    live = write_registry(tmp_path / "live")
    body, withheld = render(live)
    assert not withheld
    assert "\\defineFigureValue{RF-1}{2.0}" in body
