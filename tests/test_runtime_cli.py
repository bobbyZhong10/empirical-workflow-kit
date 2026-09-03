import json
import os
from pathlib import Path
import subprocess
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "ewf.py"


def write_profile(path, *, python_command=sys.executable, required=None):
    data = {
        "runtime_profile": {
            "profile_name": "test",
            "project_root": str(ROOT),
            "environment_bindings": {
                "EWF_CACHE_DIR": ".cache-test",
                "EWF_STATE_DIR": ".state-test",
                "EWF_PRESENTATION_ASSETS": "presentation-tooling",
            },
            "languages": {
                "python_command": python_command,
                "rscript_command": "Rscript",
            },
            "scholarly_sources": {},
            "documents": {},
            "media": {},
            "presentation": {},
            "validation": {
                "required_tools": required if required is not None else ["python"],
                "optional_tools": [],
                "minimum_versions": {},
                "r_packages": [],
            },
        }
    }
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def run(*arguments, env=None):
    merged = {**os.environ, "PYTHONNOUSERSITE": "1"}
    if env:
        merged.update(env)
    return subprocess.run(
        [sys.executable, str(CLI), *arguments],
        cwd=ROOT,
        env=merged,
        text=True,
        capture_output=True,
        check=False,
    )


def test_env_resolves_profile_paths_and_never_emits_nulls(tmp_path):
    profile = tmp_path / "runtime-profile.yaml"
    write_profile(profile)
    result = run("--repo", str(ROOT), "--profile", str(profile), "env", "--format", "json")
    assert result.returncode == 0, result.stderr
    environment = json.loads(result.stdout)
    assert environment["EWF_PROJECT_ROOT"] == str(ROOT)
    assert environment["EWF_CACHE_DIR"] == str(ROOT / ".cache-test")
    assert environment["EWF_PRESENTATION_ASSETS"] == str(ROOT / "presentation-tooling")
    assert all(value is not None for value in environment.values())


def test_run_uses_the_configured_logical_command(tmp_path):
    profile = tmp_path / "runtime-profile.yaml"
    write_profile(profile)
    result = run(
        "--repo", str(ROOT), "--profile", str(profile),
        "run", "python", "-c", "print('PROFILE-RUN-OK')",
    )
    assert result.returncode == 0, result.stderr
    assert "PROFILE-RUN-OK" in result.stdout


def test_run_accepts_an_optional_argument_separator(tmp_path):
    profile = tmp_path / "runtime-profile.yaml"
    write_profile(profile)
    result = run(
        "--repo", str(ROOT), "--profile", str(profile),
        "run", "python", "--", "-c", "print('SEPARATOR-OK')",
    )
    assert result.returncode == 0, result.stderr
    assert "SEPARATOR-OK" in result.stdout


def test_environment_command_override_precedes_the_profile(tmp_path):
    profile = tmp_path / "runtime-profile.yaml"
    write_profile(profile, python_command="definitely-not-python")
    result = run(
        "--repo", str(ROOT), "--profile", str(profile),
        "run", "python", "-c", "print('OVERRIDE-OK')",
        env={"EWF_PYTHON_COMMAND": sys.executable},
    )
    assert result.returncode == 0, result.stderr
    assert "OVERRIDE-OK" in result.stdout


def test_doctor_blocks_a_required_broken_tool(tmp_path):
    profile = tmp_path / "runtime-profile.yaml"
    write_profile(profile, python_command="definitely-not-a-real-command")
    result = run(
        "--repo", str(ROOT), "--profile", str(profile), "doctor", "--json"
    )
    assert result.returncode == 1
    findings = json.loads(result.stdout)
    assert any(
        item["status"] == "BLOCK" and item["check"] == "tool:python"
        for item in findings
    )


def test_doctor_reports_stale_canons_without_blocking_default_mode(tmp_path):
    profile = tmp_path / "runtime-profile.yaml"
    write_profile(profile)
    result = run(
        "--repo", str(ROOT), "--profile", str(profile),
        "doctor", "--json", "--today", "2028-09-03",
    )
    assert result.returncode == 0
    findings = json.loads(result.stdout)
    stale = [item for item in findings if item["check"].startswith("canon:")]
    assert len(stale) == 9
    assert all(item["status"] == "WARN" for item in stale)


def test_doctor_strict_mode_fails_on_warnings(tmp_path):
    profile = tmp_path / "runtime-profile.yaml"
    write_profile(profile)
    result = run(
        "--repo", str(ROOT), "--profile", str(profile),
        "doctor", "--strict", "--today", "2028-09-03",
    )
    assert result.returncode == 1
    assert "DOCTOR:" in result.stdout


def test_doctor_enforces_declared_minimum_versions(tmp_path):
    profile = tmp_path / "runtime-profile.yaml"
    write_profile(profile)
    data = yaml.safe_load(profile.read_text(encoding="utf-8"))
    data["runtime_profile"]["validation"]["minimum_versions"] = {"python": "99.0"}
    profile.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    result = run(
        "--repo", str(ROOT), "--profile", str(profile), "doctor", "--json"
    )
    assert result.returncode == 1
    findings = json.loads(result.stdout)
    python = next(item for item in findings if item["check"] == "tool:python")
    assert python["status"] == "BLOCK"
    assert "requires >= 99.0" in python["detail"]
