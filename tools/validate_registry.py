#!/usr/bin/env python3
"""Validate the human-editable claim-governance registry.

The validator deliberately has no project-specific imports.  Registry YAML is
loaded into a normalized dictionary, checked, and evaluated in the cascade
order defined by the v2.1 governance contract.  It never rewrites source YAML;
derived state is returned in the report under ``state``.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import re
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable

import yaml


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

COLLECTIONS = (
    "pipelines",
    "claims",
    "evidence_cards",
    "evidence_relations",
    "reported_figures",
    "revalidations",
    "outputs",
    "gate_definitions",
    "gate_evaluations",
    "semantic_facts",
    "semantic_equivalence_decisions",
    "derived_fields",
    "applicability",
)

REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    "pipelines": ("pipeline_id", "status", "first_formal_batch_at"),
    "claims": (
        "claim_key",
        "claim_revision_id",
        "pipeline_id",
        "availability",
        "assessment",
    ),
    "evidence_cards": (
        "evidence_card_id",
        "pipeline_id",
        "provenance",
        "status",
    ),
    "evidence_relations": (
        "relation_id",
        "evidence_card_id",
        "claim_revision_id",
        "relation",
        "status",
        "author",
        "date",
        "rationale",
    ),
    "reported_figures": (
        "figure_id",
        "pipeline_id",
        "value",
        "source_artifact",
        "source_locator",
        "paper_locations",
    ),
    "outputs": ("output_id", "kind", "status"),
    "gate_definitions": (
        "gate_id",
        "applies_to",
        "metric",
        "allowed_band",
        "failure_policy",
        "declared_at",
        "declared_by",
        "frozen",
    ),
    "gate_evaluations": (
        "gate_id",
        "pipeline_id",
        "evaluated_against",
        "status",
        "coverage",
        "evidence_card",
    ),
    "semantic_facts": (
        "fact_key",
        "fact_revision_id",
        "field",
        "statement",
        "valid_range",
        "authority",
        "verification",
    ),
    "derived_fields": ("derived_field_id", "fact_key", "status", "depends_on"),
    "applicability": ("requirement_id", "status"),
}

ALLOWED = {
    "pipeline_status": {"current", "superseded", "retired", "withdrawn"},
    "availability": {"current", "superseded", "retired", "withdrawn"},
    "assessment": {"supported", "challenged", "unresolved"},
    "relation": {"supports", "challenges", "bounds"},
    "relation_status": {"current", "withdrawn"},
    "provenance": {"confirmatory", "exploratory"},
    "gate_status": {
        "passed",
        "triggered",
        "satisfied",
        "released",
        "moot",
        "not_evaluated",
        "inapplicable",
    },
    "derived_status": {"verified", "unverified", "defective"},
    "applicability_status": {"completed", "pending", "blocked", "inapplicable"},
}


def _issue(code: str, **details: Any) -> dict[str, Any]:
    return {"code": code, **details}


def load_registry(root: Path) -> dict:
    """Load the ten v2.1 YAML files and retain parse errors for validation."""

    root = Path(root)
    registry: dict[str, Any] = {name: [] for name in COLLECTIONS}
    registry.update(
        {
            "analysis_window": None,
            "used_fields": [],
            "gate_set_confirmation": None,
            "_sources": {},
            "_load_errors": [],
            "_root": str(root),
        }
    )

    for filename in REGISTRY_FILES:
        path = root / filename
        registry["_sources"][filename] = path.exists()
        if not path.exists():
            registry["_load_errors"].append(
                _issue("REGISTRY_FILE_MISSING", file=filename)
            )
            continue
        try:
            document = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as error:
            registry["_load_errors"].append(
                _issue("REGISTRY_YAML_INVALID", file=filename, detail=str(error))
            )
            continue
        if document is None:
            document = {}
        if not isinstance(document, dict):
            registry["_load_errors"].append(
                _issue(
                    "REGISTRY_DOCUMENT_INVALID",
                    file=filename,
                    detail="top level must be a mapping",
                )
            )
            continue
        for key, value in document.items():
            if key in COLLECTIONS:
                if not isinstance(value, list):
                    registry["_load_errors"].append(
                        _issue(
                            "REGISTRY_COLLECTION_INVALID",
                            file=filename,
                            collection=key,
                        )
                    )
                else:
                    registry[key].extend(value)
            elif key in {
                "analysis_window",
                "used_fields",
                "gate_set_confirmation",
            }:
                registry[key] = value
    return registry


def _as_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _as_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    if value is None:
        return None
    text = str(value).replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is not None:
        return parsed.replace(tzinfo=None) - parsed.utcoffset()
    return parsed


def _id_map(items: Iterable[dict], key: str) -> dict[str, dict]:
    return {
        str(item[key]): item
        for item in items
        if isinstance(item, dict) and item.get(key) is not None
    }


def _required_field_checks(registry: dict, blocking: list[dict]) -> None:
    for collection, fields in REQUIRED_FIELDS.items():
        for index, item in enumerate(registry.get(collection, [])):
            if not isinstance(item, dict):
                blocking.append(
                    _issue(
                        "REGISTRY_OBJECT_INVALID",
                        collection=collection,
                        index=index,
                    )
                )
                continue
            for field in fields:
                if field not in item or item[field] is None:
                    blocking.append(
                        _issue(
                            "MISSING_REQUIRED_FIELD",
                            collection=collection,
                            index=index,
                            field=field,
                        )
                    )

    enum_checks = (
        ("pipelines", "status", "pipeline_status"),
        ("claims", "availability", "availability"),
        ("claims", "assessment", "assessment"),
        ("evidence_cards", "provenance", "provenance"),
        ("evidence_relations", "relation", "relation"),
        ("evidence_relations", "status", "relation_status"),
        ("gate_evaluations", "status", "gate_status"),
        ("derived_fields", "status", "derived_status"),
        ("applicability", "status", "applicability_status"),
    )
    for collection, field, allowed_key in enum_checks:
        for item in registry.get(collection, []):
            if isinstance(item, dict) and field in item and item[field] not in ALLOWED[allowed_key]:
                blocking.append(
                    _issue(
                        "INVALID_ENUM_VALUE",
                        collection=collection,
                        id=_object_id(item),
                        field=field,
                        value=item[field],
                    )
                )


def _object_id(item: dict) -> str:
    for key in (
        "claim_revision_id",
        "figure_id",
        "output_id",
        "evidence_card_id",
        "relation_id",
        "gate_id",
        "fact_revision_id",
        "derived_field_id",
        "requirement_id",
        "pipeline_id",
    ):
        if item.get(key) is not None:
            return str(item[key])
    return "unknown"


def _semantic_checks(
    registry: dict, blocking: list[dict], reports: list[dict]
) -> set[str]:
    facts = registry.get("semantic_facts", [])
    corrected_fact_keys = {
        str(fact.get("fact_key"))
        for fact in facts
        if fact.get("revision_reason") == "corrected"
    }
    for fact in facts:
        dependencies = fact.get("verification", {}).get("depends_on", [])
        for dependency in dependencies:
            if not isinstance(dependency, dict) or dependency.get("kind") not in {
                "raw_field",
                "semantic_fact",
            }:
                blocking.append(
                    _issue(
                        "SEMANTIC_BOTTOM_LAYER_VIOLATION",
                        fact_revision_id=fact.get("fact_revision_id"),
                        dependency=dependency,
                    )
                )

    window = registry.get("analysis_window")
    if not isinstance(window, list) or len(window) != 2:
        blocking.append(_issue("ANALYSIS_WINDOW_INVALID"))
        return corrected_fact_keys
    window_start, window_end = (_as_date(window[0]), _as_date(window[1]))
    if window_start is None or window_end is None or window_start > window_end:
        blocking.append(_issue("ANALYSIS_WINDOW_INVALID", value=window))
        return corrected_fact_keys

    equivalence = registry.get("semantic_equivalence_decisions", [])
    equivalent_keys = {
        str(item.get("fact_key") or item.get("field"))
        for item in equivalence
        if item.get("decision") in {"equivalent", "interchangeable"}
        and item.get("decided_by")
        and item.get("decided_at")
    }
    for field in registry.get("used_fields", []):
        intervals: list[tuple[date, date, dict]] = []
        for fact in facts:
            if fact.get("field") != field:
                continue
            valid_range = fact.get("valid_range")
            if not isinstance(valid_range, list) or len(valid_range) != 2:
                blocking.append(
                    _issue(
                        "SEMANTIC_RANGE_INVALID",
                        fact_revision_id=fact.get("fact_revision_id"),
                    )
                )
                continue
            start = _as_date(valid_range[0])
            end = _as_date(valid_range[1]) or window_end
            if start is None or start > end:
                blocking.append(
                    _issue(
                        "SEMANTIC_RANGE_INVALID",
                        fact_revision_id=fact.get("fact_revision_id"),
                    )
                )
                continue
            start, end = max(start, window_start), min(end, window_end)
            if start <= end:
                intervals.append((start, end, fact))
        intervals.sort(key=lambda item: (item[0], item[1]))
        if not intervals or intervals[0][0] > window_start:
            blocking.append(_issue("SEMANTIC_COVERAGE_GAP", field=field))
            continue
        overlap = False
        gap = False
        covered_until = window_start - timedelta(days=1)
        for start, end, _ in intervals:
            if start <= covered_until:
                overlap = True
            elif start > covered_until + timedelta(days=1):
                gap = True
            covered_until = max(covered_until, end)
        if covered_until < window_end:
            gap = True
        if overlap:
            blocking.append(_issue("SEMANTIC_COVERAGE_OVERLAP", field=field))
        if gap:
            blocking.append(_issue("SEMANTIC_COVERAGE_GAP", field=field))
        fact_key = str(intervals[0][2].get("fact_key")) if intervals else ""
        if len(intervals) > 1 and not overlap and not gap and not ({field, fact_key} & equivalent_keys):
            reports.append(
                _issue(
                    "SEMANTIC_DISCLOSURE_REQUIRED",
                    field=field,
                    fact_key=fact_key,
                    revisions=[item[2].get("fact_revision_id") for item in intervals],
                )
            )
    return corrected_fact_keys


def _reference_graph_checks(registry: dict, blocking: list[dict]) -> None:
    graph: dict[str, set[str]] = defaultdict(set)

    def add_node(kind: str, identifier: Any, dependencies: Iterable[Any]) -> None:
        if identifier is None:
            return
        node = f"{kind}:{identifier}"
        graph[node]
        for dependency in dependencies or []:
            if isinstance(dependency, dict) and dependency.get("kind") and dependency.get("id"):
                graph[node].add(f"{dependency['kind']}:{dependency['id']}")

    for fact in registry.get("semantic_facts", []):
        add_node(
            "semantic_fact",
            fact.get("fact_key"),
            fact.get("verification", {}).get("depends_on", []),
        )
    for field in registry.get("derived_fields", []):
        add_node("derived_field", field.get("derived_field_id"), field.get("depends_on", []))
    for card in registry.get("evidence_cards", []):
        add_node("evidence_card", card.get("evidence_card_id"), card.get("depends_on", []))
    for figure in registry.get("reported_figures", []):
        dependencies = []
        if figure.get("derived_from"):
            dependencies.append({"kind": "reported_figure", "id": figure["derived_from"]})
        add_node("reported_figure", figure.get("figure_id"), dependencies)
    for claim in registry.get("claims", []):
        dependencies = []
        if claim.get("supersedes"):
            dependencies.append({"kind": "claim_revision", "id": claim["supersedes"]})
        add_node("claim_revision", claim.get("claim_revision_id"), dependencies)
    for item in registry.get("applicability", []):
        dependencies = [
            {"kind": "applicability", "id": dependency}
            for dependency in item.get("substituted_by", [])
        ]
        add_node("applicability", item.get("requirement_id"), dependencies)

    visited: set[str] = set()
    active: set[str] = set()
    stack: list[str] = []

    def visit(node: str) -> bool:
        if node in active:
            cycle_start = stack.index(node) if node in stack else 0
            blocking.append(
                _issue("REFERENCE_CYCLE", cycle=stack[cycle_start:] + [node])
            )
            return True
        if node in visited:
            return False
        visited.add(node)
        active.add(node)
        stack.append(node)
        found = False
        for dependency in sorted(graph.get(node, set())):
            if dependency in graph:
                found = visit(dependency) or found
        stack.pop()
        active.remove(node)
        return found

    for node in sorted(graph):
        visit(node)


def _pipeline_binding_checks(registry: dict, blocking: list[dict]) -> None:
    cards = _id_map(registry.get("evidence_cards", []), "evidence_card_id")
    claims = _id_map(registry.get("claims", []), "claim_revision_id")
    bindings: dict[str, set[str]] = defaultdict(set)
    for claim_id, claim in claims.items():
        if claim.get("pipeline_id"):
            bindings[claim_id].add(str(claim["pipeline_id"]))
    for relation in registry.get("evidence_relations", []):
        card = cards.get(str(relation.get("evidence_card_id")))
        claim_id = str(relation.get("claim_revision_id"))
        if card and card.get("pipeline_id"):
            bindings[claim_id].add(str(card["pipeline_id"]))
    for claim_id, pipeline_ids in bindings.items():
        if len(pipeline_ids) > 1:
            blocking.append(
                _issue(
                    "CROSS_PIPELINE_CLAIM_BINDING",
                    claim_revision_id=claim_id,
                    pipeline_ids=sorted(pipeline_ids),
                )
            )


def _dependencies_on_corrected_semantics(
    registry: dict, corrected_fact_keys: set[str]
) -> tuple[set[str], set[str], set[str]]:
    derived = _id_map(registry.get("derived_fields", []), "derived_field_id")
    stale_fields: set[str] = set()
    changed = True
    while changed:
        changed = False
        for field_id, field in derived.items():
            if field_id in stale_fields:
                continue
            for dependency in field.get("depends_on", []):
                kind, identifier = dependency.get("kind"), str(dependency.get("id"))
                if (
                    kind == "semantic_fact" and identifier in corrected_fact_keys
                ) or (kind == "derived_field" and identifier in stale_fields):
                    stale_fields.add(field_id)
                    changed = True
                    break
    stale_cards = {
        str(card.get("evidence_card_id"))
        for card in registry.get("evidence_cards", [])
        if any(
            dependency.get("kind") == "derived_field"
            and str(dependency.get("id")) in stale_fields
            for dependency in card.get("depends_on", [])
            if isinstance(dependency, dict)
        )
    }
    stale_claims = {
        str(relation.get("claim_revision_id"))
        for relation in registry.get("evidence_relations", [])
        if str(relation.get("evidence_card_id")) in stale_cards
    }
    return stale_fields, stale_cards, stale_claims


def _mark_stale(
    item: dict,
    reason: str,
    code: str,
    derived: list[dict],
    **identity: Any,
) -> None:
    reasons = item.setdefault("_stale_reasons", [])
    if reason not in reasons:
        reasons.append(reason)
        derived.append(_issue(code, reason=reason, **identity))
    if "availability" in item:
        item["availability"] = "stale"
    else:
        item["status"] = "stale"


def _semantic_cascade(
    registry: dict,
    state: dict,
    corrected_fact_keys: set[str],
    derived: list[dict],
) -> None:
    stale_fields, stale_cards, stale_claims = _dependencies_on_corrected_semantics(
        registry, corrected_fact_keys
    )
    for field_id in sorted(stale_fields):
        _mark_stale(
            state["derived_fields"][field_id],
            "semantic_correction",
            "SEMANTIC_STALE_DERIVED_FIELD",
            derived,
            derived_field_id=field_id,
        )
    for card_id in sorted(stale_cards):
        _mark_stale(
            state["evidence_cards"][card_id],
            "semantic_correction",
            "SEMANTIC_STALE_EVIDENCE_CARD",
            derived,
            evidence_card_id=card_id,
        )
    for claim_id in sorted(stale_claims):
        _mark_stale(
            state["claims"][claim_id],
            "semantic_correction",
            "SEMANTIC_STALE_CLAIM",
            derived,
            claim_revision_id=claim_id,
        )


def _pipeline_cascade(registry: dict, state: dict, derived: list[dict]) -> None:
    superseded = {
        str(pipeline.get("pipeline_id"))
        for pipeline in registry.get("pipelines", [])
        if pipeline.get("status") == "superseded"
    }
    for claim_id, claim in state["claims"].items():
        if str(claim.get("pipeline_id")) in superseded:
            _mark_stale(
                claim,
                "pipeline_superseded",
                "STALE_CLAIM",
                derived,
                claim_revision_id=claim_id,
                pipeline_id=claim.get("pipeline_id"),
            )
    for figure_id, figure in state["reported_figures"].items():
        if str(figure.get("pipeline_id")) in superseded:
            _mark_stale(
                figure,
                "pipeline_superseded",
                "STALE_REPORTED_FIGURE",
                derived,
                figure_id=figure_id,
                pipeline_id=figure.get("pipeline_id"),
            )
    for output_id, output in state["outputs"].items():
        # A reconciliation's historical quotations are not live bindings of
        # the new output.  They remain stale themselves, but do not make the
        # reconciliation artifact stale merely by being quoted as history.
        referenced_pipelines = _output_pipelines(
            output,
            state,
            include_historical=output.get("cross_pipeline") != "reconciliation",
        )
        if str(output.get("pipeline_id")) in superseded or referenced_pipelines & superseded:
            _mark_stale(
                output,
                "pipeline_superseded",
                "STALE_OUTPUT",
                derived,
                output_id=output_id,
                pipeline_ids=sorted(referenced_pipelines & superseded),
            )


def _valid_revalidation(record: dict, blocking: list[dict]) -> bool:
    required = (
        "target",
        "from_pipeline",
        "to_pipeline",
        "method",
        "result",
        "performed_by",
        "performed_at",
        "evidence_card",
    )
    missing = [field for field in required if record.get(field) is None]
    if record.get("method") == "machine" and not record.get("tolerance"):
        missing.append("tolerance")
    if missing:
        blocking.append(
            _issue(
                "REVALIDATION_INCOMPLETE",
                target=record.get("target"),
                missing=sorted(set(missing)),
            )
        )
        return False
    target = record.get("target")
    if not isinstance(target, dict) or target.get("kind") not in {
        "claim_revision",
        "reported_figure",
    } or not target.get("id"):
        blocking.append(_issue("REVALIDATION_TARGET_INVALID", target=target))
        return False
    if record.get("method") not in {"machine", "manual"}:
        blocking.append(_issue("REVALIDATION_METHOD_INVALID", target=target))
        return False
    return True


def _tolerance_accepts(old: Any, new: Any, expression: str) -> bool:
    if not isinstance(old, (int, float)) or not isinstance(new, (int, float)):
        return False
    match = re.search(r"abs\s*\(\s*delta\s*\)\s*<=\s*([0-9.eE+-]+)", expression)
    if not match:
        return False
    try:
        limit = float(match.group(1))
    except ValueError:
        return False
    if abs(float(new) - float(old)) > limit:
        return False
    if "sign unchanged" in expression.lower():
        old_sign = 0 if old == 0 else math.copysign(1, old)
        new_sign = 0 if new == 0 else math.copysign(1, new)
        return old_sign == new_sign
    return True


def _resolve_figure_value(registry: dict, figure: dict, record: dict) -> Any:
    """Resolve a JSON/YAML source locator for the destination pipeline."""

    artifact_spec = figure.get("source_artifact")
    if isinstance(artifact_spec, dict):
        artifact_spec = artifact_spec.get(record["to_pipeline"])
    if not isinstance(artifact_spec, str) or not artifact_spec:
        raise ValueError("source_artifact must identify a destination artifact")
    artifact_name = artifact_spec.replace("{pipeline_id}", str(record["to_pipeline"]))
    if artifact_name == artifact_spec and record["from_pipeline"] in artifact_name:
        artifact_name = artifact_name.replace(
            str(record["from_pipeline"]), str(record["to_pipeline"]), 1
        )
    artifact_path = Path(artifact_name)
    if not artifact_path.is_absolute():
        artifact_path = Path(registry.get("_root", ".")) / artifact_path
    if not artifact_path.is_file():
        raise ValueError(f"destination source artifact not found: {artifact_name}")
    try:
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise ValueError(f"destination source artifact is unreadable: {error}") from error

    locator: Any = figure.get("source_locator")
    if isinstance(locator, dict):
        locator = locator.get(record["to_pipeline"])
    if not isinstance(locator, str) or not locator:
        raise ValueError("source_locator must be a dotted path or JSON pointer")
    parts = (
        [part.replace("~1", "/").replace("~0", "~") for part in locator.lstrip("/").split("/")]
        if locator.startswith("/")
        else locator.split(".")
    )
    value = payload
    try:
        for part in parts:
            value = value[int(part)] if isinstance(value, list) else value[part]
    except (KeyError, IndexError, TypeError, ValueError) as error:
        raise ValueError(f"source_locator not found: {locator}") from error
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError("resolved reported figure must be numeric")
    return value


def _revalidate(
    registry: dict,
    state: dict,
    blocking: list[dict],
    derived: list[dict],
) -> None:
    for record in registry.get("revalidations", []):
        if not _valid_revalidation(record, blocking) or record.get("result") != "revalidated":
            continue
        target = record["target"]
        identifier = str(target["id"])
        collection = "claims" if target["kind"] == "claim_revision" else "reported_figures"
        item = state[collection].get(identifier)
        if item is None:
            blocking.append(_issue("REVALIDATION_TARGET_UNKNOWN", target=target))
            continue
        reasons = item.get("_stale_reasons", [])
        if "semantic_correction" in reasons and record["method"] == "machine":
            blocking.append(
                _issue("MACHINE_REVALIDATION_FORBIDDEN", target=target)
            )
            continue
        if target["kind"] == "reported_figure" and record["method"] == "machine":
            try:
                resolved_value = _resolve_figure_value(registry, item, record)
            except ValueError as error:
                blocking.append(
                    _issue(
                        "REVALIDATION_SOURCE_INVALID",
                        target=target,
                        detail=str(error),
                    )
                )
                continue
            if not _tolerance_accepts(
                item.get("value"), resolved_value, str(record["tolerance"])
            ):
                blocking.append(
                    _issue("REVALIDATION_TOLERANCE_FAILED", target=target)
                )
                continue
            item["value"] = resolved_value
        if "semantic_correction" in reasons and record["method"] == "manual":
            reasons.remove("semantic_correction")
        if "pipeline_superseded" in reasons:
            reasons.remove("pipeline_superseded")
        item["pipeline_id"] = record["to_pipeline"]
        item["revalidation"] = copy.deepcopy(record)
        if not reasons:
            if collection == "claims":
                item["availability"] = item.pop("_declared_availability", "current")
            else:
                item["status"] = item.pop("_declared_status", "current")
        derived.append(
            _issue(
                "REVALIDATED_CLAIM"
                if collection == "claims"
                else "REVALIDATED_REPORTED_FIGURE",
                target=target,
                from_pipeline=record["from_pipeline"],
                to_pipeline=record["to_pipeline"],
                assessment=item.get("assessment"),
            )
        )


def _apply_transform(value: Any, transform: Any) -> float:
    if not isinstance(value, (int, float)) or not isinstance(transform, dict):
        raise ValueError("transform requires a numeric upstream and mapping")
    operation = transform.get("operation")
    operand = transform.get("operand")
    if operation == "multiply" and isinstance(operand, (int, float)):
        return float(value) * float(operand)
    if operation == "divide" and isinstance(operand, (int, float)) and operand != 0:
        return float(value) / float(operand)
    if operation == "add" and isinstance(operand, (int, float)):
        return float(value) + float(operand)
    if operation == "subtract" and isinstance(operand, (int, float)):
        return float(value) - float(operand)
    raise ValueError("unsupported transform")


def _recompute_figures(state: dict, blocking: list[dict], derived: list[dict]) -> None:
    figures = state["reported_figures"]
    pending = {identifier for identifier, figure in figures.items() if figure.get("derived_from")}
    for _ in range(len(pending) + 1):
        changed = False
        for identifier in sorted(tuple(pending)):
            figure = figures[identifier]
            upstream = figures.get(str(figure.get("derived_from")))
            if upstream is None:
                blocking.append(
                    _issue(
                        "REPORTED_FIGURE_SOURCE_UNKNOWN",
                        figure_id=identifier,
                        derived_from=figure.get("derived_from"),
                    )
                )
                pending.remove(identifier)
                continue
            if str(figure.get("derived_from")) in pending:
                continue
            try:
                recomputed = _apply_transform(upstream.get("value"), figure.get("transform"))
            except ValueError as error:
                blocking.append(
                    _issue(
                        "REPORTED_FIGURE_TRANSFORM_INVALID",
                        figure_id=identifier,
                        detail=str(error),
                    )
                )
                pending.remove(identifier)
                continue
            old_value = figure.get("value")
            old_pipeline = figure.get("pipeline_id")
            figure["value"] = recomputed
            figure["pipeline_id"] = upstream.get("pipeline_id")
            upstream_reasons = list(upstream.get("_stale_reasons", []))
            figure["_stale_reasons"] = upstream_reasons
            figure["status"] = "stale" if upstream_reasons else figure.pop("_declared_status", "current")
            if old_value != recomputed or old_pipeline != figure.get("pipeline_id"):
                derived.append(
                    _issue(
                        "RECOMPUTED_REPORTED_FIGURE",
                        figure_id=identifier,
                        old_value=old_value,
                        value=recomputed,
                        pipeline_id=figure.get("pipeline_id"),
                    )
                )
            pending.remove(identifier)
            changed = True
        if not pending or not changed:
            break
    if pending:
        blocking.append(
            _issue("REPORTED_FIGURE_REFERENCE_CYCLE", figure_ids=sorted(pending))
        )


def _dependent_claims(registry: dict, derived_field_ids: set[str]) -> set[str]:
    card_ids = {
        str(card.get("evidence_card_id"))
        for card in registry.get("evidence_cards", [])
        if any(
            dependency.get("kind") == "derived_field"
            and str(dependency.get("id")) in derived_field_ids
            for dependency in card.get("depends_on", [])
            if isinstance(dependency, dict)
        )
    }
    return {
        str(relation.get("claim_revision_id"))
        for relation in registry.get("evidence_relations", [])
        if str(relation.get("evidence_card_id")) in card_ids
    }


def _challenge_cascade(
    registry: dict, state: dict, reports: list[dict], derived: list[dict]
) -> set[str]:
    challenged: set[str] = set()
    defective_fields = {
        str(field.get("derived_field_id"))
        for field in registry.get("derived_fields", [])
        if field.get("status") == "defective"
    }
    for claim_id in sorted(_dependent_claims(registry, defective_fields)):
        if state["claims"].get(claim_id, {}).get("availability") != "stale":
            challenged.add(claim_id)
            derived.append(
                _issue(
                    "DEFECTIVE_FIELD_CHALLENGE",
                    claim_revision_id=claim_id,
                    derived_field_ids=sorted(defective_fields),
                )
            )

    disclosure_keys = {
        str(item.get("fact_key"))
        for item in reports
        if item.get("code") == "SEMANTIC_DISCLOSURE_REQUIRED"
    }
    disclosure_fields = {
        str(field.get("derived_field_id"))
        for field in registry.get("derived_fields", [])
        if field.get("fact_key") in disclosure_keys
    }
    for claim_id in sorted(_dependent_claims(registry, disclosure_fields)):
        if state["claims"].get(claim_id, {}).get("availability") != "stale":
            challenged.add(claim_id)
            derived.append(
                _issue("SEMANTIC_CHANGE_CHALLENGE", claim_revision_id=claim_id)
            )
    return challenged


def _gate_checks(
    registry: dict,
    state: dict,
    checkpoint: str,
    blocking: list[dict],
    reports: list[dict],
    derived: list[dict],
) -> None:
    confirmation = registry.get("gate_set_confirmation")
    if checkpoint in {"B", "C"} and (
        not isinstance(confirmation, dict)
        or confirmation.get("checkpoint") != "B"
        or confirmation.get("complete") is not True
        or not confirmation.get("signed_by")
        or not confirmation.get("signed_at")
    ):
        blocking.append(_issue("GATE_SET_INCOMPLETE", checkpoint="B"))

    definitions = _id_map(registry.get("gate_definitions", []), "gate_id")
    pipelines = _id_map(registry.get("pipelines", []), "pipeline_id")
    claims_by_key: dict[str, list[dict]] = defaultdict(list)
    for claim in state["claims"].values():
        claims_by_key[str(claim.get("claim_key"))].append(claim)

    for evaluation in registry.get("gate_evaluations", []):
        gate_id = str(evaluation.get("gate_id"))
        pipeline_id = str(evaluation.get("pipeline_id"))
        definition = definitions.get(gate_id)
        pipeline = pipelines.get(pipeline_id)
        if definition is None or pipeline is None:
            blocking.append(
                _issue(
                    "GATE_REFERENCE_INVALID", gate_id=gate_id, pipeline_id=pipeline_id
                )
            )
            continue
        declared_at = _as_datetime(definition.get("declared_at"))
        batch_at = _as_datetime(pipeline.get("first_formal_batch_at"))
        if declared_at is None or batch_at is None:
            blocking.append(
                _issue("GATE_TIMING_INVALID", gate_id=gate_id, pipeline_id=pipeline_id)
            )
            post_hoc = None
        else:
            post_hoc = declared_at > batch_at
        reports.append(
            _issue(
                "GATE_POST_HOC",
                gate_id=gate_id,
                pipeline_id=pipeline_id,
                post_hoc=post_hoc,
            )
        )

        status = evaluation.get("status")
        moot_change = None
        for target in definition.get("applies_to", []):
            if target.get("kind") == "claim_key":
                for claim in claims_by_key.get(str(target.get("id")), []):
                    if claim.get("availability") in {"retired", "withdrawn"}:
                        moot_change = claim.get("change_id") or claim.get("claim_revision_id")
                        break
            elif target.get("kind") in {"dataset", "pipeline_stage"}:
                target_status = target.get("status")
                if target_status in {"retired", "withdrawn", "end_of_life"}:
                    moot_change = target.get("change_id") or target.get("id")
            if moot_change:
                break
        if moot_change:
            status = "moot"
            derived.append(
                _issue(
                    "GATE_MOOT",
                    gate_id=gate_id,
                    pipeline_id=pipeline_id,
                    triggering_change_id=moot_change,
                )
            )
        elif status == "moot":
            blocking.append(
                _issue(
                    "GATE_MOOT_INVALID",
                    gate_id=gate_id,
                    pipeline_id=pipeline_id,
                    detail="no applied object has a documented end-of-life state",
                )
            )

        if checkpoint != "C":
            continue
        coverage = evaluation.get("coverage")
        if not isinstance(coverage, dict) or coverage.get("complete") is not True:
            blocking.append(
                _issue(
                    "GATE_COVERAGE_INCOMPLETE",
                    gate_id=gate_id,
                    pipeline_id=pipeline_id,
                )
            )
            status = "not_evaluated"
        if status == "triggered":
            blocking.append(
                _issue("GATE_TRIGGERED", gate_id=gate_id, pipeline_id=pipeline_id)
            )
        elif status == "not_evaluated":
            blocking.append(
                _issue("GATE_NOT_EVALUATED", gate_id=gate_id, pipeline_id=pipeline_id)
            )
        elif status == "satisfied":
            if not all(
                evaluation.get(field)
                for field in ("compensation_artifact", "accepted_by", "accepted_at")
            ):
                blocking.append(
                    _issue(
                        "GATE_SATISFIED_INCOMPLETE",
                        gate_id=gate_id,
                        pipeline_id=pipeline_id,
                    )
                )
        elif status == "released":
            release = evaluation.get("release")
            required = (
                "triggering_change_id",
                "reason",
                "authorized_by",
                "timing",
                "evidence_card",
                "compensation_disposition",
            )
            if not isinstance(release, dict) or not all(release.get(field) for field in required):
                blocking.append(
                    _issue(
                        "GATE_RELEASE_INCOMPLETE",
                        gate_id=gate_id,
                        pipeline_id=pipeline_id,
                    )
                )
            else:
                reports.append(
                    _issue("GATE_RELEASED", gate_id=gate_id, pipeline_id=pipeline_id)
                )
        elif status == "inapplicable":
            required = ("applicability_reason", "declared_by", "accepted_by")
            if not all(evaluation.get(field) for field in required):
                blocking.append(
                    _issue(
                        "GATE_INAPPLICABLE_INCOMPLETE",
                        gate_id=gate_id,
                        pipeline_id=pipeline_id,
                    )
                )
            else:
                reports.append(
                    _issue(
                        "GATE_INAPPLICABLE", gate_id=gate_id, pipeline_id=pipeline_id
                    )
                )


def _applicability_checks(registry: dict, blocking: list[dict]) -> None:
    requirements = _id_map(registry.get("applicability", []), "requirement_id")
    for requirement_id, item in requirements.items():
        if item.get("status") != "inapplicable":
            continue
        required = ("applicability_reason", "declared_by", "accepted_by", "substituted_by")
        if not all(item.get(field) for field in required):
            blocking.append(
                _issue("APPLICABILITY_INAPPLICABLE_INCOMPLETE", requirement_id=requirement_id)
            )
            continue
        incomplete = [
            target
            for target in item.get("substituted_by", [])
            if target not in requirements or requirements[target].get("status") != "completed"
        ]
        if incomplete:
            blocking.append(
                _issue(
                    "APPLICABILITY_SUBSTITUTE_INCOMPLETE",
                    requirement_id=requirement_id,
                    substitutes=sorted(incomplete),
                )
            )


def _recompute_assessments(
    registry: dict, state: dict, derived_challenges: set[str], derived: list[dict]
) -> None:
    cards = _id_map(registry.get("evidence_cards", []), "evidence_card_id")
    relations_by_claim: dict[str, list[dict]] = defaultdict(list)
    for relation in registry.get("evidence_relations", []):
        relations_by_claim[str(relation.get("claim_revision_id"))].append(relation)
    for claim_id, claim in state["claims"].items():
        relations = relations_by_claim.get(claim_id, [])
        supports = [
            relation
            for relation in relations
            if relation.get("status") != "withdrawn"
            and relation.get("relation") == "supports"
            and cards.get(str(relation.get("evidence_card_id")), {}).get("provenance")
            == "confirmatory"
        ]
        challenges = [
            relation
            for relation in relations
            if relation.get("status") != "withdrawn"
            and relation.get("relation") in {"challenges", "bounds"}
            and cards.get(str(relation.get("evidence_card_id")), {}).get("provenance")
            == "confirmatory"
        ]
        old_assessment = claim.get("assessment")
        if not supports:
            claim["assessment"] = "unresolved"
            if old_assessment != "unresolved":
                derived.append(
                    _issue("ASSESSMENT_UNRESOLVED", claim_revision_id=claim_id)
                )
        elif challenges or claim_id in derived_challenges:
            claim["assessment"] = "challenged"
        else:
            claim["assessment"] = "supported"


def _output_pipelines(output: dict, state: dict, include_historical: bool) -> set[str]:
    pipeline_ids: set[str] = set()
    claim_fields = ["claim_revision_ids"]
    if include_historical:
        claim_fields.append("historical_claim_revision_ids")
    for field in claim_fields:
        for claim_id in output.get(field, []) or []:
            claim = state["claims"].get(str(claim_id))
            if claim and claim.get("pipeline_id"):
                pipeline_ids.add(str(claim["pipeline_id"]))
    for figure_id in output.get("reported_figure_ids", []) or []:
        figure = state["reported_figures"].get(str(figure_id))
        if figure and figure.get("pipeline_id"):
            pipeline_ids.add(str(figure["pipeline_id"]))
    return pipeline_ids


def _output_checks(state: dict, blocking: list[dict]) -> set[str]:
    invalid: set[str] = set()
    for output_id, output in state["outputs"].items():
        pipeline_ids = _output_pipelines(output, state, include_historical=True)
        declared = output.get("pipeline_id")
        if declared:
            pipeline_ids.add(str(declared))
        reconciliation = output.get("cross_pipeline") == "reconciliation"
        if len(pipeline_ids) > 1:
            spanned = {str(item) for item in output.get("spanned_pipelines", [])}
            if not reconciliation or spanned != pipeline_ids:
                blocking.append(
                    _issue(
                        "MIXED_PIPELINE_OUTPUT",
                        output_id=output_id,
                        pipeline_ids=sorted(pipeline_ids),
                    )
                )
                invalid.add(output_id)
        elif reconciliation:
            spanned = {str(item) for item in output.get("spanned_pipelines", [])}
            if spanned != pipeline_ids:
                blocking.append(
                    _issue(
                        "RECONCILIATION_SCOPE_INVALID",
                        output_id=output_id,
                        pipeline_ids=sorted(pipeline_ids),
                        spanned_pipelines=sorted(spanned),
                    )
                )
                invalid.add(output_id)
    return invalid


def _challenge_is_disclosed(claim_id: str, registry: dict, claim: dict) -> bool:
    disclosures = claim.get("challenge_disclosures", [])
    if disclosures and all(item.get("adjacent") and item.get("paper_location") for item in disclosures):
        return True
    challenges = [
        relation
        for relation in registry.get("evidence_relations", [])
        if str(relation.get("claim_revision_id")) == claim_id
        and relation.get("status") != "withdrawn"
        and relation.get("relation") in {"challenges", "bounds"}
    ]
    return bool(challenges) and all(
        relation.get("disclosure", {}).get("adjacent")
        and relation.get("disclosure", {}).get("paper_location")
        for relation in challenges
    )


def _refresh_outputs_after_revalidation(state: dict, derived: list[dict]) -> None:
    for output_id, output in state["outputs"].items():
        reasons = output.get("_stale_reasons", [])
        if "pipeline_superseded" not in reasons:
            continue
        active_claims = [
            state["claims"].get(str(identifier))
            for identifier in output.get("claim_revision_ids", [])
        ]
        figures = [
            state["reported_figures"].get(str(identifier))
            for identifier in output.get("reported_figure_ids", [])
        ]
        constituents = [item for item in active_claims + figures if item]
        pipelines = {str(item.get("pipeline_id")) for item in constituents}
        if constituents and len(pipelines) == 1 and all(
            not item.get("_stale_reasons") for item in constituents
        ):
            reasons.remove("pipeline_superseded")
            output["status"] = output.pop("_declared_status", "current")
            if output.get("cross_pipeline") != "reconciliation":
                output["pipeline_id"] = next(iter(pipelines))
            derived.append(
                _issue(
                    "REVALIDATED_OUTPUT",
                    output_id=output_id,
                    pipeline_id=next(iter(pipelines)),
                )
            )


def _publication_checks(
    registry: dict,
    state: dict,
    invalid_outputs: set[str],
    checkpoint: str,
    blocking: list[dict],
) -> None:
    if checkpoint != "C":
        return
    gate_or_applicability_block = any(
        item["code"].startswith("GATE_")
        or item["code"].startswith("APPLICABILITY_")
        for item in blocking
    )
    for output_id, output in state["outputs"].items():
        if output.get("kind") != "submission":
            continue
        reasons: list[str] = []
        if output_id in invalid_outputs:
            reasons.append("mixed_pipeline")
        if output.get("status") == "stale" or output.get("_stale_reasons"):
            reasons.append("stale_output")
        for claim_id_value in output.get("claim_revision_ids", []) or []:
            claim_id = str(claim_id_value)
            claim = state["claims"].get(claim_id)
            if claim is None:
                reasons.append(f"unknown_claim:{claim_id}")
                continue
            availability = claim.get("availability")
            assessment = claim.get("assessment")
            if availability != "current":
                reasons.append(f"claim_availability:{claim_id}:{availability}")
            elif assessment == "unresolved":
                reasons.append(f"claim_unresolved:{claim_id}")
            elif assessment == "challenged" and not _challenge_is_disclosed(
                claim_id, registry, claim
            ):
                reasons.append(f"challenge_undisclosed:{claim_id}")
        for figure_id_value in output.get("reported_figure_ids", []) or []:
            figure_id = str(figure_id_value)
            figure = state["reported_figures"].get(figure_id)
            if figure is None:
                reasons.append(f"unknown_figure:{figure_id}")
            elif figure.get("status") == "stale" or figure.get("_stale_reasons"):
                reasons.append(f"stale_figure:{figure_id}")
        if gate_or_applicability_block:
            reasons.append("governance_gate")
        if reasons:
            blocking.append(
                _issue(
                    "PUBLICATION_INELIGIBLE",
                    output_id=output_id,
                    reasons=sorted(set(reasons)),
                )
            )


def _initial_state(registry: dict) -> dict:
    state = {
        "claims": copy.deepcopy(_id_map(registry.get("claims", []), "claim_revision_id")),
        "evidence_cards": copy.deepcopy(
            _id_map(registry.get("evidence_cards", []), "evidence_card_id")
        ),
        "reported_figures": copy.deepcopy(
            _id_map(registry.get("reported_figures", []), "figure_id")
        ),
        "outputs": copy.deepcopy(_id_map(registry.get("outputs", []), "output_id")),
        "derived_fields": copy.deepcopy(
            _id_map(registry.get("derived_fields", []), "derived_field_id")
        ),
    }
    for claim in state["claims"].values():
        claim["_declared_availability"] = claim.get("availability")
        claim["_stale_reasons"] = []
    for collection in ("evidence_cards", "reported_figures", "outputs", "derived_fields"):
        for item in state[collection].values():
            item["_declared_status"] = item.get("status", "current")
            item["_stale_reasons"] = []
    return state


def validate_registry(registry: dict | Path, checkpoint: str) -> dict:
    """Validate loaded data (or a registry directory) and return derived state."""

    checkpoint = str(checkpoint).upper()
    if checkpoint not in {"B", "C"}:
        raise ValueError("checkpoint must be B or C")
    if isinstance(registry, (str, Path)):
        registry = load_registry(Path(registry))
    blocking: list[dict] = copy.deepcopy(registry.get("_load_errors", []))
    reports: list[dict] = []
    derived: list[dict] = []

    _required_field_checks(registry, blocking)
    corrected_fact_keys = _semantic_checks(registry, blocking, reports)
    _reference_graph_checks(registry, blocking)
    _pipeline_binding_checks(registry, blocking)
    state = _initial_state(registry)

    # Contractual cascade order: semantics, pipelines, challenges, moot gates,
    # live-support assessment, then publication. Revalidation is an authored
    # action applied after stale derivation and before downstream recomputation.
    _semantic_cascade(registry, state, corrected_fact_keys, derived)
    _pipeline_cascade(registry, state, derived)
    _revalidate(registry, state, blocking, derived)
    _recompute_figures(state, blocking, derived)
    _refresh_outputs_after_revalidation(state, derived)
    derived_challenges = _challenge_cascade(registry, state, reports, derived)
    _gate_checks(registry, state, checkpoint, blocking, reports, derived)
    _applicability_checks(registry, blocking)
    _recompute_assessments(registry, state, derived_challenges, derived)
    invalid_outputs = _output_checks(state, blocking)
    _publication_checks(registry, state, invalid_outputs, checkpoint, blocking)
    if not blocking:
        reports.append(_issue("REGISTRY_VALID", checkpoint=checkpoint))

    return {
        "checkpoint": checkpoint,
        "blocking": blocking,
        "reports": reports,
        "derived": derived,
        "state": state,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("registry_dir", type=Path)
    parser.add_argument("--checkpoint", required=True, choices=("B", "C"))
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    report = validate_registry(load_registry(args.registry_dir), args.checkpoint)
    if args.format == "json":
        json.dump(report, sys.stdout, indent=2, sort_keys=True, default=str)
        sys.stdout.write("\n")
    else:
        print(f"Checkpoint {report['checkpoint']}: {len(report['blocking'])} blocking issue(s)")
        for item in report["blocking"]:
            print(f"BLOCK {item['code']}: {json.dumps(item, sort_keys=True, default=str)}")
        for item in report["reports"]:
            print(f"REPORT {item['code']}: {json.dumps(item, sort_keys=True, default=str)}")
        for item in report["derived"]:
            print(f"DERIVED {item['code']}: {json.dumps(item, sort_keys=True, default=str)}")
    return 0 if not report["blocking"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
