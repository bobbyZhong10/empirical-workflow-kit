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
and is restored when every supporting evidence relation is withdrawn or stale.
`stale` cannot be set or cleared manually.

Evidence cards remain execution artifacts. They record
`provenance: confirmatory | exploratory`. Only confirmatory cards may change a
claim assessment. Evidence relations are separate records with
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
   reported figure, and output artifact until valid revalidation or an explicit
   reconciliation reference exists.

Pipeline-replacement stale may be cleared by revalidation. Semantic-correction
stale may not be cleared by machine comparison.

```yaml
revalidation:
  claim_revision: H1_effect_sign.r4
  from_pipeline: p03
  to_pipeline: p04
  method: machine
  tolerance: "abs(delta) <= 0.01 and sign unchanged"
  result: revalidated
  performed_by: research_author
  performed_at: 2026-08-15T00:00:00Z
  evidence_card: evidence/estimates/p04-main.md
```

## Publication rule

A submission export accepts `current + supported` claims. It accepts
`current + challenged` claims only when every challenge has a disclosed,
adjacent paper location. It rejects stale, superseded, withdrawn, and
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
time. A definition declared after its pipeline's first formal estimation batch
is derived `post_hoc`, may exist, and is reported separately; it is not a
pre-commitment.

Each pipeline has a separate evaluation:

```yaml
gate_evaluation:
  gate_id: G-004
  pipeline_id: p03
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
`accepted_by` plus `accepted_at`. `released` requires the triggering claim
revision, reason, authorization, pre/post-result marker, evidence, and any
remaining compensation disposition. `moot` is derived only from a linked claim
withdrawal and records that withdrawal revision.

Checkpoint C blocks unresolved `triggered`, `not_evaluated`, incomplete, or
unaccepted `satisfied` evaluations. It reports post-hoc and released gates.

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
Every used field must have exactly one semantic revision covering every point
of the analysis window. Coverage gaps or overlaps block analysis.

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
4. For defective derived fields, add challenged assessment reasons to dependent
   claims unless they are already stale.
5. For withdrawn claims, derive moot state for linked gate evaluations.
6. Recompute publication eligibility from availability, assessment, disclosure,
   gate, and output-pipeline invariants.

Semantic or pipeline stale reasons remain distinguishable. Only pipeline stale
may use machine revalidation; semantic-correction stale requires a human,
evidence-backed reassessment.
