"""Scaffold and extend a registry from artefacts a project already has.

Roughly three fifths of a registry is mechanically derivable: file skeletons,
assertion-site stubs for sentences discovery has already located, and reported
figures read out of an analysis artefact. Authoring those by hand is what makes
the system too expensive to adopt, and none of it requires judgement.

What this tool never generates is the part that does require judgement:
whether an assertion is causal or discriminating, what an acceptance gate's
band should be, or which challenge bears on identification. Stubs are emitted
with those fields present and empty so the validator asks for them.

    python3 tools/scaffold_registry.py init      <registry>
    python3 tools/scaffold_registry.py sites     <registry> [--limit N]
    python3 tools/scaffold_registry.py figures   <registry> --artifact PATH --pipeline ID
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:  # script or module
    from validate_registry import (
        REGISTRY_FILES,
        _classify_assertion_text,
        _compiled_lexical_markers,
        _resolve_registry_source,
        _tex_section_role,
        load_registry,
        validate_registry,
    )
except ModuleNotFoundError:  # pragma: no cover - import shim
    from tools.validate_registry import (  # type: ignore[no-redef]
        REGISTRY_FILES,
        _classify_assertion_text,
        _compiled_lexical_markers,
        _resolve_registry_source,
        _tex_section_role,
        load_registry,
        validate_registry,
    )

SKELETONS: dict[str, str] = {
    "pipelines.yaml": (
        "# One entry per analysis pipeline generation. Superseding a pipeline\n"
        "# derives stale for everything bound to it.\n"
        "pipelines:\n"
        "  - pipeline_id: p1\n"
        "    status: current\n"
        "    first_formal_batch_at: \"\"   # required: timestamp of the first formal batch\n"
        "analysis_window: [\"\", \"\"]   # required: ISO start and end dates\n"
        "used_fields: []\n"
        "changes: []\n"
    ),
    "references.yaml": (
        "# One entry per work the manuscript cites. A citation is a claim about\n"
        "# the literature, so it carries the same obligation as any other: a\n"
        "# locator someone else can check, and a person who checked it.\n"
        "references: []\n"
    ),
    "claims.yaml": "claims: []\n",
    "evidence_cards.yaml": "evidence_cards: []\n",
    "evidence_relations.yaml": "evidence_relations: []\n",
    "reported_figures.yaml": "reported_figures: []\nrevalidations: []\n",
    "outputs.yaml": (
        "outputs:\n"
        "  - output_id: paper\n"
        "    kind: submission\n"
        "    status: current\n"
        "    pipeline_id: p1\n"
        "    claim_revision_ids: []\n"
        "    reported_figure_ids: []\n"
        "    # Discovery scans these files for assertions the registry has not\n"
        "    # registered. Without them, coverage is reported as unknown.\n"
        "    manuscript_sources: []\n"
        "    discovery_exclusions: []\n"
    ),
    "gates.yaml": (
        "# Acceptance gates are pre-result commitments. declared_at must precede\n"
        "# the pipeline's first formal batch or the evaluation is marked post hoc.\n"
        "gate_definitions: []\n"
        "gate_evaluations: []\n"
        "gate_set_confirmation:\n"
        "  checkpoint: B\n"
        "  complete: false\n"
        "  signed_by: \"\"\n"
        "  signed_at: \"\"\n"
    ),
    "semantics.yaml": "semantic_facts: []\nsemantic_equivalence_decisions: []\n",
    "derived_fields.yaml": "derived_fields: []\n",
    "applicability.yaml": "applicability: []\n",
}


def init(root: Path) -> list[str]:
    root.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for name in REGISTRY_FILES:
        target = root / name
        if target.exists():
            continue
        target.write_text(SKELETONS.get(name, f"{name.removesuffix('.yaml')}: []\n"), encoding="utf-8")
        written.append(name)
    return written


EXISTING_ANCHOR = re.compile(r"\\(?:claimsite|scopesite)\s*\{([^{}]+)\}")


def _existing_anchor(source: Path | None, line: int) -> str | None:
    """Reuse the anchor already on the line, if the author put one there.

    Suggesting a fresh name for a line that already carries ``\\claimsite{...}``
    tells the author to add a second anchor to the same sentence, which then
    resolves ambiguously. An anchor is a name for a place, and the place may
    already have one.
    """

    if source is None:
        return None
    try:
        lines = source.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return None
    if not 1 <= line <= len(lines):
        return None
    match = EXISTING_ANCHOR.search(lines[line - 1])
    return match.group(1).strip() if match else None


def _anchor_suggestion(path: str, line: int, excerpt: str) -> str:
    words = re.findall(r"[A-Za-z]+", excerpt.lower())[:3]
    stem = "-".join(words) or "assertion"
    return f"{stem}-{line}"


def sites(root: Path, limit: int | None = None) -> str:
    """Emit assertion-site stubs for sentences discovery reported unregistered."""

    report = validate_registry(load_registry(root), "C")
    findings = [
        item
        for section in ("blocking", "reports")
        for item in report[section]
        if item["code"] == "ASSERTION_SITE_UNREGISTERED"
    ]
    if not findings:
        return "# discovery reported no unregistered assertions\n"
    markers = _compiled_lexical_markers(load_registry(root))
    lines = [
        "# Generated stubs. Paste under the owning claim's assertion_sites and",
        "# add the anchor macro to the manuscript at the quoted line.",
        "# assertion_type and the judgement fields are deliberately left empty.",
    ]
    for finding in findings[: limit or len(findings)]:
        excerpt = finding.get("excerpt", "")
        strength, tier, _, _ = _classify_assertion_text(
            excerpt, {"qualifier_scope": "sentence"}, markers
        )
        role = None
        source = None
        try:
            source = _resolve_registry_source(load_registry(root), finding["path"])
            if source.suffix.lower() == ".tex":
                role = _tex_section_role(
                    source.read_text(encoding="utf-8").splitlines(), finding["line"]
                )
        except (OSError, ValueError):
            source = None
            role = None
        anchor = _existing_anchor(source, finding["line"]) or _anchor_suggestion(
            finding["path"], finding["line"], excerpt
        )
        lines += [
            "",
            f"# {finding['path']}:{finding['line']}  {excerpt}",
            f"- path: {finding['path']}",
            f"  anchor: {anchor}",
            f"  section_role: {role or ''}   # required",
            "  assertion_type:            # world | negative | methodological | discriminating | model_internal | hypothesis",
            f"  declared_tier: {tier}       # classifier read strength {strength}",
            "  qualifier_scope: sentence",
            "  counterevidence_prominence: null",
            "  underlying_precision:",
            "    estimate_id:             # <evidence_card_id>#<cell>",
            "    significant_at: null",
            "    has_sampling_distribution: null",
            "    n: null",
            "  scope_declaration: null",
            "  power_basis: null",
            "  upgrade_justification: null",
            "  alternative_explanation: null",
            "  as_modeled: null",
        ]
    return "\n".join(lines) + "\n"


def _flatten(payload: Any, prefix: str = "") -> list[tuple[str, Any]]:
    out: list[tuple[str, Any]] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            out += _flatten(value, f"{prefix}.{key}" if prefix else str(key))
    elif isinstance(payload, (int, float)) and not isinstance(payload, bool):
        out.append((prefix, payload))
    return out


def figures(root: Path, artifact: str, pipeline_id: str) -> str:
    """Emit reported-figure stubs for every numeric leaf of an artefact."""

    path = _resolve_registry_source(load_registry(root), artifact)
    payload = json.loads(path.read_text(encoding="utf-8"))
    leaves = _flatten(payload)
    if not leaves:
        return f"# {artifact} holds no numeric leaves\n"
    lines = [
        "# Generated stubs. Every value is read from the artefact, so the",
        "# validator's grounding check passes as long as the artefact does not",
        "# change. Delete the figures the manuscript does not report.",
        "reported_figures:",
    ]
    for locator, value in leaves:
        figure_id = re.sub(r"[^A-Za-z0-9]+", "_", locator).strip("_")
        lines += [
            f"  - figure_id: {figure_id}",
            f"    pipeline_id: {pipeline_id}",
            f"    value: {value}",
            f"    source_artifact: {artifact}",
            f"    source_locator: {locator}",
            "    paper_locations: []",
        ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p_init = sub.add_parser("init", help="write missing registry skeletons")
    p_init.add_argument("registry", type=Path)
    p_sites = sub.add_parser("sites", help="stub the assertions discovery found")
    p_sites.add_argument("registry", type=Path)
    p_sites.add_argument("--limit", type=int, default=None)
    p_figs = sub.add_parser("figures", help="stub reported figures from an artefact")
    p_figs.add_argument("registry", type=Path)
    p_figs.add_argument("--artifact", required=True)
    p_figs.add_argument("--pipeline", required=True)
    args = parser.parse_args(argv)

    if args.command == "init":
        written = init(args.registry)
        print("\n".join(written) if written else "# registry already initialised")
    elif args.command == "sites":
        sys.stdout.write(sites(args.registry, args.limit))
    else:
        sys.stdout.write(figures(args.registry, args.artifact, args.pipeline))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
