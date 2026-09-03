#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT=$(cd "$(dirname "$0")/../.." && pwd)
EWF_PYTHON=${EWF_PYTHON:-"$REPO_ROOT/.venv/bin/python"}

if [[ ! -x "$EWF_PYTHON" ]]; then
  EWF_PYTHON=python3
fi

OUTPUT_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/ewf-presentation-smoke.XXXXXX")
cleanup() {
  rm -rf "$OUTPUT_ROOT"
}
trap cleanup EXIT

for example in research-talk/talk teaching-lecture/lecture; do
  source_file="$REPO_ROOT/examples/$example.qmd"
  output_name=$(basename "$example").html
  "$EWF_PYTHON" "$REPO_ROOT/scripts/ewf.py" --repo "$REPO_ROOT" run quarto \
    render "$source_file" --output-dir "$OUTPUT_ROOT"
  rendered="$OUTPUT_ROOT/$output_name"
  "$EWF_PYTHON" "$REPO_ROOT/scripts/ewf.py" --repo "$REPO_ROOT" run node \
    "$REPO_ROOT/presentation-tooling/deck-check.mjs" fit "$rendered"
  "$EWF_PYTHON" "$REPO_ROOT/scripts/ewf.py" --repo "$REPO_ROOT" run node \
    "$REPO_ROOT/presentation-tooling/stage-check.mjs" "$rendered"
  "$EWF_PYTHON" "$REPO_ROOT/presentation-tooling/check-offline.py" "$rendered"
done

echo "PRESENTATION-SMOKE: PASS"
