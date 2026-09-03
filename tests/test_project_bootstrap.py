import os
from pathlib import Path
import subprocess
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = ROOT / "scripts" / "bootstrap_project.py"


def run_bootstrap(target, *arguments):
    return subprocess.run(
        [sys.executable, str(BOOTSTRAP), str(target), *arguments],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_bootstrap_existing_project_creates_portable_contract_and_runtime_views(tmp_path):
    target = tmp_path / "research-project"
    target.mkdir()
    existing = target / "data" / "raw" / "source.csv"
    existing.parent.mkdir(parents=True)
    existing.write_text("id,value\n1,2\n", encoding="utf-8")

    result = run_bootstrap(target, "--all")
    assert result.returncode == 0, result.stdout + result.stderr
    assert existing.read_text(encoding="utf-8") == "id,value\n1,2\n"

    manifest = yaml.safe_load((target / "workflow.manifest.yaml").read_text(encoding="utf-8"))
    assert manifest["workflow_version"] == "2.7"
    assert manifest["canonical_source"]["skills_root"] == ".workflow/kit/skills"
    assert manifest["canonical_source"]["bootstrap_cli"] == (
        ".workflow/kit/scripts/bootstrap_project.py"
    )
    assert (target / ".workflow" / "kit").is_symlink()
    assert (target / ".workflow" / "kit").resolve() == ROOT
    start_prompt = target / "WORKFLOW_START.md"
    assert start_prompt.is_symlink()
    assert os.readlink(start_prompt) == (
        ".workflow/kit/skills/empirical-workflow/references/start-prompts.md"
    )
    assert start_prompt.resolve() == (
        ROOT / "skills" / "empirical-workflow" / "references" / "start-prompts.md"
    )

    for runtime_view in (target / ".claude" / "skills", target / ".agents" / "skills"):
        for skill in manifest["managed_skills"]:
            link = runtime_view / skill
            assert link.is_symlink()
            assert os.readlink(link) == f"../../.workflow/kit/skills/{skill}"
            assert link.resolve() == ROOT / "skills" / skill

    for path in (
        "RESEARCH_PROTOCOL.md",
        "THIRD_PARTY_NOTICES.md",
        "CLAUDE.md",
        "AGENTS.md",
        "research.yaml",
        "runtime-profile.yaml",
        "_status.md",
        "decision-log.md",
        "evidence/README.md",
    ):
        assert (target / path).is_file(), path

    project = yaml.safe_load((target / "research.yaml").read_text(encoding="utf-8"))
    assert project["project_name"] == ""
    assert project["analysis_languages"] == {"etl": "r", "estimation": "r"}
    assert project["current_stage"] == "stage_1_data_infrastructure"
    profile = yaml.safe_load((target / "runtime-profile.yaml").read_text(encoding="utf-8"))
    assert profile["runtime_profile"]["environment_bindings"]["EWF_PRESENTATION_ASSETS"] == (
        ".workflow/kit/presentation-tooling"
    )

    version = subprocess.run(
        [str(target / ".workflow" / "bin" / "validate_registry"), "--version"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )
    assert version.returncode == 0, version.stderr
    assert version.stdout.strip() == "empirical-workflow 2.7"

    environment = subprocess.run(
        [str(target / ".workflow" / "bin" / "ewf"), "env", "--format", "json"],
        cwd=target,
        text=True,
        capture_output=True,
        check=False,
    )
    assert environment.returncode == 0, environment.stderr
    assert yaml.safe_load(environment.stdout)["EWF_PROJECT_ROOT"] == str(target)

    parity = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "verify_runtime_parity.py"),
            "--project",
            "--all",
            "--repo",
            str(target),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert parity.returncode == 0, parity.stdout + parity.stderr
    assert "PARITY OK" in parity.stdout

    repeated = run_bootstrap(target, "--all")
    assert repeated.returncode == 0, repeated.stdout + repeated.stderr
    assert "already initialized" in repeated.stdout.lower()


def test_bootstrap_preserves_existing_project_adapter_and_configuration(tmp_path):
    target = tmp_path / "research-project"
    target.mkdir()
    (target / "CLAUDE.md").write_text("# Existing project instructions\n", encoding="utf-8")
    existing_config = "project_name: inherited_project\ncurrent_stage: stage_1_data_infrastructure\n"
    (target / "research.yaml").write_text(existing_config, encoding="utf-8")

    result = run_bootstrap(target, "--claude")
    assert result.returncode == 0, result.stdout + result.stderr
    adapter = (target / "CLAUDE.md").read_text(encoding="utf-8")
    assert adapter.startswith("# Existing project instructions\n")
    assert adapter.count("<!-- empirical-workflow-kit:adapter:start -->") == 1
    assert (target / "research.yaml").read_text(encoding="utf-8") == existing_config

    repeated = run_bootstrap(target, "--claude")
    assert repeated.returncode == 0, repeated.stdout + repeated.stderr
    assert (target / "CLAUDE.md").read_text(encoding="utf-8") == adapter


def test_bootstrap_refuses_an_unmanaged_skill_collision_before_writing(tmp_path):
    target = tmp_path / "research-project"
    collision = target / ".claude" / "skills" / "empirical-workflow"
    collision.mkdir(parents=True)
    (collision / "SKILL.md").write_text("---\nname: another-owner\n---\n", encoding="utf-8")

    result = run_bootstrap(target, "--claude")
    assert result.returncode != 0
    assert "UNMANAGED" in result.stdout + result.stderr
    assert not (target / "RESEARCH_PROTOCOL.md").exists()


def test_bootstrap_preserves_workflow_ignore_rules_and_refuses_wrapper_collision(tmp_path):
    target = tmp_path / "research-project"
    workflow = target / ".workflow"
    workflow.mkdir(parents=True)
    ignore = workflow / ".gitignore"
    ignore.write_text("cache/\n", encoding="utf-8")

    first = run_bootstrap(target, "--codex")
    assert first.returncode == 0, first.stdout + first.stderr
    assert ignore.read_text(encoding="utf-8") == "cache/\nkit\n"

    second_target = tmp_path / "wrapper-collision"
    wrapper = second_target / ".workflow" / "bin" / "ewf"
    wrapper.parent.mkdir(parents=True)
    wrapper.write_text("#!/bin/sh\necho third-party\n", encoding="utf-8")
    collided = run_bootstrap(second_target, "--codex")
    assert collided.returncode != 0
    assert "UNMANAGED" in collided.stdout + collided.stderr
    assert wrapper.read_text(encoding="utf-8") == "#!/bin/sh\necho third-party\n"
    assert not (second_target / "RESEARCH_PROTOCOL.md").exists()


def test_bootstrap_refuses_an_unmanaged_start_prompt_before_writing(tmp_path):
    target = tmp_path / "research-project"
    target.mkdir()
    start_prompt = target / "WORKFLOW_START.md"
    start_prompt.write_text("# Project-owned start instructions\n", encoding="utf-8")

    result = run_bootstrap(target, "--all")

    assert result.returncode != 0
    assert "UNMANAGED" in result.stdout + result.stderr
    assert start_prompt.read_text(encoding="utf-8") == "# Project-owned start instructions\n"
    assert not (target / "RESEARCH_PROTOCOL.md").exists()


def test_bootstrap_upgrades_its_prior_external_manifest_and_adds_start_prompt(tmp_path):
    target = tmp_path / "research-project"
    target.mkdir()
    first = run_bootstrap(target, "--all")
    assert first.returncode == 0, first.stdout + first.stderr

    (target / "WORKFLOW_START.md").unlink()
    manifest_path = target / "workflow.manifest.yaml"
    prior_manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    prior_manifest["canonical_source"].pop("start_prompts")
    manifest_path.write_text(
        yaml.safe_dump(prior_manifest, sort_keys=False, allow_unicode=False),
        encoding="utf-8",
    )

    upgraded = run_bootstrap(target, "--all")

    assert upgraded.returncode == 0, upgraded.stdout + upgraded.stderr
    current = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    assert current["canonical_source"]["start_prompts"] == (
        ".workflow/kit/skills/empirical-workflow/references/start-prompts.md"
    )
    assert (target / "WORKFLOW_START.md").is_symlink()


def test_bootstrap_does_not_treat_a_project_owned_manifest_as_managed(tmp_path):
    target = tmp_path / "research-project"
    target.mkdir()
    manifest_path = target / "workflow.manifest.yaml"
    manifest_path.write_text("project_owned: true\n", encoding="utf-8")

    result = run_bootstrap(target, "--codex")

    assert result.returncode != 0
    assert "UNMANAGED" in result.stdout + result.stderr
    assert manifest_path.read_text(encoding="utf-8") == "project_owned: true\n"
    assert not (target / "RESEARCH_PROTOCOL.md").exists()
