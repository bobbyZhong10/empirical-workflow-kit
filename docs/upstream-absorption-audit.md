# Upstream absorption audit

## Audit identity

- Upstream repository: `https://github.com/ericluo04/claude-academic-workflow`
- Baseline commit: `8958cc246e65cdf7c36604f397a1c1719b7e2c14`
- Re-inspected commit: `8958cc246e65cdf7c36604f397a1c1719b7e2c14`
- Re-inspected on: 2026-09-03
- Result: upstream `main` had not changed since the baseline absorption.

The upstream commit contains 669 tracked files: 70 skill files, 151 shared slide-tooling files,
435 generated site files, five example-deck files, one agent, one output style, and six other
root files. This audit treats generated sites and examples as demonstrations, not independent
workflow instructions. Every source-bearing family is mapped below.

## Global instruction decomposition

The upstream `CLAUDE.md` is not installed as a competing runtime-specific contract. Its contents
were split by responsibility so Claude Code and Codex receive the same research behavior.

| Upstream section | Canonical destination | Disposition |
|---|---|---|
| Voice for documents, emails, code, and reports | `skills/empirical-workflow/references/research-writing.md` and operation-specific writing rules | Absorbed as durable prose, claim, limitation, quotation, and direct-language rules |
| Working style: work-value test and object inspection | `RESEARCH_PROTOCOL.md` and `references/execution-discipline.md` | Absorbed as workflow-wide execution rules |
| Working style: parallel work and critic topology | `research-council`, `manuscript-review`, and focused operation prompts | Absorbed where independent review is substantively required; not imposed as a runtime-specific blanket rule |
| Working style: destructive actions and verification | `RESEARCH_PROTOCOL.md`, `references/execution-discipline.md`, and release skills | Absorbed with explicit authority and evidence requirements |
| Working style: method selection | `references/method-governance.md` and method packs | Absorbed as literature-first method governance |
| Working style: code review | `references/code-review.md` | Absorbed as a focused review taxonomy |
| Working style: browser, paths, and local tools | `runtime-profile.example.yaml` | Converted from personal paths to portable capabilities |
| Research decisions | stage contracts, `method-governance.md`, and source skills | Absorbed into the relevant decision points |
| Research prose | `RESEARCH_PROTOCOL.md` and `research-writing.md` | Absorbed with evidence and effect-size requirements |
| Compact instructions | status, evidence, decision-log, and handoff templates | Replaced by durable cross-runtime state rather than transcript-dependent recovery |

The upstream output style controls Claude's chat presentation and does not reach other runtimes.
Its portable outcomes (answer-first reporting, concise verification, explicit open decisions) are
represented in the adapters and handoff contract. Product-specific UI commands and banned-word
preferences were not made research-validity rules.

## Skill and prompt mapping

| Upstream source | Canonical destination | Files accounted for |
|---|---|---|
| `skills/reading-papers/` | `skills/reading-papers/` facade → `skills/research-sources/` | Upstream name remains directly discoverable; `SKILL.md`, `REFERENCE.md`, and `paper.py` are owned by the canonical target, and the personal Zotero launcher was replaced by runtime-profile configuration |
| `skills/litreview/SKILL.md` | `skills/litreview/` facade → `skills/literature-review/` | Upstream name remains directly discoverable; topic discovery, ranking, deduplication, access honesty, and synthesis prompt are owned by the canonical target |
| `skills/bibcheck/SKILL.md` | `skills/bibcheck/` facade → `skills/bibliography-audit/` | Upstream name remains directly discoverable; entry-level canonical-metadata audit and corrected-copy workflow are owned by the canonical target |
| `skills/council/SKILL.md` | `skills/council/` facade → `skills/research-council/` | Upstream name remains directly discoverable; independent critic fanout and non-voting synthesis are owned by the canonical target |
| `skills/review-paper/SKILL.md` | `skills/review-paper/` facade → `skills/manuscript-review/` | Upstream name remains directly discoverable; multi-role manuscript review and severity triage are owned by the canonical target |
| `skills/referee-response/SKILL.md` | `skills/referee-response/SKILL.md` | Location verification, response drafting, and stress-test prompt absorbed |
| `skills/replication-package/` | `skills/replication-package/` facade → `skills/replication-release/` | Upstream name remains directly discoverable; the canonical target owns the skill and all four scanners, with stronger release authority gates |
| `skills/compile-latex/` | `skills/compile-latex/` facade → `skills/latex-production/` | Upstream name remains directly discoverable; the canonical target owns compile diagnostics, log patterns, and the rendered-figure loop |
| `skills/preregister/SKILL.md` | `skills/preregister/SKILL.md` | Registry-specific fields, MUST/SHOULD/MAY prompts, and retrospective-refusal gate absorbed |
| `skills/course-site/SKILL.md` | `skills/course-site/SKILL.md` | Site/deck boundary, Quarto structure, and publication workflow absorbed |
| `skills/research-talk/` | `skills/research-talk/` | Skill, starter template, four references, and house-style file absorbed |
| `skills/teaching-lecture/` | `skills/teaching-lecture/` | Skill, starter template, five references, and house-style file absorbed |
| `skills/slide-review/` | `skills/slide-review/` | Skill, three references, two scripts, and house-style file absorbed |
| `skills/causal-design/` | `skills/causal-design/` facade plus `methods/causal-design/` and `methods/selection-on-observables/` | Operational skill became the canonical `prompt.md`; thin discovery facades route both runtimes to the split design packs |
| `skills/did/` | `skills/did/` facade plus `methods/did/` | Operational skill became `prompt.md`; canon, details, R template, freshness metadata, and direct discovery retained |
| `skills/iv/` | `skills/iv/` facade plus `methods/iv/` | Operational skill became `prompt.md`; canon, details, R template, freshness metadata, and direct discovery retained |
| `skills/rdd/` | `skills/rdd/` facade plus `methods/rdd/` | Operational skill became `prompt.md`; canon, details, R template, freshness metadata, and direct discovery retained |
| `skills/synthetic-control/` | `skills/synthetic-control/` facade plus `methods/synthetic-control/` | Operational skill became `prompt.md`; canon, details, R template, freshness metadata, and direct discovery retained |
| `skills/field-experiment/` | `skills/field-experiment/` facade plus `methods/field-experiment/` | Operational skill became `prompt.md`; canon, details, R template, freshness metadata, and direct discovery retained |
| `skills/conjoint/` | `skills/conjoint/` facade plus `methods/conjoint/` | Operational skill became `prompt.md`; canon, details, R template, freshness metadata, and direct discovery retained |

`methods/fixed-effects/` is a local focused pack added for the workflow's associational panel
branch. It does not replace an upstream source.

All 20 upstream skill names are now runtime-discoverable. Seven renamed capabilities use thin,
manifest-declared compatibility facades; the facades preserve upstream trigger vocabulary while
the canonical targets remain the only owners of substantive prompts and supporting files.

## Tooling and non-skill files

| Upstream family | Canonical destination | Disposition |
|---|---|---|
| `agents/tikz-reviewer.md` | `agents/tikz-reviewer.md` and `.claude/agents/` view | Absorbed; one canonical agent file |
| `slide-tooling/` (151 files) | `presentation-tooling/` | Scripts, Quarto extension, theme, fonts, MathJax, and licenses absorbed |
| `SETUP.md` | README, `runtime-profile.example.yaml`, `scripts/ewf.py`, and runtime recipes | Decomposed; personal paths and secrets became executable, diagnosable capabilities |
| `ATTRIBUTION.md` and `LICENSE` | `THIRD_PARTY_NOTICES.md` and `docs/upstream-attribution.md` | Attribution and license obligations retained in the embedded notice and detailed lineage |
| `README.md` | repository README and this audit | Capability descriptions, warnings, prerequisites, and architecture absorbed where applicable |
| `.gitignore` | repository `.gitignore` | Relevant generated, cache, environment, and worktree exclusions absorbed |
| `examples/` (five files) | `examples/` and `tests/smoke/run_presentation_smoke.sh` | Replaced with two neutral, compact acceptance fixtures rather than copying personal example content or generated output |
| `docs/` (435 files) | No canonical implementation | Inspected as rendered examples and GitHub Pages output; reusable fonts and tooling already live in `presentation-tooling/` |
| `output-styles/concise-research.md` | Runtime adapters and handoff/reporting rules | Portable outcomes absorbed; Claude-only presentation settings remain user preference |

## Deliberate portability changes

The upstream quickstart creates independent copies under `~/.claude`. This kit replaces that
installation model with one canonical `skills/` tree and manifest-controlled runtime views. The
upstream Zotero launcher hard-codes `~/.claude/secrets/scholar.env` and a personal executable
location; the same capability is represented through `runtime-profile.yaml` and optional tool
discovery. Generated example sites are excluded because they add no research rule and would create
a second copy of the vendored presentation assets.

Because Claude Code gives a same-named personal skill priority over a project skill, the parity
tool also audits optional user-level views. It reports a regular copy as a duplicate implementation
and the installer refuses to replace an unowned collision.

These changes preserve the mature prompts and method content while removing Claude-only storage,
personal paths, duplicate implementations, and generated demonstration output from the portable
contract.

## Repeatable update audit

`upstream.lock.yaml` records the baseline Git object ID, disposition, and local destinations for
every source-bearing upstream family. `scripts/audit_upstream.py --offline` validates the local
mapping without network access. The default online run clones the current upstream ref and reports
source objects as `UNCHANGED`, `CHANGED`, `SOURCE_MISSING`, or `LOCK_MISMATCH`; use
`--fail-on-change` when any unreviewed upstream change must fail automation. The lock preserves the
upstream mirror's genericization discipline while making future re-inspection incremental.
