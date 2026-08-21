#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
cd "$repo_root"

registry_python="$repo_root/.venv/bin/python"
registry_command="$repo_root/tools/validate_registry"
bootstrap_command="bash tests/bootstrap_test_environment.sh"

preflight_error() {
  echo "ERROR: smoke-test preflight failed: $1" >&2
  echo "Prepare this repository-local environment with: $bootstrap_command" >&2
  exit 1
}

process_status_message() {
  local status=$1
  if (( status > 128 )); then
    printf 'terminated by signal %d (exit status %d)' "$((status - 128))" "$status"
  else
    printf 'exited with status %d' "$status"
  fi
}

print_diagnostic_excerpt() {
  local diagnostic_path=$1
  local label=$2
  echo "Diagnostic excerpt for $label (first 20 lines, at most 4096 bytes):" >&2
  if [[ -s "$diagnostic_path" ]]; then
    LC_ALL=C head -c 4096 "$diagnostic_path" | tr -cd '\11\12\15\40-\176' | sed -n '1,20p' >&2
  else
    echo "(no diagnostic output captured)" >&2
  fi
}

if [[ ! -x "$registry_python" ]]; then
  preflight_error "missing executable $registry_python"
fi

python_preflight_output=$(mktemp)
if "$registry_python" - >"$python_preflight_output" 2>&1 <<'PY'
try:
    import pyarrow
except Exception as error:
    raise SystemExit(f"pyarrow failed to import: {type(error).__name__}: {error}")

try:
    import yaml
except Exception as error:
    raise SystemExit(f"yaml failed to import: {type(error).__name__}: {error}")
PY
then
  rm -f "$python_preflight_output"
else
  python_preflight_status=$?
  print_diagnostic_excerpt "$python_preflight_output" "repository-local Python import preflight"
  rm -f "$python_preflight_output"
  preflight_error "the repository-local Python environment cannot import one or more required modules (PyArrow, PyYAML; $(process_status_message "$python_preflight_status"))"
fi

if ! command -v Rscript >/dev/null 2>&1; then
  preflight_error "Rscript is not installed or is not on PATH"
fi

# Prefer the repository-local R library when it is present, while preserving
# any caller-supplied R libraries after it in the search path.
if [[ -d "$repo_root/.r-lib" ]]; then
  export R_LIBS="$repo_root/.r-lib${R_LIBS:+:$R_LIBS}"
fi

check_r_package() {
  local package=$1
  local package_output
  package_output=$(mktemp)

  # Run one package per R process.  A broken package can crash R while its
  # namespace loads; isolating it keeps that crash out of the workflow run.
  if Rscript --vanilla -e '
    package <- commandArgs(trailingOnly = TRUE)[[1]]
    if (!requireNamespace(package, quietly = TRUE)) quit(status = 1)
  ' "$package" >"$package_output" 2>&1; then
    rm -f "$package_output"
  else
    local package_status=$?
    print_diagnostic_excerpt "$package_output" "R package '$package'"
    rm -f "$package_output"
    preflight_error "R package '$package' is unavailable or cannot be loaded in an isolated R session ($(process_status_message "$package_status"))"
  fi
}

for r_package in arrow yaml fixest modelsummary; do
  check_r_package "$r_package"
done

rm -f tests/smoke/output/smoke_table.md \
  tests/smoke/output/handoff_recovery.md \
  tests/smoke/output/identification_pause.md

"$registry_python" tests/smoke/generate_panel.py
"$registry_python" tests/smoke/recover_handoff.py tests/smoke/handoff-fixture

project_config=tests/smoke/handoff-fixture/research.yaml
failed_identification_output=$(mktemp)
invalid_output=$(mktemp)
invalid_identity_output=$(mktemp)
registry_output=$(mktemp)
writing_registry_root=$(mktemp -d)
trap 'rm -f "$failed_identification_output" "$invalid_output" "$invalid_identity_output" "$registry_output"; rm -rf "$writing_registry_root"' EXIT

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

assert_registry_lacks_code() {
  local unexpected_code=$1
  "$registry_python" - "$registry_output" "$unexpected_code" <<'PY'
import json
import sys

payload = json.load(open(sys.argv[1], encoding="utf-8"))
codes = {
    item["code"]
    for section in ("blocking", "reports", "derived")
    for item in payload[section]
}
if sys.argv[2] in codes:
    raise SystemExit(f"unexpected registry code {sys.argv[2]}; observed {sorted(codes)}")
PY
}

run_registry_fixture() {
  local expected_status=$1
  local fixture=$2
  local expected_code=$3
  local fixture_path="tests/smoke/registry-fixtures/$fixture"

  if [[ "$expected_status" == pass ]]; then
    if ! "$registry_command" "$fixture_path" \
      --checkpoint C --format json >"$registry_output"; then
      echo "$fixture registry unexpectedly failed" >&2
      cat "$registry_output" >&2
      exit 1
    fi
  else
    if "$registry_command" "$fixture_path" \
      --checkpoint C --format json >"$registry_output"; then
      echo "$fixture registry unexpectedly passed" >&2
      cat "$registry_output" >&2
      exit 1
    fi
  fi
  assert_registry_code "$expected_code"
}

run_writing_registry_fixture() {
  local expected_status=$1
  local fixture=$2
  local expected_code=$3
  local staged_fixture="$writing_registry_root/$fixture"

  mkdir -p "$staged_fixture"
  cp -R tests/smoke/registry-fixtures/handoff/. "$staged_fixture"
  cp -R "tests/smoke/registry-fixtures/writing-strength/$fixture/." "$staged_fixture"

  if [[ "$expected_status" == pass ]]; then
    if ! "$registry_command" "$staged_fixture" \
      --checkpoint C --format json >"$registry_output"; then
      echo "$fixture writing-strength registry unexpectedly failed" >&2
      cat "$registry_output" >&2
      exit 1
    fi
  else
    if "$registry_command" "$staged_fixture" \
      --checkpoint C --format json >"$registry_output"; then
      echo "$fixture writing-strength registry unexpectedly passed" >&2
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

run_writing_registry_fixture pass traced-upgrade UPGRADE_TRACE_MISSING
"$registry_python" - "$registry_output" <<'PY'
import json
import sys

payload = json.load(open(sys.argv[1], encoding="utf-8"))
warnings = [item for item in payload["reports"] if item["code"] == "UPGRADE_TRACE_MISSING"]
assert [item["site"] for item in warnings] == ["paper/assertions.md#title-retention"]
assert not payload["blocking"]
assert not any(
    item.get("site") == "paper/assertions.md#abstract-retention"
    for item in payload["blocking"] + warnings
)
PY

run_writing_registry_fixture fail overclaim OVERCLAIM_RESIDUAL
assert_registry_lacks_code MODEL_INTERNAL_SIGNIFICANT_UNSUPPORTED

run_writing_registry_fixture fail model-internal MODEL_INTERNAL_SIGNIFICANT_UNSUPPORTED
assert_registry_lacks_code OVERCLAIM_RESIDUAL
assert_registry_lacks_code UNDERCLAIM_RESIDUAL

run_writing_registry_fixture fail narrowing-propagation NARROWING_NOT_PROPAGATED
run_writing_registry_fixture fail buried-counterevidence COUNTEREVIDENCE_BURIED
run_writing_registry_fixture pass immediate-recovery IMMEDIATE_RECOVERY
run_writing_registry_fixture pass underclaim UNDERCLAIM_RESIDUAL

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
