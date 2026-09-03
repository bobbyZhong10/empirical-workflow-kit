# R Coding Standards

R is the default language for the empirical pipeline from ingestion through
figures and tables. The reasons are practical: transformations and estimation
results remain inspectable objects, so the workflow can verify its own output
rather than parse logs or coordinate two language environments by default.

## Project layout

```
code/
├── 00_setup.R        packages, paths, options, seed
├── 01_ingest.R       read-only ingestion and source assertions
├── 02_clean_merge.R  cleaning, entity resolution, joins, and merge audit
├── 03_entities.R     optional unit construction or crosswalks
├── 04_export.R       Parquet, data contract, and immutable merge audit
├── 05_validate_contract.R  independently validates the analysis-data boundary
├── 06_construct.R    analysis-variable construction; the attrition log lives here
├── 07_descriptives.R
├── 08_main.R         baseline and specification ladder
├── 09_diagnostics.R  design-specific evidence for identification
├── 10_robustness.R
├── 11_mechanism_het.R
└── 12_tables.R       export only, no estimation
```

R owns raw ingestion, cleaning, entity resolution, merging, construction, and
analysis by default. It exports the analysis-ready Parquet data, YAML contract,
and merge audit, then validates those artifacts independently before formal
analysis. Multiple scripts, never one file. Each script runs standalone after
`00_setup.R`. No script writes to `data/raw/`.

When a recorded Python exception produces the analysis-ready export, preserve
the same contract boundary and begin the R portion at `05_validate_contract.R`.
The exception changes the producer, not the validation, provenance, or delivery
requirements.

## Analysis-data contract gate

The Stage 1 producer supplies the analysis input as a Parquet file and a
versioned YAML contract beside it. The exact schema and required fields are defined in
`data-contract.md` and its `data-contract-template.yaml`.

`05_validate_contract.R` must run before `06_construct.R` reads or constructs
analysis variables. It loads the YAML contract, Parquet input, and versioned
merge-audit artifact, then aborts on any failed key, count, or required-field
check. It independently loads `research.yaml` and compares the contract's
project name and observation unit with the project values, then compares data
version, dataset path, producing script, time granularity, and ordered primary
key with the locked `analysis_input_contract`. It also verifies the recorded
file hash, declared types, missingness, and value ranges, and recomputes the
primary-key uniqueness result and the row, unit, and period counts from the
Parquet file; do not trust a stale YAML value.

R does not attempt to reconstruct raw matching from the final Parquet file.
Instead, it validates the merge-audit artifact's source totals, matched and
unmatched counts, match-rate arithmetic, and identity with the contract's
documented output path and row count.

The validation is a hard gate: no formal analysis, descriptives, or estimation
may proceed after a failed check. Stop with a descriptive error, correct or
replace the Python export, create a new data version and contract if needed,
and rerun validation. Record the contract and merge-audit paths, data version,
assertions, and result in `docs/data_contract_validation.md`.

## Packages

- `fixest` for ordinary least squares, high dimensional fixed effects, IV, event
  study, and DDD. `feols` and `fepois`.
- `rdrobust` for regression discontinuity.
- `did`, `didimputation`, or `staggered` for staggered adoption.
- `HonestDiD` for pre trend sensitivity.
- `modelsummary` and `etable` for tables.
- `data.table` or `dplyr` for data work, chosen once per project.
- `here` for paths. No absolute paths anywhere.

## Results

Every estimation script writes to `results/` and writes a markdown summary
beside its output: what was estimated, on what sample, what the numbers are, and
what was decided. A table with no accompanying summary is not reusable a month
later.

```
results/
├── tables/
├── figures/
└── logs/2026-08-12_main.md
```

## Verification helpers

Put assertions in the construction and estimation scripts rather than checking
by eye. Suggested pattern in `00_setup.R`:

```r
check_unique <- function(dt, keys) {
  stopifnot(!anyDuplicated(dt, by = keys))
  invisible(TRUE)
}

check_n <- function(dt, expected_n, label) {
  if (nrow(dt) != expected_n) {
    stop(sprintf("%s: expected %d rows, found %d", label, expected_n, nrow(dt)))
  }
  invisible(TRUE)
}

check_model <- function(m, min_obs, expected_fe, cluster_var) {
  stopifnot(m$nobs >= min_obs)
  stopifnot(all(expected_fe %in% names(m$fixef_sizes)))
  message(sprintf("N = %d, clusters = %s", m$nobs, cluster_var))
  invisible(TRUE)
}
```

After every estimation batch, confirm programmatically that the sample size is
constant across columns that should share a sample, that the clustering level is
the intended one, and that the treatment variable was not absorbed by the fixed
effects.

## Reproducibility

Set a seed in `00_setup.R`. Record `sessionInfo()` into `results/logs/`. Freeze
package versions with `renv` for any project that will be submitted.

## Tables for submission

Three line tables. Times New Roman 12 point, double spacing in the manuscript.
Standard errors in parentheses below coefficients. Every table note states the
sample, the fixed effects, the clustering level, and the number of clusters.
