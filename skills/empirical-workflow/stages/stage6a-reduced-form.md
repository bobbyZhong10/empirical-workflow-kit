# Stage 6a: Reduced-Form and Descriptive Analysis

## Inputs

- Router prerequisites: portable protocol, active configuration, status,
  current Evidence card, and decision-log tail.
- Locked Stage 3 hypothesis-to-estimate map and identification commitments;
  Stage 4 treatment timeline and variable map; Stage 5 measurement record and
  validated data contract.
- The approved reduced-form design, estimation sample, clustering level, and
  current literature/method authorities.

Read `references/research-writing.md` before interpretation, including economic
meaning, contribution, and behavioral explanations for the selected strategy.
Read `references/identification-decision-tree.md` before choosing an estimator
and `references/robustness-checklists.md` before planning diagnostics. Read
`references/data-contract.md`, `references/r-standards.md`, and
`references/operational-quality-loop.md` before consuming analysis data or
running R validation, construction, diagnostics, or estimation.
For non-causal measurement, description, or institutional accounting, state the
observed object, measurement/aggregation assumptions, and limits of interpretation
in the same memo. Do not invent a treatment/control pair, select an irrelevant
causal pack, or run causal diagnostics merely to populate the artifacts below.
Mark those obligations inapplicable with a reason; retain data validation,
reproduction, and claim-to-evidence review.

After a causal design is recorded and confirmed to be in `research.yaml:allowed_designs`, read
`methods/<selected-method>/prompt.md`, then that pack's `canon.md`, `details.md`, and `template.R`
as needed. Load only the selected method pack; do not combine defaults from several packs.

## Automatic actions

- Open and close each module using the router's question-evidence-inference
  contract in its Evidence card. End with the knowledge gain, unresolved
  alternatives, and a reason to continue, demote to background, narrow/delete, or
  stop. At entry, judge whether successful estimation would only reproduce a
  mechanical fact and whether that fact advances the economic question.
- Before a formal batch, run a small deterministic smoke case or fixture and
  preserve its validation result. When extending a prior analysis, reproduce
  the known baseline before accepting a new specification.
- Create an identification memo before the first formal estimation batch. It
  records Tree-0 dates (announcement, effective, actual treatment, and
  outcome), anticipation, intensity/repeat/exit rules, interference,
  entry/exit and selection risks, assignment-consistent aggregation, source of
  variation, one-sentence assumption, estimator, comparison group, clustering,
  diagnostics, and backtracking trigger.
- Record the selected method-pack path, its canon date, the binding canon authority, and any
  justified departure from the pack's default before the first formal batch.
- Execute only the locked baseline and pre-committed diagnostic plan. For
  staggered adoption, use a heterogeneity-robust estimator as the main result;
  label TWFE reference-only and run the mandatory negative-weight diagnostic.
- Build a specification ladder: minimal controls, committed controls, fixed
  effects, and locked full specification. Report coefficient, parenthesized
  standard error, N, clusters, fixed effects, dependent-variable mean, units,
  and substantive magnitude for each formal estimate.
- Review material calculation changes using `references/code-review.md`,
  prioritizing sample, estimand, and inference correctness over style. Apply the
  figure and saved-result rules in `references/r-standards.md` to main exhibits.
- Before interpretation, reconcile the target across the main estimate, main
  figure, dynamics, sensitivity analysis, and magnitude conversion using the
  estimand crosswalk in `references/robustness-checklists.md`.
- Record diagnostic execution and interpretation separately in the evidence
  matrix: assumption/error, decision rule and rationale, effect on the claim,
  and what remains unexcluded, including shared inputs and counterfactuals. Review
  each important claim's observation unit, construct, target, bridge assumptions,
  and strongest warranted sentence. Put reader-essential diagnostics in the paper;
  preserve the complete diagnostic history internally. Distinguish pre-committed from
  exploratory checks, preserve failures, and apply their stated disposition.
- Test pre-committed mechanisms and heterogeneity where the design supports
  them. Distinguish total effects, effect modification, mechanism-consistent
  evidence, and identified mediation; neither a subgroup difference nor an added
  mediator alone establishes a behavioral explanation. Report interactions rather
  than visually comparing subsample coefficients; label post-result subgroups
  exploratory.
- Run the blindspot audit after the first complete table set and follow any
  backtracking or pause requirement before producing further causal claims.
  Adjudicate material audit/reviewer allegations against original results using
  `references/operational-quality-loop.md` before treating them as defects.

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
  `docs/checkpoints/analysis_readiness.md`, decision-log entries, and updated status.

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

The analysis-readiness record authorizes evidence-backed drafting, revision, or
a pause. It links each hypothesis and planned manuscript claim to a
table/column, identification memo, Evidence card, evidence-matrix disposition,
and blindspot verdict. A diagnostic challenging identification pauses the affected causal claim for
review of its rule and implication before any design change. A qualified result
names the evidence that would change its conclusion. Separate computation
success from whether the diagnostic supports the interpretation; neither an
estimate nor a gate verdict is a sufficient knowledge gain. This record is not Checkpoint C and does not authorize
circulation or submission.

## 6a operating sequence

1. Record the economic question, possible mechanical-only success, and
   discriminating result; lock and archive the memo and batch plan before estimation.
2. Validate the analysis data against its contract, run the baseline ladder,
   and write the estimate record and Evidence card immediately.
3. Run diagnostics, then the applicable evidence-matrix rows; pause or
   backtrack on a high-severity design failure.
4. Add pre-committed mechanism and heterogeneity evidence, run the blindspot
   audit, adjudicate material findings, render three-line tables, and close each
   module with continue/background/narrow/delete/stop in the analysis-readiness review.
