#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

bootstrap_error() {
  echo "ERROR: repository-local bootstrap failed: $1" >&2
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

if ! command -v python3 >/dev/null 2>&1; then
  bootstrap_error "Python 3 is required to create .venv"
fi
if ! command -v Rscript >/dev/null 2>&1; then
  bootstrap_error "Rscript is required to install the repository-local R packages"
fi

python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-dev.txt
tools/validate_registry --version >/dev/null

mkdir -p .r-lib
install_output=$(mktemp)
if R_LIBS="$repo_root/.r-lib" Rscript --vanilla - "$repo_root/.r-lib" >"$install_output" 2>&1 <<'RS'
library_path <- commandArgs(trailingOnly = TRUE)[[1]]
required_packages <- c("arrow", "yaml", "fixest", "modelsummary")
install.packages(
  required_packages,
  lib = library_path,
  repos = "https://cloud.r-project.org"
)
RS
then
  rm -f "$install_output"
else
  install_status=$?
  print_diagnostic_excerpt "$install_output" "R package installation"
  rm -f "$install_output"
  bootstrap_error "R package installation $(process_status_message "$install_status")"
fi

verify_r_package() {
  local package=$1
  local package_output
  package_output=$(mktemp)

  # Loading one package per process keeps a broken native extension from
  # crashing the bootstrap before the failing package can be identified.
  if R_LIBS="$repo_root/.r-lib" Rscript --vanilla -e '
    args <- commandArgs(trailingOnly = TRUE)
    library_path <- args[[1]]
    package <- args[[2]]
    package_path <- find.package(package, lib.loc = library_path, quiet = TRUE)
    if (length(package_path) == 0) quit(status = 2)
    if (!requireNamespace(package, quietly = TRUE, lib.loc = library_path)) quit(status = 1)
  ' "$repo_root/.r-lib" "$package" >"$package_output" 2>&1; then
    rm -f "$package_output"
  else
    local package_status=$?
    print_diagnostic_excerpt "$package_output" "R package '$package' verification"
    rm -f "$package_output"
    bootstrap_error "R package '$package' is not installed and loadable in .r-lib ($(process_status_message "$package_status"))"
  fi
}

for r_package in arrow yaml fixest modelsummary; do
  verify_r_package "$r_package"
done

echo "Repository-local smoke-test environment is ready."
