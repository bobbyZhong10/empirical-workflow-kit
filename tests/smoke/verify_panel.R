#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) {
  stop("Usage: Rscript tests/smoke/verify_panel.R CONTRACT_PATH", call. = FALSE)
}

required_packages <- c("arrow", "yaml", "fixest", "modelsummary")
missing_packages <- required_packages[!vapply(required_packages, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing_packages) > 0) {
  stop(sprintf("Required R packages unavailable: %s", paste(missing_packages, collapse = ", ")), call. = FALSE)
}

script_arg <- commandArgs(trailingOnly = FALSE)
script_path <- sub("^--file=", "", script_arg[grepl("^--file=", script_arg)][1])
project_root <- normalizePath(file.path(dirname(script_path), "..", ".."), mustWork = TRUE)

fail_contract <- function() {
  stop("Data contract validation failed", call. = FALSE)
}

resolve_path <- function(path) {
  if (grepl("^(/|[A-Za-z]:[/\\\\])", path)) path else file.path(project_root, path)
}

sha256 <- function(path) {
  if (nzchar(Sys.which("shasum"))) {
    return(strsplit(system2("shasum", c("-a", "256", path), stdout = TRUE), "[[:space:]]+")[[1]][1])
  }
  if (nzchar(Sys.which("sha256sum"))) {
    return(strsplit(system2("sha256sum", path, stdout = TRUE), "[[:space:]]+")[[1]][1])
  }
  stop("No SHA-256 command is available", call. = FALSE)
}

matches_contract_type <- function(value, expected) {
  switch(
    expected,
    string = is.character(value),
    integer = is.integer(value),
    float = is.numeric(value),
    FALSE
  )
}

validate_contract <- function(contract_path) {
  tryCatch({
    contract <- yaml::read_yaml(contract_path)
    required_contract_fields <- c(
      "data_version", "produced_at_utc", "producing_script", "dataset_path", "data_hash",
      "source_versions", "observation_unit", "time_granularity", "primary_key", "row_count",
      "unit_count", "period_count", "required_fields", "field_types", "missingness",
      "value_ranges", "merge_audit", "merge_rates"
    )
    if (!all(required_contract_fields %in% names(contract))) fail_contract()
    if (!is.character(contract$data_version) || !nzchar(contract$data_version) ||
        !is.character(contract$produced_at_utc) || !nzchar(contract$produced_at_utc) ||
        !is.character(contract$producing_script) || !nzchar(contract$producing_script) ||
        length(contract$source_versions) == 0 || !is.character(contract$observation_unit) ||
        !nzchar(contract$observation_unit) || !is.character(contract$time_granularity) ||
        !nzchar(contract$time_granularity)) fail_contract()
    if (contract$data_hash$algorithm != "sha256" || contract$merge_audit$data_hash$algorithm != "sha256") fail_contract()

    panel_path <- resolve_path(contract$dataset_path)
    if (!file.exists(panel_path) || sha256(panel_path) != contract$data_hash$value) fail_contract()
    panel <- as.data.frame(arrow::read_parquet(panel_path))

    required_fields <- unlist(contract$required_fields, use.names = FALSE)
    if (!all(required_fields %in% names(panel)) || any(vapply(panel[required_fields], anyNA, logical(1)))) fail_contract()
    if (!all(vapply(names(contract$field_types), function(field) field %in% names(panel) && matches_contract_type(panel[[field]], contract$field_types[[field]]), logical(1)))) fail_contract()

    key_columns <- unlist(contract$primary_key$columns, use.names = FALSE)
    duplicated_count <- sum(duplicated(panel[key_columns]) | duplicated(panel[key_columns], fromLast = TRUE))
    if (!all(key_columns %in% names(panel)) || duplicated_count != contract$primary_key$duplicate_row_count ||
        isTRUE(contract$primary_key$is_unique) != (duplicated_count == 0)) fail_contract()
    if (nrow(panel) != contract$row_count || length(unique(panel[[contract$unit_count$field]])) != contract$unit_count$value ||
        length(unique(panel[[contract$period_count$field]])) != contract$period_count$value) fail_contract()

    for (field in names(contract$missingness)) {
      observed_count <- sum(is.na(panel[[field]]))
      observed_share <- observed_count / nrow(panel)
      expected <- contract$missingness[[field]]
      if (observed_count != expected$count || !isTRUE(all.equal(observed_share, expected$share))) fail_contract()
    }
    for (field in names(contract$value_ranges)) {
      rule <- contract$value_ranges[[field]]
      values <- panel[[field]]
      if (!is.null(rule$minimum) && any(values < rule$minimum)) fail_contract()
      if (!is.null(rule$maximum) && any(values > rule$maximum)) fail_contract()
      if (!is.null(rule$allowed_pattern) && any(!grepl(rule$allowed_pattern, values))) fail_contract()
    }

    audit_path <- resolve_path(contract$merge_audit$path)
    if (!file.exists(audit_path) || sha256(audit_path) != contract$merge_audit$data_hash$value) fail_contract()
    audit <- yaml::read_yaml(audit_path)
    if (audit$data_version != contract$data_version || contract$merge_audit$data_version != contract$data_version ||
        !is.character(audit$producing_script) || !nzchar(audit$producing_script) ||
        !is.character(audit$produced_at_utc) || !nzchar(audit$produced_at_utc) ||
        audit$output_dataset$path != contract$dataset_path || audit$output_dataset$row_count != contract$row_count) fail_contract()
    for (step in audit$merge_steps) {
      if (step$matched_left_row_count + step$unmatched_left_row_count != step$left_source$input_row_count ||
          !isTRUE(all.equal(step$left_match_rate, step$matched_left_row_count / step$left_source$input_row_count)) ||
          is.null(step$right_source$name) || is.null(step$right_source$version) ||
          is.null(step$left_source$name) || is.null(step$left_source$version)) fail_contract()
      matching_rate <- Filter(function(rate) identical(rate$merge_name, step$merge_name), contract$merge_rates)
      if (length(matching_rate) != 1) fail_contract()
      rate <- matching_rate[[1]]
      if (rate$left_row_count != step$left_source$input_row_count ||
          rate$matched_row_count != step$matched_left_row_count ||
          rate$unmatched_left_row_count != step$unmatched_left_row_count ||
          !isTRUE(all.equal(rate$match_rate, step$left_match_rate))) fail_contract()
    }
    panel
  }, error = function(error) fail_contract())
}

contract_path <- resolve_path(args[[1]])
panel <- validate_contract(contract_path)

model <- fixest::feols(
  outcome ~ fixest::sunab(cohort, quarter_index, ref.p = -1) | firm_id + year_qtr,
  cluster = ~firm_id,
  data = panel
)
if (model$nobs != nrow(panel) || !all(c("firm_id", "year_qtr") %in% names(model$fixef_sizes))) {
  stop("Model verification failed", call. = FALSE)
}

output_dir <- file.path(project_root, "tests", "smoke", "output")
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
output_path <- file.path(output_dir, "smoke_table.md")
note <- sprintf(
  "Note: Simulated data. N = %d. Fixed effects: firm and quarter. Clustering: firm (%d clusters).",
  model$nobs,
  length(unique(panel$firm_id))
)
table <- modelsummary::modelsummary(model, output = "markdown", notes = note)
writeLines(capture.output(print(table, output = "markdown")), output_path)
