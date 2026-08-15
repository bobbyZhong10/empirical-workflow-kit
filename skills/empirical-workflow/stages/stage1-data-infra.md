# Stage 1: Dataset Infrastructure

## Inputs

- `RESEARCH_PROTOCOL.md`, active `research.yaml` (or `research.example.yaml`),
  `_status.md`, the current Evidence card, and the tail of `decision-log.md`.
- Read-only raw sources, their provenance and license terms, and the approved
  observation unit and data-format conventions.

## Automatic actions

- Inventory every source and version; record owner, access method, coverage,
  license, refresh behavior, checksum or version identifier, and raw path.
- Profile the claimed observation key and panel structure: unit count, period
  count, balancedness, observations per unit, duplicates, calendar gaps, and
  coverage breaks.
- Validate every merge in both directions and characterize unmatched records.
  Tabulate unit entry and exit by period and investigate material changes.
- Preserve raw inputs, write reproducible numbered build scripts, and create
  Evidence cards for material source and quality findings.

## Required artifacts

- `docs/data_inventory.md`: source/version inventory, provenance, coverage,
  caveats, and reproducible raw-to-derived lineage.
- `docs/panel_dimensions.md`: observation unit, unit and period counts,
  balance, duplicate-key evidence, calendar coverage, and structural breaks.
- `docs/key_integrity_and_merge_rates.md`: key tests, merge-rate evidence in
  both directions, unmatched-record characterization, and remediation.
- `docs/entry_exit_report.md`: entry/exit tables or figures, coverage changes,
  and implications for the usable panel.
- Numbered build scripts, a derived-data manifest, relevant Evidence cards, and
  an updated `_status.md`.

## Red lines

- Never overwrite raw data, silently deduplicate keys, or discard unmatched
  records without recording the rate, reason, and effect on the sample.
- Do not call the panel usable when key integrity, source versioning, or merge
  quality is unverified.
- Pause for a recorded decision if source changes alter the observation unit,
  coverage, proposed sample, or feasible identifying design.

## Exit condition

The source/version inventory, panel dimensions, key-integrity evidence,
merge-rate evidence, and entry-exit report all exist and are reproducible.
Known limitations are documented, the intended data can support the next-stage
question, and `_status.md` records validation, risks, and Stage 2 as the next
action.
