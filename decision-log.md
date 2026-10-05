# Decision log

## 2026-10-04: Question, evidence, and inference revision

The user authorized changes to research progression, validation, and writing rules
to reduce workflow-induced rework. Scope and implementation sequence are recorded
in docs/workflow-2.8-change-plan.md. Historical records are evidence of failure
modes in use, not identification of a causal effect of the skill. Preserve raw-data
protection, prospective interpretation, failed results, reproduction, and decision
history. Use existing artifacts rather than add a parallel tracking system.

The implementation will distinguish mechanical checks from substantive and
editorial judgment. Lexical heuristics will become review prompts rather than
automatic semantic verdicts. Existing evidence-backed gate closure remains
required; historical failures must not be erased or converted into fictitious
passes. No congestion-pricing project artifact is authorized for modification.

## 2026-10-04: Management Science template replacement

The user requested replacement of the kit's writing template with the files in
`/Users/bobbyzhong/Desktop/INFORMS_MNSC_Template_6_10_2024`. The kit retains
the existing template directory path and replaces its contents with the supplied
12-file set. The Stage 7 adapter now installs `informs4.cls` and the new sample
source. The supplied class has marked circulation edits; journal submission
requirements must be checked when an actual manuscript is prepared. File and
build evidence is in `docs/evidence/mnsc-template-update-2026-10-04.md`.

## 2026-10-05: Management Science template comment adjustment

The user requested another sync from the desktop template folder. Only
`INFORMS-MNSC-Template.tex` changed: four comments clarify that the supplied
`.bib` uses full journal names and that `informs2014.bst` prints the journal
field as given. The kit source was updated without changing the class, style,
or adapter. Build and comparison evidence is in
`docs/evidence/mnsc-template-adjustment-2026-10-05.md`.

## 2026-10-05: Workflow 2.8 completed and checked

Implemented the authorized question/evidence/inference contract, claim-specific
boundaries, estimand crosswalk, separate diagnostic interpretation, internal/prose
separation, root-cause repair, cold reading, issue dispositions, cross-version
constraints, and stopping rules in the canonical workflow and existing templates.
Lexical/editorial findings now prompt review instead of imposing semantic verdicts;
source, number, dependency, and documented-closure checks remain executable.

Version 2.8 is synchronized across the validator, manifest, adapters, and current
test fixtures. The full suite passed 447 tests; project and user runtime parity
both reported zero errors; git diff --check was clean. Numerical and anchor fault
injections still failed as intended. Research Checkpoints B/C are not applicable
to kit maintenance and were not used to certify a paper. Evidence, limitations,
commands, and the manual historical replay are linked from _status.md and
`docs/workflow-2.8-handoff.md`.

Preserved the concurrent Management Science template replacement and its decision
history. No congestion-pricing artifact or existing empirical registry was edited.
Stop work on this revision unless a concrete regression or prospective use evidence
warrants reopening. This decision does not claim measured reductions in rework or
independent validation of manuscript quality.

## 2026-10-05 — Follow-up adjudication and execution-path repair

User supplied concrete congestion-pricing history and asked what 2.8 still missed.
Read the installed skill's canonical paths, Stage 6a/7, focused references, the
R9 review and D-0910-031 correction, cold read, principal feedback, and sequential
AE reviews. Preserve review misjudgments alongside correct findings. Replace the
companion review's word-position gate and automatic role recommendation with
source-based adjudication. Route Stage 6a audits, Stage 7 revisions, council, and
referee response through the same existing quality-loop reference.

Module entry now asks about mechanical-only success; exit permits background.
Claim review examines units, constructs, targets, shared inputs and assumptions.
Diagnostics distinguish shared-counterfactual evidence from independent checks.
First-draft cold reading asks about actors and economic conflict before author
context. Revisions identify the reader judgment they could change and correct
understatement as well as overreach. Existing review and response templates carry
adjudication, without a new tracker, validator, or schema/version change.

Historical replay and its limits are in docs/workflow-2.8-migration.md; inspected
sources are in docs/evidence/workflow-2.8-iteration-review.md. This follows new
specific evidence and authorization, not an unprompted reopening of homogeneous
editing. No empirical project, raw data, or unrelated template work was modified.

Follow-up validation: 447 tests passed; project/user parity zero errors, no
notices; existing finding/response YAML parsed; diff whitespace clean. Runtime
doctor zero blocks and five unrelated warnings. Logs use the `followup-` prefix
in .research-state. The installed skill resolves to the canonical Documents
checkout. No independent review or measured rework benefit is claimed.

## 2026-10-05 — Generalize interpretation and organization across methods

Authorized by the user's request to sweep all supported workflow work, with
priority on organization, economic meaning, contribution, and behavioral
explanations. Centralized those rules in research-writing.md and connected all
nine method-pack prompts, the facade path, Stage 2–7 interpretation/writing,
and direct literature/preregistration/review/talk entry. Kept stage-specific
technical obligations rather than duplicating new checklists.

Replaced forced theoretical novelty, mandatory mechanism framing and contribution
counts; corrected the post-treatment-as-mechanism escape, categorical causal
label conflict, and sensitivity/p-value-as-design-verdict wording. The rule now
supports strong warranted conclusions and bounded noncausal contributions alike.
Added one mechanical routing test; it checks links, not meaning. Existing
preservation, prospective interpretation, baseline reproduction and decision
history remain. No new method implementation or empirical claim is authorized.


Generalization verification completed: project and user parity both zero errors.
The routing test accepted a valid temporary pack and rejected removal of its
shared-reference link; log: .research-state/generalization-routing-fault.txt.
This demonstrates wiring coverage only. Final diff whitespace check is clean.
