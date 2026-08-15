#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
exec "$repo_root/.venv/bin/python" -m pytest \
  "$repo_root/tests/test_workflow_contract.py" -q
