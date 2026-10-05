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
- Read `references/research-writing.md` first for question-led organization,
  economic meaning, contribution, and behavioral boundaries; then read
  `references/writing-standards.md` for style. Its editorial defaults are six
  to eight sections; no em dash, no contraction, no possessive on a named thing, no cross-reference
  parked in parentheses. Policy text, prices, dates, company statements and
  public datasets are footnotes with links, not reference-list entries.
- Develop one central contribution through the abstract, introduction, evidence,
  and conclusion; do not repeat a contribution sentence in every section. Use the
  Stage 3 paper story as the argument map; if
  final evidence narrows the claim, record a decision and propagate the
  narrowing before revising prose.
- Make each main exhibit answer a stated reader question. Begin each paragraph
  with its proposition, advance only that proposition, and report the estimate
  before interpreting it.
- Draft from the evidence and revise the introduction to match it. Arrange the
  final paper by the questions a reader needs answered, not workflow stages or
  estimator order. Theory, mechanisms, robustness and implications earn space
  by supporting the argument; do not impose a section for each on every paper.
- Render economics-style **three-line** tables: coefficients, parenthesized
  standard errors, notation defined in self-contained notes, fixed effects,
  clustering and cluster count, N, dependent-variable mean where useful, and
  a specification ladder for main results. Put diagnostics needed to assess the
  main claim in the paper; the full audit history stays internal.
- Maintain a claim-to-evidence audit. Internally, every material abstract,
  introduction, result,
  mechanism, and contribution claim links to its table/figure, Evidence card,
  result or derivation record, assumptions, and limitations as applicable. Distinguish
  descriptive, causal, structural, and exploratory claims.
- Draft from the economic question, argument, and evidence. Use the assertion
  registry as internal traceability, not the manuscript outline. Apply
  `references/research-writing.md` to exact propositions and their assumptions;
  `references/writing-under-the-registry.md` explains the schema and advisory
  checks. Prediction counts, gate language, unused-method defenses, and routine
  repair history stay internal. Keep only reader-useful numbers in prose.
- Treat lexical residuals and disclosure-pattern checks as review prompts, not
  semantic verdicts. Correct an overreaching inference instead of adding a
  stock hedge. Propagate real narrowing to standalone summaries; explain each
  material limitation where it matters without repeating a disclaimer.
- Reconcile main results, figures, dynamics, sensitivities, and magnitude
  conversions using the estimand crosswalk in `references/robustness-checklists.md`.
  Do not use a related target's sensitivity result to certify the main target.
- Before repairing material review comments, adjudicate them against original
  outputs and the reviewed manuscript version. For each revision, name the
  reader judgment it should change and classify the root cause using
  `references/operational-quality-loop.md`; repair it and inspect new repetition,
  unnecessary numbers, claim drift, and length inflation. Check the current
  paper story's advisor requirements, withdrawals, variable meanings, and open
  questions. Stop homogeneous revisions once material issues are resolved.
- After the first complete draft, obtain an independent cold read of the actual
  manuscript version, before
  supplying the author story, registry, or executor summary. Ask the reader to
  identify the actors, their choices/objectives and economic conflict, then
  explain the economic question, main finding, contribution relative to prior
  work, and evidence boundary in their own words, with unclear passages. If
  these cannot be answered, reconsider question selection, evidence organization,
  or the contribution itself. More titles, discipline labels, and contribution
  sentences are not a remedy. Record the version and review independence; a
  self-review must be labeled and cannot be claimed as independent.
- Verify every citation's bibliographic facts, stable source, and purpose label
  before it supports text. Match the outlet framing to the verified
  theory-source, empirical-analogue, and method-authority roles.
- Run `bibliography-audit` on the cited bibliography before release. Treat metadata verification
  and claim support as separate checks: a valid record does not prove that the cited sentence is
  supported by the version actually read.
- Select review depth for the unresolved risk: internal consistency, full
  review, or referee simulation as warranted, with independent-runtime evidence
  and identification review before submission. Do not repeat the full ladder
  after a local repair unless a new material issue warrants it. Record CLEAR,
  CONDITIONAL, or HOLD, findings, and resolution in
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
  requests and findings (including the cold read), revision decisions in the
  decision log, submission checks, relevant Evidence
  cards, decision-log entries, and updated status.
- A response matrix with each claimed manuscript location independently pin-verified, and a release
  checklist recording current journal policy, confidentiality disposition, safety scans, manifest,
  source revision, and archive checksum when those operations apply.
- `docs/checkpoints/checkpoint_c.md` with the final validator command, zero
  mechanical blocking findings, scoped review dispositions, delivery evidence, and recorded
  proceed, revise, or pause decision.

## Red lines

- Do not write a claim whose claim-to-evidence row is incomplete, conceal
  failed diagnostics or robustness dispositions, or report a causal claim
  broader than its identifying assumption and interference/selection scope.
- Do not circulate an output with an unresolved substantive overclaim,
  unpropagated narrowing, or material counterevidence hidden from readers.
  Lexical scores alone establish none of these; record the substantive review.
- Do not use unverified citations, reformat tables in ways that change
  estimates, or allow a target outlet to determine the empirical conclusion.
- A HOLD from independent-runtime identification review blocks circulation or
  submission until resolved. External circulation or submission requires the
  protocol-required recorded decision.

## Exit condition

Checkpoint C has zero mechanical blocking findings, and substantive and editorial
reviews support completion. Report reproducibility, claim credibility, discussion
readiness, and submission delivery separately; a discussion-ready draft is not a
submission certificate. The manuscript has complete three-line economics tables, verified citations,
and a claim-to-evidence audit in which each substantive claim traces to a
recorded result and limitation. Independent-runtime identification review is
CLEAR or CONDITIONAL with tracked resolution; no unresolved HOLD remains; and
the publication decision and remaining limitations are documented.

## 7 operating sequence

1. Assemble evidence-backed sections and tables before drafting the
   introduction and conclusion.
2. Complete the claim-to-evidence and citation-verification audits, including
   every number in the abstract and introduction.
3. Run the manuscript-only cold read, then review at the required depth; give the independent runtime the
   identification memo, diagnostic evidence, Evidence cards, and relevant
   manuscript section rather than an executor summary.
4. Adjudicate findings before selecting repairs; retain mistaken and partially
   confirmed comments with evidence. Resolve affected claims, verify cross-references and table order, then apply the
   outlet formatting adapter and assemble the delivery tree.
5. Run Checkpoint C, record its blocking count and review disposition, and only
   then document release readiness. External circulation or submission still
   requires the separately recorded authority decision.
