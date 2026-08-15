# R Coding Standards

R is the analysis language. The reasons are practical: estimation results come
back as objects that can be checked programmatically, so the workflow can verify
its own output rather than parse a log file.

## Project layout

```
code/
├── 00_setup.R        packages, paths, options, seed
├── 01_ingest.R       raw sources to a single storage format, read only inputs
├── 02_clean.R        cleaning, one section per source
├── 03_construct.R    variable construction, the attrition log lives here
├── 04_descriptives.R
├── 05_main.R         baseline and specification ladder
├── 06_diagnostics.R  design specific evidence for identification
├── 07_robustness.R
├── 08_mechanism_het.R
└── 09_tables.R       export only, no estimation
```

Multiple scripts, never one file. Each script runs standalone after
`00_setup.R`. No script writes to `data/raw/`.

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
