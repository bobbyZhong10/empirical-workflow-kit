# Writing Under the Registry

Read this when a validator finding concerns prose or assertion coverage. The
paper is organized by its question, argument, and evidence. The registry records
internal traceability and decisions. Do not draft by transcribing the registry.

## What belongs where

| Paper | Internal record |
|---|---|
| A finding, magnitude, and uncertainty needed by readers | Exact values, CSV rows, evidence-card IDs, and figure bindings |
| The economic question and discriminating evidence | Prediction counts, identifiers, and item-by-item gate outcomes |
| The method used and assumptions bearing on the result | Defenses of every unused method and routine design-search history |
| A material deviation affecting interpretation, with reason and timing | The full decision-log history and repair sequence |
| The result's actual scope and consequential limitations | Tier labels, compensation records, registry and ledger vocabulary |

Apply `research-writing.md` to the proposition and its inferential bridge. An
appendix also needs a reader purpose. Reproducibility records can retain material
that does not belong in the manuscript or its appendix.

## What the automated checks establish

Version 2.8 retains mechanical checks on sources, anchors, numbers, declared
fields, dependencies, and gate-closure records. Lexical residuals, candidate
assertion discovery, disclosure phrasing, and house-style patterns are advisory.
`OVERCLAIM_RESIDUAL`, `COUNTEREVIDENCE_BURIED`, or
`NARROWING_NOT_PROPAGATED` names a pattern to inspect, not a proven semantic error.
The names are retained for API compatibility. A clean report cannot establish
that a proposition is supported, that the main finding is interesting, or that
the reader understands the contribution.

Do not add a hedge or a separate contrastive sentence just to satisfy a pattern.
Read the claim and evidence. If the inference overreaches, delete or correct it;
if it is already accurate, record why the prompt needs no prose change in the
existing review record. No additional per-warning clearance register is needed.
A real unresolved overclaim still prevents substantive approval for circulation.

State a condition where needed to interpret the result. Standalone summaries
must remain accurate, but every mention need not repeat the condition. The
right remedy may be a scoped noun or verb, a necessary explanation once, or
removal of an unhelpful paragraph, rather than another disclaimer.

## Internal assertion schema

The existing schema remains readable. For registered assertion sites, retain
`assertion_type`, `declared_tier`, `qualifier_scope`,
`counterevidence_prominence`, `underlying_precision`, `scope_declaration`,
`power_basis`, `upgrade_justification`, `alternative_explanation`, and
`as_modeled` as applicable. Do not create fields solely to fill a checklist.

| Type | Internal meaning |
|---|---|
| `world` | Empirical proposition, with declared T0--T4 tier and evidence link |
| `negative` | A null empirical result; review interval and economically meaningful bounds |
| `methodological` | A statement about design, measurement, or implementation |
| `model_internal` | A model implication, with `as_modeled: true` |
| `discriminating` | A comparison with a specifically named alternative explanation |
| `hypothesis` | A proposition awaiting examination |

Only `world` sites take a tier or upgrade trace. Keep `alternative_explanation`
for discriminating sites, `as_modeled` for model-internal sites, and `power_basis`
for negative sites; otherwise omit or set null. A complete `power_basis` record
is not evidence of absence. Use `robustness-checklists.md` to interpret the
interval or equivalence test and decide whether an MDE changes the judgment.
Do not print an MDE merely because the schema can hold one.

An `analytical` Evidence card names a derivation document and can support
model-internal or hypothesis sites. It cannot turn a proof into an empirical
finding. Keep calibrated parameters distinct from identified parameters and
model scenarios distinct from observed responses.

## Disclosure links and historical failures

Link a challenge once through `counterevidence_disclosure.challenge_ids` on an
assertion site or a relation's `disclosure` location. The validator checks that
the referenced text exists and the declared challenge IDs cover the live set.
It cannot check whether those words actually explain the challenge. The
substantive reviewer must do so, and the cold reader must be able to understand
the evidence boundary without consulting the registry.

Retain failures with their original evidence. A current issue can be active,
repaired, closed by claim withdrawal, or retained as a disclosed limitation.
Use existing `satisfied`, derived `moot`, `released`, or justified `inapplicable`
records only where their documented conditions hold. `satisfied` requires the
compensation artifact and acceptance; an outstanding STOP remedy remains open.
`moot` requires a documented withdrawal/end-of-life and cannot leave the withdrawn
claim in a current output. `released` records the change, reason, authority,
timing, evidence, and disposition; it is not a retroactive pass. A disclosed
limitation needs a supported remaining claim and a reasoned acceptance record.

Separate valid historical failure records from current defects in their closure
records. Do not erase a failure or fabricate a passing statistic to reduce a
blocking count. Report the remaining mechanical record issues separately from
current research defects and delivery requirements.
