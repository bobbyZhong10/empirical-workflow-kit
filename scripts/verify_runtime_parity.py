#!/usr/bin/env python3
"""Verify that Claude Code and Codex use one canonical workflow tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--project", action="store_true")
    scope.add_argument("--user", action="store_true")
    runtime = parser.add_mutually_exclusive_group(required=True)
    runtime.add_argument("--all", action="store_true")
    runtime.add_argument("--claude", action="store_true")
    runtime.add_argument("--codex", action="store_true")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def kit_version(repo: Path) -> str:
    source = (repo / "tools" / "validate_registry.py").read_text(encoding="utf-8")
    match = re.search(r'^KIT_VERSION = "([^"]+)"', source, re.MULTILINE)
    if not match:
        raise RuntimeError("KIT_VERSION is missing from tools/validate_registry.py")
    return match.group(1)


def selected_runtimes(args: argparse.Namespace) -> list[str]:
    if args.all:
        return ["claude", "codex"]
    return ["claude" if args.claude else "codex"]


def add_row(rows: list[dict[str, str]], *, view: Path, skill: str, status: str,
            target: str = "", resolved: str = "", skill_sha256: str = "") -> None:
    rows.append(
        {
            "view": str(view),
            "skill": skill,
            "link_target": target,
            "resolved": resolved,
            "skill_sha256": skill_sha256,
            "status": status,
        }
    )


def inspect_link(rows: list[dict[str, str]], view: Path, view_abs: Path, name: str,
                 canonical: Path, expected_target: str) -> None:
    entry = view_abs / name
    if not entry.exists() and not entry.is_symlink():
        add_row(rows, view=view, skill=name, status="MISSING_VIEW")
        return
    if not entry.is_symlink():
        add_row(rows, view=view, skill=name, status="DUPLICATE_IMPLEMENTATION")
        return
    target = os.readlink(entry)
    if target != expected_target:
        add_row(
            rows,
            view=view,
            skill=name,
            status="WRONG_TARGET",
            target=target,
        )
        return
    if not entry.exists():
        add_row(rows, view=view, skill=name, status="BROKEN_LINK", target=target)
        return
    resolved = entry.resolve()
    if resolved != canonical.resolve():
        add_row(rows, view=view, skill=name, status="WRONG_TARGET", target=target,
                resolved=str(resolved))
        return
    skill_file = resolved / "SKILL.md"
    if not skill_file.is_file():
        add_row(rows, view=view, skill=name, status="MISSING_SKILL", target=target,
                resolved=str(resolved))
        return
    add_row(
        rows,
        view=view,
        skill=name,
        status="ok",
        target=target,
        resolved=str(resolved),
        skill_sha256=digest(skill_file),
    )


def main() -> int:
    args = parse_args()
    repo = args.repo.expanduser().resolve()
    manifest_path = repo / "workflow.manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    version = kit_version(repo)
    rows: list[dict[str, str]] = []
    errors: list[str] = []
    notices: list[str] = []

    if str(manifest.get("workflow_version")) != version:
        errors.append(
            f"VERSION_MISMATCH manifest={manifest.get('workflow_version')} validator={version}"
        )

    managed = list(manifest["managed_skills"])
    canonical_root = repo / manifest["canonical_source"]["skills_root"]
    for name in managed:
        if not (canonical_root / name / "SKILL.md").is_file():
            errors.append(f"MISSING_SKILL {canonical_root / name / 'SKILL.md'}")

    for runtime in selected_runtimes(args):
        if args.project:
            view = Path(manifest["runtime_views"][runtime]["skills"])
            view_abs = repo / view
            expected = lambda name: f"../../skills/{name}"
        else:
            raw = manifest["user_views"][runtime]["skills"]
            view_abs = Path(os.path.expanduser(raw))
            view = view_abs
            expected = lambda name: str((canonical_root / name).resolve())
            if not view_abs.exists():
                notices.append(f"{runtime} user view not installed: {view_abs}")
                continue

        for name in managed:
            inspect_link(
                rows,
                view,
                view_abs,
                name,
                canonical_root / name,
                expected(name),
            )

        if view_abs.exists():
            for entry in view_abs.iterdir():
                if entry.name in managed or entry.name.startswith("."):
                    continue
                if entry.is_symlink():
                    try:
                        points_into_canonical = canonical_root.resolve() in entry.resolve().parents
                    except OSError:
                        points_into_canonical = False
                    if points_into_canonical:
                        add_row(rows, view=view, skill=entry.name, status="STALE_ENTRY",
                                target=os.readlink(entry))

    if args.project and "claude" in selected_runtimes(args):
        agents_view = Path(manifest["runtime_views"]["claude"]["agents"])
        for name in manifest.get("managed_agents", []):
            entry = repo / agents_view / f"{name}.md"
            canonical = repo / manifest["canonical_source"]["agents_root"] / f"{name}.md"
            target = f"../../agents/{name}.md"
            if not entry.is_symlink():
                status = "MISSING_VIEW" if not entry.exists() else "DUPLICATE_IMPLEMENTATION"
                add_row(rows, view=agents_view, skill=name, status=status)
            elif not entry.exists():
                add_row(rows, view=agents_view, skill=name, status="BROKEN_LINK",
                        target=os.readlink(entry))
            elif os.readlink(entry) != target or entry.resolve() != canonical.resolve():
                add_row(rows, view=agents_view, skill=name, status="WRONG_TARGET",
                        target=os.readlink(entry), resolved=str(entry.resolve()))
            else:
                add_row(rows, view=agents_view, skill=name, status="ok", target=target,
                        resolved=str(entry.resolve()), skill_sha256=digest(canonical))

    bad_rows = [row for row in rows if row["status"] != "ok"]
    ok = not errors and not bad_rows
    report = {
        "ok": ok,
        "manifest_version": str(manifest.get("workflow_version")),
        "validator_version": version,
        "rows": rows,
        "errors": errors,
        "notices": notices,
    }
    if args.as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"Empirical Workflow Kit {version}")
        for error in errors:
            print(error)
        for notice in notices:
            print(notice)
        for row in rows:
            target = f" -> {row['link_target']}" if row["link_target"] else ""
            suffix = " (stale copy)" if row["status"] == "DUPLICATE_IMPLEMENTATION" else ""
            print(f"{row['status']:24} {row['view']}/{row['skill']}{target}{suffix}")
        print("PARITY OK" if ok else "PARITY FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
