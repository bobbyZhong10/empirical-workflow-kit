# Stage 7: Paper Writing and Review

Goal: a draft whose claims match its results. The writing order is the
mechanism that enforces this.

## Inputs

The completed analysis artifacts, checkpoint records, Evidence cards,
decision-log tail, target-outlet requirements, and current status.

## Automatic actions

Assemble the draft in the prescribed order, trace each claim to evidence, and
run the selected independent review ladder.

## Required artifacts

The versioned draft, claim-to-evidence trace, review records, revision log,
submission checks, relevant Evidence cards, and updated status.

## Red lines

Do not write claims unsupported by recorded evidence, conceal failed checks, or
submit or circulate externally without the protocol-required recorded decision.

## Exit condition

The draft, traceability record, required reviews, and publication decision are
complete, with remaining limitations and post-review actions documented.

## 7.1 Mandatory writing order

Phase 1: Sections 2 to 6. Theory, then data, then results, then robustness.
Phase 2: Section 7, discussion and limitations.
Phase 3: Introduction and conclusion, written last.

The introduction is written last because a hook written first becomes a
constraint that the results are then bent to satisfy. Written last, the
contribution claim is a summary of what was found rather than a promise the
paper must keep.

Write in full paragraphs. Bullet lists do not belong in the body of a journal
submission.

## 7.2 Section conventions

- Data section: reuse the caveats from Stage 1.5 and the attrition table from
  Stage 4.3 rather than rewriting them from memory.
- Results section: describe what the table shows and what it means in
  substantive units. Do not restate coefficients that the reader can see.
- Robustness section: report failures. A robustness section in which everything
  passes reads as a robustness section in which nothing was tried.
- Limitations: name the binding limitation. Decorative limitations that no
  referee would raise weaken the paper by signalling that the real one is being
  avoided.

## 7.3 Six item self check

Run before any review pass:

1. Every hypothesis maps to a specific table and column.
2. Every contribution claimed in the introduction corresponds to an actual
   finding, with the table that supports it named.
3. Every competing explanation from Stage 3.4 is addressed in the text.
4. Every number in the abstract and the introduction is traceable to a table.
5. The identifying assumption appears in the text as a sentence, not only as an
   implication of the method name.
6. The stated effect size is interpreted in units a reader outside the subfield
   would understand.

## 7.4 Review ladder

Choose the depth deliberately. Deeper review on an unstable result wastes the
review.

| Level | Scope | Use when |
|---|---|---|
| Light | Internal consistency, claim to evidence mapping | After a first complete draft |
| Full | Framing, theory, identification, measurement, results, writing, contribution, positioning | Before circulating to coauthors |
| Referee simulation | Adversarial reading plus a simulated revision request | Before submission |
| Cross model | A second model reviews independently | Before submission, to catch same model blind spots |

Cross model review matters because the audit in
`references/blindspot-audit.md` is run by the same model that wrote the
analysis, and shares its priors. Run at least one cross model pass on the
identification section.

## 7.5 Assembly

Convert markdown to the submission format when the content is final, not before.
Three line tables, Times New Roman 12 point, double spacing, continuous line
numbers if the outlet requires them.

Verify before export: all cross references resolve, all tables are referenced in
the text in order, all figures have self contained notes, and the reference list
matches the citations.
