# Method Governance

## Literature-first decisions

Ground choices about methods, models, metrics, measurement, variable
classification, sample rules, standard errors, clustering, and transformations
in current methodological or theoretical literature. Identify the decision
the source settles, its scope, and any live disagreement. If the literature
does not settle the choice, label it as research judgment and give a rationale
a reviewer can evaluate.

Before adopting a method that will appear in the paper, check that it is
current, reputable, maintained, implementable, licensed for the intended use,
and describable in a methods section. Availability of code or weights,
maintenance status, and compatibility with the data count alongside reported
performance. A tutorial or inherited script is not sufficient authority.

A method already supporting a reported figure is reopened only when new
evidence changes its identifying basis, a gate triggers, or a credible reviewer
objection remains unanswered. Any change then follows the mandatory-pause and
claim-governance rules.

## Source-supplied boundary

When the user states that they will supply the papers, canon, links, or other
sources, do not start an independent literature search. Record which supplied
items are missing and request those items. This boundary does not waive
metadata, version, or claim-support checks once the sources arrive.

Use a known-paper resolver for a DOI, title, author, or link. Use a literature
review operation for a topic-level search. Read multiple papers independently
when authorized and return the same structured summary from each.

## Sweep and pilot rule

Run a sweep, pilot arm, or search over specifications only when all conditions
hold:

1. The result would change a recorded decision.
2. Literature and reasoned judgment cannot settle the uncertainty.
3. The measurement cost is proportionate to what it resolves.

Record which condition supplies the strongest justification. When the
expected response is flat, the failure is one-sided, or the conclusion does
not depend on the parameter, choose a value, label it as judgment, and state
the reason. Every sweep cell is a reported figure subject to review and
pipeline lineage.

## Method-pack freshness

Every selected method pack records `Verified through`, its principal sources,
implementation versions, scope limits, and named disputes. A stale pack
triggers a targeted update search before formal estimation. New literature is
added as a dated addendum and does not silently rewrite a previously locked
analysis.
