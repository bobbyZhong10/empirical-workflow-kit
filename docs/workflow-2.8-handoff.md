# Workflow 2.8 maintenance summary

## Completed scope

Version 2.8 updates the protocol, stage router, analysis and writing contracts,
validator reporting, review adjudication, and existing project templates.
Question, evidence, and inference define progress. Mechanical checks remain
separate from research credibility and reader comprehension.

The cross-method extension connects all nine method-pack prompts and their
facade entry to the shared writing contract. Relevant stages and companion
literature, preregistration, review, presentation, and formatting operations
apply the same organization, economic-meaning, contribution, and behavioral
interpretation rules. No new research tracking system was introduced.

## Verification

Recorded full-suite result: 448 tests passed. Project and user runtime parity
reported zero errors. Numerical, anchor, and routing fault cases failed as
intended; valid controls succeeded. These results describe mechanical coverage,
not research quality. Research Checkpoints B/C are not applicable to this
maintenance release.

Use the README's environment setup, then run from the repository root:

```sh
tools/validate_registry --version
.venv/bin/python -m pytest -q
.venv/bin/python scripts/verify_runtime_parity.py --project --all --repo .
git diff --check
```

Configured capabilities use the manifest runtime CLI and project runtime
profile.

## Migration and limitations

Existing research projects require an explicit version migration. No project
registry is upgraded or historical failure closed automatically. The
[migration guide](workflow-2.8-migration.md) describes compatibility and
hypothetical interpretation examples. The
[evidence record](evidence/workflow-2.8-iteration-review.md) distinguishes
recorded software verification from unmeasured research outcomes.

Method literature and statistical implementations have not been comprehensively
revalidated. Independent readers and prospective use are needed to assess clarity
and rework. Future maintenance should respond to a concrete defect or substantive
new evidence rather than increase checklist size.
