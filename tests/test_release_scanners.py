import importlib.util
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/replication-release/scripts"


def load(name):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_header_scanner_marks_direct_identifiers():
    scanner = load("scan_headers")
    hard, decide = scanner.classify(["email_address", "participant_id", "RecordedDate"])
    assert hard == ["email_address", "participant_id"]
    assert decide == ["RecordedDate"]


def test_value_scanner_masks_identifier_samples():
    scanner = load("scan_values")
    raw = "researcher@example.edu"
    assert scanner.PATS["email"].search(raw)
    masked = scanner.mask(raw)
    assert raw not in masked
    assert masked.startswith("res") and masked.endswith("du")


def test_qsf_scanner_reports_researcher_footprint(tmp_path):
    survey = tmp_path / "survey.qsf"
    survey.write_text(
        '{"UserID":"UR_12345678901","owner":"researcher@example.edu"}',
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "scan_qsf.py"), str(survey)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "email address" in result.stdout
    assert "qualtrics user id" in result.stdout

