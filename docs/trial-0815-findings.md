# Empirical Workflow Kit v2 -- Issue List (generalized description, independent of any specific project)

Source: one complete trial run (Stage 1-3 backfill + Stage 4/6b look-ahead). This file has had all project details stripped;
each item describes only the problem with the tool itself, its consequences, and what kind of project will hit it.

Grading: **A** = structural defect, the tool cannot do what it claims to do.
**B** = usable, but the cost exceeds the benefit. **C** = worth adding, not urgent.

---

## Root cause: three sentences

1. **The tool version-controls artifacts, not claims.** It knows when, and by which
   script, a dataset was produced; it does not know whether a "number" has been superseded, whether it may be placed in the same table as another number,
   or whether it rests on a pipeline that has been retired.
2. **The tool can express "what happened," but not "what we agreed in advance would not happen."** Pre-commitment
   has no carrier in the tool, so "a commitment was overturned" is invisible within the system.
3. **The tool writes optional premises as mandatory premises.** Several stage contracts assume one shape of project (there is a merge, there is a persistent
   observation unit, the argument has the shape of an assumption list); projects that do not meet these assumptions get a batch of empty artifacts, and empty artifacts
   are indistinguishable in appearance from "work not done."

---

# Grade A

## A-1. No concept of a "result generation" (pipeline / vintage)

**Problem**
A project typically rebuilds its analysis pipeline two or three times over its lifetime. After a rebuild, the same set of coefficients exists in multiple versions,
and the values can differ to the point of opposite signs. The tool's data contract has `data_version`, which is the version of the **dataset**;
it has no field expressing "which generation of the pipeline this set of results belongs to," nor any registration of "which generation is currently valid."

**Consequences**
- Cannot answer "which pipeline did this number in the paper come from."
- Cannot prevent a table, a figure, or a sentence from mixing results of two generations -- this is a paper-level fatal error, and it is extremely hard to discover after the fact,
  because the surface structure after mixing looks completely normal.
- Artifacts of old generations are not automatically invalidated and can be referenced downstream at any time.

**What kind of project will hit this**
Any project that has rebuilt its pipeline more than once. That is, almost every real project.

**Direction**
Add a `pipelines:` registration block to `research.yaml`, each entry carrying `status: authoritative | superseded |
deprecated | scaffolding`, `superseded_by`, path, and production date; add a `mixing_rule`;
add a `pipeline_id` column to the claim-to-evidence audit table.

---

## A-2. Evidence cards have no supersession relation

**Problem**
The card template has 18 fields, and none of them can express "the result recorded on this card has been displaced by a newer version."

**Consequences**
The purpose of the evidence card system is to make every claim traceable to an artifact. But if the card itself cannot be marked as invalid,
then after a result is recomputed, the old card remains a fully formatted, authoritative-looking record.
**This system will precisely reproduce the very error it was meant to prevent.**

**Direction**
Add three fields, `status: current | superseded`, `supersedes`, and `superseded_by`,
and add a check at Checkpoint C: every referenced card must be `current`.

---

## A-3. Pre-committed acceptance criteria (acceptance gate) do not exist in the tool

**Problem**
Mature projects write down a set of numeric acceptance criteria before estimation, of the form "if metric X falls outside the interval [a,b], stop and reconfigure."
In the tool:
- there is no place to **declare** these criteria;
- therefore there is no place to record that a criterion **was crossed**;
- therefore there is also no way to check at wrap-up whether "the remedial action promised in exchange for crossing it was actually done."

The tool does have a Mandatory pause route, covering "identification diagnostic failed." But a pause is an **event type**,
whereas a gate is a **list written down in advance**. The former relies on the person involved recognizing it on the spot; the latter depends on no one's judgment.

**Consequences** (in increasing order of severity)
1. Whether the criteria exist at all depends on the project's own discipline; the tool does not require them.
2. When a criterion is crossed, the record format is unconstrained -- in practice it degrades into a severity label (a "soft flag"),
   and a label carries no decision-maker, no date, and no "was this decision made before or after seeing the results."
3. **Most severe**: crossing a criterion usually comes with a compensating commitment ("we downgrade, but we will do X later").
   The tool has no mechanism to hold this commitment open. Failure to honor it is completely silent; months later no one will notice.

**Direction**
- Add an `acceptance_gates[]` declaration block at Checkpoint B: `{name, metric, band, on_failure:
  warn | investigate | STOP}`.
- Add a hard rule: overturning a declared gate must produce a decision-log entry, which must include the trigger,
  candidate options, authorizer, date, a **pre-result / post-result marker**, and the compensating action.
- Add a closed-loop check at Checkpoint C: for any overturned gate, its compensating action must have been delivered, otherwise block.

This item has the highest return on investment of the entire list.

---

## A-4. The data contract describes only the shape of the data, not its semantics or its generation process

**Problem**
The current contract records: path, hash, row and column counts, keys, types, missing rates, value ranges, merge rates.
These describe "what the data looks like." The things that actually determine **what a number means** have no place at all:

| What is missing | Explanation |
|---|---|
| Field semantics and their source | The authoritative definition text of the field, which document it comes from, the date of that document |
| **Negative provenance** | "No authoritative definition document exists for this batch of fields" -- this is a fact that must be recorded, not a blank |
| Field credibility grading | Has source text / inferred from testing / source unknown are three distinct states, not a boolean |
| Derived variable formulas | The formula text, inputs, and code line of every constructed variable |
| Known defects | A dataset can pass every shape check while carrying a known formula error |
| Filter ladder | Ordered filter steps, with the condition text and before/after row counts of each step. The current contract has only a single total row-count scalar |
| Units and dimensions | A type of `double` is not the same as knowing its unit; unit conflicts across data sources are a classic silent bug |
| Time window specification | Treatment date, open/closed convention for window endpoints, calendar exclusions, nominal vs effective number of periods |
| Treatment assignment lookup table | The list itself that determines who is treated, its count assertions, how many copies of it exist in the code |
| Schema that changes by vintage | A field does not exist in early data and is silently filled in -- the filling itself is invisible in the finished product |
| Distributional facts | Mode mass, conditional distributions by group. `value_ranges` has only upper and lower bounds and cannot express these |

**Consequences**
Contract passed != data usable. It can prove that the shape of the data matches expectations; it cannot prove that the meaning of the numbers matches expectations.

**Direction**
Add seven blocks: `field_semantics`, `derived_fields`, `filter_ladder`, `window_spec`,
`treatment_assignment`, `schema_by_vintage`, `known_defects`.

---

## A-5. Conditional absence: optional premises written as mandatory premises

**Problem**
Several stage contracts embed assumptions about the project's shape, with no legitimate way to express that they are not met:

| Location | Embedded assumption | When not met |
|---|---|---|
| Stage 1 | The project merges multiple data sources | The required "bidirectional merge rates, characterization of unmatched records" artifact has empty content |
| Stage 1 | The observation unit is a persistent entity trackable across periods | "Number of units," "balance," "observations per unit," "entry and exit" all break down |
| Stage 5 | An executable data contract already exists | The required "contract validation results" artifact has nothing to write about |
| Stage 3 | The argument has the shape "assumption list + competing explanations" | See B-3 |

**Consequences**
- Missing required artifact = work not done, or = not applicable? **Indistinguishable in appearance.** This produces two bad outcomes at once:
  work not done is taken as not applicable, and not applicable is taken as work not done.
- A more hidden variant: the contract governs what it should not, while letting through what it really should govern. For example, two data sources are never merged
  but are compared in the paper -- the tool can express "merge quality," but not the **construction consistency** of two never-merged datasets,
  and the latter is the precondition for the comparison's conclusion to hold.

**Direction**
- Allow required artifacts to be marked `N/A` with a **mandatory reason**, where the reason itself is auditable.
- Change merge evidence to "required when a merge exists."
- When the observation unit is not a persistent entity, allow Stage 1 to declare a `design_grid` (the Cartesian product of structural dimensions),
  which is the true unit for quantile processing, diagnostics, and acceptance.
- Add a `sibling_parity` artifact: construction consistency between data sources that are compared but not merged.

---

# Grade B

## B-1. Record redundancy

`_status.md` (9 sections), `decision-log.md`, and evidence cards repeat the same set of facts: data version,
sample rules, clustering, output paths. This does not hurt in a one-time backfill; it hurts under continuous maintenance, and the pain manifests as **someone starting to skip**.
Once skipping begins, "the repository is the single source of truth" exists in name only.

**Direction**: make evidence cards the sole source of analysis facts; `_status.md` only references current cards and does not restate them.

## B-2. Stage 3 supports only one argument shape

Stage 3 requires "identifying assumption in one sentence + at least two competing explanations." This is the **assumption list** shape of argument.
Another shape, equally common in economics and stronger, is the **baseline rejection ladder**:
propose a null model -> derive several falsifiable predictions -> the data reject them -> show that several natural patches are mathematically ineffective ->
arrive at the only remaining direction.

The most valuable artifact of this kind of argument is the "**excluded explanation classes**" -- a record stating which entire classes of alternative explanations cannot produce
the observed pattern. The tool neither asks for it nor records it.

**Direction**: add a named optional mode to Stage 3, with an "excluded classes" table (class / method of exclusion /
analytic or numerical exclusion / boundary conditions of the exclusion).

## B-3. Required artifacts have no "pending" state

Related to A-5 but fixable independently. Artifacts have only two states, "exists" and "does not exist," with no "known to be needed, not yet produced,
blocked because of X." This means stage exit conditions can only be judged all-or-nothing.

## B-4. Insufficient vocabulary for observation units

See A-5. One addition: when structural dimensions (such as "platform x direction x period x before/after") are the true unit for quantile processing,
anomaly diagnostics, and acceptance decisions, the tool is unaware of this grid throughout,
and therefore cannot check "which cells in the grid are empty" -- empty cells cause certain robustness checks to silently not exist.

---

# Grade C

## C-1. No persistent artifact for a referee response bank
Mature projects maintain a list of "questions that might be asked + prepared answers." This is in effect a pre-written response to referee comments.
Stage 7 has a referee simulation, but no artifact to hold the answer bank. Cheap to add.

## C-2. The robustness checklist only says "what to run," not "what to do when results disagree"
The checklist lists the checks each design owes the reader. It has no rule for this situation:
**a key sensitivity analysis passes in some subgroups and fails in others.**

Suggested rule: in this case the claim contracts to the subgroups that pass, and the rest are reported as secondary results with the failure stated explicitly.
This is "tightening" rather than "loosening," safe in direction, and something good projects do on their own -- worth writing down as a rule so that it does not depend on discipline.

## C-3. The identification tree lacks several common designs
The current tree covers DID, staggered DID, DDD, IV, RDD. Missing:
- **Multiple differencing** (triple and higher, e.g., adding a layer of year-over-year same-period comparison to absorb seasonality);
- The DDD rule "state a single identifying assumption about the difference of differences, rather than three parallel-trends slogans"
  should be generalized to any order of differencing and written out explicitly.

## C-4. The choice of inference method is not in the checklist
With few clusters, the choice of bootstrap variant (restricted vs unrestricted) materially affects confidence intervals,
but no checklist item prompts this choice. Similarly: what to do when the clustering level does not match the treatment assignment level.

## C-5. `research.yaml` cannot bind roles to actual actors
The protocol defines three roles, Executor / Copilot / Quality auditor; the configuration file has no field stating who fills them.
Real projects need to distinguish: the sole decision authority, advisors consulted only at design nodes, multiple executing runtimes,
and requirements such as "identification review must come from an independent runtime."

## C-6. `autonomy_mode` is a dead field
The trial run confirmed: after the field is filled in, no file in the entire repository reads it, and no file defines its value domain.
Either make it a real set of tiers or delete it -- leaving it in is misleading.

## C-7. `data_hash` is a hard requirement with no fallback path
Historical projects usually cannot obtain a hash. The contract has no way to express the real state "process reproducible, identity unverifiable";
it can only be left blank -- and a blank looks like it was forgotten.

---

# Priority of the proposed changes

**First batch (A-1 / A-2 / A-3)**: these three are three guises of the same underlying defect -- the tool does not version claims
and gives commitments no carrier. They interlock: pipeline registration makes "which generation this number came from" queryable,
card supersession makes "whether this number still counts" queryable, and gate declaration plus closed-loop checks make "whether what was promised was done" queryable.
Changing all three together yields far more than changing them separately.

**Second batch (A-4 / A-5)**: contract expansion and conditional artifacts. More work than the first batch, but the fix is straightforward.

**Third batch (B / C)**: fill in along the way, non-blocking.

**Suggested to leave alone for now**: the stage division, checkpoint positions, and the trigger conditions of the mandatory pause.
In the trial run all three behaved correctly -- the tool's "stops" landed in the right places, and everything it stopped on was a decision problem rather than a computation problem.
