# Stage 7: Paper Writing and Review

## Inputs

- Router prerequisites, completed analysis artifacts, Checkpoint records,
  Evidence cards, decision-log tail, and current status.
- Verified bibliography and literature map, selected target-outlet row from
  `references/outlet-positioning.md`, and all current tables, figures, and
  audit records.

## Automatic actions

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
- Verify every citation's bibliographic facts, stable source, and purpose label
  before it supports text. Match the outlet framing to the verified
  theory-source, empirical-analogue, and method-authority roles.
- Run the selected review ladder: internal consistency, full review, referee
  simulation, then an independent-runtime identification review before
  submission. Record CLEAR, CONDITIONAL, or HOLD, findings, and resolution in
  the review record and decision log.

## Required artifacts

- Versioned manuscript and source, journal-format adapter output only after
  scientific content is stable, and a table/figure inventory with source paths.
- `docs/claim_to_evidence_audit.md` (or versioned equivalent) with columns:

  | Claim and location | Claim type | Table/figure and column | Evidence card | Assumption or scope | Limitation | Audit status |
  |---|---|---|---|---|---|---|

- Citation-verification record, selected outlet-positioning record, review
  requests and findings, revision log, submission checks, relevant Evidence
  cards, decision-log entries, and updated status.

## Red lines

- Do not write a claim whose claim-to-evidence row is incomplete, conceal
  failed diagnostics or robustness dispositions, or report a causal claim
  broader than its identifying assumption and interference/selection scope.
- Do not use unverified citations, reformat tables in ways that change
  estimates, or allow a target outlet to determine the empirical conclusion.
- A HOLD from independent-runtime identification review blocks circulation or
  submission until resolved. External circulation or submission requires the
  protocol-required recorded decision.

## Exit condition

The manuscript has complete three-line economics tables, verified citations,
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
4. Resolve findings, verify cross-references and table order, document the
   publication decision, then apply the outlet formatting adapter.
