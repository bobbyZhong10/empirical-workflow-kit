# Claude Code runtime recipe

Claude Code reads the thin repository adapter in `CLAUDE.md` and discovers the
canonical skills through `.claude/skills/`. Those entries are relative
symlinks; do not edit them.

## Verify discovery

```bash
python3 scripts/install_runtime_views.py --project --claude --repo .
python3 scripts/verify_runtime_parity.py --project --claude --repo .
```

For optional personal discovery across projects:

```bash
python3 scripts/install_runtime_views.py --user --claude --repo .
python3 scripts/verify_runtime_parity.py --user --claude --repo .
```

A personal Claude skill with the same name can shadow a project skill. The
parity verifier reports regular copies, wrong targets, broken links, and stale
entries. The installer replaces only kit-owned entries and only when
`--replace-managed` is explicit; it refuses to overwrite another package.

For an existing external research repository, run
`python3 scripts/bootstrap_project.py /absolute/path/to/project --claude` from
the kit checkout. This installs project-local relative discovery links through
an ignored `.workflow/kit` binding and initializes only missing project records.
It does not copy prompts or overwrite existing research configuration.

## Start and hand off

Run the manifest-named runtime CLI with `doctor`, then begin at the stage recorded in
`research.yaml` and `_status.md`. A named request such as a DiD or RDD analysis
may activate its method facade, which immediately routes through the shared
Stage 6a contract and canonical method pack.

Before handing the project to Codex, finish the current atomic task and update
the evidence, decision, status, and handoff artifacts. No Claude memory file,
output style, or personal setting is part of the research record.

Use voice input, remote control, browser automation, notifications, and
external document synchronization only when they are configured on the current
machine. These interaction conveniences do not change research authority or
checkpoint requirements.
