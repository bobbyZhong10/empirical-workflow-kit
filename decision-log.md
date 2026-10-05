# Maintenance decision log

This record documents repository maintenance decisions. Private research inputs
are excluded from the public record. The privacy revision dated 2026-10-05
redacts source identifiers from earlier entries while preserving their dates,
substantive decisions, and recorded validation outcomes.

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

## 2026-10-05: Public documentation privacy and editorial revision

Revise public Markdown to exclude personal filesystem locations, private project
identifiers, unpublished numerical findings, and identifiable review histories.
Preserve maintenance decisions and validation outcomes. Replace project-specific
narratives with general implementation rationale and clearly identified
hypothetical examples. Private motivating material is not presented as publicly
reproducible evidence.

The redaction is an explicit exception to the append-only convention for the
public decision record; it does not change research results or erase maintenance
decisions. Future entries use repository-relative paths and publishable evidence.
This working-tree revision does not rewrite existing Git history or update a
remote repository.

Verification for the public documentation revision: inspected 163 tracked Markdown
files and reviewed targeted matches for personal paths and private source
identifiers. No targeted matches remained. The workflow contract suite passed
34 tests; project runtime parity reported zero errors; whitespace checks passed.
Pattern scanning is limited to the selected identifiers and does not certify
that every possible confidential detail has been detected. Public repository
links and published-source citations remain intact.
