# Python Coding Standards

Python owns ingestion, cleaning, entity resolution, cross-source merging, and
the export of analysis-ready data to R. Its purpose is transparent research
data work, not a reusable software product.

## Script layout

Use direct, numbered, linear scripts in `code/py/`, for example:

```
code/py/
├── 01_ingest.py
├── 02_clean.py
├── 03_merge.py
└── 04_export.py
```

Each script has one plainly stated purpose and can be run in sequence without
a package, class hierarchy, or deep abstraction layer. Small local functions
are appropriate for repeated checks or transformations, but do not hide the
research logic behind frameworks, generic pipelines, or clever indirection.
Keep paths repository-relative and parameters visible near the top of the
script. Do not write raw data: treat `data/raw/` as read-only and write cleaned
or derived outputs under `data/intermediate/` or `data/analysis/`.

## Exports and the R boundary

`04_export.py` writes analysis data as Parquet, writes its versioned YAML
contract beside it, and retains a versioned merge audit at
`data/analysis/audits/<data_version>.merge-audit.yaml`. The contract must follow
`references/data-contract.md` and start from
`templates/data-contract-template.yaml`. It reports facts computed from the
final Parquet export: project identity, data and source versions, file hash,
producing script, observation unit, time granularity, ordered primary key and
uniqueness result, row/panel counts, field types, missingness, value ranges, and
merge-audit reference. The audit records each merge's source versions and totals,
matched/unmatched counts, match rate, output count, and unmatched disposition.
Assert the audit arithmetic and its final output path and count against the
contract before writing the artifacts.

Export only stable, analysis-ready column names. Include the primary-key
columns, all required analysis fields, and a variable dictionary that defines
each field's source, transformation, unit, and time availability. Do not
silently replace a prior export: create a new data version and matching YAML
contract and merge audit.

Before export, read the active `research.yaml` and require a populated
`analysis_input_contract`. Assert that project name and observation unit match
the top-level project values and that data version, path, producing script,
time granularity, and ordered primary key match the locked analysis-input
identities. Do not let the export silently redefine those expected values.

## Checks and comments

Assert source schemas, key uniqueness, expected coverage, merge rates, and
value bounds in the script that creates or changes them. Fail loudly before an
invalid dataset reaches `data/analysis/`. Record row changes and merge losses
in the contract or linked attrition record.

Write concise English comments only where a research or technical decision is
not obvious from the code. Explain why a non-obvious match rule, exclusion, or
transformation is used; do not narrate routine syntax. Use meaningful concise
names such as `firm_id`, `year_qtr`, `ai_adopt`, and `sales_ln`.
