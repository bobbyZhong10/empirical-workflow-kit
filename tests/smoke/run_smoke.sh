#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
cd "$repo_root"

# Prefer the repository-local R library when it is present, while preserving
# any caller-supplied R libraries after it in the search path.
if [[ -d "$repo_root/.r-lib" ]]; then
  export R_LIBS="$repo_root/.r-lib${R_LIBS:+:$R_LIBS}"
fi

rm -f tests/smoke/output/smoke_table.md \
  tests/smoke/output/handoff_recovery.md \
  tests/smoke/output/identification_pause.md

python3 tests/smoke/generate_panel.py
python3 tests/smoke/recover_handoff.py tests/smoke/handoff-fixture

project_config=tests/smoke/handoff-fixture/research.yaml
failed_identification_output=$(mktemp)
invalid_output=$(mktemp)
invalid_identity_output=$(mktemp)
registry_output=$(mktemp)
trap 'rm -f "$failed_identification_output" "$invalid_output" "$invalid_identity_output" "$registry_output"' EXIT

registry_python="$repo_root/.venv/bin/python"

assert_registry_code() {
  local expected_code=$1
  "$registry_python" - "$registry_output" "$expected_code" <<'PY'
import json
import sys

payload = json.load(open(sys.argv[1], encoding="utf-8"))
codes = {
    item["code"]
    for section in ("blocking", "reports", "derived")
    for item in payload[section]
}
if sys.argv[2] not in codes:
    raise SystemExit(f"missing registry code {sys.argv[2]}; observed {sorted(codes)}")
PY
}

run_registry_fixture() {
  local expected_status=$1
  local fixture=$2
  local expected_code=$3
  local fixture_path="tests/smoke/registry-fixtures/$fixture"

  if [[ "$expected_status" == pass ]]; then
    if ! "$registry_python" tools/validate_registry.py "$fixture_path" \
      --checkpoint C --format json >"$registry_output"; then
      echo "$fixture registry unexpectedly failed" >&2
      cat "$registry_output" >&2
      exit 1
    fi
  else
    if "$registry_python" tools/validate_registry.py "$fixture_path" \
      --checkpoint C --format json >"$registry_output"; then
      echo "$fixture registry unexpectedly passed" >&2
      cat "$registry_output" >&2
      exit 1
    fi
  fi
  assert_registry_code "$expected_code"
}

run_registry_fixture fail pipeline-stale STALE_CLAIM
assert_registry_code PUBLICATION_INELIGIBLE

run_registry_fixture pass machine-revalidation REVALIDATED_CLAIM
"$registry_python" - "$registry_output" <<'PY'
import json
import sys

payload = json.load(open(sys.argv[1], encoding="utf-8"))
claim = payload["state"]["claims"]["H1.r1"]
assert claim["availability"] == "current"
assert claim["assessment"] == "supported"
assert claim["pipeline_id"] == "p2"
assert claim["revalidation"]["evidence_card"] == "EC-2"
assert claim["revalidation"]["resolved_comparison"] == {
    "from_value": 2.0,
    "to_value": 2.005,
}
assert payload["state"]["evidence_cards"]["EC-2"]["pipeline_id"] == "p2"
PY

run_registry_fixture fail semantic-correction MACHINE_REVALIDATION_FORBIDDEN
assert_registry_code SEMANTIC_STALE_CLAIM
run_registry_fixture fail semantic-disclosure SEMANTIC_DISCLOSURE_REQUIRED
run_registry_fixture fail incomplete-release GATE_RELEASE_INCOMPLETE
run_registry_fixture pass handoff REGISTRY_VALID
run_registry_fixture fail failed-identification GATE_TRIGGERED
run_registry_fixture fail missing-gate-evaluation GATE_NOT_EVALUATED
run_registry_fixture fail false-complete-coverage GATE_COVERAGE_MISMATCH

run_registry_fixture pass per-evaluation-post-hoc GATE_POST_HOC
"$registry_python" - "$registry_output" <<'PY'
import json
import sys

payload = json.load(open(sys.argv[1], encoding="utf-8"))
post_hoc = {
    item["pipeline_id"]: item["post_hoc"]
    for item in payload["reports"]
    if item["code"] == "GATE_POST_HOC"
}
assert post_hoc == {"p1": True, "p2": False}
PY

run_registry_fixture fail mixed-output MIXED_PIPELINE_OUTPUT
run_registry_fixture pass reconciliation STALE_CLAIM
"$registry_python" - "$registry_output" <<'PY'
import json
import sys

payload = json.load(open(sys.argv[1], encoding="utf-8"))
assert payload["state"]["claims"]["H1.r1"]["availability"] == "stale"
assert payload["state"]["outputs"]["reconciliation"]["status"] == "current"
PY

run_registry_fixture fail incomplete-substitute APPLICABILITY_SUBSTITUTE_INCOMPLETE

if Rscript tests/smoke/verify_panel.R tests/smoke/panel-contract.yaml "$project_config" \
  tests/smoke/failed-identification.yaml >"$failed_identification_output" 2>&1; then
  echo "failed identification diagnostic unexpectedly permitted estimation" >&2
  exit 1
fi
if ! grep -Fqx "Error: Failed identifying diagnostic: formal analysis blocked" "$failed_identification_output"; then
  echo "failed identification diagnostic did not emit the mandatory stop" >&2
  cat "$failed_identification_output" >&2
  exit 1
fi
test ! -f tests/smoke/output/smoke_table.md
grep -Fqx -- "- Formal estimation status: blocked" tests/smoke/output/identification_pause.md

Rscript tests/smoke/verify_panel.R tests/smoke/panel-contract.yaml "$project_config"

if Rscript tests/smoke/verify_panel.R tests/smoke/invalid-contract.yaml "$project_config" >"$invalid_output" 2>&1; then
  echo "invalid contract unexpectedly passed" >&2
  exit 1
fi
if ! grep -Fqx "Error: Data contract validation failed" "$invalid_output"; then
  echo "invalid contract did not emit the required validation failure" >&2
  cat "$invalid_output" >&2
  exit 1
fi
if Rscript tests/smoke/verify_panel.R tests/smoke/invalid-identity-contract.yaml "$project_config" >"$invalid_identity_output" 2>&1; then
  echo "contract with a mismatched project identity unexpectedly passed" >&2
  exit 1
fi
if ! grep -Fqx "Error: Data contract validation failed" "$invalid_identity_output"; then
  echo "identity mismatch did not emit the required validation failure" >&2
  cat "$invalid_identity_output" >&2
  exit 1
fi
test -f tests/smoke/output/smoke_table.md
test -f tests/smoke/output/handoff_recovery.md
