#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: Python 3 is required to create .venv." >&2
  exit 1
fi
if ! command -v Rscript >/dev/null 2>&1; then
  echo "ERROR: Rscript is required to install the repository-local R packages." >&2
  exit 1
fi

python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-dev.txt

mkdir -p .r-lib
R_LIBS_USER="$repo_root/.r-lib" Rscript --vanilla - "$repo_root/.r-lib" <<'RS'
library_path <- commandArgs(trailingOnly = TRUE)[[1]]
required_packages <- c("arrow", "yaml", "fixest", "modelsummary")
install.packages(
  required_packages,
  lib = library_path,
  repos = "https://cloud.r-project.org"
)
RS

echo "Repository-local smoke-test environment is ready."
