# Decision Log

This log is append only.

| Timestamp | Decision | Alternatives | Reason | Evidence state | Authorized by | Downstream artifacts |
|---|---|---|---|---|---|---|
| 2026-08-15 00:00 UTC | Retain the fixture's Python exception for deterministic panel generation. | Rewrite the fixture producer in R | The smoke test exists specifically to verify the supported Python-to-R boundary and its failure modes. | reviewed | smoke fixture | `research.yaml`; `../panel-contract.yaml`; `../generate_panel.py` |
| 2026-08-15 00:00 UTC | Proceed from Stage 5 to Stage 6a with the locked smoke input. | Revise; pause | The deterministic fixture passed Checkpoint B. | reviewed | smoke fixture | `_status.md`; `evidence-card.md` |
