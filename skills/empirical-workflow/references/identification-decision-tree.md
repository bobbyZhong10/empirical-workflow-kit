# Identification Decision Tree

Two trees. The first chooses the design from the source of variation. The second
chooses the estimator from the dependent variable. Walk both, and record the
path taken in the identification memo.

## Tree 1: design

### Q1. What creates variation in the treatment?

| Source of variation | Design |
|---|---|
| A policy, rule, or platform change with a date and a group not exposed to it | DID family, go to Q2 |
| Exposure varying along two dimensions, for example group and time and a third margin | DDD, go to Q3 |
| Assignment determined by a threshold on a continuous running variable | RDD, go to Q4 |
| A variable that shifts treatment and has a defensible exclusion argument | IV, go to Q5 |
| Random or as good as random assignment | Experimental estimation, differences in means with covariate adjustment |
| None of the above, only selection on observables | OLS with fixed effects, go to Q6 |

### Q2. DID: is adoption staggered?

**Not staggered** (a single treatment date, two groups): two way fixed effects
is an acceptable main specification. Required evidence: pre trends, placebo,
alternative comparison groups.

**Staggered** (units treated at different times): two way fixed effects is
biased when treatment effects vary across cohorts or over time, because already
treated units serve as controls and can enter with negative weights.

- The main specification must be a heterogeneity robust estimator: Callaway and
  Sant'Anna, Sun and Abraham, Borusyak Jaravel and Spiess, or de Chaisemartin
  and D'Haultfoeuille. Choose on the basis of the comparison group each one uses
  and state that reason.
- Two way fixed effects may appear as a reference column, labeled as such.
- A weight diagnostic is mandatory: a Goodman Bacon decomposition or a negative
  weight check. Report it even when it is reassuring.
- If treatment switches off for some units, the estimators above that assume
  absorbing treatment do not apply. Use one that permits exit.

**Pre trends**: an event study plot is necessary but not sufficient. A test that
fails to reject pre trends is weak evidence when the pre period is short or
noisy. Report a sensitivity analysis in the style of Rambachan and Roth that
states how large a violation would have to be to overturn the result.

### Q3. DDD

Use when a second contrast isolates the effect within the treated group and
time. The identifying assumption is not two parallel trends assumptions but one
assumption about the difference of differences of trends. State it explicitly.
Report each of the underlying double differences separately: a DDD whose
components are not shown hides where the identification actually comes from.

### Q4. RDD

- Sharp or fuzzy. Fuzzy RDD is IV at the cutoff and inherits every IV
  requirement.
- Estimate with local polynomial regression, bias corrected inference, and a
  data driven bandwidth. Report the effective sample within the bandwidth.
- Required evidence: density test for manipulation of the running variable,
  continuity of predetermined covariates at the cutoff, placebo cutoffs,
  bandwidth sensitivity, and a donut specification if there is heaping.
- Never present a high order global polynomial as the main specification.
- The estimand is local to the cutoff. Say so when interpreting.

### Q5. IV

- Relevance: report the first stage. With one endogenous regressor and one
  instrument, report the effective F statistic of Olea and Pflueger rather than
  a conventional rule of thumb.
- Exclusion: argued in words, never tested. Write the argument as a paragraph
  that names the specific alternative channel and why it does not operate.
- Monotonicity: required for a local average treatment effect interpretation.
  State who the compliers are.
- Always report the reduced form and the ordinary least squares estimate beside
  the two stage estimate. A reduced form that is not visible is a warning sign.
- If the first stage is not strong, use weak instrument robust inference such as
  Anderson Rubin confidence sets rather than proceeding as usual.
- Shift share and interaction based instruments require the identification
  argument to be made at the level of the shocks or the shares, not the product.

### Q6. Selection on observables

If the design is fixed effects with controls only, the paper must say what it is
estimating and under what assumption. Do not use causal language for a
specification whose identification rests on the absence of unobserved
confounders. State the assumption, offer whatever indirect evidence exists
(coefficient stability across control sets, a bounding exercise in the spirit of
Oster), and frame the contribution accordingly.

## Tree 2: estimator by dependent variable

| Dependent variable | Main estimator | Notes |
|---|---|---|
| Continuous | Ordinary least squares with high dimensional fixed effects (`feols`) | |
| Count, or non negative with many zeros | Poisson pseudo maximum likelihood (`fepois`) | Consistent without the Poisson distributional assumption; handles zeros; coefficients are semi elasticities |
| Non negative and skewed with zeros | Poisson pseudo maximum likelihood on the level | Avoid log of one plus the variable: the estimate depends on the units of measurement and is not an elasticity |
| Strictly positive and skewed | Log with ordinary least squares, or Poisson | If the object of interest is the mean rather than the median, Poisson is safer under heteroskedasticity |
| Binary | Linear probability model as the main specification, logit as robustness | In panels with unit fixed effects, conditional logit drops units without variation and changes the sample; the linear model keeps interpretation and inference simple |
| Share or proportion in the unit interval | Fractional response, or the linear model with the boundary mass reported | |
| Duration | Hazard model, with the censoring structure stated | |
| Ordinal | Report the linear model and an ordered model; interpret cautiously | |

Cluster standard errors at the level of treatment assignment in all cases.
Report the number of clusters. Below roughly 40 clusters, use wild cluster
bootstrap.

## Recording the path

The identification memo records: source of variation, design chosen, estimator
chosen, the identifying assumption in one sentence, and the diagnostics the
design therefore requires. Copy the diagnostic list into the Stage 6a plan
directly from `robustness-checklists.md`.
