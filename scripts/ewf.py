#!/usr/bin/env python3
"""Resolve, diagnose, and run Empirical Workflow Kit runtime capabilities."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILE = "runtime-profile.yaml"
FALLBACK_PROFILE = "runtime-profile.example.yaml"

TOOL_PATHS = {
    "python": ("languages", "python_command"),
    "rscript": ("languages", "rscript_command"),
    "node": ("presentation", "node_command"),
    "quarto": ("presentation", "quarto_command"),
    "latexmk": ("documents", "latexmk_command"),
    "ghostscript": ("documents", "ghostscript_command"),
    "pdf-text": ("documents", "pdf_text_command"),
    "pdf-image": ("documents", "pdf_image_command"),
    "docx-text": ("documents", "docx_text_command"),
    "video": ("media", "video_command"),
}

VERSION_ARGS = {
    "python": ["--version"],
    "rscript": ["--version"],
    "node": ["--version"],
    "quarto": ["--version"],
    "latexmk": ["--version"],
    "ghostscript": ["--version"],
}

PATH_BINDINGS = {
    "EWF_CACHE_DIR",
    "EWF_STATE_DIR",
    "EWF_PRESENTATION_ASSETS",
    "EWF_COURSE_ROOT",
    "R_LIBS_USER",
}


class ProfileError(RuntimeError):
    """A runtime profile is missing or malformed."""


@dataclass
class Finding:
    status: str
    check: str
    detail: str


def nested(data: dict[str, Any], path: tuple[str, str]) -> Any:
    current: Any = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def expand(value: str, *, base: Path, path_like: bool) -> str:
    expanded = os.path.expandvars(os.path.expanduser(value))
    if path_like and not os.path.isabs(expanded):
        expanded = str((base / expanded).resolve())
    return expanded


class RuntimeProfile:
    def __init__(self, repo: Path, profile_path: Path):
        self.repo = repo.resolve()
        self.profile_path = profile_path.resolve()
        try:
            raw = yaml.safe_load(self.profile_path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise ProfileError(f"profile not found: {self.profile_path}") from exc
        except yaml.YAMLError as exc:
            raise ProfileError(f"invalid YAML in {self.profile_path}: {exc}") from exc
        if not isinstance(raw, dict) or not isinstance(raw.get("runtime_profile"), dict):
            raise ProfileError("profile must contain a runtime_profile mapping")
        self.data = raw["runtime_profile"]
        project_root = self.data.get("project_root", ".")
        if not isinstance(project_root, str):
            raise ProfileError("runtime_profile.project_root must be a string")
        self.project_root = Path(
            expand(project_root, base=self.profile_path.parent, path_like=True)
        )

    def environment(self) -> dict[str, str]:
        bindings = self.data.get("environment_bindings", {})
        if not isinstance(bindings, dict):
            raise ProfileError("environment_bindings must be a mapping")
        result = {
            "EWF_PROJECT_ROOT": str(self.project_root),
            "EWF_RUNTIME_PROFILE": str(self.profile_path),
        }
        for name, value in bindings.items():
            if value is None:
                continue
            if not isinstance(name, str) or not isinstance(value, (str, int, float, bool)):
                raise ProfileError("environment binding names and values must be scalar")
            result[name] = expand(
                str(value), base=self.project_root, path_like=name in PATH_BINDINGS
            )
        return result

    def command(self, name: str) -> list[str]:
        if name not in TOOL_PATHS:
            raise ProfileError(f"unknown tool {name!r}; choose from {', '.join(TOOL_PATHS)}")
        override = os.environ.get(f"EWF_{name.upper().replace('-', '_')}_COMMAND")
        raw = override if override is not None else nested(self.data, TOOL_PATHS[name])
        if raw is None or raw == "":
            raise ProfileError(f"tool {name!r} is not configured")
        if not isinstance(raw, str):
            raise ProfileError(f"command for {name!r} must be a string")
        words = shlex.split(os.path.expandvars(os.path.expanduser(raw)))
        if not words:
            raise ProfileError(f"command for {name!r} is empty")
        if "/" in words[0] and not os.path.isabs(words[0]):
            words[0] = str((self.project_root / words[0]).resolve())
        return words

    def resolved_executable(self, name: str) -> tuple[list[str], str | None]:
        command = self.command(name)
        executable = command[0]
        resolved = executable if os.path.isabs(executable) else shutil.which(executable)
        return command, resolved


def resolve_profile(repo: Path, supplied: Path | None) -> Path:
    if supplied:
        return supplied if supplied.is_absolute() else repo / supplied
    active = repo / DEFAULT_PROFILE
    return active if active.exists() else repo / FALLBACK_PROFILE


def load_profile(args: argparse.Namespace) -> RuntimeProfile:
    repo = args.repo.expanduser().resolve()
    return RuntimeProfile(repo, resolve_profile(repo, args.profile))


def command_env(profile: RuntimeProfile) -> dict[str, str]:
    return {**os.environ, **profile.environment()}


def cmd_env(args: argparse.Namespace) -> int:
    profile = load_profile(args)
    environment = profile.environment()
    if args.format == "json":
        print(json.dumps(environment, indent=2, sort_keys=True))
    else:
        for name in sorted(environment):
            print(f"export {name}={shlex.quote(environment[name])}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    profile = load_profile(args)
    arguments = args.arguments[1:] if args.arguments[:1] == ["--"] else args.arguments
    command = profile.command(args.tool) + arguments
    try:
        completed = subprocess.run(
            command,
            cwd=profile.project_root,
            env=command_env(profile),
            check=False,
        )
    except FileNotFoundError:
        print(f"EWF tool not found: {command[0]}", file=sys.stderr)
        return 127
    return completed.returncode


def first_line(text: str) -> str:
    return next((line.strip() for line in text.splitlines() if line.strip()), "no output")


def tool_finding(
    profile: RuntimeProfile,
    name: str,
    required: bool,
    minimum_version: str | None = None,
) -> Finding:
    missing_status = "BLOCK" if required else "WARN"
    try:
        command, executable = profile.resolved_executable(name)
    except ProfileError as exc:
        return Finding(missing_status, f"tool:{name}", str(exc))
    if not executable or not Path(executable).is_file():
        return Finding(missing_status, f"tool:{name}", f"not found: {command[0]}")
    probe = command + VERSION_ARGS.get(name, ["--version"])
    try:
        result = subprocess.run(
            probe,
            cwd=profile.project_root,
            env=command_env(profile),
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return Finding(missing_status, f"tool:{name}", f"probe failed: {exc}")
    output = first_line(result.stdout + "\n" + result.stderr)
    if result.returncode != 0:
        return Finding(missing_status, f"tool:{name}", f"probe exited {result.returncode}: {output}")
    if minimum_version:
        actual = parse_version(output)
        minimum = parse_version(str(minimum_version))
        if actual is None or minimum is None:
            return Finding(missing_status, f"tool:{name}", f"could not verify minimum {minimum_version}: {output}")
        width = max(len(actual), len(minimum))
        if actual + (0,) * (width - len(actual)) < minimum + (0,) * (width - len(minimum)):
            return Finding(missing_status, f"tool:{name}", f"{output}; requires >= {minimum_version}")
    return Finding("PASS", f"tool:{name}", f"{executable}: {output}")


def parse_version(text: str) -> tuple[int, ...] | None:
    match = re.search(r"(?<!\d)(\d+)(?:\.(\d+))?(?:\.(\d+))?", text)
    if not match:
        return None
    return tuple(int(part or 0) for part in match.groups())


def canon_findings(profile: RuntimeProfile, today: dt.date) -> list[Finding]:
    root = profile.repo / "skills" / "empirical-workflow" / "methods"
    findings: list[Finding] = []
    if not root.is_dir():
        return [Finding("BLOCK", "canon:root", f"missing: {root}")]
    for method_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        manifest_path = method_dir / "method.manifest.yaml"
        if not manifest_path.is_file():
            findings.append(Finding("BLOCK", f"canon:{method_dir.name}", "method.manifest.yaml missing"))
            continue
        try:
            data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            reviewed = dt.date.fromisoformat(str(data["reviewed_at"]))
            max_age = int(data["refresh"]["max_age_days"])
            sources = data["sources"]
            if not isinstance(sources, dict) or not sources:
                raise TypeError("sources must be a nonempty mapping")
        except (AttributeError, KeyError, TypeError, ValueError, yaml.YAMLError) as exc:
            findings.append(Finding("BLOCK", f"canon:{method_dir.name}", f"invalid manifest: {exc}"))
            continue
        missing = [name for name in sources.values() if not (method_dir / str(name)).is_file()]
        if missing:
            findings.append(Finding("BLOCK", f"canon:{method_dir.name}", f"missing sources: {', '.join(missing)}"))
            continue
        age = (today - reviewed).days
        if age < 0:
            findings.append(Finding("BLOCK", f"canon:{method_dir.name}", f"reviewed_at is {abs(age)} days in the future"))
        elif age > max_age:
            findings.append(Finding("WARN", f"canon:{method_dir.name}", f"stale: {age} days old; limit {max_age}"))
        else:
            findings.append(Finding("PASS", f"canon:{method_dir.name}", f"reviewed {reviewed.isoformat()}; age {age}/{max_age} days"))
    return findings


def r_package_findings(profile: RuntimeProfile) -> list[Finding]:
    validation = profile.data.get("validation", {})
    packages = validation.get("r_packages", []) if isinstance(validation, dict) else []
    if not packages:
        return []
    try:
        command = profile.command("rscript")
    except ProfileError as exc:
        return [Finding("BLOCK", "r-packages", str(exc))]
    expression = (
        "p<-c(" + ",".join(json.dumps(str(package)) for package in packages) + ");"
        "m<-p[!vapply(p,requireNamespace,logical(1),quietly=TRUE)];"
        "if(length(m)){cat(paste(m,collapse=','));quit(status=1)}"
    )
    try:
        result = subprocess.run(
            command + ["--vanilla", "-e", expression],
            cwd=profile.project_root,
            env=command_env(profile),
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [Finding("WARN", "r-packages", f"probe failed: {exc}")]
    if result.returncode:
        return [Finding("WARN", "r-packages", f"missing: {first_line(result.stdout + result.stderr)}")]
    return [Finding("PASS", "r-packages", f"available: {', '.join(packages)}")]


def secret_findings(profile: RuntimeProfile) -> list[Finding]:
    scholarly = profile.data.get("scholarly_sources", {})
    if not isinstance(scholarly, dict):
        return [Finding("BLOCK", "secrets", "scholarly_sources must be a mapping")]
    findings = []
    for key in ("contact_email_env", "openalex_key_env", "semantic_scholar_key_env"):
        variable = scholarly.get(key)
        if not variable:
            continue
        status = "PASS" if os.environ.get(str(variable)) else "WARN"
        detail = f"{variable} is set" if status == "PASS" else f"{variable} is not set"
        findings.append(Finding(status, f"secret:{key}", detail))
    return findings


def doctor(profile: RuntimeProfile, today: dt.date) -> list[Finding]:
    findings = [
        Finding("PASS", "profile", str(profile.profile_path)),
        Finding(
            "PASS" if profile.project_root.is_dir() else "BLOCK",
            "project-root",
            str(profile.project_root),
        ),
    ]
    validation = profile.data.get("validation", {})
    if not isinstance(validation, dict):
        findings.append(Finding("BLOCK", "validation", "validation must be a mapping"))
        findings.extend(canon_findings(profile, today))
        return findings
    required = validation.get("required_tools", ["python", "rscript"])
    optional = validation.get("optional_tools", ["node", "quarto", "latexmk", "ghostscript"])
    minimum_versions = validation.get("minimum_versions", {})
    if not isinstance(required, list) or not isinstance(optional, list):
        findings.append(Finding("BLOCK", "validation", "required_tools and optional_tools must be lists"))
        findings.extend(canon_findings(profile, today))
        return findings
    if not isinstance(minimum_versions, dict):
        findings.append(Finding("BLOCK", "validation", "minimum_versions must be a mapping"))
        minimum_versions = {}
    for name in required:
        findings.append(tool_finding(profile, str(name), True, minimum_versions.get(name)))
    for name in optional:
        findings.append(tool_finding(profile, str(name), False, minimum_versions.get(name)))
    findings.extend(r_package_findings(profile))
    findings.extend(secret_findings(profile))
    findings.extend(canon_findings(profile, today))
    return findings


def cmd_doctor(args: argparse.Namespace) -> int:
    profile = load_profile(args)
    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    findings = doctor(profile, today)
    if args.json:
        print(json.dumps([asdict(item) for item in findings], indent=2))
    else:
        for finding in findings:
            print(f"{finding.status:5} {finding.check:32} {finding.detail}")
        counts = {status: sum(item.status == status for item in findings) for status in ("PASS", "WARN", "BLOCK")}
        print(f"DOCTOR: {counts['PASS']} pass, {counts['WARN']} warn, {counts['BLOCK']} block")
    blocked = any(item.status == "BLOCK" for item in findings)
    warned = any(item.status == "WARN" for item in findings)
    return 1 if blocked or (args.strict and warned) else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--profile", type=Path)
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    env_parser = subparsers.add_parser("env", help="emit resolved environment bindings")
    env_parser.add_argument("--format", choices=("shell", "json"), default="shell")
    env_parser.set_defaults(handler=cmd_env)

    run_parser = subparsers.add_parser("run", help="run one configured logical tool")
    run_parser.add_argument("tool", choices=tuple(TOOL_PATHS))
    run_parser.add_argument("arguments", nargs=argparse.REMAINDER)
    run_parser.set_defaults(handler=cmd_run)

    doctor_parser = subparsers.add_parser("doctor", help="diagnose tools, secrets, and method canon freshness")
    doctor_parser.add_argument("--json", action="store_true")
    doctor_parser.add_argument("--strict", action="store_true")
    doctor_parser.add_argument("--today", help=argparse.SUPPRESS)
    doctor_parser.set_defaults(handler=cmd_doctor)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.handler(args)
    except ProfileError as exc:
        print(f"EWF profile error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
