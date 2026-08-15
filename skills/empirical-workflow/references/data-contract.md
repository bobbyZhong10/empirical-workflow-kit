# Python-to-R Data Contract

Python ETL exports each analysis-ready dataset as a Parquet file and a YAML
contract. R must validate the YAML record and the Parquet data before beginning
formal analysis. The contract belongs beside the exported dataset, for example:

```
data/analysis/firm_quarter.parquet
data/analysis/firm_quarter.contract.yaml
data/analysis/audits/firm_quarter_v2026_08_15.merge-audit.yaml
```

The YAML template is
`skills/empirical-workflow/templates/data-contract-template.yaml`. Copy it for
each export; do not overwrite a contract for an earlier data version.

## Required fields

Every contract must contain the following populated fields.

| Field | Requirement |
| --- | --- |
| `data_version` | Immutable version label for this export. |
| `source_versions` | One entry per upstream source, with a source name and version or retrieval date. |
| `data_hash` | Hash of the exported Parquet file, naming the hash algorithm. |
| `producing_script` | Repository-relative numbered Python script that created the export. |
| `produced_at_utc` | UTC timestamp at which the export was produced. |
| `dataset_path` | Repository-relative Parquet path. |
| `observation_unit` | Plain-language unit represented by one row. |
| `time_granularity` | Time interval represented by a row. |
| `primary_key.columns` | Ordered key columns. |
| `primary_key.is_unique` | Result of checking key uniqueness in the exported data. |
| `primary_key.duplicate_row_count` | Number of rows in duplicate key groups. It must be zero. |
| `row_count`, `unit_count`, `period_count` | Exported row count and panel counts, with the unit and period fields named. |
| `required_fields` | Columns that must be present and nonmissing for R analysis. |
| `field_types` | Expected type for every exported analysis field. |
| `missingness` | Missing count and share for every exported analysis field. |
| `value_ranges` | Permitted lower and upper values (or an explicit categorical rule) for bounded fields. |
| `merge_audit` | Versioned merge-audit path, hash, and data version. |
| `merge_rates` | Summary of merge rates copied from the audit for quick inspection. |

`data_hash`, `row_count`, and field statistics describe the actual Parquet
export, not an intermediate object. Counts use integer values; shares are
decimal fractions from 0 through 1.

## Versioned merge-audit artifact

Python creates and retains one immutable merge audit for every data version at
`data/analysis/audits/<data_version>.merge-audit.yaml`. The contract's
`merge_audit.path`, `merge_audit.data_version`, and `merge_audit.data_hash`
identify that file. The audit is produced by the numbered Python export script
with the Parquet and contract; it is never reconstructed or edited by R.

The audit must contain its `data_version`, `producing_script`,
`produced_at_utc`, and an `output_dataset` record with the final Parquet path
and row count. Each `merge_steps` entry must identify the merge and state its
join type, left and right source names and versions, left and right input row
counts, matched-left and unmatched-left row counts, left match rate, output row
count, and disposition of unmatched rows. The Python producer must assert:

1. `matched_left_row_count + unmatched_left_row_count = left_input_row_count`.
2. `left_match_rate = matched_left_row_count / left_input_row_count` when the
   left input is nonempty.
3. The audit's `output_dataset.path` and `output_dataset.row_count` equal the
   contract's `dataset_path` and `row_count`.

The standalone audit template is
`skills/empirical-workflow/templates/merge-audit-template.yaml`. Retaining the
source totals and match outcomes makes every merge auditable even though the
final Parquet cannot reproduce the raw matching inputs.

## R validation gate

Before `code/r/01_construct.R` reads or constructs analysis variables, it must:

1. Read the YAML contract and the referenced Parquet file.
2. Confirm the data version, hash, dataset path, observation unit, and time
   granularity against the planned analysis input.
3. Confirm that every required field is present; validate declared field types.
4. Recompute the ordered primary-key uniqueness check, row count, unit count,
   period count, missingness, and value ranges from the Parquet file.
5. Read the versioned merge audit and validate its hash, data version, source
   totals, matched/unmatched identities, match-rate arithmetic, and identity
   of its documented output path and row count with the contract. Do not try
   to reconstruct raw matching from final Parquet rows.
6. Abort with a descriptive error on any failed key, count, required-field,
   hash, type, missingness, range, or merge-rate check. A visual inspection or
   manual override is not a substitute for a passing validation.

Record the validation command, contract and merge-audit paths, data version,
assertions, and result in `docs/data_contract_validation.md`. If source data
must change, produce a new Parquet export, contract, and merge audit, then
rerun the validation gate.

## Change discipline

The producer updates Parquet, contract, and merge audit in the same export
step. The R consumer does not edit any of these artifacts. A changed schema,
key, observation unit, time granularity, required analysis field, or merge
logic is a data-contract change and must be recorded before R analysis resumes.
