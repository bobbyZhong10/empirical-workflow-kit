# Setup and usage

[Documentation index](README.md) · [Project home](../README.md)

Run commands from the kit checkout unless a step explicitly changes directories.

## Install the kit checkout

Clone the repository and install the Python dependencies before running the
management commands (Python 3.11 or newer):

```bash
git clone https://github.com/bobbyZhong10/empirical-workflow-kit.git
cd empirical-workflow-kit
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/install_runtime_views.py --project --all --repo .
.venv/bin/python scripts/verify_runtime_parity.py --project --all --repo .
```

The committed project views normally make the installation command a no-op.
It is useful after an archive tool or file transfer has stripped symlinks.
Claude Code discovers `.claude/skills/empirical-workflow`; Codex discovers
`.agents/skills/empirical-workflow`. Both paths resolve to the same canonical
directory.

To repair only one runtime:

```bash
.venv/bin/python scripts/install_runtime_views.py --project --claude --repo .
.venv/bin/python scripts/install_runtime_views.py --project --codex --repo .
```

The installer does not overwrite a regular file or directory. If a previous
Empirical Workflow Kit copy must be replaced, use `--replace-managed`; the
installer first moves it to a timestamped sibling backup. A directory that
does not carry this kit's ownership markers is reported as `UNMANAGED` and is
left untouched.

## Optional user-level discovery

Project-level discovery is the recommended setup because it pins each project
to its checkout. To expose this checkout in every project on the machine:

```bash
.venv/bin/python scripts/install_runtime_views.py --user --all --repo .
.venv/bin/python scripts/verify_runtime_parity.py --user --all --repo .
```

User-level links are absolute links to the selected canonical checkout. Run
the installer again with `--replace-managed` after moving the checkout. The
installer changes only names listed in `workflow.manifest.yaml` and refuses to
replace another package that happens to use the same skill name.

Claude Code gives a personal skill priority over a project skill with the same
name. A pre-existing regular directory under `~/.claude/skills` can therefore
hide this repository's project view. Run the user-level parity check when a
runtime appears to use old instructions. If the installer reports `UNMANAGED`,
archive or rename that third-party skill only after confirming its ownership;
the installer will not make that decision for you. See the
[Claude Code skill-scope documentation](https://code.claude.com/docs/en/skills#resolve-skills-that-share-a-name).

Do not install by copying `skills/*` separately into `~/.claude/skills` and
`~/.agents/skills`. Independent copies are the split-brain condition this
repository prevents.

## Attach an existing research project

Keep the project's current data, code, results, and instructions in place. From
the kit checkout, attach the canonical workflow to that project:

```bash
.venv/bin/python scripts/bootstrap_project.py /absolute/path/to/research-project --claude
```

Use `--all` when both Claude Code and Codex will work in the project. The
bootstrapper performs a collision preflight before writing, preserves an
existing `research.yaml`, and appends a bounded workflow adapter to an existing
`CLAUDE.md` or `AGENTS.md`. It creates project-owned protocol, status, decision,
evidence, profile, and manifest files. Runtime discovery links remain relative
and resolve through the ignored local `.workflow/kit` binding, so both runtimes
execute this checkout's one canonical skill tree rather than copied prompts.

Then enter the research project, complete `research.yaml`, and diagnose it:

```bash
cd /absolute/path/to/research-project
.workflow/bin/ewf doctor
```

The bootstrap also creates `WORKFLOW_START.md`, a relative link to the kit's
canonical startup prompts. Commit the link with the project; it gives Claude
Code and Codex the same entry instructions without copying a prompt into both
runtime adapters.

On another machine, check out the project's recorded kit version and rerun the
same bootstrap command to recreate the ignored local binding. Commit the project
records and runtime-view links, but never commit `.workflow/kit` itself.

## Start a research project

1. For work inside the kit checkout, copy `research.example.yaml` to
   `research.yaml`. For an external existing project, use the bootstrap command
   above. Fill in the observation unit, designs, authority, languages, and
   analysis-input contract.
2. Inside the kit checkout, copy `runtime-profile.example.yaml` to
   `runtime-profile.yaml`; the external bootstrapper creates the corresponding
   file automatically. Enter machine-specific paths and optional tool
   availability. Never embed personal paths in a skill, prompt, adapter, or
   protocol.
3. Resolve and diagnose that profile:

   ```bash
   .venv/bin/python scripts/ewf.py env
   .venv/bin/python scripts/ewf.py doctor
   ```

4. For an attached project, use the generated state files. For work directly in
   a dedicated kit checkout, initialize project state from the templates without
   overwriting existing records. The kit's own maintenance status and decision
   log are not a new research project's state.
5. Start Claude Code or Codex at the repository root. The runtime adapter reads
   the same protocol, manifest, router, and project state.

## Start or resume a workflow

Open `WORKFLOW_START.md` in an attached external project. When working directly
inside the kit checkout, open the manifest-named canonical file at
`skills/empirical-workflow/references/start-prompts.md`. Copy one prompt, fill
only its short project-specific header, and send it to Claude Code or Codex.

### New project or automatic completion

Use `AUTONOMOUS_WITH_RED_LINES` when starting a new project or asking the
workflow to carry an existing project through all remaining stages. For an
existing data project, set the priority explicitly, for example:

```text
Objective: Reproduce and verify the existing data work, then complete the
literature review, theory development, analysis, manuscript, and internal review.
Starting point: The project already contains substantially complete data work.
Priority: Reproduce the data pipeline before relying on any existing result.
Constraints: Preserve existing data, code, results, project instructions, and
user-authored README content.
```

This is the highest-autonomy mode: routine reversible work continues without
step-by-step approval, while mandatory pauses and external-action authority
remain binding.

### Take over work already in progress

Use `TAKEOVER_AND_RESUME` after a Claude/Codex handoff, context compaction,
interruption, or partial run. Point it at the latest handoff when one exists.
The runtime reconstructs state from the protocol, project configuration,
status, current evidence, and decision log, validates that record against the
actual files, and resumes from the first unverified atomic task. It does not
create a fresh project state or blindly rerun completed work.

The two modes change only how work begins and resumes. They use the same stages,
evidence records, checkpoints, language policy, R-first rule, and mandatory
pauses. Switching between Claude Code and Codex therefore does not require a
different prompt or a separate project version.

Run configured commands through the logical tool runner so the profile affects
execution rather than documentation alone:

```bash
.venv/bin/python scripts/ewf.py run rscript --vanilla analysis.R
.venv/bin/python scripts/ewf.py run quarto render talk.qmd
.venv/bin/python scripts/ewf.py run node presentation-tooling/deck-check.mjs fit talk.html
```

See `docs/runtime-recipes/` for Claude Code and Codex discovery, handoff,
browser, document, secret, and optional-capability guidance.

At every cross-runtime handoff, the receiver reads, in order:

1. `RESEARCH_PROTOCOL.md`
2. `research.yaml`
3. `_status.md`
4. the most relevant current evidence card
5. the tail of `decision-log.md`

The sender records the completed stage, changed artifacts, checks run, open
risks, next action, and unresolved pause.

