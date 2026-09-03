# Journal Scope for Venue Passes

Current as of: 2026-09-03.

Membership was checked against the current
[UT Dallas Top 100 journal page](https://jsom.utdallas.edu/the-utd-top-100-business-school-research-rankings/index.php)
and the April 2026 FT50 revision. The latter was cross-checked through the
[Financial Times list](https://www.ft.com/ft50-journals), the
[Aalto University research-rank page](https://www.aalto.fi/en/school-of-business/ft50-articles),
and the [Singapore Management University Libraries ISSN
guide](https://library.smu.edu.sg/topics-insights/updating-your-ft50-search-strategies-verified-issns-literature-search-scopus-and).
The 2026 FT revision added Academy of Management Annals, American Sociological
Review, and Psychological Science, and removed Human Relations, Journal of
Business Ethics, and Organization Studies. Before list membership is cited in
a manuscript, memo, or outlet-positioning row, re-check the official pages and
record the access date, as `writing-standards.md` requires for any fact that can
change.

The table strings are resolver inputs, not claims that title matching is a
stable identifier. Inspect the returned venue, and prefer ISSN filtering when
the active database supports it. Never infer list membership from a search hit.

This file is read by `literature-review` Step 1b and by any skill that needs a
default journal set: `research-council`, `manuscript-review`, `preregister`,
`bibliography-audit`, and the Stage 2 outlet-positioning reference. It answers
one question: which venues a topic search must sweep explicitly so that a review
of a business-school or economics question does not come back as an arXiv-only
list.

## How a venue pass works

- `paper.py search "<topic>" --venue "<journal>"` resolves the name to one
  OpenAlex source id by exact display-name match and filters the OpenAlex slice
  to that source; Semantic Scholar receives the same string as its venue filter;
  arXiv is skipped under `--venue`. Use the exact string in the tables below. A
  paraphrase falls back to OpenAlex's relevance-ranked first hit, which can be a
  different journal (`Review of Finance` is the standing example: a loose search
  returns other "review of ... finance" titles first).
- Each `--venue` invocation is one search and is priced as one (10 OpenAlex
  credits; see `<skills_root>/research-sources/SKILL.md`). Run one invocation
  per title, concurrently only when the active runtime profile and user policy
  authorize it, and merge on the ladder in Step 2.
- Sweep the Tier 1 set of every field the question touches. Widen to Tier 2
  when the user asked for exhaustive coverage, when Tier 1 returns fewer than
  about five candidates that will score 3 or above, or when the user's target
  outlet is in Tier 2.
- Report the swept fields and titles in the source coverage line, and mark each
  entry's list membership (`UTD24`, `FT50`, both, or nothing) after the journal
  name in the `.tex` block so the tier is visible without a second lookup.
- List membership controls coverage reporting, not relevance or evidentiary
  weight. Retain a directly relevant paper outside UTD24 or FT50, and never use
  membership as a substitute for reading or evaluating the paper.

## Which fields to sweep

Infer the field from the question's vocabulary, the user's stated target
outlet, and `research.yaml:target_outlets` when a project is active. When the
signal is mixed or absent, sweep the four core fields (information systems,
operations management, marketing, and management and organization science) plus
Management Science. Add economics and industrial organization whenever the
question concerns prices, competition, platforms, auctions, contracts,
regulation, labor, or policy evaluation. Add accounting or finance when the
outcome is a disclosure, reporting, or asset-pricing variable. Say which fields
were swept and why.

Management Science publishes all four core fields and is on both lists; include
it in every core-field pass.

## Tier 1: UTD 24 and FT 50 by field

Columns: U = UTD 24, F = FT 50. Access notes summarize
`<skills_root>/research-sources/REFERENCE.md`: "walled" means the publisher site
returns a Cloudflare challenge to plain HTTP and the free copy, when one exists,
is a repository, SSRN, NBER, or author version that `paper.py resolve` locates.

### Information systems

| `--venue` string | U | F | Publisher | Access note |
|---|---|---|---|---|
| `MIS Quarterly` | U | F | MIS Research Center | walled; author copies |
| `Information Systems Research` | U | F | INFORMS | walled; SSRN copies common |
| `Journal of Management Information Systems` | | F | Taylor & Francis | walled; author copies |
| `INFORMS Journal on Computing` | U | | INFORMS | walled; arXiv or SSRN copies common |
| `Management Science` | U | F | INFORMS | walled; SSRN and NBER copies common |

### Operations management

| `--venue` string | U | F | Publisher | Access note |
|---|---|---|---|---|
| `Operations Research` | U | F | INFORMS | walled; arXiv copies common |
| `Manufacturing & Service Operations Management` | U | F | INFORMS | walled; SSRN copies common |
| `Production and Operations Management` | U | F | SAGE (Wiley before 2024) | walled; SSRN copies common |
| `Journal of Operations Management` | U | F | Wiley | walled; author copies |
| `Management Science` | U | F | INFORMS | as above |

### Marketing

| `--venue` string | U | F | Publisher | Access note |
|---|---|---|---|---|
| `Marketing Science` | U | F | INFORMS | walled; SSRN copies common |
| `Journal of Marketing Research` | U | F | SAGE | walled; SSRN or author copies |
| `Journal of Marketing` | U | F | SAGE | walled; SSRN or author copies |
| `Journal of Consumer Research` | U | F | Oxford University Press | walled; author copies |
| `Journal of Consumer Psychology` | | F | Wiley | walled; author copies |
| `Journal of the Academy of Marketing Science` | | F | Springer | mixed open access; author copies |
| `Management Science` | U | F | INFORMS | as above |

### Management, strategy, and organization science

| `--venue` string | U | F | Publisher | Access note |
|---|---|---|---|---|
| `Academy of Management Journal` | U | F | Academy of Management | walled; author copies |
| `Academy of Management Review` | U | F | Academy of Management | walled; author copies |
| `Academy of Management Annals` | | F | Academy of Management | walled; review outlet |
| `Administrative Science Quarterly` | U | F | SAGE | walled; author copies |
| `American Sociological Review` | | F | SAGE | walled; author copies |
| `Organization Science` | U | F | INFORMS | walled; SSRN copies common |
| `Strategic Management Journal` | U | F | Wiley | walled; SSRN or author copies |
| `Journal of International Business Studies` | U | F | Springer Nature | mixed open access |
| `Journal of Management` | | F | SAGE | walled |
| `Journal of Management Studies` | | F | Wiley | walled; mixed open access |
| `Organization Studies` | | | SAGE | former FT50; removed in April 2026 |
| `Organizational Behavior and Human Decision Processes` | | F | Elsevier | walled |
| `Journal of Applied Psychology` | | F | American Psychological Association | walled (psycnet) |
| `Human Relations` | | | SAGE | former FT50; removed in April 2026 |
| `Human Resource Management` | | F | Wiley | walled |
| `Research Policy` | | F | Elsevier | walled; SSRN copies common |
| `Journal of Business Venturing` | | F | Elsevier | walled |
| `Entrepreneurship Theory and Practice` | | F | SAGE | walled |
| `Strategic Entrepreneurship Journal` | | F | Wiley | walled |
| `Journal of Business Ethics` | | | Springer | former FT50; removed in April 2026 |
| `Psychological Science` | | F | SAGE | walled; author and PsyArXiv copies |
| `Harvard Business Review` | | F | Harvard Business Publishing | practitioner outlet; rarely a citation target |
| `MIT Sloan Management Review` | | F | MIT | practitioner outlet; rarely a citation target |

### Accounting

| `--venue` string | U | F | Publisher | Access note |
|---|---|---|---|---|
| `The Accounting Review` | U | F | American Accounting Association | walled; SSRN copies common |
| `Journal of Accounting Research` | U | F | Wiley | walled; SSRN copies common |
| `Journal of Accounting and Economics` | U | F | Elsevier | walled; SSRN copies common |
| `Accounting, Organizations and Society` | | F | Elsevier | walled |
| `Contemporary Accounting Research` | | F | Wiley | walled |
| `Review of Accounting Studies` | | F | Springer | walled; SSRN copies common |

### Finance

| `--venue` string | U | F | Publisher | Access note |
|---|---|---|---|---|
| `The Journal of Finance` | U | F | Wiley | walled; SSRN copies nearly always |
| `Journal of Financial Economics` | U | F | Elsevier | walled; SSRN copies nearly always |
| `Review of Financial Studies` | U | F | Oxford University Press | walled; SSRN copies nearly always |
| `Journal of Financial and Quantitative Analysis` | | F | Cambridge University Press | walled; SSRN copies |
| `Review of Finance` | | F | Oxford University Press | walled; SSRN copies; thin OpenAlex record, see the venue-string notes |

### Economics titles on the FT 50

| `--venue` string | U | F | Publisher | Access note |
|---|---|---|---|---|
| `American Economic Review` | | F | American Economic Association | article PDF walled; appendix, data, and NBER copies free |
| `Econometrica` | | F | Wiley for the Econometric Society | walled; author and arXiv copies |
| `Journal of Political Economy` | | F | University of Chicago Press | walled; NBER copies |
| `The Quarterly Journal of Economics` | | F | Oxford University Press | walled; NBER copies |
| `The Review of Economic Studies` | | F | Oxford University Press | walled; author copies |

## Top economics journals beyond the FT 50

The five FT 50 titles above are the economics "top five". For an applied
question the next tier is cited as often, and surveys in the last three rows
are where a literature review should start when the topic has one.

| `--venue` string | Role | Publisher |
|---|---|---|
| `American Economic Review: Insights` | short general-interest papers | American Economic Association |
| `American Economic Journal: Applied Economics` | applied microeconomics, program evaluation | American Economic Association |
| `American Economic Journal: Economic Policy` | policy evaluation, public economics | American Economic Association |
| `American Economic Journal: Microeconomics` | theory and IO | American Economic Association |
| `American Economic Journal: Macroeconomics` | macroeconomics | American Economic Association |
| `The Review of Economics and Statistics` | applied econometrics | MIT Press |
| `Journal of the European Economic Association` | general interest | Oxford University Press |
| `The Economic Journal` | general interest | Oxford University Press |
| `Journal of Political Economy Microeconomics` | applied theory and IO, launched 2023 | University of Chicago Press |
| `Journal of Econometrics` | econometric method | Elsevier |
| `Journal of Labor Economics` | labor | University of Chicago Press |
| `The Journal of Human Resources` | labor, education, health | University of Wisconsin Press |
| `Journal of Public Economics` | public finance and policy | Elsevier |
| `Journal of Development Economics` | development | Elsevier |
| `Journal of Monetary Economics` | monetary and macro | Elsevier |
| `Journal of Economic Literature` | surveys | American Economic Association |
| `The Journal of Economic Perspectives` | surveys, open access | American Economic Association |
| `Annual Review of Economics` | surveys | Annual Reviews |

## Industrial organization journals

Sweep these with the economics tier whenever the question is about market
structure, pricing, platforms, auctions, entry, mergers, vertical relations, or
firm conduct. `Quantitative Marketing and Economics` sits on the marketing and
IO boundary and belongs in both passes.

| `--venue` string | Publisher | Access note |
|---|---|---|
| `The RAND Journal of Economics` | Wiley | walled; author and SSRN copies |
| `Journal of Industrial Economics` | Wiley | walled; author copies |
| `International Journal of Industrial Organization` | Elsevier | walled; author and SSRN copies |
| `Journal of Economics & Management Strategy` | Wiley | walled; author copies |
| `Review of Industrial Organization` | Springer | walled; author copies |
| `The Journal of Law and Economics` | University of Chicago Press | walled; SSRN copies |
| `The Journal of Law, Economics, and Organization` | Oxford University Press | walled; SSRN copies |
| `Quantitative Marketing and Economics` | Springer | walled; SSRN copies common |

## Tier 2: field extensions

Use after Tier 1, or when the user's target is here.

| Field | `--venue` strings | Note |
|---|---|---|
| Information systems | `Journal of the Association for Information Systems`, `European Journal of Information Systems`, `Information Systems Journal`, `Journal of Information Technology`, `The Journal of Strategic Information Systems`, `Decision Support Systems`, `Information & Management`, `Information and Organization` | the AIS Senior Scholars' list of premier journals (the "basket", expanded from eight to eleven titles in 2023) together with MISQ, ISR, and JMIS above |
| Operations management | `Decision Sciences`, `IISE Transactions`, `Transportation Science`, `Naval Research Logistics (NRL)`, `Journal of Supply Chain Management`, `INFORMS Journal on Applied Analytics` | the OpenAlex display name for NRL carries the parenthetical |
| Marketing | `Quantitative Marketing and Economics`, `International Journal of Research in Marketing`, `Journal of Retailing`, `Journal of Interactive Marketing`, `Marketing Letters` | QME also appears in the IO pass |
| Management and organization | `Strategy Science` | field extension beyond the current UTD24 and FT50 sets |

## Venue-string notes

- OpenAlex prefixes `The` on some mastheads and not others. The strings above
  use whichever form matches exactly; do not "correct" them.
- `Review of Finance` has an exact OpenAlex record, but it ranks low in the
  relevance search and holds few works, so `paper.py`'s ten-result lookup can
  miss it and fall back to another "review of ... finance" title, and the
  filter returns little even when it resolves. Check the `venue` field of the
  first result; if it is not `Review of Finance`, drop the flag and filter the
  merged open-search results by venue string in Step 2 instead.
- `Journal of Law and Economics` without the leading `The` matches a different,
  minor journal by exact name. Use `The Journal of Law and Economics` for the
  Chicago journal.
- When `paper.py` warns that no OpenAlex source matched, the string is wrong or
  the journal has been renamed; look up the current masthead before retrying.
