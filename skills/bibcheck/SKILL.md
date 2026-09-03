---
name: bibcheck
description: Compatibility entry point for auditing an existing .bib against canonical metadata. TRIGGER on "/bibcheck", "audit my .bib", "verify my references", "check my bibliography", suspected fabricated citations, or a pre-submission bibliography audit. Routes to bibliography-audit.
---

# bibcheck

This is an Empirical Workflow Kit compatibility facade. Runtime views defined
in `workflow.manifest.yaml` link here; edit only the canonical tree.

Read and execute [`../bibliography-audit/SKILL.md`](../bibliography-audit/SKILL.md) in full.
That skill owns the complete prompt, safeguards, inputs, outputs, and tool rules.
This alias adds no behavior and must never become a second implementation.
