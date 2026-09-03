from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = [
    ROOT / "examples" / "research-talk" / "talk.qmd",
    ROOT / "examples" / "teaching-lecture" / "lecture.qmd",
]


def test_presentation_examples_are_small_offline_acceptance_fixtures():
    for path in EXAMPLES:
        body = path.read_text(encoding="utf-8")
        _, raw, _ = body.split("---", 2)
        metadata = yaml.safe_load(raw)
        reveal = metadata["format"]["revealjs"]
        assert reveal["embed-resources"] is True
        assert reveal["html-math-method"] == "katex"
        assert reveal["self-contained-math"] is True
        assert "presentation-tooling/stage-slide.lua" in body
        assert len(body.splitlines()) < 70


def test_presentation_smoke_invokes_every_quality_gate_through_runtime_cli():
    body = (ROOT / "tests" / "smoke" / "run_presentation_smoke.sh").read_text(encoding="utf-8")
    for phrase in (
        "scripts/ewf.py",
        "run quarto",
        "deck-check.mjs",
        "stage-check.mjs",
        "check-offline.py",
        "PRESENTATION-SMOKE: PASS",
    ):
        assert phrase in body
