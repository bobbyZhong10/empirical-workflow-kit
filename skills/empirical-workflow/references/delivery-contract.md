# The Delivery Contract

Read this at Stage 7 and again before Checkpoint C.

A project is not finished when the result is correct. It is finished when
someone else can pick it up. Those are different states, and the gap between
them is where most of a project's value quietly leaks: the panel that only
exists in a notebook, the figure nobody can regenerate, the table that lives
only inside a `.tex` file, the merge whose logic is in someone's head.

> **A finished project delivers into `output/`.** Everything a reader needs and
> nothing they have to ask for.

```
output/
  data/     the final data the paper was produced from, plus a markdown note
            saying how it was assembled
  code/     the code that runs the paper's empirical work
  result/   every figure as PNG, every table as CSV or markdown
  LaTeX/    the sources that compile the final PDF, and the PDF
```

Checkpoint C blocks on it. The codes are `OUTPUT_ROOT_MISSING`,
`OUTPUT_DIRECTORY_MISSING`, `OUTPUT_DIRECTORY_EMPTY`,
`OUTPUT_DATA_NOTE_MISSING`, `OUTPUT_PDF_MISSING` and
`OUTPUT_TABLE_EXPORT_INCOMPLETE`, with `OUTPUT_DELIVERY` as the summary report.

## `output/data`

The data the paper was actually produced from — not the raw download, not an
intermediate, the final analysis inputs. If they are too large to ship, ship
the smallest thing that reproduces the paper's numbers and say in the note what
was left out and where it lives.

**The note is the part people skip and the part readers need.** A CSV does not
explain itself. `README.md` in this directory must say:

- where each input came from, with its version or vintage;
- what was joined to what, on which key, and what kind of join;
- what was filtered and why, with the row count before and after each step;
- which derived columns exist and how each is computed;
- any field whose name does not mean what it says.

That last one is not hypothetical. A column named for the platform's commission
rate that in fact holds the driver's share of the fare will be read backwards by
every person who opens the file, and the note is the only place that gets fixed.

## `output/code`

The code that runs the paper's empirical work, in the order it runs.

**R is the default.** Panel construction, estimation, inference, tables and
figures all belong in R unless the project has recorded a reason otherwise in
`decision-log.md`. Python is for the cases where R genuinely cannot do the job —
no equivalent library, a performance ceiling, an upstream dependency that only
emits Python. Where an exception is taken, both halves ship here and the
boundary between them is a documented file, not a shared interpreter session.

A numbered sequence and a single entry point (`run_all.R`) are worth the ten
minutes they cost. So is a header on each script saying what it reads and what
it writes.

## `output/result`

Every figure the paper shows, as PNG. Every table the paper shows, as CSV or
markdown. One file per figure, one per table, named so the mapping to the paper
is obvious.

The rule is not about formats; it is about who can check the work. A reader who
has to install a LaTeX distribution to see your table will not see your table.
`OUTPUT_TABLE_EXPORT_INCOMPLETE` counts `\begin{table}` in the manuscript
sources and compares it to the number of exports, so a table added late without
its export is caught.

Generate these from the same script that generates what the paper embeds.
Exporting by hand afterwards is how the two versions come to disagree.

## `output/LaTeX`

The `.tex` sources, the class and style files, the bibliography, and the
compiled PDF. Someone with a TeX distribution and nothing else should be able
to run `pdflatex` twice and get the same document.

The PDF belongs here too, beside the sources that made it. A PDF without its
sources cannot be corrected; sources without the PDF cannot be checked against
what was submitted.

## What this contract does not do

It does not check that the delivered data produces the delivered result, that
the code runs, or that the PNG matches the figure in the PDF. Those are the
author's obligations and no directory layout can discharge them. What it does
is remove the excuse: when the four directories exist and are populated, the
question "can someone else pick this up?" has a checkable answer instead of an
optimistic one.
