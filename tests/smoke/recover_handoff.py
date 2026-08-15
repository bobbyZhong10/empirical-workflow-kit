"""Recover the durable smoke-project state in the required runtime order."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
READ_ORDER = (
    "RESEARCH_PROTOCOL.md",
    "research.yaml",
    "_status.md",
    "evidence-card.md",
    "decision-log.md",
)


def require(text: str, expected: str, label: str) -> None:
    if expected not in text:
        raise SystemExit(f"Handoff recovery failed: {label}")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 tests/smoke/recover_handoff.py PROJECT_STATE_DIR")

    state_dir = (ROOT / sys.argv[1]).resolve()
    protocol = (ROOT / READ_ORDER[0]).read_text(encoding="utf-8")
    config = yaml.safe_load((state_dir / READ_ORDER[1]).read_text(encoding="utf-8"))
    status = (state_dir / READ_ORDER[2]).read_text(encoding="utf-8")
    evidence = (state_dir / READ_ORDER[3]).read_text(encoding="utf-8")
    decision_tail = "\n".join(
        (state_dir / READ_ORDER[4]).read_text(encoding="utf-8").splitlines()[-4:]
    )
    handoff = (state_dir / "handoff.md").read_text(encoding="utf-8")

    expected = config["analysis_input_contract"]
    require(protocol, "## Mandatory pause", "portable protocol was not loaded")
    require(status, f"Project name: {config['project_name']}", "project identity mismatch")
    require(status, f"Current stage: {config['current_stage']}", "current stage mismatch")
    require(status, "Current evidence card: tests/smoke/handoff-fixture/evidence-card.md", "evidence pointer missing")
    require(evidence, f"Project name: {config['project_name']}", "evidence project mismatch")
    require(evidence, f"Data version: {expected['data_version']}", "evidence data version mismatch")
    require(decision_tail, "Proceed from Stage 5 to Stage 6a", "latest decision missing")
    require(handoff, "Completed stage: stage_5_measurement", "completed stage missing")
    require(handoff, "Unresolved pause: none", "pause state missing")

    output = ROOT / "tests" / "smoke" / "output" / "handoff_recovery.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "# Handoff Recovery\n\n"
        f"- Read order: {' -> '.join(READ_ORDER)}\n"
        f"- Project: {config['project_name']}\n"
        f"- Recovered stage: {config['current_stage']}\n"
        f"- Data version: {expected['data_version']}\n"
        "- Open mandatory pause: none\n"
        "- Next action: Validate the locked analysis input and run the reduced-form smoke estimate.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
