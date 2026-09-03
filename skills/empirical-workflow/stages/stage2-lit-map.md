# Stage 2: Literature Map

## Inputs

- The router prerequisites: protocol, active configuration, status, current
  Evidence card, and decision-log tail.
- Stage 1 inventory and caveats, the provisional research question, target
  outlets, and approved reference pools from `research.yaml`.

## Automatic actions

- Route a known DOI, title, link, or named paper through `research-sources`; route a topic-level
  search through `literature-review`; route an existing `.bib` through `bibliography-audit`.
- Search and document four tracks: core theory, empirical phenomenon and
  closest studies, identification and method precedent, and constructs,
  measures, and target-outlet positioning.
- Log searches, retained results, source links, publication metadata, and
  verification checks. Distinguish published papers from working papers, record source coverage,
  and label the exact version and access rung read.
- For each retained citation, label its purpose (theory, construct/measure,
  identification precedent, competing explanation, or outlet positioning).
- Cluster the evidence into research conversations, assess the gap as a
  falsifiable claim, and compare framing against target-outlet expectations.

## Required artifacts

- `docs/lit_map.md`: a four-track literature map, search log, conversation
  table, falsifiable gap statement, construct/measure precedent, and closest
  identification precedents.
- `docs/verified_bibliography.md` (or a versioned bibliography database):
  complete verified metadata and stable source links for every cited work.
- Citation-purpose labels attached to every retained citation.
- `docs/outlet_positioning_memo.md`: candidate outlet, conversation entered,
  contribution claim, closest papers, and likely referee demands.
- Evidence cards for material literature and measurement claims, plus an
  updated `_status.md`.

## Red lines

- Never claim novelty from an unverified or incomplete search, or cite a work
  whose bibliographic record and role have not been checked.
- Never use an abstract-only record to support a claim that requires methods, results, robustness,
  or limitations from the full text.
- Do not flatten distinct conversations into a generic related-work list or
  choose an outlet only because it is aspirational.
- Pause for a recorded decision if the best-supported framing changes the
  research question, construct, outcome, or intended contribution.

## Exit condition

All four tracks are mapped, the bibliography is verified, each retained
citation has a purpose label, and the outlet-positioning memo identifies a
defensible conversation and contribution. The status record names open gaps and
passes the evidence needed for Stage 3.
