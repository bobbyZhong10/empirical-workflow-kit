#!/usr/bin/env python3
"""Attach Empirical Workflow Kit to an existing research project safely."""

from __future__ import annotations

import argparse
import copy
import os
import stat
import sys
from pathlib import Path

import yaml


KIT_ROOT = Path(__file__).resolve().parents[1]
ADAPTER_START = "<!-- empirical-workflow-kit:adapter:start -->"
ADAPTER_END = "<!-- empirical-workflow-kit:adapter:end -->"
WRAPPER_MARKER = "# Empirical Workflow Kit managed wrapper"


class BootstrapError(RuntimeError):
    """The target cannot be initialized without overwriting unowned content."""


def selected_runtimes(args: argparse.Namespace) -> list[str]:
    if args.all:
        return ["claude", "codex"]
    return ["claude" if args.claude else "codex"]


def relative_link(source: Path, parent: Path) -> str:
    return os.path.relpath(source, start=parent)


def expected_manifest(source: dict) -> dict:
    manifest = copy.deepcopy(source)
    manifest["canonical_source"] = {
        "kit_root": ".workflow/kit",
        "protocol": "RESEARCH_PROTOCOL.md",
        "skills_root": ".workflow/kit/skills",
        "start_prompts": ".workflow/kit/skills/empirical-workflow/references/start-prompts.md",
        "presentation_tooling": ".workflow/kit/presentation-tooling",
        "agents_root": ".workflow/kit/agents",
        "bootstrap_cli": ".workflow/kit/scripts/bootstrap_project.py",
        "runtime_cli": ".workflow/bin/ewf",
        "registry_cli": ".workflow/bin/validate_registry",
        "registry_validator": ".workflow/kit/tools/validate_registry.py",
        "registry_scaffold": ".workflow/kit/tools/scaffold_registry.py",
        "figure_renderer": ".workflow/kit/tools/render_figure_macros.py",
        "parity_cli": ".workflow/kit/scripts/verify_runtime_parity.py",
        "installer_cli": ".workflow/kit/scripts/install_runtime_views.py",
        "upstream_lock": ".workflow/kit/upstream.lock.yaml",
    }
    manifest["external_project"] = {
        "kit_link": ".workflow/kit",
        "bootstrap_command": ".workflow/kit/scripts/bootstrap_project.py",
    }
    return manifest


def adapter_block(runtime: str) -> str:
    body = (KIT_ROOT / ("CLAUDE.md" if runtime == "claude" else "AGENTS.md")).read_text(
        encoding="utf-8"
    ).rstrip()
    return f"{ADAPTER_START}\n{body}\n{ADAPTER_END}\n"


def merged_adapter(existing: str | None, runtime: str) -> str:
    block = adapter_block(runtime)
    if existing is None or not existing.strip():
        return block
    if ADAPTER_START not in existing and ADAPTER_END not in existing:
        return existing.rstrip() + "\n\n" + block
    if existing.count(ADAPTER_START) != 1 or existing.count(ADAPTER_END) != 1:
        raise BootstrapError(f"UNMANAGED malformed workflow adapter markers in {runtime} adapter")
    before, remainder = existing.split(ADAPTER_START, 1)
    if ADAPTER_END not in remainder:
        raise BootstrapError(f"UNMANAGED malformed workflow adapter markers in {runtime} adapter")
    _, after = remainder.split(ADAPTER_END, 1)
    return before + block + after.lstrip("\n")


def check_link(path: Path, source: Path, target: str) -> None:
    if not path.exists() and not path.is_symlink():
        return
    if not path.is_symlink() or os.readlink(path) != target or path.resolve() != source.resolve():
        raise BootstrapError(f"UNMANAGED {path}; refusing to replace an existing entry")


def check_managed_file(path: Path, expected: str) -> None:
    if path.exists() and path.read_text(encoding="utf-8") != expected:
        raise BootstrapError(f"UNMANAGED {path}; refusing to overwrite a different file")


def check_project_manifest(path: Path, expected_data: dict, expected_text: str) -> None:
    if not path.exists() or path.read_text(encoding="utf-8") == expected_text:
        return
    try:
        existing_data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise BootstrapError(f"UNMANAGED {path}; refusing to overwrite a different file") from exc
    prior_data = copy.deepcopy(expected_data)
    prior_data["canonical_source"].pop("start_prompts", None)
    if existing_data != prior_data:
        raise BootstrapError(f"UNMANAGED {path}; refusing to overwrite a different file")


def write_missing(path: Path, content: str, written: list[str], root: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    written.append(str(path.relative_to(root)))


def write_changed(path: Path, content: str, written: list[str], root: Path) -> None:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    written.append(str(path.relative_to(root)))


def write_executable(path: Path, content: str, root: Path, written: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text(encoding="utf-8") != content:
        path.write_text(content, encoding="utf-8")
        written.append(str(path.relative_to(root)))
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def ensure_line(path: Path, line: str, root: Path, written: list[str]) -> None:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    lines = existing.splitlines()
    if line in lines:
        return
    updated = existing
    if updated and not updated.endswith("\n"):
        updated += "\n"
    updated += line + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(updated, encoding="utf-8")
    written.append(str(path.relative_to(root)))


def external_profile() -> str:
    profile = yaml.safe_load((KIT_ROOT / "runtime-profile.example.yaml").read_text(encoding="utf-8"))
    profile["runtime_profile"]["profile_name"] = "external_project"
    profile["runtime_profile"]["environment_bindings"]["EWF_PRESENTATION_ASSETS"] = (
        ".workflow/kit/presentation-tooling"
    )
    return yaml.safe_dump(profile, sort_keys=False, allow_unicode=False)


def bootstrap(target: Path, runtimes: list[str]) -> list[str]:
    target = target.expanduser().resolve()
    if target == KIT_ROOT:
        raise BootstrapError("target is the kit repository; external bootstrap is not required")
    if not target.is_dir():
        raise BootstrapError(f"target project does not exist or is not a directory: {target}")

    source_manifest = yaml.safe_load((KIT_ROOT / "workflow.manifest.yaml").read_text(encoding="utf-8"))
    project_manifest = expected_manifest(source_manifest)
    source_paths = source_manifest["canonical_source"]
    kit_skills = KIT_ROOT / source_paths["skills_root"]
    kit_agents = KIT_ROOT / source_paths["agents_root"]
    start_prompt_source = KIT_ROOT / source_paths["start_prompts"]
    start_prompt_target = project_manifest["canonical_source"]["start_prompts"]
    manifest_text = yaml.safe_dump(project_manifest, sort_keys=False, allow_unicode=False)
    kit_link = target / ".workflow" / "kit"
    check_link(kit_link, KIT_ROOT, str(KIT_ROOT))
    check_managed_file(target / "RESEARCH_PROTOCOL.md", (KIT_ROOT / "RESEARCH_PROTOCOL.md").read_text(encoding="utf-8"))
    check_managed_file(target / "THIRD_PARTY_NOTICES.md", (KIT_ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8"))
    check_project_manifest(target / "workflow.manifest.yaml", project_manifest, manifest_text)
    check_link(target / "WORKFLOW_START.md", start_prompt_source, start_prompt_target)

    view_paths = {
        "claude": target / project_manifest["runtime_views"]["claude"]["skills"],
        "codex": target / project_manifest["runtime_views"]["codex"]["skills"],
    }
    for runtime in runtimes:
        view = view_paths[runtime]
        for name in project_manifest["managed_skills"]:
            source = kit_skills / name
            link_target = relative_link(target / ".workflow" / "kit" / "skills" / name, view)
            check_link(view / name, source, link_target)
    if "claude" in runtimes:
        agents_view = target / project_manifest["runtime_views"]["claude"]["agents"]
        for name in project_manifest.get("managed_agents", []):
            source = kit_agents / f"{name}.md"
            link_target = relative_link(target / ".workflow" / "kit" / "agents" / f"{name}.md", agents_view)
            check_link(agents_view / f"{name}.md", source, link_target)

    adapter_outputs: dict[str, str] = {}
    for runtime in runtimes:
        adapter = target / ("CLAUDE.md" if runtime == "claude" else "AGENTS.md")
        existing = adapter.read_text(encoding="utf-8") if adapter.exists() else None
        adapter_outputs[runtime] = merged_adapter(existing, runtime)

    validate_wrapper = f"""#!/usr/bin/env bash
{WRAPPER_MARKER}
set -euo pipefail
project_root=$(cd "$(dirname "${{BASH_SOURCE[0]}}")/../.." && pwd)
exec "$project_root/.workflow/kit/tools/validate_registry" "$@"
"""
    ewf_wrapper = f"""#!/usr/bin/env bash
{WRAPPER_MARKER}
set -euo pipefail
project_root=$(cd "$(dirname "${{BASH_SOURCE[0]}}")/../.." && pwd)
kit_root="$project_root/.workflow/kit"
exec "$kit_root/.venv/bin/python" "$kit_root/scripts/ewf.py" \\
  --repo "$kit_root" --profile "$project_root/runtime-profile.yaml" "$@"
"""
    wrappers = {
        target / ".workflow" / "bin" / "validate_registry": validate_wrapper,
        target / ".workflow" / "bin" / "ewf": ewf_wrapper,
    }
    for path, expected in wrappers.items():
        if not path.exists():
            continue
        existing = path.read_text(encoding="utf-8")
        if existing != expected and WRAPPER_MARKER not in existing:
            raise BootstrapError(f"UNMANAGED {path}; refusing to overwrite a different wrapper")

    written: list[str] = []
    kit_link.parent.mkdir(parents=True, exist_ok=True)
    if not kit_link.is_symlink():
        kit_link.symlink_to(KIT_ROOT)
        written.append(".workflow/kit")
    ensure_line(target / ".workflow" / ".gitignore", "kit", target, written)
    write_missing(target / "RESEARCH_PROTOCOL.md", (KIT_ROOT / "RESEARCH_PROTOCOL.md").read_text(encoding="utf-8"), written, target)
    write_missing(target / "THIRD_PARTY_NOTICES.md", (KIT_ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8"), written, target)
    write_changed(target / "workflow.manifest.yaml", manifest_text, written, target)
    start_prompt_link = target / "WORKFLOW_START.md"
    if not start_prompt_link.is_symlink():
        start_prompt_link.symlink_to(start_prompt_target)
        written.append(start_prompt_link.name)

    templates = kit_skills / "empirical-workflow" / "templates"
    write_missing(target / "research.yaml", (templates / "research-template.yaml").read_text(encoding="utf-8"), written, target)
    write_missing(target / "runtime-profile.yaml", external_profile(), written, target)
    write_missing(target / "_status.md", (templates / "status-template.md").read_text(encoding="utf-8"), written, target)
    write_missing(target / "decision-log.md", (templates / "decision-log-template.md").read_text(encoding="utf-8"), written, target)
    write_missing(target / "evidence" / "README.md", (templates / "evidence-index-template.md").read_text(encoding="utf-8"), written, target)

    for runtime in runtimes:
        adapter = target / ("CLAUDE.md" if runtime == "claude" else "AGENTS.md")
        existing = adapter.read_text(encoding="utf-8") if adapter.exists() else None
        merged = adapter_outputs[runtime]
        if existing != merged:
            adapter.write_text(merged, encoding="utf-8")
            written.append(adapter.name)
        view = view_paths[runtime]
        view.mkdir(parents=True, exist_ok=True)
        for name in project_manifest["managed_skills"]:
            link = view / name
            if not link.is_symlink():
                link.symlink_to(relative_link(target / ".workflow" / "kit" / "skills" / name, view))
                written.append(str(link.relative_to(target)))

    if "claude" in runtimes:
        agents_view = target / project_manifest["runtime_views"]["claude"]["agents"]
        agents_view.mkdir(parents=True, exist_ok=True)
        for name in project_manifest.get("managed_agents", []):
            link = agents_view / f"{name}.md"
            if not link.is_symlink():
                link.symlink_to(relative_link(target / ".workflow" / "kit" / "agents" / f"{name}.md", agents_view))
                written.append(str(link.relative_to(target)))

    write_executable(target / ".workflow" / "bin" / "validate_registry", validate_wrapper, target, written)
    write_executable(target / ".workflow" / "bin" / "ewf", ewf_wrapper, target, written)
    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="existing research-project root")
    runtime = parser.add_mutually_exclusive_group(required=True)
    runtime.add_argument("--all", action="store_true")
    runtime.add_argument("--claude", action="store_true")
    runtime.add_argument("--codex", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        written = bootstrap(args.target, selected_runtimes(args))
    except (BootstrapError, OSError, UnicodeError, yaml.YAMLError) as exc:
        print(f"BOOTSTRAP FAILED: {exc}", file=sys.stderr)
        return 1
    if written:
        print("BOOTSTRAP OK")
        for path in written:
            print(f"created {path}")
    else:
        print("BOOTSTRAP OK: project already initialized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
