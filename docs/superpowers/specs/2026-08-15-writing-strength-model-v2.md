# Writing-Strength Model v2 -- Calibrated on a Corpus of 14 Top-Tier IS Papers

Corpus: 14 papers (MISQ / MS / ISR, 2012-2026), covering DID, staggered DID, RDD, RDiT, IV/2SLS,
survival models, structural estimation, and randomized experiments. 278 assertion sentences and
about 110 downgrade instances were extracted.

---

## 1. Where the Original Design Went Wrong

I set up a single-axis, five-tier scale a priori (T0 unqualified causal -> T4 pure description).
The corpus shows it works well in the **core range** (reduced-form causal sentences + observational
data) but fails systematically in four directions:

| Failure direction | Corpus evidence |
|---|---|
| **Negative/exclusionary assertions** | "does not come at the expense of", "cannot be explained by", "we rule out". The burden-of-proof structure is inverted -- it rests on **power**, not identification. The same sentence means something entirely different in a design with n=100,000 and in an experiment with n=57, yet the tier is the same. 12 instances in the corpus |
| **Methodological assertions** | "Estimating a static demand model would give biased elasticities". Grammatically a standard T0, but its truth value is settled by derivation rather than by data; there is no empirical commitment that could be falsified. Structural papers reserve their most unreserved causal language for **rejecting other people's methods**, while their own conclusions are uniformly lowered to T3 |
| **Discriminating arguments** | "It is difficult to envision a selection process that would...", "if this were the case, any observed effects would not be limited to...". The persuasive force comes from the **selectivity of the pattern**, not from the verb. Read literally they are T3/T4, yet they carry the heaviest identification work in the paper -- **tier and argumentative weight run in exactly opposite directions** |
| **Model-internal assertions** | Simulation output is grammatically isomorphic to an estimate with a standard error. "the total net gain would be 164.29 million dollars" and "reduces the probability by 21.60%" cannot be distinguished on the five-tier scale |

There are also three breakdowns at the execution level:

- **The "same sentence" rule lets punctuation decide the tier.** The same substantive commitment
  is T0 when written as two sentences and T1 when written as one. In the corpus, the actual scope
  of a qualifier has four levels: same sentence / paragraph level ("our findings are conditional
  on them", covering every conclusion that follows) / section level ("Even though the
  counterfactuals are 'partial'", covering three experiments) / cross-section forward reference
  ("we assess this in Appendix A").
- **T2 lumps three phenomena together**: a robustness failure of the same claim, a null result on
  a parallel construct, and a hypothesized direction that is reversed. The second kind is not
  counterevidence at all. "T2 density" therefore cannot be used for cross-paper comparison.
- **Hypothesis statements are grammatically T0.** Tiering them by the book would record "stating
  a proposition to be tested" as "making an unqualified causal assertion".

---

## 2. The Revised Model

### 2.1 Classify the type first, then assign the tier

Tiers are meaningful only for the `world` type. The other types follow their own rules.

| Assertion type | Test | Governance |
|---|---|---|
| `world` | Causal or associational assertion about the object of study | Assign T0--T4 |
| `negative` | Exclusionary/negative assertion | **Not tiered**. Must carry `power_basis`: the test supporting the exclusion, its sample size, and its minimum detectable effect. Without `power_basis`, always lowered to T3 wording ("does not appear to be the primary driver"); "we rule out" is forbidden |
| `methodological` | The object of the assertion is an estimator or method rather than the world | Not tiered, but the type must be tagged so that it is not counted in empirical-strength statistics |
| `discriminating` | Argument of the form "if the alternative explanation held, X should be observed" | Not tiered, but **the specific alternative explanation it rules out must be registered**. A low tier is normal for such sentences; the checker must not conclude "weak evidence" from it |
| `model_internal` | Model output with no sampling uncertainty | Must carry the `as-modeled` marker (in the corpus, `as we model` / `Given the model structure` are the cleanest boundary phrases). "significant" is forbidden |
| `hypothesis` | Proposition awaiting a test | Not tiered |

### 2.2 Tiers (`world` only), with the "same sentence" constraint removed

T0 unqualified / T1 scope-qualified / T2 causal assertion + disclosed counterevidence / T3 association or consistency / T4 description.

"Same sentence" becomes a separate field:

```
qualifier_scope: sentence | paragraph | section | cross_reference
```

Qualifiers at the `section` and `cross_reference` levels are **allowed**, but with a requirement:
the qualifying sentence itself must be registered as a `scope_declaration`, and its coverage must
be declared explicitly. This makes the P13 situation -- one 'partial' covering three experiments
but vanishing from the abstract -- detectable.

### 2.3 Three new dimensions -- these are the variables that actually separate honesty from evasion

**(1) `counterevidence_prominence`: the prominence of the counterevidence**

In the corpus the same piece of counterevidence can appear in five positions; the tier is the same,
but the actual constraining force differs by an order of magnitude:

| Position | Example |
|---|---|
| In parentheses | "attenuates the negative effects of language and cultural **(but not time zone)** differences" |
| Sentence-final coordination, no contrastive connective | "a positive and significant impact on Reservations, **albeit with a relatively small coefficient, and no significant effect on Booked Days**" |
| Standalone contrastive sentence | "**However**, the coefficient of weitaonum is insignificant." |
| Footnote/endnote | "it is **nearly impossible** to tease out the informational effect and reward effect separately." (the heaviest mechanism limitation in the whole paper) |
| Appendix | "**although the pre-treatment trends are not strictly parallel**..." (a partial failure of the core identification assumption, never mentioned in the main text) |

**Statistical fact: in 8 of the 14 papers, the single most threatening disclosure sits in a footnote, endnote, or appendix rather than in the main text.**

T2's "adjacent disclosure" must therefore be refined into checkable prominence levels, with the
rule: **when the counterevidence targets the identification assumption itself, prominence must
reach the "standalone contrastive sentence + main text" level**.

**(2) `underlying_precision`: the precision of the estimate the sentence relies on**

The three sharpest cases in the corpus: an insignificant coefficient given a substantive
interpretation ("insignificantly different from zero and slightly positive ... implying that...");
a p<0.10 coefficient promoted in the abstract to an unmarked causal verb (main text
"suggesting that..." (significant at 10%) -> abstract "generate"); a cross-sectional difference
with t=1.8 written up in the abstract as established fact.

All three sentences are **restrained in tier** and read as perfectly fine. The five-tier scale
measures grammatical commitment, not the match between wording and evidence.

**(3) The real metric, derived from the first two: the residual**

```
overclaim_residual = wording tier strength - evidence strength
```

where evidence strength is computed from fields the claim registry already has (assessment,
whether the claim has been narrowed, gate status, provenance of the supporting cards), with
`underlying_precision` layered on top.

- Positive residual -> **overclaim**, block
- Negative residual -> **wasted evidence**, report
- This is exactly the correct formalization of "block when too strong, report when too weak" from my original design

---

## 3. The Downgrade Move Library (12 Classes) and the Four Criteria for "Honest vs Evasive"

Criteria (each machine-checkable):

- **(a) Locatability**: whether the narrowing is bound to a specific specification/column number/variable/subsample
- **(b) Propagation**: whether the narrowing changed the wording of the downstream text (abstract/conclusion/title). **No propagation = evasion**
- **(c) Directionality**: whether the direction or consequence of the bias is stated, or merely "should be interpreted with caution"
- **(d) Immediate recovery**: whether, after the concession, it is cancelled in the same or the next sentence by `However / Nevertheless / Overall / Encouragingly`

| # | Move | Trigger | Lands at | Verdict |
|---|---|---|---|---|
| 1 | **Scope narrowing** | Subsample failure | T1 | Depends on propagation. "our earlier reported effects **are driven by IT-using industries**" -- the abstract does not carry this qualifier = evasion |
| 2 | **Mechanism demoted to interpretation** | Mechanism not identifiable | T3 | **Honest**. Present in 13 of the 14 papers. Marker phrases: `We interpret ... as reflecting` / `as a plausible explanation` / `We propose some potential mechanisms` |
| 3 | **Null result restated as exclusionary evidence** | Mechanism/balance test comes out null | T2/T3 | Split. The criterion is **whether it acknowledges that "absence of evidence is not evidence of absence"**: the honest ones immediately write "an absence of evidence does not constitute evidence..." |
| 4 | **Failure restated as a methodological deficiency** | Robustness failure | T2, claim not lowered | **Evasive**. "not significant, **perhaps because of the limited power** ... However, the direction and magnitude are consistent with our expectations." Gives only half the explanation |
| 5 | **Up-front declared narrowing** | Cannot be answered by design | Claim withdrawn | **Most honest**. "we are not taking a strong position that...", "we are unable to draw meaningful inferences about...". The paper consequently contains not a single T0 sentence |
| 6 | **Bias-direction statement** | Measurement error/SUTVA | T1/T3 | Depends on whom the direction favors. If the stated bias direction happens to make one's own conclusion overstated, and nothing is recovered afterwards = honest; packaging it as "we underestimate" followed by "so the true effect is even larger" = evasive |
| 7 | **Concession-recovery** | Partial balance-test failure | Net T4, claim not lowered | **Evasive**. Template: `Although [unfavorable fact], [magnitude/citation]` + next sentence `However/Overall/Encouragingly` resets. **All 14 papers use this template** |
| 8 | **Displacement and burial** | Unfavorable fact conflicts with the claim | Main-text tier unchanged | **Evasive**. In 8/14 papers the most threatening disclosure is in a footnote/appendix |
| 9 | **Conditional reassurance** | Untestable assumption | Surface T3, no substantive narrowing | **Evasive**. "**If** the share of gift purchases is small, the potential bias should be negligible." -- the condition itself is never tested |
| 10 | **Deferral to the research agenda** | Any limitation | No downgrade | **Evasive**. It is the norm for 3-4 of the 5 items in a limitations paragraph to fall into this class |
| 11 | **Target substitution** | Target construct not measurable | T1 | **Honest**. "**rather than examining** the implications for SAP behavior, **we instead examine** their implications for ISV partnership decisions." -- the limitation is exchanged for a smaller claim that the data can support. The cleanest class in the entire corpus |
| 12 | **Self-declared untestability** | Mechanisms inseparable by design | Claim withdrawn/T3 | **Most honest**. "we **admittedly have no way of testing** this conjecture." -- admits it and offers no remedy |

---

## 4. Four Statistical Facts That Change the Writing Guidance (Not Just the Checker)

**1. An abstract stronger than the main text is an industry convention, not an isolated slip.**
Of 45 comparable pairs: abstract stronger **30**, same 9, weaker 4, protective omission 2. **13/14 papers** have at least one instance.

Implication: the rule cannot be written as "the abstract must not be stronger than the main text";
everyone would violate it and it would become dead. The correct rule is
**an upgrade must leave a trace** -- when the abstract's tier is above the results section's, record how many tiers it rose and what supports it.
The four upgrade techniques (by frequency): deleting the counterevidence in the same paragraph / erasing the baseline or magnitude / swapping the self-label
(main text "back-of-the-envelope estimation" -> abstract "Our further analysis indicates") / swapping the verb.

**2. The strength peak is not always in the abstract.** All three patterns have instances: introduction > abstract; conclusion > abstract > results (the same claim
upgraded monotonically T3 -> T1 -> T0); **title > abstract > main text** (title "Optimizing", main text explicitly stating
"we do not attempt to manipulate the policies to achieve optimality").
Consistency checks must therefore cover the title.

**3. The limitations paragraph is not where downgrades happen.** Downgrades happen inside the results section (in the same sentence as the failure, or right next to it) and in the methods section.
The two discourses never reference each other -- the most fragile evidence exists exactly once, at the place where it first appears.
Of the 9 papers with a standalone limitations subsection, **3 have limitations paragraphs that mention none of the failures already disclosed in the main text**.

**4. The most counterintuitive, and most useful, finding: dropping the standalone limitations subsection makes papers more honest, not less.**

An inventory of 59 limitation statements: genuine constraints 36, ritual disclaimers 16, half-genuine 6, execution failure 1.

- With a standalone limitations subsection = 9 papers; the ritual disclaimers concentrate in three of them (4 of 5 / 3 of 5 / 2 of 5)
- **Without a standalone limitations subsection = 5 papers, and in 4 of them every limitation statement is a genuine constraint**

The mechanism is clear: **with no dedicated place to put limitations, a limitation can only be attached next to the claim it affects**, so it necessarily comes with
a column number, a variable name, a subsample, and therefore necessarily satisfies criterion (a). The extreme case has seven limitations landing in the introduction, §3, §4.4,
§4.4.3, §5.1.1 (two), and §5.2, each bound to a specific column number, with at least two admitting a failure and offering no remedy.

The cost is that readers have to piece the scattered limitations together themselves.

---

## 5. The Special Wording of Structural Estimation Papers (Listed Separately)

**The grammatical division of labor between identified and calibrated is extremely clean**:
- identified is always passive or "only ... can be identified": `the discount factor is usually not identified, so I do not attempt to estimate it`
- calibrated is always first-person active setting + endorsement by convention: `I set all discount rates to be 0.996, which has been typically assumed for monthly data`; tables are labeled directly as `0 (fixed)` / `1 (fixed)`

**A class of substantive downgrade the five-tier scale cannot see: identified -> simulated.**
"the magnitude of indirect effects ... **is difficult to identify separately by the estimated parameters** ...
**we apply simulations to explicitly quantify** the indirect effects" -- the quantity goes from "a parameter with a standard error"
to "simulation output with no standard error", grammatically indistinguishable from the other effect sizes.

**Three ways of qualifying counterfactuals**: a one-time blanket qualifier + self-deprecating scare quotes (`Even though the counterfactuals are "partial,"`,
but the qualifier vanishes entirely from the abstract and the conclusion, while its substantive consequence is heavy -- the net-gain figure flips sign across the three settings);
dispersed, repeated conditional qualifiers (repeated next to almost every policy-simulation conclusion); no qualifier at all, with the counterfactuals written as elasticity facts.

**The cleanest boundary markers: `as we model` / `Given the model structure`** -- they appear only in structural estimation papers,
and flag that "this conclusion is determined by the model specification rather than supported by the data". In one instance the authors consequently **decline to interpret the conclusion at all**:
"Given the model structure, the effect ... should be consistent qualitatively. Therefore,
**we omit the repeated qualitative interpretation**."

**The strength anomaly of methodological assertions**: the three strongest T0 sentences in a structural paper's introduction are all not about the world, but about
the bias of other people's methods. The authors' own conclusions are uniformly lowered to T3.

---

## 6. Implications for the Checker

Four new machine-checkable checks, all derived from the criteria above:

| Check | Basis | Output level |
|---|---|---|
| **Propagation**: a claim was narrowed in the results section (`revision_reason: bounded_by`), but the tier of the same claim in the abstract/conclusion/**title** did not follow | Criterion (b); 30/45 pairs in the corpus | BLOCK |
| **Immediate recovery**: `However / Overall / Nevertheless / Encouragingly` appears within 1 sentence after a concession structure and the claim's tier was not lowered | Criterion (d); 14/14 papers use this template | WARN |
| **Counterevidence prominence**: counterevidence targeting an identification assumption whose prominence is below "standalone contrastive sentence + main text" | 8/14 papers put the heaviest disclosure in a footnote/appendix | BLOCK |
| **Overclaim residual**: wording tier - evidence strength (including `underlying_precision`) > 0 | 6.10 | BLOCK (>0) / INFO (<0) |

Plus one hard rule for negative assertions: **without `power_basis`, "we rule out" may not be written**; only
"does not appear to be the primary driver" is allowed.
