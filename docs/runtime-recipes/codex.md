# Codex runtime recipe

Codex reads the thin repository adapter in `AGENTS.md` and discovers the
canonical skills through `.agents/skills/`. Those entries are relative
symlinks; do not edit them.

## Verify discovery

```bash
python3 scripts/install_runtime_views.py --project --codex --repo .
python3 scripts/verify_runtime_parity.py --project --codex --repo .
```

For optional personal discovery across projects:

```bash
python3 scripts/install_runtime_views.py --user --codex --repo .
python3 scripts/verify_runtime_parity.py --user --codex --repo .
```

The project view is preferred because it pins the task to the checkout being
edited. Use the user view only when one canonical checkout is intentionally
shared across projects.

## Start and hand off

Run `python3 scripts/ewf.py doctor`, then read `RESEARCH_PROTOCOL.md`, the
active project configuration, current status, relevant Evidence card, and the
tail of `decision-log.md`. A method facade improves automatic discovery but
cannot select an unapproved design or skip Stage 6a.

Before handing the project to Claude Code, finish the current atomic task and
write the durable handoff. Codex task context, terminal history, and local
interaction preferences are not research artifacts.

Browser sessions, remote compute, document helpers, and notifications remain
profile-controlled optional capabilities. Report a missing capability and use
an authorized alternative; do not embed a local executable or personal path in
a shared skill.
