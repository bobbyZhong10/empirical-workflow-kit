# Stage 6a: Reduced-Form Analysis

## Inputs

- Router prerequisites: portable protocol, active configuration, status,
  current Evidence card, and decision-log tail.
- Locked Stage 3 hypothesis-to-estimate map and identification commitments;
  Stage 4 treatment timeline and variable map; Stage 5 measurement record and
  validated data contract.
- The approved reduced-form design, estimation sample, clustering level, and
  current literature/method authorities.

Read `references/identification-decision-tree.md` before choosing an estimator
and `references/robustness-checklists.md` before planning diagnostics. Read
`references/data-contract.md`, `references/r-standards.md`, and
`references/operational-quality-loop.md` before consuming analysis data or
running R validation, construction, diagnostics, or estimation.

## Automatic actions

- Before a formal batch, run a small deterministic smoke case or fixture and
  preserve its validation result. When extending a prior analysis, reproduce
  the known baseline before accepting a new specification.
- Create an identification memo before the first formal estimation batch. It
  records Tree-0 dates (announcement, effective, actual treatment, and
  outcome), anticipation, intensity/repeat/exit rules, interference,
  entry/exit and selection risks, assignment-consistent aggregation, source of
  variation, one-sentence assumption, estimator, comparison group, clustering,
  diagnostics, and backtracking trigger.
- Execute only the locked baseline and pre-committed diagnostic plan. For
  staggered adoption, use a heterogeneity-robust estimator as the main result;
  label TWFE reference-only and run the mandatory negative-weight diagnostic.
- Build a specification ladder: minimal controls, committed controls, fixed
  effects, and locked full specification. Report coefficient, parenthesized
  standard error, N, clusters, fixed effects, dependent-variable mean, units,
  and substantive magnitude for each formal estimate.
- Run design diagnostics in the main paper and record all applicable
  robustness checks in the evidence matrix. Distinguish pre-committed from
  exploratory checks, preserve failures, and apply their stated disposition.
- Test pre-committed mechanisms and heterogeneity. Report interactions rather
  than visually comparing subsample coefficients; label post-result subgroups
  exploratory.
- Run the blindspot audit after the first complete table set and follow any
  backtracking or pause requirement before producing further causal claims.

## Required artifacts

- `docs/identification_memo.md` (or a versioned equivalent) for the selected
  design and the formal-batch identifier.
- A machine-readable estimate record and human-readable markdown summary for
  every formal batch, each linked to code, data-contract version, outputs,
  locked sample rule, and the hypothesis-to-estimate map.
- An **Evidence card** for every formal 6a batch, including the identification
  memo path, estimate record, observation versus inference, conclusion,
  limitation, audit status, and decision-log reference.
- Economics-style three-line tables and figures, the design-specific evidence
  matrix, mechanism/heterogeneity records, blindspot-audit verdict,
  `docs/checkpoints/checkpoint_c.md`, decision-log entries, and updated status.

## Red lines

- Do not redefine treatment from announcement to actual adoption (or reverse),
  change the main specification, sample, clustering, aggregation, or
  identifying strategy without the protocol-required recorded decision.
- Do not treat a failed identifying diagnostic as a robustness result, trade a
  high-severity failure for a collection of passing checks, or conceal omitted
  and failed checks.
- Do not use absorbing-treatment DID when treatment exit occurs, use TWFE as a
  staggered-adoption main result, or claim SUTVA while known spillovers remain
  unaddressed.
- Do not convert exploratory analyses into confirmatory evidence after seeing
  results; label them and retain their output paths.

## Exit condition

Checkpoint C records proceed, revise, or authorized pause. It links each
hypothesis and manuscript claim to a table/column, identification memo,
Evidence card, evidence-matrix disposition, and blindspot verdict. A failed
identification diagnostic returns work to the responsible earlier stage; a
qualified result names the evidence that would change its conclusion.

## 6a operating sequence

1. Lock and archive the identification memo and batch plan before estimation.
2. Validate the analysis data against its contract, run the baseline ladder,
   and write the estimate record and Evidence card immediately.
3. Run diagnostics, then the applicable evidence-matrix rows; pause or
   backtrack on a high-severity design failure.
4. Add pre-committed mechanism and heterogeneity evidence, run the blindspot
   audit, render three-line tables, and complete Checkpoint C.
