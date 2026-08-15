# Blindspot Perception Audit

Mandatory once a complete table set exists, and again before submission. The
audit exists because the reading that produced the analysis is the reading least
able to see what is missing from it.

Read the tables as a hostile referee who wants to reject the paper and has one
hour.

## Four quadrants

### 1. Unexplained feature

Something visible in the output that the paper does not account for. A control
with an implausible sign or magnitude. A coefficient that changes across
specifications more than the text admits. A subgroup where the effect reverses.
An R squared that is implausibly high or low. A sample size that differs across
columns without explanation.

For each: name it, state the most likely explanation, and state whether it
threatens the main finding.

### 2. Convenient absence

Something a referee would expect to see and that is not there. A specification
that was run and not reported. An obvious alternative measure. A subgroup that
theory implies but that the paper does not test. A period that is excluded. A
control that the literature standardly includes.

For each: name it, and either produce it or state the reason it is absent. An
absence with no stated reason is the single most common cause of a first round
rejection.

### 3. Unasked question

The question a reader will have that the paper does not anticipate. Usually one
of: why this setting, why this window, why this outcome rather than the more
natural one, what happens to the units that leave the sample, and whether the
effect is large enough to matter.

### 4. Unexploited strength

Something the data can do that the paper is not using. Variation that would
sharpen identification. An outcome that would test the mechanism directly. A
sample split that would rule out a competing explanation. Papers are often
weaker than their data.

## Verdict

| Verdict | Meaning | Action |
|---|---|---|
| CLEAR | No quadrant produced an item that threatens the main finding | Proceed |
| CONDITIONAL | Items exist and are addressable | Proceed, record each flag in the status log, resolve before submission |
| HOLD | At least one item threatens identification or the main result | Stop. Resolve before any further analysis or writing |

Record the verdict, every item, and its disposition in `_status.md`. A
CONDITIONAL verdict whose flags are never revisited is equivalent to no audit.

## Limitation of this audit

This audit is run by the same model that produced the analysis and shares its
blind spots. It is a filter, not a substitute for an independent reader. Run at
least one cross model review of the identification section before submission.
