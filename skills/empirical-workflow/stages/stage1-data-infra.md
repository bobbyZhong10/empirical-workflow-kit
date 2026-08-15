# Stage 1: Dataset Infrastructure

Goal: know exactly what the data can and cannot support, before any research
question is committed to. Most identification failures are visible at this stage
and are cheap to fix here.

Output: `docs/data_inventory.md`, plus a build script that produces a clean
panel from raw sources.

## 1.1 Inventory

List every source, its provenance, its coverage window, and its access method.
For a database, report the table count and stop. Ask which tables to profile
rather than profiling everything.

Record for each source: owner, license or terms of use, whether it can be
redistributed, and whether the version is frozen. A moving data source that
refreshes under the analysis is a replication failure waiting to happen.

## 1.2 Unit of observation and panel structure

State the unit precisely: firm by quarter, listing by day, user by session.
Then verify it. Check that the claimed key is unique, and report duplicates
rather than silently deduplicating.

Report the panel dimensions: number of units, number of periods, whether the
panel is balanced, and the distribution of the number of observations per unit.

## 1.3 Coverage, entry, and exit

Plot or tabulate units per period. Unit entry and exit is not a nuisance, it is
often the source of the identifying variation or of the bias. Report:

- when units enter and leave, and whether entry and exit correlate with anything
- calendar gaps, including gaps that come from the data provider rather than
  from the world
- any structural break in coverage, for example a change in reporting rules

## 1.4 Key integrity and merge quality

For every merge, report match rates in both directions, and characterize the
unmatched records. A merge that drops 12 percent of observations is a research
design decision, not a technical detail.

## 1.5 Known caveats

Write a caveats section that a referee would read. Include measurement changes,
definitional changes over time, top coding, censoring, and anything the data
provider documents as a limitation. This section is reused verbatim in the data
section of the paper.

## Handoff

`docs/data_inventory.md` contains: sources, unit of observation, panel
dimensions, coverage, merge diagnostics, caveats. Update `_status.md`.
