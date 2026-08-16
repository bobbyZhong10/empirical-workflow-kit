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
from functools import lru_cache
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

ASSERTION_TYPES = {
    "world",
    "negative",
    "methodological",
    "discriminating",
    "model_internal",
    "hypothesis",
}
ASSERTION_SECTION_ROLES = {
    "title",
    "abstract",
    "introduction",
    "results",
    "mechanism",
    "discussion",
    "conclusion",
}
ASSERTION_TIERS = {"T0": 4, "T1": 3, "T2": 2, "T3": 1, "T4": 0}
QUALIFIER_SCOPES = {"sentence", "paragraph", "section", "cross_reference"}
COUNTEREVIDENCE_PROMINENCE = {
    "parenthetical",
    "clause_appended",
    "separate_contrastive_sentence",
    "footnote",
    "appendix",
}
LEXICAL_CLASSES = {
    "causal",
    "scope_qualifying",
    "evidential_weak",
    "evidential_moderate",
    "evidential_strong",
    "concessive",
    "descriptive",
}

# Historical class names accepted in project configuration. ``associational``
# and ``framing`` conflated two distinct jobs: an evidential frame that lowers
# what a sentence promises, and a concessive marker that only signals where a
# recovery could follow. They are kept as aliases so existing configuration
# keeps working.
LEXICAL_CLASS_ALIASES = {
    "associational": "evidential_strong",
    "framing": "concessive",
}
DEFAULT_LEXICAL_MARKERS: dict[str, tuple[str, ...]] = {
    # Verbs that carry causal force. Matching is inflection tolerant, so one
    # lemma covers its ordinary forms; irregular participles are listed.
    "causal": (
        "cause",
        "causal effect",
        "effect on",
        "impact on",
        "affect",
        "increase",
        "decrease",
        "reduce",
        "raise",
        "lower",
        "boost",
        "generate",
        "induce",
        "drive",
        "driven",
        "lead to",
        "led to",
        "result in",
        "produce",
        "improve",
        "worsen",
        "enhance",
        "mitigate",
        "attenuate",
        "weaken",
        "strengthen",
        "expand",
        "shift",
        "yield",
        "motivate",
        "differentiate",
        "substitute",
        "crowd out",
        "offset",
        "amplify",
        "dampen",
        "explain",
        "account for",
        "attributable to",
        "translate into",
        "optimize",
        "has a positive effect on",
        "has a negative effect on",
    ),
    # Qualifiers that narrow the population, period, or level a sentence
    # speaks about. ``on average`` is deliberately absent: it states what the
    # estimate aggregates over, not who the claim is about, and admitting it
    # would qualify almost every effect sentence.
    "scope_qualifying": (
        "among",
        "within",
        "in our sample",
        "in the sample",
        "for the study population",
        "conditional on",
        "only for",
        "restricted to",
        "limited to",
        "during the study period",
        "under the registered scope",
        "all else equal",
        "all else being equal",
        "ceteris paribus",
        "bounded by",
    ),
    # Evidential frames, graded by how much they lower what the sentence
    # promises. Weak frames barely lower it at all: in the reference corpus
    # "the results indicate that X increases Y" reads as an unqualified causal
    # commitment.
    "evidential_weak": (
        "indicate",
        "show",
        "shown",
        "demonstrate",
        "document",
        "establish",
        "reveal",
        "confirm",
    ),
    "evidential_moderate": (
        "suggest",
        "imply",
        "point to",
        "find evidence that",
        "provide evidence that",
        "lend support to",
        "provide support for",
        "is evidence that",
    ),
    # Strong frames put the sentence outside causal commitment altogether,
    # including the self-deprecating noun phrases that downgrade hardest.
    "evidential_strong": (
        "associated with",
        "association",
        "correlate with",
        "correlated with",
        "related to",
        "consistent with",
        "appear to",
        "appears to",
        "seem to",
        "seems to",
        "we interpret",
        "we attribute",
        "we speculate",
        "we conjecture",
        "we surmise",
        "we posit",
        "we hypothesize",
        "reflect",
        "may",
        "might",
        "could",
        "possibly",
        "plausibly",
        "anecdotal evidence",
        "suggestive evidence",
        "preliminary evidence",
        "circumstantial",
        "back-of-the-envelope",
        "illustrative",
    ),
    # Descriptive statements make no inferential promise.
    "descriptive": (
        "we report",
        "we document",
        "observed",
        "describe",
        "descriptive",
    ),
    # Concessive markers locate where an author gives ground. They are used to
    # detect immediate recovery and never change what a sentence promises: a
    # sentence that merely contains the word "limitation" is not hedged.
    "concessive": (
        "although",
        "though",
        "despite",
        "even though",
        "admittedly",
        "notwithstanding",
        "granted that",
        "granting that",
        "limitation",
        "caveat",
        "not significant",
        "insignificant",
        "does not survive",
        "fails to",
        "cannot reject",
        "no effect",
        "imprecise",
    ),
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
            "writing_strength": {},
            "lexical_markers": None,
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
                "writing_strength",
                "lexical_markers",
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


def _finite_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _line_range(anchor: Any) -> tuple[int, int] | None:
    """Parse a human-editable one-based line range, if ``anchor`` is one."""

    if isinstance(anchor, dict):
        if set(anchor) == {"start_line", "end_line"}:
            start, end = anchor["start_line"], anchor["end_line"]
        elif set(anchor) == {"line_start", "line_end"}:
            start, end = anchor["line_start"], anchor["line_end"]
        else:
            return None
        if (
            isinstance(start, int)
            and not isinstance(start, bool)
            and isinstance(end, int)
            and not isinstance(end, bool)
            and 1 <= start <= end
        ):
            return start, end
        return None
    if not isinstance(anchor, str):
        return None
    match = re.fullmatch(
        r"(?:lines?\s*:\s*)?L?(\d+)(?:\s*-\s*L?(\d+))?",
        anchor.strip(),
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    start = int(match.group(1))
    end = int(match.group(2) or match.group(1))
    return (start, end) if 1 <= start <= end else None


def _valid_anchor_shape(anchor: Any) -> bool:
    return _nonempty_string(anchor) or _line_range(anchor) is not None


def _valid_scope_declaration_shape(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    coverage = value.get("coverage")
    return (
        _nonempty_string(value.get("path"))
        and _valid_anchor_shape(value.get("anchor"))
        and isinstance(coverage, dict)
        and _nonempty_string(coverage.get("path"))
        and _valid_anchor_shape(coverage.get("start_anchor"))
        and _valid_anchor_shape(coverage.get("end_anchor"))
    )


def _lexical_configuration(registry: dict) -> Any:
    direct = registry.get("lexical_markers")
    if direct is not None:
        return direct
    writing_strength = registry.get("writing_strength", {})
    if isinstance(writing_strength, dict):
        return writing_strength.get(
            "lexical_markers", writing_strength.get("lexical_classes", {})
        )
    return None


def _valid_marker_configuration(value: Any) -> bool:
    if value in (None, {}):
        return True
    if not isinstance(value, dict) or not set(value) <= (
        LEXICAL_CLASSES | set(LEXICAL_CLASS_ALIASES)
    ):
        return False
    for markers in value.values():
        if _string_list(markers):
            continue
        if not isinstance(markers, dict) or not set(markers) <= {
            "add",
            "remove",
            "replace",
        }:
            return False
        if not all(_string_list(items) for items in markers.values()):
            return False
    return True


def _assertion_site_schema_checks(
    registry: dict, claim_index: int, claim: dict, blocking: list[dict]
) -> None:
    if "assertion_sites" not in claim:
        return
    sites = claim.get("assertion_sites")
    location = f"claims[{claim_index}].assertion_sites"
    if not isinstance(sites, list):
        _schema_error(blocking, location, "must be a list")
        return
    required = {
        "path",
        "anchor",
        "section_role",
        "assertion_type",
        "declared_tier",
        "qualifier_scope",
        "counterevidence_prominence",
        "underlying_precision",
        "scope_declaration",
        "power_basis",
    }
    for site_index, site in enumerate(sites):
        site_location = f"{location}[{site_index}]"
        if not isinstance(site, dict):
            _schema_error(blocking, site_location, "record must be a mapping")
            continue
        missing = sorted(required - set(site))
        if missing:
            _schema_error(
                blocking,
                site_location,
                f"missing required fields: {', '.join(missing)}",
            )
            continue
        if not _nonempty_string(site.get("path")):
            _schema_error(blocking, f"{site_location}.path", "must be a relative path")
        if not _valid_anchor_shape(site.get("anchor")):
            _schema_error(
                blocking,
                f"{site_location}.anchor",
                "must be a nonempty stable marker or positive line range",
            )
        section_role = site.get("section_role")
        if not isinstance(section_role, str) or section_role not in ASSERTION_SECTION_ROLES:
            _schema_error(
                blocking, f"{site_location}.section_role", "invalid section role"
            )
        assertion_type = site.get("assertion_type")
        if not isinstance(assertion_type, str) or assertion_type not in ASSERTION_TYPES:
            _schema_error(
                blocking, f"{site_location}.assertion_type", "invalid assertion type"
            )
        declared_tier = site.get("declared_tier")
        if assertion_type == "world" and (
            not isinstance(declared_tier, str) or declared_tier not in ASSERTION_TIERS
        ):
            _schema_error(
                blocking,
                f"{site_location}.declared_tier",
                "world assertions require exactly one T0--T4 tier",
            )
        qualifier_scope = site.get("qualifier_scope")
        if not isinstance(qualifier_scope, str) or qualifier_scope not in QUALIFIER_SCOPES:
            _schema_error(
                blocking,
                f"{site_location}.qualifier_scope",
                "invalid qualifier scope",
            )
        prominence = site.get("counterevidence_prominence")
        if prominence is not None and (
            not isinstance(prominence, str)
            or prominence not in COUNTEREVIDENCE_PROMINENCE
        ):
            _schema_error(
                blocking,
                f"{site_location}.counterevidence_prominence",
                "invalid counterevidence prominence",
            )
        precision = site.get("underlying_precision")
        precision_keys = {
            "significant_at",
            "has_sampling_distribution",
            "n",
            "estimate_id",
        }
        if not isinstance(precision, dict) or not precision_keys <= set(precision):
            _schema_error(
                blocking,
                f"{site_location}.underlying_precision",
                "requires explicit significant_at, has_sampling_distribution, n, and estimate_id values",
            )
        else:
            significant_at = precision.get("significant_at")
            sample_size = precision.get("n")
            if significant_at is not None and not (
                _finite_number(significant_at) and 0 < float(significant_at) <= 1
            ):
                _schema_error(
                    blocking,
                    f"{site_location}.underlying_precision.significant_at",
                    "must be null or a finite probability in (0, 1]",
                )
            distribution = precision.get("has_sampling_distribution")
            if distribution is not True and distribution is not False and distribution is not None:
                _schema_error(
                    blocking,
                    f"{site_location}.underlying_precision.has_sampling_distribution",
                    "must be true, false, or null",
                )
            if sample_size is not None and not (
                isinstance(sample_size, int)
                and not isinstance(sample_size, bool)
                and sample_size > 0
            ):
                _schema_error(
                    blocking,
                    f"{site_location}.underlying_precision.n",
                    "must be null or a positive integer",
                )
            if precision.get("estimate_id") is not None and not _nonempty_string(
                precision.get("estimate_id")
            ):
                _schema_error(
                    blocking,
                    f"{site_location}.underlying_precision.estimate_id",
                    "must be null or a nonempty string",
                )
        scope = site.get("scope_declaration")
        if site.get("qualifier_scope") == "sentence":
            if scope is not None:
                _schema_error(
                    blocking,
                    f"{site_location}.scope_declaration",
                    "sentence-scoped assertions require null",
                )
        elif not _valid_scope_declaration_shape(scope):
            _schema_error(
                blocking,
                f"{site_location}.scope_declaration",
                "non-sentence scope requires a declaration and closed coverage range",
            )
        power = site.get("power_basis")
        if power is not None and not isinstance(power, dict):
            _schema_error(
                blocking, f"{site_location}.power_basis", "must be null or a mapping"
            )
        upgrade = site.get("upgrade_justification")
        if upgrade is not None:
            if not isinstance(upgrade, dict):
                _schema_error(
                    blocking,
                    f"{site_location}.upgrade_justification",
                    "must be null or a mapping",
                )
        disclosure = site.get("counterevidence_disclosure")
        if disclosure is not None and not (
            isinstance(disclosure, dict)
            and _nonempty_string(disclosure.get("path"))
            and _valid_anchor_shape(disclosure.get("anchor"))
        ):
            _schema_error(
                blocking,
                f"{site_location}.counterevidence_disclosure",
                "must be null or a path/anchor mapping",
            )
        for field in ("alternative_explanation",):
            if site.get(field) is not None and not _nonempty_string(site.get(field)):
                _schema_error(
                    blocking, f"{site_location}.{field}", "must be null or a string"
                )
        as_modeled = site.get("as_modeled")
        if as_modeled is not True and as_modeled is not False and as_modeled is not None:
            _schema_error(
                blocking,
                f"{site_location}.as_modeled",
                "must be true, false, or null",
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
    writing_strength = registry.get("writing_strength")
    if writing_strength is not None and not isinstance(writing_strength, dict):
        _schema_error(blocking, "writing_strength", "must be a mapping")
    if not _valid_marker_configuration(_lexical_configuration(registry)):
        _schema_error(
            blocking,
            "writing_strength.lexical_markers",
            "must contain only causal, scope_qualifying, associational, descriptive, and framing string lists",
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
        _assertion_site_schema_checks(registry, index, claim, blocking)
    for collection in ("evidence_cards", "derived_fields"):
        for index, item in enumerate(registry[collection]):
            if not _dependency_list(item.get("depends_on", [])):
                _schema_error(
                    blocking,
                    f"{collection}[{index}].depends_on",
                    "must be a list of kind/id mappings",
                )
    for index, card in enumerate(registry["evidence_cards"]):
        endpoint = card.get("comparison_endpoint")
        if endpoint is not None and not (
            isinstance(endpoint, dict)
            and set(endpoint) == {"artifact", "locator"}
            and _nonempty_string(endpoint.get("artifact"))
            and _nonempty_string(endpoint.get("locator"))
        ):
            _schema_error(
                blocking,
                f"evidence_cards[{index}].comparison_endpoint",
                "requires exactly one nonempty artifact and locator",
            )
        comparison = card.get("machine_comparison")
        if comparison is None:
            continue
        if not (
            isinstance(comparison, dict)
            and set(comparison)
            == {"source_evidence_card", "destination_evidence_card"}
            and _nonempty_string(comparison.get("source_evidence_card"))
            and _nonempty_string(comparison.get("destination_evidence_card"))
        ):
            _schema_error(
                blocking,
                f"evidence_cards[{index}].machine_comparison",
                "requires exactly source and destination evidence-card references",
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
        if figure.get("derived_from"):
            transform = figure.get("transform")
            if not (
                isinstance(transform, dict)
                and transform.get("operation")
                in {"multiply", "divide", "add", "subtract"}
                and isinstance(transform.get("operand"), (int, float))
                and not isinstance(transform.get("operand"), bool)
                and math.isfinite(float(transform["operand"]))
                and not (
                    transform.get("operation") == "divide"
                    and transform.get("operand") == 0
                )
            ):
                _schema_error(
                    blocking,
                    f"reported_figures[{index}].transform",
                    "derived figures require a supported finite arithmetic transform",
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
        if isinstance(coverage, dict):
            for field in ("declared_scope", "evaluated_scope"):
                if field in coverage and not _nonempty_string(coverage[field]):
                    _schema_error(
                        blocking,
                        f"gate_evaluations[{index}].coverage.{field}",
                        "must be a nonempty string",
                    )
        if evaluation.get("status") == "inapplicable":
            for field in ("applicability_reason", "declared_by", "accepted_by"):
                if field in evaluation and not _nonempty_string(evaluation[field]):
                    _schema_error(
                        blocking,
                        f"gate_evaluations[{index}].{field}",
                        "must be a nonempty string",
                    )
        if evaluation.get("status") == "satisfied":
            for field in ("compensation_artifact", "accepted_by"):
                if field in evaluation and not _nonempty_string(evaluation[field]):
                    _schema_error(
                        blocking,
                        f"gate_evaluations[{index}].{field}",
                        "must be a nonempty string",
                    )
            if "accepted_at" in evaluation and _as_datetime(
                evaluation["accepted_at"]
            ) is None:
                _schema_error(
                    blocking,
                    f"gate_evaluations[{index}].accepted_at",
                    "must be an ISO timestamp",
                )
        if evaluation.get("status") == "released" and isinstance(
            evaluation.get("release"), dict
        ):
            for field in (
                "triggering_change_id",
                "reason",
                "authorized_by",
                "timing",
                "evidence_card",
                "compensation_disposition",
            ):
                if field in evaluation["release"] and not _nonempty_string(
                    evaluation["release"][field]
                ):
                    _schema_error(
                        blocking,
                        f"gate_evaluations[{index}].release.{field}",
                        "must be a nonempty string",
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
    for index, decision in enumerate(registry["semantic_equivalence_decisions"]):
        revisions = decision.get("fact_revision_ids")
        valid_range = decision.get("valid_range")
        if not (
            _nonempty_string(decision.get("field"))
            and _string_list(revisions)
            and len(revisions) >= 2
            and len(revisions) == len(set(revisions))
            and isinstance(valid_range, list)
            and len(valid_range) == 2
            and _as_date(valid_range[0]) is not None
            and _as_date(valid_range[1]) is not None
            and _as_date(valid_range[0]) <= _as_date(valid_range[1])
        ):
            _schema_error(
                blocking,
                f"semantic_equivalence_decisions[{index}]",
                "requires a field, two or more unique fact revisions, and an ISO date window",
            )
        decision_value = decision.get("decision")
        if not _nonempty_string(decision_value) or decision_value not in {
            "equivalent",
            "interchangeable",
            "distinct",
            "not_equivalent",
        }:
            _schema_error(
                blocking,
                f"semantic_equivalence_decisions[{index}].decision",
                "must be an equivalence decision enum",
            )
        if (
            not _nonempty_string(decision.get("decided_by"))
            or not _nonempty_string(decision.get("decided_at"))
            or _as_datetime(decision.get("decided_at")) is None
            or not _nonempty_string(decision.get("evidence_card"))
        ):
            _schema_error(
                blocking,
                f"semantic_equivalence_decisions[{index}]",
                "requires author, ISO timestamp, and evidence card",
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
        if item.get("status") == "inapplicable":
            for field in ("applicability_reason", "declared_by", "accepted_by"):
                if field in item and not _nonempty_string(item[field]):
                    _schema_error(
                        blocking,
                        f"applicability[{index}].{field}",
                        "must be a nonempty string",
                    )
        if item.get("record_type") == "design_grid":
            dimensions = item.get("dimensions")
            cells = item.get("empty_cells")
            valid_dimensions = (
                _string_list(dimensions)
                and bool(dimensions)
                and len(dimensions) == len(set(dimensions))
            )
            valid_cells = isinstance(cells, list) and all(
                isinstance(cell, dict)
                and isinstance(cell.get("coordinates"), dict)
                and set(cell["coordinates"]) == set(dimensions or [])
                and all(
                    isinstance(value, (str, int, float, bool))
                    and not (isinstance(value, float) and not math.isfinite(value))
                    for value in cell["coordinates"].values()
                )
                and _nonempty_string(cell.get("reason"))
                for cell in cells or []
            )
            if not (valid_dimensions and valid_cells):
                _schema_error(
                    blocking,
                    f"applicability[{index}]",
                    "design_grid requires unique dimensions and coherent empty-cell records",
                )
        if item.get("record_type") == "sibling_parity":
            dimensions = item.get("dimensions")
            results = item.get("dimension_results")
            result_dimensions = [
                result.get("dimension")
                for result in results or []
                if isinstance(result, dict)
            ]
            if not (
                _string_list(dimensions)
                and bool(dimensions)
                and len(dimensions) == len(set(dimensions))
                and isinstance(results, list)
                and results
                and all(
                    isinstance(result, dict)
                    and _nonempty_string(result.get("dimension"))
                    and result.get("result") in {"match", "diverge"}
                    for result in results
                )
                and len(result_dimensions) == len(set(result_dimensions))
                and set(result_dimensions) == set(dimensions)
                and _nonempty_string(item.get("consequence_assessment"))
            ):
                _schema_error(
                    blocking,
                    f"applicability[{index}]",
                    "sibling_parity requires match/diverge results and consequence assessment",
                )
    for index, record in enumerate(registry["revalidations"]):
        target = record.get("target")
        if not (
            isinstance(target, dict)
            and set(target) == {"kind", "id"}
            and target.get("kind") in {"claim_revision", "reported_figure"}
            and _nonempty_string(target.get("id"))
        ):
            _schema_error(
                blocking,
                f"revalidations[{index}].target",
                "must contain exactly a supported kind and nonempty string id",
            )
        for field in (
            "from_pipeline",
            "to_pipeline",
            "method",
            "result",
            "performed_by",
            "performed_at",
            "evidence_card",
        ):
            if not _nonempty_string(record.get(field)):
                _schema_error(
                    blocking,
                    f"revalidations[{index}].{field}",
                    "must be a nonempty string",
                )
        if (
            record.get("method") == "machine"
            and not _nonempty_string(record.get("tolerance"))
        ):
            _schema_error(
                blocking,
                f"revalidations[{index}].tolerance",
                "machine revalidation requires a nonempty string tolerance",
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
        allowed_states = {
            "claim_revision": {"current", "superseded", "retired", "withdrawn"},
            "claim_key": {"changed", "revised", "retired", "withdrawn"},
            "dataset": {"changed", "retired", "withdrawn", "end_of_life"},
            "pipeline_stage": {
                "changed",
                "retired",
                "withdrawn",
                "end_of_life",
            },
        }
        if change.get("new_state") not in allowed_states.get(
            change.get("object_kind"), set()
        ):
            _schema_error(
                blocking,
                f"changes[{index}].new_state",
                "state is invalid for changed-object kind",
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
    semantic_fields = {str(fact.get("field")) for fact in registry["semantic_facts"]}
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
        seen_sites: set[str] = set()
        for site in claim.get("assertion_sites", []):
            reference = _site_reference(site)
            if reference in seen_sites:
                blocking.append(
                    _issue(
                        "DUPLICATE_ASSERTION_SITE",
                        claim_revision_id=claim.get("claim_revision_id"),
                        site=reference,
                    )
                )
            seen_sites.add(reference)
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
        if claim.get("change_id"):
            require(
                changes,
                claim["change_id"],
                f"claims.{claim.get('claim_revision_id')}.change_id",
            )
            change = changes.get(str(claim["change_id"]))
            if change and not (
                change.get("object_kind") == "claim_revision"
                and change.get("object_id") == claim.get("claim_revision_id")
                and str(change.get("pipeline_id")) == str(claim.get("pipeline_id"))
                and change.get("new_state") == claim.get("availability")
            ):
                blocking.append(
                    _issue(
                        "CLAIM_CHANGE_INVALID",
                        claim_revision_id=claim.get("claim_revision_id"),
                        change_id=claim.get("change_id"),
                    )
                )
    for card in registry["evidence_cards"]:
        require(pipelines, card.get("pipeline_id"), f"evidence_cards.{card.get('evidence_card_id')}.pipeline_id")
        endpoint = card.get("comparison_endpoint")
        if isinstance(endpoint, dict):
            try:
                _resolve_artifact_locator(registry, endpoint)
            except ValueError as error:
                blocking.append(
                    _issue(
                        "REVALIDATION_SOURCE_INVALID",
                        endpoint_evidence_card=card.get("evidence_card_id"),
                        detail=str(error),
                    )
                )
        comparison = card.get("machine_comparison")
        if isinstance(comparison, dict):
            source_id = comparison.get("source_evidence_card")
            destination_id = comparison.get("destination_evidence_card")
            require(
                cards,
                source_id,
                f"evidence_cards.{card.get('evidence_card_id')}.machine_comparison.source_evidence_card",
            )
            require(
                cards,
                destination_id,
                f"evidence_cards.{card.get('evidence_card_id')}.machine_comparison.destination_evidence_card",
            )
            source = cards.get(str(source_id))
            destination = cards.get(str(destination_id))
            endpoint_records = (source, destination)
            endpoint_specs = [
                endpoint.get("comparison_endpoint")
                for endpoint in endpoint_records
                if endpoint is not None
            ]
            same_endpoint = False
            if len(endpoint_specs) == 2:
                try:
                    same_endpoint = _artifact_endpoint_identity(
                        registry, endpoint_specs[0]
                    ) == _artifact_endpoint_identity(registry, endpoint_specs[1])
                except ValueError:
                    # The eager endpoint resolver above records the stable source error.
                    pass
            if (
                source_id == destination_id
                or destination_id != card.get("evidence_card_id")
                or any(
                    endpoint is None
                    or endpoint.get("status") != "current"
                    or endpoint.get("provenance") != "confirmatory"
                    or not isinstance(endpoint.get("comparison_endpoint"), dict)
                    for endpoint in endpoint_records
                )
                or len(endpoint_specs) != 2
                or same_endpoint
            ):
                blocking.append(
                    _issue(
                        "REVALIDATION_COMPARISON_INVALID",
                        evidence_card_id=card.get("evidence_card_id"),
                    )
                )
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
    equivalence_scopes: set[tuple[str, tuple[str, ...], tuple[str, str]]] = set()
    for decision in registry["semantic_equivalence_decisions"]:
        field = str(decision.get("field"))
        require(semantic_fields, field, "semantic_equivalence_decisions.field")
        revisions = [str(item) for item in decision.get("fact_revision_ids", [])]
        for revision_id in revisions:
            require(
                fact_revisions,
                revision_id,
                "semantic_equivalence_decisions.fact_revision_ids",
            )
        require(
            cards,
            decision.get("evidence_card"),
            "semantic_equivalence_decisions.evidence_card",
        )
        evidence = cards.get(str(decision.get("evidence_card")))
        resolved_facts = [fact_revisions.get(revision_id) for revision_id in revisions]
        dependency_pairs = {
            (str(item.get("kind")), str(item.get("id")))
            for item in (evidence or {}).get("depends_on", [])
        }
        fact_key_scope = {
            str(fact.get("fact_key")) for fact in resolved_facts if fact is not None
        }
        relevant_evidence = ("raw_field", field) in dependency_pairs or all(
            ("semantic_fact", fact_key) in dependency_pairs
            for fact_key in fact_key_scope
        )
        if evidence and (
            evidence.get("status") != "current"
            or evidence.get("provenance") != "confirmatory"
            or any(fact and str(fact.get("field")) != field for fact in resolved_facts)
            or not relevant_evidence
        ):
            blocking.append(
                _issue(
                    "SEMANTIC_EQUIVALENCE_EVIDENCE_INVALID",
                    field=field,
                    fact_revision_ids=revisions,
                )
            )
        valid_range = tuple(str(item) for item in decision.get("valid_range", []))
        scope = (field, tuple(revisions), valid_range)
        if scope in equivalence_scopes:
            blocking.append(
                _issue(
                    "DUPLICATE_SEMANTIC_EQUIVALENCE_DECISION",
                    field=field,
                    fact_revision_ids=revisions,
                    valid_range=list(valid_range),
                )
            )
        equivalence_scopes.add(scope)
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
    equivalent_windows = {
        (
            str(item.get("field")),
            tuple(str(revision) for revision in item.get("fact_revision_ids", [])),
            tuple(str(bound) for bound in item.get("valid_range", [])),
        )
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
        revision_ids = tuple(
            str(item[2].get("fact_revision_id")) for item in intervals
        )
        exact_window = (
            str(field),
            revision_ids,
            (window_start.isoformat(), window_end.isoformat()),
        )
        if (
            len(intervals) > 1
            and not overlap
            and not gap
            and exact_window not in equivalent_windows
        ):
            reports.append(
                _issue(
                    "SEMANTIC_DISCLOSURE_REQUIRED",
                    field=field,
                    fact_key=fact_key,
                    revisions=list(revision_ids),
                )
            )
    return corrected_fact_keys


def _dependency_topology(
    registry: dict, blocking: list[dict]
) -> tuple[list[str], dict[str, set[str]]]:
    """Build the reason-propagation DAG, excluding identity lineage edges."""

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
        node("claim_revision", claim["claim_revision_id"])
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


def _identity_cycle_checks(registry: dict, blocking: list[dict]) -> None:
    """Validate lineage/reference cycles without treating lineage as evidence."""

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

    for claim in registry["claims"]:
        destination = node("claim_lineage", claim["claim_revision_id"])
        if claim.get("supersedes"):
            edge(node("claim_lineage", claim["supersedes"]), destination)
    for fact in registry["semantic_facts"]:
        destination = node("semantic_lineage", fact["fact_revision_id"])
        if fact.get("supersedes"):
            edge(node("semantic_lineage", fact["supersedes"]), destination)
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
    for figure in registry["reported_figures"]:
        destination = node("reported_figure", figure["figure_id"])
        if figure.get("derived_from"):
            edge(node("reported_figure", figure["derived_from"]), destination)
    for item in registry["applicability"]:
        destination = node("applicability", item["requirement_id"])
        for dependency in item.get("substituted_by", []):
            edge(node("applicability", dependency), destination)

    ready = sorted(name for name, degree in indegree.items() if degree == 0)
    visited = 0
    while ready:
        current = ready.pop(0)
        visited += 1
        for destination in sorted(outgoing[current]):
            indegree[destination] -= 1
            if indegree[destination] == 0:
                ready.append(destination)
                ready.sort()
    if visited != len(indegree):
        blocking.append(
            _issue(
                "REFERENCE_CYCLE",
                nodes=sorted(name for name, degree in indegree.items() if degree > 0),
            )
        )


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
    if not isinstance(record.get("method"), str) or record.get("method") not in {
        "machine",
        "manual",
    }:
        blocking.append(_issue("REVALIDATION_METHOD_INVALID", target=target))
        return None
    if not isinstance(record.get("result"), str) or record.get("result") not in {
        "revalidated",
        "changed",
        "not_revalidated",
    }:
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
        comparison = evidence.get("machine_comparison")
        source_id = (
            comparison.get("source_evidence_card")
            if isinstance(comparison, dict)
            else None
        )
        destination_id = (
            comparison.get("destination_evidence_card")
            if isinstance(comparison, dict)
            else None
        )
        source_evidence = cards.get(str(source_id))
        destination_evidence = cards.get(str(destination_id))
        source_endpoint = (
            source_evidence.get("comparison_endpoint")
            if source_evidence is not None
            else None
        )
        destination_endpoint = (
            destination_evidence.get("comparison_endpoint")
            if destination_evidence is not None
            else None
        )
        if not (
            isinstance(comparison, dict)
            and source_id != destination_id
            and destination_id == record.get("evidence_card")
            and source_evidence is not None
            and destination_evidence is not None
            and source_evidence.get("pipeline_id") == record.get("from_pipeline")
            and destination_evidence.get("pipeline_id") == record.get("to_pipeline")
            and source_evidence.get("status") == "current"
            and destination_evidence.get("status") == "current"
            and source_evidence.get("provenance") == "confirmatory"
            and destination_evidence.get("provenance") == "confirmatory"
            and isinstance(source_endpoint, dict)
            and isinstance(destination_endpoint, dict)
        ):
            blocking.append(_issue("REVALIDATION_COMPARISON_INVALID", target=target))
            return None
        try:
            if _artifact_endpoint_identity(
                registry, source_endpoint
            ) == _artifact_endpoint_identity(registry, destination_endpoint):
                blocking.append(
                    _issue("REVALIDATION_COMPARISON_INVALID", target=target)
                )
                return None
            from_value = _resolve_artifact_locator(registry, source_endpoint)
            to_value = _resolve_artifact_locator(registry, destination_endpoint)
        except ValueError as error:
            blocking.append(
                _issue(
                    "REVALIDATION_SOURCE_INVALID",
                    target=target,
                    detail=str(error),
                )
            )
            return None
        resolved_value = {"from_value": from_value, "to_value": to_value}
        accepted = _tolerance_accepts(
            from_value, to_value, record["tolerance"]
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
            item.get("value"), resolved_value, record["tolerance"]
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


def _preflight_revalidations(
    registry: dict, state: dict, blocking: list[dict]
) -> dict[str, tuple[dict, tuple[dict, Any]]]:
    """Validate every authored revalidation before graph evaluation."""

    validated: dict[str, tuple[dict, tuple[dict, Any]]] = {}
    for record in registry["revalidations"]:
        target = record["target"]
        result = _valid_revalidation(registry, state, record, blocking)
        if result is not None:
            validated[f"{target['kind']}:{target['id']}"] = (record, result)
    return validated


def _tolerance_accepts(old: Any, new: Any, expression: str) -> bool:
    if (
        not isinstance(old, (int, float))
        or not isinstance(new, (int, float))
        or not isinstance(expression, str)
    ):
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
    locator: Any = figure.get("source_locator")
    if isinstance(locator, dict):
        locator = locator.get(record["to_pipeline"])
    return _resolve_artifact_locator(
        registry,
        {"artifact": artifact_name, "locator": locator},
    )


def _canonical_artifact_endpoint(
    registry: dict, source: dict
) -> tuple[Path, tuple[str, ...]]:
    """Return the resolved file and canonical locator tokens for an endpoint."""

    artifact_name = source.get("artifact")
    locator = source.get("locator")
    if not _nonempty_string(artifact_name) or not _nonempty_string(locator):
        raise ValueError("artifact and locator must be nonempty strings")
    artifact_path = Path(artifact_name)
    if not artifact_path.is_absolute():
        artifact_path = Path(registry.get("_root", ".")) / artifact_path
    try:
        artifact_path = artifact_path.resolve(strict=True)
    except OSError as error:
        raise ValueError(
            f"destination source artifact not found: {artifact_name}"
        ) from error
    if not artifact_path.is_file():
        raise ValueError(f"destination source artifact not found: {artifact_name}")

    parts = tuple(
        part.replace("~1", "/").replace("~0", "~")
        for part in (
            locator.lstrip("/").split("/")
            if locator.startswith("/")
            else locator.split(".")
        )
    )
    return artifact_path, parts


def _artifact_endpoint_identity(
    registry: dict, source: dict
) -> tuple[tuple[int, int], tuple[str, ...]]:
    """Return underlying file identity plus canonical locator token sequence."""

    artifact_path, parts = _canonical_artifact_endpoint(registry, source)
    payload = _load_artifact_payload(artifact_path)
    _, parts = _traverse_artifact_locator(payload, parts, source["locator"])
    stat = artifact_path.stat()
    return (stat.st_dev, stat.st_ino), parts


def _load_artifact_payload(artifact_path: Path) -> Any:
    try:
        return yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise ValueError(f"destination source artifact is unreadable: {error}") from error


def _traverse_artifact_locator(
    payload: Any, parts: tuple[str, ...], locator: str
) -> tuple[Any, tuple[str, ...]]:
    """Resolve locator tokens while enforcing one spelling for list indexes."""

    value = payload
    canonical_parts: list[str] = []
    try:
        for part in parts:
            if isinstance(value, list):
                if re.fullmatch(r"(?:0|[1-9][0-9]*)", part) is None:
                    raise ValueError(
                        "source_locator list indexes must use canonical "
                        "nonnegative decimal syntax"
                    )
                index = int(part)
                value = value[index]
                canonical_parts.append(str(index))
            else:
                value = value[part]
                canonical_parts.append(part)
    except (KeyError, IndexError, TypeError) as error:
        raise ValueError(f"source_locator not found: {locator}") from error
    return value, tuple(canonical_parts)


def _resolve_artifact_locator(registry: dict, source: dict) -> float:
    """Resolve one finite numeric value from an independent YAML/JSON artifact."""

    artifact_path, parts = _canonical_artifact_endpoint(registry, source)
    locator = source["locator"]
    payload = _load_artifact_payload(artifact_path)
    value, _ = _traverse_artifact_locator(payload, parts, locator)
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(float(value))
    ):
        raise ValueError("resolved reported figure must be numeric")
    return value


def _apply_revalidation_record(
    registry: dict,
    state: dict,
    record: dict,
    blocking: list[dict],
    derived: list[dict],
    validated: tuple[dict, Any] | None = None,
) -> None:
    """Apply one authenticated transition when its target is visited."""

    if validated is None:
        validated = _valid_revalidation(registry, state, record, blocking)
    if validated is None or record.get("result") != "revalidated":
        return
    target = record["target"]
    collection = "claims" if target["kind"] == "claim_revision" else "reported_figures"
    item, resolved_value = validated
    reasons = item.get("_stale_reasons", [])
    if not reasons:
        blocking.append(_issue("REVALIDATION_NOT_REQUIRED", target=target))
        return
    if "semantic_correction" in reasons and record["method"] == "machine":
        blocking.append(_issue("MACHINE_REVALIDATION_FORBIDDEN", target=target))
        return
    if target["kind"] == "reported_figure" and record["method"] == "machine":
        item["value"] = resolved_value
    if "semantic_correction" in reasons and record["method"] == "manual":
        reasons.remove("semantic_correction")
    if "pipeline_superseded" in reasons:
        reasons.remove("pipeline_superseded")
    item["pipeline_id"] = record["to_pipeline"]
    attached_record = copy.deepcopy(record)
    if target["kind"] == "claim_revision" and isinstance(resolved_value, dict):
        attached_record.pop("comparison", None)
        attached_record["resolved_comparison"] = copy.deepcopy(resolved_value)
    item["revalidation"] = attached_record
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


def _recompute_one_figure(
    state: dict,
    identifier: str,
    blocking: list[dict],
    derived: list[dict],
) -> None:
    figure = state["reported_figures"][identifier]
    if not figure.get("derived_from"):
        return
    upstream = state["reported_figures"][str(figure["derived_from"])]
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
        return
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


def _evaluate_dependency_cascade(
    registry: dict,
    state: dict,
    corrected_fact_keys: set[str],
    reports: list[dict],
    order: list[str],
    outgoing: dict[str, set[str]],
    blocking: list[dict],
    derived: list[dict],
    prevalidated_revalidations: dict[str, tuple[dict, tuple[dict, Any]]],
) -> dict[str, set[str]]:
    """Evaluate stale, transitions, figures, and challenges in one DAG walk."""

    semantic_events: list[dict] = []
    pipeline_events: list[dict] = []
    revalidation_events: list[dict] = []
    recompute_events: list[dict] = []
    challenge_events: list[dict] = []
    semantic_reasons: dict[str, set[str]] = defaultdict(set)
    challenge_reasons: dict[str, set[str]] = defaultdict(set)
    for fact_key in corrected_fact_keys:
        semantic_reasons[f"semantic_fact:{fact_key}"].add("semantic_correction")
    for field in registry["derived_fields"]:
        if field.get("status") == "defective":
            identifier = str(field["derived_field_id"])
            challenge_reasons[f"derived_field:{identifier}"].add(
                f"defective:{identifier}"
            )
    for item in reports:
        if item.get("code") == "SEMANTIC_DISCLOSURE_REQUIRED":
            fact_key = str(item["fact_key"])
            challenge_reasons[f"semantic_fact:{fact_key}"].add(
                f"semantic-change:{fact_key}"
            )

    superseded = {
        str(pipeline.get("pipeline_id"))
        for pipeline in registry["pipelines"]
        if pipeline.get("status") == "superseded"
    }
    for output_id, output in state["outputs"].items():
        referenced_pipelines = _output_pipelines(
            output,
            state,
            include_historical=output.get("cross_pipeline") != "reconciliation",
        )
        if (
            str(output.get("pipeline_id")) in superseded
            or referenced_pipelines & superseded
        ):
            _mark_stale(
                output,
                "pipeline_superseded",
                "STALE_OUTPUT",
                pipeline_events,
                output_id=output_id,
                pipeline_ids=sorted(referenced_pipelines & superseded),
            )

    challenged: dict[str, set[str]] = defaultdict(set)
    for name in order:
        kind, identifier = name.split(":", 1)
        if semantic_reasons[name]:
            if kind == "derived_field":
                _mark_stale(
                    state["derived_fields"][identifier],
                    "semantic_correction",
                    "SEMANTIC_STALE_DERIVED_FIELD",
                    semantic_events,
                    derived_field_id=identifier,
                )
            elif kind == "evidence_card":
                _mark_stale(
                    state["evidence_cards"][identifier],
                    "semantic_correction",
                    "SEMANTIC_STALE_EVIDENCE_CARD",
                    semantic_events,
                    evidence_card_id=identifier,
                )
            elif kind == "claim_revision":
                _mark_stale(
                    state["claims"][identifier],
                    "semantic_correction",
                    "SEMANTIC_STALE_CLAIM",
                    semantic_events,
                    claim_revision_id=identifier,
                )

        if kind == "claim_revision":
            claim = state["claims"][identifier]
            if str(claim.get("pipeline_id")) in superseded:
                _mark_stale(
                    claim,
                    "pipeline_superseded",
                    "STALE_CLAIM",
                    pipeline_events,
                    claim_revision_id=identifier,
                    pipeline_id=claim.get("pipeline_id"),
                )
        elif kind == "reported_figure":
            figure = state["reported_figures"][identifier]
            if str(figure.get("pipeline_id")) in superseded:
                _mark_stale(
                    figure,
                    "pipeline_superseded",
                    "STALE_REPORTED_FIGURE",
                    pipeline_events,
                    figure_id=identifier,
                    pipeline_id=figure.get("pipeline_id"),
                )

        prevalidated = prevalidated_revalidations.get(name)
        if prevalidated:
            record, validation = prevalidated
            _apply_revalidation_record(
                registry,
                state,
                record,
                blocking,
                revalidation_events,
                validation,
            )
        if kind == "reported_figure":
            _recompute_one_figure(
                state, identifier, blocking, recompute_events
            )
        elif kind == "claim_revision":
            claim = state["claims"][identifier]
            if claim.get("availability") != "stale":
                challenged[identifier].update(challenge_reasons[name])
                for challenge_id in sorted(challenge_reasons[name]):
                    challenge_events.append(
                        _issue(
                            "DEFECTIVE_FIELD_CHALLENGE"
                            if challenge_id.startswith("defective:")
                            else "SEMANTIC_CHANGE_CHALLENGE",
                            claim_revision_id=identifier,
                            challenge_id=challenge_id,
                        )
                    )

        for destination in outgoing[name]:
            semantic_reasons[destination].update(semantic_reasons[name])
            challenge_reasons[destination].update(challenge_reasons[name])

    _refresh_outputs_after_revalidation(state, revalidation_events)
    derived.extend(semantic_events)
    derived.extend(pipeline_events)
    derived.extend(revalidation_events)
    derived.extend(recompute_events)
    derived.extend(challenge_events)
    return challenged


def _matched_gate_scope_target(definition: dict, evaluation: dict) -> dict | None:
    """Return the exact frozen target matched by an evaluated identity."""

    evaluated = evaluation["evaluated_against"]
    pipeline_id = str(evaluation["pipeline_id"])
    evaluated_id = str(evaluated["id"])
    candidates = [
        target
        for target in definition["applies_to"]
        if target["kind"] == evaluated["kind"]
    ]
    if evaluated["kind"] == "claim_key":
        for target in candidates:
            if str(target["id"]) == evaluated_id:
                return target
    for target in candidates:
        if evaluated_id == f"{target['id']}@{pipeline_id}":
            return target
    return None


def _gate_scope_matches(definition: dict, evaluation: dict) -> bool:
    return _matched_gate_scope_target(definition, evaluation) is not None


def _gate_evaluation_key(evaluation: dict) -> str:
    return f"{evaluation.get('gate_id')}@{evaluation.get('pipeline_id')}"


def _resolve_gate_target(
    registry: dict, state: dict, definition: dict, evaluation: dict
) -> dict | None:
    """Resolve one evaluation to only its concrete pipeline-local target."""

    matched_target = _matched_gate_scope_target(definition, evaluation)
    if matched_target is None:
        return None
    evaluated = evaluation["evaluated_against"]
    pipeline_id = str(evaluation["pipeline_id"])
    if evaluated["kind"] in {"dataset", "pipeline_stage"}:
        return {
            "kind": evaluated["kind"],
            "id": str(matched_target["id"]),
            "pipeline_id": pipeline_id,
        }
    target_id = str(matched_target["id"])
    authored_claims = registry.get("claims", [])
    current_claims = state["claims"].values()
    revision_ids = {
        str(claim.get("claim_revision_id"))
        for claim in [*authored_claims, *current_claims]
        if str(claim.get("claim_key")) == target_id
        and str(claim.get("pipeline_id")) == pipeline_id
    }
    if not revision_ids:
        return None
    return {
        "kind": "claim_key",
        "id": target_id,
        "pipeline_id": pipeline_id,
        "claim_revision_ids": revision_ids,
    }


def _change_matches_gate(change: dict, target: dict | None) -> bool:
    if target is None or str(change.get("pipeline_id")) != target["pipeline_id"]:
        return False
    if target["kind"] == "claim_key":
        return (
            change.get("object_kind") == "claim_key"
            and str(change.get("object_id")) == target["id"]
        ) or (
            change.get("object_kind") == "claim_revision"
            and str(change.get("object_id")) in target["claim_revision_ids"]
        )
    return (
        change.get("object_kind") == target["kind"]
        and str(change.get("object_id")) == target["id"]
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

    for evaluation in state.get("gate_evaluations", {}).values():
        gate_id = str(evaluation.get("gate_id"))
        pipeline_id = str(evaluation.get("pipeline_id"))
        effective_evaluation = state["gate_evaluations"].get(
            _gate_evaluation_key(evaluation)
        )
        definition = definitions.get(gate_id)
        pipeline = pipelines.get(pipeline_id)
        if definition is None or pipeline is None:
            blocking.append(
                _issue(
                    "GATE_REFERENCE_INVALID", gate_id=gate_id, pipeline_id=pipeline_id
                )
            )
            continue
        resolved_target = _resolve_gate_target(
            registry, state, definition, evaluation
        )
        if not _gate_scope_matches(definition, evaluation):
            blocking.append(
                _issue(
                    "GATE_SCOPE_MISMATCH",
                    gate_id=gate_id,
                    pipeline_id=pipeline_id,
                    evaluated_against=evaluation.get("evaluated_against"),
                )
            )
        elif resolved_target is None:
            blocking.append(
                _issue(
                    "GATE_TARGET_INSTANCE_MISSING",
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
        if resolved_target and resolved_target["kind"] == "claim_key":
            for claim in claims_by_key.get(resolved_target["id"], []):
                if (
                    str(claim.get("claim_revision_id"))
                    in resolved_target["claim_revision_ids"]
                    and claim.get("availability") in {"retired", "withdrawn"}
                ):
                    change = changes.get(str(claim.get("change_id")))
                    if (
                        change
                        and _change_matches_gate(change, resolved_target)
                        and change.get("new_state") == claim.get("availability")
                    ):
                        moot_change = change["change_id"]
                        break
        elif resolved_target:
            for change in changes.values():
                if (
                    _change_matches_gate(change, resolved_target)
                    and change.get("new_state")
                    in {"retired", "withdrawn", "end_of_life"}
                ):
                    moot_change = change["change_id"]
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
            if effective_evaluation is not None:
                effective_evaluation["effective_status"] = status
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
        if effective_evaluation is not None:
            effective_evaluation["effective_status"] = status
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
                    or not _change_matches_gate(change, resolved_target)
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


def _compiled_lexical_markers(registry: dict) -> dict[str, tuple[str, ...]]:
    baseline = {
        name: list(values) for name, values in DEFAULT_LEXICAL_MARKERS.items()
    }
    extensions = {name: [] for name in DEFAULT_LEXICAL_MARKERS}
    configured = _lexical_configuration(registry) or {}
    if not isinstance(configured, dict):
        return {name: tuple(values) for name, values in baseline.items()}
    for name, extension in configured.items():
        name = LEXICAL_CLASS_ALIASES.get(name, name)
        if name not in baseline:
            continue
        if isinstance(extension, list):
            extensions[name].extend(extension)
            continue
        if not isinstance(extension, dict):
            continue
        # Project configuration may refine its extension layer, but the
        # contract's baseline semantic classes are not deletable. Otherwise a
        # valid ``replace: []`` could turn the residual engine off.
        extensions[name].extend(extension.get("replace", []))
        extensions[name].extend(extension.get("add", []))
        removed = {item.casefold() for item in extension.get("remove", [])}
        extensions[name] = [
            item for item in extensions[name] if item.casefold() not in removed
        ]
    return {
        name: tuple(
            dict.fromkeys(
                item.casefold() for item in [*baseline[name], *extensions[name]]
            )
        )
        for name in baseline
    }


@lru_cache(maxsize=4096)
def _marker_regex(marker: str, inflected: bool) -> re.Pattern[str]:
    """Compile a marker, optionally tolerating ordinary verb inflection.

    A marker list is a vocabulary, not a spelling exercise. Without inflection
    tolerance a curated list silently misses ``raises``, ``reduced`` and
    ``driving``, and a sentence that plainly commits to a causal effect scores
    as descriptive.
    """

    if not inflected:
        body = re.escape(marker)
    else:
        head, _, tail = marker.rpartition(" ")
        word = tail if head else marker
        if word.endswith("e"):
            stem = re.escape(word[:-1]) + r"(?:e|es|ed|ing)"
        elif word.endswith("y") and len(word) > 2 and word[-2] not in "aeiou":
            stem = re.escape(word[:-1]) + r"(?:y|ies|ied|ying)"
        else:
            stem = re.escape(word) + r"(?:s|es|ed|ing)?"
        body = f"{re.escape(head)} {stem}" if head else stem
    return re.compile(rf"(?<!\w){body}(?!\w)", flags=re.IGNORECASE)


def _contains_marker(text: str, marker: str, inflected: bool = False) -> bool:
    return _marker_regex(marker, inflected).search(text) is not None


def _sentence_segments(text: str) -> list[str]:
    return [
        segment.strip()
        for segment in re.split(r"(?<=[.!?])\s+", text.strip())
        if segment.strip()
    ]


INFLECTED_LEXICAL_CLASSES = {
    "causal",
    "evidential_weak",
    "evidential_moderate",
    "descriptive",
}


def _matched_markers(
    text: str, markers: dict[str, tuple[str, ...]]
) -> dict[str, list[str]]:
    matched: dict[str, list[str]] = {}
    for name, values in markers.items():
        inflected = name in INFLECTED_LEXICAL_CLASSES
        hits = [
            marker
            for marker in values
            if _contains_marker(text, marker, inflected)
        ]
        if hits:
            matched[name] = hits
    return matched


def _classify_assertion_text(
    text: str,
    site: dict,
    markers: dict[str, tuple[str, ...]],
    registered_scope_applies: bool = False,
    counterevidence_corroborated: bool = False,
) -> tuple[int, str, dict[str, list[str]], bool]:
    sentence_results: list[tuple[int, dict[str, list[str]], bool]] = []
    aggregate: dict[str, list[str]] = defaultdict(list)
    for sentence in _sentence_segments(text):
        matched = _matched_markers(sentence, markers)
        for name, values in matched.items():
            aggregate[name].extend(values)
        sentence_scoped = registered_scope_applies or "scope_qualifying" in matched
        if "causal" in matched:
            if counterevidence_corroborated:
                strength = 2
            elif sentence_scoped:
                strength = 3
            else:
                strength = 4
            # An evidential frame lowers what the sentence promises even when a
            # causal verb survives inside it. The corpus grades the frames:
            # "indicate" and "show" barely lower it, "suggest" lowers it to a
            # qualified commitment, and "is associated with" or "we interpret"
            # take it out of causal commitment altogether.
            if "evidential_strong" in matched:
                strength = min(strength, 1)
            elif "evidential_moderate" in matched:
                strength = min(strength, 3)
        elif "evidential_strong" in matched or "evidential_moderate" in matched:
            strength = 1
        else:
            strength = 0
        sentence_results.append((strength, matched, sentence_scoped))

    strength = max((item[0] for item in sentence_results), default=0)
    tier = {value: tier for tier, value in ASSERTION_TIERS.items()}[strength]
    governing = [item for item in sentence_results if item[0] == strength]
    sentence_scope_applies = registered_scope_applies or bool(governing) and all(
        item[2] for item in governing
    )
    deduplicated = {
        name: list(dict.fromkeys(values)) for name, values in aggregate.items()
    }
    return strength, tier, deduplicated, sentence_scope_applies


def _resolve_registry_source(registry: dict, authored_path: Any) -> Path:
    if not _nonempty_string(authored_path):
        raise ValueError("source path must be a nonempty relative path")
    relative = Path(authored_path)
    if relative.is_absolute():
        raise ValueError("absolute source paths are forbidden")
    root = Path(registry.get("_root", ".")).resolve(strict=True)
    try:
        source = (root / relative).resolve(strict=True)
    except OSError as error:
        raise ValueError(f"source does not resolve: {authored_path}") from error
    if source != root and root not in source.parents:
        raise ValueError("source path escapes the registry directory")
    if not source.is_file():
        raise ValueError("source path is not a regular file")
    return source


TEX_SECTION_ROLE_KEYWORDS = (
    ("introduction", "introduction"),
    ("results", "results"),
    ("findings", "results"),
    ("mechanism", "mechanism"),
    ("discussion", "discussion"),
    ("conclusion", "conclusion"),
    ("concluding", "conclusion"),
)

# A quantitative value is a numeral carrying a decimal point, a percent sign, a
# currency symbol, or a magnitude suffix. Section numbers, table references and
# hypothesis labels are deliberately out of scope.
QUANTITATIVE_VALUE = re.compile(
    r"(?<![\\\w])"
    r"(?:[$\u00a3\u20ac]\s?\d[\d,]*(?:\.\d+)?"
    r"|\d[\d,]*\.\d+\s?%?"
    r"|\d[\d,]*\s?%"
    r"|\d[\d,]*(?:\.\d+)?\s?(?:bn|m|k|million|billion|thousand)(?![a-z]))",
    flags=re.IGNORECASE,
)


def _strip_tex_comment(line: str) -> str:
    """Remove a trailing LaTeX comment, honouring an escaped percent sign."""

    out: list[str] = []
    index = 0
    while index < len(line):
        char = line[index]
        if char == "\\" and index + 1 < len(line):
            out.append(line[index : index + 2])
            index += 2
            continue
        if char == "%":
            break
        out.append(char)
        index += 1
    return "".join(out)


def _tex_visible_text(text: str) -> str:
    """Approximate the typeset text: drop control sequences, keep arguments."""

    without_math = re.sub(r"\$[^$]*\$", " ", text)
    return re.sub(r"\\[A-Za-z@]+\*?\s*(\[[^\]]*\])?", " ", without_math)


def _tex_section_role(lines: list[str], line_number: int) -> str | None:
    """Resolve the section role governing ``line_number`` in a LaTeX source."""

    role: str | None = None
    depth = 0
    for index in range(line_number):
        line = _strip_tex_comment(lines[index])
        if re.search(r"\\begin\{abstract\}", line):
            depth += 1
            role = "abstract"
            continue
        if re.search(r"\\end\{abstract\}", line):
            depth = max(depth - 1, 0)
            role = None
            continue
        if depth:
            continue
        if re.search(r"\\(?:TITLE|title)\{", line):
            role = "title"
            continue
        heading = re.search(
            r"\\(?:section|SECTION)\*?\{([^}]*)\}", line
        )
        if heading:
            name = heading.group(1).casefold()
            role = None
            for keyword, resolved in TEX_SECTION_ROLE_KEYWORDS:
                if keyword in name:
                    role = resolved
                    break
    return role


def _anchor_span(
    source: Path, anchor: Any, source_cache: dict[Path, tuple[str, list[str]]]
) -> tuple[int, int]:
    if source not in source_cache:
        body = source.read_text(encoding="utf-8")
        source_cache[source] = (body, body.splitlines())
    body, lines = source_cache[source]
    line_range = _line_range(anchor)
    if line_range is not None:
        start, end = line_range
        if end > len(lines):
            raise ValueError("line range lies outside the source")
        return start, end
    marker = str(anchor)
    if body.count(marker) != 1:
        raise ValueError("stable marker must occur exactly once")
    offset = body.index(marker)
    line_number = body.count("\n", 0, offset) + 1
    return line_number, line_number


def _anchor_text(
    source: Path, anchor: Any, source_cache: dict[Path, tuple[str, list[str]]]
) -> tuple[str, int, int]:
    start, end = _anchor_span(source, anchor, source_cache)
    _, lines = source_cache[source]
    line_range = _line_range(anchor)
    if line_range is not None:
        return "\n".join(lines[start - 1 : end]), start, end
    marker = str(anchor)
    line_number = start
    line = lines[line_number - 1]
    without_marker = line.replace(marker, "", 1)
    anchored_text = re.sub(r"<!--\s*-->|\\label\{\}|^[%#]\s*", " ", without_marker)
    if source.suffix.lower() == ".tex":
        anchored_text = _strip_tex_comment(anchored_text)
    visible = anchored_text.strip()
    if re.search(r"[A-Za-z]", visible):
        return visible, line_number, line_number
    for next_index in range(line_number, len(lines)):
        if lines[next_index].strip():
            return lines[next_index], line_number, next_index + 1
    raise ValueError("stable marker has no assertion text")


def _resolved_assertion_site(
    registry: dict,
    site: dict,
    source_cache: dict[Path, tuple[str, list[str]]],
) -> tuple[str, int, int, Path]:
    source = _resolve_registry_source(registry, site.get("path"))
    text, start, end = _anchor_text(source, site.get("anchor"), source_cache)
    return text, start, end, source


def _resolved_counterevidence_disclosure(
    registry: dict,
    site: dict,
    site_source: Path,
    site_start: int,
    site_end: int,
    source_cache: dict[Path, tuple[str, list[str]]],
) -> str | None:
    disclosure = site.get("counterevidence_disclosure")
    if disclosure is None:
        return None
    source = _resolve_registry_source(registry, disclosure.get("path"))
    text, start, end = _anchor_text(source, disclosure.get("anchor"), source_cache)
    prominence = site.get("counterevidence_prominence")
    if prominence not in {"footnote", "appendix"} and (
        source != site_source or start > site_end + 1 or end < site_start - 1
    ):
        raise ValueError("counterevidence disclosure is not adjacent to its assertion site")
    return text


def _site_reference(site: dict) -> str:
    anchor = site.get("anchor")
    anchor_text = (
        anchor
        if isinstance(anchor, str)
        else json.dumps(anchor, sort_keys=True, separators=(",", ":"))
    )
    return f"{site.get('path')}#{anchor_text}"


def _scope_declaration_applies(
    registry: dict,
    site: dict,
    site_source: Path,
    site_start: int,
    site_end: int,
    source_cache: dict[Path, tuple[str, list[str]]],
    markers: dict[str, tuple[str, ...]],
) -> bool:
    if site.get("qualifier_scope") == "sentence":
        return False
    declaration = site.get("scope_declaration")
    if not isinstance(declaration, dict):
        return False
    declaration_source = _resolve_registry_source(registry, declaration.get("path"))
    declaration_text, _, _ = _anchor_text(
        declaration_source, declaration.get("anchor"), source_cache
    )
    if not any(
        _contains_marker(declaration_text, marker)
        for marker in markers["scope_qualifying"]
    ):
        raise ValueError("scope declaration does not contain a registered scope qualifier")
    coverage = declaration["coverage"]
    coverage_source = _resolve_registry_source(registry, coverage.get("path"))
    coverage_start, _ = _anchor_span(
        coverage_source, coverage.get("start_anchor"), source_cache
    )
    _, coverage_end = _anchor_span(
        coverage_source, coverage.get("end_anchor"), source_cache
    )
    if coverage_start > coverage_end:
        raise ValueError("scope coverage anchors are reversed")
    return (
        site_source == coverage_source
        and coverage_start <= site_start
        and site_end <= coverage_end
    )


def _complete_power_basis(power: Any) -> bool:
    if not isinstance(power, dict):
        return False
    sample_size = power.get("sample_size")
    mde = power.get("minimum_detectable_effect")
    return (
        _nonempty_string(power.get("test"))
        and isinstance(sample_size, int)
        and not isinstance(sample_size, bool)
        and sample_size > 0
        and _finite_number(mde)
        and float(mde) > 0
    )


def _specific_alternative(value: Any) -> bool:
    if not _nonempty_string(value):
        return False
    normalized = " ".join(str(value).casefold().split())
    generic = {
        "selection",
        "bias",
        "confounding",
        "alternative",
        "alternative explanation",
        "other",
    }
    return normalized not in generic and bool(re.search(r"[a-z0-9]", normalized))


def _complete_upgrade_trace(
    upgrade: Any,
    result_references: set[str],
    cards: dict[str, dict],
) -> bool:
    if not isinstance(upgrade, dict):
        return False
    evidence = cards.get(str(upgrade.get("evidence_card")))
    return (
        upgrade.get("results_site") in result_references
        and _nonempty_string(upgrade.get("rationale"))
        and _nonempty_string(upgrade.get("recorded_by"))
        and _as_datetime(upgrade.get("recorded_at")) is not None
        and evidence is not None
        and evidence.get("status") == "current"
        and not evidence.get("_stale_reasons")
    )


def _relation_bears_on_identification(relation: dict) -> bool:
    if relation.get("identifying_assumption") is True:
        return True
    for field in ("bears_on", "target", "counterevidence_target"):
        value = relation.get(field)
        if isinstance(value, str) and value.casefold().replace("-", "_").replace(
            " ", "_"
        ) in {"identifying_assumption", "identification_assumption"}:
            return True
    rationale = relation.get("rationale")
    return isinstance(rationale, str) and re.search(
        r"(?<!\w)identif(?:ying|ication) assumption(?!\w)",
        rationale,
        flags=re.IGNORECASE,
    ) is not None


def _site_bears_on_identification(site: dict) -> bool:
    if site.get("identifying_assumption") is True:
        return True
    for field in ("bears_on", "counterevidence_bears_on", "counterevidence_target"):
        value = site.get(field)
        if isinstance(value, str) and value.casefold().replace("-", "_").replace(
            " ", "_"
        ) in {"identifying_assumption", "identification_assumption"}:
            return True
    return False


def _precision_evidence_reference(
    registry: dict, state: dict, claim: dict, estimate_id: Any
) -> tuple[dict | None, bool]:
    if estimate_id is None:
        return None, True
    if not _nonempty_string(estimate_id):
        return None, False
    evidence_id = str(estimate_id).split("#", 1)[0]
    evidence = state["evidence_cards"].get(evidence_id)
    live_support = any(
        str(relation.get("claim_revision_id"))
        == str(claim.get("claim_revision_id"))
        and str(relation.get("evidence_card_id")) == evidence_id
        and relation.get("relation") == "supports"
        and relation.get("status") != "withdrawn"
        for relation in registry.get("evidence_relations", [])
    )
    valid = (
        evidence is not None
        and str(evidence.get("pipeline_id")) == str(claim.get("pipeline_id"))
        and evidence.get("status") == "current"
        and not evidence.get("_stale_reasons")
        and live_support
    )
    return evidence, valid


def _claim_evidence_strength(
    registry: dict,
    state: dict,
    claim: dict,
    precision: dict,
    precision_evidence: dict | None,
    precision_reference_valid: bool,
) -> tuple[int, list[str]]:
    reasons: list[str] = []
    claim_id = str(claim.get("claim_revision_id"))
    assessment = claim.get("assessment")
    strength = {"supported": 4, "challenged": 2, "unresolved": 0}.get(
        assessment, 0
    )
    reasons.append(f"assessment:{assessment}")
    supporting_cards = []
    for relation in registry.get("evidence_relations", []):
        if (
            str(relation.get("claim_revision_id")) == claim_id
            and relation.get("status") != "withdrawn"
            and relation.get("relation") == "supports"
        ):
            card = state["evidence_cards"].get(str(relation.get("evidence_card_id")))
            if (
                card
                and card.get("provenance") == "confirmatory"
                and card.get("status") == "current"
                and not card.get("_stale_reasons")
            ):
                supporting_cards.append(card)
    if not supporting_cards:
        strength = 0
        reasons.append("no_live_confirmatory_support")
    else:
        reasons.append("live_confirmatory_support")

    revision_reason = claim.get("revision_reason")
    if isinstance(revision_reason, str) and revision_reason.startswith("bounded_by_"):
        strength = min(strength, 3)
        reasons.append(revision_reason)

    definitions = _id_map(registry.get("gate_definitions", []), "gate_id")
    relevant_gate_statuses: list[str] = []
    for evaluation in state.get("gate_evaluations", {}).values():
        if str(evaluation.get("pipeline_id")) != str(claim.get("pipeline_id")):
            continue
        definition = definitions.get(str(evaluation.get("gate_id")))
        if not definition:
            continue
        if any(
            target.get("kind") == "claim_key"
            and str(target.get("id")) == str(claim.get("claim_key"))
            for target in definition.get("applies_to", [])
        ):
            relevant_gate_statuses.append(str(evaluation.get("effective_status")))
    if any(status in {"triggered", "not_evaluated"} for status in relevant_gate_statuses):
        strength = 0
        reasons.append("applicable_gate_unresolved")
    elif "released" in relevant_gate_statuses:
        strength = min(strength, 2)
        reasons.append("applicable_gate_released")
    elif "satisfied" in relevant_gate_statuses:
        strength = min(strength, 3)
        reasons.append("applicable_gate_compensated")
    elif relevant_gate_statuses:
        reasons.append("applicable_gate_passed")

    distribution = precision.get("has_sampling_distribution")
    if not precision_reference_valid:
        strength = 0
        reasons.append("precision_evidence_invalid")
    elif precision_evidence is not None:
        if precision_evidence.get("provenance") != "confirmatory":
            strength = min(strength, 1)
            reasons.append("precision_evidence_exploratory")
        else:
            reasons.append("precision_evidence_confirmatory")
    if distribution is False:
        strength = 0
        reasons.append("no_sampling_distribution")
    elif distribution is not True:
        strength = min(strength, 1)
        reasons.append("sampling_distribution_unknown")
    elif precision.get("significant_at") is None:
        strength = min(strength, 1)
        reasons.append("sampling_precision_not_significant")
    else:
        reasons.append("sampling_precision_registered")
    if claim.get("availability") != "current":
        strength = 0
        reasons.append(f"availability:{claim.get('availability')}")
    return strength, reasons


def _has_immediate_recovery(
    text: str, concessive_markers: tuple[str, ...]
) -> bool:
    lowered = text.casefold()
    concessive_positions = [
        lowered.find(marker)
        for marker in concessive_markers
        if _contains_marker(lowered, marker)
    ]
    recovery = re.search(
        r"(?<!\w)(however|nevertheless|nonetheless|overall|encouragingly|"
        r"reassuringly|importantly)(?!\w)",
        lowered,
    )
    if not concessive_positions or recovery is None:
        return False
    concession = min(position for position in concessive_positions if position >= 0)
    if recovery.start() <= concession:
        return False
    intervening = lowered[concession : recovery.start()]
    return len(re.findall(r"[.!?]", intervening)) <= 1


def _has_separate_contrastive_sentence(text: str) -> bool:
    return re.search(
        r"[.!?]\s+(?:however|nevertheless|yet|by contrast|in contrast)(?:\s|,)",
        text,
        flags=re.IGNORECASE,
    ) is not None


COUNTEREVIDENCE_CUES = (
    "although",
    "despite",
    "however",
    "nevertheless",
    "yet",
    "albeit",
    "whereas",
    "by contrast",
    "in contrast",
    "limitation",
    "caveat",
    "imprecise",
    "insignificant",
    "not significant",
    "fails",
    "failure",
    "weakens",
    "violates",
    "cannot",
    "no effect",
)


def _has_counterevidence_cue(text: str) -> bool:
    return any(_contains_marker(text, cue) for cue in COUNTEREVIDENCE_CUES)


def _counterevidence_prominence_is_corroborated(
    assertion_text: str,
    prominence: Any,
    disclosure_text: str | None,
) -> bool:
    combined = assertion_text
    if disclosure_text:
        combined = f"{assertion_text.rstrip()} {disclosure_text.lstrip()}"
    if prominence == "parenthetical":
        return any(
            _has_counterevidence_cue(match.group(1))
            for match in re.finditer(r"\(([^()]*)\)", combined, flags=re.DOTALL)
        )
    if prominence == "clause_appended":
        return re.search(
            r"[,;—-]\s*(?:although|but|yet|albeit|whereas|despite)(?!\w)",
            combined,
            flags=re.IGNORECASE,
        ) is not None and _has_counterevidence_cue(combined)
    if prominence == "separate_contrastive_sentence":
        return _has_separate_contrastive_sentence(combined) and _has_counterevidence_cue(
            combined
        )
    if prominence == "footnote":
        return (
            re.search(r"\\footnote\{|\[\^[^\]]+\]|<sup>", combined, re.I)
            is not None
            and _has_counterevidence_cue(combined)
        )
    if prominence == "appendix":
        return _contains_marker(combined, "appendix") and _has_counterevidence_cue(
            combined
        )
    return False


def _writing_strength_checks(
    registry: dict,
    state: dict,
    blocking: list[dict],
    reports: list[dict],
) -> None:
    """Evaluate registered assertion sites against the already-derived v2.1 state."""

    markers = _compiled_lexical_markers(registry)
    source_cache: dict[Path, tuple[str, list[str]]] = {}
    cards = state["evidence_cards"]
    relations_by_claim: dict[str, list[dict]] = defaultdict(list)
    for relation in registry.get("evidence_relations", []):
        if relation.get("status") != "withdrawn":
            relations_by_claim[str(relation.get("claim_revision_id"))].append(relation)

    for claim_id, claim in state["claims"].items():
        sites = claim.get("assertion_sites", [])
        if not sites:
            continue
        resolved_sites: list[dict[str, Any]] = []
        for site_index, site in enumerate(sites):
            identity = {
                "claim_revision_id": claim_id,
                "site": _site_reference(site),
                "section_role": site.get("section_role"),
            }
            assertion_type = site.get("assertion_type")
            if assertion_type != "world" and site.get("declared_tier") is not None:
                blocking.append(_issue("UNTIERED_ASSERTION_TIERED", **identity))
            if assertion_type != "negative" and site.get("power_basis") is not None:
                blocking.append(
                    _issue(
                        "ASSERTION_FIELD_NOT_APPLICABLE",
                        field="power_basis",
                        assertion_type=assertion_type,
                        **identity,
                    )
                )
            if assertion_type != "discriminating" and site.get(
                "alternative_explanation"
            ) is not None:
                blocking.append(
                    _issue(
                        "ASSERTION_FIELD_NOT_APPLICABLE",
                        field="alternative_explanation",
                        assertion_type=assertion_type,
                        **identity,
                    )
                )
            if assertion_type != "model_internal" and site.get("as_modeled") is not None:
                blocking.append(
                    _issue(
                        "ASSERTION_FIELD_NOT_APPLICABLE",
                        field="as_modeled",
                        assertion_type=assertion_type,
                        **identity,
                    )
                )
            if assertion_type != "world" and site.get(
                "upgrade_justification"
            ) is not None:
                blocking.append(
                    _issue(
                        "ASSERTION_FIELD_NOT_APPLICABLE",
                        field="upgrade_justification",
                        assertion_type=assertion_type,
                        **identity,
                    )
                )
            if (
                site.get("counterevidence_prominence") is None
                and site.get("counterevidence_disclosure") is not None
            ):
                blocking.append(
                    _issue(
                        "ASSERTION_FIELD_NOT_APPLICABLE",
                        field="counterevidence_disclosure",
                        assertion_type=assertion_type,
                        **identity,
                    )
                )

            try:
                text, start_line, end_line, source = _resolved_assertion_site(
                    registry, site, source_cache
                )
            except (OSError, UnicodeError, ValueError) as error:
                code = (
                    "ASSERTION_SOURCE_INVALID"
                    if "source" in str(error) or "path" in str(error)
                    else "ASSERTION_ANCHOR_INVALID"
                )
                blocking.append(_issue(code, detail=str(error), **identity))
                continue

            if source.suffix.lower() == ".tex":
                _, source_lines = source_cache[source]
                resolved_role = _tex_section_role(source_lines, start_line)
                declared_role = site.get("section_role")
                if resolved_role is not None and resolved_role != declared_role:
                    blocking.append(
                        _issue(
                            "SECTION_ROLE_MISMATCH",
                            declared_section_role=declared_role,
                            resolved_section_role=resolved_role,
                            line=start_line,
                            **identity,
                        )
                    )
                literals = sorted(
                    dict.fromkeys(
                        match.group(0).strip()
                        for match in QUANTITATIVE_VALUE.finditer(
                            _tex_visible_text(text)
                        )
                    )
                )
                if literals:
                    blocking.append(
                        _issue(
                            "QUANTITATIVE_VALUE_NOT_REGISTERED",
                            literals=literals,
                            **identity,
                        )
                    )

            scope_error = False
            try:
                declared_scope_applies = _scope_declaration_applies(
                    registry,
                    site,
                    source,
                    start_line,
                    end_line,
                    source_cache,
                    markers,
                )
            except (OSError, UnicodeError, ValueError, KeyError) as error:
                blocking.append(
                    _issue("SCOPE_DECLARATION_INVALID", detail=str(error), **identity)
                )
                declared_scope_applies = False
                scope_error = True
            if (
                site.get("qualifier_scope") != "sentence"
                and not declared_scope_applies
                and not scope_error
            ):
                blocking.append(
                    _issue(
                        "SCOPE_DECLARATION_INVALID",
                        detail="assertion site lies outside the declared closed coverage range",
                        **identity,
                    )
                )

            disclosure_text = None
            try:
                disclosure_text = _resolved_counterevidence_disclosure(
                    registry,
                    site,
                    source,
                    start_line,
                    end_line,
                    source_cache,
                )
            except (OSError, UnicodeError, ValueError) as error:
                blocking.append(
                    _issue(
                        "COUNTEREVIDENCE_DISCLOSURE_INVALID",
                        detail=str(error),
                        **identity,
                    )
                )
            prominence = site.get("counterevidence_prominence")
            counterevidence_corroborated = (
                prominence is not None
                and _counterevidence_prominence_is_corroborated(
                    text, prominence, disclosure_text
                )
            )
            if prominence is not None and not counterevidence_corroborated:
                blocking.append(
                    _issue(
                        "COUNTEREVIDENCE_PROMINENCE_UNCORROBORATED",
                        prominence=prominence,
                        **identity,
                    )
                )

            lexical_strength, lexical_tier, matched, scope_applies = (
                _classify_assertion_text(
                    text,
                    site,
                    markers,
                    declared_scope_applies,
                    counterevidence_corroborated,
                )
            )
            site_state = state["claims"][claim_id]["assertion_sites"][site_index]
            site_state["_lexical_tier"] = lexical_tier
            site_state["_lexical_strength"] = lexical_strength
            site_state["_matched_lexical_classes"] = matched
            site_state["_counterevidence_corroborated"] = (
                counterevidence_corroborated
            )
            resolved = {
                "site": site,
                "identity": identity,
                "text": text,
                "lexical_strength": lexical_strength,
                "lexical_tier": lexical_tier,
                "matched": matched,
                "scope_applies": scope_applies,
                "counterevidence_corroborated": counterevidence_corroborated,
                "source": source,
                "start_line": start_line,
                "end_line": end_line,
            }
            resolved_sites.append(resolved)

            precision = site["underlying_precision"]
            estimate_id = precision.get("estimate_id")
            precision_evidence, precision_reference_valid = (
                _precision_evidence_reference(
                    registry, state, claim, estimate_id
                )
            )
            if not precision_reference_valid:
                blocking.append(
                    _issue(
                        "UNDERLYING_PRECISION_REFERENCE_INVALID",
                        estimate_id=estimate_id,
                        **identity,
                    )
                )
            if (
                precision.get("has_sampling_distribution") is False
                and precision.get("significant_at") is not None
            ):
                blocking.append(
                    _issue("UNDERLYING_PRECISION_INCONSISTENT", **identity)
                    )

            live_counterevidence = [
                relation
                for relation in relations_by_claim.get(claim_id, [])
                if relation.get("relation") in {"challenges", "bounds"}
            ]
            if (
                site.get("counterevidence_prominence") is not None
                and not live_counterevidence
            ):
                blocking.append(
                    _issue("COUNTEREVIDENCE_REFERENCE_MISSING", **identity)
                )

            if assertion_type == "negative":
                complete_power = _complete_power_basis(site.get("power_basis"))
                if not complete_power:
                    blocking.append(_issue("NEGATIVE_POWER_BASIS_REQUIRED", **identity))
                    if re.search(r"(?<!\w)(?:we\s+)?rule(?:s|d)?\s+out(?!\w)", text, re.I):
                        blocking.append(
                            _issue("NEGATIVE_RULE_OUT_UNSUPPORTED", **identity)
                        )
                    hedged = any(
                        _contains_marker(text, phrase)
                        for phrase in (
                            "does not appear",
                            "do not appear",
                            "no evidence",
                            "cannot reject",
                            "may not",
                            "might not",
                        )
                    )
                    if not hedged:
                        blocking.append(
                            _issue("NEGATIVE_UNHEDGED_WITHOUT_POWER", **identity)
                        )
            elif assertion_type == "discriminating":
                if not _specific_alternative(site.get("alternative_explanation")):
                    blocking.append(
                        _issue("DISCRIMINATING_ALTERNATIVE_REQUIRED", **identity)
                    )
            elif assertion_type == "model_internal":
                if site.get("as_modeled") is not True:
                    blocking.append(
                        _issue("MODEL_INTERNAL_AS_MODELED_REQUIRED", **identity)
                    )
                if (
                    re.search(r"(?<!\w)significant(?:ly)?(?!\w)", text, re.I)
                    and precision.get("has_sampling_distribution") is not True
                ):
                    blocking.append(
                        _issue("MODEL_INTERNAL_SIGNIFICANT_UNSUPPORTED", **identity)
                    )

            if assertion_type == "world":
                evidence_strength, evidence_basis = _claim_evidence_strength(
                    registry,
                    state,
                    claim,
                    precision,
                    precision_evidence,
                    precision_reference_valid,
                )
                residual = lexical_strength - evidence_strength
                site_state["_evidence_strength"] = evidence_strength
                site_state["_overclaim_residual"] = residual
                details = {
                    **identity,
                    "lexical_tier": lexical_tier,
                    "declared_tier": site.get("declared_tier"),
                    "lexical_strength": lexical_strength,
                    "evidence_strength": evidence_strength,
                    "residual": residual,
                    "evidence_basis": evidence_basis,
                }
                if residual > 0:
                    blocking.append(_issue("OVERCLAIM_RESIDUAL", level="BLOCK", **details))
                elif residual < 0:
                    reports.append(_issue("UNDERCLAIM_RESIDUAL", level="INFO", **details))

                if _has_immediate_recovery(text, markers["concessive"]):
                    results_strengths = [
                        ASSERTION_TIERS[item.get("declared_tier")]
                        for item in sites
                        if item.get("assertion_type") == "world"
                        and item.get("section_role") == "results"
                        and item.get("declared_tier") in ASSERTION_TIERS
                    ]
                    declared_strength = ASSERTION_TIERS[site["declared_tier"]]
                    tier_reduced = bool(results_strengths) and declared_strength < max(
                        results_strengths
                    )
                    if not tier_reduced:
                        reports.append(
                            _issue("IMMEDIATE_RECOVERY", level="WARN", **identity)
                        )

        world_sites = [
            item
            for item in resolved_sites
            if item["site"].get("assertion_type") == "world"
        ]
        result_sites = [
            item
            for item in world_sites
            if item["site"].get("section_role") == "results"
        ]
        result_references = {_site_reference(item["site"]) for item in result_sites}
        result_strengths = [
            ASSERTION_TIERS[item["site"]["declared_tier"]] for item in result_sites
        ]

        if result_strengths:
            upgrade_baseline = max(result_strengths)
            for item in world_sites:
                site = item["site"]
                if site.get("section_role") == "results":
                    continue
                declared_strength = ASSERTION_TIERS[site["declared_tier"]]
                upgrade = site.get("upgrade_justification")
                if declared_strength > upgrade_baseline:
                    if not _complete_upgrade_trace(
                        upgrade, result_references, cards
                    ):
                        reports.append(
                            _issue(
                                "UPGRADE_TRACE_MISSING",
                                level="WARN",
                                trace_status=(
                                    "missing" if upgrade is None else "invalid"
                                ),
                                results_tier=max(
                                    result_sites,
                                    key=lambda result: ASSERTION_TIERS[
                                        result["site"]["declared_tier"]
                                    ],
                                )["site"]["declared_tier"],
                                **item["identity"],
                            )
                        )
                elif upgrade is not None:
                    blocking.append(
                        _issue(
                            "ASSERTION_FIELD_NOT_APPLICABLE",
                            field="upgrade_justification",
                            assertion_type="world",
                            **item["identity"],
                        )
                    )

        revision_reason = claim.get("revision_reason")
        if isinstance(revision_reason, str) and revision_reason.startswith("bounded_by_"):
            narrowed_results_strength = min(result_strengths) if result_strengths else 3
            for item in world_sites:
                site = item["site"]
                if site.get("section_role") not in {"title", "abstract", "conclusion"}:
                    continue
                declared_strength = ASSERTION_TIERS[site["declared_tier"]]
                if declared_strength > narrowed_results_strength or not item[
                    "scope_applies"
                ]:
                    blocking.append(
                        _issue(
                            "NARROWING_NOT_PROPAGATED",
                            level="BLOCK",
                            revision_reason=revision_reason,
                            results_strength=narrowed_results_strength,
                            **item["identity"],
                        )
                    )

        identifying_relations = [
            relation
            for relation in relations_by_claim.get(claim_id, [])
            if relation.get("relation") in {"challenges", "bounds"}
            and _relation_bears_on_identification(relation)
        ]
        # The prominence rule governs the five empirical assertion types. A
        # hypothesis is a proposition awaiting a test, so it has no diagnostic
        # disclosure obligation until it is registered as an empirical site.
        prominence_sites = [
            item
            for item in resolved_sites
            if item["site"].get("assertion_type") != "hypothesis"
        ]
        if identifying_relations or any(
            _site_bears_on_identification(item["site"]) for item in prominence_sites
        ):
            for item in prominence_sites:
                if not identifying_relations and not _site_bears_on_identification(
                    item["site"]
                ):
                    continue
                relevant_relations = identifying_relations or [
                    relation
                    for relation in relations_by_claim.get(claim_id, [])
                    if relation.get("relation") in {"challenges", "bounds"}
                ]
                relation_ids = sorted(
                    str(relation.get("relation_id"))
                    for relation in relevant_relations
                )
                prominence = item["site"].get("counterevidence_prominence")
                if (
                    prominence != "separate_contrastive_sentence"
                    or not item["counterevidence_corroborated"]
                ):
                    blocking.append(
                        _issue(
                            "COUNTEREVIDENCE_BURIED",
                            level="BLOCK",
                            relation_ids=relation_ids,
                            prominence=prominence,
                            **item["identity"],
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
        "gate_evaluations": {
            _gate_evaluation_key(evaluation): copy.deepcopy(evaluation)
            for evaluation in registry.get("gate_evaluations", [])
            if isinstance(evaluation, dict)
        },
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
    for evaluation in state["gate_evaluations"].values():
        evaluation["_declared_status"] = evaluation.get("status")
        evaluation["effective_status"] = evaluation.get("status")
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
    state = _initial_state(registry)
    prevalidated_revalidations = _preflight_revalidations(
        registry, state, blocking
    )
    corrected_fact_keys = _semantic_checks(registry, blocking, reports)
    _identity_cycle_checks(registry, blocking)
    order, outgoing = _dependency_topology(registry, blocking)

    # Contractual cascade order: semantics, pipelines, challenges, moot gates,
    # live-support assessment, then publication. Revalidation is an authored
    # action applied after stale derivation and before downstream recomputation.
    derived_challenges = _evaluate_dependency_cascade(
        registry,
        state,
        corrected_fact_keys,
        reports,
        order,
        outgoing,
        blocking,
        derived,
        prevalidated_revalidations,
    )
    _gate_checks(registry, state, checkpoint, blocking, reports, derived)
    _applicability_checks(registry, blocking)
    _recompute_assessments(registry, state, derived_challenges, derived)
    if checkpoint == "C":
        _writing_strength_checks(registry, state, blocking, reports)
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
