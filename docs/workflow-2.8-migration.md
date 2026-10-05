# Workflow 2.8 migration and interpretation guide

Version 2.8 strengthens question-led progression, evidence interpretation, and
reader-facing organization. This guide describes behavior and compatibility;
it does not publish private research histories or establish a measured reduction
in rework. Verification scope is documented in
[the implementation evidence record](evidence/workflow-2.8-iteration-review.md).

## What changes in use

An analysis module starts and ends in its existing Evidence card: economic
question, competing explanations, observable evidence, inferential bridge,
decision-changing result, then learning, unresolved alternatives, and whether to
continue, narrow/delete, or stop. A measurement or accounting contribution does
not need to be relabeled causal. The same discipline applies to conditional
models and to exploratory work without pretending it was preregistered.

The paper is organized by argument and evidence. Internal prediction counts,
IDs, gate verdicts, unchosen-method defenses, and routine repair history remain
internal. Keep exact numerical provenance while selecting and rounding only
reader-useful quantities. Conditions appear where interpretation requires them,
not in a repeated disclaimer at every mention.

The existing analysis memo holds an estimand crosswalk across the main result,
main figure, dynamics, sensitivity, and magnitude conversion. Diagnostic records
separate successful execution from the appropriateness and implications of the
decision rule. Revision begins with the root cause and ends by checking for new
repetition, unnecessary numbers, claim drift, and length inflation.

The current paper story retains advisor requirements, withdrawn propositions,
settled variable meanings, prohibited inferences, main contribution/result, and
open questions. The status record reports four readiness dimensions separately.
There is no new tracking system, mandatory per-warning clearance form, or
additional universal robustness battery.

## Validator compatibility

The validator and manifest now report 2.8. Existing registry shapes remain
readable; old empirical projects are not silently migrated. To migrate a project,
review the changed rules, record the decision, update its kit_version, and rerun
the checkpoint appropriate to its actual phase. Run final C only after Stage 7.
Keep the prior version and reports for comparison. Historical v2.1/v2.2 design
documents describe their original behavior; this revision supersedes their
lexical severity and required-sentence-form rules.

The public report retains blocking, reports, derived, and state. It adds
assurance with mechanical coverage/counts and explicitly unassessed substantive
and editorial dimensions. CLI exit status now reflects mechanical blockers.
REGISTRY_VALID means only that the implemented mechanical checks passed.

The following existing codes become WARN pattern prompts in reports:

- OVERCLAIM_RESIDUAL and NARROWING_NOT_PROPAGATED.
- COUNTEREVIDENCE_BURIED and COUNTEREVIDENCE_PROMINENCE_UNCORROBORATED.
- HYPOTHESIS_WITHOUT_PROPOSITION, NEGATIVE_POWER_BASIS_REQUIRED,
  NEGATIVE_RULE_OUT_UNSUPPORTED, NEGATIVE_UNHEDGED_WITHOUT_POWER, and
  MODEL_INTERNAL_SIGNIFICANT_UNSUPPORTED.
- ASSERTION_SITE_UNREGISTERED and ASSERTION_RANGE_COVERS_MULTIPLE_ASSERTIONS.
- The four PROSE_* house-style findings.

Legacy discovery modes remain readable, but neither makes lexical candidates
semantic verdicts. Numbers, resolvable files/anchors, precision metadata,
dependencies, and required gate-closure records remain checked. Disclosure links
check actual locations and challenge-ID coverage independently of whether a
sentence contains a prescribed connective. Their adequacy requires substantive
review. Filling a power field cannot certify evidence of absence.

No gate history is automatically closed or deleted. Use the existing satisfied,
moot, released, or inapplicable paths with their evidence and authority. A current
unsupported claim remains a substantive problem even when mechanical validation
passes. Missing closure records remain record defects, rather than being reported
as evidence that every historical research finding is still wrong.

## Review adjudication examples

These hypothetical examples illustrate the rules. They are not quotations,
empirical findings, or reports about a particular research project.

| Example | Appropriate decision |
|---|---|
| A reviewer equates a period-level estimate with a change between periods. | Check the contrasts and covariance. Preserve distinct supported tests; do not count a reparameterization as independent evidence. |
| A reviewer treats a decline in one accounting component as a necessary decline in the total. | Inspect the identity and other components. Reject the necessity claim unless those components are fixed; retain any valid criticism about independent evidence. |
| A nonsignificant estimate is described as equivalence. | Assess the interval against a meaningful bound and appropriate test; retain the estimate without claiming equivalence by non-rejection. |
| An exploratory result is marked supported in an internal record. | Preserve its exploratory provenance; the status does not supply confirmatory timing or causal identification. |
| A revision adds qualifiers without changing the underlying inference. | Repair or remove the unsupported inference and stop repetitive wording changes that do not affect reader judgment. |

Numerical consistency tests should reject a deliberately corrupted value, and
source checks should reject an unresolved source or anchor. Such checks establish
only the tested mechanical behavior. They cannot establish proposition meaning,
contribution, or reader understanding.

## Illustrative cross-method scenarios

The common writing contract now applies before interpreting results, not merely
at final prose editing. The nine existing method packs link directly to it, as
does the facade contract; this covers both stage routing and named-method entry.
Stage 6b handles structural and conditional models. Measurement, description and
accounting use the existing stage paths with inapplicable causal obligations
marked, not manufactured. Stage 1 supports non-panel records without pretending
every source is a panel. Unsupported estimators still require method governance.

The following are hypothetical transfer cases, not new empirical findings or
method validations. They test the decisions the instructions now prescribe:

| Transfer case | Required interpretation and writing decision |
|---|---|
| A well-executed field experiment changes purchases; an interaction is larger for experienced users. | State the assignment effect and heterogeneity; learning, trust, or attention remain candidate explanations unless evidence discriminates among them. Do not add a mechanism section solely to rename the interaction. |
| IV estimates a response among compliers and a policy memo multiplies it by the entire population. | Name the affected margin and assumptions, keep a population-wide benefit conditional on additional transport/behavior evidence; foreground the economic question rather than first-stage diagnostics. |
| RD finds an outcome discontinuity near an eligibility threshold. | Explain the local economic consequence; do not silently generalize to all eligible people or other thresholds. Inspect diagnostic concerns substantively rather than treating one p-value as validity. |
| Synthetic control has excellent pre-fit and several related placebo plots. | Interpret the treated case and period under the counterfactual argument; fit and correlated checks do not independently establish mechanism or transportability. |
| FE or adjusted observational estimates are precise and balance improves. | Explain the variation and target; neither estimator nor balance establishes causal identification. Do not automatically disqualify a defended design either. |
| DiD dynamics appear to rise over time. | Distinguish the actual dynamic estimand from an adaptation or learning story, and from changing composition or exposure. Preserve the supported temporal finding. |
| Conjoint produces a positive task-choice effect and a simulated market share. | Keep the task distribution and model interpretation explicit; do not call the result realized uptake, general preferences, or welfare without the required bridge. |
| A classifier predicts survey labels accurately and a feature is important. | Validate the measured construct and held-out target; accuracy/feature importance does not identify motives or causal drivers. |
| A model fits its targeted moments and estimates a preference parameter tightly. | Separate maintained behavior, parameter identification and evidence discriminating alternatives. Economic and welfare implications remain conditional on their respective assumptions. |
| A new measurement shows a materially different population pattern without causal identification. | Explain what prior knowledge changes, why coverage and scale matter, and whether it is a main contribution or background. Do not force theory novelty or a policy recommendation. |
| A technically correct paper follows estimator order and repeats hypothesis IDs. | Rebuild the reader-facing sequence around the question, evidence, economic meaning and increment over closest research; retain technical provenance internally. |

Routing checks verify that each installed method path reaches the common contract;
they cannot establish that an agent will reason correctly in every future case.
The scenario assessment is implementer-led. Independent reader feedback and actual
use are still needed to evaluate clarity and rework. Existing identification and
data limits remain; no writing rule manufactures behavioral or causal evidence.
