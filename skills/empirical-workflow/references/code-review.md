# Research Code Review

Review the requested scope against the recorded research target before reviewing
style or brevity. Read the relevant code path, its inputs, and the outputs used
by the manuscript; do not infer correctness from a clean log or a plausible
coefficient. Review findings propose corrections; applying a design change still
follows the project's authority rules.

## Correctness and reproducibility

Prioritize defects by their consequences for the research claim:

- Trace source records through filters, joins, missingness, transformations,
  weights, and estimation. Check silent row loss, duplicate expansion, factor
  baselines, unit conversions, treatment timing, and post-treatment selection.
- Compare the implementation with the intended estimand, formula, and identifying
  argument. Check effective sample, fixed effects, standard errors, clustering,
  resampling unit, finite-sample adjustments, and package defaults as applicable.
- Inspect failed fits and simulations, nonfinite values, zero denominators,
  boundary cases, and random-number handling. Do not silently remove failed
  repetitions or report summaries only among successful runs without disclosure.
- Check that a fresh documented entry point can recreate the relevant outputs
  without hidden workspace objects. Record dependencies, source versions, and
  reproducible random streams; rendering should consume saved results.

Each material finding names a file/location, the violated research expectation,
a concrete failing case or inspected output, its effect on a claim, and the
smallest proposed repair. Separate static inspection from executed verification;
mark unavailable evidence unverified. Use existing review records and adjudicate
findings before treating them as confirmed defects. Style preferences do not
become correctness blockers or a numerical quality score.

For changed calculation logic, use a small analytically understood case or an
independent reference result where feasible. A regression test should catch the
identified defect, not repeat the same expression as its own expected answer.
Test edge cases that could alter the reported conclusion. Do not add tests for
purely cosmetic edits.

## Simplification

Report one actionable finding per line. Start with the fix and use these tags
when they apply:

- `delete:` dead, speculative, or duplicated code;
- `stdlib:` a standard-library function replaces the implementation;
- `native:` the platform or an existing dependency already provides it;
- `yagni:` configuration or abstraction has only one real use;
- `shrink:` show the smaller equivalent implementation.

Close a simplification review with the net line reduction that is genuinely
available, or state that no safe reduction was found. Do not change unrelated
bugs or cleanup in the same patch. A known global lock, quadratic scan, naive
heuristic, or other deliberate ceiling gets a concise comment naming the
ceiling and the condition for replacing it.

Research correctness outranks brevity. Do not remove an explicit validation,
provenance record, assumption check, gate evaluation, seed, or error path merely
to shorten the code.
