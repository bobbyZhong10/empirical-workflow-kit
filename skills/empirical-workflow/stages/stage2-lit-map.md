# Stage 2: Literature Map

Goal: locate the paper in a conversation, and extract the standard constructs,
measures, and identification strategies that conversation already accepts.
The purpose is not a summary of related work. It is to find out what the field
will take for granted and what it will demand be defended.

Output: `docs/lit_map.md`.

## 2.1 Scope the question

Write the research question in one sentence. Then write the two or three
distinct literatures it could plausibly be published in. The framing choice is
made here and it determines which contribution claim is credible.

## 2.2 Search

Use the semantic search tool over the journal corpus for the published side, and
a general scholarly search for working papers, since the newest identification
practice usually appears in working papers first.

For each search, record the query and the number of hits retained. A literature
map with no record of how it was built cannot be updated later.

## 2.3 Cluster into conversations

Organize the retained papers into three to five conversations, not into a flat
list. For each conversation produce a row:

| Conversation | Representative papers | What is settled | What is open | How our data speaks to it |

The fourth and fifth columns are where the paper lives. If no row has a
defensible entry in both, the project does not yet have a paper.

## 2.4 Locate the gap honestly

State the gap as a claim that could be wrong, and then state what would falsify
it. "No prior work has examined X" is almost always false and is the weakest
available framing. Prefer a gap of mechanism, of context boundary, or of
identification quality.

## 2.5 Constructs and standard measures

Extract, for each construct the paper will need, how prior work measured it and
what the accepted proxies are. This table feeds Stage 4 directly and is the
evidence base for the proxy justifications required at Checkpoint B.

| Construct | Standard measure in prior work | Source papers | Available in our data |

## 2.6 Identification precedent

Record how the closest three papers identified their effects, and what
robustness checks referees demanded of them. This is the most reliable available
forecast of what this paper will be asked for.

## Handoff

`docs/lit_map.md` contains: framing options, conversation table, gap statement,
construct measure table, identification precedent. Update `_status.md`.
