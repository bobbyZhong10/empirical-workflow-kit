# Writing Standards

Read this before drafting and again before the final pass. It governs prose in
the manuscript. It does not govern the registry, the decision log, or code
comments.

The target is the register of a leading journal in economics or management
science: formal, plain, and unadorned. Four of the rules below are mechanical
and the validator checks them at Checkpoint C. The rest are the author's.

## Checked

**No em dash.** Neither `---` nor a literal em dash. An em dash is almost
always a comma, a colon, a semicolon, or a full stop that has not been chosen.

> ~~The two platforms hold the same instruments---price and pay---and use them
> differently.~~
> The two platforms hold the same two instruments, price and pay, and use them
> differently.

Code `PROSE_EM_DASH`.

**No contractions.** Write `does not`, `it is`, `cannot`, `we have`. Code
`PROSE_CONTRACTION`.

**No possessive on a named thing.** A firm, a method, a model, or a system does
not own anything. Prefer `of`, a noun modifier, or the passive.

> ~~the margin of Uber's response~~ → the Uber margin response
> ~~Lyft's driver-pay share~~ → the driver-pay share on Lyft
> ~~the estimator's standard error~~ → the standard error of the estimator

Code `PROSE_NAMED_POSSESSIVE`. The bibliography is exempt.

**No cross-reference in parentheses.** A table or a figure that matters enough
to point at matters enough to name in the sentence.

> ~~Narrowing the window preserves every coefficient except one
> (Table~\ref{tab:window}).~~
> Table~\ref{tab:window} reports the same specification on a narrower window,
> where every coefficient except one is preserved.

Code `PROSE_PARENTHETICAL_REFERENCE`.

## Not checked, and still required

**Plain words.** Use the ordinary word. `use`, not `utilise`. `show`, not
`elucidate`. `because`, not `owing to the fact that`. A reader should never
have to pause over the vocabulary to reach the argument.

**One idea per sentence, and the subject early.** Long sentences are permitted
when the length carries a clause structure a reader can follow. They are not
permitted when the length is three ideas that were never separated.

**Say what moved, then by how much, then what it means.** In that order. A
sentence that opens with the interpretation and buries the estimate reads as
advocacy.

**Remove the defensive clause.** Prose written to pre-empt a referee reads as
anxious and adds nothing a reader can use. State the finding and state its
limit; do not also state that you are aware of the limit.

> ~~It should be noted that, while this result is of course subject to the
> usual caveats, the estimate is nonetheless suggestive of a real effect.~~
> The estimate is 0.87 dollars, and it does not survive a narrower window.

**Notes under a table describe the table.** The specification, the inference,
the sample, the units, and the meaning of any symbol. Not the motivation, not
the interpretation, not a defence of a choice made elsewhere. If a note runs
past five sentences it has stopped being a note.

**Section count.** Six to eight sections is the working range for a full paper.
More than that usually means two adjacent sections are one section: results and
mechanism, discussion and conclusion, limitations folded into whichever section
earned them.

## Sources outside the literature

A policy, a price, a start date, a company statement, or a public dataset is
cited in a footnote with a link and one plain sentence, not in the reference
list. The reference list is for scholarship.

```latex
\footnote{The per-trip charge is set by the Metropolitan Transportation
Authority at \$1.50 for high-volume for-hire vehicles and \$0.75 for taxis.
See \url{https://congestionreliefzone.mta.info/tolling}, accessed 16 August
2026.}
```

Give the accessed date for anything that can change. Prefer the most durable
form of a source: a numbered agency notice over a campaign microsite, a data
dictionary over a landing page.

## Citation format

**The outlet decides, and the two common ones disagree on every point.** Check
the target before drafting, and hold the bibliography as fields rather than as
rendered strings so that switching is a flag and not a rewrite.

| | INFORMS journals (ISR, Management Science, Operations Research) | MIS Quarterly |
|---|---|---|
| Style | author-year, Harvard | APA 7th |
| In text | `(Rochet and Tirole 2003)`, no comma | `(Rochet & Tirole, 2003)`, comma |
| Between works | comma, chronological | semicolon |
| Author names | `Rochet JC, Tirole J`, no periods after initials | `Rochet, J.-C., & Tirole, J.` |
| Journal name | abbreviated, roman: `J. Eur. Econom. Assoc.` | full, italic |
| Volume and pages | `1(4):990--1029` | `1(4), 990--1029` |
| DOI | **omitted** for an ordinary journal article; used only for ahead-of-print and electronic sources | **included** on every work that has one |

Two traps. First, APA 7th does require a DOI, so a paper drafted in APA and
submitted to an INFORMS journal carries sixty links that the house style does
not want. Second, MIS Quarterly abandoned its former bespoke style in favour of
APA 7th, so the `Author, A. "Title," MIS Quarterly (25:1), 2001, pp. 107-136`
form that many templates and reference managers still emit is now wrong for
that journal too.

Other UTD 24 and FT 50 outlets carry their own house styles: the SAGE marketing
journals (Journal of Marketing Research, Journal of Marketing) follow the AMA
style, the Academy of Management journals follow the AOM style guide, and the
AEA journals follow Chicago author-date. Confirm the current author guidelines
for the target before generating the `\bibpunct` line, and record the access
date.

The INFORMS class ships INFORMS punctuation and it is correct for an INFORMS
outlet. Override it only when the target is APA. Generate the `\bibpunct`
line from the same script that generates the entries, so the in-text form and
the reference list cannot disagree; see `latex-manuscript-adapter.md`.
