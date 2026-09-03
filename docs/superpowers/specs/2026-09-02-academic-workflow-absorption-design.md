# Academic Workflow Absorption Design

## Status and source

Status: approved by the user on 2026-09-02.

This design absorbs the reusable research practices from Lan E. Luo's
`claude-academic-workflow` repository at commit
`8958cc246e65cdf7c36604f397a1c1719b7e2c14`. The source is MIT licensed.
Adapted code and substantial prompt structures retain attribution in
`THIRD_PARTY_NOTICES.md`.

## Objective

Extend Empirical Workflow Kit from a governed empirical-project protocol into
a governed protocol plus a set of executable research operations. Preserve its
cross-runtime state, checkpoints, Evidence cards, mandatory pauses, and
Python-to-R contract. Add source discovery, bibliography auditing,
method-specific causal prompts, preregistration, adversarial review, referee
response verification, replication release, LaTeX production, and research
presentation tooling.

## Architecture

The implementation has four layers.

1. `RESEARCH_PROTOCOL.md` retains portable governance and adds the durable
   rules that were previously embedded in a personal global `CLAUDE.md`.
2. `skills/empirical-workflow/` remains the stage router. Its stages route to
   focused references, templates, method packs, and companion skills.
3. Companion skills under `skills/` provide independently invocable
   operations. They do not own project state and must write outputs that the
   core protocol can register.
4. Deterministic scripts implement parsing, search, validation, safety scans,
   and rendering gates. Prompt text may guide judgment but may not replace a
   deterministic check that the kit can perform.

Runtime adapters remain short. Runtime-specific paths and tool availability
belong in `runtime-profile.example.yaml`, never in the portable protocol or a
method canon.

## Global instruction decomposition

The source global `CLAUDE.md` is absorbed by responsibility.

| Source responsibility | Destination |
|---|---|
| Document voice, direct prose, claim justification, effect interpretation, local limitations, paraphrase and quotation discipline | `skills/empirical-workflow/references/research-writing.md` |
| Work-value test, object inspection, verification, scoped changes, destructive-action boundaries, parallelism rules | `skills/empirical-workflow/references/execution-discipline.md` |
| Literature-grounded method choice, current-method scan, sweep/pilot decision rule, source-supplied boundary | `skills/empirical-workflow/references/method-governance.md` |
| Code-review tags and scope discipline | `skills/empirical-workflow/references/code-review.md` |
| Browser profiles, local helper paths, caches, scholarly APIs, Overleaf and presentation assets | `runtime-profile.example.yaml` and companion-skill setup sections |
| Context compaction requirements | Existing durable handoff order and a strengthened handoff template |
| Interactive answer formatting | Not imposed as research governance; only durable document-writing rules are portable |

Parallel agents are an optional execution topology. A runtime may use them only
when authorized and supported. The artifact contract and review roles must also
work with sequential independent runtimes.

## Claim governance and commitments

Implement the approved v2.1 claim-governance design and the corrections in the
v2.2 brief before accepting new operational outputs as publication evidence.
The implementation provides templates plus a deterministic validator for:

- pipeline authority, supersession, and first-formal-batch timestamps;
- claim revision availability and assessment;
- reported figures and machine or manual revalidation;
- acceptance-gate definitions and per-pipeline evaluations;
- applicability records and required substitutes;
- publication eligibility and mixed-pipeline rejection;
- declared cross-pipeline reconciliation blocks.

Preregistration records share the same claims and gate identifiers. They must
refuse retrospective registration after the focal outcome has been inspected
or the focal analysis has run. Every confirmatory hypothesis records a
falsification rule.

## Research-source operations

Create three companion skills.

- `research-sources`: resolve, search, retrieve, map sections, and record the
  version actually read. Its deterministic CLI merges Crossref, OpenAlex,
  Semantic Scholar, arXiv, Unpaywall, and recognized repository routes.
- `literature-review`: run multiple query variants, record source coverage,
  deduplicate candidates, score relevance, and create the Stage 2 literature
  artifacts.
- `bibliography-audit`: verify existing entries, keep metadata verification
  separate from claim-support verification, and write a corrected candidate
  without overwriting the source bibliography.

Every material reading record states `version_read`, `source_rung`, full-text
status, stable identifier, coverage failures, and whether the summary is based
on full text or an abstract. Abstract consistency is never sufficient for a
material `SUPPORTED` claim.

## Method packs

Create packs for causal-design routing, selection on observables, fixed
effects, DiD and event studies, IV, RDD, synthetic control, field experiments,
and conjoint experiments. Each pack contains the applicable subset of:

- `prompt.md`, the decision and execution prompt;
- `canon.md`, the read literature record;
- `details.md`, derivations, package behavior, and failure cases;
- `template.R`, a runnable reference implementation;
- `references.bib`, verified method references.

Every canon uses the fields `Role`, `Settles`, `Binds when`, `Implement`,
`Scope limits`, `Named disagreements`, `Excluded`, and `Verified through`.
Stage 6a reads only the selected method pack. A method pack may narrow or stop
an analysis; it may not silently change a locked specification, sample,
clustering level, estimand, or identifying strategy.

## Review and revision operations

Create independent companion skills for a research council, manuscript review,
and referee response.

Review findings use a common schema with lens, severity, exact location,
quoted evidence, affected claim, required action, disposition, and reviewer
runtime. Synthesis ranks findings by consequence, not vote count. One material
identification finding outranks several cosmetic findings.

Referee-response records retain each comment verbatim and classify it before
drafting. A response may claim a manuscript change only after the exact pin has
been read and verified. Missing changes remain unresolved and may not be
described as complete.

Use of generative tools on a third party's confidential manuscript requires a
documented policy and confidentiality check. Pre-submission review of the
user's own manuscript remains allowed.

## Replication release

Create a release skill that inventories code and data, maps exhibits to their
producing scripts, scans secrets and personal data, sanitizes paths on staged
copies, captures environments and randomness, handles restricted data, builds
a SHA-256 manifest, and produces a journal-oriented archive checklist.

Packaging follows successful reproduction in a clean or documented
environment. Packaging alone is never labeled reproducibility certification.
Outlet rules are dated policy snapshots and must be checked against official
sources before external submission.

## Publication and presentation tooling

Create companion skills for LaTeX production, research talks, teaching
lectures, slide review, and course sites. Shared Quarto and browser-based gates
live under `presentation-tooling/`. The portable skill resolves tool paths from
the runtime profile. Render success does not imply visual readiness; fit,
staging, missing-resource, citation, and offline requirements have separate
verdicts.

## Testing and portability

All new deterministic Python behavior follows red-green TDD. Contract tests
verify routing, required files, attribution, absence of personal hard-coded
paths, method-pack completeness, and protocol integration. Python unit tests
cover source identity normalization and release scanners. R templates must
parse without executing unavailable packages. JavaScript tooling must pass
`node --check`.

The implementation does not copy generated example decks or rendered website
output. It imports the prompts, reference assets, scripts, and source templates
needed to generate and validate them.
