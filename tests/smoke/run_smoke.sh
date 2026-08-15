#!/usr/bin/env bash
set -euo pipefail

python3 tests/smoke/generate_panel.py
Rscript tests/smoke/verify_panel.R tests/smoke/panel-contract.yaml
if Rscript tests/smoke/verify_panel.R tests/smoke/invalid-contract.yaml; then
  echo "invalid contract unexpectedly passed" >&2
  exit 1
fi
test -f tests/smoke/output/smoke_table.md
