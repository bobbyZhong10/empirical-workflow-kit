# Python-to-R Data Contract

Python ETL exports each analysis-ready dataset as a Parquet file and a YAML
contract. R must validate the YAML record and the Parquet data before beginning
formal analysis. The contract belongs beside the exported dataset, for example:

```
data/analysis/firm_quarter.parquet
data/analysis/firm_quarter.contract.yaml
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
| `merge_rates` | One record per merge, including left rows, matched rows, match rate, unmatched rows, and disposition. |

`data_hash`, `row_count`, all field statistics, and merge rates describe the
actual Parquet export, not an intermediate object. Counts use integer values;
shares are decimal fractions from 0 through 1.

## R validation gate

Before `code/r/01_construct.R` reads or constructs analysis variables, it must:

1. Read the YAML contract and the referenced Parquet file.
2. Confirm the data version, hash, dataset path, observation unit, and time
   granularity against the planned analysis input.
3. Confirm that every required field is present; validate declared field types.
4. Recompute the ordered primary-key uniqueness check, row count, unit count,
   period count, missingness, value ranges, and each merge-rate arithmetic
   identity against the recorded contract.
5. Abort with a descriptive error on any failed key, count, required-field,
   hash, type, missingness, range, or merge-rate check. A visual inspection or
   manual override is not a substitute for a passing validation.

Record the validation command, contract path, data version, assertions, and
result in `docs/data_contract_validation.md`. If source data must change,
produce a new Parquet export and a new versioned contract, then rerun the
validation gate.

## Change discipline

The producer updates both Parquet and contract in the same export step. The R
consumer does not edit either artifact. A changed schema, key, observation
unit, time granularity, or required analysis field is a data-contract change
and must be recorded before R analysis resumes.
