"""Two runtimes, one canonical skill source.

Claude Code discovers skills under ``.claude/skills`` and Codex under
``.agents/skills``. Both directories are views: every managed entry is a
relative symlink into the canonical ``skills/`` tree, so neither runtime can
own a copy that drifts. ``workflow.manifest.yaml`` names the canonical source
and the views; ``scripts/verify_runtime_parity.py`` proves that the views
resolve to the canonical files; ``scripts/install_runtime_views.py`` creates
or repairs them without deleting anything.
"""

import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "workflow.manifest.yaml"
INSTALL = ROOT / "scripts" / "install_runtime_views.py"
VERIFY = ROOT / "scripts" / "verify_runtime_parity.py"

MANAGED_SKILLS = [
    "bibliography-audit",
    "course-site",
    "empirical-workflow",
    "latex-production",
    "literature-review",
    "manuscript-review",
    "preregister",
    "referee-response",
    "replication-release",
    "research-council",
    "research-sources",
    "research-talk",
    "slide-review",
    "teaching-lecture",
]
MANAGED_AGENTS = ["tikz-reviewer"]
PROJECT_VIEWS = {"claude": ".claude/skills", "codex": ".agents/skills"}


def kit_version():
    source = (ROOT / "tools" / "validate_registry.py").read_text(encoding="utf-8")
    return re.search(r'^KIT_VERSION = "([^"]+)"', source, re.M).group(1)


def manifest():
    return yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(script, args, cwd=None, env=None):
    merged = {**os.environ, "PYTHONNOUSERSITE": "1"}
    if env:
        merged.update(env)
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=cwd or ROOT,
        env=merged,
        text=True,
        capture_output=True,
        check=False,
    )


def clone(tmp_path, with_views=True):
    """Copy the parts of the repository the tools need, symlinks preserved."""
    target = tmp_path / "kit"
    target.mkdir()
    for name in ("workflow.manifest.yaml", "RESEARCH_PROTOCOL.md"):
        shutil.copy2(ROOT / name, target / name)
    (target / "tools").mkdir()
    shutil.copy2(ROOT / "tools" / "validate_registry.py", target / "tools" / "validate_registry.py")
    shutil.copytree(ROOT / "scripts", target / "scripts")
    shutil.copytree(ROOT / "agents", target / "agents")
    (target / "skills").mkdir()
    for skill in MANAGED_SKILLS:
        source = ROOT / "skills" / skill
        (target / "skills" / skill).mkdir()
        shutil.copy2(source / "SKILL.md", target / "skills" / skill / "SKILL.md")
    if with_views:
        for view in (".claude/skills", ".agents/skills", ".claude/agents"):
            shutil.copytree(ROOT / view, target / view, symlinks=True)
    return target


# --- manifest -----------------------------------------------------------------


def test_manifest_names_the_canonical_source_and_the_views():
    body = MANIFEST.read_text(encoding="utf-8")
    data = yaml.safe_load(body)
    assert data["schema_version"] == 1
    assert data["workflow_version"] == kit_version()
    assert data["canonical_source"] == {
        "protocol": "RESEARCH_PROTOCOL.md",
        "skills_root": "skills",
        "presentation_tooling": "presentation-tooling",
        "agents_root": "agents",
    }
    assert data["runtime_views"]["claude"] == {
        "skills": ".claude/skills",
        "agents": ".claude/agents",
    }
    assert data["runtime_views"]["codex"] == {"skills": ".agents/skills"}
    assert data["user_views"]["claude"] == {"skills": "~/.claude/skills"}
    assert data["user_views"]["codex"] == {"skills": "~/.agents/skills"}
    upstream = data["upstream"]
    assert upstream["repository"] == "https://github.com/ericluo04/claude-academic-workflow"
    assert re.fullmatch(r"[0-9a-f]{40}", upstream["baseline_commit"])
    assert re.fullmatch(r"[0-9a-f]{40}", upstream["inspected_commit"])
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", upstream["inspected_at"])
    assert "/Users/" not in body
    assert "/home/" not in body


def test_manifest_inventory_matches_the_canonical_tree():
    data = manifest()
    on_disk = sorted(p.name for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").is_file())
    assert data["managed_skills"] == MANAGED_SKILLS == on_disk
    agents = sorted(p.stem for p in (ROOT / "agents").glob("*.md"))
    assert data["managed_agents"] == MANAGED_AGENTS == agents


# --- committed project views ----------------------------------------------------


def test_project_views_are_relative_symlinks_into_the_canonical_tree():
    for skill in MANAGED_SKILLS:
        canonical = (ROOT / "skills" / skill).resolve()
        for view in PROJECT_VIEWS.values():
            link = ROOT / view / skill
            assert link.is_symlink(), f"{view}/{skill} is not a symlink"
            assert os.readlink(link) == f"../../skills/{skill}"
            assert link.resolve() == canonical
            assert sha256(link / "SKILL.md") == sha256(canonical / "SKILL.md")


def test_claude_and_codex_views_resolve_to_the_same_canonical_files():
    for skill in MANAGED_SKILLS:
        claude = (ROOT / PROJECT_VIEWS["claude"] / skill).resolve()
        codex = (ROOT / PROJECT_VIEWS["codex"] / skill).resolve()
        assert claude == codex == (ROOT / "skills" / skill).resolve()


def test_claude_agent_view_links_the_canonical_agent_file():
    for agent in MANAGED_AGENTS:
        link = ROOT / ".claude" / "agents" / f"{agent}.md"
        assert link.is_symlink()
        assert os.readlink(link) == f"../../agents/{agent}.md"
        assert link.resolve() == (ROOT / "agents" / f"{agent}.md").resolve()


def test_views_hold_only_managed_entries_and_no_regular_copies():
    for view in PROJECT_VIEWS.values():
        entries = sorted(p.name for p in (ROOT / view).iterdir() if not p.name.startswith("."))
        assert entries == MANAGED_SKILLS
        for entry in (ROOT / view).iterdir():
            if entry.name in MANAGED_SKILLS:
                assert entry.is_symlink(), f"{view}/{entry.name} is an editable copy"


def test_views_and_worktrees_are_tracked_or_ignored_deliberately():
    tracked = subprocess.run(
        ["git", "ls-files", "-z", ".claude/skills", ".agents/skills", ".claude/agents"],
        cwd=ROOT, text=True, capture_output=True, check=True,
    ).stdout.split("\0")
    tracked = [item for item in tracked if item]
    assert f".claude/skills/{MANAGED_SKILLS[0]}" in tracked
    assert f".agents/skills/{MANAGED_SKILLS[0]}" in tracked
    assert ".claude/agents/tikz-reviewer.md" in tracked
    for ignored in (".claude/worktrees/x", ".claude/settings.local.json", ".r-lib/x"):
        check = subprocess.run(
            ["git", "check-ignore", "-q", ignored], cwd=ROOT, check=False,
        )
        assert check.returncode == 0, f"{ignored} should be ignored"


def test_every_canonical_skill_declares_its_canonical_home():
    for skill in MANAGED_SKILLS:
        body = (ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
        assert "Empirical Workflow Kit" in body, skill
        assert "workflow.manifest.yaml" in body, skill


# --- verify_runtime_parity.py -----------------------------------------------------


def test_parity_verifier_passes_on_the_repository_and_reports_every_skill():
    result = run(VERIFY, ["--project", "--all", "--repo", str(ROOT)])
    assert result.returncode == 0, result.stdout + result.stderr
    for skill in MANAGED_SKILLS:
        assert skill in result.stdout
    assert "../../skills/empirical-workflow" in result.stdout
    assert kit_version() in result.stdout
    assert "PARITY OK" in result.stdout


def test_parity_verifier_json_output_names_resolved_paths_and_hashes():
    import json

    result = run(VERIFY, ["--project", "--all", "--repo", str(ROOT), "--json"])
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["ok"] is True
    assert report["manifest_version"] == kit_version()
    rows = {(row["view"], row["skill"]): row for row in report["rows"]}
    row = rows[(".claude/skills", "empirical-workflow")]
    assert row["link_target"] == "../../skills/empirical-workflow"
    assert Path(row["resolved"]) == (ROOT / "skills" / "empirical-workflow").resolve()
    assert row["skill_sha256"] == sha256(ROOT / "skills" / "empirical-workflow" / "SKILL.md")
    assert row["status"] == "ok"


def test_parity_verifier_fails_on_a_broken_link(tmp_path):
    kit = clone(tmp_path)
    shutil.rmtree(kit / "skills" / "preregister")
    result = run(VERIFY, ["--project", "--all", "--repo", str(kit)])
    assert result.returncode != 0
    assert "BROKEN_LINK" in result.stdout or "MISSING_SKILL" in result.stdout


def test_parity_verifier_fails_on_a_duplicate_regular_implementation(tmp_path):
    kit = clone(tmp_path)
    link = kit / ".agents" / "skills" / "preregister"
    link.unlink()
    shutil.copytree(kit / "skills" / "preregister", link)
    result = run(VERIFY, ["--project", "--all", "--repo", str(kit)])
    assert result.returncode != 0
    assert "DUPLICATE_IMPLEMENTATION" in result.stdout


def test_parity_verifier_fails_on_a_missing_view_entry(tmp_path):
    kit = clone(tmp_path)
    (kit / ".claude" / "skills" / "preregister").unlink()
    result = run(VERIFY, ["--project", "--all", "--repo", str(kit)])
    assert result.returncode != 0
    assert "MISSING_VIEW" in result.stdout


def test_parity_verifier_fails_on_a_link_to_the_wrong_skill(tmp_path):
    kit = clone(tmp_path)
    link = kit / ".claude" / "skills" / "preregister"
    link.unlink()
    link.symlink_to("../../skills/did")
    result = run(VERIFY, ["--project", "--all", "--repo", str(kit)])
    assert result.returncode != 0
    assert "WRONG_TARGET" in result.stdout


def test_parity_verifier_fails_on_a_stale_extra_managed_entry(tmp_path):
    kit = clone(tmp_path)
    (kit / ".claude" / "skills" / "old-workflow").symlink_to("../../skills/empirical-workflow")
    result = run(VERIFY, ["--project", "--all", "--repo", str(kit)])
    assert result.returncode != 0
    assert "STALE_ENTRY" in result.stdout


def test_parity_verifier_fails_on_a_manifest_version_mismatch(tmp_path):
    kit = clone(tmp_path)
    path = kit / "workflow.manifest.yaml"
    path.write_text(
        re.sub(r'workflow_version: "[^"]+"', 'workflow_version: "0.1"', path.read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    result = run(VERIFY, ["--project", "--all", "--repo", str(kit)])
    assert result.returncode != 0
    assert "VERSION_MISMATCH" in result.stdout


def test_parity_verifier_treats_an_absent_user_view_as_not_installed(tmp_path):
    kit = clone(tmp_path)
    home = tmp_path / "home"
    home.mkdir()
    result = run(VERIFY, ["--user", "--all", "--repo", str(kit)], env={"HOME": str(home)})
    assert result.returncode == 0, result.stdout + result.stderr
    assert "not installed" in result.stdout


def test_parity_verifier_flags_a_stale_user_level_copy(tmp_path):
    kit = clone(tmp_path)
    home = tmp_path / "home"
    (home / ".claude" / "skills").mkdir(parents=True)
    shutil.copytree(kit / "skills" / "preregister", home / ".claude" / "skills" / "preregister")
    result = run(VERIFY, ["--user", "--claude", "--repo", str(kit)], env={"HOME": str(home)})
    assert result.returncode != 0
    assert "DUPLICATE_IMPLEMENTATION" in result.stdout
    assert "stale" in result.stdout.lower()


# --- install_runtime_views.py -----------------------------------------------------


def test_installer_creates_relative_project_views(tmp_path):
    kit = clone(tmp_path, with_views=False)
    result = run(INSTALL, ["--project", "--all", "--repo", str(kit)])
    assert result.returncode == 0, result.stdout + result.stderr
    for skill in MANAGED_SKILLS:
        for view in PROJECT_VIEWS.values():
            link = kit / view / skill
            assert link.is_symlink()
            assert os.readlink(link) == f"../../skills/{skill}"
    agent_link = kit / ".claude" / "agents" / "tikz-reviewer.md"
    assert os.readlink(agent_link) == "../../agents/tikz-reviewer.md"
    assert "preregister" in result.stdout and "created" in result.stdout
    verify = run(VERIFY, ["--project", "--all", "--repo", str(kit)])
    assert verify.returncode == 0, verify.stdout


def test_installer_check_mode_reports_but_changes_nothing(tmp_path):
    kit = clone(tmp_path, with_views=False)
    result = run(INSTALL, ["--project", "--all", "--check", "--repo", str(kit)])
    assert result.returncode != 0
    assert not (kit / ".claude" / "skills").exists()
    assert "missing" in result.stdout.lower()


def test_installer_is_idempotent(tmp_path):
    kit = clone(tmp_path)
    result = run(INSTALL, ["--project", "--all", "--repo", str(kit)])
    assert result.returncode == 0, result.stdout + result.stderr
    assert "created" not in result.stdout
    assert "ok" in result.stdout.lower()


def test_installer_refuses_to_overwrite_a_regular_directory_without_the_flag(tmp_path):
    kit = clone(tmp_path)
    link = kit / ".claude" / "skills" / "preregister"
    link.unlink()
    shutil.copytree(kit / "skills" / "preregister", link)
    result = run(INSTALL, ["--project", "--claude", "--repo", str(kit)])
    assert result.returncode != 0
    assert not link.is_symlink() and link.is_dir()
    assert "--replace-managed" in result.stdout


def test_installer_replace_managed_backs_up_before_linking(tmp_path):
    kit = clone(tmp_path)
    link = kit / ".claude" / "skills" / "preregister"
    link.unlink()
    shutil.copytree(kit / "skills" / "preregister", link)
    marker = link / "note.txt"
    marker.write_text("keep me\n", encoding="utf-8")
    result = run(INSTALL, ["--project", "--claude", "--replace-managed", "--repo", str(kit)])
    assert result.returncode == 0, result.stdout + result.stderr
    assert link.is_symlink() and os.readlink(link) == "../../skills/preregister"
    backups = list((kit / ".claude" / "skills-backup").glob("empirical-workflow-kit-*/preregister/note.txt"))
    assert len(backups) == 1
    assert backups[0].read_text(encoding="utf-8") == "keep me\n"
    assert "backup" in result.stdout.lower()


def test_installer_will_not_replace_an_unmanaged_skill_with_a_managed_name(tmp_path):
    kit = clone(tmp_path)
    home = tmp_path / "home"
    foreign = home / ".claude" / "skills" / "preregister"
    foreign.mkdir(parents=True)
    foreign.joinpath("SKILL.md").write_text(
        "---\nname: preregister\ndescription: somebody else's skill\n---\n\nNot ours.\n",
        encoding="utf-8",
    )
    result = run(
        INSTALL, ["--user", "--claude", "--replace-managed", "--repo", str(kit)],
        env={"HOME": str(home)},
    )
    assert result.returncode != 0
    assert not foreign.is_symlink()
    assert "UNMANAGED" in result.stdout
    assert foreign.joinpath("SKILL.md").read_text(encoding="utf-8").endswith("Not ours.\n")


def test_installer_user_mode_links_to_the_canonical_checkout(tmp_path):
    kit = clone(tmp_path)
    home = tmp_path / "home"
    (home / ".claude" / "skills").mkdir(parents=True)
    (home / ".claude" / "skills" / "other-skill").mkdir()
    (home / ".claude" / "skills" / "other-skill" / "SKILL.md").write_text("---\nname: other-skill\n---\n")
    result = run(INSTALL, ["--user", "--all", "--repo", str(kit)], env={"HOME": str(home)})
    assert result.returncode == 0, result.stdout + result.stderr
    for skill in MANAGED_SKILLS:
        for base in (".claude/skills", ".agents/skills"):
            link = home / base / skill
            assert link.is_symlink()
            assert Path(os.readlink(link)).is_absolute()
            assert link.resolve() == (kit / "skills" / skill).resolve()
    assert (home / ".claude" / "skills" / "other-skill").is_dir()
    assert not (home / ".claude" / "skills" / "other-skill").is_symlink()
    verify = run(VERIFY, ["--user", "--all", "--repo", str(kit)], env={"HOME": str(home)})
    assert verify.returncode == 0, verify.stdout


def test_installer_reports_a_moved_checkout_and_relinks_on_request(tmp_path):
    kit = clone(tmp_path)
    home = tmp_path / "home"
    (home / ".agents" / "skills").mkdir(parents=True)
    stale = home / ".agents" / "skills" / "preregister"
    stale.symlink_to(tmp_path / "gone" / "skills" / "preregister")
    check = run(INSTALL, ["--user", "--codex", "--check", "--repo", str(kit)], env={"HOME": str(home)})
    assert check.returncode != 0
    assert "BROKEN_LINK" in check.stdout
    fix = run(INSTALL, ["--user", "--codex", "--replace-managed", "--repo", str(kit)], env={"HOME": str(home)})
    assert fix.returncode == 0, fix.stdout + fix.stderr
    assert stale.resolve() == (kit / "skills" / "preregister").resolve()


def test_installer_prints_source_target_and_status_for_every_skill(tmp_path):
    kit = clone(tmp_path)
    result = run(INSTALL, ["--project", "--all", "--repo", str(kit)])
    assert result.returncode == 0
    for skill in MANAGED_SKILLS:
        line = next(line for line in result.stdout.splitlines() if f"/{skill}" in line and ".claude/skills" in line)
        assert f"../../skills/{skill}" in line
        assert "ok" in line.lower()


# --- adapters -----------------------------------------------------------------


def test_adapters_route_both_runtimes_to_the_manifest_and_canonical_skills():
    for adapter, view in (("CLAUDE.md", ".claude/skills"), ("AGENTS.md", ".agents/skills")):
        body = (ROOT / adapter).read_text(encoding="utf-8")
        assert len(body.splitlines()) < 140, adapter
        for phrase in (
            "source of truth",
            "workflow.manifest.yaml",
            "RESEARCH_PROTOCOL.md",
            "skills/empirical-workflow/SKILL.md",
            "runtime-profile.yaml",
            "stale",
            "Speak with the user in Chinese. Write all repository artifacts in English.",
            view,
        ):
            assert phrase in body, (adapter, phrase)
        assert "canonical" in body.lower()


def test_repository_artifacts_contain_no_cjk_ideographs():
    excluded = {".git", ".venv", ".r-lib", ".pytest_cache", "__pycache__", ".worktrees"}
    text_suffixes = {
        ".R", ".bib", ".css", ".html", ".js", ".json", ".lua", ".md",
        ".mjs", ".py", ".qmd", ".scss", ".sh", ".txt", ".yaml", ".yml",
    }
    cjk = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
    findings = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in text_suffixes:
            continue
        if any(part in excluded for part in path.relative_to(ROOT).parts):
            continue
        body = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(body.splitlines(), 1):
            if cjk.search(line):
                findings.append(f"{path.relative_to(ROOT)}:{line_number}: {line}")
    assert not findings, "Repository artifacts must be English-only:\n" + "\n".join(findings)
