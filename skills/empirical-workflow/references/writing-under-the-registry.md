# Writing Under the Registry

Read this when a validator finding asks you to change prose: a buried
challenge, an overclaim residual, an unregistered assertion. It is about how to
satisfy those checks in the paper's own voice.

There is one rule, and everything below is a consequence of it.

> **The paper states what is true about the world. The registry states what the
> authors are doing about it.** Nothing that belongs in the second may appear in
> the first.

The registry is apparatus. A reader is entitled to the finding and its limits;
they are not entitled to — and should not have to read past — the bookkeeping
that produced them. When apparatus vocabulary reaches the manuscript, the paper
starts narrating its own compliance, which reads as defensive and tells the
reader nothing they can use.

## The test

Ask of any sentence a check made you write: **does this assert something about
the world, or about the claim?** A sentence about the claim goes in the
registry, in a decision log, or in a technical appendix — never in the body.

| Belongs in the paper | Belongs in the registry |
|---|---|
| the effect, its size, its sign | the claim's tier, its revision, its assessment |
| the direction or population a result holds in | that a claim was narrowed, and by which relation |
| a diagnostic that failed and what follows | which gate fired and what compensated it |
| a pre-commitment the results did not meet | the gate's band, status, and acceptance record |
| what a robustness check does and does not establish | the evidence card and its provenance |

Pre-registration is not apparatus. Saying *"this is a weaker statement than the
one we pre-committed to"* is a fact about the research and belongs in the paper.
Saying *"we restrict the causal claim accordingly"* is a fact about the registry
and does not.

## Disclosures

A challenge disclosure has to sit next to the claim, open with a contrastive
connective, and carry a counterevidence cue. That is a constraint on *form*. It
is not an instruction to write about your own claim-making, and the temptation
to do so is what the constraint tends to produce on a first pass.

Four from a real trial, before and after:

> ~~However, the divergence survives only on trips into the charged zone, **and
> we restrict the causal claim accordingly**.~~
> However, the divergence survives only on trips into the charged zone.

The restriction *is* the second sentence. Announcing it adds a clause about the
authors and subtracts nothing from the reader's uncertainty.

> ~~In contrast to the other two directions, this is the comparison that
> survives bias correction, **and it is the only one over which we state the gap
> causally**.~~
> In contrast to the other two directions, this is the comparison that survives
> bias correction.

> ~~By contrast with the other two directions, this **reading is licensed** only
> for trips into the zone.~~
> By contrast with the other two directions, this **pattern holds** only for
> trips into the zone.

A pattern holds or it does not. Whether a reading is licensed is a question
about warrant, and warrant is the registry's subject.

> ~~On trips out of the zone it does not survive, **and that direction is
> reported as secondary throughout**.~~
> On trips out of the zone it does not survive.

A reporting convention is a fact about the document. State it once where
conventions are stated, not beside each estimate it governs.

## Choosing the assertion type

The type is chosen before the tier, and it decides which checks apply at all.
Four of the six sound alike in English and are routinely confused, so:

| The sentence says | Type | What it owes |
|---|---|---|
| something about the world, from an estimate | `world` | a tier, and a residual no greater than its evidence |
| an estimate came back null | `negative` | a power basis, or a hedge |
| something about the design, the sample, or what you did not do | `methodological` | nothing beyond being true |
| what a model implies | `model_internal` | `as_modeled: true` |
| that this explanation fits and a named rival does not | `discriminating` | the rival, named specifically |
| a proposition awaiting a test | `hypothesis` | to read like one |

**`negative` is the one that gets over-used.** It means an estimate that failed
to reject — nothing else. These are *not* negative results:

> ~~*negative*~~ → *methodological*: "The parallel-trends assumption is not
> satisfied cleanly, and this is the binding limitation."
> A statement about the design, not about a null estimate.

> ~~*negative*~~ → *world*: "Six of twelve pre-period coefficients are
> distinguishable from zero at five percent."
> A pre-trend that rejects is a finding. It has a sign and a magnitude, so it
> takes a tier.

> ~~*negative*~~ → *model_internal*: "Under linear demand the volume weight
> drops out of the comparative static."
> About what the model implies, not about what the data failed to show.

> ~~*negative*~~ → *methodological*: "This is one charge, in one city, on two
> firms, over six weeks."
> A scope limit.

A genuine negative reads like this: *"We find no effect on trip volume; with
53 clusters the design can detect a change of 4 percent or more."* It names
what was not found and what could have been found, which is what the power
basis is for.

`NEGATIVE_POWER_BASIS_REQUIRED` now reports a `suggested_assertion_type`
alongside the block. It reads the sentence; take the suggestion as a prompt to
re-read it yourself, not as an answer.

## When the warrant is a proof

A claim can rest on a derivation rather than an estimate — an inertness result,
an identity, a benchmark's predictions. Register it with an `analytical`
evidence card, which names the document carrying the argument:

```yaml
- evidence_card_id: EC-derivations
  provenance: analytical
  derivation: evidence/framework-derivations.md
```

An analytical card carries no `estimates`, and it can support a claim only if
every one of that claim's sites is `model_internal` or `hypothesis`. Point a
`world` site at one and the validator blocks with
`ANALYTICAL_SUPPORT_MISPLACED`: a proof warrants a proposition, not a finding.

## Disclosing a challenge, once

A challenged claim must show the reader what is wrong with it, and there are two
places the registry will take that from:

- `counterevidence_prominence` plus `counterevidence_disclosure` on the
  assertion site — the ordinary case, and the one the writing checks talk about;
- a `disclosure: {adjacent: true, paper_location: ...}` block on the challenging
  relation — for a claim with no assertion site to hang it on.

**Either satisfies both checks.** A corroborated site disclosure now also
discharges the publication gate's `challenge_undisclosed`, so the fact is
recorded once. If you see that reason at Checkpoint C, the site disclosure is
missing or uncorroborated — fix it there rather than adding a second record on
the relation.

## Where the judgement goes instead

Every check that changes prose leaves a judgement behind: why this wording, why
this site, why not the others. That judgement is worth keeping and is worth
nobody's reading time in the manuscript.

- **Why a claim is bounded, and by what** — the `bounds` or `challenges`
  relation, in `evidence_relations.yaml`, with its rationale.
- **Why a gate was closed the way it was** — the compensation artifact the gate
  definition names, under `evidence/gates/`.
- **Why a sentence is worded as it is** — `decision-log.md`, if the wording was
  itself a decision.
- **What the checks demanded and what the author chose beyond that** — the
  project's technical report, not the paper.

## What the checks will not tell you

The adjacency rule enforces that each audience meets a qualification once, and
the residual enforces that no sentence reads stronger than its evidence.
Neither can tell whether the sentence is *well written*, and neither should
pretend to. Satisfying both with five stock connectives produces prose that is
honest and mechanical; the remedy is the author's, not the tool's.

Two habits help:

1. **Write the limit into the claim, not after it.** A sentence that already
   says *"into the charged zone"* often needs no separate disclosure, because
   the residual reads a scoped sentence as weaker. The check that never fires is
   cheaper than the one you satisfy.
2. **Vary the connective across the paper.** `however`, `nevertheless`, `yet`,
   `by contrast`, `in contrast` all satisfy the rule. Using one of them eight
   times is a choice, not a requirement.
