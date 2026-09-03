# Research Code Review

Review the requested scope and report one actionable finding per line. Start
with the fix and use these tags when they apply:

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
