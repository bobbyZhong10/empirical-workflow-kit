#!/usr/bin/env python3
"""Create or repair safe Claude Code and Codex views of canonical skills."""

from __future__ import annotations

import argparse
import datetime as dt
import os
import shutil
import sys
from pathlib import Path

import yaml


OWNER_MARKERS = ("Empirical Workflow Kit", "workflow.manifest.yaml")


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
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--replace-managed", action="store_true")
    return parser.parse_args()


def selected_runtimes(args: argparse.Namespace) -> list[str]:
    if args.all:
        return ["claude", "codex"]
    return ["claude" if args.claude else "codex"]


def owned_by_kit(path: Path) -> bool:
    skill_file = path / "SKILL.md" if path.is_dir() else path
    if not skill_file.is_file():
        return False
    body = skill_file.read_text(encoding="utf-8", errors="replace")
    return all(marker in body for marker in OWNER_MARKERS)


def backup_path(view: Path, name: str, stamp: str) -> Path:
    return view.parent / f"{view.name}-backup" / f"empirical-workflow-kit-{stamp}" / name


def install_entry(entry: Path, canonical: Path, target: str, *, check: bool,
                  replace: bool, stamp: str, is_agent: bool = False) -> tuple[bool, str]:
    label = str(entry)
    exists = entry.exists() or entry.is_symlink()
    if entry.is_symlink() and entry.exists() and os.readlink(entry) == target \
            and entry.resolve() == canonical.resolve():
        return True, f"ok      {label} -> {target}"
    if not exists:
        if check:
            return False, f"missing {label} -> {target}"
        entry.parent.mkdir(parents=True, exist_ok=True)
        entry.symlink_to(target)
        return True, f"created {label} -> {target}"

    status = "BROKEN_LINK" if entry.is_symlink() and not entry.exists() else "WRONG_TARGET"
    if not entry.is_symlink():
        status = "DUPLICATE_IMPLEMENTATION"
    if not replace:
        return False, f"{status} {label}; rerun with --replace-managed"

    if not entry.is_symlink() and not owned_by_kit(entry):
        return False, f"UNMANAGED {label}; refusing to replace another owner's file"
    if check:
        return False, f"{status} {label}; replacement required"

    if entry.is_symlink():
        saved_target = os.readlink(entry)
        backup = backup_path(entry.parent, entry.name, stamp)
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.symlink_to(saved_target)
        entry.unlink()
    else:
        backup = backup_path(entry.parent, entry.name, stamp)
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(entry), str(backup))
    entry.symlink_to(target)
    return True, f"relinked {label} -> {target}; backup {backup}"


def main() -> int:
    args = parse_args()
    repo = args.repo.expanduser().resolve()
    manifest = yaml.safe_load((repo / "workflow.manifest.yaml").read_text(encoding="utf-8"))
    canonical_skills = repo / manifest["canonical_source"]["skills_root"]
    stamp = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    results: list[tuple[bool, str]] = []

    for runtime in selected_runtimes(args):
        if args.project:
            view = repo / manifest["runtime_views"][runtime]["skills"]
            target_for = lambda name: os.path.relpath(canonical_skills / name, start=view)
        else:
            view = Path(os.path.expanduser(manifest["user_views"][runtime]["skills"]))
            target_for = lambda name: str((canonical_skills / name).resolve())
        for name in manifest["managed_skills"]:
            results.append(
                install_entry(
                    view / name,
                    canonical_skills / name,
                    target_for(name),
                    check=args.check,
                    replace=args.replace_managed,
                    stamp=stamp,
                )
            )

    if args.project and "claude" in selected_runtimes(args):
        view = repo / manifest["runtime_views"]["claude"]["agents"]
        canonical_agents = repo / manifest["canonical_source"]["agents_root"]
        for name in manifest.get("managed_agents", []):
            results.append(
                install_entry(
                    view / f"{name}.md",
                    canonical_agents / f"{name}.md",
                    os.path.relpath(canonical_agents / f"{name}.md", start=view),
                    check=args.check,
                    replace=args.replace_managed,
                    stamp=stamp,
                    is_agent=True,
                )
            )

    for _, message in results:
        print(message)
    return 0 if all(ok for ok, _ in results) else 1


if __name__ == "__main__":
    sys.exit(main())
