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

## 4. Debug by root cause

When a result, test, or validation fails:

1. Preserve the failing output and reproduce it.
2. Isolate the smallest stage, input, or assumption that changes the result.
3. Form and test a causal explanation before patching.
4. Make the smallest correction consistent with the explanation.
5. Re-run the failing check and a nearby regression check; record the
   disposition and residual risk.

Do not weaken a gate, relabel a failure, or add post-result specifications just
to make a run complete.

## 5. Close work with evidence

Before calling implementation work complete, retain the commands or entry
scripts, environment/version information, test or validation outputs, and
remaining limitations. For material changes, obtain an independent review of
the changed assumption, code path, or identification implication. A claim of
completion requires evidence from the relevant check, not an intention to run
it later.

## 6. Keep project state singular

Do not introduce a parallel TODO list, issue database, or private agent memory
as the authoritative project record. Use _status.md for current state,
decision-log.md for authorized decisions, Evidence cards for factual and
execution evidence, and the registry for claims, figures, gates, and their
dependencies.
