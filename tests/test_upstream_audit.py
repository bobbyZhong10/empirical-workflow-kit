from pathlib import Path
import subprocess
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "scripts" / "audit_upstream.py"


def command(*args, cwd=None):
    return subprocess.run(
        list(args), cwd=cwd, text=True, capture_output=True, check=False
    )


def test_repository_upstream_lock_is_complete_offline():
    result = command(
        sys.executable, str(AUDIT), "--repo", str(ROOT), "--offline"
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "LOCAL_MISSING" not in result.stdout
    assert "UPSTREAM AUDIT:" in result.stdout


def test_audit_reports_an_upstream_object_change(tmp_path):
    repo = tmp_path / "upstream"
    repo.mkdir()
    command("git", "init", "-q", cwd=repo)
    command("git", "config", "user.email", "test@example.invalid", cwd=repo)
    command("git", "config", "user.name", "Test", cwd=repo)
    source = repo / "source.md"
    destination = repo / "adapted.md"
    source.write_text("version one\n", encoding="utf-8")
    destination.write_text("adapted\n", encoding="utf-8")
    command("git", "add", ".", cwd=repo)
    command("git", "commit", "-qm", "baseline", cwd=repo)
    baseline = command("git", "rev-parse", "HEAD", cwd=repo).stdout.strip()
    oid = command("git", "rev-parse", f"{baseline}:source.md", cwd=repo).stdout.strip()
    lock = {
        "schema_version": 1,
        "repository": "https://example.invalid/upstream.git",
        "baseline_commit": baseline,
        "entries": [
            {
                "source": "source.md",
                "source_oid": oid,
                "disposition": "adapted",
                "destinations": ["adapted.md"],
            }
        ],
    }
    lock_path = repo / "upstream.lock.yaml"
    lock_path.write_text(yaml.safe_dump(lock), encoding="utf-8")
    source.write_text("version two\n", encoding="utf-8")
    command("git", "add", "source.md", cwd=repo)
    command("git", "commit", "-qm", "change", cwd=repo)

    result = command(
        sys.executable,
        str(AUDIT),
        "--repo", str(repo),
        "--lock", str(lock_path),
        "--upstream-dir", str(repo),
        "--ref", "HEAD",
        "--fail-on-change",
    )
    assert result.returncode == 1
    assert "CHANGED" in result.stdout
    assert "source.md" in result.stdout
