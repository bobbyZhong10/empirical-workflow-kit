#!/usr/bin/env python3
"""Compare locked upstream source objects with a Git ref and local destinations."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]


def git(repo: Path, *arguments: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *arguments],
        text=True,
        capture_output=True,
        check=False,
    )
    if check and result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip() if result.returncode == 0 else ""


def object_id(repo: Path, revision: str, source: str) -> str | None:
    value = git(repo, "rev-parse", f"{revision}:{source}", check=False)
    return value if len(value) == 40 else None


def validate_lock(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["lock root must be a mapping"]
    for key in ("schema_version", "repository", "baseline_commit", "entries"):
        if key not in data:
            errors.append(f"missing lock key: {key}")
    if not isinstance(data.get("entries"), list):
        errors.append("entries must be a list")
        return errors
    seen = set()
    for index, entry in enumerate(data["entries"]):
        if not isinstance(entry, dict):
            errors.append(f"entry {index} must be a mapping")
            continue
        for key in ("source", "source_oid", "disposition", "destinations"):
            if key not in entry:
                errors.append(f"entry {index} missing {key}")
        source = entry.get("source")
        if source in seen:
            errors.append(f"duplicate source: {source}")
        seen.add(source)
        oid = entry.get("source_oid", "")
        if not isinstance(oid, str) or len(oid) != 40:
            errors.append(f"invalid source_oid for {source}")
        if not isinstance(entry.get("destinations"), list):
            errors.append(f"destinations must be a list for {source}")
    return errors


def local_rows(root: Path, entries: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows = []
    for entry in entries:
        missing = [path for path in entry["destinations"] if not (root / path).exists()]
        rows.append(
            {
                "source": entry["source"],
                "status": "LOCAL_MISSING" if missing else "LOCAL_OK",
                "detail": ", ".join(missing) if missing else entry["disposition"],
            }
        )
    return rows


def upstream_rows(
    upstream: Path,
    entries: list[dict[str, Any]],
    baseline: str,
    revision: str,
) -> list[dict[str, str]]:
    rows = []
    for entry in entries:
        source = entry["source"]
        expected = entry["source_oid"]
        locked = object_id(upstream, baseline, source)
        current = object_id(upstream, revision, source)
        if locked != expected:
            status = "LOCK_MISMATCH"
            detail = f"expected {expected}; baseline has {locked or 'missing'}"
        elif current is None:
            status = "SOURCE_MISSING"
            detail = f"absent at {revision}"
        elif current != expected:
            status = "CHANGED"
            detail = f"{expected[:12]} -> {current[:12]}"
        else:
            status = "UNCHANGED"
            detail = current[:12]
        rows.append({"source": source, "status": status, "detail": detail})
    return rows


def print_rows(rows: list[dict[str, str]]) -> None:
    for row in rows:
        print(f"{row['status']:14} {row['source']:42} {row['detail']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--lock", type=Path, default=Path("upstream.lock.yaml"))
    parser.add_argument("--upstream-dir", type=Path)
    parser.add_argument("--ref", default="HEAD")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--fail-on-change", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = args.repo.expanduser().resolve()
    lock_path = args.lock if args.lock.is_absolute() else root / args.lock
    try:
        data = yaml.safe_load(lock_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        print(f"UPSTREAM LOCK ERROR: {exc}", file=sys.stderr)
        return 2
    errors = validate_lock(data)
    if errors:
        for error in errors:
            print(f"UPSTREAM LOCK ERROR: {error}", file=sys.stderr)
        return 2

    rows = local_rows(root, data["entries"])
    temporary: tempfile.TemporaryDirectory[str] | None = None
    try:
        if not args.offline:
            if args.upstream_dir:
                upstream = args.upstream_dir.expanduser().resolve()
            else:
                temporary = tempfile.TemporaryDirectory(prefix="ewf-upstream-audit-")
                upstream = Path(temporary.name) / "repo"
                result = subprocess.run(
                    ["git", "clone", "--quiet", "--filter=blob:none", "--no-checkout", data["repository"], str(upstream)],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                if result.returncode:
                    print(f"UPSTREAM CLONE ERROR: {result.stderr.strip()}", file=sys.stderr)
                    return 2
            rows.extend(
                upstream_rows(
                    upstream,
                    data["entries"],
                    str(data["baseline_commit"]),
                    args.ref,
                )
            )
    finally:
        if temporary is not None:
            temporary.cleanup()

    if args.as_json:
        print(json.dumps({"baseline_commit": data["baseline_commit"], "rows": rows}, indent=2))
    else:
        print_rows(rows)
        counts: dict[str, int] = {}
        for row in rows:
            counts[row["status"]] = counts.get(row["status"], 0) + 1
        print("UPSTREAM AUDIT: " + ", ".join(f"{key.lower()}={counts[key]}" for key in sorted(counts)))

    hard = {"LOCAL_MISSING", "LOCK_MISMATCH", "SOURCE_MISSING"}
    if args.fail_on_change:
        hard.add("CHANGED")
    return 1 if any(row["status"] in hard for row in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
