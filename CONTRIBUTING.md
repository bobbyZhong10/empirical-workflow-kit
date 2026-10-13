# Contributing

Please keep changes focused on a concrete research-workflow problem, software
error, or documentation gap. Describe the triggering case, intended behavior,
and evidence that the change works.

## Before changing files

Read [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) and the applicable runtime
adapter, [AGENTS.md](AGENTS.md) or [CLAUDE.md](CLAUDE.md). Resolve canonical paths
from [workflow.manifest.yaml](workflow.manifest.yaml).

Edit skills under `skills/`; `.claude/skills/` and `.agents/skills/` are linked
discovery views. Preserve the shared runtime contract and use the manifest-named
installer to repair views. Do not introduce runtime-specific prompt copies.

## Verification

Follow the [development guide](docs/development.md) to prepare dependencies.
Run checks appropriate to the affected behavior, then include commands and
results in the pull request. For contract or documentation changes, start with:

```bash
bash tests/run_contract_tests.sh
.venv/bin/python scripts/verify_runtime_parity.py --project --all --repo .
git diff --check
```

Validator, bootstrap, analysis, and presentation changes also need their
relevant tests or smoke checks. State which checks were not run and why.
Research Checkpoints B/C validate project registries; they are not a substitute
for testing a kit-maintenance change.

Keep decisions and evidence in the existing maintenance records as required by
the protocol. Update affected user instructions when commands or dependencies
change. Preserve source attribution and bundled license notices.

## Bug reports and public examples

Include the kit version (`tools/validate_registry --version`), runtime, command,
expected behavior, actual behavior, and a minimal reproducible example. Use
synthetic data where possible. Remove credentials, personal paths, confidential
manuscript text, and restricted data from reports, logs, and attachments.

Do not add local reading copies, journal downloads, machine-specific profiles,
or generated caches to a pull request. A file being available locally does not
establish permission to publish it. See [.gitignore](.gitignore) and
[Third-Party Notices](THIRD_PARTY_NOTICES.md).
