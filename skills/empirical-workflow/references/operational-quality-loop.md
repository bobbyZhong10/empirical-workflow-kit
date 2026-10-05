# Operational Quality Loop

Use this reference when building or changing research scripts, data pipelines,
validators, registry logic, or reproducibility infrastructure. It adapts mature
software-workflow practices to empirical research without introducing a second
task tracker. The protocol, decision log, status record, and registries remain
the only project-state systems.

## 1. Classify the work before changing it

- **Research-design change:** use the Mandatory-pause and decision-log process.
  Do not treat it as a coding task.
- **Implementation or validator change:** state the intended behavior, the
  smallest check that can falsify it, and the affected artifacts before editing.
- **Data or semantic change:** update the data contract and provenance first;
  an apparently successful script is not evidence that its inputs retain their
  prior meaning.

Use a written implementation plan for multi-step or irreversible changes. Small,
reversible documentation changes may proceed directly.

## 2. Reproduce before extending

When inheriting a replication package, previously released pipeline, or an
earlier project generation, reproduce a known baseline before accepting any
extension. Record the source version, commands, comparison target, tolerance,
and discrepancies. An extension result is not credible until the baseline has
either matched or its deviation has been explained and authorized.

## Localize replication discrepancies

Match the original sample, transformations, estimand, estimator options, and
inference procedure before extending a replicated analysis. Locate the first
divergence through intermediate row counts, constructed variables, estimates,
and uncertainty calculations. Review software defaults and finite-sample or
resampling differences rather than assuming the newest output is correct.
Both the manuscript and code can contain errors.

Use target-specific tolerances based on display precision, numerical error, or
simulation uncertainty; matching significance categories is not numerical
replication. A named alternative specification explains a difference but does
not make it a replication of the original target. Preserve both results and the
reasoned disposition in existing records.

Check both source-to-output consistency and agreement among displays of the same
result in the paper, appendix, and presentation, allowing their stated rounding.
A genuinely different target needs its own evidence link. Missing displays remain
unverified; resolve conflicting displays against their source rather than copying
whichever value looks right. No additional provenance registry is required.

## 3. Validate in increasing cost order

1. Run a small, deterministic smoke case or fixture.
2. Check schema, keys, units, missingness, and expected invariants at each
   pipeline boundary.
3. Compare a known intermediate or estimate where one exists.
4. Run the full build or formal estimation batch only after the earlier checks
   pass.

For a new invariant, add a focused regression test or fixture. A test should
fail for the prior defect and pass for the correction. Keep generated outputs
and expected values separate from raw inputs.

## Adjudicate important review comments before repair

Treat simulated and human reviews as claims to investigate. In the existing
review finding or response record, mark each material allegation `confirmed`,
`partly_confirmed`, or `mistaken`, with the inspected original output or exact
manuscript version and location, rationale, and affected claim. Keep it
`unverified` while evidence is missing; state what would resolve it. Split mixed
allegations so a valid criticism does not validate an incorrect premise. Retain
the original comment and the correction, including mistaken reviews, in history.
Adjudication precedes final priority, repair strategy, and closure. A material
unverified threat may pause the affected claim pending inspection, but is not a
proven defect. Multiple roles repeating a criticism do not independently verify it.

Keep responsibilities distinct: method review examines identification and
diagnostic interpretation; domain review examines the knowledge increment; a
cold reader sees only the manuscript and reconstructs its story; model review
checks assumptions and derivations; editorial review checks length and clarity.
Mechanical consistency findings have their own limited assurance. Role agreement
and lexical matches cannot replace inspection of evidence.

## 4. Debug by root cause

When a result, test, or validation fails:

1. Preserve the failing output and reproduce it where applicable.
2. Classify the cause before choosing a remedy:

   | Cause | Repair |
   |---|---|
   | Calculation error | Correct the calculation and dependent outputs. |
   | Design defect | Adjust the design with required authority or narrow/withdraw the claim. |
   | Inferential overreach | Delete or correct the inference, rather than hedge it. |
   | Unclear expression | Improve the argument and exhibit. |
   | Intrinsic data limit | Disclose its consequence and decide whether to continue. |

3. Test the proposed explanation on the smallest affected object.
4. State the accurate affirmative conclusion, correcting understatement too.
   Name the reader judgment this revision should change. Make the smallest substantive correction; consider removing repeatedly
   defective material that does not serve the main argument. Do not default to
   new disclaimers, robustness checks, or validators.
5. Recheck the original issue and nearby effects, including new repetitive
   qualifiers, unnecessary numbers, claim drift, and length inflation. Record
   evidence and disposition; reopen only for a material unresolved issue.

Do not weaken a gate, relabel a failure, or add post-result specifications just
to make a run complete.

Before a bulk transformation, inspect a dry-run diff and the affected-file count,
including representative edge cases. After applying it, inspect resulting content
and relevant checks; a successful editing command does not establish correctness.
For generated job runners, resolve paths before changing directories, track a
specific job/process identity, and distinguish completion, failure, and loss of
contact. A silent log does not establish that a job is still running.

## 5. Close work with evidence

Before calling implementation work complete, retain the commands or entry
scripts, environment/version information, test or validation outputs, and
remaining limitations. For material implementation changes, apply `code-review.md` and obtain an
independent review of
the changed assumption, code path, or identification implication. A claim of
completion requires evidence from the relevant check, not an intention to run
it later.

## 6. Keep project state singular

Do not introduce a parallel TODO list, issue database, or private agent memory
as the authoritative project record. Use _status.md for current state,
decision-log.md for authorized decisions, Evidence cards for factual and
execution evidence, and the registry for claims, figures, gates, and their
dependencies.

## Assurance boundaries

Separate three types of validation in the review record:

- Mechanical: numbers, files, keys, calculations, references, and declared
  dependencies agree within stated coverage and tolerances.
- Substantive: the source supports the interpretation and the design supports
  the exact claim, with its assumptions and unresolved alternatives.
- Editorial: readers understand the question, contribution, evidence, and scope
  in a proportionate amount of text.

Regexes, anchors, and lexical scores only inspect finite text patterns. Their
findings are prompts for review, not proof of proposition meaning. A declaration
or resolution record proves neither that a remedy works nor that a reader
understands it. Do not report quality improvement from a growing PASS count.

For every important mechanical check added or changed, demonstrate failure on a
known bad case or targeted fault injection, alongside an unchanged valid case.
Use an independently specified expected value or reference artifact. Comparing
an output with itself, recomputing the same mistaken expression twice, or
asserting an identity by construction does not test empirical correctness.
An accounting identity may check arithmetic, never an independent mechanism.

Bind verification to the artifact inspected: source revision, build command,
output path, and checksum when reviewing a compiled artifact. Current source
cannot attest to an older PDF. Open the actual delivered version for figure,
layout, and cold-read claims. Missing artifacts remain unverified.
