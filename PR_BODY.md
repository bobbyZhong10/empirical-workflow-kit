# Claim governance v2.1, writing strength v2.2, and an executable validator

19 commits, 161 files, ~11,600 insertions. 237 tests pass.

## What this adds

**v2.1 — claim governance.** The kit versioned artefacts but not claims. It could not
say that a number was superseded, that a table may not mix two analysis pipelines, or that
a pre-committed acceptance gate had been overridden and by whom. This branch adds claims
with stable identity and independent revisions, evidence cards and typed evidence
relations, reported figures, acceptance gates split into frozen definitions and
per-pipeline evaluations, semantic facts with provenance and validity ranges, and
conditional-artifact applicability records.

The governing rule is one sentence: **the system only makes state worse; people make it
better, and every improvement has an author, a timestamp, and supporting evidence.**
Cascades are monotone and run as a single topological pass, so termination is a property
rather than a hope, and every state that improves carries a signature.

**v2.2 — writing strength.** A layer between the results and the prose. Assertion type is
prior to tier: only `world` assertions are tiered and enter the residual, while `negative`,
`methodological`, `discriminating`, `model_internal`, and `hypothesis` assertions each
carry their own rule. The check is the residual — lexical strength minus evidence strength
— blocking when positive and reporting when negative.

The tier model and its calibration come from a 14-paper corpus of MISQ, MS, and ISR
papers (278 assertion sentences, ~110 downgrade instances), recorded in
`docs/superpowers/specs/2026-08-15-writing-strength-model-v2.md`. Three corpus facts
constrain the rules rather than the other way round: abstracts stronger than body text are
the norm (30 of 45 comparable pairs), so an upgrade requires a trace and not compliance;
strength peaks are not always in the abstract, so `title` is a checked section role; and
limitations sections are not where downgrading happens, so one cannot satisfy a disclosure
requirement.

**An executable validator.** `tools/validate_registry.py` reads the registries and emits
machine-readable Checkpoint B/C blocking reports. Without it the specification is prose and
the invariants are unenforced, which was the original diagnosis this work started from.

## The four changes made after independent review

A four-dimension review — adversarial bypass, spec conformance, corpus fidelity, adoption
burden — found that the system checked the registry against itself rather than against the
world, and that an empty registry validated exactly like a complete one.

1. **Evidential frames are graded, and matching tolerates inflection.** Framing was an
   `elif` after causal, so a frame had no effect whenever a causal verb co-occurred and
   `is associated with` scored identically to the unhedged sentence. Eight of ten ordinary
   causal sentences scored as descriptive because `raises`, `boosts`, and `driven` matched
   nothing. The corpus grading is now pinned by test.

2. **Reported figures and challenge disclosures are grounded.** A figure's value is resolved
   from the artefact it names and compared; a disclosure's paper location is resolved as a
   path and anchor. Previously a registry could hold 999.9 while the analysis output held
   7.77 and still validate, and the macro generator would typeset 999.9. The check found
   that several test fixtures declared artefacts that did not exist.

3. **Discovery replaces registration-only scanning.** Each output declares its
   `manuscript_sources`; the manuscript is scanned for sentences carrying a causal marker,
   and a candidate no registered site covers blocks. Classification still runs only at
   registered sites, so quoted scholarship is never graded. This inverts what marker recall
   controls: an over-inclusive list now costs one question to the author rather than
   letting an overclaim through. `MANUSCRIPT_COVERAGE` reports the numbers, and a registry
   that declares no manuscript source reports coverage as *inactive* rather than success.

4. **Scaffolding.** About three fifths of a registry is mechanically derivable, and none of
   it was generated. `tools/scaffold_registry.py init` reduces first contact from ten
   missing-file errors to two real decisions; `sites` stubs what discovery found, filling in
   path, anchor, section role, and the tier the classifier read while leaving the judgement
   fields empty; `figures` reads values from an analysis artefact so grounding passes by
   construction.

## Stage 7 LaTeX adapter

The manuscript binds to the registry through a no-op `\claimsite` macro, so an anchor
survives editing and changes no typeset output. Trailing LaTeX comments are stripped from
anchored text, because a comment could otherwise supply a counterevidence cue the reader
never sees. Section roles are resolved from the source rather than trusted. Quantitative
values are emitted from the registry as macros; a stale or superseded figure is withheld,
so the build fails rather than typesetting a retired number.

## Known gaps

Adversarial bypasses remain open and are documented rather than fixed: forged change
records, `inapplicable` gate evaluations scoring as passed, `estimate_id: null` scoring
higher than an honest exploratory reference, and a hard-wrapped sentence being read only to
its first line. The last is the one to fix first — hard wrapping is the LaTeX default, so
it misleads honest authors rather than only enabling motivated ones.

`bash tests/smoke/run_smoke.sh` has not been run end to end in this environment; it needs R
with `arrow`, `yaml`, `fixest`, and `modelsummary`. The registry legs were verified by
invoking the validator directly.
