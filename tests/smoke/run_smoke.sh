#!/usr/bin/env bash
set -euo pipefail

python3 tests/smoke/generate_panel.py
Rscript tests/smoke/verify_panel.R tests/smoke/panel-contract.yaml

invalid_output=$(mktemp)
trap 'rm -f "$invalid_output"' EXIT
if Rscript tests/smoke/verify_panel.R tests/smoke/invalid-contract.yaml >"$invalid_output" 2>&1; then
  echo "invalid contract unexpectedly passed" >&2
  exit 1
fi
if ! grep -Fqx "Error: Data contract validation failed" "$invalid_output"; then
  echo "invalid contract did not emit the required validation failure" >&2
  cat "$invalid_output" >&2
  exit 1
fi
test -f tests/smoke/output/smoke_table.md
