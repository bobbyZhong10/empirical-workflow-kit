# Method entry contract

Method skills at `skills/<method>/SKILL.md` are discovery facades. They make a
named empirical method visible to Claude Code and Codex while preserving one
authoritative implementation under `skills/empirical-workflow/methods/`.

When a method facade is selected:

1. Read the repository-root `RESEARCH_PROTOCOL.md`, active `research.yaml` (or
   `research.example.yaml` only when configuring a new project), `_status.md`,
   the most relevant current Evidence card, and the tail of `decision-log.md`.
2. Read `skills/empirical-workflow/SKILL.md` and
   `skills/empirical-workflow/stages/stage6a-reduced-form.md`.
3. Confirm that the named method is allowed by `research.yaml`, that Stage 6a
   is authorized, and that no unresolved Mandatory pause blocks execution.
   A facade may explain or plan a method before Stage 6a, but it must not run a
   focal analysis, silently change `current_stage`, or reinterpret an existing
   result as authorization.
4. Read the facade's named canonical `prompt.md`. Then read that pack's
   `method.manifest.yaml` and the canon, details, or R template only as the
   prompt and current task require.
5. Record the selected method, estimand, identifying assumption, canon review
   date, diagnostics, and outputs in the durable project artifacts required by
   Stage 6a. Failed identifying diagnostics trigger the protocol's backtrack or
   Mandatory-pause rule; they are not converted into caveats.

The facade contains no estimator instructions. If its wording conflicts with
the method pack, Stage 6a contract, project configuration, or research
protocol, the more specific canonical contract governs. Never copy a method
prompt into a facade or runtime-specific directory.
