#!/usr/bin/env python3
"""Validate claim, pipeline, gate, applicability, and publication invariants."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


BLOCKING_GATE_STATUSES = {"triggered", "not_evaluated"}


def parse_time(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if not isinstance(value, str) or not value.strip():
        raise ValueError("missing timestamp")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def indexed(records: list[dict[str, Any]], key: str, errors: list[str]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        value = record.get(key)
        if not value:
            errors.append(f"record missing {key}")
        elif value in result:
            errors.append(f"duplicate {key}: {value}")
        else:
            result[value] = record
    return result


def validate_registry(registry: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    pipelines = indexed(registry.get("pipelines", []), "pipeline_id", errors)
    claims = indexed(registry.get("claims", []), "claim_revision_id", errors)
    figures = indexed(registry.get("reported_figures", []), "figure_id", errors)
    gates = indexed(registry.get("gate_definitions", []), "gate_id", errors)
    applicability = indexed(registry.get("applicability_records", []), "requirement_id", errors)
    outputs = indexed(registry.get("outputs", []), "output_id", errors)

    authoritative = [p for p in pipelines.values() if p.get("status") == "authoritative"]
    if len(authoritative) != 1:
        errors.append(f"expected one authoritative pipeline, found {len(authoritative)}")

    post_hoc: dict[str, bool] = {}
    for evaluation in registry.get("gate_evaluations", []):
        gate_id = evaluation.get("gate_id")
        pipeline_id = evaluation.get("pipeline_id")
        label = f"{gate_id}@{pipeline_id}"
        definition = gates.get(gate_id)
        pipeline = pipelines.get(pipeline_id)
        if definition is None:
            errors.append(f"gate evaluation {label} has no definition")
            continue
        if pipeline is None:
            errors.append(f"gate evaluation {label} has no pipeline")
            continue
        try:
            post_hoc[label] = parse_time(definition.get("declared_at")) > parse_time(
                pipeline.get("first_formal_batch_at")
            )
        except ValueError as exc:
            errors.append(f"gate evaluation {label}: {exc}")
            continue

        status = evaluation.get("status")
        coverage = evaluation.get("coverage", {})
        if status in BLOCKING_GATE_STATUSES or not coverage.get("complete", False):
            errors.append(f"unresolved gate {label}: status={status}, coverage_complete={coverage.get('complete')}")
        elif status == "satisfied":
            for field in ("compensation_artifact", "accepted_by", "accepted_at"):
                if not evaluation.get(field):
                    errors.append(f"satisfied gate {label} missing {field}")
        elif status == "released":
            for field in ("reason", "authorized_by", "authorized_at", "result_timing"):
                if not evaluation.get(field):
                    errors.append(f"released gate {label} missing {field}")
        elif status == "inapplicable":
            for field in ("applicability_reason", "declared_by", "accepted_by"):
                if not evaluation.get(field):
                    errors.append(f"inapplicable gate {label} missing {field}")

    for requirement_id, record in applicability.items():
        status = record.get("status")
        if status in {"pending", "blocked"}:
            errors.append(f"applicability requirement {requirement_id} is {status}")
        if status == "inapplicable":
            for field in ("reason", "declared_by", "accepted_by", "substituted_by"):
                if not record.get(field):
                    errors.append(f"inapplicable requirement {requirement_id} missing {field}")
            for substitute_id in record.get("substituted_by", []):
                substitute = applicability.get(substitute_id)
                if substitute is None or substitute.get("status") != "completed":
                    errors.append(
                        f"inapplicable requirement {requirement_id} substitute {substitute_id} is not completed"
                    )

    publication = registry.get("publication", {})
    output_id = publication.get("output_id")
    output = outputs.get(output_id)
    if output is None:
        errors.append(f"publication output not found: {output_id}")
    else:
        output_pipelines = set(output.get("pipeline_ids", []))
        reconciliation = output.get("reconciliation", {})
        historical_claims = set(reconciliation.get("historical_claim_revisions", []))
        is_reconciliation = output.get("cross_pipeline") == "reconciliation"
        if len(output_pipelines) > 1 and not is_reconciliation:
            errors.append(f"output {output_id} mixes pipelines without a reconciliation block")
        if is_reconciliation and output_pipelines != set(reconciliation.get("pipelines", [])):
            errors.append(f"output {output_id} reconciliation pipeline set does not match output")

        for revision_id in output.get("claim_revisions", []):
            claim = claims.get(revision_id)
            if claim is None:
                errors.append(f"output {output_id} references unknown claim {revision_id}")
                continue
            if claim.get("pipeline_id") not in output_pipelines:
                errors.append(f"claim {revision_id} pipeline is absent from output {output_id}")
            historical = is_reconciliation and revision_id in historical_claims
            if not historical and claim.get("availability") != "current":
                errors.append(f"claim {revision_id} is not current")
            assessment = claim.get("assessment")
            if not historical and assessment == "challenged" and not claim.get("adjacent_disclosures"):
                errors.append(f"challenged claim {revision_id} lacks adjacent disclosure")
            elif not historical and assessment not in {"supported", "challenged"}:
                errors.append(f"claim {revision_id} assessment {assessment} is not publishable")

        for figure_id in output.get("reported_figures", []):
            figure = figures.get(figure_id)
            if figure is None:
                errors.append(f"output {output_id} references unknown reported figure {figure_id}")
            elif figure.get("pipeline_id") not in output_pipelines:
                errors.append(f"reported figure {figure_id} pipeline is absent from output {output_id}")

    for revalidation in registry.get("revalidations", []):
        target = revalidation.get("target", {})
        if target.get("kind") not in {"claim_revision", "reported_figure"}:
            errors.append("revalidation target kind must be claim_revision or reported_figure")
        if revalidation.get("method") == "machine" and not revalidation.get("tolerance"):
            errors.append("machine revalidation requires tolerance")
        for field in ("from_pipeline", "to_pipeline", "result", "performed_by", "performed_at", "evidence_card"):
            if not revalidation.get(field):
                errors.append(f"revalidation missing {field}")

    return {
        "eligible": not errors,
        "errors": errors,
        "derived": {
            "post_hoc": post_hoc,
            "claim_availability": {
                revision_id: claim.get("availability") for revision_id, claim in claims.items()
            },
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("registry", type=Path)
    args = parser.parse_args()
    try:
        registry = yaml.safe_load(args.registry.read_text(encoding="utf-8"))
        if not isinstance(registry, dict):
            raise ValueError("registry root must be a mapping")
        report = validate_registry(registry)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        report = {"eligible": False, "errors": [str(exc)], "derived": {}}
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["eligible"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
