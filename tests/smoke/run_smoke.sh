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
trap 'rm -f "$failed_identification_output" "$invalid_output" "$invalid_identity_output"' EXIT

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
