# LaTeX Manuscript Adapter (Management Science / INFORMS)

Read this at Stage 7, not earlier. The journal format adapter is applied only
after the scientific content is stable; copying a template into a project
before then invites formatting work to substitute for analysis.

## Installing the template

Copy the INFORMS class, bibliography style, and template into the project's
`paper/` directory at Stage 7:

```
cp Template_for_Management_Science_Journal/informs3.cls        paper/
cp Template_for_Management_Science_Journal/informs2014.bst     paper/
cp Template_for_Management_Science_Journal/Management-Science-template.tex paper/manuscript.tex
cp skills/empirical-workflow/templates/claimsite.sty           paper/
```

Use `Management-Science-template-with-ECompanion.tex` instead when the paper
carries an online appendix. `INFORMS-Style-Instructions-2016-02-22.pdf` is the
authority for anything this file does not state.

Preamble additions:

```latex
\usepackage{claimsite}
\input{figures}   % generated; never edited by hand
```

## Anchoring assertion sites

The registry binds a claim to a sentence. Line numbers do not survive editing,
so the binding is an inline marker that expands to nothing:

```latex
\claimsite{into-crz-divergence}The fee raises platform margin on inbound trips.
```

Rules:

- One anchor per sentence, immediately before the sentence it binds.
- The anchor string must occur exactly once in the source file.
- `\scopesite{...}` marks a scope declaration and its coverage bounds when a
  qualifier governs more than one sentence.
- Anchors change no typeset output. If removing every anchor changes the PDF,
  the anchor is being used for something it is not for.

The validator resolves the anchor, takes the rest of that line as the assertion
text, and **discards any trailing LaTeX comment**. A comment cannot supply a
counterevidence cue, a scope qualifier, or anything else the checks look for.

## Numbers

The manuscript never types a quantitative value. It calls the registry:

```latex
Retention rises by \figval{retention_pp} for participating firms.
```

`tools/render_figure_macros.py` writes `paper/figures.tex` from the registry's
reported figures. A figure that is stale, superseded, or bound to a superseded
pipeline is **not emitted**, so `\figval` raises a LaTeX error and the build
fails rather than typesetting a value the registry has retired. A figure
carrying `derived_from` and `transform` is recomputed by the validator; its
displayed value is never maintained by hand.

The validator rejects a quantitative literal typed at a registered assertion
site: any numeral carrying a decimal point, a percent sign, a currency symbol,
or a magnitude suffix. Section numbers, table references, and hypothesis labels
are deliberately out of scope, so `Table~2` and `H1` are fine.

```
BLOCK QUANTITATIVE_VALUE_NOT_REGISTERED  literals: ["7.68"]
```

### How a number is typeset

A figure may declare how it appears. The registry holds the value; `display`
holds the presentation, and the generator applies it:

```yaml
- figure_id: fee
  value: 1.5
  display: {decimals: 2, prefix: "\\$", unit: usd}       # -> \$1.50
- figure_id: uber_n
  value: 24013619
  display: {decimals: 0, thousands_separator: true}     # -> 24,013,619
```

`decimals` runs 0 to 6. Padding is allowed and rounding is not: a display that
rounds a non-zero value to zero, or that flips its sign, is rejected --

```
BLOCK FIGURE_DISPLAY_MISREPRESENTS  value: 0.004  displayed: 0.00
```

-- because a reader takes 0.00 for a null. The place to lie about a result is
its presentation, so presentation is checked like everything else.

The sign belongs to the number, so the prose must not repeat it. Writing
*"margin falls by \figval{x}"* where `x` is negative makes the reader subtract
twice; report the signed coefficient (*"margin moves by ..."*) or drop the
directional verb.

```
BLOCK FIGURE_SIGN_READS_BACKWARD  phrase: "falls by \figval{l_margin_into}"  value: -3.306
```

## Section roles

`section_role` is not taken on trust. For a `.tex` source the validator
resolves the governing role from the file — `\TITLE{...}`, the `abstract`
environment, and `\section{...}` headings — and blocks when the declared role
disagrees:

```
BLOCK SECTION_ROLE_MISMATCH  declared: results  resolved: abstract
```

Only `\section` participates. A `\subsection{Robustness}` nested under
`\section{Results}` resolves to `results`, so a correctly declared `robustness`
site inside it blocks. Give a section role its own `\section` when the
distinction matters to a claim; do not relabel the site to satisfy the parser.

This is what makes the propagation and upgrade-trace checks trustworthy. It
matters most for `title`, which is a checked role: a title can promise more
than the body delivers, and in the reference corpus one paper's title asserts
an optimality claim its own text explicitly disclaims.

## Class furniture

The INFORMS class prints three things that are submission apparatus rather than
content: a banner and a red usage notice at the top of page 1, and a running
head repeating `Article submitted to <journal>; manuscript no.` on every page
after it. Suppress all three in the preamble:

```latex
\makeatletter
\def\theARTICLETOP{\vspace*{-24pt}}
\makeatother
\RRHFirstLine{}\RRHSecondLine{}
\LRHFirstLine{}\LRHSecondLine{}
```

Heading fonts come from the class option. `mnsc` uses the body serif; `opre`
sets `\if@OPRE` and imposes sans-serif headings. If subsection headings look
wrong against the body text, check the option before touching the class.

### Bibliography

The class ships the INFORMS citation convention, which is correct for an
INFORMS outlet and wrong for APA. Do not choose by eye: generate both the
punctuation line and the entries from one table, and switch on the outlet.

```latex
% INFORMS: (Hall et al. 2018), abbreviated journal, no DOI
\bibpunct[, ]{(}{)}{,}{a}{}{,}%  \def\BIBand{and}%
\bibitem[Hall et al.(2018)]{hallpalsson2018} Hall JD, Palsson C, Price J
(2018) Is Uber a substitute or complement for public transit? J. Urban Econom.
108:36--50.

% APA 7th: (Hall et al., 2018), full journal, DOI required
\bibpunct[, ]{(}{)}{;}{a}{,}{,}%  \def\BIBand{\&}%
\bibitem[Hall et al.(2018)]{hallpalsson2018} Hall, J. D., Palsson, C., \&
Price, J. (2018). Is Uber a substitute or complement for public transit?
\emph{Journal of Urban Economics}, \emph{108}, 36--50.
https://doi.org/10.1016/j.jue.2018.09.003
```

`writing-standards.md` carries the full comparison. Write the `\bibpunct` line
to its own generated file and `\input` it, so a change of outlet cannot leave
the in-text form and the reference list disagreeing.

The `\bibitem` label drives `\citet`/`\citep`, so it carries the short form
(`Hall et al.(2018)`) while the entry carries the full one. Both are checked
against `references.yaml`, which holds the locator and the person who verified
it — the citation checks read keys and counts, not formatting, so a
well-formatted entry with a wrong DOI still fails.

## Adopting on an existing draft

Do not hand-author the registry. Three quarters of it is derivable.

```bash
python3 tools/scaffold_registry.py init .                 # skeletons, not blank files
python3 tools/validate_registry.py . --checkpoint C       # discovery lists what is unregistered
python3 tools/scaffold_registry.py sites . --limit 10     # stubs for those sentences
python3 tools/scaffold_registry.py figures . \
    --artifact results/p1.json --pipeline p1              # figures read from the artefact
```

`init` leaves exactly two decisions blocking: the pipeline's first formal batch
timestamp and the Checkpoint B gate-set signature. `sites` fills in what the
source and the classifier already know — path, anchor, section role, and the
tier the text actually reads as — and leaves the judgement fields empty so the
validator asks for them. Registering the whole draft at once is not the
intended path: set `writing_strength.discovery: report` while adopting, work
through the coverage report in batches, and switch to `enforce` when the count
reaches zero.

## Build

```bash
python3 tools/validate_registry.py . --checkpoint C --format json > build/registry.json
python3 tools/render_figure_macros.py . --output paper/figures.tex
cd paper && pdflatex manuscript && bibtex manuscript && pdflatex manuscript && pdflatex manuscript
```

The order is binding. The submission export gate runs first; the figure macros
are regenerated second; the PDF is produced last. A build that starts from a
stale `figures.tex` is not a submission build.

## What this adapter does not do

It does not reformat, reorder, or rewrite. It does not change an estimate, a
table, or a claim. Formatting is applied after the science is settled, and the
adapter's only enforcement is that what the manuscript says matches what the
registry holds.

It also does not tell you how to word a sentence a check has objected to. See
`writing-under-the-registry.md` for that, and in particular for the one rule
this binding makes easy to break: the registry's vocabulary must not reach the
manuscript.
