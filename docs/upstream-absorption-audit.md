# Upstream absorption audit

## Audit identity

- Upstream repository: `https://github.com/ericluo04/claude-academic-workflow`
- Baseline commit: `8958cc246e65cdf7c36604f397a1c1719b7e2c14`
- Re-inspected commit: `8958cc246e65cdf7c36604f397a1c1719b7e2c14`
- Re-inspected on: 2026-09-02
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
| `skills/reading-papers/` | `skills/research-sources/` | `SKILL.md`, `REFERENCE.md`, and `paper.py` absorbed; the personal Zotero launcher was replaced by runtime-profile configuration |
| `skills/litreview/SKILL.md` | `skills/literature-review/SKILL.md` | Topic discovery, ranking, deduplication, access honesty, and synthesis prompt absorbed |
| `skills/bibcheck/SKILL.md` | `skills/bibliography-audit/SKILL.md` | Entry-level canonical-metadata audit and corrected-copy workflow absorbed |
| `skills/council/SKILL.md` | `skills/research-council/SKILL.md` | Independent critic fanout and non-voting synthesis absorbed |
| `skills/review-paper/SKILL.md` | `skills/manuscript-review/SKILL.md` | Multi-role manuscript review and severity triage absorbed |
| `skills/referee-response/SKILL.md` | `skills/referee-response/SKILL.md` | Location verification, response drafting, and stress-test prompt absorbed |
| `skills/replication-package/` | `skills/replication-release/` | Skill and all four scanners absorbed, with stronger release authority gates |
| `skills/compile-latex/` | `skills/latex-production/` | Compile diagnostics, log patterns, and rendered-figure loop absorbed |
| `skills/preregister/SKILL.md` | `skills/preregister/SKILL.md` | Registry-specific fields, MUST/SHOULD/MAY prompts, and retrospective-refusal gate absorbed |
| `skills/course-site/SKILL.md` | `skills/course-site/SKILL.md` | Site/deck boundary, Quarto structure, and publication workflow absorbed |
| `skills/research-talk/` | `skills/research-talk/` | Skill, starter template, four references, and house-style file absorbed |
| `skills/teaching-lecture/` | `skills/teaching-lecture/` | Skill, starter template, five references, and house-style file absorbed |
| `skills/slide-review/` | `skills/slide-review/` | Skill, three references, two scripts, and house-style file absorbed |
| `skills/causal-design/` | `methods/causal-design/` plus `methods/selection-on-observables/` | Operational skill became `prompt.md`; canon, details, shared rules, bibliography, and R template were preserved and split at the design boundary |
| `skills/did/` | `methods/did/` | Operational skill became `prompt.md`; canon, details, and R template absorbed |
| `skills/iv/` | `methods/iv/` | Operational skill became `prompt.md`; canon, details, and R template absorbed |
| `skills/rdd/` | `methods/rdd/` | Operational skill became `prompt.md`; canon, details, and R template absorbed |
| `skills/synthetic-control/` | `methods/synthetic-control/` | Operational skill became `prompt.md`; canon, details, and R template absorbed |
| `skills/field-experiment/` | `methods/field-experiment/` | Operational skill became `prompt.md`; canon, details, and R template absorbed |
| `skills/conjoint/` | `methods/conjoint/` | Operational skill became `prompt.md`; canon, details, and R template absorbed |

`methods/fixed-effects/` is a local focused pack added for the workflow's associational panel
branch. It does not replace an upstream source.

## Tooling and non-skill files

| Upstream family | Canonical destination | Disposition |
|---|---|---|
| `agents/tikz-reviewer.md` | `agents/tikz-reviewer.md` and `.claude/agents/` view | Absorbed; one canonical agent file |
| `slide-tooling/` (151 files) | `presentation-tooling/` | Scripts, Quarto extension, theme, fonts, MathJax, and licenses absorbed |
| `SETUP.md` | README, `runtime-profile.example.yaml`, and skill prerequisites | Decomposed; personal paths and secrets were converted to explicit configuration |
| `ATTRIBUTION.md` and `LICENSE` | `THIRD_PARTY_NOTICES.md`, `docs/upstream-attribution.md`, and repository license | Attribution and license obligations retained |
| `README.md` | repository README and this audit | Capability descriptions, warnings, prerequisites, and architecture absorbed where applicable |
| `.gitignore` | repository `.gitignore` | Relevant generated, cache, environment, and worktree exclusions absorbed |
| `examples/` (five files) | No canonical implementation | Inspected as demonstrations; not copied because they are generated examples rather than reusable instructions |
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
