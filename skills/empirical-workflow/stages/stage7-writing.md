# Stage 7: Paper Writing and Review

## Inputs

- Router prerequisites, completed analysis artifacts, Checkpoint records,
  Evidence cards, decision-log tail, and current status.
- Verified bibliography and literature map, selected target-outlet row from
  `references/outlet-positioning.md`, and all current tables, figures, and
  audit records.
- When the journal format adapter is applied, and not before:
  `references/latex-manuscript-adapter.md` and the target outlet's class
  files.

## Automatic actions

- A gate that fired records what was actually done about it.
  `compensation_disposition` takes `taken`, `carried`, `deferred` or
  `not_required`, and `deferred` on a STOP gate blocks at Checkpoint C. Naming
  the right remedy in a compensation record reads, in prose, like completed
  work; it is not. If the remedy is a sensitivity analysis, run a version of it
  and report the bounds, or say in the disposition field that it is outstanding.
- Read `references/writing-standards.md` first. Six to eight sections; no em
  dash, no contraction, no possessive on a named thing, no cross-reference
  parked in parentheses. Policy text, prices, dates, company statements and
  public datasets are footnotes with links, not reference-list entries.
- Keep one central contribution visible in the abstract, introduction, section
  openings, and conclusion. Use the Stage 3 paper story as the argument map; if
  final evidence narrows the claim, record a decision and propagate the
  narrowing before revising prose.
- Make each main exhibit answer a stated reader question. Begin each paragraph
  with its proposition, advance only that proposition, and report the estimate
  before interpreting it.
- Write in evidence-first order: theory, data, results, robustness, discussion
  and limitations, then introduction and conclusion. The last-written
  introduction summarizes observed results rather than constraining them.
- Render economics-style **three-line** tables: coefficients, parenthesized
  standard errors, notation defined in self-contained notes, fixed effects,
  clustering and cluster count, N, dependent-variable mean where useful, and
  a specification ladder for main results. Put required identification
  diagnostics in the main paper.
- Maintain a claim-to-evidence audit. Every abstract, introduction, result,
  mechanism, and contribution claim names its table/figure, Evidence card,
  estimate record, identifying assumption, and limitation. Distinguish
  descriptive, causal, structural, and exploratory claims.
- Draft from the v2.2 assertion registry. At every substantive manuscript use,
  register `assertion_type`, `declared_tier`, `qualifier_scope`,
  `counterevidence_prominence`, `underlying_precision`, `scope_declaration`,
  `power_basis`, `upgrade_justification`, `alternative_explanation`, and
  `as_modeled`. Apply T0--T4 only to `world` assertions; keep negative,
  methodological, discriminating, model-internal, and hypothesis sites
  untiered. Record `alternative_explanation` only for discriminating sites and
  `as_modeled: true` only for model-internal sites; each field is `null` or
  absent for every other assertion type.
- Run the writing-strength validator on registered assertion sites only. Use
  project-extensible causal, scope-qualifying, associational, descriptive, and
  framing semantic classes; do not turn the check into a manuscript-wide
  banned-word scan. A positive `overclaim_residual` blocks and a negative
  residual is INFO. Low lexical strength on a discriminating assertion is
  neutral.
- Enforce narrowing propagation to title, abstract, and conclusion; disclose
  identifying-assumption counterevidence in a separate contrastive sentence
  in the main text. Treat immediate recovery and a missing abstract/title
  `upgrade_justification` trace as WARN, not blockers. A dedicated limitations
  section does not replace disclosure beside the affected claim.
- Compare `declared_tier` only among `world` sites for upgrade traces; untiered
  sites are excluded. Keep lexical drift in declaration/residual strength
  enforcement, and do not let a trace waive propagation or another blocker.
- Verify every citation's bibliographic facts, stable source, and purpose label
  before it supports text. Match the outlet framing to the verified
  theory-source, empirical-analogue, and method-authority roles.
- Run `bibliography-audit` on the cited bibliography before release. Treat metadata verification
  and claim support as separate checks: a valid record does not prove that the cited sentence is
  supported by the version actually read.
- Run the selected review ladder: internal consistency, full review, referee
  simulation, then an independent-runtime identification review before
  submission. Record CLEAR, CONDITIONAL, or HOLD, findings, and resolution in
  the review record and decision log.
- Route a focused adversarial panel through `research-council`, a complete manuscript through
  `manuscript-review`, a decision letter through `referee-response`, and the final reproducibility
  archive through `replication-release`. Store their outputs as governed records, not chat-only state.

- When the journal format adapter is applied, bind each assertion site to its
  sentence with a marker that changes no typeset output, generate the
  reported-figure macros from the registry rather than typing numerals, and
  build only after the submission export gate passes. See
  `references/latex-manuscript-adapter.md`.

## Required artifacts

- Versioned manuscript and source, journal-format adapter output only after
  scientific content is stable, and a table/figure inventory with source paths.
- `docs/claim_to_evidence_audit.md` (or versioned equivalent) with columns:

  | Claim and location | Claim type | Table/figure and column | Evidence card | Assumption or scope | Limitation | Audit status |
  |---|---|---|---|---|---|---|

  Generate this audit from the claim and assertion registry rather than
  maintaining a second source of truth, and retain validator BLOCK, WARN, and
  INFO results with their assertion-site anchors.

- `docs/paper_story.md` updated with final claim scope and a completed
  revision-diagnostics audit from `references/elite-is-paper-standards.md`.
- Citation-verification record, selected outlet-positioning record, review
  requests and findings, revision log, submission checks, relevant Evidence
  cards, decision-log entries, and updated status.
- A response matrix with each claimed manuscript location independently pin-verified, and a release
  checklist recording current journal policy, confidentiality disposition, safety scans, manifest,
  source revision, and archive checksum when those operations apply.
- `docs/checkpoints/checkpoint_c.md` with the final validator command, zero
  blocking findings, review disposition, delivery evidence, and recorded
  proceed, revise, or pause decision.

## Red lines

- Do not write a claim whose claim-to-evidence row is incomplete, conceal
  failed diagnostics or robustness dispositions, or report a causal claim
  broader than its identifying assumption and interference/selection scope.
- Do not circulate an output with a positive `overclaim_residual`, an
  unpropagated `bounded_by_*` narrowing, or identifying-assumption
  counterevidence buried below the required prominence.
- Do not use unverified citations, reformat tables in ways that change
  estimates, or allow a target outlet to determine the empirical conclusion.
- A HOLD from independent-runtime identification review blocks circulation or
  submission until resolved. External circulation or submission requires the
  protocol-required recorded decision.

## Exit condition

Checkpoint C has zero blocking findings. The manuscript has complete three-line economics tables, verified citations,
and a claim-to-evidence audit in which each substantive claim traces to a
recorded result and limitation. Independent-runtime identification review is
CLEAR or CONDITIONAL with tracked resolution; no unresolved HOLD remains; and
the publication decision and remaining limitations are documented.

## 7 operating sequence

1. Assemble evidence-backed sections and tables before drafting the
   introduction and conclusion.
2. Complete the claim-to-evidence and citation-verification audits, including
   every number in the abstract and introduction.
3. Run review at the required depth; give the independent runtime the
   identification memo, diagnostic evidence, Evidence cards, and relevant
   manuscript section rather than an executor summary.
4. Resolve findings, verify cross-references and table order, then apply the
   outlet formatting adapter and assemble the delivery tree.
5. Run Checkpoint C, record its blocking count and review disposition, and only
   then document release readiness. External circulation or submission still
   requires the separately recorded authority decision.
