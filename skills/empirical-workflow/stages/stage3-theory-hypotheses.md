# Stage 3: Theory and Hypotheses

Goal: commit to a mechanism and to a set of hypotheses whose specifications are
fixed before any estimate is seen. This stage ends at Checkpoint A.

Output: `docs/theory_hypotheses.md`.

## 3.1 Primary theoretical lens

Choose one primary lens and name it. A paper that gestures at three theories
explains nothing. Secondary theories may enter as competing explanations in 3.4.

## 3.2 Mechanism

Write the causal chain in prose: the treatment changes A, which changes B, which
changes the outcome. Each arrow is a claim. Mark which arrows the data can
observe directly and which are inferred. The observable arrows become the
mechanism tests in Stage 6.

## 3.3 Hypotheses

For each hypothesis state, in a single table row: the claim, the expected sign,
the boundary condition, the specification that will test it, the sample, and the
coefficient that carries the test.

| H | Claim | Sign | Boundary | Specification | Sample | Coefficient of interest |

This table is the pre-commitment. Any later change to it is a Decision Log entry
with a reason.

## 3.4 Competing explanations

Name at least two alternative accounts that would produce the same sign on the
main coefficient. For each, state the empirical implication that differs from
the proposed mechanism, and how it will be tested. Papers are rejected far more
often for an unaddressed alternative than for a small effect size.

## 3.5 Branch decision

Decide whether Stage 6 runs reduced form, structural, or both, and record the
reason. Structural is warranted when the question requires a counterfactual
outside the observed support, a welfare quantity, or a parameter with an
economic interpretation that no regression coefficient carries. If a reduced
form estimate answers the question, use it.

## Checkpoint A

Run the Checkpoint A table from `SKILL.md`. Write the result to
`docs/checkpoints/checkpoint_a.md` including any waivers and their reasons.
Do not begin Stage 4 until this is signed off.
