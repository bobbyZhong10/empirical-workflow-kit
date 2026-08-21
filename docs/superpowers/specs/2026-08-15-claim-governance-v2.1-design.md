# Claim Governance Layer v2.1 Design

## Governing principle

The system only makes state worse. People make state better, and every
improvement has an author, timestamp, and supporting evidence.

This design adds claim governance, acceptance gates, semantic provenance, and
conditional-artifact tracking. It does not change stage boundaries, checkpoint
placement, or mandatory-pause triggers.

## Claims, evidence, and reported figures

A claim is one assertion that can fail independently of another assertion.
Claim identity is stable; revisions are independent of pipelines.

```yaml
claim_key: H1_effect_sign
claim_revision_id: H1_effect_sign.r4
pipeline_id: p03
supersedes: H1_effect_sign.r3
revision_reason: bounded_by_sensitivity
statement: "The effect is positive for direction A only."
```

Each claim revision has two axes:

- `availability`: authorized values `current | superseded | retired |
  withdrawn`; derived-only value `stale`.
- `assessment`: `supported | challenged | unresolved`.

`unresolved` is the initial state for a claim without live supporting evidence,
and is restored when every supporting evidence relation is withdrawn. Stale
availability never changes assessment.
`stale` cannot be set or cleared manually.

Evidence cards remain execution artifacts. They record
`provenance: confirmatory | exploratory` and `status: current | stale |
withdrawn`. Only a current, non-derived-stale confirmatory card may support a
claim. Evidence relations are separate records with
`supports | challenges | bounds`, author, date, and rationale.

Reported figures are non-claim numerical values. They record `pipeline_id`,
source artifact, source locator, paper locations, `derived_from`, and
`transform`. They have no evidence state machine.

## Pipeline and output invariants

1. Every claim revision has bindings from one pipeline only.
2. A paper output may contain claim revisions and reported figures from one
   pipeline only. A declared reconciliation block is the sole exception:
   `cross_pipeline: reconciliation` plus its spanned pipeline list is required.
3. Superseding a pipeline derives `stale` for every bound claim revision,
   reported figure, and output artifact until valid revalidation occurs.

A reconciliation block is an exception to output pipeline uniformity only. It
may quote a stale revision as a historical result, but never restores its
availability or permits it as a current claim.

Pipeline-replacement stale may be cleared by revalidation. Semantic-correction
stale may not be cleared by machine comparison.

```yaml
pipeline:
  pipeline_id: p03
  first_formal_batch_at: 2026-04-17T00:00:00Z

revalidation:
  target: {kind: claim_revision | reported_figure, id: ...}
  from_pipeline: p03
  to_pipeline: p04
  method: machine | manual
  tolerance: "abs(delta) <= 0.01 and sign unchanged"   # required when method: machine
  result: revalidated | changed | not_revalidated
  performed_by: ...
  performed_at: ...
  evidence_card: ...
```

Machine tolerance is a closed grammar: `abs(delta) <= NUMBER`, optionally
followed by exactly `and sign unchanged`. Unsupported or trailing clauses are
invalid rather than silently ignored.

For `kind: reported_figure`, machine revalidation is the default path:
re-resolve `source_artifact` + `source_locator` under the new pipeline, compare
the value against `tolerance`, and on success update `value` and `pipeline_id`
in place with the revalidation record attached. A reported figure carrying
`derived_from` and `transform` has its displayed value recomputed by the
validator, not by a human, whenever its upstream figure changes. A stale
display value whose upstream was revalidated is a validator bug, not an author
error.

## Publication rule

A submission export accepts `current + supported` claims. It accepts
`current + challenged` claims only when every challenge has a disclosed,
adjacent paper location. A site-level disclosure names the stable
`challenge_ids` it covers; one generic qualification cannot satisfy multiple
challenge identities. It rejects stale, superseded, retired, withdrawn, and
unresolved claims, and any mixed-pipeline output outside a declared
reconciliation block.

The Stage 7 claim-to-evidence audit is a registry export, not an independently
maintained document.

## Acceptance gates

Gate definitions are frozen, pre-result commitments. A definition has an
independent identifier and may apply to multiple datasets, stages, or claims.

```yaml
gate_definition:
  gate_id: G-004
  applies_to:
    - {kind: dataset, id: analysis_panel}
    - {kind: claim_key, id: H1_effect_sign}
  metric: negative_margin_share_per_cell
  allowed_band: "[0, 0.01]"
  failure_policy: STOP
  declared_at: 2026-04-17T00:00:00Z
  declared_by: decision_authority
  frozen: true
  compensation:
    action: "Reconfigure construction and document the sensitivity."
    required_artifact: evidence/gates/G-004.md
```

Definitions may target `dataset | pipeline_stage | claim_key`. Checkpoint B
requires an authority-signed statement that the gate set is complete at that
time. Each pipeline records `first_formal_batch_at`. A gate definition may be a
pre-commitment for one pipeline and a post-hoc addition for another; the
derived `post_hoc` property belongs to each evaluation, not the definition.

Each pipeline has a separate evaluation:

```yaml
gate_evaluation:
  gate_id: G-004
  pipeline_id: p03
  post_hoc: derived # true when gate_definition.declared_at is later than this pipeline's first_formal_batch_at
  evaluated_against: {kind: dataset, id: analysis_panel@p03}
  status: passed
  coverage:
    declared_scope: "all platform-direction-period cells"
    evaluated_scope: "all platform-direction-period cells"
    complete: true
  evidence_card: evidence/estimates/p03-quality.md
```

Allowed statuses are `passed | triggered | satisfied | released | moot |
not_evaluated | inapplicable`. Incomplete coverage is treated as
`not_evaluated`. `satisfied` requires both the compensation artifact and
`accepted_by` plus `accepted_at`. `released` requires the triggering change
record, reason, authorization, pre/post-result marker, evidence, and any
remaining compensation disposition. The triggering change may concern a claim,
dataset, or pipeline stage. `moot` is derived only when an object to which the
gate applies enters `retired` or `withdrawn` (claims), or a documented
equivalent end-of-life state (datasets, pipeline stages), and records the
triggering change id. `inapplicable` requires `applicability_reason`,
`declared_by`, and `accepted_by`.

Checkpoint C blocks unresolved `triggered`, `not_evaluated`, incomplete, or
unaccepted `satisfied` evaluations, and any incomplete `released` record.
Checkpoint C reports post-hoc evaluations, inapplicable evaluations, and
complete released gates.

## Data semantics and applicability

Data contracts describe data shape and identity. Semantic registries describe
meaning. Applicability records are project-governance artifacts, not data.

Semantic facts have stable keys, revisions, provenance, verification, and
valid ranges. Revisions can coexist for non-overlapping date ranges.

```yaml
semantic_fact:
  fact_key: SEM-driver_pay-definition
  fact_revision_id: SEM-driver_pay-definition.r2
  supersedes: SEM-driver_pay-definition.r1
  revision_reason: corrected
  field: driver_pay
  statement: "Base driver compensation excluding tips."
  valid_range: [2024-01-01, null]
  authority: {status: sourced, source: docs/methodology.pdf}
  verification:
    method: additivity_identity
    result: pass
    performed_by: analyst
    performed_at: 2026-08-15T00:00:00Z
```

Verification cards for semantic facts may use raw fields and semantic facts,
but never derived fields. This makes the semantic layer a graph bottom layer.
At every point in the analysis window, every used field must have exactly one
valid semantic revision (so revisions may not overlap). Coverage gaps or
overlaps block analysis. When two or more non-overlapping revisions are
required to cover the window — i.e. the field's meaning changes mid-window —
the system creates a mandatory disclosure item and challenges dependent claims
unless an authored semantic-equivalence decision declares the definitions
interchangeable for the analysis.

Derived fields reference fact keys, not bare field names. They have
`verified | unverified | defective` status and known defects. A defective
derived field may be used, but automatically challenges dependent claims; it
cannot silently support them.

An applicability record uses `completed | pending | blocked | inapplicable`.
Inapplicability requires a reason, declarer, accepter, and `substituted_by`
requirement references. Every substitute must itself be completed. Design-grid
records include dimensions and empty cells; sibling-parity records include
dimension-level match/diverge results and consequence assessment.

## Cascade evaluation

Before evaluating cascades, validate that semantic verification cards depend
only on raw fields and semantic facts. The reference graph is then acyclic by
construction.

Cascade operations are monotone: they only add derived reasons or worsen
availability/assessment. They never clear state. Every improvement, including
revalidation or challenge resolution, is an authored action with timestamp and
evidence.

The engine is a single topological traversal, not an iterative fixed-point
algorithm. It records reasons in this deterministic order for reproducible
logs:

1. Resolve semantic-revision coverage for the analysis window.
2. For corrected semantic facts, propagate stale through derived fields,
   evidence cards, and claim revisions.
3. For superseded pipelines, propagate stale to claim revisions, reported
   figures, and output artifacts.
4. For defective derived fields or required semantic-change disclosures, add
   challenged assessment reasons to dependent claims unless they are already
   stale.
5. For any object to which a gate applies that has entered `retired` or
   `withdrawn` (claims), or a documented equivalent end-of-life state
   (datasets, pipeline stages), derive `moot` for the linked gate evaluations
   and record the triggering change id.
6. Recompute assessment from the set of live supporting relations, where
   "live" means not withdrawn. Stale relations remain live for this purpose.
   Then recompute publication eligibility from availability, assessment,
   disclosure, gate, and output-pipeline invariants.

Semantic or pipeline stale reasons remain distinguishable. Only pipeline stale
may use machine revalidation; semantic-correction stale requires a human,
evidence-backed reassessment.

## Validator-first implementation requirement

The first v2.1 implementation deliverable is `validate_registry`. It reads all
registries and produces machine-readable Checkpoint B/C blocking reports. It
must validate required fields, semantic coverage, semantic bottom-layer
dependencies, graph acyclicity, pipeline and output invariants, gate timing,
gate coverage and closure, cascade results, and publication eligibility.

Its smoke fixtures must cover: pipeline supersession deriving stale and
rejecting export; machine revalidation restoring availability without changing
assessment; semantic correction requiring human reassessment; multi-revision
semantic-window disclosure; incomplete release blocking Checkpoint C;
cross-runtime handoff recovery; and a failed identification diagnostic.
They must also cover: a gate declared after the first formal batch of one
pipeline and before that of another, asserting `post_hoc: true` for the first
evaluation and `false` for the second; an output artifact mixing two pipelines,
asserting rejection under invariant 2; a declared reconciliation block spanning
two pipelines that quotes a stale revision as a historical result, asserting
acceptance and that the quoted revision's availability remains `stale`; and an
`inapplicable` applicability record whose `substituted_by` target is not
`completed`, asserting rejection.
