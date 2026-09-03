---
name: replication-package
description: Compatibility entry point for assembling a journal-ready replication archive and scanning it for secrets, PII, and local paths. TRIGGER on "/replication-package", "build a replication package", "data availability statement", "zip up the code and data", or a data-editor delivery request. Routes to replication-release.
---

# replication-package

This is an Empirical Workflow Kit compatibility facade. Runtime views defined
in `workflow.manifest.yaml` link here; edit only the canonical tree.

Read and execute [`../replication-release/SKILL.md`](../replication-release/SKILL.md) in full.
That skill owns the complete prompt, safeguards, inputs, outputs, and tool rules.
This alias adds no behavior and must never become a second implementation.
