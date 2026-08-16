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
    "changes",
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
        "compensation",
    ),
    "gate_evaluations": (
        "gate_id",
        "pipeline_id",
        "evaluated_against",
        "status",
        "coverage",
        "evidence_card",
    ),
    "changes": (
        "change_id",
        "object_kind",
        "object_id",
        "pipeline_id",
        "new_state",
        "authorized_by",
        "occurred_at",
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
            if (
                isinstance(item, dict)
                and field in item
                and (
                    not isinstance(item[field], str)
                    or item[field] not in ALLOWED[allowed_key]
                )
            ):
                blocking.append(
                    _issue(
                        "INVALID_ENUM_VALUE",
                        collection=collection,
                        id=_object_id(item),
                        field=field,
                        value=item[field],
                    )
                )


def _schema_error(
    blocking: list[dict], location: str, detail: str
) -> None:
    blocking.append(_issue("SCHEMA_INVALID", location=location, detail=detail))


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and all(_nonempty_string(item) for item in value)


def _dependency_list(value: Any) -> bool:
    return isinstance(value, list) and all(
        isinstance(item, dict)
        and _nonempty_string(item.get("kind"))
        and _nonempty_string(item.get("id"))
        for item in value
    )


def _structural_checks(registry: dict, blocking: list[dict]) -> bool:
    """Validate all user-controlled shapes before semantic evaluation."""

    start = len(blocking)
    for collection in COLLECTIONS:
        value = registry.get(collection, [])
        if not isinstance(value, list):
            _schema_error(blocking, collection, "collection must be a list")
            continue
        for index, item in enumerate(value):
            if not isinstance(item, dict):
                _schema_error(blocking, f"{collection}[{index}]", "record must be a mapping")

    if len(blocking) != start:
        return False

    identity_fields = {
        "pipelines": "pipeline_id",
        "claims": "claim_revision_id",
        "evidence_cards": "evidence_card_id",
        "evidence_relations": "relation_id",
        "reported_figures": "figure_id",
        "outputs": "output_id",
        "gate_definitions": "gate_id",
        "semantic_facts": "fact_revision_id",
        "derived_fields": "derived_field_id",
        "applicability": "requirement_id",
        "changes": "change_id",
    }
    for collection, field in identity_fields.items():
        for index, item in enumerate(registry[collection]):
            if not _nonempty_string(item.get(field)):
                _schema_error(
                    blocking,
                    f"{collection}[{index}].{field}",
                    "identity must be a nonempty string",
                )

    string_fields = {
        "pipelines": ("status",),
        "claims": ("claim_key", "pipeline_id", "availability", "assessment"),
        "evidence_cards": ("pipeline_id", "provenance", "status"),
        "evidence_relations": (
            "evidence_card_id",
            "claim_revision_id",
            "relation",
            "status",
            "author",
            "rationale",
        ),
        "reported_figures": ("pipeline_id",),
        "outputs": ("kind", "status"),
        "gate_definitions": (
            "metric",
            "allowed_band",
            "failure_policy",
            "declared_by",
        ),
        "gate_evaluations": ("gate_id", "pipeline_id", "evidence_card"),
        "semantic_facts": ("fact_key", "field", "statement"),
        "derived_fields": ("fact_key", "status"),
        "applicability": ("status",),
        "changes": (
            "object_kind",
            "object_id",
            "pipeline_id",
            "new_state",
            "authorized_by",
            "evidence_card",
        ),
    }
    for collection, fields in string_fields.items():
        for index, item in enumerate(registry[collection]):
            for field in fields:
                if field in item and not _nonempty_string(item[field]):
                    _schema_error(
                        blocking,
                        f"{collection}[{index}].{field}",
                        "must be a nonempty string",
                    )

    confirmation = registry.get("gate_set_confirmation")
    if not (
        isinstance(confirmation, dict)
        and confirmation.get("checkpoint") == "B"
        and isinstance(confirmation.get("complete"), bool)
        and _nonempty_string(confirmation.get("signed_by"))
        and _as_datetime(confirmation.get("signed_at")) is not None
    ):
        _schema_error(
            blocking,
            "gate_set_confirmation",
            "requires checkpoint B, boolean complete, signer, and ISO timestamp",
        )
    if not _string_list(registry.get("used_fields")):
        _schema_error(
            blocking,
            "used_fields",
            "must be a list of nonempty field identifiers",
        )

    for index, pipeline in enumerate(registry["pipelines"]):
        if _as_datetime(pipeline.get("first_formal_batch_at")) is None:
            _schema_error(
                blocking,
                f"pipelines[{index}].first_formal_batch_at",
                "must be an ISO timestamp",
            )
    for index, claim in enumerate(registry["claims"]):
        if "challenge_disclosures" in claim and not isinstance(
            claim["challenge_disclosures"], list
        ):
            _schema_error(
                blocking,
                f"claims[{index}].challenge_disclosures",
                "must be a list",
            )
        elif "challenge_disclosures" in claim and not all(
            isinstance(item, dict)
            and _nonempty_string(item.get("challenge_id"))
            and _nonempty_string(item.get("paper_location"))
            and isinstance(item.get("adjacent"), bool)
            for item in claim["challenge_disclosures"]
        ):
            _schema_error(
                blocking,
                f"claims[{index}].challenge_disclosures",
                "entries require challenge_id, paper_location, and boolean adjacent",
            )
    for collection in ("evidence_cards", "derived_fields"):
        for index, item in enumerate(registry[collection]):
            if not _dependency_list(item.get("depends_on", [])):
                _schema_error(
                    blocking,
                    f"{collection}[{index}].depends_on",
                    "must be a list of kind/id mappings",
                )
    for index, relation in enumerate(registry["evidence_relations"]):
        if _as_date(relation.get("date")) is None:
            _schema_error(
                blocking,
                f"evidence_relations[{index}].date",
                "must be an ISO date",
            )
        if "disclosure" in relation and not isinstance(relation["disclosure"], dict):
            _schema_error(
                blocking,
                f"evidence_relations[{index}].disclosure",
                "must be a mapping",
            )
        elif "disclosure" in relation and not (
            isinstance(relation["disclosure"].get("adjacent"), bool)
            and _nonempty_string(relation["disclosure"].get("paper_location"))
        ):
            _schema_error(
                blocking,
                f"evidence_relations[{index}].disclosure",
                "requires boolean adjacent and a paper location",
            )
    for index, figure in enumerate(registry["reported_figures"]):
        value = figure.get("value")
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(float(value))
        ):
            _schema_error(
                blocking,
                f"reported_figures[{index}].value",
                "must be a finite number",
            )
        if not _string_list(figure.get("paper_locations")):
            _schema_error(
                blocking,
                f"reported_figures[{index}].paper_locations",
                "must be a list of nonempty strings",
            )
        for field in ("source_artifact", "source_locator"):
            source = figure.get(field)
            if not (
                _nonempty_string(source)
                or (
                    isinstance(source, dict)
                    and source
                    and all(
                        _nonempty_string(pipeline_id) and _nonempty_string(value)
                        for pipeline_id, value in source.items()
                    )
                )
            ):
                _schema_error(
                    blocking,
                    f"reported_figures[{index}].{field}",
                    "must be a nonempty locator or pipeline-to-locator mapping",
                )
        if figure.get("derived_from") and not isinstance(figure.get("transform"), dict):
            _schema_error(
                blocking,
                f"reported_figures[{index}].transform",
                "derived figures require a transform mapping",
            )
    for index, output in enumerate(registry["outputs"]):
        for field in (
            "claim_revision_ids",
            "historical_claim_revision_ids",
            "reported_figure_ids",
            "spanned_pipelines",
        ):
            if field in output and not _string_list(output[field]):
                _schema_error(
                    blocking,
                    f"outputs[{index}].{field}",
                    "must be a list of nonempty identifiers",
                )
    allowed_targets = {"dataset", "pipeline_stage", "claim_key"}
    for index, definition in enumerate(registry["gate_definitions"]):
        targets = definition.get("applies_to")
        if not isinstance(targets, list) or not targets or not all(
            isinstance(target, dict)
            and target.get("kind") in allowed_targets
            and _nonempty_string(target.get("id"))
            for target in targets
        ):
            _schema_error(
                blocking,
                f"gate_definitions[{index}].applies_to",
                "must contain dataset, pipeline_stage, or claim_key targets",
            )
        if definition.get("frozen") is not True:
            _schema_error(
                blocking,
                f"gate_definitions[{index}].frozen",
                "must be true",
            )
        compensation = definition.get("compensation")
        if not (
            isinstance(compensation, dict)
            and _nonempty_string(compensation.get("action"))
            and _nonempty_string(compensation.get("required_artifact"))
        ):
            _schema_error(
                blocking,
                f"gate_definitions[{index}].compensation",
                "requires action and required_artifact",
            )
        if _as_datetime(definition.get("declared_at")) is None:
            _schema_error(
                blocking,
                f"gate_definitions[{index}].declared_at",
                "must be an ISO timestamp",
            )
    for index, evaluation in enumerate(registry["gate_evaluations"]):
        target = evaluation.get("evaluated_against")
        if not (
            isinstance(target, dict)
            and target.get("kind") in allowed_targets
            and _nonempty_string(target.get("id"))
        ):
            _schema_error(
                blocking,
                f"gate_evaluations[{index}].evaluated_against",
                "must be a kind/id target mapping",
            )
        coverage = evaluation.get("coverage")
        if not isinstance(coverage, dict):
            _schema_error(
                blocking,
                f"gate_evaluations[{index}].coverage",
                "must be a mapping",
            )
        elif not isinstance(coverage.get("complete"), bool):
            _schema_error(
                blocking,
                f"gate_evaluations[{index}].coverage",
                "requires boolean complete",
            )
    for index, fact in enumerate(registry["semantic_facts"]):
        authority = fact.get("authority")
        verification = fact.get("verification")
        if not isinstance(authority, dict):
            _schema_error(
                blocking,
                f"semantic_facts[{index}].authority",
                "must be a mapping",
            )
        elif authority.get("status") not in {"sourced", "declared"} or (
            authority.get("status") == "sourced"
            and not _nonempty_string(authority.get("source"))
        ):
            _schema_error(
                blocking,
                f"semantic_facts[{index}].authority",
                "requires sourced+source or declared authority",
            )
        if not isinstance(verification, dict):
            _schema_error(
                blocking,
                f"semantic_facts[{index}].verification",
                "must be a mapping",
            )
        elif not _dependency_list(verification.get("depends_on", [])):
            _schema_error(
                blocking,
                f"semantic_facts[{index}].verification.depends_on",
                "must be a list of kind/id mappings",
            )
        elif (
            not _nonempty_string(verification.get("method"))
            or verification.get("result") not in {"pass", "fail"}
            or not _nonempty_string(verification.get("performed_by"))
            or _as_datetime(verification.get("performed_at")) is None
        ):
            _schema_error(
                blocking,
                f"semantic_facts[{index}].verification",
                "requires method, pass/fail result, performer, and ISO timestamp",
            )
        valid_range = fact.get("valid_range")
        if not isinstance(valid_range, list) or len(valid_range) != 2:
            _schema_error(
                blocking,
                f"semantic_facts[{index}].valid_range",
                "must be a two-element list",
            )
    for index, field in enumerate(registry["derived_fields"]):
        if field.get("status") == "defective" and not _string_list(
            field.get("known_defects")
        ):
            _schema_error(
                blocking,
                f"derived_fields[{index}].known_defects",
                "defective fields require known defects",
            )
    for index, item in enumerate(registry["applicability"]):
        if "substituted_by" in item and not _string_list(item["substituted_by"]):
            _schema_error(
                blocking,
                f"applicability[{index}].substituted_by",
                "must be a list of requirement identifiers",
            )
        if item.get("record_type") == "design_grid" and not (
            _string_list(item.get("dimensions"))
            and isinstance(item.get("empty_cells"), list)
        ):
            _schema_error(
                blocking,
                f"applicability[{index}]",
                "design_grid requires dimensions and empty_cells",
            )
        if item.get("record_type") == "sibling_parity":
            results = item.get("dimension_results")
            if not (
                isinstance(results, list)
                and results
                and all(
                    isinstance(result, dict)
                    and _nonempty_string(result.get("dimension"))
                    and result.get("result") in {"match", "diverge"}
                    for result in results
                )
                and _nonempty_string(item.get("consequence_assessment"))
            ):
                _schema_error(
                    blocking,
                    f"applicability[{index}]",
                    "sibling_parity requires match/diverge results and consequence assessment",
                )
    for index, record in enumerate(registry["revalidations"]):
        if not isinstance(record.get("target"), dict):
            _schema_error(
                blocking,
                f"revalidations[{index}].target",
                "must be a mapping",
            )
    for index, change in enumerate(registry["changes"]):
        if change.get("object_kind") not in {
            "claim_revision",
            "dataset",
            "pipeline_stage",
            "claim_key",
        }:
            _schema_error(
                blocking,
                f"changes[{index}].object_kind",
                "invalid changed-object kind",
            )
        if _as_datetime(change.get("occurred_at")) is None:
            _schema_error(
                blocking,
                f"changes[{index}].occurred_at",
                "must be an ISO timestamp",
            )
    return len(blocking) == start


def _identity_reference_checks(registry: dict, blocking: list[dict]) -> bool:
    """Reject duplicate identities and every dangling authored reference."""

    start = len(blocking)
    identity_fields = {
        "pipelines": "pipeline_id",
        "claims": "claim_revision_id",
        "evidence_cards": "evidence_card_id",
        "evidence_relations": "relation_id",
        "reported_figures": "figure_id",
        "outputs": "output_id",
        "gate_definitions": "gate_id",
        "semantic_facts": "fact_revision_id",
        "derived_fields": "derived_field_id",
        "applicability": "requirement_id",
        "changes": "change_id",
    }
    for collection, field in identity_fields.items():
        seen: set[str] = set()
        for item in registry[collection]:
            identifier = str(item.get(field))
            if identifier in seen:
                blocking.append(
                    _issue(
                        "DUPLICATE_ID",
                        collection=collection,
                        field=field,
                        id=identifier,
                    )
                )
            seen.add(identifier)

    pipelines = _id_map(registry["pipelines"], "pipeline_id")
    claims = _id_map(registry["claims"], "claim_revision_id")
    claim_keys = {str(claim.get("claim_key")) for claim in registry["claims"]}
    cards = _id_map(registry["evidence_cards"], "evidence_card_id")
    figures = _id_map(registry["reported_figures"], "figure_id")
    derived_fields = _id_map(registry["derived_fields"], "derived_field_id")
    fact_keys = {str(fact.get("fact_key")) for fact in registry["semantic_facts"]}
    fact_revisions = _id_map(registry["semantic_facts"], "fact_revision_id")
    requirements = _id_map(registry["applicability"], "requirement_id")
    definitions = _id_map(registry["gate_definitions"], "gate_id")
    changes = _id_map(registry["changes"], "change_id")

    def require(namespace: dict | set, identifier: Any, location: str) -> None:
        if str(identifier) not in namespace:
            blocking.append(
                _issue(
                    "UNKNOWN_REFERENCE",
                    location=location,
                    id=identifier,
                )
            )

    for claim in registry["claims"]:
        require(pipelines, claim.get("pipeline_id"), f"claims.{claim.get('claim_revision_id')}.pipeline_id")
        if claim.get("supersedes"):
            require(claims, claim["supersedes"], f"claims.{claim.get('claim_revision_id')}.supersedes")
            predecessor = claims.get(str(claim["supersedes"]))
            if predecessor and (
                predecessor.get("claim_key") != claim.get("claim_key")
                or not _nonempty_string(claim.get("revision_reason"))
            ):
                blocking.append(
                    _issue(
                        "CLAIM_REVISION_INCOHERENT",
                        claim_revision_id=claim.get("claim_revision_id"),
                    )
                )
    for card in registry["evidence_cards"]:
        require(pipelines, card.get("pipeline_id"), f"evidence_cards.{card.get('evidence_card_id')}.pipeline_id")
    for relation in registry["evidence_relations"]:
        require(cards, relation.get("evidence_card_id"), f"evidence_relations.{relation.get('relation_id')}.evidence_card_id")
        require(claims, relation.get("claim_revision_id"), f"evidence_relations.{relation.get('relation_id')}.claim_revision_id")
    for fact in registry["semantic_facts"]:
        if fact.get("supersedes"):
            require(fact_revisions, fact["supersedes"], f"semantic_facts.{fact.get('fact_revision_id')}.supersedes")
            predecessor = fact_revisions.get(str(fact["supersedes"]))
            if predecessor and (
                predecessor.get("fact_key") != fact.get("fact_key")
                or not _nonempty_string(fact.get("revision_reason"))
            ):
                blocking.append(
                    _issue(
                        "SEMANTIC_REVISION_INCOHERENT",
                        fact_revision_id=fact.get("fact_revision_id"),
                    )
                )
    for collection in ("semantic_facts", "derived_fields", "evidence_cards"):
        for item in registry[collection]:
            dependencies = (
                item.get("verification", {}).get("depends_on", [])
                if collection == "semantic_facts"
                else item.get("depends_on", [])
            )
            for dependency in dependencies:
                kind = dependency["kind"]
                if kind == "semantic_fact":
                    require(fact_keys, dependency["id"], f"{collection}.{_object_id(item)}.depends_on")
                elif kind == "derived_field":
                    require(derived_fields, dependency["id"], f"{collection}.{_object_id(item)}.depends_on")
                elif kind != "raw_field":
                    blocking.append(
                        _issue(
                            "REFERENCE_KIND_INVALID",
                            location=f"{collection}.{_object_id(item)}.depends_on",
                            kind=kind,
                        )
                    )
    for field in registry["derived_fields"]:
        require(
            fact_keys,
            field.get("fact_key"),
            f"derived_fields.{field.get('derived_field_id')}.fact_key",
        )
    for figure in registry["reported_figures"]:
        require(pipelines, figure.get("pipeline_id"), f"reported_figures.{figure.get('figure_id')}.pipeline_id")
        if figure.get("derived_from"):
            require(figures, figure["derived_from"], f"reported_figures.{figure.get('figure_id')}.derived_from")
    for output in registry["outputs"]:
        if output.get("pipeline_id"):
            require(pipelines, output["pipeline_id"], f"outputs.{output.get('output_id')}.pipeline_id")
        for identifier in output.get("claim_revision_ids", []):
            require(claims, identifier, f"outputs.{output.get('output_id')}.claim_revision_ids")
        historical = output.get("historical_claim_revision_ids", [])
        if historical and output.get("cross_pipeline") != "reconciliation":
            blocking.append(
                _issue(
                    "HISTORICAL_REFERENCE_FORBIDDEN",
                    output_id=output.get("output_id"),
                )
            )
        for identifier in historical:
            require(claims, identifier, f"outputs.{output.get('output_id')}.historical_claim_revision_ids")
        for identifier in output.get("reported_figure_ids", []):
            require(figures, identifier, f"outputs.{output.get('output_id')}.reported_figure_ids")
        for identifier in output.get("spanned_pipelines", []):
            require(pipelines, identifier, f"outputs.{output.get('output_id')}.spanned_pipelines")
    for item in registry["applicability"]:
        for identifier in item.get("substituted_by", []):
            require(requirements, identifier, f"applicability.{item.get('requirement_id')}.substituted_by")
    for evaluation in registry["gate_evaluations"]:
        require(definitions, evaluation.get("gate_id"), "gate_evaluations.gate_id")
        require(pipelines, evaluation.get("pipeline_id"), "gate_evaluations.pipeline_id")
        require(cards, evaluation.get("evidence_card"), "gate_evaluations.evidence_card")
    for definition in registry["gate_definitions"]:
        for target in definition.get("applies_to", []):
            if target.get("kind") == "claim_key":
                require(
                    claim_keys,
                    target.get("id"),
                    f"gate_definitions.{definition.get('gate_id')}.applies_to",
                )
    for change in registry["changes"]:
        require(pipelines, change.get("pipeline_id"), f"changes.{change.get('change_id')}.pipeline_id")
        require(cards, change.get("evidence_card"), f"changes.{change.get('change_id')}.evidence_card")
        evidence = cards.get(str(change.get("evidence_card")))
        if evidence and (
            str(evidence.get("pipeline_id")) != str(change.get("pipeline_id"))
            or evidence.get("status") != "current"
        ):
            blocking.append(
                _issue(
                    "CHANGE_EVIDENCE_INVALID",
                    change_id=change.get("change_id"),
                )
            )
        if change.get("object_kind") == "claim_revision":
            require(claims, change.get("object_id"), f"changes.{change.get('change_id')}.object_id")
        elif change.get("object_kind") == "claim_key":
            require(claim_keys, change.get("object_id"), f"changes.{change.get('change_id')}.object_id")
    pairs: set[tuple[str, str]] = set()
    for evaluation in registry["gate_evaluations"]:
        pair = (str(evaluation.get("gate_id")), str(evaluation.get("pipeline_id")))
        if pair in pairs:
            blocking.append(_issue("DUPLICATE_GATE_EVALUATION", gate_id=pair[0], pipeline_id=pair[1]))
        pairs.add(pair)
    revalidation_targets: set[tuple[str, str]] = set()
    for record in registry["revalidations"]:
        target = record.get("target", {})
        pair = (str(target.get("kind")), str(target.get("id")))
        if pair in revalidation_targets:
            blocking.append(
                _issue(
                    "DUPLICATE_REVALIDATION_TARGET",
                    target={"kind": pair[0], "id": pair[1]},
                )
            )
        revalidation_targets.add(pair)
    return len(blocking) == start


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
        if fact.get("verification", {}).get("result") == "fail":
            blocking.append(
                _issue(
                    "SEMANTIC_VERIFICATION_FAILED",
                    fact_revision_id=fact.get("fact_revision_id"),
                )
            )
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


def _dependency_topology(
    registry: dict, blocking: list[dict]
) -> tuple[list[str], dict[str, set[str]]]:
    """Build and topologically sort the validated cross-object graph once."""

    outgoing: dict[str, set[str]] = defaultdict(set)
    indegree: dict[str, int] = defaultdict(int)

    def node(kind: str, identifier: Any) -> str:
        name = f"{kind}:{identifier}"
        outgoing[name]
        indegree[name]
        return name

    def edge(source: str, destination: str) -> None:
        if destination not in outgoing[source]:
            outgoing[source].add(destination)
            indegree[destination] += 1

    for fact in registry["semantic_facts"]:
        destination = node("semantic_fact", fact["fact_key"])
        for dependency in fact.get("verification", {}).get("depends_on", []):
            if dependency["kind"] != "raw_field":
                edge(node(dependency["kind"], dependency["id"]), destination)
    for field in registry["derived_fields"]:
        destination = node("derived_field", field["derived_field_id"])
        for dependency in field.get("depends_on", []):
            if dependency["kind"] != "raw_field":
                edge(node(dependency["kind"], dependency["id"]), destination)
    for card in registry["evidence_cards"]:
        destination = node("evidence_card", card["evidence_card_id"])
        for dependency in card.get("depends_on", []):
            if dependency["kind"] != "raw_field":
                edge(node(dependency["kind"], dependency["id"]), destination)
    for claim in registry["claims"]:
        destination = node("claim_revision", claim["claim_revision_id"])
        if claim.get("supersedes"):
            edge(node("claim_revision", claim["supersedes"]), destination)
    cards = _id_map(registry["evidence_cards"], "evidence_card_id")
    for relation in registry["evidence_relations"]:
        card = cards.get(str(relation.get("evidence_card_id")))
        if (
            relation.get("status") != "withdrawn"
            and card
            and card.get("provenance") == "confirmatory"
        ):
            edge(
                node("evidence_card", relation["evidence_card_id"]),
                node("claim_revision", relation["claim_revision_id"]),
            )
    for figure in registry["reported_figures"]:
        destination = node("reported_figure", figure["figure_id"])
        if figure.get("derived_from"):
            edge(node("reported_figure", figure["derived_from"]), destination)
    for item in registry["applicability"]:
        destination = node("applicability", item["requirement_id"])
        for dependency in item.get("substituted_by", []):
            edge(node("applicability", dependency), destination)

    ready = sorted(name for name, degree in indegree.items() if degree == 0)
    order: list[str] = []
    while ready:
        current = ready.pop(0)
        order.append(current)
        for destination in sorted(outgoing[current]):
            indegree[destination] -= 1
            if indegree[destination] == 0:
                ready.append(destination)
                ready.sort()
    if len(order) != len(indegree):
        blocking.append(
            _issue(
                "REFERENCE_CYCLE",
                nodes=sorted(name for name, degree in indegree.items() if degree > 0),
            )
        )
    return order, outgoing


def _propagate_reasons(
    order: list[str],
    outgoing: dict[str, set[str]],
    seeds: dict[str, set[str]],
) -> dict[str, set[str]]:
    reasons: dict[str, set[str]] = defaultdict(set)
    for name, values in seeds.items():
        reasons[name].update(values)
    for name in order:
        if not reasons[name]:
            continue
        for destination in outgoing[name]:
            reasons[destination].update(reasons[name])
    return reasons


def _pipeline_binding_checks(
    registry: dict, blocking: list[dict], state: dict | None = None
) -> None:
    cards = _id_map(registry.get("evidence_cards", []), "evidence_card_id")
    claims = (
        state["claims"]
        if state is not None
        else _id_map(registry.get("claims", []), "claim_revision_id")
    )
    bindings: dict[str, set[str]] = defaultdict(set)
    for claim_id, claim in claims.items():
        if claim.get("pipeline_id"):
            bindings[claim_id].add(str(claim["pipeline_id"]))
    for relation in registry.get("evidence_relations", []):
        if relation.get("status") == "withdrawn":
            continue
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
    state: dict,
    corrected_fact_keys: set[str],
    order: list[str],
    outgoing: dict[str, set[str]],
    derived: list[dict],
) -> None:
    impacts = _propagate_reasons(
        order,
        outgoing,
        {
            f"semantic_fact:{fact_key}": {"semantic_correction"}
            for fact_key in corrected_fact_keys
        },
    )
    for field_id in sorted(state["derived_fields"]):
        if not impacts[f"derived_field:{field_id}"]:
            continue
        _mark_stale(
            state["derived_fields"][field_id],
            "semantic_correction",
            "SEMANTIC_STALE_DERIVED_FIELD",
            derived,
            derived_field_id=field_id,
        )
    for card_id in sorted(state["evidence_cards"]):
        if not impacts[f"evidence_card:{card_id}"]:
            continue
        _mark_stale(
            state["evidence_cards"][card_id],
            "semantic_correction",
            "SEMANTIC_STALE_EVIDENCE_CARD",
            derived,
            evidence_card_id=card_id,
        )
    for claim_id in sorted(state["claims"]):
        if not impacts[f"claim_revision:{claim_id}"]:
            continue
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


def _valid_revalidation(
    registry: dict,
    state: dict,
    record: dict,
    blocking: list[dict],
) -> tuple[dict, Any] | None:
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
        return None
    target = record.get("target")
    if not isinstance(target, dict) or target.get("kind") not in {
        "claim_revision",
        "reported_figure",
    } or not target.get("id"):
        blocking.append(_issue("REVALIDATION_TARGET_INVALID", target=target))
        return None
    if record.get("method") not in {"machine", "manual"}:
        blocking.append(_issue("REVALIDATION_METHOD_INVALID", target=target))
        return None
    if record.get("result") not in {"revalidated", "changed", "not_revalidated"}:
        blocking.append(_issue("REVALIDATION_RESULT_INVALID", target=target))
        return None
    if _as_datetime(record.get("performed_at")) is None:
        blocking.append(_issue("REVALIDATION_TIMESTAMP_INVALID", target=target))
        return None
    if not isinstance(record.get("performed_by"), str) or not record["performed_by"].strip():
        blocking.append(_issue("REVALIDATION_PERFORMER_INVALID", target=target))
        return None

    collection = "claims" if target["kind"] == "claim_revision" else "reported_figures"
    item = state[collection].get(str(target["id"]))
    if item is None:
        blocking.append(_issue("REVALIDATION_TARGET_UNKNOWN", target=target))
        return None
    if str(record.get("from_pipeline")) != str(item.get("pipeline_id")):
        blocking.append(
            _issue(
                "REVALIDATION_SOURCE_MISMATCH",
                target=target,
                expected=item.get("pipeline_id"),
                actual=record.get("from_pipeline"),
            )
        )
        return None
    pipelines = _id_map(registry.get("pipelines", []), "pipeline_id")
    destination = pipelines.get(str(record.get("to_pipeline")))
    if destination is None or destination.get("status") != "current":
        blocking.append(
            _issue(
                "REVALIDATION_PIPELINE_INVALID",
                target=target,
                pipeline_id=record.get("to_pipeline"),
            )
        )
        return None
    cards = _id_map(registry.get("evidence_cards", []), "evidence_card_id")
    evidence = cards.get(str(record.get("evidence_card")))
    if (
        evidence is None
        or evidence.get("pipeline_id") != record.get("to_pipeline")
        or evidence.get("status") != "current"
        or evidence.get("provenance") != "confirmatory"
    ):
        blocking.append(_issue("REVALIDATION_EVIDENCE_INVALID", target=target))
        return None
    if target["kind"] == "claim_revision":
        live_support = any(
            relation.get("status") != "withdrawn"
            and relation.get("relation") == "supports"
            and relation.get("claim_revision_id") == target["id"]
            and relation.get("evidence_card_id") == record.get("evidence_card")
            for relation in registry.get("evidence_relations", [])
        )
        if not live_support:
            blocking.append(_issue("REVALIDATION_EVIDENCE_INVALID", target=target))
            return None

    resolved_value = None
    if (
        record.get("method") == "machine"
        and target["kind"] == "claim_revision"
        and record.get("result") != "not_revalidated"
    ):
        comparison = record.get("comparison")
        if not isinstance(comparison, dict) or not all(
            isinstance(comparison.get(field), (int, float))
            and not isinstance(comparison.get(field), bool)
            and math.isfinite(float(comparison[field]))
            for field in ("from_value", "to_value")
        ):
            blocking.append(_issue("REVALIDATION_COMPARISON_INVALID", target=target))
            return None
        accepted = _tolerance_accepts(
            comparison["from_value"], comparison["to_value"], str(record["tolerance"])
        )
        expected_result = "revalidated" if accepted else "changed"
        if record.get("result") != expected_result:
            blocking.append(
                _issue(
                    "REVALIDATION_RESULT_MISMATCH",
                    target=target,
                    expected=expected_result,
                    actual=record.get("result"),
                )
            )
            return None
    elif (
        record.get("method") == "machine"
        and target["kind"] == "reported_figure"
        and record.get("result") != "not_revalidated"
    ):
        try:
            resolved_value = _resolve_figure_value(registry, item, record)
        except ValueError as error:
            blocking.append(
                _issue("REVALIDATION_SOURCE_INVALID", target=target, detail=str(error))
            )
            return None
        accepted = _tolerance_accepts(
            item.get("value"), resolved_value, str(record["tolerance"])
        )
        expected_result = "revalidated" if accepted else "changed"
        if record.get("result") != expected_result:
            blocking.append(
                _issue(
                    "REVALIDATION_RESULT_MISMATCH",
                    target=target,
                    expected=expected_result,
                    actual=record.get("result"),
                )
            )
            return None
    return item, resolved_value


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
        validated = _valid_revalidation(registry, state, record, blocking)
        if validated is None or record.get("result") != "revalidated":
            continue
        target = record["target"]
        identifier = str(target["id"])
        collection = "claims" if target["kind"] == "claim_revision" else "reported_figures"
        item, resolved_value = validated
        reasons = item.get("_stale_reasons", [])
        if not reasons:
            blocking.append(_issue("REVALIDATION_NOT_REQUIRED", target=target))
            continue
        if "semantic_correction" in reasons and record["method"] == "machine":
            blocking.append(
                _issue("MACHINE_REVALIDATION_FORBIDDEN", target=target)
            )
            continue
        if target["kind"] == "reported_figure" and record["method"] == "machine":
            item["value"] = resolved_value
        if "semantic_correction" in reasons and record["method"] == "manual":
            reasons.remove("semantic_correction")
        if "pipeline_superseded" in reasons:
            reasons.remove("pipeline_superseded")
        item["pipeline_id"] = record["to_pipeline"]
        item["revalidation"] = copy.deepcopy(record)
        item["_validated_transition"] = {
            "from_pipeline": record["from_pipeline"],
            "to_pipeline": record["to_pipeline"],
            "evidence_card": record["evidence_card"],
            "performed_by": record["performed_by"],
            "performed_at": record["performed_at"],
        }
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


def _recompute_figures(
    state: dict,
    order: list[str],
    blocking: list[dict],
    derived: list[dict],
) -> None:
    figures = state["reported_figures"]
    for name in order:
        if not name.startswith("reported_figure:"):
            continue
        identifier = name.split(":", 1)[1]
        figure = figures[identifier]
        if not figure.get("derived_from"):
            continue
        upstream = figures[str(figure["derived_from"])]
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
            continue
        old_value = figure.get("value")
        old_pipeline = figure.get("pipeline_id")
        figure["value"] = recomputed
        transition = upstream.get("_validated_transition")
        if transition and str(old_pipeline) == str(transition["from_pipeline"]):
            figure["pipeline_id"] = transition["to_pipeline"]
            reasons = figure.setdefault("_stale_reasons", [])
            if "pipeline_superseded" in reasons:
                reasons.remove("pipeline_superseded")
            figure["revalidation"] = {
                "derived_from": upstream.get("figure_id"),
                "upstream_revalidation": copy.deepcopy(upstream.get("revalidation")),
            }
            figure["_validated_transition"] = copy.deepcopy(transition)
            if not reasons:
                figure["status"] = figure.get("_declared_status", "current")
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


def _challenge_cascade(
    registry: dict,
    state: dict,
    reports: list[dict],
    order: list[str],
    outgoing: dict[str, set[str]],
    derived: list[dict],
) -> dict[str, set[str]]:
    seeds: dict[str, set[str]] = defaultdict(set)
    for field in registry["derived_fields"]:
        if field.get("status") == "defective":
            identifier = str(field["derived_field_id"])
            seeds[f"derived_field:{identifier}"].add(f"defective:{identifier}")
    for item in reports:
        if item.get("code") == "SEMANTIC_DISCLOSURE_REQUIRED":
            fact_key = str(item["fact_key"])
            seeds[f"semantic_fact:{fact_key}"].add(f"semantic-change:{fact_key}")
    propagated = _propagate_reasons(order, outgoing, seeds)
    challenged: dict[str, set[str]] = defaultdict(set)
    for claim_id, claim in state["claims"].items():
        if claim.get("availability") == "stale":
            continue
        challenge_ids = propagated[f"claim_revision:{claim_id}"]
        challenged[claim_id].update(challenge_ids)
        for challenge_id in sorted(challenge_ids):
            code = (
                "DEFECTIVE_FIELD_CHALLENGE"
                if challenge_id.startswith("defective:")
                else "SEMANTIC_CHANGE_CHALLENGE"
            )
            derived.append(
                _issue(
                    code,
                    claim_revision_id=claim_id,
                    challenge_id=challenge_id,
                )
            )
    return challenged


def _gate_scope_matches(definition: dict, evaluation: dict) -> bool:
    evaluated = evaluation["evaluated_against"]
    pipeline_id = str(evaluation["pipeline_id"])
    for target in definition["applies_to"]:
        if target["kind"] != evaluated["kind"]:
            continue
        target_id = str(target["id"])
        evaluated_id = str(evaluated["id"])
        if evaluated_id == target_id or evaluated_id == f"{target_id}@{pipeline_id}":
            return True
    return False


def _change_matches_gate(change: dict, definition: dict, pipeline_id: str) -> bool:
    if str(change.get("pipeline_id")) != pipeline_id:
        return False
    return any(
        target.get("kind") == change.get("object_kind")
        and str(target.get("id")) == str(change.get("object_id"))
        for target in definition.get("applies_to", [])
    )


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
    cards = _id_map(registry.get("evidence_cards", []), "evidence_card_id")
    changes = _id_map(registry.get("changes", []), "change_id")
    claims_by_key: dict[str, list[dict]] = defaultdict(list)
    for claim in state["claims"].values():
        claims_by_key[str(claim.get("claim_key"))].append(claim)

    evaluation_pairs = {
        (str(item.get("gate_id")), str(item.get("pipeline_id")))
        for item in registry.get("gate_evaluations", [])
    }
    if checkpoint == "C":
        for gate_id in sorted(definitions):
            for pipeline_id in sorted(pipelines):
                if (gate_id, pipeline_id) not in evaluation_pairs:
                    blocking.append(
                        _issue(
                            "GATE_NOT_EVALUATED",
                            gate_id=gate_id,
                            pipeline_id=pipeline_id,
                        )
                    )

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
        if not _gate_scope_matches(definition, evaluation):
            blocking.append(
                _issue(
                    "GATE_SCOPE_MISMATCH",
                    gate_id=gate_id,
                    pipeline_id=pipeline_id,
                    evaluated_against=evaluation.get("evaluated_against"),
                )
            )
        evidence = cards.get(str(evaluation.get("evidence_card")))
        if (
            evidence is None
            or str(evidence.get("pipeline_id")) != pipeline_id
            or evidence.get("status") != "current"
        ):
            blocking.append(
                _issue(
                    "GATE_EVIDENCE_INVALID",
                    gate_id=gate_id,
                    pipeline_id=pipeline_id,
                    evidence_card=evaluation.get("evidence_card"),
                )
            )
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
                    if (
                        str(claim.get("pipeline_id")) == pipeline_id
                        and claim.get("availability") in {"retired", "withdrawn"}
                    ):
                        change = changes.get(str(claim.get("change_id")))
                        if (
                            change
                            and change.get("object_kind") == "claim_revision"
                            and change.get("object_id") == claim.get("claim_revision_id")
                            and str(change.get("pipeline_id")) == pipeline_id
                            and change.get("new_state") == claim.get("availability")
                        ):
                            moot_change = change["change_id"]
                        break
            elif target.get("kind") in {"dataset", "pipeline_stage"}:
                for change in changes.values():
                    if (
                        change.get("object_kind") == target.get("kind")
                        and change.get("object_id") == target.get("id")
                        and str(change.get("pipeline_id")) == pipeline_id
                        and change.get("new_state")
                        in {"retired", "withdrawn", "end_of_life"}
                    ):
                        moot_change = change["change_id"]
                        break
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
        declared_scope = coverage.get("declared_scope") if isinstance(coverage, dict) else None
        evaluated_scope = coverage.get("evaluated_scope") if isinstance(coverage, dict) else None
        if (
            not isinstance(coverage, dict)
            or coverage.get("complete") is not True
            or not isinstance(declared_scope, str)
            or not declared_scope.strip()
            or not isinstance(evaluated_scope, str)
            or not evaluated_scope.strip()
        ):
            blocking.append(
                _issue(
                    "GATE_COVERAGE_INCOMPLETE",
                    gate_id=gate_id,
                    pipeline_id=pipeline_id,
                )
            )
            status = "not_evaluated"
        elif declared_scope.strip() != evaluated_scope.strip():
            blocking.append(
                _issue(
                    "GATE_COVERAGE_MISMATCH",
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
            compensation_artifact = evaluation.get("compensation_artifact")
            required_artifact = definition.get("compensation", {}).get(
                "required_artifact"
            )
            artifact_path = (
                Path(registry.get("_root", ".")) / str(compensation_artifact)
                if compensation_artifact
                else None
            )
            if (
                not all(
                evaluation.get(field)
                for field in ("compensation_artifact", "accepted_by", "accepted_at")
                )
                or _as_datetime(evaluation.get("accepted_at")) is None
                or compensation_artifact != required_artifact
                or artifact_path is None
                or not artifact_path.is_file()
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
                valid_release = True
                if release.get("timing") not in {"pre_result", "post_result"}:
                    blocking.append(
                        _issue(
                            "GATE_RELEASE_TIMING_INVALID",
                            gate_id=gate_id,
                            pipeline_id=pipeline_id,
                        )
                    )
                    valid_release = False
                change = changes.get(str(release.get("triggering_change_id")))
                if (
                    change is None
                    or not _change_matches_gate(change, definition, pipeline_id)
                    or release.get("authorized_by") != change.get("authorized_by")
                ):
                    blocking.append(
                        _issue(
                            "GATE_CHANGE_INVALID",
                            gate_id=gate_id,
                            pipeline_id=pipeline_id,
                        )
                    )
                    valid_release = False
                release_evidence = cards.get(str(release.get("evidence_card")))
                if (
                    release_evidence is None
                    or str(release_evidence.get("pipeline_id")) != pipeline_id
                    or release_evidence.get("status") != "current"
                ):
                    blocking.append(
                        _issue(
                            "GATE_EVIDENCE_INVALID",
                            gate_id=gate_id,
                            pipeline_id=pipeline_id,
                            evidence_card=release.get("evidence_card"),
                        )
                    )
                    valid_release = False
                if valid_release:
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
    registry: dict,
    state: dict,
    derived_challenges: dict[str, set[str]],
    derived: list[dict],
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
        live_challenge_ids = {
            str(relation["relation_id"]) for relation in challenges
        } | set(derived_challenges.get(claim_id, set()))
        claim["_live_challenge_ids"] = sorted(live_challenge_ids)
        old_assessment = claim.get("assessment")
        if not supports:
            claim["assessment"] = "unresolved"
            if old_assessment != "unresolved":
                derived.append(
                    _issue("ASSESSMENT_UNRESOLVED", claim_revision_id=claim_id)
                )
        elif live_challenge_ids:
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
    live_challenges = set(claim.get("_live_challenge_ids", []))
    disclosed = {
        str(item["challenge_id"])
        for item in claim.get("challenge_disclosures", [])
        if item.get("adjacent") is True and _nonempty_string(item.get("paper_location"))
    }
    cards = _id_map(registry.get("evidence_cards", []), "evidence_card_id")
    disclosed.update(
        str(relation["relation_id"])
        for relation in registry.get("evidence_relations", [])
        if str(relation.get("claim_revision_id")) == claim_id
        and relation.get("status") != "withdrawn"
        and relation.get("relation") in {"challenges", "bounds"}
        and cards.get(str(relation.get("evidence_card_id")), {}).get("provenance")
        == "confirmatory"
        and relation.get("disclosure", {}).get("adjacent") is True
        and _nonempty_string(
            relation.get("disclosure", {}).get("paper_location")
        )
    )
    return bool(live_challenges) and live_challenges <= disclosed


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
            not item.get("_stale_reasons") and item.get("_validated_transition")
            for item in constituents
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
    structurally_valid = _structural_checks(registry, blocking)
    references_valid = False
    schema_valid = structurally_valid and not blocking
    if schema_valid:
        references_valid = _identity_reference_checks(registry, blocking)
    if not schema_valid or not references_valid:
        return {
            "checkpoint": checkpoint,
            "blocking": blocking,
            "reports": reports,
            "derived": derived,
            "state": _initial_state(registry),
        }
    corrected_fact_keys = _semantic_checks(registry, blocking, reports)
    order, outgoing = _dependency_topology(registry, blocking)
    state = _initial_state(registry)

    # Contractual cascade order: semantics, pipelines, challenges, moot gates,
    # live-support assessment, then publication. Revalidation is an authored
    # action applied after stale derivation and before downstream recomputation.
    _semantic_cascade(state, corrected_fact_keys, order, outgoing, derived)
    _pipeline_cascade(registry, state, derived)
    _revalidate(registry, state, blocking, derived)
    _recompute_figures(state, order, blocking, derived)
    _refresh_outputs_after_revalidation(state, derived)
    derived_challenges = _challenge_cascade(
        registry, state, reports, order, outgoing, derived
    )
    _gate_checks(registry, state, checkpoint, blocking, reports, derived)
    _applicability_checks(registry, blocking)
    _recompute_assessments(registry, state, derived_challenges, derived)
    _pipeline_binding_checks(registry, blocking, state)
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
    try:
        report = validate_registry(load_registry(args.registry_dir), args.checkpoint)
    except Exception as error:  # Defensive JSON boundary for arbitrary registry input.
        report = {
            "checkpoint": args.checkpoint,
            "blocking": [
                _issue(
                    "REGISTRY_VALIDATION_ERROR",
                    detail=f"{type(error).__name__}: {error}",
                )
            ],
            "reports": [],
            "derived": [],
            "state": {},
        }
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
