# Brief for Codex — v2.1 spec corrections and the v2.2 writing-strength layer

Date: 2026-08-15
Reviewed: `docs/superpowers/specs/2026-08-15-claim-governance-v2.1-design.md` (worktree copy)

All seven previously requested corrections landed correctly. The
semantic-equivalence escape added at the multi-revision disclosure rule was not
requested and is a genuine improvement — keep it.

Six defects remain. Two are substantive (A-1, A-2); the rest are internal
inconsistencies that will produce a wrong implementation if left.

---

# Part A — v2.1 spec corrections

## A-1. `post_hoc` must be a property of the evaluation, not the definition

**Location:** lines 108–112.

**Current text:** "A definition declared after its pipeline's first formal
estimation batch is derived `post_hoc`."

**Problem:** a gate definition can govern more than one pipeline — `applies_to`
is a list, and evaluations are per-pipeline. A gate declared on 2026-06-01 is a
genuine pre-commitment for a pipeline whose first batch runs 2026-07-01, and a
post-hoc addition for a pipeline whose first batch ran 2026-04-01. The same
definition is therefore both. Deriving `post_hoc` on the definition forces one
answer for all pipelines and will mislabel at least one of them.

**Required change:** move `post_hoc` to `gate_evaluation` as a derived boolean:

```
post_hoc: derived — true when gate_definition.declared_at is later than the
          first formal estimation batch timestamp of this evaluation's pipeline_id
```

Each pipeline must therefore record `first_formal_batch_at`. Checkpoint C
reports post-hoc *evaluations*, not post-hoc definitions.

## A-2. Reported figures have no revalidation path

**Location:** lines 52–53 versus 62–73.

**Problem:** invariant 3 derives `stale` for claim revisions, reported figures,
and output artifacts. The `revalidation` object only accepts `claim_revision`.
A paper contains far more reported figures than claims — sample sizes, shares,
means, calibration inputs. After a pipeline supersession every one of them is
stale with no defined way back, so the honest act of declaring a new pipeline
becomes arbitrarily expensive. This is the failure mode the revalidation
mechanism exists to prevent, reintroduced for the more numerous object.

**Required change:** generalise revalidation to a `target` field:

```yaml
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

For `kind: reported_figure`, machine revalidation is the default path: re-resolve
`source_artifact` + `source_locator` under the new pipeline, compare the value
against `tolerance`, and on success update `value` and `pipeline_id` in place
with the revalidation record attached.

**Related:** a reported figure carrying `derived_from` and `transform` must have
its displayed value **recomputed by the validator**, not by a human, whenever its
upstream figure changes. A stale display value whose upstream was revalidated is
a validator bug, not an author error.

## A-3. Cascade step 5 contradicts the gate section on what triggers `moot`

**Location:** line 210 versus lines 135–136.

Line 135 (correct, generalised): "`moot` is derived only from retirement of an
object to which the gate applies."
Line 210 (not updated): "For withdrawn claims, derive moot state for linked gate
evaluations."

**Required change:** rewrite step 5 to match, and state the trigger set
explicitly rather than by the word "retirement", which is ambiguous now that
claims have both `retired` and `withdrawn`:

> 5. For any object to which a gate applies that has entered `retired` or
>    `withdrawn` (claims), or a documented equivalent end-of-life state
>    (datasets, pipeline stages), derive `moot` for the linked gate evaluations
>    and record the triggering change id.

Both `retired` and `withdrawn` must trigger `moot`. Requiring release paperwork
to withdraw a claim judged false would make the honest action more expensive
than shipping it.

## A-4. `unresolved` restoration has no cascade slot

**Location:** lines 32–34 versus the six-step list at 202–212.

The rule "restored when every supporting evidence relation is withdrawn" is
stated in the claim section but no cascade step computes it. Steps 2–5 produce
`stale`, `challenged`, and `moot` only.

**Required change:** state explicitly that assessment is **recomputed in step 6**
from the set of live supporting relations, where "live" means not withdrawn.
Stale relations remain live for this purpose — this is what keeps stale off the
assessment axis, per the correction already applied at line 34.

## A-5. Gate `inapplicable` has no justification fields, while applicability
`inapplicable` does

**Location:** line 129 versus lines 181–183.

An applicability record marked `inapplicable` requires reason, declarer,
accepter, and `substituted_by`. A gate evaluation marked `inapplicable` requires
nothing at all, so it is the cheapest way to make a declared gate disappear.

**Required change:** `gate_evaluation.status: inapplicable` requires
`applicability_reason`, `declared_by`, and `accepted_by`. Checkpoint C reports
inapplicable evaluations alongside post-hoc ones.

## A-6. Smoke fixture list is missing the three invariants most likely to be
implemented wrong

**Location:** lines 226–230.

The current list covers cascade behaviour well. Add:

- a gate declared after the first formal batch of one pipeline and before that
  of another, asserting `post_hoc: true` for the first evaluation and `false`
  for the second (this is the A-1 regression test);
- an output artifact mixing two pipelines, asserting rejection under invariant 2;
- a declared reconciliation block spanning two pipelines that quotes a stale
  revision as a historical result, asserting acceptance **and** asserting that
  the quoted revision's availability remains `stale`;
- an `inapplicable` applicability record whose `substituted_by` target is not
  `completed`, asserting rejection.

## A-7 (clarification only, no behaviour change)

Line 170 reads: "At every point in the analysis window, every used field must
have exactly one valid semantic revision. Coverage gaps or overlaps block
analysis. If more than one revision is valid across the full analysis window…"

The two sentences are consistent but easy to misread as contradictory. Suggest:
"…exactly one valid revision at each point (so revisions may not overlap). When
two or more non-overlapping revisions are required to cover the window — i.e.
the field's meaning changes mid-window — the system creates…"

---

# Part B — v2.2: the writing-strength layer

## Source

`docs/superpowers/specs/2026-08-15-writing-strength-model-v2.md` records findings
from a 14-paper corpus (MISQ / MS / ISR, 2012–2026; DID, staggered DID, RDD,
RDiT, IV, survival, structural, randomised experiments; 278 assertion sentences,
~110 downgrade instances). That document is evidence, not a spec. Part B asks
for the spec.

## What v2.2 governs

The distance between what the registry knows about a claim and how the paper
says it. Two failure directions: asserting more than the evidence licenses, and
asserting less (wasting evidence). The first blocks; the second reports.

## Object model

**Assertion type is prior to tier.** Tiers apply only to `world` assertions.

| type | rule |
|---|---|
| `world` | tiered T0–T4 |
| `negative` | untiered. Requires `power_basis`: the test supporting the exclusion, its sample size, and its minimum detectable effect. Without `power_basis`, wording is capped at hedged form; the phrase "rule out" is prohibited |
| `methodological` | untiered; the assertion's object is an estimator or a method, not the world. Must be typed so it is excluded from empirical-strength statistics |
| `discriminating` | untiered. Must register the specific alternative explanation it excludes. Low lexical strength is normal for this type and must never be read as weak evidence |
| `model_internal` | untiered. Requires an as-modeled marker. The word "significant" is prohibited unless a sampling distribution exists |
| `hypothesis` | untiered; a proposition under test, not an assertion |

**Tiers** (T0 strongest): T0 unqualified causal; T1 causal with a scope
qualifier; T2 causal with disclosed counterevidence; T3 associational or
consistency; T4 descriptive.

**Three modifiers**, recorded per assertion site:

```
qualifier_scope: sentence | paragraph | section | cross_reference
counterevidence_prominence: parenthetical | clause_appended | separate_contrastive_sentence | footnote | appendix
underlying_precision: {significant_at, has_sampling_distribution, n, estimate_id}
```

`qualifier_scope` above `sentence` is permitted, but the qualifying statement
must be registered as a `scope_declaration` with an explicit coverage range.
This is what catches a scope caveat that governs three counterfactual
experiments in the body and then vanishes from the abstract.

## Assertion sites

Each claim carries:

```yaml
assertion_sites:
  - path: paper/results.tex
    anchor: <stable anchor or line range>
    section_role: title | abstract | introduction | results | mechanism | discussion | conclusion
    declared_tier: T1
    assertion_type: world
    qualifier_scope: sentence
    counterevidence_prominence: null
    underlying_precision: {estimate_id: EC-002#row1col2, significant_at: 0.05, has_sampling_distribution: true}
```

Two-layer enforcement, and both layers are required: the declaration makes
intent auditable; a lexical scan catches drift. The scan runs **only on
registered assertion sites**, never on the full text. This is what keeps false
positives near zero — quoted literature, negated sentences, and related-work
prose are simply out of scope.

## The metric

```
overclaim_residual = lexical_tier_strength − evidence_strength
```

`evidence_strength` derives from registry state already present — assessment,
whether the revision was narrowed (`revision_reason: bounded_by_*`), gate
status, supporting card `provenance` — plus `underlying_precision`.

- residual > 0 → BLOCK (overclaiming)
- residual < 0 → INFO (wasting evidence)

Do not implement tier compliance as a standalone check. The residual is the
check; the tier alone is an input to it.

## Four checks derived from corpus-validated criteria

The corpus classifies downgrade moves as honest or evasive on four criteria:
locatability, propagation, signed direction, immediate recovery. Three are
mechanisable.

| check | rule | level |
|---|---|---|
| **propagation** | a claim narrowed in the results section (`revision_reason: bounded_by_*`) whose assertion sites in `title`, `abstract`, or `conclusion` still carry the pre-narrowing tier | BLOCK |
| **counterevidence prominence** | counterevidence bearing on an identifying assumption whose `counterevidence_prominence` is weaker than `separate_contrastive_sentence`, or whose site is a footnote or appendix | BLOCK |
| **immediate recovery** | a concessive structure at an assertion site followed within one sentence by `However / Nevertheless / Overall / Encouragingly` with no tier reduction | WARN |
| **upgrade trace** | an assertion site whose tier is stronger than the same claim's tier at its `results` site, without a recorded `upgrade_justification` | WARN, not BLOCK — see below |

## Calibration facts that constrain the rules

These come from the corpus and override intuition. Implement to them.

1. **Abstracts stronger than body text is the norm, not an error.** 30 of 45
   comparable pairs; 13 of 14 papers do it at least once. A rule that blocks it
   would be violated universally and therefore ignored. Require a trace, not
   compliance — hence `upgrade_trace` is WARN.
2. **Strength peaks are not always in the abstract.** The corpus contains
   title > abstract > body, introduction > abstract, and
   conclusion > abstract > results. `title` must be a checkable section_role.
3. **Limitations sections are not where downgrading happens.** Downgrading
   happens inside the results section, adjacent to the failure. Three of nine
   papers with a dedicated limitations section mention none of the failures
   already disclosed in their body. The checker must not treat a limitations
   section as satisfying any disclosure requirement.
4. **A dedicated limitations section correlates with ceremonial disclaimers.**
   Of five papers without one, four have limitations that are all real
   constraints, because with nowhere else to put them they attach to the claim
   they affect and therefore carry a column number or variable name. This is a
   guidance item for the Stage 7 contract, not a validator rule.

## Structural-estimation specifics

Add to the Stage 6b contract:

- `identified` versus `calibrated` must be lexically distinguishable, matching
  observed practice: identification stated passively or as "only X can be
  identified"; calibration stated as an authored setting with its source.
- Register `identified → simulated` as a downgrade type. A quantity that moves
  from an estimated parameter to a simulation output loses its sampling
  distribution while remaining grammatically identical to other effect sizes;
  this is invisible to tiering and must be typed as `model_internal`.
- Counterfactual scope caveats must be registered as `scope_declaration`s with
  explicit coverage, for the reason given above.

## Explicitly out of scope

Do not build a banned-word list, and do not constrain sentence form. The tier
governs how much a sentence promises, not how it is phrased. Lexical markers are
grouped by semantic class (causal, scope-qualifying, associational, descriptive,
framing) and must be project-extensible.

---

# Part C — implementation order

1. **A-1 through A-7** on the v2.1 spec, then `validate_registry` with the
   extended smoke fixture list. v2.1 remains prose until the validator exists;
   nothing in Part B should start before it does.
2. **v2.2 spec** authored from Part B.
3. **v2.2 validator extension**: assertion-site registration, the residual, and
   the four checks — reusing the v2.1 traversal rather than adding a second
   engine.

The registries are human-editable YAML held in the repository so that every
state change is visible in a diff. Nothing in either layer may be generated into
a form that is not reviewable as text.
