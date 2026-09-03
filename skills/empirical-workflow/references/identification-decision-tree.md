# Identification Decision Tree

Choose the design from the source and timing of variation, then choose an
estimator appropriate for the outcome. Record both paths in the Stage 6a
identification memo. The tree is a design screen, not an invitation to search
until a favorable estimator appears.

## Tree 0: causal timing and support screen

Complete this screen before choosing a policy, platform, market, or firm-panel
design. Preserve all dates in the treatment timeline: announcement date,
effective date, actual treatment or adoption date, and outcome measurement
date. The announcement is not treatment merely because it is observed. State
which date defines exposure and why the response cannot occur earlier.

| Question | Required record or action |
|---|---|
| Can actors react before the actual treatment? | Define an **anticipation** window; exclude it, model it as a lead, or explain why anticipation is impossible. Do not classify anticipated outcomes as untreated. |
| Is treatment binary, an intensity, repeated, or reversible? | Record first exposure, dose, every repeat treatment, and duration. A dose model needs a dose-response assumption; repeated events need non-overlapping or event-specific windows. |
| Can treatment end? | Record the **treatment exit** date and the rule for post-exit observations. Do not use an absorbing-treatment estimator when treatment switches off. |
| Can one unit affect another? | Name plausible **spillover** or interference paths, the exposure mapping, and the credible SUTVA scope. Use buffers, network/market exposure, or a design that models interference; otherwise limit the claim. |
| Does treatment affect being observed? | Report entry and exit, attrition, and post-treatment sample selection by treatment status. Do not condition the main sample on a post-treatment variable without a recorded design argument. |
| Does the data unit match assignment? | Aggregate or disaggregate only in a way consistent with treatment assignment. State the assigned unit, outcome unit, aggregation rule, and clustering level; avoid creating pseudo-replication. |

If a required timeline, support, or selection fact is unknown, pause before a
causal claim. Copy this screen's choices and unresolved risks into the
identification memo and its Evidence card.

## Tree 1: design from source of variation

Once the design is locked, load exactly one focused pack:

| Design decision | Focused method prompt |
|---|---|
| No defensible design selected yet | `methods/causal-design/prompt.md` |
| Plain within-unit panel comparison | `methods/fixed-effects/prompt.md` |
| Conditional exchangeability on measured covariates | `methods/selection-on-observables/prompt.md` |
| Difference-in-differences, event study, or DDD | `methods/did/prompt.md` |
| Instrumental variables | `methods/iv/prompt.md` |
| Regression discontinuity | `methods/rdd/prompt.md` |
| One or a few treated aggregate units | `methods/synthetic-control/prompt.md` |
| Randomized field intervention | `methods/field-experiment/prompt.md` |
| Conjoint or randomized profile experiment | `methods/conjoint/prompt.md` |

The router chooses the pack; the pack supplies the mature method prompt, read canon, detailed
edge cases, and reference R implementation. Do not load multiple method prompts to shop among
estimators after seeing results.

### Q1. What creates variation in the treatment?

| Source of variation | Design |
|---|---|
| A policy, rule, or platform change with a date and a group not exposed to it | DID family; apply Q2 after Tree 0 |
| Exposure varying along group, time, and a third margin | DDD; apply Q3 |
| Assignment determined by a threshold on a continuous running variable | RDD; apply Q4 |
| A variable that shifts treatment with a defensible exclusion argument | IV; apply Q5 |
| Random or as-good-as-random assignment | Experimental estimation with covariate adjustment if precommitted |
| None of the above, only selection on observables | OLS or fixed effects; apply Q6 and use non-causal language |

### Q2. DID and event studies

**Single adoption date, two groups.** Two-way fixed effects (TWFE) is an
acceptable main specification if its parallel-trends and timing diagnostics
support it. Required evidence: event-study leads and lags, placebo dates,
alternative comparison groups, and sensitivity to plausible trend violations.

**Staggered adoption.** The main specification must use a
heterogeneity-robust estimator, such as Callaway and Sant'Anna, Sun and
Abraham, Borusyak, Jaravel and Spiess, or de Chaisemartin and D'Haultfoeuille.
Choose according to its comparison group and whether treatment is absorbing,
and state that reason. TWFE is reference-only, clearly labeled as such.

- A Goodman-Bacon decomposition or direct negative-weight diagnostic is
  mandatory. Report the negative weights even if they appear harmless.
- Show cohort/event-time estimates and distinguish never-treated from
  not-yet-treated comparisons.
- If treatment exit occurs, use an estimator that permits non-absorbing,
  on/off treatment; do not recode exits as continued exposure.
- For intensity or repeat treatment, define the estimand, comparison state,
  carryover rule, and event overlap rule before estimation.
- Pre-trend non-rejection is weak evidence with short or noisy pre-periods.
  Report a Rambachan-Roth-style sensitivity analysis stating the violation that
  would overturn the conclusion.

### Q3. DDD

Use DDD when a third contrast isolates the effect within treatment and time.
State the one identifying assumption about the difference of differences of
trends, not three separate parallel-trends slogans. Report each underlying
double difference and a placebo third dimension. Apply Tree 0 separately to
each exposure margin.

### Q4. RDD

- State whether assignment is sharp or fuzzy; a fuzzy RDD also satisfies IV
  requirements at the cutoff.
- Use local-polynomial regression, bias-corrected inference, and a
  data-driven bandwidth; report the effective sample within it.
- Report density/manipulation tests, predetermined-covariate continuity,
  placebo cutoffs, bandwidth sensitivity, and a donut specification if
  heaping is plausible.
- Never use a high-order global polynomial as the main specification. The
  estimand is local to the cutoff and interpretation must say so.

### Q5. IV

- Report the first stage and, with one endogenous regressor and one instrument,
  the Olea-Pflueger effective F statistic.
- Explain exclusion in a paragraph that names the concrete alternative channel
  and why it does not operate. It is an argument, not a test.
- State monotonicity and who the compliers are for a LATE interpretation.
- Show reduced form and OLS beside 2SLS. Use weak-instrument-robust inference,
  such as Anderson-Rubin confidence sets, when strength is inadequate.
- For shift-share or interaction instruments, argue identification at the
  shock or share level rather than for the product alone.

### Q6. Selection on observables

State the estimand and the no-unobserved-confounding assumption. Present
coefficient stability and a bounding exercise where feasible, but do not use
causal language unless stronger design evidence exists. Fixed effects do not
by themselves solve time-varying selection, spillovers, or post-treatment
sample selection identified in Tree 0.

## Tree 2: estimator by dependent variable

| Dependent variable | Main estimator | Notes |
|---|---|---|
| Continuous | OLS with high-dimensional fixed effects (`feols`) | Report units and residual diagnostics relevant to the estimand. |
| Count or non-negative with many zeros | Poisson pseudo-maximum likelihood (`fepois`) | Handles zeros; coefficients are semi-elasticities without requiring Poisson outcomes. |
| Strictly positive and skewed | Log OLS or Poisson | Use Poisson when the conditional mean is central under heteroskedasticity. |
| Binary | Linear probability model; logit as robustness | Conditional logit can change the sample in fixed-effect panels. |
| Share or proportion | Fractional response or linear model | Report boundary mass. |
| Duration | Hazard model | State censoring and risk-set construction. |
| Ordinal | Linear and ordered model | Interpret cautiously. |

Cluster at treatment assignment. Report the number of clusters; with roughly
fewer than 40 clusters, use wild-cluster bootstrap or an equally justified
small-cluster method.

## Recording the path

The identification memo records the Tree 0 timeline and risks, source of
variation, chosen design and estimator, one-sentence identifying assumption,
assignment-consistent aggregation, diagnostics, and an explicit backtracking
trigger. Attach an Evidence card that links the memo to the locked design,
data-contract version, sample rule, code, outputs, and decision-log entry.
