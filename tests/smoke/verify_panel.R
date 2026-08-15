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

contract_assert <- function(condition) {
  if (!isTRUE(condition)) fail_contract()
}

is_nonempty_string <- function(value) {
  is.character(value) && length(value) == 1 && !is.na(value) && nzchar(value)
}

is_count <- function(value) {
  is.numeric(value) && length(value) == 1 && !is.na(value) && is.finite(value) && value >= 0 && value == floor(value)
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
  contract <- tryCatch(yaml::read_yaml(contract_path), error = function(error) fail_contract())
  required_contract_fields <- c(
    "data_version", "produced_at_utc", "producing_script", "dataset_path", "data_hash",
    "source_versions", "observation_unit", "time_granularity", "primary_key", "row_count",
    "unit_count", "period_count", "required_fields", "field_types", "missingness",
    "value_ranges", "merge_audit", "merge_rates"
  )
  contract_assert(is.list(contract) && all(required_contract_fields %in% names(contract)))
  contract_assert(is_nonempty_string(contract$data_version) && is_nonempty_string(contract$produced_at_utc) &&
    is_nonempty_string(contract$producing_script) && is_nonempty_string(contract$dataset_path) &&
    length(contract$source_versions) > 0 && is_nonempty_string(contract$observation_unit) &&
    is_nonempty_string(contract$time_granularity) && is_count(contract$row_count))
  contract_assert(is.list(contract$data_hash) && identical(contract$data_hash$algorithm, "sha256") && is_nonempty_string(contract$data_hash$value))
  contract_assert(is.list(contract$merge_audit) && is_nonempty_string(contract$merge_audit$path) &&
    identical(contract$merge_audit$data_version, contract$data_version) &&
    is.list(contract$merge_audit$data_hash) && identical(contract$merge_audit$data_hash$algorithm, "sha256") &&
    is_nonempty_string(contract$merge_audit$data_hash$value))

  panel_path <- resolve_path(contract$dataset_path)
  contract_assert(file.exists(panel_path) && sha256(panel_path) == contract$data_hash$value)
  panel <- as.data.frame(arrow::read_parquet(panel_path))

  contract_assert(is.character(contract$required_fields) && length(contract$required_fields) > 0 &&
    all(contract$required_fields %in% names(panel)))
  required_fields <- unlist(contract$required_fields, use.names = FALSE)
  contract_assert(!any(vapply(panel[required_fields], anyNA, logical(1))))
  contract_assert(is.list(contract$field_types) && all(required_fields %in% names(contract$field_types)) &&
    all(vapply(contract$field_types, is_nonempty_string, logical(1))) && all(names(contract$field_types) %in% names(panel)) &&
    all(vapply(names(contract$field_types), function(field) matches_contract_type(panel[[field]], contract$field_types[[field]]), logical(1))))

  contract_assert(is.list(contract$primary_key) && is.character(contract$primary_key$columns) &&
    length(contract$primary_key$columns) > 0 && all(contract$primary_key$columns %in% names(panel)) &&
    is.logical(contract$primary_key$is_unique) && length(contract$primary_key$is_unique) == 1 &&
    is_count(contract$primary_key$duplicate_row_count))
  key_columns <- unlist(contract$primary_key$columns, use.names = FALSE)
  duplicated_count <- sum(duplicated(panel[key_columns]) | duplicated(panel[key_columns], fromLast = TRUE))
  contract_assert(duplicated_count == contract$primary_key$duplicate_row_count &&
    isTRUE(contract$primary_key$is_unique) == (duplicated_count == 0))
  contract_assert(is.list(contract$unit_count) && is_nonempty_string(contract$unit_count$field) &&
    contract$unit_count$field %in% names(panel) && is_count(contract$unit_count$value) &&
    is.list(contract$period_count) && is_nonempty_string(contract$period_count$field) &&
    contract$period_count$field %in% names(panel) && is_count(contract$period_count$value))
  contract_assert(nrow(panel) == contract$row_count && length(unique(panel[[contract$unit_count$field]])) == contract$unit_count$value &&
    length(unique(panel[[contract$period_count$field]])) == contract$period_count$value)

  contract_assert(is.list(contract$missingness) && all(names(contract$missingness) %in% names(panel)))
  for (field in names(contract$missingness)) {
    expected <- contract$missingness[[field]]
    contract_assert(is.list(expected) && is_count(expected$count) && is.numeric(expected$share) &&
      length(expected$share) == 1 && expected$share >= 0 && expected$share <= 1)
    observed_count <- sum(is.na(panel[[field]]))
    observed_share <- observed_count / nrow(panel)
    contract_assert(observed_count == expected$count && isTRUE(all.equal(observed_share, expected$share)))
  }
  contract_assert(is.list(contract$value_ranges) && all(names(contract$value_ranges) %in% names(panel)))
  for (field in names(contract$value_ranges)) {
    rule <- contract$value_ranges[[field]]
    values <- panel[[field]]
    contract_assert(is.list(rule))
    if (!is.null(rule$minimum)) {
      contract_assert(is.numeric(rule$minimum) && length(rule$minimum) == 1 && is.numeric(values) && !any(values < rule$minimum))
    }
    if (!is.null(rule$maximum)) {
      contract_assert(is.numeric(rule$maximum) && length(rule$maximum) == 1 && is.numeric(values) && !any(values > rule$maximum))
    }
    if (!is.null(rule$allowed_pattern)) {
      contract_assert(is_nonempty_string(rule$allowed_pattern) && is.character(values) && !any(!grepl(rule$allowed_pattern, values)))
    }
  }

  audit_path <- resolve_path(contract$merge_audit$path)
  contract_assert(file.exists(audit_path) && sha256(audit_path) == contract$merge_audit$data_hash$value)
  audit <- tryCatch(yaml::read_yaml(audit_path), error = function(error) fail_contract())
  contract_assert(is.list(audit) && identical(audit$data_version, contract$data_version) &&
    is_nonempty_string(audit$producing_script) && is_nonempty_string(audit$produced_at_utc) &&
    is.list(audit$output_dataset) && identical(audit$output_dataset$path, contract$dataset_path) &&
    is_count(audit$output_dataset$row_count) && audit$output_dataset$row_count == contract$row_count &&
    is.list(audit$merge_steps) && length(audit$merge_steps) > 0 && is.list(contract$merge_rates))
  for (step in audit$merge_steps) {
    contract_assert(is.list(step) && is_nonempty_string(step$merge_name) && is_nonempty_string(step$join_type) &&
      is.list(step$left_source) && is_nonempty_string(step$left_source$name) && is_nonempty_string(step$left_source$version) &&
      is_count(step$left_source$input_row_count) && is.list(step$right_source) &&
      is_nonempty_string(step$right_source$name) && is_nonempty_string(step$right_source$version) &&
      is_count(step$right_source$input_row_count) && is_count(step$matched_left_row_count) &&
      is_count(step$unmatched_left_row_count) && is.numeric(step$left_match_rate) && length(step$left_match_rate) == 1 &&
      step$left_match_rate >= 0 && step$left_match_rate <= 1 && is_count(step$output_row_count) &&
      is_nonempty_string(step$unmatched_disposition))
    contract_assert(step$matched_left_row_count + step$unmatched_left_row_count == step$left_source$input_row_count)
    if (step$left_source$input_row_count == 0) {
      contract_assert(step$left_match_rate == 0)
    } else {
      contract_assert(isTRUE(all.equal(step$left_match_rate, step$matched_left_row_count / step$left_source$input_row_count)))
    }
    matching_rate <- Filter(function(rate) is.list(rate) && identical(rate$merge_name, step$merge_name), contract$merge_rates)
    contract_assert(length(matching_rate) == 1)
    rate <- matching_rate[[1]]
    contract_assert(is_count(rate$left_row_count) && is_count(rate$matched_row_count) &&
      is_count(rate$unmatched_left_row_count) && is.numeric(rate$match_rate) && length(rate$match_rate) == 1 &&
      rate$match_rate >= 0 && rate$match_rate <= 1 && is_nonempty_string(rate$unmatched_disposition) &&
      rate$left_row_count == step$left_source$input_row_count && rate$matched_row_count == step$matched_left_row_count &&
      rate$unmatched_left_row_count == step$unmatched_left_row_count && isTRUE(all.equal(rate$match_rate, step$left_match_rate)))
  }
  final_step <- audit$merge_steps[[length(audit$merge_steps)]]
  contract_assert(final_step$output_row_count == audit$output_dataset$row_count &&
    final_step$output_row_count == contract$row_count)
  panel
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
