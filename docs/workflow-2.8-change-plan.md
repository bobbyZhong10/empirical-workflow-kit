# Workflow 2.8 implementation scope

## Objective

Improve research progression, interpretation, and writing while preserving
reproducibility, prospective analysis commitments, and decision history. This is
repository maintenance, not an empirical study or a manuscript release.

## Implementation

1. Organize analysis around questions, evidence, and inference. Record what was
   learned and whether to continue, narrow, demote to background, or stop.
2. Separate mechanical validation from substantive and editorial review. Preserve
   source, numerical, dependency, and gate-closure checks; make lexical heuristics
   advisory and report their limited coverage.
3. Organize manuscripts around the argument and evidence. Keep internal process
   records out of reader-facing prose unless they affect interpretation.
4. Adjudicate review findings before repair. Use root-cause corrections,
   manuscript-only cold reading, and judgment-based stopping rules.
5. Apply common organization, economic-meaning, contribution, and behavioral
   interpretation rules across the supported methods and writing operations.
6. Verify software behavior with contract tests, targeted fault cases, and runtime
   parity checks. Evaluate interpretation through illustrative scenarios without
   claiming automated semantic assurance.

## Compatibility and boundaries

Reuse existing Evidence cards, story records, status files, and decision logs.
Version 2.8 changes validator reporting and severity semantics; existing research
registries require an explicit migration decision. No external research project
is migrated automatically. Method canons and estimation implementations are not
revalidated by this documentation revision.

Public maintenance records contain publishable implementation rationale and
repository-relative references. Private research materials and machine-specific
configuration are outside the public documentation boundary.
