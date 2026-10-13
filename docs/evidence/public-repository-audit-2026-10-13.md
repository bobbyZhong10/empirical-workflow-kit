# Evidence: public repository hygiene

- Date: 2026-10-13.
- Scope: current tracked tree, originally 689 paths; not a complete Git-history
  secret scan or a legal certification.
- Method: inspect the tracked inventory, ignore rules, text matches for common
  key formats, credential assignments, personal home paths, and contact details;
  inspect selected PDF text and the journal source headers.
- Observation: 14 full-text reading PDFs were tracked without redistribution
  authorization recorded in the repository. Two local journal style files
  (`eqndefns-left.sty` and `eqndefns-center.sty`, lines 2–11) expressly restrict
  copying, modification, and distribution without permission. The 12-file
  journal package also contains assets and a compiled example. `PR_BODY.md`
  describes obsolete versions and test results.
- Decision: retain all 27 files locally, remove them from the Git index, and
  ignore their paths. Treat the journal package as a separately obtained local
  dependency, with setup instructions in the LaTeX adapter and README.
- Observation: reviewed text matches showed placeholders, environment-variable
  lookups, scan rules, public attribution, and example contacts; no actual
  credential or personal absolute home path was identified by these checks.
  This does not establish the absence of every secret or PDF metadata field.
- Retained: runtime symlinks, maintenance provenance, synthetic fixtures,
  sample configurations, and presentation dependencies with bundled licenses.
- Verification: the 27 removed index entries still exist locally and match
  ignore rules; representative credential/cache paths are ignored; maintained
  source, examples, fixtures, and runtime links remain eligible for tracking.
  Project runtime parity reports zero errors; whitespace checks pass.
- Runtime diagnosis: zero blocks and five warnings (Quarto version, R package
  probe crash, and three unset scholarly-source variables), unrelated to the
  ignore changes. Registry CLI reports workflow 2.8.
- Limits and next action: review and commit the cleanup before publishing it.
  Previous commits retain the removed files. Any history rewrite is a separate
  coordinated action. No empirical stage or Checkpoint B/C applies.
