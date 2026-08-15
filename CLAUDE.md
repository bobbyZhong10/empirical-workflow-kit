# Claude Runtime Adapter

This repository uses [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) as its
portable research contract. Before acting, read it and the active
`research.yaml` (or [research.example.yaml](research.example.yaml) until a
project configuration exists).

Speak with the user in Chinese. Write all repository artifacts in English.

For empirical research work, load the `empirical-workflow` skill, use its stage
router, and read only the stage file needed for the current stage. Claude keeps
its reasoning in the conversation; durable decisions, evidence, and status
belong in the repository templates referenced by the protocol.

## Cross-runtime handoff

1. Finish the current atomic task and update its durable artifacts.
2. Record decisions and evidence, then update the project status.
3. Write a handoff with the completed stage, changed artifacts, open risks,
   next action, and unresolved pause.
4. Before continuing, the receiving runtime reads, in this order:
   `RESEARCH_PROTOCOL.md`, `research.yaml`, `_status.md`, the most relevant/current evidence card, then the tail of `decision-log.md`.
