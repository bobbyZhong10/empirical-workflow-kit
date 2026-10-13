# Maintenance decision log

## 2026-10-04: Question, evidence, and inference revision

Revise research progression, validation, and writing around economic questions,
evidence, and warranted inference. Preserve raw-data protection, prospective
interpretation rules, failed results, baseline reproduction, and decision history.
Reuse existing project artifacts rather than introduce a parallel tracking system.

Separate mechanical checks from substantive and editorial judgment. Treat lexical
heuristics as review prompts, retain evidence-based gate closure, and prohibit
retroactive conversion of failed results into passes. The scope is kit maintenance;
external research data and project registries remain unchanged.

## 2026-10-04: Management Science template replacement

Replace the repository template with the supplied June 2024 distribution while
retaining the existing template directory. Install the 12-file set and update the
Stage 7 adapter to use `informs4.cls` and the replacement sample source. The class
contains marked circulation edits; submission compliance requires a separate
assessment. See `docs/evidence/mnsc-template-update-2026-10-04.md`.

## 2026-10-05: Management Science template comment adjustment

Synchronize four bibliography comments in `INFORMS-MNSC-Template.tex`. The comments
clarify that the supplied bibliography uses full journal names and that the
bibliography style prints the journal field as supplied. No class, style, or
adapter behavior changed. See
`docs/evidence/mnsc-template-adjustment-2026-10-05.md`.

## 2026-10-05: Workflow 2.8 implementation

Implement question-led progression, claim-specific evidence boundaries, estimand
alignment, diagnostic interpretation, separation of internal records from prose,
root-cause repair, independent cold reading, issue dispositions, and stopping
rules. Lexical/editorial findings become advisory; source, numerical, dependency,
and documented-closure checks remain executable.

Synchronize version 2.8 across the validator, manifest, runtime adapters, and test
fixtures. Recorded verification: 447 tests passed; project and user runtime parity
reported zero errors; whitespace checks passed. Numerical and anchor fault
injections remained detectable. These results concern software behavior, not
research quality. Research checkpoints do not apply to kit maintenance.

## 2026-10-05: Review adjudication and execution-path repair

Require adjudication of material reviewer allegations before assigning repairs.
Retain confirmed, partly confirmed, mistaken, and unverified findings with their
evidence and consequences. Replace contribution-phrase positioning rules and
automatic adoption of a review role's recommendation with substantive assessment.

At module entry, assess whether successful estimation would yield only a mechanical
fact. At exit, allow background status. Inspect units, constructs, estimands,
shared inputs and counterfactuals, and bridge assumptions. Introduce manuscript-only
cold reading after the first complete draft and require each revision to identify
the reader judgment it could change. Correct understatement as well as overreach.
Use existing review and response records without adding a new state system.

Recorded verification: 447 tests passed; runtime parity reported zero errors;
review templates parsed successfully; whitespace checks passed. Independent
manuscript quality and reductions in rework were not measured.

## 2026-10-05: Cross-method interpretation and organization

Centralize manuscript organization, economic meaning, contribution, and behavioral
interpretation in `research-writing.md`. Route all nine method-pack prompts,
method facades, relevant stages, and companion writing operations through this
contract while retaining method-specific technical obligations.

Remove forced theoretical novelty, mandatory mechanism framing, and contribution
quotas. Correct instructions that treated post-treatment conditioning as a
mechanism test or significance decisions as categorical design verdicts. General
writing rules do not authorize unsupported methods or establish identification.

Recorded verification: 448 tests passed; project and user parity reported zero
errors. A routing check accepted a valid temporary method pack and rejected a
removed shared-reference link. This verifies routing, not interpretation quality.

## 2026-10-05: Scoped upstream writing and instruction update

Review upstream changes through `fad84ebe0d0d83c8ce7d17d3cc5deff49b7d527e`.
Adapt genre-sensitive technical explanation, purpose-first exposition, explicit
plan objectives, simplification review, and responsive execution into existing
shared references. Retain current evidence boundaries and authorization rules.
Do not adopt phrase-position quality gates or blanket publication, installation,
or delegation defaults. Record source attribution and disposition in
`docs/upstream-absorption-audit.md`; retain the baseline lock for other families.

Verification: 34 workflow contract tests passed. Project runtime parity and
offline upstream mapping validation passed. Whitespace checks passed.

## 2026-10-05: Econometric review and exhibit integration

Adapt selected guidance from `pedrohcgs/claude-code-my-workflow` at
`ae726177e23426b665e0a1eef5fb5bd83bd5b831`. Strengthen identification review by
evidence strategy, code review of the data-to-estimate path, rendered exhibit
inspection, and replication discrepancy diagnosis. Route these through existing
stage contracts and references. Preserve current estimand, evidence, authority,
and review-adjudication rules; add no separate state system or quality score.

Unexpected results require investigation rather than automatic rejection.
Numerical tolerances, random streams and display settings remain appropriate to
the design and output. Attribution and deliberate exclusions are recorded in
`docs/upstream-absorption-audit.md`.

Verification: 34 workflow contract tests passed; project runtime parity reported
zero errors; whitespace checks passed. This validates contract compatibility,
not a new empirical implementation or the statistical claims of the source.

## 2026-10-05: README alignment and acknowledgments

Align the README with the current research scope, stage exits, mechanical
validation limits, installation dependencies, and upstream audit coverage.
Distinguish the locked upstream baseline from selective later adaptations.
Add acknowledgments for the academic and econometric workflow sources, linked
to detailed attribution and license records. Correct a historical attribution
entry for a retired contribution gate.

Verification: 34 workflow contract tests passed; project runtime parity reported
zero errors. README local link targets and whitespace checks passed. Installation
commands were checked against the implementation; a fresh installation was not
performed.

## 2026-10-13: Public repository hygiene

Exclude local reading copies, the journal template package, and the obsolete
PR body from the public source tree while preserving every file locally.
The journal package includes explicit TNQ distribution restrictions; no
redistribution authorization is recorded for the reading corpus. Add credential,
environment, editor, cache, and LaTeX auxiliary ignore rules while retaining
examples, test fixtures, runtime links, and licensed presentation dependencies.
Update setup instructions to identify the journal assets as a local dependency.

Evidence: `docs/evidence/public-repository-audit-2026-10-13.md`. Ignore checks,
local-copy preservation, project parity, and whitespace validation passed.
No empirical checkpoint applies. No commit, push, or history rewrite is part
of this maintenance action; prior commits retain excluded files.

## 2026-10-13: GitHub documentation entry points

Reorganize the README around purpose, setup, capabilities, and documentation
navigation. Preserve detailed instructions in setup, workflow, and development
guides. Add a documentation index and contribution instructions. Recommend a
separate research directory and distinguish kit maintenance records from project
state. Align runtime recipes with the installed repository Python environment.

Evidence: `docs/evidence/github-documentation-2026-10-13.md`. All 34 workflow
contract tests passed, 63 local links and anchors checked successfully, project
parity reported zero errors, and whitespace checks passed. This documentation
change does not modify research rules or certify a fresh installation. No
commit or publication was performed.

## 2026-10-13: Expand the public README overview

Restore moderate detail to the landing page while retaining its quick-start
structure. Add focused skill links, checkpoint purposes, project records,
delivery layout, and profile/validator examples. Detailed guides remain the
reference for setup and maintenance. Verification: 34 contract tests passed,
38 README links and anchors passed, project parity reported zero errors, and
whitespace checks passed. Evidence remains in
`docs/evidence/github-documentation-2026-10-13.md`. No publication performed.
