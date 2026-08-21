# Writing-Strength Layer v2.2 Design

## Governing boundary

This layer governs the match between a governed claim's evidence state and each
place where the manuscript expresses that claim. It extends the executable v2.1
claim registry; it does not replace v2.1 state, create another traversal, or
change workflow stages, checkpoints, or Mandatory-pause triggers. Assertion
records remain human-editable YAML and manuscript text remains the source that
the validator reads.

The two mismatches have different consequences. Language that promises more
than the evidence supports blocks the relevant output. Language that promises
less is reported as an information item because it leaves supported knowledge
unused, but it does not block.

## Type before strength

**Assertion type is prior to tier.** A tier is meaningful only when
`assertion_type: world`. Applying the T0--T4 scale before typing would mistake
a hypothesis, a statement about an estimator, or a modeled quantity for a
claim about observed reality.

The five empirical assertion types and their rules are:

| `assertion_type` | Contract |
|---|---|
| `world` | A statement about an observed or counterfactual state of the world. It must declare exactly one T0--T4 tier. |
| `negative` | An exclusion or absence claim. It is untiered and requires `power_basis` naming the test, sample size, and minimum detectable effect. Without that basis, only hedged wording is licensed and `rule out` is prohibited. |
| `methodological` | A statement whose object is an estimator or method. It is untiered and excluded from empirical-strength summaries. |
| `discriminating` | A pattern used to distinguish the focal account from a named alternative. It is untiered and must register that alternative explanation. **Low lexical strength is normal** for this type and is neither weak evidence nor an underclaim residual. |
| `model_internal` | A result conditional on the model. It is untiered, requires `as_modeled: true`, and may use `significant` only when `underlying_precision.has_sampling_distribution` is true. |

`hypothesis` is also an accepted `assertion_type` value, but denotes a
proposition awaiting a test rather than an empirical assertion. It is untiered
and excluded from empirical-strength summaries. Thus the registry taxonomy has
six values while the governed empirical assertions comprise the five rows
above. Every untiered site records `declared_tier: null`.

### World-only ladder

T0 is the strongest world language and T4 the weakest:

| Tier | World-language commitment | Numeric strength |
|---|---|---:|
| `T0` | An unqualified causal commitment | 4 |
| `T1` | A causal commitment constrained by a registered scope qualifier | 3 |
| `T2` | A causal commitment accompanied by material counterevidence | 2 |
| `T3` | Association, interpretation, or consistency with an account | 1 |
| `T4` | Description without an effect or causal commitment | 0 |

The numeric value exists only for residual calculation. It is not assigned to
untiered assertion types.

## Assertion-site registry

Strength is registered for each use of a claim, not once for an entire claim
revision. Source paths are relative to the registry directory, and anchors
must resolve to a stable marker or an unambiguous line range in that source.
`title` is a first-class section role because a claim's strongest expression
may occur there.

```yaml
assertion_sites:
  - path: paper/results.tex
    anchor: result-main-effect
    section_role: results
    assertion_type: world
    declared_tier: T1
    qualifier_scope: sentence
    counterevidence_prominence: null
    underlying_precision:
      estimate_id: EC-002#row1col2
      significant_at: 0.05
      has_sampling_distribution: true
      n: 18420
    scope_declaration: null
    power_basis: null
    upgrade_justification: null
    alternative_explanation: null
    as_modeled: null
```

Allowed `section_role` values are `title | abstract | introduction | results |
mechanism | discussion | conclusion`. Each site exposes the following v2.2
fields to the validator:

- `assertion_type`: one of the six taxonomy values above.
- `declared_tier`: `T0 | T1 | T2 | T3 | T4` for `world`; `null` otherwise.
- `qualifier_scope`: `sentence | paragraph | section | cross_reference`.
- `counterevidence_prominence`: `parenthetical | clause_appended |
  separate_contrastive_sentence | footnote | appendix`, or `null` when no
  counterevidence bears on the site.
- `underlying_precision`: an object containing `significant_at`,
  `has_sampling_distribution`, `n`, and `estimate_id`. Values that do not
  exist must be explicit `null` values rather than invented precision.
- `scope_declaration`: `null` for sentence scope; otherwise a mapping locating
  the qualifying statement and explicitly bounding its coverage.
- `power_basis`: required for `negative`, `null` for other types.
- `upgrade_justification`: required when a `world` site's `declared_tier` is
  stronger than the same claim's results-site `declared_tier`; otherwise
  `null`. Untiered assertion types leave it `null` or absent.
- `alternative_explanation`: required for `discriminating` sites as a
  nonempty, specific account that the assertion distinguishes from the focal
  account; `null` or absent for every other type.
- `as_modeled`: required with the literal value `true` for `model_internal`
  sites; `null` or absent for all other types.

### Scope declarations

Paragraph, section, and cross-reference qualifiers are permitted only when the
site carries a `scope_declaration`. Its coverage is a closed manuscript range,
not an implication that a reader or validator must infer:

```yaml
scope_declaration:
  path: paper/structural-results.tex
  anchor: partial-counterfactual-caveat
  coverage:
    path: paper/structural-results.tex
    start_anchor: counterfactual-a
    end_anchor: counterfactual-c
```

The declaration governs only assertion sites inside that range. A declaration
in results does not automatically cover an abstract, title, or conclusion
site; those uses must carry their own applicable scope. This rule makes a
counterfactual caveat auditable even when it qualifies several experiments.

### Type-specific records

A negative assertion has an executable power record:

```yaml
power_basis:
  test: equivalence_test
  sample_size: 18420
  minimum_detectable_effect: 0.03
```

All three values are required. A conventional null result without an MDE is
not a power basis. Missing or incomplete `power_basis` caps the site at hedged
absence language and makes `rule out` invalid.

A discriminating assertion also records `alternative_explanation`, with a
specific account rather than a generic value such as `selection`. A
`model_internal` assertion records `as_modeled: true`. If an estimated object
becomes a simulation output, its site also sets
`underlying_precision.has_sampling_distribution: false`.

An upgrade trace is reviewable evidence for intentional strengthening:

```yaml
upgrade_justification:
  results_site: paper/results.tex#result-main-effect
  rationale: "The abstract states the preregistered estimand within its population scope."
  evidence_card: EC-002
  recorded_by: lead_author
  recorded_at: 2026-08-15T20:00:00Z
```

The trace explains the difference; it does not automatically make the stronger
site correct and cannot waive another blocking rule.

## Declaration and lexical enforcement

Every assertion is checked twice. The YAML declaration records the author's
intended type and strength. A lexical classifier independently reads the text
at the registered anchor so later editing cannot silently drift from that
intent.

Classification is limited to **registered assertion sites**. Tier, residual,
prominence, and scope are computed there and nowhere else, so quoted
scholarship, negated examples, and unrelated prose are never graded.

**Discovery** is a separate pass with a different job. Registration alone
cannot distinguish an unfinished registry from a finished one: omitting a site
removes it from every check, and an empty registry validates exactly like a
complete one. So each output declares its `manuscript_sources`, and the
manuscript is scanned for sentences carrying a causal marker. A candidate that
no registered site covers is reported as `ASSERTION_SITE_UNREGISTERED`, and a
quantitative literal outside a registered site is reported as
`QUANTITATIVE_VALUE_UNREGISTERED`.

This inverts what marker recall controls. Under registration alone, a marker
the list omits is an overclaim that cannot be caught. Under discovery, an
over-inclusive marker list costs one question to the author, and an
under-inclusive one costs a missed prompt — the failure direction is the safe
one.

Discovery runs in `enforce` mode by default and may be set to `report` during
adoption; either way the mode appears in the `MANUSCRIPT_COVERAGE` report.
Prose that reports another author's finding can be excluded by an explicit
range carrying a reason, and the number of excluded ranges is counted in that
same report. At Checkpoint C, a submission that declares no
`manuscript_sources` blocks with `MANUSCRIPT_SOURCES_REQUIRED` and yields an
`inactive` coverage report: the system states that completeness is unknown
rather than reporting success.

Lexical markers are grouped into semantic classes: causal, scope-qualifying,
evidential-weak, evidential-moderate, evidential-strong, descriptive, and
concessive. `associational` and `framing` remain accepted configuration
aliases for evidential-strong and concessive. These classes are
**project-extensible** through configuration. The extension mechanism adds or
refines semantic markers; it does not create a global banned-word list or
prescribe sentence form. The two type-specific prohibitions on `rule out` and
unsupported `significant` remain contract rules, not a general style list.

Matching is inflection tolerant, so one lemma covers its ordinary verb forms.
A marker list is a vocabulary, not a spelling exercise: without this, a
curated list silently misses `raises`, `reduced`, and `driving`, and a
sentence that plainly commits to a causal effect scores as descriptive.

Evidential frames are **graded**, and a frame lowers what a sentence promises
even when a causal verb survives inside it. A weak frame barely lowers it, so
`the results indicate that X increases Y` remains an unqualified causal
commitment; a moderate frame lowers it to a qualified one; a strong frame
takes it out of causal commitment altogether. Concessive markers locate where
an author gives ground and never change what a sentence promises: a sentence
that merely contains the word `limitation` is not hedged.

## Residual rule

For a `world` site, the validator maps the lexical classification to the
numeric ladder above and derives evidence strength from the existing v2.1
registry state plus the site's precision record:

```text
overclaim_residual = lexical_tier_strength - evidence_strength
```

Evidence strength must use the claim assessment, a narrowing reason matching
`revision_reason: bounded_by_*`, applicable gate status, provenance of live
supporting Evidence cards, and `underlying_precision`. It is computed from
registry state, not asserted as another author-editable strength number.

- `overclaim_residual > 0` emits blocking `OVERCLAIM_RESIDUAL`.
- `overclaim_residual < 0` emits informational `UNDERCLAIM_RESIDUAL`.
- `overclaim_residual == 0` emits no residual finding.

Only `world` sites participate. In particular, low-strength language on a
`discriminating` site is neutral. Tier compliance is not a separate check: a
tier and its modifiers are inputs to the residual, and the residual is the
enforcement result.

## Cross-site checks

The validator runs four checks in addition to the type-specific rules and
residual.

### 1. Propagation

When a results claim is narrowed with `revision_reason: bounded_by_*`, every
site for the same claim in `title`, `abstract`, and `conclusion` must express
the narrowed tier and scope. Retaining the pre-narrowing strength emits
blocking `NARROWING_NOT_PROPAGATED`. An `upgrade_justification` cannot override
this finding because a documented upgrade is not propagation of the bound.

### 2. Counterevidence prominence

Counterevidence that bears on an identifying assumption must appear in the
main text as at least a `separate_contrastive_sentence`. Parenthetical or
clause-appended treatment is insufficient, and footnote or appendix placement
is insufficient regardless of its local wording. A violation emits blocking
`COUNTEREVIDENCE_BURIED`.

A dedicated limitations section does not satisfy this check. The disclosure
must be adjacent to the assertion and diagnostic that it changes.

### 3. Immediate recovery

At a registered site, a concessive statement followed within one sentence by
`However`, `Nevertheless`, `Overall`, or `Encouragingly` without a tier
reduction emits reporting-only `IMMEDIATE_RECOVERY` at WARN level. The finding
calls for review; it does not infer dishonesty or block output.

### 4. Upgrade trace

Upgrade checks compare `declared_tier` only among `world` assertion sites for
the same claim. When a site's declared tier is stronger than that claim's
results-site declared tier, the stronger site must carry
`upgrade_justification`. Untiered sites never enter this comparison. Lexical
drift remains part of declaration/residual strength enforcement; it cannot be
converted into a trace-only warning. Missing justification emits
`UPGRADE_TRACE_MISSING` at WARN level. Abstract and title upgrades therefore
require a recorded trace, but missing that trace is WARN only, never BLOCK.
Strengthening these high-visibility locations is not itself an error, and an
upgrade trace cannot waive propagation and cannot waive another blocking rule.

## Structural-estimation contract

Structural work must keep `identified` and `calibrated` lexically distinct.
Identification language attributes the status to data variation, a moment, or
the likelihood (including passive forms or statements that only a particular
object can be identified). Calibration language identifies the analyst's
setting, its fixed value, and its external or conventional source.

The transition `identified → simulated` is a registered downgrade. The output
becomes `assertion_type: model_internal`, carries `as_modeled: true`, and marks
the absence of a sampling distribution in `underlying_precision`. Grammatical
similarity to an estimated effect does not preserve empirical status.

Every qualifier that governs more than one counterfactual is registered as a
`scope_declaration` with explicit coverage. Uses outside that coverage,
especially in the title, abstract, or conclusion, need a separate declaration.

## Stage 7 operating guidance

Stage 7 writes from the assertion registry and runs the v2.2 validator before
review or circulation. Authors register only substantive assertion sites and
attach a limitation where it changes the affected claim or diagnostic. A
standalone limitations section may summarize these constraints, but it cannot
substitute for adjacent registration and disclosure.

The claim-to-evidence audit remains an export of the governed registry. v2.2
adds assertion-site strength and scope to that export; it does not introduce a
second manually maintained audit.
