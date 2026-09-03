# Runtime recipes

These recipes bind the portable research contract to one machine without
putting machine-specific paths, credentials, or interaction preferences into a
canonical skill. The research protocol, method prompts, checkpoints, and
project records are identical in Claude Code and Codex.

## Configure once per checkout

Copy `runtime-profile.example.yaml` to the ignored
`runtime-profile.yaml`. Set commands and optional paths for this machine, then
run:

```bash
python3 scripts/ewf.py doctor
python3 scripts/ewf.py env
```

`doctor` reports `PASS`, `WARN`, and `BLOCK` findings. Missing required
language runtimes or invalid method manifests block the command. Optional
presentation, document, source, and notification capabilities produce warnings
when unavailable. Secret checks report only whether the named environment
variable exists; they never print its value.

Use the command wrapper whenever a workflow invokes a configured tool:

```bash
python3 scripts/ewf.py run rscript --vanilla analysis.R
python3 scripts/ewf.py run quarto render talk.qmd
python3 scripts/ewf.py run node presentation-tooling/deck-check.mjs fit talk.html
```

This makes the command in `runtime-profile.yaml` operational. A temporary
override such as `EWF_NODE_COMMAND=/path/to/node` takes precedence without
changing a tracked file. Prefer a profile entry for stable configuration.

If a tool cannot use the wrapper, load shell-safe bindings explicitly:

```bash
eval "$(python3 scripts/ewf.py env)"
```

Review the emitted bindings before evaluating them when the profile came from
an untrusted source.

## Capability boundaries

- Keep API keys and contact addresses in environment variables whose names are
  declared by the profile.
- Keep authenticated and public browser sessions separate. Serialize
  authenticated browser work unless the connector explicitly supports
  concurrency.
- Treat Overleaf, Zotero, remote compute, and notifications as optional
  capabilities. Their absence degrades that operation; it does not authorize a
  hard-coded personal path.
- Keep repository artifacts in English. At conversation start, resolve the
  user's primary language from the first substantive request and record or
  apply that policy through `research.yaml`. Switch only on an explicit user
  request; conversation language never changes the artifact contract.
- Run `doctor --strict` in a machine image or CI job that promises every
  optional capability.

See [claude-code.md](claude-code.md) and [codex.md](codex.md) for discovery and
handoff details specific to each runtime.
